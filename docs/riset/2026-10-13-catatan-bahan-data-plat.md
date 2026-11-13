# Catatan sumber: bahan data plat Indonesia yang gratis (13 Okt 2026)

> **Apa ini.** Hasil survei hanya-baca lewat web, dikerjakan sub-agen riset pada 13 Okt 2026 atas permintaan owner
> (K16). Tidak ada yang di-clone, dipasang, atau dijalankan, dan tidak ada dataset yang diunduh.
>
> **Pemeriksaan acak oleh agen utama (13 Okt).** Ketentuan Layanan YouTube dibuka ulang dan cocok: larangan
> mengunduh dan larangan akses otomatis, dengan pengecualian hanya izin tertulis atau mesin pencari; tidak ada
> pengecualian riset; berlaku 15 Des 2023.
>
> **Keandalannya.** Selain klaim di atas, agen utama **belum memeriksa ulang** baris di bawah. Tiap vonis berstatus
> **sementara** sampai diperiksa di Fase 0 (`OPEN-QUESTIONS.md` B12). Tiga hal membatasi seluruh catatan:
>
> - **Kaggle:** halaman manusia hanya memuat judul. Bukti diambil dari metadata API
>   `https://www.kaggle.com/api/v1/datasets/view/<ref>` ("API-view") atau dari daftar
>   `…/api/v1/datasets/list?search=…` ("API-list saja").
> - **Roboflow Universe:** semua halaman `universe.roboflow.com` menolak dengan HTTP 403.
> - **PDF:** alat baca web tidak mengurai PDF, jadi teks Perpol 7/2021 tidak terbaca (butir 5).
>
> Isi gambar (mobil/motor, plat hitam/putih, siang/malam) hampir tidak pernah tertulis di halaman. Bila kolom Isi
> tidak menyebutnya, artinya halaman memang diam, bukan "tidak ada".
>
> **Efek samping.** Alat baca web menyimpan otomatis dua salinan PDF Perpol 7/2021 (881 KB dan 7,4 MB) ke folder
> sementara sesi, di luar repo. Itu peraturan publik, bukan dataset.
>
> **Arti vonis:** `BOLEH-PRODUK` = berizin komersial dengan asal jelas · `RISET-SAJA` = hanya untuk belajar (K15) ·
> `BELUM-JELAS` = lisensi atau asal-usulnya tidak bisa dipastikan. Lisensi hak cipta **tidak** menyelesaikan soal
> data pribadi (UU PDP): plat di dataset mana pun tetap data pribadi.

## 1. Dataset plat Indonesia

| Nama + URL | Isi/ukuran | Lisensi (kutipan) + bukti | Vonis | Catatan |
|---|---|---|---|---|
| INDO-ALPR (ITS), https://data.mendeley.com/datasets/j3256db3fz/1 | 6.174 gambar; "roadways, proximate to traffic signals, and near gas stations"; 7 Sep 2023 | "CC BY 4.0" (halaman yang sama) | `BOLEH-PRODUK` | Format anotasi, jenis kendaraan, warna plat, siang/malam tidak tertulis. Daftar berkas kosong di halaman. Makalah pendamping tidak ditemukan. **Koreksi 13 Okt (agen utama, dibaca dari API publik Mendeley Data, tanpa mengunduh gambar):** daftar berkasnya ada di API: 67.922 berkas, 7.390 MB. Yang asli 6.174 (`original/train` 4.712, `original/test` 1.462); 61.747 lainnya gambar olahan (`augmentation/`) (semula tertulis 61.745, dari jumlah per folder di kepala jawaban API; catatan lengkap penerbit yang diambil 14 Okt menulis 61.747). Tidak ada berkas anotasi: nomor plat ada di **nama berkas**. Tiap berkas punya SHA-256 dari penerbit. |
| Indonesian License Plate Lighting Dataset, https://github.com/salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset (cermin Kaggle `yoyogogo093/indonesian-license-plate-lighting-dataset`) | 561 gambar (393/84/84); malam, sore, siang; kotak YOLOv8, 1 kelas `number-plate`; difoto sendiri oleh pembuat; Jan 2026 | README GitHub: "Lisensi: CC BY 4.0". Kaggle: "Other (specified in description)", deskripsinya tanpa teks lisensi | `BOLEH-PRODUK` | Satu-satunya yang menyebut malam secara eksplisit. Tidak ada berkas LICENSE; label dua tempat tidak seragam. |
| Indonesian License Plate Dataset (UI), https://www.kaggle.com/datasets/juanthomaswijaya/indonesian-license-plate-dataset | 1.000 gambar deteksi 3024×3024 dari HP, kotak YOLO; 1.906 potongan plat 602×189 beranotasi karakter 36 kelas; "different lighting conditions"; ±2,06 GB; Des 2024 | licenseName "Unknown" (API-view) | `RISET-SAJA` | Angka di catatan lama benar, tetapi 1.906 itu potongan plat untuk set pengenalan. Makalah JIKI 2025 berlisensi CC BY-SA 4.0 untuk artikelnya, bukan datasetnya (https://jiki.cs.ui.ac.id/index.php/jiki/article/view/1320). |
| Commercial Vehicle License Plate Dataset, https://www.kaggle.com/datasets/kennyanaga/commercial-vehicle-license-plate-dataset | "362 photo frames" 2736×1536; Jl. Perintis Kemerdekaan, Semarang; dari tepi jalan, kamera 2 m; 3 hari pukul 14.00–16.00; ±1,37 GB; Jul 2023 | "Unknown" (API-view) | `RISET-SAJA` | Hanya siang, hanya kendaraan niaga. Anotasi tidak dijelaskan. |
| Commercial Vehicle License Plate (potongan), https://www.kaggle.com/datasets/risangbaskoro/commercial-vehicle-license-plate | ±275 potongan plat 136×36, Semarang | "CC BY-NC-SA 4.0" (API-view) | `RISET-SAJA` | Pasangan dataset di atas. |
| Indonesian Vehicle License Plate Dataset, https://www.kaggle.com/datasets/linkgish/indonesian-plate-number-from-multi-sources | 1.863 plat berlabel teks (`label.csv`) + 1.383 gambar deteksi (COCO); Agu 2025 | "Apache 2.0" (API-view) | `BELUM-JELAS` | Gabungan lima dataset Kaggle. Yang judulnya cocok dan diperiksa berlabel "Unknown" (`caasperart/haarcascadeplatenumber`, `mhmmdakbar1812/plat-nomor-kendaraan`, `hashimatulzaria/nomor-plat-kendaraan`, `yuricholalenoh/nomorplat`). Pencocokan hanya lewat judul. |
| Indonesian Plate Number Recognition LMDB, https://www.kaggle.com/datasets/alimtegar/indonesian-plate-number-recognition-lmdb-dataset | 936 gambar plat (LMDB); sumber: imamdigmi + firqaaa + video | "CC BY-NC-SA 4.0" (API-view) | `RISET-SAJA` | |
| Indonesian Plate Number, https://www.kaggle.com/datasets/imamdigmi/indonesian-plate-number | "Plate number of Indramayu / Cirebon Area (E)"; ±172 MB; 2018 | "GPL 2" (API-view) | `BELUM-JELAS` | GPL pada data bersifat copyleft dan tidak lazim. Deskripsi kosong. |
| Indonesian Vehicle Plate Numbers, https://www.kaggle.com/datasets/firqaaa/indonesian-vehicle-plate-numbers | ±190 MB; 2021 | "CC BY-NC-ND 4.0" (API-view) | `RISET-SAJA` | Deskripsi kosong. |
| dataset plat nomor motor indonesia, https://www.kaggle.com/datasets/caasperart/haarcascadeplatenumber | ±1,13 GB; 2023; motor (hanya dari judul) | "Unknown" (API-view) | `RISET-SAJA` | Satu-satunya yang berjudul motor. |
| Lima dataset Kaggle berlabel komersial tanpa deskripsi: `sukmaadhiwijaya/indonesian-number-plate-detection-dataset`, `zkyfauzi/indonesia-licence-plate-darknet`, `journalcauchy/plat-nomor`, `abilcode/indonesian-license-plate-ocr-dataset` (+ `lisence-plate-indonesian-ocr-recog`), `bagusmuhammad18/plat-bonus` | 1,05 GB; 1,62 GB; 2,03 GB; 51 + 76 MB; 715 MB | "CC0: Public Domain"; "Apache 2.0"; "CC BY 4.0"; "MIT"; "MIT" (API-view) | `BELUM-JELAS` | Semua deskripsi kosong. Asal gambar dan jumlahnya tidak diketahui. |
| Kaggle lain (API-list saja): `gunawan26/labelled-indonesian-car-and-plate-number` (API-view), `agungcahyo959/plat-nomor`, `sokiww/platnomornnt`, `aisyahainii/lokasi-plat-kendaraan`, `saifulfadli/alpr-rbf` | 57 MB hingga 1,6 GB | "Unknown", kecuali alpr-rbf "CC0: Public Domain" | `RISET-SAJA` (alpr-rbf `BELUM-JELAS`) | Tanpa deskripsi. |
| Tel-U Vehicle License Plate Data-set V1.0, https://cokagung.staff.telkomuniversity.ac.id/koleksi-dataset/tel-u-vehicle-license-plate-data-set-v1-0/ | 228 gambar kendaraan (sisi depan) + 228 gambar penanda | "published only for education and research purpose"; "All rights … is reserved" | `RISET-SAJA` | Tautan unduh "on-progress"; versi penuh harus diminta. |
| License-Plate-Indonesia, https://public.roboflow.com/object-detection/license-plate-indonesia | 1 kelas "plate"; jumlah gambar tidak tertulis; Jul 2022 | "CC BY 4.0" | `BELUM-JELAS` | Unduhan "None yet", jadi tidak bisa dipakai. |
| Roboflow Universe: `umsida/plat-nomor-ilft7`, `muhammad-rizki/plat-nomor-k9x8b`, `vision-8tbf0/indonesian-plate` (49 gambar), `tes-60jyf/indonesian_plate_detection`, `plat-nomor-sovtk` (800), `arkhsat-project` (1,06–2,75 ribu) | lihat kiri | TIDAK DIBUKA (403; ringkasan pencarian menyebut CC BY 4.0 untuk dua yang pertama) | `BELUM-JELAS` | `tes-60jyf` katanya punya kelas plat baru/lama/listrik/umum. |
| InaTRC (CCTV tol Indonesia), https://data.mendeley.com/datasets/kddgphck3b/1 | 3.250 gambar CCTV, 5 golongan kendaraan, kotak YOLO; Mar–Okt 2022 | "CC BY 4.0" | `BOLEH-PRODUK` | Bukan dataset plat. Berguna untuk sudut CCTV; keterlihatan plat tidak tertulis. |
| Hugging Face, Zenodo, IEEE DataPort, GitHub | Tidak ada dataset plat Indonesia | TIDAK DITEMUKAN | – | HF dan Zenodo dicari lewat API-nya (Zenodo hanya memunculkan makalah). IEEE DataPort hanya lewat mesin pencari. GitHub: 57 repo "indonesian license plate", ±31 terlihat, hampir semua kode. |

## 2. Dataset negara lain (pra-latih pendeteksi)

| Nama + URL | Isi/ukuran | Lisensi (kutipan) + bukti | Vonis | Catatan |
|---|---|---|---|---|
| CCPD, https://github.com/detectRecog/CCPD | "over 300k images" (2019) + CCPD-Green; kotak, 4 titik sudut, dan nomor plat tersandi di nama berkas | "This dataset is open-source under MIT license." | `BOLEH-PRODUK` | Plat Tiongkok, satu plat per gambar. Unduh via Google Drive/BaiduYun. |
| Open Images V7, https://storage.googleapis.com/openimages/web/factsfigures_v7.html | ±9 juta gambar, 600 kelas berkotak | "The annotations are licensed by Google LLC under CC BY 4.0"; "The images are listed as having a CC BY 2.0 license"; "you should verify the license for each image yourself" | `BOLEH-PRODUK` | Kelas "Vehicle registration plate": dari ingatan sub-agen, tidak diverifikasi. |
| License Plates (Roboflow), https://public.roboflow.com/object-detection/license-plates-us-eu | 350 gambar, subset Open Images, kelas vehicle + license-plate | "CC BY 4.0" | `BOLEH-PRODUK` | Kecil. |
| keremberke/license-plate-object-detection, https://huggingface.co/datasets/keremberke/license-plate-object-detection | 8.823 gambar (6.176/1.765/882), 1 kelas | "CC BY 4.0" | `BOLEH-PRODUK` | Dari proyek Roboflow "Vehicle Registration Plates"; asal gambar tidak dijelaskan. |
| Artificial Mercosur License Plates, https://data.mendeley.com/datasets/nx9xbs4rgx/2 | ±3.840 gambar: plat sintetis ditempel di adegan nyata | "CC BY 4.0" | `BOLEH-PRODUK` | Kode pembuatnya tidak ditautkan. |
| UFPR-ALPR, https://web.inf.ufpr.br/vri/databases/ufpr-alpr/ | 4.500 gambar, 150 kendaraan, mobil + motor | "released for academic research only"; "free to researchers from educational or research institutes for non-commercial purposes" | `RISET-SAJA` | Perlu perjanjian lisensi. |
| RodoSol-ALPR, https://github.com/raysonlaroca/rodosol-alpr-dataset | 20.000 gambar 1280×720; 10.000 di antaranya motor; siang + malam; kamera statis gerbang tol | "released for academic research only" | `RISET-SAJA` | Perjanjian harus dikirim dari surel universitas, jadi praktis tertutup bagi perusahaan. Isinya paling mirip kebutuhan kita. |
| OpenALPR benchmarks, https://github.com/openalpr/benchmarks | Folder `endtoend`, `detection`, dll.; jumlah gambar tidak tertulis | Repo: "AGPL-3.0 license" | `BELUM-JELAS` | Hak atas gambar tidak dinyatakan. |
| license-plates-700k, https://huggingface.co/datasets/mabo7237/license-plates-700k | 20 GB; kartu kosong | "MIT" (label) | `BELUM-JELAS` | Salinan `guica/license-plates-700k`; isi tidak diketahui. |
| Global License Plate Dataset, https://arxiv.org/abs/2405.10949 | "over 5 million images", 74 negara | Lokasi unduh dan lisensi dataset tidak tertulis | `BELUM-JELAS` | Indonesia tidak disebut. |
| Sampel vendor (Unidata, TrainingData) di Kaggle/HF | Sampel kecil | "CC BY-NC-ND 4.0" (API-list) | `RISET-SAJA` | |
| `andrewmvd/car-plate-detection`; `thasan3003/nightlpbd-nighttime-license-plates-of-bangladesh` | 433 gambar; 2,8 GB plat malam Bangladesh | "CC0: Public Domain"; "CC BY 4.0" (API-list saja) | `BELUM-JELAS` | Halaman tidak dibuka. |

## 3. Pembuat plat buatan komputer (sintetis)

| Nama + URL | Cara kerja | Lisensi + bukti | Vonis | Catatan |
|---|---|---|---|---|
| darrellathaya/indonesian-license-plate-generator, https://github.com/darrellathaya/indonesian-license-plate-generator | Python. Templat putih/hitam/kuning/merah; baris utama (awalan, angka, akhiran) + baris kecil masa berlaku MM.YY; glyph PNG dari `fonts/Indonesia License Plate.ttf`; kotoran, retak, paku; tempel ke latar; keluaran gambar + masker per karakter / Pascal VOC | Tidak ada berkas LICENSE (pohon berkas lewat API GitHub). `fonts/README.md`: font "free for personal use only" | `RISET-SAJA` | Satu-satunya yang khusus Indonesia. 0 bintang, 1 commit. Aset tampak turunan pembuat plat Iran (berkas `.xcf` bernama huruf Persia); "reused from the original prototype" tanpa nama. Hanya acuan rancangan. |
| ZevonikRF/PlatNomorGenerator, https://github.com/ZevonikRF/PlatNomorGenerator | GUI Python pembuat nomor plat per kode wilayah (Jawa), mengaku mengikuti Perpol 7/2021; tanpa font atau templat gambar | Tidak ada LICENSE | `RISET-SAJA` | Menghasilkan teks nomor, bukan gambar. |
| zheng-yuwei/license-plate-generator, https://github.com/zheng-yuwei/license-plate-generator | Karakter dirender dari berkas font, ditempel ke templat plat, lalu perspektif, latar acak, HSV, derau Gauss, noda | "MIT license" | `BOLEH-PRODUK` (kode) | Pola terdekat dengan kebutuhan kita. 180 bintang. Aset font/templat Tiongkok tidak dipakai. |
| simonyos/thai-plate-synth, https://github.com/simonyos/thai-plate-synth | Perender parametrik; kotak YOLO per karakter ikut diproyeksikan ulang lewat augmentasi; font diunduh terpisah; catatan asal-usul `provenance.jsonl` | MIT | `BOLEH-PRODUK` (kode) | 0 bintang. Menangani plat 1 dan 2 baris. Pola asal-usulnya layak ditiru. |
| Belval/TextRecognitionDataGenerator, https://github.com/Belval/TextRecognitionDataGenerator | Pembuat gambar teks umum; font `.ttf` sendiri, latar gambar, distorsi, masker karakter | "MIT license" | `BOLEH-PRODUK` | 3,7 ribu bintang. Tidak mengenal tata letak plat. |
| qjadud1994/Korean-license-plate-Generator, https://github.com/qjadud1994/Korean-license-plate-Generator | Templat + folder gambar per karakter; varian kecerahan dan perspektif; label di nama berkas | MIT | `BOLEH-PRODUK` (kode) | 64 bintang, kode kecil. |
| niklaswa/license-plate-generator, https://github.com/niklaswa/license-plate-generator | Aplikasi web Next.js plat Eropa, font "EuroPlate TTF (FE-Schrift)" | "PolyForm Noncommercial 1.0.0" | `RISET-SAJA` | |
| `Pengfei8324/chinese_license_plate_generator`, `barzansaeedpour/iranian-license-plate-generator` (MIT); `yinguobing/License-Plate-Generator`, `apereiracvo/cr-plates-generator` (GPL-3.0) | Tidak dibuka satu per satu | Dari API pencarian GitHub | MIT `BOLEH-PRODUK`; GPL `BELUM-JELAS` | GPL-3.0 copyleft, hindari di produk tertutup. |

## 4. Huruf plat

| Nama + URL | Pembuat/isi | Lisensi (kutipan) + bukti | Vonis | Catatan |
|---|---|---|---|---|
| "Plat Nomor", https://wepfont.com/plat-nomor/ | Wahyu Eka Prasetya (wepfont), 2020, 95 glyph | DaFont: "Free for personal use" (https://www.dafont.com/plat-nomor.font). FontSpace: "Freeware, Non-Commercial"; "Contact the designer to purchase a commercial license" (https://www.fontspace.com/plat-nomor-font-f45735). wepfont: Desktop $9, Extended $99, App/Game $199, Server $299, Corporate $999 | `RISET-SAJA` | Tak satu pun tingkat lisensi menyebut pembuatan data latih; perlu konfirmasi tertulis pembuatnya. |
| "Indonesia License Plate", https://www.dafont.com/indonesia-license-plate.font | Budiman Ramadhan; "I trace it from Indonesia License Plate … only available in Alphabet and Number only"; di DaFont sejak 22 Apr 2013 | "Free for personal use" | `RISET-SAJA` | Jiplakan penggemar. Dari tanggalnya kemungkinan meniru huruf era 2011 (dugaan). |
| FE-Schrift asli | Karlgeorg Hoefer untuk BASt, 1978–80; BASt tidak pernah menerbitkan versi digital | Lisensi tidak dinyatakan (https://en.wikipedia.org/wiki/FE-Schrift) | `BELUM-JELAS` | Tidak ada berkas resmi. |
| "Euro Plate", https://www.andyhoppe.com/design/fonts/euro-plate-font/ | Andy Hoppe; tiruan FE-Schrift | "Die Schriftart kann für private Zwecke frei verwendet werden." | `RISET-SAJA` | Pemakaian komersial tidak disebut. |
| "GL-Nummernschild-Mtl/Eng", https://fontlibrary.org/en/font/gl-nummernschild-mtl | Gutenberg Labo; FE-Mittelschrift dan Engschrift | "M+ Fonts Project License" | `BELUM-JELAS` | Calon terbaik untuk FE-Schrift. Bahwa lisensi M+ sangat longgar: dari ingatan sub-agen, tidak diverifikasi. Situs cermin memberi label bertentangan (ringkasan pencarian). |
| Huruf resmi Korlantas | – | TIDAK DITEMUKAN | – | Ringkasan pencarian menyebut font aslinya tidak dibuka ke umum. |

Untuk plat Indonesia hanya ada dua font tiruan penggemar, keduanya khusus pemakaian pribadi. Tidak ada font terbuka.

## 5. Spesifikasi resmi plat

**Teks primer Perpol 7/2021 gagal dibaca.** Salinannya ditemukan, tetapi berupa PDF biner atau pindaian:

- https://peraturan.go.id/files/bn476-2021.pdf (Berita Negara 2021 No. 476), 881 KB.
- https://bapenda.jabarprov.go.id/JDIH/Peraturan_Polri/PERATURAN_POLRI_NOMOR_7_TAHUN_2021.pdf (pindaian), 7,4 MB.
- Belum dibuka: salinan Korlantas dan "PERKAKOR NO 1 TH 2021 TTG MATERIEL REGIDENT" di
  `k3i.korlantas.polri.go.id`, yang kemungkinan memuat spesifikasi teknis.

Yang berikut **seluruhnya dari sumber sekunder**:

- **Warna (Pasal 45 ayat 1, dikutip Kompas 13 Agu 2021,
  https://nasional.kompas.com/read/2021/08/13/09151591/ketentuan-baru-soal-warna-pelat-kendaraan-bermotor?page=all):**
  putih tulisan hitam untuk perseorangan, badan hukum, PNA, badan internasional; kuning tulisan hitam untuk umum;
  merah tulisan putih untuk instansi pemerintah; hijau tulisan hitam untuk kawasan perdagangan bebas.
- **Ayat lain Pasal 45 (Kompas):** (2) "ditambahkan tanda khusus untuk ranmor listrik", ditetapkan Keputusan
  Kakorlantas; (3) dipasang di depan dan belakang; (4) "Standardisasi spesifikasi teknis TNKB ditetapkan dengan
  keputusan Kakorlantas Polri"; (5) pengadaan terpusat.
- **Isi TNKB:** "TNKB memuat: NRKB; dan masa berlaku" (blog
  https://www.ainamulyana.com/2022/08/peraturan-polri-nomor-7-tahun-2021.html, tanpa nomor pasal).
- **Ukuran:** tidak ada sumber yang mengutip ukuran dari Perpol; menurut Kompas, rinciannya didelegasikan ke
  Keputusan Kakorlantas, yang tidak ditemukan.
  - Motor 275×110 mm dan mobil 430×135 mm sejak April 2011: detikOto 10 Mei 2011
    (https://oto.detik.com/berita/d-1636334/beda-pelat-nomor-mobil-dan-motor), Otomotifnet 13 Feb 2016
    (https://otomotifnet.gridoto.com/read/231124104/apakah-pelat-nomor-anda-standar-cek-di-sini), Wikipedia
    Indonesia.
  - Wikipedia Inggris menulis motor 275×115 mm dan mobil 460×135 mm; kalimat 460 mm tidak bersitasi.
- **Susunan baris:** "Di pelat ada 2 baris" (Otomotifnet 2016, mengutip Ditlantas Polda Metro Jaya). Baris pertama
  kode wilayah, nomor polisi, kode seri; baris kedua masa berlaku.
- **Plat motor: nomor registrasi ditulis SATU baris**, dengan baris kedua yang lebih kecil untuk masa berlaku, sama
  seperti mobil. Tidak ada sumber yang menyebut nomor motor dipecah dua baris. Pada desain 2011, masa berlaku motor
  di kanan bawah dan mobil di tengah bawah (detikOto 2011).
- **Huruf:** Kompas 2 Sep 2019 menyebut huruf dibedakan "khusus untuk nomor cantik" sejak 1 Agu 2019, tanpa nama
  font
  (https://otomotif.kompas.com/read/2019/09/02/063200615/polri-ubah-jenis-huruf-dan-angka-pada-plat-nomor-cantik).
  Wikipedia Indonesia menyebut FE-Schrift hanya untuk nomor pilihan. Klaim FE-Schrift untuk semua roda empat sejak
  November 2022 hanya ada di Wikipedia Inggris, tanpa sitasi.
- **Plat listrik:** lis biru menurut Keputusan Kakorlantas No. 5/2020 (Wikipedia Indonesia; keputusannya tidak
  dibuka).

## 6. Video daring dan ketentuan layanan

**Jenis video yang relevan:** demo vendor palang parkir LPR/ANPR · demo kamera ANPR merek CCTV oleh pemasang lokal ·
one gate system perumahan/cluster · smart gate kampus/pabrik · rekaman ETLE.

**Kata kunci (usulan, hasilnya belum terverifikasi):** halaman hasil YouTube tidak terbaca, dan pencarian web
kebanyakan memunculkan video luar negeri.

- `palang parkir otomatis LPR plat nomor`
- `sistem parkir ANPR Indonesia demo`
- `one gate system perumahan kamera plat nomor`
- `CCTV deteksi plat nomor Dahua` atau `Hikvision ANPR Indonesia`
- `smart gate kampus plat nomor`
- `manless parking Indonesia`

Contoh yang muncul di pencarian (tidak dibuka): "Dahua CCTV Deteksi plat nomer"
(https://www.youtube.com/watch?v=lDnOWpY55Uw) dan "UNV ANPR Camera with Parking Barrier"
(https://www.youtube.com/watch?v=hzvMFK1Rrj8).

**Keduanya tidak mengizinkan pengunduhan untuk riset tanpa izin tertulis, dan tidak memuat pengecualian riset.**

- **YouTube** (https://www.youtube.com/t/terms?hl=en&gl=US, berlaku 15 Des 2023; versi Indonesia menampilkan 5 Jan
  2022). Dilarang:
  - "access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or
    otherwise use any part of the Service or any Content except: (a) as expressly authorized by the Service; or (b)
    with prior written permission from YouTube and, if applicable, the respective rights holders";
  - "access the Service using any automated means (such as robots, botnets or scrapers) except (a) in the case of
    public search engines, in accordance with YouTube's robots.txt file; or (b) with YouTube's prior written
    permission".
- **TikTok** (https://www.tiktok.com/legal/page/row/terms-of-service/en, diperbarui 1 Des 2025):
  - "Such content may not be downloaded, copied, reproduced, distributed";
  - "use automated scripts to collect information from or otherwise interact with the Services";
  - "Our Services are provided for private, non-commercial use."

## Temuan terpenting untuk keputusan desain

1. **Hanya dua dataset nyata Indonesia yang berlisensi komersial dengan asal jelas:** INDO-ALPR (6.174, CC BY 4.0)
   dan Lighting Dataset (561, CC BY 4.0, ada malam). Lisensi hak cipta tidak menyelesaikan soal data pribadi (UU
   PDP); itu keputusan terpisah.
2. **Label lisensi Kaggle tidak bisa dipercaya begitu saja.** Dataset "Apache 2.0" milik linkgish dirakit dari
   dataset berlabel "Unknown", dan lima dataset berlabel CC0/MIT/Apache/CC BY tidak punya deskripsi sama sekali.
   Vonis butuh rantai asal-usul, bukan label.
3. **Motor, malam, dan komposisi plat hitam/putih hampir tidak terdokumentasi.** Hanya satu dataset berjudul motor
   (tanpa lisensi) dan satu yang menyebut malam (561 gambar). Ini alasan terkuat untuk data sintetis dan rekaman
   sendiri.
4. **Tidak ada pembuat plat sintetis Indonesia yang bisa dipakai.** Satu-satunya tidak berlisensi dan memakai font
   khusus pribadi. Pola MIT yang layak ditiru sudah ada (font → templat → augmentasi → kotak per karakter), jadi
   pembuat sendiri adalah jalan yang realistis.
5. **Font adalah sumbatan untuk data sintetis.** Pilihan untuk owner: beli lisensi wepfont plus konfirmasi tertulis
   untuk data latih, periksa berkas lisensi GL-Nummernschild, atau menggambar glyph sendiri.
6. **Tiga klaim di catatan lama tidak terdukung sumber Indonesia:** mobil 460×135 mm, FE-Schrift untuk roda empat
   sejak November 2022, dan motor 275×115 mm. Sumber Indonesia menyebut 430×135, 275×110, dan huruf khusus hanya
   untuk nomor pilihan. Pembuat sintetis sebaiknya menjadikan ukuran dan jenis huruf sebagai parameter, lalu
   dicocokkan dengan foto nyata.
7. **Tata letak sama untuk mobil dan motor:** satu baris nomor + satu baris kecil masa berlaku. Yang berbeda hanya
   rasio (±3,2:1 mobil, ±2,5:1 motor) dan posisi masa berlaku.
8. **Pra-latih pendeteksi:** CCPD dan Open Images berizin komersial. UFPR-ALPR dan RodoSol hanya untuk akademik dan
   mensyaratkan surel universitas.

## Yang tidak berhasil diverifikasi

- Teks primer Perpol 7/2021, termasuk apakah ia memang tidak memuat ukuran dan susunan baris. Keputusan Kakorlantas
  tentang spesifikasi teknis dan Perkakor 1/2021 tidak dibuka.
- Laman Korlantas "Tak Ada Perbedaan Pelat Nomor Lama dan Baru" (galat sertifikat; hanya ringkasan pencarian).
- Semua halaman Roboflow Universe (403).
- Isi nyata semua dataset: mobil/motor, warna plat, siang/malam, mutu anotasi. Banyak deskripsi Kaggle kosong.
- INDO-ALPR: format anotasi dan makalah pendamping. Makalah JIKI (PDF di atas 10 MB) tidak terbuka.
- Dataset Kaggle bertanda "API-list saja"; lima sumber hulu dataset linkgish dicocokkan hanya lewat judul.
- OpenALPR benchmarks: jumlah gambar dan hak atas gambar. Open Images: keberadaan kelas "Vehicle registration
  plate" (dari ingatan sub-agen).
- Isi lisensi M+ Fonts untuk GL-Nummernschild (dari ingatan sub-agen); pernyataan bahwa font resmi Korlantas
  dirahasiakan (ringkasan pencarian).
- Klaim Wikipedia Inggris tentang FE-Schrift untuk plat reguler (2022) dan motor (2025).
- Relevansi kata kunci video; dua contoh video tidak dibuka.
- Hasil nihil di IEEE DataPort, Zenodo, dan Hugging Face berdasar pencarian terbatas; ±26 dari 57 repo GitHub tidak
  terlihat.
