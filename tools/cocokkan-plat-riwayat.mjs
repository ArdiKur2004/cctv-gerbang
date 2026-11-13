#!/usr/bin/env node
// Apakah ada NOMOR PLAT SUNGGUHAN di riwayat git repo ini? Dijalankan sebelum repo diunggah ke GitHub.
//
// ⛔ Kenapa alat ini ada (6 Nov 2026). Mengunggah = menerbitkan; riwayat git tidak bisa ditarik kembali begitu
// tersalin. CLAUDE.md §4: plat, nama penghuni, dan jam keluar masuk TIDAK PERNAH di-push. Pemeriksaan yang menentukan
// bukan menebak dari bentuknya, melainkan MENCOCOKKAN semua pola mirip plat di riwayat git dengan plat sungguhan
// yang ada di data/. Riwayat dipindai SEPENUHNYA: berkas yang pernah di-commit lalu dihapus tetap ikut terunggah.
//
// ⛔ Dua pelajaran dari menulis alat ini, keduanya tertangkap sebelum push:
// 1. Sumber "plat sungguhan" harus sumber yang PASTI berisi plat. Versi pertama mengambil pola dari SEMUA isi JSON
//    di data/ — termasuk ID video YouTube dan nama artefak, yang juga ada di repo sebagai catatan asal-usul — dan
//    melaporkan 28 "cocok" yang ternyata tabrakan kebetulan.
// 2. Garis bawah dan tanda hubung WAJIB dijadikan spasi lebih dulu. Nama berkas INDO-ALPR berbentuk
//    "A 9999 AAA_9999", dan garis bawah dianggap bagian kata, jadi batas kata (\b) tidak pernah terjadi. Tanpa
//    langkah ini, 6.174 nama berkas menyumbang hanya 4 pola, dan "nol cocok" tidak bermakna apa pun — persis
//    jebakan pemeriksa yang melapor nol karena polanya salah (CLAUDE.md §7).
//
// ⛔ Alat ini MEMBUKA berkas berplat di data/, seperti alat lab yang membuka berkas berplat lalu hanya mengeluarkan
// ringkasan. Yang DICETAK hanya JUMLAH per sumber. Tidak ada nomor plat yang dicetak, dan pesan galat tidak memuat
// jalur di data/ (jalur di sana bisa memuat nomor plat).
//
//   node tools/cocokkan-plat-riwayat.mjs     → keluar 0 bila nol pola sepanjang plat cocok, 1 bila ada, 2 bila sumber kosong
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const POLA = /\b[A-Z]{1,2} ?\d{1,4} ?[A-Z]{1,3}\b/g;
const baku = (t) => t.replace(/\s+/g, '').toUpperCase();
export const ambil = (t) => (String(t).toUpperCase().replace(/[_-]/g, ' ').match(POLA) ?? []).map(baku);
// Plat sungguhan hampir selalu 6–9 karakter. Yang 3–4 karakter yang cocok adalah token seperti nama model mobil;
// dilaporkan terpisah, tidak disembunyikan.
const PANJANG_PLAT = 5;

// ─── 0. Kontrol positif, termasuk kasus garis bawah yang dulu lolos ─────────────────────────────────
for (const [contoh, harus] of [['B 1234 XYZ_1234', 'B1234XYZ'], ['D_1234_AB', 'D1234AB'], ['kendaraan L 77 KQ lewat', 'L77KQ']]) {
  if (!ambil(contoh).includes(harus)) throw new Error(`kontrol positif GAGAL: "${contoh}" tidak menghasilkan ${harus}`);
}
console.log('kontrol positif: pola menangkap plat berspasi, bergaris bawah, dan bertanda hubung');

function semuaBerkas(folder) {
  const keluar = [];
  const jalan = (f) => {
    let isi;
    try { isi = fs.readdirSync(f, { withFileTypes: true }); } catch { return; }
    for (const b of isi) {
      const j = path.join(f, b.name);
      if (b.isDirectory()) jalan(j); else keluar.push(j);
    }
  };
  jalan(folder);
  return keluar;
}
const nilaiJson = (v, out) => {
  if (typeof v === 'string') out.push(v);
  else if (Array.isArray(v)) v.forEach((x) => nilaiJson(x, out));
  else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => { out.push(k); nilaiJson(x, out); });
  return out;
};
const isiTeks = (j) => {
  let t;
  try { t = fs.readFileSync(j, 'utf8'); } catch { return []; }
  if (/\.jsonl$/i.test(j)) return t.split('\n').filter(Boolean).flatMap((l) => { try { return nilaiJson(JSON.parse(l), []); } catch { return []; } });
  if (/\.json$/i.test(j)) { try { return nilaiJson(JSON.parse(t), []); } catch { return []; } }
  return [t];
};

// ─── 1. Sumber yang PASTI berisi nomor plat ─────────────────────────────────────────────────────────
const SUMBER = [
  ['nama berkas INDO-ALPR (nama berkasnya ADALAH nomor plat)',
    () => semuaBerkas('data/keluaran/dataset/indo-alpr').flatMap((j) => ambil(path.parse(j).name))],
  ['label plat yang dikoreksi owner (latih-koreksi, K22–K24)',
    () => semuaBerkas('data/keluaran/latih-koreksi').filter((j) => /\.(json|jsonl|csv)$/i.test(j)).flatMap((j) => isiTeks(j).flatMap(ambil))],
  ['bacaan rantai atas CCTV (kedatangan.jsonl, hasil.jsonl)',
    () => semuaBerkas('data/keluaran').filter((j) => /(kedatangan|hasil)\.jsonl$/i.test(j)).flatMap((j) => isiTeks(j).flatMap(ambil))],
  ['label owner (rencana-31, halaman-ciri, label-ciri, lembar-*.json)',
    () => semuaBerkas('data/keluaran').filter((j) => /(rencana-31|halaman-ciri|label-ciri)[\\/]|lembar-[^\\/]*\.json$/i.test(j)
      && /\.(json|jsonl)$/i.test(j)).flatMap((j) => isiTeks(j).flatMap(ambil))],
];
const sumber = SUMBER.map(([nama, ambilSumber]) => [nama, new Set(ambilSumber())]);
console.log('\nsumber yang pasti berisi plat, dan berapa pola yang disumbangkan:');
for (const [nama, s] of sumber) console.log(`   ${String(s.size).padStart(6)}  ${nama}`);
// Sumber yang kosong membuat "nol cocok" tidak bermakna: berhenti, jangan melapor bersih.
const kosong = sumber.filter(([, s]) => s.size === 0);
if (kosong.length) {
  console.log(`\n⛔ ${kosong.length} sumber KOSONG — hasil nol tidak akan bermakna. Periksa data/ lebih dulu.`);
  process.exit(2);
}

// ─── 2. Seluruh riwayat git ─────────────────────────────────────────────────────────────────────────
const r = spawnSync('git', ['log', '--all', '-p', '--no-color', '--text', '--', '.', ':!*.png', ':!*.jpg'],
  { encoding: 'utf8', maxBuffer: 1024 * 1024 * 1024 });
if (r.status !== 0) throw new Error('git log gagal');
const diRiwayat = new Set(r.stdout.split('\n').filter((b) => b.startsWith('+') && !b.startsWith('+++')).flatMap(ambil));
console.log(`\npola mirip plat di seluruh riwayat git: ${diRiwayat.size}`);

// ─── 3. Irisan ──────────────────────────────────────────────────────────────────────────────────────
let panjang = 0;
console.log('\nirisan dengan tiap sumber (nomornya tidak dicetak):');
for (const [nama, s] of sumber) {
  const iris = [...s].filter((p) => diRiwayat.has(p));
  const plat = iris.filter((p) => p.length >= PANJANG_PLAT).length;
  panjang += plat;
  console.log(`   ${String(plat).padStart(4)} sepanjang plat · ${String(iris.length - plat).padStart(3)} pendek (3–4 karakter) · ${nama}`);
}
console.log(`\nHASIL: ${panjang === 0 ? 'NOL' : panjang} pola sepanjang plat sungguhan di riwayat git`);
process.exit(panjang === 0 ? 0 : 1);
