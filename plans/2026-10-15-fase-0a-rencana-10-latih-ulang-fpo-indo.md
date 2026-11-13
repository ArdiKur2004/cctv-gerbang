# Fase 0A, Rencana 10: Melatih ulang fast-plate-ocr dengan plat Indonesia (K26) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Mesin baca huruf `fpo-indo-1`: `cct_s_v2_global` milik fast-plate-ocr yang dilatih ulang dengan bahan latih
INDO-ALPR (2.824 plat, label dibersihkan K24), dipilih dengan validasi dari bahan latih, lalu dinilai **sekali** pada set
uji yang sama dengan Rencana 8 dan dibandingkan secara adil dengan Qwen3-VL, fast-plate-ocr terbitan, dan mesin-baca-1.

**Architecture:** Satu alat baru `tools/lab/latih_fpo.py` dengan tiga perintah (`siapkan`, `latih`, `baca`), dijalankan
di image lab tambahan lewat `tools\lab.ps1 -Fpo` (tanpa jaringan). `siapkan` menulis CSV dari sisi latih saja dengan
pembagian validasi Rencana 8. `latih` memastikan bobot terbitan termuat utuh, mengukur validasi sebelum dan sesudah, lalu
memanggil perintah latih fast-plate-ocr @ 9ce7a5b. `baca` memakai model Keras langsung dengan praproses dan pascaproses
yang sama dengan `LicensePlateRecognizer`, karena ekspor ONNX belum jalan di Keras + torch. Image lab tambahan dibangun
ulang sekali untuk mematikan pemeriksaan versi albumentations yang mencoba ke internet.

**Tech Stack:** Python di image `cctvgerbang-lab-fpo:v1` (Keras 3.15.1 di atas torch, fast-plate-ocr @ 9ce7a5b), pytest,
PowerShell (pintu lab dan pembangun image), Node (kunci image, pemeriksa mesin jualan).

**Dasar:** K26, K27 (`SEED.md` §3); laporan Rencana 8 (`bukti/2026-10-14-mesin-baca-pertama.md`); catatan pelaksanaan
Rencana 9 (syarat untuk Rencana 10); `CLAUDE.md` §4, §6, §7.

---

## Yang diukur sebelum rencana ini ditulis (15 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Bahan latih | 2.824 plat. Dengan pembagian validasi Rencana 8: inti 2.521 plat (3.954 gambar), validasi 303 plat (460 gambar), tak terbaca 0 | `bukti/2026-10-14-mesin-baca-1.json` |
| Pembanding di set uji adil (911 plat) | Qwen3-VL 65–68%, fast-plate-ocr terbitan 61–79%, mesin-baca-1 26–32% kedatangan benar per kelompok | Laporan Rencana 8 |
| Bawaan perintah latih | `--lr 0.001`, `--epochs 150`, `--batch-size 64`, EMA menyala, pemanasan 5%, turun kosinus sampai 1%, berhenti dini sesudah 100 zaman tanpa kemajuan `val_plate_acc`. `best.keras` dipilih dengan `val_plate_acc` (validasi), disimpan bersama `last.keras` dan `training_log.csv` di folder bertanggal di dalam `--output-dir` | `vendor/fast-plate-ocr/fast_plate_ocr/cli/train.py` |
| Jalur gambar di CSV | `os.path.dirname(os.path.realpath(csv)) + os.sep + image_path`: jalur penuh rusak, jadi jalur harus relatif terhadap folder CSV | `fast_plate_ocr/train/data/dataset.py` baris 36–38 |
| Lama latihan | 4.000 gambar buatan berukuran mirip potongan plat, 3 zaman, angkatan 64, dari bobot terbitan: 73,9 detik termasuk persiapan; puncak memori GPU 3.690 MiB (RTX 4060 8 GB). Kira-kira 20 detik per zaman, jadi **150 zaman ≈ 50 menit** | `data/alat-sementara/ukur-rencana-10.py`, lab `-Fpo` |
| Ekspor ONNX | **Gagal** di Keras + torch: `SymbolicValueError: Unsupported: ONNX export of convolution for kernel of unknown shape`, baik ukuran angkatan bebas maupun tetap (`--no-dynamic-batch`) | `data/alat-sementara/ukur-ekspor.py`, lab `-Fpo` |
| albumentations menelepon ke luar | Saat dimuat, ia memeriksa versi terbaru ke `https://pypi.org/pypi/albumentations/json`; di lab gagal ("Temporary failure in name resolution") karena tanpa jaringan. Bisa dimatikan dengan `NO_ALBUMENTATIONS_UPDATE=1` | `albumentations/check_version.py` baris 56 dan 143–163 |

Akibatnya bagi rencana ini:

1. **Penilaian memakai model Keras langsung**, bukan ONNX. Rencana 9 membuktikan keluaran Keras tanpa TF32 sama dengan
   ONNX terbitan (selisih 1,13e-6). Uji di Task 3 membuktikan pembaca Keras dan pembaca ONNX memberi bacaan yang sama pada
   bobot terbitan, jadi perbandingannya adil. Ekspor untuk server pindah ke Rencana 11.
2. **Image lab tambahan dibangun ulang** dengan `NO_ALBUMENTATIONS_UPDATE=1`, supaya kode pihak ketiga tidak mencoba ke
   internet, juga kelak di server (K25).
3. **Pengaturan latih memakai bawaan pembuatnya**, ditulis tegas di perintah. Tidak ada penyetelan yang melihat set uji.
4. **Validasi sama dengan Rencana 8** (pembagian per plat `bagi_validasi`), supaya angka validasinya bisa dibandingkan.
5. **Syarat dari Rencana 9 dipasang di alatnya:** kernel Triton dicabut; bobot termuat utuh (192/192) diperiksa sebelum
   melatih; CSV selalu berkolom `plate_region`; TF32 dimatikan.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–9 | Bengkel sampai persiapan melatih ulang fast-plate-ocr | Selesai 13–15 Okt |
| **10 (dokumen ini)** | Image bebas panggilan keluar, alat latih ulang, latihan penuh, penilaian adil, laporan | Ditulis dan dijalankan 15 Okt |
| 11 | Menyajikan mesin di server (ekspor atau cara lain) dan kecepatannya (K25); mencari plat di foto utuh dan video; plat buatan komputer; laporan Fase 0A | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8 dan 9. Tambahan:
- **Latihan sekitar satu jam:** jalankan di latar (`run_in_background`), keluaran ke berkas log di folder sementara sesi.
  Jangan menunggu dengan `sleep`. Satu job GPU: periksa `nvidia-smi` dan `docker ps` lebih dulu. Jangan bunuh paksa; bila
  harus berhenti, `docker stop <container>` lalu periksa sisa proses.
- **Set uji dibaca sekali**, di Task 4 Step 4, sesudah mesin dipilih dengan validasi. Bila validasi sesudah latihan lebih
  buruk daripada sebelum latihan, **berhenti sebelum membaca set uji** dan laporkan ke owner.
- Perintah lab yang memuat `/kerja/...` dijalankan lewat PowerShell, dengan jalur pintu lengkap
  (`D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1`), karena folder kerja PowerShell bisa berpindah.
- Nama berkas bukti memakai tanggal `2026-10-15`. Bila dijalankan pada tanggal lain, tanggal di nama berkas (Task 4 Step 6
  dan 7, Task 5 Step 1) diganti tanggal jalan.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab-fpo/Dockerfile` (ubah) | `NO_ALBUMENTATIONS_UPDATE=1` | 1 |
| `tools/lab/uji_fpo/test_image_fpo.py` (baru) | Uji: albumentations tidak mencoba ke internet | 1 |
| `tools/vendor.lock.json` (ubah) | `image_lab_fpo` diganti ke image yang dibangun ulang | 1 |
| `tools/lab/latih_fpo.py` (baru) | `siapkan`, `latih`, `baca`, pembaca Keras, manifes mesin | 2, 3 |
| `tools/lab/uji/test_latih_fpo.py` (baru) | Uji yang tidak butuh Keras (gerbang lab biasa) | 2, 3 |
| `tools/lab/uji_fpo/test_latih_fpo_sungguhan.py` (baru) | Uji dengan Keras dan berkas model, plat buatan (di luar gerbang) | 3 |
| `bukti/2026-10-15-*.json`, `bukti/2026-10-15-fpo-latih-ulang.md` (baru) | Ringkasan dan laporan | 4, 5 |

---

### Task 1: Image lab tambahan tanpa panggilan keluar albumentations

**Files:** Create `tools/lab/uji_fpo/test_image_fpo.py`; Modify `tools/lab-fpo/Dockerfile`, `tools/vendor.lock.json`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji_fpo/test_image_fpo.py`:

```python
"""Uji isi image lab tambahan cctvgerbang-lab-fpo:v1 yang tidak terlihat dari Dockerfile saja (di luar gerbang biasa):

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import os
import subprocess
import sys


def test_albumentations_tidak_memeriksa_versi_ke_internet():
    # albumentations memeriksa versi terbaru ke pypi.org saat dimuat (check_version.py). Di lab tanpa jaringan itu gagal
    # dengan peringatan; di server (K25) ia akan benar-benar keluar. Image mematikannya dengan NO_ALBUMENTATIONS_UPDATE=1.
    hasil = subprocess.run([sys.executable, "-W", "always", "-c", "import albumentations"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stderr[-2000:]
    assert os.environ.get("NO_ALBUMENTATIONS_UPDATE") == "1"
    assert "Error fetching version info" not in hasil.stderr
```

- [x] **Step 2: Jalankan di image yang sekarang, pastikan merah**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_image_fpo.py -q -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `1 failed`, `AssertionError` pada `NO_ALBUMENTATIONS_UPDATE`, `EXIT=1`.

- [x] **Step 3: Ubah Dockerfile**

Di `tools/lab-fpo/Dockerfile`, ganti baris `ENV KERAS_BACKEND=torch` menjadi:

```dockerfile
# NO_ALBUMENTATIONS_UPDATE: albumentations memeriksa versi terbaru ke pypi.org setiap kali dimuat (Rencana 10). Dimatikan,
# supaya kode pihak ketiga tidak mencoba ke internet, juga kelak di server (K25).
ENV KERAS_BACKEND=torch \
    NO_ALBUMENTATIONS_UPDATE=1
```

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 107`, `EXIT=0` (uji pembangun memakai docker tiruan; isi Dockerfile tidak memengaruhinya).

- [x] **Step 4: Bangun ulang, lalu buktikan pintu menolak image yang belum dicatat**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\image-lab-fpo.ps1; "EXIT=$LASTEXITCODE"`
Expected: `TERBANGUN cctvgerbang-lab-fpo:v1 ID sha256:... SIDIK ...` dengan ID dan sidik yang berbeda dari kunci, `EXIT=0`.
Lapisan paket diambil dari cache, jadi jaringan hampir tidak dipakai.

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -V; "EXIT=$LASTEXITCODE"`
Expected: `IMAGE TAK SESUAI KUNCI: ... (tools\vendor.lock.json, image_lab_fpo).`, `EXIT=6`. Ini bukti langsung bahwa
image yang berubah tidak dijalankan sebelum dicatat dengan sadar.

- [x] **Step 5: Ganti catatan image di kunci (dibaca dengan skrip)**

Buat berkas sekali pakai `data/alat-sementara/kunci-image-fpo-ulang.mjs`:

```js
// Sekali pakai (Rencana 10 Task 1): image lab tambahan dibangun ulang (NO_ALBUMENTATIONS_UPDATE=1). Mengganti butir
// image_lab_fpo di kunci dengan ID, sidik, dan SHA-256 requirements yang dibaca dari docker image inspect dan berkas repo.
// Berhenti (kode 1) bila label sidik image tak sama dengan isi repo, ID tidak berubah, atau barisnya tidak ketemu tepat sekali.
// Pakai: node data/alat-sementara/kunci-image-fpo-ulang.mjs
import fs from 'node:fs';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const KUNCI = 'tools/vendor.lock.json';
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const periksa = (format) => execFileSync('docker', ['image', 'inspect', 'cctvgerbang-lab-fpo:v1', '--format', format], { encoding: 'utf8' }).trim();

const id = periksa('{{.Id}}');
const label = periksa('{{index .Config.Labels "id.megatron.cctvgerbang.kunci-fpo"}}');
const req = fs.readFileSync('tools/lab-fpo/requirements.txt');
const sidik = sha(Buffer.concat([fs.readFileSync('tools/lab-fpo/Dockerfile'), req]));
if (label !== sidik) { console.error(`label image ${label} tak sama dengan sidik isi repo ${sidik}`); process.exit(1); }
let teks = fs.readFileSync(KUNCI, 'utf8');
const kunci = JSON.parse(teks);
if (kunci.image_lab_fpo.id === id) { console.error('ID image tidak berubah: belum dibangun ulang?'); process.exit(1); }
const baris = teks.split('\n').filter((b) => b.startsWith('  "image_lab_fpo": {'));
if (baris.length !== 1) { console.error(`baris image_lab_fpo ketemu ${baris.length} kali`); process.exit(1); }
const butir = { nama: 'cctvgerbang-lab-fpo:v1', id, dasar: kunci.image_lab.id, sidik, requirements_sha256: sha(req),
  dibangun: new Date().toLocaleDateString('sv-SE') };
teks = teks.replace(baris[0], () => `  "image_lab_fpo": { ${Object.entries(butir).map(([k, v]) => `${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(', ')} },`);
JSON.parse(teks);
fs.writeFileSync(KUNCI, teks);
console.log(`image_lab_fpo diganti: ID ${kunci.image_lab_fpo.id.slice(0, 19)} -> ${id.slice(0, 19)}, sidik ${sidik.slice(0, 12)}`);
```

Run: `node data/alat-sementara/kunci-image-fpo-ulang.mjs; echo "EXIT=$?"` lalu `git diff tools/vendor.lock.json`
Expected: `image_lab_fpo diganti: ID sha256:a498d0967316 -> sha256:...`, `EXIT=0`; diff hanya baris `image_lab_fpo`.

- [x] **Step 6: Jalankan uji image tambahan, pastikan hijau**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `6 passed` (5 dari Rencana 9 + 1 baru), tidak ada baris `Error fetching version info`, `EXIT=0`.

- [x] **Step 7: Gerbang, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `152 passed`.

Commit `tools/lab-fpo/Dockerfile`, `tools/lab/uji_fpo/test_image_fpo.py`, `tools/vendor.lock.json`, dengan alasan
(panggilan keluar albumentations, K25), ID lama dan baru, dan bukti pintu menolak image yang belum dicatat (kode 6).

---

### Task 2: Bahan latih dalam bentuk CSV fast-plate-ocr (`siapkan`)

**Files:** Create `tools/lab/latih_fpo.py`, `tools/lab/uji/test_latih_fpo.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_latih_fpo.py`:

```python
"""Uji tools/lab/latih_fpo.py yang tidak butuh Keras (gerbang lab biasa): bahan CSV hanya dari sisi latih, validasi sama
dengan Rencana 8, jalur gambar mengikuti cara fast-plate-ocr, kolom wilayah selalu ada, label di luar jangkauan model
ditolak tanpa mencetak teksnya, manifes mencatat bobot awal, dan layar tanpa nomor plat."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import latih_fpo as lf  # noqa: E402
from mesin_baca import bagi_validasi  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "latih_fpo.py"
BAHAN = Path(__file__).resolve().parents[3] / "data-asal" / "bahan.json"
LATIH = [f"B{1000 + i}AB" for i in range(40)]  # 2 di antaranya jatuh ke validasi (B1011AB, B1017AB)
UJI = ["D7777XY", "F8888ZZ"]


def gambar_plat(teks):
    kanvas = np.full((60, 200, 3), 255, np.uint8)
    cv2.putText(kanvas, teks, (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    return kanvas


def buat(tmp_path, latih=LATIH, uji=UJI):
    folder = tmp_path / "gambar"
    pembagian = {}
    for sisi, daftar in (("latih", latih), ("uji", uji)):
        pembagian[sisi] = []
        for t in daftar:
            berkas = []
            for i in range(2):
                nama = f"{sisi}/{t}_{i}.png"
                (folder / sisi).mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(folder / nama), gambar_plat(t))
                berkas.append(nama)
            pembagian[sisi].append({"teks": t, "kelompok": "mobil-terang", "berkas": berkas})
    return pembagian, folder


def baca_csv(berkas):
    with open(berkas, newline="") as f:
        return list(csv.DictReader(f))


def test_bahan_hanya_dari_sisi_latih_dan_validasinya_sama_dengan_rencana_8(tmp_path):
    pembagian, folder = buat(tmp_path)

    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    latih = {b["plate_text"] for b in baca_csv(tmp_path / "keluar/latih.csv")}
    validasi = {b["plate_text"] for b in baca_csv(tmp_path / "keluar/validasi.csv")}
    inti, val = bagi_validasi(pembagian["latih"])
    assert latih == {k["teks"] for k in inti} and validasi == {k["teks"] for k in val}
    assert validasi and not (latih | validasi) & set(UJI)


def test_jalur_gambar_mengikuti_cara_fast_plate_ocr(tmp_path):
    # fast-plate-ocr (train/data/dataset.py baris 36-38) menyambung folder CSV + os.sep + jalur gambar.
    pembagian, folder = buat(tmp_path)
    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    for nama in ("latih.csv", "validasi.csv"):
        berkas = tmp_path / "keluar" / nama
        for b in baca_csv(berkas):
            assert not os.path.isabs(b["image_path"])
            assert os.path.isfile(os.path.dirname(os.path.realpath(berkas)) + os.sep + b["image_path"])


def test_kolom_wilayah_selalu_ada(tmp_path):
    # Tanpa kolom plate_region, kepala wilayah model dibuang tanpa galat (Rencana 9: 170 dari 192 tensor).
    pembagian, folder = buat(tmp_path)
    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    baris = baca_csv(tmp_path / "keluar/latih.csv")
    assert list(baris[0]) == ["image_path", "plate_text", "plate_region"]
    assert {b["plate_region"] for b in baris} == {"Indonesia"}


def test_gambar_tak_terbaca_dilewati_dan_dihitung(tmp_path):
    pembagian, folder = buat(tmp_path)
    (folder / pembagian["latih"][0]["berkas"][0]).write_bytes(b"bukan gambar")

    hitung = lf.siapkan(pembagian, folder, tmp_path / "keluar")

    assert hitung["tak_terbaca"] == 1
    assert hitung["gambar"]["latih"] + hitung["gambar"]["validasi"] == 2 * len(LATIH) - 1


@pytest.mark.parametrize("teks", ["B1234567890X", "B-1234"])
def test_label_di_luar_jangkauan_model_ditolak_tanpa_mencetak_teksnya(tmp_path, teks):
    pembagian, folder = buat(tmp_path, latih=LATIH[:3] + [teks])

    with pytest.raises(ValueError) as galat:
        lf.siapkan(pembagian, folder, tmp_path / "keluar")

    assert teks not in str(galat.value) and "1234" not in str(galat.value)


def test_manifes_mencatat_bobot_awal_sehingga_tanda_mesin_riset_saja():
    meta = lf.manifes({"plat": {}, "gambar": {}, "tak_terbaca": 0}, "a" * 64, "b" * 64, {}, {})
    vonis = {b["id"]: b["vonis"] for b in json.loads(BAHAN.read_text())["bahan"]}

    assert meta["tujuan"] == "belajar" and meta["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
    # Rantainya ke daftar bahan: tools/periksa-jualan.mjs memberi RISET-SAJA bila satu bahan bukan BOLEH-PRODUK.
    assert vonis["dataset-indo-alpr"] == "BOLEH-PRODUK" and vonis["bobot-fast-plate-ocr"] != "BOLEH-PRODUK"


def test_baris_perintah_siapkan_tanpa_nomor_plat_di_layar(tmp_path):
    pembagian, folder = buat(tmp_path)
    (folder / pembagian["latih"][0]["berkas"][0]).unlink()
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))

    hasil = subprocess.run([sys.executable, str(SKRIP), "siapkan", str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar
    assert "tak terbaca 1" in layar
    assert not any(t in layar for t in LATIH + UJI)
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'latih_fpo'` pada `test_latih_fpo.py`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/latih_fpo.py` bagian pertama**

```python
"""Melatih ulang fast-plate-ocr (cct-s-v2-global) dengan bahan latih INDO-ALPR (K26, Rencana 10).

Tiga perintah, dijalankan di image lab tambahan lewat tools\\lab.ps1 -Fpo (tanpa jaringan):
- siapkan: kedatangan LATIH -> latih.csv dan validasi.csv. Dibagi per plat dengan bagi_validasi dari Rencana 8, jadi
  validasinya sama dengan validasi mesin-baca-1. Set uji tidak pernah dibaca. Jalur gambar relatif terhadap folder CSV,
  karena fast-plate-ocr menyambung folder CSV + os.sep + jalur gambar. Kolom plate_region selalu ada (tanpa kolom itu
  kepala wilayah dibuang tanpa galat, Rencana 9). Gambar yang tak terbaca dilewati dan hanya dihitung.
- latih: memastikan bobot terbitan termuat utuh lewat jalur perintah latih (load_weights(skip_mismatch=True) melewati
  lapisan tak cocok tanpa galat), mengukur validasi dengan bobot terbitan, menjalankan perintah latih fast-plate-ocr, lalu
  menyalin best.keras (dipilih dengan validasi, bukan set uji) menjadi mesin.keras dan menulis mesin.json.
- baca: membaca set uji dengan mesin.keras (SHA-256 diperiksa terhadap mesin.json); praproses dan pascaproses sama dengan
  LicensePlateRecognizer.

Kernel Triton bawaan torch dicabut dan TF32 dimatikan di seluruh proses (Rencana 9: image lab tanpa kompiler C; dengan TF32
keluaran Keras berselisih sampai 3,98e-3 dari ONNX). mesin.json sekaligus manifes untuk tools/periksa-jualan.mjs: bahannya
INDO-ALPR dan bobot terbitan fast-plate-ocr (BELUM-JELAS), jadi tanda mesinnya RISET-SAJA sampai izin tertulis (K26, K27).

CSV dan hasil.jsonl memuat nomor plat: tinggal di data/, agen tidak membukanya. Layar hanya hitungan.

  siapkan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py siapkan /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1
  latih:   powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py latih /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan
  baca:    powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-indo-1
"""
import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_fpo import ubah_warna  # noqa: E402
from baca_vlm import KELOMPOK, matikan_kernel_triton, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from mesin_baca import HURUF, bagi_validasi  # noqa: E402
from model_terkunci import ModelDitolak, daftar_berkas, sha256_berkas, verifikasi_berkas  # noqa: E402
from plat import bersihkan  # noqa: E402

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "fast-plate-ocr"
NAMA = "fpo-indo-1"
BAHAN = ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
BUTIR = {"keras": "fpo-cct-s-v2-keras", "plat": "fpo-cct-s-v2-config", "model": "fpo-cct-s-v2-model-config"}
SLOT_MAKS = 10  # max_plate_slots konfigurasi plat terbitan; dicocokkan uji di tools/lab/uji_fpo
WILAYAH = "Indonesia"
ZAMAN = 150
UKURAN_ANGKATAN = 64
BENIH = 0


def baris_csv(kedatangan, folder_gambar, folder_csv):
    """Kedatangan -> (baris CSV [jalur relatif, teks, wilayah], jumlah gambar tak terbaca). Label yang tak bisa dibaca model
    (huruf di luar HURUF, kosong, atau lebih dari SLOT_MAKS) ditolak tanpa mencetak teksnya."""
    baris, tak = [], 0
    for k in kedatangan:
        if not k["teks"] or len(k["teks"]) > SLOT_MAKS or any(c not in HURUF for c in k["teks"]):
            raise ValueError("label di luar huruf atau panjang yang bisa dibaca model")
        for b in k["berkas"]:
            jalur = Path(folder_gambar) / b
            if cv2.imread(str(jalur)) is None:
                tak += 1
                continue
            baris.append([os.path.relpath(os.path.realpath(jalur), os.path.realpath(folder_csv)), k["teks"], WILAYAH])
    return baris, tak


def siapkan(pembagian, folder_gambar, keluar):
    """Hanya pembagian["latih"]; set uji tidak dibaca. Kembali: hitungan (tanpa nomor plat), juga ditulis ke siapkan.json."""
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    inti, validasi = bagi_validasi(pembagian["latih"])
    hitung = {"plat": {"latih": len(inti), "validasi": len(validasi)}, "gambar": {}, "tak_terbaca": 0}
    for nama, daftar in (("latih", inti), ("validasi", validasi)):
        baris, tak = baris_csv(daftar, folder_gambar, keluar)
        with open(keluar / f"{nama}.csv", "w", newline="") as berkas:
            tulis = csv.writer(berkas)
            tulis.writerow(["image_path", "plate_text", "plate_region"])
            tulis.writerows(baris)
        hitung["gambar"][nama] = len(baris)
        hitung["tak_terbaca"] += tak
    (keluar / "siapkan.json").write_text(json.dumps(hitung, indent=1))
    return hitung


def manifes(hitung, sha_mesin, sha_awal, latihan, validasi):
    """Isi mesin.json. Sekaligus manifes untuk tools/periksa-jualan.mjs: bobot awal terbitan ikut tercatat sebagai bahan."""
    return {"nama": NAMA, "tujuan": "belajar", "bahan": BAHAN,
            "keterangan": "fast-plate-ocr @ 9ce7a5b, cct-s-v2-global, dilatih ulang dengan bahan latih INDO-ALPR (K26)",
            "sha256_mesin": sha_mesin, "sha256_bobot_awal": sha_awal, **hitung, "latihan": latihan, "validasi": validasi}


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Melatih ulang fast-plate-ocr dengan bahan latih INDO-ALPR (Rencana 10).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    s = perintah.add_parser("siapkan")
    for nama in ("pembagian", "folder_gambar", "keluar"):
        s.add_argument(nama)
    p = urai.parse_args(argumen)
    try:
        h = siapkan(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.keluar)
        print(f"plat latih {h['plat']['latih']}, validasi {h['plat']['validasi']}; gambar latih {h['gambar']['latih']}, "
              f"validasi {h['gambar']['validasi']}; tak terbaca {h['tak_terbaca']}")
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `160 passed` (152 + 8), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/latih_fpo.py` dan ujinya, dengan alasan (bentuk bahan fast-plate-ocr, validasi Rencana 8,
syarat Rencana 9) dan angka gerbang 152 → 160.

---

### Task 3: Latih dan baca (`latih`, `baca`, pembaca Keras)

**Files:** Modify `tools/lab/latih_fpo.py`, `tools/lab/uji/test_latih_fpo.py`; Create `tools/lab/uji_fpo/test_latih_fpo_sungguhan.py`

- [x] **Step 1: Tulis ujinya**

Tambahkan di akhir `tools/lab/uji/test_latih_fpo.py` (gerbang biasa; pemeriksaan SHA terjadi sebelum Keras dimuat):

```python
def test_pembaca_menolak_mesin_yang_berubah_sebelum_memuat_keras(tmp_path):
    from model_terkunci import ModelDitolak

    (tmp_path / "mesin.keras").write_bytes(b"ditukar")
    (tmp_path / "mesin.json").write_text(json.dumps({"sha256_mesin": "0" * 64}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        lf.PembacaMesinFpo(tmp_path, tmp_path / "unduhan")
```

Buat `tools/lab/uji_fpo/test_latih_fpo_sungguhan.py`:

```python
"""Uji tools/lab/latih_fpo.py yang butuh Keras dan berkas model, di image lab tambahan (di luar gerbang biasa), hanya dengan
plat buatan:

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import sys
from pathlib import Path

import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import latih_fpo as lf  # noqa: E402
from baca_fpo import PembacaFpo  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_latih_fpo import UJI, buat  # noqa: E402
from test_percobaan_fpo import ADA, TEKS, plat_buatan  # noqa: E402

pytestmark = pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")


def test_bobot_terbitan_termuat_utuh_dan_konfigurasi_salah_tertangkap(tmp_path):
    jalur = lf.jalur_terkunci(UNDUHAN)
    lf.siapkan_torch()
    assert lf.bobot_utuh(jalur) == (192, 192)

    asli = Path(jalur["model"]).read_text()
    assert asli.count("\n  layers: 5\n") == 1
    salah = tmp_path / "model_config.yaml"
    salah.write_text(asli.replace("\n  layers: 5\n", "\n  layers: 4\n"))
    sama, semua = lf.bobot_utuh({**jalur, "model": salah})
    assert sama < semua


def test_pembaca_keras_membaca_sama_dengan_pembaca_onnx_terbitan():
    # Perlakuan sama: bobot terbitan lewat PembacaKeras harus memberi bacaan yang sama dengan PembacaFpo (ONNX, Rencana 6).
    jalur = lf.jalur_terkunci(UNDUHAN)
    keras_ = lf.PembacaKeras(jalur["keras"], jalur["plat"])
    onnx_ = PembacaFpo(UNDUHAN)

    assert [keras_(plat_buatan(t)) for t in TEKS] == [onnx_(plat_buatan(t)) for t in TEKS]
    assert lf.SLOT_MAKS == keras_.cfg.max_plate_slots and set(lf.HURUF) < set(keras_.cfg.alphabet)


def test_rantai_siapkan_latih_baca_dengan_plat_buatan(tmp_path):
    pembagian, folder = buat(tmp_path)
    mesin = tmp_path / "mesin"

    lf.siapkan(pembagian, folder, mesin)
    meta = lf.latih(mesin, UNDUHAN, zaman=1)
    ringkasan = lf.baca(pembagian, folder, mesin, UNDUHAN, tmp_path / "baca")

    assert meta["sha256_mesin"] == lf.sha256_berkas(mesin / "mesin.keras")
    assert meta["latihan"]["bobot_termuat"] == "192/192" and meta["latihan"]["zaman_berjalan"] == 1
    assert meta["validasi"]["awal"]["gambar"] == meta["validasi"]["akhir"]["gambar"] > 0
    assert json.loads((mesin / "mesin.json").read_text())["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
    assert ringkasan["per_kelompok"]["mobil-terang"]["kedatangan"] == len(UJI)
    (mesin / "mesin.keras").write_bytes(b"ditukar")
    with pytest.raises(ModelDitolak):
        lf.PembacaMesinFpo(mesin, UNDUHAN)
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `1 failed, 160 passed` (`AttributeError: ... 'PembacaMesinFpo'`), `EXIT=1`.

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `3 failed, 6 passed` (`AttributeError` pada `jalur_terkunci`, `PembacaKeras`, `latih`), `EXIT=1`.

- [x] **Step 3: Tambahkan bagian latih dan baca di `tools/lab/latih_fpo.py`**

Sisipkan sesudah fungsi `manifes`:

```python
def siapkan_torch():
    """Sebelum Keras dimuat: cabut kernel Triton (image lab tanpa kompiler C), matikan TF32 (Rencana 9), dan pakai klon
    fast-plate-ocr yang terkunci."""
    matikan_kernel_triton()
    import torch

    torch.backends.cudnn.allow_tf32 = torch.backends.cuda.matmul.allow_tf32 = False
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))


def jalur_terkunci(folder_unduhan):
    """Bobot .keras, konfigurasi plat, dan konfigurasi model terbitan, masing-masing diperiksa SHA-256-nya terhadap kunci."""
    daftar = daftar_berkas()
    return {k: verifikasi_berkas(Path(folder_unduhan) / b / daftar.get(b, ("?", ""))[0], b, daftar) for k, b in BUTIR.items()}


def bobot_utuh(jalur):
    """Bobot terbitan dimuat lewat jalur perintah latih (build_model + load_weights(skip_mismatch=True)) lalu dibandingkan
    dengan model .keras utuh. Kembali: (jumlah tensor yang sama persis, jumlah tensor terbitan)."""
    import numpy as np
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.model.model_builders import build_model
    from fast_plate_ocr.train.model.model_schema import load_model_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur["plat"])
    model = build_model(load_model_config_from_yaml(jalur["model"]), cfg, enable_region_head=True)
    model.load_weights(jalur["keras"], skip_mismatch=True)
    a = [np.asarray(w) for w in model.get_weights()]
    b = [np.asarray(w) for w in load_keras_model(jalur["keras"], cfg).get_weights()]
    sama = sum(x.shape == y.shape and np.array_equal(x, y) for x, y in zip(a, b)) if len(a) == len(b) else 0
    return int(sama), len(b)


class PembacaKeras:
    """Membaca dengan model .keras fast-plate-ocr. Praproses dan pascaproses sama dengan LicensePlateRecognizer, tetapi
    modelnya dijalankan Keras (ekspor ONNX belum jalan di Keras + torch). Dipanggil dengan satu gambar urutan warna OpenCV."""

    def __init__(self, berkas_keras, berkas_plat):
        siapkan_torch()
        from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
        from fast_plate_ocr.train.utilities.utils import load_keras_model

        self.cfg = load_plate_config_from_yaml(berkas_plat)
        self._model = load_keras_model(berkas_keras, self.cfg)

    def __call__(self, gambar_bgr):
        import numpy as np
        from fast_plate_ocr.core.process import postprocess_output, preprocess_image
        from fast_plate_ocr.inference.plate_recognizer import _load_image_from_source

        x = preprocess_image(_load_image_from_source(ubah_warna(gambar_bgr, self.cfg.image_color_mode), self.cfg))
        keluar = self._model.predict(x.astype(np.float32), verbose=0)
        return postprocess_output(keluar["plate"], self.cfg.max_plate_slots, self.cfg.alphabet,
                                  pad_char=self.cfg.pad_char)[0].plate


class PembacaMesinFpo(PembacaKeras):
    """Pembaca dengan mesin hasil latih ulang. mesin.keras yang SHA-256-nya tidak sama dengan mesin.json ditolak SEBELUM
    Keras dimuat. Konfigurasi platnya berkas terbitan yang terkunci (model dilatih dengan konfigurasi itu)."""

    def __init__(self, folder_mesin, folder_unduhan):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin.json").read_text())
        if sha256_berkas(folder / "mesin.keras") != meta["sha256_mesin"]:
            raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
        super().__init__(folder / "mesin.keras", jalur_terkunci(folder_unduhan)["plat"])


def ketepatan(baca, berkas_csv):
    """Membaca semua gambar satu CSV (jalur seperti fast-plate-ocr: folder CSV + os.sep + jalur). Kembali: hitungan."""
    folder = os.path.dirname(os.path.realpath(berkas_csv))
    gambar = benar = 0
    with open(berkas_csv, newline="") as berkas:
        for b in csv.DictReader(berkas):
            g = cv2.imread(folder + os.sep + b["image_path"])
            gambar += 1
            benar += int(g is not None and bersihkan(baca(g)) == b["plate_text"])
    return {"gambar": gambar, "benar": benar}


def latih(folder, folder_unduhan, zaman=ZAMAN, benih=BENIH, ukuran_angkatan=UKURAN_ANGKATAN):
    """Melatih dari latih.csv dan validasi.csv hasil siapkan (set uji tidak pernah diberikan). Kembali: isi mesin.json."""
    folder = Path(folder)
    hitung = json.loads((folder / "siapkan.json").read_text())
    jalur = jalur_terkunci(folder_unduhan)
    siapkan_torch()
    sama, semua = bobot_utuh(jalur)
    if sama != semua:
        raise ModelDitolak(f"bobot terbitan tidak termuat utuh lewat jalur perintah latih: {sama} dari {semua} tensor sama")
    awal = ketepatan(PembacaKeras(jalur["keras"], jalur["plat"]), folder / "validasi.csv")
    print(f"validasi dengan bobot terbitan: benar {awal['benar']} dari {awal['gambar']} gambar", flush=True)
    latihan = folder / "latihan"
    if latihan.exists():
        raise FileExistsError("folder latihan sudah ada; dipindah atau dihapus dengan sadar sebelum melatih lagi")

    import torch
    from fast_plate_ocr.cli.cli import main_cli

    main_cli(["train", "--model-config-file", str(jalur["model"]), "--plate-config-file", str(jalur["plat"]),
              "--annotations", str(folder / "latih.csv"), "--val-annotations", str(folder / "validasi.csv"),
              "--weights-path", str(jalur["keras"]), "--epochs", str(zaman), "--batch-size", str(ukuran_angkatan),
              "--seed", str(benih), "--output-dir", str(latihan)], standalone_mode=False)
    (hasil,) = [p for p in latihan.iterdir() if p.is_dir()]
    shutil.copy(hasil / "best.keras", folder / "mesin.keras")
    with open(hasil / "training_log.csv", newline="") as berkas:
        log = list(csv.DictReader(berkas))
    # ModelCheckpoint menyimpan best.keras hanya bila val_plate_acc naik, jadi zaman terbaik adalah nilai tertinggi PERTAMA.
    terbaik = max(range(len(log)), key=lambda i: (float(log[i]["val_plate_acc"]), -i))
    akhir = ketepatan(PembacaKeras(folder / "mesin.keras", jalur["plat"]), folder / "validasi.csv")
    meta = manifes(hitung, sha256_berkas(folder / "mesin.keras"), sha256_berkas(jalur["keras"]),
                   {"zaman": zaman, "zaman_berjalan": len(log), "zaman_terbaik": terbaik + 1, "benih": benih,
                    "ukuran_angkatan": ukuran_angkatan, "val_plate_acc_terbaik": round(float(log[terbaik]["val_plate_acc"]), 4),
                    "bobot_termuat": f"{sama}/{semua}",
                    "perangkat": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"},
                   {"awal": awal, "akhir": akhir})
    (folder / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def baca(pembagian, folder_gambar, folder_mesin, folder_unduhan, keluar, pembaca=None):
    """Membaca set uji dengan mesin hasil latih ulang. Kembali: ringkasan (hitungan saja)."""
    pembaca = pembaca or PembacaMesinFpo(folder_mesin, folder_unduhan)
    baris, ringkasan = nilai(pembagian, folder_gambar, pembaca, "uji")
    ringkasan = {"model": NAMA, "sisi": "uji", **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for x in baris:
            berkas.write(json.dumps(x) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    return ringkasan
```

Ganti seluruh fungsi `utama` dengan:

```python
def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Melatih ulang fast-plate-ocr dengan bahan latih INDO-ALPR (Rencana 10).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    s = perintah.add_parser("siapkan")
    for nama in ("pembagian", "folder_gambar", "keluar"):
        s.add_argument(nama)
    a = perintah.add_parser("latih")
    for nama in ("folder", "folder_unduhan"):
        a.add_argument(nama)
    a.add_argument("--zaman", type=int, default=ZAMAN)
    a.add_argument("--benih", type=int, default=BENIH)
    b = perintah.add_parser("baca")
    for nama in ("pembagian", "folder_gambar", "folder_mesin", "folder_unduhan", "keluar"):
        b.add_argument(nama)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "siapkan":
            h = siapkan(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.keluar)
            print(f"plat latih {h['plat']['latih']}, validasi {h['plat']['validasi']}; gambar latih {h['gambar']['latih']}, "
                  f"validasi {h['gambar']['validasi']}; tak terbaca {h['tak_terbaca']}")
        elif p.perintah == "latih":
            m = latih(p.folder, p.folder_unduhan, p.zaman, p.benih)
            print(f"selesai: zaman terbaik {m['latihan']['zaman_terbaik']} dari {m['latihan']['zaman_berjalan']}; validasi benar "
                  f"{m['validasi']['awal']['benar']} -> {m['validasi']['akhir']['benar']} dari {m['validasi']['akhir']['gambar']} "
                  f"gambar; bobot termuat {m['latihan']['bobot_termuat']}")
        else:
            r = baca(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.folder_mesin, p.folder_unduhan, p.keluar)
            for k in KELOMPOK:
                print(f"{k:<13} {uraikan(r['per_kelompok'][k])}")
            print(f"detik per gambar: {r['detik_per_gambar']}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `161 passed`, `EXIT=0`.

Run (PowerShell): `nvidia-smi --query-gpu=memory.used --format=csv,noheader` lalu
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `9 passed`, `EXIT=0`.

Bila `test_pembaca_keras_membaca_sama_dengan_pembaca_onnx_terbitan` gagal, **berhenti**: perbandingan dengan fast-plate-ocr
terbitan tidak adil sampai sebabnya ditemukan dan diukur.

- [x] **Step 5: Gerbang Node, lalu commit**

Run: `npm test; echo "EXIT=$?"` (Expected `pass 107`)

Commit `tools/lab/latih_fpo.py` dan kedua berkas uji, dengan alasan (syarat Rencana 9, penilaian dengan Keras karena ekspor
ONNX gagal, uji perlakuan sama), angka gerbang lab 160 → 161, dan uji image tambahan 6 → 9.

---

### Task 4: Latihan penuh dan penilaian pada set uji

**Files:** Create `data/alat-sementara/periksa-bukti-10.py` (sekali pakai, di-gitignore), `bukti/2026-10-15-*.json`

- [x] **Step 1: Siapkan bahan**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py siapkan /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1; "EXIT=$LASTEXITCODE"`
Expected: `plat latih 2521, validasi 303; gambar latih 3954, validasi 460; tak terbaca 0`, `EXIT=0`. Angka ini harus sama
dengan mesin-baca-1 (Rencana 8). Bila lain, **berhenti**: pembagian atau bahannya berubah.

- [x] **Step 2: Latih (sekitar satu jam, di latar)**

Periksa dulu (PowerShell): `nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader` dan `docker ps`.
Tidak boleh ada job lab lain.

Run (PowerShell, `run_in_background`, keluaran ke `<folder sementara sesi>\latih-fpo-indo-1.txt`):
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py latih /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan *> <log>; "EXIT=$LASTEXITCODE"`
Expected: baris `validasi dengan bobot terbitan: benar A dari 460 gambar`, lalu kemajuan per zaman, lalu
`selesai: zaman terbaik N dari M; validasi benar A -> B dari 460 gambar; bobot termuat 192/192`, `EXIT=0`. Lamanya dicatat.

Bila `B < A`, **berhenti di sini**. Set uji belum dibaca, jadi masih bisa dipakai untuk penilaian yang adil sesudah owner
memutuskan langkah berikutnya.

- [x] **Step 3: Periksa tanda mesin**

Run: `node tools/periksa-jualan.mjs data/keluaran/fpo-indo-1/mesin.json; echo "EXIT=$?"`
Expected: `mesin "fpo-indo-1" (belajar): tanda mesin = RISET-SAJA`, `EXIT=0`.

- [x] **Step 4: Baca set uji (sekali)**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-indo-1; "EXIT=$LASTEXITCODE"`
Expected: empat baris per kelompok (kedatangan benar, rentang 95%, ragu, gambar benar, di luar pola), `detik per gambar`, `EXIT=0`.

- [x] **Step 5: Bandingkan dengan tiga pembaca, dua cara hitung**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/banding_pembaca.py /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/banding-pembaca-10 --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl --hasil mesin-baca-1=/kerja/data/keluaran/baca-mesin-1/hasil.jsonl --hasil fpo-indo-1=/kerja/data/keluaran/baca-fpo-indo-1/hasil.jsonl; "EXIT=$LASTEXITCODE"`
Expected: dua blok (`semua (937 kedatangan uji)` dan `tanpa-label-pilihan-pembaca (911 kedatangan uji)`), tiap kelompok
empat pembaca; angka tiga pembaca lama sama dengan `bukti/2026-10-14-banding-pembaca.json`; `EXIT=0`.

- [x] **Step 6: Salin ringkasan ke `bukti/` sesudah dibuktikan tanpa nomor plat (dengan kontrol positif)**

Buat `data/alat-sementara/periksa-bukti-10.py`:

```python
"""Sekali pakai (Rencana 10): menyalin ringkasan ke bukti-siap/ hanya bila tak satu pun teks plat atau nama berkas ada di
dalamnya. Larangan: teks plat dan nama berkas di set-uji-koreksi/pembagian-koreksi.json dan latih-koreksi/pembagian-koreksi.json,
ditambah usulan di kedua curiga.json. Kontrol positif lebih dulu pada baca-fpo-indo-1/hasil.jsonl; bila tidak menemukan
apa pun, berhenti. Hanya hitungan yang dicetak.
"""
import json
import shutil
import sys
from pathlib import Path

K = Path("/kerja/data/keluaran")
larangan = set()
for berkas in ("set-uji-koreksi/pembagian-koreksi.json", "latih-koreksi/pembagian-koreksi.json"):
    p = json.loads((K / berkas).read_text())
    larangan |= {a["teks"] for s in p.values() for a in s}
    larangan |= {Path(b).stem for s in p.values() for a in s for b in a["berkas"]}
for berkas in ("label-curiga/curiga.json", "label-curiga-latih/curiga.json"):
    larangan |= {c["usulan"] for c in json.loads((K / berkas).read_text())}


def temuan(teks):
    return sum(1 for t in larangan if t in teks)


kontrol = temuan((K / "baca-fpo-indo-1/hasil.jsonl").read_text())
print(f"ukuran daftar larangan: {len(larangan)}; kontrol positif (baca-fpo-indo-1/hasil.jsonl): {kontrol} ditemukan")
if kontrol == 0:
    sys.exit(1)
(log,) = list((K / "fpo-indo-1/latihan").glob("*/training_log.csv"))
for asal, tujuan in [(K / "fpo-indo-1/mesin.json", "fpo-indo-1.json"),
                     (log, "fpo-indo-1-latihan.csv"),
                     (K / "baca-fpo-indo-1/ringkasan.json", "baca-fpo-indo-1.json"),
                     (K / "banding-pembaca-10/ringkasan.json", "banding-pembaca-10.json")]:
    n = temuan(asal.read_text())
    print(f"{tujuan}: {n} teks plat atau nama berkas ditemukan")
    if n:
        sys.exit(1)
    shutil.copy(asal, K / "bukti-siap" / f"2026-10-15-{tujuan}")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/periksa-bukti-10.py; "EXIT=$LASTEXITCODE"`
Expected: kontrol positif lebih dari 0, keempat berkas `0 teks plat atau nama berkas ditemukan`, `EXIT=0`.

Run: `cp data/keluaran/bukti-siap/2026-10-15-fpo-indo-1.json data/keluaran/bukti-siap/2026-10-15-fpo-indo-1-latihan.csv data/keluaran/bukti-siap/2026-10-15-baca-fpo-indo-1.json data/keluaran/bukti-siap/2026-10-15-banding-pembaca-10.json bukti/`

- [x] **Step 7: Commit** keempat berkas `bukti/2026-10-15-*`, dengan angka validasi sebelum → sesudah, angka set uji per
kelompok untuk keempat pembaca pada kedua cara hitung, lama latihan, dan tanda mesin.

---

### Task 5: Laporan, catatan, dan laporan ke owner

- [x] **Step 1: Tulis laporan `bukti/2026-10-15-fpo-latih-ulang.md`**

Isinya:
- **Mesin:** cct-s-v2-global dari bobot terbitan, 192/192 tensor termuat, dilatih ulang dengan bawaan pembuatnya.
- **Bahan:** plat dan gambar latih/validasi.
- **Jalannya latihan:** dari `fpo-indo-1-latihan.csv`, yaitu `val_plate_acc` awal, terbaik, dan akhir, zaman terbaik,
  zaman berjalan, dan lama latihan.
- **Validasi:** benar sebelum → sesudah, dengan pembaca yang sama.
- **Set uji:** angka per kelompok dengan rentang 95%, keempat pembaca, kedua cara hitung.
- **Tanda mesin:** `RISET-SAJA` (K26, K27).
- **Batas:**
  - satu kali latihan dengan satu benih;
  - potongan plat, bukan kamera gerbang (K9 tidak terbukti);
  - set uji masih memuat label salah sekitar 3% (taksiran Rencana 6);
  - penilaian dengan Keras, bukan ONNX; ekspor dan kecepatan di server ada di Rencana 11;
  - izin tertulis belum ada.

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 10 ditulis" dicentang;
  - butir "Rencana 10 dijalankan" dicentang dengan angka;
  - butir berikutnya sesuai jawaban owner;
  - baris status dan changelog.
- `CLAUDE.md` §7:
  - mesin `fpo-indo-1` ada di `data/keluaran/fpo-indo-1/` dan hanya dimuat lewat `PembacaMesinFpo` (SHA-256 terhadap
    `mesin.json`);
  - ekspor ONNX belum jalan di Keras + torch.
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 10".
- Rencana ini: kotak dicentang dan catatan pelaksanaan.

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `161 passed`.

- [x] **Step 4: BERHENTI. Laporkan ke owner**

Ringkas dalam bahasa sederhana:
- apakah melatih ulang menaikkan angka baca, dan untuk kelompok mana;
- seberapa jauh dari Qwen3-VL;
- apa batasnya.

Lalu **satu** pertanyaan pilihan ganda dengan saran di depan, sesuai hasilnya:
- Bila naik jelas: menulis Rencana 11 (menyajikan di server dan kecepatannya, mencari plat di foto utuh dan video, plat
  buatan komputer, laporan Fase 0A).
- Bila naik sedikit atau tidak naik: pilihan memperbaiki lewat validasi saja, misalnya:
  - menambah plat buatan komputer;
  - menyetel laju belajar dengan validasi;
  - menambah kedatangan motor-gelap;
  - atau tetap lanjut ke Rencana 11.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K26:** melatih ulang (Task 3–4), dinilai adil pada set uji yang sama dengan pembaca lain (Task 3 uji perlakuan
  sama, Task 4 Step 5), tanda riset sampai izin (Task 2 manifes, Task 4 Step 3).
- **Set uji tidak bocor ke pemilihan:** `siapkan` hanya membaca sisi latih (diuji); `best.keras` dipilih dengan validasi;
  set uji dibaca sekali sesudahnya, dan ada titik berhenti bila validasi memburuk.
- **Syarat Rencana 9:**
  - kernel Triton dan TF32: `siapkan_torch`;
  - bobot utuh: `bobot_utuh` dengan kontrol negatif;
  - kolom wilayah: diuji;
  - jalur relatif: diuji dengan rumus fast-plate-ocr.
- **Rantai pasok:** image dibangun ulang hanya untuk menutup panggilan keluar; pintu menolak image yang belum dicatat
  (dibuktikan langsung); paket tidak berubah.
- **Data pribadi:**
  - layar hanya hitungan (diuji di proses terpisah);
  - galat hanya mencetak jenisnya;
  - ringkasan disalin ke `bukti/` sesudah pemeriksaan larangan dengan kontrol positif.
- **Tanpa isian kosong pada kode:** semua kode uji dan alat tertulis lengkap. Satu-satunya skrip yang hanya dijelaskan
  adalah pencatat Task 5 Step 2 (pola sama dengan Rencana 9).
- **Angka gerbang:** Node 107 tetap; lab 152 → 160 → 161; uji image tambahan 5 → 6 → 9.
- **Nama konsisten:**
  - `siapkan`, `baris_csv`, `manifes`, `siapkan_torch`, `jalur_terkunci`, `bobot_utuh`, `PembacaKeras`,
    `PembacaMesinFpo`, `ketepatan`, `latih`, `baca`, `utama`;
  - kunci `mesin.json`: `sha256_mesin`, `latihan.bobot_termuat`, `latihan.zaman_berjalan`, `validasi.awal`,
    `validasi.akhir`.

## Catatan pelaksanaan (15 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Commit: `ad950d5` (Task 1), `cba0795` (Task 2), `2a34edc` (Task 3), `93d2fd7`
(Task 4), dan commit laporan dan catatan (Task 5).

| Task | Hasil | Menyimpang dari rencana |
|---|---|---|
| 1 | Merah dulu di image lama; dibangun ulang dalam 1 detik (paket dari cache); pintu menolak image baru dengan kode 6 sampai kunci diperbarui; ID `sha256:5b57c7b2fd9d…`; uji image tambahan 6 lulus | — |
| 2 | Merah dulu (modul belum ada); lab 152 → 160 | — |
| 3 | Merah dulu (1 gagal di gerbang biasa, 3 gagal di image tambahan, semuanya `AttributeError`); lab 161, uji image tambahan 9 | Uji rantai mencetak "benar 0 dari 4" untuk bobot terbitan pada plat buatan. Diperiksa dengan skrip sekali pakai: model membaca angka 0 sebagai huruf O pada huruf buatan komputer (ONNX dan Keras sama), dan `ketepatan` memberi 3 dari 3 bila label diisi bacaan model sendiri |
| 4 | `siapkan` sama persis dengan Rencana 8; validasi 301 → 388 dari 460; set uji dibaca sekali; tiga pembaca lama sama persis dengan Rencana 8; tanda `RISET-SAJA`; bukti diperiksa dengan kontrol positif (2.379) | Latihan 174,6 menit, bukan sekitar 50 menit (76–81 detik per zaman); sebabnya belum diukur. `val_plate_acc` fast-plate-ocr 85,1% vs pembaca kita 84,3% |
| 5 | Laporan `bukti/2026-10-15-fpo-latih-ulang.md`, catatan, gerbang Node 107 dan lab 161 | — |

**Untuk rencana berikutnya:**
- Taksiran lama latihan diukur dengan bahan sungguhan, bukan plat buatan.
- Menjalankan fpo-indo-1 di server butuh jalan keluar dari ekspor ONNX yang gagal di Keras + torch.
- "Keuntungan tuan rumah" hanya bisa dijawab dengan gambar dari luar INDO-ALPR, misalnya kamera gerbang sungguhan atau video riset.
