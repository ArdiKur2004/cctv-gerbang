# Baca huruf pertama: set uji INDO-ALPR dan pembanding Qwen3-VL-2B

> Rencana 5 Fase 0A, dijalankan 14 Okt 2026 atas lampu hijau owner ("A").
> **Angka sementara dari bahan luar. Bukan angka produk dan bukan bukti K9.**
> Sumber angka: [`2026-10-14-set-uji-baca-pertama.json`](2026-10-14-set-uji-baca-pertama.json) dan
> [`2026-10-14-baca-vlm-pertama.json`](2026-10-14-baca-vlm-pertama.json) di folder ini. Isinya hitungan saja, dan
> sebelum disalin ke sini keduanya diperiksa tidak memuat satu pun dari 9.692 teks plat dan nama berkas di pembagian
> (sisi latih dan uji). Pemeriksanya diuji dulu pada berkas yang memang berisi plat, dan menemukan semuanya. Angka lain dibaca dari keluaran
> layar alat yang dicatat di pesan commit.

## 1. Apa yang diukur

Langkah 3 mesin baca plat saja (baca huruf), pada potongan plat INDO-ALPR: gambar yang isinya sudah plat saja. Langkah 1
(mencari plat di foto utuh atau video) belum diukur.

Pembacanya Qwen3-VL-2B, AI serba-bisa kecil yang berjalan di laptop tanpa jaringan, dengan satu pertanyaan tetap
(teksnya ada di JSON). Di sini ia punya dua peran: pembanding pertama (spec 8.1 langkah 6) dan calon pelabel otomatis
untuk bahan yang belum berlabel teks (video riset, dataset pencahayaan).

## 2. Set uji

Pembagian latih-uji dari penerbit **tidak dipakai**. Diukur 14 Okt: 713 dari 1.462 gambar ujinya memuat plat yang juga
ada di bagian latih. Bagian latih dan uji penerbit digabung lalu dibagi ulang **per plat**: semua gambar berplat sama
masuk satu sisi, dan sisinya ditentukan dari SHA-256 teks platnya (hasilnya sama setiap kali dijalankan). Satu plat
dihitung satu kedatangan.

| Kelompok | Latih: kedatangan (gambar) | Uji: kedatangan (gambar) |
|---|---|---|
| mobil-terang | 2.003 (3.384) | 642 (1.099) |
| mobil-gelap | 164 (200) | 60 (67) |
| motor-terang | 646 (843) | 221 (241) |
| motor-gelap | 37 (40) | 22 (24), **terlalu sedikit untuk disimpulkan** |
| **Jumlah** | **2.850 (4.467)** | **945 (1.431)** |

- **Plat di kedua sisi: 0.**
- **Dikecualikan: 276 gambar**, karena nama berkasnya tidak sesuai pola plat. Jumlahnya cocok: 4.467 + 1.431 + 276 = 6.174.
- Golongan menurut nomor urut, sisi uji: mobil penumpang 353, motor 243, barang dan khusus wilayah Polda Metro Jaya 228,
  bus 55, barang 39, khusus 27. Kelompok "mobil" di tabel berarti semua yang bukan motor (K9 hanya membedakan mobil dan
  motor).
- **Tentang angka 276.** Rencana memperkirakan sekitar 291. Selisihnya diukur dengan skrip sekali pakai yang hanya
  mencetak bentuk samaran (huruf → A, angka → 9). `tools/lab/plat.py` menyambung 26 nama berspasi tak lazim yang ditolak
  pengukur lama (misalnya spasi di tengah angka). Ia juga menolak 7 nama yang diterima pengukur lama, karena nomor
  urutnya berawalan 0, dan itu tidak sah menurut Perpol 7/2021. Hitungannya 295 − 26 + 7 = 276.

## 3. Angka Qwen3-VL-2B

"Benar" berarti **sama dengan label penerbit**. Label itu tidak selalu benar: dari 60 contoh yang diperiksa owner, 4 sampai
6 labelnya salah (bagian 4). Kedatangan dinilai dari bacaan
terbanyak atas gambar-gambar berplat sama. Bila ada seri di puncak, kedatangan itu dihitung "ragu", bukan ditebak.

| Kelompok | Kedatangan benar | Rentang 95% | Ragu | Gambar benar | Bacaan di luar pola plat |
|---|---|---|---|---|---|
| mobil-terang | 414 dari 642 (64,5%) | 60,7–68,1% | 26 | 759 dari 1.099 | 199 |
| mobil-gelap | 39 dari 60 (65,0%) | 52,4–75,8% | 1 | 45 dari 67 | 8 |
| motor-terang | 135 dari 221 (61,1%) | 54,5–67,3% | 5 | 148 dari 241 | 35 |
| motor-gelap | 15 dari 22, terlalu sedikit untuk disimpulkan | — | 0 | 17 dari 24 | 6 |

**Kecepatan:** 0,277 detik per gambar di kartu grafis RTX 4060 laptop ini. Ini bukan taksiran untuk kotak murah (B5).

**Jenis salah, per gambar, semua kelompok.** Dihitung dengan skrip sekali pakai yang hanya mencetak hitungan: 969 benar,
462 salah.

| Jenis | Gambar |
|---|---|
| Panjang sama, beda 1 huruf | 236 |
| Panjang sama, beda 2 huruf | 85 |
| Panjang sama, beda 3 huruf atau lebih | 37 |
| Panjang berbeda, jarak 1 / 2 / 3 atau lebih | 24 / 24 / 40 |
| Label ditambah sesuatu di belakang (dugaan: baris masa berlaku ikut terbaca) | 14 |
| Terpotong di belakang / tambahan di depan | 1 / 1 |

**Artinya (bacaan agen):**

- Sekitar dua dari tiga plat terbaca sama dengan labelnya. Untuk gerbang, sasarannya 99% (K9), jadi ini jauh di bawah.
  Untuk pelabel otomatis, artinya label dari Qwen3-VL tidak bisa dipakai apa adanya; tiap labelnya perlu diperiksa.
- Kesalahan terbanyak hanya beda satu huruf. Owner menemukan label penerbit salah pada 4 sampai 6 dari 60 contoh,
  kebanyakan juga beda satu huruf. Jadi sebagian "salah baca" Qwen3-VL mungkin sebenarnya label yang salah; berapa banyak
  belum diukur.
- Terang dan gelap **tidak bisa disebut berbeda**, karena rentangnya saling menutupi (mobil: 60,7–68,1% dan 52,4–75,8%).
  Mobil dan motor juga **tidak bisa disebut berbeda** (60,7–68,1% dan 54,5–67,3%).

## 4. Label penerbit

Owner memeriksa 60 contoh pada 14 Okt (15 per kelompok, tiga lembar di `data/keluaran/lembar-contoh/`). Agen tidak
membuka lembar itu (K19). Owner menyebut enam baris. Baris lain tidak disebut, dan dibaca agen sebagai sama dengan
platnya. Nomor platnya sendiri tidak dicatat di repo.

| Baris | Kelompok | Yang ditemukan owner |
|---|---|---|
| 19 | mobil-gelap | Satu huruf seri salah |
| 22 | mobil-gelap | Seri kurang satu huruf di depan; huruf itu tidak terbaca jelas oleh owner |
| 25 | mobil-gelap | Satu huruf seri salah |
| 35 | motor-terang | Huruf kode wilayah dan satu huruf seri salah |
| 36 | motor-terang | Owner membaca huruf kode wilayah berbeda dari label. Bagian atas huruf itu sudah terpotong di potongan gambar dataset (lembar tidak memotong gambar; diperiksa di kode), jadi ini dugaan owner. Bila benar, kelompoknya ikut berubah dari motor ke mobil, karena batas nomor urut berbeda per wilayah |
| 54 | motor-gelap | Satu huruf seri salah |

- **Label salah yang pasti: 4 dari 60** (6,7%, rentang 95% 2,6–15,9%).
- **Bila baris 22 dan 36 ikut dihitung: 6 dari 60** (10,0%, rentang 95% 4,7–20,1%).
- Per kelompok: mobil-terang 0, mobil-gelap 3, motor-terang 2, motor-gelap 1, masing-masing dari 15. Itu terlalu sedikit
  untuk membandingkan kelompok.
- Kelompok tiap baris dibaca dari urutan lembar. Alat memilih 15 contoh per kelompok dengan urutan mobil-terang,
  mobil-gelap, motor-terang, motor-gelap, dan keempat kelompok punya paling sedikit 15 kedatangan uji.
- Rentang dihitung dengan rumus yang sama dengan `baca_vlm.py`, dan rumusnya dicek ulang dengan kontrol ujinya (50 dari
  100 → 40,4–59,6%).

Yang juga diketahui tanpa melihat gambar: 7 nama berkas bernomor urut berawalan 0 (dikecualikan), dan 26 nama berspasi
tak lazim yang disambung. Apakah ke-26 label itu benar belum diketahui.

**Artinya (bacaan agen):** sekitar 1 dari 10 label penerbit salah, dengan rentang yang lebar (sekitar 3–20%). Dengan label
salah sebanyak itu, mesin yang sempurna pun hanya akan tercatat sekitar 90% benar. Jadi set uji ini tidak bisa mengukur
ketepatan setinggi sasaran K9 sebelum labelnya dibetulkan. Bahan latihnya kemungkinan membawa label salah dalam porsi yang
mirip; itu belum diperiksa.

## 5. Batas, apa adanya

- **Potongan plat, bukan gambar kamera gerbang.** K9 tidak bisa dibuktikan dari sini (spec 8.4). Langkah mencari plat di
  gambar utuh belum diukur.
- **Terang atau gelap adalah taksiran** dari terang rata-rata potongan (di bawah 60 dari 255 = gelap). Itu **bukan** siang
  atau malam menurut spec 8.3, yang ditentukan dari langit dan sumber cahaya pada gambar utuh.
- **Kedatangan = gambar berplat sama.** Itu taksiran; dataset ini tidak punya video.
- **Mobil atau motor dibaca dari nomor urut** menurut Perpol 7/2021, bukan dari kendaraan yang terlihat. Kode B dianggap
  wilayah Polda Metro Jaya: anggapan agen yang belum diperiksa ke lampiran kode wilayah.
- **Satu pertanyaan saja** yang dicoba pada Qwen3-VL, dengan gambar berukuran paling besar 448 titik pada sisi
  terpanjangnya. Pertanyaan lain bisa memberi angka lain.
- **Label penerbit salah pada 4 sampai 6 dari 60 contoh dan belum dibetulkan**, jadi "benar" berarti "sama dengan label".
  Baris yang tidak disebut owner dibaca sebagai benar; itu bacaan agen atas jawaban owner.
- **Motor-gelap hanya 22 kedatangan uji**, terlalu sedikit untuk disimpulkan.
- Qwen3-VL di sini **alat lab, bukan bagian produk**. Angka ini angka pembanding, bukan angka mesin yang akan dijual.

## 6. Catatan pelaksanaan

Rencana dijalankan task demi task; tiap uji baru terlihat merah dulu karena fiturnya belum ada.

- **Gerbang uji.** Lab 51 → 72 → 80 → 84 → 91 → 98 → 100; Node tetap 99. Rencana menulis 51 → 72 → 79 → 83 → 90 → 97.
  Selisihnya tiga uji tambahan, semuanya soal kebocoran nama berkas (yang isinya nomor plat):
  - `bagi_set_uji.py` versi rencana mencetak nama berkas bila ada gambar rusak. Dibuktikan dengan menjalankan kode
    rencana apa adanya, lalu ditutup dengan pola yang sudah dipakai alat lain di repo ini.
  - Cacat sepupunya ada di `lembar_contoh.py` dan `baca_vlm.py`: OpenCV mencetak jalur berkas yang tidak bisa dibuka.
    Ditutup dengan membisukan log OpenCV di kedua alat. Pengukuran di bagian 3 tidak terpengaruh, karena log jalannya
    tidak memuat satu pun peringatan semacam itu.
- **Uji model sungguhan** (di luar gerbang, `tools/lab/uji_gpu/`): Qwen3-VL membaca plat buatan "B 1234 XYZ" dengan benar.
  Dijalankan sebelum dan sesudah perubahan terakhir, keduanya 1 lulus.
- **Model** disalin dari vision-seed (K14), tidak diunduh. Ada 11 berkas, dan tiap berkas cocok dengan SHA-256 di
  `tools/vendor.lock.json`.

Mengulang (PowerShell, dari akar repo):

```
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/bagi_set_uji.py /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/set-uji-baca
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_contoh.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-contoh
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_vlm.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/models/qwen3-vl-2b-instruct /kerja/data/keluaran/baca-vlm
```

## 7. Berikutnya

1. ~~Owner membuka tiga lembar contoh dan menyebut nomor baris yang tulisan birunya tidak sama dengan platnya.~~ Selesai
   14 Okt; hasilnya di bagian 4.
2. ~~Rencana 6 ditulis: pembanding paket jadi (misalnya fast-plate-ocr) pada set uji yang sama, mesin belajar pertama untuk
   baca huruf, mencari plat di foto utuh dan video, plat buatan komputer, taksiran kecepatan, laporan.~~ Diubah 14 Okt
   sesudah K22: Rencana 6 hanya berisi pembaca kedua (fast-plate-ocr) dan pembetulan label set uji; sisanya pindah ke
   Rencana 7.
