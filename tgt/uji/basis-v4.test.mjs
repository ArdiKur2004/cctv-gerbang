// Uji migrasi skema versi 4: masuk dengan email + OTP (Rencana T5, keputusan owner K72).
//
// Versi ini MEMBANGUN ULANG tabel pengguna, bukan sekadar menambah kolom, karena di versi 3 nomor WhatsApp
// dan sandi wajib diisi. Pembangunan ulang adalah migrasi paling berbahaya yang ada di repo ini: kalau
// penyalinannya meleset, data orang hilang tanpa ada yang mengeluh. Karena itu ujinya paling rinci.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { VERSI_SKEMA, buka, bukaVersi, versi, naik, turun, susunan } from '../basis.mjs';

test('versi 4 masih bisa dipasang sendiri, walau skema terbaru sudah lebih tinggi', () => {
  // DIBALIK, bukan dihapus — bentuk yang sama dengan uji versi 2 dan 3, supaya tidak perlu diubah lagi tiap
  // versi baru. Yang dijaga: langkah versi 4 tetap bisa dipasang terpisah, untuk basis yang tertinggal.
  assert.ok(VERSI_SKEMA >= 4, 'versi skema tidak boleh turun di bawah 4');
  const db = bukaVersi(':memory:', 4);
  try {
    assert.equal(versi(db), 4);
    assert.ok(new Set(susunan(db)).has('otp.kode_hash'));
  } finally {
    db.close();
  }
});

test('kolom email dan tabel otp ada', () => {
  const db = buka(':memory:');
  try {
    const punya = new Set(susunan(db));
    for (const kolom of ['pengguna.email', 'otp.email', 'otp.kode_hash', 'otp.kedaluwarsa', 'otp.coba']) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada di skema versi 4`);
    }
  } finally {
    db.close();
  }
});

test('⛔ basis versi 3 BERISI DATA naik ke versi 4 tanpa kehilangan satu baris pun', () => {
  const db = bukaVersi(':memory:', 3);
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'AB12CD')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gate Contoh', 'kantor', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Bos Contoh', '628100000001', 'hash-a')").run();
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Ani Contoh', '628100000002', 'hash-b')").run();
    db.prepare("INSERT INTO anggota (grup_id, pengguna_id, peran) VALUES (1, 1, 'pengelola')").run();
    db.prepare(
      `INSERT INTO kendaraan (gerbang_id, jenis, plat, atas_nama, pengguna_id)
       VALUES (1, 'mobil', 'L1234AB', 'Ani Contoh', 2)`,
    ).run();

    // Sengaja berhenti di versi 4: yang diuji di sini hanya langkah 3 → 4.
    naik(db, 4);

    assert.equal(versi(db), 4);
    const orang = db.prepare('SELECT id, nama, wa, sandi_hash, email FROM pengguna ORDER BY id').all();
    assert.deepEqual(orang.map((o) => [o.id, o.nama, o.wa, o.sandi_hash, o.email]), [
      [1, 'Bos Contoh', '628100000001', 'hash-a', null],
      [2, 'Ani Contoh', '628100000002', 'hash-b', null],
    ], 'baris pengguna berubah saat tabelnya dibangun ulang');

    // Yang paling mudah rusak saat tabel dibangun ulang: tautan dari tabel lain ke nomor penggunanya.
    assert.equal(db.prepare('SELECT pengguna_id FROM kendaraan WHERE id = 1').get().pengguna_id, 2,
      'tautan kendaraan ke pemiliknya putus saat pengguna dibangun ulang');
    assert.equal(db.prepare('SELECT peran FROM anggota WHERE pengguna_id = 1').get().peran, 'pengelola');
  } finally {
    db.close();
  }
});

test('kunci asing menyala lagi sesudah migrasi, bukan tertinggal mati', () => {
  // Migrasi versi 4 mematikan kunci asing sebentar. Kalau ia tertinggal mati, seluruh pagar keterkaitan data
  // di basis ini diam-diam lumpuh untuk sisa umur sambungan.
  const db = buka(':memory:');
  try {
    assert.equal(db.prepare('PRAGMA foreign_keys').get().foreign_keys, 1, 'kunci asing tertinggal mati');
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'EF34GH')").run();
    assert.throws(
      () => db.prepare(
        `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota) VALUES (99, 'X', 'kantor', 'J', 'S')`,
      ).run(),
      /FOREIGN KEY|constraint/i,
      'gerbang bisa menunjuk grup yang tidak ada: pagar kunci asing tidak bekerja',
    );
  } finally {
    db.close();
  }
});

test('email unik, tetapi banyak akun boleh tanpa email', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Satu', 'satu@example.test')").run();
    assert.throws(
      () => db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Dua', 'satu@example.test')").run(),
      /UNIQUE|constraint/i,
    );
    // Akun lama dari versi 3 belum punya email; banyak NULL harus boleh.
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Tiga', '628100000003', 'x')").run();
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Empat', '628100000004', 'y')").run();
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 3);
  } finally {
    db.close();
  }
});

test('turun dari 4 ke 3 mengembalikan susunan lama bila semua akun masih punya nomor WhatsApp', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Bos', '628100000001', 'hash-a')").run();
    turun(db, 3);
    assert.equal(versi(db), 3);
    const punya = new Set(susunan(db));
    assert.ok(!punya.has('pengguna.email'), 'kolom email harus tercabut');
    assert.ok(!punya.has('otp.kode_hash'), 'tabel otp harus tercabut');
    assert.equal(db.prepare('SELECT nama FROM pengguna WHERE id = 1').get().nama, 'Bos');
  } finally {
    db.close();
  }
});

test('⛔ turun ke versi 3 GAGAL KERAS bila ada akun yang hanya punya email', () => {
  // Disengaja. Versi 3 hanya mengenal masuk dengan nomor WhatsApp + sandi, jadi akun yang hanya punya email
  // TIDAK BISA ADA di sana. Menebak nomornya atau menyisipkan nilai palsu akan memalsukan data orang, jadi
  // migrasinya berhenti dan memberi tahu — bukan diam-diam mengarang.
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Ani', 'ani@example.test')").run();
    assert.throws(() => turun(db, 3), /NOT NULL|constraint/i);
  } finally {
    db.close();
  }
});

test('migrasi bolak-balik penuh tetap menghasilkan susunan yang sama', () => {
  const db = buka(':memory:');
  try {
    const sebelum = susunan(db);
    turun(db, 0);
    assert.equal(susunan(db).length, 0);
    naik(db);
    assert.deepEqual(susunan(db), sebelum);
  } finally {
    db.close();
  }
});
