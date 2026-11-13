# Rantai utuh di video riset: pertama kali dijalankan dan dinilai owner

> Rencana 14 Fase 0A, dijalankan 16 Okt 2026 atas lampu hijau owner ("A. Jalankan sekarang"), dengan lembar yang diperiksa owner
> (K32). **Video daring, bukan kamera gerbang: bukan bukti K9.** Pencari plat dan pembaca bertanda `RISET-SAJA`.
> Sumber angka: [`2026-10-16-rantai-video-ulang-ringkasan.json`](2026-10-16-rantai-video-ulang-ringkasan.json) (hitungan dan
> kecepatan), [`2026-10-16-rantai-video-ringkasan.json`](2026-10-16-rantai-video-ringkasan.json) (jalan pertama, hitungan
> identik), dan [`2026-10-16-rantai-video-nilai.json`](2026-10-16-rantai-video-nilai.json) (dari jawaban owner) di folder ini.
> Isinya hitungan saja. Sebelum disalin, ketiganya diperiksa tidak memuat satu pun dari 10.521 teks plat dan nama berkas,
> termasuk 221 bacaan rantai itu sendiri. Pemeriksanya diuji dulu: dari 782 teks yang pasti ada di berkas uji, 784 ditemukan.

## 1. Rantai yang dijalankan

Lima langkah spec 2.1, kecuali langkah 2:
1. **Cari plat:** YOLOX-Nano-640 (K31), dengan ambang 0,25 yang dibaca dari `mesin.json` hasil validasi.
2. **Luruskan:** belum ada. Potongan dibaca apa adanya, dengan diperlebar 5%.
3. **Baca huruf:** fpo-indo-1 (ONNX). Keyakinan tiap bacaan adalah peluang terendah di semua slot.
4. **Cek pola:** hanya bacaan yang sesuai pola plat Indonesia yang dihitung.
5. **Gabung:** kotak diikuti dari gambar ke gambar (IoU minimal 0,3, jeda paling lama 1 detik). Plat yang terlihat minimal 2 kali
   dihitung satu kedatangan. Statusnya **"yakin"** bila teks terbanyak didukung minimal 2 bacaan **dan** minimal 60% bacaan sah;
   selain itu **"ragu"**, artinya gerbang tidak dibuka.

Ambang-ambang ini ditetapkan di rencana sebelum hasil dilihat, dan **tidak diubah sesudahnya**. Dari tiap detik video diambil 5
gambar.

## 2. Hitungan

30 video (17 bersudut gerbang, 13 kamera diam lain), 33.906 gambar sampel:

| Sudut | Video | Gambar sampel | Penampakan plat | Kedatangan | Jalur terlihat sekali |
|---|---|---|---|---|---|
| Gerbang | 17 | 20.881 | 6.007 | 219 | 496 |
| Kamera diam lain | 13 | 13.025 | 682 | 50 | 86 |
| **Jumlah** | 30 | 33.906 | 6.689 | **269** (13 yakin, 256 ragu) | 582 |

- **Satu video gerbang 640×360 yang panjang menyumbang 149 dari 269 kedatangan.** Ada 7 video tanpa kedatangan sama sekali.
- **Per kategori video:** siang 248, malam 16, tak jelas 5.
- **Jalan ulang memberi hasil identik:** SHA-256 `kedatangan.jsonl` sama, dan 269 potongan di kedua jalan.

## 3. Dari lembar owner

Owner memeriksa 120 dari 269 kedatangan. Barisnya dipilih tetap, bergiliran antarvideo, dari urutan SHA-256.

| Jawaban owner | Baris | Status rantai |
|---|---|---|
| **Bukan plat** | **99** | 7 yakin, 92 ragu |
| Tak terbaca (manusia pun tidak bisa membaca) | 14 | 14 ragu |
| Plat yang bisa dinilai | **7** | lihat di bawah |

| 7 plat yang dinilai | Jumlah |
|---|---|
| Benar dan yakin (gerbang membuka bila terdaftar) | 3 |
| Benar tetapi ragu (gerbang tidak membuka) | 2 |
| Salah dan ragu (mesin menahan diri) | 2 |
| **Salah tetapi yakin** (bahaya buka-salah) | **0** |

- **Tujuh plat terlalu sedikit untuk disimpulkan.** Rentang 95% untuk benar-yakin adalah 16–75%.
- **Tidak ada motor** di antara baris yang plat. Enam plat dari video siang dan satu dari video "tak jelas".
- **Dua baris yang salah** kemungkinan kendaraan yang sama, diam lama (masing-masing terlihat lebih dari 20 kali), dan terpecah
  menjadi dua kedatangan. Owner menulis nomor plat yang benar untuk keduanya. Nomor itu tidak disalin ke berkas mana pun
  (`CLAUDE.md` §4).

## 4. Yang paling penting: "yakin" tidak melindungi dari benda bukan plat

- **Dari 10 kedatangan "yakin" di lembar, 7 adalah benda bukan plat.** Yang benar plat hanya 3.
- **Bukan plat di 82% baris (99 dari 120).** Pencari plat dilatih dengan 393 foto plat-lighting, yang sebagian besar plat dari
  dekat, dan di sana kotak palsunya sedikit (12 untuk 99 plat validasi). Di video riset ia menemukan banyak benda lain. Delapan
  di antaranya terlihat lebih dari 20 kali, kemungkinan benda diam seperti tulisan atau papan; ini dugaan agen, karena agen tidak
  melihat gambarnya.
- **Akibatnya bagi keselamatan:** yang menahan buka-salah sekarang hanya pemeriksaan daftar izin (spec 3.1). Benda bukan plat
  yang dibaca "yakin" hanya membuka gerbang bila bacaannya kebetulan sama dengan plat terdaftar. Itu jarang, tetapi bukan nol.
  Penahan kedua harus dibangun di pencari plat itu sendiri.

## 5. Kenapa hampir semua "ragu"

Hitungan dari `kedatangan.jsonl`, tanpa membuka teksnya:
- **Bacaan per gambar umumnya sesuai pola:** 5.374 dari 6.107 penampakan di kedatangan (88%).
- **Masalahnya kesepakatan.** Dari 256 yang ragu, 203 punya dua bacaan sah atau lebih yang tidak sama persis. 35 tidak punya
  bacaan sah sama sekali, dan 18 hanya punya satu.
- **Artinya:** pembaca memberi teks yang sedikit berbeda dari gambar ke gambar. Sebagian besar "ragu" itu adalah benda bukan
  plat, dan untuk benda bukan plat, ragu justru benar. Untuk plat sungguhan, pemungutan suara per huruf mungkin lebih kuat
  daripada per teks utuh; ini belum diuji.

## 6. Kecepatan

**Laptop** (Ryzen 7 8700F, 2 utas; dari jalan ulang yang bersih):

| Bagian | Median | p95 |
|---|---|---|
| Dekode satu gambar sampel | 0,67 ms | 2,06 ms |
| Cari plat per gambar (letterbox, model, NMS) | 17,7 ms | 20,2 ms |
| Baca per potongan | 13,9 ms | 15,8 ms |

Detik video dari plat pertama terlihat sampai bacaan "yakin": median 0,2 detik, p95 0,4 detik (13 kedatangan yakin).

Dekode murah karena separuh gambar sampel berasal dari video 640×360. Gambar yang dilewati juga ikut didekode oleh pembaca
video, tetapi waktunya tidak dihitung, karena kamera gerbang kelak cukup mengirim gambar yang dipakai.

**Taksiran Mini PC** (bacaan agen, bukan ukuran):
- Model Nano-640 sekitar 150 ms dan pembaca sekitar 100 ms per potongan, dari ukuran di Mini PC (Rencana 12, 13, 2 utas).
- Dekode laptop dikali 8–10.
- Totalnya **sekitar 0,26 detik per gambar dengan satu plat**, jadi sekitar 4 gambar per detik per kamera.
- Keputusan "yakin" butuh minimal dua bacaan yang sama. Bila platnya terbaca konsisten, itu sekitar 0,5 detik kerja ditambah
  0,2 detik video, di bawah sasaran dua detik (spec 2.6).
- **Bila bacaan tidak konsisten,** seperti pada sebagian besar kedatangan di sini, keputusan "yakin" tidak pernah datang, dan
  gerbang tidak membuka.

## 7. Batas, apa adanya

- **Video daring, bukan kamera gerbang.** Semua video bersudut gerbang adalah siang. Banyak plat terlalu kecil atau buram: 14 dari
  21 plat di lembar tak terbaca bahkan oleh manusia.
- **Kendaraan yang platnya tidak pernah ditemukan tidak muncul di lembar,** jadi angka plat terlewat tidak terukur di sini.
- **Lembar memuat 120 dari 269 kedatangan.** Satu kendaraan bisa terpecah menjadi dua kedatangan.
- **Langkah meluruskan belum ada.**
- **Pencari plat dan pembaca `RISET-SAJA`.**
- **Mini PC hanya ditaksir:** video riset dan model hasil latih tidak dibawa ke sana (K15).

## 8. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 107; lab 190 → 199 → 203; uji image tambahan 17 → 19. Tiap uji baru terlihat merah dulu.
- **Gangguan sesi lain, lagi.**
  - Saat rantai akan dijalankan pertama kali, uji mutasi milik sesi lain sedang menyala, jadi ditunggu sampai selesai.
  - Saat jalan pertama berlangsung, uji sesi lain menyala lagi sekitar 6 dari 13 menit. Ini tertangkap oleh perekam proses yang
    **ditambahkan di luar rencana**.
  - Rantai lalu dijalankan ulang ke `rantai-video-ulang` saat tenang, dengan 75 rekaman tanpa uji sesi lain. Hasilnya identik,
    dan kecepatan diambil dari jalan ulang.
- **Jawaban owner diterjemahkan ke nomor baris:** benar 5, salah 2, tak terbaca 14, bukan plat 99 ("sisanya bukan plat"),
  motor 0.
- **Diagnosis di luar rencana**, keduanya hanya mencetak hitungan:
  - sebab "ragu" (`data/alat-sementara/sebab-ragu-14.py`);
  - status rantai per jenis jawaban owner (`data/alat-sementara/status-per-jenis-14.py`).

## 9. Berikutnya (usulan agen)

Rantai sudah jalan utuh dan terukur. Yang paling lemah ada dua: pencari plat yang menemukan benda bukan plat, dan bahan video
yang terlalu kecil untuk dibaca. Pilihan berikutnya diajukan ke owner:
- **Rencana 15: laporan Fase 0A** dan keputusan owner (lanjut, tunggu lokasi, atau ubah arah). Temuan ini masuk ke laporan.
- **Atau lebih dulu memperkuat pencari plat** dengan contoh "bukan plat" dari video riset. Ini butuh lembar lagi untuk owner.
