// Uji pintu pengambil video riset tools/ambil-video.ps1 (yt-dlp dari sumber terkunci, di container terisolasi).
// Yang dikunci di sini adalah JANJI di sisi host: alat hanya melihat sumbernya sendiri (read-only) dan SATU folder
// keluaran; tak pernah melihat repo, bobot, atau berkas host lain; opsi berisiko yt-dlp dimatikan dan tak bisa
// diselundupkan; alat yang tak persis sama dengan yang diaudit tidak dijalankan.
//
// Asal: disalin dari vision-seed @3591530 (tools/uji/ambil-video.test.mjs) pada 2026-10-13 (K14). Yang diubah di sini:
// uji `suara` diganti penolakan (proyek ini tidak memakai suara), dan image lab dijaga lewat ID di kunci vendor.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'ambil-video.ps1');
const OPSI_AMAN = ['--ignore-config', '--no-plugin-dirs', '--no-js-runtimes', '--no-remote-components', '--no-update',
  '--no-cache-dir', '--no-exec'];

function jalankan(args, env = {}) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', SKRIP, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
    timeout: 60_000,
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

function argumenDocker(args, env) {
  const r = jalankan(['-Kering', ...args], env);
  assert.equal(r.kode, 0, `ambil-video.ps1 -Kering gagal: ${r.galat}${r.keluar}`);
  return JSON.parse(r.keluar);
}

const pasangan = (a, kunci) => a.flatMap((x, i) => (x === kunci ? [a[i + 1]] : []));

function repoSementara() {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-alat-'));
  const git = (...a) => {
    const r = spawnSync('git', ['-C', folder, '-c', 'user.name=uji', '-c', 'user.email=uji@contoh.test', ...a], { encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
    return r.stdout.trim();
  };
  git('init', '--quiet');
  fs.writeFileSync(path.join(folder, 'isi.txt'), 'asli\n');
  git('add', '.');
  git('commit', '--quiet', '-m', 'awal');
  return { folder, sha: git('rev-parse', 'HEAD') };
}

function kunciSementara(sha, imageLab) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  const kunci = { repo: [{ nama: 'yt-dlp', repo: 'yt-dlp/yt-dlp', ref: 'uji', sha }] };
  if (imageLab) kunci.image_lab = imageLab;
  fs.writeFileSync(berkas, JSON.stringify(kunci));
  return berkas;
}

test('cari: container hanya melihat sumber alat (read-only) dan satu folder keluaran; tanpa repo, bobot, atau GPU', () => {
  const a = argumenDocker(['cari', 'kasir minimarket', '5']);

  const pasang = pasangan(a, '--mount');
  assert.equal(pasang.length, 2, pasang.join(' | '));
  assert.match(pasang[0], /vendor\\yt-dlp,target=\/alat,readonly$/);
  assert.match(pasang[1], /data\\video\\riset,target=\/keluar$/);
  assert.ok(!a.some((x) => /target=\/kerja/.test(x)), 'repo tak boleh terlihat dari dalam container');
  assert.ok(!a.some((x) => /models/.test(x)) && !a.includes('--gpus'));
  assert.ok(a.includes('--read-only') && a.includes('no-new-privileges'));
  assert.deepEqual(pasangan(a, '--cap-drop'), ['ALL']);
  assert.ok(pasangan(a, '--env').includes('PYTHONPATH=/alat') && pasangan(a, '--env').includes('YTDLP_NO_PLUGINS=1'));
});

test('cari: opsi berisiko yt-dlp dimatikan, kueri tiba sebagai SATU argumen, dan tak ada yang diunduh', () => {
  const a = argumenDocker(['cari', 'kasir minimarket --exec jahat', '5']);

  const i = a.indexOf('yt_dlp');
  assert.deepEqual(a.slice(i - 2, i + 1), ['python', '-m', 'yt_dlp']);
  for (const opsi of OPSI_AMAN) assert.ok(a.includes(opsi), `opsi ${opsi} hilang`);
  assert.ok(a.includes('--flat-playlist') && a.includes('--skip-download'));
  assert.equal(a.at(-1), 'ytsearch5:kasir minimarket --exec jahat');
  assert.ok(!a.includes('--exec'), '--exec di dalam kueri tak boleh menjadi argumen tersendiri');
});

test('unduh: nama berkas tetap, resolusi dibatasi, satu video, info asal-usul ikut ditulis', () => {
  const a = argumenDocker(['unduh', 'https://www.youtube.com/watch?v=abc123', '480']);

  for (const opsi of OPSI_AMAN) assert.ok(a.includes(opsi), `opsi ${opsi} hilang`);
  assert.ok(a.includes('--no-playlist') && a.includes('--write-info-json') && a.includes('--restrict-filenames'));
  assert.deepEqual(pasangan(a, '-o'), ['%(extractor)s-%(id)s.%(ext)s']);
  assert.deepEqual(pasangan(a, '--paths'), ['/keluar']);
  // Batas memakai `res` (sisi TERPENDEK), bukan `height`: video tegak 576x1024 punya tinggi 1024 dan dulu ditolak
  // seluruhnya oleh saringan height<=720 ("Requested format is not available", ditemukan pada uji TikTok 2026-10-10).
  assert.deepEqual(pasangan(a, '-S'), ['res:480']);
  assert.ok(!pasangan(a, '-f')[0].includes('height'), 'saringan keras tinggi tak boleh kembali');
  assert.equal(a.at(-1), 'https://www.youtube.com/watch?v=abc123');
});

test('unduh tanpa angka memakai batas resolusi bawaan 720', () => {
  const a = argumenDocker(['unduh', 'https://www.tiktok.com/@toko/video/123']);

  assert.deepEqual(pasangan(a, '-S'), ['res:720']);
});

for (const url of ['https://jahat.example/v', 'http://www.youtube.com/watch?v=abc', 'file:///etc/passwd', '--exec', '-U',
  'https://youtube.com.jahat.example/watch?v=abc']) {
  test(`unduh menolak alamat di luar daftar: ${url}`, () => {
    const r = jalankan(['-Kering', 'unduh', url]);

    assert.equal(r.kode, 2, r.keluar + r.galat);
    assert.match(r.keluar, /DITOLAK/);
  });
}

test('perintah tak dikenal dan jumlah hasil tak wajar ditolak', () => {
  assert.equal(jalankan(['-Kering', 'apa-saja', 'x']).kode, 2);
  assert.equal(jalankan(['-Kering', 'cari', 'kasir', '9999']).kode, 2);
  assert.equal(jalankan(['-Kering', 'unduh', 'https://youtu.be/abc', '99999']).kode, 2);
});

test('periksa: alat yang persis sama dengan kunci diterima', () => {
  const { folder, sha } = repoSementara();

  const r = jalankan(['periksa'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunciSementara(sha) });

  assert.equal(r.kode, 0, r.keluar + r.galat);
});

test('periksa: alat yang commit-nya bukan yang diaudit ditolak (kode 7)', () => {
  const { folder } = repoSementara();

  const r = jalankan(['periksa'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunciSementara('0'.repeat(40)) });

  assert.equal(r.kode, 7, r.keluar + r.galat);
  assert.match(r.keluar, /bukan commit yang diaudit/);
});

test('periksa: alat yang berkasnya diubah sesudah diaudit ditolak (kode 7)', () => {
  const { folder, sha } = repoSementara();
  fs.writeFileSync(path.join(folder, 'isi.txt'), 'disusupi\n');

  const r = jalankan(['periksa'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunciSementara(sha) });

  assert.equal(r.kode, 7, r.keluar + r.galat);
  assert.match(r.keluar, /berubah/);
});

test('unduh sungguhan (bukan -Kering) berhenti di gerbang alat sebelum menyentuh docker', () => {
  const { folder } = repoSementara();

  const r = jalankan(['unduh', 'https://youtu.be/abc'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunciSementara('0'.repeat(40)) });

  assert.equal(r.kode, 7, r.keluar + r.galat);
});

test('suara tidak ada di proyek ini: ditolak sebagai perintah tak dikenal (kode 2)', () => {
  // Di vision-seed perintah ini mengambil ucapan kasir. Proyek gerbang tidak memakai suara, jadi pintunya ditutup.
  const r = jalankan(['-Kering', 'suara', 'https://www.youtube.com/watch?v=abc123']);

  assert.equal(r.kode, 2, r.keluar + r.galat);
  assert.match(r.keluar, /tak dikenal/);
});

test('image lab yang ID-nya bukan yang tercatat di kunci tidak dijalankan (kode 6)', () => {
  // Repo ini tidak membangun image sendiri (K14): yang dijaga adalah "image yang dijalankan persis yang dicatat".
  const { folder, sha } = repoSementara();
  const kunci = kunciSementara(sha, { nama: 'vision-seed-lab:v1', id: `sha256:${'0'.repeat(64)}` });

  const r = jalankan(['info', 'https://youtu.be/abc'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunci });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE/);
});

test('kunci tanpa catatan image lab ditolak (kode 6): gagal tertutup', () => {
  const { folder, sha } = repoSementara();

  const r = jalankan(['info', 'https://youtu.be/abc'], { VS_ALAT_YTDLP: folder, VS_KUNCI_VENDOR: kunciSementara(sha) });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE/);
});

function dockerTiruan() {
  // Pengganti docker untuk uji rantai. Menjawab `image inspect` dengan ID dari TIRUAN_ID; pada `run` ia menulis satu
  // berkas bernama TIRUAN_BERKAS ke folder yang dipasang sebagai /keluar lalu keluar 0, seperti pengunduh yang
  // melapor berhasil.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    "$pasang = $args | Where-Object { $_ -like 'type=bind,source=*,target=/keluar' }",
    "$keluar = ($pasang -replace '^type=bind,source=', '') -replace ',target=/keluar$', ''",
    "Set-Content -LiteralPath (Join-Path $keluar $env:TIRUAN_BERKAS) -Value 'x'",
    'exit 0',
  ].join('\r\n'));
  return berkas;
}

function unduhDenganTiruan(namaBerkas) {
  const { folder, sha } = repoSementara();
  const keluar = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-keluar-'));
  const r = jalankan(['unduh', 'https://youtu.be/abc'], {
    VS_ALAT_YTDLP: folder,
    VS_KUNCI_VENDOR: kunciSementara(sha, { nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' }),
    VS_DOCKER: dockerTiruan(),
    VS_KELUAR: keluar,
    TIRUAN_ID: 'sha256:tiruan',
    TIRUAN_BERKAS: namaBerkas,
  });
  return { ...r, isiKeluar: fs.readdirSync(keluar) };
}

test('unduh yang meninggalkan berkas .part dilaporkan GAGAL (kode 8) walau pengunduhnya keluar 0', () => {
  // Terjadi 13 Okt pada 2 dari 49 video: unduhan terpotong di batas 400 MB, kode keluar 0, video utuhnya tidak ada.
  const r = unduhDenganTiruan('youtube-abc.mp4.part');

  assert.deepEqual(r.isiKeluar, ['youtube-abc.mp4.part'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 8, r.keluar + r.galat);
  assert.match(r.keluar, /UNDUHAN TERPOTONG/);
  assert.match(r.keluar, /youtube-abc\.mp4\.part/);
});

test('unduh yang menghasilkan berkas utuh tetap kode 0', () => {
  const r = unduhDenganTiruan('youtube-abc.mp4');

  assert.deepEqual(r.isiKeluar, ['youtube-abc.mp4'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 0, r.keluar + r.galat);
});
