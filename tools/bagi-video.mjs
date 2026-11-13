#!/usr/bin/env node
// Pembagian video Fase 1 ke sisi latih dan uji, per video (spec Fase 1 bagian 1; spec 8.3): satu video tidak pernah di dua sisi.
// Tiap video ditentukan dari SHA-256 "fase1/<berkas>"-nya sendiri: huruf heksadesimal pertama 0-7 = uji, 8-f = latih. Jadi
// pembagian tidak berubah saat video baru ditambahkan atau isian manifes lain diubah. Video yang pernah di sisi uji tidak pernah
// pindah ke latih, karena itu akan membocorkan set uji. Akibatnya keseimbangan per lapis (sudut x kategori) tidak dijamin;
// hitungannya dicetak dan disimpan.
// Hanya video bersudut gerbang, parkiran, atau kamera-diam-lain yang dibagi.
// Pakai: node tools/bagi-video.mjs [manifes] [keluaran]
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AKAR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
export const SUDUT_DIBAGI = ['gerbang', 'parkiran', 'kamera-diam-lain'];

export function sisi(berkas) {
  return parseInt(crypto.createHash('sha256').update(`fase1/${berkas}`).digest('hex')[0], 16) < 8 ? 'uji' : 'latih';
}

export function bagi(video) {
  const hasil = {
    aturan: 'per video: SHA-256 "fase1/<berkas>", huruf heksadesimal pertama 0-7 uji, 8-f latih; sudut gerbang, parkiran, kamera-diam-lain',
    uji: [], latih: [], per_lapis: {},
  };
  for (const v of video.filter((x) => SUDUT_DIBAGI.includes(x.sudut))) {
    const s = sisi(v.berkas);
    hasil[s].push(v.berkas);
    const lapis = `${v.sudut}|${v.kategori || 'tanpa-kategori'}`;
    hasil.per_lapis[lapis] ??= { uji: 0, latih: 0 };
    hasil.per_lapis[lapis][s] += 1;
  }
  hasil.uji.sort();
  hasil.latih.sort();
  hasil.per_lapis = Object.fromEntries(Object.entries(hasil.per_lapis).sort(([a], [b]) => a.localeCompare(b)));
  return hasil;
}

function utama(argumen) {
  const manifes = argumen[0] ?? path.join(AKAR, 'data-asal', 'video-riset.json');
  const keluar = argumen[1] ?? path.join(AKAR, 'data-asal', 'pembagian-video-fase1.json');
  try {
    const h = bagi(JSON.parse(fs.readFileSync(manifes, 'utf8')).video);
    fs.writeFileSync(keluar, `${JSON.stringify(h, null, 2)}\n`);
    for (const [lapis, n] of Object.entries(h.per_lapis)) console.log(`${lapis}: uji ${n.uji}, latih ${n.latih}`);
    console.log(`jumlah: uji ${h.uji.length}, latih ${h.latih.length} -> ${keluar}`);
    return 0;
  } catch (galat) {
    console.error(`GAGAL: ${galat.message}`);
    return 1;
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) process.exit(utama(process.argv.slice(2)));
