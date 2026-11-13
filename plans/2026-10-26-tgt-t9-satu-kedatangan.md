# TGT T9: satu kendaraan = satu kedatangan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dasar: persetujuan owner 26 Okt atas jendela **20 detik**. Ini bagian pertama T9 (uji gerbang percontohan)
> yang bisa dikerjakan tanpa rekaman gerbang owner (K43).

**Goal:** kamera gerbang melihat satu kendaraan dalam belasan bingkai. TGT harus memperlakukannya sebagai
**satu kedatangan**, bukan belasan kejadian.

## Cacat yang diperbaiki, diukur bukan diduga

Probe 26 Okt, satu mobil penghuni, lima bingkai masuk lalu tiga bingkai keluar:

```
MASUK   bingkai 1: buka            notifikasi=tidak
        bingkai 2-5: buka          notifikasi=YA  "status janggal"   ← satpam diteriaki 4×
KELUAR  bingkai 1: buka            notifikasi=tidak
        bingkai 2-3: PANGGIL SATPAM                                  ← GERBANG DITAHAN
Beranda: 5 masuk, 3 keluar untuk SATU mobil.
```

Sebabnya bukan aturan K73 — aturan itu benar. Sebabnya TGT belum punya pengertian "satu kedatangan", padahal
mesin baca di lab sudah punya (`rantai.py` → `kedatangan.jsonl`). **Akibat di lapangan: setiap mobil yang
keluar menahan gerbang dan memanggil satpam di bingkai keduanya** — di perumahan 150 mobil sehari, 150
panggilan palsu per hari. Produk tidak bisa dipakai.

## ⛔ Batas keselamatan yang disetujui owner, dan harus tetap tertulis

Di dalam jendela 20 detik, mesin **tidak bisa membedakan** "mobil yang sama masih di depan kamera" dari "mobil
kedua dengan plat tiruan". Yang membatasi risikonya:

| | |
|---|---|
| Jendelanya **pendek** | 20 detik; mobil kedua berplat sama di gerbang dan arah yang sama dalam 20 detik tidak masuk akal |
| **Tidak ada putusan baru** | Bingkai lanjutan mengembalikan putusan bingkai pertama. Tidak ada jalan yang melonggarkan |
| Gerbang **sudah terbuka** | Mobil pertama memang sudah dibukakan; bingkai lanjutan tidak menambah izin |
| Angkanya **satu tempat** | `JENDELA_KEDATANGAN_DETIK`, bisa diubah lewat `TGT_JENDELA_KEDATANGAN` |

**Semua bacaan TETAP DISIMPAN (K74).** Yang berubah hanyalah pengelompokannya: tidak ada bacaan yang dibuang.

## Task 1: Kolom kedatangan dan pengelompokannya

**Files:** Modify `tgt/basis.mjs` (versi 7), `tgt/layanan.mjs`, `tgt/pengaturan.mjs`; create
`tgt/uji/kedatangan.test.mjs`.

- [x] **Step 1: Uji merah:** migrasi versi 7 naik-turun dari basis versi 6 **berisi data** · bacaan kedua atas
  plat yang sama, arah yang sama, dalam 20 detik menunjuk kedatangan yang sama · bacaan di luar jendela menjadi
  kedatangan baru · **arah yang berbeda selalu kedatangan baru** · plat yang berbeda tidak pernah digabung ·
  gerbang yang berbeda tidak pernah digabung · bacaan tanpa plat **tidak digabung** (batas yang dicatat) ·
  jendela dibaca dari satu tempat dan bisa diubah · nilai jendela yang tidak masuk akal memakai bawaan, bukan
  menggabung segalanya.
- [x] **Step 2:** Tulis kodenya.

## Task 2: Putusan tidak dibuat ulang untuk bingkai lanjutan

**Files:** Modify `tgt/akses.mjs`; modify `tgt/uji/kedatangan.test.mjs`.

- [x] **Step 1: Uji merah (lewat `akses.bacaanGerbang`, rantainya):** lima bingkai masuk → **satu** notifikasi,
  bukan lima · tiga bingkai keluar → **nol** `panggil_satpam` · putusan bingkai lanjutan **sama persis** dengan
  bingkai pertama · jawabannya menandai `ulangan: true` supaya layar satpam tidak menampilkannya sebagai
  kejadian baru · ⛔ **janggal yang sungguhan tetap memanggil satpam**: plat yang sama keluar lagi **sesudah**
  jendela lewat tetap `panggil_satpam` (pagar K73 tidak ikut lumpuh).
- [x] **Step 2:** Tulis kodenya.

## Task 3: Beranda menghitung kedatangan, bukan baris

**Files:** Modify `tgt/layanan.mjs`; modify `tgt/uji/kedatangan.test.mjs`.

- [x] **Step 1: Uji merah:** `ubinBeranda` dan `ringkasanJam` menghitung **kedatangan**, jadi satu mobil lima
  bingkai = 1 masuk · angka lama (menghitung baris) dibalik di ujinya, bukan dihapus.
- [x] **Step 2:** Tulis kodenya.

## Task 4: Bukti dan catatan

- [x] **Step 1:** Probe yang sama dijalankan ulang dan hasilnya dibandingkan sebelum→sesudah. Gerbang penuh.
- [x] **Step 2:** SEED.md (K75), ROADMAP, changelog, `CLAUDE.md`, `docs/tgt/batas-demo.md`, commit, laporan.

**Batas yang sudah diketahui sebelum mulai:**
- **Bacaan tanpa plat tidak digabung.** Kendaraan yang platnya tak terbaca di sepuluh bingkai tetap menjadi
  sepuluh kejadian. Itu tidak menahan gerbang dan tidak memanggil satpam palsu, jadi dibiarkan — menggabung
  dari waktu saja bisa menyatukan dua kendaraan tak dikenal yang berbeda, dan itu lebih buruk.
- Jendela 20 detik **tidak membedakan** mobil yang sama dari plat tiruan di dalam jendela itu (lihat tabel).
- Ini **belum** uji gerbang percontohan yang sebenarnya: itu butuh rekaman dari gerbang sungguhan (K43).
