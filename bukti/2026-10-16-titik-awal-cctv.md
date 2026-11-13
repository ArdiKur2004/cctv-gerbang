# Titik awal Fase 1: rantai yang sekarang di set uji video CCTV

> Rencana 17 Fase 1, dijalankan 16 Okt 2026 secara mandiri (K37), dengan dua lembar yang diperiksa owner (K19). Mesin yang dinilai:
> **mesin belajar** YOLOX-Nano-640 + fpo-indo-1 (`RISET-SAJA`). Tolak ukurnya **set uji video CCTV daring** (K36), yaitu 41 video
> sisi uji `data-asal/pembagian-video-fase1.json`.
> Sumber angka: [`2026-10-16-titik-awal-cctv-ringkasan.json`](2026-10-16-titik-awal-cctv-ringkasan.json),
> [`2026-10-16-titik-awal-cctv-nilai-kedatangan.json`](2026-10-16-titik-awal-cctv-nilai-kedatangan.json), dan
> [`2026-10-16-titik-awal-cctv-nilai-bingkai.json`](2026-10-16-titik-awal-cctv-nilai-bingkai.json). Isinya hitungan saja, dan
> diperiksa tidak memuat satu pun dari 10.605 teks plat dan nama berkas. Kontrol positifnya menemukan 868 dari minimal 866.

## 1. Rantai di 41 video uji

48.068 gambar sampel, **416 kedatangan (41 yakin, 375 ragu)**, dan 697 jalur yang hanya terlihat sekali.

## 2. Lembar kedatangan (owner, 120 dari 416)

| Jawaban owner | Baris | Di antaranya "yakin" |
|---|---|---|
| **Bukan plat** | **105** | 11 |
| Plat tak terbaca | 11 | 1 |
| Plat dinilai | 4 | 2 |

- **Dari 4 plat yang dinilai:** 2 benar dan yakin, 2 benar tetapi ragu, dan tidak ada yang salah.
- **Dari 14 kedatangan "yakin" di lembar, 11 adalah benda bukan plat.** Polanya sama dengan Rencana 14 (7 dari 10).

## 3. Lembar bingkai (owner, satu bingkai per video uji)

- **41 bingkai:** 31 tidak dinilai, karena buram, terlalu jauh, atau videonya tidak relevan menurut owner. Tersisa 10 yang
  dinilai.
- **4 dari 10 bingkai yang dinilai memuat plat terbaca yang tidak berkotak (terlewat).** Itu terjadi di gerbang siang, parkiran
  campuran (2), dan kamera diam lain.
- **Catatan owner per bingkai:**
  - kotak di benda bukan plat pada 3 bingkai;
  - kotak tepat di plat pada 2 bingkai, termasuk plat motor yang jauh;
  - tanpa kendaraan atau plat pada 2 bingkai;
  - satu bingkai memperlihatkan nomor plat yang sudah ditulis oleh sistem kamera di layar. Owner menyebutnya "contoh yang bagus,
    dalam bentuk sistem".

## 4. Bacaan agen

- **Pencari plat lemah di dua sisi pada video CCTV.** Ia banyak menemukan benda yang bukan plat, dan juga melewatkan plat yang
  terbaca. Pencari ini dilatih dengan 393 foto plat-lighting yang platnya dari dekat, jadi ia belum mengenal pemandangan CCTV.
- **"Yakin" belum bisa dipercaya untuk keselamatan.** Penahan buka-salah tetap hanya daftar izin (spec 3.1).
- **Akurasi baca per kedatangan belum bisa diukur:** hanya 4 plat yang bisa dinilai. Sebabnya sebagian besar baris bukan plat,
  dan banyak video beresolusi rendah atau platnya jauh.
- **Langkah berikutnya yang paling berguna:** melatih ulang pencari plat dengan gambar CCTV sisi latih (Rencana 19).
  - Kotak plat dan kotak bukan plat dipilah owner lewat lembar.
  - Plat buatan (Rencana 18) ditempel ke gambar CCTV.
  - Hasilnya diukur lagi dengan lembar yang sama.

## 5. Batas

- **Set uji kecil untuk dinilai:** 4 plat (kedatangan) dan 10 bingkai. Semua kelompok "terlalu sedikit".
- **Lembar kedatangan memuat 120 dari 416 kedatangan.** Lembar bingkai memuat satu gambar per video, diambil di tengah video.
- **Kecepatan dari jalan ini tidak dipakai,** karena uji milik sesi lain menyala sekitar dua pertiga jalan. Angka yang bersih
  ada di Rencana 14.
- **Video daring, bukan kamera gerbang sungguhan.** Mesin `RISET-SAJA`.

## 6. Catatan pelaksanaan

- **Gerbang uji:** lab 203 → 205 → 210; uji image tambahan 19 → 21. Uji rantai Task 3 tidak sempat merah karena kodenya sudah
  selesai, jadi diganti kontrol di dalam uji.
- **Lembar bingkai dibuat ulang.** Versi pertama (4 per video, paling banyak 60, urut nama) hanya mencakup 15 dari 41 video uji.
  Versi kedua mengambil satu bingkai per video (41).
- **Hitungan status per jenis pertama salah.** PowerShell membuang argumen kosong sehingga daftar bergeser. Hitungan diulang
  dengan argumen yang benar sebelum dipakai.
- **Owner menulis dua nomor plat dan melampirkan satu potongan plat** di percakapan. Tidak ada yang disalin ke berkas mana pun.
