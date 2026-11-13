#!/usr/bin/env node
// Pemeriksa SEBELUM repo ini diunggah ke GitHub (permintaan owner 6 Nov 2026: repo untuk partner bisnis).
//
// ⛔ Mengunggah = menerbitkan. Repo privat pun tersimpan di server pihak lain, dan riwayat git tidak bisa ditarik
// kembali begitu sudah tersalin. CLAUDE.md §4: foto dan rekaman plat, nama penghuni, dan jam keluar masuk TIDAK
// PERNAH di-push. Pemeriksa ini memeriksa SELURUH RIWAYAT, bukan hanya isi sekarang — berkas yang pernah
// di-commit lalu dihapus tetap ada di riwayat dan ikut terunggah.
//
// ⛔ Pemeriksa ini TIDAK PERNAH mencetak isi yang dicurigai. Bila ada nomor plat sungguhan di riwayat, mencetaknya
// ke layar sudah mengirimnya ke layanan AI (CLAUDE.md §4). Yang dicetak hanya NAMA BERKAS dan JUMLAH.
//
// Kontrol positif dijalankan lebih dulu (CLAUDE.md §7): pemeriksa yang melapor "0 ketemu" karena polanya salah
// tidak bisa dibedakan dari pemeriksa yang melapor bersih.
//
//   node tools/periksa-sebelum-push.mjs          → keluar 0 bila bersih, 1 bila ada yang harus diperiksa manusia
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';

const git = (...a) => {
  const r = spawnSync('git', a, { encoding: 'utf8', maxBuffer: 512 * 1024 * 1024 });
  if (r.status !== 0) throw new Error(`git ${a[0]} gagal: ${r.stderr.trim().slice(0, 200)}`);
  return r.stdout;
};

// Plat Indonesia: 1–2 huruf wilayah, 1–4 angka, 1–3 huruf seri. Sengaja longgar — lebih baik curiga berlebihan.
// Pencocokan sungguhan terhadap plat di data/ ada di tools/cocokkan-plat-riwayat.mjs; alat ini hanya pemeriksa kasar.
const POLA_PLAT = /\b[A-Z]{1,2} ?\d{1,4} ?[A-Z]{1,3}\b/g;
// ⛔ Garis bawah dan tanda hubung dijadikan spasi dulu: "A 9999 AAA_9999" (bentuk nama berkas INDO-ALPR) tidak punya
// batas kata sesudah huruf serinya, jadi tanpa langkah ini ia lolos. Tertangkap 6 Nov sebelum push.
const cariPlat = (teks) => teks.replace(/[_-]/g, ' ').match(POLA_PLAT);
const POLA_RAHASIA = [
  ['kunci privat', /-----BEGIN [A-Z ]*PRIVATE KEY-----/],
  ['token GitHub', /\bgh[pousr]_[A-Za-z0-9]{30,}/],
  ['kunci Anthropic/OpenAI', /\bsk-(?:ant-)?[A-Za-z0-9_-]{30,}/],
  ['kunci AWS', /\bAKIA[0-9A-Z]{16}\b/],
  ['kunci Google', /\bAIza[0-9A-Za-z_-]{35}\b/],
  ['sandi tertulis', /(?:password|sandi|passwd)\s*[:=]\s*['"][^'"\s]{6,}['"]/i],
];

// Folder tempat plat KARANGAN memang ditulis dengan sengaja (uji, contoh di kode). Plat di sini bukan data orang.
const BOLEH_PLAT_KARANGAN = [/^tgt\/uji\//, /^tools\/uji\//, /^tools\/lab\/uji/, /^tgt\/web\//, /^tgt\/[a-z]+\.mjs$/,
  /^tools\/lab\/[a-z_]+\.py$/, /^tools\/[a-z-]+\.mjs$/];

// Jalur yang TIDAK BOLEH pernah ada di riwayat.
const JALUR_TERLARANG = [
  ['folder data/ (plat, video, basis data)', /^data\//],
  ['folder models/', /^models\//],
  ['video', /\.(mp4|mov|avi|mkv|webm)$/i],
  ['basis data', /\.(sqlite|sqlite3|db)$/i],
  ['bobot model', /\.(onnx|safetensors|keras|pt|pth|ckpt|pkl|h5)$/i],
  ['kunci VAPID / berkas rahasia', /(vapid\.json|\.env|id_rsa|id_ed25519|\.pem|\.key)$/i],
];

let masalah = 0;
const lapor = (judul, isi) => { console.log(`\n⚠  ${judul}`); for (const b of isi) console.log(`   ${b}`); masalah += 1; };

// ─── 0. Kontrol positif ─────────────────────────────────────────────────────────────────────────────
for (const contohPlat of ['kendaraan B 1234 XYZ lewat', 'B 1234 XYZ_1234']) {
  if (!(cariPlat(contohPlat) ?? []).length) throw new Error(`kontrol positif GAGAL: pola plat tidak menemukan "${contohPlat}"`);
}
if (!POLA_RAHASIA[1][1].test(`gho_${'A'.repeat(36)}`)) throw new Error('kontrol positif GAGAL: pola token tidak bekerja');
if (!JALUR_TERLARANG[0][1].test('data/keluaran/x.json')) throw new Error('kontrol positif GAGAL: pola jalur tidak bekerja');
console.log('kontrol positif: ketiga pola terbukti bisa menemukan yang dicari');

// ─── 1. Semua berkas yang PERNAH ada di riwayat ─────────────────────────────────────────────────────
const pernahAda = [...new Set(git('log', '--all', '--name-only', '--pretty=format:').split('\n').filter(Boolean))];
console.log(`\nberkas yang pernah ada di riwayat: ${pernahAda.length}`);
for (const [nama, pola] of JALUR_TERLARANG) {
  const kena = pernahAda.filter((j) => pola.test(j));
  if (kena.length) lapor(`${nama} PERNAH masuk riwayat (${kena.length} berkas)`, kena.slice(0, 15));
}

// ─── 2. Gambar yang ikut terunggah ─────────────────────────────────────────────────────────────────
const gambar = pernahAda.filter((j) => /\.(png|jpe?g|gif|webp|bmp)$/i.test(j));
console.log(`gambar di riwayat: ${gambar.length}`);
for (const g of gambar) console.log(`   ${g}`);

// ─── 3. Ukuran: GitHub menolak berkas > 100 MB, memperingatkan > 50 MB ──────────────────────────────
const besar = git('rev-list', '--objects', '--all').split('\n').filter(Boolean)
  .map((b) => b.split(' ')).filter((b) => b[1]);
const ukuran = git('cat-file', '--batch-check=%(objectname) %(objectsize)', '--batch-all-objects')
  .split('\n').filter(Boolean).map((b) => b.split(' ')).reduce((m, [h, s]) => m.set(h, Number(s)), new Map());
const besarSekali = besar.map(([h, j]) => [j, ukuran.get(h) ?? 0]).filter(([, s]) => s > 20 * 1024 * 1024)
  .sort((a, b) => b[1] - a[1]);
if (besarSekali.length) lapor('berkas di atas 20 MB', besarSekali.map(([j, s]) => `${(s / 1048576).toFixed(1)} MB  ${j}`));

// ─── 4. Isi seluruh riwayat: rahasia dan pola plat ─────────────────────────────────────────────────
// Semua versi tiap berkas teks, bukan hanya yang terakhir.
const isiRiwayat = git('log', '--all', '-p', '--no-color', '--text', '--', '.', ':!*.png', ':!*.jpg', ':!*.jpeg');
let berkasKini = '';
const rahasiaKena = new Map();
const platPerBerkas = new Map();
for (const baris of isiRiwayat.split('\n')) {
  const m = /^\+\+\+ b\/(.+)$/.exec(baris);
  if (m) { berkasKini = m[1]; continue; }
  if (!baris.startsWith('+') || baris.startsWith('+++')) continue;
  for (const [nama, pola] of POLA_RAHASIA) {
    // Sandi CONTOH di uji TGT (sandi-contoh-1, sandi-salah-99, …) diperiksa satu per satu 6 Nov dan palsu semua.
    // Hanya nilai itu yang dikecualikan, bukan seluruh folder uji: sandi sungguhan bisa saja tertinggal di uji.
    // Pemeriksa yang selalu gagal karena hal yang sudah diketahui akan diabaikan orang, dan berhenti menjadi pagar.
    if (nama === 'sandi tertulis' && /sandi-(contoh|salah|lain|baru|uji|benar)/i.test(baris)) continue;
    if (pola.test(baris)) rahasiaKena.set(`${nama} — ${berkasKini}`, (rahasiaKena.get(`${nama} — ${berkasKini}`) ?? 0) + 1);
  }
  if (BOLEH_PLAT_KARANGAN.some((p) => p.test(berkasKini))) continue;
  const plat = cariPlat(baris);
  if (plat) platPerBerkas.set(berkasKini, (platPerBerkas.get(berkasKini) ?? 0) + plat.length);
}
if (rahasiaKena.size) lapor('kemungkinan RAHASIA di riwayat (isinya tidak dicetak)',
  [...rahasiaKena].map(([k, n]) => `${n}×  ${k}`));

// Plat-mirip di luar folder uji: TIDAK otomatis masalah (banyak dokumen memuat contoh karangan, kode keputusan
// seperti "K 74", atau singkatan). Dicetak sebagai daftar berkas untuk diperiksa, tanpa isinya.
const platTerurut = [...platPerBerkas].sort((a, b) => b[1] - a[1]);
console.log(`\nberkas di luar folder uji yang memuat pola mirip plat: ${platTerurut.length}`);
console.log('(isinya TIDAK dicetak — hanya nama berkas dan jumlah; yang mencurigakan diperiksa manusia)');
for (const [j, n] of platTerurut.slice(0, 40)) console.log(`   ${String(n).padStart(4)}×  ${j}`);

// ─── 5. Rincian server (K77, owner 6 Nov 2026): tidak masuk repo yang dibagikan ke partner ──────────
//
// Dua lapis. (a) Pola umum: alamat Tailscale (rentang CGNAT 100.64/10) dan alamat jaringan lokal — menangkap alamat BARU yang
// belum pernah dicatat. (b) Daftar persis dari catatan-lokal/ganti.json, yang di-gitignore: daftar itu TIDAK ditulis
// di sini, karena berkas ini ikut terunggah, dan daftar larangan yang terunggah membocorkan isinya sendiri.
// Yang dicetak hanya nama pola dan nama berkas, tidak pernah nilainya.
const POLA_SERVER = [
  ['alamat Tailscale', /\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b/],
  ['alamat jaringan lokal', /\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b/],
];
// Alamat contoh kontrol positif DISUSUN saat berjalan: bila ditulis utuh di sini, pemeriksa ini menandai dirinya
// sendiri pada setiap jalan — dan pemeriksa yang selalu gagal karena hal yang diketahui akan diabaikan orang.
const contohTailscale = ['100', '64', '1', '2'].join('.');
const contohLokal = ['192', '168', '1', '5'].join('.');
if (!POLA_SERVER[0][1].test(contohTailscale) || !POLA_SERVER[1][1].test(contohLokal)) {
  throw new Error('kontrol positif GAGAL: pola alamat server tidak bekerja');
}
let larangan = [];
try {
  larangan = JSON.parse(fs.readFileSync('catatan-lokal/ganti.json', 'utf8')).pengganti.map(([dari], i) => [`rincian server #${i + 1}`, dari]);
  console.log(`\ndaftar larangan rincian server: ${larangan.length} butir (dari catatan-lokal/, isinya tidak dicetak)`);
} catch {
  console.log('\ncatatan-lokal/ganti.json tidak ada: hanya pola umum alamat server yang diperiksa');
}
const pesanCommit = git('log', '--all', '--format=%B');
const kenaServer = new Map();
const tambahKena = (nama, tempat) => kenaServer.set(`${nama} — ${tempat}`, (kenaServer.get(`${nama} — ${tempat}`) ?? 0) + 1);
let berkasServer = '';
for (const baris of isiRiwayat.split('\n')) {
  const m = /^\+\+\+ b\/(.+)$/.exec(baris);
  if (m) { berkasServer = m[1]; continue; }
  if (!baris.startsWith('+') || baris.startsWith('+++')) continue;
  for (const [nama, pola] of POLA_SERVER) if (pola.test(baris)) tambahKena(nama, berkasServer);
  for (const [nama, teks] of larangan) if (baris.includes(teks)) tambahKena(nama, berkasServer);
}
for (const baris of pesanCommit.split('\n')) {
  for (const [nama, pola] of POLA_SERVER) if (pola.test(baris)) tambahKena(nama, 'pesan commit');
  for (const [nama, teks] of larangan) if (baris.includes(teks)) tambahKena(nama, 'pesan commit');
}
if (kenaServer.size) lapor('RINCIAN SERVER di riwayat (K77: tidak masuk repo; isinya tidak dicetak)',
  [...kenaServer].map(([k, n]) => `${n}×  ${k}`));
else console.log('rincian server di isi berkas dan pesan commit: tidak ada');

console.log(`\n${masalah === 0 ? 'TIDAK ADA temuan yang menghalangi' : `${masalah} temuan harus diperiksa sebelum push`}`);
process.exit(masalah === 0 ? 0 : 1);
