# Rencana 28: Tiga dataset merek Indonesia dari Roboflow diunduh dan diperiksa (K53) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Owner mengunduh
> (Roboflow mewajibkan akun; sandi selalu diketik owner) dan memeriksa lembar contoh; selain itu mandiri (K37).

**Goal:** tiga dataset (all-cars-logo v7, brand v11 milik akun JMTO, car-type-final-1 v2; semuanya berlabel CC BY 4.0) dipastikan **aman
dari malware** dan **isinya benar**, lalu owner memutuskan boleh tidaknya dipakai. Pemeriksaan bukan izin pakai; sampai owner memutuskan,
bahan ini `BELUM-JELAS` (K53). Bahan Fase 3 (S3, K8 tahap 1); tidak ada pelatihan di rencana ini.

**Yang dibaca dari halaman Roboflow (19 Okt, peramban terpisah tanpa akun, hanya teks):**

| Dataset | Pengunggah | Versi | Gambar (latih / validasi / uji) | Pra-proses | Augmentasi | Izin |
|---|---|---|---|---|---|---|
| all-cars-logo-r9pfo | zendyyonghero | v7 "Full 80 - 20 split for all labels" | 16.920 (13.540 / 3.380 / 0) | Auto-Orient | tidak ada | CC BY 4.0 |
| brand-o0woc | JMTO | v11 (2025-10-10) | 7.339 (5.871 / 735 / 733) | tidak ada | tidak ada | CC BY 4.0 |
| car-type-final-1 | Skripsi | v2 (2024-03-15) | 1.823 (1.272 / 551 / 0) | Resize 600×600 (v1) | tidak ada | CC BY 4.0 |

Keamanan halaman (dibaca agen): domain resmi Roboflow; Google Safe Browsing "tidak ditemukan konten berbahaya" untuk universe.roboflow.com
dan app.roboflow.com; sertifikat dari Google Trust Services dan berlaku; masuk Google lewat accounts.google.com lalu kembali ke
app.roboflow.com.

## Cara aman (zip diperlakukan tak tepercaya)

1. Zip tidak pernah dibuka atau dijalankan di Windows. Disalin dari Downloads ke `data/unduhan/roboflow-<nama>/`, SHA-256 dihitung, lalu
   dicatat di `tools/vendor.lock.json` (daftar `berkas`, diganti sebagai teks) dan di `data-asal/bahan.json` (vonis `BELUM-JELAS`).
2. Windows Defender memindai zip. Kontrol positif lebih dulu: berkas uji antivirus resmi EICAR (tidak berbahaya) harus terdeteksi, supaya
   "0 ancaman" bisa dipercaya.
3. `tools/lab/buka_arsip.py` membuka zip di lab tanpa jaringan: jalur mutlak, "..", tautan simbolik, dan ukuran berlebih membatalkan semuanya;
   hanya akhiran gambar dan teks yang dikeluarkan.
4. `tools/lab/periksa_dataset.py periksa` (baru) di lab tanpa jaringan:
   - **Keamanan:** jenis tiap berkas dicek dari isinya (JPEG `FF D8 FF`, PNG `89 50 4E 47`; berkas teks harus UTF-8 tanpa byte nol); tanda
     berkas program (`MZ`, `\x7fELF`, `#!`, arsip `PK` di dalam arsip, `%PDF`) di awal berkas apa pun dihitung; `data.yaml` dibaca dengan
     `yaml.safe_load` (tag Python ditolak, tidak dijalankan); tiap gambar didekode utuh.
   - **Kebenaran:** daftar kelas dari `data.yaml`; per sisi: gambar, label, gambar tanpa label, label tanpa gambar, label kosong, baris
     rusak (bukan 5 angka), kelas di luar daftar, koordinat di luar 0–1, kotak berukuran nol; kotak dan gambar per kelas; gambar kembar
     persis (SHA-256) dan hampir kembar (dHash 64 bit sama) di dalam sisi dan antarsisi (kebocoran latih/uji); ukuran gambar.
   - Hanya hitungan dan nama kelas yang dicetak; nama berkas tidak (bisa memuat nomor plat).
5. `periksa_dataset.py lembar` (baru): lembar contoh untuk **owner**: paling banyak 3 potongan kotak per kelas, bernomor baris dan bertulis
   nama kelasnya. Owner menyebut nomor baris yang labelnya salah. Agen tidak membuka lembar (gambar memuat kendaraan dan plat orang).

## Task 1: Alat pemeriksa (sebelum zip datang)

**Files:** Create `tools/lab/periksa_dataset.py`, `tools/lab/uji/test_periksa_dataset.py`.

- [x] **Step 1: Uji merah** dengan dataset buatan: dataset sehat; berkas `.jpg` yang isinya program (`MZ`); berkas teks berbyte nol;
  `data.yaml` bertag Python; baris label rusak, kelas di luar daftar, koordinat di luar 0–1; gambar kembar lintas sisi; gambar tanpa label dan
  label tanpa gambar; lembar 3 per kelas; nama berkas tidak muncul di keluaran; CLI sampai berkas keluaran. (7 uji, merah karena modulnya
  belum ada; uji `yaml` membuktikan perintah di tag Python tidak dijalankan.)
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (Lab 332 → 339, image tambahan 35, Node 120.) Kotak dan
  hitungan per kelas hanya dari label yang punya gambar; cacat label diperiksa di semua label.

## Task 2: Unduh (owner) dan kunci

- [x] **Step 1 (owner):** tiga zip di Downloads. **Diubah saat dijalankan:** car-type ternyata dataset klasifikasi, jadi diunduh format
  Folder Structure, bukan YOLOv8; `periksa_dataset.py` diperluas untuk susunan klasifikasi (uji merah dulu).
- [x] **Step 2:** salin ke `data/unduhan/roboflow-<nama>/`, SHA-256, catat di kunci dan daftar bahan (`node tools/bahan.mjs periksa`: 16 bahan).
- [x] **Step 3:** Defender dengan kontrol positif EICAR (terdeteksi, kode 2), lalu pindai ketiga zip (kode 0).

## Task 3: Buka dan periksa

- [x] **Step 1:** `buka_arsip.py daftar` lalu `buka` ke `data/keluaran/dataset/roboflow-<nama>/`. **Diubah saat dijalankan:** all-cars-logo
  ditolak karena `data.yaml` kembar; salinannya identik, jadi aturan `buka_arsip.py` diubah (uji merah dulu): salinan identik dibuka sekali,
  isi berbeda tetap ditolak.
- [x] **Step 2:** `periksa_dataset.py periksa` untuk ketiganya; ringkasan ke `bukti/2026-10-19-dataset-roboflow.json`.
- [x] **Step 3:** `periksa_dataset.py lembar` untuk ketiganya (182, 110, 12 baris).

## Task 4: Laporan, lalu BERHENTI

- [x] **Step 1:** `bukti/2026-10-19-dataset-roboflow.md` (keamanan, kebenaran, kecocokan dengan halaman Roboflow), ROADMAP dan changelog.
  Gerbang penuh, lalu commit. (Lab 339 → 344, image tambahan 35, Node 120.)
- [x] **Step 2: BERHENTI untuk owner:** lembar contoh per kelas (owner menyebut nomor baris yang salah), lalu keputusan boleh tidaknya dipakai
  di mesin jualan. **19 Okt:** boleh dipakai sejak K56; owner memeriksa kelima lembar, semua benar (car-type benar tetapi datanya sedikit).

**Batas:** asal gambar tidak diketahui (pengunggah anonim); label CC BY 4.0 dari halaman pengunggah, bukan dari pemilik gambar; lembar contoh
hanya sampel, bukan pemeriksaan semua label.
