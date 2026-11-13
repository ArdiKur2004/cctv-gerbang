# Kotak plat dirapikan dengan pencarian kedua (Rencana 27, K54, 19 Okt 2026)

> Hitungan saja. Gambar, potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari layar
> `halaman_label.py nilai`, `data/alat-sementara/ukuran-kotak-25.mjs`, dan `banding-rantai-25.mjs`.

## Pertanyaan

Di Rencana 26, dari 4 bacaan yang rusak di tangkapan uji, dua kotak pencari C1 jauh lebih besar dari plat dan satu lebih sempit. Apakah
menjalankan pencari sekali lagi di potongan sekitar kotak pertama (`tools/lab/rapikan.py`, `--rapikan <konteks>`) membuat kotak lebih pas
dan bacaan lebih benar?

## Cara

- Rantai Rencana 25: kendaraan cadangan gambar utuh, pencari C1 ambang 0,25, pembaca fpo-indo-1 ONNX, varian potongan v0.
- Calon (ditetapkan sebelum angka dilihat, `9ff71c9`): konteks 0 (mati), 1,0 (potongan 3 kali kotak), 2,0 (5 kali kotak).
- Dipilih di sisi latih (`dibaca_benar` terbanyak; seri: konteks 0), lalu diukur sekali di sisi uji.

## Hasil

### Sisi latih (memilih)

| Konteks | Mobil (53 berteks) | Motor (72 berteks) | Jumlah | IoU median kotak terhadap label (motor / mobil) | Rasio tinggi (motor / mobil) |
|---|---|---|---|---|---|
| **0** | 45 | 40 | **85** | 0,873 / 0,908 | 1,006 / 1,008 |
| 1,0 | 43 | 39 | 82 | 0,796 / 0,840 | 0,949 / 0,965 |
| 2,0 | 45 | 35 | 80 | 0,848 / 0,900 | 0,969 / 0,995 |

**Terpilih konteks 0: rapikan tidak dipakai** (di-commit sebelum uji dibuka, `afea2cc`). Dari konteks 0 ke 1,0 di sisi latih: 3 bacaan
membaik, 5 memburuk, dan 1 plat motor tidak lagi ditemukan.

### Sisi uji (diukur sekali, konteks 0)

21 dari 34 (mobil 13, motor 8), sama dengan Rencana 25 dan 26, sesuai harapan karena jalurnya sama.

## Kenapa tidak menolong

Pencarian kedua membuat kotak **kurang pas**, bukan lebih pas: IoU terhadap label turun dan tinggi kotak menyusut ke sekitar 0,95. Saat plat
diperbesar di potongan kecil, pencari C1 memberi kotak yang lebih pendek dan memotong huruf. Pencarinya tidak konsisten antarskala, karena ia
dilatih dengan plat yang tampak kecil di gambar utuh atau potongan kendaraan, bukan plat yang memenuhi gambar.

## Kesimpulan

- Rapikan dengan pencarian kedua **tidak dipakai**. Alatnya tetap ada (`--rapikan`), bawaan 0.
- Tiga cara murah untuk memperbaiki empat bacaan yang rusak sudah dicoba, dan tidak ada yang menolong di uji: cara pakai pencari (Rencana
  25), potongan tahan geser (Rencana 26), dan pencarian kedua (Rencana 27). Masalahnya ada di ketepatan kotak pencari dan ketahanan pembaca.

## Usulan berikutnya (belum dikerjakan)

1. **Melatih pencari dengan ukuran kotak yang lebih konsisten:** kotak label tangkapan berasal dari dua sumber (kotak mesin lama dan kotak yang
   ditarik owner), sehingga batas kotak tidak seragam. Menyeragamkan cara menarik kotak lalu melatih ulang C1 bisa membuat kotaknya lebih pas.
2. **Melatih pembaca dengan potongan dari kotak pencari, bukan kotak label,** supaya pembaca terbiasa dengan kotak yang sedikit keliru.
3. **Mengukur di video uji,** tempat banyak bingkai per kedatangan digabung; kesalahan satu bingkai mungkin tertutup bingkai lain.

## Batas

- Tangkapan uji kecil (38 gambar, 34 berteks); tangkapan bukan rekaman gerbang (bukan K9).
- Gambar latih ikut melatih C1.
- Kotak label untuk plat yang ditemukan rantai lama berasal dari kotak rantai lama, jadi "pas" diukur terhadap kotak itu.
- Kecepatan tidak diukur, karena cara ini tidak dipakai (rencana Task 3 Step 2 dilewati dengan sengaja).
