# Fase 1, Rencana 16: Video CCTV gelombang ketiga (K36) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37): tanpa menunggu "Jalankan". Berhenti hanya di Task 4 Step 2 (lembar gambar kecil diperiksa owner
> lebih dulu, K19).

**Goal:** Bahan tolak ukur Fase 1 (spec Fase 1 bagian 1–2): video CCTV yang diunduh terarah, dari gerbang berbagai tempat dan
parkiran gedung dengan motor, siang dan malam. Video diperiksa utuh, dicatat di manifes, dipilah dari gambar kecil yang buram
(K19), lalu dibagi latih/uji per video.

**Architecture:**
- **Pintu unduh yang ada** (`tools/ambil-video.ps1`): `cari` hanya mendaftar, dan `unduh` mengambil video dengan sisi terpendek
  paling besar 1080, supaya plat lebih tajam daripada bawaan 720.
- **Alat yang ada:** `tools/lab/periksa_utuh.py`, `tools/manifes-video.mjs`, dan `tools/lab/lembar_kecil.py`.
- **Ubah:** nilai `sudut` baru `parkiran` di manifes (spec Fase 1: jenis tempat dilaporkan).
- **Baru:** `tools/bagi-video.mjs` membagi video ke latih/uji per video secara tetap.

**Tech Stack:** PowerShell (pintu Docker), Node, Python di lab.

---

## Aturan

- **Pencarian dan pilihan dari judul**, yaitu teks publik.
  - Dipilih: video kamera diam yang judulnya menyebut CCTV atau kamera di gerbang, portal, palang, pintu masuk, pos satpam,
    parkir, atau basement.
  - Utamakan Indonesia, ditambah sebagian luar negeri untuk ragam kamera.
  - Lama 20 detik sampai 30 menit.
  - Tidak dipilih: video yang sudah ada di manifes, siaran langsung, dan kompilasi berita dengan tulisan menutupi gambar
    (sebisanya dari judul).
- **Satu unduhan pada satu waktu**, di latar dengan log. Berhasil atau tidaknya dinilai dari berkas yang utuh
  (`periksa_utuh.py`), bukan dari kode keluar (temuan K20).
- **Gambar video tidak dibuka agen.** Lembar gambar kecil (sisi 48 px, dikaburkan) baru dibuka agen sesudah owner
  memeriksanya (K19, `CLAUDE.md` §7).

## Kueri pencarian (masing-masing 15 hasil)

1. `cctv gerbang perumahan mobil masuk`
2. `cctv pintu gerbang rumah mobil`
3. `cctv portal parkir mobil masuk`
4. `cctv palang parkir`
5. `cctv pos satpam gerbang`
6. `cctv gerbang sekolah`
7. `cctv apartemen pintu masuk mobil`
8. `cctv kantor parkir mobil`
9. `cctv parkir motor gedung`
10. `cctv basement parkir motor`
11. `cctv parkiran motor malam`
12. `cctv gerbang malam mobil`
13. `cctv infrared parkiran`
14. `license plate recognition camera gate entrance`
15. `parking garage cctv motorcycle`
16. `ANPR camera footage parking entrance`

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/manifes-video.mjs`, `tools/uji/manifes-video.test.mjs` (ubah) | `sudut` boleh `parkiran` | 1 |
| `data/keluaran/cari-gelombang-3/` (keluaran) | Daftar hasil pencarian | 2 |
| `data/alat-sementara/pilih-gelombang-3.txt` (sekali pakai) | Id video yang dipilih | 2 |
| `data-asal/video-riset.json` (ubah, lewat alat) | Video baru dan pemilahannya | 3, 4 |
| `tools/bagi-video.mjs`, `tools/uji/bagi-video.test.mjs` (baru) | Pembagian latih/uji per video | 5 |
| `data-asal/pembagian-video-fase1.json` (baru, lewat alat) | Hasil pembagian | 5 |

---

### Task 1: `sudut` parkiran

- [x] **Step 1: Uji merah.** Di `tools/uji/manifes-video.test.mjs`, daftar uji sudut yang diterima ditambah `'parkiran'`:

```js
for (const sudut of ['gerbang', 'parkiran', 'kamera-diam-lain', 'dasbor', 'lain']) {
```

Run: `npm test; echo "EXIT=$?"` → Expected: satu uji gagal (`sudut "parkiran" diterima`), `EXIT=1`.

- [x] **Step 2: Ubah `tools/manifes-video.mjs`.** Nilai sah dan keterangannya:

```js
const SUDUT_SAH = new Set(['', 'gerbang', 'parkiran', 'kamera-diam-lain', 'dasbor', 'lain']);
```

Pada komentar kepala berkas, keterangan `kamera-diam-lain` diganti menjadi "kamera diam di jalan atau tempat lain, bukan di
gerbang atau parkiran", dan `parkiran` ditambahkan sebagai "kamera diam di parkiran gedung atau basement".

Run: `npm test; echo "EXIT=$?"` → Expected: `pass 112`, `EXIT=0`.

- [x] **Step 3: Commit** dengan alasan (spec Fase 1: jenis tempat dilaporkan; K36 parkiran motor) dan gerbang Node 111 → 112.

### Task 2: Cari dan pilih

- [x] **Step 1: Cari.** Untuk tiap kueri:
  `powershell -NoProfile -File tools\ambil-video.ps1 cari "<kueri>" 15 > data\keluaran\cari-gelombang-3\<nomor>.txt`
  Satu per satu.
- [x] **Step 2: Pilih dari judul** menurut aturan di atas. Tulis id terpilih ke `data/alat-sementara/pilih-gelombang-3.txt`,
  satu per baris dengan kueri asalnya. Sasaran 60–90 video. Jumlah per kueri dicatat.

### Task 3: Unduh, periksa utuh, catat

- [x] **Step 1: Unduh (di latar, log).** Skrip sekali pakai `data/alat-sementara/unduh-gelombang-3.ps1` memanggil
  `tools\ambil-video.ps1 unduh https://www.youtube.com/watch?v=<id> 1080` untuk tiap id. Skrip mencatat kode keluar per id
  dan tidak berhenti pada satu kegagalan.
- [x] **Step 2: Periksa utuh** di lab:
  `tools\lab.ps1 python /kerja/tools/lab/periksa_utuh.py /kerja/data/video/riset /kerja/data/keluaran/video-utuh.json`.
  Berkas yang tidak utuh dihapus dan dicatat sebagai gagal.
- [x] **Step 3: Catat di manifes:** `node tools/manifes-video.mjs; echo "EXIT=$?"`. Expected: `EXIT=0`. Jumlah video baru
  sama dengan jumlah yang lulus pemeriksaan utuh.

### Task 4: Pilah (K19)

- [x] **Step 1: Lembar gambar kecil** untuk video baru saja:
  `tools\lab.ps1 python /kerja/tools/lab/lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil-3 /kerja/data/keluaran/lembar-kecil /kerja/data/keluaran/lembar-kecil-2`
- [x] **Step 2: BERHENTI. Owner memeriksa lembar-kecil-3** di laptop: tidak ada plat yang terbaca. Bila ada, lembarnya dibuat
  ulang lebih kecil atau lebih kabur, dan diperiksa lagi.
- [x] **Step 3: Agen memilah** dari lembar yang sudah diperiksa:
  - `sudut`: gerbang, parkiran, kamera-diam-lain, dasbor, atau lain;
  - `kategori`: siang, malam, remang, campuran, atau tak-jelas;
  - `isi`: satu kalimat.

  Isiannya ditulis ke manifes dengan skrip pencatat (jangkar tepat sekali), lalu `node tools/manifes-video.mjs` dijalankan
  lagi dan harus `EXIT=0`.

### Task 5: Bagi latih dan uji per video

- [x] **Step 1: Uji merah** `tools/uji/bagi-video.test.mjs`:
  - hanya `sudut` gerbang, parkiran, dan kamera-diam-lain yang dibagi;
  - pembagian tetap untuk masukan yang sama, dan tidak berubah bila video baru ditambahkan, karena tiap video ditentukan dari
    SHA-256 id-nya sendiri;
  - kira-kira separuh ke uji; hitungan per lapis (`sudut` × `kategori`) dilaporkan;
  - tidak ada video di dua sisi;
  - CLI menulis berkas dan mencetak hitungan per lapis.
- [x] **Step 2: Tulis `tools/bagi-video.mjs`.** Tiap video ditentukan dari SHA-256 "fase1/<berkas>"-nya sendiri: huruf
  heksadesimal pertama 0–7 masuk uji, dan 8–f masuk latih. Keluaran `data-asal/pembagian-video-fase1.json`: `{ aturan, uji:
  [berkas], latih: [berkas], per_lapis }`.
  *Dikoreksi sebelum dijalankan (16 Okt):* versi awal mengurutkan per lapis lalu mengambil separuh pertama. Itu bertentangan
  dengan "tidak berubah bila video baru ditambahkan": menambah video menggeser batasnya, sehingga video yang pernah di sisi
  uji bisa pindah ke latih dan membocorkan set uji. Akibatnya keseimbangan per lapis tidak dijamin. Hitungannya dilaporkan,
  dan lapis yang timpang ditulis sebagai batas.
  Run: `npm test; echo "EXIT=$?"` → Expected: `pass` bertambah sebanyak uji baru, `EXIT=0`.
- [x] **Step 3: Jalankan** pada manifes sungguhan, lalu commit alat, uji, dan pembagiannya.

### Task 6: Catatan

- [x] **Step 1:** Laporan singkat `bukti/<tanggal>-video-cctv-gelombang-3.md`, berisi:
  - kueri, jumlah dipilih, terunduh, dan utuh;
  - hasil pemilahan per sudut dan kategori;
  - pembagian per lapis;
  - batas.
- [x] **Step 2:** `ROADMAP.md` (butir, status, changelog) dan `CLAUDE.md` §7 (nilai `sudut` parkiran; pembagian video Fase 1).
  Gerbang penuh, lalu commit. Lanjut ke Rencana 17 (K37).
