# Pembaca dummy 1: uji jalur latih plat motor modif di laptop baru (K78, K79, 15 Nov 2026)

> Hitungan saja. Gambar, potongan, CSV berteks plat, dan bobot tinggal di `data/keluaran/pembaca-dummy-1/` (di-gitignore, CLAUDE.md §4).
> **Bukan model jualan, tidak dipasang di rantai.** Tujuannya membuktikan jalur latih → nilai berjalan di laptop ini sambil menunggu
> bobot `pembaca-lanjut-r4` dan bahan latih asli dari laptop lama.

## Jalur

- Laptop `Miil-TUF`, RTX 3050 Ti 4 GB, tanpa Docker lab. Venv `data/alat-sementara/venv-fpo` (system-site-packages untuk torch 2.11+cu128),
  versi paket sama dengan `tools/lab-fpo/requirements.txt` (keras 3.15.1, albumentations 2.0.8, …). **Batas:** hash di requirements dibuat untuk
  Linux/py3.12, jadi di Windows dipasang dengan versi yang sama tanpa `--require-hashes`.
- `vendor/fast-plate-ocr` lewat `tools/klon-terkunci.ps1` (@ 9ce7a5b, cocok kunci).
- Bobot publik `cct_s_v2_global.keras` + dua konfigurasi diunduh dari URL di `tools/vendor.lock.json`; ketiga SHA-256 cocok dengan kunci.
  Termuat utuh 192/192 tensor lewat jalur perintah latih.
- Skrip: `tools/lab/pembaca_dummy.py` (memakai fungsi `latih_fpo.py` apa adanya) dan `tools/lab/lembar_beda.py`.

## Bahan

| | Jumlah |
|---|---|
| Latih: plat-modif-1 / plat-modif-acuan-1 / plat-tempel-1 | 450 / 450 / 483 = 1.383 |
| Validasi (sama, dari ketiga set) | 50 / 50 / 53 = 153 |
| Teks validasi yang juga ada di latih | 0 |
| Nilai plat polos: potongan kotak `dummy-1` | 200 |
| Nilai Bardi: baris `status = yakin` di `data/cctv bardi/hasil-baca.csv` | 62 |

Semua plat sintetis memakai kolom `plate_region = Indonesia` (tanpa kolom itu kepala wilayah terbuang diam-diam, Rencana 9).

## Latihan

60 zaman, laju 0,0001, angkatan 64, benih 0. Zaman terbaik 52, `val_plate_acc` 0,7367.

## Hasil (ambang yakin 0,8 seperti `baca_lokal.py`)

| Set | Publik benar | Dummy benar | Yakin-tetapi-salah publik → dummy |
|---|---|---|---|
| Plat modif sintetis (153) | 40 | 104 | 4 dari 31 → 3 dari 75 |
| Plat polos sintetis (200) | 100 | 165 | 9 dari 88 → 3 dari 152 |
| Bardi "yakin" (62) | 62 (menurut definisi) | 54 sama, 8 berbeda | — → 1 dari 47 |

Bardi per tipe (sama dengan publik / jumlah): Vario 125 9/15, Vario 150 19/20, Supra X 125 26/27.

## Cara membaca

- Label Bardi "yakin" adalah **tebakan pembaca publik itu sendiri**, jadi publik pasti 62/62; angka dummy di sana hanya mengukur seberapa
  sering dummy **berbeda**, bukan benar/salah. 8 plat yang berbeda dikirim ke owner lewat `periksa-beda.html` (lokal).
- Plat polos ikut naik karena huruf kisinya sama dengan bahan latih sintetis. Kenaikan di sintetis belum bukti untuk kamera asli.
- Yang memberi harapan: yakin-tetapi-salah turun di kedua set sintetis.

## Langkah berikutnya

1. Jawaban owner atas 8 plat berbeda → apakah sintetis membantu plat motor asli.
2. Bobot `pembaca-lanjut-r4`, `fpo-indo-1`, `data/unduhan`, INDO-ALPR, tangkapan owner dari laptop lama → latih lanjut dari r4 dengan
   campuran asli + sintetis; dibandingkan dengan r4, bukan dengan publik.
3. Label manusia untuk 173 plat Bardi menggantikan 62 label sementara.
