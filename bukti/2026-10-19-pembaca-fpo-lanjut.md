# Pembaca fpo-indo-1 dilatih lanjut dengan potongan tangkapan owner (Rencana 25 Task 6, 19 Okt 2026)

> Hitungan saja. Potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari `mesin.json` calon, layar
> `data/alat-sementara/ukur-pembaca-25.py` dan `tools/lab/banding_pembaca.py`; semuanya ada di `bukti/2026-10-19-rantai-optimal.json`
> (bagian `pembaca`). Pasangan huruf ditulis "dibaca->sebenarnya", satu huruf saja.

## Calon dan bahan

Semua calon berangkat dari fpo-indo-1 (`latih_fpo.py latih-lanjut`), dengan konfigurasi model dan plat terbitan (`BOLEH-PRODUK` sejak
K47). Bobot termuat utuh 192/192 di keduanya. Bahan berwilayah dari `bahan_pembaca.py`.

| Calon | Bahan latih | Gambar latih | Zaman | Zaman terbaik | Menit |
|---|---|---|---|---|---|
| R0 | fpo-indo-1 apa adanya | — | — | — | — |
| R1 | INDO-ALPR latih inti 3.954 + potongan tangkapan latih 96 × 5 | 4.434 | 40 | 1 | 55,1 |
| R2 | R1 + 10.000 plat buatan | 14.434 | 20 | 3 | 68,2 |

Validasi sama untuk semua: INDO-ALPR 460 dan potongan tangkapan 29 (489). Laju belajar bawaan pembuatnya, 0,001.

## Memilih (aturan ditulis sebelum angka dilihat)

Benar terbanyak di potongan tangkapan validasi; bila seri, benar terbanyak di INDO-ALPR validasi. Calon yang INDO-ALPR validasinya
turun lebih dari 10 gambar dari R0 ditolak.

| Calon | Tangkapan validasi (29) | INDO-ALPR validasi (460) | Keputusan |
|---|---|---|---|
| **R0** | 19 | 388 | **terpilih** |
| R1 | 19 | 387 | seri di tangkapan, kalah 1 di INDO-ALPR |
| R2 | 22 | 376 | ditolak: INDO-ALPR turun 12 |

Angka R0 sama persis dengan Rencana 24 (`banding-pembaca-24.json`: 388 dan 19), jadi validasinya sama. Pilihan di-commit sebelum set uji
dibuka (`d4f6b4b`).

**Kenapa latihan lanjut tidak menolong (bacaan agen, dari `training_log.csv`):** di R1, ketepatan latih naik dari 0,80 ke 0,90, tetapi
`val_plate_acc` tetap 0,80–0,83 dan tertinggi di zaman pertama. Mesin menghafal bahan latih tanpa membaik di validasi. Dua sebab yang
mungkin, belum dibuktikan:
- laju belajar 0,001 adalah bawaan untuk melatih dari nol, terlalu besar untuk melatih lanjut;
- zaman dipilih dengan `val_plate_acc` gabungan, yang 94% isinya INDO-ALPR, jadi kemajuan di tangkapan tidak terlihat.

## Diukur sekali di uji

R1 dan R2 ikut diukur hanya sebagai informasi; pilihan sudah tetap.

### INDO-ALPR uji, cara hitung adil (911 plat tanpa label pilihan pembaca)

| Kelompok | R0 (fpo-indo-1) | R1 | R2 | P3 (dari nol, Rencana 24) |
|---|---|---|---|---|
| mobil-terang (625) | 496 (79,4%; 76,0–82,3%) | 499 (79,8%) | 485 (77,6%) | 414 (66,2%) |
| mobil-gelap (57) | 49 (86,0%; 74,7–92,7%) | 49 (86,0%) | 50 (87,7%) | 39 (68,4%) |
| motor-terang (208) | 166 (79,8%; 73,8–84,7%) | 165 (79,3%) | 159 (76,4%) | 123 (59,1%) |
| motor-gelap (21) | 17 (terlalu sedikit) | 17 | 16 | 14 |

R0 sama persis dengan angka fpo-indo-1 di Rencana 10 (79,4%, 86,0%, 79,8%).

### Potongan tangkapan uji (dari kotak label, 34 plat berteks)

| Pembaca | Mobil (16) | Motor (18) | Semua | Huruf salah | Di pasangan mirip owner |
|---|---|---|---|---|---|
| **R0** | 13 | 11 | **24** | 13 | 4 (Q->O 2, M->W 2) |
| R1 | 13 | 11 | 24 | 13 | 4 |
| R2 | 14 | 11 | 25 | 13 | 3 |
| P3 | 12 | 7 | 19 | 30 | 2 |

Huruf salah R0 di tangkapan uji (dibaca->sebenarnya): Q->O 2, M->W 2, B->D 2, H->R, A->I, 5->6, 3->5, D->C, A->F, E->F. Huruf bulat
(O, B, D) dan pasangan owner masih menjadi kesalahan terbanyak, sama dengan pola Rencana 24.

## Kesimpulan

- Pembaca jualan tetap **fpo-indo-1** (sudah ONNX sejak Rencana 11; `BOLEH-PRODUK` sejak K47). Tidak ada mesin pembaca baru yang dipakai.
- Melatih lanjut dengan potongan tangkapan, dengan cara ini, tidak menaikkan bacaan. R2 sedikit lebih baik di tangkapan (25 lawan 24)
  tetapi lupa sebagian INDO-ALPR.
- P3 (dari nol) tetap jauh di belakang: 19 lawan 24 di tangkapan uji, 66% lawan 79% di mobil-terang.

## Batas

- Validasi tangkapan hanya 29 potongan dan uji 34; selisih 1–3 potongan tidak bermakna.
- Potongan tangkapan diambil dari kotak label, bukan dari pencari; di rantai, kotak pencari bergeser sedikit dan bacaan bisa berubah
  (lihat `bukti/2026-10-19-rantai-optimal.md`).
- Hanya satu laju belajar yang dicoba; dua sebab di atas belum dibuktikan.
