// Uji tgt/layanan.mjs bagian kejadian, kunjungan tamu, dan ringkasan jam (Rencana T1 Task 3).
//
// Rencana menulis uji ini di layanan.test.mjs; dipisah ke berkas sendiri karena berkas itu sudah panjang.
// Keduanya ikut gerbang `npm test` lewat pola tgt/uji/*.test.mjs, jadi tidak ada yang luput.
//
// Semua plat di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import {
  buatGrup, buatGerbang, daftarkanKendaraan, tambahTamu,
  ARAH, catatKejadian, kejadianGerbang, kunjunganTamu, ringkasanJam,
} from '../layanan.mjs';

function siapkan() {
  const db = buka(':memory:');
  const grup = buatGrup(db, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id, nama: 'Kantor Contoh Gate Selatan', jenisLokasi: 'kantor',
    alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
  });
  return { db, grup, gerbang };
}

// ─── Kejadian ───────────────────────────────────────────────────────────────────────────────────────

test('arah kejadian hanya masuk atau keluar: daftar putih', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.deepEqual([...ARAH], ['masuk', 'keluar']);
    for (const arah of ['Masuk', 'parkir', '', undefined, null]) {
      assert.throws(
        () => catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah, plat: 'L 1234 AB' }),
        /arah/i,
        `arah ${JSON.stringify(arah)} seharusnya ditolak`,
      );
    }
  } finally {
    db.close();
  }
});

test('kejadian kendaraan terdaftar ditautkan ke kendaraannya', () => {
  const { db, gerbang } = siapkan();
  try {
    const k = daftarkanKendaraan(db, {
      gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB', atasNama: 'Budi Contoh',
    });
    const kej = catatKejadian(db, {
      gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'l-1234-ab', yakin: 0.91,
    });
    assert.equal(kej.kendaraan_id, k.id);
    assert.equal(kej.tamu_id, null);
    assert.equal(kej.plat, 'L1234AB', 'plat kejadian harus tersimpan dalam bentuk baku');
  } finally {
    db.close();
  }
});

test('kejadian plat yang tidak terdaftar TETAP dicatat, tanpa tautan', () => {
  const { db, gerbang } = siapkan();
  try {
    const kej = catatKejadian(db, {
      gerbangId: gerbang.id, waktu: '2026-10-26T08:05:00', arah: 'masuk', plat: 'N 9999 ZZ',
    });
    assert.equal(kej.kendaraan_id, null);
    assert.equal(kej.tamu_id, null);
    assert.equal(kejadianGerbang(db, gerbang.id).length, 1, 'kejadian tak dikenal tidak boleh dibuang: catatan satpam');
  } finally {
    db.close();
  }
});

test('kejadian tanpa plat terbaca tetap dicatat, karena bacaan bisa gagal', () => {
  const { db, gerbang } = siapkan();
  try {
    const kej = catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:06:00', arah: 'masuk', plat: null });
    assert.equal(kej.plat, null);
    assert.equal(kejadianGerbang(db, gerbang.id).length, 1);
  } finally {
    db.close();
  }
});

test('ciri kendaraan hanya dicatat bersama kejadian (K63)', () => {
  const { db, gerbang } = siapkan();
  try {
    const kej = catatKejadian(db, {
      gerbangId: gerbang.id, waktu: '2026-10-26T08:07:00', arah: 'masuk', plat: 'L 1234 AB',
      ciriJenis: 'mobil', ciriWarna: 'hitam', ciriMerek: null,
    });
    assert.equal(kej.ciri_jenis, 'mobil');
    assert.equal(kej.ciri_warna, 'hitam');
    assert.equal(kej.ciri_merek, null);
  } finally {
    db.close();
  }
});

test('kejadian satu gerbang tidak terbaca dari gerbang lain (K67)', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'L 1111 AA' });
    catatKejadian(db, { gerbangId: lain.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'L 2222 BB' });

    assert.deepEqual(kejadianGerbang(db, gerbang.id).map((k) => k.plat), ['L1111AA']);
    assert.deepEqual(kejadianGerbang(db, lain.id).map((k) => k.plat), ['L2222BB']);
  } finally {
    db.close();
  }
});

// ─── Kunjungan tamu dan lewat batas ─────────────────────────────────────────────────────────────────

test('tamu masuk membuka kunjungan berstatus di dalam', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'pikap', plat: 'W 1212 ZZ', lamaHari: 1,
    });
    const kej = catatKejadian(db, {
      gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'w 1212 zz',
    });
    assert.equal(kej.tamu_id, t.id);

    const kunjungan = kunjunganTamu(db, t.id);
    assert.equal(kunjungan.length, 1);
    assert.equal(kunjungan[0].masuk, '2026-10-26T08:00:00');
    assert.equal(kunjungan[0].keluar, null);
    assert.equal(kunjungan[0].status, 'di_dalam');
  } finally {
    db.close();
  }
});

test('tamu keluar di dalam batas menutup kunjungan berstatus selesai', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'mobil', plat: 'W 1313 YY', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'W 1313 YY' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T15:30:00', arah: 'keluar', plat: 'W 1313 YY' });

    const [kunjungan] = kunjunganTamu(db, t.id);
    assert.equal(kunjungan.keluar, '2026-10-26T15:30:00');
    assert.equal(kunjungan.status, 'selesai');
  } finally {
    db.close();
  }
});

test('lewat batas dihitung dari JAM masuk + lama kunjungan, bukan dari tanggal kalender', () => {
  const { db, gerbang } = siapkan();
  try {
    // Masuk 23:00, lama 1 hari, keluar jam 10:00 esok hari = 11 jam. Tanggalnya berganti, tetapi batasnya belum lewat.
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Malam', jenis: 'truk', plat: 'W 1414 XX', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T23:00:00', arah: 'masuk', plat: 'W 1414 XX' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-27T10:00:00', arah: 'keluar', plat: 'W 1414 XX' });

    assert.equal(kunjunganTamu(db, t.id)[0].status, 'selesai');
  } finally {
    db.close();
  }
});

test('keluar sesudah jam masuk + lama kunjungan berstatus lewat batas', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Lama', jenis: 'mobil', plat: 'W 1515 WW', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'W 1515 WW' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-27T09:00:00', arah: 'keluar', plat: 'W 1515 WW' });

    assert.equal(kunjunganTamu(db, t.id)[0].status, 'lewat_batas');
  } finally {
    db.close();
  }
});

test('lewat batas TIDAK menahan kendaraan: kejadian keluarnya tetap tercatat (CLAUDE.md §3)', () => {
  const { db, gerbang } = siapkan();
  try {
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Lama', jenis: 'mobil', plat: 'W 1616 VV', lamaHari: 1 });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'W 1616 VV' });
    const keluar = catatKejadian(db, {
      gerbangId: gerbang.id, waktu: '2026-10-30T08:00:00', arah: 'keluar', plat: 'W 1616 VV',
    });
    assert.ok(keluar.id, 'kejadian keluar harus tercatat walau tamunya lewat batas');
    assert.equal(kejadianGerbang(db, gerbang.id).length, 2);
  } finally {
    db.close();
  }
});

test('tamu yang keluar tanpa pernah tercatat masuk tidak membuat kunjungan hantu', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'mobil', plat: 'W 1717 UU', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T15:00:00', arah: 'keluar', plat: 'W 1717 UU' });
    assert.equal(kunjunganTamu(db, t.id).length, 0);
  } finally {
    db.close();
  }
});

test('tamu masuk dua kali tanpa keluar tidak membuka kunjungan kedua', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'mobil', plat: 'W 1818 TT', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'W 1818 TT' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:02:00', arah: 'masuk', plat: 'W 1818 TT' });

    const kunjungan = kunjunganTamu(db, t.id);
    assert.equal(kunjungan.length, 1, 'bacaan ganda di gerbang tidak boleh menjadi dua kunjungan');
    assert.equal(kunjungan[0].masuk, '2026-10-26T08:00:00', 'jam masuk yang pertama yang berlaku');
  } finally {
    db.close();
  }
});

test('tamu kedua berplat sama tidak membuat kunjungan tamu pertama tersangkut "di dalam"', () => {
  // Cacat sepupu yang ditemukan sesudah Task 3 ditulis: pencarian tamu mengambil yang terbaru, jadi tamu lama
  // yang masih di dalam tidak pernah ditutup, dan angka "di dalam sekarang" di dashboard ikut salah.
  const { db, gerbang } = siapkan();
  try {
    const pertama = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Kurir Senin', jenis: 'pikap', plat: 'W 1919 SS', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'W 1919 SS' });

    // Pengundang lain mendaftarkan kurir yang sama lagi, sementara kendaraannya masih di dalam.
    const kedua = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Kurir Senin', jenis: 'pikap', plat: 'W 1919 SS', lamaHari: 1,
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T09:00:00', arah: 'keluar', plat: 'W 1919 SS' });

    assert.equal(kunjunganTamu(db, pertama.id)[0].status, 'selesai', 'kunjungan yang terbuka yang harus ditutup');
    assert.equal(kunjunganTamu(db, kedua.id).length, 0);
  } finally {
    db.close();
  }
});

test('waktu kejadian wajib berbentuk ISO jam setempat, karena ringkasan jam membacanya per huruf', () => {
  // Cacat sepupu kedua: ringkasanJam memotong huruf ke-12 dan ke-13 sebagai jam. Bentuk lain ("2026-10-26",
  // "2026-10-26 08:00") dulu diterima dan membuat angka dashboard salah DIAM-DIAM. Sekarang ditolak di pintu.
  const { db, gerbang } = siapkan();
  try {
    for (const waktu of ['2026-10-26', '2026-10-26 08:00:00', '2026-10-26T8:00:00', '26/10/2026 08:00']) {
      assert.throws(
        () => catatKejadian(db, { gerbangId: gerbang.id, waktu, arah: 'masuk', plat: 'L 1234 AB' }),
        /waktu/i,
        `waktu ${JSON.stringify(waktu)} seharusnya ditolak`,
      );
    }
    // Yang benar diterima, dengan atau tanpa detik.
    assert.equal(
      catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T08:00', arah: 'masuk', plat: 'L 1 A' }).waktu,
      '2026-10-26T08:00:00',
      'tanpa detik dilengkapi menjadi :00, supaya panjangnya selalu sama',
    );
  } finally {
    db.close();
  }
});

test('waktu yang tidak diisi memakai jam setempat, bukan UTC', () => {
  const { db, gerbang } = siapkan();
  try {
    const kej = catatKejadian(db, { gerbangId: gerbang.id, arah: 'masuk', plat: 'L 2 B' });
    assert.match(kej.waktu, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/);
    const jamSetempat = String(new Date().getHours()).padStart(2, '0');
    assert.equal(kej.waktu.slice(11, 13), jamSetempat, 'jam yang dicatat harus jam di layar satpam');
  } finally {
    db.close();
  }
});

// ─── Ringkasan jam (dashboard) ──────────────────────────────────────────────────────────────────────

test('ringkasan jam memberi 24 baris, masuk dan keluar per jam', () => {
  const { db, gerbang } = siapkan();
  try {
    for (const [waktu, arah] of [
      ['2026-10-26T07:10:00', 'masuk'],
      ['2026-10-26T07:40:00', 'masuk'],
      ['2026-10-26T08:05:00', 'masuk'],
      ['2026-10-26T17:30:00', 'keluar'],
      ['2026-10-26T17:45:00', 'keluar'],
    ]) {
      catatKejadian(db, { gerbangId: gerbang.id, waktu, arah, plat: 'L 1234 AB' });
    }

    const ringkasan = ringkasanJam(db, gerbang.id, '2026-10-26');
    assert.equal(ringkasan.length, 24, 'dashboard butuh 24 batang, termasuk jam yang kosong');
    assert.deepEqual(ringkasan[7], { jam: 7, masuk: 2, keluar: 0 });
    assert.deepEqual(ringkasan[8], { jam: 8, masuk: 1, keluar: 0 });
    assert.deepEqual(ringkasan[17], { jam: 17, masuk: 0, keluar: 2 });
    assert.deepEqual(ringkasan[0], { jam: 0, masuk: 0, keluar: 0 });
  } finally {
    db.close();
  }
});

test('ringkasan jam hanya menghitung tanggal dan gerbang yang diminta', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-26T07:10:00', arah: 'masuk', plat: 'L 1 A' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: '2026-10-25T07:10:00', arah: 'masuk', plat: 'L 2 B' });
    catatKejadian(db, { gerbangId: lain.id, waktu: '2026-10-26T07:10:00', arah: 'masuk', plat: 'L 3 C' });

    const ringkasan = ringkasanJam(db, gerbang.id, '2026-10-26');
    assert.deepEqual(ringkasan[7], { jam: 7, masuk: 1, keluar: 0 });
    assert.equal(ringkasan.reduce((j, b) => j + b.masuk + b.keluar, 0), 1);
  } finally {
    db.close();
  }
});
