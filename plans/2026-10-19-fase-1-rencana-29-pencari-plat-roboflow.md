# Fase 1, Rencana 29: Pencari plat dilatih lanjut dengan dataset plat Roboflow (K56) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K56). Owner dihentikan hanya di akhir.

**Goal:** pencari plat C1 (Rencana 25) dilatih lanjut dengan kotak plat dari "vehicle and license plate" v3 (Roboflow, MIT, `BOLEH-PRODUK`
sejak K56), lalu dibandingkan dengan C1 di soal yang sama.

**Bahan tambahan (dari `bukti/2026-10-19-dataset-roboflow.md`):** 5.555 gambar 640×640 (latih 5.102, validasi 432, uji 21), kelas
License_Plate, cars, motorcyle, truck. Plat ditulis sebagai kotak dan 1.780 poligon. Gambar diregangkan ke 640×640, jadi plat bisa
terdistorsi.

**Architecture:**
- `dataset_jualan.tambah_ke_latih(folder_dataset, folder_tambah, kelas, bahan, awalan="r-")` (baru): gambar dari SEMUA sisi dataset tambahan
  masuk ke `train` saja, berawalan `r-`. Hanya baris berkelas di `kelas` yang dipakai, ditulis sebagai kelas 0; poligon diubah menjadi kotak
  pembungkusnya. Gambar tanpa kotak terpakai dilewati (bisa menyembunyikan plat tak berlabel, pelajaran Rencana 19 dan 25). `valid` tidak
  disentuh, supaya soal memilih sama dengan Rencana 25. `ringkasan.json` mencatat hitungan dan bahan tambahan.
- Dataset `dataset/cctv3`: dibangun persis seperti `cctv2-c1` (Rencana 25), lalu `tambah_ke_latih` dengan kelas License_Plate dan bahan
  `dataset-roboflow-vehicle-license-plate`.
- Calon **C3:** dari C1 (`--bobot-awal-mesin pencari-cctv2-c1`), 30 zaman, tujuan jualan.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Pencari:** C3 dipilih bila F1 pada ambangnya sendiri di validasi gabungan yang sama dengan Rencana 25 (`cctv2-c1/valid`, 203 gambar,
  179 plat), dinilai dengan alat yang sama (`pilih-pencari-25.py`: ONNX, `deteksi`), **lebih tinggi** dari C1 (0,9257). Bila sama atau lebih
  rendah, C1 tetap.
- **Diukur sekali** di tangkapan uji dan plat-lighting uji (`ukur-pencari-25.py`), C1 dan calon terpilih.
- **Bila C3 terpilih:** ambang C3 di rantai dipilih di sisi latih tangkapan dari {0,25; 0,4; 0,6} dengan aturan Rencana 25 (dibaca benar
  terbanyak; seri: kotak di luar label paling sedikit; seri: 0,6), lalu rantai diukur sekali di tangkapan uji dan dibandingkan dengan
  Rencana 25 (21 dari 34).

## Task 1: `tambah_ke_latih`

**Files:** Modify `tools/lab/dataset_jualan.py`; uji `test_dataset_jualan.py`.

- [x] **Step 1: Uji merah:** semua sisi tambahan masuk `train` berawalan `r-`; kelas disaring dan ditulis 0; poligon menjadi kotak
  pembungkus; gambar tanpa kotak terpakai dilewati; `valid` tidak berubah; bahan dan hitungan tercatat; tanpa bahan ditolak; CLI
  `tambah-latih` sampai berkas keluaran.
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (Lab 344 → 346, image tambahan 35, Node 120.)

## Task 2: Dataset dan pelatihan

- [x] **Step 1:** Bangun `dataset/cctv3`; pastikan `valid`-nya sama persis dengan `cctv2-c1/valid` (sidik nama, isi, dan label).
  (5.555 gambar Roboflow masuk latih: 5.847 kotak, 1.780 dari poligon, 0 dilewati; latih total 6.527 gambar.)
- [x] **Step 2:** Latih C3 (30 zaman) di latar dengan penjaga memori GPU; ekspor ONNX. (85,7 menit; zaman terbaik 24; ONNX sama dengan
  safetensors di 20 dari 20 gambar.)

## Task 3: Memilih dan mengukur

- [x] **Step 1:** F1 C1 dan C3 di validasi yang sama; pilih menurut aturan; di-commit sebelum uji dibuka. **C3 terpilih:** F1 0,9431
  (ambang 0,55; 174 dari 179 plat, 16 kotak palsu) lawan C1 0,9257 (ambang 0,6; 162 dari 179, 9 kotak palsu). F1 C1 dihitung ulang dan
  sama dengan Rencana 25, jadi alatnya sama. `bukti/2026-10-19-pencari-plat-roboflow-pilih.json`.
- [x] **Step 2:** Ukur sekali di tangkapan uji dan plat-lighting uji. (Tangkapan: C1 35, C3 37 dari 39. Plat-lighting: C1 94, C3 95 dari 102.
  Angka C1 sama dengan Rencana 25.)
- [x] **Step 3:** Bila C3 terpilih: ambang di sisi latih, lalu rantai di tangkapan uji sekali, dan perpindahan per plat. (Ambang 0,6: dibaca
  benar 84 di ketiga ambang, kotak di luar label paling sedikit. Uji: 18 dari 34, lawan 21 dengan C1. **Ditambah saat dijalankan:** ukuran
  kotak terhadap label, untuk menjelaskan turunnya; dan keputusan rantai bawaan, yang tidak diatur rencana ini: tetap C1, alasannya di
  laporan.)

## Task 4: Laporan, lalu BERHENTI

- [x] **Step 1:** `bukti/2026-10-19-pencari-plat-roboflow.md`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh, lalu commit.
- [ ] **Step 2: BERHENTI untuk owner.**

**Batas:** lembar contoh dataset belum diperiksa owner saat pelatihan dimulai (bila owner menemukan banyak label salah, C3 ditinjau ulang);
gambar Roboflow diregangkan dan banyak yang mirip satu sama lain; tangkapan uji kecil; bukan rekaman gerbang.
