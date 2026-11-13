# Pencari plat: pembanding di foto utuh dan kecepatan calon di laptop dan Mini PC

> Rencana 12 Fase 0A, dijalankan 16 Okt 2026 atas lampu hijau owner ("a"), termasuk mengukur di Mini PC.
> **Taksiran dari bahan luar dan masukan buatan, bukan angka produk dan bukan bukti K9.**
> Sumber angka: [`2026-10-16-pencari-oim.json`](2026-10-16-pencari-oim.json),
> [`2026-10-16-pencari-oim-cepat.json`](2026-10-16-pencari-oim-cepat.json),
> [`2026-10-16-cepat-calon-laptop.json`](2026-10-16-cepat-calon-laptop.json), dan
> [`2026-10-16-cepat-calon-minipc.json`](2026-10-16-cepat-calon-minipc.json) di folder ini. Isinya hitungan saja. Sebelum
> disalin, keempatnya diperiksa tidak memuat satu pun dari 10.300 teks plat dan nama berkas. Pemeriksanya diuji dulu pada
> daftar nama berkas plat-lighting, dan menemukan 561 di antaranya.

## 1. Pembanding siap pakai di foto utuh

open-image-models @ eaeb588, `yolo-v9-t-384-license-plate-end2end` (ONNX, CPU). Hanya pembanding: bobotnya `BELUM-JELAS` dan
kode latih induknya GPL-3.0. Dinilai dengan `tools/lab/deteksi.py` pada plat-lighting (CC BY 4.0): ambang keyakinan dipilih di
validasi (0,35), lalu set uji dibaca sekali (84 foto, 102 plat). Sebuah plat dihitung ditemukan bila IoU-nya minimal 0,5.

| Kelompok | Plat ditemukan | Rentang 95% | Kotak palsu |
|---|---|---|---|
| Semua | 31 dari 102 (30%) | 22–40% | 51 |
| Terang | 30 dari 99 | 22–40% | 50 |
| Gelap | 1 dari 3 | terlalu sedikit | 1 |
| Kecil (tinggi < 3% tinggi foto) | 0 dari 16 | terlalu sedikit | — |
| Besar | 31 dari 86 (36%) | 27–47% | — |

**Kenapa serendah itu (diukur, bukan ditebak):** penilainya diperiksa lebih dulu pada sisi validasi.
- **Kotaknya pas:** setiap kali ada tebakan yang menyentuh plat, rasio lebar 0,95, rasio tinggi 1,02, dan pusatnya tidak
  bergeser. Jadi koordinatnya benar.
- **Sisanya tidak tersentuh sama sekali:** 54 dari 99 plat tidak tersentuh tebakan mana pun, bahkan pada keyakinan 0,01.
- **Sebabnya ukuran:** plat yang terlewat tingginya kira-kira separuh plat yang ditemukan. Foto 1920×1080 dikecilkan ke
  384 piksel, sehingga plat kecil nyaris hilang.

Ini sifat model dan ukuran masukannya, bukan cacat penilai.

**Pelajaran untuk pencari plat kita:** ukuran masukan menentukan apakah plat kecil terlihat, dan ukuran masukan bertukar
dengan kecepatan. Di gerbang sungguhan kamera bisa diarahkan supaya plat tampak lebih besar, atau hanya bagian jalur yang
dipotong lebih dulu. Keduanya belum diukur.

## 2. Kecepatan di CPU

Satu panggilan model dengan masukan buatan (`tools/ukur_onnx_cpu.py`; model saja, tanpa membuka berkas dan praproses).
Ketiga calon buatan sendiri memakai bobot acak, karena kecepatan ditentukan susunan model.

| Model | Laptop (Ryzen 7 8700F) 1 / 2 / 4 utas | **Mini PC (Celeron N5095)** 1 / 2 / 4 utas |
|---|---|---|
| YOLOX-Nano 416 px (0,9 juta parameter, 3,7 MB) | 11,5 / 7,0 / 5,0 ms | **117 / 73 / 138 ms** |
| YOLOX-Tiny 416 px (5,0 juta, 20 MB) | 50,9 / 28,0 / 16,5 ms | 471 / 251 / 139 ms |
| RF-DETR Nano 384 px (107 MB) | 262,9 / 140,5 / 83,8 ms | **2.709 / 1.403 / 1.163 ms** |
| Pembanding YOLOv9-t-384 | 25,6 / 15,7 / 10,7 ms | 195 / 105 / 78 ms |
| Pembaca huruf (susunan fpo-indo-1) | 23,2 / 14,7 / 12,6 ms | 183 / 100 / 70 ms |

- **Celeron sekitar 8–10 kali lebih lambat per utas** daripada CPU laptop.
- **Pada Mini PC, 4 utas tidak selalu lebih cepat.** YOLOX-Nano: 138 ms dengan 4 utas, lawan 73 ms dengan 2 utas. Sebabnya
  Mini PC juga menjalankan layanan lain; beban naik ke 5,2 selama pengukuran.
- **Pembanding foto utuh di laptop** (praproses, model, dan pascaproses, 60 foto validasi): 28,6 / 17,8 / 12,6 ms.

**Taksiran per foto di Mini PC** (bacaan agen, 2 utas, cari plat + baca huruf, model saja):

| Calon | Per foto | Tiga foto per kedatangan | Terhadap sasaran 2 detik (spec 2.6) |
|---|---|---|---|
| YOLOX-Nano | sekitar 0,17 detik | sekitar 0,5 detik | masih ada ruang untuk unggah, dekode, dan pencocokan |
| YOLOX-Tiny | sekitar 0,35 detik | sekitar 1,1 detik | sempit |
| RF-DETR Nano | sekitar 1,5 detik | sekitar 4,5 detik | **melewati** |

Unggah foto, membuka berkas, praproses, dan pencocokan dengan daftar pengguna belum dihitung.

## 3. Biaya untuk melatih tiap calon (Rencana 13)

| Calon | Paket baru untuk melatih | Bobot awal | Izin bobot awal |
|---|---|---|---|
| YOLOX-Nano / Tiny | loguru, tabulate, pycocotools (3), lewat pemeriksaan celah | COCO dari rilis YOLOX | Tidak dinyatakan: `BELUM-JELAS` |
| RF-DETR Nano | sekitar 12 (pytorch_lightning, torchmetrics, peft, empat pustaka penilai COCO, simplejpeg, roboflow, torch-hungarian pra-rilis) | Sudah ada di vision-seed, SHA-256 terkunci | Ditandai Apache 2.0; bahan latih COCO tidak dinyatakan: `BELUM-JELAS` |

Kode YOLOX @ 4197784 berusia beberapa tahun. Kecocokannya dengan numpy 2.5 dan torch 2.14 **untuk melatih** belum terbukti;
yang terbukti hanya membangun model dan ekspor ONNX.

## 4. Batas, apa adanya

- **Bahan uji deteksi kecil:** 84 foto dan 102 plat, dari satu dataset, sebagian besar bingkai video 1080p. Kelompok gelap
  hanya 3 plat.
- **Kecepatan memakai masukan buatan dan bobot acak**, model saja. Rantai utuh belum diukur.
- **Mini PC menjalankan layanan lain,** jadi angkanya bergantung pada beban saat itu (1,3 sebelum, 5,2 saat mengukur).
- **SHA-256 pembanding dipercaya pada unduhan pertama,** karena GitHub tidak menerbitkan digest untuk aset 2024.
- **Pembanding bervonis `BELUM-JELAS`:** hanya pembanding.

## 5. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 107; lab 170 → 177 → 178; uji image tambahan 12 → 14. Tiap uji baru terlihat merah dulu.
- **Mini PC:**
  - venv sementara di `/tmp/cctvgerbang-ukur`, paket ber-hash, OSV 0 celah (kontrol positif 19 celah);
  - `nice -n 19`, `timeout 900`, `trap`;
  - sesudahnya folder dihapus dan tidak ada proses yang tersisa;
  - pemeriksaan proses yang pertama menangkap shell SSH sendiri (`pgrep -f` cocok dengan baris perintahnya), jadi diulang
    dengan pola yang tidak bisa cocok dengan dirinya sendiri.
- **Alat ukur dicurigai dulu:** angka 30% pembanding diperiksa ke koordinat dan ukuran plat sebelum diterima.

## 6. Berikutnya

Owner memilih jenis pencari plat yang dilatih di Rencana 13. Sesudah itu:
- **Rencana 14:** rantai utuh di video riset (cari plat, potong, baca, gabung per kedatangan) dan kecepatannya.
- **Rencana 15:** laporan Fase 0A.
