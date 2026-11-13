# TGT T1: Susunan data dan layanan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37); spec TGT versi 1 disetujui owner (K69).

**Goal:** dasar data TGT yang benar sejak awal — gerbang beralamat sebagai satuan utama, kendaraan dan tamu menempel padanya, dan
kejadian keluar masuk bisa diringkas per jam. Belum ada layar; T1 hanya mesin datanya.

## Perkakas (keputusan agen, bisa dibalik)

**Node 24 dengan `node:sqlite` dan `node:http` bawaan. Tidak ada dependensi baru sama sekali.**
- Repo ini sekarang **nol dependensi**; menambah paket berarti masuk aturan rantai pasok (`CLAUDE.md` §6). Node 24.13 sudah membawa
  SQLite, jadi tidak perlu.
- Satu berkas basis data mudah dipindah antara Mini PC dan VPS, dan mudah dicadangkan.
- Gerbang uji tetap satu: `npm test` diperluas supaya ikut menjalankan `tgt/uji/*.test.mjs`. Tanpa itu, uji TGT tidak akan pernah jalan.
- **Cara membalik:** ganti `tgt/basis.mjs` dengan basis data lain; lapisan layanan di atasnya tidak berubah.

`node:sqlite` masih ditandai percobaan oleh Node, jadi ia mencetak peringatan. Itu dicatat sebagai batas, bukan disembunyikan.

## Tempat berkas

- Kode: `tgt/` (produk, bukan alat bengkel; `tools/` tetap untuk bengkel).
- Basis data berisi plat dan jam keluar masuk = **data pribadi**, jadi berkasnya di `data/tgt/` yang sudah di-gitignore
  (`CLAUDE.md` §4). Uji memakai basis data sementara, tidak pernah yang sungguhan.

## Susunan tabel (versi skema 1)

| Tabel | Isi |
|---|---|
| `grup` | nama, jenis (pribadi/perusahaan), kode undangan |
| `gerbang` | grup, nama, jenis lokasi, **alamat**, kota, koordinat, patokan, status (belum_aktif/aktif) |
| `kendaraan` | gerbang, jenis, merek, warna, **plat**, atas nama, unit |
| `tamu` | gerbang, nama, keperluan, kendaraan tamu, **lama kunjungan (hari)**, kode undangan |
| `kunjungan` | tamu, jam masuk, jam keluar, status |
| `kejadian` | gerbang, waktu, arah, plat, yakin, ciri, kendaraan atau tamu yang cocok |

## Aturan yang ditegakkan di lapisan data, bukan hanya di layar

1. **Versi 1 hanya roda 4 ke atas** (K65). Daftar jenis yang diterima: mobil, pikap, truk, bus. Jenis lain, termasuk motor dan jenis
   yang belum dikenal, **ditolak** dengan pesan yang menyebut sebabnya. Gagal ke arah membatasi, dan daftar putih, bukan daftar larangan.
2. **Plat dinormalkan** sebelum disimpan dan dibandingkan: huruf besar, spasi ganda dibuang. Dua ejaan plat yang sama tidak boleh menjadi
   dua kendaraan.
3. **Plat unik di dalam satu gerbang**, tetapi plat yang sama boleh terdaftar di gerbang lain.
4. **Semua data menempel pada gerbang** (K67). Kendaraan gerbang A tidak pernah terbawa saat membaca gerbang B.
5. **Lewat batas dihitung dari jam masuk + lama kunjungan**, bukan dari tanggal kalender.

## Migrasi

Naik dan turun, diuji bolak-balik (`naik → turun → naik`), karena skema ini akan berubah di T2–T6 dan basis data pelanggan tidak boleh
dibangun ulang dari nol tiap kali.

## Task 1: Basis data dan migrasi

**Files:** Create `tgt/basis.mjs`, `tgt/uji/basis.test.mjs`; modify `package.json`.

- [x] **Step 1: Uji merah:** membuka basis data membuat skema versi 1; versi tercatat; membuka ulang tidak mengulang migrasi;
  `naik → turun → naik` menghasilkan daftar tabel yang sama; basis data di memori dipakai uji.
- [x] **Step 2:** Tulis kodenya, dan perluas `npm test` supaya menjalankan `tgt/uji` juga. Gerbang hijau, dengan jumlah uji sebelum dan
  sesudah disebut.

## Task 2: Layanan gerbang, kendaraan, tamu

**Files:** Create `tgt/layanan.mjs`, `tgt/uji/layanan.test.mjs`.

- [x] **Step 1: Uji merah:** gerbang dibuat dengan nama dan alamat, status awal `belum_aktif`, tanpa alamat ditolak · kendaraan
  motor ditolak dan mobil diterima · plat dinormalkan · plat kembar di gerbang sama ditolak, di gerbang lain diterima · tamu dengan lama
  kunjungan · daftar kendaraan satu gerbang tidak memuat kendaraan gerbang lain.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 3: Kejadian dan ringkasan jam

**Files:** Modify `tgt/layanan.mjs`; uji `tgt/uji/layanan.test.mjs`.

- [x] **Step 1: Uji merah:** kejadian masuk dan keluar dicatat · kunjungan tamu dibuka saat masuk dan ditutup saat keluar · status
  `lewat_batas` muncul bila keluar melewati jam masuk + lama kunjungan, dan tidak muncul bila masih di dalam batas · ringkasan per jam
  memberi angka masuk dan keluar untuk dashboard · ringkasan hanya untuk satu gerbang.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 4: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP dan changelog, `CLAUDE.md` §7 (tempat basis data dan aturan jenis kendaraan). Gerbang penuh, commit.
  **BERHENTI untuk owner** dengan ringkasan apa yang sudah berdiri dan apa yang belum.

**Batas:**
- T1 tidak punya layar dan tidak punya jaringan; belum bisa didemokan.
- Hak akses (peran) baru dikerjakan di T2; T1 belum membedakan siapa yang memanggil layanan.
- `node:sqlite` masih fitur percobaan di Node.
- Belum ada sambungan ke mesin baca plat; kejadian diisi oleh pemanggil.
