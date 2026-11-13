// Uji langganan notifikasi: siapa boleh berlangganan, dan siapa yang diberi tahu (Rencana T5 Task 4, K72).
//
// Semua alamat perangkat di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka, bukaVersi, versi, naik, turun, susunan, VERSI_SKEMA } from '../basis.mjs';
import { mintaOtp, masukDenganOtp } from '../akun.mjs';
import * as akses from '../akses.mjs';

const sesi = (orang) => ({ penggunaId: orang.id });

function akunBaru(db, email, nama) {
  let kode;
  mintaOtp(db, { email, kirim: (_e, k) => { kode = k; } });
  return masukDenganOtp(db, { email, kode, nama });
}

function siapkan() {
  const db = buka(':memory:');
  const bos = akunBaru(db, 'bos@example.test', 'Bos Contoh');
  const { grup } = akses.buatGrup(db, sesi(bos), { nama: 'RT 05 Contoh', jenis: 'pribadi' });

  const pakSatpam = akunBaru(db, 'satpam@example.test', 'Pak Satpam');
  akses.ikutGrup(db, sesi(pakSatpam), grup.kode_undangan);
  akses.tetapkanPeran(db, sesi(bos), grup.id, pakSatpam.id, 'satpam');

  const ani = akunBaru(db, 'ani@example.test', 'Ani Contoh');
  akses.ikutGrup(db, sesi(ani), grup.kode_undangan);

  const orangLuar = akunBaru(db, 'luar@example.test', 'Orang Luar');
  akses.buatGrup(db, sesi(orangLuar), { nama: 'Grup Lain', jenis: 'pribadi' });

  const gerbang = akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Gerbang Depan', jenisLokasi: 'perumahan', alamat: 'Jl. Contoh 1', kota: 'Sidoarjo',
  });
  return { db, grup, gerbang, bos, pakSatpam, ani, orangLuar };
}

const PERANGKAT = (n = 1) => ({
  alamat: `https://contoh.test/push/perangkat-${n}`,
  kunci: `kunci-umum-palsu-${n}`,
  rahasia: `rahasia-palsu-${n}`,
});

// ─── Migrasi versi 5 ────────────────────────────────────────────────────────────────────────────────

test('versi 5 masih bisa dipasang sendiri, dan tabel langganan ada', () => {
  // DIBALIK, bukan dihapus (Rencana T8): dulu ia menuntut `VERSI_SKEMA === 5`, dan itu menjadi salah begitu
  // versi 6 lahir. Bentuknya disamakan dengan uji versi 2, 3, dan 4, supaya tidak perlu diubah lagi.
  assert.ok(VERSI_SKEMA >= 5, 'versi skema tidak boleh turun di bawah 5');
  const db = bukaVersi(':memory:', 5);
  try {
    assert.equal(versi(db), 5);
    const punya = new Set(susunan(db));
    for (const kolom of ['langganan.pengguna_id', 'langganan.grup_id', 'langganan.alamat', 'langganan.kunci']) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada`);
    }
  } finally {
    db.close();
  }
});

test('basis versi 4 berisi data naik ke versi 5 tanpa kehilangan apa pun, dan bolak-balik utuh', () => {
  const db = bukaVersi(':memory:', 4);
  try {
    db.prepare("INSERT INTO pengguna (nama, email) VALUES ('Ani', 'ani@example.test')").run();
    // Sengaja berhenti di 5: yang diuji di sini hanya langkah 4 → 5.
    naik(db, 5);
    assert.equal(versi(db), 5);
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 1);

    const sesudahNaik = susunan(db);
    turun(db, 4);
    assert.ok(!new Set(susunan(db)).has('langganan.alamat'));
    naik(db, 5);
    assert.deepEqual(susunan(db), sesudahNaik);
  } finally {
    db.close();
  }
});

// ─── Siapa boleh berlangganan ───────────────────────────────────────────────────────────────────────

test('satpam dan pengelola boleh berlangganan notifikasi grupnya', () => {
  const { db, grup, bos, pakSatpam } = siapkan();
  try {
    assert.ok(akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1)).id);
    assert.ok(akses.berlangganan(db, sesi(bos), grup.id, PERANGKAT(2)).id);
  } finally {
    db.close();
  }
});

test('penghuni TIDAK boleh berlangganan: catatan gerbang bukan untuk sesama penghuni', () => {
  const { db, grup, ani } = siapkan();
  try {
    assert.throws(() => akses.berlangganan(db, sesi(ani), grup.id, PERANGKAT(3)), /tidak berhak/i);
  } finally {
    db.close();
  }
});

test('orang luar tidak boleh berlangganan grup ini', () => {
  const { db, grup, orangLuar } = siapkan();
  try {
    assert.throws(() => akses.berlangganan(db, sesi(orangLuar), grup.id, PERANGKAT(4)), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

test('⛔ perangkat yang sama berlangganan dua kali tidak menerima dua kali', () => {
  const { db, grup, pakSatpam } = siapkan();
  try {
    akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1));
    akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1));
    assert.equal(akses.langgananGrup(db, grup.id).length, 1, 'satu perangkat tercatat dua kali');
  } finally {
    db.close();
  }
});

test('berhenti berlangganan menghapus perangkat itu saja', () => {
  const { db, grup, bos, pakSatpam } = siapkan();
  try {
    akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1));
    akses.berlangganan(db, sesi(bos), grup.id, PERANGKAT(2));
    akses.berhentiLangganan(db, sesi(pakSatpam), PERANGKAT(1).alamat);
    assert.deepEqual(akses.langgananGrup(db, grup.id).map((l) => l.alamat), [PERANGKAT(2).alamat]);
  } finally {
    db.close();
  }
});

test('langganan yang isinya tidak lengkap ditolak', () => {
  const { db, grup, pakSatpam } = siapkan();
  try {
    for (const p of [{}, { alamat: 'x' }, { alamat: '', kunci: 'a', rahasia: 'b' }, null]) {
      assert.throws(() => akses.berlangganan(db, sesi(pakSatpam), grup.id, p), /langganan|alamat|kunci/i);
    }
  } finally {
    db.close();
  }
});

// ─── Siapa yang diberi tahu ─────────────────────────────────────────────────────────────────────────

test('⛔ langganan grup lain TIDAK ikut diberi tahu', () => {
  const { db, grup, pakSatpam, orangLuar } = siapkan();
  try {
    const grupLain = akses.grupSaya(db, sesi(orangLuar))[0];
    akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1));
    akses.berlangganan(db, sesi(orangLuar), grupLain.id, PERANGKAT(9));

    const daftar = akses.langgananGrup(db, grup.id);
    assert.equal(daftar.length, 1);
    assert.equal(daftar[0].alamat, PERANGKAT(1).alamat);
  } finally {
    db.close();
  }
});

test('kejadian janggal menghasilkan daftar penerima; kejadian wajar tidak', () => {
  const { db, grup, gerbang, pakSatpam, ani } = siapkan();
  try {
    akses.berlangganan(db, sesi(pakSatpam), grup.id, PERANGKAT(1));
    akses.tambahKendaraan(db, sesi(ani), { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB' });

    const wajar = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00',
    });
    assert.equal(wajar.notifikasi, null, 'kendaraan yang lewat wajar tidak boleh memberi notifikasi');

    const asing = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'N9999XX', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:05:00',
    });
    assert.ok(asing.notifikasi, 'plat tak dikenal harus memberi notifikasi');
    assert.equal(asing.notifikasi.penerima.length, 1);
    assert.match(asing.notifikasi.judul + asing.notifikasi.pesan, /N9999XX/);
  } finally {
    db.close();
  }
});

test('tanpa ada yang berlangganan, kejadian janggal tetap tercatat dan tidak gagal', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'N9999XX', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:05:00',
    });
    assert.ok(h.kejadian.id);
    assert.equal(h.notifikasi.penerima.length, 0);
  } finally {
    db.close();
  }
});
