# fpo-indo-1 dalam format ONNX dan kecepatannya di CPU

> Rencana 11 Fase 0A, dijalankan 15 Okt 2026 atas lampu hijau owner ("A").
> **Taksiran kecepatan dari CPU mesin ini, bukan angka server IBE (P16) dan bukan angka produk.** Tanda mesin `RISET-SAJA`
> sampai izin tertulis pembuat fast-plate-ocr datang (K26, K27).
> Sumber angka: [`2026-10-15-fpo-indo-1-onnx.json`](2026-10-15-fpo-indo-1-onnx.json) (manifes ONNX dan pemeriksaan
> kesamaan), [`2026-10-15-baca-fpo-indo-1-onnx.json`](2026-10-15-baca-fpo-indo-1-onnx.json), dan
> [`2026-10-15-cepat-fpo-indo-1.json`](2026-10-15-cepat-fpo-indo-1.json) di folder ini. Isinya hitungan saja. Sebelum
> disalin ke sini, ketiganya diperiksa tidak memuat satu pun dari 9.739 teks plat dan nama berkas. Pemeriksanya diuji dulu
> pada bacaan mesin, dan menemukan 2.379 di antaranya.

## 1. Caranya: menukar bobot, bukan mengekspor ulang

Ekspor ONNX bawaan gagal di Keras + torch (Rencana 10). Tetapi ONNX terbitan `cct_s_v2_global` punya susunan yang sama persis
dengan fpo-indo-1; yang berbeda hanya angka bobotnya. Jadi:

1. **Pemetaan dicari dari pasangan terbitan** (`.keras` dan `.onnx` dari rilis yang sama), dengan mencocokkan nilainya. Ke-192
   tensor bobot masing-masing cocok dengan tepat satu initializer ONNX, satu-satu: 147 sama, 40 berbentuk lain, 5 kernel
   konvolusi dengan sumbu disusun ulang. Yang tidak disentuh: kernel pemotong petak (bukan bobot latih) dan 8 konstanta
   bentuk.
2. **Pemeriksaan tukar-diri:** menukar dengan bobot terbitan sendiri harus tidak mengubah ONNX terbitan sedikit pun.
3. **Bobot fpo-indo-1 dipasang** dengan cara yang sama.
4. **Disimpan hanya bila sama:** bacaannya harus sama dengan Keras pada semua gambar validasi, dengan selisih terbesar di
   bawah 1e-4.

Tidak ada paket baru dan tidak ada image baru.

## 2. Kesamaan dengan Keras

| Pemeriksaan | Hasil |
|---|---|
| Gambar validasi (sisi latih), semua slot huruf sama | **460 dari 460** |
| Selisih terbesar peluang huruf, ONNX vs Keras | 1,30e-5 (batas 1e-4) |
| Set uji, bacaan per gambar ONNX vs Keras | **1.422 gambar, beda 0** |
| Angka set uji per kelompok | Sama persis dengan Rencana 10: mobil-terang 506/638, mobil-gelap 51/59, motor-terang 173/219, motor-gelap 17/21 |

Set uji dibaca ulang hanya untuk membuktikan kesamaan. Tidak ada pilihan yang diambil dari angka ini.

## 3. Kecepatan di CPU

AMD Ryzen 7 8700F (8 inti, 16 utas); container lab melihat 12 CPU. 460 gambar validasi, 10 pertama untuk pemanasan, diukur saat
mesin tenang (hanya satu container lain yang diam, GPU 4%, beban CPU 17%). Pembacanya `LicensePlateRecognizer` dengan ONNX
Runtime di CPU, sama dengan pembaca fast-plate-ocr terbitan.

| Utas | Praproses + model + pascaproses, median | p95 | Model saja, median | Dekode berkas gambar, median |
|---|---|---|---|---|
| 1 | 23,3 ms | 41,5 ms | 22,9 ms | 9,3 ms |
| 2 | 14,3 ms | 28,3 ms | 14,0 ms | 8,5 ms |
| 4 | 10,4 ms | 14,1 ms | 10,1 ms | 8,7 ms |

Pembanding: fast-plate-ocr terbitan 11 ms per gambar di CPU (utas bawaan, Rencana 6). fpo-indo-1 dengan utas bawaan juga
11 ms, wajar karena susunannya sama. Lewat Keras di kartu grafis 44 ms (Rencana 10).

**Taksiran kasar (bacaan agen):** dengan satu inti, membaca satu potongan plat butuh sekitar 33 ms termasuk dekode, atau
kira-kira **30 potongan plat per detik per inti**. Ini hanya langkah baca huruf. Mencari plat di foto utuh (Rencana 12),
unggah foto ke server, dan pencocokan dengan daftar pengguna belum dihitung. Mencari plat kemungkinan lebih berat daripada
membaca hurufnya.

## 4. Batas, apa adanya

- **CPU mesin ini, bukan server IBE.** Spesifikasi server belum diketahui (P16).
- **Hanya baca huruf dari potongan plat.** Kecepatan rantai utuh (unggah, mencari plat, membaca, mencocokkan, membalas) belum
  bisa ditaksir.
- **Satu gambar per panggilan.** Membaca beberapa plat sekaligus bisa lebih cepat per plat; itu belum diukur.
- **Mesin dipakai bersama:** p95 pada 1 utas (41,5 ms) jauh di atas median, kemungkinan karena gangguan dari proses lain.
- **Tanda `RISET-SAJA`** dan izin tertulis belum ada (K27).

## 5. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 107; lab 161 → 167 → 170; uji image tambahan 9 → 12. Tiap uji baru terlihat merah dulu.
- **Satu cacat tertangkap oleh pengamannya sendiri.** Pada run pertama, pemeriksaan tukar-diri menolak: 19 alpha DyT yang di
  ONNX terbitan berbentuk skalar `()` menjadi `(1,)`. Keluaran ONNX tidak berubah, dan uji fungsional dua arah tetap lulus,
  jadi cacat ini akan lolos tanpa pemeriksaan tukar-diri. Sebabnya diukur dengan skrip sekali pakai:
  `np.ascontiguousarray` mengubah skalar menjadi larik satu dimensi, dan pemeriksaan bentuk terjadi sebelum langkah itu. Uji
  skalar ditambahkan (merah dulu), lalu diperbaiki. Tukar-diri kini 0 beda.
- **Menyimpang dari rencana:**
  - satu uji tambahan (lab 170, bukan 169);
  - nama berkas bukti bertanggal 2026-10-15, bukan 2026-10-16, karena dijalankan pada tanggal itu.

## 6. Berikutnya

- **Rencana 12:** mencari plat di foto utuh dan video riset. Calon pencari plat, izinnya, bahan berkotak, dan kecepatannya,
  supaya rantai foto → plat → huruf utuh.
- **Rencana 13:** laporan Fase 0A untuk keputusan owner, termasuk taksiran biaya server bila P16 sudah dijawab.
