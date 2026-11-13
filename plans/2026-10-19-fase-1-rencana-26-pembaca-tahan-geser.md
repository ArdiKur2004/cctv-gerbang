# Fase 1, Rencana 26: Pembaca tahan geser (K51) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K51). Owner dihentikan hanya di akhir (Task 5).

**Goal:** bacaan plat tidak berubah hanya karena kotak pencari sedikit bergeser. Di Rencana 25, di tangkapan uji, 4 plat yang dulu dibaca
benar menjadi salah dengan pembaca yang sama (fpo-indo-1), karena kotak C1 bergeser: rasio ukuran 0,98–1,08, tetapi IoU median 0,84
(motor) dan 0,88 (mobil) terhadap kotak label (`bukti/2026-10-19-rantai-optimal.md`). Pembaca membaca beberapa potongan yang sedikit
digeser atau diperlebar, lalu memungut suara. Tidak ada pelatihan.

**Architecture:**
- Modul baru `tools/lab/tahan_geser.py`:
  - `potong_geser(gambar, kotak, margin, geser_x, geser_y)`: potongan kotak yang diperlebar `margin`, lalu digeser sebesar pecahan
    lebar dan tinggi kotak. Pada (0,05; 0; 0) potongannya sama persis dengan `rantai.potong`.
  - `VARIAN`: daftar (margin, geser_x, geser_y) per nama:
    - `v0`: (0,05; 0; 0), cara sekarang;
    - `v1`: v0 ditambah margin 0 dan 0,12 (3 potongan);
    - `v2`: v1 ditambah geser ±0,06 lebar dan ±0,10 tinggi pada margin 0,05 (7 potongan).
    Besarannya diturunkan dari Rencana 25: IoU 0,85 dengan ukuran sama kira-kira sesuai geser 8% lebar; tinggi plat kecil, jadi geser
    tegak dibuat sedikit lebih besar dalam pecahan.
  - `pungut_suara(bacaan)`: hanya bacaan yang sesuai pola plat (`plat.urai`) yang dihitung. Teks terbanyak menang; bila seri, jumlah
    yakin terbesar; bila masih seri, yang lebih dulu di urutan varian. Bila tak satu pun sesuai pola, bacaan potongan pertama dipakai
    (sama dengan cara sekarang). Yakin = rata-rata yakin suara pemenang × (suara pemenang / jumlah potongan).
  - `baca_tahan_geser(gambar, kotak, baca, varian)`: kembali (teks, yakin, potongan pertama).
- `baca_gambar.py` dan `rantai.py` mendapat `--varian-potong` (bawaan `v0`, jadi perilaku lama tidak berubah). Ringkasan mencatatnya.
- Tanpa nomor plat di layar atau di berkas bersama, seperti alat lain.

**Tech Stack:** lab biasa untuk uji; image tambahan `-Fpo` untuk menjalankan pembaca ONNX di CPU. Tanpa GPU.

---

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Calon:** v0, v1, v2, masing-masing dengan rantai Rencana 25 (kendaraan cadangan gambar utuh, pencari C1 ambang 0,25, pembaca
  fpo-indo-1 ONNX).
- **Dipilih** `dibaca_benar` terbanyak (mobil + motor) dengan `halaman_label.nilai_label` di **sisi latih** tangkapan. Bila seri, yang
  potongannya lebih sedikit (v0, lalu v1, lalu v2), karena lebih cepat.
- **Diukur sekali** di tangkapan uji, hanya calon terpilih, dan dibandingkan dengan Rencana 25 (dibaca benar 21 dari 34), termasuk
  perpindahan per plat.
- **Batas yang sudah diketahui:** gambar latih ikut melatih C1, jadi kotak C1 di sisi latih mungkin lebih tepat daripada di uji, dan
  manfaat tahan geser di latih bisa lebih kecil daripada di uji. Pembaca (fpo-indo-1) tidak pernah melihat tangkapan.

## Task 1: Modul tahan geser dan sambungannya

**Files:** Create `tools/lab/tahan_geser.py`, `tools/lab/uji/test_tahan_geser.py`; Modify `tools/lab/baca_gambar.py`, `tools/lab/rantai.py`,
uji `test_baca_gambar.py`, `test_rantai.py`, dan `uji_fpo/test_rantai_sungguhan.py` (yang menuntut isi ringkasan `baca_gambar`).

- [x] **Step 1: Uji merah.**
  - `potong_geser` sama dengan `rantai.potong` pada v0, dan geseran memindahkan jendela sesuai pecahan kotak;
  - jumlah potongan v0/v1/v2 = 1/3/7; nama varian tak dikenal ditolak;
  - `pungut_suara`: bacaan di luar pola diabaikan, terbanyak menang, seri dipecah dengan jumlah yakin, tak ada yang sesuai pola →
    potongan pertama;
  - `baca_gambar.jalankan(..., varian="v2")` memanggil pembaca 7 kali per plat dan mencatat varian di ringkasan; v0 sama persis dengan
    cara lama;
  - `rantai.jalankan_semua(..., varian="v1")` sama;
  - uji rantai lewat CLI (`--varian-potong`) sampai berkas keluaran, untuk `baca_gambar` dan `rantai`.
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (11 uji baru merah dulu; lab 313 → 324, image tambahan 35,
  Node 120.) Jalur v0 memakai kode lama yang sama persis, supaya teks mentah yang disimpan rantai tidak berubah.

## Task 2: Memilih di sisi latih

- [x] **Step 1:** `baca_gambar` dengan v0, v1, dan v2 pada `data/capture` (rantai Rencana 25). `nilai_label` sisi latih saja.
  Pemeriksaan: v0 harus sama dengan Rencana 25 (`rantai-ambang-0.25`, dibaca benar 85). **Hasil:** v0 45 + 40 = 85 (sama), v1 46 + 42 = 88,
  v2 46 + 43 = 89. Plat ditemukan sama di ketiganya (54 dan 75).
- [x] **Step 2:** Pilih menurut aturan. **Terpilih v2.** Dicatat dan di-commit sebelum sisi uji dibuka.

## Task 3: Kecepatan

- [x] **Step 1:** Milidetik per plat untuk membaca (v0, v1, v2) di CPU dengan 2 utas, pada potongan sisi latih. Catat apakah mesin tenang
  (`docker ps`, `nvidia-smi`, proses uji sesi lain); bila tidak, tulis sebagai batas. **Hasil:** v0 16,9, v1 50,3, v2 110,8 ms per plat;
  beban CPU sebelum 4%, tanpa kontainer lab atau uji lain; putaran berselisih (dicatat sebagai batas).

## Task 4: Ukur sekali di uji

- [x] **Step 1:** `nilai_label` sisi uji untuk calon terpilih, dibandingkan dengan Rencana 25, ditambah perpindahan per plat
  (`banding-rantai-25.mjs`). **Hasil:** v2 21 dari 34, sama persis dengan Rencana 25 (tidak ada plat yang berubah status). Geometri empat
  plat yang benar → salah di Rencana 25 (`geometri-pindah-26.mjs`): dua kotak jauh lebih besar (sampai 1,48 kali lebar), satu lebih sempit,
  satu hampir sama tetapi salah di semua potongan. **v2 tidak dijadikan bawaan** (bawaan alat tetap v0), seperti saringan letak Rencana 21.

## Task 5: Laporan, lalu BERHENTI

- [x] **Step 1:** `bukti/2026-10-19-pembaca-tahan-geser.md`, ROADMAP dan changelog, `CLAUDE.md` §7 bila ada alat baru. Gerbang penuh,
  lalu commit.
- [ ] **Step 2: BERHENTI untuk owner:** hasil A, ditambah ringkasan survei merek dan warna mobil (K51) bila sudah selesai.

**Batas yang sudah diketahui:**
- Tangkapan uji kecil (38 gambar, 34 berteks); perbedaan 1–3 plat tidak bermakna.
- Tangkapan bukan rekaman gerbang (bukan K9).
- Di video, rantai menggabung banyak bingkai per kedatangan; manfaat tahan geser di video belum diukur di rencana ini.
