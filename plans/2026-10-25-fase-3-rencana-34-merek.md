# Fase 3, Rencana 34: Pengenal merek kendaraan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K62). Owner dihentikan hanya di akhir.

**Goal:** merek kendaraan dikenali dari potongan kendaraan, melengkapi jenis dan warna (Rencana 33). Ini ciri terakhir di tahap 1
(K8, spec Fase 3 bagian 4.1). Ukurannya sama: **nilai = benar − salah**, karena ciri salah berarti peringatan palsu. Sejak K63 ciri hanya
dicatat, belum memicu peringatan; angka ini yang akan dipakai owner kelak memutuskan.

## Bahan

| Sumber | Dipakai | Catatan |
|---|---|---|
| Label owner (`ciri.json`) | merek | Latih: Honda 71, Toyota 22, Yamaha 13, Daihatsu 12, Suzuki 5, Mitsubishi 4, Nissan 3, Wuling 2, Mazda 1, lainnya 4, tak yakin 4. Uji: Honda 21, Daihatsu 4, Toyota 4, Mitsubishi 2, Suzuki 1, Yamaha 2, lainnya 1, tak yakin 4 |
| Roboflow "brand" (JMTO), 7.339 gambar 1920×1080 | merek mobil | 41 kelas; 37 di antaranya sudah nama merek. Empat kelas nama model dipetakan: `agya`, `alphard` → Toyota; `ayla`, `sigra` → Daihatsu. Merek di luar daftar kita (audi, bmw, byd, chery, …, 27 kelas) → `lainnya` |
| Roboflow "Merk dan Warna Motor" | merek motor | Kata pertama nama kelas: `Honda_*` → Honda, `Yamaha_*` → Yamaha |

**Tidak dipakai:** Roboflow "all-cars-logo" (16.920 kotak **logo**, bukan kotak kendaraan). Mencampurnya ke pengenal potongan kendaraan
akan melatih dua macam gambar sebagai satu hal. Ia disimpan untuk cara kedua (pencari logo), yang baru dikerjakan bila pengenal potongan
tidak cukup.

**Batas yang sudah diketahui:** daftar merek mobil kita 10 merek + "lainnya", sedangkan 27 merek Roboflow semuanya jatuh ke "lainnya",
jadi kelas itu memuat mobil yang sangat berbeda-beda. Merek motor hanya Honda dan Yamaha di bahan; Suzuki dan Kawasaki hanya dari owner
(masing-masing sangat sedikit).

## Architecture

- `tools/lab/potongan_ciri.py` mendapat ciri ketiga, `merek`:
  - label owner dari kartu (seperti jenis dan warna; "tak yakin" ditulis kosong);
  - sumber Roboflow: `merek_kelas` {nama kelas: merek} di susunan (eksplisit dan bisa diperiksa), `merek_kata_pertama` untuk nama kelas
    seperti `Honda_Beat_Hitam`, dan `merek_sisa` untuk kelas yang tidak dipetakan (mis. `lainnya`; tanpa itu barisnya dilewati dan
    dihitung).
  - `ciri.csv` bertambah kolom `merek`. Uji lama yang menyamakan isi hitungan **diperluas**, bukan dihapus: perilakunya tidak dicabut.
- `tools/lab/ciri.py` tidak berubah: `latih`/`ekspor`/`PengenalCiri` sudah menerima nama ciri apa pun.

## Calon

| Calon | Isi |
|---|---|
| **M0** (tanpa latihan) | selalu menjawab merek terbanyak di sisi latih. Lantai yang jujur: pengenal yang tidak mengalahkannya tidak berguna |
| **M1** | CNN dari Roboflow brand + Merk dan Warna Motor + owner |
| **M2** | CNN dari owner saja |

Ambang {0; 0,5; 0,7; 0,9}.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

Sama persis dengan Rencana 33: dinilai di **validasi owner**, **nilai = benar − salah** tertinggi; seri → salah paling sedikit; seri →
calon tanpa latihan (M0), lalu M1; seri → ambang terkecil. **Penjaga:** calon terpilih dipakai hanya bila nilainya lebih besar dari M0.
Pilihan di-commit sebelum uji dibuka, lalu diukur sekali di kartu owner sisi uji.

## Task 1: Merek di potongan ciri

**Files:** Modify `tools/lab/potongan_ciri.py`, `tools/lab/uji/test_potongan_ciri.py`.

- [x] **Step 1: Uji merah:** merek owner masuk kolom baru; `merek_kelas` memetakan nama kelas; `merek_kata_pertama`; `merek_sisa`
  menampung kelas yang tidak dipetakan, dan tanpa itu barisnya dilewati dan dihitung; hitungan per kelas merek; uji lama diperluas.
  (5 uji merah; uji lama `test_tak_yakin...` diperluas, bukan dihapus: perilakunya tidak dicabut, hanya bertambah satu ciri.)
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, Node hijau. (Lab 414 → 418, image tambahan 38, Node 120.)

## Task 2: Bahan dan pelatihan

- [x] **Step 1:** Bangun ulang potongan ciri dengan sumber brand ditambahkan; periksa hitungan per kelas merek. Potongan jenis dan warna
  harus tetap sama dengan Rencana 33. (**Diubah saat dijalankan:** dibangun ke folder **baru** `potongan-ciri-2`, bukan menimpa
  `potongan-ciri`, supaya bahan Rencana 33 tetap persis seperti saat diukur. 9.973 potongan; dari brand 597 kotak merek di luar daftar
  kita dilewati, dan `merek_sisa` tidak dipakai supaya kelas "lainnya" tidak membengkak melebihi kenyataan di gerbang.)
- [x] **Step 2:** Latih M1 dan M2 di latar dengan penjaga GPU; ekspor ONNX. (2,9 dan 0,2 menit; ONNX sama dengan torch 40 dari 40.)

## Task 3: Memilih, mengukur, lalu BERHENTI

- [x] **Step 1:** Nilai M0, M1, M2 × ambang di validasi owner; pilih menurut aturan; commit sebelum uji dibuka. (**M1 ambang 0,7** nilai 9;
  M2 ambang 0,5 juga 9 tetapi salahnya 3 lawan 2; M0 "selalu Honda" −4. **Diperjelas saat dijalankan:** M0 memakai merek terbanyak di
  potongan **owner** sisi latih, bukan seluruh bahan latih, karena itu prior tempat pemakaiannya dan lantainya jadi lebih tinggi.)
- [x] **Step 2:** Ukur sekali di kartu owner sisi uji; `periksa-jualan`; hitung juga per kelas merek. (34 potongan berlabel merek: benar 12,
  salah 3, tak yakin 19. **Ditambah saat dijalankan:** hitungan "benar di luar merek terbanyak", yang membuka bahwa 12 benar itu semuanya
  Honda dan nol benar di luar Honda.)
- [x] **Step 3:** Laporan `bukti/2026-10-25-merek.md` dan `.json`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh, commit.
  **BERHENTI untuk owner.**

**Batas:** uji owner hanya 39 kartu, dan sesudah "tak yakin" dibuang tinggal sekitar 35; Honda mengisi lebih dari separuhnya, jadi
pengenal yang selalu menjawab Honda sudah terlihat lumayan — itulah gunanya calon M0. Merek selain Honda, Toyota, dan Daihatsu hampir
tidak terukur. Potongan berasal dari kotak kendaraan yang owner periksa, bukan rekaman gerbang.
