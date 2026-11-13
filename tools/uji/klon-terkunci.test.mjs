// Uji tools/klon-terkunci.ps1: repo pihak ketiga diklon PERSIS di commit yang tercatat di kunci, tanpa memasang atau
// menjalankan apa pun. "GitHub" diganti folder lokal lewat VS_ASAL_GIT, jadi uji ini tidak menyentuh jaringan.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'klon-terkunci.ps1');
// Bila alamatnya salah, git harus gagal cepat: tidak menunggu sandi dan tidak membuka jendela login.
const TANPA_TANYA = { GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never', GIT_ASKPASS: 'echo' };

function asalLokal() {
  // "GitHub tiruan": <dasar>/uji-lokal/contoh.git adalah repo git biasa dengan satu commit.
  const dasar = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-asal-'));
  const repo = path.join(dasar, 'uji-lokal', 'contoh.git');
  fs.mkdirSync(repo, { recursive: true });
  const git = (...a) => {
    const r = spawnSync('git', ['-C', repo, '-c', 'user.name=uji', '-c', 'user.email=uji@contoh.test', ...a], { encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
    return r.stdout.trim();
  };
  git('init', '--quiet');
  fs.writeFileSync(path.join(repo, 'LICENSE'), 'izin contoh\n');
  git('add', '.');
  git('commit', '--quiet', '-m', 'awal');
  return { dasar: dasar + path.sep, sha: git('rev-parse', 'HEAD') };
}

function kunci(sha) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  fs.writeFileSync(berkas, JSON.stringify({ repo: [{ nama: 'contoh', repo: 'uji-lokal/contoh', ref: 'uji', sha, vonis: 'UJI' }] }));
  return berkas;
}

function klon(nama, berkasKunci, dasar) {
  const tujuan = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-vendor-'));
  const r = spawnSync('powershell', ['-NoProfile', '-File', SKRIP, '-Nama', nama, '-Kunci', berkasKunci, '-Tujuan', tujuan], {
    encoding: 'utf8', env: { ...process.env, ...TANPA_TANYA, VS_ASAL_GIT: dasar }, timeout: 120_000,
  });
  return { kode: r.status, keluar: r.stdout + r.stderr, tujuan };
}

test('repo diklon persis di commit yang tercatat di kunci', () => {
  const { dasar, sha } = asalLokal();

  const r = klon('contoh', kunci(sha), dasar);

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /OK\s+contoh/);
  const hasil = path.join(r.tujuan, 'contoh');
  const head = spawnSync('git', ['-C', hasil, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).stdout.trim();
  assert.equal(head, sha);
  assert.ok(fs.existsSync(path.join(hasil, 'LICENSE')), 'berkas dari commit itu harus ter-checkout');
  // Isi dibandingkan dari commit-nya, bukan dari berkas di cakram: di mesin ber-`core.autocrlf=true` git mengubah
  // akhir baris saat checkout. `git show` inilah yang dipakai mengarsipkan berkas izin (Rencana 2, Task 2).
  const isi = spawnSync('git', ['-C', hasil, 'show', `${sha}:LICENSE`], { encoding: 'utf8' }).stdout;
  assert.equal(isi, 'izin contoh\n');
});

test('commit di kunci yang tidak ada di repo: gagal (kode 1), tidak diam-diam memakai commit lain', () => {
  const { dasar } = asalLokal();

  const r = klon('contoh', kunci('0'.repeat(40)), dasar);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /GAGAL\s+contoh: checkout/);
});

test('nama yang tidak ada di kunci ditolak (kode 1): yang tak tercatat tidak diklon', () => {
  const { dasar, sha } = asalLokal();

  const r = klon('entah', kunci(sha), dasar);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /TAK ADA DI KUNCI: entah/);
});
