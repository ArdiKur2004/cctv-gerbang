# Pembaca tahan geser (Rencana 26, K51, 19 Okt 2026)

> Hitungan saja. Gambar, potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari layar
> `halaman_label.py nilai`, `data/alat-sementara/cepat-geser-26.py`, `banding-rantai-25.mjs`, dan `geometri-pindah-26.mjs`; hitungannya di
> `bukti/2026-10-19-pembaca-tahan-geser.json`.

## Pertanyaan

Di Rencana 25, di tangkapan uji, 4 plat yang dulu dibaca benar menjadi salah dengan pembaca yang sama (fpo-indo-1), karena kotak pencari
baru (C1) berbeda dari kotak lama. Apakah membaca beberapa potongan yang sedikit diperlebar atau digeser, lalu memungut suara, memulihkan
bacaan itu?

## Cara

- Rantai Rencana 25: kendaraan dengan cadangan gambar utuh, pencari C1 ambang 0,25, pembaca fpo-indo-1 ONNX.
- Varian potongan (`tools/lab/tahan_geser.py`, ditetapkan sebelum angka dilihat):
  - v0 = cara lama, 1 potongan;
  - v1 = 3 potongan (margin 0,05; 0; 0,12);
  - v2 = 7 potongan (v1 ditambah geser ±6% lebar dan ±10% tinggi).
- Pungut suara: hanya bacaan yang sesuai pola plat; terbanyak menang.
- Dipilih di sisi latih (`dibaca_benar` terbanyak; seri: potongan lebih sedikit), lalu diukur sekali di sisi uji.

## Hasil

### Sisi latih (memilih)

| Varian | Mobil (53 berteks) | Motor (72 berteks) | Jumlah | Plat ditemukan |
|---|---|---|---|---|
| v0 | 45 | 40 | 85 (sama dengan Rencana 25) | 54 / 75 |
| v1 | 46 | 42 | 88 | 54 / 75 |
| **v2** | 46 | 43 | **89** | 54 / 75 |

Terpilih v2 (di-commit sebelum sisi uji dibuka, `de4af2c`). Di sisi latih, dibanding v0, v2 memperbaiki 8 bacaan (mobil 1, motor 7) dan
merusak 4 (motor).

### Sisi uji (diukur sekali)

| | Rencana 25 (v0) | v2 |
|---|---|---|
| Mobil, dibaca benar dari 16 | 13 | 13 |
| Motor, dibaca benar dari 18 | 8 | 8 |
| **Semua, dari 34** | **21** | **21** |

Tidak ada satu plat pun yang berubah status antara Rencana 25 dan v2. Keempat plat yang berubah dari benar ke salah di Rencana 25 tetap
salah.

### Kenapa keempat plat itu tidak pulih (geometri kotak C1 terhadap kotak label)

| Plat | IoU | Rasio lebar | Rasio tinggi | Geser tengah (lebar, tinggi) |
|---|---|---|---|---|
| mobil | 0,79 | 0,88 | 0,94 | +0,03, −0,05 |
| motor | 0,74 | 1,15 | 1,15 | +0,09, −0,03 |
| motor | 0,55 | 1,48 | 1,23 | +0,20, +0,02 |
| motor | 0,89 | 0,98 | 0,97 | +0,04, −0,01 |

- Dua kotak motor **jauh lebih besar** dari kotak label (sampai 1,48 kali lebarnya). Varian v2 hanya memperlebar, paling banyak 12%, dan tidak
  pernah mempersempit, jadi tidak menjangkaunya.
- Satu kotak mobil sedikit **lebih sempit** (0,88 lebarnya), dan v2 tidak punya potongan yang lebih lebar ke sisi yang terpotong.
- Satu kotak motor hampir sama (IoU 0,89), tetapi bacaannya salah di semua potongan. Pembaca memang ragu pada plat itu, berapa pun geserannya.

Jadi dugaan Rencana 25 ("pergeseran kecil") hanya sebagian benar: yang lebih menentukan adalah **ukuran** kotak yang keliru (terlalu besar
atau terlalu kecil), ditambah plat yang memang sulit dibaca.

### Kecepatan (CPU laptop, 2 utas, 60 plat sisi latih, median dari 3 putaran bergiliran)

| Varian | Milidetik per plat | Kali v0 |
|---|---|---|
| v0 | 16,9 | 1 |
| v1 | 50,3 | 3,0 |
| v2 | 110,8 | 6,5 |

Mesin sebelum pengukuran: beban CPU 4%, tanpa kontainer lab lain, tanpa uji sesi lain. Putaran ke putaran berselisih (v0 13–17 ms, v2 94–131
ms). Di Mini PC, satu panggilan pembaca dengan 2 utas sekitar 100 ms, lawan 14,3 ms di laptop (Rencana 11 dan 12), kira-kira 7 kali lebih
lambat; jadi v2 bisa sekitar 0,8 detik per plat di Mini PC. Ini taksiran, bukan ukuran.

## Kesimpulan

- **Di uji, pembaca tahan geser tidak menaikkan bacaan (21 → 21)**, walau di latih naik 85 → 89. Biayanya 6,5 kali waktu baca.
- **Tidak dijadikan bawaan.** Bawaan alat tetap v0; v1 dan v2 tersedia lewat `--varian-potong`. Alasannya sama dengan saringan letak di
  Rencana 21: terpilih di sisi latih, tetapi tidak menolong di uji.
- Sasaran yang lebih tepat untuk empat plat itu adalah **kotak plat yang lebih pas**, bukan potongan yang digeser.

## Usulan berikutnya (belum dikerjakan)

1. **Kotak plat dirapikan dengan pencarian kedua:** pencari plat dijalankan sekali lagi di potongan kecil sekitar kotak pertama, supaya
   kotak yang terlalu besar menyempit dan yang terlalu kecil melebar. Ini menyasar tiga dari empat plat.
2. **Di video, bacaan beberapa bingkai digabung** (rantai sudah memungut suara per kedatangan). Tahan geser mungkin tidak perlu di sana;
   itu bisa diukur di video uji (pilihan C sebelumnya).
3. Plat yang memang sulit dibaca menjadi bahan latih pembaca berikutnya.

## Batas

- Tangkapan uji kecil (38 gambar, 34 berteks); hasil "sama persis" di uji tidak membuktikan v2 tidak berguna di tempat lain.
- Gambar latih ikut melatih C1, jadi kotak di sisi latih lebih pas daripada di uji; manfaat v2 di latih bisa berbeda di uji.
- Kecepatan diukur di laptop yang juga dipakai sesi lain; angkanya berselisih antarputaran.
- Tangkapan bukan rekaman gerbang (bukan K9).
