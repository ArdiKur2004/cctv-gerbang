# TGT T8: Masuk lewat tautan undangan, dan sesi yang bertahan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dikerjakan mandiri (K37). Dasar: persetujuan owner 26 Okt atas usulan agen — masuk lewat **tautan undangan**
> sebagai cara utama, email OTP menyusul bila perlu.

**Goal:** pengelola membuat anggota, menyalin tautannya, mengirimnya lewat WhatsApp miliknya sendiri. Penghuni
menekan tautan itu **sekali**, dan sesudah itu tidak perlu kode apa pun lagi.

## Kenapa ini lebih baik, bukan sekadar lebih murah

- Pengurus RT **memang kenal warganya**. Tautan yang diberikan langsung lebih dekat dengan cara mereka bekerja
  daripada kode yang dikirim mesin.
- Tidak ada pihak ketiga, tidak ada biaya, tidak ada batas harian yang bisa membuat orang gagal masuk.
- Alamat email menjadi **tidak wajib**: cukup nama. Banyak warga tidak punya email yang mereka buka.

## ⛔ Tautan undangan adalah KUNCI MASUK. Pagarnya

| | |
|---|---|
| Tanda acak **panjang** | 32 bita acak; tidak pernah bisa ditebak |
| Tersimpan **ter-hash** | Yang membaca basis data tidak bisa memakai tautannya |
| **Sekali pakai** | Tautan yang terlanjur tersebar tidak bisa dipakai orang kedua |
| **Kedaluwarsa** | Bawaan 14 hari; tautan lama di riwayat WhatsApp tidak berlaku selamanya |
| Hanya **pengelola** yang membuatnya | Dan hanya untuk grupnya sendiri |
| Bisa **dicabut** | Pengelola membuat tautan baru; yang lama langsung mati |

**Sekali pakai hanya masuk akal bila sesinya bertahan lama.** Karena itu Task 1 mengerjakan sesi yang tersimpan
di basis data — sekaligus menutup batas yang sudah tercatat sejak T4: server yang dinyalakan ulang membuat
semua orang masuk lagi, dan antrean luring baru tersusul sesudah itu.

## Task 1: Sesi yang bertahan

**Files:** Modify `tgt/basis.mjs` (versi 6), `tgt/server.mjs`; create `tgt/sesi.mjs`, `tgt/uji/sesi.test.mjs`.

- [x] **Step 1: Uji merah:** sesi tersimpan dan terbaca kembali sesudah server "dinyalakan ulang" (gudang baru
  atas basis yang sama) · tanda sesi tersimpan **ter-hash** · sesi kedaluwarsa ditolak dan dibersihkan · keluar
  menghapus sesinya · tanda yang dipalsukan ditolak · sesi milik pengguna yang dihapus tidak berlaku.
- [x] **Step 2:** Tulis kodenya; migrasi versi 6 naik-turun, diuji bolak-balik dari basis versi 5 **berisi data**.

## Task 2: Tautan undangan per orang

**Files:** Modify `tgt/akun.mjs`, `tgt/akses.mjs`; create `tgt/uji/undangan-masuk.test.mjs`.

- [x] **Step 1: Uji merah:** pengelola membuat anggota **tanpa email**, cukup nama · tautan dibuat beserta tanda
  acak · tanda tersimpan ter-hash · menukar tanda menghasilkan sesi untuk orang itu · tanda yang sama ditolak
  pada pemakaian **kedua** · tanda kedaluwarsa ditolak · tanda palsu ditolak dengan pesan yang **sama** ·
  satpam dan penghuni tidak bisa membuat tautan · pengelola tidak bisa membuat tautan di grup lain · membuat
  tautan baru **mematikan** yang lama.
- [x] **Step 2:** Tulis kodenya.

## Task 3: Jalur server

**Files:** Modify `tgt/server.mjs`; modify `tgt/uji/server.test.mjs`.

- [x] **Step 1: Uji merah (lewat HTTP):** pengelola meminta tautan dan menerimanya **satu kali** · tanda tidak
  pernah ikut keluar di jalur lain mana pun · menukar tanda memberi kuki sesi · tanda bekas menjawab 401 ·
  penghuni dan satpam ditolak 403 saat membuat tautan.
- [x] **Step 2:** Tulis kodenya.

## Task 4: Layar

**Files:** Modify `tgt/web/app.js`; create `tgt/web/undang.html`, `tgt/web/undang.js`.

- [x] **Step 1:** Halaman Grup: tiap anggota punya tombol **"Buat tautan masuk"**, dan tautannya bisa disalin.
  Tautan hanya tampil **sekali**, dengan kalimat yang menyebut itu.
- [x] **Step 2:** Halaman `undang.html`: penghuni menekan tautan, melihat nama grupnya, menekan "Masuk", lalu
  langsung berada di dalam aplikasi. Tanda yang tidak berlaku memberi pesan yang bisa dimengerti.

## Task 5: Bukti di peramban

- [x] **Step 1:** Pengelola membuat anggota tanpa email, membuat tautannya, lalu tautan itu dibuka di jendela
  lain dan menghasilkan sesi untuk orang itu.
- [x] **Step 2:** Tautan yang sama dibuka **kedua kalinya** ditolak. Dan: server **dinyalakan ulang**, lalu
  dibuktikan sesinya masih berlaku — batas lama dari T4 benar-benar tertutup.

## Task 6: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7, dan `docs/tgt/batas-demo.md` diperbarui. Gerbang penuh,
  commit, laporan.

**Batas yang sudah diketahui sebelum mulai:**
- Tautan dikirim **dengan tangan** oleh pengelola lewat WhatsApp miliknya sendiri; tidak ada pengiriman otomatis.
- Siapa pun yang memegang tautan sebelum dipakai bisa memakainya. Itu sifat tautan masuk, dan pagarnya adalah
  sekali pakai, kedaluwarsa, dan bisa dicabut.
- Email OTP tetap ada berdampingan; mode demo tetap harus dimatikan sebelum ada pengguna sungguhan.
