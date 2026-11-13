# Pencari plat dilatih lanjut dengan plat Roboflow (Rencana 29, K56, 19 Okt 2026)

> Hitungan saja. Teks plat, gambar, dan nama berkas tidak ada di repo (`CLAUDE.md` §4). Semua angka dibaca dari layar alat dan dari
> `bukti/2026-10-19-pencari-plat-roboflow.json` (dibuat `data/alat-sementara/gabung-bukti-29.mjs` dari berkas nilai; jumlah dan rentang
> Wilson 95% dihitung di skrip, tidak disalin tangan), `-pilih.json`, dan `-ukur.json`.

## Ringkasan

- **Pencari C3 lebih pandai menemukan plat.** Validasi: F1 0,9257 → 0,9431 (174 lawan 162 dari 179 plat). Tangkapan uji: 35 → 37 dari 39.
  Plat-lighting uji: 94 → 95 dari 102.
- **Tetapi rantai utuh tidak membaca lebih banyak plat dengan benar.** Sisi latih: 85 → 84 dari 125. Tangkapan uji: 21 → 18 dari 34. Rentang
  keduanya tumpang tindih lebar (45–76% lawan 37–69%), jadi turunnya belum pasti, tetapi naik jelas tidak.
- **Sebabnya kotak plat C3 kurang pas.** Kotaknya lebih tinggi dan IoU terhadap label owner turun (uji: motor 0,835 → 0,814, mobil 0,877
  → 0,855). Pembaca fpo-indo-1 peka terhadap kotak yang kurang pas, seperti yang ditemukan di Rencana 25–27. Gaya kotak Roboflow
  (gambar diregangkan, 1.780 poligon yang diubah menjadi kotak pembungkus) kemungkinan berbeda dari gaya label owner; ini dugaan, belum
  diukur langsung.
- **Keputusan:** menurut aturan, C3 adalah pencari terpilih dan disimpan sebagai pencari terbaik. **Rantai bawaan tetap memakai C1** (ambang
  0,25). Lihat bagian "Rantai bawaan" untuk alasan dan cara membaliknya.

## Bahan dan pelatihan

- Dataset `dataset/cctv3`: dibangun persis seperti `cctv2-c1` (Rencana 25), lalu `dataset_jualan.py tambah-latih` memasukkan 5.555 gambar
  "vehicle and license plate" v3 (semua sisi) ke latih saja: 5.847 kotak plat, 1.780 di antaranya dari poligon, 0 gambar dilewati. Latih
  total 6.527 gambar. `valid` sama persis dengan `cctv2-c1/valid` (sidik nama, isi, dan label).
- C3: dari C1 (`--bobot-awal-mesin pencari-cctv2-c1`, SHA-256 bobot awal diperiksa), 30 zaman, tujuan jualan, 85,7 menit di GPU. Zaman terbaik
  24 (F1 validasi saat latih 0,9431, ambang 0,55). ONNX sama dengan safetensors di 20 dari 20 gambar.
- Bahan C3 (dari `mesin.json`): dataset-plat-lighting, bobot-yolox, video-riset-youtube, plat-buatan, tangkapan-owner,
  dataset-roboflow-vehicle-license-plate. Semuanya `BOLEH-PRODUK` (K44, K48, K49, K56); `node tools/periksa-jualan.mjs` memberi tanda
  mesin `BOLEH-PRODUK` (kode 0).

## Memilih (aturan ditulis sebelum angka dilihat, pilihan di-commit sebelum uji dibuka)

| Calon | F1 validasi (ambang sendiri) | Plat ditemukan | Kotak palsu |
|---|---|---|---|
| C1 (Rencana 25) | 0,9257 (0,6) | 162 / 179 | 9 |
| **C3** | **0,9431** (0,55) | **174 / 179** | 16 |

F1 C1 dihitung ulang dan sama dengan Rencana 25, jadi alat nilainya sama. C3 lebih tinggi, jadi C3 terpilih (commit `9faf09c`).

## Diukur sekali di uji (ambang dari validasi masing-masing)

| | Tangkapan uji (38 gambar) | Plat-lighting uji (84 gambar) |
|---|---|---|
| C1 | 35 / 39 (rentang 76–96%), 1 kotak palsu | 94 / 102 (85–96%), 8 kotak palsu |
| **C3** | **37 / 39** (83–99%), 1 kotak palsu | **95 / 102** (87–97%), 11 kotak palsu |

Angka C1 sama persis dengan Rencana 25.

## Rantai utuh di tangkapan owner

Susunan: kendaraan YOLOX-Tiny COCO dengan cadangan gambar utuh, pencari plat, fpo-indo-1 ONNX, varian v0. Ambang C3 dipilih di sisi latih
dari {0,25; 0,4; 0,6}: dibaca benar sama di ketiganya (84), kotak di luar label paling sedikit di 0,6 (13 / 10 / 8), jadi 0,6.

| | Ditemukan | Dibaca benar (dari berteks) | Kotak di luar label |
|---|---|---|---|
| Sisi latih, C1 ambang 0,25 (Rencana 25) | 129 / 141 | **85 / 125** (59–76%) | 6 |
| Sisi latih, C3 ambang 0,6 | 126 / 141 | **84 / 125** (59–75%) | 8 |
| Tangkapan uji, C1 ambang 0,25 (Rencana 25) | 34 / 39 | **21 / 34** (45–76%) | 1 |
| Tangkapan uji, C3 ambang 0,6 | 35 / 39 | **18 / 34** (37–69%) | 3 |

Per kelompok di uji: mobil 13 → 13 dari 16 (ditemukan 15 → 16); motor 8 → 5 dari 18.

**Perpindahan per plat (C1 → C3), tangkapan uji, 34 plat berteks:**
- mobil: benar → benar 12, benar → salah 1, salah → salah 2, tak ditemukan → benar 1;
- motor: benar → benar 4, **benar → salah 3**, benar → tak ditemukan 1, salah → salah 7, tak ditemukan → benar 1, tak ditemukan → tak
  ditemukan 2.

Di sisi latih (125 plat): mobil naik 3 (2 salah → benar, 1 tak ditemukan → benar; 2 tak ditemukan → salah), motor turun 4 (benar → salah 5,
benar → tak ditemukan 6, salah → benar 6, tak ditemukan → benar 1). Jadi C3 membantu sebagian plat dan merugikan plat lain. Kerugiannya
terkumpul di motor.

**Kotak rantai terhadap kotak label owner (median, plat yang ditemukan):**

| | Motor: rasio lebar / tinggi / IoU | Mobil: rasio lebar / tinggi / IoU |
|---|---|---|
| Uji, C1 | 1,016 / 0,975 / 0,835 | 1,007 / 1,079 / 0,877 |
| Uji, C3 | 1,012 / **1,113** / **0,814** | 0,982 / **1,108** / **0,855** |
| Latih, C1 | 1,002 / 1,006 / 0,873 | 1,008 / 1,008 / 0,908 |
| Latih, C3 | 1,011 / **1,043** / **0,820** | 0,971 / 1,019 / **0,878** |

## Rantai bawaan

Aturan Rencana 29 hanya mengatur pilihan pencari, bukan penggantian pencari di rantai. Keputusan agen, dibuat **sesudah** angka di atas
dilihat: rantai bawaan tetap C1 (ambang 0,25). Prinsipnya sama dengan aturan pencari: yang lama tetap bila yang baru tidak lebih baik.
Buktinya diambil dari sisi latih, yang boleh dipakai memilih: di ketiga ambang, rantai C3 membaca 84, C1 85. Angka uji (18 lawan 21) tidak
dipakai untuk memilih, tetapi sejalan.

**Cara membalik:** jalankan `baca_gambar.py jalan` atau `rantai.py jalan` dengan folder pencari `data/keluaran/pencari-cctv3-c3` dan
`--ambang 0.6`. Tidak ada kode yang perlu diubah.

## Yang dipelajari

- Menambah plat dari dataset luar menaikkan angka **menemukan** plat, tetapi tidak menaikkan angka **membaca** plat. Yang membatasi rantai
  sekarang adalah kecocokan kotak dan pembaca, bukan jumlah plat yang ditemukan. Ini sejalan dengan Rencana 25–27.
- Langkah berikut yang masuk akal: melatih pembaca dengan potongan dari pencari itu sendiri (kotak C1 dan C3, bukan kotak label), supaya
  pembaca tahan terhadap kotak yang kurang pas. Belum direncanakan.

## Batas

- Tangkapan uji kecil (38 gambar, 34 plat berteks). Selisih 3 plat ada di dalam rentang kebetulan.
- Dugaan gaya kotak Roboflow belum diukur langsung pada label Roboflow.
- Lembar contoh dataset Roboflow hanya sampel (paling banyak 3 per kelas), dan semuanya benar menurut owner.
- Ini tangkapan layar owner, bukan rekaman gerbang sungguhan. Rekaman HP owner (K43) belum ada.
- Kecepatan tidak diukur. C3 bersusunan sama dengan C1 (YOLOX-Nano-640), jadi waktunya diperkirakan sama, tetapi itu belum dibuktikan.
