# Plat dicari di dalam potongan kendaraan (K39 langkah 3)

> Rencana 20 Fase 1, dijalankan 16–17 Okt 2026 secara mandiri (K37), dengan tiga lembar yang diperiksa owner (K19): satu lembar
> kendaraan latih dan dua lembar uji. Mesin yang dinilai adalah **mesin belajar** (`RISET-SAJA`):
> - pencari plat YOLOX-Nano-640 yang dilatih ulang di Rencana 19;
> - pencari kendaraan YOLOX-Tiny COCO;
> - pembaca fpo-indo-1.
>
> Tolak ukurnya **set uji video CCTV daring** (K36): 41 video sisi uji, dengan 41 bingkai yang sama dengan Rencana 17 dan 19.
>
> Sumber angka:
> - [`-banding-latih.json`](2026-10-17-plat-di-dalam-kendaraan-banding-latih.json)
> - [`-ringkasan.json`](2026-10-17-plat-di-dalam-kendaraan-ringkasan.json)
> - [`-nilai-kedatangan.json`](2026-10-17-plat-di-dalam-kendaraan-nilai-kedatangan.json)
> - [`-nilai-bingkai.json`](2026-10-17-plat-di-dalam-kendaraan-nilai-bingkai.json)
> - [`-nilai-bingkai-ketat.json`](2026-10-17-plat-di-dalam-kendaraan-nilai-bingkai-ketat.json)
>
> Semua berkas di atas berawalan `2026-10-17-plat-di-dalam-kendaraan`. Isinya hitungan saja, dan sudah diperiksa tidak memuat
> satu pun dari 11.345 teks plat, nama berkas, dan nama video. Kontrol positifnya menemukan 1.611 dari minimal 1.606.

## Ringkasan untuk owner

- **Mencari plat di dalam potongan kendaraan menemukan lebih banyak plat.**
  - Di video latih: 11 dari 17 plat terbaca, dari sebelumnya 3.
  - Di bingkai uji: bingkai 12 dan 17, yang terlewat di Rencana 17 dan 19, kini ditemukan.
- **Tetapi benda bukan plat kembali banyak, terutama di kamera parkiran.**
  - Bukan plat: 46 dari 120 baris lembar kedatangan (Rencana 19: 6).
  - "Yakin" yang bukan plat: 18 dari 43, dan 14 di antaranya dari video parkiran.
- **Di video gerbang hasilnya lebih baik:** dari 16 kedatangan "yakin", 10 benar, 1 bukan plat, 5 platnya tak terbaca manusia,
  dan 0 salah.
- **Bacaan salah tetapi yakin turun dari 2 ke 1** (di parkiran). Bacaan benar-yakin tetap 14.

## 1. Pemilihan di sisi latih (lembar kendaraan)

Owner menandai **17 kendaraan berplat terbaca** di 78 bingkai dari 39 video latih. Ada 138 kendaraan bernomor. Tidak ada
kendaraan berplat terbaca yang luput dari kotak biru.

| Calon (pencari-cara-ambang) | Ditemukan (dari 17) | Kotak salah tempat | Tanpa 4 bingkai dekat latih (dari 13) |
|---|---|---|---|
| lama-saring-0.25 (pencari Rencana 14) | 3 | 1 | 1 |
| baru-saring-0.5 (Rencana 19) | 3 | 0 | 1 |
| lama-potong-0.1 | 8 | 7 | 6 |
| lama-potong-0.25 | 7 | 2 | 5 |
| baru-potong-0.1 | 11 | 5 | 8 |
| **baru-potong-0.25 (terpilih)** | **11** | **2** | **8** |
| baru-potong-0.5 | 9 | 1 | 7 |

Tabel lengkap 12 calon ada di rencana dan di `-banding-latih.json`.
- **Aturan memilih ditulis sebelum angka dilihat:** temuan terbanyak, lalu kotak salah tempat tersedikit. Pencari baru hanya boleh
  menang bila tidak kalah di 4 video validasi.
- **Penjaga validasi kosong**, karena keempat video validasi tidak punya plat terbaca.
- **Pemeriksaan pengganti:** 4 bingkai berlabel punya gambar latih berplat dalam 2 detik. Tanpa keempatnya, pilihan tetap sama.

## 2. Rantai di 41 video uji

| | Titik awal (R17) | R19 (saring, 0,5) | **R20 (potong, 0,25)** |
|---|---|---|---|
| Kedatangan (yakin) | 416 (41) | 198 (22) | **425 (91)** |
| Malam / remang | 31 / 21 | 0 / 0 | 1 / 0 |

## 3. Lembar kedatangan (owner, 120 dari 425)

| Jawaban owner | Titik awal | R19 | **R20** |
|---|---|---|---|
| Bukan plat | 105 | 6 | **46** |
| Plat tak terbaca | 11 | 91 | 55 |
| Plat dinilai | 4 | 23 | 19 |
| Benar-yakin / benar-ragu / salah-ragu / salah-yakin | 2 / 2 / 0 / 0 | 14 / 6 / 1 / 2 | **14 / 4 / 0 / 1** |
| "Yakin" yang bukan plat | 11 dari 14 | 1 dari 19 | **18 dari 43** |

**Menurut sudut kamera:**

| Sudut | Benar (yakin) | Bukan plat (yakin) | Tak terbaca (yakin) | Salah (yakin) |
|---|---|---|---|---|
| Gerbang | 13 (10) | 6 (1) | 33 (5) | 0 |
| Kamera diam lain | 5 (4) | 18 (3) | 3 (0) | 0 |
| Parkiran | 0 | 22 (14) | 19 (5) | 1 (1) |

- **10 kedatangan "yakin" platnya tak terbaca manusia.** Bacaan seperti itu tidak bisa diperiksa.
- **Cara menghitung:**
  - Baris yang tidak disebut owner dihitung benar (18 baris).
  - Baris 15 ("tidak terbaca atau salah posisi") dihitung tak terbaca. Kedua pilihan sama-sama tidak dinilai.
  - Hanya 2 baris disebut motor. Kelompok motor punya 1 baris yang dinilai.

## 4. Lembar bingkai (owner, 41 bingkai yang sama)

| Hitungan | Titik awal | R19 | **R20** |
|---|---|---|---|
| Owner, plat buram ikut dihitung: ada plat terlewat / dinilai | 4 / 10 | 12 / 13 | **7 / 10** |
| Ketat, hanya plat terbaca: ada plat terlewat / dinilai | – | 3 / 4 | **2 / 5** |

- **Ditemukan:** bingkai 12, 17, dan 38. Bingkai 12 dan 17 terlewat di titik awal dan R19.
- **Terlewat:**
  - plat terbaca: bingkai 6 dan 15;
  - plat buram: bingkai 2, 19, 22, 26, dan 41.
- **Tak disebut:** bingkai 3, 5, dan 8, yang di R19 disebut terlewat, kali ini tidak disebut, jadi dihitung tak jelas.

## 5. Bacaan agen

- **Langkah 3 usulan owner bekerja untuk menemukan plat.** Di sisi latih dan di bingkai uji, plat yang terlewat berkurang.
- **Penilaian di sisi latih tidak meramalkan benda bukan plat di parkiran.** Ada dua sebab:
  1. "Ditemukan" dihitung bila ada kotak di mana pun di kendaraan berplat terbaca, bukan harus di platnya.
  2. Lembar latih (2 gambar per video) hanya memuat sedikit kendaraan parkiran yang cukup besar.

  Akibatnya, kotak bukan plat di dalam kendaraan, seperti lampu, stiker, atau bagian motor, tidak terhitung salah.
- **Di dalam potongan kendaraan, pencari plat menemukan benda mirip plat, dan pembaca membacanya "yakin".** Ini paling banyak di
  kamera parkiran yang memandang banyak kendaraan dari atas. Langkah 2 usulan owner (tampak depan atau belakang) dan letak plat di
  dalam kendaraan belum dipakai, padahal keduanya bisa menyaring benda seperti itu.
- **Bacaan "yakin" untuk plat yang tak terbaca manusia (10)** tidak bisa dinilai, dan tetap menjadi risiko.

## 6. Batas

- **Angkanya kecil:** 19 plat dinilai dan 10 bingkai. Semua kelompok "terlalu sedikit". Motor dan malam hampir tidak punya baris
  yang dinilai.
- **Lembar mengambil 120 baris dari jumlah kedatangan yang berbeda** (R19 198, R20 425). Hitungan per baris lembar tidak bisa
  dikalikan langsung menjadi jumlah per kedatangan.
- **Pencari baru dilatih dengan video latih yang sama** dengan lembar kendaraan. Penjaga validasi kosong; pemeriksaan
  penggantinya ditulis sesudah rencana.
- **Kecepatan tidak dipakai.** Uji sesi lain menyala di 410 dari 838 rekaman proses. Yang terbaca (median, 2 utas):
  - kendaraan 69,1 ms per gambar;
  - cari plat di potongan 63,8 ms per gambar (p95 491,9 ms di bingkai parkiran yang penuh kendaraan);
  - baca 14,7 ms.
- **Mesin `RISET-SAJA`, dan video daring, bukan kamera gerbang sungguhan.**

## 7. Catatan pelaksanaan

- **Gerbang uji:**
  - lab 231 → 241, dengan merah dilihat dulu;
  - uji image tambahan 25 → 29. Tiga uji baris perintah ditulis sesudah kode, jadi tidak dilihat merah; uji `--ambang` lembar
    bingkai dilihat merah dulu.
- **Owner menjawab lembar kendaraan dengan nomor bingkai saja.** Owner ditanya sekali lagi untuk 10 bingkai yang punya lebih dari
  satu kendaraan bernomor.
- **K40 dicatat:** resolusi kamera dan jarak kamera ke kendaraan menjadi parameter, diringkas sebagai tinggi plat dalam piksel.
- **Kali ini kotak per bingkai di set uji tidak dilihat** sebelum owner memeriksa. Yang dicek hanya bahwa bingkainya sama.
