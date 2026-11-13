# Fase 1, Rencana 25: Optimalkan yang sudah ada dengan data owner (K50) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37). Owner dihentikan hanya di akhir (Task 7) atau bila ada keputusan tentang apa yang dijual.

**Goal:** rantai yang boleh dijual (K47, K48, K49) dibuat lebih baik di CCTV owner tanpa mulai dari nol. Ada tiga bagian, sesuai K50:
- **kendaraan:** YOLOX COCO dimodifikasi cara pakainya;
- **plat:** cctv1 dilatih lanjut dengan kotak plat tangkapan owner;
- **baca:** fpo-indo-1 dilatih lanjut dengan potongan tangkapan owner.

Setiap perubahan diukur otomatis terhadap label owner (`label.json`, Rencana 24), dibandingkan dengan titik awal dan dengan cadangan
dari nol (Rencana 24 Bagian B).

**Architecture:**
- **Penilai yang dipakai:**
  - `halaman_label.nilai_label` menilai rantai pada gambar tangkapan, dengan gambar dicocokkan lewat jalur berkas;
  - `deteksi.nilai` menilai pencari plat;
  - validasi CSV dan `baca_vlm.nilai` menilai pembaca.
- **Memilih di sisi latih, menguji sekali di sisi uji.**
  - Sisi latih tangkapan (140 gambar) dipakai memilih cara pakai kendaraan, karena mesinnya belum pernah melihat gambar itu.
  - Sesudah pencari dan pembaca dilatih dengan tangkapan latih, pemilihan memakai validasi masing-masing.
  - Tangkapan uji (38 gambar) diukur sekali di akhir.
- **Semua mesin baru bertujuan `jualan`.** Manifesnya diperiksa `tools/periksa-jualan.mjs`.

**Tech Stack:** lab biasa (YOLOX, torch GPU) dan image tambahan `-Fpo` (fast-plate-ocr, Keras GPU). Mengukur di CPU. Satu job GPU pada
satu waktu (`antrean-24d.ps1` menjadi contoh penjaga memori GPU; pelatihan boleh bersamaan dengan aplikasi lain owner).

---

## Yang diketahui sebelum rencana ini ditulis (19 Okt)

| Hal | Angka | Dari mana |
|---|---|---|
| Rantai belajar di tangkapan (kendaraan COCO, cctv1 cara potong ambang 0,25, fpo-indo-1) | pembaca benar 98 dari 126 plat yang ditemukan dan bisa dinilai; plat terlewat di 9 dari 74 gambar mobil dan 34 dari 103 gambar motor; di 7 dari 43 gambar terlewat, kendaraannya tidak ditemukan | `bukti/2026-10-18-tangkapan-owner.md` |
| Label tangkapan | latih 140 gambar, 141 kotak, 125 teks; uji 38 gambar, 39 kotak, 34 teks; 1 plat tanpa kotak (butir 42) | sama |
| Huruf salah fpo-indo-1 di tangkapan | 35 huruf dari 24 bacaan: 11 di pasangan owner, 5 huruf bulat, 7 angka | sama |
| Pembaca di validasi 489 gambar | fpo-indo-1 407; dari nol P3 319, P2 293 | `data/keluaran/banding-pembaca-24.json` |
| Pencari plat di validasi | cctv1 F1 0,9236 (COCO + plat-lighting + video riset + tempel); D1 dari nol 0,845 | `bukti/2026-10-16-pencari-plat-cctv.md`, log D1 |
| Dataset cctv1 (`dataset/cctv-fase1`) | latih: 269 gambar video (44 kotak, **225 gambar tanpa kotak**), 202 tempel, 393 plat-lighting; valid: 64 video (3 kotak), 24 tempel, 84 plat-lighting | `ringkasan.json` dataset |

Catatan Rencana 19: gambar "tanpa kotak" bisa menyembunyikan plat yang tidak pernah ditemukan, sehingga plat itu diajarkan sebagai latar.
Rencana ini menguji itu dengan calon tanpa gambar-gambar tersebut.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- **Cara pakai kendaraan (Task 2).** Dipilih dengan `nilai_label` di sisi latih tangkapan, memakai pencari dan pembaca belajar
  yang ada. Dipilih `dibaca_benar` terbanyak (semua kelompok). Bila seri, dipilih `kotak_di_luar_label` paling sedikit. Bila masih seri,
  dipilih cara yang ada sekarang.
- **Pencari plat (Task 5).** Calon:
  - C0: cctv1 apa adanya;
  - C1: cctv1 dilatih lanjut dengan cctv-fase1 utuh ditambah tangkapan latih;
  - C2: sama dengan C1, tetapi tanpa 225 gambar video yang tanpa kotak.

  Dipilih F1 tertinggi pada ambangnya sendiri, di validasi gabungan (cctv-fase1 valid ditambah tangkapan validasi). Bila seri, C0.
  Diuji sekali di tangkapan uji dan plat-lighting uji, bersama Nano-640 dan D1 sebagai pembanding.
- **Pembaca (Task 6).** Calon:
  - R0: fpo-indo-1 apa adanya;
  - R1: fpo-indo-1 dilatih lanjut dengan INDO-ALPR latih inti ditambah potongan tangkapan latih yang diulang 5 kali;
  - R2: R1 ditambah 10.000 plat buatan.

  Dipilih benar terbanyak pada potongan tangkapan validasi (29). Bila seri, dipilih yang benar terbanyak di INDO-ALPR validasi (460).
  Calon yang INDO-ALPR validasinya turun lebih dari 10 gambar dari R0 ditolak, karena lupa pada plat bersih tidak dibayar dengan
  29 potongan. Diuji sekali di INDO-ALPR uji (911 adil) dan potongan tangkapan uji (34), bersama P3 sebagai cadangan.
- **Rantai jualan (Task 7).** Kendaraan dengan cara terpilih, pencari terpilih, dan pembaca terpilih, dinilai sekali di tangkapan uji
  dan dibandingkan dengan titik awal.
- **Ambang pencari di rantai (Task 7; ditambahkan 19 Okt sesudah Task 5, sebelum rantai baru dijalankan sekali pun).** Rencana belum
  menyebutnya. Titik awal memakai 0,25, yang dipilih di sisi latih (Rencana 20), sedangkan ambang validasi C1 0,6 (gambar utuh). Calon
  {0,25; 0,4; 0,6}, dengan kendaraan cara terpilih dan pembaca terpilih, dinilai `nilai_label` sisi latih. Dipilih `dibaca_benar`
  terbanyak; bila seri, `kotak_di_luar_label` paling sedikit; bila masih seri, 0,6. **Batas:** gambar latih ikut melatih C1 dan
  potongannya ikut melatih pembaca, jadi pilihan ini bisa condong ke ambang rendah; sisi uji tetap diukur sekali.

## Task 1: Titik awal di tangkapan

- [x] **Step 1:** `halaman_label.py nilai` pada `data/keluaran/tangkapan-owner-baca` (rantai belajar, Rencana 24 Task 2), untuk sisi `latih`
  dan sisi `uji`. Simpan ke `bukti/2026-10-19-titik-awal-tangkapan.json` (hitungan saja; disalin dari `data/keluaran`, karena di lab repo
  read-only).
  - **Hasil (19 Okt):** latih mobil 43 dari 53 berteks dibaca benar, motor 35 dari 72; uji mobil 12 dari 16, motor 9 dari 18.
  - **Batas penilai:** kotak label plat yang dulu ditemukan rantai ini berasal dari kotak rantai ini sendiri, jadi titik awal pasti
    "menemukan" plat itu. Calon lain harus mengenai kotak itu dengan IoU minimal 0,3.

## Task 2: Kendaraan, dua modifikasi cara pakai (K45, K50 butir 1)

**Files:** Modify `tools/lab/kendaraan.py`, `tools/lab/baca_gambar.py`, `tools/lab/rantai.py`; uji `test_kendaraan.py`, `test_baca_gambar.py`.

- [x] **Step 1: Uji merah.**
  - `urut_terdekat(kendaraan)` mengurutkan kendaraan dari tepi bawah terendah (K45: 23 dari 25 cocok).
  - `cari_dalam_kendaraan(..., maks_kendaraan=None)` hanya memproses `maks_kendaraan` kendaraan terdekat.
  - `baca_gambar.jalankan(..., cadangan_utuh=True)` mencari plat di gambar utuh bila tidak ada kendaraan setinggi `MIN_TINGGI`.
  - Pilihan yang sama di `rantai.py` (`--maks-kendaraan`, `--cadangan-utuh`), dengan uji rantai: CLI sampai keluaran.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau. (9 uji baru merah dulu; lab 289 → 298.) Batas jumlah kendaraan dihitung sesudah
  kendaraan pendek dibuang. Keduanya ditolak tanpa tahap kendaraan (dan di rantai, tanpa cara potong).
- [x] **Step 3:** Jalankan `baca_gambar` dengan model belajar untuk empat cara: sekarang; cadangan utuh; terdekat 1; cadangan utuh +
  terdekat 1. Nilai di sisi latih, lalu pilih menurut aturan. Kalau motor yang tidak terlihat tetap banyak, catat usulan melatih ulang
  pencari kendaraan dengan kotak kendaraan yang diperiksa owner. Itu tidak dikerjakan di sini.
  - **Hasil sisi latih (`dibaca_benar` mobil + motor):** sekarang 43 + 35 = 78; cadangan utuh 43 + 36 = 79; terdekat 1 38 + 34 = 72;
    keduanya 38 + 35 = 73. **Terpilih: cadangan utuh.** Jalan ulang "sekarang" persis sama dengan titik awal.
  - **Temuan:** terdekat 1 membuang 8 plat mobil yang tadinya ditemukan. K45 dipakai sebagai urutan membaca, bukan batas.
  - **Motor yang tidak terlihat sedikit:** hanya 4 gambar motor latih tanpa kendaraan sama sekali, dan cadangan utuh menemukan plat di
    3 di antaranya. Sisi uji tidak punya gambar seperti itu. Jadi pencari kendaraan belum perlu dilatih ulang; penghambatnya pencari plat.

## Task 3: Dataset lanjutan cctv1

**Files:** Modify `tools/lab/dataset_jualan.py`; uji `test_dataset_jualan.py`.

- [x] **Step 1: Uji merah:** `bangun(..., tambah=<folder dataset YOLO>, tambah_bahan=[...], tanpa_negatif_tambah=False)`.
  - Gambar `train` dan `valid` dari dataset tambahan disalin dengan awalan `x-`, kecuali yang berawalan `pl-` (plat-lighting sudah ada,
    jangan kembar).
  - Bila `tanpa_negatif_tambah`, gambar tambahan tanpa kotak dilewati. **Diubah saat dijalankan:** hanya di `train`. Validasi C1 dan C2
    harus sama, kalau tidak F1 C0, C1, dan C2 tidak diukur di soal yang sama.
  - Bahan digabung, dan hitungan baru tercatat di `ringkasan.json`. Dataset tambahan tanpa daftar bahan ditolak.
- [x] **Step 2:** Tulis kodenya, lalu bangun `dataset/cctv2-c1` dan `dataset/cctv2-c2`, dengan bahan tambahan `video-riset-youtube` dan
  `plat-buatan`. C1: latih 501 + 471, valid 115 + 88. C2: latih 501 + 246 (225 gambar tanpa kotak dibuang), valid sama. Hitungan
  cocok dengan `ringkasan.json` cctv-fase1. **Batas:** 202 gambar tempel di cctv-fase1 juga berasal dari bingkai tanpa temuan pencari
  lama, jadi bisa menyembunyikan plat sungguhan; keduanya tetap di C2 karena berkotak (plat buatan).

## Task 4: `latih_yolox` dari mesin sendiri

**Files:** Modify `tools/lab/latih_yolox.py`; uji `test_latih_yolox.py`.

- [ ] **Step 1: Uji merah (CPU, kecil):** `latih(..., bobot_awal_mesin=<folder>, jualan=True)`.
  - Memuat `mesin.safetensors` lewat `muat_mesin`, yang memeriksa SHA-256.
  - Tidak membaca bobot COCO.
  - Bahan = gabungan bahan mesin awal dan dataset.
  - Tujuan `jualan` hanya bila diminta. `bobot_awal` mencatat nama dan SHA-256 mesin awal.

  Kontrol: mesin awal yang berubah ditolak.
- [x] **Step 2:** Tulis kodenya dan CLI `--bobot-awal-mesin`, `--jualan`. Gerbang hijau. (Task 3 dan 4: 7 uji baru merah dulu; lab
  298 → 305.) `bobot_awal` juga mencatat nama folder, karena nama di `mesin.json` cctv1 sama dengan pencari lama.

## Task 5: Melatih dan memilih pencari plat

- [x] **Step 1:** C1 dan C2 dari cctv1, masing-masing 60 zaman, di latar dengan log dan penjaga memori GPU. (C1 44 menit, C2 35 menit;
  `data/alat-sementara/antrean-25a.ps1`.)
- [x] **Step 2:** Pilih menurut aturan, lalu ekspor ONNX (`latih_yolox.py ekspor`, image `-Fpo`). **Diubah saat dijalankan:** C1 dan C2
  sama-sama diekspor dulu, supaya C0, C1, dan C2 dinilai dengan alat yang sama (ONNX, `pilih-pencari-25.py`). F1: C0 0,8971, **C1
  0,9257**, C2 0,9244. Terpilih C1.
- [x] **Step 3:** Ukur sekali (`deteksi.nilai`) di tangkapan uji dan plat-lighting uji untuk C0, terpilih, Nano-640, dan D1. Hasilnya
  `bukti/2026-10-19-pencari-cctv2.md`. Tangkapan uji (gambar utuh): C0 16, Nano-640 24, D1 31, C1 35 dari 39. Plat-lighting uji: 96, 96,
  93, 94 dari 102. D1 diekspor ke ONNX lebih dulu.

## Task 6: Pembaca, fpo-indo-1 dilatih lanjut

**Files:** Modify `tools/lab/bahan_pembaca.py` (`wilayah=True` menambah kolom `plate_region`, `ulang_tangkapan=N`),
`tools/lab/latih_fpo.py` (`latih_lanjut`); uji `test_bahan_pembaca.py`, `test_latih_fpo.py`, `uji_fpo/test_latih_lanjut.py`.

- [ ] **Step 1: Uji merah.**
  - CSV berwilayah ("Indonesia") untuk model berkepala wilayah.
  - Potongan tangkapan latih diulang N kali; validasi tidak diulang.
  - `latih_lanjut(folder, bobot_awal=<fpo-indo-1>)`:
    - memeriksa SHA-256 mesin awal terhadap `mesin.json`;
    - memakai konfigurasi terbitan (`BOLEH-PRODUK` sejak K47);
    - memeriksa bahwa bobot termuat utuh;
    - memantau `val_plate_acc`;
    - menulis manifes bertujuan `jualan` dengan bahan gabungan dan `bobot_awal` = fpo-indo-1.
  - Uji GPU di `uji_fpo`: 1 zaman pada bahan kecil.
  - **Ditambah saat dijalankan:** `ketepatan_per_sumber` (validasi dipecah INDO-ALPR dan tangkapan, dengan aturan pecah
    `banding-pembaca-24.py`), dan `bahan_pembaca.py uji-tangkapan` (potongan tangkapan uji berkelompok di nama, untuk Step 4).
- [x] **Step 2:** Tulis kodenya. Ketiga gerbang hijau. Kode ditulis selama pelatihan Task 5 memegang kunci bengkel, jadi merahnya
  dibuktikan sesudahnya dengan `git stash` kode baru (9 uji merah karena fiturnya belum ada), lalu hijau. Gerbang: lab 305 → 313, image
  tambahan 34 → 35, Node 120. Satu uji image tambahan (`test_cli_baca_gambar_dengan_model_sungguhan...`) merah karena ringkasan
  `baca_gambar` kini memuat `aturan` (Task 2): sepupu yang terlewat karena di luar gerbang biasa; asersinya diperluas.
- [x] **Step 3:** Latih R1 (40 zaman) dan R2 (20 zaman), lalu pilih menurut aturan. (`antrean-25b.ps1`; R1 55 menit, R2 68 menit.)
  - Validasi (tangkapan 29 / INDO-ALPR 460): R0 19 / 388; R1 19 / 387 (zaman terbaik 1 dari 40); R2 22 / 376 (zaman terbaik 3 dari 20).
  - **Terpilih: R0 (fpo-indo-1 apa adanya).** R2 ditolak karena INDO-ALPR turun 12 (> 10); R0 dan R1 seri di tangkapan, R0 lebih banyak di
    INDO-ALPR. Dicatat dan di-commit sebelum set uji dibuka.
  - **Kenapa latihan lanjut tidak menolong (bacaan agen):** laju belajar 0,001 (bawaan untuk melatih dari nol); ketepatan latih naik
    0,80 → 0,90, validasi tetap 0,80–0,82 sejak zaman pertama. Zaman dipilih dengan `val_plate_acc` gabungan, yang 94% isinya INDO-ALPR,
    jadi tidak bisa melihat kemajuan di tangkapan. Usulan berikutnya, belum dikerjakan: laju lebih kecil dan memilih zaman dari validasi
    tangkapan, dengan aturan ditulis dulu.
- [x] **Step 4:** Ukur sekali di INDO-ALPR uji dan potongan tangkapan uji (R0, terpilih, P3). Buat ONNX terpilih (`onnx_fpo.py buat`), lalu
  hitung ulang huruf yang salah (`hitung-label-24.mjs`) pada pembaca terpilih. Hasilnya `bukti/2026-10-19-pembaca-fpo-lanjut.md`.
  - Terpilih R0, yang sudah punya ONNX (Rencana 11), jadi `onnx_fpo.py buat` tidak perlu. R1 dan R2 ikut diukur sebagai informasi.
  - INDO-ALPR uji adil (911): R0 79,4% / 86,0% / 79,8% (sama dengan Rencana 10); R1 79,8 / 86,0 / 79,3; R2 77,6 / 87,7 / 76,4; P3 66,2 /
    68,4 / 59,1. Potongan tangkapan uji (34): R0 24, R1 24, R2 25, P3 19.
  - Huruf salah dihitung di potongan tangkapan uji (`ukur-pembaca-25.py`), bukan dengan `hitung-label-24.mjs`, karena bacaan salah lama ada
    di sisi latih yang sudah dipakai melatih. R0: 13 huruf salah, 4 di pasangan owner.

## Task 7: Rantai jualan di tangkapan uji, lalu BERHENTI

- [x] **Step 1:** `baca_gambar` dengan kendaraan (cara terpilih), pencari terpilih (ONNX), dan pembaca terpilih (ONNX), pada `data/capture`.
  Lalu `nilai_label` sisi uji, dibandingkan dengan Task 1. (`rantai-25.ps1`.) Ambang di sisi latih: 0,25 → 85, 0,4 → 84, 0,6 → 81;
  terpilih 0,25. Uji: plat ditemukan 28 → 34 dari 39; dibaca benar 21 → 21 dari 34 (mobil 12 → 13, motor 9 → 8). Empat plat benar → salah
  karena kotak C1 bergeser (IoU median 0,84–0,88), empat plat terlewat → benar.
- [x] **Step 2:** Laporan `bukti/2026-10-19-rantai-optimal.md`, ROADMAP, dan changelog. Gerbang penuh, lalu commit.
- [ ] **Step 3: BERHENTI untuk owner:** hasil per bagian. Usulan berikutnya: lembar video uji untuk baris yang berubah saja, uji dengan
  rekaman HP dan CCTV kantor (K43), dan pelatihan ulang pencari kendaraan bila Task 2 menunjukkan perlu.

**Batas yang sudah diketahui:**
- Tangkapan uji kecil (38 gambar, 34 teks).
- Tangkapan diambil owner saat platnya terlihat, jadi bukan rekaman gerbang.
- Validasi tangkapan pembaca hanya 29 potongan.
- Plat lain di gambar tangkapan yang tidak dilabeli muncul sebagai "kotak di luar label".
