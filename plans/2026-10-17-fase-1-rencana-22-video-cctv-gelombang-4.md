# Fase 1, Rencana 22: Video CCTV gelombang keempat (K41) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Berhenti sekali: lembar gambar kecil diperiksa owner lebih dulu (K19).

**Goal:** Plat yang bisa dinilai bertambah, supaya perbaikan berikutnya bisa dibedakan dari kebetulan. Di Rencana 19–21, plat
yang bisa dinilai per lembar hanya 18–23, hampir semuanya mobil siang. Gelombang keempat dicari terarah ke tiga kekurangan:
- gerbang tempat kendaraan berhenti dekat kamera (plat besar dan jelas);
- gerbang dan parkiran motor;
- malam atau inframerah.

**Architecture:** Semua alat sudah ada sejak Rencana 16; rencana ini tidak menambah kode.
- `tools/ambil-video.ps1` (`cari`, `unduh` dengan sisi terpendek paling besar 1080);
- `tools/lab/periksa_utuh.py`;
- `tools/manifes-video.mjs`;
- `tools/lab/lembar_kecil.py` (hanya video yang belum ada di lembar kecil 1–3);
- `tools/bagi-video.mjs`. Tiap video dibagi menurut SHA-256-nya sendiri, jadi video lama tidak berpindah sisi.

**Tech Stack:** PowerShell (pintu Docker), Node, Python di lab.

---

## Yang diukur sebelum rencana ini ditulis (17 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Plat yang bisa dinilai per lembar uji | R19 23, R20 19, R21 18; hampir semuanya mobil siang | Laporan Rencana 19–21 |
| Lembar bingkai | Owner: banyak bingkai "terlalu buram atau terlalu jauh" | Jawaban owner Rencana 20–21 |
| Video Fase 1 | 41 uji, 39 latih (gelombang ketiga) | `data-asal/pembagian-video-fase1.json` |

## Aturan

- **Pencarian dan pilihan dari judul**, yaitu teks publik. Aturan pilihan sama dengan Rencana 16:
  - kamera diam, lama 20 detik sampai 30 menit;
  - bukan video yang sudah ada di manifes, bukan siaran langsung, dan bukan kompilasi berita.
- **Diutamakan judul yang menyebut** plat, palang, portal, karcis, gardu, atau tempat kendaraan berhenti, juga motor, malam,
  atau inframerah.
- **Satu unduhan pada satu waktu,** di latar dengan log. Hasilnya dinilai dari berkas yang utuh, bukan dari kode keluar.
- **Gambar video tidak dibuka agen.** Lembar gambar kecil baru dibuka sesudah owner memeriksanya (K19).
- **Pembagian latih/uji memakai alat yang sama.** Sesudahnya, semua video lama harus tetap di sisinya; ini diperiksa dengan skrip
  pembanding. Angka di 41 video uji lama tetap dilaporkan terpisah di putaran berikutnya.

## Kueri pencarian (masing-masing 15 hasil)

1. `cctv palang parkir mobil berhenti plat nomor`
2. `cctv portal parkir karcis mobil masuk`
3. `cctv gerbang tol mobil`
4. `cctv pintu masuk mall parkir mobil`
5. `cctv gerbang perumahan mobil berhenti`
6. `cctv pos satpam mobil berhenti`
7. `cctv portal parkir motor`
8. `cctv parkir motor masuk karcis`
9. `cctv motor masuk gerbang perumahan`
10. `cctv motor masuk parkiran kampus`
11. `cctv malam mobil masuk gerbang rumah`
12. `cctv malam motor masuk perumahan`
13. `cctv infrared mobil malam`
14. `license plate recognition indonesia`
15. `parking barrier gate camera license plate`
16. `ANPR camera motorcycle entrance`

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `data/keluaran/cari-gelombang-4/` (keluaran) | Daftar hasil pencarian | 1 |
| `data/alat-sementara/pilih-gelombang-4.txt` (sekali pakai) | Id video yang dipilih | 1 |
| `data-asal/video-riset.json` (ubah, lewat alat) | Video baru dan pemilahannya | 2, 3 |
| `data-asal/pembagian-video-fase1.json` (ubah, lewat alat) | Pembagian, video lama tetap di sisinya | 4 |
| `bukti/<tanggal>-video-cctv-gelombang-4.md` | Laporan | 5 |

---

### Task 1: Cari dan pilih

- [x] **Step 1:** Docker menyala (`docker version`). Cari dengan skrip sekali pakai `data/alat-sementara/cari-gelombang-4.ps1`, satu
  kueri pada satu waktu. Keluaran: `data/keluaran/cari-gelombang-4/NN.txt`.

  *Hasil (17 Okt):* ke-16 kueri `kode=0`, masing-masing 15 hasil.
  - **Penyimpangan:** kueri malam 11–13 hanya memberi video hantu, tutorial kamera, dan ulasan produk. Karena itu 3 kueri malam
    ditambahkan (`cari-gelombang-4-malam.ps1`, keluaran 17–19):
    - 17: `maling motor malam hari terekam cctv parkiran`;
    - 18: `rekaman cctv malam hari mobil masuk komplek`;
    - 19: `cctv parkir basement malam mobil keluar`.
- [x] **Step 2:** Pilih dari judul menurut aturan di atas. Tulis id terpilih ke `data/alat-sementara/pilih-gelombang-4.txt`,
  satu per baris dengan kueri asalnya. Sasaran 60–90 video. Jumlah per kueri dicatat.

  *Hasil:* **86 video dipilih** (`daftar-cari-4.mjs` menandai yang sudah ada di manifes, yang kembar, dan yang di luar 20 detik
  sampai 30 menit).

  | Kueri | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | Dipilih | 1 | 4 | 3 | 3 | 6 | 1 | 3 | 9 | 4 | 9 | 0 | 0 | 0 | 7 | 9 | 10 | 10 | 5 | 2 |

  - **Banyak yang dibuang** adalah berita kecelakaan di jalan, video hantu, tutorial, dan ulasan produk.
  - **Demo kamera pembaca plat dan palang parkir** (kueri 14–16) kemungkinan memberi plat yang dekat dan jelas, tetapi sebagian
    di luar negeri (Vietnam, Thailand, dan lain-lain), dengan plat yang tidak berpola Indonesia.
  - **Malam** belum pasti. Kueri 17–18 berisi rekaman pencurian dari kamera diam; malam atau tidaknya baru terlihat saat
    pemilahan.

### Task 2: Unduh, periksa utuh, catat

- [x] **Step 1:** Unduh di latar dengan log (`data/alat-sementara/unduh-gelombang-4.ps1`, satu per satu). Kode keluar dicatat per
  id, dan skrip tidak berhenti pada satu kegagalan.

  *Hasil (17 Okt, 11.33–11.56):* 82 `kode=0` dan 4 `kode=1`.
- [x] **Step 2:** `periksa_utuh.py` di lab. Berkas yang tidak utuh dihapus dan dicatat sebagai gagal.

  *Hasil:* 259 utuh, 0 bermasalah (177 lama + 82 baru). Tidak ada berkas `.part` atau `.ytdl` tersisa. Jadi 4 video yang gagal
  memang tidak terunduh.
- [x] **Step 3:** `node tools/manifes-video.mjs; echo "EXIT=$?"` → `EXIT=0`. Jumlah video baru sama dengan jumlah yang utuh.

  *Hasil:* 259 video di manifes (`EXIT=0`), 82 di antaranya baru. Enam video lama dari 13 Okt sudah tanpa `sudut` sejak dulu, dan
  tidak disentuh di sini.

### Task 3: Pilah (K19)

- [x] **Step 1:** Lembar gambar kecil untuk video baru saja:
  `lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil-4 /kerja/data/keluaran/lembar-kecil /kerja/data/keluaran/lembar-kecil-2 /kerja/data/keluaran/lembar-kecil-3`.

  *Dikoreksi saat menjalankan:* lembar lama diberikan sebagai `.../ikhtisar.json`, bukan foldernya. Dengan folder, alat menolak
  (`IsADirectoryError`, kode 2) tanpa membuat lembar apa pun.

  *Hasil:* 82 video di 6 lembar `data/keluaran/lembar-kecil-4/`; 177 dilewati karena sudah ada di lembar lama.
- [x] **Step 2: BERHENTI.** Owner memeriksa `lembar-kecil-4` di laptop: tidak boleh ada plat yang terbaca.

  *Hasil (17 Okt):* owner: "saya sudah periksa, dan tidak ada yang bisa terbaca".
- [x] **Step 3:** Agen memilah dari lembar yang sudah diperiksa: `sudut`, `kategori`, dan `isi`. Isiannya ditulis dengan skrip
  pencatat (jangkar tepat sekali), lalu manifes diperiksa lagi (`EXIT=0`).

  *Hasil:* `catat-pilah-gelombang-4.mjs` (gagal tertutup; tiap nomor tepat satu video yang belum dipilah).
  - gerbang 26, parkiran 22, kamera diam lain 17, lain 17;
  - tanpa "lain": siang 46, malam 7, remang 5, campuran 4, tak jelas 3;
  - manifes `EXIT=0`.

### Task 4: Bagi latih dan uji

- [x] **Step 1:** Salin pembagian lama ke `data/alat-sementara/pembagian-video-fase1-r21.json`, lalu
  `node tools/bagi-video.mjs`.
- [x] **Step 2:** Skrip pembanding: semua video lama harus tetap di sisinya (uji tetap uji, latih tetap latih). Bila ada satu saja
  yang pindah, berhenti dan cari sebabnya sebelum commit.
- [x] **Step 3:** Catat hitungan per lapis (sudut × kategori) untuk video baru dan untuk semua video.

  *Hasil:*
  - `banding-pembagian-22.mjs`: video lama yang pindah atau hilang: **0**.
  - **Uji:** 41 → 77. **Latih:** 39 → 68.
  - **Video baru:** uji 36, latih 29. Hitungan per lapis ada di laporan.
  - **Malam di sisi uji sesudahnya:** gerbang 1, parkiran 1, kamera diam lain 3.

### Task 5: Catatan

- [x] **Step 1:** Laporan `bukti/<tanggal>-video-cctv-gelombang-4.md`:
  - kueri, jumlah dipilih, terunduh, dan utuh;
  - pemilahan per sudut dan kategori;
  - pembagian per lapis;
  - batas.
- [x] **Step 2:** ROADMAP, gerbang penuh, commit. Lanjut: rantai cara terbaik (Rencana 20) di set uji yang bertambah, untuk titik
  awal baru dengan lembar owner, lalu Rencana 23 (pembaca).
