# Fase 1, Rencana 23: Pembaca, dimulai dengan titik awal baru di 77 video uji — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Rencana ini ditulis dalam dua bagian:
> - **Bagian A**, titik awal, ditulis dan dijalankan lebih dulu.
> - **Bagian B**, pembaca, ditulis sesudah angka Bagian A ada dan sebelum Bagian B dijalankan, karena pilihan pembaca bergantung
>   pada jenis salah yang terlihat di titik awal.

**Goal (Bagian A):** angka rantai terbaik sejauh ini di set uji Fase 1 yang bertambah (77 video, Rencana 22). Angka ini menjadi
pembanding semua putaran berikutnya. Rantainya cara Rencana 20:
- pencari plat yang dilatih ulang;
- cara potong, ambang 0,25;
- tanpa saringan letak.

Angka di 41 video lama dilaporkan terpisah, supaya tetap bisa dibandingkan dengan Rencana 17–21.

**Architecture (Bagian A):** tanpa kode baru. Yang dipakai: `rantai.py jalan`, `lembar_rantai.py`, `lembar_bingkai.py --maks 80`,
dan skrip status per jenis yang memisahkan video lama dan baru.

**Tech Stack:** Python di image tambahan (`-Fpo`), CPU.

---

## Yang diukur sebelum rencana ini ditulis (17 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Set uji Fase 1 | 77 video: 41 lama dan 36 baru | `data-asal/pembagian-video-fase1.json`, laporan Rencana 22 |
| Rantai terbaik sejauh ini | Rencana 20 (potong, 0,25, tanpa letak). Di 41 video lama: 14 benar-yakin, 1 salah-yakin; "yakin" bukan plat 18 dari 43, dan semua 26 di Rencana 21 berasal dari 2 video | Laporan Rencana 20 dan 21 |
| Lama jalan | Rencana 20 di 41 video: 2 jam 25 menit | Rencana 20 Task 6 |

## Bagian A: Titik awal di 77 video uji

### Task 1: Rantai di 77 video uji

- [x] **Step 1:** Mesin tenang. Rantai `--kendaraan ... --cara potong --ambang 0.25` di sisi uji → `rantai-uji-fase1-r23`, di latar
  dengan perekam proses (`jalan-rantai-23-uji.ps1`).

  *Hasil (17 Okt, 13.36–16.25):*
  - 77 video, 65.046 gambar sampel.
  - **Kedatangan:** 529, dengan 131 yakin.
  - **Per kategori:** siang 516, remang 8, campuran 3, malam 2.
  - Uji sesi lain menyala di 327 dari 984 rekaman proses, jadi kecepatannya tidak dipakai.
- [x] **Step 2:** Lembar kedatangan (`--urut sha`, 120 baris) → `lembar-uji-fase1-r23`.
  - Lembar bingkai `--per-video 1 --maks 80 --kendaraan ... --cara potong --ambang 0.25` → `lembar-bingkai-fase1-r23`.
  - Bingkai 1–41 harus sama dengan lembar bingkai sebelumnya. Bingkai video baru menyusul menurut urutan nama berkas. Ini dicek
    dengan skrip tanpa melihat kotak per bingkai.

  **Batas yang sudah diketahui:** urutan bingkai menurut nama berkas, jadi bingkai video baru bisa terselip di antara bingkai
  lama dan menggeser nomornya. Skrip pembanding mencocokkan menurut video dan nomor gambar, bukan menurut nomor bingkai.

  *Hasil:*
  - Lembar kedatangan: 120 baris dari 529, di 6 halaman.
  - Lembar bingkai: 77 bingkai di 20 halaman.
  - `banding-bingkai-23.mjs`: ke-41 bingkai lama ada dengan video dan gambar yang sama (`EXIT=0`).
  - **Peta nomor lama → baru:** 1→2, 2→3, 3→4, 4→6, 5→9, 6→10, 7→11, 8→12, 9→13, 10→14, 11→15, 12→16, 13→21, 14→28, 15→31,
    16→33, 17→37, 18→38, 19→39, 20→40, 21→41, 22→45, 23→47, 24→48, 25→51, 26→52, 27→59, 28→60, 29→61, 30→62, 31→64, 32→65,
    33→66, 34→67, 35→68, 36→70, 37→71, 38→72, 39→75, 40→76, 41→77.

### Task 2: Owner memeriksa

- [x] **Step 1: BERHENTI.** Owner memeriksa kedua lembar dengan petunjuk Rencana 20.
- [x] **Step 2:** `nilai` keduanya. Status per jenis dihitung per sudut dan **dipisah antara video lama (41) dan baru (36)**
  (`status-per-jenis-23.py`).

  *Hasil (17 Okt).* Jawaban owner dipecah oleh `jawaban-23-uji.mjs`; isinya hanya nomor.
  - **Dua pertentangan diselesaikan dengan pilihan yang paling merugikan angka:** baris 101 (salah dan tak terbaca) dihitung
    salah, dan baris 23 (bukan plat dan tak terbaca) dihitung bukan plat.
  - **Lembar kedatangan:** bukan plat 51, tak terbaca 45, dinilai 24.
    - mobil 16: 11 benar-yakin, 5 benar-ragu, 0 salah;
    - motor 8: 3 benar-yakin, 4 salah-ragu, 1 salah-yakin.
  - **Lembar bingkai (77):** dinilai 20, terlewat 16; ketat: dinilai 9, terlewat 5.
  - **Sesudahnya:** di 41 bingkai lama, kotak identik dengan R20 (`banding-kotak-20-23.mjs`), tetapi penilaian owner pada
    beberapa bingkai yang sama berbeda dari R20.

### Task 3: Catat titik awal

- [x] **Step 1:** Pemeriksa bukti dengan kontrol positif, lalu salin hitungan.

  *Hasil:* `periksa-bukti-23.py`. Larangan 11.584; kontrol positif menemukan 1.850 dari minimal 1.845. Empat berkas bersih.
- [x] **Step 2:** Laporan singkat `bukti/<tanggal>-titik-awal-77-video.md`:
  - semua video;
  - 41 lama (pembanding Rencana 17–21);
  - 36 baru;
  - jenis salah (salah baca, tak terbaca, bukan plat) menurut sudut;
  - batas.
- [x] **Step 3:** ROADMAP, commit. Lalu tulis Bagian B (pembaca) menurut angka ini, sebelum dijalankan.

  *Ditahan (17 Okt):* bersama jawaban lembarnya, owner bertanya apakah produk ini akan laku dan apakah model masih perlu
  dilatih. Analisa bisnis (`docs/riset/2026-10-17-analisa-bisnis-cctv-gerbang.md`) menunjukkan bahwa kamera ANPR jadi seharga
  Rp 8–17,5 juta sudah membuka palang sendiri. Arah produk adalah keputusan owner, jadi Bagian B ditulis sesudah owner memilih.

  *Dilanjutkan (18 Okt):* owner memilih paket Rp 8 juta dengan mesin sendiri (K42), dan menyelesaikan mesin dulu (K43).

## Bagian B: Pembaca (ditulis 18 Okt, sesudah angka Bagian A)

**Yang terbaca dari Bagian A dan catatan lama sebelum Bagian B ditulis:**

| Hal | Angka | Dari mana |
|---|---|---|
| Pembaca di potongan plat bersih (INDO-ALPR, set uji) | mobil-terang 506/638, motor-terang 173/219: sama-sama sekitar 79% | `bukti/2026-10-15-baca-fpo-indo-1.json` |
| Pembaca di video CCTV (Bagian A) | mobil 11/16 benar-yakin, 0 salah; motor 3/8 benar-yakin, 4 salah-ragu, 1 salah-yakin | Laporan Bagian A |
| Format video HP | Video 4K dan video tegak terbaca. Penulis H.264/HEVC tidak tersedia, tetapi itu tidak dibutuhkan untuk membaca. HEVC belum bisa dibuktikan tanpa contoh | `cek-video-hp-23.py` |

**Bacaan agen:** pembaca sendiri sama baiknya untuk motor di potongan bersih. Jadi kelemahan motor di CCTV kemungkinan datang dari
dua hal:
- potongan yang kecil dan buram;
- cara bacaan beberapa gambar digabung. Sekarang yang dipungut adalah teks utuh yang paling sering muncul, termasuk dari gambar
  yang buram.

Bagian B karena itu mendahulukan perbaikan **penggabungan**, yang tidak butuh latihan:
- gambar paling tajam per kedatangan (K40);
- pemungutan suara per huruf.

Melatih ulang pembaca dengan potongan yang dibuat buram dan kecil menyusul di Bagian C, bila angka penggabungan belum cukup.

**Label tanpa set uji:** lembar latih Rencana 21 (100 kedatangan dari rantai cara potong di sisi latih). Jawaban owner di sana:
bukan plat 25, buram 22, salah 1. Sisanya (52) **dianggap** plat dengan bacaan benar. Anggapan ini ditanyakan ke owner sebelum
angkanya dipakai memilih.

### Task 4: Bacaan per gambar disimpan

- [x] **Step 1: Uji merah** di `tools/lab/uji/test_rantai.py`: `jalankan_semua(..., simpan_bacaan=True)` menulis `bacaan.jsonl`.
  - Satu baris per kedatangan: `{"video", "kedatangan", "bacaan": [[gambar, teks, yakin_baca, ketajaman, tinggi], ...]}`.
  - **ketajaman:** varian Laplacian potongan kelabu, dibulatkan 1 desimal.
  - **tinggi:** tinggi potongan dalam piksel.
  - `ringkasan.json` tidak memuat teks.
- [x] **Step 2:** `rantai.py`:
  - tiap penampakan mencatat `ketajaman` dan `tinggi`;
  - `jalankan_semua(..., simpan_bacaan=False)`;
  - CLI `--simpan-bacaan`.

  Gerbang lab → Expected `252 passed`. Commit.

  *Hasil:* merah dilihat (`unexpected keyword argument 'simpan_bacaan'`), lalu `252 passed`.

### Task 5: Varian penggabungan

- [x] **Step 1: Uji merah** `tools/lab/uji/test_gabung_varian.py`:
  - **V0** = `rantai.gabung` sekarang.
  - **V1 tajam:** bacaan diurutkan menurut ketajaman, separuh yang paling tajam dipakai (minimal `MIN_SETUJU`), lalu
    `rantai.gabung`.
  - **V2 per huruf:**
    1. Bacaan sah dikelompokkan menurut panjangnya, dan kelompok terbanyak dipakai.
    2. Tiap posisi diambil hurufnya dengan suara terbanyak; seri dipecah dengan jumlah `yakin_baca`.
    3. Hasilnya "yakin" bila tiap posisi didukung minimal `MIN_SETUJU` bacaan dan minimal `BAGIAN_SETUJU` dari bacaan di kelompok
       itu, **dan** teks hasilnya sesuai pola plat.
  - **V3** = V1 lalu V2.

  Uji memakai bacaan buatan: tiga bacaan yang masing-masing salah satu huruf di posisi berbeda harus menghasilkan teks yang benar
  dengan V2. V0 menyatakan ragu untuk kasus yang sama.
- [x] **Step 2:** `tools/lab/gabung_varian.py` berisi `varian(nama, bacaan) -> {"teks", "status"}` dan CLI
  `nilai bacaan.jsonl lembar.json keluar.json --bukan-plat --buram --salah`. Hitungan per varian:
  - **benar-yakin:** di kedatangan berlabel benar, teks sama dengan teks lembar dan statusnya yakin;
  - **berubah:** di kedatangan berlabel benar, teks berbeda dari teks lembar;
  - **yakin di bukan plat, buram, dan salah.**

  Gerbang lab → Expected naik sebanyak uji baru. Commit.

  *Hasil:* merah dilihat (`ImportError`: modul belum ada), lalu `8 passed`; gerbang lab 252 → 260.
  - **Dikoreksi sebelum merah dijalankan:** baris berlabel salah yang teksnya berubah dihitung terpisah (`salah_berubah`). Owner
    tidak mengetik plat yang benar, jadi teks baru di baris itu belum diketahui benar atau salah. Yang tidak boleh bertambah hanya
    "yakin" dengan teks lama yang pasti salah.

### Task 6: Pilih di sisi latih

- [x] **Step 1:** Rantai sisi latih dijalankan ulang dengan pengaturan Rencana 21 (cara potong, ambang 0,25) ditambah
  `--simpan-bacaan` → `rantai-latih-fase1-r23b`. Jumlah kedatangan dan teks gabungannya harus sama dengan `rantai-latih-fase1-r21`.
  Ini dicek dengan hitungan dan sidik SHA-256, tanpa mencetak teks.

  *Hasil (18 Okt, 08.46–09.37):*
  - Rantai dijalankan dengan salinan pembagian lama (`pembagian-video-fase1-r21.json`, 39 video latih), karena pembagian kini
    sudah memuat gelombang keempat.
  - 100 kedatangan; sidik sama dengan Rencana 21; semua kedatangan punya bacaan (`sama-latih-23b.py`).
- [x] **Step 2:** `gabung_varian.py nilai` dengan label lembar latih Rencana 21, sesudah owner memastikan anggapan "baris yang tidak
  disebut = bacaan benar".

  *Dikoreksi:* owner menjawab bahwa bacaan baris-baris itu belum ia pastikan ("hanya terbaca saja"). Jadi anggapan itu tidak
  dipakai. Owner lalu memeriksa ke-52 baris itu di lembar yang sama: 26 salah, 1 tak terbaca, dan 25 benar. Label gabungannya
  (`jawaban-23b-latih.mjs`): bukan plat 25, buram 23, salah 27, benar 25.
- [x] **Step 3: Aturan memilih, ditetapkan sebelum angka dilihat:**
  1. Varian dengan benar-yakin terbanyak dipilih, asalkan "yakin" di bukan plat, buram, dan salah tidak bertambah dibanding V0, dan
     tidak ada kedatangan benar yang teksnya berubah.
  2. Bila seri, V0 tetap.

  *Hasil:*

  | Varian | Benar-yakin (dari 25) | Benar yang berubah | Yakin di bukan plat / buram / salah | Salah yang berubah |
  |---|---|---|---|---|
  | V0 | 20 | 0 | 7 / 2 / 1 | 0 |
  | **V1 tajam** | **22** | 0 | 4 / 3 / 1 | 4 |
  | V2 per huruf | 23 | 1 | 7 / 4 / 2 | 1 |
  | V3 | 24 | 1 | 4 / 7 / 2 | 5 |

  - **Terpilih: V1.** V2 dan V3 gugur karena masing-masing mengubah satu bacaan yang benar, dan menambah yakin di baris yang
    keliru (13 lawan 10).
  - **Bacaan agen:** perbaikannya kecil (+2). Masalah yang lebih besar ada di pembaca: 27 dari 52 plat yang terbaca manusia dibaca
    salah. Pembaca perlu dilatih ulang dengan potongan CCTV (Bagian C).

### Task 7: Ukur di set uji dengan label yang dikunci

- [x] **Step 1:** Rantai 77 video uji dengan varian terpilih → `rantai-uji-fase1-r23b`. Kedatangannya sama dengan Bagian A, karena
  pencari tidak berubah.

  *Hasil (18 Okt, 09.40–12.29):*
  - Rantai dijalankan ulang dengan `--simpan-bacaan`; 529 kedatangan dengan sidik yang sama dengan Bagian A (`sama-uji-23b.py`).
  - **Ditambahkan:** subperintah `gabung_varian.py terapkan` (merah dulu, gerbang lab 260 → 261). Ia menyalin hasil rantai dengan
    teks dan status menurut V1, sehingga lembar dibuat ulang dengan baris yang sama.
  - **V1:** teks berubah di 107 dari 529 kedatangan, status berubah di 24.
- [ ] **Step 2:** Label lembar Bagian A dipakai ulang, sesuai temuan "label dikunci sekali".
  - Baris yang teksnya tidak berubah dinilai langsung, termasuk perubahan status.
  - Hanya baris yang teksnya berubah masuk lembar kecil untuk owner.

  *Sementara (18 Okt):*
  - Lembar V1 (`lembar-uji-fase1-r23b-v1`) memuat 120 baris yang sama; teksnya berubah di 25 baris.
  - **Label bukan plat dan tak terbaca menilai potongan, bukan bacaan,** jadi tetap berlaku walau teksnya berubah. Yang perlu
    diperiksa owner lagi hanya 6 baris yang dulu berlabel benar atau salah: 19, 30, 42, 58, 65, 94.
  - **Tanpa keenam baris itu (114 baris), V1 sama persis dengan V0:**
    - mobil: 10 dari 12 benar-yakin, 0 salah;
    - motor: 3 dari 6 benar-yakin, 1 salah-yakin;
    - yakin di bukan plat 11, di tak terbaca 12. Perubahan statusnya saling meniadakan.
  - **Akibatnya:** kenaikan di sisi latih (+2) tidak terlihat di 114 baris uji. Hasil akhirnya bergantung pada 6 baris itu.
- [ ] **Step 3:** Laporan, ROADMAP, gerbang penuh, commit.
