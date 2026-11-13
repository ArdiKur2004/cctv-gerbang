# Pencari plat cctv1 dilatih lanjut dengan tangkapan owner (Rencana 25 Task 5, 19 Okt 2026)

> Hitungan saja. Gambar, potongan, teks plat, dan nama berkas tidak ada di repo (CLAUDE.md §4). Angka dibaca dari layar dan JSON
> `data/alat-sementara/pilih-pencari-25.py` dan `ukur-pencari-25.py`, disalin ke `bukti/2026-10-19-pencari-cctv2-pilih.json` dan
> `bukti/2026-10-19-pencari-cctv2-ukur.json`.

## Calon dan bahan

Semua calon berangkat dari cctv1 (`pencari-yolox-nano-640-cctv1`, YOLOX-Nano-640) lewat `latih_yolox.py --bobot-awal-mesin`, 60 zaman,
tanpa membaca bobot COCO lagi. Tujuan mesin `jualan` (K47–K49: semua bahannya `BOLEH-PRODUK`).

| Calon | Bahan latih | Gambar latih | Zaman terbaik | Menit |
|---|---|---|---|---|
| C0 | cctv1 apa adanya | — | — | — |
| C1 | cctv-fase1 utuh (471) + plat-lighting (393) + tangkapan latih (108) | 972 | 28 | 44,1 |
| C2 | sama dengan C1, tanpa 225 gambar video tanpa kotak | 747 | 41 | 35,4 |

Validasi gabungan, sama persis untuk ketiganya (diperiksa sidik SHA-256 nama, isi gambar, dan label): cctv-fase1 valid 88, plat-lighting
valid 84, tangkapan validasi 31; 203 gambar, 179 plat.

## Memilih (aturan ditulis sebelum angka dilihat)

F1 tertinggi pada ambangnya sendiri di validasi gabungan, semuanya dinilai dengan alat yang sama (ONNX lewat `PencariYolox`,
`deteksi.kumpulkan`, `pilih_ambang`, `f1`). Bila seri, C0.

| Calon | F1 | Ambang | Plat ditemukan | Kotak palsu |
|---|---|---|---|---|
| C0 | 0,8971 | 0,5 | 157/179 | 14 |
| **C1** | **0,9257** | 0,6 | 162/179 | 9 |
| C2 | 0,9244 | 0,65 | 165/179 | 13 |

**Terpilih: C1** (`data/keluaran/pencari-cctv2-c1`). F1 lewat ONNX sama dengan F1 torch saat latihan (0,9257 dan 0,9244); ekspor ONNX
C1 dan C2 sama dengan torch pada 20 dari 20 gambar. `tools/periksa-jualan.mjs` pada `mesin.json` dan `mesin-onnx.json` C1 dan C2:
`BOLEH-PRODUK` (bahan: plat-lighting, bobot YOLOX, video riset, plat buatan, tangkapan owner).

- C1 dan C2 hampir seri (selisih 0,0013). C2 menemukan 3 plat lebih banyak, tetapi membuat 4 kotak palsu lebih banyak. Jadi membuang
  225 gambar tanpa kotak (dugaan Rencana 19) tidak terbukti menolong atau merugikan dengan jelas.
- F1 C0 di validasi gabungan (0,8971) lebih rendah dari F1 lamanya (0,9236), karena validasi kini memuat tangkapan.

## Diukur sekali di uji

Ambang dipilih di validasi gabungan yang sama untuk semua calon, lalu dipakai sekali di uji. Plat dicari di **gambar utuh** (tanpa
tahap kendaraan), IoU minimal 0,5.

| Pencari | Tangkapan uji: ditemukan dari 39 | Rentang 95% | Kotak palsu | Plat-lighting uji: ditemukan dari 102 | Rentang 95% | Kotak palsu |
|---|---|---|---|---|---|---|
| C0 (cctv1) | 16 | 0,271–0,566 | 1 | 96 | 0,878–0,973 | 10 |
| Nano-640 (COCO + plat-lighting) | 24 | 0,459–0,751 | 5 | 96 | 0,878–0,973 | 14 |
| D1 (dari nol, Rencana 24) | 31 | 0,645–0,892 | 5 | 93 | 0,841–0,953 | 16 |
| **C1 (terpilih)** | **35** | 0,764–0,959 | 1 | 94 | 0,853–0,960 | 8 |

- Di tangkapan, C1 menemukan 35 dari 39 plat di gambar utuh; cctv1 hanya 16. Semua 39 plat tangkapan uji terhitung "besar" dan
  "terang" menurut `deteksi.py`.
- Di plat-lighting, C1 turun 2 plat dari C0 (96 → 94), masih di dalam rentang kebetulan. Plat kecil 12 dari 16 di keduanya.

## Batas

- **Kotak label tangkapan** untuk plat yang ditemukan rantai lama berasal dari kotak rantai lama (cctv1 di dalam kendaraan). Bias ini
  menguntungkan C0, bukan C1.
- Tangkapan uji kecil (38 gambar, 39 plat), diambil owner saat platnya terlihat; bukan rekaman gerbang.
- Angka di sini untuk gambar utuh. Di rantai, plat dicari di dalam potongan kendaraan; itu diukur di Task 7.
- 202 gambar tempel cctv-fase1 berasal dari bingkai tanpa temuan pencari lama, jadi bisa menyembunyikan plat sungguhan; keduanya tetap
  ada di C1 dan C2.
- Selisih C1 dan C2 di validasi terlalu kecil untuk menyimpulkan apa pun tentang gambar tanpa kotak.
