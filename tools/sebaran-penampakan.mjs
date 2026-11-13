#!/usr/bin/env node
// Sebaran jumlah penampakan per kedatangan, dari penampakan.jsonl keluaran tools/lab/rantai.py.
//
// Menjawab pertanyaan Rencana T9: BERAPA BINGKAI yang dibutuhkan per kendaraan sebelum platnya terbaca?
// Itu yang menentukan apakah 1 detik per bingkai di perangkat gerbang yang lemah terasa di palang.
//
// ⛔ Yang dibaca: penampakan.jsonl, yang menurut dokumentasi rantai.py memuat "nomor gambar dan kotak, TANPA
// TEKS". Jadi berkas ini tidak memuat nomor plat. Alat ini tetap hanya mencetak ANGKA RINGKAS — tidak pernah
// satu baris mentah pun — supaya kalau kelak isinya berubah, tidak ada yang bocor ke layar.
// `kedatangan.jsonl` memuat plat dan TIDAK dibaca di sini.
//
//   node tools/sebaran-penampakan.mjs <folder-keluaran-rantai>
import fs from 'node:fs';
import path from 'node:path';

const folder = process.argv[2];
if (!folder) {
  console.error('Pakai: node tools/sebaran-penampakan.mjs <folder-keluaran-rantai>');
  process.exit(2);
}

const jalur = path.join(folder, 'penampakan.jsonl');
const baris = fs.readFileSync(jalur, 'utf8').split('\n').filter((b) => b.trim());

// Tiap baris = satu jalur (satu kendaraan yang dilacak). Jumlah penampakannya = berapa bingkai ia terlihat.
const jumlah = [];
let adaTeks = false;
for (const b of baris) {
  const j = JSON.parse(b);
  // Penjaga: bila kelak penampakan.jsonl ikut memuat teks, alat ini berhenti, bukan mencetaknya.
  if (JSON.stringify(j).match(/"teks"|"plat"/)) adaTeks = true;
  const tampak = j.tampak ?? j.penampakan ?? [];
  jumlah.push(Array.isArray(tampak) ? tampak.length : 0);
}
if (adaTeks) {
  console.error('BERHENTI: penampakan.jsonl memuat teks plat. Alat ini tidak dibuat untuk berkas berplat.');
  process.exit(1);
}

jumlah.sort((a, b) => a - b);
const n = jumlah.length;
const persen = (p) => jumlah[Math.min(n - 1, Math.floor((p / 100) * n))];
const rata = jumlah.reduce((a, b) => a + b, 0) / n;

const ringkasan = JSON.parse(fs.readFileSync(path.join(folder, 'ringkasan.json'), 'utf8'));
const laju = ringkasan.aturan.sampel_per_detik;
const minTampak = ringkasan.aturan.min_tampak;

console.log(`folder          : ${path.basename(folder)}`);
console.log(`laju contoh     : ${laju} gambar per detik video`);
console.log(`jalur terlacak  : ${n}`);
console.log(`ambang kedatangan: minimal ${minTampak} penampakan`);
console.log('');
console.log('BINGKAI PER JALUR (berapa bingkai satu kendaraan terlihat):');
for (const p of [10, 25, 50, 75, 90, 99]) {
  const v = persen(p);
  console.log(`  persentil ${String(p).padStart(2)}: ${String(v).padStart(3)} bingkai  = ${(v / laju).toFixed(1)} detik video`);
}
console.log(`  rata-rata : ${rata.toFixed(1)} bingkai  = ${(rata / laju).toFixed(1)} detik video`);
console.log(`  terbanyak : ${jumlah[n - 1]} bingkai`);
console.log('');

const sekali = jumlah.filter((x) => x < minTampak).length;
console.log(`jalur di bawah ambang (dibuang): ${sekali} dari ${n} (${(100 * sekali / n).toFixed(0)}%)`);
const cukup = jumlah.filter((x) => x >= minTampak);
console.log(`jalur yang menjadi kedatangan  : ${cukup.length}`);
if (cukup.length) {
  const r = cukup.reduce((a, b) => a + b, 0) / cukup.length;
  console.log(`  rata-rata bingkainya: ${r.toFixed(1)} = ${(r / laju).toFixed(1)} detik video`);
}
