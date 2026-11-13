// Uji tgt/basis.mjs: basis data TGT dan migrasinya (Rencana T1 Task 1).
//
// Basis data sungguhan memuat plat nomor dan jam keluar masuk = data pribadi (CLAUDE.md §4), jadi ia tinggal di
// data/tgt/ yang di-gitignore. Uji di sini TIDAK PERNAH menyentuh berkas itu: semuanya di memori atau di folder
// sementara milik sistem.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { VERSI_SKEMA, buka, versi, naik, turun, susunan } from '../basis.mjs';

const folderSementara = () => fs.mkdtempSync(path.join(os.tmpdir(), 'tgt-basis-'));

test('basis baru dibuka langsung bersusunan versi terbaru', () => {
  const db = buka(':memory:');
  try {
    assert.equal(versi(db), VERSI_SKEMA);
    assert.ok(VERSI_SKEMA >= 1, 'versi skema dimulai dari 1');
  } finally {
    db.close();
  }
});

test('keenam tabel versi 1 ada, beserta kolom yang dipakai spec', () => {
  const db = buka(':memory:');
  try {
    const punya = new Set(susunan(db));
    for (const kolom of [
      'grup.nama', 'grup.jenis', 'grup.kode_undangan',
      'gerbang.grup_id', 'gerbang.nama', 'gerbang.jenis_lokasi', 'gerbang.alamat', 'gerbang.kota',
      'gerbang.koordinat', 'gerbang.patokan', 'gerbang.status',
      'kendaraan.gerbang_id', 'kendaraan.jenis', 'kendaraan.merek', 'kendaraan.warna', 'kendaraan.plat',
      'kendaraan.atas_nama', 'kendaraan.unit',
      'tamu.gerbang_id', 'tamu.nama', 'tamu.keperluan', 'tamu.plat', 'tamu.lama_hari', 'tamu.kode_undangan',
      'kunjungan.tamu_id', 'kunjungan.masuk', 'kunjungan.keluar', 'kunjungan.status',
      'kejadian.gerbang_id', 'kejadian.waktu', 'kejadian.arah', 'kejadian.plat', 'kejadian.yakin',
      'kejadian.kendaraan_id', 'kejadian.tamu_id',
    ]) {
      assert.ok(punya.has(kolom), `kolom ${kolom} belum ada di skema`);
    }
  } finally {
    db.close();
  }
});

test('membuka ulang basis yang sudah ada tidak mengulang migrasi dan tidak menghapus data', () => {
  const folder = folderSementara();
  const jalur = path.join(folder, 'tgt.sqlite');

  let db = buka(jalur);
  db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('PT Contoh', 'perusahaan', 'AB12')").run();
  const migrasiPertama = db.prepare('SELECT count(*) AS n FROM migrasi').get().n;
  db.close();

  db = buka(jalur);
  try {
    assert.equal(versi(db), VERSI_SKEMA);
    assert.equal(
      db.prepare('SELECT count(*) AS n FROM migrasi').get().n,
      migrasiPertama,
      'migrasi tercatat dua kali: ia dijalankan ulang padahal basisnya sudah mutakhir',
    );
    assert.equal(db.prepare('SELECT count(*) AS n FROM grup').get().n, 1, 'data grup hilang saat dibuka ulang');
  } finally {
    db.close();
    fs.rmSync(folder, { recursive: true, force: true });
  }
});

test('migrasi bolak-balik: naik -> turun -> naik menghasilkan susunan yang sama', () => {
  const db = buka(':memory:');
  try {
    const sebelum = susunan(db);

    turun(db, 0);
    assert.equal(versi(db), 0, 'sesudah turun ke 0, versinya harus 0');
    assert.equal(susunan(db).length, 0, 'sesudah turun ke 0, tidak boleh ada tabel isi yang tersisa');

    naik(db);
    assert.equal(versi(db), VERSI_SKEMA);
    assert.deepEqual(susunan(db), sebelum, 'susunan sesudah naik kedua berbeda dengan yang pertama');
  } finally {
    db.close();
  }
});

test('turun membuang data, jadi ia memang mencabut tabelnya, bukan sekadar mengubah nomor versi', () => {
  const db = buka(':memory:');
  try {
    db.prepare("INSERT INTO grup (nama, jenis, kode_undangan) VALUES ('Cluster Contoh', 'pribadi', 'CD34')").run();
    turun(db, 0);
    naik(db);
    assert.equal(db.prepare('SELECT count(*) AS n FROM grup').get().n, 0);
  } finally {
    db.close();
  }
});

test('naik dua kali berturut-turut tidak menggandakan catatan migrasi', () => {
  const db = buka(':memory:');
  try {
    const n = db.prepare('SELECT count(*) AS n FROM migrasi').get().n;
    naik(db);
    assert.equal(db.prepare('SELECT count(*) AS n FROM migrasi').get().n, n);
  } finally {
    db.close();
  }
});
