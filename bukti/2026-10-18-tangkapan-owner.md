# Tangkapan layar owner dibaca mesin belajar dan diperiksa owner (Rencana 24 Bagian A, 18 Okt 2026)

> Hitungan saja. Gambar, potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari layar
> `lembar_rantai.py nilai`, `data/alat-sementara/hitung-tangkapan-24.mjs`, `hitung-jawaban-24.mjs`, dan `ragu-vs-salah-24.mjs`.

## Bahan dan cara

- **Bahan:** 181 tangkapan layar CCTV dari owner (`tangkapan-owner`, `BOLEH-PRODUK`, K44): 76 mobil, 105 motor. Pembagian per isi
  berkas (`baca_gambar.sisi`): uji 38 gambar (mobil 16, motor 22), latih 143.
- **Mesin pengusul (mesin belajar, `RISET-SAJA`):** kendaraan YOLOX-Tiny COCO (ambang 0,25), plat dicari di dalam potongan
  kendaraan dengan pencari cctv1 (ambang 0,25), dibaca fpo-indo-1 ONNX. Ini konfigurasi terbaik Rencana 20.
- **Owner memeriksa dua lembar:** lembar plat (144 potongan beserta bacaan mesin) dan lembar gambar tanpa plat (46 gambar, kendaraan
  bernomor).
- Satu gambar diam tidak bisa dipungut suaranya, jadi semua bacaan berstatus "ragu"; kolom benar-yakin di `nilai.json` selalu 0
  dan tidak bermakna di sini.

## Hasil

### Bacaan pada plat yang ditemukan

| Kelompok | Sisi | Dinilai | Benar | Rentang 95% | Tak terbaca | Bukan plat |
|---|---|---|---|---|---|---|
| mobil | latih | 50 | 43 | 0,738–0,930 | 1 | 3 |
| mobil | uji | 14 | 12 | 0,601–0,960 | 0 | 0 |
| motor | latih | 50 | 34 | 0,542–0,792 | 9 | 3 |
| motor | uji | 12 | 9 | 0,468–0,911 | 2 | 0 |
| **mobil** | semua | 64 | 55 | 0,754–0,924 | | |
| **motor** | semua | 62 | 43 | 0,570–0,794 | | |
| **semua** | semua | 126 | 98 | 0,698–0,842 | 12 | 6 |

- Dari 144 kotak, 6 bukan plat.
- Pembaca di tangkapan (98 dari 126 benar) jauh lebih baik daripada di potongan video CCTV Rencana 23 (25 dari 52). Bacaan agen:
  tangkapan dipilih owner saat platnya terlihat, jadi lebih tajam daripada gambar yang diambil rantai dari video. Ini belum diukur.

### Plat yang terlewat

| Kelompok | Gambar dengan plat ditemukan | Gambar tanpa plat ditemukan, platnya terbaca owner | Di kendaraan berkotak | Kendaraannya tanpa kotak |
|---|---|---|---|---|
| mobil | 65 | 9 | 9 | 0 |
| motor | 69 (+1 gambar yang kotaknya hanya bukan plat) | 34 | 27 | 7 |

- Dari 46 gambar tanpa plat ditemukan: 43 gambar Indonesia platnya terbaca owner, 2 gambar kendaraan luar Indonesia dikeluarkan
  owner, dan 1 gambar dikeluarkan owner dari data.
- Di gambar yang memuat plat asli (platnya ditemukan, atau terlewat tetapi terbaca owner), tidak ada satu plat pun yang ditemukan
  pada mobil di 9 dari 74 gambar dan pada motor di 34 dari 103 gambar. Satu gambar motor yang kotaknya hanya bukan plat tidak
  dihitung. **Batas:** di 135 gambar berkotak owner tidak ditanya apakah ada plat lain yang terlewat.
- Pada 36 dari 43 gambar itu, kendaraannya sudah ditemukan tetapi platnya tidak. Jadi untuk motor, yang lemah adalah pencari plat.

### Kendaraan terdekat (K45)

Owner meminta kendaraan yang terdekat dari kamera dibaca lebih dulu. Ini diuji di lembar tanpa plat, pada gambar yang platnya terbaca
dan memuat lebih dari satu kendaraan berkotak (25 gambar). Kendaraan yang platnya terbaca owner adalah kendaraan dengan tepi bawah
terendah di gambar pada 23 dari 25 gambar, dan kendaraan dengan kotak terbesar juga pada 23 dari 25.

### Keraguan pembaca dan bacaan salah (untuk usulan owner soal huruf sensitif)

`yakin_baca` adalah peluang terendah di antara huruf satu plat. Ambang dibaca di sisi latih; sisi uji hanya pemeriksaan.

| Ragu bila yakin di bawah | Latih: salah tertangkap | Latih: benar ikut ditandai | Uji: salah tertangkap | Uji: benar ikut ditandai |
|---|---|---|---|---|
| 0,5 | 9 / 23 | 1 / 77 | 2 / 5 | 1 / 21 |
| 0,7 | 17 / 23 | 11 / 77 | 3 / 5 | 3 / 21 |
| 0,8 | 18 / 23 | 15 / 77 | 4 / 5 | 3 / 21 |
| 0,9 | 21 / 23 | 24 / 77 | 5 / 5 | 6 / 21 |
| 0,95 | 22 / 23 | 30 / 77 | 5 / 5 | 7 / 21 |
| 0,98 | 23 / 23 | 42 / 77 | 5 / 5 | 10 / 21 |

Mesin biasanya tahu kapan ia ragu: pada ambang 0,9 ia menandai 21 dari 23 bacaan salah di sisi latih. Harganya, 24 dari 77 bacaan
benar ikut ditandai. **Belum diketahui:** apakah keraguan itu jatuh pada pasangan huruf yang disebut owner (H/N, V/Y, O/Q, D/O,
N/K, N/M, W/M). Untuk itu dibutuhkan teks benar dari 28 baris yang salah.

### Label dari halaman pelabelan (Task 4)

Owner mengisi 71 butir halaman pelabelan (43 plat terlewat, 28 bacaan salah). Hasil `halaman_label.py terima`:

| Sisi | Gambar | Kotak plat | Dengan teks benar | Tak terbaca | Plat tanpa label | Bukan plat |
|---|---|---|---|---|---|---|
| latih | 140 | 141 | 125 | 16 | 1 | 6 |
| uji | 38 | 39 | 34 | 5 | 0 | 0 |

- 3 gambar dikeluarkan owner (2 kendaraan luar Indonesia, 1 atas permintaan owner). Tidak ada teks di luar pola.
- "Plat tanpa label" satu butir (butir 42 halaman): teksnya ada, kotaknya belum ditarik. Owner diminta melengkapinya.

**Huruf yang salah dibaca mesin** (`hitung-label-24.mjs`, penjajaran Levenshtein antara bacaan mesin dan teks owner; hanya
pasangan huruf yang dicetak):

- Dari 28 bacaan salah, owner menandai 4 tidak terbaca di halaman. Dari 24 sisanya, 14 salah satu huruf, 6 salah dua huruf, 3 salah
  tiga huruf atau lebih, dan 1 sama dengan bacaan mesin (di lembar disebut salah, di halaman diketik sama).
- Dari 35 huruf yang salah:
  - 11 ada di pasangan yang disebut owner (M→W 3, W→M 1, V→Y 3, Q→O 2, N→H 1, K→N 1);
  - 5 di huruf bulat lain (O→B 2, G→D, B→D, G→O);
  - 7 di angka (misalnya 3→5, 3→9, 8→0);
  - 12 lainnya tersebar.
- Jadi daftar huruf owner menjelaskan sepertiga kesalahan. Ini mendukung pemicu jalur cermat dari keraguan mesin per huruf (K46),
  bukan dari daftar huruf.

## Batas

- Tangkapan dipilih owner dari internet, bukan rekaman gerbang; angka ini bukan angka K9.
- Sisi uji kecil (26 bacaan dinilai); rentangnya lebar.
- ~~Teks benar untuk 28 bacaan salah dan kotak plat untuk 43 gambar yang terlewat belum ada.~~ Dilengkapi lewat halaman pelabelan
  (lihat di atas), kecuali satu kotak.
- Hitungan huruf salah berasal dari 24 bacaan saja.
- Di 135 gambar berkotak, owner tidak ditanya apakah ada plat lain yang terlewat. Gambar tanpa label tidak boleh dianggap bebas plat
  saat melatih pencari plat.
