# Desain induk CCTV Gerbang

> **Status: DISETUJUI OWNER 13 Okt 2026.** Kedelapan bagian disetujui satu per satu saat dipaparkan, lalu dokumen
> utuhnya disetujui. Kata owner: "Spek disetujui". Rencana Fase 0A: [`../plans/`](../plans/).
>
> Mengubah isi dokumen ini sesudah disetujui hanya lewat keputusan owner yang dicatat di `SEED.md` §3, atau lewat
> hasil ukur Fase 0 yang membuktikan sebuah bagian keliru; koreksinya masuk commit yang sama dengan buktinya.
>
> Keputusan owner (K1–K17) dan usulan agen (U1–U9) tinggal di [`../SEED.md`](../SEED.md); dokumen ini merujuknya,
> tidak mengulangnya. Yang belum terbukti tinggal di [`../OPEN-QUESTIONS.md`](../OPEN-QUESTIONS.md) bagian B.
> Status dan antrean tinggal di [`../ROADMAP.md`](../ROADMAP.md).
>
> Dokumen ini adalah rancangan seluruh produk ditambah rincian Fase 0. Fase 1 sampai 6 mendapat spec rincinya
> sendiri saat gilirannya.

| # | Bagian | Status |
|---|---|---|
| 1 | Gambaran utuh | ✅ disetujui owner 13 Okt |
| 2 | Mesin baca plat (S1) | ✅ disetujui owner 13 Okt |
| 3 | Keputusan buka gerbang dan keselamatan (S2) | ✅ disetujui owner 13 Okt |
| 4 | Ciri kendaraan (S3) | ✅ disetujui owner 13 Okt |
| 5 | Aplikasi pengelola (S4) | ✅ disetujui owner 13 Okt |
| 6 | Perangkat dan pemasangan (S5) | ✅ disetujui owner 13 Okt |
| 7 | Siap jual (S6) | ✅ disetujui owner 13 Okt |
| 8 | Rincian Fase 0 | ✅ disetujui owner 13 Okt |

> **Catatan perubahan sesudah disetujui.** Teks yang disetujui tidak dihapus; keputusan dan akibatnya ada di `../SEED.md` §3.
> - **K25 (15 Okt 2026): baca plat di server IBE, bukan di kotak di gerbang.** Yang terkena: bagian 1 (bagan; tugas "Kotak di
>   gerbang" dan "Server kita"; batas butir 4 "video dan foto tidak keluar dari lokasi"), 2.6 (kecepatan di kotak tanpa
>   internet), 6.1 (kotak komputasi), 6.3 (internet putus), 6.6 (data di kotak), dan 7.5 (data pribadi). Rinciannya
>   ditetapkan saat spec Fase 2 dan Fase 5 ditulis; perilaku saat internet putus menunggu jawaban owner (P15).
> - **K26 (15 Okt 2026): pembaca huruf berangkat dari bobot fast-plate-ocr yang dilatih ulang dengan plat Indonesia.** Yang
>   terkena: 2.3 ("bobotnya dilatih sendiri"). Bobot awal dari pihak ketiga dipakai lalu dilatih ulang sendiri; izin
>   tertulis diminta dari pembuatnya, dan sampai izin itu ada mesinnya bertanda riset.

## 1. Gambaran utuh

✅ Disetujui owner 13 Okt 2026. Kata-kata owner: "saya setuju dengan anda".

```
Kamera CCTV ──► Kotak di gerbang ──► Relay ──► Motor gerbang (hanya perintah BUKA)
                      │
                      └─► catatan kejadian, tanpa video ──► Server kita ──► Aplikasi di HP
```

Produk bekerja di empat tempat. Tiap tempat punya satu tugas, dan yang melintas di antara mereka dibatasi.

| Tempat | Tugasnya | Yang masuk | Yang keluar |
|---|---|---|---|
| **Kotak di gerbang** | Melihat lewat kamera, membaca plat, mencocokkan ciri kendaraan, memutuskan, menyalakan relay. Menyimpan salinan daftar izin, jadi tetap bekerja saat internet putus | Gambar dari kamera; daftar izin dari server | Perintah buka ke relay; catatan kejadian ke server |
| **Server kita** | Menyimpan daftar kendaraan dan tamu, riwayat, akun, langganan; menghitung analisis untuk paket perusahaan (K13) | Catatan kejadian dari kotak; perubahan daftar dari aplikasi | Daftar izin ke kotak; data ke aplikasi |
| **Aplikasi di HP** | Dipakai pengelola, penghuni, dan satpam: mendaftarkan kendaraan, memberi izin tamu, melihat riwayat | Data dari server | Perubahan daftar ke server |
| **Bengkel di laptop** | Melatih dan mengukur mesin. **Bukan bagian produk yang dikirim ke pembeli** | Bahan latih dan bahan uji | Berkas mesin terlatih untuk kotak, beserta angka ukurnya |

Batas yang mengikat semua bagian:

1. **Hanya perintah buka.** Produk tidak pernah memberi perintah tutup dan tidak menggantikan pengaman gerbang
   (U5, `CLAUDE.md` §3).
2. **Ragu berarti tidak membuka** (U6).
3. **Remote yang sudah ada tetap menjadi cara buka cadangan** (U6).
4. **Video dan foto tidak keluar dari lokasi pembeli.** Yang sampai ke server hanya catatan kejadian: plat, waktu,
   dan keputusan (U2, U4).
5. **Tanpa pengenalan wajah atau identitas orang** (U3).

## 2. Mesin baca plat (S1)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** mengubah gambar kamera menjadi satu bacaan plat per kedatangan kendaraan. Mesin ini tidak memutuskan
buka atau tidak; itu tugas bagian 3.

**Kedatangan** = satu kendaraan yang diikuti dari pertama terlihat di area baca sampai keluar dari area itu, atau
sampai bagian 3 memutuskan. Semua angka lulus (K9) dihitung per kedatangan, bukan per gambar.

### 2.1 Lima langkah

```
gambar kamera ─► 1. cari plat ─► 2. luruskan ─► 3. baca huruf ─► 4. cek pola ─► 5. gabungkan ─► satu bacaan + tingkat yakin
```

| Langkah | Yang dikerjakan | Yang dijaga |
|---|---|---|
| 1. Cari plat | Menemukan letak plat di tiap gambar, mobil dan motor (K7) | Plat kecil dan jauh (motor) diukur terpisah |
| 2. Luruskan | Meluruskan plat yang miring dan memotongnya; baris kecil masa berlaku dibuang | Baris masa berlaku ada di semua plat dan tidak boleh ikut terbaca sebagai nomor |
| 3. Baca huruf | Membaca huruf dan angka pada potongan plat | Semua warna plat dibaca: putih, hitam, kuning, merah. Ragam warna yang resmi dicocokkan ke peraturannya di Fase 0 |
| 4. Cek pola | Mencocokkan bacaan dengan pola plat Indonesia: huruf wilayah, angka, huruf seri | Bacaan di luar pola tidak pernah dianggap benar. Pola plat khusus (dinas, diplomatik) ditetapkan dari data, tidak dikarang |
| 5. Gabungkan | Mengikuti kendaraan yang sama dari gambar ke gambar, mengumpulkan bacaannya, mengambil yang paling konsisten | Hasilnya satu bacaan dengan tingkat yakin. Tingkat yakin rendah = **ragu**, bukan tebakan terbaik |

### 2.2 Yang diserahkan ke bagian 3, per kedatangan

Bacaan plat · tingkat yakin (atau "ragu") · jenis kendaraan (mobil atau motor) · warna plat · waktu · potongan gambar
bukti, yang tetap tinggal di kotak.

### 2.3 Bahan penyusun

Tiap langkah memakai komponen sumber terbuka yang lisensinya membolehkan produk tertutup yang dijual, dan bobotnya
dilatih sendiri (K16, U7). **Komponen dipilih dari hasil ukur di Fase 0, bukan dari perkiraan.** Calon per langkah,
dengan vonis lisensi yang masih sementara, ada di
[`../docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md`](../docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md).
Tiga hal dari survei itu mengikat rancangan ini:

- Pendeteksi plat bawaan paket jadi berasal dari kode berlisensi GPL, jadi pendeteksi produk dilatih sendiri.
- Pendeteksi berlisensi Apache yang sudah dipakai vision-seed berukuran besar, jadi untuk kotak murah diukur juga
  calon yang lebih ringan.
- Mesin dikirim ke kotak dalam format yang tidak bisa membawa kode (bukan pickle), sesuai U8.

### 2.4 Dua mesin, bukan satu

| | Mesin belajar | Mesin jualan |
|---|---|---|
| Dilatih dengan | Semua bahan, termasuk yang bertanda `RISET-SAJA` (K15, K17) | Hanya bahan yang boleh dijual: plat buatan komputer, dataset berizin jual, rekaman sendiri yang berizin |
| Gunanya | Mencari tahu cara mana yang berhasil | Yang dipasang di kotak pembeli |
| Boleh dijual | Tidak, selamanya | Ya |
| Angkanya | Tidak boleh dilaporkan sebagai angka produk | Inilah yang harus memenuhi K9 |

Pemeriksa otomatis menolak mesin jualan bila daftar bahan latihnya memuat satu saja bahan bertanda `RISET-SAJA`.
Pemeriksa itu dibangun di Fase 0, karena bahan pertama sudah tercatat sejak K17.

**Diubah K21 (owner, 14 Okt):** bahan dari internet boleh masuk mesin jualan selama sumbernya tidak menyebut larangan
dipakai belajar. Baris "Dilatih dengan" untuk mesin jualan kini: bahan berizin jual, ditambah bahan yang sumbernya tidak
menyebut larangan itu. Arti "larangan" untuk label non-komersial dan syarat situs belum diputuskan (P14). Pemeriksa
otomatis tetap menolak bahan yang vonisnya bukan `BOLEH-PRODUK`; yang berubah adalah cara vonis tiap bahan dibaca.

### 2.5 Cara mengukur

- Bahan uji dipisah total dari bahan latih dan tidak pernah dipakai melatih.
- Angka dihitung per kedatangan, **terpisah** untuk mobil-siang, mobil-malam, motor-siang, motor-malam. Yang terlemah
  menentukan lulus atau tidak (K9). Arti "siang" dan "malam" ditetapkan di bagian 8.
- Angka per gambar tetap dicatat, sebagai alat mencari langkah mana yang lemah, bukan sebagai angka lulus.
- Paket jadi dan AI serba-bisa dijalankan pada bahan uji yang sama sebagai pembanding (K16).
- Angka dari video daring tidak dilaporkan sebagai "K9 tercapai": K9 hanya bisa dibuktikan dari kamera di posisi
  gerbang.

### 2.6 Kecepatan

Mesin berjalan di kotak murah tanpa internet (U2). **Sasaran awal: dua detik dari kendaraan berhenti sampai perintah
buka.** Angka ini usulan agen dan belum diukur; ia dikunci atau dikoreksi sesudah Fase 0 mengukur. Sampai kotak ada
(K6), kecepatan hanya bisa ditaksir di laptop (B5).

### 2.7 Yang belum diputuskan di bagian ini

- Komponen mana per langkah: menunggu ukuran Fase 0.
- Apakah satu kamera cukup untuk mobil dan motor sekaligus: menunggu ukuran (akibat K7).
- Huruf untuk plat buatan komputer versi jualan: digambar sendiri atau membeli lisensi (akibat K16); diajukan ke
  owner saat diperlukan.

## 3. Keputusan buka gerbang dan keselamatan (S2)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** memutuskan apakah gerbang dibuka untuk satu kedatangan, memberi perintah buka, dan mencatat kejadiannya.

### 3.1 Empat pemeriksaan, semuanya harus lolos

| # | Pemeriksaan | Aturannya |
|---|---|---|
| 1 | Plat ada di daftar izin | **Cocok persis.** Beda satu huruf pun tidak dibuka; kejadiannya dicatat sebagai "hampir cocok" |
| 2 | Bacaan yakin | Hasil "ragu" dari bagian 2 tidak pernah membuka (U6) |
| 3 | Izin masih berlaku | Izin tetap (penghuni, armada) berlaku sampai dicabut. Izin sementara (tamu) punya batas tanggal dan jam. Plat di daftar blokir tidak pernah dibuka |
| 4 | Kendaraan di depan gerbang | Kendaraan yang sekadar lewat di jalan tidak memicu apa pun |

Bagian 4 menambah satu pemeriksaan lagi (ciri kendaraan) saat sudah terbukti; aturannya ditetapkan di sana.

### 3.2 Daftar izin

Server menyimpan daftar induknya; kotak menyimpan salinannya dan memakai salinan terakhir saat internet putus.
Berapa lama perubahan daftar boleh terlambat sampai ke kotak ditetapkan di spec Fase 2.

### 3.3 Perintah buka

Satu denyut singkat ke relay, sama seperti menekan tombol buka sekali. Satu perintah per kedatangan, dengan jeda
sebelum perintah berikutnya, supaya gerbang tidak dibuka berulang-ulang. Lama denyut dan jeda ditetapkan di spec
Fase 2 sesudah ragam motor gerbang diperiksa (B11).

### 3.4 Saat gerbang tidak dibuka

- Kejadian dicatat beserta alasannya: tidak terdaftar, ragu, izin habis, diblokir, atau hampir cocok.
- Di lokasi yang punya satpam, kejadian muncul di HP satpam dan **satpam yang memutuskan**. Cara satpam membuka
  dirancang di bagian 5.
- Di lokasi tanpa satpam, gerbang tetap tertutup. Penghuni memakai remote, atau memberi izin tamu lewat aplikasi.

### 3.5 Catatan kejadian

Tiap kedatangan dicatat, dibuka maupun tidak, dengan alasannya. Potongan gambar bukti disimpan di kotak dengan batas
umur (U4); yang dikirim ke server hanya plat, waktu, keputusan, dan alasan. Batas umur gambar ditetapkan di spec
Fase 6, sesudah kewajiban data pribadi diperiksa (bagian 7, B9).

### 3.6 Keselamatan

1. **Hanya perintah buka.** Menutup dan menahan gerbang tetap urusan motor gerbang dan pengamannya sendiri (U5).
2. **Syarat pasang tertulis.** Produk hanya dipasang di gerbang yang punya pengaman berfungsi, misalnya sensor
   penghalang. Ini masuk daftar periksa pemasang (bagian 6).
3. **Gagal ke arah diam.** Bila kotak mati, macet, atau kehilangan listrik, relay tidak menyala: gerbang tetap
   seperti semula dan remote tetap bekerja.
4. **Batas jumlah perintah** per kedatangan dan per satuan waktu.
5. **Masa percobaan senyap di tiap lokasi baru.** Selama beberapa hari pertama kotak hanya mencatat apa yang akan
   ia putuskan, tanpa membuka. Pemasang melihat hasilnya, baru menyalakan pembukaan otomatis. Lamanya ditetapkan di
   spec Fase 5.
6. **Sampai Fase 5, relay hanya menyalakan lampu di meja uji.** Gerbang sungguhan hanya digerakkan dengan owner hadir
   dan menyetujuinya saat itu (`CLAUDE.md` §3).

### 3.7 Cara menguji

Rantai penuh di meja uji: dari gambar atau video, lewat mesin baca plat dan keputusan, sampai relay menyalakan lampu.
Sasaran: **nol buka-salah** pada set uji (K9). Uji menelusuri rantainya, bukan memanggil keputusan secara langsung,
supaya pemeriksaan yang ada tetapi tidak pernah dilewati tidak lolos sebagai "hijau". Besar set uji ditetapkan di
bagian 8.

### 3.8 Yang belum diputuskan di bagian ini

Lama denyut dan jeda · batas keterlambatan daftar izin · lama masa percobaan senyap · batas umur gambar bukti.
Masing-masing punya tempat penetapannya di atas.

## 4. Ciri kendaraan (S3)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** menangkal plat tiruan, yaitu plat yang cocok tetapi terpasang di kendaraan yang bukan terdaftar. Sesuai
K8, ciri dikenali sampai nama model, dibangun dua tahap; keduanya selesai sebelum produk dijual.

### 4.1 Tahap 1: jenis, warna, merek

Kotak mengenali jenis kendaraan (mobil, pikap, truk, motor), warnanya, dan mereknya dari gambar, lalu
membandingkannya dengan data yang diisi saat kendaraan didaftarkan.

> **K55 (owner, 19 Okt 2026):** ciri dicatat bersama kejadian masuk dan keluar dan dicocokkan dengan data pendaftaran. Bila tidak cocok,
> satpam diberi peringatan; gerbang tetap mengikuti plat sampai pengenal ciri terbukti akurat. Malam hari, warna dilihat dengan penerangan
> yang cukup, bukan inframerah (K52).

### 4.2 Tahap 2: nama model, dengan dua cara yang saling melengkapi

| | Cara A: mencocokkan rupa dengan kendaraan terdaftar | Cara B: mengenali nama model kendaraan yang tidak terdaftar |
|---|---|---|
| Untuk apa | Penangkal plat tiruan pada kendaraan terdaftar | Tamu, dan analisis paket perusahaan (K13) |
| Cara kerja | Saat didaftarkan, kamera gerbang memotret kendaraan beberapa kali; kotak menyimpan "sidik rupa"-nya. Tiap kedatangan dibandingkan dengan sidik rupa milik plat itu | Pengenal yang dilatih dengan foto mobil berlabel model |
| Nama model | Diambil dari isian pendaftaran | Dikenali dari gambar |
| Latih ulang tiap ada model baru | Tidak perlu | Perlu |
| Motor | Berlaku | Tidak dikejar dulu |
| Bahan | Tidak butuh kumpulan foto berlabel model | Butuh foto mobil pasar Indonesia berlabel model. Survei 13 Okt tidak menemukannya, dan dataset besar yang ada semuanya non-komersial ⇒ dikumpulkan sendiri |
| Urutan | Dikerjakan lebih dulu | Sesudah cara A |

Foto pendaftaran dan sidik rupa tinggal di kotak (U2, U4). Mengumpulkan foto dari lokasi pembeli untuk melatih
cara B adalah keputusan terpisah karena menyangkut data pribadi (B9); tidak diandaikan di sini.

### 4.3 Pengaruh pada keputusan buka gerbang

| Hasil perbandingan ciri | Gerbang | Catatan |
|---|---|---|
| Cocok | Dibuka | — |
| Jelas berbeda | Tidak dibuka | Dicatat "ciri tidak cocok"; satpam diberi tahu |
| Tidak yakin (gelap, kendaraan kotor) | **Tetap dibuka**, karena platnya cocok dan yakin | Dicatat. Bisa diperketat per lokasi menjadi "tidak dibuka" |

Baris ketiga adalah usulan agen yang disetujui owner bersama bagian ini. Alasannya: menjadikannya "tidak dibuka"
secara bawaan menambah gagal-buka dan memberatkan sasaran 99% (K9).

### 4.4 Dinyalakan bertahap

Pembanding ciri mula-mula **hanya mencatat**, tanpa menahan gerbang. Ia baru boleh menahan gerbang sesudah terbukti
jarang salah menuduh kendaraan yang sah. Batas "jarang" ditetapkan di spec Fase 3 dari hasil ukur.

### 4.5 Cara menguji

Di Fase 3: plat tiruan dipasang pada kendaraan lain di set uji dan harus ditolak; kendaraan sah yang salah dituduh
dihitung terpisah. Sampai itu diukur, B7 (seberapa mudah plat tiruan menipu dan seberapa menolong pembanding ini)
berstatus belum terbukti.

### 4.6 Yang belum diputuskan di bagian ini

Batas "jarang salah menuduh" · sumber foto untuk cara B · kedalaman ciri motor di luar warna dan sidik rupa.

## 5. Aplikasi pengelola (S4)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** tempat orang mengisi dan melihat daftar izin, tamu, dan riwayat gerbang.

### 5.1 Peran

| Peran | Yang bisa dilakukan | Yang tidak |
|---|---|---|
| Pengelola | Mengelola seluruh daftar kendaraan, menambah penghuni dan satpam, melihat semua riwayat | — |
| Penghuni atau karyawan | Mendaftarkan kendaraannya sendiri, memberi izin tamu, melihat riwayat kendaraannya sendiri | Melihat data penghuni lain |
| Satpam | Melihat kedatangan saat itu, memutuskan untuk kendaraan yang tertahan, mencatat tamu | Mengubah daftar tetap |

Di rumah dan kost, satu orang merangkap semua peran.

### 5.2 Isi

1. **Daftar kendaraan:** plat, jenis, warna, merek, model, pemilik. Daftar besar bisa dimasukkan sekaligus dari
   Excel. Isian jenis, warna, merek, dan model dipakai bagian 4 sebagai pembanding.
2. **Izin tamu:** berlaku untuk tanggal dan jam tertentu, dibuat penghuni atau satpam. Kurir dan ojek daring
   dibukakan satpam, atau diberi izin sekali pakai.
3. **Riwayat keluar-masuk:** bisa dicari per plat atau tanggal, dan bisa diunduh ke Excel.
4. **Pemberitahuan:** ke satpam saat ada kendaraan tertahan; ke penghuni saat tamunya tiba.
5. **Analisis dan proyeksi** untuk paket perusahaan (K13): jumlah kedatangan per jam dan per hari, tamu yang paling
   sering datang, dan perkiraan jumlah tamu beberapa hari ke depan dari pola sebelumnya.

### 5.3 Aturan

- **Satpam membuka lewat aplikasi** untuk kendaraan yang tertahan. Itu tetap perintah buka (bagian 3), diputuskan
  manusia, dan dicatat siapa yang membukanya.
- **Penghuni hanya melihat data miliknya sendiri.** Nama, plat, dan jam keluar-masuk adalah data pribadi
  (`CLAUDE.md` §4).
- **Saat langganan berhenti,** gerbang tetap membuka untuk kendaraan yang sudah terdaftar. Yang terkunci hanya fitur
  aplikasinya. Gerbang tidak pernah dijadikan alat menagih.
- **Nama dan logo bisa diganti** tanpa mengubah kode, untuk jalur OEM (K11).

### 5.4 Urutan dan bentuk

- **Urutan:** bentuk untuk klaster dan untuk gudang, pabrik, kantor dibangun lebih dulu (K10). Bentuk untuk rumah
  dan kost adalah penyederhanaannya.
- **Bentuk:** aplikasi web yang bisa dipasang di layar HP seperti aplikasi biasa dan juga dibuka di komputer. Sekali
  bangun untuk keduanya, dan penggantian merek untuk OEM lebih mudah. Aplikasi lewat toko aplikasi menyusul bila
  dibutuhkan. Ini usulan agen yang disetujui owner bersama bagian ini.

### 5.5 Yang belum diputuskan di bagian ini

- Bentuk berkas Excel untuk memasukkan daftar sekaligus.
- Saluran pemberitahuan (di dalam aplikasi saja, atau juga lewat layanan pesan).
- Cara satpam membuka bila internet antara HP dan kotak putus; sampai itu dirancang, cadangannya remote.
- Rincian hitungan analisis dan proyeksi, dan kewajiban data pribadi yang menyertainya (B9): ditetapkan di spec
  Fase 4.

## 6. Perangkat dan pemasangan (S5)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** barang yang dipasang di gerbang pembeli, dan cara memasangnya sampai bekerja.

### 6.1 Isi paket per gerbang

| Barang | Keterangan |
|---|---|
| Kamera CCTV biasa | Boleh kamera yang sudah dimiliki pembeli, asal termasuk daftar yang sudah diuji (U1) |
| Kotak komputasi kecil | Jenisnya dipilih dari hasil ukur Fase 0. Belum dibeli (K6) |
| Relay | Disambung ke terminal "tombol buka" pada motor gerbang |
| Lampu tambahan | Hanya bila hasil ukur malam menunjukkan perlu (B3) |

Satu kamera untuk mobil dan motor sekaligus, atau dua kamera, ditentukan dari hasil ukur (akibat K7).

### 6.2 Sambungan ke motor gerbang

- Relay bekerja seperti tombol tekan biasa; motor gerbang tidak diubah (K12, pilihan A).
- Daftar motor gerbang yang didukung disusun beserta cara sambungnya per merek. Ragam motor di lapangan belum
  diperiksa (B11).
- Bila owner kelak menjual motor sendiri (K12, pilihan C), motornya dipilih dari model yang sudah diuji.

### 6.3 Tahan gangguan

| Gangguan | Perilaku |
|---|---|
| Internet putus | Gerbang tetap bekerja dari daftar di kotak; catatan kejadian dikirim saat tersambung lagi |
| Listrik padam | Kotak pulih sendiri saat listrik kembali, **tanpa membuka gerbang** |
| Pembaruan bermasalah | Pembaruan dikirim dari jauh dan bisa dibatalkan ke versi sebelumnya |
| Kotak atau kamera bermasalah | Terlihat dari pemantauan jarak jauh: kotak hidup atau tidak, kamera tersambung atau tidak, mutu bacaan menurun |

### 6.4 Pemasangan

Sasaran (`SEED.md` §5.3 butir 3, menjadi syarat jual sejak K11): pemasang yang belum pernah bertemu kita bisa
memasang di gerbang baru hanya dari panduan.

1. **Daftar periksa keselamatan.** Pengaman gerbang harus berfungsi; kalau tidak, pemasangan tidak dilanjutkan.
2. **Memasang kamera** dengan alat bantu di aplikasi yang menunjukkan apakah plat sudah cukup besar dan tajam di
   gambar (tanda hijau atau merah).
3. **Menyambung relay** sesuai panduan merek motornya.
4. **Uji baca** dengan beberapa kendaraan.
5. **Masa percobaan senyap** (bagian 3), lalu pembukaan otomatis dinyalakan.

Beberapa lokasi pertama dipasang sendiri, karena panduan pasang hanya bisa ditulis dari pengalaman memasang.

### 6.5 Merek dan sertifikasi

Kita tidak membuat kotak sendiri: yang dipakai komputer kecil dan relay bermerek yang sudah bersertifikat, supaya
sertifikasi perangkat tidak terpicu (`SEED.md` §5.2). Untuk jalur OEM, siapa yang wajib mengurus sertifikasi bila
kotaknya membawa merek pihak lain **belum diperiksa** (B10) dan harus terjawab sebelum penawaran OEM pertama.

### 6.6 Perlindungan data di kotak

Daftar izin dan gambar bukti adalah data pribadi: isi kotak terkunci, dan hubungan ke server terenkripsi. Caranya
ditetapkan di spec Fase 5.

### 6.7 Yang belum diputuskan di bagian ini

Jenis kotak · daftar kamera yang didukung · satu atau dua kamera per jalur · perlu tidaknya lampu tambahan · daftar
motor gerbang yang didukung · cara mengunci isi kotak. Empat yang pertama menunggu hasil ukur; dua yang terakhir
ditetapkan di spec Fase 2 dan Fase 5.

## 7. Siap jual (S6)

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas:** semua yang harus ada supaya produk bisa dijual dan dipakai orang yang tidak mengenal kita.

### 7.1 Harga dan aktivasi (K13)

- Dua daftar harga: **perorangan** (aplikasi Rp 5.000 per bulan, angka owner) dan **perusahaan** (beberapa paket,
  termasuk langganan dengan analisis dan proyeksi tamu).
- Tiap kotak diaktifkan dengan kode yang mengenali jenis pembeli dan paketnya. Untuk OEM, aktivasi dihitung per
  pemilik merek.
- **Gerbang tidak pernah dimatikan karena tagihan.** Yang terkunci hanya fitur aplikasi (bagian 5).
- Tagihan Rp 5.000 diusulkan ditagih per tahun. Biaya transaksi pembayarannya **belum diperiksa**.

### 7.2 Jalur jual (K11) dan urutannya

Beberapa lokasi pertama dipasang sendiri (bagian 6). Sesudah itu, urutan usulan agen yang disetujui owner bersama
bagian ini:

| Urutan | Jalur | Yang harus disiapkan |
|---|---|---|
| 1 | Pemasang dan distributor CCTV (jalur 1 dan 4 di K11) | Panduan pasang, pelatihan, harga bertingkat, garansi dan retur |
| 2 | Jual daring (jalur 2) | Halaman produk, paket siap kirim, dukungan jarak jauh |
| 3 | OEM ke pemilik merek (jalur 3) | Merek yang bisa diganti, lisensi per unit, kepastian soal sertifikasi perangkat (B10) |

### 7.3 Batas lingkup pemasaran digital

Workspace ini menyiapkan **bahan produk**: halaman produk, panduan, dan video peragaan. Pekerjaan iklan dan konten
harian dikerjakan di luar workspace ini, supaya lingkupnya tidak melebar (`CLAUDE.md` §2).

### 7.4 Izin komponen (U7, K15)

- Pemeriksa otomatis menolak versi jualan yang masih memuat bahan bertanda `RISET-SAJA` (bagian 2).
- Daftar komponen beserta izinnya disertakan dalam produk, karena sebagian izin mewajibkan pencantuman pembuatnya.

### 7.5 Data pribadi (UU PDP 27/2022)

- Papan pemberitahuan di gerbang bahwa area itu memakai kamera pembaca plat.
- Batas umur untuk riwayat dan gambar bukti, dan cara menghapus data atas permintaan.
- Perjanjian pemrosesan data dengan pembeli perusahaan, karena catatan mereka sampai ke server kita (akibat K13).
- **Belum diperiksa.** Semua butir di atas harus diperiksa ahli hukum (B9) sebelum merekam di lokasi pihak lain dan
  sebelum paket perusahaan ditawarkan.

### 7.6 Keselamatan, dukungan, dan garansi

- Syarat keselamatan gerbang (bagian 3) diberikan tertulis kepada pembeli dan pemasang.
- Dukungan lapis pertama: pemasang atau distributor. Lapis kedua: kita, dari jauh, dengan unit pengganti.

### 7.7 Batas "selesai"

Produk baru disebut siap jual bila keempat hal ini terbukti **di gerbang nyata** (`SEED.md` §5.3):

1. Kendaraan terdaftar dibukakan pada angka K9 (99% per kelompok), siang dan malam.
2. Kendaraan tidak terdaftar tidak dibukakan.
3. Pemasang yang belum pernah bertemu kita bisa memasang hanya dari panduan.
4. Pembeli bisa mengelola daftarnya sendiri tanpa menghubungi kita.

### 7.8 Yang sengaja belum diisi

Besaran paket perusahaan · harga perangkat · klaster masuk daftar harga mana. Belum ada data tentang berapa orang mau
membayar (B8), jadi angka-angka itu ditetapkan bersama owner di spec Fase 6.

## 8. Rincian Fase 0

✅ Disetujui owner 13 Okt 2026. Kata owner: "sesuai".

**Tugas Fase 0:** sebelum membangun, mengukur sendiri apakah mesin buatan sendiri layak dan apa yang dibutuhkannya.
Semuanya di laptop ini, tanpa pengeluaran (K6).

Karena lokasi dan kamera belum ada (K5, K6), Fase 0 dibagi dua.

### 8.1 Fase 0A: dengan bahan dari luar, dikerjakan sekarang

| # | Langkah | Hasil yang harus ada |
|---|---|---|
| 1 | **Menyiapkan bengkel.** Ruang uji tertutup tanpa jaringan disalin dari vision-seed (K14); daftar bahan beserta tandanya; pemeriksa "mesin jualan" (bagian 2); perbaikan alat unduh yang melapor berhasil saat unduhan terpotong | Uji yang pernah merah lalu hijau untuk tiap alat |
| 2 | **Vonis izin tiap komponen yang dipakai:** kode, bobot, dan bahan latihnya, diperiksa terpisah pada commit yang dikunci (B12) | Tabel vonis di `docs/`, dengan kutipan dan alamat sumber tiap vonis |
| 3 | **Membaca peraturan plat** dari teks aslinya: ukuran, warna, susunan baris | Ringkasan dengan kutipan pasal; catatan lama yang keliru dikoreksi |
| 4 | **Menyiapkan bahan.** Memilah 45 video (K17); mengambil dua dataset berizin jual dan dataset riset lain; membuat pembuat plat buatan komputer untuk mobil dan motor | Manifes terisi (isi dan sudut tiap video); tiap unduhan tercatat asal, izin, dan SHA-256-nya |
| 5 | **Set uji pertama.** Label diperiksa manusia; dipisah dari bahan latih; dikelompokkan mobil-siang, mobil-malam, motor-siang, motor-malam | Jumlah kedatangan per kelompok, dilaporkan apa adanya |
| 6 | **Mengukur pembanding:** paket jadi dan AI serba-bisa pada set uji itu (K16) | Angka per kelompok untuk tiap pembanding |
| 7 | **Mesin belajar pertama:** dua atau tiga calon per langkah, diukur per langkah dan per kedatangan | Angka per kelompok; calon terbaik per langkah beserta alasannya |
| 8 | **Menaksir kecepatan** di laptop tanpa kartu grafis | Taksiran, ditulis sebagai taksiran (B5) |
| 9 | **Laporan** | Berkas di `bukti/`: angka per kelompok, yang belum terjawab, saran. Lalu **keputusan owner**: lanjut, tunggu lokasi, atau ubah arah |

### 8.2 Fase 0B: dari posisi kamera gerbang, dikerjakan saat lokasi atau kamera ada

Merekam dari posisi kamera gerbang dengan izin pengelola lokasinya, lalu mengukur yang tidak bisa dijawab dari video
daring: plat motor dari sudut gerbang (B2), malam dan silau yang sebenarnya (B3), dan kecepatan di kotak sungguhan
(B5). Sisi hukum merekam di lokasi pihak lain (B9) diperiksa lebih dulu.

### 8.3 Aturan ukur

- **Kedatangan pada video luar** = satu kendaraan yang platnya terlihat berturut-turut dalam satu potongan video.
- **Siang dan malam pada bahan luar** ditandai saat pelabelan dari gambarnya: "malam" bila langit gelap dan
  penerangan utamanya lampu; "siang" bila terang alami. Yang remang dicatat sebagai "remang" dan dilaporkan
  terpisah, tidak dimasukkan ke siang maupun malam. Pada rekaman lokasi (0B), siang dan malam ditentukan dari jam
  setempat terhadap matahari terbit dan terbenam.
- **Latih dan uji dipisah per video sumber**, bukan per gambar: satu video tidak boleh menyumbang ke keduanya,
  supaya plat yang sama tidak muncul di bahan latih dan bahan uji.
- **Tiap angka dilaporkan bersama jumlahnya** (misalnya "71 dari 80") dan rentang ketidakpastiannya. Kelompok
  dengan kurang dari 30 kedatangan ditulis "terlalu sedikit untuk disimpulkan", bukan diberi persentase.
- **Kelompok yang kosong ditulis kosong.**
- **Besar set uji akhir tidak ditetapkan di Fase 0A.** Untuk berani menyebut "di bawah 1 dari 100", sebuah kelompok
  butuh sekitar 300 kedatangan uji tanpa satu pun gagal (hitungan agen dengan aturan statistik umum). Besar set uji
  gagal-buka dikunci di spec Fase 1, dan besar set uji buka-salah di spec Fase 2, keduanya dengan cara hitung ini.

### 8.4 Yang tidak akan terjawab oleh Fase 0A

- **K9 (99% per kelompok).** Hanya bisa dibuktikan dari kamera di posisi gerbang, dan untuk berani menyebut "gagal
  di bawah 1 dari 100" tiap kelompok butuh sekitar 300 kedatangan uji tanpa gagal (hitungan agen). Angka Fase 0A
  berstatus sementara dan tidak dilaporkan sebagai "K9 tercapai".
- **B2 dan B3 dari sudut gerbang.** Fase 0A hanya memberi jawaban awal.
- **Jumlah bahan uji per kelompok** belum bisa dijanjikan: isi 45 video belum dilihat.

### 8.5 Yang dibutuhkan dari owner selama Fase 0A

| Kebutuhan | Keterangan |
|---|---|
| Pemeriksaan label | AI di laptop memberi label lebih dulu. Hasilnya diperiksa manusia: owner memeriksa lembar contohnya, **atau** owner mengizinkan agen melihat potongan gambar. Izin itu **belum diberikan**; tanpa izin, agen tidak melihat gambar plat (`CLAUDE.md` §4) |
| Rekaman sendiri (tidak wajib) | Plat cetak di papan dan kendaraan owner sendiri, direkam HP (U9 butir 5 dan 6). Satu-satunya cara mendapat jawaban awal soal motor dan malam sebelum ada lokasi |
| Izin lokasi kenalan | Sedang diurus owner (K5) |
| Keputusan di akhir | Lanjut, tunggu lokasi, atau ubah arah |

### 8.6 Aturan kerja

- **Satu pekerjaan berat pada satu waktu.** Kartu grafis dipakai bersama vision-seed: `nvidia-smi` diperiksa sebelum
  melatih (`CLAUDE.md` §7).
- **Unduhan model dan dataset baru dimulai sesudah spec ini diperiksa owner dan rencana Fase 0 ada.** Tiap unduhan
  dikunci, dicatat asal dan izinnya, dan dihitung SHA-256-nya. Bobot berformat pickle dipindai; `trust_remote_code`
  dilarang (`CLAUDE.md` §6).
- **Repo pihak ketiga dijalankan pertama kali di ruang uji tanpa jaringan** (U8).
- **Gambar plat tidak keluar dari laptop** dan tidak masuk git (`CLAUDE.md` §4).
- **Tanpa pembelian** (K6).
- Gerbang uji dijalankan penuh, dengan kode keluar yang tidak disembunyikan.

### 8.7 Bukti untuk naik status

- **Fase 0A selesai** bila laporan tertulis ada di `bukti/` dengan angka per kelompok dan daftar yang belum
  terjawab, dan keputusan owner tercatat di `ROADMAP.md`.
- **Fase 0 selesai seluruhnya** bila Fase 0B juga selesai: B2, B3, dan B5 terjawab dari posisi kamera gerbang.
- Fase 1 boleh dimulai sesudah Fase 0A bila owner memutuskan lanjut; Fase 0B dikerjakan begitu lokasi atau kamera
  ada.
