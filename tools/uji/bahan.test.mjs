// Uji tools/bahan.mjs: daftar bahan latih dan bahan uji (K15). Tiap bahan punya asal, izin, dan vonis; yang cacat
// ditolak, karena daftar inilah yang dibaca tools/periksa-jualan.mjs saat menilai sebuah mesin.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'bahan.mjs');
const BAIK = {
  id: 'dataset-contoh', jenis: 'dataset', nama: 'Dataset contoh', sumber: 'https://contoh.test/data',
  lisensi: 'CC BY 4.0', bukti_lisensi: 'https://contoh.test/lisensi', vonis: 'BOLEH-PRODUK', dicatat: '2026-10-13',
};

function tulis(isi) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-bahan-')), 'bahan.json');
  fs.writeFileSync(berkas, typeof isi === 'string' ? isi : JSON.stringify(isi));
  return berkas;
}

function periksa(...args) {
  const r = spawnSync('node', [SKRIP, 'periksa', ...args], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}

test('daftar yang benar diterima dan diringkas per vonis', () => {
  const r = periksa(tulis({ bahan: [BAIK, { ...BAIK, id: 'video-contoh', jenis: 'video', vonis: 'RISET-SAJA', bukti_lisensi: '' }] }));

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /2 bahan tercatat/);
  assert.match(r.keluar, /BOLEH-PRODUK=1/);
  assert.match(r.keluar, /RISET-SAJA=1/);
});

for (const kolom of ['id', 'jenis', 'nama', 'sumber', 'lisensi', 'vonis', 'dicatat']) {
  test(`bahan tanpa "${kolom}" ditolak (kode 1)`, () => {
    const r = periksa(tulis({ bahan: [{ ...BAIK, [kolom]: '' }] }));

    assert.equal(r.kode, 1, r.keluar);
    assert.match(r.keluar, new RegExp(`"${kolom}" wajib diisi`));
  });
}

test('vonis di luar daftar ditolak: salah ketik tidak boleh lolos sebagai vonis baru', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, vonis: 'BOLEH' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /vonis "BOLEH" tak dikenal/);
});

test('jenis di luar daftar ditolak', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, jenis: 'gambar' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /jenis "gambar" tak dikenal/);
});

test('id yang dipakai dua kali ditolak', () => {
  const r = periksa(tulis({ bahan: [BAIK, BAIK] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /id dipakai dua kali/);
});

test('vonis BOLEH-PRODUK tanpa bukti izin ditolak: yang boleh dijual harus bisa ditunjukkan dasarnya', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, bukti_lisensi: '' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bukti_lisensi/);
});

test('berkas yang tak terbaca ditolak (kode 1), bukan dianggap daftar kosong', () => {
  const r = periksa(tulis('{ ini bukan json'));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /tak terbaca/);
});

test('perintah selain periksa ditolak (kode 2)', () => {
  const r = spawnSync('node', [SKRIP, 'hapus'], { encoding: 'utf8' });

  assert.equal(r.status, 2, r.stdout + r.stderr);
});

test('rantai: daftar bahan milik repo ini lolos pemeriksaan dan tidak kosong', () => {
  // Tanpa argumen berkas, yang diperiksa adalah data-asal/bahan.json sungguhan. Jumlahnya sengaja tidak dikunci:
  // daftar itu bertambah tiap ada bahan baru.
  const r = periksa();

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /^[1-9]\d* bahan tercatat/);
});
