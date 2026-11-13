// Uji daftar izin, status kendaraan, dan jalur bacaan gerbang (Rencana T4 Task 2).
//
// Semua plat di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import { buatAkun, buatGrupBaru, ikutGrup, tetapkanPeran } from '../akun.mjs';
import * as akses from '../akses.mjs';
import { PUTUSAN } from '../putusan.mjs';

const SANDI = 'sandi-contoh-1';
const sesi = (orang) => ({ penggunaId: orang.id });

function siapkan({ jenisLokasi = 'kantor' } = {}) {
  const db = buka(':memory:');
  const bos = buatAkun(db, { nama: 'Bos Contoh', wa: '081200000001', sandi: SANDI });
  const { grup } = buatGrupBaru(db, bos.id, { nama: 'PT Contoh', jenis: 'perusahaan' });

  const pakSatpam = buatAkun(db, { nama: 'Pak Satpam', wa: '081200000002', sandi: SANDI });
  ikutGrup(db, pakSatpam.id, grup.kode_undangan);
  tetapkanPeran(db, grup.id, pakSatpam.id, 'satpam');

  const ani = buatAkun(db, { nama: 'Ani Contoh', wa: '081200000003', sandi: SANDI });
  ikutGrup(db, ani.id, grup.kode_undangan);

  const orangLuar = buatAkun(db, { nama: 'Orang Luar', wa: '081200000009', sandi: SANDI });
  buatGrupBaru(db, orangLuar.id, { nama: 'Grup Lain', jenis: 'pribadi' });

  const gerbang = akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Gate Contoh', jenisLokasi, alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });
  akses.tambahKendaraan(db, sesi(ani), { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB' });
  akses.tambahTamu(db, sesi(ani), {
    gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'pikap', plat: 'W 1111 ZZ', lamaHari: 1,
  });

  return { db, grup, gerbang, bos, pakSatpam, ani, orangLuar };
}

// ─── Daftar izin ────────────────────────────────────────────────────────────────────────────────────

test('daftar izin memuat kendaraan penghuni dan tamu, beserta jenis dan statusnya', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const izin = akses.daftarIzin(db, sesi(pakSatpam), gerbang.id);
    const peta = Object.fromEntries(izin.map((i) => [i.plat, i]));
    assert.deepEqual(Object.keys(peta).sort(), ['L1234AB', 'W1111ZZ']);
    assert.equal(peta.L1234AB.jenis, 'penghuni');
    assert.equal(peta.W1111ZZ.jenis, 'tamu');
    assert.equal(peta.L1234AB.status, 'di_luar', 'yang belum pernah masuk dianggap di luar');
  } finally {
    db.close();
  }
});

test('daftar izin TIDAK memuat nama orang atau nomor WhatsApp', () => {
  // Daftar ini disalin ke kotak di gerbang untuk dipakai luring. Ia hanya perlu plat, jenis, dan status.
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const teks = JSON.stringify(akses.daftarIzin(db, sesi(pakSatpam), gerbang.id));
    assert.ok(!teks.includes('Ani Contoh'), 'nama penghuni ikut tersalin ke kotak gerbang');
    assert.ok(!teks.includes('6281'), 'nomor WhatsApp ikut tersalin ke kotak gerbang');
  } finally {
    db.close();
  }
});

test('daftar izin hanya untuk satpam dan pengelola', () => {
  const { db, gerbang, bos, pakSatpam, ani, orangLuar } = siapkan();
  try {
    assert.equal(akses.daftarIzin(db, sesi(bos), gerbang.id).length, 2);
    assert.equal(akses.daftarIzin(db, sesi(pakSatpam), gerbang.id).length, 2);
    assert.throws(() => akses.daftarIzin(db, sesi(ani), gerbang.id), /tidak berhak/i);
    assert.throws(() => akses.daftarIzin(db, sesi(orangLuar), gerbang.id), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

test('status berubah mengikuti kejadian terakhir', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00',
    });
    const sesudahMasuk = akses.daftarIzin(db, sesi(pakSatpam), gerbang.id).find((i) => i.plat === 'L1234AB');
    assert.equal(sesudahMasuk.status, 'di_dalam');

    akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'keluar', waktu: '2026-10-26T17:00:00',
    });
    const sesudahKeluar = akses.daftarIzin(db, sesi(pakSatpam), gerbang.id).find((i) => i.plat === 'L1234AB');
    assert.equal(sesudahKeluar.status, 'di_luar');
  } finally {
    db.close();
  }
});

// ─── Bacaan gerbang ─────────────────────────────────────────────────────────────────────────────────

test('bacaan gerbang mengembalikan putusan beserta alasannya, dan kejadiannya tercatat', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00',
      yakin: 0.93, ciriJenis: 'mobil', ciriWarna: 'hitam',
    });
    assert.equal(h.putusan, PUTUSAN.BUKA);
    assert.ok(h.alasan);
    assert.equal(h.kejadian.plat, 'L1234AB');
    assert.equal(h.kejadian.putusan, 'buka');
    assert.equal(h.kejadian.ciri_jenis, 'mobil', 'ciri dicatat (K63)');
  } finally {
    db.close();
  }
});

test('bacaan yang tidak dikenal tetap dicatat, dengan putusan tidak dikenal', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'N9999XX', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:05:00',
    });
    assert.equal(h.putusan, PUTUSAN.TIDAK_DIKENAL);
    assert.equal(akses.kejadianTerbaru(db, sesi(pakSatpam), gerbang.id).length, 1);
  } finally {
    db.close();
  }
});

test('⛔ penanda yang sama dikirim dua kali TIDAK menggandakan catatan', () => {
  // Inilah yang membuat penyusulan data sesudah luring aman: kotak gerbang boleh mengirim ulang.
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const kirim = () => akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk',
      waktu: '2026-10-26T08:00:00', penanda: 'kotak-1-abc',
    });
    const pertama = kirim();
    const kedua = kirim();

    assert.equal(akses.kejadianTerbaru(db, sesi(pakSatpam), gerbang.id).length, 1);
    assert.equal(kedua.kejadian.id, pertama.kejadian.id, 'kejadian yang sama harus dikembalikan, bukan dibuat ulang');
    assert.equal(kedua.sudahAda, true);
  } finally {
    db.close();
  }
});

test('bacaan ragu lebih dari dua posisi tidak pernah berputusan buka, dan tetap dicatat', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [0, 1, 2], arah: 'masuk', waktu: '2026-10-26T08:10:00',
    });
    assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
    assert.equal(akses.kejadianTerbaru(db, sesi(pakSatpam), gerbang.id)[0].putusan, 'panggil_satpam');
  } finally {
    db.close();
  }
});

test('tamu terdaftar langsung masuk di gerbang perumahan (K72)', () => {
  // DIBALIK, bukan dihapus. Dulu uji ini menuntut satpam dipanggil untuk tamu di perumahan, sesuai bacaan
  // agen atas K46. Owner mengoreksinya 26 Okt: tamu bisa langsung masuk lewat gerbang depan perumahan.
  const { db, gerbang, pakSatpam } = siapkan({ jenisLokasi: 'perumahan' });
  try {
    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'W1111ZZ', ragu: [4], arah: 'masuk', waktu: '2026-10-26T08:15:00',
    });
    assert.equal(h.putusan, PUTUSAN.BUKA);
  } finally {
    db.close();
  }
});

test('penghuni dan orang luar tidak boleh mengirim bacaan gerbang', () => {
  const { db, gerbang, ani, orangLuar } = siapkan();
  try {
    const kirim = (orang) => akses.bacaanGerbang(db, sesi(orang), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00',
    });
    assert.throws(() => kirim(ani), /tidak berhak/i);
    assert.throws(() => kirim(orangLuar), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

// ─── Buka manual ────────────────────────────────────────────────────────────────────────────────────

test('satpam boleh membuka dengan tangan, dan itu tercatat sebagai dibuka satpam', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const h = akses.bukaManual(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, plat: 'N 9999 XX', arah: 'masuk', alasan: 'tamu dadakan, diperiksa satpam',
      waktu: '2026-10-26T08:20:00',
    });
    assert.equal(h.putusan, 'dibuka_satpam', 'putusan manusia tidak boleh tercatat sebagai putusan mesin');
    assert.equal(h.dibuka_oleh, pakSatpam.id);
    assert.match(h.alasan, /tamu dadakan/);
  } finally {
    db.close();
  }
});

test('penghuni tidak boleh membuka gerbang dengan tangan', () => {
  const { db, gerbang, ani } = siapkan();
  try {
    assert.throws(
      () => akses.bukaManual(db, sesi(ani), { gerbangId: gerbang.id, plat: 'N 1 A', arah: 'masuk', alasan: 'coba' }),
      /tidak berhak/i,
    );
  } finally {
    db.close();
  }
});

test('buka manual wajib menyertakan alasan: satpam harus mempertanggungjawabkannya', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    for (const alasan of ['', '   ', undefined]) {
      assert.throws(
        () => akses.bukaManual(db, sesi(pakSatpam), { gerbangId: gerbang.id, plat: 'N 1 A', arah: 'masuk', alasan }),
        /alasan/i,
      );
    }
  } finally {
    db.close();
  }
});

// ─── Kejadian terbaru ───────────────────────────────────────────────────────────────────────────────

test('kejadian terbaru diurutkan dari yang paling baru, dan dibatasi jumlahnya', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    for (const jam of ['08:00', '09:00', '10:00']) {
      akses.bacaanGerbang(db, sesi(pakSatpam), {
        gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: `2026-10-26T${jam}:00`,
      });
    }
    const semua = akses.kejadianTerbaru(db, sesi(pakSatpam), gerbang.id);
    assert.equal(semua[0].waktu, '2026-10-26T10:00:00', 'yang terbaru di atas');
    assert.equal(akses.kejadianTerbaru(db, sesi(pakSatpam), gerbang.id, 2).length, 2);
  } finally {
    db.close();
  }
});

test('penghuni tidak melihat lalu lalang seluruh gerbang', () => {
  // Catatan kejadian memuat plat semua orang: itu bukan untuk dibaca sesama penghuni.
  const { db, gerbang, ani } = siapkan();
  try {
    assert.throws(() => akses.kejadianTerbaru(db, sesi(ani), gerbang.id), /tidak berhak/i);
  } finally {
    db.close();
  }
});

// ─── Jenis dari kamera, lewat jalur gerbang (Rencana T6) ────────────────────────────────────────────

test('RANTAI: jenis yang tidak cocok memberi notifikasi, TETAPI gerbang tetap dibuka', () => {
  const { db, grup, gerbang, pakSatpam } = siapkan();
  try {
    akses.berlangganan(db, sesi(pakSatpam), grup.id, {
      alamat: 'https://contoh.test/push/1', kunci: 'k', rahasia: 'r',
    });

    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk',
      waktu: '2026-10-26T08:00:00', ciriJenis: 'truk',
    });

    assert.equal(h.putusan, PUTUSAN.BUKA, 'ciri tidak boleh menahan gerbang (K55)');
    assert.equal(h.ciriJanggal, true);
    assert.ok(h.notifikasi, 'satpam harus diberi tahu');
    assert.match(h.notifikasi.judul, /jenis/i);
    assert.equal(h.kejadian.ciri_jenis, 'truk', 'jenis yang terbaca tetap dicatat (K63)');
  } finally {
    db.close();
  }
});

test('RANTAI: jenis yang COCOK tidak memberi notifikasi sama sekali', () => {
  const { db, grup, gerbang, pakSatpam } = siapkan();
  try {
    akses.berlangganan(db, sesi(pakSatpam), grup.id, {
      alamat: 'https://contoh.test/push/1', kunci: 'k', rahasia: 'r',
    });

    const h = akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk',
      waktu: '2026-10-26T08:00:00', ciriJenis: 'mobil',
    });
    assert.equal(h.putusan, PUTUSAN.BUKA);
    assert.equal(h.ciriJanggal, false);
    assert.equal(h.notifikasi, null);
  } finally {
    db.close();
  }
});

test('RANTAI: satu bacaan kamera menyalakan status kendaraan dari di luar menjadi di dalam', () => {
  // Inilah "mentriger status" yang diminta owner: satu gambar dari kamera mengubah keadaan gerbang.
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const sebelum = akses.daftarIzin(db, sesi(pakSatpam), gerbang.id).find((i) => i.plat === 'L1234AB');
    assert.equal(sebelum.status, 'di_luar');

    akses.bacaanGerbang(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, bacaan: 'L1234AB', ragu: [], arah: 'masuk',
      waktu: '2026-10-26T08:00:00', ciriJenis: 'mobil',
    });

    const sesudah = akses.daftarIzin(db, sesi(pakSatpam), gerbang.id).find((i) => i.plat === 'L1234AB');
    assert.equal(sesudah.status, 'di_dalam', 'status tidak berubah setelah kendaraan masuk');
  } finally {
    db.close();
  }
});

// ─── Dashboard (Rencana T7) ─────────────────────────────────────────────────────────────────────────

function lewat(db, orang, gerbang, plat, arah, waktu) {
  return akses.bacaanGerbang(db, sesi(orang), { gerbangId: gerbang.id, bacaan: plat, ragu: [], arah, waktu });
}

test('ubin beranda: di dalam sekarang, masuk hari ini, keluar hari ini, lewat batas', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const hariIni = new Date().toISOString().slice(0, 10);
    const jam = (j) => `${hariIni}T${String(j).padStart(2, '0')}:00:00`;

    lewat(db, pakSatpam, gerbang, 'L1234AB', 'masuk', jam(7));     // penghuni masuk, masih di dalam
    lewat(db, pakSatpam, gerbang, 'W1111ZZ', 'masuk', jam(8));     // tamu masuk, masih di dalam
    lewat(db, pakSatpam, gerbang, 'L1234AB', 'keluar', jam(17));   // lalu keluar

    const u = akses.ubinBeranda(db, sesi(pakSatpam), gerbang.id, hariIni);
    assert.equal(u.masukHariIni, 2);
    assert.equal(u.keluarHariIni, 1);
    assert.equal(u.diDalam, 1, 'yang masuk lalu keluar tidak boleh dihitung masih di dalam');
    assert.equal(u.lewatBatas, 0);
  } finally {
    db.close();
  }
});

test('ubin beranda menghitung tamu yang lewat batas', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    // Tamu lama_hari 1, masuk 5 hari lalu, keluar hari ini: lewat batas.
    const lalu = new Date(Date.now() - 5 * 86400000).toISOString().slice(0, 10);
    const hariIni = new Date().toISOString().slice(0, 10);
    lewat(db, pakSatpam, gerbang, 'W1111ZZ', 'masuk', `${lalu}T08:00:00`);
    lewat(db, pakSatpam, gerbang, 'W1111ZZ', 'keluar', `${hariIni}T08:00:00`);

    assert.equal(akses.ubinBeranda(db, sesi(pakSatpam), gerbang.id, hariIni).lewatBatas, 1);
  } finally {
    db.close();
  }
});

test('ubin beranda pada gerbang yang belum pernah dilewati memberi nol, bukan galat', () => {
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const u = akses.ubinBeranda(db, sesi(pakSatpam), gerbang.id, '2026-10-26');
    assert.deepEqual(u, { diDalam: 0, masukHariIni: 0, keluarHariIni: 0, lewatBatas: 0 });
  } finally {
    db.close();
  }
});

test('ringkasan jam dan ubin hanya untuk satpam dan pengelola', () => {
  const { db, gerbang, bos, pakSatpam, ani, orangLuar } = siapkan();
  try {
    assert.equal(akses.ringkasanJam(db, sesi(bos), gerbang.id, '2026-10-26').length, 24);
    assert.equal(akses.ringkasanJam(db, sesi(pakSatpam), gerbang.id, '2026-10-26').length, 24);
    assert.throws(() => akses.ringkasanJam(db, sesi(ani), gerbang.id, '2026-10-26'), /tidak berhak/i);
    assert.throws(() => akses.ubinBeranda(db, sesi(ani), gerbang.id, '2026-10-26'), /tidak berhak/i);
    assert.throws(() => akses.ubinBeranda(db, sesi(orangLuar), gerbang.id, '2026-10-26'), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

test('⛔ angka dashboard hanya milik gerbang yang diminta', () => {
  const { db, grup, gerbang, bos, pakSatpam } = siapkan();
  try {
    const lain = akses.buatGerbang(db, sesi(bos), {
      grupId: grup.id, nama: 'Gate Lain', jenisLokasi: 'kantor', alamat: 'Jl. Lain 2', kota: 'Surabaya',
    });
    const hariIni = new Date().toISOString().slice(0, 10);
    lewat(db, pakSatpam, gerbang, 'L1234AB', 'masuk', `${hariIni}T07:00:00`);

    assert.equal(akses.ubinBeranda(db, sesi(pakSatpam), lain.id, hariIni).masukHariIni, 0);
    assert.equal(akses.ringkasanJam(db, sesi(pakSatpam), lain.id, hariIni)[7].masuk, 0);
  } finally {
    db.close();
  }
});
