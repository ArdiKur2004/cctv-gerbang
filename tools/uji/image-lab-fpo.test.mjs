// Uji pembangun image lab tambahan tools/image-lab-fpo.ps1 (K26). Yang dikunci: image dasar harus persis yang tercatat,
// daftar paket harus ber-SHA-256, dan isi image ditandai sidik Dockerfile + requirements.txt.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'image-lab-fpo.ps1');
const pasangan = (a, k) => a.flatMap((x, i) => (x === k ? [a[i + 1]] : []));

function sementara(nama, isi) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-fpo-')), nama);
  fs.writeFileSync(berkas, isi);
  return berkas;
}

function dockerTiruan() {
  return sementara('docker-tiruan.ps1', ["if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }", 'exit 0'].join('\r\n'));
}

function jalankan(env) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', SKRIP, '-Kering'], {
    encoding: 'utf8', timeout: 60_000,
    env: { ...process.env, VS_DOCKER: dockerTiruan(), TIRUAN_ID: 'sha256:tiruan',
      VS_KUNCI_VENDOR: sementara('vendor.lock.json', JSON.stringify({ image_lab: { nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' } })),
      ...env },
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

test('image dasar yang ID-nya bukan yang tercatat: tidak dibangun (kode 6)', () => {
  const r = jalankan({ TIRUAN_ID: 'sha256:lain' });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE DASAR TAK SESUAI KUNCI/);
});

test('image dasar sesuai: docker build dengan nama image, folder lab-fpo, dan sidik isi', () => {
  const r = jalankan({});

  assert.equal(r.kode, 0, r.keluar + r.galat);
  const a = JSON.parse(r.keluar);
  assert.equal(a[0], 'build');
  assert.deepEqual(pasangan(a, '-t'), ['cctvgerbang-lab-fpo:v1']);
  assert.match(pasangan(a, '--build-arg')[0], /^KUNCI_LAB_FPO=[0-9a-f]{64}$/);
  assert.match(a.at(-1), /tools[\\/]lab-fpo$/);
});

test('daftar paket tanpa SHA-256 ditolak (kode 2)', () => {
  const folder = path.dirname(sementara('Dockerfile', 'FROM vision-seed-lab:v1\n'));
  fs.writeFileSync(path.join(folder, 'requirements.txt'), 'keras==3.15.1\n');

  const r = jalankan({ VS_LAB_FPO_FOLDER: folder });

  assert.equal(r.kode, 2, r.keluar + r.galat);
  assert.match(r.keluar, /DITOLAK/);
});
