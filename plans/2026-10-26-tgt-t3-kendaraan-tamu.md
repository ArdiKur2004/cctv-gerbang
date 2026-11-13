# TGT T3: Kendaraan, tamu, lama kunjungan, dan masa simpan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Di repo ini eksekusi juga wajib memakai
> skill `honest-slice-execution`. Dikerjakan mandiri (K37). Spec disetujui (K69); tempat data K70; mesin dan syarat
> "data tidak boleh disimpan semua" K71.

**Goal:** penghuni mendaftarkan kendaraannya sendiri, mengundang tamu dengan lama kunjungan, dan tamu menerima tautan
berisi QR — sementara **yang disimpan hanya seperlunya dan yang lewat masa simpan benar-benar terhapus**.

## Yang baru dibanding T2, dan kenapa

| | |
|---|---|
| **Masa simpan ditegakkan di kode** (K71) | "Data tidak boleh disimpan semua". Masa simpan yang hanya tertulis di spec §8 tidak menghapus apa pun. Penghapusnya diuji **dua arah**: yang lewat masa simpan hilang, yang masih di dalamnya tetap ada. |
| **Penghuni hanya melihat miliknya** | Kolom pemilik sudah ada sejak T2 (`kendaraan.pengguna_id`, `tamu.pengundang_id`). Sekarang dipakai. |
| **QR tamu** | Dibuat sendiri tanpa paket luar. **Wajib dibuktikan bisa dibaca**, bukan sekadar "terlihat seperti QR". |

## ⛔ QR: bahaya dan cara membuktikannya

Gambar yang *terlihat* seperti QR tetapi tidak terbaca adalah kegagalan senyap yang paling mahal: satpam di gerbang
akan menyalahkan kameranya, bukan kodenya.

**Pembuktian:** QR dibuat, digambar ke canvas di peramban sungguhan, lalu **dibaca ulang dengan `BarcodeDetector`
milik peramban** (pembaca yang sama sekali bukan buatan kita). Teks hasil baca wajib sama persis dengan masukannya.
Kalau `BarcodeDetector` tidak ada di peramban ini, **QR tidak dinyatakan bekerja** — batasnya ditulis, dan tamu tetap
bisa memakai kode undangan yang tercetak besar.

## Aturan yang ditegakkan (tambahan atas T1 dan T2)

1. **Penghuni** boleh menambah kendaraan **atas namanya sendiri** dan mengundang tamu; ia **tidak** melihat kendaraan
   atau tamu orang lain. **Pengelola** melihat semuanya di grupnya. **Satpam** membaca daftar izin tetapi **tidak bisa
   mengubahnya** (spec §4).
2. Jenis kendaraan tetap daftar putih roda 4 ke atas (K65) — sudah di T1, dipakai ulang, tidak ditulis dua kali.
3. Kode undangan tamu adalah cara masuk gerbang: ia **tidak ikut keluar** ke orang yang bukan pengundangnya atau
   pengelola.
4. Halaman undangan tamu dibuka **tanpa akun**, hanya dengan kodenya, dan **hanya menampilkan seperlunya**: nama tamu,
   nama gerbang, alamat, masa berlaku, dan QR. **Tidak** menampilkan daftar penghuni, kendaraan lain, atau nomor WA.

## Task 1: Masa simpan (K71)

**Files:** Create `tgt/simpan.mjs`, `tgt/uji/simpan.test.mjs`; modify `tgt/pengaturan.mjs`.

- [x] **Step 1: Uji merah:** masa simpan dibaca dari pengaturan (`TGT_SIMPAN_FOTO`, `TGT_SIMPAN_KEJADIAN`,
  `TGT_SIMPAN_TAMU`), bukan angka yang disalin ke kode · `bersihkan()` menghapus kejadian yang lewat masa simpan dan
  **menyisakan** yang masih di dalamnya · tamu yang kunjungannya selesai dan lewat masa simpan terhapus beserta
  kunjungannya · **tamu yang masih di dalam tidak pernah terhapus walau lama** · kendaraan terdaftar tidak terhapus ·
  `bersihkan()` melaporkan jumlah yang dihapus per jenis · dijalankan dua kali tidak menghapus apa pun lagi.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau, angka sebelum→sesudah disebut.

## Task 2: Kendaraan dan tamu di pintu hak akses

**Files:** Modify `tgt/akses.mjs`; create `tgt/uji/akses-kendaraan.test.mjs`.

- [x] **Step 1: Uji merah:** untuk tiap peran, tiap operasi diuji **boleh** dan **ditolak** · penghuni melihat hanya
  kendaraan dan tamunya sendiri · satpam membaca semua tetapi tidak bisa menambah atau menghapus · pengelola bisa
  semuanya di grupnya · orang luar mendapat "tidak ditemukan" · kendaraan yang dibuat penghuni tercatat pemiliknya ·
  penghuni tidak bisa menghapus kendaraan orang lain.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 3: Jalur server dan uji rantai

**Files:** Modify `tgt/server.mjs`; modify `tgt/uji/server.test.mjs`.

- [x] **Step 1: Uji merah:** semua lewat HTTP sungguhan — satpam menambah kendaraan ditolak 403 · penghuni melihat
  daftar hanya berisi miliknya · tamu dibuat dan kodenya keluar untuk pengundang · halaman undangan terbuka **tanpa
  sesi** dengan kode yang benar dan **404 dengan kode yang salah** · halaman undangan **tidak** memuat nomor WA.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau. Uji rantai lama (server tidak mengimpor `layanan.mjs`) tetap hijau.

## Task 4: QR yang terbukti terbaca

**Files:** Create `tgt/web/qr.js`, `tgt/uji/qr.test.mjs`.

- [x] **Step 1: Uji merah:** pembuat QR menghasilkan matriks berukuran sah, pola pencari di tiga sudut, dan **menolak**
  teks yang terlalu panjang alih-alih memotongnya diam-diam.
- [x] **Step 2:** Tulis kodenya. Lalu **bukti di peramban**: QR digambar, dibaca ulang dengan `BarcodeDetector`, dan
  teksnya wajib sama persis. Bila tidak bisa dibuktikan, tulis batasnya dan jangan menyebutnya bekerja.

## Task 5: Layar kendaraan, tamu, dan halaman undangan

**Files:** Modify `tgt/web/app.js`; create `tgt/web/undangan.html`, `tgt/web/undangan.js`.

- [x] **Step 1:** Halaman Kendaraan dan Tamu memakai gaya yang sudah disetujui; pilihan "Motor" **tampil tetapi
  dimatikan** bertuliskan "menyusul di versi 2", supaya batas versi 1 terlihat calon pembeli (spec §2).
- [x] **Step 2:** **Dibuktikan di peramban:** penghuni menambah kendaraan dan mengundang tamu; penghuni kedua tidak
  melihat milik yang pertama; satpam tidak punya tombol tambah **dan** tembakan langsung ke server ditolak; halaman
  undangan terbuka tanpa akun dan QR-nya terbaca.

## Task 6: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7. Gerbang penuh, commit, laporan beserta batasnya.

**Batas yang sudah diketahui sebelum mulai:**
- `bersihkan()` belum dijadwalkan otomatis; ia dipanggil dengan tangan atau lewat penjadwal mesin. Penjadwalan ikut
  pemasangan di PC IBE, yang masih menunggu owner (K71).
- Belum ada HTTPS; sesi masih di memori (T2).
- Tamu belum bisa diberi tahu lewat WhatsApp secara otomatis; tautannya disalin pengundang.
