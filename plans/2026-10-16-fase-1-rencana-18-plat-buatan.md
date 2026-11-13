# Fase 1, Rencana 18: Plat buatan komputer dengan huruf yang digambar sendiri (K35) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37), tanpa titik berhenti untuk owner. Plat buatan tidak memuat data pribadi: teksnya acak, jadi agen
> boleh melihat contohnya untuk memeriksa gambar.

**Goal:** Pembuat plat nomor Indonesia buatan komputer (spec Fase 1 bagian 2; K35) untuk mobil dan motor, lima warna, siang,
malam, dan inframerah, dengan huruf yang digambar sendiri. Bahannya `BOLEH-PRODUK`, jadi bisa melatih mesin jualan.
Kemiripannya dengan plat nyata diukur dari hasil pembaca, bukan diklaim.

**Architecture:** satu modul `tools/lab/plat_buatan.py`, berisi:
- `HURUF`: 36 huruf dan angka, ditambah titik, sebagai garis di kisi 6×10;
- `teks_acak`: teks menurut pola Perpol 7/2021, diperiksa dengan `plat.urai`;
- `plat`: menggambar satu plat;
- `ubah`: variasi;
- `buat`: CLI yang menulis gambar dan `label.csv`.

**Tech Stack:** Python di lab (numpy, cv2).

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Lebar/tinggi kotak plat nyata | Kuantil 10/25/50/75/90: 1,97 / 2,21 / 2,49 / 2,90 / 3,25 (493 kotak, termasuk efek miring) | Label YOLO sisi latih plat-lighting, `data/alat-sementara/rasio-plat-14.py` (tanpa membuka gambar) |
| Tinggi kotak / tinggi foto | Kuantil 10/50/90: 0,023 / 0,042 / 0,077 | sama |
| Warna dan isi plat | Putih/hitam, kuning/hitam, merah/putih, hijau/hitam; kode wilayah, nomor 1–9999, seri 0–3 huruf. Ukuran dan bentuk huruf tidak diatur di peraturan yang terbaca | `docs/peraturan-plat.md` |

Akibatnya:
- **Rentang lebar/tinggi:** motor 2,0–2,6 dan mobil 2,6–3,4.
- **Plat hitam/putih (lama) ikut**, karena masih beredar (S1 di `SEED.md` §5.1).
- **Kode wilayah dibuat acak** (satu atau dua huruf), karena pembaca harus membaca huruf apa pun. Tidak ada daftar kode yang
  disalin.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/plat_buatan.py`, `tools/lab/uji/test_plat_buatan.py` (baru) | Pembuat plat | 1, 2 |
| `data-asal/bahan.json` (ubah) | Butir `plat-buatan`, `BOLEH-PRODUK` | 3 |
| `tools/lab/uji_fpo/test_plat_buatan_baca.py` (baru) | Kemiripan diukur dengan fpo-indo-1 | 4 |

---

### Task 1: Huruf, teks, dan gambar plat

- [x] **Step 1: Uji merah** `tools/lab/uji/test_plat_buatan.py`:

```python
"""Uji tools/lab/plat_buatan.py: huruf yang digambar sendiri lengkap dan di dalam kisi, teks selalu sesuai pola plat Indonesia,
gambar plat berukuran dan berwarna benar, variasi tetap dengan benih, dan CLI yang menulis gambar dan label."""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plat_buatan as pb  # noqa: E402
from plat import urai  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "plat_buatan.py"


def test_huruf_lengkap_dan_di_dalam_kisi():
    assert set(pb.HURUF) == set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.")
    for garis in pb.HURUF.values():
        for g in garis:
            assert len(g) >= 2 and all(0 <= x <= pb.LEBAR_KISI and 0 <= y <= pb.TINGGI_KISI + 0.5 for x, y in g)


def test_teks_acak_selalu_sesuai_pola_dan_beragam():
    teks = [pb.teks_acak(np.random.default_rng(i)) for i in range(500)]

    assert all(urai(t) is not None and urai(t).teks == t for t in teks)
    assert {len(urai(t).seri) for t in teks} == {0, 1, 2, 3}
    assert {len(urai(t).wilayah) for t in teks} == {1, 2}


def test_plat_berukuran_dan_berwarna_benar():
    rng = np.random.default_rng(0)
    gambar = pb.plat("B1234XY", "mobil", "putih", rng, tinggi=96)
    dasar, tulisan = pb.WARNA["putih"]

    assert gambar.shape[0] == 96 and 2.6 * 96 - 1 <= gambar.shape[1] <= 3.4 * 96 + 1
    assert np.abs(gambar[1, gambar.shape[1] // 2].astype(int) - dasar).max() < 40  # dasar di luar bingkai tipis
    assert (np.abs(gambar.astype(int) - tulisan).max(axis=2) < 40).mean() > 0.05  # ada tulisan
    assert not np.array_equal(gambar, pb.plat("D5678AB", "mobil", "putih", np.random.default_rng(0), tinggi=96))


def test_plat_motor_lebih_sempit():
    lebar = [pb.plat("B12AB", "motor", "hitam", np.random.default_rng(i)).shape[1] / 96 for i in range(20)]

    assert all(2.0 - 0.02 <= x <= 2.6 + 0.02 for x in lebar)
```

Run `npm run test:lab; echo "EXIT=$?"` → Expected: `ModuleNotFoundError: No module named 'plat_buatan'`, `EXIT` bukan 0.

- [x] **Step 2: Tulis `tools/lab/plat_buatan.py`** (huruf, teks, plat; `ubah` dan `buat` di Task 2):

```python
"""Plat buatan komputer (Rencana 18, K35): plat nomor Indonesia yang digambar sendiri, untuk melatih pembaca (dan kelak pencari)
dengan bahan BOLEH-PRODUK (data-asal/bahan.json butir plat-buatan).

- HURUF: 36 huruf dan angka (dan titik) yang DIGAMBAR SENDIRI sebagai garis di kisi 6 x 10 (K35, spec 2.7), ditebalkan saat
  digambar. Bentuknya meniru huruf tegak tebal pada plat; kemiripannya diukur dari hasil pembaca, tidak diklaim.
- Isi: pola Perpol 7/2021 (tools/lab/plat.py): kode wilayah 1-2 huruf (acak), nomor urut 1-9999, seri 0-3 huruf; baris kecil
  masa berlaku "MM.YY".
- Warna (docs/peraturan-plat.md): putih/hitam, kuning/hitam, merah/putih, hijau/hitam, ditambah hitam/putih (plat lama).
- Bentuk: lebar/tinggi mobil 2,6-3,4 dan motor 2,0-2,6, dari kuantil kotak plat-lighting (10% 1,97; 50% 2,49; 90% 3,25).
- Variasi (ubah): miring dan perspektif dengan sedikit latar, kecil (tinggi 12-60 px lalu dibesarkan lagi), buram, derau,
  kompresi JPEG, gelap/malam dengan silau, inframerah (kelabu), kotoran.

  buat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/plat_buatan.py buat <jumlah> <keluar> [--benih N]
Keluaran: <keluar>/gambar/NNNNNN.png dan <keluar>/label.csv (berkas, teks, jenis, warna, kondisi). Teksnya acak, bukan plat orang.
"""
import argparse
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

LEBAR_KISI, TINGGI_KISI = 6, 10
HURUF = {
    "0": [[(1, 0), (5, 0), (6, 1), (6, 9), (5, 10), (1, 10), (0, 9), (0, 1), (1, 0)]],
    "1": [[(1.5, 2), (3.5, 0), (3.5, 10)]],
    "2": [[(0, 2), (1, 0), (5, 0), (6, 1), (6, 4), (0, 10), (6, 10)]],
    "3": [[(0, 1), (1, 0), (5, 0), (6, 1), (6, 4), (5, 5), (2, 5)], [(5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "4": [[(5, 10), (5, 0), (0, 7), (6, 7)]],
    "5": [[(6, 0), (0, 0), (0, 5), (5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "6": [[(5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9), (6, 6), (5, 5), (0, 5)]],
    "7": [[(0, 0), (6, 0), (2, 10)]],
    "8": [[(1, 5), (0, 4), (0, 1), (1, 0), (5, 0), (6, 1), (6, 4), (5, 5), (1, 5), (0, 6), (0, 9), (1, 10), (5, 10), (6, 9),
           (6, 6), (5, 5)]],
    "9": [[(6, 5), (1, 5), (0, 4), (0, 1), (1, 0), (5, 0), (6, 1), (6, 9), (5, 10), (1, 10)]],
    "A": [[(0, 10), (0, 2), (2, 0), (4, 0), (6, 2), (6, 10)], [(0, 6), (6, 6)]],
    "B": [[(0, 0), (0, 10), (5, 10), (6, 9), (6, 6), (5, 5), (0, 5)], [(0, 0), (5, 0), (6, 1), (6, 4), (5, 5)]],
    "C": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9)]],
    "D": [[(0, 0), (0, 10), (4, 10), (6, 8), (6, 2), (4, 0), (0, 0)]],
    "E": [[(6, 0), (0, 0), (0, 10), (6, 10)], [(0, 5), (5, 5)]],
    "F": [[(6, 0), (0, 0), (0, 10)], [(0, 5), (5, 5)]],
    "G": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9), (6, 5), (3, 5)]],
    "H": [[(0, 0), (0, 10)], [(6, 0), (6, 10)], [(0, 5), (6, 5)]],
    "I": [[(3, 0), (3, 10)], [(1, 0), (5, 0)], [(1, 10), (5, 10)]],
    "J": [[(6, 0), (6, 9), (5, 10), (1, 10), (0, 9), (0, 7)]],
    "K": [[(0, 0), (0, 10)], [(6, 0), (0, 6)], [(2, 4.5), (6, 10)]],
    "L": [[(0, 0), (0, 10), (6, 10)]],
    "M": [[(0, 10), (0, 0), (3, 5), (6, 0), (6, 10)]],
    "N": [[(0, 10), (0, 0), (6, 10), (6, 0)]],
    "O": [[(2, 0), (4, 0), (6, 2), (6, 8), (4, 10), (2, 10), (0, 8), (0, 2), (2, 0)]],
    "P": [[(0, 10), (0, 0), (5, 0), (6, 1), (6, 4), (5, 5), (0, 5)]],
    "Q": [[(2, 0), (4, 0), (6, 2), (6, 8), (4, 10), (2, 10), (0, 8), (0, 2), (2, 0)], [(3.5, 7), (6, 10.5)]],
    "R": [[(0, 10), (0, 0), (5, 0), (6, 1), (6, 4), (5, 5), (0, 5)], [(3, 5), (6, 10)]],
    "S": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 4), (1, 5), (5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "T": [[(0, 0), (6, 0)], [(3, 0), (3, 10)]],
    "U": [[(0, 0), (0, 9), (1, 10), (5, 10), (6, 9), (6, 0)]],
    "V": [[(0, 0), (3, 10), (6, 0)]],
    "W": [[(0, 0), (1.5, 10), (3, 4), (4.5, 10), (6, 0)]],
    "X": [[(0, 0), (6, 10)], [(6, 0), (0, 10)]],
    "Y": [[(0, 0), (3, 5), (6, 0)], [(3, 5), (3, 10)]],
    "Z": [[(0, 0), (6, 0), (0, 10), (6, 10)]],
    ".": [[(2.6, 9.6), (3.4, 9.6)]],
}
WARNA = {  # nama: (dasar, tulisan), BGR
    "putih": ((235, 235, 235), (20, 20, 20)),
    "hitam": ((25, 25, 25), (230, 230, 230)),
    "kuning": ((40, 200, 235), (20, 20, 20)),
    "merah": ((40, 40, 190), (235, 235, 235)),
    "hijau": ((60, 150, 40), (20, 20, 20)),
}
PELUANG_WARNA = {"putih": 0.45, "hitam": 0.3, "kuning": 0.15, "merah": 0.05, "hijau": 0.05}
RASIO = {"mobil": (2.6, 3.4), "motor": (2.0, 2.6)}
ABJAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def teks_acak(rng):
    """Teks plat acak menurut pola Perpol 7/2021: wilayah 1-2 huruf, nomor 1-9999 tanpa nol di depan, seri 0-3 huruf."""
    wilayah = "".join(rng.choice(list(ABJAD), size=int(rng.choice([1, 2], p=[0.6, 0.4]))))
    panjang = int(rng.integers(1, 5))
    nomor = str(int(rng.integers(1, 10))) + "".join(str(int(d)) for d in rng.integers(0, 10, size=panjang - 1))
    seri = "".join(rng.choice(list(ABJAD), size=int(rng.choice([0, 1, 2, 3], p=[0.05, 0.25, 0.45, 0.25]))))
    return f"{wilayah}{nomor}{seri}"


def gambar_huruf(kanvas, huruf, x, y, lebar, tinggi, tebal, warna):
    for garis in HURUF[huruf]:
        titik = np.array([[x + gx / LEBAR_KISI * lebar, y + gy / TINGGI_KISI * tinggi] for gx, gy in garis], np.float32)
        cv2.polylines(kanvas, [np.round(titik * 16).astype(np.int32)], False, warna, tebal, cv2.LINE_AA, shift=4)


def gambar_baris(kanvas, kelompok, tengah_x, y, tinggi_huruf, lebar_maks, tebal_bagian, warna):
    """Kelompok teks (misalnya ["B", "1234", "XY"]) berjarak antarkelompok, di tengah tengah_x; dikecilkan bila terlalu lebar."""
    lebar_huruf = 0.55 * tinggi_huruf
    jarak, jarak_kelompok = 0.18 * lebar_huruf, 0.7 * lebar_huruf
    huruf_total = sum(len(k) for k in kelompok)
    lebar_total = huruf_total * lebar_huruf + (huruf_total - len(kelompok)) * jarak + (len(kelompok) - 1) * jarak_kelompok
    if lebar_total > lebar_maks:
        s = lebar_maks / lebar_total
        lebar_huruf, jarak, jarak_kelompok, lebar_total = lebar_huruf * s, jarak * s, jarak_kelompok * s, lebar_maks
    tebal = max(1, round(tebal_bagian * lebar_huruf))
    x = tengah_x - lebar_total / 2
    for i, k in enumerate(kelompok):
        for j, h in enumerate(k):
            gambar_huruf(kanvas, h, x, y, lebar_huruf, tinggi_huruf, tebal, warna)
            x += lebar_huruf + (jarak if j < len(k) - 1 else 0)
        if i < len(kelompok) - 1:
            x += jarak_kelompok


def plat(teks, jenis, warna, rng, tinggi=96):
    """Satu plat bersih: dasar berwarna, bingkai tipis, baris nomor, dan baris kecil masa berlaku."""
    p = urai(teks)
    if p is None:
        raise ValueError("teks tidak sesuai pola plat")
    lebar = round(tinggi * rng.uniform(*RASIO[jenis]))
    dasar, tulisan = WARNA[warna]
    kanvas = np.full((tinggi, lebar, 3), dasar, np.uint8)
    tepi = max(1, round(0.04 * tinggi))
    cv2.rectangle(kanvas, (tepi, tepi), (lebar - 1 - tepi, tinggi - 1 - tepi), tulisan, max(1, tepi // 2), cv2.LINE_AA)
    kelompok = [k for k in (p.wilayah, str(p.nomor), p.seri) if k]
    gambar_baris(kanvas, kelompok, lebar / 2, 0.14 * tinggi, 0.56 * tinggi, 0.9 * lebar, 0.16, tulisan)
    masa = f"{int(rng.integers(1, 13)):02d}.{int(rng.integers(24, 31)):02d}"
    gambar_baris(kanvas, [masa], lebar / 2, 0.76 * tinggi, 0.14 * tinggi, 0.4 * lebar, 0.14, tulisan)
    return kanvas
```

Run → Expected: `214 passed` (210 + 4), `EXIT=0`.

- [x] **Step 3: Lihat contoh.** Lembar 24 plat bersih (`data/keluaran/plat-buatan-contoh.png`), dibuat skrip sekali pakai. Agen
  memeriksa bentuk huruf, karena teksnya acak dan tidak memuat data pribadi. Yang janggal diperbaiki dulu, lalu uji dijalankan
  lagi.
- [x] **Step 4: Commit** dengan alasan (K35: huruf digambar sendiri; rasio dari plat-lighting) dan angka gerbang.

### Task 2: Variasi dan CLI

- [x] **Step 1: Uji merah**, ditambahkan di berkas uji yang sama:

```python
def test_ubah_tetap_dengan_benih_dan_inframerah_kelabu():
    bersih = pb.plat("B1234XY", "mobil", "putih", np.random.default_rng(1))
    a, ka = pb.ubah(bersih, np.random.default_rng(5))
    b, kb = pb.ubah(bersih, np.random.default_rng(5))

    assert np.array_equal(a, b) and ka == kb and a.dtype == np.uint8 and a.ndim == 3
    for i in range(60):
        g, kondisi = pb.ubah(bersih, np.random.default_rng(i))
        if "inframerah" in kondisi:
            assert np.array_equal(g[..., 0], g[..., 1]) and np.array_equal(g[..., 1], g[..., 2])
            break
    else:
        raise AssertionError("inframerah tidak pernah terpilih dalam 60 benih")


def test_cli_buat_menulis_gambar_dan_label_yang_tetap(tmp_path):
    jalan = lambda d: subprocess.run([sys.executable, str(SKRIP), "buat", "20", str(d), "--benih", "3"], capture_output=True, text=True)  # noqa: E731
    a, b = jalan(tmp_path / "a"), jalan(tmp_path / "b")

    assert a.returncode == 0 and b.returncode == 0, a.stdout + a.stderr
    baris = list(csv.DictReader(open(tmp_path / "a" / "label.csv", newline="")))
    assert len(baris) == 20 and len(list((tmp_path / "a" / "gambar").glob("*.png"))) == 20
    assert all(urai(r["teks"]) is not None and r["jenis"] in ("mobil", "motor") and r["warna"] in pb.WARNA for r in baris)
    assert (tmp_path / "a" / "label.csv").read_text() == (tmp_path / "b" / "label.csv").read_text()
```

Run → Expected: 2 gagal (`AttributeError: ubah`; CLI keluar bukan 0), `EXIT=1`.

- [x] **Step 2: Tambahkan `ubah`, `buat`, dan `utama`:**

```python
def ubah(gambar, rng):
    """Variasi acak untuk satu plat. Kembali: (gambar, kondisi "a+b+..."). Selalu ada sedikit latar dan kemiringan."""
    kondisi = []
    t, l = gambar.shape[:2]
    pinggir = int(0.12 * t)
    latar = tuple(int(x) for x in rng.integers(30, 200, size=3))
    kanvas = cv2.copyMakeBorder(gambar, pinggir, pinggir, pinggir, pinggir, cv2.BORDER_CONSTANT, value=latar)
    T, L = kanvas.shape[:2]
    asal = np.float32([[pinggir, pinggir], [L - pinggir, pinggir], [L - pinggir, T - pinggir], [pinggir, T - pinggir]])
    goyang = rng.uniform(-0.06, 0.06, size=(4, 2)) * [l, t]
    m = cv2.getPerspectiveTransform(asal, (asal + goyang).astype(np.float32))
    g = cv2.warpPerspective(kanvas, m, (L, T), borderMode=cv2.BORDER_CONSTANT, borderValue=latar)
    if rng.random() < 0.5:
        kondisi.append("kecil")
        tinggi_kecil = int(rng.integers(12, 61))
        s = tinggi_kecil / T
        g = cv2.resize(cv2.resize(g, (max(1, round(L * s)), tinggi_kecil), interpolation=cv2.INTER_AREA), (L, T),
                       interpolation=cv2.INTER_LINEAR)
    if rng.random() < 0.4:
        kondisi.append("buram")
        k = int(rng.choice([3, 5, 7]))
        g = cv2.GaussianBlur(g, (k, k), 0)
    if rng.random() < 0.25:
        kondisi.append("malam")
        g = np.clip(g.astype(np.float32) * rng.uniform(0.2, 0.5), 0, 255).astype(np.uint8)
        if rng.random() < 0.5:
            kondisi.append("silau")
            pusat = (int(rng.integers(0, L)), int(rng.integers(0, T)))
            silau = np.zeros((T, L), np.float32)
            cv2.circle(silau, pusat, int(rng.integers(T // 4, T)), 1.0, -1)
            silau = cv2.GaussianBlur(silau, (0, 0), T / 4)[..., None]
            g = np.clip(g + silau * 200, 0, 255).astype(np.uint8)
    if rng.random() < 0.15:
        kondisi.append("inframerah")
        abu = cv2.cvtColor(g, cv2.COLOR_BGR2GRAY)
        abu = cv2.normalize(abu, None, 0, 255, cv2.NORM_MINMAX)
        g = cv2.cvtColor(abu, cv2.COLOR_GRAY2BGR)
    if rng.random() < 0.2:
        kondisi.append("kotor")
        for _ in range(int(rng.integers(3, 15))):
            abu = int(rng.integers(40, 120))  # kelabu, supaya gambar inframerah tetap kelabu
            cv2.circle(g, (int(rng.integers(0, L)), int(rng.integers(0, T))), int(rng.integers(1, max(2, T // 12))),
                       (abu, abu, abu), -1, cv2.LINE_AA)
    if rng.random() < 0.5:
        kondisi.append("derau")
        g = np.clip(g.astype(np.float32) + rng.normal(0, rng.uniform(3, 12), g.shape), 0, 255).astype(np.uint8)
        if "inframerah" in kondisi:
            g = cv2.cvtColor(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    if rng.random() < 0.6:
        kondisi.append("jpeg")
        _, isi = cv2.imencode(".jpg", g, [cv2.IMWRITE_JPEG_QUALITY, int(rng.integers(20, 91))])
        g = cv2.imdecode(isi, cv2.IMREAD_COLOR)
        if "inframerah" in kondisi:
            g = cv2.cvtColor(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    return g, "+".join(kondisi) or "bersih"


def buat(jumlah, keluar, benih=0):
    """Menulis `jumlah` plat buatan ke keluar/gambar/ dan keluar/label.csv. Kembali: hitungan per jenis dan warna."""
    keluar = Path(keluar)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    hitung = {"jenis": {}, "warna": {}}
    with open(keluar / "label.csv", "w", newline="") as berkas:
        tulis = csv.writer(berkas)
        tulis.writerow(["berkas", "teks", "jenis", "warna", "kondisi"])
        for i in range(jumlah):
            rng = np.random.default_rng([benih, i])
            jenis = "mobil" if rng.random() < 0.6 else "motor"
            warna = str(rng.choice(list(PELUANG_WARNA), p=list(PELUANG_WARNA.values())))
            teks = teks_acak(rng)
            g, kondisi = ubah(plat(teks, jenis, warna, rng, tinggi=int(rng.integers(64, 129))), rng)
            nama = f"{i:06d}.png"
            cv2.imwrite(str(keluar / "gambar" / nama), g)
            tulis.writerow([nama, teks, jenis, warna, kondisi])
            hitung["jenis"][jenis] = hitung["jenis"].get(jenis, 0) + 1
            hitung["warna"][warna] = hitung["warna"].get(warna, 0) + 1
    return hitung


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Plat buatan komputer (Rencana 18, K35).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("buat")
    b.add_argument("jumlah", type=int)
    b.add_argument("keluar")
    b.add_argument("--benih", type=int, default=0)
    p = pengurai.parse_args(argumen)
    try:
        h = buat(p.jumlah, p.keluar, p.benih)
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{p.jumlah} plat buatan: jenis {h['jenis']}, warna {h['warna']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

Run → Expected: `216 passed`, `EXIT=0`.

- [x] **Step 3: Lihat contoh** yang sudah diubah (lembar 24 plat, sekali pakai). Agen memeriksa bahwa variasinya masuk akal: tidak
  hitam total, tidak terpotong.
- [x] **Step 4: Commit.**

### Task 3: Butir bahan

- [x] **Step 1:** Butir `plat-buatan` di `data-asal/bahan.json`, lewat skrip pencatat dengan jangkar tepat sekali:
  - jenis `dataset`;
  - sumber dan bukti lisensi `tools/lab/plat_buatan.py`;
  - lisensi "dibuat sendiri; huruf digambar sendiri (K35)";
  - vonis `BOLEH-PRODUK`;
  - catatan tentang cara membuat dan batasnya.
- [x] **Step 2:** `npm test; echo "EXIT=$?"`, yang juga memeriksa `bahan.json` sungguhan. Expected: hijau. Lalu commit.

### Task 4: Kemiripan diukur dengan pembaca (image tambahan)

- [x] **Step 1:** `tools/lab/uji_fpo/test_plat_buatan_baca.py`, di luar gerbang: fpo-indo-1 membaca 200 plat buatan bersih dan
  200 yang diubah.
  - Persentase terbaca benar dicetak dan dicatat.
  - Uji hanya menuntut kedua angka ada dan bacaan bersih lebih tinggi daripada bacaan yang diubah. Kemiripan tidak diklaim
    lulus.
  - fpo-indo-1 tidak pernah melihat huruf buatan ini, jadi angka bersihnya menunjukkan seberapa mirip huruf kita dengan plat
    nyata.
- [x] **Step 2:** Jalankan di image tambahan, lalu catat angkanya di laporan Rencana 18
  (`bukti/<tanggal>-plat-buatan.md`). Isinya: contoh jumlah per jenis dan warna, angka kemiripan, dan batas (huruf hanya
  mirip, ukuran tidak resmi).
- [x] **Step 3:** ROADMAP dan commit. Lanjut ke Rencana 19 (K37).
