# Fase 1, Rencana 24: Mesin jualan dari nol dengan bahan BOLEH-PRODUK (K44) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37), dalam dua bagian:
> - **Bagian A**, label dari tangkapan owner, ditulis dan dijalankan lebih dulu.
> - **Bagian B**, melatih pembaca dan pencari plat dari nol, ditulis sesudah jumlah label Bagian A diketahui.

**Goal (Bagian A):** 181 tangkapan layar CCTV dari owner (76 mobil, 105 motor; bahan `tangkapan-owner`, `BOLEH-PRODUK`, K44)
menjadi label yang diperiksa owner:
- kotak plat, untuk melatih pencari plat jualan;
- teks plat yang benar, untuk melatih pembaca jualan;
- daftar gambar yang platnya terlewat, untuk mengukur.

Usulan kotak dan bacaan dibuat mesin belajar sebagai alat bantu (K44); yang menjadi label hanya yang sudah diperiksa owner.

**Architecture (Bagian A):**
- **`tools/lab/baca_gambar.py` (baru):** membaca gambar diam dengan urutan rantai yang sama (kendaraan, plat di dalam potongan
  kendaraan, baca), memakai fungsi yang sudah ada di `kendaraan.py`, `rantai.py`, dan pembaca.
- **Keluarannya ditulis dalam bentuk yang dikenal `lembar_rantai.py`**, sehingga lembar dan penilaiannya tidak perlu alat baru.
- **Gambar tanpa plat yang ditemukan** masuk lembar terpisah, dengan kendaraan diberi kotak biru. Owner menyebut gambar mana yang
  sebenarnya memuat plat terbaca.
- **Pembagian latih/uji per gambar** menurut SHA-256 isi berkasnya: seperempat untuk uji.

**Tech Stack:** Python di image tambahan (`-Fpo`), CPU.

---

## Yang diukur sebelum rencana ini ditulis (18 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Tangkapan owner | 181 PNG (mobil 76, motor 105). Lebar median 1153 (mobil) dan 1107 (motor), tinggi sekitar 700; tidak ada yang kembar persis | `cek-capture-24.py` |
| Mesin yang boleh dijual sekarang | Hanya mesin-baca-1 (26–32% plat benar di INDO-ALPR). Pencari plat, pencari kendaraan, dan fpo-indo-1 `RISET-SAJA` | `data-asal/bahan.json`, `mesin.json` |
| Pembaca di potongan CCTV latih | 27 dari 52 plat terbaca dibaca salah oleh fpo-indo-1 | Rencana 23 Task 6 |

## Bagian A: Label dari tangkapan owner

### Task 1: `baca_gambar.py`

- [x] **Step 1: Uji merah** `tools/lab/uji/test_baca_gambar.py`:

```python
"""Uji tools/lab/baca_gambar.py (Rencana 24, K44): gambar diam dibaca dengan urutan rantai (kendaraan, plat di dalam kendaraan,
baca), keluaran berbentuk kedatangan.jsonl untuk lembar_rantai.py, nama berkas asli tidak muncul di keluaran atau layar, gambar
tanpa plat dicatat terpisah, dan pembagian latih/uji tetap per isi berkas."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_gambar as bg  # noqa: E402


def kendaraan(gambar):
    return [(40.0, 20.0, 200.0, 140.0, 0.8, "mobil")]


kendaraan.ambang = 0.25


def cari(gambar):
    t, l = gambar.shape[:2]
    return [(0.4 * l, 0.7 * t, 0.6 * l, 0.8 * t, 0.9)] if gambar.mean() > 60 else []


def baca(potongan):
    return "B1234XY", 0.9


def siapkan(tmp_path):
    for sub, nama, terang in (("capture cctv mobil", "B1234XY rahasia.png", 120), ("capture cctv motor", "gelap.png", 10)):
        (tmp_path / "capture" / sub).mkdir(parents=True)
        cv2.imwrite(str(tmp_path / "capture" / sub / nama), np.full((180, 320, 3), terang, np.uint8))
    return tmp_path / "capture"


def test_gambar_dibaca_dan_keluaran_untuk_lembar_rantai(tmp_path):
    r = bg.jalankan(siapkan(tmp_path), tmp_path / "keluar", cari, kendaraan, baca, 0.25)

    assert r == {"gambar": 2, "plat": 1, "gambar_tanpa_plat": 1, "per_kelompok": {"mobil": 1, "motor": 1}}
    tiba = [json.loads(x) for x in (tmp_path / "keluar" / "kedatangan.jsonl").read_text().splitlines()]
    assert [(t["kategori"], t["teks"], t["nomor"]) for t in tiba] == [("mobil", "B1234XY", 1)]
    assert (tmp_path / "keluar" / "potongan" / tiba[0]["potongan"]).exists()
    tanpa = json.loads((tmp_path / "keluar" / "tanpa-plat.json").read_text())
    assert [t["kelompok"] for t in tanpa] == ["motor"]


def test_nama_berkas_asli_tidak_muncul_di_keluaran_bersama(tmp_path):
    bg.jalankan(siapkan(tmp_path), tmp_path / "keluar", cari, kendaraan, baca, 0.25)

    for nama in ("kedatangan.jsonl", "ringkasan.json", "tanpa-plat.json"):
        assert "rahasia" not in (tmp_path / "keluar" / nama).read_text()
    assert "rahasia" in (tmp_path / "keluar" / "peta-berkas.json").read_text()  # peta ke berkas asli, hanya untuk lab


def test_sisi_per_isi_berkas_tetap():
    assert bg.sisi(b"isi-a") == bg.sisi(b"isi-a") and {bg.sisi(bytes([i])) for i in range(64)} == {"uji", "latih"}
```

  Merah yang diharapkan: `ModuleNotFoundError: No module named 'baca_gambar'`.
- [x] **Step 2: Tulis `tools/lab/baca_gambar.py`:**
  - **`sisi(isi)`:** huruf heksadesimal pertama SHA-256 dari `"capture/" + isi` adalah 0–3 untuk `uji`, selain itu `latih`.
  - **`jalankan(folder_capture, keluar, cari, cari_kendaraan, baca, ambang)`:** tiap subfolder `capture cctv <kelompok>` dibaca,
    dan berkas diurutkan menurut SHA-256 isinya, bukan namanya. Untuk tiap gambar:
    - kendaraan dicari;
    - plat dicari dengan `kendaraan.cari_dalam_kendaraan`;
    - tiap kotak dipotong dengan `rantai.potong` lalu dibaca.
  - **Tiap plat menjadi satu baris `kedatangan.jsonl`:**
    - `video` = `"g0001"` (nomor gambar), `nomor` = urutan plat di gambar, `kategori` = kelompok, `sudut` = `"tangkapan"`;
    - `teks` = bacaan bila sesuai pola, selain itu `""`;
    - `status` = `"ragu"`, karena satu gambar tidak bisa dipungut suaranya;
    - `potongan`, `yakin_kotak`, `yakin_baca`, `kotak`, `sisi`.
  - **Gambar tanpa plat** ditulis ke `tanpa-plat.json` (`gambar`, `kelompok`, `sisi`, `kendaraan`).
  - **`peta-berkas.json`** memetakan nomor gambar ke jalur asli (hanya untuk lab; agen tidak membukanya).
  - **`ringkasan.json`** berisi hitungan saja.
  - **CLI** `jalan folder_capture keluar folder_pencari folder_kendaraan folder_baca folder_unduhan --ambang 0.25`. Galat hanya
    mencetak jenisnya.

  Run gerbang lab → Expected `264 passed` (261 + 3). Commit.

  **Dijalankan 18 Okt:** ketiga uji merah karena modulnya belum ada, lalu hijau. Saat menulis CLI, ketahuan satu celah di kode
  pertama: gambar yang tak bisa dibuka dilewati diam-diam, padahal tetap terhitung di `gambar`. Ditambah:
  - uji keempat (`test_gambar_yang_tak_bisa_dibuka_menghentikan_jalan`), terlihat merah `DID NOT RAISE`; sekarang jalan berhenti
    dengan `ValueError` tanpa jalur;
  - uji CLI dengan model sungguhan di `uji_fpo/test_rantai_sungguhan.py`, yang memastikan nama berkas tidak muncul di layar, juga
    saat ada berkas rusak. Uji ini ditulis sesudah kodenya, dan bagian berkas rusaknya padanan uji keempat.

  Gerbang lab 261 → **265 passed**, image tambahan 30 → **31 passed**.

### Task 2: Jalankan dan dua lembar untuk owner

- [x] **Step 1:** `baca_gambar.py jalan` dengan mesin belajar Rencana 20 sebagai pengusul: pencari cctv1, kendaraan, cara potong,
  ambang 0,25, fpo-indo-1 → `data/keluaran/tangkapan-owner-baca`.

  **Hasil 18 Okt** (hitungan dari `hitung-tangkapan-24.mjs`, tanpa teks):
  - 144 plat dari 135 gambar (126 gambar satu plat, 9 gambar dua plat). 142 plat berteks sesuai pola, 2 tanpa teks.
  - 46 gambar tanpa plat: mobil 11 dari 76, motor 35 dari 105.
  - Sisi: uji 38 gambar (mobil 16, motor 22), latih 143.
- [x] **Step 2: Lembar plat** (`lembar_rantai.py lembar ... --maks 1000`), berisi semua plat yang ditemukan.
  **Lembar gambar tanpa plat** (`lembar_kendaraan.gambar_bernomor` untuk kendaraannya, satu gambar per kartu): owner menyebut
  gambar yang memuat plat terbaca tanpa kotak.

  **Dijalankan 18 Okt:** lembar plat `data/keluaran/lembar-tangkapan-plat/` (144 baris, 8 halaman). Lembar tanpa plat dibuat oleh
  subperintah baru `baca_gambar.py lembar-tanpa` (uji `test_lembar_tanpa_plat_...` terlihat merah dulu) ke
  `data/keluaran/lembar-tangkapan-tanpa-plat/` (46 kartu, 104 kendaraan bernomor, 12 halaman). Gerbang lab 265 → **266 passed**.
- [x] **Step 3: BERHENTI.** Owner memeriksa kedua lembar:
  - lembar plat: salah, tak terbaca, bukan plat, motor;
  - lembar tanpa plat: nomor gambar yang platnya terbaca.

  **Pilihan untuk owner, bukan kewajiban:** untuk baris yang salah, owner boleh mengetik teks plat yang benar ke berkas
  `data/capture/label-benar.txt` di laptop (nomor baris dan teks), bukan di percakapan. Agen memakainya di lab tanpa membukanya.

  **Dijawab owner 18 Okt** (nomor saja, di `data/alat-sementara/jawaban-24-plat.txt` dan `jawaban-24-tanpa-plat.json`):
  - lembar plat: 28 salah, 12 tak terbaca, 6 bukan plat;
  - lembar tanpa plat: 36 kartu platnya terbaca di kendaraan bernomor, 7 terbaca tetapi kendaraannya tanpa kotak, 2 kendaraan luar
    Indonesia, 1 dikeluarkan dari data;
  - `label-benar.txt` belum dibuat.

  Owner juga memberi K45 (kendaraan terdekat lebih dulu) dan mengajukan P17 (huruf mirip).

### Task 3: Label jadi dan catatan

- [ ] **Step 1:** `lembar_rantai.py nilai` untuk angka mesin belajar pada tangkapan (mobil dan motor). Label diubah menjadi bahan
  latih dengan skrip sekali pakai (**18 Okt:** nilai selesai, 98 dari 126 benar; pengubahan label menunggu kotak dan teks yang
  belum ada, lihat Task 4):
  - kotak plat yang bukan "bukan plat" → label pencari plat;
  - teks yang benar → label pembaca;
  - per sisi latih/uji.
- [ ] **Step 2:** Laporan singkat `bukti/<tanggal>-tangkapan-owner.md` (hitungan saja), ROADMAP, commit. Lalu tulis Bagian B menurut
  jumlah label yang ada. (**18 Okt:** bagian pengukuran ditulis di `bukti/2026-10-18-tangkapan-owner.md`; bagian label menyusul
  sesudah Task 4.)

### Task 4: Kotak dan teks yang belum ada (ditambahkan 18 Okt, sesudah jawaban owner)

Ada 43 plat terlewat tanpa kotak dan tanpa teks, dan 28 bacaan salah tanpa teks benar. Padahal justru plat-plat itu yang paling
berguna untuk melatih mesin jualan: di sanalah mesin belajar gagal. **Owner memilih halaman pelabelan (18 Okt).** Halaman itu
dibuka owner di laptop tanpa internet: owner menarik kotak di plat dan mengetik teksnya. Hasilnya tersimpan di laptop, dan agen
tidak membuka isinya.

**Files:** Create `tools/lab/halaman_label.py`, `tools/lab/uji/test_halaman_label.py`.

- [x] **Step 1: Uji merah** `tools/lab/uji/test_halaman_label.py` (lima uji). Bahan uji buatan berisi lima gambar bernama "rahasia":
  - g0001: dua plat di lembar plat, satu benar dan satu salah;
  - g0002: terlewat, kendaraan bernomor;
  - g0003: terlewat, kendaraan tanpa kotak;
  - g0004: luar Indonesia;
  - g0005: satu bukan plat dan satu tak terbaca.

  Yang diuji:
  - `buat` menghasilkan tiga butir halaman (t1, t2, s2) beserta salinan gambar bernama nomor. Nama asli dan alamat luar tidak
    muncul di halaman.
  - `terima` menggabungkan label tetap dari lembar dengan jawaban halaman menjadi `label.json`. Teks dirapikan menjadi huruf besar
    tanpa spasi, gambar terlewat yang belum diisi ditandai `plat_tanpa_label`, bukan plat dan tak terbaca dicatat, dan gambar luar
    Indonesia dikeluarkan.
  - Kotak di luar gambar ditolak.
  - Nomor butir asing ditolak.
  - Teks di luar pola tidak menjadi label, dan dihitung.

  Merah yang diharapkan: `ModuleNotFoundError: No module named 'halaman_label'`.
- [x] **Step 2: Tulis `tools/lab/halaman_label.py`:**
  - **`buat(folder_capture, folder_baca, lembar_plat, lembar_tanpa, jawaban_tanpa, keluar, salah, tak_terbaca, bukan_plat)`:**
    - Butir halaman:
      - "terlewat": satu per kartu terbaca (`t<kartu>`), dengan kotak kendaraan yang disebut owner atau `None`;
      - "salah": satu per baris salah (`s<baris>`), dengan kotak temuan dan bacaan mesin.
    - Gambar disalin ke `gambar/<nomor gambar><akhiran>`, dengan lebar dan tinggi dari OpenCV.
    - `butir.json` memuat butir, label `tetap` (baris benar, tak terbaca, dan bukan plat dari lembar plat, per gambar),
      kelompok dan sisi tiap gambar dari `kedatangan.jsonl` dan `lembar-tanpa-plat.json`, serta gambar yang `dikeluarkan`
      beserta alasannya.
    - `halaman.html` satu berkas tanpa sumber luar. Butir tertanam sebagai JSON (`<` di-escape). Isinya:
      - kanvas gambar dengan pilihan perbesar 1× atau 2×, kotak kendaraan biru, dan kotak plat merah yang ditarik dengan
        pointer;
      - pratinjau potongan diperbesar;
      - kolom teks dengan peringatan bila di luar pola, dan pilihan "tidak bisa dibaca";
      - kemajuan tersimpan di `localStorage` (dengan try/catch), dan tombol "Simpan berkas" yang mengunduh
        `label-tangkapan.json`.
  - **`terima(butir_json, simpanan, keluar)`:**
    - Teks dirapikan; yang di luar `plat.POLA` menjadi `None` dan dihitung.
    - Kotak harus di dalam gambar dan berukuran minimal 4 piksel. Bila tidak, `ValueError` (tanpa teks plat).
    - Hasilnya `label.json` (per gambar: kelompok, sisi, `plat` [kotak, teks, tak_terbaca, asal], `bukan_plat`, `plat_tanpa_label`;
      ditambah `dikeluarkan`) dan `ringkasan-label.json`, yang berisi hitungan per sisi saja.
  - **CLI:** `buat ... --salah --tak-terbaca --bukan-plat` dan `terima butir_json simpanan keluar`. Galat hanya mencetak jenisnya.

  Run gerbang lab → Expected `271 passed` (266 + 5). **18 Okt:** merah `ModuleNotFoundError`, lalu **271 passed**.
- [x] **Step 3: Bukti halaman bekerja, tanpa data plat.** Halaman dibuat dari gambar buatan bergaris acak (tanpa plat) lalu dibuka
  dengan Playwright: tarik kotak, ketik teks, muat ulang (kemajuan tetap ada), lalu simpan; berkas yang diunduh diteruskan ke
  `terima`. Halaman dengan data sungguhan tidak pernah dibuka agen.

  **Dijalankan 18 Okt** (`data/alat-sementara/buat-uji-halaman-24.py`):
  - Playwright menolak alamat `file:`, jadi halaman buatan dilayani `layan-uji-halaman-24.mjs` di 127.0.0.1. **Batas:** owner
    membukanya lewat `file:`, dan cara itu tidak diuji agen.
  - Dengan mouse sungguhan dari Playwright, kotak yang ditarik tercatat persis dalam piksel asli pada perbesaran 1×, 2× (digulir),
    dan "Pas". Teks dirapikan saat diketik, teks di luar pola memunculkan peringatan, kemajuan bertahan sesudah dimuat ulang, dan
    "Simpan berkas" mengunduh `label-tangkapan.json`.
  - Berkas itu diterima `terima` dan menghasilkan `label.json` yang benar.
  - Dari potretan, dua perbaikan ditambahkan: mode "Pas" sebagai bawaan (gambar 1× lebih lebar dari panel) dan panel gambar tidak
    lagi memanjang kosong.
- [ ] **Step 4:** Halaman sungguhan dibuat ke `data/keluaran/label-tangkapan/` (lab). Commit. **18 Okt:** 71 butir (43 terlewat,
  28 salah), 3 gambar dikeluarkan. `periksa-halaman-24.mjs` dengan kontrol positif (181 dari 181 nama ketemu di peta) menemukan
  0 nama asli di halaman, `butir.json`, dan nama salinan gambar, serta 0 alamat luar. **Owner mengisi 71 butir (18 Okt)**; berkasnya
  disalin dari Downloads ke `data/capture/label-tangkapan.json` (SHA-256 sama, tidak dibuka). `terima`: 71 terisi, 0 di luar pola,
  180 kotak plat, 159 teks benar, 21 tak terbaca, 1 plat tanpa kotak (butir 42; owner diminta melengkapinya).
  **BERHENTI:** owner mengisi halaman dan
  memberi tahu letak berkas yang diunduh. Agen menyalinnya ke `data/capture/label-tangkapan.json` tanpa membukanya, lalu menjalankan
  `terima`.

---

## Bagian B: Pembaca dan pencari plat jualan dari nol (ditulis 18 Okt, sesudah label Bagian A diterima)

> **Ditutup sebagian 19 Okt (K47–K50).** Owner menerima bobot fast-plate-ocr (K47) dan bobot YOLOX COCO yang dimodifikasi (K48) untuk
> produk jual, menyatakan izin verbal untuk video riset (K49), lalu meminta fokus mengoptimalkan yang sudah ada (K50).
>
> Hasil yang sudah ada disimpan sebagai cadangan:
> - pembaca dari nol P2 293 dan P3 319 dari 489 gambar validasi (fpo-indo-1 407, mesin-baca-1 148);
> - pencari dari nol D1, F1 validasi 0,845 (cctv1 0,92).
>
> P1 dan D2 tidak dilatih. Pemilihan calon dan pengukuran di set uji (Task 7 Step 3, Task 8 Step 2, Task 10 Step 2–3, Task 11
> Step 2) pindah ke Rencana 25, yang membandingkan mesin yang dioptimalkan dengan cadangan ini.

**Goal (Bagian B):** pembaca dan pencari plat yang lolos `tools/periksa-jualan.mjs` sebagai mesin `jualan`. Semua bahannya
`BOLEH-PRODUK` dan tanpa bobot awal. Keduanya diukur di set yang sama dengan mesin belajar, supaya jaraknya diketahui; kalau kalah,
itu dilaporkan apa adanya.

**Architecture (Bagian B):**
- **Pembaca:** arsitektur `cct_s_v2` dari kode fast-plate-ocr @ 9ce7a5b (MIT, `vendor/fast-plate-ocr/models/cct_s_v2.yaml`) dengan
  konfigurasi plat buatan sendiri (`tools/lab/fpo-jualan-plat.yaml`: 10 slot, `0-9A-Z` dan `_`, 64×128 RGB, tanpa kepala wilayah).
  Tidak memakai berkas rilis apa pun. Pelatih CLI di `vendor` hanya memuat bobot awal bila `--weights-path` diberikan
  (`fast_plate_ocr/cli/train.py:480`); `latih_fpo.py` mendapat jalan "dari nol".
  - Bentuk ini dipilih, bukan CRNN mesin-baca-1, karena keluarannya per slot (N, 10, 37). Keyakinan dan kemungkinan kedua per posisi
    yang diminta K46 langsung terbaca dari situ.
- **Pencari plat:** YOLOX-Nano-640 dari kode YOLOX (Apache-2.0, sudah di `latih_yolox.py`) tanpa `muat_bobot_awal`.
- **Bahan:**
  - INDO-ALPR, sisi latih `pembagian-koreksi.json` (potongan plat berteks): 2.521 plat dan 3.954 gambar untuk latih inti, 303 plat
    dan 460 gambar untuk validasi;
  - plat-lighting (foto utuh berkotak): latih 393, valid 84;
  - plat buatan (`plat_buatan.py`);
  - tangkapan owner, sisi latih saja (`label.json`): 141 kotak dan 125 teks.

  Video riset (`RISET-SAJA`) tidak masuk sama sekali.

**Tech Stack:** image tambahan (`-Fpo`), GPU RTX 4060 untuk melatih (satu job GPU pada satu waktu, di latar dengan log), CPU untuk
mengukur.

### Yang diukur sebelum bagian ini ditulis

| Hal | Angka | Dari mana |
|---|---|---|
| Pembaca dari nol yang pernah ada (mesin-baca-1, CRNN, INDO-ALPR saja) | 146 dari 460 gambar validasi (31,7%); menghafal | `bukti/2026-10-14-mesin-baca-pertama.md` |
| fpo-indo-1 (dengan bobot awal terbitan) | 388 dari 460 gambar validasi; 79–86% kedatangan per kelompok di set uji INDO-ALPR; di tangkapan 98 dari 126 plat yang ditemukan | `bukti/2026-10-15-fpo-indo-1.json`, ROADMAP, `bukti/2026-10-18-tangkapan-owner.md` |
| Waktu latih fpo-indo-1 | 76–81 detik per zaman untuk 3.954 gambar | `bukti/2026-10-15-fpo-latih-ulang.md` |
| Pencari Nano-640 (bobot awal COCO, plat-lighting) | 96 dari 102 plat uji plat-lighting | `bukti/2026-10-16-pencari-plat-yolox.md` |
| Pencari cctv1 (COCO + video riset) | F1 validasi 0,9236; 68 menit untuk 100 zaman, 864 gambar | `bukti/2026-10-16-pencari-plat-cctv.md` |
| Plat buatan dibaca fpo-indo-1 tanpa latihan | 96 dari 200 bersih, 91 dari 200 bervariasi | `bukti/2026-10-16-plat-buatan.md` |

### Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Pembaca:** tiga calon, semuanya dari nol:
  - P1 "nyata": INDO-ALPR latih inti ditambah tangkapan latih inti;
  - P2 "campur": P1 ditambah plat buatan di set latih yang sama;
  - P3 "pralatih": tahap 1 hanya plat buatan, tahap 2 melanjutkan bobot tahap 1 dengan bahan P1. Bobot tahap 1 adalah mesin kita
    sendiri, jadi bahannya ikut tercatat.

  Yang dipilih adalah calon dengan gambar benar terbanyak di `validasi.csv` gabungan (INDO-ALPR validasi 460 gambar ditambah tangkapan
  validasi, yaitu 1 dari 5 potongan tangkapan latih menurut SHA-256). Bila seri, dipilih yang lebih sederhana, dengan urutan P1, P2,
  P3. Set uji INDO-ALPR (911 plat adil) dan potongan tangkapan uji diukur **sekali**, untuk calon terpilih dan fpo-indo-1 sebagai
  pembanding.
- **Anggaran waktu per calon pembaca: sekitar 4 jam GPU.** Jumlah plat buatan dan zaman dihitung dari waktu per 1.000 gambar yang
  diukur di Task 7 Step 1. Zaman = min(150, anggaran × laju ÷ gambar per zaman).
- **Pencari plat:** dua calon, YOLOX-Nano-640 dari nol, 200 zaman:
  - D1: plat-lighting latih ditambah tangkapan latih inti (gambar ber-`plat_tanpa_label` dikeluarkan);
  - D2: D1 ditambah gambar tempel plat buatan di latar yang sama.

  Yang dipilih adalah calon dengan F1 terbaik pada ambangnya sendiri (`deteksi.pilih_ambang`) di validasi gabungan (plat-lighting
  valid ditambah tangkapan validasi, yaitu 1 dari 5 gambar tangkapan latih menurut SHA-256). Bila seri, D1. Plat-lighting uji
  (102 plat) dan tangkapan uji (39 plat) diukur **sekali**, untuk calon terpilih serta Nano-640 dan cctv1 sebagai pembanding.
- **Rantai jualan** (pencari jualan ditambah pembaca jualan, tanpa tahap kendaraan) dinilai otomatis di 38 gambar tangkapan uji
  terhadap `label.json`:
  - plat berlabel "ditemukan" bila ada kotak dengan IoU ≥ 0,3;
  - "dibaca benar" bila ditemukan dan bacaannya sama dengan teks label.

  Rantai belajar (kendaraan, cctv1 dengan cara potong, ambang 0,25, fpo-indo-1) dinilai dengan cara yang sama.

### Task 5: Bahan pembaca jualan

**Files:** Create `tools/lab/bahan_pembaca.py`, `tools/lab/uji/test_bahan_pembaca.py`.

- [x] **Step 1: Uji merah.** Bahan uji buatan:
  - pembagian INDO-ALPR (2 plat latih dan 1 plat uji, bergambar);
  - `label.json` dan `peta-berkas.json` dengan gambar tangkapan latih dan uji (nama berkas berisi "rahasia");
  - folder plat buatan (`label.csv` dan `gambar/`).

  Yang diuji:
  - `siapkan(pembagian, folder_indo, folder_capture, folder_label_tangkapan, keluar, folder_plat_buatan=None)` menulis `latih.csv`
    dan `validasi.csv` (`image_path,plate_text`);
  - potongan tangkapan diambil hanya dari sisi latih: tidak ada satu pun dari gambar uji, dan tidak ada plat berteks `None` atau
    tak terbaca;
  - validasi memuat INDO-ALPR validasi dan tangkapan validasi; plat buatan hanya masuk latih;
  - `siapkan.json` memuat hitungan per sumber dan daftar `bahan`: `dataset-indo-alpr` dan `tangkapan-owner`, ditambah `plat-buatan`
    bila ada;
  - nama berkas asli tidak muncul di CSV maupun nama potongan.

  Merah yang diharapkan: `ModuleNotFoundError`.
- [x] **Step 2:** Tulis `bahan_pembaca.py`:
  - INDO-ALPR lewat `mesin_baca.bagi_validasi`;
  - tangkapan: potongan `rantai.potong(gambar, kotak)` disimpan ke `potongan/t-<gambar>-<n>.png`; validasi bila heksadesimal pertama
    SHA-256 `"validasi/<gambar>-<n>"` habis dibagi 5;
  - plat buatan: semua baris `label.csv` masuk latih.

  CLI `siapkan`. Gerbang lab hijau (271 + uji baru). **18 Okt:** tiga uji merah `ModuleNotFoundError`, lalu hijau.

### Task 6: `latih_fpo.py` dari nol

**Files:** Modify `tools/lab/latih_fpo.py`, `tools/lab/uji/test_latih_fpo_manifes.py` (baru),
`tools/lab/uji_fpo/test_latih_fpo_dari_nol.py` (baru); Create `tools/lab/fpo-jualan-plat.yaml`.

- [x] **Step 1: Uji merah (lab):** `manifes_jualan(hitung, sha_mesin, latihan, validasi, nama)` menghasilkan `tujuan` `"jualan"`, `bahan`
  sama dengan `hitung["bahan"]` (tanpa `bobot-fast-plate-ocr`), dan `sha256_bobot_awal` `None`. Manifes itu lolos
  `node tools/periksa-jualan.mjs`, yang dipanggil uji Node. Sebagai kontrol, manifes yang memuat `bobot-fast-plate-ocr` ditolak
  dengan exit 1.
- [x] **Step 2: Uji merah (`uji_fpo`, GPU, dengan tangan):** `latih_dari_nol(folder, zaman=1)` pada 64 plat buatan berjalan tanpa membaca
  berkas rilis apa pun (folder unduhan tidak diberikan), menghasilkan `mesin.keras` dan `mesin.json` bertujuan `jualan`, dan pembacanya
  memuat dengan `fpo-jualan-plat.yaml`. Untuk P3 juga ada `bobot_awal=<folder mesin sendiri>`: SHA-256-nya diperiksa terhadap
  `mesin.json` mesin itu, dan bahannya ikut digabung. Mesin sendiri yang bertujuan `belajar` ditolak.
- [x] **Step 3:** Tulis `fpo-jualan-plat.yaml`, `manifes_jualan`, `latih_dari_nol(folder, zaman, benih, ukuran_angkatan, bobot_awal=None,
  nama=...)`, dan `PembacaMesinJualan` (SHA-256 terhadap `mesin.json`). Lalu CLI `latih-jualan`. Kedua gerbang hijau, ditambah uji
  `uji_fpo` baru.

  **18 Okt:**
  - Uji lab merah (`AttributeError`, 4 uji), lalu uji GPU merah (`latih_dari_nol` belum ada). Sesudah kode ditulis, uji GPU
    menangkap cacat sungguhan: tanpa kepala wilayah, fast-plate-ocr menamai metriknya `val_acc`, bukan `val_plate_acc`
    (`cli/train.py:91-98`). Diperbaiki, lalu hijau.
  - Tahap kedua memeriksa bahwa bobot sendiri termuat utuh (`bobot_utuh(..., kepala_wilayah=False)`).
  - Bagian sesudah pelatihan dipakai bersama dengan `latih` lama (`_jalankan_latih`).
  - Uji Node penjaga: manifes dengan tiga bahan jualan lolos `periksa-jualan` di daftar bahan repo.
  - Gerbang: Node 117 → 118, lab 271 → 278, image tambahan 31 → 32.

### Task 7: Melatih tiga calon pembaca

- [x] **Step 1: Ukur laju.** Buat 4.000 plat buatan (`plat_buatan.py buat`), lalu jalankan `latih-jualan` 2 zaman pada bahan P2 kecil.
  Catat detik per 1.000 gambar per zaman dan waktu membuat 1.000 plat buatan. Dari situ tetapkan jumlah plat buatan dan zaman
  menurut anggaran, dan tulis angkanya di sini sebelum calon dilatih.

  **Diukur 18 Okt** (`data/alat-sementara/ukur-laju-24.ps1`; GPU kosong sebelum tiap jalan, 1–2%; 8.050 gambar per zaman, terdiri
  dari INDO-ALPR 3.954, tangkapan 96, dan plat buatan 4.000):
  - Membuat 4.000 plat buatan butuh 33 detik termasuk menyalakan lab, sekitar 8 ms per plat.
  - Satu zaman butuh 161,5 detik dan tiga zaman 407,3 detik, jadi **122,9 detik per zaman, atau 15,3 detik per 1.000 gambar per
    zaman**. Biaya tetap per jalan sekitar 39 detik.
  - Validasi plat utuh masih 0 dari 489 sesudah 3 zaman. Model tetap belajar: rugi 2,79 → 2,33 → 2,27, dan ketepatan per huruf di
    validasi 0,24 → 0,34 → 0,35.

  **Ditetapkan dari angka itu** (anggaran 14.400 detik per calon; zaman = min(150, anggaran ÷ detik per zaman)):
  - **P1:** 4.050 gambar per zaman (61,8 detik), 150 zaman, sekitar 2,6 jam.
  - **P2:** 10.000 plat buatan (benih 24), 14.050 gambar per zaman (214,5 detik), 67 zaman.
  - **P3:**
    - tahap 1: 30.000 plat buatan (benih 24) selama 15 zaman, sekitar 2 jam;
    - tahap 2: bahan P1 selama 116 zaman, sekitar 2 jam.

    Agar tahap 1 hanya berlatih dengan plat buatan, `bahan_pembaca` mendapat pilihan `--latih-hanya-buatan`. Validasinya tetap
    bahan nyata, dan bahan nyata tetap tercatat, karena ikut menentukan zaman terbaik.
- [ ] **Step 2:** P1, P2, P3 dilatih berurutan di latar, masing-masing dengan log ke berkas. Cek `nvidia-smi` dan `docker ps` sebelum tiap
  jalan; satu job GPU pada satu waktu.

  **Jalan pertama P1 dihentikan (18 Okt, zaman 47 dari 150, `docker stop`, tanpa sisa proses).** Penyebabnya cacat di Task 6:
  - checkpoint dan henti dini memantau ketepatan plat utuh di validasi (`val_acc`, bawaan pembuatnya);
  - dari nol, angka itu 0 di semua zaman sampai 47, padahal ketepatan per huruf naik dari 0,24 ke 0,48;
  - akibatnya `best.keras` tertahan di zaman 1, dan henti dini akan berhenti di zaman 101.

  Perbaikannya: mesin dari nol memilih zaman dengan `val_char_acc` (`--early-stopping-metric val_plate_char_acc`), dan
  `metrik_pilih` dicatat di `mesin.json`. Ujinya dilihat merah (`KeyError: 'metrik_pilih'`), lalu hijau. Pemilihan ini hanya
  memakai validasi, dan belum ada calon yang dinilai, jadi aturan memilih calon tidak berubah. Log jalan pertama disimpan di
  `pembaca-jualan-p1/latihan-jalan1-dihentikan/`.

  Kunci bengkel (`lab.ps1`, mutex bersama) membuat uji lab tidak bisa jalan selama pelatihan. Karena itu sebagian kode Task 8–11
  ditulis sebelum ujinya terlihat merah. Merahnya dibuktikan sesudahnya: perubahan kode disimpan sementara dengan `git stash`
  (dan `dataset_jualan.py` disingkirkan), lalu suite dijalankan. Hasilnya, hanya uji baru yang gagal (7 gagal dan 1 galat kumpul;
  278 uji lama lulus), dan uji GPU `rincian` dan metrik pilih gagal dengan `AttributeError` dan `KeyError`. Sesudah kode
  dikembalikan: lab 278 → **289**, image tambahan 32 → **34**, Node 118.

  **Antrean GPU (18 Okt, 17:39):**
  - `data/alat-sementara/antrean-24.ps1` menjalankan D1, D2, P2, P3 tahap 1, P3 tahap 2, lalu P1, satu job pada satu waktu dengan
    log per job.
  - D1 dan D2 gagal dalam 0,2 detik. Pengisi folder unduhan `-` ditolak `powershell -File` sebelum `lab.ps1` berjalan ("Cannot
    process argument"; dicoba ulang dengan `-Kering`). Pengisinya diganti jalur yang tidak ada, karena `--dari-nol` tidak membaca
    folder itu.
  - D1 dan D2 dijalankan `antrean-24b.ps1` sesudah antrean pertama selesai. Contoh di keterangan `baca_gambar.py` yang memakai `-`
    juga dibetulkan.

  Bahan yang disiapkan:
  - P2: 14.050 gambar latih;
  - P3 tahap 1: 30.000 plat buatan saja;
  - P3 tahap 2 dan P1: 4.050 gambar latih;
  - semuanya dengan validasi yang sama, 489 gambar (INDO-ALPR 460, tangkapan 29);
  - D1: 501 gambar latih (603 kotak) dan 115 gambar validasi (130 kotak); D2 sama, ditambah 501 gambar tempel. Satu gambar dikeluarkan
    karena plat tanpa label (butir 42).
- [ ] **Step 3:** Hitung benar per calon di `validasi.csv` gabungan, juga fpo-indo-1 dan mesin-baca-1 sebagai acuan. Pilih menurut
  aturan, lalu catat `bukti/<tanggal>-pembaca-jualan.json`.

### Task 8: Ukur pembaca terpilih, dan rincian per posisi (K46)

- [x] **Step 1: Uji merah (`uji_fpo`):** `PembacaKeras.rincian(gambar)` mengembalikan, per slot yang bukan bantalan, `(huruf, peluang,
  huruf_kedua, peluang_kedua)`. Huruf pertamanya membentuk teks yang sama dengan `__call__`, dan peluangnya menurun.
- [ ] **Step 2:** Ukur sekali di set uji INDO-ALPR (`baca_vlm.nilai`, 911 plat adil, per kelompok) dan potongan tangkapan uji (34
  teks), untuk pembaca terpilih dan fpo-indo-1. Hasilnya `bukti/<tanggal>-pembaca-jualan.md`, hitungan saja.

### Task 9: Bahan pencari jualan

**Files:** Create `tools/lab/dataset_jualan.py`, `tools/lab/uji/test_dataset_jualan.py`.

- [x] **Step 1: Uji merah:** `bangun(folder_plat_lighting, folder_capture, folder_label_tangkapan, keluar, tempel_per_gambar=0)` menulis
  format YOLO `train/` dan `valid/`. Yang diuji:
  - tangkapan uji tidak pernah masuk;
  - gambar tangkapan ber-`plat_tanpa_label` dikeluarkan;
  - semua kotak plat `label.json`, termasuk yang tak terbaca, menjadi label, dan kotak bukan plat tidak;
  - tempel (D2) memakai `dataset_cctv.tempel` di gambar latih saja;
  - nama berkas memakai nomor gambar;
  - `ringkasan.json` memuat hitungan dan `bahan`.
- [x] **Step 2:** Tulis `dataset_jualan.py`. Gerbang lab hijau.

### Task 10: `latih_yolox.py` dari nol, dan dua calon pencari

- [x] **Step 1: Uji merah (lab):** `latih(..., dari_nol=True)` tidak membaca berkas bobot COCO (folder unduhan boleh tidak ada), dan
  manifesnya bertujuan `jualan` dengan `bahan` dari `ringkasan.json` dataset (tanpa `bobot-yolox`). Kontrol: tanpa `dari_nol`,
  `bobot-yolox` tetap tercatat.
- [ ] **Step 2:** D1 dan D2 dilatih berurutan di latar, 200 zaman. Pilih menurut aturan.
- [ ] **Step 3:** Ukur sekali di plat-lighting uji dan tangkapan uji (dataset uji tangkapan dibuat `dataset_jualan.py` dengan sisi
  `test`), untuk calon terpilih, Nano-640, dan cctv1. Hasilnya `bukti/<tanggal>-pencari-jualan.md`.

### Task 11: Rantai jualan di tangkapan uji

**Files:** Modify `tools/lab/baca_gambar.py` (`--tanpa-kendaraan`, `--pembaca-jualan`), `tools/lab/halaman_label.py` (`nilai_label`),
uji masing-masing.

- [x] **Step 1: Uji merah:**
  - `nilai_label(label_json, kedatangan_jsonl, peta_gambar, sisi="uji", iou=0.3)` menghitung ditemukan, dibaca benar, dan kotak di
    luar label per kelompok. Uji memakai `label.json` dan `kedatangan.jsonl` buatan, termasuk satu plat yang ditemukan tetapi
    terbaca salah, dan satu kotak di luar label.
  - `baca_gambar.jalankan` tanpa kendaraan mencari plat di gambar utuh.
- [ ] **Step 2:** Jalankan kedua rantai di tangkapan uji, nilai otomatis, lalu tulis laporan `bukti/<tanggal>-rantai-jualan.md`,
  ROADMAP, dan changelog. Bagian C berikutnya: ekspor ONNX tanpa berkas terbitan, pencari kendaraan dari kotak yang diperiksa owner,
  dan rekaman HP owner (K43).

**Batas yang sudah diketahui sebelum mulai:**
- Potongan INDO-ALPR bersih, bukan CCTV.
- Validasi dan uji tangkapan kecil (sekitar 25 dan 34 teks).
- Di gambar tangkapan berkotak, plat lain yang terlewat tidak diperiksa owner, jadi "kotak di luar label" bisa berisi plat
  sungguhan.
- Rantai jualan belum punya tahap kendaraan (K45 dan "cara potong" baru bisa dipakai sesudah ada pencari kendaraan jualan).
