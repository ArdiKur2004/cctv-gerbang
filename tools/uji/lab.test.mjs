// Uji pintu lab tools/lab.ps1. Yang dikunci di sini adalah JANJI bengkel di sisi host: tanpa jaringan, repo read-only,
// image persis yang tercatat, dan "kunci bengkel" (satu job lab pada satu waktu, bersama vision-seed).
//
// Asal: disusun dari vision-seed @3591530 (tools/uji/lab.test.mjs) pada 2026-10-13 (K14). Yang diubah di sini: uji
// mode -Kamera, -Jaringan, dan gudang aset diganti penolakan; uji kunci image diganti penjagaan lewat ID image.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const LAB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'lab.ps1');
const NAMA_KUNCI = 'Global\\vision-seed-bengkel';

function lab(args, env = {}) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', LAB, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
    timeout: 60_000,
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

function argumenDocker(args, env) {
  const r = lab(['-Kering', ...args], env);
  assert.equal(r.kode, 0, `lab.ps1 -Kering gagal: ${r.galat}${r.keluar}`);
  return JSON.parse(r.keluar);
}

const pasangan = (a, kunci) => a.flatMap((x, i) => (x === kunci ? [a[i + 1]] : []));

function dockerTiruan() {
  // Pengganti docker: menjawab `image inspect` dengan ID dari TIRUAN_ID; pada `run` keluar dengan kode TIRUAN_KODE.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    'exit [int]$env:TIRUAN_KODE',
  ].join('\r\n'));
  return berkas;
}

function kunciSementara(imageLab) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  const kunci = { repo: [] };
  if (imageLab) kunci.image_lab = imageLab;
  fs.writeFileSync(berkas, JSON.stringify(kunci));
  return berkas;
}

test('mode biasa: tanpa jaringan, GPU, repo read-only, hanya data/keluaran yang bisa ditulis', () => {
  const a = argumenDocker(['python', '-V']);

  assert.deepEqual(pasangan(a, '--network'), ['none']);
  assert.ok(a.includes('--gpus') && a.includes('--read-only') && a.includes('no-new-privileges'));
  assert.deepEqual(pasangan(a, '--cap-drop'), ['ALL']);
  const pasang = pasangan(a, '--mount');
  assert.equal(pasang.length, 2, pasang.join(' | '));
  assert.match(pasang[0], /target=\/kerja,readonly$/);
  assert.match(pasang[1], /data\\keluaran,target=\/kerja\/data\/keluaran$/);
  assert.deepEqual(a.slice(-2), ['python', '-V']);
});

for (const mode of ['-Kamera', '-Jaringan']) {
  test(`mode ${mode} tidak ada di repo ini: ditolak (kode 2), lab hanya berjalan tanpa jaringan`, () => {
    const r = lab(['-Kering', mode, 'python', '-V']);

    assert.equal(r.kode, 2, r.keluar + r.galat);
    assert.match(r.keluar, /DITOLAK/);
  });
}

test('tanpa perintah: ditolak dengan petunjuk pakai (kode 2)', () => {
  assert.equal(lab(['-Kering']).kode, 2);
});

test('kunci bengkel sama dengan vision-seed: bila job lab lain memegang kunci, menunggu lalu menyerah dengan kode 3', async () => {
  const pemegang = spawn('powershell', ['-NoProfile', '-Command',
    `$m = New-Object System.Threading.Mutex($false, '${NAMA_KUNCI}'); [void]$m.WaitOne(); 'SIAP'; Start-Sleep -Seconds 30`]);
  try {
    await new Promise((selesai, gagal) => {
      pemegang.stdout.on('data', (d) => String(d).includes('SIAP') && selesai());
      pemegang.on('exit', () => gagal(new Error('pemegang kunci keluar sebelum SIAP')));
    });

    const r = lab(['-Kering', 'python', '-V'], { VS_KUNCI_TUNGGU_DTK: '2' });

    assert.equal(r.kode, 3, `harus kode 3 (bengkel dipakai), dapat ${r.kode}: ${r.keluar}${r.galat}`);
    assert.match(r.keluar + r.galat, /bengkel sedang dipakai/);
  } finally {
    pemegang.kill(); // satu proses powershell tanpa anak: aman dihentikan, mutex otomatis lepas
  }
});

test('kunci bengkel lepas: tanpa pemegang lain, lab.ps1 langsung jalan', () => {
  const r = lab(['-Kering', 'python', '-V'], { VS_KUNCI_TUNGGU_DTK: '2' });

  assert.equal(r.kode, 0, r.galat);
});

test('image lab yang ID-nya bukan yang tercatat di kunci tidak dijalankan (kode 6)', () => {
  const r = lab(['python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:lain' }),
    TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE TAK SESUAI KUNCI/);
});

test('kunci tanpa catatan image lab ditolak (kode 6): gagal tertutup', () => {
  const r = lab(['python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara(), TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 6, r.keluar + r.galat);
});

for (const kode of ['0', '4']) {
  test(`image sesuai kunci: perintah dijalankan dan kode keluarnya (${kode}) diteruskan apa adanya`, () => {
    const r = lab(['python', '-V'], {
      VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' }),
      TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: kode, VS_KUNCI_TUNGGU_DTK: '5',
    });

    assert.equal(r.kode, Number(kode), r.keluar + r.galat);
  });
}

test('-Fpo: image lab tambahan yang dijalankan, dengan janji yang sama (tanpa jaringan, repo read-only)', () => {
  const a = argumenDocker(['-Fpo', 'python', '-V']);

  assert.ok(a.includes('cctvgerbang-lab-fpo:v1') && !a.includes('vision-seed-lab:v1'));
  assert.deepEqual(pasangan(a, '--network'), ['none']);
  assert.match(pasangan(a, '--mount')[0], /target=\/kerja,readonly$/);
  assert.deepEqual(a.slice(-2), ['python', '-V']);
});

test('-Fpo dengan kunci tanpa catatan image_lab_fpo: tidak dijalankan (kode 6)', () => {
  const r = lab(['-Fpo', 'python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' }),
    TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE TAK SESUAI KUNCI/);
});

test('-Fpo mencocokkan ID image dengan image_lab_fpo, bukan image_lab', () => {
  const kunci = kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:lain' });
  fs.writeFileSync(kunci, JSON.stringify({ ...JSON.parse(fs.readFileSync(kunci, 'utf8')),
    image_lab_fpo: { nama: 'cctvgerbang-lab-fpo:v1', id: 'sha256:tiruan' } }));

  const r = lab(['-Fpo', 'python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunci, TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 0, r.keluar + r.galat);
});
