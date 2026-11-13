#!/usr/bin/env node
// Manifes asal-usul video riset (keputusan owner K6, K15, K17).
// Video tinggal di data/video/riset/ (di-gitignore). Yang masuk repo hanya manifes ini: dari mana tiap berkas berasal,
// SHA-256-nya, lisensi yang dinyatakan sumbernya, dan vonis RISET-SAJA (tak boleh masuk build yang dijual).
//
// Asal: disalin dari vision-seed @3591530 (tools/manifes-video.mjs) pada 2026-10-13 (K14). Yang diubah di sini: berkas
// suara tidak dicatat (proyek ini tidak mengambil suara), pilihan `sudut` untuk kamera gerbang, dan letak manifes.
//
// Gagal tertutup: video tanpa berkas .info.json (asal tak diketahui) atau yang isinya berubah sejak dicatat => exit 1,
// manifes tidak ditulis. Isian tangan (`kategori`, `isi`, `sudut`) bertahan saat manifes dibuat ulang.
// `sudut` = sudut pandang kamera setelah videonya dilihat. Angka lulus (K9) hanya sah dari kamera di posisi gerbang:
// gerbang (kamera diam menghadap kendaraan yang masuk atau keluar gerbang/palang) · parkiran (kamera diam di parkiran
// gedung atau basement; spec Fase 1, K36) · kamera-diam-lain (kamera diam di jalan atau tempat lain, bukan di gerbang atau
// parkiran) · dasbor (kamera bergerak di kendaraan) · lain (HP, peragaan, layar perangkat lunak, wawancara). Nilai lain
// ditolak.
//
// Video BARU hanya dicatat bila lulus tools/lab/periksa_utuh.py (temuan K20: berkas yang ada belum tentu utuh).
// Urutannya: unduh -> periksa_utuh.py di lab -> alat ini.
//
// Pakai:  node tools/manifes-video.mjs [folder-video] [berkas-manifes] [berkas-catatan-utuh]
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AKAR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const folder = process.argv[2] ?? path.join(AKAR, 'data', 'video', 'riset');
const berkasManifes = process.argv[3] ?? path.join(AKAR, 'data-asal', 'video-riset.json');
const berkasUtuh = process.argv[4] ?? path.join(AKAR, 'data', 'keluaran', 'video-utuh.json');
const AKHIRAN_VIDEO = new Set(['.mp4', '.webm', '.mkv', '.mov']);
const ISIAN_TANGAN = ['kategori', 'isi', 'sudut'];
const SUDUT_SAH = new Set(['', 'gerbang', 'parkiran', 'kamera-diam-lain', 'dasbor', 'lain']);

const sha256 = (berkas) => new Promise((ok, gagal) => {
  const h = crypto.createHash('sha256');
  fs.createReadStream(berkas).on('data', (d) => h.update(d)).on('end', () => ok(h.digest('hex'))).on('error', gagal);
});
const tanggal = (t) => (/^\d{8}$/.test(t ?? '') ? `${t.slice(0, 4)}-${t.slice(4, 6)}-${t.slice(6, 8)}` : null);

const lama = fs.existsSync(berkasManifes) ? JSON.parse(fs.readFileSync(berkasManifes, 'utf8')) : { video: [] };
const lamaPerBerkas = new Map(lama.video.map((v) => [v.berkas, v]));
// Catatan keutuhan dari tools/lab/periksa_utuh.py. Tanpa catatan yang terbaca, tidak ada video baru yang diterima.
let utuh = {};
let gambar = {};
try {
  const catatan = JSON.parse(fs.readFileSync(berkasUtuh, 'utf8'));
  utuh = catatan.utuh ?? {};
  // Catatan yang dibuat sebelum 26 Okt tidak punya kunci `gambar`; manifes lalu memakai metadata sumber.
  gambar = catatan.gambar ?? {};
} catch { /* gagal tertutup di bawah */ }
const galat = [];
const video = [];
for (const nama of fs.readdirSync(folder).filter((n) => AKHIRAN_VIDEO.has(path.extname(n).toLowerCase())).sort()) {
  const berkasInfo = path.join(folder, `${path.basename(nama, path.extname(nama))}.info.json`);
  if (!fs.existsSync(berkasInfo)) { galat.push(`${nama}: tanpa berkas .info.json, asal-usul tak diketahui`); continue; }
  const info = JSON.parse(fs.readFileSync(berkasInfo, 'utf8'));
  const dulu = lamaPerBerkas.get(nama);
  if (!dulu && utuh[nama] !== fs.statSync(path.join(folder, nama)).size) {
    galat.push(`${nama}: belum tercatat utuh di ${path.basename(berkasUtuh)}. Jalankan tools/lab/periksa_utuh.py lebih dulu`);
    continue;
  }
  const hash = await sha256(path.join(folder, nama));
  if (dulu && dulu.sha256 !== hash) { galat.push(`${nama}: isi berubah sejak dicatat (${dulu.sha256.slice(0, 12)} -> ${hash.slice(0, 12)})`); continue; }
  if (!SUDUT_SAH.has(dulu?.sudut ?? '')) { galat.push(`${nama}: sudut "${dulu.sudut}" tak dikenal (pilihan: ${[...SUDUT_SAH].filter(Boolean).join(', ')})`); continue; }
  video.push({
    berkas: nama,
    sumber: info.webpage_url,
    situs: info.extractor,
    judul: info.title,
    kanal: info.channel ?? info.uploader ?? null,
    tanggal_unggah: tanggal(info.upload_date),
    detik: info.duration ?? null,
    // ⛔ Ukuran gambar dibaca dari BERKASNYA (dicatat tools/lab/periksa_utuh.py), bukan dari .info.json.
    // Sebabnya, 26 Okt 2026: satu video satu jam diunduh dengan batas resolusi dan berkasnya menjadi 640x360,
    // tetapi .info.json menyatakan 1280x720 — yaitu resolusi aslinya di sumber. Manifes mencatat 1280x720, dan
    // setiap angka pengukuran yang memakainya akan menyesatkan tanpa ada yang tahu sebabnya.
    // Yang dinyatakan sumber tetap disimpan sebagai `ukuran_sumber`, supaya keduanya bisa dibandingkan.
    ukuran: gambar[nama] ?? (info.width && info.height ? `${info.width}x${info.height}` : null),
    ukuran_sumber: info.width && info.height ? `${info.width}x${info.height}` : null,
    lisensi: info.license ?? 'tidak dinyatakan sumber (lisensi standar situs)',
    vonis: 'RISET-SAJA',
    sha256: hash,
    dicatat: dulu?.dicatat ?? new Date().toISOString().slice(0, 10),
    ...Object.fromEntries(ISIAN_TANGAN.map((k) => [k, dulu?.[k] ?? ''])),
  });
}
if (galat.length) {
  for (const g of galat) console.error(`DITOLAK ${g}`);
  console.error(`${galat.length} berkas bermasalah; manifes tidak ditulis.`);
  process.exit(1);
}
const manifes = {
  _tentang: 'Asal-usul video RISET (K6, K15, K17). Videonya di data/video/riset/ (di-gitignore), diambil lewat tools/ambil-video.ps1. ' +
    'vonis RISET-SAJA = boleh dipelajari di laptop, DILARANG masuk build yang dijual dan tak boleh disebarkan ulang. ' +
    'Plat nomor di dalam video adalah data pribadi. ' +
    'kategori, isi, dan sudut (sudut pandang kamera) diisi tangan setelah videonya dilihat.',
  video,
};
fs.mkdirSync(path.dirname(berkasManifes), { recursive: true });
fs.writeFileSync(berkasManifes, `${JSON.stringify(manifes, null, 2)}\n`);
console.log(`${video.length} video dicatat di ${berkasManifes}`);
