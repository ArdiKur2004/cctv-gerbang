# Fase 3, Rencana 31: Halaman ciri kendaraan untuk owner — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37); spec Fase 3 tahap 1 disetujui owner (K61). Owner dihentikan di akhir untuk mengisi halaman.

**Goal:** label jenis, warna, dan merek untuk kendaraan di tangkapan owner, tanpa agen melihat gambar (spec Fase 3 bagian 3). Label ini
menjadi tolak ukur Rencana 32–35 (sisi uji) dan bahan latih (sisi latih).

**Kenapa bahan Roboflow tidak di rencana ini** (spec bagian 6 menaruhnya di Rencana 31): bahan itu dipakai berbeda untuk jenis
(kotak kendaraan) dan merek (kotak logo dan kelas merek). Bahan disiapkan di Rencana 32 dan 34, tempat bahan itu dipakai. Rencana ini
dibuat kecil supaya owner bisa mulai mengisi halaman lebih cepat.

## Architecture

`tools/lab/halaman_ciri.py`:
- **buat** `folder_capture peta_label label_json folder_kendaraan keluar`:
  - untuk tiap gambar di `label.json`, pencari kendaraan (sekarang YOLOX COCO, mesin belajar, hanya untuk usulan) dijalankan;
  - tiap plat berlabel (berteks atau tidak) dipasangkan dengan kendaraan terkecil yang memuat tengah platnya
    (`kendaraan.kendaraan_pemuat`);
  - satu kartu per kendaraan; dua plat di kendaraan yang sama menjadi satu kartu;
  - plat tanpa kendaraan mendapat kotak perkiraan di sekitar platnya, ditandai "perkiraan";
  - usulan jenis dari kelas COCO (mobil, motor, bus, truk); warna dan merek kosong, dipilih owner;
  - keluaran: `halaman.html`, `gambar/` (salinan bernama nomor, tanpa nama asli), dan `butir.json`. Halaman tidak memuat apa pun dari luar.
- **terima** `butir_json simpanan keluar`: jawaban owner (`label-ciri.json` dari halaman) diperiksa terhadap daftar kelas, lalu menjadi
  `ciri.json` (per kendaraan: gambar, sisi, kelompok, kotak, plat yang dimuat, usulan, jenis, warna, merek, "kotak tidak pas") dan
  `ringkasan-ciri.json` (hitungan saja). Nilai di luar daftar ditolak tanpa menulis apa pun.
- Daftar kelas (spec bagian 1) adalah konstanta modul. Halaman dan `terima` memakai daftar yang sama.
- Kartu selesai bila jenis, warna, dan merek terisi, atau bila jenisnya "bukan kendaraan". Merek motor dan merek mobil berbeda daftar.

## Task 1: Alat

**Files:** Create `tools/lab/halaman_ciri.py`, `tools/lab/uji/test_halaman_ciri.py`.

- [x] **Step 1: Uji merah:**
  - kartu per kendaraan pemuat plat; dua plat satu kendaraan = satu kartu; plat tanpa kendaraan diberi kotak perkiraan;
  - usulan jenis dari kelas COCO;
  - halaman memuat semua kartu dan daftar kelas yang sama dengan konstanta;
  - nama berkas asli tidak muncul di keluaran;
  - `terima`: nilai sah menjadi `ciri.json`; nilai di luar daftar, merek motor untuk mobil, dan butir yang tidak ada ditolak sebelum menulis;
    kartu belum lengkap dihitung kosong; "bukan kendaraan" tidak butuh warna dan merek;
  - CLI sampai berkas, dan layar tanpa nama berkas asli.
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, dan Node hijau. (11 uji merah karena modulnya belum ada, lalu hijau. Lab
  357 → 369, image tambahan 35, Node 120.)

## Task 2: Bukti halaman berjalan, dengan gambar buatan

- [x] **Step 1:** Halaman dibuat dari gambar buatan tanpa plat (kotak berwarna di kanvas polos) di scratchpad. (**Diubah saat
  dijalankan:** di `data/keluaran/rencana-31/buatan`, karena lab hanya bisa menulis ke `data/keluaran`; disajikan server lokal 127.0.0.1.)
- [x] **Step 2:** Halaman dibuka di peramban lewat Playwright. Isi beberapa kartu, simpan berkas, lalu `terima` membaca berkas yang terunduh.
  Kemajuan bertahan sesudah halaman dimuat ulang. (4 kartu diisi: mobil, motor, truk dengan "kotak tidak pas", dan kartu perkiraan
  "bukan kendaraan"; `ciri.json` berisi persis yang diklik. **Ditemukan di peramban:** pesan "merek dikosongkan" tidak pernah tampil karena
  ditulis sebelum `tampil()`. Diperbaiki, dan uji penjaga urutannya ditambah, terbukti merah dengan urutan lama. Kotak centang dirapikan,
  dan ikon kosong ditambah supaya peramban tidak meminta `favicon.ico`.)

## Task 3: Halaman sungguhan, lalu BERHENTI

- [x] **Step 1:** `buat` untuk tangkapan owner di image lab tambahan. Yang dilaporkan hanya hitungan: kartu, perkiraan, usulan per jenis.
  (180 kartu dari 176 gambar; 7 kotak perkiraan; usulan mobil 61, motor 98, truk 12, bus 2.)
- [x] **Step 2:** ROADMAP dan changelog, `CLAUDE.md` §7. Commit.
- [x] **Step 3: BERHENTI untuk owner:** owner membuka halaman, mengisi, menekan "Simpan berkas", lalu memberi tahu letak
  `label-ciri.json`. Owner tidak menulis nomor plat atau ciri per kendaraan di percakapan. (24 Okt: owner mengisi 180 kartu,
  `label-ciri (2).json`. **Ditambah saat dijalankan:** `terima` memeriksa tanda halaman, karena di Downloads ada tiga berkas jawaban; uji
  merah dulu. Hasil: 180 lengkap, 8 kotak tidak pas, usulan jenis sama 161 dari 173.)

**Batas:** usulan jenis dari pencari COCO (mesin belajar) hanya membantu owner, dan tidak pernah dipakai tanpa diperiksa. Hanya
kendaraan yang platnya berlabel yang masuk halaman. Kendaraan lain di gambar tidak dilabeli.
