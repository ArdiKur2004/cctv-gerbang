// Uji pintu pengambil berkas tools/ambil-berkas.ps1 (arsip dan catatan dataset, spec bagian 8.6).
// Yang dikunci di sini adalah JANJI di sisi host: container hanya melihat pengunduhnya sendiri (read-only) dan SATU
// folder keluaran; hanya berkas yang tercatat di kunci, hanya https, hanya host yang didaftar pintu; dan berhasil
// atau tidaknya dinilai dari berkasnya, bukan dari kode keluar pengunduh.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'ambil-berkas.ps1');
const BUTIR = { nama: 'contoh', url: 'https://codeload.github.com/a/b/zip/abc', berkas: 'contoh.zip', maks_gb: 1, sha256: '' };
const IMAGE = { nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' };
const HOST = ['data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com',
  'github.com', 'release-assets.githubusercontent.com'];

function kunci(butir = [BUTIR], imageLab = IMAGE) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  const isi = {};
  if (butir) isi.berkas = butir;
  if (imageLab) isi.image_lab = imageLab;
  fs.writeFileSync(berkas, JSON.stringify(isi));
  return berkas;
}

function jalankan(args, env = {}) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', SKRIP, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
    timeout: 60_000,
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

function argumenDocker(butir = BUTIR) {
  const r = jalankan(['-Kering', butir.nama], { VS_KUNCI_VENDOR: kunci([butir]) });
  assert.equal(r.kode, 0, `ambil-berkas.ps1 -Kering gagal: ${r.galat}${r.keluar}`);
  return JSON.parse(r.keluar);
}

const pasangan = (a, kunciArg) => a.flatMap((x, i) => (x === kunciArg ? [a[i + 1]] : []));

test('container hanya melihat folder pengunduh (read-only) dan satu folder keluaran; tanpa repo, bobot, atau GPU', () => {
  const a = argumenDocker();

  const pasang = pasangan(a, '--mount');
  assert.equal(pasang.length, 2, pasang.join(' | '));
  assert.match(pasang[0], /tools\\ambil,target=\/alat,readonly$/);
  assert.match(pasang[1], /data\\unduhan\\contoh,target=\/keluar$/);
  assert.ok(!a.some((x) => /target=\/kerja/.test(x)), 'repo tak boleh terlihat dari dalam container');
  assert.ok(!a.some((x) => /models|vendor/.test(x)) && !a.includes('--gpus'));
  assert.ok(a.includes('--read-only') && a.includes('no-new-privileges'));
  assert.deepEqual(pasangan(a, '--cap-drop'), ['ALL']);
  assert.deepEqual(pasangan(a, '--network'), ['bridge']);
});

test('yang dijalankan hanya pengunduh bawaan repo, dengan alamat, batas ukuran, dan daftar host dari pintunya', () => {
  const a = argumenDocker();

  const i = a.indexOf('/alat/ambil_berkas.py');
  assert.deepEqual(a.slice(i - 2, i + 1), ['python', '-I', '/alat/ambil_berkas.py']);
  assert.deepEqual(pasangan(a, '--alamat'), [BUTIR.url]);
  assert.deepEqual(pasangan(a, '--keluar'), ['/keluar']);
  assert.deepEqual(pasangan(a, '--nama'), ['contoh.zip']);
  assert.deepEqual(pasangan(a, '--maks-byte'), [String(1024 ** 3)]);
  assert.deepEqual(pasangan(a, '--host'), HOST);
  assert.ok(!a.includes('--sha256'), 'butir yang belum dikunci tidak mengirim sha256');
});

test('butir yang sudah dikunci mengirim SHA-256-nya ke pengunduh', () => {
  const a = argumenDocker({ ...BUTIR, sha256: 'a'.repeat(64) });

  assert.deepEqual(pasangan(a, '--sha256'), ['a'.repeat(64)]);
});

test('berkas rilis GitHub diterima: alamat github.com sampai ke pengunduh apa adanya', () => {
  const rilis = { ...BUTIR, url: 'https://github.com/a/b/releases/download/t/model.onnx', berkas: 'model.onnx', maks_gb: 0.1 };

  const a = argumenDocker(rilis);

  assert.deepEqual(pasangan(a, '--alamat'), [rilis.url]);
  assert.deepEqual(pasangan(a, '--nama'), ['model.onnx']);
});

const TOLAK = {
  'nama yang tidak tercatat di kunci': [['lain'], [BUTIR]],
  'nama berhuruf besar atau bertitik': [['../Contoh'], [BUTIR]],
  'nama yang tercatat dua kali': [['contoh'], [BUTIR, BUTIR]],
  'kunci tanpa daftar berkas': [['contoh'], null],
  'alamat bukan https': [['contoh'], [{ ...BUTIR, url: 'http://codeload.github.com/a/b/zip/abc' }]],
  'alamat di host yang mirip tetapi di luar daftar': [['contoh'], [{ ...BUTIR, url: 'https://codeload.github.com.jahat.example/a.zip' }]],
  'alamat di host GitHub yang mirip tetapi di luar daftar': [['contoh'], [{ ...BUTIR, url: 'https://github.com.jahat.example/a/b/releases/download/t/m.onnx' }]],
  'nama berkas jadi yang memuat folder': [['contoh'], [{ ...BUTIR, berkas: '..\\luar.zip' }]],
  'sha256 yang bukan 64 huruf heksa': [['contoh'], [{ ...BUTIR, sha256: 'abc' }]],
  'batas ukuran nol': [['contoh'], [{ ...BUTIR, maks_gb: 0 }]],
  'batas ukuran di atas plafon pintu': [['contoh'], [{ ...BUTIR, maks_gb: 999 }]],
};
for (const [judul, [args, butir]] of Object.entries(TOLAK)) {
  test(`ditolak sebelum menyentuh docker (kode 2): ${judul}`, () => {
    const r = jalankan(['-Kering', ...args], { VS_KUNCI_VENDOR: kunci(butir) });

    assert.equal(r.kode, 2, r.keluar + r.galat);
    assert.match(r.keluar, /DITOLAK/);
  });
}

function dockerTiruan() {
  // Pengganti docker untuk uji rantai. Menjawab `image inspect` dengan TIRUAN_ID. Pada `run` ia menulis berkas bernama
  // TIRUAN_BERKAS (bila diisi) ke folder yang dipasang sebagai /keluar, lalu keluar dengan TIRUAN_KODE.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    "$pasang = $args | Where-Object { $_ -like 'type=bind,source=*,target=/keluar' }",
    "$keluar = ($pasang -replace '^type=bind,source=', '') -replace ',target=/keluar$', ''",
    "if ($env:TIRUAN_BERKAS) { Set-Content -LiteralPath (Join-Path $keluar $env:TIRUAN_BERKAS) -Value 'x' }",
    '$kode = [int]$env:TIRUAN_KODE',
    'exit $kode',
  ].join('\r\n'));
  return berkas;
}

function ambilDenganTiruan({ berkas = '', kode = '0', butir = BUTIR, image = IMAGE, idTiruan = IMAGE.id } = {}) {
  const dasar = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-unduhan-'));
  const r = jalankan([butir.nama], {
    VS_KUNCI_VENDOR: kunci([butir], image),
    VS_DOCKER: dockerTiruan(),
    VS_KELUAR: dasar,
    TIRUAN_ID: idTiruan,
    TIRUAN_BERKAS: berkas,
    TIRUAN_KODE: kode,
  });
  const folder = path.join(dasar, butir.nama);
  return { ...r, isi: fs.existsSync(folder) ? fs.readdirSync(folder) : null };
}

test('image lab yang ID-nya bukan yang tercatat di kunci tidak dijalankan (kode 6)', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', idTiruan: 'sha256:lain' });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE/);
  assert.deepEqual(r.isi, [], 'pengunduh tidak boleh sempat berjalan');
});

test('kunci tanpa catatan image lab ditolak (kode 6): gagal tertutup', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', image: null });

  assert.equal(r.kode, 6, r.keluar + r.galat);
});

test('unduhan yang meninggalkan berkas .part dilaporkan GAGAL (kode 8) walau pengunduhnya keluar 0', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip.part' });

  assert.deepEqual(r.isi, ['contoh.zip.part'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 8, r.keluar + r.galat);
  assert.match(r.keluar, /UNDUHAN TERPOTONG/);
});

test('pengunduh yang keluar 0 tanpa meninggalkan berkas jadi dilaporkan GAGAL (kode 9)', () => {
  // Cacat sepupu dari pintu video: pengunduh yang menolak sebelum mulai mengunduh keluar 0 tanpa berkas apa pun.
  const r = ambilDenganTiruan({ berkas: '' });

  assert.deepEqual(r.isi, []);
  assert.equal(r.kode, 9, r.keluar + r.galat);
  assert.match(r.keluar, /TAK ADA BERKAS JADI/);
});

test('berkas jadi yang belum dikunci: kode 0, dengan peringatan bahwa ia belum boleh dibuka', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip' });

  assert.deepEqual(r.isi, ['contoh.zip']);
  assert.equal(r.kode, 0, r.keluar + r.galat);
  assert.match(r.keluar, /BELUM DIKUNCI/);
});

test('berkas jadi yang sudah dikunci: kode 0 tanpa peringatan', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', butir: { ...BUTIR, sha256: 'a'.repeat(64) } });

  assert.equal(r.kode, 0, r.keluar + r.galat);
  assert.doesNotMatch(r.keluar, /BELUM DIKUNCI/);
});

test('kode 7 dari pengunduh (SHA-256 tidak cocok) diteruskan apa adanya', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip.part', kode: '7' });

  assert.equal(r.kode, 7, r.keluar + r.galat);
});
