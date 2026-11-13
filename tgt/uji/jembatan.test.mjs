// Uji tgt/jembatan.mjs: jembatan berkas antara TGT dan mesin baca (Rencana T6 Task 3).
//
// Mesin baca berjalan di lab tanpa jaringan, jadi jembatannya folder. Yang paling berbahaya di sini bukan
// "lambat", melainkan MENGGANTUNG SELAMANYA: layar satpam yang menunggu hasil yang tidak pernah datang
// membuat gerbang berhenti bekerja tanpa ada pesan apa pun.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { buatJembatan } from '../jembatan.mjs';

function folderSementara() {
  const akar = fs.mkdtempSync(path.join(os.tmpdir(), 'tgt-jembatan-'));
  return { akar, masuk: path.join(akar, 'masuk'), keluar: path.join(akar, 'keluar') };
}

const GAMBAR = Buffer.from('bukan gambar sungguhan, tetapi cukup untuk menguji jembatannya');

test('gambar ditulis beserta keterangannya, dengan nama yang tidak bisa ditebak', () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar });
  const id = j.kirim(GAMBAR, { gerbangId: 1, arah: 'masuk' });

  assert.ok(id.length >= 16, 'nama berkas harus panjang dan acak: ia duduk di folder bersama');
  assert.ok(fs.existsSync(path.join(masuk, `${id}.png`)));
  const keterangan = JSON.parse(fs.readFileSync(path.join(masuk, `${id}.json`), 'utf8'));
  assert.equal(keterangan.gerbangId, 1);
  assert.equal(keterangan.arah, 'masuk');
});

test('dua kiriman tidak pernah bernama sama', () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar });
  const nama = new Set();
  for (let i = 0; i < 50; i += 1) nama.add(j.kirim(GAMBAR, {}));
  assert.equal(nama.size, 50);
});

test('hasil yang muncul dibaca, lalu berkasnya dibuang', async () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 2000, jedaMs: 20 });
  const id = j.kirim(GAMBAR, { gerbangId: 1 });

  fs.mkdirSync(keluar, { recursive: true });
  fs.writeFileSync(path.join(keluar, `${id}.json`), JSON.stringify({ plat: 'L1234AB', jenis: 'mobil', ragu: [] }));

  const hasil = await j.tungguHasil(id);
  assert.equal(hasil.plat, 'L1234AB');
  assert.equal(hasil.jenis, 'mobil');
  assert.ok(!fs.existsSync(path.join(keluar, `${id}.json`)), 'hasil memuat plat: ia tidak boleh tertinggal');
});

test('⛔ hasil yang tidak pernah datang punya BATAS WAKTU, tidak menggantung selamanya', async () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 150, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});

  const mulai = Date.now();
  await assert.rejects(() => j.tungguHasil(id), /waktu|mesin baca/i);
  assert.ok(Date.now() - mulai < 2000, 'batas waktunya tidak bekerja');
});

test('kiriman yang kedaluwarsa dibersihkan dari folder masuk', async () => {
  // Gambar yang tidak pernah diproses tidak boleh menumpuk: ia memuat plat (K71).
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 150, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});

  await assert.rejects(() => j.tungguHasil(id));
  assert.ok(!fs.existsSync(path.join(masuk, `${id}.png`)), 'gambar yang kedaluwarsa harus dibuang');
  assert.ok(!fs.existsSync(path.join(masuk, `${id}.json`)));
});

test('hasil yang rusak tidak menjatuhkan server, dan dilaporkan sebagai galat', async () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 1000, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});

  fs.mkdirSync(keluar, { recursive: true });
  fs.writeFileSync(path.join(keluar, `${id}.json`), 'bukan json');

  await assert.rejects(() => j.tungguHasil(id), /terbaca|rusak/i);
  assert.ok(!fs.existsSync(path.join(keluar, `${id}.json`)), 'hasil rusak pun harus dibuang');
});

test('galat dari mesin baca diteruskan apa adanya', async () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 1000, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});

  fs.mkdirSync(keluar, { recursive: true });
  fs.writeFileSync(path.join(keluar, `${id}.json`), JSON.stringify({ plat: null, galat: 'gagal dibaca (ValueError)' }));

  await assert.rejects(() => j.tungguHasil(id), /gagal dibaca/);
});

test('⛔ satu hasil tidak pernah terbaca dua kali', async () => {
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 500, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});

  fs.mkdirSync(keluar, { recursive: true });
  fs.writeFileSync(path.join(keluar, `${id}.json`), JSON.stringify({ plat: 'L1234AB', ragu: [] }));

  assert.equal((await j.tungguHasil(id)).plat, 'L1234AB');
  await assert.rejects(() => j.tungguHasil(id), /waktu|mesin baca/i, 'hasil yang sama terbaca dua kali');
});

test('mesin baca yang belum pernah jalan memberi pesan yang bisa dimengerti', async () => {
  // Folder keluar belum ada sama sekali. Satpam harus tahu sebabnya, bukan melihat galat berkas.
  const { masuk, keluar } = folderSementara();
  const j = buatJembatan({ masuk, keluar, batasMs: 120, jedaMs: 20 });
  const id = j.kirim(GAMBAR, {});
  await assert.rejects(() => j.tungguHasil(id), /mesin baca/i);
});

test('folder masuk dibuat sendiri bila belum ada', () => {
  const { masuk, keluar } = folderSementara();
  assert.ok(!fs.existsSync(masuk));
  buatJembatan({ masuk, keluar }).kirim(GAMBAR, {});
  assert.ok(fs.existsSync(masuk));
});
