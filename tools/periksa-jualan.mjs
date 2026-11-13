#!/usr/bin/env node
// Pemeriksa tanda mesin (spec bagian 2.4, K15).
// - Mesin JUALAN hanya boleh memuat bahan bervonis BOLEH-PRODUK. Satu saja bahan lain => exit 1.
// - Mesin BELAJAR boleh memuat bahan apa pun yang TERCATAT; tandanya menurun: ada satu bahan bukan BOLEH-PRODUK =>
//   mesin itu RISET-SAJA dan angkanya tidak boleh dilaporkan sebagai angka produk.
// - Bahan yang tak tercatat di daftar bahan selalu ditolak: asal yang tak diketahui tidak bisa dinilai.
//
// Manifes mesin: { "nama": "...", "tujuan": "jualan" | "belajar", "bahan": ["id-bahan", ...] }
// "bahan" memuat SEMUA yang ikut membentuk mesin: dataset, video, huruf, dan bobot awal.
//
// Pakai:  node tools/periksa-jualan.mjs <manifes-mesin.json> [berkas-bahan]
import fs from 'node:fs';
import { muatBahan, BERKAS_BAHAN } from './bahan.mjs';

const TUJUAN = ['jualan', 'belajar'];
const [berkasMesin, berkasBahan = BERKAS_BAHAN] = process.argv.slice(2);
if (!berkasMesin) {
  console.error('Pakai: node tools/periksa-jualan.mjs <manifes-mesin.json> [berkas-bahan]');
  process.exit(2);
}

const { bahan, galat } = muatBahan(berkasBahan);
const tolak = [...galat];
let mesin = {};
try {
  mesin = JSON.parse(fs.readFileSync(berkasMesin, 'utf8'));
} catch (e) {
  tolak.push(`${berkasMesin}: tak terbaca (${e.message})`);
}

if (!TUJUAN.includes(mesin.tujuan)) tolak.push(`tujuan "${mesin.tujuan}" tak dikenal (pilihan: ${TUJUAN.join(', ')})`);
const dipakai = Array.isArray(mesin.bahan) ? mesin.bahan : [];
if (dipakai.length === 0) tolak.push('daftar "bahan" kosong: mesin tanpa asal-usul bahan tidak bisa dinilai');

const perId = new Map(bahan.map((b) => [b.id, b]));
let tanda = 'BOLEH-PRODUK';
for (const id of dipakai) {
  const b = perId.get(id);
  if (!b) {
    tolak.push(`bahan "${id}" tidak tercatat di daftar bahan`);
    continue;
  }
  if (b.vonis !== 'BOLEH-PRODUK') {
    tanda = 'RISET-SAJA';
    if (mesin.tujuan === 'jualan') tolak.push(`bahan "${id}" bervonis ${b.vonis}: tidak boleh ada di mesin jualan`);
  }
}

if (tolak.length) {
  for (const t of tolak) console.error(`DITOLAK ${t}`);
  console.error(`mesin "${mesin.nama ?? '?'}" ditolak (${tolak.length} alasan).`);
  process.exit(1);
}
console.log(`mesin "${mesin.nama}" (${mesin.tujuan}): tanda mesin = ${tanda}`);
