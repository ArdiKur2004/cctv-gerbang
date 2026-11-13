// Uji tools/periksa-jualan.mjs (spec bagian 2.4, K15): mesin jualan tidak boleh memuat bahan bukan BOLEH-PRODUK, dan
// tanda bahan menurun ke mesinnya.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'periksa-jualan.mjs');
const bahanKe = (id, vonis) => ({
  id, jenis: 'dataset', nama: id, sumber: 'https://contoh.test/' + id, lisensi: 'contoh',
  bukti_lisensi: 'https://contoh.test/lisensi', vonis, dicatat: '2026-10-13',
});
const DAFTAR = { bahan: [bahanKe('bersih-a', 'BOLEH-PRODUK'), bahanKe('bersih-b', 'BOLEH-PRODUK'), bahanKe('riset-a', 'RISET-SAJA'), bahanKe('samar-a', 'BELUM-JELAS')] };

function tulis(nama, isi) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-jualan-')), nama);
  fs.writeFileSync(berkas, JSON.stringify(isi));
  return berkas;
}

function periksa(mesin, daftar = DAFTAR) {
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', mesin), tulis('bahan.json', daftar)], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}

test('mesin jualan dari bahan bersih semua diterima dan bertanda BOLEH-PRODUK', () => {
  const r = periksa({ nama: 'm1', tujuan: 'jualan', bahan: ['bersih-a', 'bersih-b'] });

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /tanda mesin = BOLEH-PRODUK/);
});

test('mesin jualan yang memuat satu bahan RISET-SAJA ditolak (kode 1) dan bahannya disebut', () => {
  const r = periksa({ nama: 'm2', tujuan: 'jualan', bahan: ['bersih-a', 'riset-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bahan "riset-a" bervonis RISET-SAJA/);
});

test('mesin jualan yang memuat bahan BELUM-JELAS ditolak: yang belum jelas tidak dianggap boleh', () => {
  const r = periksa({ nama: 'm3', tujuan: 'jualan', bahan: ['samar-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bahan "samar-a" bervonis BELUM-JELAS/);
});

test('bahan yang tak tercatat ditolak, untuk mesin jualan maupun mesin belajar', () => {
  for (const tujuan of ['jualan', 'belajar']) {
    const r = periksa({ nama: 'm4', tujuan, bahan: ['entah-dari-mana'] });

    assert.equal(r.kode, 1, `${tujuan}: ${r.keluar}`);
    assert.match(r.keluar, /bahan "entah-dari-mana" tidak tercatat/);
  }
});

test('mesin tanpa daftar bahan ditolak: asal-usul kosong tidak bisa dinilai', () => {
  const r = periksa({ nama: 'm5', tujuan: 'jualan', bahan: [] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /daftar "bahan" kosong/);
});

test('mesin belajar boleh memuat bahan RISET-SAJA, dan tandanya menurun menjadi RISET-SAJA', () => {
  const r = periksa({ nama: 'm6', tujuan: 'belajar', bahan: ['bersih-a', 'riset-a'] });

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /tanda mesin = RISET-SAJA/);
});

test('tujuan di luar daftar ditolak', () => {
  const r = periksa({ nama: 'm7', tujuan: 'produksi', bahan: ['bersih-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /tujuan "produksi" tak dikenal/);
});

test('daftar bahan yang cacat membuat semua mesin ditolak', () => {
  const r = periksa({ nama: 'm8', tujuan: 'jualan', bahan: ['bersih-a'] }, { bahan: [{ ...bahanKe('bersih-a', 'BOLEH-PRODUK'), bukti_lisensi: '' }] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bukti_lisensi/);
});

test('tanpa argumen: ditolak dengan petunjuk pakai (kode 2)', () => {
  const r = spawnSync('node', [SKRIP], { encoding: 'utf8' });

  assert.equal(r.status, 2, r.stdout + r.stderr);
});

test('rantai: bahan pembaca jualan Rencana 24 (INDO-ALPR, tangkapan owner, plat buatan) lolos di daftar bahan repo', () => {
  // Penjaga: manifes latih_fpo.manifes_jualan memakai id bahan dari bahan_pembaca.py. Bila salah satu id berubah atau vonisnya
  // turun, mesin jualan harus ditolak di sini, bukan lolos diam-diam.
  const mesin = { nama: 'pembaca-jualan', tujuan: 'jualan', bahan: ['dataset-indo-alpr', 'tangkapan-owner', 'plat-buatan'] };
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', mesin)], { encoding: 'utf8' });

  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /tanda mesin = BOLEH-PRODUK/);
});

test('rantai: K47 — pembaca dari bobot fast-plate-ocr (fpo-indo-1: INDO-ALPR + bobot terbitan) lolos sebagai mesin jualan', () => {
  // Owner (K47, 19 Okt) menerima pernyataan pemelihara fast-plate-ocr di GitHub sebagai izin bobot. Sebelum K47 manifes ini
  // ditolak (bobot-fast-plate-ocr BELUM-JELAS). Bila K47 dibalik, uji ini harus dibalik juga.
  const mesin = { nama: 'fpo-indo-jualan', tujuan: 'jualan', bahan: ['dataset-indo-alpr', 'bobot-fast-plate-ocr', 'tangkapan-owner'] };
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', mesin)], { encoding: 'utf8' });

  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /tanda mesin = BOLEH-PRODUK/);
});

test('rantai: K48 dan K49 — pencari plat cctv1 (bobot YOLOX COCO + plat-lighting + video riset + plat buatan) lolos sebagai jualan', () => {
  // Dibalik dua kali. Semula (K47): "bobot YOLOX BELUM-JELAS, ditolak". K48: bobot YOLOX yang dimodifikasi boleh, tetapi cctv1 masih
  // ditolak karena video riset RISET-SAJA. K49 (19 Okt): owner menyatakan izin verbal untuk video riset, jadi cctv1 lolos.
  const cctv1 = { nama: 'm11', tujuan: 'jualan', bahan: ['dataset-plat-lighting', 'bobot-yolox', 'video-riset-youtube', 'plat-buatan'] };
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', cctv1)], { encoding: 'utf8' });

  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /tanda mesin = BOLEH-PRODUK/);
});

test('rantai: tanpa berkas bahan, yang dibaca adalah daftar bahan repo ini, dan bahan BELUM-JELAS repo ditolak untuk jualan', () => {
  // Uji ini menelusuri jalannya: manifes mesin -> data-asal/bahan.json sungguhan -> keputusan. Bila pemeriksa tidak benar-benar
  // membaca daftar repo, bahan "bobot-qwen3-vl" akan terbaca "tidak tercatat", bukan "BELUM-JELAS". Sebelum K49 uji ini memakai
  // video riset (RISET-SAJA); sejak K49 video riset BOLEH-PRODUK, jadi bahannya diganti bobot Qwen3-VL (alat lab, BELUM-JELAS).
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', { nama: 'm9', tujuan: 'jualan', bahan: ['bobot-qwen3-vl'] })], { encoding: 'utf8' });

  assert.equal(r.status, 1, r.stdout + r.stderr);
  assert.match(r.stdout + r.stderr, /bahan "bobot-qwen3-vl" bervonis BELUM-JELAS/);
});
