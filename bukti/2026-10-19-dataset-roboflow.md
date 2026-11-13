# Tiga dataset merek Indonesia dari Roboflow: aman dan benar? (Rencana 28, K53, 19 Okt 2026)

> Hitungan dan nama kelas saja. Gambar, lembar, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari layar
> `buka_arsip.py`, `periksa_dataset.py`, dan Windows Defender (`MpCmdRun`); semuanya ada di `bukti/2026-10-19-dataset-roboflow.json`.

## Asal

| Dataset | Pengunggah | Versi | Izin di halaman | Jenis tugas | SHA-256 zip (dikunci di `tools/vendor.lock.json`) |
|---|---|---|---|---|---|
| all-cars-logo | zendyyonghero | v7 | CC BY 4.0 | deteksi (kotak logo) | `170455e8…2d0` |
| brand | JMTO | v11 | CC BY 4.0 | deteksi (kotak kendaraan) | `d9403aa3…91e` |
| car-type-final-1 | Skripsi | v2 | CC BY 4.0 | klasifikasi (gambar utuh) | `16b3adf5…883` |

Diunduh owner lewat peramban (Roboflow mewajibkan akun). Halaman diperiksa agen lebih dulu: domain resmi Roboflow, Google Safe Browsing "tidak
ditemukan konten berbahaya" untuk universe.roboflow.com dan app.roboflow.com, sertifikat Google Trust Services yang berlaku, masuk Google lewat
accounts.google.com.

## Keamanan: bersih

| Pemeriksaan | all-cars-logo | brand | car-type |
|---|---|---|---|
| Windows Defender (kontrol positif EICAR terdeteksi, kode 2) | bersih (kode 0) | bersih | bersih |
| Jalur arsip (mutlak, "..", tautan simbolik) | aman | aman | aman |
| Berkas berakhiran terlarang (skrip, program) | 0 | 0 | 0 |
| Nama kembar | 1 salinan identik `data.yaml` | 2 salinan identik `data.yaml` | 0 |
| Gambar yang isinya bukan gambar | 0 | 0 | 0 |
| Tanda berkas program di awal berkas | 0 | 0 | 0 |
| Berkas teks berbyte nol atau bukan UTF-8 | 0 | 0 | 0 |
| Gambar yang tidak bisa dibuka | 0 | 0 | 0 |
| `data.yaml` dibaca aman (`safe_load`) | ya | ya | (tidak ada) |

Kejadian: `buka_arsip.py` mula-mula menolak all-cars-logo karena nama `data.yaml` kembar. Diperiksa dulu tanpa mengekstrak: salinannya identik
(CRC dan ukuran sama). Aturan pembuka arsip lalu diubah dengan uji merah dulu: salinan identik dibuka sekali; nama kembar dengan isi berbeda,
termasuk yang hanya beda huruf besar-kecil, tetap ditolak sebelum menulis.

## Kebenaran isi

| | all-cars-logo | brand | car-type |
|---|---|---|---|
| Gambar (latih / validasi / uji) | 13.540 / 3.380 / 0 (cocok dengan halaman) | 5.871 / 735 / 733 (cocok) | 1.272 / 551 / 0 (cocok) |
| Kelas | 63 (6 bernama `_unused`, masih berisi contoh) | 41 | 4 (avanza, fortuner, innova, other) |
| Kotak | 18.183 | 7.334 | — (klasifikasi) |
| Label rusak, kelas di luar daftar, koordinat di luar 0–1, kotak nol | 0 | 0 | — |
| Label kosong | 1 | 8 | — |
| Kembar persis di dalam sisi | 8 | 0 | **109** |
| Kembar persis antarsisi (kebocoran latih/uji) | 3 | 0 | 0 |
| Mirip antarsisi (dHash sama) | 51 | 31 | 7 |
| Ukuran gambar (lebar terkecil / tengah / terbesar) | 139 / 1.023 / 11.517 | 1.920 / 1.920 / 1.920 | 600 (diregangkan) |

**Temuan per dataset:**
- **all-cars-logo:** sebaran kelasnya tidak mirip jalanan Indonesia: Ferrari 1.018 kotak, Wuling 900, Rolls-Royce 722, sedangkan Honda 8,
  dan Nissan, Mazda, serta Chery masing-masing 1. Ukuran gambarnya sangat beragam, jadi kemungkinan besar dikumpulkan dari internet, bukan
  CCTV. Kelasnya mencampur merek dengan kelompok (TOYOTA, TOYOTA_LCGC, TOYOTA_ALPHARD; NETA_LOGO dan NETA_TEXT; satu kelas bernama "LEPAS").
  Halaman yang dibaca agen riset menyebut 68 kelas; `data.yaml` memuat 63.
- **brand (JMTO):** paling mirip bahan kita: semua gambar 1920×1080 seperti bingkai kamera, satu kotak per gambar, dan sebaran masuk akal
  (Toyota 2.490, Honda 1.353, Mitsubishi 547, Suzuki 453, Daihatsu 429). Tetapi kelasnya mencampur merek dan model: "toyota" berdiri sejajar
  dengan "agya" dan "alphard", "daihatsu" sejajar dengan "ayla" dan "sigra". Untuk melatih, kelas model perlu digabung ke mereknya atau
  dipisah menjadi tingkat kedua. 31 pasang gambar mirip antara latih dan validasi/uji, kemungkinan bingkai berurutan dari kamera yang sama.
- **car-type:** hanya 4 kelas mobil Toyota (Avanza, Fortuner, Innova, lainnya), diregangkan ke 600×600. 109 gambar kembar persis di dalam
  sisi yang sama.

## Lembar contoh untuk owner

`periksa_dataset.py lembar` membuat paling banyak 3 contoh per kelas, bernomor baris dan bertulis nama kelasnya, di
`data/keluaran/rencana-28/lembar-<dataset>/`: all-cars-logo 182 baris (8 halaman), brand 110 baris (5 halaman), car-type 12 baris
(1 halaman). Agen tidak membukanya (gambar memuat kendaraan dan plat orang). Owner menyebut nomor baris yang labelnya salah.

## Kesimpulan sementara (sebelum lembar diperiksa)

- **Aman:** ketiganya hanya berisi gambar dan label yang jenisnya cocok dengan isinya; tidak ada tanda program; Defender bersih.
- **Benar secara teknis:** label terbaca dan berada di dalam gambar; jumlahnya cocok dengan halaman Roboflow.
- **Mutu untuk kita:** brand (JMTO) paling berguna (gambar seperti kamera, merek pasar Indonesia), dengan catatan kelas merek dan model
  bercampur. all-cars-logo condong ke foto internet dan mobil mewah. car-type sempit (4 kelas Toyota) dan banyak kembar.
- **Izin:** tetap `BELUM-JELAS`. Asal gambar tidak diketahui, dan label CC BY 4.0 dari pengunggah, bukan dari pemilik gambar.

## Dua dataset tambahan (diunduh owner 19 Okt, diperiksa dengan cara yang sama)

| | vehicle and license plate | Merk dan Warna Motor |
|---|---|---|
| Alamat (dari README di dalam zip) | universe.roboflow.com/plat-kendaraan/vehicle-and-license-plate, v3 | universe.roboflow.com/arfah/merk-dan-warna-motor, v19 |
| Izin di halaman dan `data.yaml` | MIT | CC BY 4.0 |
| SHA-256 zip | `665699c1…365` | `334af010…8dd` |
| Defender (kontrol EICAR terdeteksi) | bersih | bersih |
| Berkas menyamar, tanda program, teks kotor, gambar rusak | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Gambar (latih / validasi / uji) | 5.102 / 432 / 21 (halaman model menyebut 2.167) | 7.212 / 687 / 344 (halaman: 3.435) |
| Ukuran gambar | 640×640 | 640×640 |
| Kelas | 4: License_Plate, cars, motorcyle, truck (halaman model: 5, termasuk bus) | 13 gabungan model dan warna: Honda Beat (biru-putih, hijau, hitam, silver), Honda Vario (hitam, merah, putih), Yamaha Aerox (hitam, kuning, putih), Yamaha NMAX (hitam, merah, putih) |
| Label | 10.038 kotak dan **1.780 poligon plat** (bentuk kotak lain, bisa diubah menjadi kotak; 0 rusak) | 8.243 kotak, 0 cacat |
| Kembar persis di dalam sisi / mirip antarsisi | 75 / 145 | 5 / 192 |
| Lembar contoh | 12 baris (1 halaman) | 39 baris (2 halaman) |

**Temuan:**
- Jumlah gambar di zip lebih banyak dari halaman model, dan banyak gambar mirip antara latih dan uji. Kemungkinan bagian latih sudah
  diperbanyak (augmentasi) dan bingkai berurutan dari video yang sama tersebar ke latih dan uji. Akibatnya **angka 99,5% di halaman Roboflow
  diukur di soal yang hampir sama dengan bahan latihnya**, jadi tidak bisa dibandingkan dengan angka kita di CCTV owner.
- README "vehicle and license plate" menyebut dataset ini **gabungan dari dataset pengguna Roboflow lain** (antara lain
  habib-robbani/indonesian-motorcycle-plate). Label MIT ditempel pengunggah gabungan; izin sumber aslinya belum dibaca.
- "Merk dan Warna Motor" sempit: 4 model motor dan 13 pasangan warna. Untuk dipakai, model dan warna lebih baik dipisah menjadi dua label.

## Pemeriksaan owner (19 Okt)

Owner membuka kelima lembar contoh dan menjawab per lembar, apa adanya: "lembar vehicle and license plate sudah benar semua. all cars logo= sudah
benar semua; lembar brand= sudah sesuai; car type= data terlalu sedikit, tapi sudah benar; merk warna motor= sudah benar semua". Jadi semua
contoh yang diperiksa (all-cars-logo 182, brand 110, car-type 12, vehicle and license plate 12, Merk dan Warna Motor 39 baris) berlabel benar.
Kelima dataset dipakai sebagai bahan latih sejak K56.

## Batas

- Lembar contoh hanya sampel (paling banyak 3 per kelas), bukan pemeriksaan semua label.
- "Mirip" (dHash sama) adalah petunjuk, bukan bukti gambar yang sama.
- Defender dan pemeriksaan jenis berkas tidak menjamin gambar bebas celah pembaca gambar; karena itu gambar hanya dibuka di lab tanpa
  jaringan.
