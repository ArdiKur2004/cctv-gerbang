# Bukan plat di dalam kendaraan: saringan letak plat dan tampak depan/belakang (K39 langkah 2)

> Rencana 21 Fase 1, dijalankan 17 Okt 2026 secara mandiri (K37), dengan tiga lembar yang diperiksa owner (K19): satu lembar latih
> dan dua lembar uji. Mesin yang dinilai adalah **mesin belajar** (`RISET-SAJA`):
> - pencari plat yang dilatih ulang (Rencana 19);
> - pencari kendaraan YOLOX-Tiny COCO, cara potong (Rencana 20);
> - pembaca fpo-indo-1.
>
> Tolak ukurnya **set uji video CCTV daring** (K36): 41 video sisi uji, dengan 41 bingkai yang sama dengan Rencana 17, 19, dan 20.
>
> Sumber angka:
> - [`-banding-letak.json`](2026-10-17-bukan-plat-di-dalam-kendaraan-banding-letak.json)
> - [`-ringkasan.json`](2026-10-17-bukan-plat-di-dalam-kendaraan-ringkasan.json)
> - [`-nilai-kedatangan.json`](2026-10-17-bukan-plat-di-dalam-kendaraan-nilai-kedatangan.json)
> - [`-nilai-bingkai.json`](2026-10-17-bukan-plat-di-dalam-kendaraan-nilai-bingkai.json)
> - [`-nilai-bingkai-ketat.json`](2026-10-17-bukan-plat-di-dalam-kendaraan-nilai-bingkai-ketat.json)
>
> Semua berkas di atas berawalan `2026-10-17-bukan-plat-di-dalam-kendaraan`. Isinya hitungan saja, dan sudah diperiksa tidak memuat
> satu pun dari 11.431 teks plat, nama berkas, dan nama video. Kontrol positifnya menemukan 1.697 dari minimal 1.692.

## Ringkasan untuk owner

- **Saringan letak tidak menolong secara keseluruhan, jadi tidak dijadikan bawaan.**
  - Bukan plat di lembar kedatangan: 52 dari 120 (R20: 46).
  - Plat terlewat di bingkai: 11 dari 12 (R20: 7 dari 10).
  - Bingkai 12 dan 38, yang ditemukan di R20, kini terlewat.
- **Di video gerbang hasilnya bersih:** 12 kedatangan "yakin" benar, 0 bukan plat, 0 salah.
- **Semua 26 "yakin" yang bukan plat berasal dari hanya 2 video:** 20 dari satu video parkiran dan 6 dari satu video kamera diam
  lain. Di kedua video itu, benda yang sama terbaca berulang dengan teks yang sama sebagai banyak "kedatangan".
- **Jumlah plat yang bisa dinilai tetap kecil** (18 di lembar). Owner menyarankan menambah video dari internet atau YouTube.

## 1. Pemilihan aturan di sisi latih

Rantai cara potong di 39 video latih menghasilkan 100 kedatangan. Owner menandai 25 bukan plat, 7 di antaranya "yakin". Plat 75,
termasuk 22 yang buram dan 1 yang salah baca.

| Aturan | Plat lolos (dari 75) | Bukan plat lolos (dari 25) | Bukan plat "yakin" lolos (dari 7) |
|---|---|---|---|
| tanpa | 75 | 25 | 7 |
| tampak | 72 | 19 | 5 |
| rx0.3 | 74 | 18 | 5 |
| **ry0.4_rx0.3_tampak (terpilih)** | **69** | **13** | **4** |
| ry0.6_rx0.3_tampak (gugur, di bawah 90% plat) | 63 | 10 | 4 |

Tabel 24 aturan ada di rencana dan di `-banding-letak.json`.
- **Aturan memilih ditulis sebelum label dilihat:** minimal 90% plat lolos, lalu bukan plat tersedikit, lalu syarat tersedikit.
- **Di sisi latih saringan sudah terlihat sedang:** ia membuang 12 dari 25 bukan plat, dengan ongkos 6 dari 75 plat.

## 2. Rantai di 41 video uji

| | Titik awal (R17) | R19 | R20 (potong) | **R21 (potong + letak)** |
|---|---|---|---|---|
| Kedatangan (yakin) | 416 (41) | 198 (22) | 425 (91) | **291 (84)** |
| Kotak dibuang aturan letak | – | – | – | 3.546 |

## 3. Lembar kedatangan (owner, 120 dari 291)

| Jawaban owner | Titik awal | R19 | R20 | **R21** |
|---|---|---|---|---|
| Bukan plat | 105 | 6 | 46 | **52** |
| Plat tak terbaca | 11 | 91 | 55 | 50 |
| Plat dinilai | 4 | 23 | 19 | 18 |
| Benar-yakin / benar-ragu / salah-ragu / salah-yakin | 2 / 2 / 0 / 0 | 14 / 6 / 1 / 2 | 14 / 4 / 0 / 1 | **16 / 1 / 1 / 0** |
| "Yakin" yang bukan plat | 11 dari 14 | 1 dari 19 | 18 dari 43 | **26 dari 52** |

**Menurut sudut kamera (R21):**

| Sudut | Benar (yakin) | Bukan plat (yakin) | Tak terbaca (yakin) | Salah (yakin) |
|---|---|---|---|---|
| Gerbang | 12 (12) | 9 (0) | 27 (4) | 1 (0) |
| Kamera diam lain | 4 (3) | 23 (6) | 1 (0) | 0 |
| Parkiran | 1 (1) | 20 (20) | 22 (6) | 0 |

- **Asal "yakin" yang bukan plat** (hitungan dari `diam-parkiran-21.py`):
  - parkiran: 20 baris, semuanya dari 1 video;
  - kamera diam lain: 6 baris, dari 1 video;
  - 23 dari 26 baris itu punya kedatangan lain dengan teks gabungan yang persis sama di video yang sama.
  - **Pembanding:** baris "yakin" lainnya juga sering punya kembar teks (21 dari 26), karena kendaraan yang menunggu juga terbaca
    berulang. Jadi teks berulang saja bukan pembeda.
- **Cara menghitung:**
  - Baris yang tidak disebut owner dihitung benar (17 baris).
  - 14 baris disebut motor; 13 di antaranya tak terbaca.

## 4. Lembar bingkai (owner, 41 bingkai yang sama)

| Hitungan | Titik awal | R19 | R20 | **R21** |
|---|---|---|---|---|
| Owner, plat buram ikut dihitung: ada plat terlewat / dinilai | 4 / 10 | 12 / 13 | 7 / 10 | **11 / 12** |
| Ketat, hanya plat terbaca: ada plat terlewat / dinilai | – | 3 / 4 | 2 / 5 | **1 / 2** |

- **Ditemukan:** bingkai 17.
- **Terlewat, plat terbaca:** bingkai 12. Plat ini ditemukan di R20.
- **Terlewat, plat buram:** 2, 3, 5, 6, 13, 15, 19, 26, 38, 41. Bingkai 38 ditemukan di R19 dan R20.
- **Catatan owner:** bingkai lain berisi kendaraan yang platnya tak terbaca, atau terlalu buram, atau terlalu jauh.

## 5. Bacaan agen

- **Saringan letak membuang plat sungguhan** (bingkai 12 dan 38) dan tidak mengurangi benda bukan plat di lembar uji. Ia tidak
  dijadikan bawaan. Cara terbaik sejauh ini tetap Rencana 20 (potong, tanpa letak), dengan kelemahan benda bukan plat di dua video.
- **Masalah "yakin" yang bukan plat terpusat di dua adegan**, tempat benda yang sama terbaca berulang. Ini bukan soal letak, tetapi
  soal benda yang tetap berada di tempatnya. Pembeda yang mungkin:
  - isi potongan (pemilah plat dan bukan plat yang dilatih dari label owner sisi latih: 106 + 25 bukan plat, 14 + 75 plat);
  - lama sebuah benda diam di tempat yang sama.

  Keduanya belum diukur.
- **Lembar kedatangan mengambil baris bergiliran per video.** Satu video dengan banyak kedatangan berulang bisa mengisi banyak
  baris. Ini menjelaskan mengapa satu video parkiran memberi 20 baris.
- **Saran owner menambah video tepat waktunya.** Plat yang bisa dinilai per lembar hanya 18–23, dan hampir semuanya mobil siang.
  Motor dan malam hampir tidak terukur.

## 6. Batas

- **Angkanya kecil:** 18 plat dinilai dan 12 bingkai. Semua kelompok "terlalu sedikit".
- **Lembar latih hanya 100 kedatangan.** Aturan dipilih dari 75 plat dan 25 bukan plat.
- **Rasio kendaraan hanya pengganti "tampak depan atau belakang".** Tampak sesungguhnya tidak dilabeli.
- **Kecepatan tidak dipakai:** uji sesi lain menyala di 265 dari 812 rekaman proses.
- **Mesin `RISET-SAJA`, dan video daring, bukan kamera gerbang sungguhan.**

## 7. Catatan pelaksanaan

- **Gerbang uji:**
  - lab 241 → 251, dengan merah dilihat dulu;
  - uji image tambahan 29 → 30. Uji baris perintah `--letak` ditulis sesudah kode, jadi tidak dilihat merah.
- **Penyaring letak ditaruh di `letak.saring_letak`,** supaya rantai dan lembar bingkai memakai fungsi yang sama.
- **`penampakan.jsonl` mendapat daftar `kendaraan` yang sejajar dengan `tampak`.** `dataset_cctv.py` membongkar butir `tampak`
  sebagai `g, *kotak`, jadi daftar itu tidak diubah.
- **Kali ini kotak per bingkai di set uji tidak dilihat** sebelum owner memeriksa.
