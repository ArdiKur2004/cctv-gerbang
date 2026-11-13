// Uji sesi yang tersimpan di basis data (Rencana T8 Task 1).
//
// Yang ditutup di sini adalah batas yang sudah TERTULIS di tgt/server.mjs sejak T2: sesi disimpan di memori,
// jadi server yang dinyalakan ulang membuat semua orang masuk lagi. Itu terbukti mengganggu saat antrean luring
// dibuktikan di T4 — kejadian tersusul hanya sesudah orangnya masuk sekali lagi.
//
// Sesi adalah KUNCI MASUK. Karena itu tandanya disimpan ter-hash, sama seperti OTP: siapa pun yang membaca
// berkas basis data tidak boleh bisa memakai sesi orang lain.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

import { VERSI_SKEMA, buka, bukaVersi, versi, naik, turun, susunan } from '../basis.mjs';
import { UMUR_SESI_HARI, buatSesi, bacaSesi, hapusSesi, bersihkanSesi } from '../sesi.mjs';

function dbUji() {
  const db = buka(':memory:');
  db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Ani', 'ani@example.test')").run();
  db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Budi', 'budi@example.test')").run();
  return db;
}

// ─── Skema ──────────────────────────────────────────────────────────────────────────────────────────

test('versi 5 masih bisa dipasang sendiri, walau skema terbaru sudah lebih tinggi', () => {
  // DIBALIK, bukan dihapus: uji lama "versi skema sekarang 5" akan selalu basi. Yang dijaga adalah langkah
  // versi 5 tetap bisa dipasang terpisah, untuk basis yang tertinggal.
  assert.ok(VERSI_SKEMA >= 6, 'versi skema tidak boleh turun di bawah 6');
  const db = bukaVersi(':memory:', 5);
  try {
    assert.equal(versi(db), 5);
    assert.ok(!new Set(susunan(db)).has('sesi.tanda_hash'), 'tabel sesi seharusnya belum ada di versi 5');
  } finally {
    db.close();
  }
});

test('⛔ basis versi 5 BERISI DATA naik ke versi 6 tanpa kehilangan satu baris pun', () => {
  const db = bukaVersi(':memory:', 5);
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('RT 05', 'perumahan', 'AB12CD')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gerbang Depan', 'perumahan', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Ani', 'ani@example.test')").run();
    db.prepare("INSERT INTO anggota (grup_id, pengguna_id, peran) VALUES (1, 1, 'pengelola')").run();
    db.prepare(
      `INSERT INTO kendaraan (gerbang_id, jenis, plat, atas_nama, pengguna_id)
       VALUES (1, 'mobil', 'L1234AB', 'Ani', 1)`,
    ).run();

    naik(db, 6);

    assert.equal(versi(db), 6);
    const punya = new Set(susunan(db));
    for (const kolom of [
      'sesi.pengguna_id', 'sesi.tanda_hash', 'sesi.kedaluwarsa',
      'undangan_masuk.pengguna_id', 'undangan_masuk.grup_id', 'undangan_masuk.tanda_hash',
      'undangan_masuk.kedaluwarsa', 'undangan_masuk.dipakai_pada',
    ]) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada di skema versi 6`);
    }
    assert.equal(db.prepare('SELECT nama FROM pengguna WHERE id = 1').get().nama, 'Ani');
    assert.equal(db.prepare('SELECT pengguna_id FROM kendaraan WHERE id = 1').get().pengguna_id, 1);
  } finally {
    db.close();
  }
});

test('migrasi versi 6 bolak-balik: naik → turun → naik menghasilkan susunan yang sama', () => {
  const db = buka(':memory:');
  try {
    const sebelum = susunan(db);
    turun(db, 5);
    assert.equal(versi(db), 5);
    assert.ok(!new Set(susunan(db)).has('sesi.tanda_hash'), 'tabel sesi harus tercabut saat turun');
    naik(db);
    assert.deepEqual(susunan(db), sebelum);

    // Dan bolak-balik penuh sampai kosong, seperti versi-versi sebelumnya.
    turun(db, 0);
    assert.equal(susunan(db).length, 0);
    naik(db);
    assert.deepEqual(susunan(db), sebelum);
  } finally {
    db.close();
  }
});

// ─── Sesi ───────────────────────────────────────────────────────────────────────────────────────────

test('sesi yang dibuat bisa dibaca kembali', () => {
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 1);
    assert.equal(typeof tanda, 'string');
    assert.ok(tanda.length >= 32, 'tanda sesi terlalu pendek untuk kunci masuk');
    assert.deepEqual(bacaSesi(db, tanda), { penggunaId: 1 });
  } finally {
    db.close();
  }
});

test('⛔ sesi masih berlaku sesudah SERVER DINYALAKAN ULANG', () => {
  // Inti seluruh rencana ini. "Dinyalakan ulang" diperagakan dengan membuang semua keadaan di memori:
  // tandanya hanya dipegang pemanggil, dan basis datanya yang sama dibaca lagi.
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 2);
    // Tidak ada gudang, tidak ada Map, tidak ada apa pun yang diteruskan — hanya db dan tandanya.
    const sesudahNyalaUlang = bacaSesi(db, tanda);
    assert.deepEqual(sesudahNyalaUlang, { penggunaId: 2 },
      'sesi hilang: ia masih bergantung pada keadaan di memori');
  } finally {
    db.close();
  }
});

test('⛔ tanda sesi tersimpan TER-HASH, tidak pernah apa adanya', () => {
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 1);
    const baris = db.prepare('SELECT * FROM sesi').all();
    assert.equal(baris.length, 1);
    const semuaNilai = JSON.stringify(baris);
    assert.ok(!semuaNilai.includes(tanda),
      'tanda sesi tersimpan apa adanya: siapa pun yang membaca berkas basis data bisa memakai sesi orang lain');
    // Dan hash-nya memang hash tandanya, bukan nilai lain yang kebetulan tidak sama.
    assert.equal(baris[0].tanda_hash, createHash('sha256').update(tanda).digest('base64'));
  } finally {
    db.close();
  }
});

test('tanda palsu ditolak, dan tanda kosong tidak pernah cocok dengan apa pun', () => {
  const db = dbUji();
  try {
    buatSesi(db, 1);
    assert.equal(bacaSesi(db, 'bukan-tanda'), undefined);
    assert.equal(bacaSesi(db, ''), undefined);
    assert.equal(bacaSesi(db, undefined), undefined);
    assert.equal(bacaSesi(db, null), undefined);
  } finally {
    db.close();
  }
});

test('sesi kedaluwarsa ditolak, dan barisnya dibuang', () => {
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 1);
    // Majukan kedaluwarsanya ke masa lalu, cara yang sama dengan uji OTP.
    db.prepare("UPDATE sesi SET kedaluwarsa = datetime('now', '-1 second')").run();
    assert.equal(bacaSesi(db, tanda), undefined, 'sesi kedaluwarsa masih diterima');
    assert.equal(db.prepare('SELECT count(*) AS n FROM sesi').get().n, 0,
      'sesi kedaluwarsa tidak dibuang: alamat dan jejaknya tersimpan lebih lama dari perlunya (K71)');
  } finally {
    db.close();
  }
});

test(`umur sesi ${UMUR_SESI_HARI} hari dibaca dari satu tempat, bukan disalin`, () => {
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 1);
    const baris = db.prepare('SELECT kedaluwarsa, dibuat FROM sesi').get();
    const umurHari = (Date.parse(`${baris.kedaluwarsa}Z`) - Date.parse(`${baris.dibuat}Z`)) / 86_400_000;
    assert.ok(Math.abs(umurHari - UMUR_SESI_HARI) < 0.01,
      `umur sesi tersimpan ${umurHari} hari, bukan ${UMUR_SESI_HARI}`);
    assert.ok(bacaSesi(db, tanda));
  } finally {
    db.close();
  }
});

test('keluar menghapus sesinya sendiri, dan tidak menyentuh sesi orang lain', () => {
  const db = dbUji();
  try {
    const milikAni = buatSesi(db, 1);
    const milikBudi = buatSesi(db, 2);
    hapusSesi(db, milikAni);
    assert.equal(bacaSesi(db, milikAni), undefined);
    assert.deepEqual(bacaSesi(db, milikBudi), { penggunaId: 2 }, 'keluar menghapus sesi orang lain juga');
  } finally {
    db.close();
  }
});

test('satu orang boleh punya beberapa sesi: HP dan layar gerbang sekaligus', () => {
  const db = dbUji();
  try {
    const hp = buatSesi(db, 1);
    const layar = buatSesi(db, 1);
    assert.notEqual(hp, layar);
    assert.deepEqual(bacaSesi(db, hp), { penggunaId: 1 });
    assert.deepEqual(bacaSesi(db, layar), { penggunaId: 1 });
  } finally {
    db.close();
  }
});

test('⛔ sesi milik pengguna yang dihapus tidak berlaku lagi', () => {
  const db = dbUji();
  try {
    const tanda = buatSesi(db, 2);
    db.prepare('DELETE FROM pengguna WHERE id = 2').run();
    assert.equal(bacaSesi(db, tanda), undefined,
      'sesi hidup lebih lama dari akunnya: orang yang dikeluarkan masih bisa masuk');
  } finally {
    db.close();
  }
});

test('sesi untuk pengguna yang tidak ada ditolak di pintu', () => {
  const db = dbUji();
  try {
    assert.throws(() => buatSesi(db, 99), /pengguna|constraint|FOREIGN/i);
  } finally {
    db.close();
  }
});

test('bersihkanSesi membuang yang kedaluwarsa saja, bukan yang masih berlaku', () => {
  const db = dbUji();
  try {
    const baru = buatSesi(db, 2);
    const lama = buatSesi(db, 1);
    // Hanya sesi Ani yang dimajukan ke masa lalu; sesi Budi dibiarkan.
    db.prepare("UPDATE sesi SET kedaluwarsa = datetime('now', '-1 day') WHERE pengguna_id = 1").run();

    assert.equal(bersihkanSesi(db), 1, 'jumlah sesi yang dibuang salah');
    assert.equal(bacaSesi(db, lama), undefined);
    assert.deepEqual(bacaSesi(db, baru), { penggunaId: 2 }, 'sesi yang masih berlaku ikut terbuang');
  } finally {
    db.close();
  }
});

test('membuat sesi baru ikut menyapu sesi kedaluwarsa, tanpa perlu dipanggil tersendiri', () => {
  // Tanpa ini, tabel sesi tumbuh selamanya di gerbang yang tidak pernah dinyalakan ulang — dan tiap baris
  // adalah jejak siapa masuk kapan, yang menurut K71 tidak boleh disimpan lebih lama dari perlunya.
  const db = dbUji();
  try {
    buatSesi(db, 1);
    db.prepare("UPDATE sesi SET kedaluwarsa = datetime('now', '-1 day')").run();
    buatSesi(db, 2);
    assert.equal(db.prepare('SELECT count(*) AS n FROM sesi').get().n, 1,
      'sesi kedaluwarsa menumpuk: buatSesi tidak menyapu');
  } finally {
    db.close();
  }
});
