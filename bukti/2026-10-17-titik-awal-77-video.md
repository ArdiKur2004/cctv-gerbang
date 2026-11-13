# Titik awal di 77 video uji (Rencana 23 Bagian A)

> Rencana 23 Fase 1, Bagian A, dijalankan 17 Okt 2026 secara mandiri (K37), dengan dua lembar yang diperiksa owner (K19).
> Mesin yang dinilai adalah **mesin belajar** (`RISET-SAJA`) dengan cara Rencana 20, rantai terbaik sejauh ini:
> - pencari plat yang dilatih ulang;
> - pencari kendaraan;
> - cara potong, ambang 0,25, tanpa saringan letak;
> - pembaca fpo-indo-1.
>
> Tolak ukurnya **set uji video CCTV daring** sesudah gelombang keempat (K41): 77 video, terdiri dari 41 video lama dan 36 video
> baru.
>
> Sumber angka:
> - [`-ringkasan.json`](2026-10-17-titik-awal-77-video-ringkasan.json)
> - [`-nilai-kedatangan.json`](2026-10-17-titik-awal-77-video-nilai-kedatangan.json)
> - [`-nilai-bingkai.json`](2026-10-17-titik-awal-77-video-nilai-bingkai.json)
> - [`-nilai-bingkai-ketat.json`](2026-10-17-titik-awal-77-video-nilai-bingkai-ketat.json)
>
> Semua berkas di atas berawalan `2026-10-17-titik-awal-77-video`. Isinya hitungan saja, dan sudah diperiksa tidak memuat satu
> pun dari 11.584 teks plat, nama berkas, dan nama video. Kontrol positifnya menemukan 1.850 dari minimal 1.845.

## 1. Rantai

77 video, 65.046 gambar sampel, **529 kedatangan (131 yakin)**. Kategori: siang 516, remang 8, campuran 3, malam 2.

## 2. Lembar kedatangan (owner, 120 dari 529)

Lembar berisi 63 baris dari 18 video lama dan 57 baris dari 16 video baru.

| Jawaban owner | Baris | Di antaranya "yakin" |
|---|---|---|
| Bukan plat | 51 | 11 |
| Plat tak terbaca | 45 | 12 |
| Plat dinilai | 24 | 15 |

| Kelompok | Dinilai | Benar-yakin | Benar-ragu | Salah-ragu | Salah-yakin |
|---|---|---|---|---|---|
| **Mobil siang** | 16 | 11 | 5 | 0 | **0** |
| **Motor siang** (pertama kali terukur) | 8 | 3 | 0 | 4 | **1** |
| Semua | 24 | 14 | 5 | 4 | 1 |

Semua kelompok "terlalu sedikit".

**Menurut asal dan sudut, benar (yakin) / bukan plat (yakin) / tak terbaca (yakin) / salah (yakin):**

| Sudut | 41 video lama | 36 video baru |
|---|---|---|
| Gerbang | 9 (7) / 5 (1) / 14 (1) / 0 | 2 (2) / 12 (2) / 5 (3) / 0 |
| Kamera diam lain | 4 (3) / 5 (0) / 4 (1) / 1 (0) | 1 (0) / 7 (2) / 5 (1) / 0 |
| Parkiran | 0 / 11 (4) / 10 (4) / 0 | 3 (2) / 11 (2) / 7 (2) / 4 (1) |

**Cara menghitung:**
- Baris yang tidak disebut owner dihitung benar dan mobil (19 baris).
- **Dua pertentangan di jawaban owner diselesaikan dengan pilihan yang paling merugikan angka:**
  - baris 101, yang disebut salah dan tak terbaca, dihitung salah;
  - baris 23, yang disebut bukan plat dan tak terbaca, dihitung bukan plat. Kedua pilihan untuk baris ini sama-sama tidak
    dinilai.

  Keduanya dibalik bila owner mengoreksi.

## 3. Lembar bingkai (owner, 77 bingkai, satu per video)

| Hitungan | Dinilai | Ada plat terlewat |
|---|---|---|
| Owner, plat buram ikut dihitung | 20 | 16 |
| Ketat, hanya plat terbaca | 9 | 5 |

- **Ditemukan:** bingkai 16 dan 37 (video lama; dulu bingkai 12 dan 17), serta bingkai 20 dan 55 (video baru).
- **Terlewat, plat terbaca:** bingkai 1, 3, 24, 27, 29. Bingkai 3 adalah bingkai lama nomor 2; sisanya video baru.

## 4. Temuan tentang alat ukur

- **Pada 41 bingkai lama, kotak plat dan kendaraan identik dengan lembar Rencana 20** (`banding-kotak-20-23.mjs`; rantai dan
  pengaturannya sama).
- **Meski begitu, penilaian owner pada bingkai yang sama bisa berbeda antar putaran.** Bingkai lama 38 dinilai "benar" di R20 dan
  "terlewat, buram" sekarang. Bingkai lama 6 dan 15 disebut "terlewat, terbaca" di R20, dan sekarang tidak disebut, sehingga
  dihitung tak jelas.
- **Akibatnya:** sebagian perbedaan angka antar putaran berasal dari penilaian, bukan dari mesin. Dengan jumlah sekecil ini, satu
  atau dua bingkai yang dinilai berbeda sudah mengubah angka. Pembanding antar putaran sebaiknya memakai label yang dikunci
  sekali, lalu dipakai ulang.

## 5. Batas

- **Angkanya kecil:** 24 plat dinilai dan 9–20 bingkai.
- **Malam hampir tidak ada:** 2 kedatangan malam.
- **Video daring, bukan kamera gerbang yang dipasang menghadap plat.** Mesin `RISET-SAJA`.
- **Kecepatan tidak dipakai:** uji sesi lain menyala di 327 dari 984 rekaman proses.
