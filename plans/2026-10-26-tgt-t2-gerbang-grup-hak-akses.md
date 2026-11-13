# TGT T2: Gerbang, grup, dan hak akses — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri (K37); spec TGT versi 1
> disetujui owner (K69), tempat data diputuskan owner (K70).

**Goal:** akun pribadi dan perusahaan bisa dibuat, grup bisa dibuat atau diikuti, gerbang beralamat bisa didaftarkan — dan
**tiga peran benar-benar dibatasi**, bukan hanya di layar.

## Bahaya utama rencana ini, dan cara menghindarinya

**Pagar hak akses yang benar tetapi tak pernah dipanggil terlihat persis seperti pagar yang bekerja.** Itu sudah pernah
terjadi di proyek lain milik owner: `billingActive()` ada, teruji, dan **nol pemanggil produksi**.

Karena itu T2 memakai susunan ini:
- `tgt/layanan.mjs` tetap lapisan data mentah **tanpa hak akses**. Ia dipakai mesin gerbang, yang tidak punya pengguna.
- `tgt/akses.mjs` menjadi **satu-satunya pintu** untuk lapisan web. Tiap fungsinya menuntut `sesi` dan memeriksa peran.
- **Uji rantai (wajib, bukan tambahan):** satu uji membaca sumber `tgt/server.mjs` dan **gagal bila ia mengimpor
  `layanan.mjs` langsung**. Tanpa uji itu, lapisan web bisa menembus pagar dan semua uji tetap hijau.
- Satu uji lagi menembak lewat **HTTP sungguhan**: satpam yang mencoba membuat gerbang harus ditolak oleh server, bukan
  hanya oleh fungsinya.

## Tiga peran (spec §4)

| Peran | Boleh | Tidak boleh |
|---|---|---|
| **pengelola** | Membuat gerbang beserta alamatnya; semua isi grupnya | Menyentuh grup lain |
| **satpam** | Membaca daftar izin gerbangnya, layar gerbang | Mengubah daftar kendaraan, membuat gerbang, menghapus catatan |
| **penghuni** | Kendaraan miliknya dan tamu yang ia undang | Melihat kendaraan atau tamu orang lain |

**Gagal ke arah menutup:** peran yang tidak dikenal, sesi yang tidak ada, atau grup yang tidak cocok = **ditolak**, bukan
dilewatkan. Daftar putih, bukan daftar larangan.

## Tempat simpan (K70)

Jalur basis data dan jalur foto **dibaca dari pengaturan**, tidak dipaku di kode, karena NAS akan dipasang nanti. Bawaannya
`data/tgt/` (di-gitignore). Uji tidak pernah menyentuh jalur sungguhan.

## Task 1: Migrasi versi 2 — pengguna dan keanggotaan

**Files:** Modify `tgt/basis.mjs`; create `tgt/uji/basis-v2.test.mjs`.

- [x] **Step 1: Uji merah:** versi skema menjadi 2 · tabel `pengguna` dan `anggota` ada · **basis versi 1 yang sudah berisi
  data naik ke versi 2 tanpa kehilangan data** (ini yang membuat migrasi berguna) · `naik → turun → naik` tetap menghasilkan
  susunan yang sama · turun dari 2 ke 1 menyisakan tabel versi 1 beserta datanya.
- [x] **Step 2:** Tulis migrasi versi 2. Gerbang hijau, angka sebelum→sesudah disebut.

## Task 2: Akun dan keanggotaan grup

**Files:** Create `tgt/akun.mjs`, `tgt/uji/akun.test.mjs`.

- [x] **Step 1: Uji merah:** daftar akun dengan nomor WA dan sandi · sandi disimpan **ter-hash** (scrypt dari `node:crypto`,
  tanpa paket luar) dan tidak pernah tersimpan apa adanya · nomor WA dinormalkan (08… dan +62… dianggap sama) dan unik ·
  masuk dengan sandi benar berhasil, sandi salah gagal, dan **pesan gagalnya sama** untuk nomor tak ada maupun sandi salah ·
  pembuat grup otomatis menjadi `pengelola` · ikut grup dengan kode undangan menjadi `penghuni` · kode salah ditolak ·
  satu orang bisa berada di dua grup dengan peran berbeda.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 3: Pintu hak akses

**Files:** Create `tgt/akses.mjs`, `tgt/uji/akses.test.mjs`.

- [x] **Step 1: Uji merah:** untuk tiap peran, tiap operasi T2 diuji **boleh** dan **ditolak** · tanpa sesi = ditolak ·
  sesi ke grup lain = ditolak · peran yang tidak dikenal = ditolak · penghuni hanya melihat kendaraannya sendiri ·
  satpam membaca daftar izin tetapi tidak bisa mengubahnya · pesan penolakan tidak membocorkan isi grup lain
  (misalnya tidak membedakan "gerbang tidak ada" dari "bukan grup Anda").
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 4: Server dan uji rantai

**Files:** Create `tgt/server.mjs`, `tgt/pengaturan.mjs`, `tgt/uji/server.test.mjs`.

- [x] **Step 1: Uji merah:** **uji rantai** — sumber `tgt/server.mjs` tidak boleh mengimpor `layanan.mjs` (uji ini dibuktikan
  bisa merah dengan sengaja menambah impor itu sementara) · permintaan tanpa sesi ditolak 401 · **satpam yang membuat gerbang
  lewat HTTP ditolak 403** · pengelola berhasil · sesi disimpan sebagai cookie `HttpOnly` · jalur basis data dibaca dari
  pengaturan, bukan dipaku.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 5: Layar gerbang dan grup

**Files:** Create `tgt/web/` (dari konsep UI yang disetujui, K68); modify `tgt/server.mjs`.

- [x] **Step 1:** Ambil cangkang dan gaya dari `docs/tgt/konsep-ui.html` (disetujui K68), sambungkan halaman pendaftaran,
  grup, dan Gerbang dan Alamat ke server. Data karangan dibuang; yang tampil datang dari basis data.
- [x] **Step 2:** **Dibuktikan di peramban**, bukan hanya di uji: daftar akun, buat grup, buat gerbang, dan lihat gerbang itu
  muncul. Lalu masuk sebagai satpam dan buktikan tombol buat gerbang **tidak ada, dan jalur HTTP-nya tetap menolak**.

## Task 6: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7. Gerbang penuh, commit, laporan ke owner beserta batasnya.

**Batas yang sudah diketahui sebelum mulai:**
- Belum ada HTTPS; sandi lewat jaringan lokal masih terbuka. Itu dicatat dan diselesaikan sebelum ada pengguna sungguhan.
- Belum ada cadangan sampai NAS dibeli (K70).
- Letak PC belum pasti ("seperti Yanmar"), jadi cara penyusulan data dari gerbang belum bisa diputuskan — itu T4/T6.
- Belum ada sambungan ke mesin baca plat (T6).
