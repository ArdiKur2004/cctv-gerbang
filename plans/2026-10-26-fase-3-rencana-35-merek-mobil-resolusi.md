# Fase 3, Rencana 35: Merek mobil — menguji dugaan resolusi — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37); owner menyetujui langkah ini 26 Okt ("ya jalankan"). Owner dihentikan di akhir.

**Goal:** menguji satu dugaan, bukan membangun fitur besar. Di Rencana 34 pengenal merek menjawab "tak yakin" untuk **semua 13** potongan
mobil uji. Dugaan agen yang pertama ("logo mobil terlalu kecil di CCTV") sudah **terbukti salah**: potongan mobil owner lebarnya
159/514/1.185 piksel. Dugaan kedua, yang diuji di sini: **masukan pengenal hanya 96 × 96 piksel**, jadi mobil selebar 514 piksel
diperkecil sekitar lima kali dan logonya hilang; motor selamat karena jati dirinya ada pada bentuk dan corak bodi.

**Bila dugaan ini benar,** pencari logo tersendiri (dataset all-cars-logo) tidak perlu dibangun. **Bila salah,** kita tahu masalahnya
memang di logo, dan pilihan itu menjadi berdasar, bukan tebakan.

## Bahan (sudah ada, dari Rencana 34)

Potongan berjenis **mobil** yang berlabel merek di `data/keluaran/potongan-ciri-2/`:

| Sisi | Jumlah | Dari owner | Dari Roboflow brand |
|---|---|---|---|
| latih | 3.309 | 35 | 3.274 |
| validasi | 427 | **17** | 410 |
| uji | **13** | 13 | — |

Owner, sisi uji: Daihatsu 4, Toyota 4, Honda 3, Suzuki 1, lainnya 1.

## Architecture

`tools/lab/ciri.py` mendapat dua pilihan, tanpa mengubah perilaku bawaan:
- **`ukuran`**: ukuran masukan mesin, bawaan `UKURAN` (96). Dicatat di `mesin.json` dan `mesin-onnx.json`, dan dibaca kembali oleh
  `ekspor` dan `PengenalCiri`, jadi tidak ada ukuran yang tersembunyi atau berbeda antara latih dan pakai. Mesin lama (ukuran 96 di
  `mesin-onnx.json`) tetap terbaca seperti sebelumnya.
- **`jenis`**: hanya potongan berjenis itu yang dipakai melatih dan memvalidasi (di sini `mobil`).

## Calon

| Calon | Masukan | Bahan |
|---|---|---|
| **B0** (tanpa latihan) | — | selalu menjawab merek mobil terbanyak di owner sisi latih |
| **C96** (kendali) | 96 | mobil saja |
| **C192** | 192 | mobil saja |
| **C256** | 256 | mobil saja |

C96 adalah **kendali**: ia memisahkan pengaruh "mobil saja" dari pengaruh "masukan lebih besar". Tanpa C96, naiknya angka tidak bisa
dibaca sebagai bukti untuk dugaan resolusi.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- Dinilai di **validasi owner mobil** (17 potongan), ambang {0; 0,5; 0,7; 0,9}, **nilai = benar − salah**.
- Nilai tertinggi menang; seri → salah paling sedikit; seri → B0, lalu masukan terkecil (96, 192, 256); seri → ambang terkecil.
- **Penjaga:** calon terpilih dipakai hanya bila nilainya lebih besar dari B0.
- **Vonis dugaan resolusi** (ditetapkan sekarang, supaya tidak dikarang sesudah melihat angka): dugaan disebut **didukung** hanya bila
  nilai C192 atau C256 **lebih besar** dari nilai C96 di validasi owner mobil, pada ambang terbaik masing-masing. Bila tidak, dugaan
  **tidak didukung**, dan laporannya menyebut begitu.
- Pilihan di-commit sebelum uji dibuka, lalu diukur sekali di 13 potongan mobil uji.

## Task 1: `ukuran` dan `jenis` di `ciri.py`

**Files:** Modify `tools/lab/ciri.py`; uji `tools/lab/uji/test_ciri.py`, `tools/lab/uji_fpo/test_ciri_sungguhan.py`.

- [ ] **Step 1: Uji merah:** `latih(ukuran=...)` mencatat ukuran di `mesin.json`; `latih(jenis=...)` hanya memakai baris berjenis itu
  (latih **dan** validasi); mesin lama tetap terbaca. **Uji rantai (bukan cuma cabang):** satu uji menelusuri jalannya dari latih →
  ekspor → `PengenalCiri` dengan ukuran bukan bawaan, dan membuktikan bentuk masukan ONNX serta hasilnya memakai ukuran itu.
- [ ] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, Node hijau.

## Task 2: Melatih tiga calon

- [x] **Step 1:** Latih C96, C192, C256 di latar dengan penjaga GPU; ekspor ONNX masing-masing. (1,7 · 4,6 · 8,1 menit; ONNX sama dengan
  torch 40 dari 40 untuk ketiganya. **Tanda awal:** C192 dan C256 memilih zaman 1 dari 30.)

## Task 3: Memilih, mengukur, lalu BERHENTI

- [x] **Step 1:** Nilai B0, C96, C192, C256 × ambang di validasi owner mobil; pilih menurut aturan; tulis vonis dugaan resolusi; commit
  sebelum uji dibuka. (Nilai terbaik: C96 **1**, C192 0, C256 0, B0 −5. **Vonis: dugaan TIDAK didukung.** Terpilih C96 ambang 0,7.)
- [x] **Step 2:** Ukur sekali di 13 potongan mobil uji; hitung juga benar di luar merek terbanyak; `periksa-jualan` bila ada yang dipakai.
  (C96 benar **0**, salah 1, tak yakin 12. B0, C192, C256 masing-masing benar 4 salah 9; M1 lama benar 1 salah 12. Tidak ada yang dipakai,
  jadi `periksa-jualan` tidak dijalankan untuk memutuskan apa pun.)
- [x] **Step 3:** Laporan `bukti/2026-10-26-merek-mobil-resolusi.md` dan `.json`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh,
  commit. **BERHENTI untuk owner** dengan usulan langkah berikutnya menurut vonisnya.

**Batas, ditulis sekarang supaya tidak dilupakan saat melapor:**
- **Validasi owner mobil hanya 17 potongan, dan uji hanya 13.** Dari 16 pasangan calon × ambang yang dinilai pada 17 potongan, calon
  terbaik hampir pasti terlihat lebih baik daripada kenyataannya. Angka uji yang jujur, dan 13 potongan tidak bisa membuktikan banyak:
  rencana ini **menguji arah**, bukan menetapkan mutu.
- Bahan mobil hampir seluruhnya dari dataset brand (3.274 dari 3.309 potongan latih), yang bingkainya 1920×1080, bukan tangkapan CCTV.
- Merek mobil owner sangat sedikit: di sisi latih Toyota 14, Daihatsu 6, Suzuki 4, Honda 3, Mitsubishi 3, sisanya 1.
- Masukan lebih besar berarti latihan dan pemakaian lebih lambat; kecepatannya tidak diukur di rencana ini.
