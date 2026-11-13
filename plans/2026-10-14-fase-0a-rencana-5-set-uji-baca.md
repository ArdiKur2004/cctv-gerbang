# Fase 0A, Rencana 5: Set uji pertama untuk langkah baca huruf — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Set uji pertama yang jujur untuk langkah 3 mesin baca plat (baca huruf): diambil dari INDO-ALPR, dibagi ulang
supaya tidak ada plat yang muncul di bahan latih dan bahan uji sekaligus, dikelompokkan mobil atau motor dan terang atau
gelap, labelnya diperiksa owner lewat lembar contoh, dan diukur dengan pembanding pertama: AI serba-bisa Qwen3-VL-2B yang
berjalan di laptop tanpa jaringan.

**Architecture:** Satu modul pola plat (`tools/lab/plat.py`) dipakai bersama oleh tiga alat lab: pembagi set uji,
pembuat lembar contoh untuk owner, dan pembaca Qwen3-VL. Model Qwen3-VL-2B disalin dari vision-seed beserta kuncinya dan
diperiksa SHA-256 tiap berkasnya sebelum dimuat. Semua alat hanya mencetak hitungan; berkas yang memuat nomor plat
tinggal di `data/`.

**Tech Stack:** Python 3.12 dengan OpenCV 4.14, Pillow 12.3, NumPy, torch, transformers, dan pytest 9.1 **yang sudah ada
di image lab** · `tools\lab.ps1` (tanpa jaringan, dengan kartu grafis). Tidak ada yang dipasang dan tidak ada yang
diunduh.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md)
bagian 2.1 (langkah 3 dan 4), 2.5, 8.1 langkah 5 dan 6 (sebagian), 8.3. Keputusan K14, K19, K21 di
[`../SEED.md`](../SEED.md) §3. Peraturan plat di [`../docs/peraturan-plat.md`](../docs/peraturan-plat.md).

---

## Yang diukur sebelum rencana ini ditulis (14 Okt 2026)

Diukur di lab dengan dua skrip sekali pakai di `data/alat-sementara/` (`ukur_dataset.py`, `ukur_nama.py`). Tidak ada
gambar yang dibuka agen; yang dicetak hanya hitungan dan bentuk samaran nama berkas.

| Hal | INDO-ALPR (bagian asli) | Dataset pencahayaan |
|---|---|---|
| Bentuk | **Potongan plat**, bukan foto adegan: lebar tengah 364 titik, tinggi tengah 108, rasio lebar-tinggi tengah 2,98 | Foto adegan utuh 1920×1080 (sebagian 860×931), 1 sampai 4 plat per foto |
| Label | Nomor plat di nama berkas. 4.476 dari 4.712 (latih) dan 1.403 dari 1.462 (uji) sesuai pola plat; sisanya kebanyakan tanpa kode wilayah (bentuk samaran `9999 AAA`) | Kotak letak plat, tanpa teks plat. Lebar plat tengah hanya 5% lebar foto |
| Jenis kendaraan menurut nomor urut (dihitung per gambar) | Latih: mobil penumpang 1.522, motor 818, sisanya bus, barang, khusus. Uji: mobil 478, motor 329 | Tidak diketahui |
| Gelap (terang rata-rata di bawah 60 dari 255) | Latih 276, uji 92 | 54 dari 561 |
| Kode wilayah | 49 kode; terbanyak B (2.947 di latih), lalu AG, E, F | — |
| **Kebocoran pembagian penerbit** | **500 plat muncul di latih dan uji sekaligus; 713 dari 1.462 gambar uji memuat plat yang juga ada di latih** | — |
| Gambar per plat | Kebanyakan satu (2.381 plat di latih); paling banyak 19 (latih) dan 91 (uji) | — |

Akibatnya bagi rencana ini:

1. **Pembagian penerbit tidak bisa dipakai** untuk mengukur: separuh set ujinya pernah "dilihat" saat melatih. Set uji
   dibagi ulang per plat.
2. INDO-ALPR cocok untuk langkah 3 (baca huruf) saja. Langkah 1 (cari plat di foto utuh) butuh dataset pencahayaan dan
   video, dan itu rencana berikutnya.
3. Motor ada (sekitar 1.150 gambar menurut nomor urut; dihitung per gambar, bukan per plat), jadi kelompok motor bisa diukur sejak awal (K7).
4. Siang dan malam menurut spec 8.3 ditentukan dari langit dan sumber cahaya pada gambar utuh. Pada potongan plat itu
   tidak terlihat. Di sini yang dipakai adalah **terang atau gelap potongannya**, dan ditulis begitu, bukan sebagai
   siang atau malam.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1 | Bengkel | Selesai 13 Okt |
| 2 | Vonis izin komponen; peraturan plat | Selesai 13 Okt |
| 3 | Perbaikan pemindai; pemilahan video (K19) | Selesai 13 Okt |
| 4 | Pemeriksa keutuhan video; pintu unduh berkas; pembuka arsip; dua dataset berizin jual | Selesai 14 Okt |
| **5 (dokumen ini)** | Pola plat; set uji baca huruf dari INDO-ALPR; lembar contoh untuk owner; pelabel dan pembanding Qwen3-VL-2B | Ditulis |
| 6 | Pembanding paket jadi (misalnya fast-plate-ocr) pada set uji yang sama; mesin belajar pertama untuk baca huruf; mencari plat di foto utuh dan video; plat buatan komputer; taksiran kecepatan; laporan | Ditulis saat Rencana 5 selesai; dipecah lagi bila terlalu besar |

## Aturan eksekusi untuk semua task

- **Nomor plat tidak keluar dari laptop** (`CLAUDE.md` §4, K19). Agen tidak membuka gambar dataset, lembar contoh,
  `pembagian.json`, `lembar-contoh.json`, atau `hasil.jsonl`; semuanya memuat nomor plat. Yang dibaca agen hanya
  `ringkasan.json` dan keluaran layar alat, yang berisi hitungan saja.
- **Satu suite uji pada satu waktu.** Tanpa `| tail` atau `| head` pada perintah uji.
- **Dua gerbang uji:** `npm test` (Node, di host) dan `npm run test:lab` (Python, di lab tanpa jaringan). Kode 3 dari
  gerbang lab berarti bengkel sedang dipakai job lain; kode 6 bisa berarti Docker Desktop belum menyala
  (`D:\Docker\Docker Desktop.exe`). Keduanya bukan uji merah.
- **Satu job kartu grafis pada satu waktu:** periksa `nvidia-smi` sebelum menjalankan Qwen3-VL.
- **Perintah yang memuat jalur `/kerja/...` dijalankan lewat PowerShell.** `npm run test:lab` aman dari Git Bash.
- **vision-seed hanya dibaca.** Jangan `cd` ke sana; pakai jalur mutlak.
- Skrip sekali pakai ditulis sebagai **berkas**, tidak diketik di baris perintah (garis miring terbalik pernah hilang).
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri baris
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Perintah lain dijalankan dari akar repo `D:\Projects\super-team-v1\cctvgerbang-seed` lewat Git Bash.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/plat.py` (baru) | Pola nomor polisi; golongan kendaraan menurut nomor urut; pengurai nama berkas INDO-ALPR | 1 |
| `tools/lab/uji/test_plat.py` (baru) | Ujinya | 1 |
| `tools/lab/bagi_set_uji.py` (baru) | Membagi ulang INDO-ALPR per plat; kelompok; ringkasan tanpa nomor plat | 2 |
| `tools/lab/uji/test_bagi_set_uji.py` (baru) | Ujinya | 2 |
| `tools/lab/lembar_contoh.py` (baru) | Lembar contoh label untuk diperiksa owner | 3 |
| `tools/lab/uji/test_lembar_contoh.py` (baru) | Ujinya | 3 |
| `tools/lab/model_terkunci.py` (baru) | Gerbang folder model: isinya harus persis yang dikunci | 4 |
| `tools/lab/uji/test_model_terkunci.py` (baru) | Ujinya | 4 |
| `tools/vendor.lock.json` (ubah) | Daftar `model_hf` dengan Qwen3-VL-2B, disalin dari kunci vision-seed | 4 |
| `tools/lab/baca_vlm.py` (baru) | Pembaca Qwen3-VL dan penilai per gambar dan per kedatangan | 5 |
| `tools/lab/uji/test_baca_vlm.py` (baru) | Ujinya (pembaca diganti tiruan) | 5 |
| `tools/lab/uji_gpu/test_gpu_baca_vlm.py` (baru) | Uji dengan model sungguhan, di luar gerbang biasa | 5 |
| `bukti/2026-10-14-baca-huruf-pertama.md` dan dua `*.json` (baru) | Laporan angka, tanpa nomor plat | 6 |
| `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Catatan | 6 |

---

### Task 1: Pola plat dan golongan kendaraan

**Files:**
- Create: `tools/lab/plat.py`
- Create: `tools/lab/uji/test_plat.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_plat.py`:

```python
"""Uji tools/lab/plat.py: pola nomor polisi Indonesia dan golongan kendaraan menurut nomor urut (Perpol 7/2021)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plat import Plat, golongan, kelompok_kendaraan, urai, urai_nama_indo_alpr  # noqa: E402


def test_plat_dengan_spasi_diurai():
    plat = urai("B 1234 XYZ")

    assert plat == Plat("B", 1234, "XYZ")
    assert plat.teks == "B1234XYZ"


def test_huruf_kecil_dan_seri_kosong_diterima():
    assert urai("ag 12 a") == Plat("AG", 12, "A")
    assert urai("D1") == Plat("D", 1, "")


@pytest.mark.parametrize("teks", ["1234 XYZ", "ABC 12 X", "B 12345 X", "B 0123 X", "B 1234 WXYZ", ""])
def test_bentuk_di_luar_pola_ditolak(teks):
    assert urai(teks) is None


def test_nama_berkas_indo_alpr_diurai():
    assert urai_nama_indo_alpr("B 1234 XYZ_0001.png") == Plat("B", 1234, "XYZ")
    # Empat nama berkas di dataset memuat spasi di dalam seri huruf; dibaca sebagai satu seri.
    assert urai_nama_indo_alpr("D 2345 A B_0007.jpg") == Plat("D", 2345, "AB")


def test_nama_berkas_tanpa_kode_wilayah_atau_tanpa_urutan_ditolak():
    assert urai_nama_indo_alpr("1234 XYZ_12.png") is None
    assert urai_nama_indo_alpr("tanpa-garis-bawah.png") is None


@pytest.mark.parametrize("nomor, nama", [(1999, "mobil"), (2000, "motor"), (6999, "motor"), (7000, "bus"),
                                         (8000, "barang"), (9000, "khusus")])
def test_golongan_di_luar_polda_metro_jaya(nomor, nama):
    assert golongan(Plat("D", nomor, "AB")) == nama


@pytest.mark.parametrize("nomor, nama", [(2999, "mobil"), (3000, "motor"), (8500, "mobil"), (9000, "barang-khusus")])
def test_golongan_di_polda_metro_jaya(nomor, nama):
    assert golongan(Plat("B", nomor, "AB")) == nama


def test_kelompok_kendaraan_hanya_mobil_atau_motor():
    assert kelompok_kendaraan(Plat("D", 2000, "AB")) == "motor"
    assert kelompok_kendaraan(Plat("B", 2500, "AB")) == "mobil"
    assert kelompok_kendaraan(Plat("D", 7500, "AB")) == "mobil"  # bus dihitung kelompok mobil (K9: mobil dan motor)
```

- [x] **Step 2: Jalankan, pastikan merah karena modulnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat saat mengumpulkan uji, `ModuleNotFoundError: No module named 'plat'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis modulnya**

Buat `tools/lab/plat.py`:

```python
"""Pola nomor polisi Indonesia dan golongan kendaraan menurut nomor urut (spec bagian 2.1 langkah 4).

Dasar: Perpol 7/2021 (docs/peraturan-plat.md). NRKB = kode wilayah (1-2 huruf) + nomor urut (1-9999) + seri huruf
(0-3 huruf). Golongan menurut nomor urut, Lampiran hlm. 93: di luar Polda Metro Jaya 1-1999 mobil penumpang,
2000-6999 sepeda motor, 7000-7999 bus, 8000-8999 mobil barang, 9000-9999 kendaraan khusus; di wilayah Polda Metro Jaya
1-2999 mobil penumpang, 3000-6999 sepeda motor, 7000-7999 bus, 8000-8999 mobil penumpang, 9000-9999 mobil barang dan
kendaraan khusus.

Anggapan agen yang belum diperiksa ke lampiran kode wilayah: kode "B" = wilayah Polda Metro Jaya. Golongan dari nomor
urut adalah taksiran dari peraturan, bukan jenis kendaraan yang terlihat. Plat berpola lain (CD, CC, dinas) belum
dikenali dan dianggap di luar pola.
"""
import re
from dataclasses import dataclass

POLA = re.compile(r"^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$")
KODE_METRO = {"B"}
BATAS_UMUM = ((1999, "mobil"), (6999, "motor"), (7999, "bus"), (8999, "barang"), (9999, "khusus"))
BATAS_METRO = ((2999, "mobil"), (6999, "motor"), (7999, "bus"), (8999, "mobil"), (9999, "barang-khusus"))


@dataclass(frozen=True)
class Plat:
    wilayah: str
    nomor: int
    seri: str

    @property
    def teks(self):
        return f"{self.wilayah}{self.nomor}{self.seri}"


def bersihkan(teks):
    """Huruf besar, hanya huruf dan angka."""
    return re.sub(r"[^A-Z0-9]", "", str(teks).upper())


def urai(teks):
    """Plat bila `teks` (sesudah dibersihkan) sesuai pola nomor polisi Indonesia, selain itu None."""
    cocok = POLA.match(bersihkan(teks))
    if not cocok or cocok[2].startswith("0"):
        return None
    return Plat(cocok[1], int(cocok[2]), cocok[3])


def urai_nama_indo_alpr(nama_berkas):
    """Plat dari nama berkas INDO-ALPR ("<plat>_<urutan>.<akhiran>"), atau None bila bagian platnya tidak sesuai pola."""
    batang = nama_berkas.rsplit(".", 1)[0]
    depan, garis, _ = batang.rpartition("_")
    return urai(depan) if garis else None


def golongan(plat):
    """Jenis kendaraan menurut nomor urut: mobil, motor, bus, barang, khusus, atau barang-khusus (Polda Metro Jaya)."""
    batas = BATAS_METRO if plat.wilayah in KODE_METRO else BATAS_UMUM
    return next(nama for atas, nama in batas if plat.nomor <= atas)


def kelompok_kendaraan(plat):
    """Kelompok K9: "motor" untuk nomor urut sepeda motor, "mobil" untuk selainnya."""
    return "motor" if golongan(plat) == "motor" else "mobil"
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `72 passed` (51 lama + 21 baru) dan `EXIT=0`.

- [x] **Step 5: Commit**

```bash
git add tools/lab/plat.py tools/lab/uji/test_plat.py
git commit -q -F - <<'EOF'
Pola nomor polisi Indonesia dan golongan kendaraan menurut nomor urut

Alasan: tiga alat Rencana 5 butuh cara yang sama untuk membaca label
INDO-ALPR, mengenali bacaan yang di luar pola, dan memisahkan mobil dari
motor. Ini juga bahan langkah 4 mesin baca plat (cek pola, spec 2.1).

Dasarnya Perpol 7/2021: kode wilayah, nomor urut 1-9999, seri 0-3 huruf;
golongan menurut nomor urut dari Lampiran hlm. 93, dengan aturan Polda
Metro Jaya tersendiri. Kode B dianggap Polda Metro Jaya: anggapan agen yang
ditulis di kepala modul, belum diperiksa ke lampiran kode wilayah.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 51 -> 72.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Pembagi set uji per plat

**Files:**
- Create: `tools/lab/bagi_set_uji.py`
- Create: `tools/lab/uji/test_bagi_set_uji.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_bagi_set_uji.py`:

```python
"""Uji tools/lab/bagi_set_uji.py: tidak ada plat di dua sisi, pembagian tetap, dan ringkasan tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bagi_set_uji as bs  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "bagi_set_uji.py"


def gambar(jalur, terang=150):
    jalur.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.full((10, 30), terang, np.uint8)).save(jalur)
    return jalur


def cari(pembagian, teks):
    return next(a for s in ("latih", "uji") for a in pembagian[s] if a["teks"] == teks)


def jalankan(tmp_path):
    keluar = tmp_path / "keluar"
    assert bs.utama(tmp_path / "original", keluar) == 0
    return json.loads((keluar / "pembagian.json").read_text()), json.loads((keluar / "ringkasan.json").read_text())


def test_plat_yang_sama_di_latih_dan_uji_penerbit_masuk_satu_sisi(tmp_path):
    # Inilah kebocoran yang terukur 14 Okt: 500 plat ada di latih dan uji penerbit sekaligus.
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")
    gambar(tmp_path / "original/test/D 2345 AB_0002.png")

    pembagian, ringkasan = jalankan(tmp_path)

    semua = pembagian["latih"] + pembagian["uji"]
    assert [a["teks"] for a in semua] == ["D2345AB"]
    assert sorted(semua[0]["berkas"]) == ["test/D 2345 AB_0002.png", "train/D 2345 AB_0001.png"]
    assert ringkasan["plat_di_kedua_sisi"] == 0


def test_pembagian_tetap_bila_dijalankan_ulang(tmp_path):
    for n in range(1, 40):
        gambar(tmp_path / f"original/train/D {n} AB_0001.png")

    bs.utama(tmp_path / "original", tmp_path / "satu")
    bs.utama(tmp_path / "original", tmp_path / "dua")

    assert (tmp_path / "satu/pembagian.json").read_text() == (tmp_path / "dua/pembagian.json").read_text()


def test_sekitar_seperempat_plat_masuk_uji(tmp_path):
    for n in range(1, 401):
        gambar(tmp_path / f"original/train/D {n} AB_0001.png")

    _, ringkasan = jalankan(tmp_path)

    bagian = ringkasan["sisi"]["uji"]["kedatangan"] / 400
    assert 0.18 < bagian < 0.32, bagian


def test_nama_tak_sesuai_pola_dikecualikan_dan_dihitung(tmp_path):
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")
    gambar(tmp_path / "original/train/2345 AB_0002.png")

    pembagian, ringkasan = jalankan(tmp_path)

    assert ringkasan["dikecualikan_tak_sesuai_pola"] == 1
    assert len(pembagian["latih"] + pembagian["uji"]) == 1


def test_kelompok_dari_nomor_urut_dan_terang(tmp_path):
    gambar(tmp_path / "original/train/D 1500 X_0001.png", terang=200)
    gambar(tmp_path / "original/train/D 3000 X_0001.png", terang=20)

    pembagian, _ = jalankan(tmp_path)

    assert cari(pembagian, "D1500X")["kelompok"] == "mobil-terang"
    assert cari(pembagian, "D3000X")["kelompok"] == "motor-gelap"


def test_ringkasan_tanpa_teks_plat_dan_kelompok_kosong_tetap_ditulis(tmp_path):
    gambar(tmp_path / "original/train/D 1500 X_0001.png")
    gambar(tmp_path / "original/test/D 3000 X_0001.png")

    jalankan(tmp_path)

    teks = (tmp_path / "keluar/ringkasan.json").read_text()
    for larangan in ("D1500X", "D3000X", "1500", "3000", ".png"):
        assert larangan not in teks
    ringkasan = json.loads(teks)
    for s in ("latih", "uji"):
        assert set(ringkasan["sisi"][s]["per_kelompok"]) == set(bs.KELOMPOK)


def test_baris_perintah_sampai_ke_berkas_tanpa_mencetak_plat(tmp_path):
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "original"), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/pembagian.json").exists() and (tmp_path / "keluar/ringkasan.json").exists()
    assert "plat di kedua sisi: 0" in hasil.stdout
    assert "2345" not in hasil.stdout
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'bagi_set_uji'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/bagi_set_uji.py`:

```python
"""Membagi ulang INDO-ALPR menjadi bahan latih dan set uji per PLAT, bukan per gambar (spec bagian 8.3).

Pembagian dari penerbitnya bocor: diukur 14 Okt, 713 dari 1.462 gambar uji memuat plat yang juga ada di bagian latih.
Di sini semua gambar berplat sama masuk ke satu sisi saja. Satu plat = satu "kedatangan" (taksiran: gambar berplat sama
dianggap kendaraan yang sama; spec mendefinisikan kedatangan dari video, yang tidak ada di dataset ini).

Sisi tiap plat ditentukan dari SHA-256 teks platnya (UJI_DARI_EMPAT dari empat bagian), jadi pembagiannya tetap setiap
kali dijalankan tanpa angka acak. Gambar yang nama berkasnya tidak sesuai pola plat dikecualikan dan dihitung.

Kelompok per kedatangan: "mobil" atau "motor" dari nomor urut (tools/lab/plat.py), dan "terang" atau "gelap" dari terang
rata-rata gambarnya (di bawah AMBANG_GELAP = gelap). Terang-gelap ini taksiran dari potongan plat, BUKAN siang-malam
menurut spec bagian 8.3, yang ditentukan dari langit dan sumber cahaya pada gambar utuh.

Keluaran di folder keluaran:
- pembagian.json: daftar kedatangan per sisi, beserta teks plat dan nama berkas. Memuat nomor plat: tinggal di data/.
- ringkasan.json: hitungan saja, tanpa teks plat atau nama berkas. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/bagi_set_uji.py /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/set-uji-baca
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import golongan, kelompok_kendaraan, urai_nama_indo_alpr  # noqa: E402

AKHIRAN_GAMBAR = {".png", ".jpg", ".jpeg"}
KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
UJI_DARI_EMPAT = 1
AMBANG_GELAP = 60
SEDIKIT = 30  # kelompok dengan kedatangan lebih sedikit dari ini: "terlalu sedikit untuk disimpulkan" (spec 8.3)


def sisi(teks):
    """"uji" untuk kira-kira UJI_DARI_EMPAT dari empat plat, selain itu "latih". Selalu sama untuk teks yang sama."""
    return "uji" if int(hashlib.sha256(teks.encode()).hexdigest()[:8], 16) % 4 < UJI_DARI_EMPAT else "latih"


def terang(jalur):
    """Terang rata-rata 0-255 sesudah gambar dikecilkan menjadi 32x32 kelabu."""
    with Image.open(jalur) as gambar:
        return float(np.asarray(gambar.convert("L").resize((32, 32))).mean())


def kumpulkan(folder):
    """Gambar dari semua subfolder, dikelompokkan per plat. Kembali: (plat -> daftar jalur, jumlah dikecualikan)."""
    per_plat, dikecualikan = defaultdict(list), 0
    for jalur in sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in AKHIRAN_GAMBAR):
        plat = urai_nama_indo_alpr(jalur.name)
        if plat is None:
            dikecualikan += 1
        else:
            per_plat[plat].append(jalur)
    return per_plat, dikecualikan


def utama(folder, keluar):
    folder, keluar = Path(folder), Path(keluar)
    per_plat, dikecualikan = kumpulkan(folder)
    pembagian = {"latih": [], "uji": []}
    hitung = {s: {k: Counter() for k in KELOMPOK} for s in pembagian}
    golongan_sisi = {s: Counter() for s in pembagian}
    for plat in sorted(per_plat, key=lambda p: p.teks):
        jalur = per_plat[plat]
        cahaya = float(np.mean([terang(j) for j in jalur]))
        kelompok = f"{kelompok_kendaraan(plat)}-{'gelap' if cahaya < AMBANG_GELAP else 'terang'}"
        s = sisi(plat.teks)
        pembagian[s].append({"teks": plat.teks, "golongan": golongan(plat), "kelompok": kelompok,
                             "terang": round(cahaya, 1), "berkas": [j.relative_to(folder).as_posix() for j in jalur]})
        hitung[s][kelompok]["kedatangan"] += 1
        hitung[s][kelompok]["gambar"] += len(jalur)
        golongan_sisi[s][golongan(plat)] += 1
    bocor = len({a["teks"] for a in pembagian["latih"]} & {a["teks"] for a in pembagian["uji"]})
    ringkasan = {
        "sumber": "INDO-ALPR bagian original: train dan test penerbit digabung, lalu dibagi ulang per plat",
        "aturan": {"uji_dari_empat": UJI_DARI_EMPAT, "ambang_gelap": AMBANG_GELAP, "sedikit": SEDIKIT},
        "dikecualikan_tak_sesuai_pola": dikecualikan,
        "plat_di_kedua_sisi": bocor,
        "sisi": {s: {"kedatangan": len(pembagian[s]), "gambar": sum(len(a["berkas"]) for a in pembagian[s]),
                     "per_kelompok": {k: {"kedatangan": hitung[s][k]["kedatangan"], "gambar": hitung[s][k]["gambar"],
                                          "terlalu_sedikit": hitung[s][k]["kedatangan"] < SEDIKIT} for k in KELOMPOK},
                     "per_golongan": dict(sorted(golongan_sisi[s].items()))}
                 for s in pembagian},
    }
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian.json").write_text(json.dumps(pembagian, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for s in ("latih", "uji"):
        r = ringkasan["sisi"][s]
        print(f"{s}: {r['kedatangan']} kedatangan, {r['gambar']} gambar")
        for k in KELOMPOK:
            n = r["per_kelompok"][k]
            catatan = "  (terlalu sedikit untuk disimpulkan)" if n["terlalu_sedikit"] else ""
            print(f"  {k:<13}{n['kedatangan']:>6} kedatangan{n['gambar']:>7} gambar{catatan}")
        print(f"  golongan: {r['per_golongan']}")
    print(f"dikecualikan (nama berkas tak sesuai pola plat): {dikecualikan}")
    print(f"plat di kedua sisi: {bocor}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Pakai: python bagi_set_uji.py <folder-original> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2]))
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `79 passed` (72 + 7 baru) dan `EXIT=0`.

- [x] **Step 5: Jalankan pada INDO-ALPR sungguhan**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/bagi_set_uji.py /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/set-uji-baca; "EXIT=$LASTEXITCODE"`

Expected: `EXIT=0`; `dikecualikan (nama berkas tak sesuai pola plat): ` sekitar 295 (236 + 59 dari pengukuran 14 Okt,
kurang sedikit karena empat nama berspasi di dalam seri kini diterima); `plat di kedua sisi: 0`; sisi uji sekitar
seperempat dari seluruh plat. Angka per kelompok dicatat apa adanya; kelompok di bawah 30 kedatangan bertanda "terlalu
sedikit untuk disimpulkan".

Run: `git status --short`
Expected: kosong (keluaran ada di `data/`).

- [x] **Step 6: Commit**

```bash
git add tools/lab/bagi_set_uji.py tools/lab/uji/test_bagi_set_uji.py
git commit -q -F - <<'EOF'
Pembagi set uji INDO-ALPR per plat, bukan per gambar

Alasan: pembagian dari penerbit bocor. Diukur 14 Okt: 713 dari 1.462 gambar
uji memuat plat yang juga ada di bagian latih, jadi angka dari set uji itu
akan terlalu bagus. Spec 8.3 menuntut latih dan uji dipisah per sumber.

Di sini semua gambar berplat sama masuk ke satu sisi, sisinya ditentukan
dari SHA-256 teks plat (tetap tanpa angka acak), dan tiap kedatangan diberi
kelompok mobil atau motor (nomor urut) dan terang atau gelap (taksiran dari
potongan plat, bukan siang-malam). Ringkasannya tanpa nomor plat.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 72 -> 79. Pada
INDO-ALPR sungguhan: <angka dari Step 5>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

Isian `<angka dari Step 5>` diganti angka yang terbaca (kedatangan dan gambar per sisi, dikecualikan, plat di kedua sisi).

---

### Task 3: Lembar contoh untuk owner

**Files:**
- Create: `tools/lab/lembar_contoh.py`
- Create: `tools/lab/uji/test_lembar_contoh.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_lembar_contoh.py`:

```python
"""Uji tools/lab/lembar_contoh.py: contoh dipilih tetap per kelompok dari set uji, dan layar tidak memuat nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_contoh as lc  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_contoh.py"


def siapkan(tmp_path, jumlah):
    """Pembagian tiruan: `jumlah` = {kelompok: banyak kedatangan}, satu gambar per kedatangan."""
    folder = tmp_path / "gambar"
    (folder / "train").mkdir(parents=True)
    uji, n = [], 0
    for kelompok, banyak in jumlah.items():
        for _ in range(banyak):
            n += 1
            nama = f"train/D {1000 + n} AB_0001.png"
            cv2.imwrite(str(folder / nama), np.full((30, 100, 3), 200, np.uint8))
            uji.append({"teks": f"D{1000 + n}AB", "kelompok": kelompok, "berkas": [nama]})
    pembagian = {"latih": [{"teks": "D9999AB", "kelompok": "mobil-terang", "berkas": ["train/x.png"]}], "uji": uji}
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))
    return pembagian, berkas, folder


def test_contoh_dipilih_per_kelompok_tetap_dan_hanya_dari_uji(tmp_path):
    pembagian, _, _ = siapkan(tmp_path, {"mobil-terang": 20, "motor-gelap": 3})

    pertama = lc.pilih(pembagian)

    kelompok = [a["kelompok"] for a in pertama]
    assert kelompok.count("mobil-terang") == lc.PER_KELOMPOK and kelompok.count("motor-gelap") == 3
    assert pertama == lc.pilih(pembagian)
    assert all(a["teks"] != "D9999AB" for a in pertama)


def test_lembar_dan_daftarnya_ditulis(tmp_path):
    _, berkas, folder = siapkan(tmp_path, {"mobil-terang": 20, "motor-gelap": 3})
    keluar = tmp_path / "keluar"

    assert lc.utama(berkas, folder, keluar) == 0

    lembar = cv2.imread(str(keluar / "lembar-contoh-1.png"))
    assert lembar.shape == (18 * (lc.TINGGI + 8), lc.LEBAR_NOMOR + lc.LEBAR_POTONGAN + lc.LEBAR_TEKS, 3)
    daftar = json.loads((keluar / "lembar-contoh.json").read_text())
    assert [c["nomor"] for c in daftar["contoh"]] == list(range(1, 19))
    assert daftar["halaman"] == ["lembar-contoh-1.png"]


def test_keluaran_layar_tanpa_teks_plat(tmp_path, capsys):
    _, berkas, folder = siapkan(tmp_path, {"motor-terang": 2})

    lc.utama(berkas, folder, tmp_path / "keluar")

    cetak = capsys.readouterr().out
    assert "D1001AB" not in cetak and "1001" not in cetak
    assert "agen tidak membukanya" in cetak


def test_baris_perintah(tmp_path):
    _, berkas, folder = siapkan(tmp_path, {"mobil-gelap": 1})

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), str(berkas)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/lembar-contoh-1.png").exists()
    assert salah.returncode == 2
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'lembar_contoh'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/lembar_contoh.py`:

```python
"""Lembar contoh label untuk diperiksa OWNER (K19): potongan plat dari set uji beserta label penerbitnya.

Lembar ini memuat plat yang terbaca, jadi agen TIDAK PERNAH membukanya (CLAUDE.md §7). Owner membuka berkas PNG-nya di
laptop dan menyebut nomor baris yang labelnya tidak sama dengan platnya. Dari situ terukur seberapa sering label
penerbit salah.

Contoh dipilih tetap, bukan acak: per kelompok, kedatangan diurutkan menurut SHA-256 teks platnya, lalu diambil
PER_KELOMPOK yang pertama; satu gambar per kedatangan (yang pertama). Kelompok yang lebih kecil diambil semuanya.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_contoh.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-contoh
"""
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
PER_KELOMPOK = 15
PER_LEMBAR = 20
TINGGI = 72  # tinggi potongan plat di lembar, piksel
LEBAR_NOMOR = 70
LEBAR_POTONGAN = 320
LEBAR_TEKS = 300


def pilih(pembagian):
    terpilih = []
    for kelompok in KELOMPOK:
        anggota = [a for a in pembagian["uji"] if a["kelompok"] == kelompok]
        anggota.sort(key=lambda a: hashlib.sha256(a["teks"].encode()).hexdigest())
        terpilih += anggota[:PER_KELOMPOK]
    return terpilih


def tulisan(teks):
    """Label dengan spasi, seperti tertulis di plat: "B 1234 XYZ"."""
    plat = urai(teks)
    return f"{plat.wilayah} {plat.nomor} {plat.seri}".strip() if plat else teks


def baris(nomor, gambar, teks):
    kanvas = np.full((TINGGI + 8, LEBAR_NOMOR + LEBAR_POTONGAN + LEBAR_TEKS, 3), 255, np.uint8)
    if gambar is None:
        cv2.putText(kanvas, "gambar tak terbaca", (LEBAR_NOMOR + 8, TINGGI // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
    else:
        tinggi, lebar = gambar.shape[:2]
        skala = min(TINGGI / tinggi, LEBAR_POTONGAN / lebar)
        cara = cv2.INTER_AREA if skala < 1 else cv2.INTER_CUBIC
        kecil = cv2.resize(gambar, (max(1, round(lebar * skala)), max(1, round(tinggi * skala))), interpolation=cara)
        kanvas[4:4 + kecil.shape[0], LEBAR_NOMOR:LEBAR_NOMOR + kecil.shape[1]] = kecil
    cv2.putText(kanvas, str(nomor), (6, TINGGI // 2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(kanvas, tulisan(teks), (LEBAR_NOMOR + LEBAR_POTONGAN + 12, TINGGI // 2 + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (160, 0, 0), 2)
    return kanvas


def utama(berkas_pembagian, folder_gambar, keluar):
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    barisan, contoh = [], []
    for nomor, kedatangan in enumerate(pilih(pembagian), 1):
        berkas = kedatangan["berkas"][0]
        barisan.append(baris(nomor, cv2.imread(str(Path(folder_gambar) / berkas)), kedatangan["teks"]))
        contoh.append({"nomor": nomor, "kelompok": kedatangan["kelompok"], "berkas": berkas, "teks": kedatangan["teks"]})
    if not barisan:
        print("Set uji kosong: tidak ada lembar yang dibuat.")
        return 1
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-contoh-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-contoh.json").write_text(json.dumps({"per_kelompok": PER_KELOMPOK, "halaman": halaman, "contoh": contoh}, indent=1))
    jumlah = {k: sum(c["kelompok"] == k for c in contoh) for k in KELOMPOK}
    print(f"{len(contoh)} contoh {jumlah} -> {len(halaman)} lembar di {keluar}. "
          "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python lembar_contoh.py <pembagian.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `83 passed` (79 + 4 baru) dan `EXIT=0`.

- [x] **Step 5: Buat lembar dari set uji sungguhan, tanpa membukanya**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_contoh.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-contoh; "EXIT=$LASTEXITCODE"`
Expected: `60 contoh {...} -> 3 lembar di /kerja/data/keluaran/lembar-contoh. ... agen tidak membukanya.` dan `EXIT=0`
(lebih sedikit dari 60 bila ada kelompok di bawah 15 kedatangan). **Agen tidak membuka berkas-berkas itu.** Owner
diminta memeriksanya di Task 6.

- [x] **Step 6: Commit**

```bash
git add tools/lab/lembar_contoh.py tools/lab/uji/test_lembar_contoh.py
git commit -q -F - <<'EOF'
Lembar contoh label untuk diperiksa owner

Alasan: label INDO-ALPR (nomor plat di nama berkas) belum pernah diperiksa
siapa pun di sini. Spec 8.1 langkah 5 menuntut label set uji diperiksa
manusia, dan K19 menetapkan owner yang memeriksa label huruf plat dari
lembar contoh di laptop.

Contoh dipilih tetap per kelompok (15 per kelompok, satu gambar per
kedatangan), dengan nomor baris dan label di sebelah potongan platnya.
Lembar memuat plat yang terbaca, jadi agen tidak membukanya; layar hanya
mencetak hitungan.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 79 -> 83.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Qwen3-VL-2B disalin dari vision-seed dan dikunci

Vision-seed sudah mengunduh model ini pada 10 Okt dari organisasi aslinya, pada revisi yang dipin, dengan SHA-256 tiap
berkas (`vision-seed/tools/vendor.lock.json`, `model_hf`). Repo ini menyalinnya (K14) dan memeriksa ulang tiap berkas.

**Files:**
- Create: `tools/lab/model_terkunci.py`
- Create: `tools/lab/uji/test_model_terkunci.py`
- Modify: `tools/vendor.lock.json`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_model_terkunci.py`:

```python
"""Uji tools/lab/model_terkunci.py: folder model hanya boleh dimuat bila isinya persis yang dikunci."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model_terkunci as mt  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "model_terkunci.py"


def siapkan(tmp_path):
    folder = tmp_path / "model-contoh"
    folder.mkdir()
    isi = {"config.json": b"{}", "model.safetensors": b"bobot"}
    for nama, data in isi.items():
        (folder / nama).write_bytes(data)
    kunci = tmp_path / "vendor.lock.json"
    kunci.write_text(json.dumps({"model_hf": [{"nama": "model-contoh",
                                               "berkas": {n: hashlib.sha256(d).hexdigest() for n, d in isi.items()}}]}))
    return folder, mt.daftar_model_hf(kunci)


def test_folder_yang_persis_sama_dengan_kunci_diterima(tmp_path):
    folder, daftar = siapkan(tmp_path)

    assert mt.verifikasi_folder_model(folder, daftar) == folder


def test_berkas_tambahan_membuat_folder_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "selundupan.py").write_text("import os")

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar"):
        mt.verifikasi_folder_model(folder, daftar)


def test_berkas_yang_berubah_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "model.safetensors").write_bytes(b"ditukar")

    with pytest.raises(mt.ModelDitolak, match="SHA-256"):
        mt.verifikasi_folder_model(folder, daftar)


def test_berkas_yang_hilang_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "config.json").unlink()

    with pytest.raises(mt.ModelDitolak, match="tidak ada"):
        mt.verifikasi_folder_model(folder, daftar)


def test_folder_yang_tidak_terdaftar_ditolak(tmp_path):
    _, daftar = siapkan(tmp_path)
    lain = tmp_path / "model-lain"
    lain.mkdir()

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar di kunci model"):
        mt.verifikasi_folder_model(lain, daftar)


def test_kunci_repo_mencatat_pelabel_qwen3_vl():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa butir ini pelabel tidak bisa dimuat sama sekali.
    berkas = mt.daftar_model_hf()["qwen3-vl-2b-instruct"]

    assert "model.safetensors" in berkas and len(berkas) == 11


def test_baris_perintah_menolak_folder_tak_terdaftar_dengan_kode_1(tmp_path):
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(lain)], capture_output=True, text=True)

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'model_terkunci'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis gerbangnya**

Buat `tools/lab/model_terkunci.py`:

```python
"""Gerbang folder model Hugging Face: isi folder harus PERSIS yang dicatat di tools/vendor.lock.json (model_hf).

Asal: disalin dari vision-seed @3591530 (inti/deteksi/bobot.py: sha256_berkas, daftar_model_hf,
verifikasi_folder_model) pada 2026-10-14 (K14). Yang diubah: hanya bagian model Hugging Face yang diambil, letak kunci,
nama galat, dan baris perintah untuk memeriksa satu folder. Berkas yang tak terdaftar membuat seluruh folder ditolak,
dan alat lab tidak pernah mengunduh model sendiri.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/model_terkunci.py /kerja/models/qwen3-vl-2b-instruct
"""
import hashlib
import json
import sys
from pathlib import Path

LOKASI_KUNCI = Path(__file__).resolve().parents[1] / "vendor.lock.json"


class ModelDitolak(Exception):
    """Folder model tak boleh dimuat: tak terdaftar, berkasnya lebih atau kurang, atau isinya berubah."""


def sha256_berkas(berkas):
    sidik = hashlib.sha256()
    with Path(berkas).open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            sidik.update(blok)
    return sidik.hexdigest()


def daftar_model_hf(lokasi=LOKASI_KUNCI):
    """Nama folder -> {nama berkas: sha256}, dari daftar model_hf di kunci."""
    isi = json.loads(Path(lokasi).read_text(encoding="utf-8"))
    return {e["nama"]: {n: s.lower() for n, s in e["berkas"].items()} for e in isi.get("model_hf", [])}


def verifikasi_folder_model(folder, daftar):
    folder = Path(folder)
    berkas = daftar.get(folder.name)
    if berkas is None:
        raise ModelDitolak(f"{folder.name}: tidak terdaftar di kunci model (tools/vendor.lock.json, model_hf)")
    ada = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()} if folder.is_dir() else set()
    lebih = sorted(ada - set(berkas))
    if lebih:
        raise ModelDitolak(f"{folder.name}: {len(lebih)} berkas tidak terdaftar di kunci, folder ditolak ({', '.join(lebih[:5])})")
    for nama, sha in berkas.items():
        jalur = folder / nama
        if not jalur.is_file():
            raise ModelDitolak(f"{folder.name}/{nama}: berkas model tidak ada")
        nyata = sha256_berkas(jalur)
        if nyata != sha:
            raise ModelDitolak(f"{folder.name}/{nama}: SHA-256 {nyata} tidak sama dengan yang terdaftar {sha}")
    return folder


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Pakai: python model_terkunci.py <folder-model>")
        sys.exit(2)
    try:
        hasil = verifikasi_folder_model(sys.argv[1], daftar_model_hf())
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        sys.exit(1)
    print(f"COCOK {hasil.name}: {len(daftar_model_hf()[hasil.name])} berkas sesuai kunci")
    sys.exit(0)
```

- [x] **Step 4: Jalankan; enam lulus, satu tetap merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `1 failed, 89 passed`, `EXIT=1`. Yang gagal hanya `test_kunci_repo_mencatat_pelabel_qwen3_vl` dengan
`KeyError: 'qwen3-vl-2b-instruct'`: kuncinya belum memuat model itu. Ini merah yang diharapkan sampai Step 5.

- [x] **Step 5: Salin butir kunci dari vision-seed (dibaca dari berkasnya, tidak diketik ulang)**

Tulis berkas sekali pakai `data/alat-sementara/salin-kunci-model.mjs`:

```js
// Sekali pakai: menyalin butir model_hf "qwen3-vl-2b-instruct" dari kunci vision-seed ke tools/vendor.lock.json,
// dengan catatan asal-usul. Disisipkan sebelum kurung penutup, supaya bagian lain kunci tidak berubah bentuk.
import fs from 'node:fs';

const VS = 'D:/Projects/super-team-v1/vision-seed/tools/vendor.lock.json';
const KITA = 'tools/vendor.lock.json';
const asal = JSON.parse(fs.readFileSync(VS, 'utf8')).model_hf.find((m) => m.nama === 'qwen3-vl-2b-instruct');
if (!asal) { console.error('butir tidak ada di kunci vision-seed'); process.exit(1); }
const teks = fs.readFileSync(KITA, 'utf8');
if (JSON.parse(teks).model_hf) { console.error('kunci repo ini sudah punya model_hf; tidak ditimpa'); process.exit(1); }
const butir = {
  ...asal,
  peran: 'alat lab: pelabel otomatis dan pembanding "AI serba-bisa" untuk langkah baca huruf (Rencana 5). BUKAN bagian produk',
  asal_salinan: 'butir ini disalin dari vision-seed @3591530 (tools/vendor.lock.json, model_hf) dan foldernya dari vision-seed/models/qwen3-vl-2b-instruct pada 2026-10-14 (K14). SHA-256 tiap berkas diperiksa ulang di lab oleh tools/lab/model_terkunci.py',
};
const tentang = 'Model Hugging Face (satu folder di models/, di-gitignore). Hanya kelas bawaan transformers (tanpa trust_remote_code), hanya safetensors. Folder yang isinya tidak persis daftar berkas di bawah ditolak tools/lab/model_terkunci.py.';
const sisip = `,\n  "_model_hf": ${JSON.stringify(tentang)},\n  "model_hf": [\n${JSON.stringify(butir, null, 2).replace(/^/gm, '    ')}\n  ]\n}`;
const akhir = teks.trimEnd();
if (!akhir.endsWith('}')) { console.error('kunci tidak diakhiri kurung kurawal'); process.exit(1); }
fs.writeFileSync(KITA, `${akhir.slice(0, -1).trimEnd()}${sisip}\n`);
const baru = JSON.parse(fs.readFileSync(KITA, 'utf8'));
console.log(`model_hf: ${baru.model_hf.map((m) => `${m.nama} (${Object.keys(m.berkas).length} berkas, revisi ${m.revisi.slice(0, 7)})`).join(', ')}`);
```

Run: `node data/alat-sementara/salin-kunci-model.mjs; echo "EXIT=$?"`
Expected: `model_hf: qwen3-vl-2b-instruct (11 berkas, revisi 8964489)` dan `EXIT=0`.

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 99`, `EXIT=0` (pintu-pintu lain tetap bisa membaca kunci).

- [x] **Step 6: Salin foldernya, lalu periksa di lab**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
(hanya untuk dicatat; menyalin tidak memakai kartu grafis).

Run (PowerShell):
`New-Item -ItemType Directory -Force models | Out-Null; Copy-Item -LiteralPath 'D:\Projects\super-team-v1\vision-seed\models\qwen3-vl-2b-instruct' -Destination models\ -Recurse; Get-ChildItem models\qwen3-vl-2b-instruct | Measure-Object Length -Sum | ForEach-Object { "{0} berkas, {1} byte" -f $_.Count, $_.Sum }`
Expected: `11 berkas, ...` (sekitar 4,27 miliar byte).

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/model_terkunci.py /kerja/models/qwen3-vl-2b-instruct; "EXIT=$LASTEXITCODE"`
Expected: `COCOK qwen3-vl-2b-instruct: 11 berkas sesuai kunci` dan `EXIT=0`.

Run: `npm run test:lab; echo "EXIT=$?"` lalu `git status --short`
Expected: `90 passed`, `EXIT=0`; `git status` hanya ` M tools/vendor.lock.json` dan berkas uji/alat baru (folder
`models/` di-gitignore).

- [x] **Step 7: Commit**

```bash
git add tools/lab/model_terkunci.py tools/lab/uji/test_model_terkunci.py tools/vendor.lock.json
git commit -q -F - <<'EOF'
Qwen3-VL-2B disalin dari vision-seed dan dikunci per berkas

Alasan: Rencana 5 butuh pelabel otomatis yang berjalan di laptop tanpa
jaringan, dan spec 8.1 langkah 6 butuh pembanding "AI serba-bisa". Model ini
sudah diunduh vision-seed dari organisasi aslinya pada revisi yang dipin,
jadi tidak perlu diunduh lagi.

Butir kuncinya disalin dari kunci vision-seed dengan skrip (tidak diketik
ulang), foldernya disalin apa adanya, lalu tiap berkas diperiksa ulang di
lab: 11 berkas cocok. Gerbang folder model disalin dari vision-seed
inti/deteksi/bobot.py dengan catatan asal-usul (K14). Berkas yang tak
terdaftar membuat seluruh folder ditolak.

Uji ditulis lebih dulu dan terlihat merah; satu uji rantai tetap merah
sampai butir kunci disalin. Gerbang lab: 83 -> 90.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 5: Pelabel dan pembanding Qwen3-VL pada set uji

**Files:**
- Create: `tools/lab/baca_vlm.py`
- Create: `tools/lab/uji/test_baca_vlm.py`
- Create: `tools/lab/uji_gpu/test_gpu_baca_vlm.py`

- [x] **Step 1: Tulis ujinya (pembaca diganti tiruan)**

Buat `tools/lab/uji/test_baca_vlm.py`:

```python
"""Uji tools/lab/baca_vlm.py dengan pembaca tiruan: penilaian per gambar dan per kedatangan, dan tanpa nomor plat di
ringkasan maupun layar. Model sungguhan diuji terpisah di tools/lab/uji_gpu/."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_vlm as bv  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "baca_vlm.py"


def siapkan(tmp_path, kedatangan):
    """`kedatangan` = daftar (teks, kelompok, banyak gambar)."""
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    uji = []
    for teks, kelompok, banyak in kedatangan:
        berkas = []
        for i in range(banyak):
            nama = f"test/{teks}_{i}.png"
            cv2.imwrite(str(folder / nama), np.full((30, 100, 3), 200, np.uint8))
            berkas.append(nama)
        uji.append({"teks": teks, "kelompok": kelompok, "berkas": berkas})
    pembagian = {"latih": [], "uji": uji}
    jalur = tmp_path / "pembagian.json"
    jalur.write_text(json.dumps(pembagian))
    return pembagian, jalur, folder


def pembaca(jawaban):
    sisa = iter(jawaban)
    return lambda gambar: next(sisa)


def test_bacaan_dibersihkan_lalu_dibandingkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 1)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["b 1234 xyz."]))

    k = ringkasan["per_kelompok"]["mobil-terang"]
    assert (k["gambar"], k["gambar_benar"], k["kedatangan_benar"]) == (1, 1, 1)


def test_kedatangan_memakai_bacaan_terbanyak(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "motor-gelap", 3)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["B1234XYZ", "B1234XY2", "B1234XYZ"]))

    k = ringkasan["per_kelompok"]["motor-gelap"]
    assert (k["gambar_benar"], k["kedatangan_benar"], k["kedatangan_ragu"]) == (2, 1, 0)


def test_seri_di_puncak_menjadi_ragu_bukan_tebakan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "motor-gelap", 2)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["B1234XYZ", "B1234XY2"]))

    k = ringkasan["per_kelompok"]["motor-gelap"]
    assert (k["kedatangan_benar"], k["kedatangan_ragu"]) == (0, 1)


def test_bacaan_di_luar_pola_dihitung(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-gelap", 1)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["HELLO"]))

    k = ringkasan["per_kelompok"]["mobil-gelap"]
    assert (k["gambar_benar"], k["gambar_luar_pola"]) == (0, 1)


def test_rentang_wilson():
    assert bv.wilson(0, 0) is None
    bawah, atas = bv.wilson(50, 100)
    assert abs(bawah - 0.404) < 0.001 and abs(atas - 0.596) < 0.001


def test_utama_menulis_hasil_dan_ringkasan_tanpa_nomor_plat(tmp_path, capsys):
    _, jalur, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 2), ("D5678AB", "motor-terang", 1)])
    keluar = tmp_path / "keluar"

    kode = bv.utama(jalur, folder, tmp_path / "model-tiruan", keluar, baca=pembaca(["B1234XYZ", "B1234XYZ", "D5678A"]))

    assert kode == 0
    assert len((keluar / "hasil.jsonl").read_text().splitlines()) == 3
    teks = (keluar / "ringkasan.json").read_text()
    for larangan in ("B1234XYZ", "D5678AB", "D5678A", "1234", "5678"):
        assert larangan not in teks
    assert set(json.loads(teks)["per_kelompok"]) == set(bv.KELOMPOK)
    cetak = capsys.readouterr().out
    assert "1234" not in cetak and "5678" not in cetak
    assert "mobil-gelap   kosong" in cetak


def test_baris_perintah_menolak_folder_model_tak_terdaftar_dengan_kode_2(tmp_path):
    # Rantainya: baris perintah -> gerbang folder model, SEBELUM torch dimuat atau set uji dibaca.
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path), str(lain),
                            str(tmp_path / "keluar")], capture_output=True, text=True)

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout
    assert not (tmp_path / "keluar").exists()
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'baca_vlm'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/baca_vlm.py`:

```python
"""Pelabel otomatis dan pembanding pertama untuk langkah "baca huruf": Qwen3-VL-2B lokal, tanpa jaringan.

Membaca tiap gambar set uji (tools/lab/bagi_set_uji.py) lalu membandingkannya dengan label penerbit: per gambar, dan
per kedatangan (bacaan terbanyak dari gambar-gambar berplat sama; seri di puncak = "ragu", bukan tebakan). Hasilnya
mengukur dua hal: seberapa bisa dipercaya pelabel otomatis untuk bahan tanpa label teks (video, dataset pencahayaan),
dan angka pembanding pertama "AI serba-bisa" untuk langkah baca huruf (spec bagian 8.1 langkah 6).

Folder model diverifikasi (tools/lab/model_terkunci.py) SEBELUM torch dan transformers diimpor. Kelas model bawaan
transformers, tanpa trust_remote_code. Jawaban deterministik (tanpa sampling). Angka per kelompok disertai rentang
ketidakpastian 95% (Wilson); kelompok di bawah 30 kedatangan ditulis "terlalu sedikit untuk disimpulkan" (spec 8.3).

Keluaran:
- hasil.jsonl: bacaan tiap gambar. Memuat nomor plat: tinggal di data/, agen tidak membukanya.
- ringkasan.json: hitungan saja. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/baca_vlm.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/models/qwen3-vl-2b-instruct /kerja/data/keluaran/baca-vlm
"""
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_terkunci import ModelDitolak, daftar_model_hf, verifikasi_folder_model  # noqa: E402
from plat import bersihkan, urai  # noqa: E402

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
SEDIKIT = 30
PERTANYAAN = ("This image shows one Indonesian vehicle license plate. Read the registration number on it and ignore "
              "the small expiry date row. Reply with only the letters and digits of the registration number, "
              "without spaces.")
TOKEN_MAKS = 16
SISI_MAKS = 448
ISIAN = ("kedatangan", "kedatangan_benar", "kedatangan_ragu", "gambar", "gambar_benar", "gambar_luar_pola")


def perkecil(gambar, sisi_maks=SISI_MAKS):
    """Perkecil sampai sisi terpanjang <= sisi_maks (tak pernah memperbesar)."""
    tinggi, lebar = gambar.shape[:2]
    skala = sisi_maks / max(tinggi, lebar)
    if skala >= 1.0:
        return gambar
    return cv2.resize(gambar, (max(1, round(lebar * skala)), max(1, round(tinggi * skala))), interpolation=cv2.INTER_AREA)


def matikan_kernel_triton():
    """Asal: vision-seed @3591530 inti/mesin/kernel.py (K14). Image lab tidak punya kompiler C, sedangkan torch mengganti
    beberapa operasi dengan kernel Triton yang dikompilasi saat pertama dipakai. Override itu dicabut lewat jalur resmi
    torch; hasil hitungnya sama."""
    try:
        from torch._native import registry
    except ImportError:
        return False
    registry.deregister_op_overrides(disable_dsl_names="triton")
    return True


class PembacaQwen:
    """Pembaca plat dengan Qwen3-VL. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali teks mentah."""

    def __init__(self, folder_model):
        folder = verifikasi_folder_model(Path(folder_model), daftar_model_hf())

        import torch
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        matikan_kernel_triton()
        self._torch = torch
        self._prosesor = AutoProcessor.from_pretrained(str(folder), local_files_only=True)
        self._model = Qwen3VLForConditionalGeneration.from_pretrained(str(folder), local_files_only=True, dtype=torch.float16)
        self._model.to("cuda").eval()

    def __call__(self, gambar_bgr):
        from PIL import Image

        gambar = Image.fromarray(np.ascontiguousarray(perkecil(gambar_bgr)[..., ::-1]))
        pesan = [{"role": "user", "content": [{"type": "image", "image": gambar}, {"type": "text", "text": PERTANYAAN}]}]
        masukan = self._prosesor.apply_chat_template(pesan, tokenize=True, add_generation_prompt=True, return_dict=True,
                                                     return_tensors="pt").to(self._model.device)
        with self._torch.inference_mode():
            keluar = self._model.generate(**masukan, max_new_tokens=TOKEN_MAKS, do_sample=False)
        return self._prosesor.batch_decode(keluar[:, masukan["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip()


def suara_terbanyak(bacaan):
    """Bacaan yang paling sering; "" (ragu) bila tak ada bacaan atau ada seri di puncak."""
    hitung = Counter(b for b in bacaan if b)
    if not hitung:
        return ""
    urut = hitung.most_common()
    if len(urut) > 1 and urut[1][1] == urut[0][1]:
        return ""
    return urut[0][0]


def wilson(benar, jumlah, z=1.96):
    """Rentang ketidakpastian 95% (Wilson) untuk benar/jumlah; None bila jumlah nol."""
    if jumlah == 0:
        return None
    p = benar / jumlah
    penyebut = 1 + z * z / jumlah
    tengah = (p + z * z / (2 * jumlah)) / penyebut
    lebar = z * math.sqrt(p * (1 - p) / jumlah + z * z / (4 * jumlah * jumlah)) / penyebut
    return max(0.0, tengah - lebar), min(1.0, tengah + lebar)


def nilai(pembagian, folder_gambar, baca):
    """Membaca semua gambar set uji. Kembali: (baris per gambar, ringkasan tanpa nomor plat)."""
    hitung = {k: Counter() for k in KELOMPOK}
    baris, detik = [], 0.0
    for kedatangan in pembagian["uji"]:
        c = hitung[kedatangan["kelompok"]]
        bacaan = []
        for berkas in kedatangan["berkas"]:
            gambar = cv2.imread(str(Path(folder_gambar) / berkas))
            mulai = time.perf_counter()
            mentah = baca(gambar) if gambar is not None else ""
            detik += time.perf_counter() - mulai
            bersih = bersihkan(mentah)
            bacaan.append(bersih)
            c["gambar"] += 1
            c["gambar_benar"] += bersih == kedatangan["teks"]
            c["gambar_luar_pola"] += urai(bersih) is None
            baris.append({"berkas": berkas, "kelompok": kedatangan["kelompok"], "label": kedatangan["teks"],
                          "bacaan": bersih, "mentah": mentah})
        akhir = suara_terbanyak(bacaan)
        c["kedatangan"] += 1
        c["kedatangan_benar"] += akhir == kedatangan["teks"]
        c["kedatangan_ragu"] += akhir == ""
    per_kelompok = {}
    for k in KELOMPOK:
        rentang = wilson(hitung[k]["kedatangan_benar"], hitung[k]["kedatangan"])
        per_kelompok[k] = {**{n: hitung[k][n] for n in ISIAN},
                           "rentang_95_kedatangan": [round(rentang[0], 3), round(rentang[1], 3)] if rentang else None,
                           "terlalu_sedikit": hitung[k]["kedatangan"] < SEDIKIT}
    gambar = sum(hitung[k]["gambar"] for k in KELOMPOK)
    return baris, {"per_kelompok": per_kelompok, "detik_per_gambar": round(detik / gambar, 3) if gambar else None}


def uraikan(r):
    n, benar = r["kedatangan"], r["kedatangan_benar"]
    if n == 0:
        return "kosong"
    if r["terlalu_sedikit"]:
        kedatangan = f"kedatangan benar {benar} dari {n} (terlalu sedikit untuk disimpulkan)"
    else:
        bawah, atas = r["rentang_95_kedatangan"]
        kedatangan = f"kedatangan benar {benar} dari {n} ({100 * benar / n:.1f}%, rentang 95% {100 * bawah:.1f}-{100 * atas:.1f}%)"
    return (f"{kedatangan}; ragu {r['kedatangan_ragu']}; gambar benar {r['gambar_benar']} dari {r['gambar']}; "
            f"di luar pola {r['gambar_luar_pola']}")


def utama(berkas_pembagian, folder_gambar, folder_model, keluar, baca=None):
    if baca is None:
        try:
            baca = PembacaQwen(folder_model)
        except ModelDitolak as galat:
            print(f"DITOLAK: {galat}")
            return 2
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    baris, ringkasan = nilai(pembagian, folder_gambar, baca)
    ringkasan = {"model": Path(folder_model).name, "pertanyaan": PERTANYAAN, **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for k in KELOMPOK:
        print(f"{k:<13} {uraikan(ringkasan['per_kelompok'][k])}")
    print(f"detik per gambar: {ringkasan['detik_per_gambar']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Pakai: python baca_vlm.py <pembagian.json> <folder-gambar> <folder-model> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `97 passed` (90 + 7 baru) dan `EXIT=0`.

- [x] **Step 5: Uji dengan model sungguhan (di luar gerbang biasa)**

Buat `tools/lab/uji_gpu/test_gpu_baca_vlm.py`:

```python
"""Uji dengan Qwen3-VL sungguhan. Di luar gerbang biasa karena memuat model 4 GB ke kartu grafis. Dijalankan dengan tangan:

  powershell -NoProfile -File tools\\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_vlm as bv  # noqa: E402

MODEL = Path(__file__).resolve().parents[3] / "models" / "qwen3-vl-2b-instruct"


@pytest.mark.skipif(not MODEL.is_dir(), reason="folder model belum disalin (Rencana 5 Task 4)")
def test_pembaca_qwen_membaca_plat_buatan():
    # Plat buatan tulisan komputer, bukan plat siapa pun: membuktikan rantainya (gerbang model -> muat -> tanya -> teks).
    gambar = np.zeros((110, 360, 3), np.uint8)
    cv2.putText(gambar, "B 1234 XYZ", (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 3)

    bacaan = bv.bersihkan(bv.PembacaQwen(MODEL)(gambar))

    assert bacaan == "B1234XYZ"
```

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
Expected: memori terpakai jauh di bawah 8 GB (tidak ada job vision-seed yang sedang memakai kartu grafis). Bila ada,
tunggu; jangan menjalankan dua job kartu grafis bersamaan.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu -q -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `1 passed`, `EXIT=0`. Bila bacaannya lain, itu temuan tentang model, bukan alasan mengubah ujinya: catat
bacaannya (plat buatan, bukan data pribadi), lalu laporkan sebelum lanjut ke Step 6.

- [x] **Step 6: Jalankan pada set uji sungguhan (di latar)**

Run (PowerShell, di latar, keluaran ke berkas log di folder kerja sementara):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_vlm.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/models/qwen3-vl-2b-instruct /kerja/data/keluaran/baca-vlm; "EXIT=$LASTEXITCODE"`

Expected di akhir: empat baris kelompok (atau "kosong"), `detik per gambar: <angka>`, `EXIT=0`. Lamanya belum diketahui;
dari pengalaman vision-seed, beberapa per sepuluh detik per gambar.

Run: `git status --short`
Expected: hanya berkas uji dan alat baru. `hasil.jsonl` dan `ringkasan.json` ada di `data/`.

- [x] **Step 7: Commit**

```bash
git add tools/lab/baca_vlm.py tools/lab/uji/test_baca_vlm.py tools/lab/uji_gpu/test_gpu_baca_vlm.py
git commit -q -F - <<'EOF'
Pelabel dan pembanding Qwen3-VL untuk langkah baca huruf

Alasan: bahan tanpa label teks (video riset, dataset pencahayaan) butuh
pelabel otomatis, dan seberapa bisa dipercaya pelabel itu harus diukur dulu
pada bahan yang labelnya sudah ada. Pengukuran yang sama adalah angka
pembanding pertama "AI serba-bisa" (spec 8.1 langkah 6).

Penilaian per gambar dan per kedatangan (bacaan terbanyak; seri = ragu),
per kelompok mobil atau motor dan terang atau gelap, dengan rentang 95%.
Model diverifikasi sebelum dimuat. Ringkasan dan layar tanpa nomor plat.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 90 -> 97; uji model
sungguhan di luar gerbang: <hasil Step 5>. Pada set uji: <angka Step 6>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 6: Laporan, catatan, dan permintaan ke owner

**Files:**
- Create: `bukti/2026-10-14-set-uji-baca-pertama.json`, `bukti/2026-10-14-baca-vlm-pertama.json`,
  `bukti/2026-10-14-baca-huruf-pertama.md`
- Modify: `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md`

- [x] **Step 1: Salin kedua ringkasan ke `bukti/`, sesudah dibuktikan tanpa nomor plat**

Tulis berkas sekali pakai `data/alat-sementara/periksa-bukti.py`:

```python
"""Sekali pakai: menyalin ringkasan ke bukti/ hanya bila tak satu pun teks plat atau nama berkas set uji ada di dalamnya."""
import json
import shutil
import sys
from pathlib import Path

pembagian = json.loads(Path("/kerja/data/keluaran/set-uji-baca/pembagian.json").read_text())
larangan = {a["teks"] for s in pembagian.values() for a in s} | {Path(b).stem for s in pembagian.values() for a in s for b in a["berkas"]}
for asal, tujuan in [("/kerja/data/keluaran/set-uji-baca/ringkasan.json", "set-uji-baca-pertama.json"),
                     ("/kerja/data/keluaran/baca-vlm/ringkasan.json", "baca-vlm-pertama.json")]:
    teks = Path(asal).read_text()
    temuan = sum(1 for t in larangan if t in teks)
    print(f"{tujuan}: {temuan} teks plat atau nama berkas ditemukan")
    if temuan:
        sys.exit(1)
    shutil.copy(asal, f"/kerja/data/keluaran/bukti-siap/2026-10-14-{tujuan}")
```

Run (PowerShell):
`New-Item -ItemType Directory -Force data\keluaran\bukti-siap | Out-Null; powershell -NoProfile -File tools\lab.ps1 python -I /kerja/data/alat-sementara/periksa-bukti.py; "EXIT=$LASTEXITCODE"`
Expected: dua baris `... 0 teks plat atau nama berkas ditemukan`, `EXIT=0`.

Run: `mkdir -p bukti && cp data/keluaran/bukti-siap/2026-10-14-*.json bukti/ && ls bukti/`
Expected: dua berkas JSON.

- [x] **Step 2: Tulis laporan `bukti/2026-10-14-baca-huruf-pertama.md`**

Isinya, semua angka dibaca dari kedua JSON di `bukti/` dan dari keluaran Task 2 sampai 5:

1. **Apa yang diukur:** langkah 3 (baca huruf) saja, pada potongan plat INDO-ALPR, dengan Qwen3-VL-2B lokal sebagai
   pembanding pertama dan sebagai calon pelabel otomatis.
2. **Set uji:** kedatangan dan gambar per sisi dan per kelompok; jumlah yang dikecualikan; plat di kedua sisi = 0. Sebut
   bahwa pembagian penerbit bocor (713 dari 1.462) dan karena itu tidak dipakai.
3. **Angka Qwen3-VL per kelompok:** "benar X dari N (P%, rentang 95% A–B%)", ragu, di luar pola, detik per gambar.
   Kelompok di bawah 30 kedatangan ditulis "terlalu sedikit untuk disimpulkan"; kelompok kosong ditulis kosong.
4. **Label penerbit:** "menunggu pemeriksaan owner atas 60 contoh" (diisi sesudah owner menjawab).
5. **Batas, apa adanya:** potongan plat, bukan gambar kamera gerbang (K9 tidak bisa dibuktikan dari sini, spec 8.4);
   terang atau gelap adalah taksiran dari potongan, bukan siang atau malam; kedatangan = plat yang sama (taksiran);
   golongan mobil atau motor dari nomor urut, bukan dari kendaraan yang terlihat, dan kode B dianggap Polda Metro Jaya;
   satu pertanyaan saja yang dicoba pada Qwen3-VL; angka ini mesin belajar dan pembanding, bukan angka produk.

- [x] **Step 3: Perbarui catatan**

Tulis skrip pencatat sebagai **berkas** di folder kerja sementara, dengan pola yang sama seperti sebelumnya (baca
dengan `\r\n` diseragamkan; tiap jangkar ketemu tepat sekali sebelum menulis):

1. `data-asal/bahan.json`, butir `dataset-indo-alpr`: catatan ditambah "Dibagi ulang per plat (Rencana 5): <angka>.
   Pembagian penerbit bocor dan tidak dipakai." Butir `bobot-qwen3-vl`: catatan diganti "Disalin dari vision-seed 14 Okt
   ke models/ (dikunci per berkas di tools/vendor.lock.json, model_hf). Dipakai sebagai alat lab (pelabel dan
   pembanding), bukan bagian produk. Vonis untuk produk dibaca ulang saat bahan mesin jualan dipilih (P13, P14)."
2. `CLAUDE.md` §7, butir baru: "Agen tidak membuka `pembagian.json`, `lembar-contoh*`, atau `hasil.jsonl` di
   `data/keluaran/`: semuanya memuat nomor plat. Yang dibaca agen hanya `ringkasan.json` dan keluaran layar alat. Model
   ada di `models/` (di-gitignore) dan hanya dimuat lewat `tools/lab/model_terkunci.py`."
3. `OPEN-QUESTIONS.md` bagian B, paragraf baru di atas `**Sesudah Rencana 4 Fase 0A (14 Okt):**`: set uji baca huruf
   ada, angkanya, dan artinya bagi B2 (motor ada di INDO-ALPR, tetapi bukan dari sudut gerbang) dan B3 (gelap hanya
   taksiran).
4. `ROADMAP.md`: butir "Rencana 5 ditulis" dicentang, butir "Rencana 5 dijalankan" dicentang dengan angka, butir baru
   `- [ ] Owner memeriksa 60 contoh label (lembar contoh) ← di sini sekarang`, lalu `- [ ] Rencana 6 Fase 0A ditulis`;
   baris status diperbarui; satu baris changelog dengan hasil, alasan, dan batas.

- [x] **Step 4: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 99` dan `97 passed`, keduanya `EXIT=0`.

Run: `git status --short`
Expected: hanya `bukti/` dan berkas catatan. Tidak ada berkas dari `data/` atau `models/`.

```bash
git add bukti/ data-asal/bahan.json CLAUDE.md OPEN-QUESTIONS.md ROADMAP.md plans/2026-10-14-fase-0a-rencana-5-set-uji-baca.md
git commit -q -F - <<'EOF'
Catat hasil Rencana 5 Fase 0A (set uji baca huruf pertama)

Alasan: <satu paragraf: angka pertama Fase 0A, apa artinya, dan kenapa
belum boleh dibaca sebagai angka produk>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

- [x] **Step 5: BERHENTI. Minta owner memeriksa lembar contoh**

Minta owner membuka berkas ini di laptop (agen tidak membukanya):

```
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-contoh\lembar-contoh-1.png
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-contoh\lembar-contoh-2.png
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-contoh\lembar-contoh-3.png
```

dan menjawab satu hal: **nomor baris mana yang tulisan birunya tidak sama dengan plat di gambarnya** (atau "semua
sama"). Baris yang gambarnya tidak terbaca oleh owner disebut terpisah.

Sesudah owner menjawab: jumlah label salah dicatat di laporan `bukti/` dan di `ROADMAP.md`, butir pemeriksaan owner
dicentang, lalu commit.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan spec:** 8.1 langkah 5 (set uji pertama, label diperiksa manusia, dipisah dari bahan latih, dikelompokkan)
  → Task 2, 3, 6. Langkah 6 (pembanding) → Task 5 untuk AI serba-bisa; paket jadi menyusul di Rencana 6. 8.3 (dipisah
  per sumber, angka dengan jumlah dan rentang, kelompok di bawah 30 dan kelompok kosong) → Task 2 dan 5. Yang **tidak**
  dicakup: siang-malam menurut 8.3 (tidak bisa dari potongan plat; ditulis sebagai batas), kedatangan dari video
  (Rencana 6).
- **Tanpa isian kosong pada kode:** semua kode alat dan uji tertulis lengkap. Isian bersudut hanya pada angka hasil dan
  pesan commit yang baru ada sesudah dijalankan; tiap isian menyebut dari langkah mana ia dibaca.
- **Nama yang konsisten:** `Plat`, `urai`, `bersihkan`, `golongan`, `kelompok_kendaraan`, `urai_nama_indo_alpr`
  (plat.py) dipakai sama di tiga alat. `KELOMPOK` sama di tiga alat. `ModelDitolak`, `daftar_model_hf`,
  `verifikasi_folder_model` (model_terkunci.py) dipakai baca_vlm.py.
- **Angka gerbang:** Node tetap 99. Lab 51 → 72 → 79 → 83 → 90 → 97; satu uji model sungguhan di luar gerbang.

## Catatan pelaksanaan (14 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Hasil dan batasnya di
[`../bukti/2026-10-14-baca-huruf-pertama.md`](../bukti/2026-10-14-baca-huruf-pertama.md). Yang berbeda dari tulisan di atas:

- **Tiga uji tambahan, semuanya soal kebocoran nama berkas berplat.** Task 2: `test_galat_membaca_tidak_membocorkan_nama_berkas`.
  Kode `bagi_set_uji.py` di atas mencetak nama berkas saat gambar rusak, dan itu dibuktikan dengan menjalankannya apa
  adanya; kini `utama` menangkap `OSError`. Sesudah Task 5: `test_gambar_yang_hilang_tidak_membocorkan_nama_berkas` di
  uji lembar contoh dan uji baca_vlm, karena OpenCV mencetak jalur berkas yang tidak bisa dibuka; log OpenCV kini
  dibisukan di kedua alat.
- **Angka gerbang lab yang terjadi:** 51 → 72 → 80 → 84 → 91 → 98 → 100 (tertulis di atas 51 → 72 → 79 → 83 → 90 → 97).
  Task 4 Step 4: 1 failed, 90 passed (tertulis 89). Node tetap 99.
- **Task 2 Step 5:** dikecualikan 276, bukan sekitar 291. Selisihnya diukur: 26 nama berspasi tak lazim kini disambung,
  dan 7 nama bernomor urut berawalan 0 kini ditolak.
- **Sesudah Task 5:** jenis kesalahan Qwen3-VL dihitung dengan skrip sekali pakai yang hanya mencetak hitungan.
  Ringkasan di `bukti/` diperiksa tanpa nomor plat dengan pemeriksa yang lebih dulu diuji pada berkas yang memang berisi plat.
- **Task 6 Step 5:** owner menjawab 14 Okt. Enam baris disebut: 4 label pasti salah, 1 seri kurang satu huruf yang
  tidak terbaca jelas, dan 1 dugaan karena huruf terpotong di potongan gambar dataset. Rinciannya di laporan `bukti/`.
  Owner menulis nomor plat lengkap di percakapan; yang dicatat di repo hanya nomor baris dan jenis salahnya.
