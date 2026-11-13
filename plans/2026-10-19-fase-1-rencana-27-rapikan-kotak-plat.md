# Fase 1, Rencana 27: Kotak plat dirapikan dengan pencarian kedua (K54) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K54). Owner dihentikan hanya di akhir.

**Goal:** kotak plat yang terlalu besar atau terlalu kecil dibuat pas sebelum dibaca. Di Rencana 26, dari 4 bacaan yang rusak di tangkapan
uji, dua kotak C1 jauh lebih besar dari plat (1,15 dan 1,48 kali lebar), dan satu lebih sempit (0,88 kali lebar)
(`bukti/2026-10-19-pembaca-tahan-geser.md`).

**Architecture:**
- Modul baru `tools/lab/rapikan.py`:
  - `rapikan_kotak(gambar, kotak, cari, ambang, konteks)`: potongan sekitar kotak, diperlebar `konteks` × lebar dan tinggi kotak di tiap
    sisi (dipotong pada batas gambar), dicari lagi dengan pencari yang sama. Letterbox pencari memperbesar potongan, jadi plat terlihat
    lebih besar dan kotaknya lebih rinci. Dari kotak di atas ambang yang tengahnya berada di dalam kotak pertama, dipilih yang yakinnya
    terbesar; koordinatnya dikembalikan ke gambar utuh, dan unsur lain kotak (jenis dan kotak kendaraan) dibawa. Bila tidak ada, kotak
    pertama dipakai apa adanya.
  - `konteks = 0` berarti mati (kode lama yang sama persis).
- `baca_gambar.py` dan `rantai.py` mendapat `--rapikan <konteks>` (bawaan 0), dicatat di aturan ringkasan. Rapikan dikerjakan sesudah
  kotak ditemukan dan sebelum dipotong untuk dibaca.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Calon:** konteks 0 (mati), 1,0 (potongan 3 kali kotak), dan 2,0 (5 kali kotak). Alasannya: di potongan kendaraan yang dipakai melatih
  C1, plat kira-kira mengisi sepertiga sampai seperlima lebar potongan, jadi skala plat di pencarian kedua mendekati skala yang dikenal
  pencari.
- Rantai lain sama dengan Rencana 25 dan 26: kendaraan cadangan gambar utuh, pencari C1 ambang 0,25, pembaca fpo-indo-1 ONNX, varian
  potongan v0.
- **Dipilih** `dibaca_benar` terbanyak (mobil + motor) dengan `nilai_label` di **sisi latih** tangkapan. Bila seri, konteks 0 (paling cepat).
- **Diukur sekali** di tangkapan uji, hanya calon terpilih, dibandingkan dengan Rencana 25 dan 26 (21 dari 34), termasuk perpindahan per plat
  dan geometri kotak terhadap label.
- **Batas yang sudah diketahui:** gambar latih ikut melatih C1. Kotak label untuk plat yang ditemukan rantai lama berasal dari kotak rantai
  lama (`cctv1`), sehingga "pas" diukur terhadap kotak itu.

## Task 1: Modul rapikan dan sambungannya

**Files:** Create `tools/lab/rapikan.py`, `tools/lab/uji/test_rapikan.py`; Modify `tools/lab/baca_gambar.py`, `tools/lab/rantai.py`, uji
`test_baca_gambar.py`, `test_rantai.py`, `uji_fpo/test_rantai_sungguhan.py` (isi ringkasan `baca_gambar`).

- [x] **Step 1: Uji merah.**
  - kotak yang terlalu besar menjadi pas, dan yang terlalu kecil melebar (pencari tiruan yang melihat plat di potongan);
  - tanpa kotak kedua di dalam kotak pertama, kotak pertama dipakai; konteks 0 = cara lama;
  - unsur kotak lain (jenis, kotak kendaraan) dibawa; konteks negatif ditolak;
  - `baca_gambar.jalankan(..., rapikan=1.0)` dan `rantai.jalankan_semua(..., rapikan=1.0)` memakai kotak rapi untuk dipotong dan dibaca,
    dan mencatatnya di aturan; konteks 0 sama persis dengan cara lama;
  - uji rantai lewat CLI (`--rapikan`) sampai berkas keluaran, untuk `baca_gambar` dan `rantai`.
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (9 uji baru merah dulu; lab 324 → 332, image tambahan 35,
  Node 120.)

## Task 2: Memilih di sisi latih

- [x] **Step 1:** `baca_gambar` dengan konteks 0, 1,0, 2,0 pada `data/capture`. `nilai_label` sisi latih saja. Pemeriksaan: konteks 0 harus
  sama dengan Rencana 26 v0 (dibaca benar 85). **Hasil:** konteks 0: 45 + 40 = 85 (sama); 1,0: 43 + 39 = 82; 2,0: 45 + 35 = 80.
  Geometri sisi latih: kotak yang dirapikan **kurang pas** terhadap label (IoU median motor 0,873 → 0,796 dan mobil 0,908 → 0,840 pada
  konteks 1,0; rasio tinggi sekitar 0,95), jadi pencarian kedua memendekkan kotak.
- [x] **Step 2:** Pilih menurut aturan; di-commit sebelum sisi uji dibuka. **Terpilih: konteks 0 (rapikan tidak dipakai).**

## Task 3: Ukur sekali di uji, dan kecepatan

- [x] **Step 1:** `nilai_label` sisi uji untuk calon terpilih; perpindahan per plat (`banding-rantai-25.mjs`) dan geometri kotak terhadap
  label (`ukuran-kotak-25.mjs`, `geometri-pindah-26.mjs`). **Hasil:** konteks 0, 21 dari 34, sama dengan Rencana 25 (jalur sama, jadi
  perpindahan dan geometri uji juga sama dengan Rencana 26).
- [ ] ~~**Step 2:** Milidetik per plat untuk merapikan di CPU 2 utas (satu panggilan pencari tambahan per plat).~~ Dilewati dengan sengaja:
  rapikan tidak dipakai.

## Task 4: Laporan, lalu BERHENTI

- [x] **Step 1:** `bukti/2026-10-19-rapikan-kotak-plat.md`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh, lalu commit.
- [ ] **Step 2: BERHENTI untuk owner.**

**Batas:** tangkapan uji kecil (38 gambar, 34 berteks); bukan rekaman gerbang (bukan K9); manfaat di video belum diukur.
