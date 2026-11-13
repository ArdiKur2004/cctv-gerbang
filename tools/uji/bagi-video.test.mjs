// Uji tools/bagi-video.mjs (Rencana 16): pembagian latih/uji Fase 1 per video, tetap per video (video lama tidak pernah pindah
// sisi saat video baru ditambahkan), dan hanya sudut gerbang, parkiran, dan kamera-diam-lain yang dibagi.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { bagi, sisi } from '../bagi-video.mjs';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'bagi-video.mjs');
const v = (berkas, sudut, kategori = 'siang') => ({ berkas, sudut, kategori });

test('sisi tiap video dari SHA-256 "fase1/<berkas>"-nya sendiri', () => {
  for (const b of ['youtube-a.mp4', 'youtube-b.mp4', 'youtube-c.webm']) {
    const h = crypto.createHash('sha256').update(`fase1/${b}`).digest('hex');
    assert.equal(sisi(b), parseInt(h[0], 16) < 8 ? 'uji' : 'latih');
  }
});

test('hanya gerbang, parkiran, dan kamera-diam-lain yang dibagi; tidak ada video di dua sisi', () => {
  const h = bagi([v('a.mp4', 'gerbang'), v('b.mp4', 'parkiran'), v('c.mp4', 'kamera-diam-lain'), v('d.mp4', 'dasbor'),
    v('e.mp4', 'lain'), v('f.mp4', '')]);
  assert.deepEqual([...h.uji, ...h.latih].sort(), ['a.mp4', 'b.mp4', 'c.mp4']);
  assert.equal(h.uji.filter((x) => h.latih.includes(x)).length, 0);
});

test('menambah video atau mengubah kategori tidak memindahkan video lama', () => {
  const lama = Array.from({ length: 40 }, (_, i) => v(`v${i}.mp4`, 'gerbang'));
  const a = bagi(lama);
  const b = bagi([...lama.map((x) => ({ ...x, kategori: 'malam' })), ...Array.from({ length: 40 }, (_, i) => v(`baru${i}.mp4`, 'parkiran'))]);
  for (const x of a.uji) assert.ok(b.uji.includes(x));
  for (const x of a.latih) assert.ok(b.latih.includes(x));
});

test('kira-kira separuh ke uji, dan hitungan per lapis', () => {
  const h = bagi(Array.from({ length: 400 }, (_, i) => v(`v${i}.mp4`, i % 2 ? 'gerbang' : 'parkiran', i % 3 ? 'siang' : 'malam')));
  assert.ok(h.uji.length > 160 && h.uji.length < 240);
  assert.equal(Object.values(h.per_lapis).reduce((t, n) => t + n.uji + n.latih, 0), 400);
  assert.deepEqual(Object.keys(h.per_lapis), ['gerbang|malam', 'gerbang|siang', 'parkiran|malam', 'parkiran|siang']);
});

test('CLI menulis pembagian dan mencetak hitungan; manifes yang tidak ada gagal', () => {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-bagi-'));
  fs.writeFileSync(path.join(d, 'm.json'), JSON.stringify({ video: [v('a.mp4', 'gerbang'), v('b.mp4', 'dasbor')] }));
  const r = spawnSync('node', [SKRIP, path.join(d, 'm.json'), path.join(d, 'p.json')], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /gerbang\|siang/);
  const p = JSON.parse(fs.readFileSync(path.join(d, 'p.json'), 'utf8'));
  assert.deepEqual([...p.uji, ...p.latih], ['a.mp4']);
  assert.equal(spawnSync('node', [SKRIP, path.join(d, 'tidak-ada.json'), path.join(d, 'q.json')]).status, 1);
});
