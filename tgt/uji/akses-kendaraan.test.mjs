// Uji hak akses kendaraan dan tamu (Rencana T3 Task 2).
//
// Tiap operasi diuji DUA arah untuk TIAP peran. Pagar "penghuni hanya melihat miliknya" paling mudah ditulis
// setengah: daftarnya disaring, tetapi mengambil satu butir langsung tetap lolos. Keduanya diuji di sini.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import { buatAkun, buatGrupBaru, ikutGrup, tetapkanPeran } from '../akun.mjs';
import * as akses from '../akses.mjs';

const SANDI = 'sandi-contoh-1';
const sesi = (orang) => ({ penggunaId: orang.id });

function siapkan() {
  const db = buka(':memory:');

  const bos = buatAkun(db, { nama: 'Bos Contoh', wa: '081200000001', sandi: SANDI });
  const { grup } = buatGrupBaru(db, bos.id, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });

  const pakSatpam = buatAkun(db, { nama: 'Pak Satpam', wa: '081200000002', sandi: SANDI });
  ikutGrup(db, pakSatpam.id, grup.kode_undangan);
  tetapkanPeran(db, grup.id, pakSatpam.id, 'satpam');

  const ani = buatAkun(db, { nama: 'Ani Contoh', wa: '081200000003', sandi: SANDI });
  ikutGrup(db, ani.id, grup.kode_undangan);
  const budi = buatAkun(db, { nama: 'Budi Contoh', wa: '081200000004', sandi: SANDI });
  ikutGrup(db, budi.id, grup.kode_undangan);

  const orangLuar = buatAkun(db, { nama: 'Orang Luar', wa: '081200000005', sandi: SANDI });
  buatGrupBaru(db, orangLuar.id, { nama: 'Grup Lain', jenis: 'pribadi' });

  const gerbang = akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Gate Contoh', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });

  const mobilAni = akses.tambahKendaraan(db, sesi(ani), {
    gerbangId: gerbang.id, jenis: 'mobil', merek: 'Toyota', warna: 'hitam', plat: 'L 1111 AA',
  });
  const mobilBudi = akses.tambahKendaraan(db, sesi(budi), {
    gerbangId: gerbang.id, jenis: 'pikap', plat: 'L 2222 BB',
  });

  return { db, grup, gerbang, bos, pakSatpam, ani, budi, orangLuar, mobilAni, mobilBudi };
}

// ─── Kendaraan: siapa melihat apa ───────────────────────────────────────────────────────────────────

test('penghuni yang mendaftarkan kendaraan tercatat sebagai pemiliknya, dan atas nama terisi namanya', () => {
  const { db, ani, mobilAni } = siapkan();
  try {
    assert.equal(mobilAni.pengguna_id, ani.id);
    assert.equal(mobilAni.atas_nama, 'Ani Contoh', 'atas nama diisi dari akunnya, bukan diketik ulang');
    assert.equal(mobilAni.plat, 'L1111AA');
  } finally {
    db.close();
  }
});

test('penghuni hanya melihat kendaraannya sendiri, di daftar MAUPUN saat mengambil satu butir', () => {
  const { db, ani, mobilAni, mobilBudi } = siapkan();
  try {
    assert.deepEqual(akses.kendaraanGerbang(db, sesi(ani), mobilAni.gerbang_id).map((k) => k.id), [mobilAni.id]);
    assert.equal(akses.kendaraan(db, sesi(ani), mobilAni.id).id, mobilAni.id);
    assert.throws(() => akses.kendaraan(db, sesi(ani), mobilBudi.id), /tidak ditemukan/i,
      'mengambil satu butir melewati saringan daftar');
  } finally {
    db.close();
  }
});

test('pengelola dan satpam melihat semua kendaraan di gerbangnya', () => {
  const { db, gerbang, bos, pakSatpam, mobilAni, mobilBudi } = siapkan();
  try {
    for (const orang of [bos, pakSatpam]) {
      const daftar = akses.kendaraanGerbang(db, sesi(orang), gerbang.id).map((k) => k.id).sort();
      assert.deepEqual(daftar, [mobilAni.id, mobilBudi.id].sort());
    }
  } finally {
    db.close();
  }
});

test('satpam TIDAK bisa menambah atau menghapus kendaraan', () => {
  const { db, gerbang, pakSatpam, mobilAni } = siapkan();
  try {
    assert.throws(
      () => akses.tambahKendaraan(db, sesi(pakSatpam), { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 3333 CC' }),
      /tidak berhak/i,
    );
    assert.throws(() => akses.hapusKendaraan(db, sesi(pakSatpam), mobilAni.id), /tidak berhak/i);
    assert.equal(akses.kendaraanGerbang(db, sesi(pakSatpam), gerbang.id).length, 2);
  } finally {
    db.close();
  }
});

test('penghuni tidak bisa menghapus kendaraan orang lain, tetapi bisa menghapus miliknya', () => {
  const { db, ani, mobilAni, mobilBudi } = siapkan();
  try {
    assert.throws(() => akses.hapusKendaraan(db, sesi(ani), mobilBudi.id), /tidak ditemukan/i);
    akses.hapusKendaraan(db, sesi(ani), mobilAni.id);
    assert.equal(akses.kendaraanGerbang(db, sesi(ani), mobilAni.gerbang_id).length, 0);
  } finally {
    db.close();
  }
});

test('pengelola bisa menghapus kendaraan siapa pun di grupnya', () => {
  const { db, gerbang, bos, mobilBudi } = siapkan();
  try {
    akses.hapusKendaraan(db, sesi(bos), mobilBudi.id);
    assert.equal(akses.kendaraanGerbang(db, sesi(bos), gerbang.id).length, 1);
  } finally {
    db.close();
  }
});

test('orang luar tidak melihat dan tidak bisa menambah kendaraan di gerbang grup lain', () => {
  const { db, gerbang, orangLuar, mobilAni } = siapkan();
  try {
    assert.throws(() => akses.kendaraanGerbang(db, sesi(orangLuar), gerbang.id), /tidak ditemukan/i);
    assert.throws(() => akses.kendaraan(db, sesi(orangLuar), mobilAni.id), /tidak ditemukan/i);
    assert.throws(
      () => akses.tambahKendaraan(db, sesi(orangLuar), { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 9 Z' }),
      /tidak ditemukan/i,
    );
  } finally {
    db.close();
  }
});

test('pagar versi 1 tetap berlaku lewat pintu akses: motor ditolak (K65)', () => {
  const { db, gerbang, ani, bos } = siapkan();
  try {
    for (const orang of [ani, bos]) {
      assert.throws(
        () => akses.tambahKendaraan(db, sesi(orang), { gerbangId: gerbang.id, jenis: 'motor', plat: 'L 7 M' }),
        /versi 2/i,
      );
    }
  } finally {
    db.close();
  }
});

// ─── Tamu ───────────────────────────────────────────────────────────────────────────────────────────

function undang(db, orang, gerbangId, nama, plat) {
  return akses.tambahTamu(db, sesi(orang), {
    gerbangId, nama, jenis: 'mobil', plat, lamaHari: 2, keperluan: 'rapat',
  });
}

test('tamu tercatat siapa pengundangnya, dan kodenya keluar untuk pengundang', () => {
  const { db, gerbang, ani } = siapkan();
  try {
    const tamu = undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    assert.equal(tamu.pengundang_id, ani.id);
    assert.ok(tamu.kode_undangan?.length >= 4);
    assert.equal(tamu.lama_hari, 2);
  } finally {
    db.close();
  }
});

test('penghuni hanya melihat tamu yang ia undang', () => {
  const { db, gerbang, ani, budi } = siapkan();
  try {
    const tamuAni = undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    const tamuBudi = undang(db, budi, gerbang.id, 'Tamu Budi', 'W 2222 BB');

    assert.deepEqual(akses.tamuGerbang(db, sesi(ani), gerbang.id).map((t) => t.id), [tamuAni.id]);
    assert.throws(() => akses.tamu(db, sesi(ani), tamuBudi.id), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

test('pengelola dan satpam melihat semua tamu; satpam BOLEH mengundang, tetapi hanya menghapus miliknya (K72)', () => {
  // DIBALIK, bukan dihapus. Dulu uji ini menuntut satpam ditolak 403 saat mengundang tamu, sesuai spec §4
  // yang ditulis sebelum K72. Owner mengoreksinya: satpam adalah admin TGT grupnya. Yang tetap dijaga di
  // sini adalah batas yang BARU — satpam tidak boleh menghapus tamu milik penghuni lain.
  const { db, gerbang, bos, pakSatpam, ani, budi } = siapkan();
  try {
    const tamuAni = undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    undang(db, budi, gerbang.id, 'Tamu Budi', 'W 2222 BB');

    for (const orang of [bos, pakSatpam]) {
      assert.equal(akses.tamuGerbang(db, sesi(orang), gerbang.id).length, 2);
    }
    const tamuSatpam = undang(db, pakSatpam, gerbang.id, 'Tamu Satpam', 'W 3333 CC');
    assert.equal(tamuSatpam.pengundang_id, pakSatpam.id);

    assert.throws(() => akses.hapusTamu(db, sesi(pakSatpam), tamuAni.id), /tidak berhak/i,
      'satpam tidak boleh menghapus tamu milik penghuni lain');
    akses.hapusTamu(db, sesi(pakSatpam), tamuSatpam.id);
    assert.equal(akses.tamuGerbang(db, sesi(bos), gerbang.id).length, 2);
  } finally {
    db.close();
  }
});

test('kode undangan tamu TIDAK keluar untuk yang bukan pengundangnya atau pengelola', () => {
  const { db, gerbang, bos, pakSatpam, ani } = siapkan();
  try {
    undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');

    const [untukAni] = akses.tamuGerbang(db, sesi(ani), gerbang.id);
    const [untukBos] = akses.tamuGerbang(db, sesi(bos), gerbang.id);
    const [untukSatpam] = akses.tamuGerbang(db, sesi(pakSatpam), gerbang.id);

    assert.ok(untukAni.kode_undangan, 'pengundang butuh kodenya untuk dikirim ke tamu');
    assert.ok(untukBos.kode_undangan, 'pengelola bertanggung jawab atas gerbangnya');
    assert.equal(untukSatpam.kode_undangan, undefined, 'satpam tidak perlu kode: kode itu cara masuk gerbang');
  } finally {
    db.close();
  }
});

// ─── Halaman undangan: tanpa akun, hanya seperlunya ─────────────────────────────────────────────────

test('undangan terbuka tanpa sesi dengan kode yang benar, dan hanya memuat seperlunya', () => {
  const { db, gerbang, ani } = siapkan();
  try {
    const tamu = undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    const u = akses.undangan(db, tamu.kode_undangan);

    assert.equal(u.tamu, 'Tamu Ani');
    assert.equal(u.plat, 'W1111AA');
    assert.equal(u.gerbang, 'Gate Contoh');
    assert.equal(u.alamat, 'Jl. Contoh 1');
    assert.equal(u.lama_hari, 2);
    assert.equal(u.kode, tamu.kode_undangan);

    // Yang TIDAK boleh ada: nomor WhatsApp siapa pun, id dalam basis data, daftar penghuni atau kendaraan lain.
    const teks = JSON.stringify(u);
    assert.ok(!teks.includes('6281'), 'nomor WhatsApp bocor ke halaman yang bisa dibuka siapa saja');
    assert.equal(u.pengundang_id, undefined);
    assert.equal(u.gerbang_id, undefined);
    assert.equal(u.id, undefined);
  } finally {
    db.close();
  }
});

test('undangan dengan kode salah tidak ditemukan, dan kode kosong tidak membuka apa pun', () => {
  const { db, gerbang, ani } = siapkan();
  try {
    undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    for (const kode of ['ZZZZZZ', '', null, undefined, ' ']) {
      assert.throws(() => akses.undangan(db, kode), /tidak ditemukan/i, `kode ${JSON.stringify(kode)} membuka sesuatu`);
    }
  } finally {
    db.close();
  }
});

test('undangan memakai kode undangan TAMU, bukan kode undangan GRUP', () => {
  // Keduanya enam huruf dan berasal dari kumpulan huruf yang sama: kalau tertukar, kode grup bisa dipakai
  // membuka halaman undangan, atau sebaliknya.
  const { db, grup, gerbang, ani } = siapkan();
  try {
    undang(db, ani, gerbang.id, 'Tamu Ani', 'W 1111 AA');
    assert.throws(() => akses.undangan(db, grup.kode_undangan), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});
