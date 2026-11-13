# TGT T6: Jenis kendaraan masuk ke rantai, dan kamera menyalakan status — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dikerjakan mandiri (K37). Dasar: permintaan owner 26 Okt — *"pasang dulu jenis kendaraan ke rantai juga,
> sambungkan agar demonya sempurna, menggunakan kamera untuk menentukan bahwa kendaraan tersebut sesuai, dan
> mentriger status"*.

**Goal:** satu gambar dari kamera menghasilkan **plat + jenis kendaraan**, TGT memeriksa apakah jenisnya cocok
dengan yang terdaftar, mencatat kejadiannya, dan menyalakan status masuk/keluar — semuanya terlihat di layar satpam.

## ⛔ Yang HARUS diputuskan dengan benar: apa akibat jenis yang tidak cocok

Angka yang sudah diukur (`bukti/2026-10-24-jenis-dan-warna.md`): jenis benar **12 dari 14 mobil**. Artinya sekitar
**1 dari 7 mobil akan salah dikenali**.

Karena itu:

| | |
|---|---|
| Jenis tidak cocok ⇒ **memberi tahu satpam** | Sesuai K55 dan K72 |
| Jenis tidak cocok ⇒ **TIDAK menahan gerbang** | K55 apa adanya: *"hanya memberi peringatan ke satpam, tidak menahan gerbang... sampai pengenal ciri terbukti akurat dan owner memutuskan lain"*. Dengan 1 dari 7 salah, menahan berarti menahan orang yang tidak bersalah berkali-kali tiap hari |
| Jenis **tidak pernah** menjadi alasan membuka | Yang membuka tetap plat. Ciri hanya menambah catatan |

**Disurface ke owner:** K73 menahan kendaraan yang keluar bila statusnya janggal, karena plat tiruan berarti
barang orang hilang. Pertanyaan yang sama berlaku untuk jenis yang tidak cocok saat keluar — tetapi dengan
ketelitian hari ini (1 dari 7 salah), menahannya akan lebih sering salah daripada benar. Rencana ini **tidak**
menahannya; owner tinggal meminta bila mau, dan biayanya disebut.

## Jembatan mesin ke aplikasi: lewat BERKAS, bukan jaringan

Lab berjalan dengan `--network none` (`tools/lab.ps1`), dan itu **tidak diubah** — justru pagar itu yang membuat
bobot model dari luar aman dijalankan. Jadi batas antara mesin dan aplikasi berbentuk folder:

```
data/keluaran/baca-masuk/<id>.jpg   ← ditulis TGT (atau kotak gerbang)
data/keluaran/baca-masuk/<id>.json  ← keterangan: gerbang, arah, waktu
data/keluaran/baca-keluar/<id>.json ← ditulis mesin: plat, ragu, yakin, jenis
```

Ini juga bentuk yang benar untuk produk: kotak di gerbang menaruh gambar, mesin memungutnya. Tidak ada port
terbuka di antara keduanya.

⛔ `baca-masuk/` dan `baca-keluar/` memuat gambar kendaraan dan nomor plat: **agen tidak membukanya**. Yang dibaca
agen hanya ringkasan berupa angka.

## Task 1: Jenis yang tidak cocok masuk ke putusan dan notifikasi

**Files:** Modify `tgt/putusan.mjs`, `tgt/notifikasi.mjs`, `tgt/akses.mjs`; modify ujinya.

- [x] **Step 1: Uji merah:** jenis yang cocok tidak mengubah apa pun · jenis yang TIDAK cocok memberi
  `ciriJanggal` dan memanggil notifikasi, **tetapi putusannya tetap buka** · jenis yang tidak terbaca mesin
  (null) **bukan** ketidakcocokan · jenis tidak pernah mengubah putusan dari tidak-buka menjadi buka ·
  notifikasinya menyebut jenis yang terbaca dan yang terdaftar, tanpa data pribadi lain.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau, angka sebelum→sesudah.

## Task 2: Layanan baca satu gambar, dengan jenis

**Files:** Create `tools/lab/layanan_baca.py`, `tools/lab/uji/test_layanan_baca.py`.

- [x] **Step 1: Uji merah (di lab):** satu gambar menghasilkan JSON bersusunan tetap · gambar tanpa kendaraan
  menghasilkan hasil kosong yang sah, bukan galat · berkas rusak tidak menghentikan antrean · **jalur berkas tidak
  pernah ikut tercetak** saat galat (aturan yang sama dengan alat berplat lain) · jenis diambil dari
  `ciri-jenis-j1` dengan ambang yang disebut, bukan tersembunyi di mesin.
- [x] **Step 2:** Tulis kodenya memakai rantai yang sudah ada (`kendaraan-jualan-k1` → `pencari-cctv2-c1` →
  `pembaca-lanjut-r4`) ditambah `ciri-jenis-j1`.

## Task 3: Jembatan folder di sisi TGT

**Files:** Create `tgt/jembatan.mjs`, `tgt/uji/jembatan.test.mjs`.

- [x] **Step 1: Uji merah:** gambar ditulis dengan nama acak · hasil yang muncul dibaca sekali lalu dibuang ·
  hasil yang tidak pernah datang punya batas waktu dan tidak menggantung selamanya · hasil rusak tidak
  menjatuhkan server · satu hasil tidak pernah diproses dua kali.
- [x] **Step 2:** Tulis kodenya.

## Task 4: Kamera di layar satpam

**Files:** Modify `tgt/web/app.js`, `tgt/server.mjs`.

- [x] **Step 1:** Layar satpam mendapat tombol ambil gambar dari kamera perangkat (`getUserMedia`), lalu
  mengirimnya ke server. Hasilnya tampil sebagai putusan beserta alasannya, dengan jenis sebagai catatan.
- [x] **Step 2:** Bila kamera tidak ada atau ditolak, layar **mengatakan sebabnya** dan jalur unggah berkas tetap
  ada — gerbang tidak boleh buntu karena satu izin.

## Task 5: Bukti utuh

- [x] **Step 1:** Satu gambar sungguhan masuk dari ujung ke ujung, dan status kendaraannya berubah
  (di luar → di dalam). **Agen tidak membuka gambarnya**; yang diperiksa hanya angka dan susunan hasilnya.
- [x] **Step 2:** Jenis yang tidak cocok memunculkan notifikasi, dan gerbangnya tetap terbuka.

## Task 6: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7, dan **daftar batas untuk dipakai saat demo**. Gerbang penuh,
  commit, laporan.

**Batas yang sudah diketahui sebelum mulai:**
- **Merek dan warna mobil tetap tidak bekerja** dan tidak dipasang. Hanya jenis yang masuk.
- Jenis salah pada sekitar 1 dari 7 mobil.
- Angka rantai berasal dari tangkapan layar, **bukan kamera gerbang sungguhan** (K43).
- Mesin berjalan di lab tanpa jaringan; di gerbang sungguhan ia perlu dijalankan sebagai layanan tersendiri, dan
  itu belum dikerjakan.
