// Uji tgt/web/qr.js: pembuat QR untuk undangan tamu (Rencana T3 Task 4).
//
// ⚠️ Apa yang berkas ini BISA dan TIDAK BISA buktikan.
// Ia memeriksa susunan matriksnya dan MEMBACA BALIK isinya dengan kode kita sendiri. Itu menangkap kesalahan
// penempatan, topeng, dan koreksi galat — tetapi TIDAK membuktikan pemindai sungguhan bisa membacanya, karena
// pembaca baliknya buatan kita juga. Pembuktian sebenarnya memakai pembaca bawaan peramban (BarcodeDetector),
// dijalankan terpisah di peramban. Selama itu belum ada, QR tidak boleh disebut bekerja.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buatQr, kapasitas, bacaKembali } from '../web/qr.js';

const CONTOH = 'http://198.51.100.200:8787/undangan.html?kode=7PD7HQ';

// ─── Susunan dasar ──────────────────────────────────────────────────────────────────────────────────

test('ukuran matriks mengikuti versinya: 4 x versi + 17', () => {
  for (const teks of ['A', CONTOH, 'x'.repeat(150)]) {
    const qr = buatQr(teks);
    assert.equal(qr.ukuran, 4 * qr.versi + 17);
    assert.equal(qr.modul.length, qr.ukuran);
    assert.equal(qr.modul[0].length, qr.ukuran);
  }
});

test('pola pencari ada di tiga sudut, dan TIDAK ada di sudut kanan bawah', () => {
  const qr = buatQr(CONTOH);
  const n = qr.ukuran;
  // Pola pencari: kotak 7x7, tepi hitam, cincin putih, inti 3x3 hitam.
  const pencariDi = (y0, x0) => {
    for (let y = 0; y < 7; y += 1) {
      for (let x = 0; x < 7; x += 1) {
        const tepi = y === 0 || y === 6 || x === 0 || x === 6;
        const inti = y >= 2 && y <= 4 && x >= 2 && x <= 4;
        if (qr.modul[y0 + y][x0 + x] !== (tepi || inti)) return false;
      }
    }
    return true;
  };
  assert.ok(pencariDi(0, 0), 'pola pencari kiri atas salah');
  assert.ok(pencariDi(0, n - 7), 'pola pencari kanan atas salah');
  assert.ok(pencariDi(n - 7, 0), 'pola pencari kiri bawah salah');
  assert.ok(!pencariDi(n - 7, n - 7), 'kanan bawah tidak boleh berpola pencari');
});

test('pola waktu berselang-seling di baris dan kolom ke-6', () => {
  const qr = buatQr(CONTOH);
  for (let i = 8; i < qr.ukuran - 8; i += 1) {
    assert.equal(qr.modul[6][i], i % 2 === 0, `pola waktu mendatar salah di ${i}`);
    assert.equal(qr.modul[i][6], i % 2 === 0, `pola waktu tegak salah di ${i}`);
  }
});

test('modul gelap wajib ada di tempat tetapnya', () => {
  const qr = buatQr(CONTOH);
  assert.equal(qr.modul[4 * qr.versi + 9][8], true);
});

// ─── Baca balik ─────────────────────────────────────────────────────────────────────────────────────

test('isi QR terbaca kembali sama persis, untuk berbagai panjang teks', () => {
  for (const teks of [
    'A',
    'TAMU-7PD7HQ',
    CONTOH,
    'http://contoh.local/undangan.html?kode=ABC123&nama=Tamu%20Contoh',
    'x'.repeat(100),
  ]) {
    const terbaca = bacaKembali(buatQr(teks));
    assert.equal(terbaca, teks, `teks sepanjang ${teks.length} tidak terbaca kembali`);
  }
});

test('huruf di luar ASCII tetap utuh (nama tamu bisa memakai tanda baca)', () => {
  const teks = 'Tamu: Ani Contoh — gerbang selatan';
  assert.equal(bacaKembali(buatQr(teks)), teks);
});

test('QR yang sama dibuat dua kali menghasilkan matriks yang sama persis', () => {
  const a = buatQr(CONTOH);
  const b = buatQr(CONTOH);
  assert.deepEqual(a.modul, b.modul);
});

// ─── Batas ──────────────────────────────────────────────────────────────────────────────────────────

test('teks yang terlalu panjang DITOLAK, bukan dipotong diam-diam', () => {
  const batas = kapasitas(10, 'M');
  assert.ok(batas > 100 && batas < 300, `kapasitas versi 10 di luar dugaan: ${batas}`);

  // Pas di batas masih boleh; satu huruf lebih ditolak.
  assert.ok(buatQr('x'.repeat(batas)).versi <= 10);
  assert.throws(() => buatQr('x'.repeat(batas + 1)), /panjang|muat/i);
});

test('teks kosong ditolak', () => {
  for (const teks of ['', null, undefined]) {
    assert.throws(() => buatQr(teks), /kosong|teks/i);
  }
});

test('versi naik saat teks memanjang, dan tidak pernah turun', () => {
  let versiSebelum = 0;
  for (const panjang of [5, 20, 40, 80, 120, 160, 200]) {
    const versi = buatQr('x'.repeat(panjang)).versi;
    assert.ok(versi >= versiSebelum, `versi turun dari ${versiSebelum} ke ${versi} di panjang ${panjang}`);
    versiSebelum = versi;
  }
});

// ─── Keterangan format: urutan bitnya, terhadap nilai baku ──────────────────────────────────────────

/**
 * Nilai baku keterangan format untuk taraf M, topeng 0-7. Bukan disalin dari ingatan: tiap nilai diturunkan
 * ulang di uji berikutnya dengan BCH(15,5) dari standar, jadi kalau tabel ini salah ketik, ujinya merah.
 */
const FORMAT_M = [
  '101010000010010', '101000100100101', '101111001111100', '101101101001011',
  '100010111111001', '100000011001110', '100111110010111', '100101010100000',
];

test('nilai baku keterangan format benar menurut BCH(15,5), bukan sekadar disalin', () => {
  for (let topeng = 0; topeng < 8; topeng += 1) {
    const data = (0b00 << 3) | topeng; // taraf M = 00
    let sisa = data;
    for (let i = 0; i < 10; i += 1) sisa = (sisa << 1) ^ (((sisa >> 9) & 1) * 0x537);
    const nilai = ((((data << 10) | sisa) ^ 0x5412) & 0x7fff).toString(2).padStart(15, '0');
    assert.equal(nilai, FORMAT_M[topeng], `nilai baku topeng ${topeng} salah`);
  }
});

test('⛔ keterangan format ditulis dari bit TERBESAR dulu, di kedua salinannya', () => {
  // Cacat yang pernah terjadi (26 Okt): urutannya terbalik. Wilayah datanya sudah benar persis sama dengan
  // QR rujukan, tetapi seluruh keterangan formatnya terbalik, jadi TIDAK ADA pemindai yang bisa membacanya.
  // bacaKembali() memakai urutan yang sama, jadi ia tidak pernah menangkapnya.
  const qr = buatQr(CONTOH);
  const n = qr.ukuran;
  const baku = FORMAT_M[qr.topeng];

  const salinan1 = [
    [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 7], [8, 8],
    [7, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8],
  ];
  const salinan2 = [
    ...Array.from({ length: 7 }, (_, i) => [n - 1 - i, 8]),
    ...Array.from({ length: 8 }, (_, i) => [8, n - 8 + i]),
  ];

  for (const [nama, daftar] of [['salinan 1', salinan1], ['salinan 2', salinan2]]) {
    const terbaca = daftar.map(([y, x]) => (qr.modul[y][x] ? '1' : '0')).join('');
    assert.equal(terbaca, baku, `${nama} keterangan format salah urutan atau salah letak`);
  }
});

test('modul gelap menimpa bit terakhir salinan kedua, bukan sebaliknya', () => {
  const qr = buatQr(CONTOH);
  assert.equal(qr.modul[qr.ukuran - 8][8], true);
});
