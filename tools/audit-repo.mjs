#!/usr/bin/env node
// Pemindai STATIS repo pihak ketiga — mencari tanda backdoor, kiriman data ke server lain, dan muatan berbahaya.
// Asal: disalin dari vision-seed @3591530 (tools/audit-repo.mjs) pada 2026-10-13 (K14). Yang diubah di sini: aturan
// unduh-otomatis ditambah urlopen, requests ber-stream, dan torch.hub.load_state_dict_from_url.
// HANYA membaca teks; tak pernah menjalankan, meng-import, atau meng-install apa pun dari repo yang dipindai.
// Hasilnya PETUNJUK untuk dibaca manusia, bukan vonis: "bersih" di sini ≠ terbukti aman (lihat docs/PROTOKOL-KEAMANAN-REPO.md).
//
// Pakai:  node tools/audit-repo.mjs <folder-repo> [--md laporan.md] [--json hasil.json] [--gagal-bila-tinggi] [--maks 25]
// Exit:   0 = laporan jadi · 1 = ada temuan TINGGI dan --gagal-bila-tinggi dipasang · 2 = argumen/folder salah
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const EXT_KODE = new Set(['.py', '.pyx', '.pyi', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.svelte', '.html',
  '.sh', '.bash', '.zsh', '.ps1', '.psm1', '.bat', '.cmd', '.go', '.rs', '.c', '.cc', '.cpp', '.cu', '.h', '.hpp',
  '.java', '.kt', '.rb', '.php', '.lua', '.toml', '.cfg', '.ini', '.yaml', '.yml', '.ipynb', '.json']);
const NAMA_KODE = new Set(['Dockerfile', 'Makefile', 'setup.py', 'setup.cfg', 'pyproject.toml', 'package.json']);
const EXT_MEDIA = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico', '.bmp', '.tif', '.tiff', '.mp4', '.mov',
  '.avi', '.webm', '.mkv', '.mp3', '.wav', '.ogg', '.flac', '.pdf', '.ttf', '.otf', '.woff', '.woff2', '.eot']);
const EXT_DOK = new Set(['.md', '.rst', '.txt', '.tex', '.bib', '.csv', '.tsv', '.license', '']);
const EXT_BINER = new Set(['.so', '.dll', '.exe', '.dylib', '.pyd', '.bin', '.pt', '.pth', '.ckpt', '.pkl', '.pickle', '.onnx',
  '.engine', '.whl', '.jar', '.msi', '.npy', '.npz', '.h5', '.safetensors', '.gguf', '.tflite', '.pb', '.zip', '.tar', '.gz', '.7z']);
const LEWATI_DIR = new Set(['.git', 'node_modules', '.venv', 'venv', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache']);
const MAKS_UKURAN = 2_000_000;

// Domain yang wajar muncul di repo ML (kode hosting, registry paket, makalah). Bucket umum (storage.googleapis.com,
// drive.google.com, s3) SENGAJA tidak dimasukkan: siapa pun bisa menaruh berkas di sana.
const DOMAIN_UMUM = ['github.com', 'raw.githubusercontent.com', 'objects.githubusercontent.com', 'huggingface.co', 'hf.co',
  'pypi.org', 'files.pythonhosted.org', 'pytorch.org', 'arxiv.org', 'doi.org', 'apache.org', 'opensource.org',
  'creativecommons.org', 'localhost', 'json-schema.org', 'www.w3.org', 'schemas.microsoft.com'];
const umum = (h) => DOMAIN_UMUM.some((d) => h === d || h.endsWith('.' + d));

const PY = (c) => ['.py', '.pyx', '.pyi', '.ipynb'].includes(c.ext);
const JS = (c) => ['.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.svelte', '.html'].includes(c.ext);
const SKRIP_SHELL = (c) => ['.sh', '.bash', '.zsh', '.ps1', '.psm1', '.bat', '.cmd'].includes(c.ext) || c.nama === 'Dockerfile' || c.nama === 'Makefile';
const BUKAN_JSON = (c) => c.ext !== '.json';
const SEMUA = () => true;

const IP_PRIVAT = /^(?:10\.|127\.|0\.0\.0\.0$|192\.168\.|169\.254\.|172\.(?:1[6-9]|2\d|3[01])\.|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.)/;
const ipPublik = (ip) => /^\d{1,3}(?:\.\d{1,3}){3}$/.test(ip) && ip.split('.').every((o) => +o <= 255) && !IP_PRIVAT.test(ip);
const RE_URL = /\b(?:https?|wss?|ftp):\/\/([a-zA-Z0-9.-]+)(?::\d+)?/g;
const MAGIC_GAMBAR = /^(?:iVBORw0KGgo|\/9j\/|R0lGOD|UklGR|PHN2Zy)/;

// tingkat: TINGGI = pola yang jarang punya alasan sah · SEDANG = wajar di banyak repo tapi wajib dibaca · INFO = inventaris
const ATURAN = [
  { id: 'exec-tersamar', tingkat: 'TINGGI', arti: 'menjalankan kode hasil decode/dekompresi (pola klasik muatan tersembunyi)', berlaku: BUKAN_JSON,
    cocok: (b) => /\b(?:exec|eval)\s*\(\s*(?:[\w.]*(?:b64decode|b32decode|a85decode|decompress|fromhex|loads)\b|base64|zlib|marshal|codecs)/.test(b)
      || /\b(?:eval|Function)\s*\(\s*(?:atob|Buffer\.from)\b/.test(b) || /\bmarshal\.loads\s*\(/.test(b) },
  { id: 'blob-base64', tingkat: 'TINGGI', arti: 'string base64 panjang di kode (bisa muatan tersembunyi)', berlaku: (c) => BUKAN_JSON(c) && c.ext !== '.ipynb',
    cocok: (b) => { const m = b.match(/['"`]([A-Za-z0-9+/]{300,}={0,2})['"`]/); return !!m && !MAGIC_GAMBAR.test(m[1]); } },
  { id: 'ip-publik', tingkat: 'TINGGI', arti: 'alamat IP publik tertanam (server tak bernama)', berlaku: SEMUA,
    cocok: (b) => [...b.matchAll(RE_URL)].some((m) => ipPublik(m[1])) || [...b.matchAll(/['"](\d{1,3}(?:\.\d{1,3}){3})['"]\s*,\s*\d{2,5}/g)].some((m) => ipPublik(m[1])) },
  { id: 'pipa-shell', tingkat: 'TINGGI', arti: 'unduh lalu langsung jalankan (curl|bash, iwr|iex)', berlaku: SEMUA,
    cocok: (b) => /\b(?:curl|wget)\b[^|\n]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b/.test(b) || /\b(?:curl|wget)\b[^|\n]*\|\s*python/.test(b)
      || /\b(?:iwr|irm|Invoke-WebRequest|Invoke-RestMethod)\b[^|\n]*\|\s*iex\b/i.test(b) || /\biex\s*\(\s*New-Object\s+Net\.WebClient/i.test(b) },
  { id: 'kait-install', tingkat: 'TINGGI', arti: 'kode yang jalan otomatis saat pip/npm install', berlaku: (c) => c.nama === 'setup.py' || c.nama === 'package.json',
    cocok: (b, c) => (c.nama === 'setup.py' && /class\s+\w+\s*\(\s*(?:install|develop|egg_info)\s*\)/.test(b))
      || (c.nama === 'package.json' && /"(?:preinstall|install|postinstall)"\s*:/.test(b)) },
  { id: 'ci-pr-target', tingkat: 'TINGGI', arti: 'workflow pull_request_target (jalur serangan insiden Ultralytics 2024)', berlaku: (c) => /^\.github\/workflows\//.test(c.rel),
    cocok: (b) => /\bpull_request_target\b/.test(b) },
  { id: 'rahasia-tertanam', tingkat: 'SEDANG', arti: 'kunci/token API tertulis di kode', berlaku: SEMUA,
    cocok: (b) => /\b(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{36}|hf_[A-Za-z0-9]{34}|xox[baprs]-[A-Za-z0-9-]{10,})\b/.test(b) },
  { id: 'cmdclass', tingkat: 'SEDANG', arti: 'perintah build kustom di setup.py (sering sah untuk ekstensi C/CUDA)', berlaku: (c) => c.nama === 'setup.py',
    cocok: (b) => /\bcmdclass\s*=/.test(b) },
  { id: 'telemetri', tingkat: 'SEDANG', arti: 'pustaka/kata kunci analitik & pelacakan pemakaian', berlaku: BUKAN_JSON,
    cocok: (b) => /\b(?:posthog|sentry_sdk|mixpanel|amplitude|google-analytics|googletagmanager|telemetry|usage[_-]?(?:stats|tracking|collection|analytics)|track_event|send_event|phone_?home)\b/i.test(b)
      || /@sentry\/|\bgtag\s*\(|\bsegment\.(?:io|com)\b/.test(b)
      // RUM / session replay / analitik web — celah v1 (Observer: datadogRum.init + sessionReplaySampleRate 100)
      || /\b(?:datadogRum|dd-trace|sessionReplaySampleRate|hotjar|logrocket|fullstory|newrelic|bugsnag|rollbar|smartlook|mouseflow|matomo|piwik|umami|heapanalytics|applicationinsights)\b/i.test(b)
      || /@datadog\/browser-|@fullstory\/|clarity\.ms|plausible\.io|cdn\.heapanalytics|static\.hotjar\.com/i.test(b) },
  { id: 'pustaka-jaringan', tingkat: 'SEDANG', arti: 'kode yang bisa membuka koneksi jaringan', berlaku: (c) => PY(c) || JS(c),
    cocok: (b, c) => PY(c)
      ? /^\s*import\s+[\w.,\s]*\b(?:requests|urllib3?|httpx|aiohttp|socket|websockets?|grpc|paramiko|ftplib|smtplib)\b/.test(b)
        || /^\s*from\s+(?:requests|urllib3?|urllib\.request|httpx|aiohttp|socket|websockets?|grpc|paramiko|ftplib|smtplib|http\.client)\b/.test(b)
      : /\bfetch\s*\(|\baxios\b|XMLHttpRequest|new\s+WebSocket\s*\(|(?:require\(\s*|from\s+)['"](?:node:)?(?:http|https|net|dgram|tls)['"]/.test(b) },
  { id: 'eksekusi-dinamis', tingkat: 'SEDANG', arti: 'exec/eval/subprocess (sering sah, tapi jalur favorit backdoor)', berlaku: (c) => PY(c) || JS(c),
    cocok: (b, c) => PY(c)
      ? /(?<![\w.])(?:exec|eval)\s*\(/.test(b) || /\bsubprocess\.(?:run|call|Popen|check_output|check_call|getoutput)\b|\bos\.(?:system|popen|exec\w*)\s*\(|\bpty\.spawn\b/.test(b)
      : /\bchild_process\b|\bnew\s+Function\s*\(|(?<![\w.])eval\s*\(/.test(b) },
  { id: 'deserialisasi-tak-aman', tingkat: 'SEDANG', arti: 'memuat pickle/torch/yaml dengan cara yang bisa menjalankan kode', berlaku: PY,
    cocok: (b, c, lanjut) => /\b(?:c?[Pp]ickle|dill|cloudpickle)\.loads?\s*\(|\bjoblib\.load\s*\(|allow_pickle\s*=\s*True/.test(b)
      || (/\btorch\.load\s*\(/.test(b) && !/weights_only\s*=\s*True/.test(lanjut))
      || (/\byaml\.load\s*\(/.test(b) && !/Loader\s*=\s*(?:yaml\.)?C?(?:Safe|Base)Loader/.test(lanjut)) },
  { id: 'kode-remote', tingkat: 'SEDANG', arti: 'mengunduh lalu menjalankan kode dari hub (trust_remote_code, torch.hub)', berlaku: PY,
    cocok: (b) => /trust_remote_code\s*=\s*True/.test(b) || /\btorch\.hub\.load\s*\(/.test(b) },
  { id: 'unduh-otomatis', tingkat: 'INFO', arti: 'mengunduh bobot/berkas saat berjalan (periksa sumber & hash)', berlaku: (c) => PY(c) || SKRIP_SHELL(c),
    cocok: (b) => /\bhf_hub_download\b|\bsnapshot_download\b|\.from_pretrained\s*\(|\bgdown\b|\burlretrieve\s*\(|\bwget\s+['"]?https?:|\bcurl\s+[^\n]*https?:\/\//.test(b)
      // Ditambah 2026-10-13: tiga pola yang lolos pada komponen calon (lihat uji).
      || /\burlopen\s*\(/.test(b) || /\bload_state_dict_from_url\b/.test(b) || /\brequests\.get\s*\([^)\n]*\bstream\s*=\s*True/.test(b) },
  { id: 'layanan-cloud-ml', tingkat: 'INFO', arti: 'integrasi layanan ML cloud (mengirim metrik/artefak bila diaktifkan)', berlaku: PY,
    cocok: (b) => /^\s*(?:import|from)\s+(?:wandb|comet_ml|neptune|clearml|mlflow)\b/.test(b) },
];

function jalani(akar) {
  const out = [];
  const tumpuk = [''];
  while (tumpuk.length) {
    const rel = tumpuk.pop();
    for (const e of fs.readdirSync(path.join(akar, rel), { withFileTypes: true })) {
      const r = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) { if (!LEWATI_DIR.has(e.name)) tumpuk.push(r); } else if (e.isFile()) out.push(r);
    }
  }
  return out.sort();
}

function barisKode(teks, ext) {
  if (ext !== '.ipynb') return teks.split(/\r?\n/).map((t, i) => ({ t, n: i + 1 }));
  try {
    const nb = JSON.parse(teks);
    return (nb.cells || []).flatMap((s, i) => s.cell_type !== 'code' ? []
      : [].concat(s.source || []).join('').split(/\r?\n/).map((t) => ({ t, n: `sel ${i + 1}` })));
  } catch { return teks.split(/\r?\n/).map((t, i) => ({ t, n: i + 1 })); }
}

export function pindai(akar) {
  const hasil = { akar, temuan: [], domain: {}, domainUmum: {}, biner: [], dipindai: 0, dilewati: [] };
  for (const rel of jalani(akar)) {
    const nama = path.basename(rel);
    const ext = path.extname(nama).toLowerCase();
    const penuh = path.join(akar, rel);
    const ukuran = fs.statSync(penuh).size;
    if (EXT_MEDIA.has(ext)) continue;
    let kepala;
    try { const fd = fs.openSync(penuh, 'r'); kepala = Buffer.alloc(Math.min(8000, ukuran)); fs.readSync(fd, kepala, 0, kepala.length, 0); fs.closeSync(fd); }
    catch { hasil.dilewati.push(`${rel} (tak terbaca)`); continue; }
    if (kepala.toString('utf8').startsWith('version https://git-lfs')) { hasil.biner.push({ berkas: rel, ukuran, jenis: 'pointer LFS (isi tidak diunduh)' }); continue; }
    if (EXT_BINER.has(ext) || kepala.includes(0)) { hasil.biner.push({ berkas: rel, ukuran, jenis: ext || 'tanpa ekstensi' }); continue; }
    const kode = EXT_KODE.has(ext) || NAMA_KODE.has(nama);
    if (!kode) continue; // dokumen (.md/.txt/...) tidak dieksekusi: tidak dipindai
    if (ext === '.json' && nama !== 'package.json' && ukuran > 200_000) { hasil.dilewati.push(`${rel} (JSON data besar)`); continue; }
    if (ukuran > MAKS_UKURAN) { hasil.dilewati.push(`${rel} (${(ukuran / 1e6).toFixed(1)} MB)`); continue; }
    hasil.dipindai++;
    const c = { rel, nama, ext };
    const baris = barisKode(fs.readFileSync(penuh, 'utf8'), ext);
    baris.forEach(({ t, n }, i) => {
      for (const m of t.matchAll(RE_URL)) {
        const h = m[1].toLowerCase().replace(/\.$/, '');
        if (/^\d{1,3}(?:\.\d{1,3}){3}$/.test(h) || !h.includes('.') && h !== 'localhost') continue;
        const wadah = umum(h) ? hasil.domainUmum : hasil.domain;
        wadah[h] = (wadah[h] || 0) + 1;
      }
      const lanjut = baris.slice(i, i + 4).map((x) => x.t).join(' ');
      for (const a of ATURAN) {
        if (a.berlaku(c) && a.cocok(t, c, lanjut)) {
          hasil.temuan.push({ aturan: a.id, tingkat: a.tingkat, berkas: rel, baris: n, cuplikan: t.trim().slice(0, 160) });
        }
      }
    });
  }
  return hasil;
}

function commitDari(akar) {
  const r = spawnSync('git', ['-C', akar, 'rev-parse', 'HEAD'], { encoding: 'utf8' });
  return r.status === 0 ? r.stdout.trim() : 'tidak diketahui';
}

export function laporanMd(h, maks = 25) {
  const urut = { TINGGI: 0, SEDANG: 1, INFO: 2 };
  const per = Object.groupBy ? Object.groupBy(h.temuan, (t) => t.aturan)
    : h.temuan.reduce((a, t) => ((a[t.aturan] ||= []).push(t), a), {});
  const daftar = ATURAN.filter((a) => per[a.id]).sort((a, b) => urut[a.tingkat] - urut[b.tingkat]);
  const dom = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([d, n]) => `\`${d}\` (${n})`).join(' · ') || '—';
  const L = [];
  L.push(`# Audit statis: \`${path.basename(path.resolve(h.akar))}\``, '');
  L.push(`- Commit: \`${commitDari(h.akar)}\` · berkas kode dipindai: **${h.dipindai}** · dilewati: ${h.dilewati.length}`);
  L.push(`- TINGGI: **${h.temuan.filter((t) => t.tingkat === 'TINGGI').length}** · SEDANG: **${h.temuan.filter((t) => t.tingkat === 'SEDANG').length}** · INFO: ${h.temuan.filter((t) => t.tingkat === 'INFO').length}`, '');
  L.push('## Ringkasan per aturan', '', '| Aturan | Tingkat | Jumlah | Arti |', '|---|---|---|---|');
  for (const a of daftar) L.push(`| \`${a.id}\` | ${a.tingkat} | ${per[a.id].length} | ${a.arti} |`);
  if (!daftar.length) L.push('| — | — | 0 | tak ada pola yang cocok |');
  L.push('', '## Domain yang disebut di KODE', '', `- **Perlu dicek (bukan domain umum):** ${dom(h.domain)}`, `- Domain umum: ${dom(h.domainUmum)}`);
  L.push('', `## Berkas biner / bobot (${h.biner.length})`, '');
  for (const b of h.biner.slice(0, maks)) L.push(`- \`${b.berkas}\` · ${(b.ukuran / 1e6).toFixed(2)} MB · ${b.jenis}`);
  if (h.biner.length > maks) L.push(`- … +${h.biner.length - maks} lagi`);
  L.push('', '## Temuan', '');
  for (const a of daftar) {
    L.push(`### \`${a.id}\` — ${a.tingkat} (${per[a.id].length})`);
    for (const t of per[a.id].slice(0, maks)) L.push(`- \`${t.berkas}:${t.baris}\` — \`${t.cuplikan.replace(/`/g, "'")}\``);
    if (per[a.id].length > maks) L.push(`- … +${per[a.id].length - maks} lagi`);
    L.push('');
  }
  L.push('> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut',
    '> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.');
  return L.join('\n') + '\n';
}

function utama(argv) {
  const folder = argv.find((a) => !a.startsWith('--') && !['--md', '--json', '--maks'].includes(argv[argv.indexOf(a) - 1]));
  const opsi = (k) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : undefined; };
  if (!folder || !fs.existsSync(folder) || !fs.statSync(folder).isDirectory()) {
    console.error(`Folder repo tidak ada: ${folder ?? '(kosong)'}\nPakai: node tools/audit-repo.mjs <folder-repo> [--md out.md] [--json out.json] [--gagal-bila-tinggi]`);
    return 2;
  }
  const h = pindai(folder);
  const md = laporanMd(h, Number(opsi('--maks') ?? 25));
  if (opsi('--md')) fs.writeFileSync(opsi('--md'), md); else process.stdout.write(md);
  if (opsi('--json')) fs.writeFileSync(opsi('--json'), JSON.stringify(h, null, 2));
  const tinggi = h.temuan.filter((t) => t.tingkat === 'TINGGI').length;
  console.error(`${path.basename(path.resolve(folder))}: TINGGI=${tinggi} SEDANG=${h.temuan.filter((t) => t.tingkat === 'SEDANG').length} domain-asing=${Object.keys(h.domain).length} biner=${h.biner.length}`);
  return argv.includes('--gagal-bila-tinggi') && tinggi > 0 ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exit(utama(process.argv.slice(2)));
