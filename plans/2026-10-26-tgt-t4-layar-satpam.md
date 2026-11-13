# TGT T4: Layar satpam, aturan putusan, dan mode luring — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Wajib juga `honest-slice-execution`.
> Dikerjakan mandiri (K37). Spec disetujui K69; tempat data K70; mesin dan masa simpan K71.

**Goal:** satpam punya layar yang menunjukkan apa yang lewat gerbang, apa putusannya, dan kenapa — dan layar itu
**tetap bekerja saat internet putus**, lalu menyusulkan catatannya saat tersambung lagi.

## ⛔ Keselamatan gerbang — baca sebelum menulis baris pertama

Ini bagian paling berbahaya di seluruh produk. Aturan `CLAUDE.md` §3 berlaku penuh:

1. **Produk hanya memberi perintah BUKA.** Tidak pernah perintah tutup, dan tidak menggantikan pengaman gerbang
   (fotosel, pembatas gaya).
2. **Sampai Fase 5, tidak ada keluaran relay sama sekali.** Rencana ini **tidak** menulis kode yang menggerakkan
   perangkat apa pun. Yang dihasilkan hanya **putusan yang dicatat dan ditampilkan**. Siapa pun yang kelak
   menyambungkan relay harus melewati keputusan owner lebih dulu.
3. **Ragu = tidak membuka**, dengan pengecualian K46 yang dirinci di bawah.
4. **Ciri hanya dicatat** (K63): jenis, warna, merek tidak pernah menahan gerbang dan tidak memberi peringatan.
5. Tamu **lewat batas tetap dibukakan** (spec §7); yang terjadi hanya pemberitahuan ke pengundang.

## Aturan putusan (K46), beserta bacaan agen yang perlu dikoreksi owner bila salah

K46 apa adanya: *"bacaan yang ragu pada 1–2 posisi boleh membuka bila tidak ada plat berstatus sama (misalnya
sama-sama MASUK) yang cocok di posisi yang yakin; bila ada, satpam dipanggil. Di perumahan hanya bila cocok tepat
satu plat penghuni. Lebih dari 2 posisi ragu tidak pernah menyalakan relay."*

**Bacaan agen yang akan dikodekan:**

| Keadaan | Putusan |
|---|---|
| Lebih dari 2 posisi ragu | **tidak pernah buka** — tanpa pengecualian, bahkan bila hanya satu calon |
| 0–2 posisi ragu, **tepat satu** plat terdaftar cocok di posisi yang yakin dan statusnya masuk akal untuk arahnya | **buka** |
| 0–2 posisi ragu, **dua atau lebih** calon berstatus sama | **panggil satpam** |
| Tidak ada calon sama sekali | **tidak dikenal** — satpam memutuskan dengan tangan |
| Di **perumahan**, bacaan ragu yang calonnya hanya **tamu** (bukan penghuni) | **panggil satpam** |

"Status" dibaca dari kejadian terakhir plat itu: yang sedang **di luar** masuk akal untuk arah masuk, yang sedang
**di dalam** masuk akal untuk arah keluar. Itulah guna kalimat "berstatus sama" di K46.

**Dua hal yang owner perlu periksa:** (a) bahwa pembatasan "hanya plat penghuni" di perumahan memang hanya berlaku
untuk bacaan yang **ragu**, bukan untuk bacaan yang yakin — tamu yang diundang dengan benar dan terbaca jelas tetap
dibukakan; (b) bahwa plat yang **sama persis** terbaca tanpa ragu tetap dibuka walau statusnya tidak masuk akal
(misalnya terbaca masuk dua kali), karena kamera bisa melewatkan satu kejadian — yang terjadi hanya catatan
"status tidak masuk akal", bukan penolakan.

## Mode luring

Kotak di gerbang harus tetap bekerja saat server mati atau internet putus (spec §5):
- **daftar izin** disalin ke perangkat dan dipakai saat luring;
- **kejadian diantrekan** di perangkat, lalu disusulkan saat tersambung;
- penyusulan **tidak boleh menggandakan** kejadian: tiap kejadian punya penanda sendiri dari kotaknya.

## Task 1: Aturan putusan

**Files:** Create `tgt/putusan.mjs`, `tgt/uji/putusan.test.mjs`.

- [x] **Step 1: Uji merah:** tiap baris tabel di atas diuji · lebih dari 2 ragu tidak pernah buka **walau hanya satu
  calon** · pencocokan menghormati panjang plat · posisi ragu di luar jangkauan ditolak · daftar kosong tidak pernah
  buka · perumahan dengan calon tamu saja memanggil satpam · **putusan tidak pernah "buka" untuk masukan yang tidak
  dikenal bentuknya** (gagal ke arah menutup) · alasan putusan selalu terisi dan bisa dibaca orang.
- [x] **Step 2:** Tulis kodenya. Gerbang hijau, angka sebelum→sesudah.

## Task 2: Jalur kotak gerbang dan layar satpam

**Files:** Modify `tgt/server.mjs`, `tgt/akses.mjs`; modify `tgt/uji/server.test.mjs`.

- [x] **Step 1: Uji merah:** kotak gerbang mengirim bacaan dan menerima putusan **beserta alasannya**; kejadiannya
  tercatat · penanda kejadian yang sama dikirim dua kali **tidak** menggandakan catatan · satpam melihat kejadian
  terbaru gerbangnya · satpam boleh membuka dengan tangan, dan itu tercatat sebagai **dibuka satpam**, bukan sebagai
  putusan mesin · penghuni **tidak** boleh membuka · daftar izin untuk luring hanya boleh diambil satpam dan
  pengelola.
- [x] **Step 2:** Tulis kodenya. Uji rantai lama tetap hijau.

## Task 3: Luring di perangkat

**Files:** Create `tgt/web/luring.js`; modify `tgt/web/app.js`.

- [x] **Step 1: Uji merah** (yang bisa diuji di Node): antrean kejadian disimpan dan dibaca kembali · penyusulan
  membuang yang sudah berhasil terkirim dan **menahan** yang gagal · penanda kejadian unik.
- [x] **Step 2:** Tulis kodenya.

## Task 4: Layar satpam

**Files:** Modify `tgt/web/app.js`, `tgt/web/gaya.css`.

- [x] **Step 1:** Layar gerbang: bacaan terakhir, putusan beserta alasannya dengan kata (bukan warna saja), plat
  digambar seperti plat sungguhan, ciri ditampilkan sebagai catatan (K63), pencarian plat dengan tangan, tombol buka
  manual, dan penanda **luring** yang jelas beserta jumlah kejadian yang belum tersusul.
- [x] **Step 2:** Tombol buka manual **tidak menggerakkan apa pun**; ia hanya mencatat. Tulisannya menyebut itu.

## Task 5: Bukti di peramban, termasuk uji cabut internet

- [x] **Step 1:** Jalankan server, kirim beberapa bacaan, lihat putusannya di layar.
- [x] **Step 2:** **Matikan servernya di tengah jalan**, kirim kejadian lagi dari layar, nyalakan lagi, dan buktikan
  tidak ada kejadian yang hilang maupun tergandakan.

## Task 6: Catatan dan BERHENTI

- [x] **Step 1:** ROADMAP, changelog, `CLAUDE.md` §7. Gerbang penuh, commit, laporan beserta batasnya dan **dua
  pertanyaan K46 untuk owner**.

**Batas yang sudah diketahui sebelum mulai:**
- **Tidak ada relay, tidak ada perangkat.** Putusan hanya dicatat dan ditampilkan.
- Belum ada kamera: bacaan masuk lewat jalur server, dan sambungan ke mesin baca plat baru di T6.
- Belum ada HTTPS; sesi masih di memori.
- Mesin baca plat belum memenuhi K9, jadi angka benar-salahnya bukan tanggung jawab rencana ini.
