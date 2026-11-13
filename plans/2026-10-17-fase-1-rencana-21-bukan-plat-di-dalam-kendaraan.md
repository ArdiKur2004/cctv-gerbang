# Fase 1, Rencana 21: Bukan plat di dalam kendaraan — tampak depan/belakang dan letak plat (K39 langkah 2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Berhenti dua kali untuk owner: lembar latih (Task 4) dan dua lembar uji (Task 6).

**Goal:** Benda bukan plat di dalam kendaraan, terutama yang dibaca "yakin", berkurang tanpa membuang plat. Di Rencana 20, 18 dari
43 kedatangan "yakin" di lembar uji bukan plat (14 di kamera parkiran). Saringannya memakai langkah 2 usulan owner (tampak depan
atau belakang) dan letak plat di dalam kendaraan. Aturannya dipilih di **sisi latih** dari label owner, lalu diukur sekali di
set uji.

**Architecture:**
- **`tools/lab/kendaraan.py`:** kotak plat dari `saring` dan `cari_dalam_kendaraan` membawa kotak kendaraannya sebagai unsur
  ketujuh.
- **`tools/lab/rantai.py`:** tiap penampakan mencatat kotak kendaraannya. `penampakan.jsonl` mendapat daftar `kendaraan` yang
  sejajar dengan `tampak`, karena `dataset_cctv.py` membongkar tiap butir `tampak` sebagai `g, *kotak`.
- **`tools/lab/letak.py` (baru):** ciri letak satu kotak plat di kendaraannya:
  - `rx`, `ry`: tengah plat relatif terhadap kotak kendaraan (0..1);
  - rasio lebar/tinggi plat;
  - rasio lebar/tinggi kendaraan, sebagai pengganti "tampak depan atau belakang".

  Modul ini juga berisi 24 aturan yang ditetapkan di sini, penilaian aturan dari label owner sisi latih, dan aturan memilih.
- **`rantai.py` dan `lembar_bingkai.py`:** `--letak <nama aturan>` membuang penampakan yang tidak lolos, sebelum dibaca.

**Tech Stack:** Python di lab dan image tambahan (`-Fpo`), CPU.

---

## Yang diukur sebelum rencana ini ditulis (17 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| "Yakin" yang bukan plat, Rencana 20 | 18 dari 43 di lembar uji: parkiran 14, kamera diam lain 3, gerbang 1 | `bukti/2026-10-17-plat-di-dalam-kendaraan.md` |
| Bentuk kendaraan menurut tampak | Mobil dari depan atau belakang sekitar 1,7 m × 1,5 m (lebar/tinggi ±1,1–1,3); dari samping ±4,5 m × 1,5 m (±3). Motor dari depan atau belakang ±0,7 m × 1,1–1,6 m (±0,5–0,7); dari samping ±1,9 m × 1,1 m (±1,7) | Ukuran umum kendaraan; ambang di bawah ditetapkan dari sini, bukan dari data |
| Penilaian sisi latih Rencana 20 | "Ditemukan" dihitung bila ada kotak di mana pun di kendaraan, jadi kotak bukan plat di kendaraan berplat terbaca tidak terlihat | Laporan Rencana 20 bagian 5 |

## Aturan (24, ditetapkan sebelum label dilihat)

Tiap aturan adalah gabungan syarat-syarat berikut, termasuk "tanpa syarat":
- `ry` minimal 0,4 atau 0,6 (plat di bagian bawah kendaraan);
- `|rx − 0,5|` paling banyak 0,3 (plat di tengah mendatar);
- rasio plat 1,0–6,0;
- **tampak**: rasio kendaraan paling banyak 1,8 untuk mobil, truk, dan bus, dan paling banyak 1,2 untuk motor (tampak depan atau
  belakang, bukan samping).

Jumlahnya 3 (`ry`: tanpa/0,4/0,6) × 2 × 2 × 2 = 24. Nama aturan menggabungkan syarat yang aktif dengan `_`, misalnya
`ry0.4_rx0.3_tampak`. Aturan tanpa syarat bernama `tanpa`.

## Aturan memilih (ditetapkan sebelum label dilihat)

1. **Satuannya kedatangan berlabel di lembar latih.** Sebuah kedatangan lolos bila minimal `MIN_TAMPAK` (2) penampakannya lolos,
   sama seperti rantai.
2. **Calon:** aturan yang meloloskan minimal 90% kedatangan plat (plat terbaca maupun tak terbaca).
3. **Di antara calon:** pilih yang paling sedikit meloloskan bukan plat. Bila seri, pilih yang syaratnya paling sedikit, lalu
   menurut nama.
4. Set uji tidak dipakai memilih.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/kendaraan.py`, `rantai.py`, ujinya (ubah) | Kotak kendaraan ikut di kotak plat dan di `penampakan.jsonl` | 1 |
| `tools/lab/letak.py`, `tools/lab/uji/test_letak.py` (baru) | Ciri, 24 aturan, penilaian, pilih, CLI `banding` | 2 |
| `rantai.py`, `lembar_bingkai.py`, ujinya, `uji_fpo` (ubah) | `--letak` | 3 |
| `bukti/<tanggal>-bukan-plat-di-dalam-kendaraan*` | Hitungan dan laporan | 7 |

---

### Task 1: Kotak kendaraan ikut di kotak plat dan penampakan

- [x] **Step 1: Uji merah.**
  - Di `test_kendaraan.py`, `test_saring_membuang_plat_di_luar_kendaraan_dan_menambah_jenis` kini menuntut
    `terima == [(140, 200, 160, 210, 0.9, "motor", (100, 100, 200, 250))]`. Isinya diperluas, bukan dihapus.
  - Uji baru:

```python
def test_cari_dalam_kendaraan_membawa_kotak_kendaraan():
    motor = (100.0, 100.0, 200.0, 300.0, 0.8, "motor")

    hasil = kd.cari_dalam_kendaraan(np.zeros((400, 600, 3), np.uint8), [motor], cari_relatif, 0.25, margin=0.1)

    assert hasil[0][6] == (100.0, 100.0, 200.0, 300.0)
```

  Di `test_rantai.py`:

```python
def test_penampakan_mencatat_kotak_kendaraan_sejajar_dengan_tampak(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca_tiruan, 0.25, tmp_path / "k", simpan_penampakan=True,
                          cari_kendaraan=kendaraan_tiruan)

    t = [json.loads(b) for b in (tmp_path / "k" / "penampakan.jsonl").read_text().splitlines()]
    assert len(t) == 1 and len(t[0]["kendaraan"]) == len(t[0]["tampak"]) == 5
    assert t[0]["kendaraan"][0] == [50.0, 30.0, 110.0, 66.0, "motor"] and len(t[0]["tampak"][0]) == 5
```

  Merah yang diharapkan: tuple tanpa unsur ketujuh, dan `KeyError: 'kendaraan'`.
- [x] **Step 2:**
  - `saring` dan `cari_dalam_kendaraan` menambah `tuple(float(x) for x in v[:4])` sebagai unsur ketujuh.
  - Penampakan di `jalankan_video` mendapat `"kotak_kendaraan": k[6] if len(k) > 6 else None`.
  - `penampakan.jsonl` mendapat `"kendaraan": [[*kotak dibulatkan 1 desimal, jenis] atau None per penampakan]`.

  Run gerbang lab → Expected `243 passed` (241 + 2). Commit.

  *Hasil:* merah dilihat (`3 failed`: `IndexError` dua kali, `KeyError: 'kendaraan'`), lalu gerbang lab `243 passed`.

### Task 2: `letak.py`

- [x] **Step 1: Uji merah** `tools/lab/uji/test_letak.py`:

```python
"""Uji tools/lab/letak.py (Rencana 21, K39 langkah 2): ciri letak plat di kendaraan, 24 aturan, penilaian dari label owner sisi
latih, aturan memilih, dan CLI banding tanpa model."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import letak  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "letak.py"
MOBIL_DEPAN = [100, 100, 300, 260, "mobil"]  # lebar/tinggi 1,25: tampak depan atau belakang
MOBIL_SAMPING = [100, 100, 400, 200, "mobil"]  # 3,0: tampak samping


def test_ciri_letak_plat_di_kendaraan():
    f = letak.ciri([180, 220, 220, 236], MOBIL_DEPAN)

    assert {k: f[k] for k in ("rx", "ry", "rasio_plat", "rasio_kendaraan")} == pytest.approx(
        {"rx": 0.5, "ry": 0.8, "rasio_plat": 2.5, "rasio_kendaraan": 1.25}) and f["jenis"] == "mobil"


def test_dua_puluh_empat_aturan_bernama_unik():
    assert len(letak.ATURAN) == 24 and "tanpa" in letak.ATURAN and "ry0.4_rx0.3_rp_tampak" in letak.ATURAN


def test_lolos_per_syarat():
    bawah_tengah = letak.ciri([180, 220, 220, 236], MOBIL_DEPAN)
    atas = letak.ciri([180, 110, 220, 126], MOBIL_DEPAN)
    samping = letak.ciri([230, 170, 270, 186], MOBIL_SAMPING)

    assert letak.lolos(bawah_tengah, letak.ATURAN["ry0.6_rx0.3_rp_tampak"])
    assert not letak.lolos(atas, letak.ATURAN["ry0.4"]) and letak.lolos(atas, letak.ATURAN["tanpa"])
    assert not letak.lolos(samping, letak.ATURAN["tampak"]) and letak.lolos(samping, letak.ATURAN["ry0.6"])
    assert letak.lolos(letak.ciri([180, 220, 220, 236], None), letak.ATURAN["tanpa"])
    assert not letak.lolos(letak.ciri([180, 220, 220, 236], None), letak.ATURAN["ry0.4"])  # tanpa kendaraan: tidak lolos syarat


def penampakan_(nomor, kotak, kendaraan):
    return {"video": "v.mp4", "jalur": nomor, "kedatangan": nomor, "tampak": [[i, *kotak] for i in range(3)],
            "kendaraan": [kendaraan] * 3}


def test_nilai_aturan_per_kedatangan_berlabel():
    tampak = [penampakan_(1, [180, 220, 220, 236], MOBIL_DEPAN), penampakan_(2, [180, 110, 220, 126], MOBIL_DEPAN),
              penampakan_(3, [230, 170, 270, 186], MOBIL_SAMPING)]
    lembar = {"baris": [{"nomor": n, "video": "v.mp4", "kedatangan": n, "status": "yakin"} for n in (1, 2, 3)]}

    h = letak.nilai_aturan(tampak, lembar, bukan_plat={2, 3}, aturan=letak.ATURAN["ry0.6_tampak"])

    assert h == {"plat": 1, "plat_lolos": 1, "bukan": 2, "bukan_lolos": 0, "bukan_yakin": 2, "bukan_yakin_lolos": 0}


def test_pilih_aturan_minimal_90_persen_plat_lalu_bukan_plat_tersedikit_lalu_syarat_tersedikit():
    hasil = [{"nama": "tanpa", "syarat": 0, "plat": 10, "plat_lolos": 10, "bukan_lolos": 20},
             {"nama": "ry0.6", "syarat": 1, "plat": 10, "plat_lolos": 8, "bukan_lolos": 2},  # 80% < 90%
             {"nama": "ry0.4", "syarat": 1, "plat": 10, "plat_lolos": 9, "bukan_lolos": 5},
             {"nama": "ry0.4_tampak", "syarat": 2, "plat": 10, "plat_lolos": 9, "bukan_lolos": 5}]

    assert letak.pilih_aturan(hasil)["nama"] == "ry0.4"


def test_cli_banding_dari_berkas_tanpa_model(tmp_path):
    (tmp_path / "p.jsonl").write_text("\n".join(json.dumps(t) for t in [
        penampakan_(1, [180, 220, 220, 236], MOBIL_DEPAN), penampakan_(2, [180, 110, 220, 126], MOBIL_DEPAN)]))
    (tmp_path / "l.json").write_text(json.dumps({"baris": [
        {"nomor": n, "video": "v.mp4", "kedatangan": n, "status": "ragu"} for n in (1, 2)]}))

    hasil = subprocess.run([sys.executable, str(SKRIP), "banding", str(tmp_path / "p.jsonl"), str(tmp_path / "l.json"),
                            str(tmp_path / "b.json"), "--bukan-plat", "2"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    b = json.loads((tmp_path / "b.json").read_text())
    assert len(b["aturan"]) == 24 and b["terpilih"]["plat_lolos"] == 1 and b["terpilih"]["bukan_lolos"] == 0
    assert "v.mp4" not in hasil.stdout + hasil.stderr
```

Merah yang diharapkan: `ModuleNotFoundError: No module named 'letak'`.

- [x] **Step 2: Tulis `tools/lab/letak.py`:**
  - `RASIO_TAMPAK = {"mobil": 1.8, "truk": 1.8, "bus": 1.8, "motor": 1.2}`, `RASIO_PLAT = (1.0, 6.0)`, `MIN_BAGIAN_PLAT = 0.9`,
    `MIN_TAMPAK` dibaca dari `rantai`.
  - **`ciri(plat, kendaraan)`:**
    - masukan: `plat` (x1, y1, x2, y2) dan `kendaraan` ([x1, y1, x2, y2, jenis] atau `None`);
    - kembali: `{"rx", "ry", "rasio_plat", "rasio_kendaraan", "jenis"}`;
    - tanpa kendaraan, semua ciri kendaraan `None`.
  - **`ATURAN`:** dict nama → `{"ry_min", "rx_jarak", "rasio_plat", "tampak", "syarat"}`, disusun dari gabungan di atas.
  - **`lolos(ciri, aturan)`:**
    - semua syarat aktif harus terpenuhi;
    - syarat yang butuh kendaraan gagal bila kendaraan `None`;
    - jenis yang tidak ada di `RASIO_TAMPAK` gagal syarat tampak.
  - **`nilai_aturan(penampakan, lembar, bukan_plat, aturan)`:** per baris lembar, penampakan kedatangannya dicari, lalu kedatangan
    lolos bila minimal `MIN_TAMPAK` penampakannya lolos. Kembali: `plat`, `plat_lolos`, `bukan`, `bukan_lolos`, `bukan_yakin`,
    `bukan_yakin_lolos`.
  - **`pilih_aturan(hasil)`:** aturan memilih di atas.
  - **CLI** `banding penampakan.jsonl lembar.json keluar.json --bukan-plat <n,...>`:
    - menulis semua aturan dan `terpilih`;
    - layar menampilkan tabel hitungan tanpa nama video;
    - galat hanya mencetak jenisnya.

  Run gerbang lab → Expected `249 passed` (243 + 6). Commit.

  *Hasil:*
  - Merah dilihat: `ModuleNotFoundError: No module named 'letak'`.
  - `letak` membaca `MIN_TAMPAK` dari `rantai` **di dalam fungsi**, karena `rantai` mengimpor `letak`.
  - Penyaring kotak untuk rantai dan lembar bingkai ditaruh di `letak.saring_letak`, supaya keduanya memakai fungsi yang sama.
    Fungsi ini tidak ada di rencana; ia ditambahkan saat menulis Task 3.

### Task 3: `--letak` di rantai dan lembar bingkai

- [x] **Step 1: Uji merah.** Di `test_rantai.py`:

```python
def test_letak_membuang_penampakan_yang_tidak_lolos_sebelum_dibaca(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dibaca = []

    def baca(potongan):
        dibaca.append(1)
        return "B1234XY", 0.8

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "mobil")]  # KOTAK (60..100, 40..56): tengahnya ry 0,5 < 0,6
    kendaraan.ambang = 0.25

    r = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca, 0.25, tmp_path / "k", cari_kendaraan=kendaraan,
                              letak="ry0.6")

    assert r["kedatangan"] == 0 and r["tersaring_letak"] == 5 and r["aturan"]["letak"] == "ry0.6" and not dibaca
```

  Di `test_lembar_bingkai.py`: `buat_lembar(..., cari_kendaraan=..., letak="ry0.6")` dengan kotak yang sama → baris
  `kotak == 0` dan `tersaring_letak == 1`.

  Merah yang diharapkan: `unexpected keyword argument 'letak'`.
- [x] **Step 2:**
  - **`jalankan_video(..., letak=None)`:**
    - sesudah tahap kendaraan, bila `letak` ada, kotak yang tidak lolos `letak.lolos(letak.ciri(k[:4], kendaraannya),
      ATURAN[letak])` dibuang dan dihitung;
    - kembalian menjadi `(jalur, waktu, tersaring, tersaring_letak)`;
    - nama aturan yang tidak dikenal → `ValueError`.
  - **`jalankan_semua(..., letak=None)`:** `aturan.letak`, `tersaring_letak`, `per_video[].tersaring_letak`.
  - **CLI `jalan --letak <nama>`.** `lembar_bingkai` mendapat hal yang sama: `buat_lembar(..., letak=None)`, `--letak`, dan
    `tersaring_letak` per baris.
  - **Uji image tambahan:** `rantai.py jalan --kendaraan ... --cara potong --letak ry0.4` dan
    `lembar_bingkai.py lembar ... --letak ry0.4` pada video buatan → `EXIT=0` dan `letak` tercatat.

  Run gerbang lab → Expected `251 passed`; image tambahan → `31 passed`. Commit.

  *Hasil:*
  - Merah dilihat (`2 failed`, `unexpected keyword argument 'letak'`), lalu gerbang lab `251 passed`.
  - **Dikoreksi saat menjalankan:** kembalian `jalankan_video` tetap tiga nilai. `tersaring` kini dict `{"kendaraan", "letak"}`,
    supaya uji lama yang membongkar tiga nilai tidak berubah.
  - **Image tambahan `30 passed`, bukan 31:** uji baris perintah rantai dan lembar bingkai `--letak` digabung menjadi satu. Uji
    itu ditulis sesudah kode, jadi tidak dilihat merah.

### Task 4: Label sisi latih

- [x] **Step 1:** Sesudah Task 1, mesin tenang. Rantai di sisi latih dengan `--kendaraan ... --cara potong --ambang 0.25
  --simpan-penampakan` → `data/keluaran/rantai-latih-fase1-r21`, di latar dengan perekam proses.
- [x] **Step 2:** `lembar_rantai.py lembar ... /kerja/data/keluaran/lembar-latih-fase1-r21` (urut sha, 120 baris).

  *Hasil (17 Okt):*
  - Rantai di 39 video latih (01.54–02.45): 29.970 gambar sampel, **100 kedatangan** (30 yakin); siang 85, tak jelas 15.
  - Lembar memuat ke-100 kedatangan itu, di 5 halaman, karena jumlahnya di bawah 120.
  - Sisi latih menghasilkan jauh lebih sedikit kedatangan daripada sisi uji (425). Label yang tersedia untuk memilih aturan juga
    lebih sedikit.
- [x] **Step 3: BERHENTI.** Owner menyebut nomor baris yang **bukan plat**. Baris lain dihitung plat, baik terbaca maupun tidak.

  *Hasil (17 Okt):*
  - Owner menyebut 25 baris bukan plat, 22 baris buram, dan 1 baris salah baca.
  - Yang buram dan yang salah baca tetap plat, jadi plat 75 dan bukan plat 25. Dari 25 bukan plat, 7 berstatus "yakin".

### Task 5: Banding dan pilih

- [x] **Step 1:** Jawaban owner (nomor saja) → `letak.py banding .../penampakan.jsonl .../lembar-rantai.json
  .../banding-letak.json --bukan-plat <...>`.
- [x] **Step 2:** Catat tabel 24 aturan dan aturan terpilih di rencana ini. Bila aturan terpilih adalah `tanpa`, saringan tidak
  dipakai, dan itu dilaporkan apa adanya.

  *Hasil (17 Okt), plat 75, bukan plat 25 (7 "yakin"). Batas 90% plat berarti minimal 68 plat lolos:*

  | Aturan | Plat lolos | Bukan plat lolos | Bukan plat "yakin" lolos |
  |---|---|---|---|
  | tanpa | 75 | 25 | 7 |
  | rp | 75 | 25 | 7 |
  | rx0.3 | 74 | 18 | 5 |
  | ry0.4 | 73 | 23 | 7 |
  | ry0.6 | 66 | 17 | 7 |
  | tampak | 72 | 19 | 5 |
  | rp_tampak | 72 | 19 | 5 |
  | rx0.3_rp | 74 | 18 | 5 |
  | rx0.3_tampak | 71 | 14 | 4 |
  | ry0.4_rp | 73 | 23 | 7 |
  | ry0.4_rx0.3 | 72 | 17 | 5 |
  | ry0.4_tampak | 70 | 17 | 5 |
  | ry0.6_rp | 66 | 17 | 7 |
  | ry0.6_rx0.3 | 65 | 13 | 5 |
  | ry0.6_tampak | 64 | 12 | 5 |
  | rx0.3_rp_tampak | 71 | 14 | 4 |
  | ry0.4_rp_tampak | 70 | 17 | 5 |
  | ry0.4_rx0.3_rp | 72 | 17 | 5 |
  | **ry0.4_rx0.3_tampak** | **69** | **13** | **4** |
  | ry0.6_rp_tampak | 64 | 12 | 5 |
  | ry0.6_rx0.3_rp | 65 | 13 | 5 |
  | ry0.6_rx0.3_tampak | 63 | 10 | 4 |
  | ry0.4_rx0.3_rp_tampak | 69 | 13 | 4 |
  | ry0.6_rx0.3_rp_tampak | 63 | 10 | 4 |

  - **Terpilih menurut aturan: `ry0.4_rx0.3_tampak`.** Ia seri dengan `ry0.4_rx0.3_rp_tampak`, lalu menang karena syaratnya lebih
    sedikit.
  - Saringan ini membuang 12 dari 25 bukan plat dan 3 dari 7 bukan plat "yakin", dengan ongkos 6 dari 75 plat (8%).
  - Rasio plat (`rp`) tidak membuang apa pun.
  - **Bacaan agen: efeknya sedang.** Separuh benda bukan plat masih berada di bagian bawah-tengah kendaraan yang tampak depan atau
    belakang. Saringan letak saja tidak cukup; pembeda plat dan bukan plat perlu juga dari isi potongannya.

### Task 6: Ukur sekali di set uji

- [x] **Step 1:** Rantai di sisi uji: `--kendaraan ... --cara potong --ambang 0.25 --letak <terpilih>` →
  `rantai-uji-fase1-r21`, di latar dengan perekam proses.

  *Hasil (17 Okt, 03.39–05.58):* `--letak ry0.4_rx0.3_tampak`.
  - **Kedatangan:** 291, dengan 84 yakin. Rencana 20: 425 (91).
  - **Dibuang aturan letak:** 3.546 kotak plat, sebelum dibaca.
  - **Per kategori:** siang 290, campuran 1.
  - Uji sesi lain menyala di 265 dari 812 rekaman proses, jadi kecepatannya tidak dipakai.
- [x] **Step 2:** Lembar kedatangan (`--urut sha`, 120 baris) dan lembar bingkai (`--per-video 1 --kendaraan ... --cara potong
  --ambang 0.25 --letak <terpilih>`). Bingkainya sama dengan tiga lembar bingkai sebelumnya, dicek tanpa melihat kotak per
  bingkai.

  *Hasil:*
  - Lembar kedatangan: 120 baris dari 291, di 6 halaman.
  - Lembar bingkai: 41 bingkai di 11 halaman. Sama dengan R17, R19, dan R20 pada 41 dari 41 (`banding-bingkai-21.mjs`).
- [x] **Step 3: BERHENTI.** Owner memeriksa kedua lembar dengan petunjuk Rencana 20.
- [x] **Step 4:** `nilai` keduanya dan `status-per-jenis` (per sudut).

  *Hasil (17 Okt).* Jawaban owner dipecah oleh `jawaban-21-uji.mjs`; isinya hanya nomor.
  - **Lembar kedatangan:**
    - bukan plat 52, tak terbaca 50, motor 14;
    - dinilai 18: 16 benar-yakin, 1 benar-ragu, 1 salah-ragu, 0 salah-yakin.
  - **"Yakin" di lembar 52:** 16 benar, 26 bukan plat (parkiran 20, kamera diam lain 6), 10 tak terbaca.
  - **Video gerbang:** 12 "yakin" benar, 0 bukan plat.
  - **Lembar bingkai:**
    - plat terbaca terlewat: bingkai 12;
    - plat buram terlewat: 2, 3, 5, 6, 13, 15, 19, 26, 38, 41;
    - benar: 17;
    - hitungan owner 11 dari 12, ketat 1 dari 2.
  - **Pemeriksaan sesudahnya** (`diam-parkiran-21.py`, hitungan saja):
    - 20 "yakin" bukan plat di parkiran berasal dari 1 video, dan 6 di kamera diam lain dari 1 video;
    - 23 dari 26 punya kedatangan lain berteks sama di video yang sama. Pembanding: plat sungguhan 21 dari 26.
  - **Keputusan agen (K37):** saringan letak tidak dijadikan bawaan. Ia membuang plat yang ditemukan di R20 (bingkai 12 dan 38) dan
    tidak mengurangi bukan plat di lembar.

### Task 7: Bukti, laporan, catatan

- [x] **Step 1:** Pemeriksa bukti dengan kontrol positif (larangan ditambah bacaan rantai baru), lalu salin hitungan.

  *Hasil:* `periksa-bukti-21.py`. Larangan 11.431; kontrol positif menemukan 1.697 dari minimal 1.692. Lima berkas bersih, lalu
  disalin ke `bukti/` dengan awalan `2026-10-17-bukan-plat-di-dalam-kendaraan`.
- [x] **Step 2:** Laporan `bukti/<tanggal>-bukan-plat-di-dalam-kendaraan.md`:
  - tabel 24 aturan di sisi latih;
  - titik awal, R19, R20, dan R21 di set uji, per sudut;
  - batas.
- [x] **Step 3:** ROADMAP, `CLAUDE.md` §7 (`letak.py`, `--letak`, `kendaraan` di `penampakan.jsonl`), gerbang penuh, commit.
  Lanjut ke Rencana 22 (pembaca).

  *Dikoreksi saat menutup (17 Okt):* Rencana 22 bukan pembaca. Owner menyarankan menambah video dari internet atau YouTube (K41),
  karena plat yang bisa dinilai per lembar hanya 18–23. Jadi Rencana 22 adalah video CCTV gelombang keempat, dan pembaca pindah ke
  Rencana 23.
