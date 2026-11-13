#!/usr/bin/env node
// Daftar bahan latih dan bahan uji (K15, spec bagian 2.4). Tiap bahan punya satu baris di data-asal/bahan.json: asal,
// izin, dan vonisnya. Bahan yang tak tercatat di sana tidak boleh dipakai melatih.
//
// Gagal tertutup: berkas yang tak terbaca, kolom wajib yang kosong, id ganda, atau vonis di luar daftar => exit 1.
// Vonis BOLEH-PRODUK wajib punya bukti_lisensi (alamat halaman izin yang dibaca), supaya "boleh dijual" bisa ditunjukkan
// dasarnya.
//
// Pakai:  node tools/bahan.mjs periksa [berkas-bahan]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AKAR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
export const BERKAS_BAHAN = path.join(AKAR, 'data-asal', 'bahan.json');
export const VONIS = ['BOLEH-PRODUK', 'RISET-SAJA', 'DILARANG', 'BELUM-JELAS'];
export const JENIS = ['video', 'dataset', 'bobot', 'huruf', 'sintetis', 'rekaman'];
const WAJIB = ['id', 'jenis', 'nama', 'sumber', 'lisensi', 'vonis', 'dicatat'];
const terisi = (nilai) => typeof nilai === 'string' && nilai.trim() !== '';

export function muatBahan(berkas = BERKAS_BAHAN) {
  let isi;
  try {
    isi = JSON.parse(fs.readFileSync(berkas, 'utf8'));
  } catch (e) {
    return { bahan: [], galat: [`${berkas}: tak terbaca (${e.message})`] };
  }
  if (!Array.isArray(isi.bahan)) return { bahan: [], galat: [`${berkas}: kunci "bahan" harus berupa daftar`] };

  const galat = [];
  const terlihat = new Set();
  for (const [i, b] of isi.bahan.entries()) {
    const sebut = terisi(b?.id) ? `bahan "${b.id}"` : `bahan ke-${i + 1}`;
    for (const k of WAJIB) if (!terisi(b?.[k])) galat.push(`${sebut}: "${k}" wajib diisi`);
    if (terisi(b?.id)) {
      if (!/^[a-z0-9][a-z0-9-]*$/.test(b.id)) galat.push(`${sebut}: id hanya boleh huruf kecil, angka, dan tanda hubung`);
      if (terlihat.has(b.id)) galat.push(`${sebut}: id dipakai dua kali`);
      terlihat.add(b.id);
    }
    if (terisi(b?.jenis) && !JENIS.includes(b.jenis)) galat.push(`${sebut}: jenis "${b.jenis}" tak dikenal (pilihan: ${JENIS.join(', ')})`);
    if (terisi(b?.vonis) && !VONIS.includes(b.vonis)) galat.push(`${sebut}: vonis "${b.vonis}" tak dikenal (pilihan: ${VONIS.join(', ')})`);
    if (b?.vonis === 'BOLEH-PRODUK' && !terisi(b.bukti_lisensi)) {
      galat.push(`${sebut}: vonis BOLEH-PRODUK wajib punya "bukti_lisensi" (alamat halaman izin yang dibaca)`);
    }
  }
  return { bahan: isi.bahan, galat };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [perintah, berkas] = process.argv.slice(2);
  if (perintah !== 'periksa') {
    console.error('Pakai: node tools/bahan.mjs periksa [berkas-bahan]');
    process.exit(2);
  }
  const { bahan, galat } = muatBahan(berkas ?? BERKAS_BAHAN);
  if (galat.length) {
    for (const g of galat) console.error(`DITOLAK ${g}`);
    console.error(`${galat.length} cacat; daftar bahan tidak sah.`);
    process.exit(1);
  }
  console.log(`${bahan.length} bahan tercatat: ${VONIS.map((v) => `${v}=${bahan.filter((b) => b.vonis === v).length}`).join(', ')}`);
}
