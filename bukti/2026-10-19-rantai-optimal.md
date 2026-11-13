# Rantai jualan yang dioptimalkan dengan data owner (Rencana 25, K50, 19 Okt 2026)

> Hitungan saja. Gambar, potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Semua angka dibaca dari layar alat dan
> dari `bukti/2026-10-19-rantai-optimal.json`. Rincian bagian plat ada di `bukti/2026-10-19-pencari-cctv2.md`, dan bagian baca di
> `bukti/2026-10-19-pembaca-fpo-lanjut.md`.

## Ringkasan per bagian ("tiga petugas gerbang")

| Bagian | Sebelum | Sesudah | Dipilih dengan | Hasil |
|---|---|---|---|---|
| **Kendaraan** (YOLOX COCO) | kendaraan dicari, plat hanya di dalam kendaraan | ditambah **cadangan gambar utuh** bila tidak ada kendaraan setinggi 40 piksel | sisi latih tangkapan, `dibaca_benar` | 78 → 79 di sisi latih |
| **Plat** (cctv1) | cctv1 | **C1**: cctv1 dilatih lanjut dengan cctv-fase1 + tangkapan latih | F1 di validasi gabungan | F1 0,897 → 0,926; tangkapan uji (gambar utuh) 16 → 35 dari 39 plat |
| **Baca** (fpo-indo-1) | fpo-indo-1 | **tetap fpo-indo-1** | benar di potongan tangkapan validasi | R1 seri, R2 ditolak (lupa INDO-ALPR) |

Semua mesin di rantai baru `BOLEH-PRODUK` menurut `tools/periksa-jualan.mjs` (K47–K49).

## Kendaraan: dua modifikasi cara pakai (Task 2)

Dinilai di sisi latih tangkapan (140 gambar), dengan pencari dan pembaca lama, menurut aturan yang ditulis sebelum angka dilihat.

| Cara | Plat ditemukan (mobil / motor) | Dibaca benar (mobil / motor) | Jumlah | Kotak di luar label |
|---|---|---|---|---|
| sekarang | 51 / 59 | 43 / 35 | 78 | 6 |
| **cadangan gambar utuh** | 51 / 62 | 43 / 36 | **79** | 6 |
| terdekat 1 (K45 sebagai batas) | 43 / 52 | 38 / 34 | 72 | 3 |
| cadangan + terdekat 1 | 43 / 55 | 38 / 35 | 73 | 3 |

- **Terdekat 1 merugikan:** 8 plat mobil dan 7 plat motor yang tadinya ditemukan hilang. Ke-8 plat mobil itu ada di gambar yang hanya punya
  satu plat berlabel. Jadi di 8 dari 58 gambar mobil, plat yang terbaca owner tidak berada di kendaraan dengan tepi bawah terendah menurut
  kotak pencari. **Akibat untuk produk:** K45 dipakai sebagai urutan (baca kendaraan terdekat dulu, lalu lanjut ke kendaraan berikutnya bila
  tidak ada plat terbaca), bukan batas satu kendaraan.
- **Pencari kendaraan belum perlu dilatih ulang:** hanya 4 gambar motor latih yang tidak punya kendaraan sama sekali, dan cadangan gambar
  utuh menemukan plat di 3 di antaranya. Di sisi uji tidak ada gambar seperti itu. Plat motor yang masih terlewat hampir semuanya ada di
  kendaraan yang sudah terlihat; penghambatnya pencari plat.

## Rantai utuh di tangkapan (Task 7)

Rantai baru: kendaraan cara cadangan gambar utuh, pencari C1 (ONNX), pembaca fpo-indo-1 (ONNX). Ambang pencari dipilih di sisi latih dari
{0,25; 0,4; 0,6} menurut aturan yang di-commit sebelum rantai dijalankan (`2bf523a`): dibaca benar 85, 84, 81. **Terpilih 0,25**, sama
dengan titik awal. Sisi uji dinilai sekali, hanya untuk ambang terpilih.

| Sisi | Kelompok | Plat ditemukan: awal → baru | Dibaca benar (dari yang berteks): awal → baru | Rentang 95% baru | Kotak di luar label: awal → baru |
|---|---|---|---|---|---|
| latih | mobil (58 plat, 53 berteks) | 51 → 54 | 43 → 45 | | 3 → 1 |
| latih | motor (83 plat, 72 berteks) | 59 → 75 | 35 → 40 | | 3 → 5 |
| latih | semua | 110 → 129 | 78 → 85 | 0,594–0,755 | 6 → 6 |
| **uji** | mobil (16 plat, 16 berteks) | 14 → 15 | 12 → 13 | 0,570–0,934 | 0 → 0 |
| **uji** | motor (23 plat, 18 berteks) | 14 → 19 | 9 → 8 | 0,246–0,663 | 0 → 1 |
| **uji** | **semua** | **28 → 34** (0,733–0,944) | **21 → 21** (0,450–0,761) | | 0 → 1 |

Perpindahan per plat berteks di sisi uji (`banding-rantai-25.mjs`, cocok dengan hitungan alat resmi):

| Kelompok | Benar → benar | Benar → salah | Salah → benar | Tak ditemukan → benar | Tak ditemukan → salah | Tetap tak ditemukan |
|---|---|---|---|---|---|---|
| mobil | 11 | 1 | 1 | 1 | 0 | 1 |
| motor | 6 | **3** | 0 | 2 | 2 | 3 |

- **Plat yang ditemukan naik jelas:** di uji 28 → 34 dari 39, di latih 110 → 129 dari 141. Motor paling banyak naik (uji 14 → 19).
- **Bacaan benar di uji tidak naik (21 → 21):** 4 plat yang dulu terlewat kini terbaca benar, tetapi 4 plat yang dulu benar kini salah,
  padahal pembacanya sama. Kotak C1 rata-rata seukuran kotak label (median rasio lebar dan tinggi 0,98–1,08), tetapi bergeser: IoU
  median 0,84 (motor) dan 0,88 (mobil), sedangkan kotak lama 0,98 (label dibuat dari kotak lama). **Pembaca peka terhadap pergeseran kecil
  potongan.**
- Motor tetap terlemah: di uji 19 dari 23 plat ditemukan, tetapi hanya 8 dari 18 yang berteks dibaca benar.

## Usulan berikutnya (belum dikerjakan; aturan memilih ditulis dulu bila dijalankan)

1. **Pembaca tahan geser:** baca beberapa potongan yang sedikit digeser atau diperlebar lalu pungut suara, atau latih pembaca dengan potongan
   yang digeser. Ini sasaran langsung dari 4 plat benar → salah.
2. **Latih lanjut pembaca dengan laju lebih kecil** dan zaman dipilih dari validasi tangkapan, bukan validasi gabungan.
3. **Lembar video uji untuk baris yang berubah saja** (rantai baru di 77 video uji), supaya label yang sudah dikunci dipakai ulang.
4. **Uji dengan rekaman HP owner dan CCTV kantor** (K43), karena tangkapan bukan rekaman gerbang.
5. Melatih ulang pencari kendaraan **tidak** diusulkan sekarang (lihat bagian kendaraan).

## Batas

- **Bahan uji kecil:** 38 gambar, 39 plat, 34 berteks. Rentang 95% lama dan baru tumpang tindih di semua baris uji; "naik" di sini hanya
  pasti untuk plat yang ditemukan.
- **Kotak label** untuk plat yang ditemukan rantai lama berasal dari kotak rantai lama. Bias ini menguntungkan titik awal (IoU 0,98).
- **Tangkapan bukan rekaman gerbang:** diambil owner saat platnya terlihat. Angka ini tidak boleh dibaca sebagai K9.
- **Sisi latih bukan ukuran adil untuk rantai baru:** gambar latih ikut melatih C1. Pilihan ambang 0,25 di sisi latih bisa condong ke ambang
  rendah (dicatat di aturan).
- Plat lain di gambar tangkapan yang tidak dilabeli muncul sebagai "kotak di luar label".
- Kecepatan rantai baru (cadangan gambar utuh menambah satu pencarian di gambar tanpa kendaraan) tidak diukur.
- Rantai baru belum dijalankan di video uji.
