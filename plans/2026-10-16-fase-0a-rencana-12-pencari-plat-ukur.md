# Fase 0A, Rencana 12: Pencari plat — ukur dulu, latih kemudian (K28, K29) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Sebelum melatih pencari plat sendiri (langkah 1 spec 2.1), dua hal diukur:
1. Seberapa baik pencari plat ringan siap pakai menemukan plat di foto utuh Indonesia. Dipakai sebagai pembanding, pada set
   uji plat-lighting.
2. Seberapa cepat tiga jenis calon pencari plat buatan sendiri (YOLOX-Nano, YOLOX-Tiny, RF-DETR Nano) di CPU laptop **dan di
   Mini PC** yang akan menjadi server fase awal (K29).

Hasilnya dipakai owner untuk memilih jenis mana yang dilatih di Rencana 13.

**Architecture:**
- `tools/lab/deteksi.py` menilai pencari mana pun pada foto berlabel kotak YOLO: plat ditemukan, kotak palsu, kelompok
  terang/gelap dan kecil/besar. Ambang keyakinan dipilih di validasi, lalu dipakai sekali di uji.
- `tools/lab/pencari_oim.py` membungkus pembanding open-image-models YOLOv9-t-384. Berkasnya terkunci SHA-256, dan
  kode open-image-models dimuat dari klon terkunci.
- `tools/ukur_onnx_cpu.py` mengukur lama satu panggilan model ONNX di CPU dengan masukan buatan. Ia hanya butuh numpy dan
  onnxruntime, supaya bisa dijalankan apa adanya di Mini PC.

Calon buatan sendiri diukur dengan bobot acak, karena kecepatan ditentukan susunan model, bukan nilai bobotnya.

**Tech Stack:** Python di image lab (`vision-seed-lab:v1`: rfdetr 1.11.1, onnxruntime 1.30.0) dan image tambahan
(`cctvgerbang-lab-fpo:v1`: onnx), PowerShell, Node, SSH ke Mini PC (`mini-megatron`).

**Dasar:** K25, K28, K29 (`SEED.md` §3); spec 2.1, 2.3 ("untuk kotak murah diukur juga calon yang lebih ringan"), 2.6
(sasaran dua detik), 8.1 langkah 7 dan 8; `docs/VONIS-LISENSI.md`.

---

## Yang diukur sebelum rencana ini ditulis (15 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Bahan berkotak plat | Hanya plat-lighting: 561 foto (latih 393, valid 84, uji 84), 694 kotak plat, 1 kelas, label YOLO; 428 foto 1920×1080 dan 133 foto 860×931; Roboflow Universe `plat-nomor-bpqge` v3, izin CC BY 4.0, `BOLEH-PRODUK`. Dua berkas README ikut berakhiran `.txt` di folder label. INDO-ALPR berisi potongan plat, bukan foto utuh | `data/alat-sementara/ukur-pustaka-deteksi.py`; `data-asal/bahan.json` |
| Dataset deteksi lain | UI (1.000 foto 3024×3024, izin "Unknown", `RISET-SAJA`, butuh akun Kaggle) dan kendaraan niaga Semarang (362 bingkai, "Unknown") | `docs/riset/2026-10-13-catatan-bahan-data-plat.md` |
| Pustaka di image lab | rfdetr 1.11.1, supervision 0.30.6, torch 2.14.1, onnxruntime-gpu 1.30.0; tidak ada onnx, pycocotools, albumentations. Image tambahan punya onnx 1.23.2 | sama |
| Latih RF-DETR | **Belum bisa:** `rfdetr[train]` tidak terpasang. Paket yang diminta: pytorch_lightning, torchmetrics[detection], peft, hotcoco, faster-coco-eval, ultrafast-pycocotools, vernier, pycocotools, scipy, simplejpeg, roboflow, dan torch-hungarian 0.1.0rc0 (pra-rilis) | `vendor/rf-detr/pyproject.toml` |
| Latih YOLOX | Kode klon (Apache-2.0) bisa membangun model hanya dengan tiruan `loguru` dan `thop`; untuk melatih butuh loguru, tabulate, dan pycocotools | `data/alat-sementara/ukur-yolox-cpu.py` |
| Kecepatan calon di CPU laptop, model saja, bobot acak, masukan acak | YOLOX-Nano 416 px (0,9 juta parameter, 3,7 MB): **11,8 / 7,0 / 5,1 ms** dengan 1 / 2 / 4 utas. YOLOX-Tiny 416 px (5,0 juta, 20 MB): 51,7 / 27,9 / 15,8 ms. RF-DETR Nano 384 px (107 MB): **265 / 141 / 89 ms**. RF-DETR Small 512 px: 487 / 273 / 471 ms (tidak stabil) | `ukur-yolox-cpu.py`, `ukur-rfdetr-cpu.py` |
| Ekspor ONNX RF-DETR | Jalan di image tambahan tanpa onnxsim, bobot acak, 7,8 detik; membangun tanpa bobot awal tidak mencoba mengunduh | `ukur-rfdetr-cpu.py` |
| Pembanding siap pakai | open-image-models @ eaeb588: `yolo-v9-t-{256,384,416,512,640}` dan `yolo-v9-s-608` plat (ONNX end2end, sekitar 7,8 MB untuk t). Aset rilis 2024 **tanpa digest** dari GitHub. `create_detector(berkas_lokal, backend="yolo_v9", class_labels=..., conf_thresh=..., providers=..., sess_options=...)` menerima berkas lokal tanpa mengunduh. Kebutuhannya numpy, opencv, tqdm, rich, onnxruntime | API rilis GitHub; `open_image_models/detection/factory.py` |
| Mini PC | Celeron N5095, 4 inti, RAM 7,5 GiB dengan sekitar 2,3 GiB tersedia, beban sekitar 1,5 (menjalankan layanan Mini, actions-runner, dan lain-lain); Python 3.12.3, venv ada; ruang kosong 17 GB | SSH, perintah baca saja |

Akibatnya bagi rencana ini:

1. **RF-DETR Nano berat di CPU**, sekitar 22 kali lebih lambat daripada YOLOX-Nano di laptop. Di Celeron kemungkinan jauh
   lebih lambat, padahal sasaran spec 2.6 adalah dua detik dari kendaraan berhenti sampai perintah buka. Jadi kecepatan di
   Mini PC diukur **sebelum** memilih jenis yang dilatih.
2. **Melatih butuh paket baru** apa pun jenisnya: YOLOX tiga paket, RF-DETR sekitar dua belas termasuk satu pra-rilis.
   Rantai pasok itu dikerjakan di Rencana 13 untuk jenis yang dipilih saja.
3. **Bahan uji deteksi kecil:** 84 foto uji. Angka dilaporkan dengan rentang 95%, dan kelompok di bawah 30 plat ditulis
   "terlalu sedikit".
4. **Pembanding bervonis `BELUM-JELAS`** (kode latih induknya GPL-3.0): hanya pembanding, tidak pernah masuk produk.
5. **Ke Mini PC hanya dibawa** model ONNX berbobot acak atau model publik, plus alat ukur; masukannya buatan. Tidak ada foto
   plat yang keluar dari laptop (`CLAUDE.md` §4). Mini PC menjalankan layanan hidup, jadi pengukuran dijalankan dengan
   `nice -n 19` dan `timeout`, di folder sementara yang dihapus sesudahnya, termasuk bila gagal (Prinsip #3).

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–11 | Bengkel sampai fpo-indo-1 dalam format ONNX | Selesai 13–15 Okt |
| **12 (dokumen ini)** | Penilai deteksi; pembanding siap pakai pada foto utuh; kecepatan tiga calon di laptop dan Mini PC | Ditulis dan dijalankan 16 Okt |
| 13 | Melatih pencari plat sendiri dari jenis yang dipilih owner (paket latih, bobot awal dan izinnya, dinilai dengan `deteksi.py`) | Sesudahnya |
| 14 | Rantai utuh di video riset (cari → potong → baca → gabung per kedatangan) dan kecepatannya | Sesudahnya |
| 15 | Laporan Fase 0A dan keputusan owner. Plat buatan komputer (langkah 4) diputuskan di sini | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8–11. Tambahan:
- **Mini PC:**
  - hanya lewat SSH (`~/.ssh/{kunci-ssh-mini-pc}`, `megatron@{ip-mini-pc}`), hanya di `/tmp/cctvgerbang-ukur`;
  - tidak menyentuh layanan, paket sistem, atau berkas lain;
  - beban dan RAM dicatat sebelum dan sesudah;
  - bila beban sebelum mulai di atas 3, tunggu atau laporkan; jangan memaksa.
- **Set uji plat-lighting dibaca sekali per calon**, sesudah ambang dipilih di validasi.
- Nama berkas bukti memakai tanggal jalan (`2026-10-16` di bawah). Bila dijalankan pada tanggal lain, tanggal itu diganti.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/deteksi.py` (baru) | Penilai pencari plat: label YOLO, IoU, pencocokan, kelompok, ambang dari validasi | 1 |
| `tools/lab/uji/test_deteksi.py` (baru) | Uji penilai (gerbang lab biasa) | 1 |
| `tools/vendor.lock.json` (ubah) | Butir `oim-yolo-v9-t-384-plat` | 2 |
| `tools/lab/pencari_oim.py` (baru) | Pembanding YOLOv9-t-384: `nilai`, `cepat` | 2 |
| `tools/lab/uji/test_pencari_oim.py` (baru) | Uji penolakan berkas yang tidak sama dengan kunci (gerbang lab biasa) | 2 |
| `tools/ukur_onnx_cpu.py` (baru) | Ukur lama model ONNX di CPU, berdiri sendiri | 3 |
| `tools/lab/uji_fpo/test_cpu_sungguhan.py` (baru) | Uji pembanding dengan model sungguhan dan alat ukur berdiri sendiri (di luar gerbang) | 2, 3 |
| `bukti/2026-10-16-*` (baru) | Ringkasan dan laporan | 2, 3, 4, 5 |

---

### Task 1: Penilai pencari plat

**Files:** Create `tools/lab/deteksi.py`, `tools/lab/uji/test_deteksi.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_deteksi.py`:

```python
"""Uji tools/lab/deteksi.py: IoU, label YOLO, pencocokan tebakan dengan kebenaran, kelompok, ambang dari validasi, dan
ringkasan tanpa nama berkas."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deteksi as dt  # noqa: E402


def test_iou():
    assert dt.iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert dt.iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert abs(dt.iou((0, 0, 10, 10), (5, 0, 15, 10)) - 50 / 150) < 1e-9


def test_baca_label_ke_piksel_dan_melewati_baris_bukan_kotak(tmp_path):
    berkas = tmp_path / "a.txt"
    # Pecahan biner (0,25; 0,5) supaya hasilnya tepat tanpa galat pembulatan desimal.
    berkas.write_text("0 0.5 0.5 0.25 0.5\nThis dataset was exported via roboflow.com\n1 2 3\n")

    assert dt.baca_label(berkas, 200, 100) == [(75.0, 25.0, 125.0, 75.0)]


def test_cocokkan_satu_kebenaran_paling_banyak_satu_tebakan():
    kebenaran = [(0, 0, 10, 10)]

    assert dt.cocokkan([(0, 0, 10, 10, 0.9), (1, 1, 10, 10, 0.8)], kebenaran) == ({0}, 1)
    assert dt.cocokkan([(50, 50, 60, 60, 0.9)], kebenaran) == (set(), 1)


def test_cocokkan_mendahulukan_keyakinan_tertinggi():
    kebenaran = [(0, 0, 10, 10), (100, 0, 110, 10)]

    ketemu, palsu = dt.cocokkan([(1, 0, 11, 10, 0.3), (0, 0, 10, 10, 0.9)], kebenaran)

    assert ketemu == {0} and palsu == 1


def gambar(gelap, kebenaran, tebakan, tinggi=1000):
    return {"gelap": gelap, "tinggi": tinggi, "kebenaran": kebenaran, "tebakan": tebakan}


def test_ringkas_per_kelompok_dan_ambang():
    per_gambar = [gambar(False, [(0, 0, 100, 50)], [(0, 0, 100, 50, 0.9)]),
                  gambar(True, [(0, 0, 100, 20)], [(0, 0, 100, 20, 0.4), (500, 500, 600, 550, 0.8)])]

    r = dt.ringkas(per_gambar, 0.5)

    assert (r["semua"]["plat"], r["semua"]["plat_ditemukan"], r["semua"]["kotak_palsu"]) == (2, 1, 1)
    assert (r["gelap"]["plat"], r["gelap"]["plat_ditemukan"]) == (1, 0)
    assert (r["kecil"]["plat"], r["besar"]["plat"]) == (1, 1)
    assert r["semua"]["terlalu_sedikit"] and r["terang"]["gambar"] == 1


def test_pilih_ambang_f1_terbesar_dan_terendah_bila_seri():
    per_gambar = [gambar(False, [(0, 0, 100, 50)], [(0, 0, 100, 50, 0.9), (500, 500, 600, 550, 0.2)])]

    assert dt.pilih_ambang(per_gambar) == 0.25


def test_nilai_ambang_dari_validasi_lalu_uji_tanpa_nama_berkas(tmp_path):
    for sisi in ("valid", "test"):
        (tmp_path / sisi / "images").mkdir(parents=True)
        (tmp_path / sisi / "labels").mkdir(parents=True)
        for i in range(3):
            cv2.imwrite(str(tmp_path / sisi / "images" / f"B{1000 + i}XY_{sisi}.jpg"), np.full((100, 200, 3), 200, np.uint8))
            (tmp_path / sisi / "labels" / f"B{1000 + i}XY_{sisi}.txt").write_text("0 0.5 0.5 0.2 0.2\n")

    def cari(_):
        return [(80, 40, 120, 60, 0.9), (0, 0, 10, 10, 0.2)]

    hasil = dt.nilai(tmp_path, cari)

    assert hasil["ambang"] == 0.25
    assert hasil["uji"]["semua"]["plat_ditemukan"] == hasil["uji"]["semua"]["plat"] == 3
    assert hasil["uji"]["semua"]["kotak_palsu"] == 0
    assert "B100" not in json.dumps(hasil)
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'deteksi'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/deteksi.py`**

```python
"""Penilaian pencari plat (langkah 1, spec 2.1) pada foto utuh berlabel kotak format YOLO (Rencana 12).

- Kebenaran: label YOLO (kelas cx cy w h, ternormalisasi). Baris yang bukan lima angka dilewati (README Roboflow ikut
  berakhiran .txt).
- Cocok: tebakan diurutkan menurut keyakinan; tiap tebakan dipasangkan ke kebenaran yang belum terpakai dengan IoU terbesar,
  minimal IOU_MIN. Kebenaran yang tak terpasangkan = plat terlewat; tebakan yang tak terpasangkan = kotak palsu.
- Ambang keyakinan dipilih pada sisi validasi (F1 terbesar; bila seri, yang terendah, karena plat terlewat berarti gerbang
  tidak membuka), lalu dipakai sekali pada sisi uji.
- Kelompok: gambar terang/gelap (rerata kelabu < AMBANG_GELAP, sama dengan set uji baca huruf) dan plat kecil/besar (tinggi
  kotak < BAGIAN_KECIL x tinggi gambar).
Ringkasan hanya hitungan; nama berkas tidak pernah masuk ringkasan.
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bagi_set_uji import AMBANG_GELAP, SEDIKIT  # noqa: E402
from baca_vlm import wilson  # noqa: E402

IOU_MIN = 0.5
BAGIAN_KECIL = 0.03
CALON_AMBANG = tuple(round(0.05 * i, 2) for i in range(1, 20))
KELOMPOK = ("semua", "terang", "gelap", "kecil", "besar")
AKHIRAN = (".jpg", ".jpeg", ".png")


def baca_label(berkas, lebar, tinggi):
    """Label YOLO -> daftar kotak (x1, y1, x2, y2) dalam piksel."""
    kotak = []
    for baris in Path(berkas).read_text().splitlines():
        bagian = baris.split()
        if len(bagian) != 5:
            continue
        try:
            _, cx, cy, w, h = (float(x) for x in bagian)
        except ValueError:
            continue
        kotak.append(((cx - w / 2) * lebar, (cy - h / 2) * tinggi, (cx + w / 2) * lebar, (cy + h / 2) * tinggi))
    return kotak


def iou(a, b):
    lebar = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    tinggi = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    irisan = lebar * tinggi
    gabung = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - irisan
    return irisan / gabung if gabung > 0 else 0.0


def cocokkan(tebakan, kebenaran, iou_min=IOU_MIN):
    """tebakan: (x1, y1, x2, y2, yakin); kebenaran: (x1, y1, x2, y2). Kembali: (indeks kebenaran yang ditemukan, kotak palsu)."""
    terpakai, palsu = set(), 0
    for t in sorted(tebakan, key=lambda t: -t[4]):
        nilai_iou, i = max(((iou(t[:4], k), i) for i, k in enumerate(kebenaran) if i not in terpakai), default=(0.0, None))
        if i is not None and nilai_iou >= iou_min:
            terpakai.add(i)
        else:
            palsu += 1
    return terpakai, palsu


def ringkas(per_gambar, ambang):
    """per_gambar: daftar {"gelap", "tinggi", "kebenaran", "tebakan"}. Kembali: hitungan per kelompok."""
    hasil = {k: {"plat": 0, "plat_ditemukan": 0, "kotak_palsu": 0, "gambar": 0} for k in KELOMPOK}
    for g in per_gambar:
        ketemu, palsu = cocokkan([t for t in g["tebakan"] if t[4] >= ambang], g["kebenaran"])
        cahaya = "gelap" if g["gelap"] else "terang"
        for k in ("semua", cahaya):
            hasil[k]["gambar"] += 1
            hasil[k]["kotak_palsu"] += palsu
        for i, kotak in enumerate(g["kebenaran"]):
            ukuran = "kecil" if (kotak[3] - kotak[1]) < BAGIAN_KECIL * g["tinggi"] else "besar"
            for k in ("semua", cahaya, ukuran):
                hasil[k]["plat"] += 1
                hasil[k]["plat_ditemukan"] += int(i in ketemu)
    for r in hasil.values():
        rentang = wilson(r["plat_ditemukan"], r["plat"])
        r["rentang_95_ditemukan"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["plat"] < SEDIKIT
    return hasil


def f1(per_gambar, ambang):
    s = ringkas(per_gambar, ambang)["semua"]
    benar, terlewat, palsu = s["plat_ditemukan"], s["plat"] - s["plat_ditemukan"], s["kotak_palsu"]
    return 2 * benar / (2 * benar + palsu + terlewat) if benar else 0.0


def pilih_ambang(per_gambar, calon=CALON_AMBANG):
    """Ambang dengan F1 terbesar pada sisi validasi; bila seri, yang terendah."""
    return max(calon, key=lambda a: (f1(per_gambar, a), -a))


def kumpulkan(folder_sisi, cari):
    """folder_sisi berisi images/ dan labels/ (YOLO Roboflow). cari(gambar_bgr) -> daftar (x1, y1, x2, y2, yakin).
    Kembali: (per_gambar, detik per gambar median, gambar tak terbaca)."""
    per_gambar, detik, tak = [], [], 0
    for berkas in sorted(p for p in (Path(folder_sisi) / "images").iterdir() if p.suffix.lower() in AKHIRAN):
        g = cv2.imread(str(berkas))
        if g is None:
            tak += 1
            continue
        tinggi, lebar = g.shape[:2]
        label = Path(folder_sisi) / "labels" / f"{berkas.stem}.txt"
        mulai = time.perf_counter()
        tebakan = cari(g)
        detik.append(time.perf_counter() - mulai)
        per_gambar.append({"gelap": float(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY).mean()) < AMBANG_GELAP, "tinggi": tinggi,
                           "kebenaran": baca_label(label, lebar, tinggi) if label.exists() else [],
                           "tebakan": [tuple(float(x) for x in t) for t in tebakan]})
    return per_gambar, (round(float(np.median(detik)), 4) if detik else None), tak


def nilai(folder_dataset, cari):
    """Ambang dipilih di valid, lalu dipakai sekali di test. Kembali: ringkasan tanpa nama berkas."""
    val, detik_val, tak_val = kumpulkan(Path(folder_dataset) / "valid", cari)
    ambang = pilih_ambang(val)
    uji, detik_uji, tak_uji = kumpulkan(Path(folder_dataset) / "test", cari)
    return {"ambang": ambang, "iou_min": IOU_MIN, "validasi": ringkas(val, ambang), "uji": ringkas(uji, ambang),
            "detik_per_gambar": {"validasi": detik_val, "uji": detik_uji}, "tak_terbaca": tak_val + tak_uji}
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `177 passed` (170 + 7), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/deteksi.py` dan ujinya, dengan alasan (penilai yang sama untuk semua calon; ambang
dari validasi) dan angka gerbang 170 → 177.

---

### Task 2: Pembanding siap pakai YOLOv9-t-384 pada plat-lighting

**Files:** Modify `tools/vendor.lock.json`; Create `tools/lab/pencari_oim.py`, `tools/lab/uji/test_pencari_oim.py`,
`tools/lab/uji_fpo/test_cpu_sungguhan.py`

- [x] **Step 1: Catat butir di kunci (tanpa SHA, karena GitHub tidak menerbitkan digest untuk aset 2024)**

Berkas sekali pakai `data/alat-sementara/kunci-oim.mjs`:

```js
// Sekali pakai (Rencana 12 Task 2): menambah butir pembanding pencari plat ke kunci. Ukuran dibaca dari API rilis GitHub;
// sha256 kosong dulu (aset 2024 tanpa digest), lalu diisi dari berkas unduhan dengan "isi". Teks disisipkan pada jangkar
// yang harus ketemu TEPAT SEKALI, supaya baris lain di kunci tidak berubah.
// Pakai: node data/alat-sementara/kunci-oim.mjs tambah | node data/alat-sementara/kunci-oim.mjs isi
import fs from 'node:fs';
import crypto from 'node:crypto';

const KUNCI = 'tools/vendor.lock.json';
const NAMA = 'oim-yolo-v9-t-384-plat';
const BERKAS = 'yolo-v9-t-384-license-plates-end2end.onnx';
let teks = fs.readFileSync(KUNCI, 'utf8').replace(/\r\n/g, '\n');
const kunci = JSON.parse(teks);
const tepatSekali = (jangkar) => teks.split(jangkar).length - 1 === 1;
if (process.argv[2] === 'tambah') {
  if (kunci.berkas.some((b) => b.nama === NAMA)) { console.error('butir sudah ada'); process.exit(1); }
  const r = await fetch('https://api.github.com/repos/ankandrew/open-image-models/releases/tags/assets',
    { headers: { 'User-Agent': 'cctvgerbang-baca', Accept: 'application/vnd.github+json' } });
  const aset = (await r.json()).assets.find((a) => a.name === BERKAS);
  if (!aset) { console.error('aset tidak ada di rilis'); process.exit(1); }
  const butir = { nama: NAMA, url: aset.browser_download_url, berkas: BERKAS, maks_gb: 0.05, sha256: '',
    sumber: 'https://github.com/ankandrew/open-image-models/releases/tag/assets', ukuran_byte: aset.size,
    isi_dibaca: `API rilis GitHub assets: ${aset.size} byte, diunggah ${aset.updated_at}, TANPA digest dari GitHub; sha256 diisi dari unduhan pertama (dipercaya pada pemakaian pertama)`,
    peran: 'alat lab: pembanding pencari plat (Rencana 12). BUKAN bagian produk; bobot BELUM-JELAS, kode latih induk GPL-3.0',
    dibaca: new Date().toLocaleDateString('sv-SE') };
  const jangkar = '\n    }\n  ],\n  "_model_hf"';
  if (!tepatSekali(jangkar)) { console.error('jangkar penutup daftar berkas tidak ketemu tepat sekali'); process.exit(1); }
  const isiButir = JSON.stringify(butir, null, 2).split('\n').map((b) => `    ${b}`).join('\n');
  teks = teks.replace(jangkar, () => `\n    },\n${isiButir}\n  ],\n  "_model_hf"`);
} else if (process.argv[2] === 'isi') {
  const b = kunci.berkas.find((x) => x.nama === NAMA);
  const isi = fs.readFileSync(`data/unduhan/${NAMA}/${BERKAS}`);
  if (!b || b.sha256) { console.error('butir tidak ada atau sha256 sudah terisi'); process.exit(1); }
  if (isi.length !== b.ukuran_byte) { console.error(`ukuran ${isi.length} bukan ${b.ukuran_byte}`); process.exit(1); }
  const awal = teks.indexOf(`"nama": "${NAMA}"`);
  const kosong = teks.indexOf('"sha256": ""', awal);
  const berikut = teks.indexOf('"nama": ', awal + 1);
  if (awal < 0 || kosong < 0 || (berikut > 0 && kosong > berikut)) { console.error('sha256 butir tidak ketemu'); process.exit(1); }
  teks = `${teks.slice(0, kosong)}"sha256": "${crypto.createHash('sha256').update(isi).digest('hex')}"${teks.slice(kosong + '"sha256": ""'.length)}`;
} else { console.error('Pakai: tambah | isi'); process.exit(2); }
JSON.parse(teks);
fs.writeFileSync(KUNCI, teks);
console.log(`${process.argv[2]}: ${NAMA}`);
```

Run: `node data/alat-sementara/kunci-oim.mjs tambah; echo "EXIT=$?"` lalu `git diff --stat tools/vendor.lock.json`
Expected: `tambah: oim-yolo-v9-t-384-plat`, `EXIT=0`; diff hanya menambah butir itu.

- [x] **Step 2: Unduh lewat pintu, lalu kunci SHA-256-nya**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\ambil-berkas.ps1 oim-yolo-v9-t-384-plat; "EXIT=$LASTEXITCODE"`
Expected: `TERSIMPAN ...` dengan peringatan belum dikunci, `EXIT=0`.

Run: `node data/alat-sementara/kunci-oim.mjs isi; echo "EXIT=$?"` lalu `npm test; echo "EXIT=$?"`
Expected: `isi: oim-yolo-v9-t-384-plat`, lalu `pass 107`.

- [x] **Step 3: Tulis ujinya**

Buat `tools/lab/uji/test_pencari_oim.py`:

```python
"""Uji tools/lab/pencari_oim.py tanpa model sungguhan: berkas yang tidak sama dengan kunci ditolak sebelum onnxruntime dan
open-image-models dimuat."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pencari_oim as po  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402


def test_berkas_yang_berubah_ditolak_sebelum_memuat_apa_pun(tmp_path):
    folder = tmp_path / "unduhan" / po.BUTIR
    folder.mkdir(parents=True)
    (folder / "model.onnx").write_bytes(b"ditukar")
    kunci = tmp_path / "kunci.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": po.BUTIR, "berkas": "model.onnx",
                                             "sha256": hashlib.sha256(b"asli").hexdigest()}]}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        po.PencariOim(tmp_path / "unduhan", kunci=kunci)
```

Buat `tools/lab/uji_fpo/test_cpu_sungguhan.py`:

```python
"""Uji dengan model sungguhan di image lab tambahan (di luar gerbang biasa): pembanding YOLOv9-t-384 mengembalikan kotak
dengan bentuk yang diharapkan, dan tools/ukur_onnx_cpu.py jalan berdiri sendiri (tanpa impor dari repo).

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
UKUR = AKAR / "tools" / "ukur_onnx_cpu.py"
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import pencari_oim as po  # noqa: E402

ADA_OIM = (UNDUHAN / po.BUTIR).is_dir()


@pytest.mark.skipif(not ADA_OIM, reason="model pembanding belum diunduh (Rencana 12 Task 2)")
def test_pembanding_mengembalikan_kotak_dengan_keyakinan():
    cari = po.PencariOim(UNDUHAN, utas=1)
    gambar = np.full((1080, 1920, 3), 128, np.uint8)

    hasil = cari(gambar)

    assert isinstance(hasil, list)
    assert all(len(t) == 5 and 0.0 <= t[4] <= 1.0 and t[0] <= t[2] and t[1] <= t[3] for t in hasil)


def test_ukur_onnx_cpu_berdiri_sendiri(tmp_path):
    import onnx
    from onnx import TensorProto, helper

    masuk = helper.make_tensor_value_info("input", TensorProto.UINT8, [1, 8])
    keluar = helper.make_tensor_value_info("keluar", TensorProto.FLOAT, [1, 8])
    satu = helper.make_tensor("satu", TensorProto.FLOAT, [1], [1.0])
    graf = helper.make_graph([helper.make_node("Cast", ["input"], ["f"], to=TensorProto.FLOAT),
                              helper.make_node("Add", ["f", "satu"], ["keluar"])], "kecil", [masuk], [keluar], [satu])
    model = helper.make_model(graf, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 8
    onnx.save(model, tmp_path / "kecil.onnx")

    # -I: tanpa folder skrip di sys.path, jadi impor apa pun dari repo pasti gagal.
    hasil = subprocess.run([sys.executable, "-I", str(UKUR), str(tmp_path / "kecil.onnx"), "--keluar", str(tmp_path / "h.json")],
                           capture_output=True, text=True, cwd=tmp_path)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    data = json.loads((tmp_path / "h.json").read_text())
    assert set(data["model"][0]["per_utas"]) == {"1", "2", "4"}
    assert data["model"][0]["per_utas"]["1"]["median_ms"] >= 0 and data["cpu_terlihat"] >= 1
```

- [x] **Step 4: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'pencari_oim'`, `EXIT` bukan 0.

- [x] **Step 5: Tulis `tools/lab/pencari_oim.py`**

```python
"""Pembanding pencari plat siap pakai (Rencana 12): open-image-models @ eaeb588, yolo-v9-t-384-license-plate-end2end (ONNX,
CPU). Bobotnya BELUM-JELAS (docs/VONIS-LISENSI.md; kode latih induknya GPL-3.0): hanya pembanding, tidak masuk produk.

Berkas model diunduh lewat tools/ambil-berkas.ps1 dan diverifikasi SHA-256-nya sebelum onnxruntime dan open-image-models
dimuat. Kode open-image-models dibaca dari klon terkunci di vendor/open-image-models; jalur unduh otomatisnya tidak pernah
dipakai (model diberi lewat jalur berkas). Ambang keyakinan dipilih tools/lab/deteksi.py di validasi, jadi model dijalankan
dengan ambang rendah (AMBANG_MODEL) supaya semua calon kotak ikut dinilai.

  nilai: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_oim.py nilai /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/ringkasan.json
  cepat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_oim.py cepat /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/cepat.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
import deteksi  # noqa: E402
from model_terkunci import LOKASI_KUNCI, ModelDitolak, daftar_berkas, verifikasi_berkas  # noqa: E402

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "open-image-models"
BUTIR = "oim-yolo-v9-t-384-plat"
AMBANG_MODEL = 0.01
UTAS = (1, 2, 4)


class PencariOim:
    """Pencari plat pembanding. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali daftar (x1, y1, x2, y2, yakin)."""

    def __init__(self, folder_unduhan, utas=None, kunci=LOKASI_KUNCI):
        daftar = daftar_berkas(kunci)
        jalur = verifikasi_berkas(Path(folder_unduhan) / BUTIR / daftar.get(BUTIR, ("?", ""))[0], BUTIR, daftar)
        if str(VENDOR) not in sys.path:
            sys.path.insert(0, str(VENDOR))
        import onnxruntime as ort
        from open_image_models.detection.factory import create_detector

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self._d = create_detector(jalur, backend="yolo_v9", class_labels=["license_plate"], conf_thresh=AMBANG_MODEL,
                                  providers=["CPUExecutionProvider"], sess_options=opsi)

    def __call__(self, gambar_bgr):
        return [(d.bounding_box.x1, d.bounding_box.y1, d.bounding_box.x2, d.bounding_box.y2, float(d.confidence))
                for d in self._d.predict(gambar_bgr)]


def cepat(folder_dataset, folder_unduhan, utas=UTAS, jumlah=60, panaskan=5):
    """Milidetik per foto utuh (praproses + model + pascaproses) di CPU, pada foto validasi."""
    berkas = sorted(p for p in (Path(folder_dataset) / "valid" / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN)
    gambar = [g for g in (cv2.imread(str(b)) for b in berkas[:jumlah]) if g is not None]
    hasil = {"gambar": len(gambar), "panaskan": panaskan, "per_utas": {}}
    for u in utas:
        cari = PencariOim(folder_unduhan, utas=u)
        lama = []
        for i, g in enumerate(gambar):
            mulai = time.perf_counter()
            cari(g)
            if i >= panaskan:
                lama.append(1000 * (time.perf_counter() - mulai))
        hasil["per_utas"][str(u)] = {"median_ms": round(float(np.median(lama)), 1),
                                     "p95_ms": round(float(np.percentile(lama, 95)), 1)}
    return hasil


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Pembanding pencari plat YOLOv9-t-384 (Rencana 12).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    for nama in ("nilai", "cepat"):
        p = perintah.add_parser(nama)
        for a in ("folder_dataset", "folder_unduhan", "keluar"):
            p.add_argument(a)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "nilai":
            hasil = deteksi.nilai(p.folder_dataset, PencariOim(p.folder_unduhan))
            for k, r in hasil["uji"].items():
                print(f"uji {k:<7} plat ditemukan {r['plat_ditemukan']} dari {r['plat']} (rentang 95% "
                      f"{r['rentang_95_ditemukan']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}); kotak palsu "
                      f"{r['kotak_palsu']}; gambar {r['gambar']}")
            print(f"ambang dari validasi {hasil['ambang']}; detik per gambar {hasil['detik_per_gambar']}; tak terbaca "
                  f"{hasil['tak_terbaca']}")
        else:
            hasil = cepat(p.folder_dataset, p.folder_unduhan)
            for u, x in hasil["per_utas"].items():
                print(f"utas {u}: median {x['median_ms']} ms (p95 {x['p95_ms']}) per foto utuh; gambar {hasil['gambar']}")
        Path(p.keluar).parent.mkdir(parents=True, exist_ok=True)
        Path(p.keluar).write_text(json.dumps(hasil, indent=1))
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

`LOKASI_KUNCI` adalah bawaan `daftar_berkas(lokasi=LOKASI_KUNCI)` di `model_terkunci.py` (diperiksa saat rencana ditulis).

- [x] **Step 6: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `178 passed`, `EXIT=0`.

- [x] **Step 7: Nilai pembanding (valid lalu uji sekali) dan kecepatannya di CPU laptop**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/pencari_oim.py nilai /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/ringkasan.json; "EXIT=$LASTEXITCODE"`
Expected: lima baris `uji semua/terang/gelap/kecil/besar ...`, lalu ambang dan detik per gambar; `EXIT=0`.

Run (PowerShell, mesin tenang): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/pencari_oim.py cepat /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/cepat.json; "EXIT=$LASTEXITCODE"`
Expected: tiga baris `utas 1/2/4: median ... ms`, `EXIT=0`.

- [x] **Step 8: Commit** kunci, `pencari_oim.py`, dan kedua berkas uji, dengan alasan (pembanding ringan, hanya pembanding),
SHA-256 dari unduhan pertama (batas: tanpa digest GitHub), gerbang 177 → 178, dan angka pembanding.

---

### Task 3: Kecepatan tiga calon dan dua model siap pakai di CPU laptop

**Files:** Create `tools/ukur_onnx_cpu.py`, `data/alat-sementara/ekspor-calon-acak.py` (sekali pakai)

- [x] **Step 1: Jalankan uji alat ukur, pastikan merah**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_cpu_sungguhan.py -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `1 failed, 1 passed` (`test_ukur_onnx_cpu_berdiri_sendiri`: skrip tidak ada), `EXIT=1`.

- [x] **Step 2: Tulis `tools/ukur_onnx_cpu.py`**

```python
"""Lama satu panggilan model ONNX di CPU dengan masukan buatan (tanpa data), untuk 1, 2, dan 4 utas (Rencana 12, K29).

Hanya memakai numpy dan onnxruntime, dan tidak mengimpor apa pun dari repo, supaya bisa dijalankan apa adanya di Mini PC.
Tiap model: PANASKAN panggilan pemanasan, lalu ULANG panggilan diukur. Beban mesin (loadavg) dicatat sebelum dan sesudah.

  python ukur_onnx_cpu.py <berkas.onnx> [<berkas.onnx> ...] --keluar hasil.json
"""
import argparse
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort

UTAS = (1, 2, 4)
ULANG = 20
PANASKAN = 5
JENIS = {"tensor(uint8)": np.uint8, "tensor(float)": np.float32, "tensor(int64)": np.int64}


def masukan_buatan(sesi, rng):
    hasil = {}
    for m in sesi.get_inputs():
        bentuk = [d if isinstance(d, int) and d > 0 else 1 for d in m.shape]
        jenis = JENIS.get(m.type)
        if jenis is None:
            raise ValueError(f"tipe masukan {m.type} belum didukung")
        hasil[m.name] = (rng.integers(0, 256, bentuk).astype(jenis) if jenis is np.uint8
                         else rng.integers(0, 2, bentuk).astype(jenis) if jenis is np.int64
                         else rng.random(bentuk).astype(jenis))
    return hasil


def ukur(berkas, utas, ulang=ULANG, panaskan=PANASKAN):
    opsi = ort.SessionOptions()
    opsi.intra_op_num_threads = utas
    opsi.inter_op_num_threads = 1
    sesi = ort.InferenceSession(str(berkas), opsi, providers=["CPUExecutionProvider"])
    x = masukan_buatan(sesi, np.random.default_rng(0))
    for _ in range(panaskan):
        sesi.run(None, x)
    lama = []
    for _ in range(ulang):
        mulai = time.perf_counter()
        sesi.run(None, x)
        lama.append(1000 * (time.perf_counter() - mulai))
    return {"median_ms": round(float(np.median(lama)), 1), "p95_ms": round(float(np.percentile(lama, 95)), 1), "ulang": ulang}


def cpu():
    try:
        with open("/proc/cpuinfo") as berkas:
            for baris in berkas:
                if baris.startswith("model name"):
                    return baris.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def beban():
    return [round(x, 2) for x in os.getloadavg()] if hasattr(os, "getloadavg") else None


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Lama model ONNX di CPU dengan masukan buatan.")
    urai.add_argument("berkas", nargs="+")
    urai.add_argument("--keluar", required=True)
    p = urai.parse_args(argumen)
    hasil = {"cpu": cpu(), "cpu_terlihat": os.cpu_count(), "onnxruntime": ort.__version__, "beban_sebelum": beban(),
             "model": []}
    for b in p.berkas:
        per_utas = {str(u): ukur(b, u) for u in UTAS}
        hasil["model"].append({"berkas": Path(b).name, "ukuran_byte": Path(b).stat().st_size, "per_utas": per_utas})
        print(f"{Path(b).name}: " + "; ".join(f"utas {u} median {x['median_ms']} ms (p95 {x['p95_ms']})" for u, x in per_utas.items()))
    hasil["beban_sesudah"] = beban()
    Path(p.keluar).write_text(json.dumps(hasil, indent=1))
    print(f"cpu {hasil['cpu']}; terlihat {hasil['cpu_terlihat']}; beban {hasil['beban_sebelum']} -> {hasil['beban_sesudah']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(utama())
```

- [x] **Step 3: Jalankan, pastikan hijau**

Run (PowerShell): sama dengan Step 1.
Expected: `2 passed`, `EXIT=0`. Lalu seluruh folder: `... -m pytest /kerja/tools/lab/uji_fpo ...`, Expected `14 passed`.

- [x] **Step 4: Ekspor tiga calon berbobot acak**

Berkas sekali pakai `data/alat-sementara/ekspor-calon-acak.py`:

```python
"""Sekali pakai (Rencana 12 Task 3): ONNX berbobot acak untuk mengukur kecepatan tiga calon pencari plat buatan sendiri.
Bobot acak cukup karena kecepatan ditentukan susunan model. Tanpa data plat dan tanpa jaringan. YOLOX dibangun dari klon
vendor/yolox (Apache-2.0); loguru dan thop yang tidak ada di image diganti tiruan karena tidak dipakai saat menghitung.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/data/alat-sementara/ekspor-calon-acak.py /kerja/data/keluaran/cepat-calon
"""
import importlib.machinery
import logging
import shutil
import sys
import types
from pathlib import Path

sys.path.insert(0, "/kerja/vendor/yolox")
sys.path.insert(0, "/kerja/tools/lab")
from baca_vlm import matikan_kernel_triton  # noqa: E402

matikan_kernel_triton()
import torch  # noqa: E402


def tiruan(nama, **isi):
    m = types.ModuleType(nama)
    m.__spec__ = importlib.machinery.ModuleSpec(nama, None)
    m.__dict__.update(isi)
    sys.modules.setdefault(nama, m)


def tidak_dipakai(*a, **k):
    raise NotImplementedError("tiruan untuk pengukuran kecepatan")


tiruan("loguru", logger=logging.getLogger("yolox"))
tiruan("thop", profile=tidak_dipakai)
from yolox.models import YOLOPAFPN, YOLOX, YOLOXHead  # noqa: E402
from rfdetr import RFDETRNano  # noqa: E402

keluar = Path(sys.argv[1])
keluar.mkdir(parents=True, exist_ok=True)
torch.manual_seed(0)
for nama, lebar in (("nano", 0.25), ("tiny", 0.375)):
    model = YOLOX(YOLOPAFPN(0.33, lebar, in_channels=[256, 512, 1024], depthwise=(nama == "nano")),
                  YOLOXHead(1, lebar, in_channels=[256, 512, 1024], depthwise=(nama == "nano"))).eval()
    torch.onnx.export(model, torch.zeros(1, 3, 416, 416), str(keluar / f"acak-yolox-{nama}-416.onnx"),
                      input_names=["images"], output_names=["output"], opset_version=17, dynamo=False)
hasil = RFDETRNano(pretrain_weights=None).export(output_dir=str(keluar / "rfdetr"), format="onnx", verbose=False)
shutil.move(str(hasil), str(keluar / "acak-rfdetr-nano-384.onnx"))
shutil.rmtree(keluar / "rfdetr", ignore_errors=True)
for b in sorted(keluar.glob("*.onnx")):
    print(f"{b.name}: {b.stat().st_size} byte")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/data/alat-sementara/ekspor-calon-acak.py /kerja/data/keluaran/cepat-calon; "EXIT=$LASTEXITCODE"`
Expected: tiga berkas `acak-yolox-nano-416.onnx` (sekitar 3,7 MB), `acak-yolox-tiny-416.onnx` (sekitar 20 MB),
`acak-rfdetr-nano-384.onnx` (sekitar 107 MB); `EXIT=0`.

- [x] **Step 5: Ukur lima model di CPU laptop dengan alat yang sama (mesin tenang)**

Lima model: tiga calon acak, pembanding YOLOv9-t-384, dan pembaca huruf terbitan `cct_s_v2_global.onnx` (susunannya sama
dengan fpo-indo-1, jadi kecepatannya sama).

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/ukur_onnx_cpu.py /kerja/data/keluaran/cepat-calon/acak-yolox-nano-416.onnx /kerja/data/keluaran/cepat-calon/acak-yolox-tiny-416.onnx /kerja/data/keluaran/cepat-calon/acak-rfdetr-nano-384.onnx /kerja/data/unduhan/oim-yolo-v9-t-384-plat/yolo-v9-t-384-license-plates-end2end.onnx /kerja/data/unduhan/fpo-cct-s-v2-onnx/cct_s_v2_global.onnx --keluar /kerja/data/keluaran/cepat-calon/laptop.json; "EXIT=$LASTEXITCODE"`
Expected: lima baris model dengan median per utas, lalu baris CPU dan beban; `EXIT=0`. YOLOX dan RF-DETR kira-kira sama
dengan pengukuran sebelum rencana (YOLOX-Nano sekitar 12 / 7 / 5 ms; RF-DETR Nano sekitar 265 / 141 / 89 ms). Bila jauh
berbeda, catat dan cari sebabnya sebelum lanjut.

- [x] **Step 6: Commit** `tools/ukur_onnx_cpu.py`, dengan alasan (alat ukur berdiri sendiri untuk Mini PC) dan angka uji
image tambahan 12 → 14.

---

### Task 4: Kecepatan di Mini PC (server fase awal, K29)

**Files:** Create `data/alat-sementara/minipc/` (sekali pakai): `requirements.txt`, `jalan.sh`

- [x] **Step 1: Daftar paket ber-hash untuk Mini PC (Python 3.12, Linux x86_64) dan pemeriksaan celah**

Run (Git Bash; folder sementara sesi sebagai `$D`):

```bash
mkdir -p data/alat-sementara/minipc
printf "onnxruntime==1.30.0\nnumpy==2.5.3\n" > "$D/masukan-minipc.txt"
"$HOME/.local/bin/uv.exe" pip compile "$D/masukan-minipc.txt" --python-version 3.12 --python-platform x86_64-manylinux_2_28 \
  --only-binary :all: --generate-hashes --no-header --no-annotate -o data/alat-sementara/minipc/requirements.txt; echo "EXIT=$?"
```

Expected: `EXIT=0`. Bila `onnxruntime==1.30.0` tidak punya wheel CPU untuk Linux cp312, pakai versi terbaru yang ada dan
catat.

Lalu periksa celahnya ke OSV dengan berkas sekali pakai `data/alat-sementara/audit-osv.mjs`. Skrip ini membaca daftar
`nama==versi` langsung dari `requirements.txt` (membuang ` \` di ujung baris, penyebab alat ukur keliru di Rencana 9), dan
memeriksa kontrol positif lebih dulu:

```js
// Sekali pakai: celah tercatat di OSV untuk tiap paket di requirements.txt ber-hash. Kontrol positif lebih dulu
// (keras==3.12.1 punya celah tercatat); bila kontrol tidak menemukan apa pun, alat ukurnya rusak dan skrip berhenti.
// Pakai: node data/alat-sementara/audit-osv.mjs <requirements.txt>
import fs from 'node:fs';

const tanya = async (name, version) => {
  const r = await fetch('https://api.osv.dev/v1/query', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ package: { name, ecosystem: 'PyPI' }, version }) });
  return ((await r.json()).vulns || []).map((v) => v.id);
};
const kontrol = await tanya('keras', '3.12.1');
console.log(`kontrol positif keras==3.12.1: ${kontrol.length} celah`);
if (kontrol.length === 0) process.exit(1);
const paket = fs.readFileSync(process.argv[2], 'utf8').split(/\r?\n/).filter((b) => /^[A-Za-z0-9]/.test(b))
  .map((b) => b.replace(/\s*\\\s*$/, '').trim()).map((b) => b.split('=='));
let celah = 0;
for (const [nama, versi] of paket) {
  if (!/^[0-9][0-9A-Za-z.+-]*$/.test(versi || '')) { console.log(`${nama}: versi tak terbaca "${versi}"`); celah += 1; continue; }
  const id = await tanya(nama, versi);
  celah += id.length;
  console.log(`${nama}==${versi}: ${id.length ? id.join(', ') : 'tidak ada celah tercatat'}`);
}
console.log(`jumlah celah atau gagal periksa: ${celah}`);
process.exit(celah ? 1 : 0);
```

Run: `node data/alat-sementara/audit-osv.mjs data/alat-sementara/minipc/requirements.txt; echo "EXIT=$?"`
Expected: kontrol positif lebih dari 0 celah; tiap paket `tidak ada celah tercatat`; `jumlah celah atau gagal periksa: 0`;
`EXIT=0`. Bila ada celah, **berhenti** dan laporkan (paket, ID celah, versi yang menutupnya).

- [x] **Step 2: Skrip yang dijalankan di Mini PC**

`data/alat-sementara/minipc/jalan.sh`:

```bash
#!/usr/bin/env bash
# Sekali pakai (Rencana 12 Task 4), dijalankan DI Mini PC dari /tmp/cctvgerbang-ukur: venv sementara, onnxruntime ber-hash,
# ukur dengan prioritas terendah, lalu venv dihapus walau gagal (trap). Hanya model ONNX publik atau berbobot acak dan
# masukan buatan; tidak ada data plat.
set -euo pipefail
D=/tmp/cctvgerbang-ukur
trap 'rm -rf "$D/venv"' EXIT
echo "sebelum: beban $(cut -d' ' -f1-3 /proc/loadavg); RAM tersedia $(free -m | awk '/^Mem:/{print $7}') MiB"
python3 -m venv "$D/venv"
"$D/venv/bin/pip" install --quiet --require-hashes --no-deps --only-binary :all: -r "$D/requirements.txt"
nice -n 19 timeout 900 "$D/venv/bin/python" -I "$D/ukur_onnx_cpu.py" "$D"/*.onnx --keluar "$D/hasil.json"
echo "sesudah: beban $(cut -d' ' -f1-3 /proc/loadavg); RAM tersedia $(free -m | awk '/^Mem:/{print $7}') MiB"
```

- [x] **Step 3: Periksa Mini PC, kirim, jalankan, ambil hasil, bersihkan**

Run (Git Bash), satu per satu:

```bash
M="ssh -i $HOME/.ssh/{kunci-ssh-mini-pc} -o ConnectTimeout=15 -o BatchMode=yes megatron@{ip-mini-pc}"
$M 'cat /proc/loadavg; free -m | head -2; test ! -e /tmp/cctvgerbang-ukur && echo kosong'
```

Expected: beban satu menit di bawah 3; `kosong`. Bila beban 3 atau lebih, tunggu dan ulangi; jangan memaksa.

```bash
$M 'mkdir /tmp/cctvgerbang-ukur'
scp -i $HOME/.ssh/{kunci-ssh-mini-pc} tools/ukur_onnx_cpu.py data/alat-sementara/minipc/requirements.txt data/alat-sementara/minipc/jalan.sh \
  data/keluaran/cepat-calon/acak-yolox-nano-416.onnx data/keluaran/cepat-calon/acak-yolox-tiny-416.onnx \
  data/keluaran/cepat-calon/acak-rfdetr-nano-384.onnx data/unduhan/oim-yolo-v9-t-384-plat/yolo-v9-t-384-license-plates-end2end.onnx \
  data/unduhan/fpo-cct-s-v2-onnx/cct_s_v2_global.onnx megatron@{ip-mini-pc}:/tmp/cctvgerbang-ukur/
$M 'bash /tmp/cctvgerbang-ukur/jalan.sh'; echo "EXIT=$?"
scp -i $HOME/.ssh/{kunci-ssh-mini-pc} megatron@{ip-mini-pc}:/tmp/cctvgerbang-ukur/hasil.json data/keluaran/cepat-calon/minipc.json
$M 'rm -rf /tmp/cctvgerbang-ukur; test ! -e /tmp/cctvgerbang-ukur && echo bersih; pgrep -f ukur_onnx_cpu || echo "tanpa sisa proses"'
```

Expected: baris beban dan RAM sebelum dan sesudah; lima baris model dengan median per utas; `EXIT=0`; `bersih`;
`tanpa sisa proses`. Bila `jalan.sh` gagal, tetap jalankan perintah pembersihan terakhir dan laporkan galatnya.

- [x] **Step 4: Salin ringkasan ke `bukti/` sesudah diperiksa tanpa nomor plat (dengan kontrol positif)**

Buat `data/alat-sementara/periksa-bukti-12.py`:

```python
"""Sekali pakai (Rencana 12): menyalin ringkasan ke bukti-siap/ hanya bila tak satu pun teks plat atau nama berkas ada di
dalamnya. Larangan: teks plat dan nama berkas dari kedua pembagian-koreksi.json dan kedua curiga.json (sama dengan Rencana
10 dan 11), ditambah stem nama berkas gambar plat-lighting. Kontrol positif lebih dulu: daftar stem plat-lighting ditulis
ke berkas sementara lalu diperiksa; bila tidak ditemukan apa pun, berhenti. Hanya hitungan yang dicetak.
Pakai: python periksa-bukti-12.py <tanggal-jalan>
"""
import json
import shutil
import sys
from pathlib import Path

K = Path("/kerja/data/keluaran")
tanggal = sys.argv[1]
larangan = set()
for berkas in ("set-uji-koreksi/pembagian-koreksi.json", "latih-koreksi/pembagian-koreksi.json"):
    p = json.loads((K / berkas).read_text())
    larangan |= {a["teks"] for s in p.values() for a in s}
    larangan |= {Path(b).stem for s in p.values() for a in s for b in a["berkas"]}
for berkas in ("label-curiga/curiga.json", "label-curiga-latih/curiga.json"):
    larangan |= {c["usulan"] for c in json.loads((K / berkas).read_text())}
stem = {b.stem for b in (K / "dataset/plat-lighting").rglob("*") if b.suffix.lower() in (".jpg", ".jpeg", ".png")}
larangan |= stem


def temuan(teks):
    return sum(1 for t in larangan if t in teks)


sementara = K / "bukti-siap" / "kontrol-12.tmp"
sementara.write_text("\n".join(sorted(stem)))
kontrol = temuan(sementara.read_text())
sementara.unlink()
print(f"ukuran daftar larangan: {len(larangan)}; kontrol positif (stem plat-lighting): {kontrol} ditemukan")
if kontrol == 0:
    sys.exit(1)
for asal, tujuan in [("pencari-oim/ringkasan.json", "pencari-oim.json"), ("pencari-oim/cepat.json", "pencari-oim-cepat.json"),
                     ("cepat-calon/laptop.json", "cepat-calon-laptop.json"), ("cepat-calon/minipc.json", "cepat-calon-minipc.json")]:
    n = temuan((K / asal).read_text())
    print(f"{tujuan}: {n} teks plat atau nama berkas ditemukan")
    if n:
        sys.exit(1)
    shutil.copy(K / asal, K / "bukti-siap" / f"{tanggal}-{tujuan}")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/periksa-bukti-12.py 2026-10-16; "EXIT=$LASTEXITCODE"`
Expected: kontrol positif lebih dari 0; keempat berkas `0 teks plat atau nama berkas ditemukan`; `EXIT=0`. Lalu salin
keempatnya dari `data/keluaran/bukti-siap/` ke `bukti/`.

- [x] **Step 5: Commit** keempat berkas bukti, dengan angka per model per utas di laptop dan Mini PC, beban dan RAM Mini PC
sebelum dan sesudah, dan bukti pembersihan.

---

### Task 5: Laporan, catatan, dan pertanyaan ke owner

- [x] **Step 1: Tulis laporan `bukti/2026-10-16-pencari-plat-ukur.md`**

Isinya:
- **Pembanding siap pakai pada plat-lighting uji:** plat ditemukan, kotak palsu, kelompok terang/gelap dan kecil/besar,
  rentang 95%, dan ambang dari validasi.
- **Tabel kecepatan:** lima model × 1/2/4 utas, laptop vs Mini PC.
- **Taksiran per kedatangan di Mini PC:** cari plat + baca huruf, untuk satu dan tiga foto, dibandingkan dengan sasaran dua
  detik (spec 2.6).
- **Biaya rantai pasok tiap calon untuk dilatih:**
  - YOLOX: 3 paket;
  - RF-DETR: sekitar 12 paket, termasuk 1 pra-rilis.
- **Izin bobot awal tiap calon:**
  - YOLOX COCO: `BELUM-JELAS`;
  - RF-DETR N: izin bobot Apache 2.0, bahan COCO;
  - menurut bacaan K21 untuk P13.
- **Batas:**
  - 84 foto uji;
  - satu dataset, sebagian besar bingkai video 1080p;
  - masukan buatan untuk kecepatan;
  - Mini PC menjalankan layanan lain;
  - pembanding `BELUM-JELAS`.

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 12 dijalankan" dicentang dengan angka;
  - butir berikutnya "Owner memilih jenis pencari plat yang dilatih (Rencana 13)";
  - status dan changelog.
- `CLAUDE.md` §7:
  - `tools/ukur_onnx_cpu.py` untuk mesin lain;
  - aturan Mini PC (hanya `/tmp/cctvgerbang-ukur`, `nice`, bersihkan, tanpa data plat).
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 12" (B5).
- `data-asal/bahan.json`: catatan pemakaian plat-lighting.
- Rencana ini: kotak dicentang dan catatan pelaksanaan.

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `178 passed`.

- [x] **Step 4: BERHENTI. Laporkan ke owner**

Ringkas dalam bahasa sederhana. Lalu **satu** pertanyaan pilihan ganda dengan saran di depan, sesuai angka Mini PC: jenis
pencari plat mana yang dilatih di Rencana 13. Pilihannya YOLOX-Nano, YOLOX-Tiny, atau RF-DETR Nano. Untuk tiap pilihan
disebutkan:
- kecepatan di Mini PC;
- jumlah paket baru;
- izin bobot awal;
- akibatnya.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K28, K29, spec 2.3, 2.6, dan 8.1 langkah 7–8:**
  - penilai yang sama untuk semua calon (Task 1);
  - pembanding pada foto utuh (Task 2);
  - kecepatan calon ringan dan berat di laptop (Task 3) dan di server fase awal (Task 4);
  - pilihan jenis yang dilatih diserahkan ke owner dengan angka (Task 5).
- **Set uji tidak bocor:** ambang dipilih di validasi; uji dibaca sekali.
- **Data pribadi:**
  - ringkasan tanpa nama berkas (diuji);
  - ke Mini PC hanya model publik atau berbobot acak dan masukan buatan;
  - bukti diperiksa dengan kontrol positif.
- **Rantai pasok:**
  - pembanding terkunci SHA-256 (dipercaya pada pemakaian pertama karena tanpa digest, dicatat sebagai batas);
  - paket Mini PC ber-hash dan diperiksa OSV dengan kontrol positif;
  - tidak ada paket baru di image lab.
- **Mesin (Prinsip #3):** Mini PC dengan `nice`, `timeout`, folder sementara, `trap`, pemeriksaan sisa proses, beban dan RAM
  sebelum dan sesudah.
- **Angka gerbang:** Node 107 tetap; lab 170 → 177 → 178; uji image tambahan 12 → 14.
- **Nama konsisten:**
  - `baca_label`, `iou`, `cocokkan`, `ringkas`, `f1`, `pilih_ambang`, `kumpulkan`, `nilai`;
  - `PencariOim`, `BUTIR`, `cepat`;
  - `ukur`, `masukan_buatan`;
  - kunci ringkasan `plat`, `plat_ditemukan`, `kotak_palsu`, `rentang_95_ditemukan`, `terlalu_sedikit`.

## Catatan pelaksanaan (16 Okt 2026)

Dijalankan atas lampu hijau owner ("a"), termasuk mengukur di Mini PC. Commit: `9bb02d7` (Task 1), `d5cef2f` (Task 2),
`cce6c65` (Task 3), `65c0410` (Task 4), dan commit laporan dan catatan (Task 5).

| Task | Hasil | Menyimpang dari rencana |
|---|---|---|
| 1 | Merah dulu (modul belum ada); lab 170 → 177 | — |
| 2 | Kunci: hanya butir baru bertambah; SHA-256 dari unduhan pertama sama dengan cetakan pintu. Merah dulu; lab 178. Pembanding: 31/102 plat, ambang 0,35; 28,6 / 17,8 / 12,6 ms per foto utuh di laptop | Angka 30% diperiksa dengan skrip sekali pakai sebelum diterima (koordinat pas; plat yang terlewat kira-kira separuh tinggi yang ditemukan). Perkiraan piksel di skrip itu memakai skala tinggi foto, padahal letterbox 1920×1080 mengikuti lebar; perbandingan separuhnya tetap |
| 3 | Merah dulu (skrip belum ada); uji image tambahan 14; lima model di laptop konsisten dengan ukuran sebelum rencana | — |
| 4 | 5 paket ber-hash, OSV 0 (kontrol 19); ukur di Mini PC; folder dihapus; tanpa sisa proses | Pemeriksaan proses pertama menangkap shell SSH sendiri; diulang dengan pola aman. YOLOX-Nano 4 utas lebih lambat daripada 2 utas karena berebut CPU dengan layanan Mini |
| 5 | Laporan `bukti/2026-10-16-pencari-plat-ukur.md`, catatan, gerbang Node 107 dan lab 178 | — |

**Untuk Rencana 13:** ukuran masukan harus dipilih dengan validasi (plat kecil hilang pada 384 px); kecocokan kode YOLOX
@ 4197784 untuk melatih dengan numpy 2.5 dan torch 2.14 harus dibuktikan sebelum paket dikunci.
