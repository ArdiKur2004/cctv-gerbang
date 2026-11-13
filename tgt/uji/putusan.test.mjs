// Uji tgt/putusan.mjs: aturan memutuskan membuka gerbang (Rencana T4 Task 1, keputusan owner K46).
//
// ⛔ Ini kode paling menyangkut keselamatan di produk ini. Tiap aturan diuji DUA arah: yang boleh membuka
// benar-benar membuka, DAN yang tidak boleh membuka benar-benar tidak. Uji satu arah bisa lulus oleh aturan
// yang membuka untuk segalanya.
//
// Semua plat di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { PUTUSAN, putuskan } from '../putusan.mjs';

/** Satu kendaraan terdaftar. `status` = di mana ia sekarang menurut kejadian terakhirnya. */
const izin = (plat, { status = 'di_luar', jenis = 'penghuni' } = {}) => ({ plat, status, jenis });

const DAFTAR = [
  izin('L1234AB'),
  izin('L5678CD'),
  izin('W1111ZZ', { jenis: 'tamu' }),
];

const minta = (lebih = {}) => ({
  bacaan: 'L1234AB',
  ragu: [],
  arah: 'masuk',
  jenisLokasi: 'kantor',
  daftar: DAFTAR,
  ...lebih,
});

// ─── Bacaan yang yakin ──────────────────────────────────────────────────────────────────────────────

test('bacaan yakin yang cocok tepat satu plat: buka', () => {
  const h = putuskan(minta());
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.deepEqual(h.calon.map((c) => c.plat), ['L1234AB']);
  assert.ok(h.alasan.length > 0, 'alasan wajib terisi supaya satpam tahu kenapa');
});

test('bacaan yakin yang tidak ada di daftar: tidak dikenal, bukan buka', () => {
  const h = putuskan(minta({ bacaan: 'N9999XX' }));
  assert.equal(h.putusan, PUTUSAN.TIDAK_DIKENAL);
  assert.deepEqual(h.calon, []);
});

test('daftar izin kosong tidak pernah membuka', () => {
  assert.equal(putuskan(minta({ daftar: [] })).putusan, PUTUSAN.TIDAK_DIKENAL);
});

test('tamu yang terbaca yakin tetap dibukakan, juga di perumahan', () => {
  // Pembatasan "hanya plat penghuni" di K46 berlaku untuk bacaan yang RAGU. Tamu yang diundang dengan benar
  // dan terbaca jelas tidak boleh ditahan.
  for (const jenisLokasi of ['kantor', 'perumahan']) {
    const h = putuskan(minta({ bacaan: 'W1111ZZ', jenisLokasi }));
    assert.equal(h.putusan, PUTUSAN.BUKA, `tamu yakin di ${jenisLokasi} seharusnya dibuka`);
  }
});

test('status janggal saat MASUK: tetap dibuka, hanya ditandai supaya satpam diberi tahu (K73)', () => {
  // Kamera bisa melewatkan satu kejadian, jadi "sudah di dalam lalu terbaca masuk lagi" bukan alasan menahan
  // orang di gerbang. Masuk adalah arah yang berisiko kecil.
  const h = putuskan(minta({ arah: 'masuk', daftar: [izin('L1234AB', { status: 'di_dalam' })] }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.equal(h.statusJanggal, true);
  assert.match(h.alasan, /status/i);
});

test('⛔ status janggal saat KELUAR: TIDAK dibuka, satpam dipanggil (K73)', () => {
  // Owner, 26 Okt: "NAMUN tidak untuk keluar, karena ini berbahaya, bisa jadi anda meloloskan maling atau
  // pencuri dengan platnomor yang sama". Kendaraan yang keluar padahal tidak pernah tercatat masuk adalah
  // tanda yang harus dilihat orang, bukan diloloskan mesin.
  const h = putuskan(minta({ arah: 'keluar', daftar: [izin('L1234AB', { status: 'di_luar' })] }));
  assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
  assert.equal(h.statusJanggal, true);
  assert.match(h.alasan, /keluar|tidak pernah tercatat masuk/i);
});

test('keluar yang wajar tetap dibuka', () => {
  const h = putuskan(minta({ arah: 'keluar', daftar: [izin('L1234AB', { status: 'di_dalam' })] }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.equal(h.statusJanggal, false);
});

test('bedanya memang arah, bukan kebetulan: masukan sama persis selain arahnya', () => {
  // Penjaga terhadap pembacaan yang keliru kelak: satu-satunya yang membedakan kedua hasil ini adalah arah.
  const daftarMasuk = [izin('L1234AB', { status: 'di_dalam' })];
  const daftarKeluar = [izin('L1234AB', { status: 'di_luar' })];
  assert.equal(putuskan(minta({ arah: 'masuk', daftar: daftarMasuk })).putusan, PUTUSAN.BUKA);
  assert.equal(putuskan(minta({ arah: 'keluar', daftar: daftarKeluar })).putusan, PUTUSAN.PANGGIL_SATPAM);
});

// ─── Bacaan ragu: pagar utama K46 ───────────────────────────────────────────────────────────────────

test('⛔ lebih dari 2 posisi ragu TIDAK PERNAH membuka, walau calonnya hanya satu', () => {
  // Pagar paling keras di K46. Diuji justru pada keadaan yang paling menggoda: calon tunggal yang jelas.
  for (const ragu of [[0, 1, 2], [0, 1, 2, 3], [1, 3, 5, 6]]) {
    const h = putuskan(minta({ bacaan: 'L1234AB', ragu, daftar: [izin('L1234AB')] }));
    assert.notEqual(h.putusan, PUTUSAN.BUKA, `${ragu.length} posisi ragu seharusnya tidak membuka`);
    assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
    assert.match(h.alasan, /ragu/i);
  }
});

test('ragu 1-2 posisi dengan tepat satu calon: buka', () => {
  // Posisi 4 ragu: "L123?AB". Hanya L1234AB yang cocok di posisi yang yakin.
  const h = putuskan(minta({ bacaan: 'L1234AB', ragu: [4] }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.deepEqual(h.calon.map((c) => c.plat), ['L1234AB']);
});

// Dua plat yang berbeda HANYA pada posisi yang diragukan: "L12??AB". Inilah keadaan yang benar-benar
// membingungkan mesin, dan yang diatur K46.
const KEMBAR = (status1, status2) => [
  izin('L1234AB', { status: status1 }),
  izin('L1299AB', { status: status2 }),
];

test('ragu 1-2 posisi dengan DUA calon berstatus sama: panggil satpam', () => {
  const h = putuskan(minta({ bacaan: 'L1234AB', ragu: [3, 4], daftar: KEMBAR('di_luar', 'di_luar') }));
  assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
  assert.equal(h.calon.length, 2);
  assert.match(h.alasan, /2 plat|dua|lebih dari satu|beberapa/i);
});

test('dua calon yang BERBEDA status tidak membingungkan: yang masuk akal untuk arahnya yang dipakai', () => {
  // Inilah guna kalimat "berstatus sama" di K46: yang sedang di dalam tidak mungkin sedang masuk.
  const h = putuskan(minta({
    bacaan: 'L1234AB', ragu: [3, 4], daftar: KEMBAR('di_luar', 'di_dalam'), arah: 'masuk',
  }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.deepEqual(h.calon.map((c) => c.plat), ['L1234AB']);
});

test('arah keluar memilih yang sedang di dalam', () => {
  const h = putuskan(minta({
    bacaan: 'L1299AB', ragu: [3, 4], daftar: KEMBAR('di_luar', 'di_dalam'), arah: 'keluar',
  }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.deepEqual(h.calon.map((c) => c.plat), ['L1299AB']);
});

test('dua calon kembar yang sama-sama di dalam, arah keluar: tetap panggil satpam', () => {
  const h = putuskan(minta({
    bacaan: 'L1234AB', ragu: [3, 4], daftar: KEMBAR('di_dalam', 'di_dalam'), arah: 'keluar',
  }));
  assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
  assert.equal(h.calon.length, 2);
});

test('ragu tanpa calon sama sekali: tidak dikenal', () => {
  const h = putuskan(minta({ bacaan: 'N123?XX', ragu: [4], daftar: DAFTAR }));
  assert.equal(h.putusan, PUTUSAN.TIDAK_DIKENAL);
});

test('⛔ tamu terdaftar BOLEH langsung masuk, juga di perumahan dan juga saat bacaannya ragu (K72)', () => {
  // DIBALIK, bukan dihapus. Dulu uji ini menuntut "di perumahan, bacaan ragu bercalon tamu memanggil satpam",
  // sesuai bacaan agen atas K46. Owner mengoreksinya 26 Okt: "soal perumahan, setiap tamu bisa langsung masuk
  // lewat gerbang depan perumahan". Jadi jenis calon (tamu atau penghuni) TIDAK PERNAH lagi menjadi alasan
  // menahan; yang menahan hanyalah KERAGUAN — bacaan yang cocok lebih dari satu plat, atau ragu di atas batas.
  const daftar = [izin('W1111ZZ', { jenis: 'tamu' })];
  for (const jenisLokasi of ['perumahan', 'kantor', 'apartemen', 'pabrik']) {
    const h = putuskan(minta({ bacaan: 'W1111ZZ', ragu: [4], daftar, jenisLokasi }));
    assert.equal(h.putusan, PUTUSAN.BUKA, `tamu terdaftar di ${jenisLokasi} seharusnya langsung masuk`);
  }
});

test('keraguan tetap menahan di perumahan: dua calon tetap memanggil satpam', () => {
  // Yang dicabut K72 hanya pembatasan menurut JENIS calon. Pagar keraguan K46 tidak ikut longgar.
  const daftar = [izin('W1111ZZ', { jenis: 'tamu' }), izin('W1199ZZ', { jenis: 'penghuni' })];
  const h = putuskan(minta({ bacaan: 'W1111ZZ', ragu: [3, 4], daftar, jenisLokasi: 'perumahan' }));
  assert.equal(h.putusan, PUTUSAN.PANGGIL_SATPAM);
});

test('di perumahan, bacaan ragu dengan tepat satu plat PENGHUNI tetap boleh buka', () => {
  const daftar = [izin('L1234AB', { jenis: 'penghuni' })];
  const h = putuskan(minta({ bacaan: 'L1234AB', ragu: [4], daftar, jenisLokasi: 'perumahan' }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
});

// ─── Pencocokan ─────────────────────────────────────────────────────────────────────────────────────

test('plat yang panjangnya berbeda tidak pernah dianggap cocok', () => {
  const daftar = [izin('L1234ABC')];
  assert.equal(putuskan(minta({ bacaan: 'L1234AB', ragu: [4], daftar })).putusan, PUTUSAN.TIDAK_DIKENAL);
});

test('pencocokan tidak peka huruf besar-kecil dan mengabaikan spasi', () => {
  const h = putuskan(minta({ bacaan: 'l 1234 ab' }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
});

test('posisi ragu dihitung setelah plat dirapikan, bukan sebelum', () => {
  // "l 1234 ab" dirapikan menjadi "L1234AB"; posisi 4 adalah angka terakhir, bukan spasi.
  const h = putuskan(minta({ bacaan: 'L1239AB', ragu: [4], daftar: [izin('L1234AB')] }));
  assert.equal(h.putusan, PUTUSAN.BUKA, 'posisi ragu seharusnya menutupi angka yang salah baca');
});

// ─── Gagal ke arah menutup ──────────────────────────────────────────────────────────────────────────

test('⛔ masukan yang tidak dikenal bentuknya TIDAK PERNAH membuka', () => {
  const buruk = [
    { bacaan: '', ragu: [] },
    { bacaan: null, ragu: [] },
    { bacaan: 'L1234AB', ragu: [99] },           // posisi ragu di luar jangkauan
    { bacaan: 'L1234AB', ragu: [-1] },
    { bacaan: 'L1234AB', ragu: 'bukan daftar' },
    { bacaan: 'L1234AB', ragu: [], arah: 'parkir' },
    { bacaan: 'L1234AB', ragu: [], arah: undefined },
    { bacaan: 'L1234AB', ragu: [], daftar: null },
    { bacaan: 'L1234AB', ragu: [], jenisLokasi: undefined },
  ];
  for (const b of buruk) {
    const h = putuskan(minta(b));
    assert.notEqual(h.putusan, PUTUSAN.BUKA, `masukan ${JSON.stringify(b)} seharusnya tidak membuka`);
    assert.ok(h.alasan, 'alasan wajib terisi walau masukannya rusak');
  }
});

test('⛔ putusan hanya boleh salah satu dari daftar yang dikenal', () => {
  const nilaiSah = Object.values(PUTUSAN);
  assert.deepEqual([...nilaiSah].sort(), ['buka', 'panggil_satpam', 'tidak_dikenal']);
  for (const b of [{}, { bacaan: 'L1234AB', ragu: [0, 1, 2, 3, 4, 5, 6] }, { daftar: [] }]) {
    assert.ok(nilaiSah.includes(putuskan(minta(b)).putusan));
  }
});

test('putusan tidak pernah menyebut perintah tutup', () => {
  // CLAUDE.md §3: produk hanya memberi perintah BUKA. Tidak boleh ada jalan yang menghasilkan "tutup".
  const semua = [
    putuskan(minta()),
    putuskan(minta({ bacaan: 'N9999XX' })),
    putuskan(minta({ ragu: [0, 1, 2] })),
  ];
  for (const h of semua) {
    assert.ok(!/tutup/i.test(JSON.stringify(h)), 'tidak boleh ada perintah tutup di mana pun');
  }
});

test('putusan menyertakan bacaan yang sudah dirapikan, untuk dicatat apa adanya', () => {
  const h = putuskan(minta({ bacaan: 'l-1234-ab' }));
  assert.equal(h.plat, 'L1234AB');
});

// ─── Jenis kendaraan dari kamera (Rencana T6) ───────────────────────────────────────────────────────
//
// Jenis benar pada 12 dari 14 mobil (bukti/2026-10-24-jenis-dan-warna.md) — sekitar 1 dari 7 salah. Karena
// itu ia TIDAK PERNAH menahan gerbang (K55); ia hanya menambah catatan supaya satpam diberi tahu.

test('jenis yang COCOK tidak mengubah putusan apa pun', () => {
  const daftar = [izin('L1234AB')];
  const h = putuskan(minta({ daftar, jenisTerbaca: 'mobil' }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.equal(h.ciriJanggal, false);
});

test('⛔ jenis yang TIDAK cocok memberi tanda, tetapi gerbang TETAP DIBUKA', () => {
  // K55: ciri hanya memberi peringatan ke satpam, tidak menahan gerbang. Dengan 1 dari 7 salah, menahan
  // berarti menahan orang yang tidak bersalah berkali-kali tiap hari.
  const daftar = [{ ...izin('L1234AB'), jenisKendaraan: 'mobil' }];
  const h = putuskan(minta({ daftar, jenisTerbaca: 'truk' }));
  assert.equal(h.putusan, PUTUSAN.BUKA, 'jenis tidak boleh menahan gerbang');
  assert.equal(h.ciriJanggal, true);
  assert.match(h.alasan, /jenis/i);
});

test('⛔ jenis yang tidak cocok juga tidak menahan saat KELUAR', () => {
  // Disurface ke owner: K73 menahan status janggal saat keluar. Untuk jenis, ketelitiannya belum cukup.
  const daftar = [{ ...izin('L1234AB', { status: 'di_dalam' }), jenisKendaraan: 'mobil' }];
  const h = putuskan(minta({ daftar, arah: 'keluar', jenisTerbaca: 'bus' }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.equal(h.ciriJanggal, true);
});

test('jenis yang tidak terbaca mesin BUKAN ketidakcocokan', () => {
  // Mesin sering menjawab "tak yakin". Itu tidak boleh menjadi tuduhan.
  const daftar = [{ ...izin('L1234AB'), jenisKendaraan: 'mobil' }];
  for (const jenisTerbaca of [null, undefined, '', 'tak_yakin']) {
    const h = putuskan(minta({ daftar, jenisTerbaca }));
    assert.equal(h.ciriJanggal, false, `jenis ${JSON.stringify(jenisTerbaca)} seharusnya bukan ketidakcocokan`);
  }
});

test('kendaraan terdaftar tanpa jenis tercatat bukan ketidakcocokan', () => {
  const h = putuskan(minta({ daftar: [izin('L1234AB')], jenisTerbaca: 'truk' }));
  assert.equal(h.ciriJanggal, false, 'yang tidak punya jenis terdaftar tidak bisa dibilang tidak cocok');
});

test('⛔ jenis TIDAK PERNAH mengubah putusan dari tidak-buka menjadi buka', () => {
  // Pagar paling penting: ciri hanya boleh menambah catatan, tidak pernah melonggarkan.
  const kasus = [
    { bacaan: 'N9999XX', ragu: [], daftar: [izin('L1234AB')] },
    { bacaan: 'L1234AB', ragu: [0, 1, 2], daftar: [izin('L1234AB')] },
    { bacaan: 'L1234AB', ragu: [3, 4], daftar: [izin('L1234AB'), izin('L1299AB')] },
  ];
  for (const k of kasus) {
    const tanpa = putuskan(minta(k)).putusan;
    for (const jenisTerbaca of ['mobil', 'truk', null]) {
      assert.equal(putuskan(minta({ ...k, jenisTerbaca })).putusan, tanpa,
        `jenis ${jenisTerbaca} mengubah putusan ${JSON.stringify(k.bacaan)}`);
    }
  }
});

test('bacaan RAGU yang membuka juga menandai jenis yang tidak cocok', () => {
  const daftar = [{ ...izin('L1234AB'), jenisKendaraan: 'mobil' }];
  const h = putuskan(minta({ bacaan: 'L1234AB', ragu: [4], daftar, jenisTerbaca: 'truk' }));
  assert.equal(h.putusan, PUTUSAN.BUKA);
  assert.equal(h.ciriJanggal, true);
});

test('⛔ setiap jalan keluar putusan selalu memuat ciriJanggal', () => {
  // Penjaga terhadap jalan keluar baru yang lupa mengisinya: nilai undefined akan terbaca "tidak janggal"
  // di tempat lain, dan ketidakcocokan menghilang diam-diam.
  const kasus = [
    {}, { bacaan: 'N9999XX' }, { ragu: [0, 1, 2] }, { arah: 'parkir' }, { daftar: null },
    { bacaan: 'L1234AB', ragu: [4] }, { arah: 'keluar', daftar: [izin('L1234AB', { status: 'di_luar' })] },
  ];
  for (const k of kasus) {
    assert.equal(typeof putuskan(minta(k)).ciriJanggal, 'boolean', `ciriJanggal hilang di ${JSON.stringify(k)}`);
  }
});
