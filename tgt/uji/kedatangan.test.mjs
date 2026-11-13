// Uji "satu kendaraan = satu kedatangan" (Rencana T9, persetujuan owner 26 Okt: jendela 20 detik).
//
// ⛔ CACAT YANG DIPERBAIKI, dan kenapa ia lolos selama enam rencana.
// Kamera gerbang menghasilkan belasan bingkai per kendaraan. Semua uji TGT sebelum ini mengirim SATU bacaan
// per kendaraan, jadi tidak ada yang pernah menyentuh keadaan ini. Probe 26 Okt memperlihatkan akibatnya:
// satu mobil penghuni keluar, dan bingkai KEDUA menjadi `panggil_satpam` — gerbang ditahan untuk penghuni yang
// tidak bersalah. Di perumahan 150 mobil sehari, itu 150 panggilan palsu per hari.
//
// Aturan K73 (janggal saat keluar menahan gerbang) TIDAK salah. Yang salah adalah TGT belum punya pengertian
// "satu kedatangan", padahal mesin baca di lab sudah punya.
//
// Semua plat KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { VERSI_SKEMA, buka, bukaVersi, versi, naik, turun, susunan } from '../basis.mjs';
import {
  JENDELA_KEDATANGAN_DETIK, jendelaKedatangan,
  buatGrup, buatGerbang, daftarkanKendaraan, catatKejadian, ubinBeranda, ringkasanJam,
} from '../layanan.mjs';
import * as akses from '../akses.mjs';
import { mintaOtp, masukDenganOtp } from '../akun.mjs';

const dua = (x) => String(x).padStart(2, '0');
const HARI = (() => {
  const t = new Date();
  return `${t.getFullYear()}-${dua(t.getMonth() + 1)}-${dua(t.getDate())}`;
})();
const jam = (menit, detik = 0) => `${HARI}T08:${dua(menit)}:${dua(detik)}`;

function siapkan() {
  const db = buka(':memory:');
  const grup = buatGrup(db, { nama: 'PT Contoh', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id, nama: 'Gate Satu', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });
  const gerbangDua = buatGerbang(db, {
    grupId: grup.id, nama: 'Gate Dua', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 2', kota: 'Surabaya',
  });
  daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L1234AB', atasNama: 'Penghuni Satu' });
  return { db, gerbang, gerbangDua };
}

const bacaan = (db, gerbangId, plat, arah, waktu) =>
  catatKejadian(db, { gerbangId, waktu, arah, plat, yakin: 0.95 });

// ─── Skema versi 7 ──────────────────────────────────────────────────────────────────────────────────

test('versi 6 masih bisa dipasang sendiri, walau skema terbaru sudah lebih tinggi', () => {
  assert.ok(VERSI_SKEMA >= 7, 'versi skema tidak boleh turun di bawah 7');
  const db = bukaVersi(':memory:', 6);
  try {
    assert.equal(versi(db), 6);
    assert.ok(!new Set(susunan(db)).has('kejadian.kedatangan_id'),
      'kolom kedatangan_id seharusnya belum ada di versi 6');
  } finally {
    db.close();
  }
});

test('⛔ basis versi 6 BERISI DATA naik ke versi 7, dan kejadian lama ikut punya kedatangan', () => {
  const db = bukaVersi(':memory:', 6);
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'AB12CD')").run();
    db.prepare(
      `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, status)
       VALUES (1, 'Gate', 'kantor', 'Jl. Contoh 1', 'Surabaya', 'aktif')`,
    ).run();
    db.prepare(
      "INSERT INTO kejadian (gerbang_id, waktu, arah, plat) VALUES (1, ?, 'masuk', 'L9999ZZ')",
    ).run(jam(0));

    naik(db, 7);
    assert.equal(versi(db), 7);
    assert.ok(new Set(susunan(db)).has('kejadian.kedatangan_id'));

    // Kejadian lama tidak boleh kehilangan apa pun, dan tiap kejadian lama adalah kedatangannya sendiri:
    // menebak pengelompokan kejadian lama akan mengarang data yang tidak pernah ada.
    const k = db.prepare('SELECT id, plat, kedatangan_id FROM kejadian').get();
    assert.equal(k.plat, 'L9999ZZ');
    assert.equal(k.kedatangan_id, k.id, 'kejadian lama tidak ditautkan ke kedatangannya sendiri');
  } finally {
    db.close();
  }
});

test('migrasi versi 7 bolak-balik menghasilkan susunan yang sama', () => {
  const db = buka(':memory:');
  try {
    const sebelum = susunan(db);
    turun(db, 6);
    assert.ok(!new Set(susunan(db)).has('kejadian.kedatangan_id'));
    naik(db);
    assert.deepEqual(susunan(db), sebelum);
    turun(db, 0);
    assert.equal(susunan(db).length, 0);
    naik(db);
    assert.deepEqual(susunan(db), sebelum);
  } finally {
    db.close();
  }
});

// ─── Pengelompokan ──────────────────────────────────────────────────────────────────────────────────

test('⛔ bingkai berurutan atas plat yang sama menjadi SATU kedatangan', () => {
  const { db, gerbang } = siapkan();
  try {
    const pertama = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    assert.equal(pertama.kedatangan_id, pertama.id, 'bingkai pertama harus menjadi kedatangannya sendiri');
    assert.equal(pertama.ulangan, false);

    for (const detik of [1, 5, 19]) {
      const lanjut = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, detik));
      assert.equal(lanjut.kedatangan_id, pertama.id, `bingkai pada detik ${detik} menjadi kedatangan baru`);
      assert.equal(lanjut.ulangan, true, `bingkai pada detik ${detik} tidak ditandai ulangan`);
    }

    // SEMUA bacaan tetap tersimpan (K74): yang berubah hanya pengelompokannya.
    assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 4,
      'ada bacaan yang dibuang; K74 menuntut semuanya disimpan');
    assert.equal(db.prepare('SELECT count(DISTINCT kedatangan_id) AS n FROM kejadian').get().n, 1);
  } finally {
    db.close();
  }
});

test('bacaan di LUAR jendela menjadi kedatangan baru', () => {
  const { db, gerbang } = siapkan();
  try {
    const pertama = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    const jauh = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 21));
    assert.equal(jauh.kedatangan_id, jauh.id, 'bacaan 21 detik kemudian seharusnya kedatangan baru');
    assert.equal(jauh.ulangan, false);
    assert.notEqual(jauh.kedatangan_id, pertama.id);
  } finally {
    db.close();
  }
});

test('⛔ ARAH yang berbeda SELALU kedatangan baru, walau dalam jendela', () => {
  // Masuk lalu keluar dua detik kemudian memang aneh, tetapi itu dua peristiwa yang berbeda dan keduanya
  // harus tercatat sebagai kedatangan tersendiri. Menggabungkannya akan menyembunyikan kendaraan yang
  // berputar di gerbang.
  const { db, gerbang } = siapkan();
  try {
    const masuk = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    const keluar = bacaan(db, gerbang.id, 'L1234AB', 'keluar', jam(0, 2));
    assert.equal(keluar.kedatangan_id, keluar.id);
    assert.notEqual(keluar.kedatangan_id, masuk.kedatangan_id);
  } finally {
    db.close();
  }
});

test('plat yang berbeda tidak pernah digabung', () => {
  const { db, gerbang } = siapkan();
  try {
    const satu = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    const dualah = bacaan(db, gerbang.id, 'L5678CD', 'masuk', jam(0, 1));
    assert.notEqual(dualah.kedatangan_id, satu.kedatangan_id);
    assert.equal(dualah.ulangan, false);
  } finally {
    db.close();
  }
});

test('⛔ GERBANG yang berbeda tidak pernah digabung', () => {
  // Mobil yang sama bisa lewat dua gerbang milik satu grup dalam beberapa detik. Keduanya kedatangan nyata.
  const { db, gerbang, gerbangDua } = siapkan();
  try {
    const satu = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    const lain = bacaan(db, gerbangDua.id, 'L1234AB', 'masuk', jam(0, 1));
    assert.notEqual(lain.kedatangan_id, satu.kedatangan_id);
  } finally {
    db.close();
  }
});

test('bacaan TANPA PLAT tidak digabung — batas yang disengaja', () => {
  // Menggabung dari waktu saja bisa menyatukan dua kendaraan tak dikenal yang berbeda, dan itu lebih buruk
  // daripada dua baris catatan. Ini tidak menahan gerbang dan tidak memanggil satpam palsu.
  const { db, gerbang } = siapkan();
  try {
    const a = catatKejadian(db, { gerbangId: gerbang.id, waktu: jam(0, 0), arah: 'masuk', plat: null });
    const b = catatKejadian(db, { gerbangId: gerbang.id, waktu: jam(0, 1), arah: 'masuk', plat: null });
    assert.equal(a.kedatangan_id, a.id);
    assert.equal(b.kedatangan_id, b.id, 'bacaan tanpa plat digabung: dua kendaraan tak dikenal bisa menyatu');
  } finally {
    db.close();
  }
});

test('plat dinormalkan dulu, jadi "l 1234 ab" tetap satu kedatangan dengan "L1234AB"', () => {
  const { db, gerbang } = siapkan();
  try {
    const pertama = bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, 0));
    const lanjut = bacaan(db, gerbang.id, 'l 1234 ab', 'masuk', jam(0, 2));
    assert.equal(lanjut.kedatangan_id, pertama.id, 'plat yang sama dengan tulisan berbeda menjadi dua kedatangan');
  } finally {
    db.close();
  }
});

test(`jendela bawaan ${JENDELA_KEDATANGAN_DETIK} detik dibaca dari satu tempat, dan bisa diubah`, () => {
  const asli = process.env.TGT_JENDELA_KEDATANGAN;
  try {
    delete process.env.TGT_JENDELA_KEDATANGAN;
    assert.equal(jendelaKedatangan(), JENDELA_KEDATANGAN_DETIK);
    process.env.TGT_JENDELA_KEDATANGAN = '45';
    assert.equal(jendelaKedatangan(), 45);
    // Nilai yang tidak masuk akal memakai bawaan. Arah gagalnya: JANGAN menggabung segalanya — jendela
    // raksasa akan menyembunyikan kendaraan yang benar-benar datang dua kali.
    for (const salah of ['0', '-5', 'entah', '', ' ', '99999999']) {
      process.env.TGT_JENDELA_KEDATANGAN = salah;
      assert.equal(jendelaKedatangan(), JENDELA_KEDATANGAN_DETIK, `nilai "${salah}" tidak memakai bawaan`);
    }
  } finally {
    if (asli === undefined) delete process.env.TGT_JENDELA_KEDATANGAN;
    else process.env.TGT_JENDELA_KEDATANGAN = asli;
  }
});

// ─── Rantai: lewat akses.bacaanGerbang, jalur yang dipakai gerbang ──────────────────────────────────

function siapkanAkses() {
  const db = buka(':memory:');
  const sesi = (o) => ({ penggunaId: o.id });
  let kode;
  mintaOtp(db, { email: 'bos@example.test', kirim: (_e, k) => { kode = k; } });
  const bos = masukDenganOtp(db, { email: 'bos@example.test', kode, nama: 'Bos Contoh' });
  const { grup } = akses.buatGrup(db, sesi(bos), { nama: 'Cluster Contoh', jenis: 'pribadi' });
  akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Gerbang Depan', jenisLokasi: 'perumahan', alamat: 'Jl. Contoh 1', kota: 'Sidoarjo',
  });
  const g = akses.gerbangSaya(db, sesi(bos))[0];
  akses.aktifkanGerbang(db, sesi(bos), g.id);
  daftarkanKendaraan(db, { gerbangId: g.id, jenis: 'mobil', plat: 'L1234AB', atasNama: 'Penghuni Contoh' });
  return { db, g, bos, sesi };
}

const baca = (db, sesi, bos, g, arah, waktu) => akses.bacaanGerbang(db, sesi(bos), {
  gerbangId: g.id, bacaan: 'L1234AB', ragu: [], arah, waktu, ciriJenis: 'mobil',
});

test('⛔ RANTAI: lima bingkai MASUK memberi SATU notifikasi, bukan lima', () => {
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    const hasil = [0, 1, 2, 3, 4].map((d) => baca(db, sesi, bos, g, 'masuk', jam(0, d)));
    const notif = hasil.filter((h) => h.notifikasi).length;
    assert.equal(notif, 0, `satpam diteriaki ${notif} kali untuk satu mobil penghuni yang masuk wajar`);
    for (const h of hasil) assert.equal(h.putusan, 'buka');
    // Bingkai lanjutan ditandai, supaya layar satpam tidak menampilkannya sebagai kejadian baru.
    assert.equal(hasil[0].ulangan, false);
    assert.deepEqual(hasil.slice(1).map((h) => h.ulangan), [true, true, true, true]);
  } finally {
    db.close();
  }
});

test('⛔ RANTAI: tiga bingkai KELUAR tidak pernah menahan gerbang untuk penghuni yang sah', () => {
  // Inilah cacat yang menghentikan produk: dulu bingkai kedua menjadi panggil_satpam, jadi SETIAP mobil yang
  // keluar menahan gerbang.
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    baca(db, sesi, bos, g, 'masuk', jam(0, 0));
    const keluar = [0, 1, 2].map((d) => baca(db, sesi, bos, g, 'keluar', jam(1, d)));
    const ditahan = keluar.filter((h) => h.putusan === 'panggil_satpam');
    assert.equal(ditahan.length, 0,
      `gerbang ditahan ${ditahan.length} kali untuk penghuni yang sah: ${ditahan.map((h) => h.alasan).join(' | ')}`);
    for (const h of keluar) assert.equal(h.putusan, 'buka');
  } finally {
    db.close();
  }
});

test('putusan bingkai lanjutan SAMA PERSIS dengan bingkai pertama, bukan dihitung ulang', () => {
  // Kalau ia dihitung ulang, ada jalan yang bisa melonggarkan. Yang dikembalikan adalah putusan yang sudah
  // tersimpan, jadi tidak ada putusan baru yang bisa lahir di dalam jendela.
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    const pertama = baca(db, sesi, bos, g, 'masuk', jam(0, 0));
    const lanjut = baca(db, sesi, bos, g, 'masuk', jam(0, 3));
    assert.equal(lanjut.putusan, pertama.putusan);
    assert.equal(lanjut.alasan, pertama.alasan);
  } finally {
    db.close();
  }
});

test('⛔ JANGGAL YANG SUNGGUHAN tetap memanggil satpam: pagar K73 tidak ikut lumpuh', () => {
  // Pagar terpenting di rencana ini. Plat yang keluar lagi SESUDAH jendela lewat, padahal catatan mengatakan
  // ia tidak di dalam, tetap ditahan — itu kemungkinan plat tiruan (K73, alasan owner).
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    baca(db, sesi, bos, g, 'masuk', jam(0, 0));
    const keluarSah = baca(db, sesi, bos, g, 'keluar', jam(1, 0));
    assert.equal(keluarSah.putusan, 'buka');

    // 21 detik kemudian: di luar jendela, dan catatan mengatakan ia sudah di luar.
    const keluarJanggal = baca(db, sesi, bos, g, 'keluar', jam(1, 21));
    assert.equal(keluarJanggal.putusan, 'panggil_satpam',
      'plat yang keluar dua kali di luar jendela TIDAK ditahan: pagar K73 lumpuh');
    assert.equal(keluarJanggal.ulangan, false);
    assert.match(keluarJanggal.alasan, /satpam/i);
  } finally {
    db.close();
  }
});

// ─── Beranda menghitung kedatangan ──────────────────────────────────────────────────────────────────

test('⛔ beranda menghitung KEDATANGAN, bukan baris: satu mobil lima bingkai = 1 masuk', () => {
  const { db, gerbang } = siapkan();
  try {
    for (const d of [0, 1, 2, 3, 4]) bacaan(db, gerbang.id, 'L1234AB', 'masuk', jam(0, d));
    for (const d of [0, 1, 2]) bacaan(db, gerbang.id, 'L1234AB', 'keluar', jam(5, d));

    const ubin = ubinBeranda(db, gerbang.id, HARI);
    assert.equal(ubin.masukHariIni, 1, 'beranda masih menghitung bingkai, bukan kendaraan');
    assert.equal(ubin.keluarHariIni, 1);
    assert.equal(ubin.diDalam, 0);

    const perJam = ringkasanJam(db, gerbang.id, HARI);
    assert.equal(perJam[8].masuk, 1, 'grafik jam masih menghitung bingkai');
    assert.equal(perJam[8].keluar, 1);
  } finally {
    db.close();
  }
});

test('beranda tetap benar untuk kendaraan yang BERBEDA di jam yang sama', () => {
  // Penjaga arah lain: pengelompokan tidak boleh ikut menelan kendaraan yang memang berbeda.
  const { db, gerbang } = siapkan();
  try {
    for (const p of ['L1111AA', 'L2222BB', 'L3333CC']) {
      for (const d of [0, 1]) bacaan(db, gerbang.id, p, 'masuk', jam(0, d));
    }
    const ubin = ubinBeranda(db, gerbang.id, HARI);
    assert.equal(ubin.masukHariIni, 3, 'tiga kendaraan berbeda seharusnya tiga kedatangan');
    assert.equal(ringkasanJam(db, gerbang.id, HARI)[8].masuk, 3);
  } finally {
    db.close();
  }
});

test('⛔ bingkai lanjutan dari PANGGIL_SATPAM tidak pernah berubah menjadi buka', () => {
  // Arah keselamatan yang paling penting di rencana ini. Pengelompokan hanya boleh menyalin putusan bingkai
  // pertama; kalau ia bisa melonggarkan, satpam yang sudah dipanggil bisa dibatalkan oleh bingkai berikutnya.
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    // Plat yang TIDAK terdaftar, dengan tiga posisi ragu: lebih dari MAKS_RAGU, jadi tidak pernah dibuka.
    const kirim = (waktu) => akses.bacaanGerbang(db, sesi(bos), {
      gerbangId: g.id, bacaan: 'B9999ZZ', ragu: [0, 1, 2], arah: 'masuk', waktu,
    });
    const pertama = kirim(jam(10, 0));
    assert.notEqual(pertama.putusan, 'buka', 'penyiapan ujinya salah: bacaan ini seharusnya tidak dibuka');

    for (const d of [1, 5, 15]) {
      const lanjut = kirim(jam(10, d));
      assert.equal(lanjut.putusan, pertama.putusan,
        `bingkai pada detik ${d} mengubah putusan ${pertama.putusan} menjadi ${lanjut.putusan}`);
      assert.notEqual(lanjut.putusan, 'buka', 'pengelompokan melonggarkan putusan: gerbang dibuka oleh bingkai lanjutan');
    }
  } finally {
    db.close();
  }
});

test('⛔ bingkai lanjutan tidak pernah memberi notifikasi KEDUA, tetapi yang pertama tetap sampai', () => {
  // Penjaga dua arah: pengelompokan tidak boleh ikut membungkam notifikasi yang memang perlu.
  const { db, g, bos, sesi } = siapkanAkses();
  try {
    const kirim = (waktu) => akses.bacaanGerbang(db, sesi(bos), {
      gerbangId: g.id, bacaan: 'B8888YY', ragu: [], arah: 'masuk', waktu,
    });
    const pertama = kirim(jam(20, 0));
    const lanjut = [1, 2].map((d) => kirim(jam(20, d)));
    // Plat tak dikenal memanggil satpam; bingkai pertama HARUS memberi notifikasi.
    assert.ok(pertama.notifikasi, 'notifikasi bingkai pertama ikut hilang: satpam tidak pernah diberi tahu');
    assert.deepEqual(lanjut.map((h) => h.notifikasi), [null, null], 'ada notifikasi kedua');
  } finally {
    db.close();
  }
});
