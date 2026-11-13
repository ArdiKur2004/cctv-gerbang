// Uji tools/laporan-0a.mjs (Rencana 15): angka laporan dibaca dari JSON bukti, gagal tertutup bila kuncinya tidak ada, dan
// laporan yang menyimpang dari sumbernya tertangkap.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { AKHIR, BUKTI, MULAI, TABEL, baca, isi, sel } from '../laporan-0a.mjs';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'laporan-0a.mjs');
const CONTOH = {
  'a.json': {
    uji: { semua: { benar: 496, jumlah: 625, rentang: [0.76, 0.823] } }, besar: 33906, waktu: 17.73,
    model: [{ berkas: 'x.onnx', ms: 149.9 }, { berkas: 'y.onnx', ms: 544 }],
  },
};

function folder(isiBerkas) {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-laporan-'));
  for (const [nama, x] of Object.entries(isiBerkas)) fs.writeFileSync(path.join(d, nama), JSON.stringify(x));
  return d;
}

test('baca mengikuti kunci bersarang dan memilih elemen daftar menurut isinya', () => {
  const d = folder(CONTOH);
  assert.equal(baca(d, 'a.json', ['uji', 'semua', 'benar']), 496);
  assert.equal(baca(d, 'a.json', ['model', { berkas: 'y.onnx' }, 'ms']), 544);
});

test('baca gagal tertutup: kunci tidak ada, atau elemen daftar tidak cocok tepat sekali', () => {
  const d = folder(CONTOH);
  assert.throws(() => baca(d, 'a.json', ['uji', 'semua', 'hilang']), /hilang/);
  assert.throws(() => baca(d, 'a.json', ['model', { berkas: 'z.onnx' }, 'ms']), /0 kali/);
});

test('sel menulis bagian dengan persen dan rentang, ribuan, dan milidetik dengan koma', () => {
  const d = folder(CONTOH);
  assert.equal(sel(d, { dari: ['a.json', ['uji', 'semua']], benar: 'benar', jumlah: 'jumlah', rentang: 'rentang' }),
    '496 dari 625 (79,4%) [76–82%]');
  assert.equal(sel(d, { n: ['a.json', ['besar']] }), '33.906');
  assert.equal(sel(d, { ms: ['a.json', ['waktu']] }), '17,7 ms');
  assert.equal(sel(d, 'belum diukur'), 'belum diukur');
});

test('rantai: tulis dari bukti sungguhan, periksa sama; laporan yang diubah tangan atau tanpa penanda tertangkap', () => {
  const laporan = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-laporan-')), 'laporan.md');
  fs.writeFileSync(laporan, `# Laporan\n\n${MULAI}\nlama\n${AKHIR}\n\nPenutup.\n`);
  const jalan = (perintah) => spawnSync('node', [SKRIP, perintah, laporan], { encoding: 'utf8' });

  assert.equal(jalan('tulis').status, 0);
  const tertulis = fs.readFileSync(laporan, 'utf8');
  assert.ok(tertulis.includes(isi(BUKTI, TABEL)) && tertulis.endsWith('Penutup.\n') && !tertulis.includes('lama'));
  assert.equal(jalan('periksa').status, 0);

  fs.writeFileSync(laporan, tertulis.replace(' dari ', ' dari 1'));
  const r = jalan('periksa');
  assert.equal(r.status, 1);
  assert.match(r.stdout + r.stderr, /tidak sama/);

  fs.writeFileSync(laporan, '# tanpa penanda\n');
  assert.equal(jalan('tulis').status, 1);
});
