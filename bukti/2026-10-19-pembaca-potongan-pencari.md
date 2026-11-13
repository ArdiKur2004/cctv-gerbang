# Pembaca dilatih lanjut dengan potongan dari rantai kita sendiri (Rencana 30, 19 Okt 2026)

> Hitungan dan pasangan satu huruf saja ("dibaca->sebenarnya"). Teks plat, potongan, dan nama berkas tidak ada di repo (`CLAUDE.md` §4).
> Angka dibaca dari layar alat dan dari `bukti/2026-10-19-pembaca-potongan-pencari.json` (dibuat `data/alat-sementara/gabung-bukti-30.mjs`
> dari berkas sumber; jumlah dan rentang Wilson 95% rantai dihitung di skrip) dan `-pilih.json`.

## Ringkasan

- **Pembaca baru R4 terpilih** menurut aturan yang ditulis sebelum angka dilihat. Di plat validasi lewat rantai bawaan, R4 membaca benar
  22 dari 29 (fpo-indo-1 20).
- **Di soal uji, naik sedikit dan tidak ada yang rusak:**
  - rantai utuh 21 → **22 dari 34** (motor 8 → 9). Per plat: 1 salah → benar, 0 benar → salah;
  - pembaca saja di potongan label uji: 24 → **26 dari 34** (motor 11 → 13; huruf salah 13 → 11).
- **INDO-ALPR uji hampir sama** (911 plat, cara hitung adil):
  - mobil-terang 496 → 496, mobil-gelap 49 → 50, motor-terang 166 → 161, motor-gelap 17 → 17;
  - turunnya 5 di motor-terang ada di dalam rentang kebetulan, tetapi dicatat sebagai tanda lupa.
- **Rantai bawaan sekarang memakai R4** (ONNX, sama dengan Keras di 79 dari 79 gambar validasi dan 34 dari 34 potongan uji), dengan pencari
  C1 ambang 0,25. R4 bertanda `BOLEH-PRODUK` (`tools/periksa-jualan.mjs`, Keras dan ONNX).
- **Kenaikannya kecil.** Rentang rantai di uji masih tumpang tindih lebar: 45–76% lawan 48–79%. Yang terbukti hanyalah R4 tidak
  merusak bacaan dan sedikit lebih baik di motor. Bahwa R4 jauh lebih baik belum terbukti.

## Apa yang diubah dari Rencana 25, dan kenapa

| | Rencana 25 (R1, R2) | Rencana 30 (R3, R4) |
|---|---|---|
| Laju belajar | 0,001 (bawaan untuk melatih dari nol) | **0,0001** |
| Validasi yang memilih zaman | INDO-ALPR 460 + potongan label 29 (94% INDO-ALPR) | **potongan tangkapan saja** (label 29 + rantai 50); INDO-ALPR terpisah, hanya penjaga |
| Bahan latih tangkapan | potongan kotak label 96 × 5 | potongan label 96 × 5 + **potongan rantai sendiri 181 × 5** (C1 90, C3 91); R4 juga **576 potongan geser** (6 per plat, isian Rencana 26) |

Potongan rantai adalah berkas `potongan/` keluaran `baca_gambar.py`, yaitu persis yang dibaca pembaca di rantai. Potongan itu dicocokkan ke
plat berlabel dengan aturan `nilai_label`, yang kini satu fungsi bersama (`halaman_label.cocokkan`). Teksnya dari label owner. Potongan C1
di ambang 0,4 dan 0,6, serta C3 di 0,4 dan 0,6, kembar semua dengan ambang 0,25, jadi dilewati.

## Pelatihan

| Calon | Gambar latih | Zaman terbaik (dari 30) | Menit | Validasi tangkapan (79) | INDO-ALPR validasi (460) |
|---|---|---|---|---|---|
| R0 (fpo-indo-1) | — | — | — | 58 | 388 |
| R3 | 5.339 | 21 | 43,7 | 64 | 384 |
| R4 | 5.915 | 16 | 46,7 | 65 | 380 |

Bobot termuat 192/192 di keduanya. Sebelum melatih, R0 diukur dan sama dengan Rencana 25 (potongan label 19 dari 29, INDO-ALPR 388 dari
460), jadi validasinya sama.

## Memilih (aturan ditulis sebelum angka dilihat; pilihan di-commit `e67cb79` sebelum uji dibuka)

| Calon | Rantai C1 0,25 (29 plat) | Rantai C3 0,6 (29 plat) | Potongan label (29) | INDO-ALPR (460) |
|---|---|---|---|---|
| R0 | 20 | 19 | 19 | 388 |
| R3 | 21 | 19 | 24 | 384 |
| **R4** | **22** | 19 | 24 | 380 (turun 8, di dalam batas 10) |

R4 tertinggi di ukuran utama. Dengan R4, rantai C3 0,6 (19) tidak lebih tinggi dari C1 0,25 (22), jadi pencari tetap C1. Plat validasi yang
tidak ditemukan rantai (4 dari 29) dihitung salah untuk semua calon.

## Diukur sekali di uji

**Rantai utuh di tangkapan uji** (kendaraan cadangan utuh, C1 ambang 0,25, varian v0; jumlah kotak sama dengan Rencana 25, 171 plat di 181
gambar, dan plat yang tidak ditemukan sama):

| | Mobil (16) | Motor (18) | Semua (34) | Rentang 95% |
|---|---|---|---|---|
| Rencana 25 (fpo-indo-1) | 13 | 8 | 21 | 45–76% |
| **Rencana 30 (R4)** | 13 | **9** | **22** | 48–79% |

Perpindahan per plat: mobil benar → benar 13, salah → salah 2, tak ditemukan 1; motor benar → benar 8, **salah → benar 1**, salah → salah 6,
tak ditemukan 3. Tidak ada benar → salah.

**Pembaca saja di potongan label uji** (sama dengan Rencana 25):

| Pembaca | Mobil (16) | Motor (18) | Semua | Huruf salah | Di pasangan mirip owner |
|---|---|---|---|---|---|
| R0 | 13 | 11 | 24 | 13 | 4 |
| **R4** | 13 | **13** | **26** | 11 | 3 |

Huruf salah R4 (dibaca->sebenarnya): Q->O 2, E->F 2, H->R, C->I, (tambahan)->E, 5->6, 3->5, D->C, M->W. "(tambahan)->E" berarti satu
huruf E di plat tidak terbaca (nama dari `ukur-pembaca-25.py`). Dibanding R0, B->D 2, A->I, A->F, dan satu M->W hilang; E->F bertambah
satu, dan muncul C->I serta satu E yang terlewat.

**INDO-ALPR uji** (`banding_pembaca.py`, 911 plat tanpa label pilihan pembaca):

| Kelompok | R0 | R4 |
|---|---|---|
| mobil-terang (625) | 496 (79,4%; 76,0–82,3%) | 496 (79,4%) |
| mobil-gelap (57) | 49 (86,0%) | 50 (87,7%) |
| motor-terang (208) | 166 (79,8%; 73,8–84,7%) | 161 (77,4%; 71,3–82,6%) |
| motor-gelap (21) | 17 | 17 |

R0 sama persis dengan Rencana 25 di ketiga ukuran uji (21, 24, dan 496/49/166/17).

## Yang dipelajari

- Dua perubahan cara melatih (laju kecil, zaman dipilih dari potongan tangkapan) membuat latihan lanjut akhirnya menolong. Di Rencana 25,
  R1 terbaik di zaman pertama dan tidak membaik. Mana dari dua perubahan itu yang berpengaruh belum dipisahkan.
- Potongan geser (R4) menambah 1 plat validasi dibanding R3. Itu terlalu kecil untuk disebut bukti.
- Pencari C3 masih kalah dari C1 walau dengan pembaca baru (19 lawan 22 di validasi). Kotak C3 yang kurang pas belum tertutup oleh pembaca.
- Sisa di rantai uji, dari 34 plat berteks: 8 dibaca salah (motor 6, mobil 2) dan 4 tidak ditemukan (motor 3, mobil 1). Menurut owner
  (K58), banyak tangkapan diambil dari samping, sehingga platnya miring.

## Batas

- Validasi hanya 29 plat, dan uji 34. Validasi yang sama dipakai untuk memilih zaman dan memilih calon, jadi angka validasi R4 cenderung
  terlalu baik. Angka uji yang jujur.
- Pencari C1 dan C3 dilatih dengan gambar tangkapan sisi latih, jadi potongan rantai di bahan latih lebih pas daripada di gambar baru.
- INDO-ALPR motor-terang turun 5 (dari 208). Bila tanda lupa ini tumbuh di latihan berikutnya, penjaganya perlu diperketat.
- Pemeriksaan ONNX sama dengan Keras kini 79 gambar validasi, ditambah 34 potongan uji. Untuk fpo-indo-1 dulu 460 gambar. Sekarang lebih
  sedikit karena `onnx_fpo.py buat` memeriksa `validasi.csv`, dan validasi INDO-ALPR pindah ke `validasi-indo.csv`. Selisih terbesar
  2,8e-06.
- Kecepatan R4 tidak diukur. Susunannya sama dengan fpo-indo-1, jadi waktunya diperkirakan sama, tetapi itu belum dibuktikan.
- Tangkapan layar owner, bukan rekaman gerbang. Rekaman HP owner (K43) belum ada.

**Cara membalik:** jalankan rantai dengan folder pembaca `data/keluaran/fpo-indo-1`, bukan `data/keluaran/pembaca-lanjut-r4`. Tidak ada kode
yang perlu diubah.
