# Fase 0A, Rencana 14: Rantai utuh di video riset dan lembar untuk owner (K31, K32) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Rantai baca plat dijalankan utuh untuk pertama kalinya pada 30 video riset (17 bersudut gerbang, 13 kamera diam
lain): cari plat dengan YOLOX-Nano-640 (K31), potong, baca dengan fpo-indo-1 (ONNX), cek pola plat Indonesia, lalu gabung
menjadi satu bacaan per kedatangan dengan status "yakin" atau "ragu". Owner memeriksa satu lembar (K32), dan dari jawabannya
terukur berapa kedatangan yang terbaca benar dan yakin, per kelompok. Kecepatan rantai per gambar dan waktu sampai bacaan
yakin juga diukur.

**Architecture:**
- **`tools/lab/rantai.py`**: bagian yang kelak jalan di server. Isinya hanya numpy dan cv2; model disuntikkan sebagai fungsi
  `cari` dan `baca`, jadi semua logikanya teruji tanpa model.
  - Sampel 5 gambar per detik.
  - Kotak di bawah ambang validasi pencari dibuang. Ambangnya dibaca dari `mesin.json`, tidak disalin.
  - Potongan diperlebar 5% di tiap sisi.
  - Pelacak IoU antargambar sampel.
  - Gabung: hanya bacaan yang sesuai pola dihitung, lalu suara terbanyak. Status yakin bila didukung minimal 2 bacaan dan
    minimal 60% bacaan sah.
  - Detik sampai yakin.
  - Baris perintah `jalan` merangkai `PencariYolox` dan `PembacaOnnxMesin`.
- **`tools/lab/lembar_rantai.py`**: lembar PNG untuk owner, memakai ulang `baris` dari `lembar_contoh.py`. Penilaian dihitung
  dari nomor baris per jenis jawaban: salah, tak terbaca, bukan plat, motor.
- **`tools/lab/onnx_fpo.py`**: `PembacaOnnxMesin.dengan_yakin`, yaitu bacaan ditambah peluang terendah di semua slot.

**Tech Stack:** Python di image lab (numpy, cv2, onnxruntime) dan image tambahan (`lab.ps1 -Fpo`, karena pembaca fpo-indo-1
memakai `LicensePlateRecognizer` dari klon fast-plate-ocr), PowerShell, Node.

**Dasar:** K15, K19, K31, K32 (`SEED.md` §3); laporan Rencana 13 (`bukti/2026-10-16-pencari-plat-yolox.md`); spec 2.1 (lima
langkah), 2.2, 2.5, 2.6, 8.3 (arti kedatangan pada video luar, angka bersama jumlahnya, kelompok kurang dari 30); `CLAUDE.md`
§3 (ragu = tidak membuka), §4, §7.

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Video riset yang dipakai | 17 bersudut gerbang (4.176 detik; 3.451 di antaranya satu video 640×360; semuanya kategori siang) dan 13 kamera diam lain (2.590 detik; dua malam, dua tak jelas). Resolusi 480×360 sampai 1920×1080, 25–60 fps. Pada 5 gambar per detik: 33.830 gambar sampel | `data-asal/video-riset.json` (objek dengan daftar `video`) dan `data/video/riset/*.info.json` |
| Membuka video di image tambahan | 30 dari 30 terbuka dengan jumlah gambar > 0; isinya tidak dibaca | `data/alat-sementara/ukur-rantai-14.py` |
| Video buatan untuk uji | `cv2.VideoWriter` MJPG (`.avi`) dan mp4v menulis 12 gambar dan membaca kembali 12 | sama |
| Keyakinan pembaca | `run_one(..., return_confidence=True)` memberi `char_probs` berbentuk (10,): peluang terbesar per slot, **termasuk slot bantalan `_`**; bacaannya sama dengan `PembacaOnnxMesin.__call__` | sama; `vendor/fast-plate-ocr/fast_plate_ocr/core/process.py` baris 265–267 |
| Pencari di image tambahan | `PencariYolox` nano-640 jalan; `ambang_validasi` di `mesin.json` 0,25 | sama |
| Alat yang dipakai ulang | `plat.urai` (pola plat, langkah 4); `deteksi.iou`; `baca_vlm.wilson`; `bagi_set_uji.SEDIKIT` (30); `lembar_contoh.baris` dan `PER_LEMBAR` | `tools/lab/` |
| Kode rencana ini | Keenam blok Python lolos kompilasi; ke-13 uji gerbang biasa (Task 1 dan 2) lulus pada salinan sementara sebelum rencana di-commit. Uji model sungguhan (Task 3) belum, karena butuh `dengan_yakin` di repo. Saat dijalankan, uji tetap harus terlihat merah dulu di repo | `data/alat-sementara/cek-r14.mjs` (salinan dihapus sesudahnya) |

Akibatnya bagi rencana ini:

1. **Rantai dijalankan di image tambahan** (`lab.ps1 -Fpo`). Logika rantai dan lembar diuji di gerbang biasa dengan model
   tiruan. Rantai dengan model sungguhan diuji di `tools/lab/uji_fpo/`.
2. **Langkah 2 (meluruskan) belum ada:** potongan dibaca apa adanya, seperti saat fpo-indo-1 dinilai. Ini ditulis sebagai batas.
3. **Ambang rantai ditetapkan sekarang dan tidak disetel dengan jawaban owner**, supaya angka dari lembar tidak bocor menjadi
   pilihan. Ambang itu: sampel 5 per detik; IoU ikut 0,3; jeda 1 detik; minimal terlihat 2 kali; yakin bila didukung minimal 2
   bacaan dan minimal 60% bacaan sah.
4. **Tanpa Mini PC.** Model hasil latih dan video riset tidak dibawa ke sana (K15). Kecepatan Mini PC ditaksir dari angka model
   yang sudah diukur di sana (Rencana 12, 13) ditambah dekode laptop dikali 8–10, dan ditulis sebagai taksiran.
5. **Data pribadi:** `kedatangan.jsonl`, `potongan/`, dan lembar memuat plat. Semuanya tinggal di `data/` dan agen tidak
   membukanya. `ringkasan.json` dan `nilai.json` hanya berisi hitungan, tanpa nama berkas video. Bukti diperiksa dengan daftar
   larangan yang **ditambah bacaan rantai itu sendiri**, dengan kontrol positif.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–13 | Bengkel sampai pencari plat buatan sendiri | Selesai 13–16 Okt |
| **14 (dokumen ini)** | Rantai utuh di video riset, lembar untuk owner, kecepatan | Ditulis |
| 15 | Laporan Fase 0A dan keputusan owner; plat buatan komputer diputuskan di sini | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8–13. Tambahan:
- **Jalan utama di latar**, dengan keluaran ke berkas log. Jangan menunggu dengan `sleep`. Sebelum mulai, mesin diperiksa
  tenang: `docker ps`, `nvidia-smi`, **uji milik sesi lain** (vitest, uji mutasi), dan beban CPU (`CLAUDE.md` §7).
- **Lembar hanya dibuka owner.** Agen menyebut jalurnya dan menunggu jawaban. Bila owner menulis nomor plat, nomor itu tidak
  disalin ke berkas mana pun.
- Nama berkas bukti memakai tanggal jalan (`2026-10-16` di bawah). Bila dijalankan pada tanggal lain, tanggal itu diganti.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/rantai.py` (baru) | Sampel, potong, lacak, gabung, detik sampai yakin, jalan per video dan semua video, CLI `jalan` | 1 |
| `tools/lab/uji/test_rantai.py` (baru) | Uji gerbang biasa, model tiruan dan video buatan | 1 |
| `tools/lab/lembar_rantai.py` (baru) | Pilih baris, lembar PNG, penilaian dari jawaban owner, CLI `lembar` dan `nilai` | 2 |
| `tools/lab/uji/test_lembar_rantai.py` (baru) | Uji gerbang biasa | 2 |
| `tools/lab/onnx_fpo.py` (ubah) | `PembacaOnnxMesin.dengan_yakin` | 3 |
| `tools/lab/uji_fpo/test_rantai_sungguhan.py` (baru) | Pembaca dengan keyakinan dan CLI rantai dengan model sungguhan (di luar gerbang) | 3 |
| `bukti/2026-10-16-rantai-video-*` (baru) | Ringkasan, nilai, laporan | 6, 7 |

---

### Task 1: Rantai: sampel, potong, lacak, gabung, dan jalan dari manifes

**Files:** Create `tools/lab/rantai.py`, `tools/lab/uji/test_rantai.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji tools/lab/rantai.py tanpa model: sampel, potong, lacak, gabung (cek pola), detik sampai yakin, dan rantai dari manifes
sampai berkas keluaran dengan pencari dan pembaca tiruan pada video buatan."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rantai  # noqa: E402

KOTAK = (60, 40, 100, 56)


def test_langkah_sampel_lima_per_detik_dan_fps_tak_terbaca():
    assert [rantai.langkah_sampel(f) for f in (30, 25, 60, 4)] == [6, 5, 12, 1]
    assert rantai.langkah_sampel(0) == rantai.langkah_sampel(float("nan")) == 6


def test_potong_dengan_tepi_dan_batas_gambar():
    gambar = np.zeros((100, 200, 3), np.uint8)

    assert rantai.potong(gambar, (10, 20, 50, 40)).shape == (22, 44, 3)
    assert rantai.potong(gambar, (190, 90, 210, 110)).shape == (11, 11, 3)
    assert rantai.potong(gambar, (250, 0, 260, 10)) is None


def tampak(kotak, yakin=0.9):
    return {"kotak": kotak, "yakin_kotak": yakin}


def test_pelacak_menyambung_kotak_bertumpuk_dan_memutus_sesudah_jeda():
    lacak = rantai.Pelacak()
    lacak.tambah(0.0, [tampak((10, 10, 50, 30))])
    lacak.tambah(0.2, [tampak((12, 10, 52, 30)), tampak((100, 100, 140, 120))])
    lacak.tambah(0.4, [])
    lacak.tambah(1.6, [tampak((12, 10, 52, 30))])

    assert [len(j) for j in lacak.jalur] == [2, 1, 1]
    assert [p["detik"] for p in lacak.jalur[0]] == [0.0, 0.2]


def test_pelacak_dua_kotak_di_satu_gambar_tidak_masuk_jalur_yang_sama():
    lacak = rantai.Pelacak()
    lacak.tambah(0.0, [tampak((10, 10, 50, 30))])
    lacak.tambah(0.2, [tampak((10, 10, 50, 30), 0.5), tampak((11, 10, 51, 30), 0.9)])

    assert [len(j) for j in lacak.jalur] == [2, 1]
    assert lacak.jalur[0][1]["yakin_kotak"] == 0.9


def bacaan(teks, yakin=0.8):
    return {"teks": teks, "yakin_baca": yakin}


def test_gabung_suara_terbanyak_dari_bacaan_sesuai_pola():
    hasil = rantai.gabung([bacaan("B1234XY"), bacaan("b 1234 xy"), bacaan("B1234XV"), bacaan("12AB")])

    assert hasil == {"teks": "B1234XY", "status": "yakin", "setuju": 2, "sah": 3, "tampak": 4}


def test_gabung_ragu_bila_dukungan_kurang_dan_seri_dipecah_dengan_yakin():
    hasil = rantai.gabung([bacaan("B1234XY", 0.5), bacaan("B1234XV", 0.9)])

    assert hasil["teks"] == "B1234XV" and hasil["status"] == "ragu" and hasil["setuju"] == 1
    assert rantai.gabung([bacaan(""), bacaan("??")]) == {"teks": "", "status": "ragu", "setuju": 0, "sah": 0, "tampak": 2}
    # Dua dari empat bacaan sah (50%) kurang dari BAGIAN_SETUJU: ragu walau didukung dua bacaan.
    assert rantai.gabung([bacaan("B1234XY"), bacaan("B1234XY"), bacaan("B1234XV"), bacaan("B1234XW")])["status"] == "ragu"


def test_detik_yakin_saat_bacaan_pertama_kali_cukup():
    jalur = [{**bacaan(t), "detik": d} for t, d in (("B1234XV", 0.0), ("B1234XY", 0.2), ("B1234XY", 0.4))]

    assert rantai.detik_yakin(jalur) == 0.4
    assert rantai.detik_yakin(jalur[:1]) is None


def video_buatan(jalur, terang, fps=10):
    """Video MJPG 160x96; gambar ke-i memuat persegi putih di KOTAK bila terang[i]."""
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), fps, (160, 96))
    for ada in terang:
        g = np.full((96, 160, 3), 40, np.uint8)
        if ada:
            cv2.rectangle(g, KOTAK[:2], KOTAK[2:], (255, 255, 255), -1)
        tulis.write(g)
    tulis.release()


def cari_tiruan(gambar):
    """Kotak di KOTAK bila tengahnya terang, ditambah kotak lemah di bawah ambang yang harus dibuang."""
    kotak = [(10.0, 10.0, 30.0, 20.0, 0.1)]
    if gambar[48, 80].mean() > 128:
        kotak.append((*map(float, KOTAK), 0.9))
    return kotak


def baca_tiruan(potongan):
    return "B1234XY", 0.8


def test_jalankan_video_sampel_lacak_dan_satu_potongan_per_jalur(tmp_path):
    video_buatan(tmp_path / "v.avi", [True] * 10 + [False] * 10)

    jalur, waktu = rantai.jalankan_video(tmp_path / "v.avi", cari_tiruan, baca_tiruan, ambang=0.25)

    assert len(waktu["dekode"]) == len(waktu["cari"]) == 10  # 20 gambar pada 10 fps, 5 sampel per detik
    assert [len(j) for j in jalur] == [5] and len(waktu["baca"]) == 5
    assert [p["detik"] for p in jalur[0]] == [0.0, 0.2, 0.4, 0.6, 0.8]
    assert sum("potongan" in p for p in jalur[0]) == 1


def test_rantai_dari_manifes_sampai_berkas_hanya_sudut_terpilih_dan_tanpa_teks_di_ringkasan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10 + [False] * 10)
    video_buatan(folder / "dasbor.avi", [True] * 20)
    (tmp_path / "manifes.json").write_text(json.dumps({"video": [
        {"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"},
        {"berkas": "dasbor.avi", "sudut": "dasbor", "kategori": "siang"}]}))

    r = rantai.jalankan_semua(tmp_path / "manifes.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "keluar")

    baris = [json.loads(b) for b in (tmp_path / "keluar" / "kedatangan.jsonl").read_text().splitlines()]
    assert [(b["video"], b["teks"], b["status"], b["detik_yakin"]) for b in baris] == [("gerbang.avi", "B1234XY", "yakin", 0.2)]
    assert (tmp_path / "keluar" / "potongan" / baris[0]["potongan"]).exists()
    assert r["video"] == 1 and r["kedatangan"] == r["yakin"] == 1 and r["gambar_sampel"] == 10
    ringkasan = (tmp_path / "keluar" / "ringkasan.json").read_text()
    assert "B1234" not in ringkasan and "gerbang.avi" not in ringkasan
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'rantai'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/rantai.py`**

```python
"""Rantai utuh di video riset (Rencana 14, K31, K32): cari plat (YOLOX-Nano-640), potong, baca huruf (fpo-indo-1), cek pola,
lalu gabung per kedatangan (spec 2.1 langkah 1, 3, 4, 5). Langkah 2 (meluruskan) belum ada: potongan dibaca apa adanya.

- Sampel: SAMPEL_PER_DETIK gambar per detik video. Gambar di antaranya dilewati dengan grab() dan tidak dihitung waktunya.
- Cari: kotak dengan keyakinan minimal ambang validasi pencari (dibaca dari mesin.json pencari, tidak disalin).
- Potong: kotak diperlebar MARGIN dari lebar dan tingginya di tiap sisi, dipotong pada batas gambar.
- Baca: (teks, yakin) per potongan; yakin = peluang terendah di semua slot pembaca.
- Lacak: kotak pada gambar sampel berikutnya ikut jalur yang sama bila IoU-nya dengan kotak terakhir jalur minimal IOU_IKUT
  dan jalur itu terakhir terlihat paling lama JEDA_MAKS_DETIK sebelumnya. Jalur yang terlihat minimal MIN_TAMPAK kali = satu
  kedatangan (spec 8.3: plat terlihat berturut-turut dalam satu potongan video); jalur yang terlihat sekali dihitung terpisah.
- Gabung: hanya bacaan yang sesuai pola plat Indonesia (plat.urai) yang dihitung. Teks yang paling sering dipilih (seri:
  jumlah yakin terbesar). Status "yakin" bila teks itu didukung minimal MIN_SETUJU bacaan dan minimal BAGIAN_SETUJU dari bacaan
  yang sah; selain itu "ragu" (ragu = tidak membuka). Semua ambang ditetapkan sebelum hasil dilihat dan tidak disetel dengan
  jawaban owner.
- detik_yakin: detik video dari penampakan pertama sampai bacaan gabungan pertama kali "yakin" bila bacaan diproses berurutan.

Keluaran di <keluar>: kedatangan.jsonl dan potongan/*.png memuat plat (data/; agen tidak membukanya); ringkasan.json hanya
hitungan dan waktu, tanpa nama berkas video. Layar hanya hitungan.

  jalan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/rantai.py jalan /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/rantai-video
"""
import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from deteksi import iou  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from plat import urai  # noqa: E402

SAMPEL_PER_DETIK = 5
IOU_IKUT = 0.3
JEDA_MAKS_DETIK = 1.0
MIN_TAMPAK = 2
MIN_SETUJU = 2
BAGIAN_SETUJU = 0.6
MARGIN = 0.05
SUDUT = ("gerbang", "kamera-diam-lain")
UTAS = 2
FPS_BAWAAN = 30.0


def fps_sah(fps):
    """fps dari video; yang tak terbaca (0, negatif, NaN) dianggap FPS_BAWAAN."""
    return float(fps) if fps and fps == fps and fps > 0 else FPS_BAWAAN


def langkah_sampel(fps, per_detik=SAMPEL_PER_DETIK):
    """Tiap berapa gambar diambil satu sampel."""
    return max(1, round(fps_sah(fps) / per_detik))


def potong(gambar, kotak, margin=MARGIN):
    """Potongan dari kotak (x1, y1, x2, y2, ...) yang diperlebar margin di tiap sisi; None bila kosong sesudah dipotong."""
    tinggi, lebar = gambar.shape[:2]
    x1, y1, x2, y2 = kotak[:4]
    dx, dy = (x2 - x1) * margin, (y2 - y1) * margin
    a, b = max(0, math.floor(x1 - dx)), max(0, math.floor(y1 - dy))
    c, d = min(lebar, math.ceil(x2 + dx)), min(tinggi, math.ceil(y2 + dy))
    return gambar[b:d, a:c].copy() if c > a and d > b else None


def luas(p):
    x1, y1, x2, y2 = p["kotak"]
    return (x2 - x1) * (y2 - y1)


class Pelacak:
    """Mengikuti kotak plat dari gambar sampel ke gambar sampel. jalur: daftar jalur; tiap jalur daftar penampakan (dict dengan
    "kotak", "yakin_kotak", "detik", dan isi lain yang dibawa pemanggil). aktif: indeks jalur yang masih bisa disambung."""

    def __init__(self, iou_ikut=IOU_IKUT, jeda_maks=JEDA_MAKS_DETIK):
        self.iou_ikut, self.jeda_maks = iou_ikut, jeda_maks
        self.jalur, self.aktif = [], []

    def tambah(self, detik, penampakan):
        self.aktif = [i for i in self.aktif if detik - self.jalur[i][-1]["detik"] <= self.jeda_maks]
        terpakai = set()
        for p in sorted(penampakan, key=lambda p: -p["yakin_kotak"]):
            nilai, i = max(((iou(p["kotak"], self.jalur[i][-1]["kotak"]), i) for i in self.aktif if i not in terpakai),
                           default=(0.0, None))
            if i is None or nilai < self.iou_ikut:
                self.jalur.append([])
                i = len(self.jalur) - 1
                self.aktif.append(i)
            terpakai.add(i)
            self.jalur[i].append({**p, "detik": detik})


def simpan_potongan_terbesar(jalur):
    """Hanya penampakan dengan kotak terbesar yang menyimpan potongannya (untuk lembar), supaya memori tidak tumbuh."""
    berpotongan = [p for p in jalur if "potongan" in p]
    if len(berpotongan) > 1:
        terbesar = max(berpotongan, key=luas)
        for p in berpotongan:
            if p is not terbesar:
                del p["potongan"]


def gabung(tampak, min_setuju=MIN_SETUJU, bagian_setuju=BAGIAN_SETUJU):
    """Penampakan satu jalur -> satu bacaan (spec 2.1 langkah 4 dan 5): teks, status ("yakin"/"ragu"), jumlah bacaan yang
    mendukung teks itu, jumlah bacaan sesuai pola, jumlah penampakan."""
    sah = [(urai(p["teks"]).teks, p["yakin_baca"]) for p in tampak if urai(p["teks"])]
    if not sah:
        return {"teks": "", "status": "ragu", "setuju": 0, "sah": 0, "tampak": len(tampak)}
    hitung, jumlah_yakin = Counter(), Counter()
    for teks, yakin in sah:
        hitung[teks] += 1
        jumlah_yakin[teks] += yakin
    teks = max(hitung, key=lambda t: (hitung[t], jumlah_yakin[t]))
    setuju = hitung[teks]
    status = "yakin" if setuju >= min_setuju and setuju >= bagian_setuju * len(sah) else "ragu"
    return {"teks": teks, "status": status, "setuju": setuju, "sah": len(sah), "tampak": len(tampak)}


def detik_yakin(tampak, min_setuju=MIN_SETUJU, bagian_setuju=BAGIAN_SETUJU):
    """Detik video dari penampakan pertama sampai bacaan gabungan pertama kali "yakin"; None bila tidak pernah."""
    for k in range(1, len(tampak) + 1):
        if gabung(tampak[:k], min_setuju, bagian_setuju)["status"] == "yakin":
            return round(tampak[k - 1]["detik"] - tampak[0]["detik"], 3)
    return None


def jalankan_video(jalur_video, cari, baca, ambang, per_detik=SAMPEL_PER_DETIK):
    """Satu video -> (jalur penampakan, waktu). cari(gambar) -> [(x1, y1, x2, y2, yakin)]; baca(potongan) -> (teks, yakin).
    waktu: milidetik dekode dan cari per gambar sampel, dan baca per potongan."""
    video = cv2.VideoCapture(str(jalur_video))
    if not video.isOpened():
        raise OSError("video tidak bisa dibuka")
    fps = fps_sah(video.get(cv2.CAP_PROP_FPS))
    langkah = langkah_sampel(fps, per_detik)
    pelacak = Pelacak()
    waktu = {"dekode": [], "cari": [], "baca": []}
    nomor = 0
    try:
        while True:
            if nomor % langkah:
                if not video.grab():
                    break
                nomor += 1
                continue
            mulai = time.perf_counter()
            ada, gambar = video.read()
            if not ada:
                break
            waktu["dekode"].append(1000 * (time.perf_counter() - mulai))
            mulai = time.perf_counter()
            kotak = [k for k in cari(gambar) if k[4] >= ambang]
            waktu["cari"].append(1000 * (time.perf_counter() - mulai))
            penampakan = []
            for k in kotak:
                p = potong(gambar, k)
                if p is None:
                    continue
                mulai = time.perf_counter()
                teks, yakin = baca(p)
                waktu["baca"].append(1000 * (time.perf_counter() - mulai))
                penampakan.append({"kotak": tuple(float(x) for x in k[:4]), "yakin_kotak": float(k[4]), "teks": str(teks),
                                   "yakin_baca": float(yakin), "potongan": p})
            pelacak.tambah(nomor / fps, penampakan)
            for i in pelacak.aktif:
                simpan_potongan_terbesar(pelacak.jalur[i])
            nomor += 1
    finally:
        video.release()
    return pelacak.jalur, waktu


def daftar_video(manifes, sudut=SUDUT):
    isi = json.loads(Path(manifes).read_text(encoding="utf-8"))
    return [v for v in isi["video"] if v.get("sudut") in sudut]


def _ms(daftar):
    if not daftar:
        return None
    return {"n": len(daftar), "median": round(float(np.median(daftar)), 2), "p95": round(float(np.percentile(daftar, 95)), 2)}


def jalankan_semua(manifes, folder_video, cari, baca, ambang, keluar):
    """Semua video bersudut SUDUT di manifes. Kembali: ringkasan (hitungan dan waktu saja)."""
    keluar = Path(keluar)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    semua_waktu = {"dekode": [], "cari": [], "baca": []}
    per_video, baris = [], []
    for urutan, v in enumerate(daftar_video(manifes), 1):
        jalur, waktu = jalankan_video(Path(folder_video) / v["berkas"], cari, baca, ambang)
        tiba = [j for j in jalur if len(j) >= MIN_TAMPAK]
        for nomor, j in enumerate(tiba, 1):
            nama = f"{Path(v['berkas']).stem}-{nomor}.png"
            cv2.imwrite(str(keluar / "potongan" / nama), next(p["potongan"] for p in j if "potongan" in p))
            baris.append({"video": v["berkas"], "kategori": v["kategori"], "sudut": v["sudut"], "nomor": nomor, **gabung(j),
                          "detik_mulai": round(j[0]["detik"], 3), "detik_yakin": detik_yakin(j), "potongan": nama})
        per_video.append({"urutan": urutan, "kategori": v["kategori"], "sudut": v["sudut"], "gambar_sampel": len(waktu["dekode"]),
                          "penampakan": sum(len(j) for j in jalur), "kedatangan": len(tiba),
                          "tampak_sekali": len(jalur) - len(tiba)})
        for k in semua_waktu:
            semua_waktu[k] += waktu[k]
    with open(keluar / "kedatangan.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    yakin = [b for b in baris if b["status"] == "yakin"]
    ringkasan = {
        "aturan": {"sampel_per_detik": SAMPEL_PER_DETIK, "ambang_kotak": ambang, "iou_ikut": IOU_IKUT,
                   "jeda_maks_detik": JEDA_MAKS_DETIK, "min_tampak": MIN_TAMPAK, "min_setuju": MIN_SETUJU,
                   "bagian_setuju": BAGIAN_SETUJU, "margin": MARGIN},
        "video": len(per_video), "gambar_sampel": sum(v["gambar_sampel"] for v in per_video),
        "kedatangan": len(baris), "yakin": len(yakin), "ragu": len(baris) - len(yakin),
        "tampak_sekali": sum(v["tampak_sekali"] for v in per_video),
        "per_kategori": {k: sum(b["kategori"] == k for b in baris) for k in sorted({b["kategori"] for b in baris})},
        "detik_yakin": _ms([b["detik_yakin"] for b in yakin]),
        "waktu_ms": {k: _ms(x) for k, x in semua_waktu.items()},
        "per_video": per_video,
    }
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=1))
    return ringkasan


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Rantai utuh di video riset (Rencana 14).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    j = perintah.add_parser("jalan")
    for nama in ("manifes", "folder_video", "folder_pencari", "folder_baca", "folder_unduhan", "keluar"):
        j.add_argument(nama)
    j.add_argument("--utas", type=int, default=UTAS)
    p = pengurai.parse_args(argumen)
    try:
        import onnx_fpo
        from pencari_yolox import PencariYolox

        cari = PencariYolox(p.folder_pencari, utas=p.utas)
        pembaca = onnx_fpo.PembacaOnnxMesin(p.folder_baca, p.folder_unduhan, utas=p.utas)
        ambang = json.loads((Path(p.folder_pencari) / "mesin.json").read_text())["ambang_validasi"]
        r = jalankan_semua(p.manifes, p.folder_video, cari, pembaca.dengan_yakin, ambang, p.keluar)
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{r['video']} video, {r['gambar_sampel']} gambar sampel; {r['kedatangan']} kedatangan ({r['yakin']} yakin, "
          f"{r['ragu']} ragu); {r['tampak_sekali']} jalur terlihat sekali")
    waktu = ", ".join(f"{k} {v['median']}" for k, v in r["waktu_ms"].items() if v)
    print(f"median ms (utas {p.utas}): {waktu}; detik sampai yakin: {r['detik_yakin']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

`utama` memanggil `PembacaOnnxMesin.dengan_yakin`, yang baru ditambahkan di Task 3. Baris perintah `jalan` baru dipakai sesudah
Task 3.

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `199 passed` (190 + 9), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/rantai.py` dan ujinya, dengan alasan (rantai dengan model disuntikkan, ambang ditetapkan
sebelum hasil dilihat, ringkasan tanpa teks plat dan nama video) dan angka gerbang 190 → 199.

---

### Task 2: Lembar untuk owner dan penilaian dari jawabannya

**Files:** Create `tools/lab/lembar_rantai.py`, `tools/lab/uji/test_lembar_rantai.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji tools/lab/lembar_rantai.py: pilihan baris tetap dan bergiliran antarvideo, penilaian dari jawaban owner (nomor baris dan
jenis saja), penolakan jawaban yang tidak cocok dengan lembar, dan rantai CLI lembar lalu nilai dengan layar tanpa teks plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_rantai as lr  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_rantai.py"


def kedatangan(video, nomor, teks="B1234XY", status="yakin", kategori="siang"):
    return {"video": video, "nomor": nomor, "teks": teks, "status": status, "kategori": kategori,
            "potongan": f"{video}-{nomor}.png"}


def test_pilih_baris_tetap_dan_bergiliran_antarvideo():
    semua = [kedatangan("a", n) for n in range(1, 6)] + [kedatangan("b", 1)] + [kedatangan("c", n) for n in (1, 2)]

    pilih = lr.pilih_baris(semua, maks=4)

    assert [k["video"] for k in pilih] == ["a", "b", "c", "a"]
    assert pilih == lr.pilih_baris(list(reversed(semua)), maks=4)
    assert len(lr.pilih_baris(semua, maks=100)) == 8


def lembar_(baris):
    return {"baris": [{"nomor": i, **b} for i, b in enumerate(baris, 1)]}


def test_nilai_dari_nomor_baris_dan_jenis():
    lembar = lembar_([
        {"teks": "B1234XY", "status": "yakin", "kategori": "siang"},  # 1 benar, yakin
        {"teks": "B1234XY", "status": "yakin", "kategori": "siang"},  # 2 salah, yakin
        {"teks": "B1234XY", "status": "ragu", "kategori": "siang"},  # 3 benar, ragu, motor
        {"teks": "", "status": "ragu", "kategori": "siang"},  # 4 tanpa bacaan sah: salah, ragu
        {"teks": "B1234XY", "status": "yakin", "kategori": "malam"},  # 5 tak terbaca: tidak dinilai
        {"teks": "B1234XY", "status": "yakin", "kategori": "malam"},  # 6 bukan plat: tidak dinilai
    ])

    h = lr.nilai(lembar, salah=[2], tak_terbaca=[5], bukan_plat=[6], motor=[3])

    assert (h["baris"], h["tak_terbaca"], h["bukan_plat"], h["motor"]) == (6, 1, 1, 1)
    s = h["kelompok"]["semua"]
    assert (s["dinilai"], s["benar_yakin"], s["benar_ragu"], s["salah_ragu"], s["salah_yakin"]) == (4, 1, 1, 1, 1)
    assert h["kelompok"]["siang-mobil"]["dinilai"] == 3 and h["kelompok"]["siang-motor"]["benar_ragu"] == 1
    assert "malam-mobil" not in h["kelompok"] and s["terlalu_sedikit"] is True


def test_nilai_menolak_nomor_yang_tidak_ada_dan_jenis_yang_bertentangan():
    lembar = lembar_([{"teks": "B1234XY", "status": "yakin", "kategori": "siang"}] * 3)

    with pytest.raises(ValueError, match="tidak ada"):
        lr.nilai(lembar, salah=[4])
    with pytest.raises(ValueError, match="sekaligus"):
        lr.nilai(lembar, salah=[1], bukan_plat=[1])


def test_rantai_cli_lembar_lalu_nilai_tanpa_teks_plat_di_layar(tmp_path):
    folder = tmp_path / "rantai"
    (folder / "potongan").mkdir(parents=True)
    semua = [kedatangan("v1", 1), kedatangan("v1", 2, status="ragu"), kedatangan("v2", 1, teks="")]
    for k in semua:
        cv2.imwrite(str(folder / "potongan" / k["potongan"]), np.full((20, 60, 3), 200, np.uint8))
    (folder / "kedatangan.jsonl").write_text("".join(json.dumps(k) + "\n" for k in semua))

    a = subprocess.run([sys.executable, str(SKRIP), "lembar", str(folder), str(tmp_path / "lembar")],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, str(SKRIP), "nilai", str(tmp_path / "lembar" / "lembar-rantai.json"),
                        str(tmp_path / "lembar" / "nilai.json"), "--salah", "2", "--motor", "1"], capture_output=True, text=True)

    layar = a.stdout + a.stderr + b.stdout + b.stderr
    assert a.returncode == 0 and b.returncode == 0, layar[-2000:]
    assert "B1234" not in layar
    assert (tmp_path / "lembar" / "lembar-rantai-1.png").exists()
    nilai = json.loads((tmp_path / "lembar" / "nilai.json").read_text())
    assert nilai["baris"] == 3 and nilai["kelompok"]["semua"]["dinilai"] == 3
    assert "B1234" not in (tmp_path / "lembar" / "nilai.json").read_text()
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'lembar_rantai'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/lembar_rantai.py`**

```python
"""Lembar rantai utuh untuk diperiksa OWNER (K32) dan penilaian dari jawabannya (Rencana 14).

Lembar memuat plat yang terbaca, jadi agen TIDAK PERNAH membukanya (CLAUDE.md §7). Tiap baris: nomor, potongan plat terbesar
satu kedatangan, dan bacaan gabungan mesin ("-" bila tidak ada bacaan yang sesuai pola). Owner menyebut nomor baris untuk
empat jenis saja:
- salah: bacaan tidak sama dengan plat di potongan;
- tak terbaca: plat di potongan tidak bisa dibaca manusia (tidak dinilai);
- bukan plat: potongan tidak berisi plat (tidak dinilai);
- motor: kendaraannya sepeda motor.
Baris yang tidak disebut: bacaan benar, mobil. Baris "-" yang tidak disebut tak terbaca atau bukan plat dihitung salah.

Bila kedatangan lebih dari MAKS_BARIS, baris dipilih tetap (bukan acak): per video diurutkan menurut SHA-256 "<video>/<nomor>",
lalu diambil bergiliran antarvideo sampai MAKS_BARIS.

Kelompok: kategori video dari manifes (siang, malam, remang, tak-jelas, campuran) x mobil/motor dari jawaban owner. Per
kelompok: benar-yakin (gerbang membuka bila platnya terdaftar), benar-ragu dan salah-ragu (tidak membuka: gagal-buka bila
terdaftar), salah-yakin (bacaan salah yang yakin: bahaya buka-salah bila bacaan salah itu kebetulan terdaftar).

  lembar: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_rantai.py lembar /kerja/data/keluaran/rantai-video /kerja/data/keluaran/lembar-rantai
  nilai:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_rantai.py nilai /kerja/data/keluaran/lembar-rantai/lembar-rantai.json /kerja/data/keluaran/lembar-rantai/nilai.json --salah <n,...> --tak-terbaca <n,...> --bukan-plat <n,...> --motor <n,...>
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import wilson  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from bagi_set_uji import SEDIKIT  # noqa: E402
from lembar_contoh import PER_LEMBAR, baris  # noqa: E402

MAKS_BARIS = 120


def pilih_baris(kedatangan, maks=MAKS_BARIS):
    per_video = {}
    for k in kedatangan:
        per_video.setdefault(k["video"], []).append(k)
    antre = [sorted(d, key=lambda k: hashlib.sha256(f"{k['video']}/{k['nomor']}".encode()).hexdigest())
             for _, d in sorted(per_video.items())]
    terpilih = []
    while len(terpilih) < maks and any(antre):
        for d in antre:
            if d and len(terpilih) < maks:
                terpilih.append(d.pop(0))
    return terpilih


def buat_lembar(folder_rantai, keluar, maks=MAKS_BARIS):
    folder = Path(folder_rantai)
    kedatangan = [json.loads(b) for b in (folder / "kedatangan.jsonl").read_text().splitlines() if b.strip()]
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    barisan, isi = [], []
    for nomor, k in enumerate(pilih_baris(kedatangan, maks), 1):
        barisan.append(baris(nomor, cv2.imread(str(folder / "potongan" / k["potongan"])), k["teks"] or "-"))
        isi.append({"nomor": nomor, "video": k["video"], "kedatangan": k["nomor"], "kategori": k["kategori"],
                    "status": k["status"], "teks": k["teks"]})
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-rantai-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-rantai.json").write_text(json.dumps({"maks_baris": maks, "kedatangan": len(kedatangan),
                                                           "halaman": halaman, "baris": isi}, indent=1))
    return {"kedatangan": len(kedatangan), "baris": len(isi), "halaman": len(halaman)}


def nilai(lembar, salah=(), tak_terbaca=(), bukan_plat=(), motor=()):
    """Hitungan per kelompok dari jawaban owner (nomor baris per jenis). Kembali: hitungan saja."""
    semua = {b["nomor"]: b for b in lembar["baris"]}
    sebut = {"salah": set(salah), "tak_terbaca": set(tak_terbaca), "bukan_plat": set(bukan_plat), "motor": set(motor)}
    for nama, nomor in sebut.items():
        asing = nomor - set(semua)
        if asing:
            raise ValueError(f"nomor baris {nama} tidak ada di lembar: {sorted(asing)}")
    for a, b in (("salah", "tak_terbaca"), ("salah", "bukan_plat"), ("tak_terbaca", "bukan_plat"), ("motor", "bukan_plat")):
        dua = sebut[a] & sebut[b]
        if dua:
            raise ValueError(f"baris {sorted(dua)} disebut {a} dan {b} sekaligus")
    hasil = {"baris": len(semua), "tak_terbaca": len(sebut["tak_terbaca"]), "bukan_plat": len(sebut["bukan_plat"]),
             "motor": len(sebut["motor"]), "kelompok": {}}
    for nomor, b in sorted(semua.items()):
        if nomor in sebut["tak_terbaca"] or nomor in sebut["bukan_plat"]:
            continue
        jenis = "motor" if nomor in sebut["motor"] else "mobil"
        benar = nomor not in sebut["salah"] and bool(b["teks"])
        for k in ("semua", f"{b['kategori']}-{jenis}"):
            r = hasil["kelompok"].setdefault(k, {"dinilai": 0, "benar_yakin": 0, "benar_ragu": 0, "salah_ragu": 0, "salah_yakin": 0})
            r["dinilai"] += 1
            r[f"{'benar' if benar else 'salah'}_{b['status']}"] += 1
    for r in hasil["kelompok"].values():
        rentang = wilson(r["benar_yakin"], r["dinilai"])
        r["rentang_95_benar_yakin"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["dinilai"] < SEDIKIT
    return hasil


def nomor_baris(teks):
    return [int(x) for x in teks.split(",") if x.strip()] if teks else []


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Lembar rantai utuh untuk owner dan penilaiannya (Rencana 14, K32).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("lembar")
    a.add_argument("folder_rantai")
    a.add_argument("keluar")
    a.add_argument("--maks", type=int, default=MAKS_BARIS)
    b = perintah.add_parser("nilai")
    b.add_argument("lembar")
    b.add_argument("keluar")
    for nama in ("salah", "tak-terbaca", "bukan-plat", "motor"):
        b.add_argument(f"--{nama}", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "lembar":
            r = buat_lembar(p.folder_rantai, p.keluar, p.maks)
            print(f"{r['kedatangan']} kedatangan -> {r['baris']} baris di {r['halaman']} lembar. "
                  "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
        else:
            h = nilai(json.loads(Path(p.lembar).read_text()), p.salah, p.tak_terbaca, p.bukan_plat, p.motor)
            Path(p.keluar).write_text(json.dumps(h, indent=1))
            print(f"{h['baris']} baris: tak terbaca {h['tak_terbaca']}, bukan plat {h['bukan_plat']}, motor {h['motor']}")
            for k, r in sorted(h["kelompok"].items()):
                print(f"{k:<16} dinilai {r['dinilai']}: benar-yakin {r['benar_yakin']} (rentang 95% "
                      f"{r['rentang_95_benar_yakin']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}), "
                      f"benar-ragu {r['benar_ragu']}, salah-ragu {r['salah_ragu']}, salah-yakin {r['salah_yakin']}")
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "baris" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

Pesan `ValueError` dari `nilai` hanya memuat nomor baris dan nama jenis, jadi dicetak apa adanya. `ValueError` lain hanya dicetak
jenisnya.

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `203 passed` (199 + 4), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/lembar_rantai.py` dan ujinya, dengan alasan (lembar hanya dibuka owner, jawaban hanya nomor
baris per jenis, baris "-" dihitung salah, pilihan baris tetap) dan angka gerbang 199 → 203.

---

### Task 3: Pembaca dengan keyakinan, dan rantai dengan model sungguhan

**Files:** Modify `tools/lab/onnx_fpo.py`; Create `tools/lab/uji_fpo/test_rantai_sungguhan.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji rantai utuh dengan model sungguhan di image lab tambahan (di luar gerbang biasa): fpo-indo-1 ONNX memberi bacaan beserta
keyakinannya, dan baris perintah rantai.py jalan berjalan dari manifes sampai ringkasan dengan YOLOX-Nano-640 dan fpo-indo-1 pada
video buatan, dengan layar tanpa nama berkas.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
KELUARAN = AKAR / "data" / "keluaran"
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import onnx_fpo as of  # noqa: E402
from test_percobaan_fpo import TEKS, plat_buatan  # noqa: E402

BACA = KELUARAN / "fpo-indo-1"
CARI = KELUARAN / "pencari-yolox-nano-640"
SKRIP = AKAR / "tools" / "lab" / "rantai.py"
pytestmark = pytest.mark.skipif(not ((BACA / "mesin.onnx").exists() and (CARI / "mesin.onnx").exists()),
                                reason="fpo-indo-1 atau pencari-yolox-nano-640 belum ada (Rencana 11, 13)")


def test_dengan_yakin_sama_dengan_bacaan_biasa_dan_yakin_di_antara_nol_dan_satu():
    pembaca = of.PembacaOnnxMesin(BACA, UNDUHAN, utas=2)

    for t in TEKS:
        gambar = plat_buatan(t)
        teks, yakin = pembaca.dengan_yakin(gambar)
        assert teks == pembaca(gambar) and 0.0 < yakin <= 1.0


def test_baris_perintah_rantai_dengan_model_sungguhan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis = cv2.VideoWriter(str(folder / "buatan-gerbang.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 10, (640, 360))
    plat = cv2.resize(plat_buatan(TEKS[0]), (160, 48))
    for _ in range(20):
        g = np.full((360, 640, 3), 90, np.uint8)
        g[200:248, 240:400] = plat
        tulis.write(g)
    tulis.release()
    (tmp_path / "manifes.json").write_text(json.dumps({"video": [
        {"berkas": "buatan-gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    hasil = subprocess.run([sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI),
                            str(BACA), str(UNDUHAN), str(tmp_path / "keluar")], capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    assert "buatan-gerbang" not in layar
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    ambang = json.loads((CARI / "mesin.json").read_text())["ambang_validasi"]
    assert r["video"] == 1 and r["gambar_sampel"] == 10 and r["aturan"]["ambang_kotak"] == ambang
```

- [x] **Step 2: Jalankan, pastikan merah**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `2 failed, 17 passed`, keduanya karena `PembacaOnnxMesin` belum punya `dengan_yakin` (yang kedua: proses anak keluar
dengan `AttributeError`). `EXIT=1`.

- [x] **Step 3: Tambahkan `dengan_yakin` di `PembacaOnnxMesin`** (`tools/lab/onnx_fpo.py`), sesudah `__call__`:

```python
    def dengan_yakin(self, gambar_bgr):
        """(teks, yakin): yakin = peluang terendah di semua slot, termasuk slot bantalan, jadi keraguan soal panjang plat ikut
        terhitung (Rencana 14)."""
        hasil = self._model.run_one(ubah_warna(gambar_bgr, self.cfg.image_color_mode), return_confidence=True)
        return hasil.plate, float(np.min(hasil.char_probs))
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run (PowerShell): sama dengan Step 2.
Expected: `19 passed`, `EXIT=0`.

Run: `npm run test:lab; echo "EXIT=$?"` (Expected `203 passed`) lalu `npm test; echo "EXIT=$?"` (Expected `pass 107`).

- [x] **Step 5: Commit** `tools/lab/onnx_fpo.py` dan `tools/lab/uji_fpo/test_rantai_sungguhan.py`, dengan alasan (keyakinan
per bacaan untuk tingkat yakin per kedatangan; uji rantai CLI dengan model sungguhan) dan angka uji image tambahan 17 → 19.

---

### Task 4: Jalankan rantai di 30 video dan buat lembar

**Files:** keluaran saja (`data/keluaran/rantai-video/`, `data/keluaran/lembar-rantai/`)

- [x] **Step 1: Pastikan mesin tenang**

Run (PowerShell): `docker ps --format '{{.Image}} {{.Status}}'`; `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader`;
`Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'vitest|jalankan-mutasi|playwright test|next dev|pytest' } | Measure-Object`;
beban CPU tiga kali dengan `Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 3`.
Expected: tidak ada job lab lain, tidak ada uji sesi lain, beban CPU rendah. Bila ada, tunggu; jangan menyentuh proses sesi lain.

- [x] **Step 2: Jalankan rantai (di latar, keluaran ke berkas log)**

Run (PowerShell, `run_in_background`, log ke `<folder sementara sesi>\rantai-video.txt`):
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/rantai.py jalan /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/rantai-video *> <log>; "EXIT=$LASTEXITCODE"`
Expected: `30 video, ... gambar sampel; ... kedatangan (... yakin, ... ragu); ... jalur terlihat sekali`, baris median ms, `EXIT=0`.
Jumlah gambar sampel harus dekat 33.830; bila jauh berbeda, periksa dulu sebelum melanjutkan.

- [x] **Step 3: Buat lembar**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/lembar_rantai.py lembar /kerja/data/keluaran/rantai-video /kerja/data/keluaran/lembar-rantai; "EXIT=$LASTEXITCODE"`
Expected: `<n> kedatangan -> <m> baris di <h> lembar. ...`, `EXIT=0`. Bila kedatangan 0, **berhenti** dan laporkan ke owner
(tidak ada yang bisa diperiksa); jangan menurunkan ambang untuk memunculkan kedatangan.

---

### Task 5: Owner memeriksa lembar (K32)

- [x] **Step 1: BERHENTI. Minta owner memeriksa lembar**

Agen tidak membuka lembar. Pesan ke owner, dalam bahasa sederhana:
- **Letak lembar:** `D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-rantai\lembar-rantai-1.png` sampai
  `-<h>.png`, 20 baris per lembar.
- **Isi tiap baris:** nomor, potongan plat dari video, dan bacaan mesin ("-" bila mesin tidak punya bacaan yang sesuai pola).
- **Yang disebut owner,** nomor baris saja, untuk empat jenis: **salah** (bacaan tidak sama dengan plat), **tak terbaca**
  (manusia pun tak bisa membaca platnya), **bukan plat**, **motor**. Baris yang tidak disebut dianggap bacaan benar dan mobil.
- **Jangan menulis nomor plat.** Cukup nomor baris dan jenisnya (`CLAUDE.md` §4). Bila owner tetap menulisnya, nomor itu tidak
  disalin ke berkas mana pun.

- [x] **Step 2: Catat penilaian dari jawaban owner**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/lembar_rantai.py nilai /kerja/data/keluaran/lembar-rantai/lembar-rantai.json /kerja/data/keluaran/lembar-rantai/nilai.json --salah <n,...> --tak-terbaca <n,...> --bukan-plat <n,...> --motor <n,...>; "EXIT=$LASTEXITCODE"`
Expected: satu baris jumlah, lalu satu baris per kelompok, `EXIT=0`. Bila `GAGAL` menyebut nomor yang tidak ada atau jenis yang
bertentangan, tanyakan baris itu ke owner; jangan menebak.

---

### Task 6: Bukti, diperiksa tanpa nomor plat (dengan kontrol positif)

**Files:** Create `data/alat-sementara/periksa-bukti-14.py` (sekali pakai); `bukti/2026-10-16-rantai-video-*.json`

- [x] **Step 1: Tulis pemeriksa**

```python
"""Sekali pakai (Rencana 14): menyalin ringkasan ke bukti-siap/ hanya bila tak satu pun teks plat atau nama berkas ada di
dalamnya. Larangan: sama dengan periksa-bukti-13.py, DITAMBAH bacaan rantai utuh di video riset (kedatangan.jsonl).
Kontrol positif: semua bacaan rantai dan stem plat-lighting ditulis ke berkas sementara, lalu harus ditemukan semuanya.
Pakai: python periksa-bukti-14.py <tanggal-jalan>
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
bacaan = {json.loads(b)["teks"] for b in (K / "rantai-video/kedatangan.jsonl").read_text().splitlines() if b.strip()} - {""}
larangan |= stem | bacaan


def temuan(teks):
    return sum(1 for t in larangan if t in teks)


sementara = K / "bukti-siap" / "kontrol-14.tmp"
sementara.write_text("\n".join(sorted(stem | bacaan)))
kontrol = temuan(sementara.read_text())
sementara.unlink()
print(f"ukuran daftar larangan: {len(larangan)} (bacaan rantai {len(bacaan)}); kontrol positif: {kontrol} ditemukan, "
      f"harus minimal {len(stem | bacaan)}")
if kontrol < len(stem | bacaan):
    sys.exit(1)
for asal, tujuan in (("rantai-video/ringkasan.json", "rantai-video-ringkasan.json"),
                     ("lembar-rantai/nilai.json", "rantai-video-nilai.json")):
    n = temuan((K / asal).read_text())
    print(f"{tujuan}: {n} teks plat atau nama berkas ditemukan")
    if n:
        sys.exit(1)
    shutil.copy(K / asal, K / "bukti-siap" / f"{tanggal}-{tujuan}")
```

- [x] **Step 2: Jalankan, lalu salin ke `bukti/`**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/periksa-bukti-14.py 2026-10-16; "EXIT=$LASTEXITCODE"`
Expected: kontrol positif minimal sebanyak daftarnya; kedua berkas 0 temuan; `EXIT=0`. Bila ada temuan, **berhenti**:
periksa penyebabnya (misalnya bacaan pendek yang kebetulan muncul di angka) sebelum mengubah apa pun.
Lalu salin kedua berkas dari `data/keluaran/bukti-siap/` ke `bukti/`.

- [x] **Step 3: Commit** kedua berkas bukti, dengan jumlah kedatangan, yakin dan ragu, angka per kelompok dari lembar, waktu per
gambar, dan detik sampai yakin.

---

### Task 7: Laporan, catatan, dan pertanyaan ke owner

- [x] **Step 1: Tulis laporan `bukti/2026-10-16-rantai-utuh-video.md`**

Isinya:
- **Rantai yang dijalankan:** lima langkah dan yang belum ada (meluruskan), ambang rantai dan alasannya ditetapkan sebelum hasil.
- **Hitungan:** video, gambar sampel, penampakan, kedatangan (yakin dan ragu), jalur terlihat sekali, per kategori.
- **Dari lembar owner:** baris, tak terbaca, bukan plat, motor; per kelompok benar-yakin, benar-ragu, salah-ragu, salah-yakin,
  dengan rentang 95% dan "terlalu sedikit" bila kurang dari 30. Salah-yakin disebut terpisah karena itu bahaya buka-salah.
- **Kecepatan:** median dan p95 dekode, cari per gambar, baca per potongan di laptop (2 utas); detik video sampai bacaan yakin;
  taksiran Mini PC dari angka model yang diukur di sana (Nano-640 150 ms, pembaca 100 ms, 2 utas) ditambah dekode laptop × 8–10,
  terhadap sasaran dua detik (spec 2.6), ditulis sebagai taksiran.
- **Batas:**
  - video daring, bukan kamera gerbang (bukan bukti K9);
  - semua video bersudut gerbang siang;
  - kendaraan yang platnya tidak pernah ditemukan tidak muncul di lembar;
  - satu kendaraan bisa terpecah menjadi dua kedatangan;
  - langkah meluruskan belum ada;
  - mesin `RISET-SAJA`.

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 14 ditulis" dan "Rencana 14 dijalankan" dicentang dengan angka;
  - butir berikutnya "Rencana 15 ditulis: laporan Fase 0A";
  - status dan changelog.
- `CLAUDE.md` §7:
  - rantai di `tools/lab/rantai.py`, dijalankan di image tambahan;
  - keluaran `data/keluaran/rantai-video/` (`kedatangan.jsonl` dan `potongan/` memuat plat; agen hanya membaca
    `ringkasan.json`);
  - lembar dari `tools/lab/lembar_rantai.py` hanya dibuka owner.
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 14" (bagi B5, dan apa yang belum terbukti).
- Rencana ini: kotak dicentang dan catatan pelaksanaan.

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `203 passed`.

- [x] **Step 4: BERHENTI. Laporkan ke owner**

Ringkas dalam bahasa sederhana, lalu **satu** pertanyaan pilihan ganda dengan saran di depan: menulis Rencana 15 (laporan
Fase 0A dan keputusan lanjut, tunggu lokasi, atau ubah arah), atau lebih dulu memperbaiki langkah yang paling lemah menurut
lembar (misalnya meluruskan plat, atau pembaca yang dilatih dengan potongan dari pencari sendiri).

---

## Pemeriksaan diri atas rencana ini

- **Cakupan spec 2.1 dan K32:**
  - langkah 1 (cari), 3 (baca), 4 (cek pola), 5 (gabung) ada;
  - langkah 2 (meluruskan) ditulis sebagai batas;
  - satu bacaan per kedatangan dengan status yakin atau ragu (2.2);
  - lembar diperiksa owner, jawabannya nomor baris saja (K19, K32).
- **Spec 8.3:**
  - kedatangan = plat terlihat berturut-turut (minimal 2 gambar sampel);
  - angka bersama jumlahnya dan rentangnya;
  - kelompok kurang dari 30 ditandai;
  - kelompok yang kosong tidak muncul (dinyatakan di laporan).
- **Set uji tidak bocor ke pilihan:** ambang rantai ditetapkan sebelum hasil dan tidak disetel dengan jawaban owner. Pencari dan
  pembaca tidak pernah dilatih dengan video riset.
- **Data pribadi:**
  - `kedatangan.jsonl`, potongan, dan lembar hanya di `data/`;
  - ringkasan tanpa teks plat dan tanpa nama video (diuji);
  - layar CLI tanpa nama berkas (diuji di proses terpisah);
  - bukti diperiksa dengan larangan yang memuat bacaan rantai sendiri dan kontrol positif.
- **Uji rantai:**
  - manifes → video → berkas keluaran dengan model tiruan (gerbang biasa);
  - CLI lembar → CLI nilai (gerbang biasa);
  - CLI rantai dengan YOLOX-Nano-640 dan fpo-indo-1 sungguhan (image tambahan).
- **Angka gerbang:** Node 107 tetap; lab 190 → 199 → 203; uji image tambahan 17 → 19.
- **Nama konsisten:**
  - `fps_sah`, `langkah_sampel`, `potong`, `luas`, `Pelacak` (`tambah`, `jalur`, `aktif`), `simpan_potongan_terbesar`;
  - `gabung`, `detik_yakin`, `jalankan_video`, `daftar_video`, `jalankan_semua`;
  - `pilih_baris`, `buat_lembar`, `nilai`, `nomor_baris`, `MAKS_BARIS`;
  - `PembacaOnnxMesin.dengan_yakin`;
  - kunci `kedatangan.jsonl`: `video`, `kategori`, `sudut`, `nomor`, `teks`, `status`, `setuju`, `sah`, `tampak`,
    `detik_mulai`, `detik_yakin`, `potongan`.

## Catatan pelaksanaan (16 Okt)

- Dijalankan atas lampu hijau owner ("A. Jalankan sekarang"). Laporan:
  [`bukti/2026-10-16-rantai-utuh-video.md`](../bukti/2026-10-16-rantai-utuh-video.md).
- **Menyimpang dari rencana, dengan alasan:**
  - **Perekam proses ditambahkan pada jalan utama** (`data/alat-sementara/jalan-rantai-14.ps1`), karena di Rencana 13 uji
    milik sesi lain merusak angka kecepatan. Ia menangkap uji sesi lain menyala sekitar 6 dari 13 menit jalan pertama.
  - **Rantai dijalankan ulang** ke `data/keluaran/rantai-video-ulang/` saat tenang (75 rekaman tanpa uji sesi lain). Hasilnya
    identik dengan jalan pertama (SHA-256 `kedatangan.jsonl` sama), dan kecepatan di laporan diambil dari jalan ulang. Lembar dan
    penilaian tetap dari jalan pertama. Ringkasan jalan ulang ikut disalin ke bukti, sehingga pemeriksa bukti memeriksa tiga
    berkas, bukan dua.
  - **Diagnosis tambahan**, keduanya hanya mencetak hitungan: `data/alat-sementara/sebab-ragu-14.py` dan
    `data/alat-sementara/status-per-jenis-14.py`.
- **Jawaban owner:** benar 5 baris, salah 2, tak terbaca 14, bukan plat 99 ("sisanya bukan plat"), motor 0. Owner menulis
  nomor plat untuk dua baris yang salah; nomor itu tidak disalin ke berkas mana pun.
- **Gerbang:** Node 107; lab 190 → 199 → 203; uji image tambahan 17 → 19.
