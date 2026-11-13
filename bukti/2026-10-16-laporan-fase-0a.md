# Laporan Fase 0A: pembuktian dengan bahan dari luar

> Rencana 15, ditulis 16 Okt 2026 atas lampu hijau owner ("A. Jalankan sekarang"). Menutup Fase 0A sesuai spec 8.1 langkah 9
> dan 8.7: angka per kelompok, yang belum terjawab, saran, lalu **keputusan owner**.
> **Semua angka di sini dari bahan luar** (dataset publik dan video daring). Angka ini sementara dan **bukan bukti K9**, karena
> K9 hanya bisa dibuktikan dari kamera di posisi gerbang (spec 2.5, 8.4).
> Tabel angka di bagian 3 ditulis `tools/laporan-0a.mjs` langsung dari berkas JSON di folder ini, dan diperiksa ulang
> di gerbang uji. Tidak ada angka tabel yang diketik tangan.

## 1. Ringkasan untuk owner

**Yang sudah ada.** Selama tiga hari, bengkel dan alat ukur sudah dibangun, izin komponen diperiksa, peraturan plat dibaca, bahan
dikumpulkan, dan set uji disiapkan. Hasil pentingnya:
- **Baca huruf dari potongan plat sudah kuat.** fpo-indo-1, yaitu fast-plate-ocr yang dilatih ulang dengan plat Indonesia,
  membaca benar sekitar 8 dari 10 kendaraan per kelompok. Itu lebih baik daripada semua pembanding siap pakai.
- **Mencari plat di foto plat-lighting juga baik.** YOLOX-Nano-640 buatan sendiri menemukan 96 dari 102 plat, sedangkan
  pembanding siap pakai hanya 31.
- **Rantai utuh sudah berjalan sampai akhir di video riset:** cari plat, potong, baca, lalu gabungkan per kendaraan.

**Yang paling lemah.**
- **Di video riset, pencari plat menemukan banyak benda yang bukan plat.** Dari 120 baris yang Anda periksa, 99 bukan plat.
  Bahkan 7 dari 10 bacaan "yakin" ternyata bukan plat.
- **Banyak plat di video terlalu kecil untuk dibaca,** oleh mesin maupun oleh Anda.
- **Belum ada satu pun rekaman malam atau motor dari sudut gerbang.**

Kelemahan ini tidak bisa diperbaiki dengan video dari internet. Yang dibutuhkan adalah rekaman dari posisi gerbang.

**Yang belum boleh.** Semua mesin hasil latih masih bertanda `RISET-SAJA`, karena izin bobot awalnya (fast-plate-ocr, YOLOX)
tidak dinyatakan. Jadi **belum ada mesin yang boleh dijual**.

**Yang diminta dari Anda:** dua keputusan di bagian 6.

## 2. Kesembilan langkah Fase 0A (spec 8.1)

| # | Langkah | Status | Bukti |
|---|---|---|---|
| 1 | Bengkel: ruang uji tanpa jaringan, daftar bahan dan tandanya, pemeriksa mesin jualan, perbaikan alat unduh | Selesai | [Rencana 1](../plans/2026-10-13-fase-0a-rencana-1-bengkel.md) |
| 2 | Vonis izin tiap komponen | Selesai. Tidak ada bobot bawaan yang bervonis boleh dijual | [`docs/VONIS-LISENSI.md`](../docs/VONIS-LISENSI.md) |
| 3 | Peraturan plat dari teks aslinya | Selesai | [`docs/peraturan-plat.md`](../docs/peraturan-plat.md) |
| 4 | Bahan | **Sebagian.** 100 video dipilah (17 bersudut gerbang, tak satu pun malam); dua dataset berizin jual (INDO-ALPR dan plat-lighting). **Pembuat plat buatan komputer belum dibangun** (keputusan 2) | [`data-asal/`](../data-asal/), `ROADMAP.md` |
| 5 | Set uji pertama, label diperiksa manusia | Selesai, **dengan beda dari spec**. Set uji baca huruf 937 plat, labelnya dibetulkan lewat pemeriksaan Anda (K22–K24). Kelompoknya mobil/motor × **terang/gelap** dari potongan plat, bukan siang/malam dari video. Ditambah set uji cari plat (plat-lighting) dan lembar rantai utuh | [Rencana 5–7](2026-10-14-label-dan-pembaca-kedua.md), [Rencana 12](2026-10-16-pencari-plat-ukur.md), [Rencana 14](2026-10-16-rantai-utuh-video.md) |
| 6 | Pembanding: paket jadi dan AI serba-bisa | Selesai: Qwen3-VL-2B, fast-plate-ocr terbitan, YOLOv9-t-384 | [Rencana 5](2026-10-14-baca-huruf-pertama.md), [Rencana 6](2026-10-14-label-dan-pembaca-kedua.md), [Rencana 12](2026-10-16-pencari-plat-ukur.md) |
| 7 | Mesin belajar pertama: dua atau tiga calon per langkah | Selesai. Baca huruf: mesin-baca-1 (dari nol) dan fpo-indo-1 (dilatih ulang). Cari plat: empat YOLOX. Rantai utuh di video | [Rencana 8](2026-10-14-mesin-baca-pertama.md), [10](2026-10-15-fpo-latih-ulang.md), [13](2026-10-16-pencari-plat-yolox.md), [14](2026-10-16-rantai-utuh-video.md) |
| 8 | Taksiran kecepatan | Selesai sebagai taksiran: laptop, dan Mini PC untuk model saja. Rantai utuh di Mini PC belum diukur | [Rencana 11](2026-10-15-fpo-indo-1-onnx.md), [12](2026-10-16-pencari-plat-ukur.md), [13](2026-10-16-pencari-plat-yolox.md) |
| 9 | Laporan dan keputusan owner | Dokumen ini; keputusan di bagian 6 | — |

## 3. Angka

<!-- angka:mulai (ditulis tools/laporan-0a.mjs; jangan diubah tangan) -->

**Baca huruf: kedatangan terbaca benar pada set uji adil (potongan plat INDO-ALPR; dalam kurung siku rentang 95%)**

| Pembaca | Mobil terang | Mobil gelap | Motor terang | Motor gelap |
|---|---|---|---|---|
| fpo-indo-1 (fast-plate-ocr dilatih ulang, K26) | 496 dari 625 (79,4%) [76–82%] | 49 dari 57 (86,0%) [75–93%] | 166 dari 208 (79,8%) [74–85%] | 17 dari 21 (81,0%) [60–92%] |
| fast-plate-ocr terbitan | 388 dari 625 (62,1%) [58–66%] | 45 dari 57 (78,9%) [67–88%] | 126 dari 208 (60,6%) [54–67%] | 14 dari 21 (66,7%) [45–83%] |
| Qwen3-VL-2B | 413 dari 625 (66,1%) [62–70%] | 39 dari 57 (68,4%) [56–79%] | 135 dari 208 (64,9%) [58–71%] | 15 dari 21 (71,4%) [50–86%] |
| mesin-baca-1 (dari nol) | 200 dari 625 (32,0%) [28–36%] | 15 dari 57 (26,3%) [17–39%] | 55 dari 208 (26,4%) [21–33%] | 5 dari 21 (23,8%) [11–45%] |

Sumber: `2026-10-15-banding-pembaca-10.json`, set uji tanpa plat yang labelnya dipilih dari bacaan pembaca. Kelompok motor gelap kurang dari 30 kedatangan.

**Cari plat di foto utuh (set uji plat-lighting; plat ditemukan bila IoU minimal 0,5)**

| Pencari | Plat ditemukan | Kotak palsu | Plat kecil ditemukan |
|---|---|---|---|
| YOLOX-Nano-640 (dipakai, K31) | 96 dari 102 (94,1%) [88–97%] | 14 | 12 dari 16 (75,0%) |
| YOLOX-Tiny-640 | 96 dari 102 (94,1%) [88–97%] | 10 | 13 dari 16 (81,3%) |
| YOLOX-Tiny-416 | 94 dari 102 (92,2%) [85–96%] | 10 | 11 dari 16 (68,8%) |
| YOLOX-Nano-416 | 91 dari 102 (89,2%) [82–94%] | 14 | 10 dari 16 (62,5%) |
| Pembanding siap pakai YOLOv9-t-384 | 31 dari 102 (30,4%) [22–40%] | 51 | 0 dari 16 (0,0%) |

Ambang keyakinan dipilih di validasi; set uji dibaca sekali per pencari. Plat kecil: tingginya kurang dari 3% tinggi foto.

**Rantai utuh di video riset (cari plat, potong, baca, gabung per kedatangan), dinilai dari lembar owner**

| Hal | Angka |
|---|---|
| Video | 30 |
| Gambar sampel per detik video | 5 |
| Gambar sampel | 33.906 |
| Kedatangan | 269 |
| Kedatangan "yakin" | 13 |
| Kedatangan "ragu" (gerbang tidak dibuka) | 256 |
| Baris lembar yang diperiksa owner | 120 |
| Bukan plat, menurut owner | 99 |
| Plat tak terbaca, juga oleh owner | 14 |
| Plat yang dinilai | 7 |
| Benar dan yakin | 3 dari 7 (42,9%) [16–75%] |
| Benar tetapi ragu | 2 |
| Salah dan ragu | 2 |
| Salah dan yakin (bahaya buka-salah) | 0 |

Sumber: `2026-10-16-rantai-video-ulang-ringkasan.json` dan `2026-10-16-rantai-video-nilai.json`.

**Kecepatan: median per panggilan dengan 2 utas**

| Bagian | Laptop (Ryzen 7 8700F) | Mini PC (Celeron N5095), model saja |
|---|---|---|
| Cari plat, YOLOX-Nano-640 | 17,4 ms | 149,9 ms |
| Baca huruf, per potongan plat | 14,3 ms | 100,3 ms |
| Rantai di video: cari plat per gambar sampel | 17,7 ms | belum diukur |
| Rantai di video: baca per potongan | 13,9 ms | belum diukur |

Laptop: foto utuh atau potongan sungguhan, termasuk praproses. Mini PC: model saja, masukan buatan, bobot acak bersusunan sama (model hasil latih tidak dibawa ke sana, K15); pembacanya ONNX terbitan fast-plate-ocr yang susunannya sama dengan fpo-indo-1.

<!-- angka:akhir -->

**Cara membaca:**
- **Baca huruf** dinilai per kedatangan, yaitu satu plat yang difoto beberapa kali. "Terang" dan "gelap" diukur dari kecerahan
  potongan plat, bukan dari jam.
- **Kotak palsu** adalah kotak yang bukan plat.
- **Di rantai utuh, "ragu" berarti gerbang tidak dibuka.** Yang berbahaya hanya "salah dan yakin".

## 4. Yang belum terjawab

| Hal | Kenapa belum | Dijawab di mana |
|---|---|---|
| **K9** (gagal-buka 99% per kelompok, buka-salah nol) | Hanya bisa dibuktikan dari kamera di posisi gerbang, dengan sekitar 300 kedatangan uji per kelompok (spec 8.3, 8.4) | Fase 0B, lalu Fase 1 dan 2 |
| **B2:** plat motor dari sudut gerbang | Tidak ada video motor dari sudut gerbang; di lembar rantai utuh tidak ada satu pun motor | Fase 0B |
| **B3:** malam, hujan, silau | Dari 17 video bersudut gerbang tidak satu pun malam | Fase 0B |
| **B5:** kecepatan di server sungguhan | Mini PC baru diukur untuk model saja; unggah, dekode, dan rantai utuh di sana belum | Fase 0B |
| Plat yang terlewat di video | Kendaraan yang platnya tidak pernah ditemukan tidak muncul di lembar | Rekaman berlabel dari posisi gerbang |
| Akurasi rantai per kedatangan | Hanya 7 plat yang bisa dinilai | Fase 0B |
| **P14:** arti "larangan" untuk label non-komersial dan syarat situs | Menunggu owner | Keputusan owner |
| Izin bobot fast-plate-ocr (K27) | Pesan izin dikirim owner sendiri, kapan saja | Jawaban pembuatnya |
| Pemungutan suara per huruf di rantai | Belum diuji. Dari 256 kedatangan "ragu", 203 punya bacaan yang sesuai pola tetapi tidak sama persis | Sesudah ada plat yang cukup banyak untuk dinilai |

## 5. Risiko dan batas

- **Belum ada mesin yang boleh dijual.** fpo-indo-1 memakai bobot awal fast-plate-ocr dan pencari plat memakai bobot awal COCO
  YOLOX. Izin keduanya tidak dinyatakan (`BELUM-JELAS`), jadi mesinnya `RISET-SAJA`. Bahan latihnya sendiri (INDO-ALPR,
  plat-lighting) bervonis `BOLEH-PRODUK`.
- **Penahan buka-salah sekarang hanya daftar izin.** Di rantai utuh, benda bukan plat bisa dibaca "yakin". Gerbang hanya membuka
  bila bacaan itu sama dengan plat terdaftar; itu jarang, tetapi bukan nol. Pencari plat perlu diajari menolak benda bukan plat
  dengan rekaman dari posisi gerbang.
- **Bahan luar berbeda dari kamera gerbang.** Dataset potongan plat dan foto plat dari dekat terlalu mudah, sedangkan video
  daring terlalu kecil dan tanpa malam.
- **Data pribadi:** foto dan bacaan plat tetap di laptop (`data/`, tidak masuk git). Lembar hanya dibuka owner, dan nomor plat
  yang pernah ditulis di percakapan tidak disalin ke berkas mana pun.

## 6. Keputusan yang diminta dari owner

### Keputusan 1: sesudah Fase 0A

| Pilihan | Artinya | Akibat |
|---|---|---|
| **Fase 0B dulu di lokasi Anda sendiri (usulan agen)** | Merekam dari posisi gerbang Anda (K5), dengan HP atau CCTV yang sudah ada, tanpa pembelian (K6). Mobil dan motor, siang dan malam | Menjawab B2, B3, dan B5 yang sebenarnya. Memberi bahan untuk mengajari pencari plat menolak benda bukan plat, dan plat yang cukup besar untuk dinilai. Butuh waktu Anda untuk merekam |
| Lanjut ke Fase 1 sekarang | Membangun mesin baca plat produk dari bahan yang ada | Bisa jalan tanpa menunggu rekaman, tetapi angka lulus Fase 1 tetap butuh rekaman dari posisi gerbang, dan kelemahan pencari plat belum terlihat penyebabnya |
| Ubah arah | Misalnya memakai paket jadi atau AI serba-bisa sebagai produk | Bertentangan dengan K16; angka pembanding di bagian 3 lebih rendah daripada mesin sendiri |

**Kenapa agen mengusulkan Fase 0B:** kelemahan terbesar ada di sisi bahan, bukan di sisi pembaca. Rekaman dari gerbang Anda
sendiri tidak butuh izin pihak lain (B9), dan bisa dimulai dengan HP. **Cara membaliknya:** Fase 0B bisa dihentikan kapan saja,
dan Fase 1 bisa dimulai sesudahnya atau berdampingan.

### Keputusan 2: plat buatan komputer (spec 8.1 langkah 4)

| Pilihan | Artinya | Akibat |
|---|---|---|
| **Tunda (usulan agen)** | Dibangun bila Fase 0B menunjukkan kekurangan bahan, atau bila izin fast-plate-ocr ditolak | Tidak ada kerja sekarang. Bila izin ditolak, plat buatan komputer menjadi jalan untuk melatih pembaca jualan tanpa bobot awal yang belum jelas |
| Bangun sekarang | Pembuat plat mobil dan motor, termasuk versi malam | Menyiapkan jalan mesin jualan lebih awal. Hurufnya harus digambar sendiri atau dibeli lisensinya (spec 2.7) |
| Tidak dipakai | Hanya bahan nyata | Bergantung penuh pada izin bobot awal dan rekaman sendiri |

**Kenapa agen mengusulkan menunda:** bahan latih yang ada sudah boleh dijual. Yang menghalangi mesin jualan sekarang adalah izin
bobot awal, dan jawabannya belum ada. **Cara membaliknya:** pembuatnya bisa dibangun kapan saja sebagai rencana tersendiri.

## 7. Catatan pelaksanaan

- **Gerbang uji:** Node 107 → 111; lab tetap 203. Uji alat angka terlihat merah dulu.
- **Angka di luar tabel** (100 video, 17 bersudut gerbang, 937 plat, 120 baris lembar, 99 bukan plat, 7 dari 10 "yakin", 203
  dari 256 "ragu") berasal dari laporan rencana yang ditautkan di bagian 2 dan dari `ROADMAP.md`.
