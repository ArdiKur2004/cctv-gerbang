# Fase 0A, Rencana 9: Persiapan melatih ulang fast-plate-ocr (K26) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Semua yang dibutuhkan untuk melatih ulang fast-plate-ocr dengan plat Indonesia (K26) ada dan terbukti, tanpa
menyentuh data plat: bobot `.keras` terbitan dikunci; 16 paket tambahan dikunci dengan SHA-256 dan diperiksa celahnya;
image lab tambahan dibangun di atas image lab yang ada; pintu lab bisa memilihnya; dan percobaan pertama dengan plat buatan
membuktikan bahwa (1) Keras berjalan di atas torch, (2) bobot `.keras` memberi keluaran yang sama dengan ONNX terbitan, dan
(3) perintah latih fast-plate-ocr bisa melatih ulang satu zaman. Ditambah draf permintaan izin tertulis kepada pembuat
fast-plate-ocr untuk disetujui owner. Latihan penuh dengan INDO-ALPR dan penilaiannya ada di Rencana 10.

**Architecture:** Image `cctvgerbang-lab-fpo:v1` dibangun dari `tools/lab-fpo/Dockerfile` di atas `vision-seed-lab:v1`
(ID-nya diperiksa terhadap kunci), memasang hanya wheel yang SHA-256-nya ada di `tools/lab-fpo/requirements.txt`
(`--require-hashes --no-deps --no-build`). Jaringan hanya dipakai saat membangun. Saat jalan, image itu dipakai lewat
`tools\lab.ps1 -Fpo` dengan janji yang sama: tanpa jaringan, repo read-only, ID image diperiksa terhadap kunci
(`image_lab_fpo`). Keras memakai torch yang sudah ada sebagai mesinnya (`KERAS_BACKEND=torch`); TensorFlow tidak dipasang.

**Tech Stack:** PowerShell (pembangun dan pintu), Node test (uji pintu), Python di lab. Paket baru: keras 3.15.1,
albumentations 2.0.8, albucore 0.0.24, pandas 2.3.3, h5py 3.15.1, onnx 1.23.2, onnxslim 0.1.98, dan turunan kecilnya.

**Dasar:** K25 dan K26 (`SEED.md` §3); `CLAUDE.md` §6 (rantai pasok); `docs/VONIS-LISENSI.md` (fast-plate-ocr: kode MIT,
bobot `BELUM-JELAS`); laporan Rencana 8.

---

## Yang diukur sebelum rencana ini ditulis (15 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Cara melatih ulang | `fast-plate-ocr train ... --weights-path <model.keras>`; data berbentuk CSV `image_path,plate_text[,plate_region]` (jalur gambar relatif terhadap CSV); keluaran model terbaik dan akhir | `docs/training/cli/train.md`, `docs/training/dataset.md`, `cli/train.py` |
| Mesin Keras | Keras 3 mendukung TensorFlow, JAX, dan PyTorch (`KERAS_BACKEND`). torch 2.14.1 sudah ada di image lab, jadi **TensorFlow tidak perlu** | `docs/training/backend.md` |
| Ekspor ONNX | Bawaan Keras (`model.export(format="onnx")`) ditambah onnx dan onnxslim; tanpa TensorFlow | `cli/export.py` |
| Bobot untuk dilatih ulang | `cct_s_v2_global.keras` 17.657.419 byte, `cct_s_v2_global_model_config.yaml` 1.171 byte, `cct_s_v2_global_val_results.json` 24.242 byte; semuanya ber-SHA-256 terbitan GitHub, diunggah 2026-03-14 | API rilis `arg-plates` |
| Pustaka latih yang dimuat | keras, albumentations, pandas, pydantic, click, rich, yaml, cv2, numpy | Impor di `cli/train.py`, `train/**` |
| Yang sudah ada di image lab | click 8.5.0, pydantic 2.13.5, scipy 1.18.1, pyyaml 6.0.3, rich 15.0.0, opencv-python-headless 4.14.0.94, numpy 2.5.3, onnxruntime-gpu 1.30.0 (86 paket) | `data/alat-sementara/daftar_paket_lab.py` |
| Penyelesaian paket | `uv pip compile` (hanya wheel, Linux x86_64, Python 3.12, dibatasi daftar image lab): **16 paket baru**, 19 paket lama dipakai dengan versi yang sama, **0 berubah versi** | `uv` 0.11.18 di laptop, hanya membaca katalog PyPI |
| Celah keamanan (OSV) | keras 3.12.1 (versi di kunci fast-plate-ocr) punya **19 celah tercatat**, antara lain lewat pemuatan berkas model; 3.14.1 masih 14; **3.15.0 dan 3.15.1: 0**. Dengan keras 3.15.1, ke-16 paket baru: **0 celah tercatat** | `api.osv.dev` |

Akibatnya bagi rencana ini:

1. **keras 3.15.1, bukan 3.12.1.** Kita akan memuat berkas `.keras` dari pihak ketiga, dan sebagian celah 3.12.1 justru lewat
   pemuatan model. Apakah kode fast-plate-ocr @ `9ce7a5b` cocok dengan 3.15.1 dibuktikan di Task 5. Bila tidak cocok,
   **berhenti dan laporkan**; jangan turun ke versi bercelah tanpa keputusan owner.
2. Image tambahan, bukan mengubah image vision-seed (dibaca, tidak diubah).
3. Percobaan pertama memakai plat buatan saja; data plat baru dipakai di Rencana 10.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–8 | Bengkel sampai mesin baca huruf pertama | Selesai 13–14 Okt |
| **9 (dokumen ini)** | Bobot `.keras`, paket terkunci, image lab tambahan, pintu `-Fpo`, percobaan pertama, draf izin | Ditulis dan dijalankan 15 Okt |
| 10 | Melatih ulang fast-plate-ocr dengan bahan latih INDO-ALPR; penilaian adil pada set uji; laporan | Ditulis saat Rencana 9 selesai |
| 11 | Mencari plat di foto utuh dan video; plat buatan komputer; kecepatan di server (K25); laporan Fase 0A | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8. Tambahan:
- **Jaringan hanya saat membangun image** (Task 3), dan hanya untuk wheel ber-SHA-256 terkunci. Saat jalan, image tambahan
  selalu tanpa jaringan.
- **vision-seed dan image `vision-seed-lab:v1` hanya dibaca**; image tambahan dibangun di atasnya, tidak menggantinya.
- **Pesan ke pembuat fast-plate-ocr tidak dikirim** di rencana ini. Draf disetujui owner lebih dulu, kata per kata.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/vendor.lock.json` (ubah) | Tiga butir `berkas` (bobot `.keras`, konfigurasi model, hasil validasi pembuat); `image_lab_fpo` | 1, 3 |
| `tools/lab/uji/test_model_terkunci.py` (ubah) | Uji rantai: kunci memuat butir `.keras` | 1 |
| `tools/lab-fpo/requirements.txt` (baru) | 16 paket dengan SHA-256 | 2 |
| `tools/lab-fpo/Dockerfile`, `tools/image-lab-fpo.ps1`, `tools/uji/image-lab-fpo.test.mjs` (baru) | Pembangun image tambahan | 3 |
| `tools/lab.ps1`, `tools/uji/lab.test.mjs` (ubah) | Pilihan `-Fpo` | 4 |
| `tools/lab/uji_fpo/test_percobaan_fpo.py` (baru) | Percobaan pertama, di luar gerbang | 5 |
| `docs/izin/2026-10-15-draf-izin-fast-plate-ocr.md` (baru) | Draf pesan untuk disetujui owner | 6 |

---

### Task 1: Bobot `.keras`, konfigurasi model, dan hasil validasi pembuat

**Files:** Modify `tools/lab/uji/test_model_terkunci.py`, `tools/vendor.lock.json`

- [x] **Step 1: Tulis uji rantainya**

Tambahkan di akhir `tools/lab/uji/test_model_terkunci.py`:

```python
def test_kunci_repo_mencatat_bobot_keras_fast_plate_ocr():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa butir ini fast-plate-ocr tidak bisa dilatih ulang (K26).
    daftar = mt.daftar_berkas()

    for butir, nama in (("fpo-cct-s-v2-keras", "cct_s_v2_global.keras"),
                        ("fpo-cct-s-v2-model-config", "cct_s_v2_global_model_config.yaml"),
                        ("fpo-cct-s-v2-val", "cct_s_v2_global_val_results.json")):
        assert daftar[butir][0] == nama and len(daftar[butir][1]) == 64
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `1 failed, 151 passed`, `KeyError: 'fpo-cct-s-v2-keras'`, `EXIT=1`.

- [x] **Step 3: Kunci ketiga berkas ke digest GitHub (dibaca dengan skrip, tidak diketik)**

Salin `data/alat-sementara/kunci-fpo.mjs` menjadi `data/alat-sementara/kunci-fpo-keras.mjs`, lalu ganti daftar `BUTIR`
menjadi:

```js
const BUTIR = [['fpo-cct-s-v2-keras', 'cct_s_v2_global.keras', 0.1],
               ['fpo-cct-s-v2-model-config', 'cct_s_v2_global_model_config.yaml', 0.01],
               ['fpo-cct-s-v2-val', 'cct_s_v2_global_val_results.json', 0.01]];
```

dan hapus bagian yang mengganti keterangan `_berkas` (sudah diganti di Rencana 6).

Run: `node data/alat-sementara/kunci-fpo-keras.mjs; echo "EXIT=$?"`
Expected: tiga baris `cct_s_v2_global.keras, 17657419 byte, sha256 dc6db494714d`, `..._model_config.yaml, 1171 byte,
sha256 244c3c712205`, `..._val_results.json, 24242 byte, sha256 cc9ea0f5bfd7`; `EXIT=0`. Bila angkanya lain, **berhenti**.

- [x] **Step 4: Unduh lewat pintu**

Run (PowerShell, satu per satu): `powershell -NoProfile -File tools\ambil-berkas.ps1 <nama>; "EXIT=$LASTEXITCODE"` untuk
`fpo-cct-s-v2-keras`, `fpo-cct-s-v2-model-config`, `fpo-cct-s-v2-val`.
Expected: tiap baris `TERSIMPAN ...` dengan SHA-256 sama dengan kunci, dari `release-assets.githubusercontent.com`; `EXIT=0`.

- [x] **Step 5: Gerbang, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"`
Expected: `pass 101` dan `152 passed`.

Commit `tools/vendor.lock.json` dan uji, dengan alasan (K26), angka unduhan, dan catatan bahwa berkas `.keras` dimuat Keras
dengan `safe_mode` bawaan.

---

### Task 2: Daftar paket terkunci dan pemeriksaan celah

**Files:** Create `tools/lab-fpo/requirements.txt`

- [x] **Step 1: Selesaikan paket dengan SHA-256**

Run (Git Bash; berkas sementara di folder kerja sementara `$D`):

```bash
sed 's/+cu130//' data/keluaran/paket-lab-dasar.txt | grep -v "^nvidia-\|^triton==" > "$D/batasan-lab.txt"
printf "keras==3.15.1\nalbumentations==2.0.8\npandas==2.3.3\nh5py==3.15.1\nonnx\nonnxslim\n" > "$D/masukan-fpo.txt"
"$HOME/.local/bin/uv.exe" pip compile "$D/masukan-fpo.txt" -c "$D/batasan-lab.txt" --python-version 3.12 \
  --python-platform x86_64-manylinux_2_28 --only-binary :all: --generate-hashes --no-header --no-annotate -o "$D/hasil-fpo.txt"; echo "EXIT=$?"
```

Expected: `EXIT=0`.

- [x] **Step 2: Ambil hanya paket baru, beserta hash-nya**

Tulis berkas sekali pakai `data/alat-sementara/pilih-paket-baru.mjs` yang membaca `$D/hasil-fpo.txt` (blok per paket:
baris `nama==versi \` lalu baris-baris `--hash=sha256:...`), membuang blok yang nama dan versinya sama dengan baris di
`data/keluaran/paket-lab-dasar.txt` (nama dinormalkan: huruf kecil, `_` menjadi `-`; akhiran `+cu130` dibuang), **berhenti
dengan kode 1 bila ada paket lama yang versinya berbeda**, lalu menulis `tools/lab-fpo/requirements.txt` dengan kepala
komentar (asal, tanggal, perintah `uv`, "jangan diubah dengan tangan").

Run: `node data/alat-sementara/pilih-paket-baru.mjs "$D/hasil-fpo.txt"; echo "EXIT=$?"`
Expected: `16 paket baru, 19 paket lama dengan versi sama, 0 berubah`, `EXIT=0`. Tiap paket di `requirements.txt` punya
paling sedikit satu `--hash=sha256:`.

- [x] **Step 3: Periksa celah (OSV)**

Run: `node <folder kerja sementara>/audit-osv.mjs <daftar nama==versi dari requirements.txt>; echo "EXIT=$?"`
Expected: 16 baris `tidak ada celah tercatat`, `jumlah celah atau gagal periksa: 0`, `EXIT=0`. Bila ada celah, **berhenti**
dan laporkan (paket, ID celah, versi yang menutupnya).

- [x] **Step 4: Commit** `tools/lab-fpo/requirements.txt`, dengan alasan, angka penyelesaian, dan hasil OSV.

---

### Task 3: Pembangun image lab tambahan

**Files:** Create `tools/lab-fpo/Dockerfile`, `tools/image-lab-fpo.ps1`, `tools/uji/image-lab-fpo.test.mjs`;
Modify `tools/vendor.lock.json`

- [x] **Step 1: Tulis ujinya**

Buat `tools/uji/image-lab-fpo.test.mjs`:

```js
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
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm test; echo "EXIT=$?"`
Expected: `fail 3` (skrip belum ada), `EXIT=1`.

- [x] **Step 3: Tulis Dockerfile dan pembangunnya**

Buat `tools/lab-fpo/Dockerfile`:

```dockerfile
# Image lab tambahan untuk melatih ulang fast-plate-ocr (K26). Dibangun HANYA lewat tools\image-lab-fpo.ps1, di atas image
# lab vision-seed yang ID-nya dikunci (tools/vendor.lock.json, image_lab). Jaringan dipakai hanya saat membangun, untuk
# mengunduh wheel yang SHA-256-nya terkunci di requirements.txt (--require-hashes --no-deps --no-build). Saat jalan selalu
# lewat tools\lab.ps1 -Fpo: tanpa jaringan, repo read-only. Keras memakai torch yang sudah ada; TensorFlow tidak dipasang.
FROM vision-seed-lab:v1
USER root
COPY requirements.txt /bangun-fpo/requirements.txt
RUN uv pip install --python /opt/venv/bin/python --require-hashes --no-deps --no-build -r /bangun-fpo/requirements.txt \
    && rm -rf /root/.cache/uv /bangun-fpo
ENV KERAS_BACKEND=torch
USER lab
ARG KUNCI_LAB_FPO=tak-diketahui
LABEL id.megatron.cctvgerbang.kunci-fpo=$KUNCI_LAB_FPO
```

Buat `tools/image-lab-fpo.ps1`:

```powershell
<#
.SYNOPSIS
  Membangun image lab tambahan cctvgerbang-lab-fpo:v1 (K26) dari tools\lab-fpo, di atas image lab vision-seed.

.DESCRIPTION
  - Image dasar vision-seed-lab:v1 harus ber-ID persis yang tercatat di tools\vendor.lock.json (image_lab); bila tidak,
    tidak dibangun (kode 6).
  - Daftar paket (requirements.txt) harus ber-SHA-256; bila tidak, ditolak (kode 2). Dockerfile memasangnya dengan
    --require-hashes --no-deps --no-build.
  - Image diberi label sidik SHA-256 (Dockerfile + requirements.txt). Sesudah dibangun, ID image dicatat di kunci
    (image_lab_fpo) supaya tools\lab.ps1 -Fpo hanya menjalankan image itu.
  - Jaringan dipakai docker build untuk mengunduh wheel. Saat jalan, image selalu tanpa jaringan (lab.ps1).

  Bendera: -Kering   cetak argumen docker sebagai JSON tanpa membangun (dipakai tools\uji\image-lab-fpo.test.mjs)

.EXAMPLE
  powershell -NoProfile -File tools\image-lab-fpo.ps1
#>
$ErrorActionPreference = 'Stop'
$folder = if ($env:VS_LAB_FPO_FOLDER) { $env:VS_LAB_FPO_FOLDER } else { Join-Path $PSScriptRoot 'lab-fpo' }
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$kering = ($args.Count -gt 0 -and $args[0] -eq '-Kering')
$image = 'cctvgerbang-lab-fpo:v1'

$idDasar = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).image_lab.id
$ErrorActionPreference = 'Continue'
$idAda = & $docker image inspect vision-seed-lab:v1 --format '{{.Id}}' 2>$null
$ErrorActionPreference = 'Stop'
if (-not $idDasar -or "$idAda".Trim() -ne $idDasar) {
    Write-Host "IMAGE DASAR TAK SESUAI KUNCI: vision-seed-lab:v1 ber-ID '$idAda', yang tercatat '$idDasar'."
    exit 6
}
$dockerfile = Join-Path $folder 'Dockerfile'
$req = Join-Path $folder 'requirements.txt'
$baris = @(Get-Content $req | Where-Object { $_ -match '^[A-Za-z0-9]' })
$berhash = @(Get-Content $req | Where-Object { $_ -match '--hash=sha256:[0-9a-f]{64}' })
if ($baris.Count -eq 0 -or $berhash.Count -lt $baris.Count) {
    Write-Host "DITOLAK: tiap paket di requirements.txt harus punya --hash=sha256 ($($baris.Count) paket, $($berhash.Count) hash)."
    exit 2
}
$sha = [Security.Cryptography.SHA256]::Create()
$isi = [byte[]]([IO.File]::ReadAllBytes($dockerfile) + [IO.File]::ReadAllBytes($req))
$sidik = -join ($sha.ComputeHash($isi) | ForEach-Object { $_.ToString('x2') })
$argumen = @('build', '--build-arg', "KUNCI_LAB_FPO=$sidik", '-t', $image, $folder)
if ($kering) { ConvertTo-Json -InputObject $argumen -Compress; exit 0 }

& $docker @argumen
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$id = & $docker image inspect $image --format '{{.Id}}'
Write-Host "TERBANGUN $image ID $id SIDIK $sidik"
exit 0
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 104`, `EXIT=0`.

- [x] **Step 5: Bangun (jaringan, satu kali)**

Run (PowerShell): `powershell -NoProfile -File tools\image-lab-fpo.ps1; "EXIT=$LASTEXITCODE"`
Expected: keluaran docker build, lalu `TERBANGUN cctvgerbang-lab-fpo:v1 ID sha256:... SIDIK ...`, `EXIT=0`. Lamanya dicatat.

- [x] **Step 6: Catat ID image di kunci (dibaca dengan skrip)**

Berkas sekali pakai `data/alat-sementara/kunci-image-fpo.mjs`: membaca ID dan label sidik dengan
`docker image inspect cctvgerbang-lab-fpo:v1`, menghitung SHA-256 `tools/lab-fpo/requirements.txt`, lalu menyisipkan sesudah
baris `"image_lab": {...},` di kunci:

```json
  "_image_lab_fpo": "Image lab tambahan untuk melatih ulang fast-plate-ocr (K26), dibangun tools/image-lab-fpo.ps1 di atas image_lab. Dijalankan hanya lewat tools/lab.ps1 -Fpo.",
  "image_lab_fpo": { "nama": "cctvgerbang-lab-fpo:v1", "id": "<ID>", "dasar": "<image_lab.id>", "sidik": "<label>", "requirements_sha256": "<sha>", "dibangun": "<tanggal>" },
```

Jangkar harus ketemu tepat sekali. Run: `node data/alat-sementara/kunci-image-fpo.mjs; echo "EXIT=$?"` lalu
`npm test; echo "EXIT=$?"` (Expected `pass 104`).

- [x] **Step 7: Commit** Dockerfile, pembangun, uji, dan kunci, dengan alasan (K26, rantai pasok), lama membangun, dan ID.

---

### Task 4: Pintu lab dengan pilihan `-Fpo`

**Files:** Modify `tools/lab.ps1`, `tools/uji/lab.test.mjs`

- [x] **Step 1: Tulis ujinya**

Tambahkan di akhir `tools/uji/lab.test.mjs`:

```js
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
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm test; echo "EXIT=$?"`
Expected: `fail 2`, `EXIT=1`.

- [x] **Step 3: Tambahkan pilihan `-Fpo` di `tools/lab.ps1`**

- Docstring: tambahkan di bagian bendera `-Fpo   jalankan image lab tambahan cctvgerbang-lab-fpo:v1 (K26; ID dari kunci
  image_lab_fpo). Janji pintu sama.`
- Sesudah baris yang membaca `-Kering`, tambahkan:

```powershell
$kunciImage = 'image_lab'
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Fpo') {
    $image = 'cctvgerbang-lab-fpo:v1'
    $kunciImage = 'image_lab_fpo'
    $sisa = @($sisa | Select-Object -Skip 1)
}
```

- Baris pembaca ID kunci menjadi:
  `$idKunci = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).$kunciImage.id`
- Pesan galat `IMAGE TAK SESUAI KUNCI` menyebut `$kunciImage`, bukan tulisan tetap `image_lab`.

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 106`, `EXIT=0`.

Run (PowerShell): `powershell -NoProfile -File tools\lab.ps1 -Fpo python -c "import keras, sys; print(keras.__version__, keras.backend.backend(), sys.version.split()[0])"; "EXIT=$LASTEXITCODE"`
Expected: `3.15.1 torch 3.12.15`, `EXIT=0`.

Run: `npm run test:lab; echo "EXIT=$?"` (Expected `152 passed`: gerbang lab biasa tidak berubah).

- [x] **Step 5: Commit** `tools/lab.ps1` dan ujinya.

---

### Task 5: Percobaan pertama di image tambahan (plat buatan, tanpa data plat)

**Files:** Create `tools/lab/uji_fpo/test_percobaan_fpo.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Percobaan pertama jalur latih ulang fast-plate-ocr di image lab tambahan (K26), tanpa jaringan dan tanpa data plat (hanya
plat buatan tulisan komputer). Di luar gerbang biasa: butuh image cctvgerbang-lab-fpo:v1 dan berkas model di data/unduhan.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
VENDOR = AKAR / "vendor" / "fast-plate-ocr"
UNDUHAN = AKAR / "data" / "unduhan"
sys.path.insert(0, str(VENDOR))
sys.path.insert(0, str(AKAR / "tools" / "lab"))
from model_terkunci import daftar_berkas, verifikasi_berkas  # noqa: E402

TEKS = ["B1234XY", "D5678AB", "AB12CD", "F9012Z", "H3456KL", "L7890MN", "N2468PQ", "R1357ST"]
BUTIR = {"keras": ("fpo-cct-s-v2-keras", "cct_s_v2_global.keras"), "onnx": ("fpo-cct-s-v2-onnx", "cct_s_v2_global.onnx"),
         "plat": ("fpo-cct-s-v2-config", "cct_s_v2_global_plate_config.yaml"),
         "model": ("fpo-cct-s-v2-model-config", "cct_s_v2_global_model_config.yaml")}
ADA = all((UNDUHAN / b / n).is_file() for b, n in BUTIR.values())


def jalur(kunci):
    butir, nama = BUTIR[kunci]
    return verifikasi_berkas(UNDUHAN / butir / nama, butir, daftar_berkas())


def plat_buatan(teks):
    kanvas = np.full((110, 360, 3), 255, np.uint8)
    cv2.putText(kanvas, teks, (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 0, 0), 3)
    return kanvas


def test_keras_berjalan_di_atas_torch():
    import keras

    assert keras.backend.backend() == "torch" and keras.__version__ == "3.15.1"


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_bobot_keras_sama_dengan_onnx_terbitan():
    # Bobotnya sama: model .keras yang dijalankan Keras di atas torch harus memberi keluaran yang sama dengan ONNX terbitan.
    import onnxruntime as ort
    from fast_plate_ocr.core.process import resize_image
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur("plat"))
    model = load_keras_model(jalur("keras"), cfg)
    x = np.stack([resize_image(cv2.cvtColor(plat_buatan(t), cv2.COLOR_BGR2RGB), cfg.img_height, cfg.img_width,
                               image_color_mode=cfg.image_color_mode, keep_aspect_ratio=cfg.keep_aspect_ratio,
                               interpolation_method=cfg.interpolation, padding_color=cfg.padding_color) for t in TEKS])
    keluar = model.predict(x.astype(np.float32), verbose=0)
    k = keluar["plate"] if isinstance(keluar, dict) else (keluar[0] if isinstance(keluar, (list, tuple)) else keluar)
    sesi = ort.InferenceSession(str(jalur("onnx")), providers=["CPUExecutionProvider"])
    nama = [o.name for o in sesi.get_outputs()]
    o = sesi.run(["plate" if "plate" in nama else nama[0]], {"input": x.astype(np.uint8)})[0]
    k, o = np.asarray(k).reshape(len(TEKS), -1), np.asarray(o).reshape(len(TEKS), -1)
    print(f"\nselisih terbesar keras vs onnx: {np.abs(k - o).max():.2e}")
    assert np.allclose(k, o, atol=1e-3)


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_latih_ulang_satu_zaman_pada_plat_buatan(tmp_path):
    # Rantainya: perintah latih fast-plate-ocr (Keras di atas torch, tanpa jaringan) memuat bobot terbitan, melatih, menyimpan.
    for sisi in ("latih", "val"):
        folder = tmp_path / sisi
        folder.mkdir()
        with open(folder / "anotasi.csv", "w", newline="") as berkas:
            tulis = csv.writer(berkas)
            tulis.writerow(["image_path", "plate_text", "plate_region"])
            for i, t in enumerate(TEKS * 2):
                cv2.imwrite(str(folder / f"{i}.png"), plat_buatan(t))
                tulis.writerow([f"{i}.png", t, "Indonesia"])

    hasil = subprocess.run(
        [sys.executable, "-c", "from fast_plate_ocr.cli.cli import main_cli; main_cli()", "train",
         "--model-config-file", str(jalur("model")), "--plate-config-file", str(jalur("plat")),
         "--annotations", str(tmp_path / "latih/anotasi.csv"), "--val-annotations", str(tmp_path / "val/anotasi.csv"),
         "--weights-path", str(jalur("keras")), "--epochs", "1", "--batch-size", "8", "--seed", "0",
         "--output-dir", str(tmp_path / "keluar")],
        capture_output=True, text=True, cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(VENDOR)})

    assert hasil.returncode == 0, hasil.stdout[-3000:] + hasil.stderr[-3000:]
    assert list((tmp_path / "keluar").rglob("*.keras"))
```

- [x] **Step 2: Jalankan di image tambahan**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used --format=csv,noheader` lalu
`powershell -NoProfile -File tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `3 passed`, satu baris `selisih terbesar keras vs onnx: ...`, `EXIT=0`.

Bila uji kedua atau ketiga gagal karena kode fast-plate-ocr @ `9ce7a5b` tidak cocok dengan keras 3.15.1, **berhenti dan
laporkan** pesan galatnya (plat buatan, tanpa data pribadi). Pilihan sesudahnya (memakai versi keras lain yang bercelah,
menambal kode, atau jalur lain) adalah keputusan owner.

- [x] **Step 3: Commit** uji percobaan, dengan hasilnya.

---

### Task 6: Draf izin, catatan, dan permintaan ke owner

- [x] **Step 1: Tulis draf pesan izin**

`docs/izin/2026-10-15-draf-izin-fast-plate-ocr.md`: pesan berbahasa Inggris kepada pemelihara fast-plate-ocr
(`ankandrew`), ditambah terjemahan Indonesia untuk owner. Isinya: siapa kami (tanpa data pribadi selain yang owner setujui),
bahwa kami ingin melatih ulang `cct_s_v2_global` dengan plat Indonesia dan memakai hasilnya di layanan berbayar yang
berjalan di server kami (K25), apakah bobot terbitan boleh dipakai begitu dan dengan syarat apa (misalnya menyebut sumber),
dan rujukan ke pernyataan pemelihara di diskusi GitHub yang dicatat survei 13 Okt (alamatnya dibaca dari
`docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md`, bila ada). **Tidak dikirim.**

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali): `data-asal/bahan.json` (butir bobot
fast-plate-ocr: berkas `.keras` diunduh dan dikunci); `CLAUDE.md` §7 (image tambahan dan `lab.ps1 -Fpo`; paket baru hanya
lewat `tools/lab-fpo/requirements.txt` ber-SHA-256 dan pemeriksaan OSV); `ROADMAP.md` (butir dicentang dengan angka; butir
baru `- [ ] Owner menyetujui draf izin fast-plate-ocr ← di sini sekarang` dan `- [ ] Rencana 10 Fase 0A ditulis`; baris
status; changelog); rencana ini (kotak dicentang, catatan pelaksanaan).

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 106` dan `152 passed`.

- [x] **Step 4: BERHENTI. Minta owner memeriksa draf pesan**

Tunjukkan isi terjemahannya secara ringkas, lalu **satu** pertanyaan: setuju isi pesannya (dan siapa yang mengirim), atau
ada yang diubah. Rencana 10 (latihan penuh) boleh berjalan sebelum izin datang karena hasilnya bertanda riset (K15, K21).

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K26:** bobot awal (Task 1), pustaka baru lewat pemeriksaan keamanan (Task 2–4), bukti bahwa jalurnya bekerja
  (Task 5), izin tertulis (Task 6). Latihan penuh sengaja di Rencana 10.
- **Rantai pasok:** image dasar diperiksa ID-nya; wheel dikunci SHA-256 dan dipasang tanpa dependensi tambahan dan tanpa
  membangun dari sumber; celah diperiksa ke OSV, dan versi keras dipilih yang tanpa celah tercatat; image dijalankan tanpa
  jaringan; berkas `.keras` dimuat dengan `safe_mode` bawaan Keras dan sudah diperiksa SHA-256-nya.
- **Data pribadi:** tidak ada data plat yang disentuh rencana ini; percobaan memakai plat buatan.
- **Tanpa isian kosong pada kode:** kode uji, Dockerfile, dan pembangun tertulis lengkap. Dua skrip sekali pakai (Task 2
  Step 2, Task 3 Step 6) dijelaskan perilakunya dan diperiksa keluarannya.
- **Angka gerbang:** Node 101 → 104 → 106. Lab 151 → 152. Uji percobaan (3) di luar gerbang.

## Catatan pelaksanaan (15 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Commit: `bfb9973` (Task 1), `97c4200` (Task 2), `56bf1d5` (Task 3), `5733f8f`
(Task 4), `3c7749b` (Task 5), dan commit catatan (Task 6).

| Task | Hasil | Menyimpang dari rencana |
|---|---|---|
| 1 | Tiga berkas diunduh lewat pintu, SHA-256 sama dengan terbitan GitHub. Lab 151 → 152 | Tanggal `dibaca` ketiganya tertulis 14 Okt karena skrip memakai jam UTC; dikoreksi di Task 3 |
| 2 | 16 paket baru, 484 hash, 0 paket lama berubah versi; OSV 0 celah | Audit pertama melaporkan 50 celah karena nama paket masih berakhiran garis miring terbalik; diulang dengan `nama==versi` bersih (keras tanpa versi 40, versi rusak 27, versi bersih 0) |
| 3 | Image dibangun 20 detik; ID `sha256:a498d0967316…` dikunci (`image_lab_fpo`). Node 101 → 104 | — |
| 4 | `lab.ps1 -Fpo`: `3.15.1 torch 3.12.15`; tanpa jaringan dibuktikan langsung (hanya `lo`). Node 104 → 107; lab tetap 152 | Satu uji rantai tambahan (ID dicocokkan ke `image_lab_fpo`, bukan `image_lab`), jadi Node 107, bukan 106 |
| 5 | 5 lulus dalam 21 detik; merah dulu di image lab biasa (3 gagal, tanpa keras) | Uji kedua mematikan TF32 (dengan TF32 selisih 3,98e-3, tanpa 1,13e-6, CPU 6,62e-6; huruf sama) dan juga memeriksa huruf terpilih. Uji ketiga memanggil `matikan_kernel_triton()` sebelum perintah latih ("Failed to find C compiler"). Dua uji tambahan: perintah latih memuat 192/192 tensor terbitan, dengan kontrol negatif `layers: 4` (dimuat tanpa galat, 138 dari 174 tensor sama) |
| 6 | Draf izin ditulis; kutipan pemelihara dibaca ulang dari GitHub; #98 masih tanpa jawaban | — |

**Syarat untuk Rencana 10 (dari Task 5):**
- Pelatih memanggil `matikan_kernel_triton()` sebelum memuat Keras.
- Bobot termuat utuh (192/192) diperiksa sebelum melatih, karena `skip_mismatch=True` melewati lapisan tak cocok tanpa galat.
- CSV memuat kolom `plate_region`: tanpa kolom itu kepala wilayah dibuang tanpa galat (170 tensor).
- Perbandingan keluaran yang halus (misalnya dengan ONNX hasil ekspor) dilakukan tanpa TF32.
