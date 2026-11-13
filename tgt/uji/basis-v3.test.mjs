// Uji migrasi skema versi 3: putusan gerbang pada kejadian (Rencana T4).
//
// Berbeda dengan versi 2 yang belum pernah jalan di luar uji, versi 2 sekarang SUDAH tersimpan di commit, jadi
// kolom baru masuk sebagai versi 3 tersendiri — bukan disisipkan ke versi 2.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { VERSI_SKEMA, buka, bukaVersi, versi, naik, turun, susunan } from '../basis.mjs';

test('versi 3 masih bisa dipasang sendiri, walau skema terbaru sudah lebih tinggi', () => {
  // DIBALIK, bukan dihapus — sama seperti yang dilakukan pada uji versi 2. Ditulis begini supaya TIDAK perlu
  // diubah lagi tiap versi baru: yang dijaga adalah "langkah versi 3 tetap bisa dipasang terpisah", dan itu
  // tetap benar selamanya. Basis data pelanggan yang tertinggal harus bisa dinaikkan bertahap.
  assert.ok(VERSI_SKEMA >= 3, 'versi skema tidak boleh turun di bawah 3');
  const db = bukaVersi(':memory:', 3);
  try {
    assert.equal(versi(db), 3);
    assert.ok(new Set(susunan(db)).has('kejadian.penanda'));
  } finally {
    db.close();
  }
});

test('kolom putusan gerbang ada di kejadian', () => {
  const db = buka(':memory:');
  try {
    const punya = new Set(susunan(db));
    for (const kolom of ['kejadian.penanda', 'kejadian.putusan', 'kejadian.alasan', 'kejadian.dibuka_oleh']) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada di skema versi 3`);
    }
  } finally {
    db.close();
  }
});

test('basis versi 2 yang SUDAH BERISI DATA naik ke versi 3 tanpa kehilangan apa pun', () => {
  const db = bukaVersi(':memory:', 2);
  try {
    assert.equal(versi(db), 2);
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'AB12CD')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gate Contoh', 'kantor', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare("INSERT INTO kejadian (gerbang_id, waktu, arah, plat) VALUES (1, '2026-10-26T08:00:00', 'masuk', 'L9999QQ')").run();
    db.prepare("INSERT INTO pengguna (nama, wa, sandi_hash) VALUES ('Aldy Contoh', '628100000001', 'x')").run();

    // Sengaja berhenti di versi 3: yang diuji di sini hanya langkah 2 → 3.
    naik(db, 3);

    assert.equal(versi(db), 3);
    assert.equal(db.prepare('SELECT plat FROM kejadian WHERE id = 1').get().plat, 'L9999QQ');
    assert.equal(db.prepare('SELECT putusan FROM kejadian WHERE id = 1').get().putusan, null,
      'kejadian lama tidak punya putusan, dan itu bukan galat');
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 1);
  } finally {
    db.close();
  }
});

test('turun dari 3 ke 2 mencabut kolom baru tetapi menyisakan kejadiannya', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'EF34GH')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gate Contoh', 'kantor', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare(
      `INSERT INTO kejadian (gerbang_id, waktu, arah, plat, putusan, alasan, penanda)
       VALUES (1, '2026-10-26T08:00:00', 'masuk', 'L1111AA', 'buka', 'terdaftar', 'kotak-1')`,
    ).run();

    turun(db, 2);

    assert.equal(versi(db), 2);
    assert.equal(db.prepare('SELECT plat FROM kejadian WHERE id = 1').get().plat, 'L1111AA');
    const punya = new Set(susunan(db));
    assert.ok(!punya.has('kejadian.putusan'), 'kolom putusan harus tercabut');
    assert.ok(!punya.has('kejadian.penanda'));
    assert.ok(punya.has('pengguna.wa'), 'tabel versi 2 harus tetap ada');
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

test('penanda kejadian unik: kotak gerbang tidak bisa menggandakan catatan', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'IJ56KL')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gate Contoh', 'kantor', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    const sisip = db.prepare(
      "INSERT INTO kejadian (gerbang_id, waktu, arah, plat, penanda) VALUES (1, '2026-10-26T08:00:00', 'masuk', 'L1A', ?)",
    );
    sisip.run('kotak-1-abc');
    assert.throws(() => sisip.run('kotak-1-abc'), /UNIQUE|constraint/i);

    // Penanda kosong boleh berulang: kejadian lama dan kejadian yang dibuat tangan tidak punya penanda.
    const tanpa = db.prepare(
      "INSERT INTO kejadian (gerbang_id, waktu, arah, plat) VALUES (1, '2026-10-26T09:00:00', 'masuk', 'L2B')",
    );
    tanpa.run();
    tanpa.run();
    assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 3);
  } finally {
    db.close();
  }
});
