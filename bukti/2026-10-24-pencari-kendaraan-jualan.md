# Pencari kendaraan jualan (Rencana 32, Fase 3, K48, 24 Okt 2026)

> Hitungan saja. Gambar, kotak, teks plat, dan nama berkas tidak ada di repo (`CLAUDE.md` §4). Angka dibaca dari layar alat dan dari
> `bukti/2026-10-24-pencari-kendaraan-jualan.json` (dibuat `data/alat-sementara/gabung-bukti-32.mjs` dari berkas sumber; jumlah dan rentang
> Wilson 95% dihitung di skrip) dan `-pilih.json`.

## Ringkasan

- **Rantai sekarang punya pencari kendaraan yang boleh dijual.** Pencari lama adalah YOLOX COCO apa adanya, bertujuan "belajar"; K48
  mensyaratkan modifikasi. Penggantinya, K1 (`data/keluaran/kendaraan-jualan-k1`), adalah YOLOX-Tiny-640 yang dilatih ulang dari bobot
  COCO. Tujuannya jualan, dan `tools/periksa-jualan.mjs` memberi tanda `BOLEH-PRODUK` (safetensors dan ONNX).
- **Rantai tidak menjadi lebih buruk; di uji sedikit lebih baik:**
  - tangkapan uji: dibaca benar 22 → **24 dari 34** (mobil 13 → 14, motor 9 → 10); plat ditemukan 34 → 35 dari 39;
  - per plat: 1 salah → benar, 1 tak ditemukan → benar, **0 benar → salah**;
  - rentang masih tumpang tindih (48–79% lawan 54–83%), jadi naiknya belum pasti.
- **Plat yang punya kendaraan pemuat:** sisi latih 135 → 138 dari 141, uji 38 → 39 dari 39. Kotak di luar label di sisi latih 6 → 0.
- **Jenis tidak dikenali pencari ini.** Pencari dibuat satu kelas ("kendaraan"), dan jenis pindah ke Rencana 33 bersama warna dan merek.
  Alasannya di rencana: dataset Roboflow praktis melabeli satu kendaraan per gambar, dan pikap serta bus hampir tidak ada datanya.

## Bahan: label dilengkapi pencari lama

Dataset Roboflow hanya melabeli sebagian kendaraan. Karena itu label dilengkapi kotak "guru", yaitu pencari COCO lama, yang yakin ≥ 0,4
dan tidak menimpa label (IoU < 0,5). Nama berkas baru dibuat dari SHA-256 nama asli, karena nama berkas dataset bisa memuat nomor plat.

| Sumber | Sisi | Gambar | Kotak label | Kotak guru |
|---|---|---|---|---|
| vehicle and license plate (cars, motorcyle, truck) | latih (train + test) | 5.123 | 5.506 | 9.274 |
| | validasi | 432 | 465 | 868 |
| Merk dan Warna Motor (maks. 250 per kelas) | latih | 2.826 (4.730 dibatasi) | 2.826 | 934 |
| | validasi (maks. 50 per kelas) | 466 | 466 | 128 |
| Bingkai CCTV `cctv-fase1` (hanya K2) | latih | 864 | 0 | 3.410 |
| | validasi | 172 | 0 | 695 |

Kotak guru di "vehicle and license plate" (9.274) lebih banyak dari kotak labelnya (5.506). Itu membenarkan bahwa dataset itu hanya
melabeli sebagian kendaraan. Kotak plat (3.747 di latih, 320 di validasi) dan poligon plat (1.637 dan 143) dibuang.

## Pelatihan

| Calon | Gambar latih | Zaman terbaik (dari 15) | F1 validasi | Menit | ONNX = torch |
|---|---|---|---|---|---|
| K1 | 7.949 | 15 | 0,929 | 66,3 | 20 / 20 |
| K2 (+ bingkai CCTV) | 8.813 | 13 | 0,905 | 74 | 20 / 20 |

Bobot COCO dimuat 456 tensor; 6 dilewati, yaitu kepala kelas (80 kelas → 1 kelas). Bahan K1: dataset Roboflow vehicle and license plate,
Merk dan Warna Motor, dan bobot-yolox. Bahan K2 ditambah video riset, plat-lighting, dan plat buatan. Semuanya `BOLEH-PRODUK`.

## Memilih (aturan di rencana sebelum angka; pilihan di-commit `de3df13` sebelum uji dibuka)

Rantai tangkapan sisi latih: pencari plat C1 ambang 0,25, pembaca R4 ONNX, kendaraan dengan cadangan gambar utuh.

| Calon | Dibaca benar (125) | Ditemukan (141) | Kotak di luar label | Plat berkendaraan (141) |
|---|---|---|---|---|
| K0 pencari COCO 0,25 (pembanding) | 112 | 129 | 6 | 135 |
| **K1 0,25** | **115** | 130 | 0 | **138** |
| K1 0,4 | 115 | 130 | 0 | 137 |
| K2 0,25 | 114 | 127 | 4 | 135 |
| K2 0,4 | 113 | 127 | 5 | 134 |

K1 0,25 dan 0,4 seri di dibaca benar. Serinya dipecah plat berkendaraan (138 lawan 137). Syarat dipakai terpenuhi: tidak lebih rendah dari
K0. Bingkai CCTV (K2) tidak menolong. Kotak gurunya berasal dari pencari lama, jadi bingkai itu tidak membawa pengetahuan baru.

Angka bacaan sisi latih terlalu baik, karena pembaca R4 dilatih dengan potongan sisi latih. Perbandingan antarpencari tetap adil karena
pembacanya sama.

## Ditetapkan dan diukur sekali di uji

`kendaraan.py tetapkan kendaraan-jualan-k1 --ambang 0.25` menulis `kendaraan.json`, terikat ke SHA-256 `mesin.onnx`. Rantai uji dijalankan
lewat baris perintah `baca_gambar` biasa, yang memuat ambang dari berkas itu.

| | Mobil (16) | Motor (18) | Semua (34) | Rentang 95% | Ditemukan (39) |
|---|---|---|---|---|---|
| Rencana 30 (pencari COCO) | 13 | 9 | 22 | 48–79% | 34 |
| **Rencana 32 (K1)** | **14** | **10** | **24** | 54–83% | 35 |

- Perpindahan per plat: mobil benar → benar 13, **salah → benar 1**, salah → salah 1, tak ditemukan 1. Motor benar → benar 9, salah →
  salah 6, **tak ditemukan → benar 1**, tak ditemukan 2.
- Kotak kendaraan yang lain membuat potongan tempat plat dicari ikut berubah. Kotak plat terhadap label owner: IoU median motor 0,827 dan
  mobil 0,856.
- Plat berlabel sisi uji yang punya kendaraan pemuat: K0 38, **K1 39** dari 39.

## Batas

- Kotak guru berasal dari pencari COCO, jadi pencari baru sebagian belajar dari pencari lama. Perbaikannya kemungkinan datang dari kotak
  berlabel Roboflow, tetapi itu belum dipisahkan.
- Tangkapan uji kecil (34 plat berteks); selisih 2 plat ada di dalam rentang kebetulan.
- Kecepatan tidak diukur. Susunannya sama dengan pencari lama (YOLOX-Tiny-640), jadi waktunya diperkirakan sama, tetapi itu belum
  dibuktikan.
- Pencari baru tidak memberi jenis. Usulan jenis di halaman ciri kelak harus datang dari pengenal ciri (Rencana 33).
- Bukan rekaman gerbang.

**Cara membalik:** jalankan rantai dengan folder kendaraan `data/keluaran/kendaraan-yolox-coco` (rantai belajar). Tidak ada kode yang perlu
diubah.
