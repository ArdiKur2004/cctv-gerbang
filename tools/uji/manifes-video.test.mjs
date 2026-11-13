// Uji tools/manifes-video.mjs: daftar asal-usul video riset (D16, D17). Video tinggal di data/ (di-gitignore);
// yang masuk repo hanya manifesnya: dari mana tiap berkas berasal, SHA-256-nya, dan tanda RISET-SAJA.
//
// Asal: disalin dari vision-seed @3591530 (tools/uji/manifes-video.test.mjs) pada 2026-10-13 (K14). Yang diubah di sini:
// uji berkas suara dibuang (proyek ini tidak mengambil suara), dan pilihan `sudut` diganti untuk kamera gerbang.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'manifes-video.mjs');

const jalurUtuh = (folder) => path.join(folder, '..', `${path.basename(folder)}-utuh.json`);

// Catatan keutuhan seperti yang ditulis tools/lab/periksa_utuh.py: nama video -> ukurannya dalam byte.
function catatUtuh(folder, ubah = (daftar) => daftar) {
  const daftar = Object.fromEntries(fs.readdirSync(folder).filter((n) => n.endsWith('.mp4'))
    .map((n) => [n, fs.statSync(path.join(folder, n)).size]));
  fs.writeFileSync(jalurUtuh(folder), JSON.stringify({ utuh: ubah(daftar), rusak: {} }));
}

function siapkan(berkas) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-riset-'));
  for (const [nama, isi] of Object.entries(berkas)) fs.writeFileSync(path.join(folder, nama), typeof isi === 'string' ? isi : JSON.stringify(isi));
  catatUtuh(folder);
  return { folder, manifes: path.join(folder, '..', `${path.basename(folder)}-manifes.json`) };
}

function jalankan(folder, manifes) {
  const r = spawnSync('node', [SKRIP, folder, manifes, jalurUtuh(folder)], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}

const INFO = {
  id: 'abc123', extractor: 'youtube', webpage_url: 'https://www.youtube.com/watch?v=abc123', title: 'SOP kasir',
  channel: 'Toko Contoh', channel_id: 'UC1', upload_date: '20240131', duration: 116, license: null, width: 640, height: 352, fps: 25,
  formats: [{ besar: 'x'.repeat(5000) }], description: 'panjang sekali '.repeat(500),
};

test('tiap video dicatat asal-usulnya, SHA-256-nya, dan ditandai RISET-SAJA', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 0, r.keluar);
  const m = JSON.parse(fs.readFileSync(manifes, 'utf8'));
  assert.equal(m.video.length, 1);
  const v = m.video[0];
  assert.equal(v.berkas, 'youtube-abc123.mp4');
  assert.equal(v.sumber, 'https://www.youtube.com/watch?v=abc123');
  assert.equal(v.judul, 'SOP kasir');
  assert.equal(v.kanal, 'Toko Contoh');
  assert.equal(v.tanggal_unggah, '2024-01-31');
  assert.equal(v.detik, 116);
  assert.equal(v.ukuran, '640x352');
  assert.equal(v.sha256, crypto.createHash('sha256').update('isi-video').digest('hex'));
  assert.equal(v.vonis, 'RISET-SAJA');
  assert.match(v.lisensi, /tidak dinyatakan/);
  assert.ok(!JSON.stringify(m).includes('panjang sekali'), 'deskripsi & daftar format tak ikut disalin');
});

test('lisensi Creative Commons dari sumber dicatat apa adanya, vonis tetap RISET-SAJA sampai dibaca manusia', () => {
  const { folder, manifes } = siapkan({
    'youtube-cc1.mp4': 'x', 'youtube-cc1.info.json': { ...INFO, id: 'cc1', license: 'Creative Commons Attribution license (reuse allowed)' },
  });

  jalankan(folder, manifes);

  const v = JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0];
  assert.match(v.lisensi, /Creative Commons Attribution/);
  assert.equal(v.vonis, 'RISET-SAJA');
});

test('isian tangan (kategori, isi) bertahan saat manifes dibuat ulang', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  jalankan(folder, manifes);
  const m = JSON.parse(fs.readFileSync(manifes, 'utf8'));
  m.video[0].kategori = 'pelayanan';
  m.video[0].isi = 'peragaan salam kasir';
  fs.writeFileSync(manifes, JSON.stringify(m));
  fs.writeFileSync(path.join(folder, 'youtube-baru.mp4'), 'lain');
  fs.writeFileSync(path.join(folder, 'youtube-baru.info.json'), JSON.stringify({ ...INFO, id: 'baru', webpage_url: 'https://youtu.be/baru' }));
  catatUtuh(folder);

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 0, r.keluar);
  const sesudah = JSON.parse(fs.readFileSync(manifes, 'utf8'));
  assert.deepEqual(sesudah.video.map((v) => v.berkas), ['youtube-abc123.mp4', 'youtube-baru.mp4']);
  assert.equal(sesudah.video[0].kategori, 'pelayanan');
  assert.equal(sesudah.video[0].isi, 'peragaan salam kasir');
  assert.equal(sesudah.video[1].kategori, '');
});

test('video tanpa berkas asal-usul ditolak: manifes tidak ditulis (kode 1)', () => {
  const { folder, manifes } = siapkan({ 'entah-dari-mana.mp4': 'isi' });

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /entah-dari-mana\.mp4/);
  assert.ok(!fs.existsSync(manifes));
});

test('berkas yang isinya berubah sejak dicatat ditolak (kode 1)', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  jalankan(folder, manifes);
  fs.writeFileSync(path.join(folder, 'youtube-abc123.mp4'), 'isi-ditukar');

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /berubah/);
});

test('catatan video tidak memuat kolom suara: proyek ini tidak mengambil suara', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });

  jalankan(folder, manifes);

  assert.ok(!('suara' in JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0]));
});

test('sudut kamera (isian tangan) bertahan, dan nilai di luar daftar ditolak (kode 1)', () => {
  // Angka lulus (K9) hanya sah dari kamera di posisi gerbang. Tiap video ditandai sudutnya setelah dilihat; salah
  // ketik tak boleh lolos diam-diam karena kolom ini dipakai memilih video ukur.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  jalankan(folder, manifes);
  const m = JSON.parse(fs.readFileSync(manifes, 'utf8'));
  assert.equal(m.video[0].sudut, '');
  m.video[0].sudut = 'gerbang';
  fs.writeFileSync(manifes, JSON.stringify(m));

  let r = jalankan(folder, manifes);

  assert.equal(r.kode, 0, r.keluar);
  assert.equal(JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0].sudut, 'gerbang');
  m.video[0].sudut = 'cctv-kasir'; // pilihan vision-seed, bukan pilihan proyek ini
  fs.writeFileSync(manifes, JSON.stringify(m));
  r = jalankan(folder, manifes);
  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /sudut/);
  assert.equal(JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0].sudut, 'cctv-kasir'); // manifes tidak ditimpa
});

for (const sudut of ['gerbang', 'parkiran', 'kamera-diam-lain', 'dasbor', 'lain']) {
  test(`sudut "${sudut}" diterima`, () => {
    const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
    jalankan(folder, manifes);
    const m = JSON.parse(fs.readFileSync(manifes, 'utf8'));
    m.video[0].sudut = sudut;
    fs.writeFileSync(manifes, JSON.stringify(m));

    const r = jalankan(folder, manifes);

    assert.equal(r.kode, 0, r.keluar);
  });
}

test('video baru yang tidak tercatat utuh ditolak: manifes tidak ditulis (kode 1)', () => {
  // Temuan K20: satu unduhan meninggalkan .mp4 yang tak bisa dibuka, dan berkas itu nyaris tercatat sebagai bahan.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  catatUtuh(folder, () => ({}));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /belum tercatat utuh/);
  assert.ok(!fs.existsSync(manifes));
});

test('video baru yang ukurannya berbeda dari catatan keutuhan ditolak (kode 1)', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  catatUtuh(folder, (daftar) => ({ 'youtube-abc123.mp4': daftar['youtube-abc123.mp4'] + 1 }));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /belum tercatat utuh/);
});

test('tanpa berkas catatan keutuhan sama sekali, video baru ditolak: gagal tertutup', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  fs.rmSync(jalurUtuh(folder));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.ok(!fs.existsSync(manifes));
});

test('video yang sudah tercatat di manifes tidak menuntut catatan keutuhan lagi', () => {
  // Yang sudah tercatat dijaga SHA-256-nya; catatan keutuhan hanya pintu masuk bagi video baru.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  assert.equal(jalankan(folder, manifes).kode, 0);
  fs.rmSync(jalurUtuh(folder));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 0, r.keluar);
});

test('⛔ ukuran gambar dicatat dari BERKASNYA, bukan dari metadata sumbernya', () => {
  // Cacat nyata, 26 Okt 2026: satu video satu jam diunduh dengan batas resolusi, dan berkasnya menjadi
  // 640x360 — tetapi manifes mencatat 1280x720, yaitu resolusi ASLI video di YouTube. Setiap angka
  // pengukuran yang memakai catatan itu akan menyesatkan, dan tidak ada yang akan tahu sebabnya.
  //
  // Yang benar: resolusi dibaca dari berkas yang ada di disk — itu dicatat tools/lab/periksa_utuh.py, yang
  // memang sudah membuka tiap berkas. Metadata sumber tetap disimpan terpisah sebagai `ukuran_sumber`.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  // INFO menyatakan 640x352; berkasnya ternyata 320x176 menurut pemeriksa keutuhan.
  const catatan = JSON.parse(fs.readFileSync(jalurUtuh(folder), 'utf8'));
  catatan.gambar = { 'youtube-abc123.mp4': '320x176' };
  fs.writeFileSync(jalurUtuh(folder), JSON.stringify(catatan));

  const { kode } = jalankan(folder, manifes);
  assert.equal(kode, 0);
  const v = JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0];
  assert.equal(v.ukuran, '320x176', 'manifes memakai resolusi sumber, bukan resolusi berkasnya');
  assert.equal(v.ukuran_sumber, '640x352', 'resolusi yang dinyatakan sumber hilang; keduanya perlu dibandingkan');
});

test('bila pemeriksa keutuhan belum mencatat ukuran gambar, manifes memakai metadata sumber', () => {
  // Catatan keutuhan yang dibuat sebelum 26 Okt tidak punya kunci `gambar`. Manifes tidak boleh kosong
  // ukurannya hanya karena catatannya lebih tua.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  const { kode } = jalankan(folder, manifes);
  assert.equal(kode, 0);
  const v = JSON.parse(fs.readFileSync(manifes, 'utf8')).video[0];
  assert.equal(v.ukuran, '640x352');
  assert.equal(v.ukuran_sumber, '640x352');
});
