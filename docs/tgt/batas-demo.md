# TGT — apa yang boleh dijanjikan saat demo, dan apa yang belum

> Ditulis agen 26 Okt 2026, untuk dipakai owner saat memperagakan TGT ke perusahaan dan perumahan.
> Semua angka di sini **dibaca dari berkas bukti**, bukan dari ingatan. Sumbernya disebut di tiap baris.
>
> Alasan dokumen ini ada: menjanjikan yang belum ada lebih mahal daripada menunda penjualan. Pembeli yang
> kecewa saat pemasangan tidak akan membeli yang kedua, dan akan bercerita ke calon pembeli lain.

## 1. Yang boleh ditunjukkan dan dijanjikan

| Yang ditunjukkan | Keadaan |
|---|---|
| **Masuk lewat tautan undangan, tanpa email sama sekali** | Jalan. Pengelola membuat anggota (cukup nama), menyalin tautannya, dan mengirimnya lewat WhatsApp sendiri. Penghuni menekannya sekali |
| Daftar akun dengan email, masuk tanpa sandi | Jalan. Sekarang jalur kedua, bukan jalur utama |
| Tetap masuk walau server dinyalakan ulang | Jalan. Sesi tersimpan 90 hari di basis data |
| Grup: buat sendiri atau ikut dengan kode undangan | Jalan |
| Satu grup punya **beberapa gerbang** | Jalan |
| Pemilik akun membuat anggota sendiri (keluarga, PIC) | Jalan, dari layar Grup. **Email tidak wajib** |
| Tiga peran: pengelola, satpam, penghuni | Jalan, dan **benar-benar membatasi di server** |
| Penghuni mendaftarkan kendaraannya sendiri | Jalan |
| Tamu diundang penghuni **atau satpam**, dengan lama kunjungan | Jalan |
| Tamu menerima tautan berisi **QR** | Jalan; QR terbukti terbaca pembaca di luar kode kami |
| Layar satpam: putusan beserta **alasannya dalam bahasa biasa** | Jalan |
| **Mode luring**: catatan tertahan saat internet putus, lalu menyusul | Jalan, dibuktikan dengan mematikan server di tengah jalan |
| Kamera: satu gambar → plat → putusan → **status masuk/keluar berubah** | Jalan |
| Baca plat | Jalan, **dengan angka di bagian 3** |
| Jenis kendaraan dikenali | Jalan, **dengan angka di bagian 3** |

## 2. Yang TIDAK boleh dijanjikan

| | Kenapa |
|---|---|
| **Merek kendaraan** | Tidak bekerja untuk mobil: **0 benar dari 13** di set uji. Vonis tertulis: "dugaan tidak didukung" (`bukti/2026-10-26-merek-mobil-resolusi.md`). **Tidak dipasang** di produk |
| **Warna kendaraan** | Tidak bekerja untuk mobil: abu-abu/perak **0 benar dari 5**, dan 15 dari 37 dijawab "tak yakin" (`bukti/2026-10-24-jenis-dan-warna.md`). **Tidak dipasang** |
| **Motor** | Versi 1 hanya roda 4 ke atas (K65). Pilihannya tampil di layar tetapi dimatikan, supaya batasnya terlihat jujur |
| **Membuka palang sungguhan** | Belum ada perangkat, belum ada relay. Yang ada baru putusan yang dicatat dan ditampilkan |
| **Notifikasi sampai ke HP** | Kodenya ada dan kirimannya diterima layanan Google (jawaban 201), tetapi **belum pernah terbukti muncul di layar HP mana pun** |
| **Kode masuk lewat email** | Layanan surel belum dibeli. Saat demo, kodenya **tampil di layar** dengan tulisan "MODE DEMO". **Sejak Rencana T8 ini tidak lagi menghalangi apa pun**: peragakan lewat tautan undangan, dan email tidak perlu disebut |
| **Tautan undangan dikirim otomatis** | Tidak ada. Pengelola menyalin tautannya dan mengirimnya sendiri lewat WhatsApp miliknya. Itu memang rancangannya, bukan yang belum jadi |

## 3. Angka yang harus disebut bila ditanya

**Baca plat** — dari tangkapan layar owner, **bukan kamera gerbang sungguhan**:

- mobil: **14 benar dari 16** plat berteks
- rantai utuh di tangkapan uji: **24 dari 34**
- sasaran kami sendiri (K9) adalah **99% per kelompok**, dan itu **belum tercapai**

**Jenis kendaraan** (`bukti/2026-10-24-jenis-dan-warna.md`):

- mobil: **12 benar dari 14** — sekitar **1 dari 7 salah**
- karena itu jenis **tidak pernah menahan gerbang**; ia hanya memberi tahu satpam

**Kecepatan**: sekitar **81 ms** per gambar di laptop ini, mesin dimuat sekali di awal (3 detik).

## 4. Kalimat yang aman dipakai

> "Plat nomor sudah terbaca, dan angkanya ini — belum 99%, dan kami tidak akan mengatakan sudah, sebelum diuji
> di kamera gerbang Bapak sendiri."

> "Jenis kendaraan sudah dikenali dan dicatat. Kalau jenisnya tidak cocok dengan yang terdaftar, satpam diberi
> tahu — tetapi gerbang tetap dibuka, karena mesinnya masih salah sekitar satu dari tujuh, dan kami tidak mau
> menahan penghuni yang tidak bersalah."

> "Merek dan warna belum. Untuk motor sudah bisa, untuk mobil belum, dan kami sedang mengerjakannya."

> "Yang belum ada: perangkat gerbangnya. Yang Bapak lihat ini aplikasinya dan mesin bacanya."

Tentang cara warga masuk:

> "Warga tidak perlu email dan tidak perlu mengingat sandi. Bapak sebagai pengurus membuat namanya, lalu mengirimkan satu tautan lewat WhatsApp. Ia menekannya sekali, dan sesudah itu HP-nya ingat sendiri."

> "Tautannya hanya bisa dipakai sekali dan berlaku dua minggu. Kalau salah kirim, Bapak buat tautan baru dan yang lama langsung mati."


## 5. Yang harus disiapkan sebelum ada pelanggan sungguhan

1. **HTTPS** — sudah menyala untuk uji lewat Tailscale, tetapi pemasangan di lokasi pelanggan belum dirancang.
2. ~~**Layanan surel** untuk kode masuk~~ — **tidak lagi menghalangi** sejak Rencana T8: masuk lewat tautan undangan tidak memakai email. Layanan surel menjadi pilihan, bukan syarat.
3. **Cadangan data** — belum ada sampai NAS dibeli (K70). Satu disk rusak berarti catatan hilang.
4. **Mematikan MODE DEMO.** Selama ia menyala, siapa pun yang tahu alamat email seseorang bisa masuk sebagai
   orang itu.
5. **Masa simpan data pribadi** diperiksa ahli hukum. **Keadaan sekarang (K74, owner 26 Okt): SEMUA DATA
   DISIMPAN, tidak ada yang dihapus.** Angka lama (foto 7 hari, catatan 90 hari) adalah tebakan agen yang
   owner koreksi; penghapusan hanya menyala bila disetel sengaja. Yang boleh dijanjikan ke pembeli: **catatan
   keluar masuk tersimpan selamanya.** Yang harus disebut: menyimpan selamanya adalah hal yang perlu
   diperiksa ahli hukum terhadap UU PDP, dan **cadangan belum ada** sampai NAS dibeli — jadi "tersimpan
   selamanya" masih bergantung pada satu disk yang belum tersalin ke mana pun.
6. **Ukuran penyimpanan**, bila ditanya: catatan tumbuh **10 MB setahun** pada 150 kendaraan sehari (diukur,
   190 bita per kejadian) — kecil. **Foto bukti** yang akan menjadi besar: 4–42 GB setahun per gerbang
   tergantung ukuran gambar, dan foto itu **belum dibangun**. TGT berhenti menulis gambar baru bila sisa ruang
   disk di bawah 5 GB, dan tidak pernah menghapus catatan untuk memberi tempat.
7. **Rekaman gerbang sungguhan** (K43) — semua angka baca plat berasal dari tangkapan layar dan video internet.
