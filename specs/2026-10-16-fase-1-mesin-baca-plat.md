# Spec Fase 1: Mesin baca plat (S1)

> Ditulis agen 16 Okt 2026 sesudah Fase 0A selesai ([`bukti/2026-10-16-laporan-fase-0a.md`](../bukti/2026-10-16-laporan-fase-0a.md)).
> ✅ **Disetujui owner 16 Okt 2026 (K38).** Jawaban owner: "A. Setuju, mulai kerja". ~~Status: menunggu persetujuan owner.~~
> **Dasar:**
> - keputusan owner K7, K9, K15, K16, K21, K25, K26, K29, K31, K34, K35, K36, K37 (`SEED.md` §3);
> - spec induk [`2026-10-13-cctv-gerbang-desain-induk.md`](2026-10-13-cctv-gerbang-desain-induk.md) bagian 2 (mesin baca
>   plat) dan 8.3 (aturan ukur);
> - peraturan plat [`docs/peraturan-plat.md`](../docs/peraturan-plat.md).

## 1. Tujuan dan tolak ukur

**Tujuan (K36):** plat di video CCTV terbaca dengan benar. Ini mencakup mobil dan motor, siang dan malam (termasuk gambar
inframerah), dari macam-macam kamera.

**Tolak ukur (K36):** set uji video CCTV dari internet, dikumpulkan terarah:
- **CCTV gerbang:** rumah, perumahan, sekolah, apartemen, perkantoran, dan tempat lain;
- **parkiran gedung:** plat semua motor yang masuk atau terparkir.

Satu video hanya boleh berada di sisi latih **atau** sisi uji, tidak keduanya (spec 8.3).

**Yang dihitung per kedatangan** (satu kendaraan yang platnya terlihat berturut-turut, spec 2.1 dan 8.3):

| Ukuran | Arti untuk gerbang |
|---|---|
| Benar dan yakin | Gerbang membuka bila platnya terdaftar |
| Ragu (benar atau salah) | Gerbang tidak membuka: gagal-buka bila platnya terdaftar |
| **Salah dan yakin** | Bahaya buka-salah bila bacaan salah itu kebetulan terdaftar |
| Plat terlewat | Kendaraan berplat terbaca yang tidak pernah ditemukan: gagal-buka |

**Kelompok:** mobil/motor × siang/malam. Malam berarti langit gelap dengan lampu sebagai penerangan utama, atau gambar inframerah.
Siang/malam ditandai per video saat pemilahan dari gambar kecil yang buram (K19). Video yang memuat keduanya dilaporkan sebagai
"campuran", tidak dimasukkan ke siang maupun malam. Mobil/motor ditandai owner di lembar. Jenis tempat (gerbang, parkiran) dan resolusi kamera dilaporkan sebagai rincian. Tiap angka ditulis bersama jumlah dan rentang
95%-nya, dan kelompok dengan kurang dari 30 kedatangan ditulis "terlalu sedikit" (spec 8.3).

**Sasaran (K9):**
- benar dan yakin minimal 99% per kelompok;
- salah dan yakin nol.

Untuk berani menyebut "gagal di bawah 1 dari 100", sebuah kelompok butuh sekitar 300 kedatangan uji (spec 8.3), jadi set uji
bertambah dari putaran ke putaran. Laporan selalu menyebut sumbernya, yaitu "pada set uji video CCTV daring" (K36). Bukti di
gerbang nyata tetap di Fase 5.

## 2. Bahan

| Bahan | Isi | Tanda |
|---|---|---|
| **Video CCTV gelombang ketiga** (baru) | Diunduh terarah lewat pintu `tools/ambil-video.ps1`: CCTV gerbang berbagai tempat, parkiran gedung dengan motor, siang dan malam. Dipilah dari lembar gambar kecil yang buram (K19), diperiksa keutuhannya, dicatat di `data-asal/video-riset.json` | `RISET-SAJA` (video daring; P14) |
| Video riset yang sudah ada | 100 video gelombang 1 dan 2 | `RISET-SAJA` |
| **Plat buatan komputer** (baru, K35) | Plat mobil dan motor; warna dasar dan tulisan menurut peraturan (putih/hitam, kuning/hitam, merah/putih, hijau/hitam) ditambah plat hitam lama; nomor menurut pola Perpol 7/2021; baris kecil masa berlaku; huruf **digambar sendiri**. Variasi: ukuran kecil, buram, miring, gelap, silau, inframerah (kelabu), kotor | `BOLEH-PRODUK` (dibuat sendiri) |
| INDO-ALPR, plat-lighting | Potongan plat dan foto berkotak plat | `BOLEH-PRODUK` |

Ukuran plat dan bentuk huruf tidak diatur dalam peraturan yang terbaca ([`docs/peraturan-plat.md`](../docs/peraturan-plat.md)).
Keduanya dicocokkan dengan foto nyata, dan kemiripannya diukur dari hasil pembaca, bukan diklaim.

## 3. Label, tanpa agen melihat plat

Agen tidak pernah melihat plat yang terbaca (K19, `CLAUDE.md` §4 dan §7). Label didapat begini:

- **Kotak plat di gambar CCTV:**
  - kotak diusulkan pencari plat;
  - owner memilah lewat lembar, cukup nomor baris dan jenisnya (plat, bukan plat, tak terbaca, motor), seperti Rencana 14;
  - kotak plat menjadi contoh positif, dan kotak bukan plat menjadi contoh negatif untuk melatih pencari.
- **Plat terlewat:** lembar bingkai berisi gambar sampel dari video uji dengan kotak yang ditemukan digambar. Owner menyebut
  nomor bingkai yang memuat plat terbaca tanpa kotak.
- **Teks plat:**
  - untuk menilai, owner menyatakan bacaan mesin benar atau salah, tanpa mengetik nomor plat;
  - untuk melatih pembaca, dipakai bacaan yang dinyatakan benar oleh owner, plat buatan komputer (teksnya diketahui), dan
    INDO-ALPR.
- **Waktu owner:** paling banyak sekitar 120 baris per lembar. Barisnya dipilih tetap, dan yang paling berguna didahulukan.

## 4. Mesin

Rantai lima langkah (spec 2.1): cari plat, luruskan, baca huruf, cek pola, gabung. Sejak K39 (16 Okt), rantai didahului tahap kendaraan: cari kendaraan, tentukan tampak depan atau belakang, lalu cari plat di area kendaraan itu.

| Langkah | Fase 1 |
|---|---|
| Cari kendaraan (K39) | YOLOX COCO terkunci, kelas kendaraan saja. Kotak plat diterima bila tengahnya di dalam kotak kendaraan. Tampak depan atau belakang menyusul. **Hanya mesin belajar** (bobot COCO `BELUM-JELAS`); mesin jualan butuh pencari kendaraan dari bahan `BOLEH-PRODUK` |
| Cari plat | YOLOX-Nano-640 (K31) **dilatih ulang** dengan gambar CCTV latih (kotak plat dan kotak bukan plat dari lembar owner), plat-lighting, dan gambar CCTV latih yang ditempeli plat buatan komputer |
| Luruskan | Calon baru: meluruskan potongan yang miring. Dipakai hanya bila menaikkan angka di validasi |
| Baca huruf | **Mesin belajar:** fpo-indo-1 dilatih ulang dengan potongan CCTV latih dan plat buatan komputer. **Mesin jualan:** pembaca dilatih dari nol hanya dengan bahan `BOLEH-PRODUK` (INDO-ALPR, plat-lighting, plat buatan komputer), supaya tidak bergantung pada izin bobot fast-plate-ocr (K35) |
| Cek pola | Pola Perpol 7/2021 (`tools/lab/plat.py`), tetap |
| Gabung | Pemungutan suara **per huruf** dicoba di samping per teks utuh (Rencana 14: 203 dari 256 kedatangan "ragu" punya bacaan sah yang tidak sama persis). Ambang "yakin" dipilih di validasi |

- **Pencari plat jualan:** bobot awal COCO YOLOX berstatus `BELUM-JELAS`. Pencari jualan dilatih tanpa bobot itu, hanya dengan
  bahan `BOLEH-PRODUK`. Video daring tidak boleh masuk mesin jualan sampai P14 dijawab. Selisih angka antara mesin belajar dan
  mesin jualan dilaporkan apa adanya.
- **Pilihan diambil di validasi.** Zaman, ambang, dan calon dipilih di sisi latih yang disisihkan, tidak pernah di set uji.
  Set uji dibaca sekali per putaran.

## 5. Kamera dan infrastruktur yang lentur (K36)

- **Satu antarmuka sumber gambar:** berkas video, aliran kamera IP (RTSP atau HTTP), atau foto tunggal yang dikirim pemicu
  (K25).
  - Resolusi 360p sampai 4K dengan rasio apa pun.
  - Gambar inframerah kelabu dibaca seperti gambar berwarna.
  - Ukuran masukan pencari dan jumlah gambar per detik bisa diatur per kamera.
- **Mesin dalam ONNX**, tanpa torch di server.
  - Berjalan di CPU laptop, Mini PC (Celeron N5095), dan Hostinger KVM 2 sampai 8 (K29).
  - Jumlah utas bisa diatur.
  - Kartu grafis dipakai bila ada, tanpa mengubah hasil bacaan.
- **Layanan baca sederhana:** gambar atau klip masuk, bacaan per kedatangan keluar (spec 2.2). Ini batas antara S1 dan S2
  (keputusan gerbang, Fase 2).
  - Layanan diuji di laptop.
  - Di Mini PC, layanan baru dijalankan dengan mesin jualan, karena mesin `RISET-SAJA` tidak dibawa ke sana (K15), atau
    dengan izin owner.
- **Kecepatan diukur per perangkat:** rantai utuh di laptop; model saja di Mini PC (bobot acak bersusunan sama); dan di KVM
  bila owner membelinya. Membeli adalah keputusan owner (`CLAUDE.md` §8).
- **Sasaran tetap dua detik** dari kendaraan berhenti sampai bacaan "yakin" (spec 2.6).
- **Resolusi dan jarak kamera (K40):** diringkas menjadi tinggi plat dalam piksel. Hasil baca dilaporkan menurut tinggi plat, dan
  syarat pemasangan kamera diturunkan dari tinggi plat terkecil yang masih terbaca. Buram karena gerak ditangani dengan memilih
  gambar paling tajam per kedatangan.

## 6. Putaran kerja dan urutan rencana

Fase 1 berjalan dalam putaran. Tiap putaran: latih, pilih di validasi, baca set uji sekali, lembar owner, laporan di `bukti/`.
Tabel angkanya ditulis alat dari JSON bukti, seperti `tools/laporan-0a.mjs`.

| Rencana | Isi |
|---|---|
| 16 | Video CCTV gelombang ketiga: cari, unduh, periksa utuh, pilah (K19), bagi latih/uji per video |
| 17 | Titik awal: rantai sekarang di set uji CCTV; lembar kedatangan dan lembar bingkai untuk owner |
| 18 | Pembuat plat buatan komputer (K35), dengan huruf yang digambar sendiri |
| 19 | Pencari plat dilatih ulang (CCTV latih, bukan plat dari lembar, plat buatan ditempel); ukur |
| 20 | Plat terlewat: plat dicari di dalam potongan kendaraan (K39); calon dipilih di sisi latih dari label owner. *Ditambahkan 16 Okt sesudah Rencana 19, menurut angka* |
| 21 | Bukan plat di dalam kendaraan: tampak depan atau belakang dan letak plat (K39 langkah 2); label dari sisi latih. *Ditambahkan 17 Okt sesudah Rencana 20, menurut angka* |
| 22 | Video CCTV gelombang keempat (K41): gerbang dengan plat dekat dan jelas, gerbang motor, malam. *Ditambahkan 17 Okt sesudah Rencana 21* |
| 23 | Pembaca: mesin belajar dilatih ulang; mesin jualan dari nol; gabung per huruf; luruskan; gambar paling tajam (K40); ukur |
| 24 | Antarmuka sumber gambar dan layanan baca; kecepatan per perangkat |
| 25 | Laporan putaran pertama, lalu putaran berikutnya menurut angka |

Urutan bisa berubah menurut angka. Perubahannya dicatat di `ROADMAP.md` beserta alasannya.

## 7. Cara bekerja (K37)

- **Agen bekerja mandiri:** memilih cara, menulis rencana, menjalankannya, dan melaporkan hasilnya tanpa menunggu "Jalankan"
  per rencana.
- **Agen berhenti untuk owner hanya bila:**
  - ada lembar berisi plat yang terbaca, karena hanya owner yang boleh melihatnya (K19);
  - ada pembelian (`CLAUDE.md` §8);
  - ada push atau publikasi (§9);
  - ada keputusan yang mengubah apa yang dijual, keselamatan gerbang, atau data pribadi.
- **Aturan yang tetap berlaku:** uji merah dulu; gerbang penuh dengan angka sebelum dan sesudah; angka dibaca dari sumber; satu
  job GPU dan satu suite uji pada satu waktu; mesin dianggap tenang hanya bila tidak ada uji milik sesi lain (`CLAUDE.md` §7).

## 8. Data pribadi dan izin

- **Plat tetap di laptop:**
  - video, potongan, lembar, dan bacaan tinggal di `data/` dan tidak masuk git;
  - bukti di `bukti/` hanya berisi hitungan, dan diperiksa dengan kontrol positif.
- **Mesin jualan hanya memuat bahan `BOLEH-PRODUK`.** Diperiksa `tools/periksa-jualan.mjs`.
- **Foto berplat yang kelak dikirim ke server (K25)** menyangkut UU PDP (B9). Itu dirancang di Fase 2 dan Fase 6, bukan di
  sini.

## 9. Yang tidak dikerjakan di Fase 1

- **Keputusan buka gerbang, daftar izin, dan relay:** S2, Fase 2.
- **Ciri kendaraan:** S3, Fase 3. Mencari kendaraan sebagai tahap membaca plat (K39) bukan ciri kendaraan: hasilnya hanya kotak dan jenis kendaraan, dan tidak dicocokkan dengan kendaraan terdaftar.
- **Aplikasi:** S4, Fase 4.
- **Pemasangan di gerbang nyata:** S5, Fase 5.
- **Membeli kamera, server, atau lisensi:** keputusan owner.

## 10. Selesai

Fase 1 selesai bila dua hal terpenuhi:
- laporan putaran terakhir menunjukkan sasaran bagian 1 tercapai per kelompok pada set uji video CCTV daring, dengan jumlah
  kedatangan yang cukup;
- **atau** owner memutuskan berhenti atau mengubah arah sesudah membaca laporan putaran mana pun.

Laporan selalu menyebut mesin mana yang dinilai, yaitu mesin belajar atau mesin jualan, dan tandanya.
