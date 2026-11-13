# Fase 3, Rencana 33: Pengenal jenis dan warna kendaraan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K61, K62). Owner dihentikan hanya di akhir.

**Goal:** jenis dan warna kendaraan dikenali dari potongan kendaraan yang sudah ditemukan rantai. Merek menyusul di Rencana 34.
Spec Fase 3 bagian 4 menaruh warna di Rencana 33 dan jenis di Rencana 32; jenis pindah ke sini bersama warna karena pencari kendaraan
dibuat satu kelas (Rencana 32, alasannya di sana).

**Ukuran yang dipakai (spec bagian 1):** ciri **salah** adalah peringatan palsu, yaitu satpam dipanggil untuk kendaraan yang sah.
"Tak yakin" tidak pernah memanggil satpam. Jadi tiap calon dinilai dengan **benar − salah**, bukan benar saja.

## Bahan

| Sumber | Dipakai untuk | Catatan |
|---|---|---|
| Label owner (`data/keluaran/label-ciri/ciri.json`, 180 kendaraan) | jenis, warna | Kotak yang ditandai owner "tidak pas" (8) dibuang dari semua sisi: potongannya tidak mewakili satu kendaraan |
| Roboflow "vehicle and license plate" (cars, motorcyle, truck) | jenis | 4.638 + 1.144 + 189 kotak |
| Roboflow "Merk dan Warna Motor" (13 kelas model × warna) | jenis (motor), warna | Warna dari nama kelas: Hitam, Merah, Putih, Kuning, Hijau, Silver → `abu_perak`. **"Biru-Putih" dibuang** (dua warna, tidak bisa dipetakan ke satu kelas) |

Semua `BOLEH-PRODUK` (K44, K56). Dataset "brand" dan "all-cars-logo" disimpan untuk Rencana 34 (merek).

**Sisi:** owner kartu sisi latih dibagi tetap menurut SHA-256 id kartu, 1 dari 4 ke validasi; kartu sisi uji → uji. Roboflow train dan
test → latih, valid → validasi Roboflow (penjaga, tidak memilih calon).

## Architecture

- `tools/lab/potongan_ciri.py bangun`: potongan kendaraan dari semua sumber ke `<keluar>/potongan/<awalan>-<sidik>.png` dan
  `<keluar>/ciri.csv` (berkas, sumber, sisi, jenis, warna). Nama berkas baru dari SHA-256 nama asli (nama asli bisa memuat nomor plat).
  Batas per kelas per sisi tersedia (deterministik dari SHA-256), supaya mobil tidak menenggelamkan motor. `ringkasan.json`: hitungan per
  sumber, sisi, dan kelas, beserta daftar bahan.
- `tools/lab/ciri.py`:
  - `warna_aturan(potongan)` (calon W0, tanpa latihan): bagian tengah potongan, HSV; jenuh rendah → putih/abu_perak/hitam menurut
    terang; selain itu dari rona → merah/kuning/hijau/biru.
  - `nyaris_tanpa_warna(potongan)`: median jenuh di bawah `AMBANG_ABU` → warna selalu `tak_yakin` (K52, gambar inframerah). Berlaku untuk
    W0 maupun mesin.
  - `MesinCiri`: CNN kecil (96×96 RGB) → satu kepala kelas. `latih` memilih zaman dengan benar − salah di validasi owner; `ekspor` ke ONNX
    hanya bila sama dengan torch; `PengenalCiri` memuat ONNX dengan pemeriksaan SHA-256, memberi `(kelas, yakin)` dan `tak_yakin` di bawah
    ambang di `mesin-onnx.json`.
  - Variasi latihan tidak mengubah rona atau jenuh (itu akan merusak label warna): hanya cermin, putar kecil, geser, terang ±10%, kabur,
    derau.
  - `jenis_coco(potongan, cari)` (calon J0, tanpa latihan): pencari kendaraan COCO dijalankan pada potongan; kelas kotak terbesar menjadi
    jenis; tanpa kotak → `tak_yakin`.

## Calon

| Ciri | Calon |
|---|---|
| Jenis | **J0** pencari COCO (tanpa latihan, pembanding) · **J1** CNN dari Roboflow + owner latih · **J2** CNN dari owner latih saja |
| Warna | **W0** aturan piksel (tanpa latihan) · **W1** CNN dari Merk dan Warna Motor + owner latih · **W2** CNN dari owner latih saja |

Ambang yakin tiap calon dipilih dari {0; 0,5; 0,7; 0,9} (0 = tidak pernah "tak yakin").

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- Dinilai di **validasi owner** (kartu sisi latih yang jatuh ke validasi), per ciri: **benar − salah** tertinggi menang. "Tak yakin"
  tidak dihitung benar maupun salah.
- Seri: salah paling sedikit. Seri: calon tanpa latihan (J0/W0), lalu J1/W1. Seri: ambang terkecil.
- **Penjaga:** calon terpilih dipakai hanya bila benar − salah-nya di validasi owner lebih besar dari calon tanpa latihan. Bila tidak,
  calon tanpa latihan yang dipakai, dan itu dilaporkan apa adanya.
- Validasi Roboflow dilaporkan sebagai penjaga, tidak memilih.
- Pilihan di-commit sebelum uji dibuka.
- **Diukur sekali di uji:** benar, salah, dan tak yakin per ciri di kartu owner sisi uji, dengan ambang terpilih.

## Task 1: Potongan ciri

**Files:** Create `tools/lab/potongan_ciri.py`, `tools/lab/uji/test_potongan_ciri.py`.

- [x] **Step 1: Uji merah:** potongan owner dari `ciri.json` (kotak tidak pas dibuang dan dihitung; `bukan_kendaraan` dan yang belum
  lengkap dibuang); sisi latih dibagi tetap ke latih/validasi, sisi uji ke uji; warna dari nama kelas Roboflow, "Biru-Putih" dibuang;
  jenis dari kelas Roboflow; batas per kelas deterministik; nama asli tidak muncul; ringkasan dan bahan; CLI sampai berkas.
  (**Ditambah:** kotak yang sisinya di bawah `MIN_SISI` 24 piksel dilewati dan dihitung; "tak yakin" ditulis kosong dan ciri lain di
  kartu itu tetap dipakai.)
- [x] **Step 2:** Tulis kodenya. Gerbang hijau. (9 uji merah dulu karena modulnya belum ada.)

## Task 2: Aturan warna dan pengenal CNN

**Files:** Create `tools/lab/ciri.py`, `tools/lab/uji/test_ciri.py`; uji sungguhan di `tools/lab/uji_fpo/`.

- [x] **Step 1: Uji merah:** `warna_aturan` pada tampalan warna buatan; `nyaris_tanpa_warna` pada gambar kelabu; latihan memilih zaman
  dengan benar − salah; ambang "tak yakin"; `ekspor` menolak ONNX yang beda dari torch; `PengenalCiri` menolak berkas yang berubah;
  variasi latihan tidak mengubah rona. (20 uji merah dulu; ditambah 2 uji ONNX sungguhan di image tambahan.)
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, Node hijau. (Lab 385 → 414, image tambahan 36 → 38, Node 120.)
  **Diubah dari rencana, dan kenapa:**
  - saringan inframerah memakai **gambar penuh**, bukan potongan: kendaraan hitam atau putih juga nyaris tanpa warna, jadi potongan
    sendiri tidak bisa membedakannya dari gambar inframerah. `saring_inframerah(warna, gambar_penuh)` dipisah dari `warna_aturan`;
  - zaman dipilih dengan **benar terbanyak** di validasi owner, bukan benar − salah: pada ambang 0 tidak ada "tak yakin", jadi
    benar − salah = 2 × benar − jumlah, yang urutannya sama persis. Pemilihan **calon** tetap memakai benar − salah per ambang;
  - ambang "tak yakin" **tidak disimpan di mesin**: `PengenalCiri` menuntutnya sebagai argumen, supaya tidak ada ambang tersembunyi.
    Ambang terpilih dicatat di laporan dan dipasang di rantai pada Rencana 35.

## Task 3: Bahan dan pelatihan

- [x] **Step 1:** Bangun potongan ciri; periksa hitungan per kelas. (6.289 potongan: owner 172 — 8 kotak tidak pas dibuang —,
  vehicle and license plate 3.033, Merk dan Warna Motor 3.084 dengan 208 "Biru-Putih" dibuang.)
- [x] **Step 2:** Latih J1, J2, W1, W2 di latar dengan penjaga GPU; ekspor ONNX. (3,3 · 0,2 · 1,6 · 0,2 menit; ONNX sama dengan torch
  40 dari 40 untuk keempatnya.)

## Task 4: Memilih, mengukur, lalu BERHENTI

- [x] **Step 1:** Nilai semua calon × ambang di validasi owner; pilih menurut aturan; commit sebelum uji dibuka. (**J1 ambang 0** nilai 31
  lawan J2 27 dan pencari COCO 21; **W1 ambang 0,7** nilai 9 lawan W2 7 dan aturan piksel −3. Seri W1 di ambang 0 dan 0,7 dipecah salah
  paling sedikit.)
- [x] **Step 2:** Ukur sekali di kartu owner sisi uji; `periksa-jualan` untuk mesin terpilih. (37 potongan: jenis benar 32 salah 5;
  warna benar 16 salah 6 tak yakin 15. Keduanya `BOLEH-PRODUK`.)
- [x] **Step 3:** Laporan `bukti/2026-10-24-jenis-dan-warna.md` dan `.json`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh, commit.
  **BERHENTI untuk owner.**

**Batas yang sudah diketahui sekarang:**
- jenis langka hampir tidak ada di label owner (pikap 3, truk 2, bus 0), jadi angkanya akan ditulis "terlalu sedikit untuk disimpulkan";
- warna biru dan coklat/krem hanya ada di label owner dan sedikit; Roboflow tidak punya coklat/krem;
- validasi owner dipakai untuk memilih zaman dan memilih calon sekaligus, jadi angka validasinya terlalu baik; angka uji yang jujur;
- tidak ada gambar inframerah di label owner, jadi aturan "tak yakin" untuk inframerah hanya diuji dengan gambar buatan;
- potongan berasal dari kotak pencari kendaraan dan kotak owner, bukan dari rekaman gerbang.
