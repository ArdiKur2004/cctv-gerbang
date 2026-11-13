# TGT T10: yang sudah dibangun tetapi tidak pernah dijalankan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dikerjakan mandiri (K37). T9 (uji gerbang percontohan) menunggu rekaman dari owner (K43), jadi T10 dikerjakan
> lebih dulu. Nomornya tidak ditukar supaya changelog tetap bisa dibaca.

**Goal:** menutup tiga hal yang **ada dan benar, tetapi tidak pernah dipanggil siapa pun**. Pola ini ketemu tiga
kali berturut-turut di T8, dan yang ketiga adalah yang paling serius.

## Kenapa ini bukan pekerjaan rapi-rapi

Di T8 saya menemukan jalur `POST /api/grup/:id/anggota` yang ada sejak T5 tanpa satu pun layar memanggilnya.
Sapuan sesudahnya menemukan dua lagi. Yang ketiga ini bukan soal kenyamanan:

> **`tgt/simpan.mjs` → `bersihkan()` tidak pernah dipanggil apa pun selain ujinya sendiri.**

Jadi masa simpan yang menurut K71 "ditegakkan di dalam kode" **tidak menghapus apa pun**. Foto kendaraan dan
catatan plat beserta jam keluar masuk menumpuk selamanya. Itu data pribadi menurut UU PDP 27/2022 (§4), dan
di `CLAUDE.md` §7 ia sudah dituliskan sebagai "ditegakkan di kode" — klaim yang belum benar.

**Fungsi yang benar tetapi tak pernah dipanggil terlihat persis seperti fungsi yang bekerja.** 23 uji
`simpan.test.mjs` hijau sejak T3, dan semuanya memanggil `bersihkan()` langsung.

## Task 1: Pembersih masa simpan benar-benar berjalan

**Files:** Modify `tgt/simpan.mjs`, `tgt/server.mjs`; modify `tgt/uji/simpan.test.mjs`.

- [x] **Step 1: Uji merah — RANTAINYA, bukan cabangnya.** Uji yang memanggil `bersihkan()` langsung sudah ada 23
  dan semuanya hijau; itu justru buktinya uji seperti itu tidak cukup. Yang ditulis:
  - **lewat `jalankan()`**, jalur yang dipakai produksi, dengan `TGT_BASIS`/`TGT_FOTO`/`TGT_SIMPAN_*` ke folder
    sementara: baris kejadian tua dan foto tua **benar-benar hilang** sesudah server menyala;
  - penjadwal berjalan **sekali saat menyala**, bukan hanya menunggu selang berikutnya — gerbang yang dinyalakan
    ulang tiap hari tidak boleh berarti tidak pernah bersih;
  - penjadwal **berjalan lagi** pada selang berikutnya;
  - pewaktunya **`unref()`** sehingga proses tetap bisa keluar (Prinsip #3: perkakas tidak boleh menahan mesin);
  - pembersih yang **melempar galat tidak mematikan server**, tetapi galatnya **tercatat**, bukan ditelan;
  - jumlah yang dihapus **dicatat ke layar**, supaya owner bisa melihatnya bekerja.
- [x] **Step 2:** Tulis `jadwalkanBersih()` di `tgt/simpan.mjs` dan panggil dari `jalankan()`.
  ⛔ **`buatServer()` tidak menjadwalkan apa pun**: ia dipakai 50-an uji, dan penjadwal yang ikut di sana akan
  menyapu folder foto SUNGGUHAN di `data/tgt/foto` tiap kali uji jalan. Penjadwalan tinggal di `jalankan()`.

## Task 2: Tombol berhenti berlangganan notifikasi

**Files:** Modify `tgt/web/app.js`; modify `tgt/uji/langganan.test.mjs` atau `server.test.mjs`.

- [x] **Step 1: Uji merah:** satpam yang sudah berlangganan bisa berhenti, dan sesudah berhenti ia **tidak lagi
  menerima** kiriman. Plus penjaga di `web.test.mjs`: tiap jalur `DELETE` di server punya pemanggil di layar.
- [x] **Step 2:** Tombolnya ada, dan tulisannya menyebut keadaan sekarang (berlangganan atau tidak).

## Task 3: Klaim lama yang sudah tidak benar

- [x] **Step 1:** `CLAUDE.md` §7 masih menulis **"sesi masih disimpan di memori server"** pada bagian mode luring
  — sudah tidak benar sejak T8. Dikoreksi, beserta kalimat "antrean baru tersusul sesudah ia masuk".
- [x] **Step 2:** `CLAUDE.md` §7 menulis `bersihkan()` "belum dijadwalkan otomatis"; diperbarui sesudah Task 1.

## Task 4: Sapuan cacat sepupu, sekali lagi

- [x] **Step 1:** Sapuan T8 hanya melihat jalur HTTP. Kali ini: **fungsi yang diekspor dari `tgt/*.mjs` yang
  tidak dipanggil berkas produksi mana pun** (hanya oleh ujinya). Hasilnya dibaca dengan mata, bukan dipercaya.
  Yang ketemu dan nyata diperbaiki atau dicatat.

## Task 5: Bukti dan catatan

- [x] **Step 1:** Gerbang penuh (Node dan lab), angka sebelum→sesudah. Bukti hidup: server dinyalakan dengan
  basis berisi kejadian tua dan foto tua, lalu diperlihatkan keduanya hilang dan jumlahnya tercatat di layar.
- [x] **Step 2:** ROADMAP, changelog, `CLAUDE.md`, commit, laporan.

**Batas yang sudah diketahui sebelum mulai:**
- Penjadwal hidup **di dalam proses server**. Kalau servernya mati, tidak ada yang membersihkan — itu memang
  rancangannya, karena penjadwalan di tingkat sistem ikut pemasangan di PC IBE (K71, menunggu owner).
- Masa simpan bawaan (foto 7 hari, kejadian 90, tamu 30) masih **usulan agen**, belum diperiksa ahli hukum.
  Menyalakan pembersih membuat angka itu mulai berlaku sungguhan: itu disebut ke owner, bukan dianggap beres.
