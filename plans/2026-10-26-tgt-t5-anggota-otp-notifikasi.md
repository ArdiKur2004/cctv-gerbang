# TGT T5: Anggota, masuk lewat email + OTP, satpam sebagai admin, dan notifikasi janggal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dikerjakan mandiri (K37). Dasar: **K72** (owner, 26 Okt), yang mengubah bentuk akun, peran, dan cara masuk.

**Goal:** satu arsitektur yang sama melayani rumah, perumahan, pabrik, dan apartemen — bedanya hanya berapa
anggotanya dan siapa mereka.

## Yang berubah dari yang sudah berdiri, dan kenapa

| Sekarang | Jadi (K72) |
|---|---|
| Masuk dengan nomor WhatsApp + sandi | **Masuk dengan email + OTP**, tanpa sandi |
| Anggota hanya bisa ikut lewat kode undangan | Pemilik akun **juga bisa membuat anggota sendiri** (untuk keluarga, PIC) |
| Satpam tidak boleh mendaftarkan tamu (403) | Satpam **boleh** — ia admin TGT grupnya |
| Yang janggal hanya ditandai di layar | Yang janggal **memanggil satpam lewat notifikasi di HP** |

## ⛔ Dua hal yang tidak boleh dikerjakan diam-diam

1. **Mengirim surel OTP butuh layanan berbayar** — itu keputusan uang (`CLAUDE.md` §8). Rencana ini membangun
   jalur OTP dengan **pengirim yang bisa diganti**; bawaannya **mencetak OTP di layar server dan tidak mengirim ke
   mana pun**. Itu ditulis sebagai batas, dan tidak boleh disebut "OTP sudah jalan".
2. **Mengganti cara masuk mencabut sandi.** Uji yang mengunci cara lama **dibalik menjadi penjaga bahwa sandi tidak
   boleh hidup lagi**, bukan dihapus — kalau tidak, jalur sandi bisa kembali diam-diam dan menjadi jalan masuk kedua
   yang tidak dijaga OTP.

## Empat studi kasus, satu arsitektur (K72)

| Lokasi | Anggotanya | Yang membedakan di kode |
|---|---|---|
| Rumah pribadi | keluarga saja | tidak ada — hanya jumlah anggotanya sedikit |
| Perumahan / RT | beberapa pemilik rumah | tidak ada |
| Pabrik | banyak orang, atau PIC saja | tidak ada |
| Apartemen | penghuninya sendiri | tidak ada |

Ini sengaja: **tidak ada cabang kode menurut jenis lokasi** selain yang sudah ada di aturan putusan. Kalau kelak
muncul cabang baru, itu tanda arsitekturnya mulai pecah dan harus ditanyakan ke owner lebih dulu.

## Task 1: Masuk dengan email + OTP

**Files:** Modify `tgt/basis.mjs` (versi 4), `tgt/akun.mjs`; create `tgt/uji/otp.test.mjs`.

- [ ] **Step 1: Uji merah:** email dinormalkan (huruf kecil, spasi dibuang) dan unik · meminta OTP untuk email yang
  **belum terdaftar** dan yang **sudah** memberi jawaban yang SAMA (tidak membocorkan siapa punya akun) · OTP enam
  angka, **tersimpan ter-hash**, berumur pendek, dan **sekali pakai** · OTP salah ditolak · OTP kedaluwarsa ditolak ·
  **percobaan dibatasi** supaya tidak bisa ditebak dengan mencoba terus · OTP lama batal saat yang baru diminta ·
  pengirim bisa diganti, dan bawaannya tidak mengirim ke mana pun.
- [ ] **Step 2:** Tulis kodenya. Migrasi versi 4 naik-turun, diuji bolak-balik dari basis versi 3 **berisi data**.

## Task 2: Anggota dibuat pemilik akun

**Files:** Modify `tgt/akun.mjs`, `tgt/akses.mjs`; create `tgt/uji/anggota.test.mjs`.

- [ ] **Step 1: Uji merah:** pengelola membuat anggota dengan email saja · anggota baru berperan penghuni · anggota
  yang emailnya sudah punya akun **ditambahkan ke grup**, bukan ditolak dan bukan dibuatkan akun kedua · satpam dan
  penghuni **tidak** boleh membuat anggota · pengelola tidak bisa membuat anggota di grup lain · anggota bisa
  dikeluarkan dari grup, dan pengelola terakhir tidak bisa dikeluarkan.
- [ ] **Step 2:** Tulis kodenya.

## Task 3: Satpam sebagai admin TGT grupnya

**Files:** Modify `tgt/akses.mjs`; modify `tgt/uji/akses-kendaraan.test.mjs`.

- [ ] **Step 1: Uji merah (dan uji lama DIBALIK):** satpam **boleh** mendaftarkan tamu beserta lama kunjungan dan
  alasannya · satpam **tetap tidak boleh** mengubah daftar kendaraan penghuni (itu bukan wewenangnya dan tidak
  diminta owner) · satpam melihat kode undangan tamu yang **ia buat sendiri**.
- [ ] **Step 2:** Tulis kodenya. Uji lama yang menuntut 403 diubah menjadi penjaga batas yang baru, bukan dihapus.

## Task 4: Notifikasi janggal ke HP

**Files:** Create `tgt/web/sw.js`, `tgt/web/manifest.webmanifest`, `tgt/notifikasi.mjs`; modify `tgt/server.mjs`.

- [ ] **Step 1: Uji merah:** kejadian yang **janggal** (putusan bukan `buka`, atau status janggal) menghasilkan satu
  pemberitahuan untuk satpam grup itu · kejadian biasa **tidak** · pemberitahuan memuat alasan yang bisa dibaca orang ·
  pemberitahuan **tidak memuat data pribadi selain plat** · langganan notifikasi hanya boleh dibuat satpam dan
  pengelola · satu perangkat yang berlangganan dua kali tidak menerima dua kali.
- [ ] **Step 2:** Tulis kodenya. PWA bisa dipasang (manifest + service worker), dan **dibuktikan terpasang di HP
  sungguhan** lewat skill `verifikasi-di-perangkat`. Bila notifikasi dorong tidak bisa dibuktikan sampai ke HP,
  **tulis batasnya** — jangan menyebutnya jalan.

## Task 5: Layar menyesuaikan

**Files:** Modify `tgt/web/app.js`, `tgt/web/index.html`.

- [ ] **Step 1:** Layar masuk menjadi dua langkah (email → OTP). Halaman Grup mendapat daftar anggota beserta tombol
  tambah anggota. Halaman Tamu terbuka untuk satpam. Penanda "notifikasi menyala/mati".
- [ ] **Step 2:** **Dibuktikan di peramban:** daftar dengan email, masuk dengan OTP dari layar server, pengelola
  menambah anggota, satpam mendaftarkan tamu, dan kejadian janggal memunculkan pemberitahuan.

## Task 6: Catatan dan BERHENTI

- [ ] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7. Gerbang penuh, commit, laporan beserta batas dan **keputusan
  uang untuk layanan surel**.

**Batas yang sudah diketahui sebelum mulai:**
- OTP **belum benar-benar terkirim** sampai owner memutuskan layanan surel.
- Belum ada HTTPS; notifikasi dorong menuntut HTTPS di peramban, jadi di laptop hanya bisa diuji lewat `localhost`.
- Sesi masih di memori (batas T4): server yang dinyalakan ulang membuat orang harus masuk lagi.
- Tidak ada relay dan tidak ada kamera (T7).
