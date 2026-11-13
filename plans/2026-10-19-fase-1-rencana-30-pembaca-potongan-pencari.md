# Fase 1, Rencana 30: Pembaca dilatih lanjut dengan potongan dari rantai kita sendiri — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37); arah disetujui owner 19 Okt ("silahkan lanjut melatih pembaca huruf dengan potongan dari pencari kita sendiri, supaya tetap
> membaca benar walau kotaknya kurang pas"). Owner dihentikan hanya di akhir.

**Goal:** pembaca fpo-indo-1 tetap membaca benar walau kotak dari pencari kurang pas. Rencana 25–29 menunjukkan pembacalah yang membatasi
rantai: pencari C3 menemukan lebih banyak plat, tetapi bacaan benar tidak naik, karena kotaknya kurang pas.

**Kenapa cara Rencana 25 diubah** (R1 dan R2 tidak menolong; dua sebab yang mungkin, dari `bukti/2026-10-19-pembaca-fpo-lanjut.md`):
1. laju belajar 0,001 (bawaan untuk melatih dari nol) terlalu besar untuk melatih lanjut → di sini **0,0001**;
2. zaman dipilih dengan validasi gabungan yang 94% isinya INDO-ALPR → di sini `validasi.csv` (yang memilih zaman) **hanya potongan
   tangkapan**; INDO-ALPR validasi pindah ke `validasi-indo.csv` dan hanya menjadi penjaga.
3. potongan latih dulu hanya dari kotak label → di sini ditambah **potongan yang dibuat rantai kita sendiri** (berkas `potongan/` keluaran
   `baca_gambar.py`, persis yang dibaca pembaca di rantai), dicocokkan ke plat berlabel dengan aturan `halaman_label.nilai_label`
   (IoU ≥ 0,3, satu kotak per plat). Teksnya dari label owner, bukan dari bacaan rantai.

**Bahan (semuanya `BOLEH-PRODUK`):** INDO-ALPR latih inti (3.954) dan validasi (460), seperti Rencana 25; tangkapan owner sisi latih dengan
pembagian validasi per plat yang sama dengan Rencana 25 (`bahan_pembaca.validasi_tangkapan`, 96 plat latih dan 29 validasi); keluaran
rantai yang sudah ada di sisi latih: C1 (`rencana-25/rantai-ambang-0.25`, `-0.4`, `-0.6`) dan C3 (`rencana-29/rantai-ambang-0.25`,
`-0.4`, `-0.6`). Sisi uji tangkapan, INDO-ALPR uji, dan potongan rantai dari gambar uji tidak dibaca saat menyiapkan atau memilih.

## Architecture

- `bahan_pembaca.siapkan(..., rantai=(), geser=False, validasi_terpisah=False)`:
  - `rantai`: daftar folder keluaran `baca_gambar.py`. Untuk tiap plat berteks di gambar sisi latih, kotak rantai yang cocok (aturan
    `nilai_label`) diambil, dan berkas potongannya disalin sebagai `potongan/c<i>-<gambar>-<n>.png` (i = urutan folder). Potongan yang isinya
    sama persis dengan potongan lain dari plat yang sama dilewati. Plat latih → `latih.csv` (diulang `ulang_tangkapan` kali); plat validasi →
    `validasi.csv`, dan per folder rantai `validasi-rantai-<i>.csv`.
  - `geser`: untuk plat latih, 6 potongan tambahan dari kotak label dengan isian `tahan_geser.VARIAN["v2"]` selain potongan pertama
    (`potongan/g<k>-...`), sekali saja. Ini meniru kotak yang kurang pas tanpa angka uji: isiannya ditetapkan di Rencana 26.
  - `validasi_terpisah`: `validasi.csv` hanya potongan tangkapan (kotak label dan rantai); INDO-ALPR validasi ke `validasi-indo.csv`.
  - `siapkan.json` mencatat hitungan per sumber dan per folder rantai, termasuk jumlah plat validasi berteks dan yang cocok di tiap folder.
- `latih_fpo.latih_lanjut(..., laju=None)`: `--lr` diteruskan ke perintah latih fast-plate-ocr (None = bawaan pembuatnya, seperti Rencana 25).
  Bila `validasi-indo.csv` ada, ketepatannya ikut diukur sebelum dan sesudah. CLI `latih-lanjut --laju`.
- `latih_fpo.ketepatan_per_sumber`: di samping `tangkapan` (semua `potongan/`, seperti sebelumnya), dipecah `tangkapan_label` (`t-`),
  `tangkapan_rantai` (`c`), dan `tangkapan_geser` (`g`).

## Calon (masing-masing dari fpo-indo-1, laju 0,0001, 30 zaman, benih 0)

| Calon | Bahan latih |
|---|---|
| R0 | fpo-indo-1 apa adanya |
| R3 | INDO-ALPR latih inti + potongan label plat latih × 5 + potongan rantai (C1 dan C3, 6 folder) plat latih × 5 |
| R4 | R3 + 6 potongan geser per plat latih |

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Ukuran utama:** dibaca benar di `validasi-rantai` C1 ambang 0,25 (plat validasi berteks; plat yang tidak ditemukan rantai dihitung salah,
  sama untuk semua calon). Ini sama dengan rantai bawaan dengan pembaca calon, di plat validasi.
- Terbanyak menang. Seri: dibaca benar terbanyak di potongan label validasi. Masih seri: R0. (Ditambah 19 Okt, sebelum angka calon mana
  pun dilihat, saat R3 dan R4 masih dilatih: bila R3 dan R4 seri di kedua ukuran dan keduanya di atas R0, R3 dipilih karena bahannya
  lebih sederhana.)
- **Penjaga:** calon yang INDO-ALPR validasinya turun lebih dari 10 gambar dari R0 ditolak (sama dengan Rencana 25).
- **Pencari di rantai bawaan sesudahnya:** dengan pembaca terpilih, C3 ambang 0,6 menggantikan C1 ambang 0,25 hanya bila dibaca benarnya
  di `validasi-rantai` C3 ambang 0,6 **lebih tinggi**; sama atau lebih rendah, C1 tetap.
- Pilihan di-commit sebelum uji dibuka.
- **Diukur sekali:** rantai utuh (`baca_gambar.py`, ONNX) dengan pembaca dan pencari terpilih di tangkapan uji (Rencana 25: 21 dari 34);
  pembaca terpilih di potongan label tangkapan uji (R0: 24 dari 34) dan INDO-ALPR uji (911 plat). Bila R0 dan C1 yang terpilih, tidak ada
  yang baru untuk diukur, dan itu dilaporkan apa adanya.

## Task 1: Bahan dari potongan rantai

**Files:** Modify `tools/lab/bahan_pembaca.py`, `tools/lab/latih_fpo.py`; uji `tools/lab/uji/test_bahan_pembaca.py`,
`tools/lab/uji/test_latih_fpo.py` (dan `uji_fpo/test_latih_lanjut.py` bila perlu).

- [x] **Step 1: Uji merah:** potongan rantai dicocokkan dengan aturan `nilai_label` (kotak terdekat yang belum dipakai, IoU ≥ 0,3) dan
  disalin persis dari berkas potongan rantai; gambar sisi uji tidak disentuh walau ada di folder rantai; potongan kembar per plat dilewati;
  plat latih diulang, validasi tidak; `validasi-rantai-<i>.csv` per folder; potongan geser 6 per plat latih, latih saja; validasi terpisah
  (INDO-ALPR ke `validasi-indo.csv`); `siapkan.json` mencatat semuanya; CLI `--rantai`, `--geser`, `--validasi-terpisah` sampai ke berkas.
  `ketepatan_per_sumber` memecah sumber baru. `latih_lanjut` meneruskan `--lr` (perintah latih dipalsukan) dan mengukur `validasi-indo.csv`.
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (12 uji baru merah dulu karena fiturnya belum ada; uji
  Keras sungguhan `uji_fpo/test_latih_lanjut.py` ditambah `laju` dan `validasi-indo.csv`, terbukti merah tanpa kode baru, lalu hijau dengan
  perintah latih fast-plate-ocr yang asli. **Ditambah saat dijalankan:** aturan cocok dipindah ke `halaman_label.cocokkan`, dipakai
  `nilai_label` dan `bahan_pembaca`, supaya keduanya tidak bisa menyimpang; penilaian ulang rantai C3 di uji sama persis dengan hasil
  Rencana 29. Lab 346 → 357, image tambahan 35, Node 120.)

## Task 2: Bahan dan pelatihan

- [x] **Step 1:** Siapkan bahan R3 dan R4. Pastikan potongan label validasi tetap 29 dan INDO-ALPR validasi 460, seperti Rencana 25.
  (Latih R3 5.339 gambar: INDO-ALPR 3.954, potongan label 96 × 5, potongan rantai 181 × 5 (C1 90, C3 91; C1 0,4 dan 0,6 serta C3 0,4 dan
  0,6 kembar semua); R4 5.915 (+576 geser). Validasi 79: label 29, rantai C1 25, rantai C3 25.)
- [x] **Step 2:** Latih R3 lalu R4 di latar (penjaga memori GPU, satu job pada satu waktu). (R3 43,7 menit, zaman terbaik 21; R4 46,7 menit,
  zaman terbaik 16; bobot termuat 192/192.)

## Task 3: Memilih dan mengukur

- [x] **Step 1:** R0, R3, R4 dinilai di `validasi-rantai` (C1 0,25 dan C3 0,6), potongan label validasi, dan INDO-ALPR validasi; R0 harus
  sama dengan Rencana 25 (19 dari 29 potongan label, 388 dari 460 INDO-ALPR). Pilih menurut aturan; commit sebelum uji dibuka.
  **R4 terpilih:** rantai C1 0,25 22 dari 29 (R3 21, R0 20); potongan label 24 (R3 24, R0 19); INDO-ALPR 380 (R3 384, R0 388; turun 8,
  di dalam batas 10). Rantai C3 0,6 19 untuk ketiganya, jadi pencari tetap C1 0,25. R0 sama dengan Rencana 25.
  `bukti/2026-10-19-pembaca-potongan-pencari-pilih.json`.
- [x] **Step 2:** Bila calon baru terpilih: `onnx_fpo.py buat`, lalu rantai utuh di tangkapan uji sekali, potongan label uji, INDO-ALPR uji,
  dan perpindahan per plat. (ONNX R4 sama dengan Keras 79/79 validasi dan 34/34 potongan uji. Rantai 21 → 22 dari 34, 0 benar → salah;
  potongan label 24 → 26; INDO-ALPR adil 496/49/166/17 → 496/50/161/17. R0 diukur ulang dan sama dengan Rencana 25.)

## Task 4: Laporan, lalu BERHENTI

- [x] **Step 1:** `bukti/2026-10-19-pembaca-potongan-pencari.md` dan `.json`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh, lalu commit.
- [ ] **Step 2: BERHENTI untuk owner.**

**Batas:**
- validasi tangkapan hanya 29 plat, dan uji 34;
- pencari C1 dan C3 dilatih dengan gambar tangkapan sisi latih, jadi kotaknya di sisi latih lebih pas daripada di gambar baru: potongan
  rantai di bahan latih meniru kotak yang kurang pas lebih lemah daripada di uji (karena itu calon R4 ditambah potongan geser);
- tangkapan layar owner, bukan rekaman gerbang; sebagian besar diambil dari samping (pengamatan owner, 19 Okt).
