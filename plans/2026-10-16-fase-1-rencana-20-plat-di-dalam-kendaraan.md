# Fase 1, Rencana 20: Plat terlewat — plat dicari di dalam potongan kendaraan (K39 langkah 3) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Berhenti dua kali untuk owner: lembar kendaraan latih (Task 4) dan dua lembar uji (Task 6).

**Goal:** Plat yang terlewat berkurang. Di Rencana 19, plat terlewat di 12 dari 13 bingkai uji berplat, padahal kendaraannya
selalu ditemukan. Calon cara mencari plat dipilih di **sisi latih**, dari label owner "kendaraan yang platnya terbaca", lalu
yang terpilih diukur sekali di set uji dengan lembar yang sama seperti Rencana 17 dan 19.

**Architecture:**
- **`tools/lab/kendaraan.py`:** `cari_dalam_kendaraan` menjalankan langkah 3 usulan owner (K39) secara harfiah:
  - plat dicari di dalam potongan tiap kendaraan, yang diperlebar sedikit;
  - letterbox pencari memperbesar potongan, jadi plat kecil mendapat lebih banyak piksel;
  - kotak dikembalikan ke koordinat gambar utuh.
- **`rantai.py` dan `lembar_bingkai.py`:** `--cara saring|potong`. `saring` adalah cara Rencana 19, dan tetap menjadi bawaan.
- **`tools/lab/lembar_kendaraan.py` (baru):**
  - **lembar latih untuk owner:** kendaraan berkotak biru bernomor; owner menyebut nomor kendaraan yang platnya terbaca;
  - **`banding`:** menilai 12 calon (pencari lama/baru × saring/potong × ambang 0,1/0,25/0,5) pada gambar yang sama, tanpa
    menambah kerja owner;
  - **`pilih`:** menerapkan aturan yang ditulis di rencana ini, sebelum angka dilihat.

**Tech Stack:** Python di lab dan image tambahan (`-Fpo`), CPU. Tidak ada latihan GPU.

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Hasil Rencana 19 di set uji | Bukan plat 6 dari 120 baris; plat terlewat di 12 dari 13 bingkai berplat; kendaraan ditemukan di semua bingkai berplat yang disebut owner | `bukti/2026-10-16-pencari-plat-cctv.md` |
| Ambang pencari | Lama (plat-lighting saja) 0,25; baru (CCTV latih) 0,5 | `mesin.json` keduanya |
| Video latih yang tidak dipakai melatih pencari baru | 4 dari 39 (sisi validasi `dataset_cctv.sisi_validasi`), semuanya gerbang (siang 2, campuran 1, tak jelas 1) | `data/alat-sementara/hitung-valid-20.mjs` |

**Akibat untuk cara memilih:**
- **Pencari lama** tidak pernah melihat CCTV. Perbandingan calonnya adil di semua 39 video latih.
- **Pencari baru** dilatih dengan gambar dari 35 video latih, jadi ia diuntungkan di sana. Ia hanya boleh menang bila di 4 video
  validasi ia tidak menemukan lebih sedikit daripada calon pencari lama yang terbaik.

## Aturan memilih (ditetapkan sebelum angka dilihat)

1. Urutkan calon menurut:
   1. kendaraan berplat terbaca yang mendapat kotak plat (`ditemukan`), terbanyak dulu;
   2. jumlah kotak salah tempat (`kotak_lebih + kotak_kendaraan_lain + kotak_luar`), tersedikit dulu;
   3. nama calon (supaya tetap).
2. Bila calon teratas memakai pencari baru, dan di video validasi `ditemukan`-nya lebih kecil daripada calon pencari lama
   teratas, yang dipilih calon pencari lama teratas.
3. Set uji tidak dipakai memilih.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/kendaraan.py`, `tools/lab/uji/test_kendaraan.py` (ubah) | `cari_dalam_kendaraan` | 1 |
| `tools/lab/rantai.py`, `tools/lab/lembar_bingkai.py`, ujinya (ubah) | `--cara saring\|potong` | 2 |
| `tools/lab/lembar_kendaraan.py`, `tools/lab/uji/test_lembar_kendaraan.py` (baru) | Lembar kendaraan latih, `banding`, `pilih` | 3 |
| `tools/lab/uji_fpo/test_rantai_sungguhan.py` (ubah) | Uji rantai baris perintah dengan model sungguhan | 3 |
| `bukti/<tanggal>-plat-di-dalam-kendaraan*` | Hitungan dan laporan | 7 |

---

### Task 1: `cari_dalam_kendaraan`

- [x] **Step 1: Uji merah**, ditambahkan di `tools/lab/uji/test_kendaraan.py`:

```python
def cari_relatif(gambar):
    """Pencari tiruan: satu kotak di bagian bawah tengah gambar MASUKAN, apa pun ukurannya, ditambah kotak lemah."""
    t, l = gambar.shape[:2]
    return [(0.4 * l, 0.7 * t, 0.6 * l, 0.8 * t, 0.9), (0.0, 0.0, 0.1 * l, 0.1 * t, 0.05)]


def test_cari_dalam_kendaraan_memetakan_kotak_potongan_ke_gambar_utuh():
    gambar = np.zeros((400, 600, 3), np.uint8)
    motor = (100.0, 100.0, 200.0, 300.0, 0.8, "motor")

    hasil = kd.cari_dalam_kendaraan(gambar, [motor], cari_relatif, 0.25, margin=0.1)

    # Potongan x 90..210, y 80..320 (diperlebar 10%): kotak di 0,4-0,6 lebar dan 0,7-0,8 tinggi potongan.
    assert [tuple(round(x) for x in k[:4]) + (k[5],) for k in hasil] == [(138, 248, 162, 272, "motor")]


def test_cari_dalam_kendaraan_melewati_kendaraan_pendek_dan_menyatukan_kotak_kembar():
    gambar = np.zeros((400, 600, 3), np.uint8)
    besar = (100.0, 100.0, 200.0, 300.0, 0.8, "mobil")
    hampir_sama = (101.0, 100.0, 201.0, 300.0, 0.7, "truk")
    pendek = (400.0, 100.0, 500.0, 120.0, 0.9, "mobil")  # tinggi 20 piksel < MIN_TINGGI

    hasil = kd.cari_dalam_kendaraan(gambar, [besar, hampir_sama, pendek], cari_relatif, 0.25, margin=0.0)

    # Dua kotak hampir sama (IoU 0,9) dengan yakin yang sama: satu disimpan, entah dari kendaraan yang mana.
    assert len(hasil) == 1 and hasil[0][5] in {"mobil", "truk"}


def test_cari_dalam_kendaraan_membuang_kotak_yang_tengahnya_di_luar_kendaraannya():
    gambar = np.zeros((400, 600, 3), np.uint8)

    def cari_tepi(potongan):
        t, l = potongan.shape[:2]
        return [(0.0, 0.0, 0.08 * l, 0.08 * t, 0.9)]  # di pojok margin, di luar kotak kendaraan

    assert kd.cari_dalam_kendaraan(gambar, [(100.0, 100.0, 200.0, 300.0, 0.8, "motor")], cari_tepi, 0.25, margin=0.2) == []
```

Merah yang diharapkan: `AttributeError: module 'kendaraan' has no attribute 'cari_dalam_kendaraan'`.

- [x] **Step 2:** di `tools/lab/kendaraan.py`:

```python
MIN_TINGGI = 40  # piksel gambar utuh; kendaraan yang lebih pendek tidak dicari platnya (plat manusia pun tak terbaca)
MARGIN = 0.1


def cari_dalam_kendaraan(gambar, kendaraan, cari, ambang, margin=MARGIN, min_tinggi=MIN_TINGGI):
    """K39 langkah 3: plat dicari di dalam potongan tiap kendaraan setinggi minimal min_tinggi, yang diperlebar margin dari lebar
    dan tingginya. Letterbox pencari memperbesar potongan kecil. Kotak di atas ambang dikembalikan ke koordinat gambar utuh dan
    ditambah jenis kendaraannya; yang tengahnya di luar kendaraannya dibuang; kotak kembar dari kendaraan yang bertumpuk disatukan
    dengan NMS. Kembali: [(x1, y1, x2, y2, yakin, jenis)]."""
    tinggi, lebar = gambar.shape[:2]
    semua = []
    for v in kendaraan:
        if v[3] - v[1] < min_tinggi:
            continue
        mx, my = margin * (v[2] - v[0]), margin * (v[3] - v[1])
        x1, y1 = max(0, int(v[0] - mx)), max(0, int(v[1] - my))
        x2, y2 = min(lebar, int(np.ceil(v[2] + mx))), min(tinggi, int(np.ceil(v[3] + my)))
        if x2 - x1 < 2 or y2 - y1 < 2:
            continue
        for k in cari(gambar[y1:y2, x1:x2]):
            if k[4] < ambang:
                continue
            utuh = (k[0] + x1, k[1] + y1, k[2] + x1, k[3] + y1, k[4])
            if kendaraan_pemuat(utuh, [v]) is not None:
                semua.append((*utuh, v[5]))
    if not semua:
        return []
    simpan = pyx.nms(np.array([s[:4] for s in semua], np.float64), np.array([s[4] for s in semua], np.float64))
    return [semua[i] for i in simpan]
```

  Run gerbang lab → Expected `234 passed` (231 + 3). Commit.

  *Hasil:* merah dilihat (`3 failed`, `AttributeError`), lalu `8 passed` di berkas uji itu.

### Task 2: `--cara saring|potong` di rantai dan lembar bingkai

- [x] **Step 1: Uji merah**, ditambahkan di `tools/lab/uji/test_rantai.py`:

```python
def test_cara_potong_mencari_plat_di_dalam_potongan_kendaraan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dipanggil = []

    def cari_ukuran(gambar):
        dipanggil.append(gambar.shape[:2])
        t, l = gambar.shape[:2]
        return [(0.4 * l, 0.4 * t, 0.6 * l, 0.6 * t, 0.9)]

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "mobil")]
    kendaraan.ambang = 0.25

    r = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_ukuran, baca_tiruan, 0.25, tmp_path / "k",
                              cari_kendaraan=kendaraan, cara="potong")

    assert r["kedatangan"] == 1 and r["aturan"]["cara_kendaraan"] == "potong"
    # Hanya potongan kendaraan (x 32..128, y 14..82, diperlebar 10%) yang dicari, tidak pernah gambar utuh 96 x 160.
    assert set(dipanggil) == {(68, 96)}
    assert r["waktu_ms"]["kendaraan"]["n"] == 5
```

  Ditambahkan di `tools/lab/uji/test_lembar_bingkai.py`:

```python
def test_lembar_cara_potong_mencatat_cara_dan_kotak(tmp_path):
    video(tmp_path / "a.avi")

    def cari(gambar):
        t, l = gambar.shape[:2]
        return [(0.4 * l, 0.4 * t, 0.6 * l, 0.6 * t, 0.9)]

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "motor")]

    lb.buat_lembar([{"berkas": "a.avi"}], tmp_path, cari, 0.25, tmp_path / "keluar", per_video=1, maks=1,
                   cari_kendaraan=kendaraan, cara="potong")

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert isi["cara_kendaraan"] == "potong" and [(b["kotak"], b["kendaraan"]) for b in isi["baris"]] == [(1, 1)]
```

Merah yang diharapkan: `unexpected keyword argument 'cara'` di kedua uji.

- [x] **Step 2:**
  - **`rantai.jalankan_video(..., cari_kendaraan=None, cara="saring")`:** bila `cara == "potong"` dan ada `cari_kendaraan`:
    - kendaraan dicari di **tiap** gambar sampel (waktunya masuk `waktu["kendaraan"]`);
    - kotak plat berasal dari `cari_dalam_kendaraan(gambar, kendaraan, cari, ambang)` (waktunya masuk `waktu["cari"]`);
    - `tersaring` tetap 0.

    Cara lain tetap seperti Rencana 19. `cara` yang bukan `saring` atau `potong` → `ValueError`.
  - **`jalankan_semua(..., cara="saring")`:** meneruskan `cara`; `aturan.cara_kendaraan` = `cara` bila ada `cari_kendaraan`,
    selain itu `None`.
  - **CLI `jalan --cara saring|potong`** (bawaan `saring`).
  - **`lembar_bingkai.buat_lembar(..., cara="saring")`:** cara `potong` memakai `cari_dalam_kendaraan`; json mencatat
    `cara_kendaraan`; CLI `lembar --cara`.

  Run gerbang lab → Expected `236 passed`. Commit.

  *Hasil:* merah dilihat (`2 failed`, `unexpected keyword argument 'cara'`), lalu gerbang lab `236 passed` (`EXIT=0`).

### Task 3: Lembar kendaraan latih, `banding`, dan `pilih`

- [x] **Step 1: Uji merah** `tools/lab/uji/test_lembar_kendaraan.py`:

```python
"""Uji tools/lab/lembar_kendaraan.py (Rencana 20, K39): lembar kendaraan bernomor dari video buatan, jawaban owner, penilaian
calon, aturan memilih, dan banding dari video sampai hitungan, dengan pencari tiruan."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_kendaraan as lk  # noqa: E402


def video(jalur, n=20):
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), 10, (320, 192))
    for _ in range(n):
        tulis.write(np.full((192, 320, 3), 90, np.uint8))
    tulis.release()


TINGGI = (20.0, 20.0, 120.0, 180.0, 0.8, "mobil")
PENDEK = (200.0, 20.0, 260.0, 40.0, 0.7, "motor")  # tinggi 20 < MIN_TINGGI: tidak bernomor


def dua_kendaraan(gambar):
    return [TINGGI, PENDEK]
dua_kendaraan.ambang = 0.25


def test_baca_jawaban_per_bingkai_dan_penolakan():
    assert lk.baca_jawaban("3: 1, 4; 7: 2\n9:") == {3: {1, 4}, 7: {2}, 9: set()}
    assert lk.baca_jawaban("") == {}
    with pytest.raises(ValueError, match="jawaban"):
        lk.baca_jawaban("3 1 4")


def test_buat_lembar_hanya_kendaraan_tinggi_yang_bernomor(tmp_path):
    video(tmp_path / "a.avi")

    r = lk.buat_lembar([{"berkas": "a.avi", "sudut": "gerbang", "kategori": "siang"}], tmp_path, dua_kendaraan,
                       tmp_path / "keluar", per_video=2, maks=5)

    isi = json.loads((tmp_path / "keluar" / "lembar-kendaraan.json").read_text())
    assert r == {"video": 1, "bingkai": 2, "kendaraan_bernomor": 2, "halaman": 1}
    assert [b["gambar"] for b in isi["baris"]] == [5, 15]
    assert isi["baris"][0]["bernomor"] == [list(TINGGI[:4]) + [TINGGI[4], TINGGI[5]]] and len(isi["baris"][0]["kendaraan"]) == 2
    halaman = cv2.imread(str(tmp_path / "keluar" / "lembar-kendaraan-1.png"))
    assert tuple(halaman[40 + 100, 20]) == lk.BIRU


def lembar_satu(bernomor, kendaraan=None, video_="a.avi"):
    return {"baris": [{"nomor": 1, "video": video_, "gambar": 5, "bernomor": bernomor,
                       "kendaraan": kendaraan if kendaraan is not None else bernomor}]}


def test_nilai_calon_menghitung_ditemukan_dan_kotak_salah_tempat():
    a, b = [0, 0, 100, 100, 0.9, "mobil"], [200, 0, 300, 100, 0.9, "motor"]
    lembar = lembar_satu([a, b])
    kotak = {1: [(40, 60, 60, 70, 0.9), (10, 10, 20, 20, 0.5), (240, 60, 260, 70, 0.9), (500, 500, 510, 505, 0.9)]}

    h = lk.nilai_calon(lembar, {1: {1}}, kotak)

    assert h == {"plat_terbaca": 1, "ditemukan": 1, "kotak_lebih": 1, "kotak_kendaraan_lain": 1, "kotak_luar": 1}
    with pytest.raises(ValueError, match="kendaraan"):
        lk.nilai_calon(lembar, {1: {3}}, kotak)
    with pytest.raises(ValueError, match="bingkai"):
        lk.nilai_calon(lembar, {2: {1}}, kotak)


def hasil_(nama, ditemukan, salah, ditemukan_valid):
    return {"nama": nama, "pencari": nama.split("-")[0], "semua": {"ditemukan": ditemukan, "kotak_lebih": salah,
            "kotak_kendaraan_lain": 0, "kotak_luar": 0}, "validasi": {"ditemukan": ditemukan_valid}}


def test_pilih_menurut_aturan_dan_pencari_baru_harus_tidak_kalah_di_validasi():
    calon = [hasil_("lama-potong-0.25", 10, 3, 2), hasil_("lama-saring-0.25", 10, 1, 2), hasil_("baru-potong-0.1", 12, 0, 1)]

    assert lk.pilih(calon)["nama"] == "lama-saring-0.25"  # baru menang di semua, tetapi kalah di validasi (1 < 2)
    calon[2]["validasi"]["ditemukan"] = 2
    assert lk.pilih(calon)["nama"] == "baru-potong-0.1"


def test_banding_dari_video_potong_menemukan_yang_saring_lewatkan(tmp_path):
    video(tmp_path / "a.avi")
    lk.buat_lembar([{"berkas": "a.avi", "sudut": "gerbang", "kategori": "siang"}], tmp_path, dua_kendaraan, tmp_path / "keluar",
                   per_video=1, maks=1)
    lembar = json.loads((tmp_path / "keluar" / "lembar-kendaraan.json").read_text())

    def cari_bawah(gambar):
        """Kotak di 0,45-0,55 lebar dan 0,8-0,9 tinggi MASUKAN: di gambar utuh tengahnya (160, 163) di luar kendaraan;
        di potongan kendaraan tengahnya di dalam."""
        t, l = gambar.shape[:2]
        return [(0.45 * l, 0.8 * t, 0.55 * l, 0.9 * t, 0.3)]

    hasil = lk.banding(lembar, tmp_path, {"lama": cari_bawah}, {1: {1}}, validasi=set())

    per_nama = {h["nama"]: h["semua"] for h in hasil}
    assert len(hasil) == 6  # satu pencari x 2 cara x 3 ambang
    assert per_nama["lama-saring-0.25"]["ditemukan"] == 0 and per_nama["lama-potong-0.25"]["ditemukan"] == 1
    assert per_nama["lama-potong-0.5"]["ditemukan"] == 0  # yakin 0,3 di bawah ambang
```

Merah yang diharapkan: `ModuleNotFoundError: No module named 'lembar_kendaraan'`.

  Ditambahkan di `tools/lab/uji_fpo/test_rantai_sungguhan.py` (uji rantai baris perintah; tanpa ini jalur CLI bisa mati senyap):
  - `rantai.py jalan --kendaraan ... --cara potong` pada video buatan: `EXIT=0` dan `aturan.cara_kendaraan == "potong"`.
  - `lembar_kendaraan.py lembar` dengan pencari kendaraan sungguhan pada dua video buatan dan pembagian `--sisi latih`: `EXIT=0`,
    `lembar-kendaraan.json` ada, hanya video sisi latih, layar tanpa nama berkas.
  - `lembar_kendaraan.py banding` pada lembar itu dengan pencari lama dan baru sungguhan, `--terbaca ""`: `EXIT=0` dan
    `banding.json` memuat 12 calon dan satu `terpilih`.

- [x] **Step 2: Tulis `tools/lab/lembar_kendaraan.py`:**
  - `PER_VIDEO = 2`, `MAKS = 80`, `LEBAR = 960`, `PER_HALAMAN = 4`, `BIRU = (200, 0, 0)`, dan
    `AMBANG_CALON = (0.1, 0.25, 0.5)`.
  - **`gambar_bernomor(gambar, bernomor)`:** salinan gambar dengan kotak biru dan nomornya (1, 2, ...), di pita biru kecil di pojok
    kiri atas kotak.
  - **`buat_lembar(daftar, folder_video, cari_kendaraan, keluar, per_video, maks)`:**
    - gambar diambil dengan `lembar_bingkai.titik_ambil`;
    - `kendaraan` = semua kendaraan; `bernomor` = yang tingginya minimal `kendaraan.MIN_TINGGI`;
    - kartu dibuat seperti `lembar_bingkai.kartu` (nomor bingkai di pita atas, tidak diperbesar);
    - json berisi `per_video`, `maks`, `ambang_kendaraan`, `min_tinggi`, `halaman`, dan `baris` (`nomor`, `video`, `gambar`,
      `sudut`, `kategori`, `kendaraan`, `bernomor`);
    - kembali: hitungan saja.
  - **`baca_jawaban(teks)`:**
    - format: `"<bingkai>: <nomor>, <nomor>; ..."`, dengan baris baru juga sebagai pemisah;
    - butir tanpa titik dua → `ValueError("jawaban ...")`.
  - **`nilai_calon(lembar, terbaca, kotak_per_bingkai)`:**
    - nomor bingkai yang tidak ada → `ValueError("... bingkai ...")`; nomor kendaraan di luar `bernomor` →
      `ValueError("... kendaraan ...")`;
    - tiap kotak dihubungkan ke kendaraan bernomor terkecil yang memuat tengahnya. Kotak pertama di kendaraan berplat terbaca
      menambah `ditemukan`, kotak berikutnya di kendaraan yang sama menambah `kotak_lebih`. Kotak di kendaraan bernomor lain
      menambah `kotak_kendaraan_lain`, dan kotak yang tidak di kendaraan bernomor mana pun menambah `kotak_luar`;
    - kembali: hitungan.
  - **`banding(lembar, folder_video, pencari, terbaca, validasi)`:**
    - `pencari`: nama → fungsi cari. Tiap bingkai dibaca sekali dari video.
    - Untuk tiap pencari: `cari(gambar)` sekali untuk cara `saring`, lalu per ambang `saring` dengan **semua** kendaraan di
      bingkai itu, sama seperti rantai.
    - `cari_dalam_kendaraan(gambar, kendaraan, cari, min(AMBANG_CALON))` sekali untuk cara `potong`, lalu disaring per ambang.
      Menyaring sesudah NMS sama dengan NMS sesudah menyaring, karena kotak hanya dibuang oleh kotak yang lebih yakin.
    - Kembali: daftar `{"nama": f"{pencari}-{cara}-{ambang}", "pencari", "cara", "ambang", "semua": nilai_calon(...),
      "validasi": nilai_calon(...)}` pada bingkai dari video di `validasi` saja.
  - **`pilih(hasil)`:** aturan di atas. Kembali: calon terpilih ditambah `alasan`.
  - **CLI:**
    - `lembar manifes folder_video pembagian folder_kendaraan keluar [--sisi latih] [--per-video] [--maks]`;
    - `banding lembar.json folder_video folder_pencari_lama folder_pencari_baru keluar.json --terbaca <teks atau @berkas>`:
      - pencari dimuat lewat `PencariYolox`;
      - video validasi dihitung dengan `dataset_cctv.sisi_validasi`;
      - `banding.json` berisi semua calon dan `terpilih`;
      - layar menampilkan tabel hitungan.
    - Galat hanya mencetak jenisnya.

  Run gerbang lab → Expected `241 passed` (236 + 5). Commit.

  *Hasil:*
  - Merah dilihat: `ModuleNotFoundError: No module named 'lembar_kendaraan'`. Lalu `5 passed`, dan gerbang lab `241 passed`.
  - Uji image tambahan baru ditulis sesudah kode, jadi tidak dilihat merah. Isinya:
    - rantai `--cara potong`;
    - `lembar_kendaraan.py lembar` dan `banding` dengan model sungguhan (satu uji);
    - `lembar_bingkai.py lembar --cara potong`. Uji ini tidak ada di rencana; ia ditambahkan karena jalur baris perintahnya baru.

    Hasilnya `28 passed`.

### Task 4: Lembar kendaraan latih

- [x] **Step 1:** Mesin tenang. Uji image tambahan → Expected `28 passed` (25 + 3). *Hasil:* `28 passed` (`EXIT=0`).
- [x] **Step 2:** `lembar_kendaraan.py lembar ... --sisi latih` → `data/keluaran/lembar-kendaraan-latih/`.

  *Hasil (16 Okt):* 39 video, 78 bingkai, 138 kendaraan bernomor, di 20 halaman.
- [x] **Step 3: BERHENTI.** Owner menyebut, per bingkai, nomor kendaraan yang platnya bisa ia baca (`3: 1, 4`), dan nomor
  bingkai yang memuat kendaraan berplat terbaca tanpa kotak biru. Owner tidak mengetik nomor plat.

### Task 5: Banding dan pilih

- [x] **Step 1:** Jawaban owner ditulis ke `data/alat-sementara/jawaban-20-kendaraan.txt` (nomor saja).
  `lembar_kendaraan.py banding ... --terbaca @/kerja/data/alat-sementara/jawaban-20-kendaraan.txt` →
  `data/keluaran/lembar-kendaraan-latih/banding.json`.
- [x] **Step 2:** Catat tabel 12 calon (semua dan validasi) dan calon terpilih di rencana ini. Kendaraan berplat terbaca yang tak
  berkotak biru dicatat sebagai batas pencari kendaraan.

  *Hasil (16 Okt).*
  - **Jawaban owner:** 16 bingkai dengan 17 kendaraan berplat terbaca. Jawaban pertama hanya menyebut nomor bingkai. Untuk 10
    bingkai yang punya lebih dari satu kendaraan bernomor, owner ditanya lagi dan menyebut nomor kendaraannya.
  - **Kotak biru:** tidak ada bingkai yang disebut memuat kendaraan berplat terbaca tanpa kotak biru.
  - **Pengamatan owner:** banyak plat tak terbaca hanya karena buram, karena resolusi, jarak, atau gerak. Ini dicatat sebagai K40.

  | Calon | Ditemukan (dari 17) | Lebih | Kendaraan lain | Luar | Tanpa 4 bingkai dekat latih (dari 13) |
  |---|---|---|---|---|---|
  | lama-saring-0.1 | 3 | 0 | 2 | 0 | 1 |
  | lama-saring-0.25 | 3 | 0 | 1 | 0 | 1 |
  | lama-saring-0.5 | 2 | 0 | 0 | 0 | 0 |
  | lama-potong-0.1 | 8 | 2 | 5 | 0 | 6 |
  | lama-potong-0.25 | 7 | 1 | 1 | 0 | 5 |
  | lama-potong-0.5 | 7 | 1 | 1 | 0 | 5 |
  | baru-saring-0.1 | 5 | 0 | 1 | 0 | 2 |
  | baru-saring-0.25 | 4 | 0 | 0 | 0 | 1 |
  | baru-saring-0.5 (Rencana 19) | 3 | 0 | 0 | 0 | 1 |
  | baru-potong-0.1 | 11 | 1 | 4 | 0 | 8 |
  | **baru-potong-0.25** | **11** | 1 | 1 | 0 | **8** |
  | baru-potong-0.5 | 9 | 1 | 0 | 0 | 7 |

  - **Terpilih menurut aturan: `baru-potong-0.25`.** Ia seri dengan `baru-potong-0.1` dalam temuan, tetapi kotak salah tempatnya
    lebih sedikit (2 lawan 5).
  - **Cara potong menemukan jauh lebih banyak di kedua pencari:** lama 3 → 7–8, baru 3–5 → 9–11.
  - **Penjaga validasi kosong.** Keempat video validasi tidak punya satu pun plat terbaca (0/0), jadi langkah 2 aturan tidak bisa
    bekerja.
  - **Pemeriksaan pengganti (tambahan, tidak ada di aturan asli):**
    - `dekat-latih-20.py` menemukan 4 dari 16 bingkai berlabel (18, 33, 60, 78) yang punya gambar latih berplat dari video yang
      sama dalam 0,8–1,9 detik. Di bingkai itu kendaraannya kemungkinan ikut dilatih.
    - `banding-jauh-20.py` menilai ulang tanpa keempat bingkai itu. `baru-potong-0.25` tetap teratas: 8 dari 13, sedangkan calon
      pencari lama terbaik 6 dari 13.
    - Pilihan tetap.
  - **Ambang 0,25 berbeda dari ambang validasi pencari baru (0,5),** jadi rantai dan lembar bingkai di Task 6 diberi
    `--ambang 0.25`.

### Task 6: Ukur sekali di set uji

- [x] **Step 1:** Rantai di sisi uji dengan calon terpilih (`rantai-uji-fase1-r20`), di latar dengan perekam proses.

  *Hasil (16 Okt, 20.07–22.32):* `--kendaraan ... --cara potong --ambang 0.25`.
  - **Kedatangan:** 425, dengan 91 yakin. Rencana 19: 198 (22). Titik awal: 416 (41).
  - **Per kategori:** siang 423, campuran 1, malam 1.
  - **Jalur terlihat sekali:** 671.
  - **Kecepatan (median, 2 utas):** kendaraan 69,1 ms per gambar sampel; cari plat di potongan 63,8 ms per gambar sampel (p95
    491,9 ms, karena bingkai parkiran memuat banyak kendaraan); baca 14,7 ms.
  - Uji sesi lain menyala di 410 dari 838 rekaman proses, jadi kecepatan ini tidak dipakai.
- [x] **Step 2:** Dua lembar seperti Rencana 19:
  - lembar kedatangan (`--urut sha`, 120 baris);
  - lembar bingkai `--per-video 1 --kendaraan ... --cara <terpilih>`.

  Kedua lembar memakai bingkai yang sama dengan Rencana 17 dan 19, dan dicek dengan skrip banding bingkai.

  *Hasil:*
  - Lembar kedatangan: 120 baris dari 425, di 6 halaman.
  - Lembar bingkai: 41 bingkai di 11 halaman. Sama dengan Rencana 17 dan 19 pada 41 dari 41 (`banding-bingkai-20.mjs`). Kali ini
    kotak per bingkai yang sudah berlabel owner sengaja tidak dilihat sebelum owner memeriksa.
  - **Ditambahkan saat menjalankan:** `lembar_bingkai.py lembar` belum punya `--ambang`, jadi lembar akan memakai ambang
    validasi pencari baru (0,5), bukan 0,25 seperti rantai. `--ambang` ditambahkan dengan uji di image tambahan. Ujinya dilihat
    merah dulu (argparse menolak `--ambang`), dan uji image tambahan kini `29 passed`.
- [x] **Step 3: BERHENTI.** Owner memeriksa kedua lembar dengan petunjuk yang sama seperti Rencana 19. "Terlewat" dijawab dalam dua
  jenis, supaya hitungan ketat dan longgar bisa dibuat: plat terbaca, dan plat yang ada tetapi buram.
- [x] **Step 4:** `nilai` keduanya, lalu `status-per-jenis`.

  *Hasil (17 Okt).* Jawaban owner dipecah oleh `jawaban-20-uji.mjs`. Isinya hanya nomor; baris 15 ("tidak terbaca atau salah
  posisi") dihitung tak terbaca.
  - **Lembar kedatangan:**
    - bukan plat 46, tak terbaca 55, motor 2;
    - dinilai 19: 14 benar-yakin, 4 benar-ragu, 0 salah-ragu, 1 salah-yakin;
    - 18 baris tidak disebut, jadi dihitung benar.
  - **"Yakin" di lembar 43:** 14 benar, 1 salah, 18 bukan plat (14 di parkiran), 10 tak terbaca.
  - **Per sudut, benar (yakin) / bukan plat (yakin):**
    - gerbang 13 (10) / 6 (1);
    - kamera diam lain 5 (4) / 18 (3);
    - parkiran 0 / 22 (14).
  - **Lembar bingkai:**
    - plat terbaca terlewat: bingkai 6 dan 15;
    - plat buram terlewat: 2, 19, 22, 26, 41;
    - benar: 12, 17, 38;
    - sisanya tak jelas;
    - dua hitungan: owner 7 dari 10, ketat 2 dari 5.

### Task 7: Bukti, laporan, catatan

- [x] **Step 1:** Pemeriksa bukti dengan kontrol positif (larangan ditambah bacaan rantai baru), lalu salin hitungan.

  *Hasil:* `periksa-bukti-20.py`. Larangan 11.345; kontrol positif menemukan 1.611 dari minimal 1.606. Lima berkas hitungan
  bersih, lalu disalin ke `bukti/` dengan awalan `2026-10-17-plat-di-dalam-kendaraan`.
- [x] **Step 2:** Laporan `bukti/<tanggal>-plat-di-dalam-kendaraan.md`:
  - tabel 12 calon di sisi latih dan alasan memilih;
  - titik awal, Rencana 19, dan sesudah, di set uji;
  - batas.
- [x] **Step 3:** ROADMAP, `CLAUDE.md` §7 (`lembar_kendaraan`, `--cara`), gerbang penuh, commit. Lanjut ke Rencana 21 (pembaca).

  *Dikoreksi saat menutup (17 Okt):* Rencana 21 bukan pembaca. "Yakin" yang bukan plat (18 dari 43) adalah bahaya
  keselamatan. Karena itu Rencana 21 menyaring benda bukan plat di dalam kendaraan dengan langkah 2 usulan owner (tampak depan
  atau belakang) dan letak plat, dan pembaca pindah ke Rencana 22. Spec bagian 6 dan ROADMAP mencatat alasannya.
