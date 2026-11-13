# Pencari plat dilatih ulang dengan gambar CCTV, ditambah tahap kendaraan (K39)

> Rencana 19 Fase 1, dijalankan 16 Okt 2026 secara mandiri (K37), dengan tiga lembar yang diperiksa owner (K19): satu lembar
> latih dan dua lembar uji. Mesin yang dinilai adalah **mesin belajar** (`RISET-SAJA`): pencari plat YOLOX-Nano-640 yang dilatih
> ulang, pencari kendaraan YOLOX-Tiny COCO, dan pembaca fpo-indo-1. Tolak ukurnya **set uji video CCTV daring** (K36): 41 video
> sisi uji, dengan bingkai yang sama dengan titik awal ([`2026-10-16-titik-awal-cctv.md`](2026-10-16-titik-awal-cctv.md)).
> Sumber angka:
> - [`-ringkasan.json`](2026-10-16-pencari-plat-cctv-ringkasan.json)
> - [`-nilai-kedatangan.json`](2026-10-16-pencari-plat-cctv-nilai-kedatangan.json)
> - [`-nilai-bingkai.json`](2026-10-16-pencari-plat-cctv-nilai-bingkai.json)
> - [`-nilai-bingkai-ketat.json`](2026-10-16-pencari-plat-cctv-nilai-bingkai-ketat.json)
> - [`-dataset.json`](2026-10-16-pencari-plat-cctv-dataset.json)
> - [`-mesin.json`](2026-10-16-pencari-plat-cctv-mesin.json) dan [`-mesin-onnx.json`](2026-10-16-pencari-plat-cctv-mesin-onnx.json)
> - [`-kendaraan-onnx.json`](2026-10-16-pencari-plat-cctv-kendaraan-onnx.json)
>
> Semua berkas di atas berawalan `2026-10-16-pencari-plat-cctv`. Isinya hitungan saja, dan sudah diperiksa tidak memuat satu pun
> dari 11.106 teks plat, nama berkas, dan nama video. Kontrol positifnya menemukan 1.371 dari minimal 1.367.

## Ringkasan untuk owner

- **Saringan kendaraan (usulan Anda, K39) bekerja.**
  - Benda bukan plat di lembar kedatangan turun dari 105 ke 6, dari 120 baris.
  - "Yakin" yang bukan plat turun dari 11 dari 14 ke 1 dari 19.
- **Plat yang bisa dinilai naik dari 4 ke 23**, dan yang terbaca benar dan yakin naik dari 2 ke 14.
- **Ada 2 bacaan salah tetapi yakin**, keduanya di video parkiran. Di titik awal tidak ada, tetapi saat itu hanya 4 plat yang
  dinilai.
- **Masalah terbesar sekarang plat yang terlewat.** Dari 13 bingkai yang menurut Anda memuat plat, hanya 1 yang platnya
  ditemukan (bingkai 38). Bingkai 41, yang dulu ditemukan, kini terlewat. Pencari kendaraan menemukan kendaraannya; yang gagal
  adalah pencari platnya.

## 1. Bahan dan latihan

**Lembar latih (sisi latih, 120 baris, diurutkan menurut keyakinan kotak):** owner menyebut 14 plat dan 106 bukan plat. Owner
hanya memilah plat dan bukan plat, tidak memeriksa bacaannya.

**Dataset** (`tools/lab/dataset_cctv.py`):
- Kotak yang tidak dipilah owner ditutup buram.
- Gambar latar ditempeli plat buatan (Rencana 18).
- Plat-lighting ikut.

| Sisi | Gambar CCTV | Kotak plat | Gambar tanpa plat | Kotak ditutup buram | Gambar tempel | Plat-lighting |
|---|---|---|---|---|---|---|
| Latih | 269 | 44 | 225 | 151 | 202 | 393 |
| Validasi | 64 | 3 | 61 | 10 | 24 | 84 |

**Latihan:**
- YOLOX-Nano-640 dengan bobot awal COCO, 864 gambar latih, 100 zaman, selama 68,4 menit di GPU.
- Zaman terbaik 67, dengan F1 validasi 0,9236 pada ambang 0,5. Pencari lama: 0,917 pada ambang 0,25.
- **Kedua F1 tidak sebanding.** Validasi pencari baru hanya memuat 3 kotak plat CCTV.
- ONNX sama dengan torch pada 20 dari 20 gambar.

## 2. Tahap kendaraan (K39)

Owner mengusulkan urutan: kendaraan, lalu tampak depan atau belakang, lalu plat di area kendaraan itu.
- **Yang dipasang:** langkah pertama dan ketiga. Kotak plat diterima hanya bila tengahnya berada di dalam kotak kendaraan
  (`tools/lab/kendaraan.py`; `rantai.py` dan `lembar_bingkai.py` mendapat `--kendaraan`).
- **Belum ada:** langkah tampak depan atau belakang.

**Pemilihan di sisi latih.** Aturannya ditulis sebelum angka dilihat: semua 14 plat harus lolos; lalu dipilih yang paling sedikit
meloloskan bukan plat.

| Pencari kendaraan | Ambang | Plat lolos (dari 14) | Bukan plat lolos (dari 106) |
|---|---|---|---|
| Nano COCO | 0,15 / 0,25 / 0,4 | 12 / 12 / 9 | 21 / 19 / 9 |
| **Tiny COCO** | 0,15 / **0,25** / 0,4 | 14 / **14** / 12 | 24 / **14** / 10 |

- **Terpilih:** tiny pada ambang 0,25.
- Kelas sepeda tidak mengubah satu angka pun, jadi tidak ikut.
- Angka lewat ONNX sama persis dengan pengukuran awal lewat torch.

## 3. Rantai di 41 video uji

| | Titik awal (Rencana 17) | Sesudah |
|---|---|---|
| Ambang kotak plat | 0,25 | 0,5 |
| Kedatangan (yakin) | 416 (41) | 198 (22) |
| Siang / campuran / malam / remang / tak jelas | 326 / 33 / 31 / 21 / 5 | 197 / 1 / 0 / 0 / 0 |
| Kotak plat dibuang tahap kendaraan | – | 2.505 |

**Kedatangan malam dan remang hilang semua.** Di video malam, tahap kendaraan hanya membuang 11 kotak. Jadi yang hilang terutama
datang dari pencari plat baru, yang kini jarang memberi kotak di atas ambang 0,5.

## 4. Lembar kedatangan (owner, 120 dari 198)

| Jawaban owner | Titik awal | Sesudah | Di antaranya "yakin" (sesudah) |
|---|---|---|---|
| **Bukan plat** | **105** | **6** | 1 |
| Plat tak terbaca | 11 | 91 | 2 |
| Plat dinilai | 4 | 23 | 16 |

- **Dari 23 plat yang dinilai:**
  - benar dan yakin: 14;
  - benar tetapi ragu: 6;
  - salah dan ragu: 1;
  - **salah tetapi yakin: 2**, keduanya di video parkiran.
- **Dari 19 kedatangan "yakin" di lembar:**
  - 14 benar;
  - 2 salah;
  - 1 bukan plat;
  - 2 platnya tak terbaca manusia.
- **85 baris adalah motor, dan semuanya tak terbaca** menurut owner. Baris yang dinilai semuanya mobil dari video siang. Kelompok
  lain tidak punya baris yang dinilai.
- **Cara menghitung.** Owner menjawab dengan nomor baris untuk salah, tak terbaca, bukan plat, dan motor. Baris yang tidak disebut
  dihitung benar dan mobil, sesuai petunjuk lembar. Ada 20 baris seperti itu.
- **Jenis kendaraan dari tahap kendaraan belum bisa dipakai membedakan mobil dari truk.** Dari 20 baris benar, 12 dicatat
  sebagai "truk" oleh pencari COCO.

## 5. Lembar bingkai (owner, 41 bingkai yang sama dengan titik awal)

Kotak biru menandai kendaraan; kotak hijau menandai plat yang diterima.
- **Bingkai berplat menurut owner:** 13. Hanya 1 yang platnya ditemukan, yaitu bingkai 38. Owner menilainya "paling benar,
  sudah terlihat kendaraan dan platnya benar".
- **Plat terlewat di 12 bingkai.** Owner juga menghitung plat yang buram atau tak terbaca sebagai terlewat, jadi dua hitungan
  disimpan:

| Hitungan | Dinilai | Ada plat terlewat | Rentang 95% |
|---|---|---|---|
| Owner, plat buram ikut dihitung | 13 | 12 | 0,67–0,99 |
| Ketat: hanya plat yang terbaca (cara titik awal) | 4 | 3 | 0,30–0,95 |
| Titik awal (Rencana 17) | 10 | 4 | 0,17–0,69 |

- **Pada 6 bingkai yang di titik awal disebut berplat** (2, 5, 12, 17, 38, 41), plat ditemukan di 2 bingkai dulu dan 1 bingkai
  sekarang.
- **Kendaraan ditemukan di keenam bingkai itu.** Owner tidak menyebut satu pun kendaraan yang terlewat.
- **Gambar dari owner:** owner melampirkan satu gambar mobil putih di gerbang berpalang. Platnya besar dan jelas, tetapi tetap
  terlewat. Nomornya tidak disalin.

## 6. Bacaan agen

- **Saringan kendaraan menjawab masalah utama titik awal.** Benda bukan plat hampir hilang dari lembar dan dari "yakin". Ini cocok
  dengan pengukuran di sisi latih (92 dari 106 bukan plat tersaring).
- **Pencari plat yang dilatih ulang lebih buruk dalam menemukan plat**, bahkan plat besar yang jelas. Dua dugaan, keduanya belum
  terbukti:
  1. **Ambang 0,5 terlalu ketat untuk CCTV.** Ia dipilih di validasi yang isinya terutama plat-lighting (plat dari dekat).
     Pencari lama memakai 0,25.
  2. **Gambar "tanpa plat" di dataset mungkin memuat plat yang tidak pernah ditemukan pencari lama.** Plat seperti itu tidak
     ditutup buram, jadi pencari baru bisa belajar bahwa plat kecil atau gelap adalah latar. Kotak yang tidak ditemukan sama
     sekali tidak bisa ditutup.
- **Usulan owner langkah ketiga, "lokasi plat di area kendaraan", belum dipakai sepenuhnya.** Saat ini plat dicari di seluruh
  gambar, lalu disaring. Langkah berikutnya mencari plat di dalam potongan kendaraan yang diperbesar, sehingga plat kecil
  mendapat lebih banyak piksel. Kendaraan sudah ditemukan dengan baik, jadi langkah ini memanfaatkan bagian rantai yang paling
  kuat.
- **Bacaan salah tetapi yakin (2) adalah bahaya buka-salah.** Penahannya tetap daftar izin (spec 3.1). Gabung per huruf
  (Rencana pembaca) perlu menimbang ini.

## 7. Batas

- **Angkanya kecil:** 23 plat dinilai dan 13 bingkai berplat. Semua kelompok "terlalu sedikit". Motor dan malam belum punya
  satu baris pun yang dinilai.
- **Pencari plat baru dan tahap kendaraan berubah bersama.** Bagian tahap kendaraan terukur hanya di sisi latih, dengan pencari
  lama.
- **Lembar latih dipakai dua kali:** melatih pencari plat dan memilih pencari kendaraan. Keduanya di sisi latih; set uji tidak
  dipakai memilih.
- **Agen melihat hitungan kotak di set uji sebelum owner memeriksa.** Yang dilihat: kotak per bingkai di 6 bingkai yang berplat
  menurut jawaban owner Rencana 17, dan kedatangan per kategori. Pengamatan ini hanya memicu pemeriksaan. Pembetulan berikutnya
  dipilih di sisi latih.
- **Tampak depan atau belakang belum ada.** Pencari kendaraan berbobot COCO bervonis `BELUM-JELAS`, jadi ia hanya untuk mesin
  belajar. Mesin jualan butuh pencari kendaraan dari bahan `BOLEH-PRODUK`.
- **Kecepatan dari jalan ini tidak dipakai:** uji sesi lain menyala di 22 dari 142 rekaman proses. Median yang terbaca: cari plat
  16,7 ms, kendaraan 69,0 ms, baca 14,4 ms (2 utas).
- **Video daring, bukan kamera gerbang sungguhan.** Mesin `RISET-SAJA`.

## 8. Catatan pelaksanaan

- **Gerbang uji:**
  - lab 224 → 231, dengan merah dilihat dulu;
  - uji image tambahan 22 → 25. Tiga uji barunya tidak dilihat merah lebih dulu. Daya bedanya ada di dalam uji: jalan tanpa
    `--kendaraan` menjadi kontrol.
- **Task 7b ditambahkan sesudah Task 6**, karena usulan owner (K39) datang bersama jawaban lembar latih.
- **`mesin.json` pencari baru bernama `pencari-yolox-nano-640`, sama dengan pencari lama.** Nama diturunkan dari jenis dan
  ukuran; yang membedakan hanya folder dan SHA-256. Ini dicatat dan belum diperbaiki.
- **Jawaban owner untuk lembar bingkai memakai "terlewat" juga untuk plat yang buram.** Karena itu dua hitungan disimpan.
- **Owner melampirkan satu gambar berplat** di percakapan. Nomornya tidak disalin ke berkas mana pun.
