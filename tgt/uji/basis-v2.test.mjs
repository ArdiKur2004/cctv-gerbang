// Uji migrasi skema versi 2: pengguna dan keanggotaan grup (Rencana T2 Task 1).
//
// Yang paling penting di berkas ini adalah uji "basis versi 1 BERISI DATA naik ke versi 2": tanpa itu, migrasi hanya
// terbukti jalan di basis kosong, padahal gunanya justru untuk basis yang sudah dipakai pelanggan.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { VERSI_SKEMA, buka, bukaVersi, versi, naik, turun, susunan } from '../basis.mjs';

test('versi 2 masih bisa dipasang sendiri, walau skema terbaru sudah lebih tinggi', () => {
  // Dulu uji ini berbunyi "versi skema sekarang 2". Itu sudah usang sejak versi 3 (Rencana T4), tetapi TIDAK
  // dihapus: ia dibalik menjadi penjaga bahwa langkah versi 2 tetap bisa dipasang terpisah. Basis data
  // pelanggan yang tertinggal di versi 2 harus tetap bisa dinaikkan bertahap.
  assert.ok(VERSI_SKEMA >= 2, 'versi skema tidak boleh turun di bawah 2');
  const db = bukaVersi(':memory:', 2);
  try {
    assert.equal(versi(db), 2);
    assert.ok(new Set(susunan(db)).has('anggota.peran'));
  } finally {
    db.close();
  }
});

test('tabel pengguna dan anggota ada, beserta kolom yang dipakai hak akses', () => {
  const db = buka(':memory:');
  try {
    const punya = new Set(susunan(db));
    for (const kolom of [
      'pengguna.nama', 'pengguna.wa', 'pengguna.sandi_hash', 'pengguna.dibuat',
      'anggota.grup_id', 'anggota.pengguna_id', 'anggota.peran', 'anggota.dibuat',
      // Pemilik kendaraan dan pengundang tamu: dasar pagar "penghuni hanya melihat miliknya sendiri".
      'kendaraan.pengguna_id', 'tamu.pengundang_id',
    ]) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada di skema versi 2`);
    }
  } finally {
    db.close();
  }
});

test('basis versi 1 yang SUDAH BERISI DATA naik ke versi 2 tanpa kehilangan apa pun', () => {
  const db = bukaVersi(':memory:', 1);
  try {
    assert.equal(versi(db), 1);
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'AB12CD')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Kantor Contoh Gate Selatan', 'kantor', 'Jl. Contoh 42', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare(
      `INSERT INTO kendaraan (gerbang_id, jenis, plat, atas_nama) VALUES (1, 'mobil', 'L9999QQ', 'Budi Contoh')`,
    ).run();

    // Sengaja berhenti di versi 2: yang diuji di sini adalah langkah 1 → 2 saja. Langkah berikutnya punya
    // ujinya sendiri di basis-v3.test.mjs.
    naik(db, 2);

    assert.equal(versi(db), 2);
    assert.equal(db.prepare('SELECT count(*) AS n FROM grup').get().n, 1);
    assert.equal(db.prepare("SELECT nama FROM gerbang WHERE id = 1").get().nama, 'Kantor Contoh Gate Selatan');
    assert.equal(db.prepare("SELECT plat FROM kendaraan WHERE id = 1").get().plat, 'L9999QQ');
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 0, 'tabel baru lahir kosong');
  } finally {
    db.close();
  }
});

test('turun dari 2 ke 1 menyisakan tabel versi 1 beserta datanya', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'EF34GH')").run();
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Aldy Contoh', '628100000001', 'x')").run();

    turun(db, 1);

    assert.equal(versi(db), 1);
    assert.equal(db.prepare('SELECT count(*) AS n FROM grup').get().n, 1, 'data versi 1 tidak boleh ikut terbuang');
    const punya = new Set(susunan(db));
    assert.ok(!punya.has('pengguna.nama'), 'tabel pengguna harus tercabut saat turun ke versi 1');
    assert.ok(!punya.has('anggota.peran'));
    assert.ok(!punya.has('kendaraan.pengguna_id'), 'kolom pemilik harus ikut tercabut');
    assert.ok(!punya.has('tamu.pengundang_id'));
    assert.ok(punya.has('gerbang.alamat'), 'tabel versi 1 harus tetap ada');
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

test('bukaVersi menolak versi yang tidak ada, supaya salah tulis tidak menghasilkan basis setengah jadi', () => {
  assert.throws(() => bukaVersi(':memory:', 99), /versi/i);
  assert.throws(() => bukaVersi(':memory:', 0), /versi/i);
});
