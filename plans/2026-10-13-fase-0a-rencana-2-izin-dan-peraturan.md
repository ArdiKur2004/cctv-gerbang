# Fase 0A, Rencana 2: Vonis izin komponen dan peraturan plat — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Mengunci tiap komponen calon ke satu commit, membaca izinnya dari berkas aslinya (kode, bobot, dan bahan latih
dinilai terpisah), memindai kodenya sebelum dijalankan, dan meringkas peraturan plat dari teks aslinya.

**Architecture:** Dua alat disalin dari vision-seed ke `tools/`: pengunci repo (clone persis di commit tercatat, tanpa
memasang atau menjalankan apa pun) dan pemindai statis (hanya membaca teks). Hasil kerja rencana ini berupa catatan
yang bisa diperiksa ulang: entri di `tools/vendor.lock.json`, salinan berkas izin di `docs/lisensi/`, laporan pindai
di `docs/audit/`, satu tabel vonis, dan satu ringkasan peraturan.

**Tech Stack:** Node 24 (`node:test`) · Windows PowerShell 5.1 · git. Tidak ada paket yang dipasang. Yang diunduh
hanya **kode sumber** repo calon (lewat `git clone`) dan satu PDF peraturan; tidak ada bobot model dan tidak ada
dataset.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md)
bagian 8.1 langkah 2 dan 3, bagian 2.3, dan bagian 8.6. Aturan proyek `../CLAUDE.md` §5 dan §6. Calon komponen
berasal dari [`../docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md`](../docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md),
yang vonisnya masih **sementara**: rencana inilah yang membuatnya sah.

---

## Penyesuaian terhadap pembagian di Rencana 1

Rencana 1 menulis bahwa Rencana 2 juga memuat "unduhan dataset berizin". Itu dipindah ke Rencana 3, karena mengunduh
dataset butuh pintu unduh berkas yang belum ada, dan pintu itu satu keluarga dengan pekerjaan bahan lainnya
(pemilahan video, plat buatan komputer). Rencana 2 jadi hanya memuat pengetahuan: izin dan peraturan.

| Rencana | Isi | Status |
|---|---|---|
| 1 | Bengkel | Selesai 13 Okt |
| **2 (dokumen ini)** | Vonis izin komponen; peraturan plat | Ditulis |
| 3 | Pintu unduh berkas; dataset berizin; pemilahan 45 video; pembuat plat buatan komputer; set uji pertama | Ditulis saat Rencana 2 selesai |
| 4 | Pembanding; mesin belajar pertama; taksiran kecepatan; laporan ke `bukti/` | Ditulis saat Rencana 3 selesai |

## Aturan eksekusi untuk semua task

- **Clone bukan menjalankan.** Tidak ada `pip install`, `uv sync`, `npm install`, atau skrip dari repo yang diklon.
  Menjalankan komponen baru terjadi di Rencana 4, lewat `tools\lab.ps1` (tanpa jaringan).
- **Izin dibaca dari berkasnya, pada commit yang dikunci.** Label di halaman repo, ringkasan pencarian, dan catatan
  survei bukan bukti.
- **Tiga izin dinilai terpisah:** kode, bobot bawaan, dan bahan yang melatih bobot itu. Yang tidak dinyatakan ditulis
  "tidak dinyatakan", tidak diisi dengan dugaan.
- **Satu suite uji pada satu waktu.** Tanpa `| tail` atau `| head` pada perintah uji. Gerbang uji: `npm test`.
- **vision-seed hanya dibaca.**
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri baris
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Semua perintah dijalankan dari akar repo `D:\Projects\super-team-v1\cctvgerbang-seed` lewat Git Bash, kecuali
  disebut lain.

## Arti vonis

Sama dengan `tools/bahan.mjs` dan catatan survei, supaya satu kata berarti satu hal di seluruh repo:

| Vonis | Arti |
|---|---|
| `BOLEH-PRODUK` | Izinnya membolehkan produk tertutup yang dijual, dan buktinya diarsipkan |
| `RISET-SAJA` | Hanya untuk belajar di lab (K15). Tidak boleh masuk mesin jualan |
| `DILARANG` | Tidak boleh masuk produk: GPL, AGPL, bergantung pada `ultralytics`, atau melarang pemakaian komersial dalam produksi |
| `BELUM-JELAS` | Izin tidak dinyatakan atau tidak berhasil dibaca. Diperlakukan seperti `RISET-SAJA` sampai jelas |

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/klon-terkunci.ps1` (baru, disalin lalu disesuaikan) | Clone repo persis di commit yang tercatat di kunci | 1 |
| `tools/uji/klon-terkunci.test.mjs` (baru) | Uji pengunci repo dengan "GitHub tiruan" lokal | 1 |
| `tools/audit-repo.mjs` (baru, disalin) | Pemindai statis: hanya membaca teks | 1 |
| `tools/uji/audit-repo.test.mjs` (baru, disalin) | Uji pemindai | 1 |
| `tools/vendor.lock.json` (ubah) | Ditambah satu entri per komponen calon | 2 |
| `docs/lisensi/<pemilik>__<repo>/` (baru) | Salinan berkas izin pada commit yang dikunci | 2 |
| `docs/audit/<nama>@<sha7>.md` (baru) | Laporan pindai + catatan baca manual | 2 |
| `docs/VONIS-LISENSI.md` (baru) | Satu tabel vonis: kode, bobot, bahan latih, bukti | 2 |
| `docs/peraturan-plat.md` (baru) | Ringkasan peraturan plat dengan nomor pasal | 3 |
| `data-asal/bahan.json` (ubah) | Ditambah entri untuk bobot, dataset, dan huruf yang sudah bervonis | 4 |
| `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | B12 dan B2 diperbarui; hasil dicatat | 4 |

---

### Task 1: Pengunci repo dan pemindai statis

Pengunci disalin dari vision-seed lalu diberi satu pengganti alamat asal (`VS_ASAL_GIT`), supaya rantainya bisa diuji
dengan repo lokal tanpa menyentuh GitHub. vision-seed tidak punya uji untuk alat ini; di sini uji itu ditulis.
Pemindai disalin apa adanya bersama ujinya.

**Files:**
- Create: `tools/klon-terkunci.ps1`
- Create: `tools/audit-repo.mjs`
- Test: `tools/uji/klon-terkunci.test.mjs`
- Test: `tools/uji/audit-repo.test.mjs`

- [ ] **Step 1: Salin ketiga berkas apa adanya**

Run:

```bash
VS="D:/Projects/super-team-v1/vision-seed"
cp "$VS/tools/klon-terkunci.ps1" "$VS/tools/audit-repo.mjs" tools/
cp "$VS/tools/uji/audit-repo.test.mjs" tools/uji/
git -C "$VS" log --oneline -1
```

Expected: tiga berkas baru ada, dan commit vision-seed yang tercetak adalah `3591530`. Bila commit-nya lain, pakai
commit yang tercetak di kalimat "Asal" pada Step 4.

- [ ] **Step 2: Tulis uji pengunci repo**

Buat `tools/uji/klon-terkunci.test.mjs`:

```js
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
  // (Dikoreksi saat eksekusi 13 Okt: versi rencana semula membandingkan berkas di cakram dan gagal karena CRLF.)
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
```

- [ ] **Step 3: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 73`, `ℹ fail 2`, `EXIT=1`. Dua uji pertama di `klon-terkunci.test.mjs` gagal: pengunci salinan
belum mengenal `VS_ASAL_GIT`, jadi ia mencoba `https://github.com/uji-lokal/contoh.git` dan melapor
`GAGAL  contoh: clone`. Uji ketiga dan empat uji `audit-repo.test.mjs` sudah lulus karena perilakunya diwarisi dari
salinan. 66 uji lama tetap lulus.

- [ ] **Step 4: Sesuaikan `tools/klon-terkunci.ps1` dan beri asal-usul pada pemindai**

(a) Di `tools/klon-terkunci.ps1`, ganti blok `.DESCRIPTION` (dari baris `.DESCRIPTION` sampai baris sebelum
`.EXAMPLE`) menjadi:

```
.DESCRIPTION
  Asal: disalin dari vision-seed @3591530 (tools\klon-terkunci.ps1) pada 2026-10-13 (K14). Yang diubah di sini: alamat
  asal bisa diganti lewat VS_ASAL_GIT, supaya rantainya bisa diuji dengan repo lokal (tools\uji\klon-terkunci.test.mjs).

  Hanya clone + checkout. TIDAK menjalankan install, skrip repo, atau mengunduh bobot:
  Git LFS dimatikan (GIT_LFS_SKIP_SMUDGE=1) sehingga berkas model besar tidak ikut turun.
  Setelah checkout, HEAD dibandingkan dengan SHA di kunci. Beda atau gagal => exit 1.
  Clone != menjalankan: baca kodenya dulu (CLAUDE.md §6) sebelum memasang apa pun.

```

(b) Di berkas yang sama, tepat sesudah baris `$env:GIT_LFS_SKIP_SMUDGE = '1'`, tambahkan:

```powershell
# Untuk uji rantai: "GitHub" bisa diganti folder lokal. Di luar uji, asalnya selalu github.com.
$asal = if ($env:VS_ASAL_GIT) { $env:VS_ASAL_GIT } else { 'https://github.com/' }
```

(c) Di berkas yang sama, ganti

```powershell
    git clone --quiet --filter=blob:none --no-checkout ("https://github.com/" + $e.repo + ".git") $folder
```

menjadi

```powershell
    git clone --quiet --filter=blob:none --no-checkout ($asal + $e.repo + ".git") $folder
```

(d) Di `tools/audit-repo.mjs`, tepat sesudah baris kedua berkas
(`// Pemindai STATIS repo pihak ketiga — mencari tanda backdoor, ...`), tambahkan satu baris:

```js
// Asal: disalin apa adanya dari vision-seed @3591530 (tools/audit-repo.mjs) pada 2026-10-13 (K14).
```

(e) Di `tools/uji/audit-repo.test.mjs`, tepat sesudah baris komentar pertama berkas, tambahkan satu baris:

```js
// Asal: disalin apa adanya dari vision-seed @3591530 (tools/uji/audit-repo.test.mjs) pada 2026-10-13 (K14).
```

- [ ] **Step 5: Jalankan uji untuk memastikan lulus**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 73`, `ℹ pass 73`, `ℹ fail 0`, `EXIT=0`

- [ ] **Step 6: Commit**

```bash
git add tools/klon-terkunci.ps1 tools/audit-repo.mjs tools/uji/klon-terkunci.test.mjs tools/uji/audit-repo.test.mjs
git commit -q -F - <<'EOF'
Pengunci repo dan pemindai statis

Rantai pasok (CLAUDE.md §6): repo pihak ketiga dikunci ke satu commit dan
dibaca dulu sebelum dijalankan. Kedua alatnya disalin dari vision-seed
@3591530 (K14).

Pengunci diberi satu pengganti alamat asal supaya rantainya bisa diuji
dengan repo lokal. vision-seed tidak punya uji untuk alat ini; di sini
ditulis tiga: klon persis di commit tercatat, commit yang tak ada ditolak,
dan nama yang tak tercatat ditolak.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Mengunci, mengarsipkan izin, dan memindai tiap komponen calon

Sepuluh komponen. Enam diklon dan dipindai sekarang karena akan dijalankan di putaran ukur pertama (Rencana 4); empat
hanya dibaca izinnya, dan baru diklon bila putaran pertama menunjukkan perlunya.

| # | `nama` | `repo` | Acuan yang dikunci | Peran | Sekarang |
|---|---|---|---|---|---|
| 1 | `rf-detr` | `roboflow/rf-detr` | Sama dengan vision-seed (dibaca dari kuncinya) | Pendeteksi acuan | Klon + pindai |
| 2 | `trackers` | `roboflow/trackers` | Sama dengan vision-seed (dibaca dari kuncinya) | Pelacak | Klon + pindai |
| 3 | `yolox` | `Megvii-BaseDetection/YOLOX` | Tag rilis terbaru | Pendeteksi ringan | Klon + pindai |
| 4 | `fast-plate-ocr` | `ankandrew/fast-plate-ocr` | Tag rilis terbaru | Pembaca huruf; bagian pembanding | Klon + pindai |
| 5 | `open-image-models` | `ankandrew/open-image-models` | Tag rilis terbaru | Bagian pembanding (pendeteksi plat) | Klon + pindai |
| 6 | `fast-alpr` | `ankandrew/fast-alpr` | Tag rilis terbaru | Pembanding paket jadi | Klon + pindai |
| 7 | `d-fine` | `Peterande/D-FINE` | Kepala cabang bawaan | Pendeteksi ringan cadangan | Izin saja |
| 8 | `nanodet` | `RangiLyu/nanodet` | Tag rilis terbaru | Pendeteksi ringan cadangan | Izin saja |
| 9 | `paddleocr` | `PaddlePaddle/PaddleOCR` | Tag rilis terbaru | Pembaca huruf cadangan | Izin saja |
| 10 | `qwen3-vl` | `QwenLM/Qwen3-VL` | Sama dengan vision-seed (dibaca dari kuncinya) | Pelabel otomatis (alat lab) | Izin saja |

**Files:**
- Modify: `tools/vendor.lock.json`
- Create: `docs/lisensi/<pemilik>__<repo>/` untuk tiap komponen
- Create: `docs/audit/<nama>@<sha7>.md` untuk komponen 1 sampai 6
- Create: `docs/VONIS-LISENSI.md`

- [ ] **Step 1: Baca tiga entri dari kunci vision-seed (dibaca, tidak diketik ulang)**

Run:

```bash
node -e 'const k=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));for(const n of ["rf-detr","trackers","qwen3-vl"]){const r=k.repo.find(x=>x.nama===n);console.log(JSON.stringify({nama:r.nama,repo:r.repo,ref:r.ref,sha:r.sha}))}' "D:/Projects/super-team-v1/vision-seed/tools/vendor.lock.json"
```

Expected: tiga baris JSON berisi `nama`, `repo`, `ref`, dan `sha` 40 karakter. Pakai nilai yang tercetak itu di Step 3.

- [ ] **Step 2: Tentukan commit untuk tujuh komponen lain**

Untuk komponen bertag (3, 4, 5, 6, 8, 9), jalankan per repo, dengan `<repo>` dari tabel:

```bash
git ls-remote --tags --sort=-v:refname "https://github.com/<repo>.git" | sed -n '1,12p'
```

Expected: daftar tag, terbaru di atas, masing-masing diawali SHA. Pilih **tag rilis terbaru yang bukan pra-rilis**
(bukan `rc`, `dev`, `alpha`, `beta`). Bila sebuah tag punya baris kedua berakhiran `^{}`, SHA di baris `^{}` itulah
commit-nya; kalau tidak, SHA di baris tag itu sendiri.

Untuk komponen 7 (`d-fine`), yang tidak dirilis lewat tag:

```bash
git ls-remote "https://github.com/Peterande/D-FINE.git" HEAD
```

Expected: satu baris `<sha>	HEAD`. Catat SHA itu dan tanggal hari ini sebagai `ref` (bentuk `HEAD@2026-10-13`).

Bila sebuah repo tidak bisa dihubungi atau tidak punya tag rilis, **jangan menebak**: catat komponen itu di
`docs/VONIS-LISENSI.md` dengan vonis `BELUM-JELAS` dan alasan "commit tidak bisa ditentukan", lalu lanjut ke
komponen berikutnya.

- [ ] **Step 3: Tambahkan sepuluh entri ke `tools/vendor.lock.json`**

Di dalam daftar `"repo"`, sesudah entri `yt-dlp`, tambahkan satu entri per komponen dengan bentuk ini (satu baris per
entri; `vonis` diisi `BELUM-JELAS` dulu dan diperbarui di Step 8):

```json
{ "nama": "<nama>", "repo": "<repo>", "ref": "<tag, atau HEAD@tanggal>", "sha": "<sha 40 karakter dari Step 1 atau 2>", "lisensi_kode": "", "lisensi_bobot": "", "vonis": "BELUM-JELAS", "peran": "<peran dari tabel>", "diklon": <true untuk komponen 1-6, false untuk 7-10>, "dicatat": "2026-10-13" }
```

Run: `node -e 'const k=JSON.parse(require("fs").readFileSync("tools/vendor.lock.json","utf8"));console.log(k.repo.length, k.repo.every(r=>/^[0-9a-f]{40}$/.test(r.sha)))'`
Expected: `11 true` (sepuluh komponen + `yt-dlp`), atau angka yang lebih kecil sebanyak komponen yang di Step 2
dicatat "commit tidak bisa ditentukan".

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ fail 0`, `EXIT=0`. Kunci yang berubah tidak boleh merusak pintu pengunduh dan pintu lab.

- [ ] **Step 4: Klon enam komponen yang akan dijalankan**

Run (PowerShell):
`powershell -NoProfile -File tools\klon-terkunci.ps1 -Nama rf-detr,trackers,yolox,fast-plate-ocr,open-image-models,fast-alpr; "EXIT=$LASTEXITCODE"`
Expected: enam baris `OK     <nama> ...`, lalu `6 entri cocok dengan kunci.` dan `EXIT=0`. Bila ada baris `GAGAL` atau
`BEDA`, berhenti: commit di kunci tidak sama dengan yang didapat. Periksa SHA di Step 2 sebelum melanjutkan.

Run: `git status --short`
Expected: hanya `tools/vendor.lock.json` yang berubah. Folder `vendor/` di-gitignore dan tidak boleh muncul.

- [ ] **Step 5: Arsipkan berkas izin, pada commit yang dikunci**

Untuk komponen 1 sampai 6 (sudah diklon), jalankan per komponen. `<nama>` dan `<sha>` dari kunci; `<pemilik>__<repo>`
adalah kolom `repo` dengan `/` diganti `__`:

```bash
T="docs/lisensi/<pemilik>__<repo>"; mkdir -p "$T"
for f in $(git -C "vendor/<nama>" ls-tree --name-only "<sha>" | grep -i -E '^(licen[sc]e|copying|notice)'); do
  git -C "vendor/<nama>" show "<sha>:$f" > "$T/$f"
done
ls -la "$T"
```

Expected: paling sedikit satu berkas izin tidak kosong di folder itu. Bila folder itu kosong, repo tersebut tidak
punya berkas izin di akarnya: catat "tidak ada berkas izin di akar repo" untuk komponen itu, dan vonis kodenya
`BELUM-JELAS`.

Untuk komponen 7 sampai 10 (izin saja), ambil hanya berkas izinnya lewat klon sementara tanpa isi:

```bash
S="$TEMP/izin-<nama>"; rm -rf "$S"
GIT_LFS_SKIP_SMUDGE=1 git clone --quiet --filter=blob:none --no-checkout "https://github.com/<repo>.git" "$S"
git -C "$S" cat-file -e "<sha>^{commit}" || git -C "$S" fetch --quiet origin "<sha>"
T="docs/lisensi/<pemilik>__<repo>"; mkdir -p "$T"
for f in $(git -C "$S" ls-tree --name-only "<sha>" | grep -i -E '^(licen[sc]e|copying|notice)'); do
  git -C "$S" show "<sha>:$f" > "$T/$f"
done
ls -la "$T"; rm -rf "$S"
```

Expected: sama dengan di atas. Yang turun dari jaringan hanya daftar berkas dan berkas izinnya, bukan seluruh repo.

- [ ] **Step 6: Pindai keenam komponen yang diklon, lalu baca temuannya**

Run per komponen (`<sha7>` = tujuh karakter pertama SHA):

```bash
mkdir -p docs/audit
node tools/audit-repo.mjs "vendor/<nama>" --md "docs/audit/<nama>@<sha7>.md"; echo "EXIT=$?"
sed -n '1,20p' "docs/audit/<nama>@<sha7>.md"
```

Expected: `EXIT=0` dan laporan yang kepalanya memuat commit, jumlah berkas yang dipindai, dan jumlah temuan
`TINGGI` / `SEDANG` / `INFO`.

Lalu, untuk tiap laporan, **baca sendiri** setiap temuan `TINGGI` dan setiap temuan `unduh-otomatis` di berkas
aslinya (`vendor/<nama>/<jalur>`), dan tambahkan di akhir laporan itu bagian:

```markdown
## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| <id aturan> | <jalur berkas> | <apa yang sebenarnya dilakukan baris itu> | <wajar / dihindari dengan cara ... / alasan komponen ditolak> |

**Unduhan otomatis:** <berkas mana yang mengunduh apa, dari alamat mana, dan apakah keutuhannya diperiksa>.
**Batas:** pemindai statis hanya petunjuk; berkas yang tidak ditandai tidak dibaca baris demi baris.
```

Satu baris per temuan `TINGGI`. Bila tidak ada temuan `TINGGI`, tulis satu baris "tidak ada temuan TINGGI".
Temuan yang tidak bisa dijelaskan sesudah dibaca adalah alasan sah untuk memberi vonis `BELUM-JELAS` dan tidak
menjalankan komponen itu.

- [ ] **Step 7: Baca izin bobot dan bahan latihnya dari sumber aslinya**

Izin kode sudah diarsipkan di Step 5. Izin bobot dan bahan latih biasanya tidak ada di berkas `LICENSE`. Untuk tiap
komponen, baca sumber berikut **pada commit yang dikunci** dan catat kalimat persisnya beserta alamatnya di
`docs/lisensi/<pemilik>__<repo>/BOBOT.md`:

| Komponen | Yang dibaca |
|---|---|
| `rf-detr` | Bagian "License" di `vendor/rf-detr/README.md`: ukuran mana berizin Apache dan mana yang tidak. Bandingkan dengan butir `_bobot` di kunci vision-seed |
| `trackers` | `vendor/trackers/README.md`: apakah pelacak butuh bobot sama sekali |
| `yolox` | `vendor/yolox/README.md`: tabel bobot, dari mana diunduh, dilatih dengan apa, dan apakah izinnya dinyatakan |
| `fast-plate-ocr` | `vendor/fast-plate-ocr/README.md` dan berkas konfigurasi model: asal bobot, bahan latih, daftar wilayah (apakah Indonesia ada) |
| `open-image-models` | `vendor/open-image-models/README.md` dan kode pengunduh bobotnya: dari mana bobot pendeteksi plat berasal dan dengan kode apa dilatih |
| `fast-alpr` | `vendor/fast-alpr/pyproject.toml`: dependensinya, dan apakah ada `ultralytics` |
| `d-fine`, `nanodet`, `paddleocr`, `qwen3-vl` | Berkas izin yang diarsipkan di Step 5. Izin bobotnya ditulis "belum dibaca: komponen belum diklon" |

Isi `BOBOT.md` per komponen:

```markdown
# Izin bobot dan bahan latih: <nama> @ <sha7>

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci, atau alamat) |
|---|---|---|
| Izin bobot | "<kutipan>" atau "tidak dinyatakan" | <jalur berkas atau alamat> |
| Bahan latih bobot | "<kutipan>" atau "tidak dinyatakan" | <jalur berkas atau alamat> |
| Izin bahan latih | "<kutipan>" atau "tidak dinyatakan" | <jalur berkas atau alamat> |
| Bergantung pada `ultralytics` | ya / tidak, dilihat di <berkas dependensi> | <jalur berkas> |
| Format bobot | pickle (`.pt`, `.pth`, `.bin`) / ONNX / safetensors | <jalur berkas atau alamat> |
| Unduhan otomatis saat dipakai | ya / tidak; keutuhan diperiksa atau tidak | <jalur berkas> |
```

Yang tidak tertulis di sumber ditulis "tidak dinyatakan". Pernyataan pemelihara di sebuah issue boleh dicatat sebagai
keterangan, dengan alamat issue-nya, tetapi **bukan** pengganti berkas izin.

- [ ] **Step 8: Tulis `docs/VONIS-LISENSI.md` dan perbarui kunci**

Buat `docs/VONIS-LISENSI.md` dengan kepala ini, lalu satu baris per komponen:

```markdown
# Vonis izin komponen (B12)

> Dibuat 2026-10-13 dalam Rencana 2 Fase 0A. Tiap vonis dibaca dari berkas pada commit yang dikunci di
> `tools/vendor.lock.json`; buktinya diarsipkan di `docs/lisensi/`. Kode, bobot, dan bahan latih dinilai terpisah
> (`CLAUDE.md` §5). Yang tidak dinyatakan sumbernya ditulis "tidak dinyatakan".
>
> Vonis ini menggantikan vonis sementara di `docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md` untuk
> komponen yang tercantum. Komponen bertanda "izin saja" belum diklon dan belum dipindai: vonis kodenya sah, vonis
> bobotnya belum.

| Komponen @ commit | Peran | Izin kode | Izin bobot | Bahan latih bobot dan izinnya | Pakai `ultralytics` | Vonis kode | Vonis bobot | Bukti |
|---|---|---|---|---|---|---|---|---|
```

Aturan mengisi vonis, diterapkan tanpa kelonggaran:

| Yang terbaca | Vonis |
|---|---|
| Izin kode MIT, Apache-2.0, BSD, atau Unlicense, terbaca di berkas arsip | Kode `BOLEH-PRODUK` |
| Izin kode GPL atau AGPL, atau dependensinya memuat `ultralytics` | Kode `DILARANG` |
| Berkas izin tidak ada, atau isinya tidak baku | Kode `BELUM-JELAS` |
| Izin bobot dinyatakan permisif **dan** bahan latihnya dinyatakan boleh dipakai komersial | Bobot `BOLEH-PRODUK` |
| Bobot dilatih dengan kode GPL/AGPL, atau bahan latihnya non-komersial | Bobot `RISET-SAJA` |
| Izin bobot atau bahan latihnya tidak dinyatakan | Bobot `BELUM-JELAS` |

Kolom "Bukti" memuat jalur ke folder `docs/lisensi/<pemilik>__<repo>/` dan, untuk yang dipindai, ke laporan
`docs/audit/<nama>@<sha7>.md`.

Lalu di `tools/vendor.lock.json`, isi `lisensi_kode`, `lisensi_bobot`, dan `vonis` tiap entri dengan hasil tabel itu.
`vonis` entri diisi vonis yang **lebih ketat** di antara vonis kode dan vonis bobot.

Run: `node -e 'const k=JSON.parse(require("fs").readFileSync("tools/vendor.lock.json","utf8"));const v=["BOLEH-PRODUK","RISET-SAJA","DILARANG","BELUM-JELAS","AMAN-KOMERSIAL"];console.log(k.repo.every(r=>v.includes(r.vonis)), k.repo.filter(r=>r.lisensi_kode==="").map(r=>r.nama).join(",")||"semua terisi")'`
Expected: `true semua terisi`. (`AMAN-KOMERSIAL` hanya milik entri `yt-dlp` yang disalin dari vision-seed.)

- [ ] **Step 9: Bandingkan dengan vonis sementara dari survei, dan koreksi yang berbeda**

Buka `docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md` bagian A. Untuk tiap komponen di tabel vonis,
bandingkan vonis sementara di sana dengan vonis di `docs/VONIS-LISENSI.md`. Di akhir `docs/VONIS-LISENSI.md`,
tambahkan bagian:

```markdown
## Beda dengan vonis sementara dari survei 13 Okt

| Komponen | Vonis sementara (survei) | Vonis sekarang | Sebabnya |
|---|---|---|---|
```

Satu baris per komponen yang vonisnya berbeda. Bila tidak ada yang berbeda, tulis satu baris "tidak ada yang berbeda".
Catatan survei itu sendiri tidak diubah: ia tetap catatan sumber, dan vonis sahnya kini ada di sini.

- [ ] **Step 10: Commit**

```bash
git add tools/vendor.lock.json docs/lisensi docs/audit docs/VONIS-LISENSI.md
git status --short
git commit -q -F - <<'EOF'
Vonis izin komponen calon (B12)

Sepuluh komponen dikunci ke satu commit. Izin kodenya diarsipkan dari
berkas pada commit itu; izin bobot dan bahan latihnya dicatat terpisah
dengan kalimat persis dan sumbernya. Enam komponen yang akan dijalankan
di putaran ukur pertama diklon dan dipindai; temuan TINGGI dibaca manual.

Vonis di sini menggantikan vonis sementara dari survei 13 Okt. Yang tidak
dinyatakan sumbernya ditulis "tidak dinyatakan", dan vonisnya BELUM-JELAS:
tidak ada yang diisi dengan dugaan.

Belum ada yang dipasang atau dijalankan dari komponen ini.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

Expected: sebelum commit, `git status --short` tidak memuat `vendor/`.

---

### Task 3: Ringkasan peraturan plat dari teks aslinya

Catatan sejauh ini bersumber dari Wikipedia dan media otomotif, dan saling tidak cocok soal ukuran. Yang dibutuhkan
desain mesin (spec 2.1) dan pembuat plat buatan komputer (Rencana 3): warna dasar dan warna tulisan per jenis
kendaraan, isi dan susunan baris, dan ukuran bila ada.

**Files:**
- Create: `docs/peraturan-plat.md`

- [ ] **Step 1: Ambil teks Peraturan Kepolisian Nomor 7 Tahun 2021**

Buka `https://peraturan.go.id/files/bn476-2021.pdf` dengan alat baca web. Alat itu menyimpan salinan PDF-nya ke
folder sementara sesi dan mencetak jalurnya. Ini peraturan publik: bukan bobot, bukan dataset, dan tidak masuk repo.

Expected: jalur berkas PDF tercetak. Bila alamat itu gagal, pakai
`https://bapenda.jabarprov.go.id/JDIH/Peraturan_Polri/PERATURAN_POLRI_NOMOR_7_TAHUN_2021.pdf`. Bila keduanya gagal,
lewati ke Step 4 dan tulis ringkasan dari sumber sekunder saja, dengan kepala "TEKS PRIMER BELUM TERBACA".

- [ ] **Step 2: Temukan pasal tentang Tanda Nomor Kendaraan Bermotor**

> **Catatan eksekusi 13 Okt:** alat baca berkas tidak bisa membuka PDF di mesin ini (`pdftoppm` tidak terpasang), dan
> image lab tidak punya pustaka PDF. Tidak ada yang dipasang. Teksnya ditarik di lab tanpa jaringan dengan skrip sekali
> pakai yang hanya memakai pustaka bawaan Python (`data/unduhan/ekstrak_pdf.py`, tidak masuk git), lalu dicari dengan
> `grep`. Langkah di bawah ini dijalankan atas teks hasil tarikan itu.

Baca PDF itu dengan alat baca berkas, 20 halaman per permintaan, mulai dari halaman 1. Di tiap rentang halaman, cari
kata "Tanda Nomor Kendaraan Bermotor" dan "TNKB". Catat nomor halaman dan nomor pasal tiap kemunculan yang mengatur:

1. warna dasar dan warna tulisan, per jenis kendaraan;
2. apa saja yang dimuat TNKB (nomor registrasi, masa berlaku, dan lainnya);
3. ukuran, bahan, dan bentuk huruf, bila ada;
4. tanda khusus kendaraan listrik;
5. pasal yang menyerahkan rincian teknis ke keputusan lain (sebutkan keputusan apa).

Expected: daftar pasal dengan nomor halamannya. Bila sebuah hal tidak ditemukan di peraturan ini, catat "tidak diatur
di Perpol 7/2021" untuk hal itu.

- [ ] **Step 3: Coba baca keputusan yang ditunjuk untuk rincian teknis**

Bila Step 2 menemukan pasal yang menyerahkan spesifikasi teknis ke keputusan Kepala Korlantas, cari keputusan itu
dengan alat cari web (kata kunci: nama dan nomor keputusan persis seperti tertulis di pasalnya) dan baca teksnya.

Expected: teks keputusan terbaca, atau catatan "keputusan <nama> tidak ditemukan dalam bentuk yang bisa dibaca".
Jangan mengisi ukuran dari sumber sekunder seolah-olah dari keputusan itu.

- [ ] **Step 4: Tulis `docs/peraturan-plat.md`**

```markdown
# Peraturan plat nomor: yang tertulis di teks aslinya

> Dibuat 2026-10-13 dalam Rencana 2 Fase 0A. Sumber primer: Peraturan Kepolisian Nomor 7 Tahun 2021 tentang Registrasi
> dan Identifikasi Kendaraan Bermotor (<alamat yang dipakai>), dibaca langsung dari PDF-nya.
> Tiap butir memuat nomor pasal. Yang berasal dari sumber sekunder ditandai **[sekunder]** beserta sumbernya.
> Yang tidak ditemukan di teks ditulis "tidak diatur di sini", bukan diisi.

## Warna dasar dan warna tulisan

| Jenis kendaraan | Warna dasar | Warna tulisan | Pasal |
|---|---|---|---|

## Isi dan susunan

| Hal | Yang tertulis | Pasal |
|---|---|---|
| Yang dimuat TNKB | | |
| Susunan baris | | |
| Nomor registrasi motor: satu baris atau dua | | |

## Ukuran, bahan, dan bentuk huruf

| Hal | Yang tertulis | Sumber |
|---|---|---|
| Ukuran plat roda dua dan tiga | | |
| Ukuran plat roda empat atau lebih | | |
| Bentuk huruf | | |

## Tanda khusus

| Hal | Yang tertulis | Pasal |
|---|---|---|
| Kendaraan listrik | | |

## Yang diserahkan ke keputusan lain

| Hal | Diserahkan ke | Terbaca atau tidak |
|---|---|---|

## Akibat untuk rancangan

- Ragam warna yang harus dibaca mesin (spec 2.1 langkah 3): <daftar dari tabel pertama>.
- Parameter pembuat plat buatan komputer (Rencana 3) yang punya dasar peraturan: <daftar>. Yang tidak punya dasar
  peraturan dijadikan parameter yang dicocokkan dengan foto nyata: <daftar>.
```

Setiap sel diisi dari Step 2 dan Step 3. Sel yang tidak punya dasar di teks diisi "tidak diatur di sini" atau
"[sekunder] <isi> (<sumber>)". Tidak ada sel yang dibiarkan kosong.

- [ ] **Step 5: Periksa tidak ada sel kosong, lalu commit**

Run: `grep -n -E '\|\s+\|' docs/peraturan-plat.md; echo "EXIT=$?"`
Expected: tidak ada baris tercetak dan `EXIT=1` (tidak ditemukan sel yang hanya berisi spasi). Baris pemisah tabel
`|---|---|` tidak terjaring pola ini.

```bash
git add docs/peraturan-plat.md
git commit -q -F - <<'EOF'
Ringkasan peraturan plat dari teks aslinya

Catatan sebelumnya bersumber dari Wikipedia dan media otomotif dan saling
tidak cocok soal ukuran. Ringkasan ini dibaca langsung dari Perpol 7/2021,
dengan nomor pasal di tiap butir. Yang tidak diatur di sana ditulis "tidak
diatur di sini"; yang dari sumber sekunder ditandai.

Dipakai dua tempat: ragam warna yang harus dibaca mesin (spec 2.1) dan
parameter pembuat plat buatan komputer (Rencana 3).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Mencatat hasil

**Files:**
- Modify: `data-asal/bahan.json`
- Modify: `OPEN-QUESTIONS.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Catat bobot yang sudah bervonis di daftar bahan**

Untuk tiap komponen di `docs/VONIS-LISENSI.md` yang punya bobot bawaan (bukan `trackers` dan bukan `fast-alpr`, yang
tidak punya bobot sendiri), tambahkan satu entri di `data-asal/bahan.json`:

```json
{
  "id": "bobot-<nama>",
  "jenis": "bobot",
  "nama": "Bobot bawaan <nama> @ <sha7>",
  "sumber": "https://github.com/<repo>",
  "lisensi": "<isi kolom Izin bobot di tabel vonis>",
  "bukti_lisensi": "docs/lisensi/<pemilik>__<repo>/BOBOT.md",
  "vonis": "<vonis bobot dari tabel>",
  "dicatat": "2026-10-13",
  "catatan": "Belum diunduh. Vonis dari docs/VONIS-LISENSI.md."
}
```

Run: `node tools/bahan.mjs periksa; echo "EXIT=$?"`
Expected: `<N> bahan tercatat: ...` dan `EXIT=0`, dengan N = 1 + jumlah entri bobot yang ditambahkan.

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 73`, `ℹ fail 0`, `EXIT=0`

- [ ] **Step 2: Perbarui `OPEN-QUESTIONS.md`**

Di bagian B, tepat sesudah paragraf yang berawal `**Sesudah K17 (13 Okt):**`, tambahkan paragraf:

```markdown
**Sesudah Rencana 2 Fase 0A (13 Okt):**

- **B12:** vonis izin kini sah untuk komponen yang tercantum di [`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md),
  dibaca dari berkas pada commit yang dikunci. <satu kalimat: berapa komponen yang kode dan bobotnya BOLEH-PRODUK,
  berapa yang bobotnya RISET-SAJA atau BELUM-JELAS>. Empat komponen "izin saja" belum punya vonis bobot.
- **B2 dan warna plat:** [`docs/peraturan-plat.md`](docs/peraturan-plat.md) memuat yang tertulis di Perpol 7/2021.
  <satu kalimat: apa yang ternyata diatur di sana, dan apa yang diserahkan ke keputusan lain>.
```

Kedua bagian dalam kurung sudut diisi dengan angka dan temuan yang sebenarnya dari Task 2 dan Task 3.

- [ ] **Step 3: Perbarui `ROADMAP.md`**

(a) Di daftar "Status", ganti baris

```
- [ ] Rencana 2 Fase 0A dijalankan ← di sini sekarang (menunggu lampu hijau owner)
```

menjadi

```
- [x] Rencana 2 Fase 0A dijalankan: <N> komponen dikunci dan divonis ([`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md)); peraturan plat diringkas dari teks aslinya ([`docs/peraturan-plat.md`](docs/peraturan-plat.md)). Gerbang uji 66 → 73, semuanya hijau
- [ ] Rencana 3 Fase 0A ditulis (pintu unduh berkas, dataset berizin, pemilahan video, plat buatan komputer, set uji pertama) ← di sini sekarang
```

(b) Di akhir tabel "Changelog", tambahkan satu baris bertanggal `2026-10-13` yang memuat: apa yang berubah di
ROADMAP; **alasan** tiap vonis yang berbeda dari survei; angka gerbang uji sebelum dan sesudah; dan **batas**: empat
komponen "izin saja" belum punya vonis bobot, belum ada komponen yang dijalankan, dan hal peraturan yang tidak
terbaca dari sumber primer.

(c) Perbarui kalimat status di kepala berkas menjadi
`· RENCANA 2 FASE 0A (IZIN DAN PERATURAN) SELESAI — BERIKUTNYA: MENULIS RENCANA 3 FASE 0A.**`

- [ ] **Step 4: Commit**

```bash
git add data-asal/bahan.json OPEN-QUESTIONS.md ROADMAP.md
git commit -q -F - <<'EOF'
Catat hasil Rencana 2 Fase 0A (izin dan peraturan)

B12 diperbarui dari "vonis sementara" menjadi vonis yang dibaca dari berkas
pada commit terkunci. Bobot yang sudah bervonis masuk daftar bahan, supaya
pemeriksa mesin jualan mengenalnya sejak sebelum diunduh.

Batas ditulis di ROADMAP: empat komponen baru dibaca izin kodenya, belum
ada komponen yang dijalankan, dan hal peraturan yang tidak terbaca dari
sumber primer disebut satu per satu.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
git status --short
```

Expected: `git status --short` tidak mencetak apa pun.

---

## Selesai bila

- [ ] `npm test` mencetak `ℹ tests 73`, `ℹ fail 0`, `EXIT=0`.
- [ ] Tiap komponen di `tools/vendor.lock.json` punya SHA 40 karakter, dan enam yang diklon lolos
      `tools\klon-terkunci.ps1` (HEAD sama dengan kunci).
- [ ] Tiap vonis di `docs/VONIS-LISENSI.md` menunjuk berkas bukti yang ada di `docs/lisensi/`.
- [ ] Tiap laporan di `docs/audit/` punya bagian "Dibaca manual".
- [ ] `docs/peraturan-plat.md` tidak punya sel kosong, dan tiap butir primer memuat nomor pasal.
- [ ] `git -C "D:/Projects/super-team-v1/vision-seed" status --short` kosong.
- [ ] Tidak ada yang dipasang dan tidak ada komponen yang dijalankan.

## Yang sengaja tidak dikerjakan di rencana ini

- Mengunduh bobot atau dataset: Rencana 3 (dataset) dan Rencana 4 (bobot), lewat pintu unduh berkas.
- Menjalankan komponen mana pun: Rencana 4, lewat `tools\lab.ps1`.
- Memutuskan komponen mana yang dipakai produk: itu hasil ukur Rencana 4 (spec 2.3), bukan hasil membaca izin.
  Rencana ini hanya menyaring mana yang **boleh** dipertimbangkan.
- Vonis izin dataset plat dan huruf plat: Rencana 3, saat bahannya diambil.
