# Transportation Gate Track (TGT) — konsep dan alur platform

> Ditulis agen 26 Okt 2026 atas permintaan owner. **Status: konsep, menunggu persetujuan owner.** Belum ada kode produk
> (`CLAUDE.md` §1). Yang sudah ada hanya **konsep UI** di [`konsep-ui.html`](konsep-ui.html), sebuah halaman contoh berisi data karangan
> untuk dilihat dan diklik, bukan aplikasi.
>
> Tempatnya di peta fase: TGT adalah **S4 (aplikasi pengelola)** di `SEED.md` §5, ditarik ke depan atas permintaan owner, ditambah
> pendaftaran tamu yang sebelumnya belum dirinci.

## 1. Keputusan owner yang mendasari

| | Isi |
|---|---|
| **Versi 1 hanya roda 4 ke atas** (K65) | Mobil, pikap, truk, bus. Motor menyusul di versi 2. Tujuannya bisa segera didemokan ke perusahaan dan perumahan. |
| **Fokus sementara ke TGT** (K66) | Platform PWA pendaftaran kendaraan dan tamu, dengan dashboard jam keluar masuk. |
| **Ciri dicatat saja** (K63) | Jenis, warna, dan merek dicatat bersama kejadian, tanpa peringatan ke satpam. |
| **Tiap gerbang punya alamat sendiri** (K67) | Gerbang adalah satuan utama, bukan turunan dari grup. Satu lokasi dengan dua pintu menjadi dua gerbang, misalnya "Kantor Rungkut Gate Selatan" dan "Kantor Rungkut Gate Utara". **Koreksi owner 26 Okt:** tidak ada peran tim sales di aplikasi; pemasangan alat dikerjakan tim operasional IBE di luar aplikasi, dan yang dicatat hanya nama serta alamat gerbang. |

## 1b. Susunan data

```
Grup  (PT Sinar Niaga / Cluster Griya Asri)
 └── Gerbang  (nama + alamat + kota + koordinat + patokan)
      ├── Kendaraan terdaftar   (menempel pada gerbang, bukan pada grup)
      ├── Tamu dan kunjungannya
      └── Kejadian keluar masuk  (dipakai dashboard)
```

Semua angka di beranda selalu milik **satu gerbang** yang sedang dibuka. Gerbang baru lahir dengan status "belum aktif" sampai
perangkatnya terpasang dan terhubung, sehingga tim sales bisa mendaftarkan dulu di lapangan tanpa menunggu pemasangan.

## 2. Alur yang diminta owner, dan bentuknya di layar

| Langkah owner | Layar | Catatan rancangan |
|---|---|---|
| 0. Buat gerbang | **Gerbang dan Alamat** | Nama gerbang memuat lokasi dan posisinya. Isian: nama, jenis lokasi, alamat, kota, koordinat (boleh kosong), grup penaung, patokan. Tidak disebut owner di urutan awal, tetapi harus ada lebih dulu, karena kendaraan dan tamu menempel pada gerbang. Pemasangan alatnya di luar aplikasi, oleh tim operasional IBE. |
| 1. Daftar pribadi atau perusahaan | **Pendaftaran** | Perusahaan mendapat isian tambahan: nama badan usaha, NIB atau NPWP, penanggung jawab. Perusahaan boleh mendaftarkan kendaraan atas nama orang lain. |
| 2. Grup: buat baru atau ikut | **Pendaftaran** | Satu grup = satu gerbang atau satu lokasi. Pembuat grup menjadi pengelola dan menyetujui anggota. Yang ikut memasukkan kode undangan. |
| 3. Daftarkan kendaraan | **Kendaraan** | Jenis, merek, warna, plat, atas nama, blok atau divisi. Pilihan "Motor" ada tetapi dimatikan, bertuliskan "menyusul di versi 2", supaya batas versi 1 terlihat jujur. |
| 4. Simpan | **Kendaraan** | Langsung masuk daftar kendaraan terdaftar. |
| 5. Tambah tamu | **Tamu** | Nama tamu (orang atau perusahaan) dan keperluan. |
| 6. Kendaraan tamu | **Tamu** | Isian sama dengan kendaraan tetap, tanpa "atas nama". |
| 7. Lama kunjungan (hari) | **Tamu** | Dihitung dari jam masuk. Lewat dari itu, status menjadi "lewat batas". |
| 8. Simpan | **Tamu** | Menghasilkan kode QR untuk tamu, supaya satpam tidak mencatat tangan. |

**Dua layar tambahan yang tidak disebut owner, tetapi dibutuhkan supaya alurnya utuh:**
- **Layar gerbang (satpam).** Bacaan plat, kecocokan, dan tombol buka palang. Di sini jugalah K63 terlihat: ciri ditampilkan sebagai
  catatan, bukan peringatan. Layar ini harus bekerja saat internet putus, karena gerbang sering di luar jangkauan.
- **Beranda.** Ringkasan hari ini dan grafik jam keluar masuk yang owner minta.

## 3. Dashboard jam keluar masuk

Grafik batang per jam, dua deret: masuk dan keluar. Dipakai untuk melihat jam sibuk (antar pagi dan pulang kerja), yang menentukan
berapa gerbang atau petugas yang dibutuhkan. Angkanya bisa dibuka sebagai tabel, supaya tetap terbaca bagi yang sulit membedakan warna.

Ubin ringkasan: **di dalam sekarang**, **masuk hari ini**, **keluar hari ini**, dan **lewat batas**.

## 4. Fitur tambahan yang owner sebut, dan kenapa belum masuk versi 1

| Fitur | Kenapa belum |
|---|---|
| Manajemen ban | Butuh pencatatan tangan atau sensor TPMS. Tidak ada hubungannya dengan kamera gerbang. |
| Lacak GPS | Butuh alat GPS per kendaraan dan langganan data. Pembelian adalah keputusan owner (`CLAUDE.md` §8). |
| Jadwal servis | Jarak tempuh tidak bisa dibaca kamera; harus diisi tangan atau diambil dari alat GPS. |

Ketiganya ada di layar **Lainnya** sebagai rencana, bukan sebagai fitur yang seolah sudah jalan.

## 5. Rancangan tampilan

- **Cangkang aplikasi:** rel kiri di layar lebar, bilah bawah di ponsel, satu area isi yang berganti. Cocok untuk PWA.
- **Plat nomor digambar seperti plat sungguhan** (putih untuk pribadi, kuning untuk umum, merah untuk pemerintah, sesuai Perpol 7/2021),
  karena itu yang paling cepat dikenali satpam.
- **Warna:** emas sebagai warna merek, dari garis palang gerbang. Grafik memakai biru (masuk) dan hijau laut (keluar); pasangan itu sudah
  diperiksa agar tetap terbedakan oleh mata yang sulit membedakan warna, di tema terang maupun gelap.
- **Tema gelap** disediakan karena layar gerbang dipakai malam hari.
- Huruf: Archivo untuk judul, IBM Plex Sans untuk teks, IBM Plex Mono untuk plat dan angka.

## 6. Yang masih harus diputuskan owner sebelum ada kode

1. **Di mana datanya disimpan?** Mini PC di rumah owner (rencana API, `OPEN-QUESTIONS.md`), atau VPS. Ini menentukan hampir semua
   hal lain.
2. **Siapa yang memakai aplikasi ini:** penghuni, satpam, pengelola, atau ketiganya? Hak aksesnya berbeda.
3. **Apakah tamu perlu memasang aplikasi,** atau cukup menerima tautan atau QR? Rancangan sekarang menganggap cukup tautan.
4. **Apa yang terjadi bila tamu lewat batas?** Sekarang hanya ditandai. Apakah satpam ditelepon, atau pengundangnya yang diberi tahu?
5. **Berapa lama catatan keluar masuk disimpan?** Ini wajib dijawab sebelum ada pengguna sungguhan (UU PDP 27/2022).

## 7. Batas yang harus diingat saat demo

- **Mesin baca plat belum memenuhi sasaran K9 (99% per kelompok).** Angka terakhir di tangkapan layar owner: mobil **14 benar dari 16**
  plat berteks, motor 10 dari 18 (`bukti/2026-10-24-pencari-kendaraan-jualan.md`). Untuk roda 4 ke atas angkanya jauh lebih baik, dan itu
  mendukung keputusan versi 1, tetapi 14 dari 16 bukan 99%.
- Angka itu dari tangkapan layar, **bukan dari kamera di gerbang sungguhan**. Belum pernah ada rekaman gerbang (K43 masih menunggu).
- Ciri: **jenis** bekerja (mobil 12 dari 14), **warna mobil tidak** (4 benar, 4 salah dari 14), **merek mobil tidak** (0 dari 13).
- Konsep UI memakai data karangan. Tidak ada satu pun plat sungguhan di dalamnya.
