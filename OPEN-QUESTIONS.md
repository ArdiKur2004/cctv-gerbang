# OPEN-QUESTIONS — CCTV Gerbang

> Dua jenis hal yang belum diketahui, sengaja dipisah:
> **A** = keputusan owner (dijawab dengan memilih). **B** = hal yang belum terbukti (dijawab dengan mengukur,
> bukan dengan pendapat). Dibuat 2026-10-13. Status tiap butir dipelihara di sini; antreannya di
> [`ROADMAP.md`](ROADMAP.md).

## A. Pertanyaan untuk owner

Ditanyakan **satu per satu**, urut nomor. "Usulan agen" adalah titik berangkat, bukan keputusan.

| # | Pertanyaan | Usulan agen | Yang berubah bila jawabannya lain | Status |
|---|---|---|---|---|
| P1 | Siapa pembeli pertama yang dibidik: rumah pribadi · klaster atau perumahan · kost atau apartemen kecil · gudang, pabrik, atau kantor? | Klaster/perumahan dan gudang/kantor. Bukan rumah pribadi: laporan riset tidak menemukan satu pun produk konsumen sejenis di Indonesia, dan penggantinya remote Rp 215 ribu | Besar daftar izin, alur tamu, porsi motor, isi S4, jalur jual | ✅ **Terjawab 13 Okt → K4: keempatnya dibidik** (berbeda dari usulan agen). Akibatnya di `SEED.md` §3 |
| P2 | Gerbang mana yang bisa dipakai uji dan merekam plat sungguhan, dengan izin pengelolanya? | Belum ada. Catatan vision-seed 3 Okt menyebut jaringan PT IBE dengan klien pabrik/gudang; belum ditanyakan apakah bisa dipakai untuk ini | Tanpa lokasi, Fase 0 hanya bisa memakai video dan dataset luar yang kurang mewakili | ✅ **Terjawab 13 Okt → K5:** yang dituju lokasi owner sendiri, lalu lokasi kenalan; **sementara belum ada lokasi**, jadi Fase 0 mulai dari data luar. Izin lokasi kenalan sedang diurus owner. Lokasi klien tidak disebut owner. Akibatnya di `SEED.md` §3 |
| P3 | Perangkat uji (kamera CCTV, kotak komputasi, relay): sudah ada, atau perlu dibeli? Berapa anggarannya? | Belum ada (membeli = keputusan owner) | Kapan Fase 0 bisa mulai mengukur | ✅ **Terjawab 13 Okt → K6:** set uji disetujui tetapi **tidak dibeli sekarang**; belum ada kamera maupun kotak komputasi; semua memakai laptop. Tanpa pengeluaran. Akibatnya di `SEED.md` §3 |
| P4 | Plat motor ikut dibaca sejak awal? | Ya | Tanpa motor S1 lebih ringan, tetapi produk tidak melayani sebagian besar kendaraan | ✅ **Terjawab 13 Okt → K7:** ya, mobil dan motor sejak awal (sama dengan usulan agen). Akibatnya di `SEED.md` §3 |
| P5 | "Model mobil": cukup jenis + warna + merek sebagai pembanding, atau sampai model (Avanza vs Xenia)? | Mulai dari jenis, warna, merek; model spesifik sesudahnya | Model spesifik butuh data mobil pasar Indonesia dan latih ulang tiap ada model baru (laporan menaksir +4–8 minggu-kerja, lalu terus-menerus) | ✅ **Terjawab 13 Okt → K8:** sampai nama model, bertahap (jenis, warna, merek dulu; nama model menyusul; keduanya sebelum dijual). Sama dengan usulan agen. Akibatnya di `SEED.md` §3 |
| P6 | Angka lulus: seberapa sering gerbang boleh gagal membuka untuk kendaraan terdaftar, dan berapa toleransi membuka untuk yang tidak terdaftar? | Buka-salah: nol pada set uji. Gagal-buka: ditetapkan sesudah garis dasar Fase 0 terukur | Lama Fase 1 dan banyaknya data yang dibutuhkan. Sesudah K4 juga menentukan janji "tanpa kartu": tiap gagal-buka memaksa pembeli kembali ke remote | ✅ **Terjawab 13 Okt → K9:** gagal-buka sasaran 99%, terpisah untuk mobil, motor, siang, malam; buka-salah nol pada set uji. Sasaran dikunci di spec sesudah Fase 0 mengukur. Akibatnya di `SEED.md` §3 |
| P7 | Dijual lewat siapa: pemasang CCTV/gerbang · langsung ke pembeli · lisensi ke integrator parkir? **Dan dari empat kelompok pembeli (K4), mana yang digarap lebih dulu?** (bagian kedua ditambahkan 13 Okt sesudah K4) | Lewat pemasang | Isi S5 dan S6: panduan pasang, harga grosir, bentuk dukungan | ✅ **Terjawab 13 Okt → K10 dan K11.** K10: klaster/perumahan dan gudang, pabrik, kantor lebih dulu; kost dan rumah pribadi menyusul. K11: empat jalur jual (distributor · jual daring · OEM ke pemilik merek · distributor pemasangan CCTV), lebih luas dari usulan agen. Akibatnya di `SEED.md` §3 |
| P8 | Ikut menjual dan memasang motor gerbang, atau hanya menyambung ke motor yang sudah ada? | Hanya menyambung | Ikut memasang berarti stok, pekerjaan sipil, dan tanggung jawab keselamatan yang lebih besar | ✅ **Terjawab 13 Okt → K12:** menyambung ke motor yang sudah ada, dan owner terbuka untuk menjual serta memasang motor sendiri. Lebih luas dari usulan agen. Kapan pilihan kedua dijalankan belum ditetapkan. Akibatnya di `SEED.md` §3 |
| P9 | Model harga: sekali bayar atau langganan? | Belum ada usulan. Laporan: pesaing lokal menjual "tanpa iuran bulanan" | Isi S6 dan cara aktivasi | ✅ **Terjawab 13 Okt → K13:** harga dibedakan menurut pembeli. Masyarakat biasa: langganan Rp 5.000 per bulan untuk aplikasinya. Perusahaan: beberapa paket, termasuk langganan dengan analisis dan proyeksi tamu. Bentuk gabungan, langganan saja juga boleh. Besaran paket perusahaan dan harga perangkat belum disebut. Akibatnya di `SEED.md` §3 |
| P10 | Hubungan kode dengan vision-seed: repo mandiri yang membaca vision-seed sebagai acuan · memakai ulang `inti/` · menjadi anak-seed 08? | Mandiri dulu; pemakaian ulang diputuskan saat ada kode yang benar-benar sama di dua tempat | Cara kerja lab dan tempat kode bersama tinggal (SEED T2) | ✅ **Terjawab 13 Okt → K14:** repo mandiri yang menyalin bagian `inti/` yang dibutuhkan, dengan catatan asal-usul; vision-seed tidak diubah dari sini. Akibatnya di `SEED.md` §3 |
| P11 | Lisensi di fase riset: ikut vision-seed D16 (bahan riset-saja boleh di laptop, ditandai, diganti sebelum dijual) atau ketat sejak awal? | Ikut D16 | Pilihan dataset dan bobot untuk Fase 0 | ✅ **Terjawab 13 Okt → K15:** boleh untuk belajar dengan pagar (dicatat dan ditandai `RISET-SAJA` · hanya di laptop · dilatih ulang dengan bahan bersih sebelum dijual, dijaga pemeriksaan otomatis · agen boleh mengunduh video dengan alat teraudit sesudah spec disetujui). Sama dengan usulan agen. Akibatnya di `SEED.md` §3 |
| P12 | Sumber data plat selain lokasi uji: rekam sendiri · video YouTube (seperti vision-seed D17/D18) · dataset publik? | Ketiganya, masing-masing dicatat asalnya | Kecepatan Fase 0 dan mutu ukurannya. Sesudah K5: sampai ada lokasi uji, sumber-sumber ini **satu-satunya** bahan Fase 0, jadi lisensi dan asal-usulnya (P11, B12) menentukan apa yang boleh dipakai | ✅ **Terjawab 13 Okt lewat K6, bersama P3:** video TikTok dan YouTube, termasuk rekaman di mall dan pabrik, plus cara kreatif tanpa biaya. Dataset publik sudah tercakup K5. Rincian sumber = U9 di `SEED.md` §6 (usulan agen, dikunci di spec) |
| P13 | Bobot awal untuk mesin jualan: tetap ketat (dilatih dari nol, hanya bahan bersih) atau menerima bobot awal yang izin bobotnya dinyatakan permisif walau izin bahan latihnya tidak dinyatakan? (muncul 13 Okt dari [`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md)) | Menerima bobot awal berizin permisif, seperti vonis "CAMPURAN" di vision-seed, dan menanyakan sisa keraguannya ke ahli hukum bersama B9. Alasannya: melatih dari nol dengan bahan bersih yang sedikit kemungkinan jauh lebih lemah; itu belum diukur | Bila tetap ketat: mesin jualan butuh bahan jauh lebih banyak. Bila menerima: tersisa keraguan pada bahan latih pihak ketiga | ✅ **Dijawab lewat K21, 14 Okt (bacaan agen; owner menjawab "ya lanjutkan" atas laporan yang memuat bacaan ini, tidak mengoreksinya):** "selama tidak menyebutkan larangan untuk digunakan dalam pembelajaran, maka kita bisa gunakan". Jadi bobot awal berizin permisif boleh dipakai mesin jualan. Bila bukan itu maksud owner, dibuka lagi |
| P14 | Menurut K21, apakah label "non-komersial" atau "riset saja" (misalnya CC BY-NC), dan syarat situs yang melarang mengunduh tanpa izin (YouTube), dihitung sebagai "larangan"? (muncul 14 Okt dari K21) | Label non-komersial dan "riset saja" dihitung larangan untuk mesin jualan, karena modelnya dijual. Syarat YouTube ditanyakan ke pihak hukum yang sama | Menentukan apakah 100 video riset dan dataset berlabel non-komersial boleh masuk mesin jualan | ✅ **Terjawab 19 Okt untuk video riset → K49:** owner sudah mendapat izin secara verbal (pernyataan owner, tidak tertulis). Dataset berlabel non-komersial belum ada yang dipakai; bila ada, ditanyakan lagi |
| P15 | Dengan baca plat di server (K25), apa yang terjadi di gerbang saat internet atau server putus? (muncul 15 Okt dari K25) | Gerbang tidak membuka otomatis; remote yang ada (U6) menjadi cara buka; kejadian dicatat dan dikirim saat tersambung lagi. Pilihan lain: pembaca kecil di lokasi khusus saat putus, tetapi itu menaruh model di sisi pengguna, yang tidak dikehendaki owner | Seberapa sering penghuni kembali ke remote; janji "tanpa kartu, stiker, atau remote" (K4); isi spec 6.3 | ⏳ Belum ditanyakan; ditanyakan saat spec Fase 2 atau Fase 5 ditulis |
| P16 | Server IBE yang akan menjalankan baca plat (K25): berapa inti CPU, ada kartu grafis atau tidak, dan di mana letaknya (sewa cloud, VPS, atau mesin sendiri)? (muncul 15 Okt dari K28) | Mulai dengan CPU saja; taksiran kecepatan Fase 0A diukur di CPU laptop dengan 1, 2, dan 4 utas sebagai pengganti | Taksiran kecepatan dan biaya per foto (B5, B8); perlu tidaknya kartu grafis di server | ✅ **Terjawab 15 Okt → K29:** bertahap. Mini PC seperti Mini di fase awal, lalu Hostinger KVM 2 sampai KVM 8. Semuanya tanpa kartu grafis (spesifikasi dibaca agen; `SEED.md` §3, "Akibat K29") |
| P17 | Saat mesin ragu pada huruf yang mirip (owner, 18 Okt: H/N, V/Y, O/Q, D/O, N/K, N/M, W/M), apa yang dilakukan gerbang? Owner mengusulkan dua jalur: scan cepat bila tidak ada huruf sensitif, scan normal yang ditandai bila ada | Jalur dipicu oleh keraguan mesin pada huruf itu, bukan oleh hurufnya saja, karena N, H, D, K, M, dan W juga huruf kode wilayah yang umum. Bila ragu: ambil beberapa gambar paling tajam dari kedatangan yang sama; bila masih ragu, gerbang tidak membuka dan foto dikirim ke satpam atau penghuni untuk dikonfirmasi. Tidak pernah membuka karena "paling mirip dengan plat terdaftar" | Seberapa sering penghuni menunggu konfirmasi; risiko membuka untuk kendaraan tak terdaftar yang platnya beda satu huruf; aturan "ragu = tidak membuka" (CLAUDE.md §3) | ✅ **Terjawab 18 Okt → K46**, dengan aturan owner sendiri: 1–2 posisi ragu diloloskan bila tidak ada plat berstatus sama yang cocok, selain itu satpam dipanggil; menurut lokasi (perumahan hanya plat terdaftar). Berbeda dari usulan agen (tahan dan konfirmasi). Akibatnya di `SEED.md` §3 |
| P18 | Untuk apa ciri kendaraan (jenis, merek, warna) dikenali: hanya dicatat bersama kejadian masuk dan keluar, atau juga dicocokkan dengan data pendaftaran supaya plat tiruan (plat penghuni yang dipasang di kendaraan lain) ketahuan? (muncul 19 Okt dari pertanyaan owner; spec induk bagian 4, disetujui K18, menulis tugas S3 "menangkal plat tiruan") | Dicatat **dan** dicocokkan: ciri yang sudah dikenali hampir tanpa biaya bisa dibandingkan dengan data pendaftaran, dan bila berbeda satpam diberi tahu. Pencocokan rupa (cara A spec) menyusul bila perlu | Bila hanya dicatat: S3 lebih ringan, tetapi gerbang membuka untuk plat tiruan; nama model (K8) mungkin tidak perlu dikejar sejauh itu | ✅ **Terjawab 19 Okt → K55** (sama dengan usulan agen): dicatat dan dicocokkan; bila tidak cocok, satpam diberi peringatan, dan gerbang tetap mengikuti plat sampai pengenal ciri terbukti akurat. Akibatnya di `SEED.md` §3 |
| P19 | Analitik pengunjung untuk F&B, kafe, dan mal (usulan owner 19 Okt): (1) motor lawan mobil, untuk luas parkir yang dibutuhkan lawan keuntungan; (2) mobil mewah, keluarga, atau kota, untuk segmen pasar dan belanja; (3) warna plat, termasuk lis biru kendaraan listrik, untuk jumlah pemilik kendaraan listrik. Kapan dikerjakan? (Mal dan F&B belum termasuk kelompok pembeli K4) | Mulai sekarang sebagai prototipe murah dari video parkiran yang sudah ada: hitung motor lawan mobil dan warna plat per video, tanpa pembelian; segmen mobil menyusul sesudah pengenal merek dan model dilatih. Hanya angka agregat, tanpa cap per orang (UU PDP Pasal 10) | Bila sesudah mesin gerbang: analitik tertunda sampai K43 selesai; bila langsung uji coba di lokasi: butuh izin pengelola dan data penjualan kafe | ✅ **Terjawab 19 Okt → K57:** menyusul (berbeda dari usulan agen: prototipe sekarang). Akibatnya di `SEED.md` §3 |
| P20 | Dataset dan model jadi dari Roboflow (all-cars-logo, brand JMTO, car-type, vehicle and license plate, Merk dan Warna Motor) dipakai bagaimana? (muncul 19 Okt dari temuan owner) | Datasetnya saja, sebagai bahan latih tambahan untuk mesin kita, diukur di set uji kita sebelum dan sesudah; label izin di halaman (MIT, CC BY 4.0) diterima seperti K21, dengan risiko asal gambar dicatat. Model jadi mereka tidak dipakai: gambar berplat akan dikirim ke server Roboflow, butuh internet dan akun, dan izin bobotnya tidak dinyatakan | Bila model jadi dipakai: produk bergantung pada layanan luar dan data plat keluar dari server kita (`CLAUDE.md` §4, K25); bila tidak dipakai sama sekali: bahan merek dan warna motor harus dikumpulkan sendiri | ✅ **Terjawab 19 Okt → K56** (sama dengan usulan agen): datasetnya digabung sebagai bahan latih mesin kita, label izin diterima, model jadi tidak dipakai. Akibatnya di `SEED.md` §3 |

## B. Yang belum terbukti

Kolom tengah menyebut **apa yang ada hari ini dan dari mana**. Angka di tabel dibaca dari
[`docs/riset/`](docs/riset/), kecuali yang diberi tanda koreksi. ~~Tidak ada yang diukur sendiri.~~ Koreksi 14 Okt: sejak
Rencana 3 ada angka yang diukur sendiri; letaknya di paragraf "Sesudah …" di bawah dan di [`bukti/`](bukti/).

**Sesudah K5 (13 Okt):** belum ada lokasi uji. Selama itu, "Fase 0" pada B1–B3 hanya menghasilkan angka
sementara dari data luar. B2 dan B3 baru benar-benar terjawab saat ada rekaman dari kamera di gerbang berizin;
B1 terjawab sebagian (plat Indonesia ya, sudut kamera gerbang belum tentu).

**Sesudah K6 (13 Okt):** tanpa pengeluaran dan tanpa perangkat. B5 hanya **ditaksir** di laptop sampai kotak
komputasi ada. B4 tidak dikerjakan sampai owner membeli atau meminjam satu kamera pembaca plat. Plat cetak di
papan yang direkam HP (U9 butir 5) memberi jawaban awal untuk B2 dan B3, dengan batas: HP bukan kamera CCTV.

**Sesudah K9 (13 Okt):** sasaran 99% berlaku terpisah untuk empat kelompok (mobil dan motor, siang dan malam).
B6 membesar: set uji saja butuh lebih dari 1.200 kedatangan berlabel dari posisi kamera gerbang (hitungan agen,
dikunci di spec). Angka dari video daring tidak boleh dilaporkan sebagai "K9 tercapai".

**Sesudah K11 (13 Okt):** salah satu jalur jual adalah OEM ke pemilik merek. B10 (sertifikasi perangkat) harus
terjawab sebelum penawaran OEM pertama, bukan di Fase 5: siapa yang wajib mengurus sertifikasi bila kotaknya
membawa merek pihak lain belum diperiksa.

**Sesudah K13 (13 Okt):** paket perusahaan memuat analisis dan proyeksi tamu, jadi catatan kejadian sampai ke
server kita dan kita ikut memproses data pribadi pembeli. B9 membesar dan harus diperiksa sebelum paket
perusahaan ditawarkan. B8 kini punya satu angka dari owner (Rp 5.000 per bulan untuk perorangan); kesediaan
orang membayarnya tetap belum terbukti.

**Sesudah survei hanya-baca 13 Okt** (dua catatan baru di [`docs/riset/`](docs/riset/); tiga klaim diperiksa
acak agen utama dan cocok, sisanya belum diperiksa ulang):

- **B12:** tiap komponen kini punya vonis **sementara**. Pendeteksi plat bawaan paket jadi berasal dari kode
  GPL; RF-DETR yang Apache hanya ukuran N sampai L; kode fast-plate-ocr MIT tetapi lisensi bobotnya hanya
  pernyataan di sebuah issue. Vonis tetap baru sah sesudah diperiksa pada commit yang dikunci di Fase 0.
- **B6:** dataset plat Indonesia berizin komersial dengan asal jelas hanya dua: INDO-ALPR (6.174 gambar) dan
  Lighting Dataset (561 gambar, ada malam). Label lisensi di Kaggle terbukti tidak bisa dipercaya begitu saja.
- **B2:** sumber sekunder (media otomotif) menyebut nomor polisi motor ditulis satu baris, sama dengan mobil.
  Teks Perpol 7/2021 sendiri belum terbaca.
- **Baru:** ukuran plat di catatan biaya-bangun (460×135 dan 275×115 mm, dari Wikipedia Inggris) tidak cocok
  dengan sumber Indonesia (430×135 dan 275×110 mm). Belum ada yang diperiksa ke peraturannya.
- **Baru:** tidak ditemukan dataset mobil pasar Indonesia untuk K8.

**Sesudah K17 (13 Okt):** 45 video riset dari YouTube tersimpan di `data/video/riset/` dan tercatat di
[`data-asal/video-riset.json`](data-asal/video-riset.json). Ini **bahan**, belum **bukti**: tidak ada satu pun
butir B yang terjawab olehnya. Isi videonya belum dilihat (aturan data pribadi), jadi belum diketahui berapa
yang platnya terbaca, berapa yang dari sudut gerbang, dan berapa yang memuat motor atau malam. 20 dari 45 video
bersisi terpendek di bawah 720 piksel.

**Sesudah K19 (13 Okt):** cara pemeriksaan label video diputuskan owner: agen hanya melihat gambar yang dikecilkan dan
dikaburkan sampai platnya tidak terbaca; label huruf plat diperiksa owner dari lembar contoh di laptop. Ini bukan butir
bagian A (tidak pernah bernomor P), jadi dicatat di sini dan di `SEED.md` §3.

**Sesudah K56 (19 Okt):** lima dataset Roboflow menjadi bahan latih mesin kita (`BOLEH-PRODUK`, risiko asal gambar dicatat). **Yang belum
terbukti:**
- apakah "vehicle and license plate" (plat) menaikkan pencari plat C1 di set uji CCTV owner (Rencana 29);
- apakah labelnya benar menurut lembar contoh yang diperiksa owner.

**Usulan owner (19 Okt): menjual fitur ini sebagai API per panggilan, sekitar Rp 3 per panggilan, supaya dipakai banyak orang dan data
model bertambah.** Bacaan agen, disampaikan ke owner, belum menjadi keputusan:
- **Biaya:** harga per panggilan harus di atas biaya hitung server per gambar. Laju di Mini PC dan VPS sudah sebagian terukur (pencari plat
  sekitar 150 ms dan pembaca sekitar 100 ms per panggilan di Mini PC, Rencana 12–13), tetapi biaya per gambar dalam rupiah belum dihitung.
- **Memakai gambar pelanggan untuk melatih:** gambar pelanggan memuat plat orang lain, jadi ini pemrosesan data pribadi (UU PDP). Butuh dasar
  hukum, persetujuan di syarat layanan, dan pemeriksaan ahli hukum (B9) sebelum dijalankan.
- **Penyalahgunaan:** API baca plat bisa dipakai untuk melacak orang. Pelanggan perlu diverifikasi dan pemakaian dibatasi; ini bagian
  spec layanan API kelak.
- Tempatnya di peta fase: layanan API berjalan di server kita (K25, K29), jadi sejalan dengan Fase 2 dan Fase 6.

Tambahan owner (19 Okt), apa adanya: "perihal API Rp3 rupiah per panggilan, saya rasa nanti rencananya adalah untuk membeli 1 Mini PC sendiri,
kemudian hosting sebagai server saja. agar lebih murah, lebih simple, lebih kecil memakan listrik, dan internet di rumah sangat cepat. untuk data,
sudah akan di katakan di depan untuk menyetujui dulu  dalam bentuk form, namun data tersebut tidak langsung dijadikan pelatihan. dan pemakaian
pasti di batasi, dengan dasar hukum yang jelas," dan owner bertanya di mana API itu bisa dijual, terutama di pasar Indonesia. Bacaan agen:
membeli Mini PC adalah keputusan uang owner (`CLAUDE.md` §8), sejalan dengan K29 (Mini PC di fase awal). Riset saluran jual dan syarat legal
dikerjakan hanya-baca, hasilnya di ~~`docs/riset/`~~ [`docs/riset/2026-10-19-riset-saluran-jual-api.md`](docs/riset/2026-10-19-riset-saluran-jual-api.md) (19 Okt).

**Sesudah riset saluran jual (19 Okt):** jual dulu dari situs sendiri dengan saldo prabayar; pembeli pertama yang realistis pemasang CCTV
dan gerbang serta pengembang kecil; operator parkir besar dan Telkom sudah punya baca plat sendiri. Rp 3 per panggilan lebih murah dari semua
harga publik yang ditemukan, tetapi satu gerbang dengan 300 kendaraan per hari hanya menghasilkan sekitar Rp 27 ribu per bulan, jadi harga
tetap per gerbang layak dipertimbangkan. **Keputusan owner kelak:** menjual sebagai perorangan atau PT; izin tertulis dari ISP untuk server di
rumah; harga per panggilan atau per gerbang. **Yang belum terbukti:** tarif Xendit, kode KBLI final, isi resmi PP 33/2026 dan PP 20/2026,
syarat ISP selain IndiHome (daftar lengkap di bagian 7 berkas riset).

**Sesudahnya, owner (19 Okt) → K59:** 2.000 panggilan pertama gratis setiap bulan; pelanggan enterprise yang menghubungkan perangkat lunak
lain diberi harga berbeda. Harga enterprise belum ditentukan.

**Sesudah dua dataset Roboflow tambahan (19 Okt):** vehicle and license plate (MIT) dan Merk dan Warna Motor (CC BY 4.0) aman, tetapi
gambar latih dan ujinya banyak yang mirip. **Yang belum terbukti:**
- apakah menambah dataset ini ke bahan latih menaikkan angka kita di set uji CCTV owner;
- izin sumber asli dataset gabungan (vehicle and license plate);
- apakah angka 99,5% di halaman Roboflow bertahan di CCTV owner (kemungkinan tidak, karena diukur di soal yang mirip bahan latihnya).

**Sesudah Rencana 28 (19 Okt):** tiga dataset Roboflow aman dan labelnya sah secara teknis (`bukti/2026-10-19-dataset-roboflow.md`). **Yang belum
terbukti:**
- apakah labelnya benar (owner memeriksa lembar contoh, paling banyak 3 per kelas);
- apakah dataset brand (JMTO) menolong pengenal merek di CCTV owner, dan bagaimana kelas merek dan model yang bercampur sebaiknya disusun;
- izin: asal gambar tidak diketahui dan label CC BY 4.0 berasal dari pengunggah.

**Sesudah K55 (19 Okt):** ciri kendaraan dicatat dan dicocokkan dengan data pendaftaran; ketidakcocokan memberi peringatan ke satpam tanpa
menahan gerbang. **Yang belum terbukti:**
- seberapa sering ciri salah dibaca pada kendaraan terdaftar (peringatan palsu ke satpam), per jenis, merek, dan warna;
- pada akurasi berapa pencocokan boleh ikut menahan gerbang (keputusan owner sesudah diukur).

**Sesudah Rencana 27 (19 Okt):** merapikan kotak plat dengan pencarian kedua membuat kotak kurang pas dan bacaan turun di sisi latih, jadi tidak
dipakai (`bukti/2026-10-19-rapikan-kotak-plat.md`). **Yang belum terbukti:**
- apakah kotak label yang ditarik dengan cara seragam, lalu dipakai melatih ulang C1, membuat kotak pencari lebih pas;
- apakah pembaca yang dilatih dengan potongan dari kotak pencari menjadi tahan terhadap kotak yang sedikit keliru.

**Sesudah K52, K53, dan K54 (19 Okt):** warna malam dilihat dengan penerangan (K52), dataset merek Indonesia di Roboflow diunduh owner lalu
diperiksa (K53), dan kotak plat dirapikan (K54, Rencana 27). **Yang belum terbukti:**
- apakah lampu putih yang cukup membuat warna terbaca tanpa membuat plat silau (butuh gerbang sungguhan);
- apakah ketiga dataset Roboflow aman (hanya gambar dan label yang jenisnya cocok dengan isinya) dan labelnya benar;
- asal gambar dataset itu tetap tidak diketahui, jadi izinnya bersandar pada label CC BY 4.0 di halaman pengunggah.

**Sesudah survei merek dan warna (K51, 19 Okt):** `docs/riset/2026-10-19-catatan-merek-warna-mobil.md`. **Yang belum terbukti:**
- seberapa tepat model warna dan jenis Intel (7 warna, 4 jenis; 81–83% di COCO) pada potongan kendaraan CCTV owner, siang, dan seberapa cepat
  di Mini PC;
- apakah logo merek cukup besar di potongan kamera 2K dari jarak gerbang;
- apakah pencocok rupa tanpa latih (SigLIP2, DINOv2) membedakan kendaraan sejenis di CCTV;
- izin dataset Roboflow Indonesia (pengunggah anonim) dan dataset berlabel non-komersial (bagian P14 yang masih terbuka).

**Sesudah Rencana 26 (19 Okt):** pembaca tahan geser (7 potongan, pungut suara) tidak menaikkan bacaan di tangkapan uji (21 → 21 dari 34) dan
memakan 6,5 kali waktu baca, jadi tidak dijadikan bawaan (`bukti/2026-10-19-pembaca-tahan-geser.md`). **Yang belum terbukti:**
- apakah merapikan kotak plat dengan pencarian kedua di sekitar kotak pertama memulihkan bacaan yang rusak karena kotak terlalu besar atau
  terlalu kecil;
- apakah tahan geser berguna di video, tempat rantai sudah menggabung banyak bingkai per kedatangan.

**Sesudah K51 (19 Okt):** owner memilih pembaca tahan geser (Rencana 26) dan meminta survei repo pengenal merek dan warna mobil. **Yang belum
terbukti:**
- apakah memungut suara dari beberapa potongan bergeser memulihkan bacaan yang berubah karena kotak bergeser, dan berapa biaya waktunya di CPU;
- apakah ada pengenal merek dan warna yang kode, bobot, dan datasetnya boleh dijual, dan yang bekerja untuk mobil pasar Indonesia dari sudut
  kamera CCTV. Survei 13 Okt: OpenVINO dan PP-Vehicle mengenali warna dan jenis, tetapi izin bobotnya tidak dinyatakan; dataset merek
  besar non-komersial.

**Sesudah Rencana 25 (19 Okt):** rantai jualan sekarang: kendaraan YOLOX COCO dengan cadangan gambar utuh, pencari plat C1 (`pencari-cctv2-c1`),
pembaca fpo-indo-1; semuanya `BOLEH-PRODUK`. Di tangkapan uji, plat ditemukan 28 → 34 dari 39, tetapi dibaca benar tetap 21 dari 34
(`bukti/2026-10-19-rantai-optimal.md`). **Yang belum terbukti:**
- apakah pembaca yang membaca beberapa potongan bergeser lalu memungut suara (atau dilatih dengan potongan bergeser) memulihkan 4 bacaan yang
  berubah dari benar ke salah;
- apakah melatih lanjut fpo-indo-1 dengan laju lebih kecil, dan zaman dipilih dari validasi tangkapan, menaikkan bacaan tanpa melupakan
  INDO-ALPR;
- apakah C1 juga lebih baik di 77 video uji (rantai baru belum dijalankan di video);
- angka di gerbang sungguhan (K43: rekaman HP owner dan CCTV kantor).

**Sesudah K49 dan K50 (19 Okt):** semua bahan yang dipakai rantai kini `BOLEH-PRODUK` (K44, K47, K48, K49), dan kerja berpindah ke
mengoptimalkan mesin yang sudah ada dengan data owner. **Yang belum terbukti:**
- seberapa jauh cctv1 dan fpo-indo-1 naik bila dilatih lanjut dengan tangkapan owner (141 kotak dan 125 teks di sisi latih), diukur di
  38 gambar tangkapan uji;
- apakah pencari kendaraan COCO perlu dilatih ulang: di lembar tanpa plat, 7 dari 43 plat terlewat karena kendaraannya tidak ditemukan,
  kebanyakan motor;
- izin verbal video riset tidak tertulis (K49).

**Sesudah K48 (19 Okt):** bobot YOLOX COCO boleh menjadi dasar mesin jualan bila dimodifikasi. **Yang belum terbukti:**
- apakah anggapan hukum owner ("dimodifikasi berarti model baru") berlaku; ini masuk pertanyaan untuk ahli hukum bersama B9;
- seberapa jauh Nano-640 (COCO + plat-lighting) naik bila dilatih lanjut dengan kotak plat tangkapan owner, dibanding cctv1 yang memakai
  video riset dan D1 yang dari nol.

**Sesudah K47 (19 Okt):** bobot fast-plate-ocr boleh masuk mesin jualan, dan pembaca jualan berangkat dari fpo-indo-1 yang
dioptimalkan dengan data owner. **Yang belum terbukti:**
- seberapa jauh fpo-indo-1 naik bila dilatih ulang dengan potongan tangkapan owner, termasuk 28 bacaan salah yang kini berteks benar;
- apakah plat buatan masih menolong pembaca yang berangkat dari bobot terbitan (di pembaca dari nol, plat buatan menaikkan 30% ke
  60–65%);
- apakah bobot YOLOX COCO boleh diperlakukan sama. Itu keputusan owner, belum ditanyakan.

**Sesudah K44 (18 Okt):** tangkapan layar owner (181 gambar) boleh melatih mesin yang dijual, dan fokus berpindah ke mesin jualan. **Yang belum terbukti:**
- seberapa jauh pembaca dan pencari plat yang dilatih dari nol (tanpa bobot awal) dari mesin belajar;
- apakah pencari kendaraan dibutuhkan di mesin jualan bila kamera dipasang menurut resep (plat dekat), mengingat belum ada bahan kendaraan yang boleh dijual;
- apakah kotak yang diusulkan mesin belajar lalu diperiksa owner boleh dipakai melatih mesin jualan. Bacaan agen: boleh, karena labelnya diperiksa manusia; ini dicatat sebagai anggapan.

**Usulan owner (18 Okt), untuk Fase 3:** analitik kendaraan bagi pedagang, mal, dan apartemen (jenis, warna, merek, jam ramai). Bacaan agen:
- disajikan sebagai sebaran agregat tanpa cap per orang;
- tafsiran seperti "sedan = kaya" diuji dengan data dulu;
- cap "pickup = potensi maling" tidak dipakai, karena diskriminatif dan berisiko menurut UU PDP Pasal 10 (pemrofilan). Peringatan keamanan didasarkan pada kejadian: plat tak terdaftar, plat tidak cocok dengan kendaraan, atau masuk di luar jam.

**Sesudah K43 (17 Okt):** mesin diselesaikan dulu, lalu pengujian penuh dengan rekaman HP owner atau CCTV kantor. **Yang belum terbukti:**
- apakah rantai membaca berkas video HP (format, orientasi, ukuran 4K) tanpa masalah;
- seberapa dekat hasil di video YouTube dengan hasil di rekaman gerbang sungguhan.

**Sesudah K42 (17 Okt):** arah produk adalah paket Rp 8 juta (CCTV 2K, ESP32 ke server kita, modul pagar, pemasangan), tanpa kamera ANPR. **Yang belum terbukti:**
- apakah kamera CCTV 2K biasa membaca plat dengan andal di malam hari, terutama silau inframerah pada plat putih;
- berapa harga mesin pagar dan pemasangan yang membuat modal Rp 5 juta tercapai;
- berapa langganan bulanan yang menutup biaya server per lokasi;
- apakah pembeli rumah dan perusahaan mau membayar Rp 8 juta.

**Sesudah K41 (17 Okt):** video CCTV gelombang keempat dicari terarah: gerbang tempat kendaraan berhenti dekat kamera, gerbang motor, dan malam atau inframerah. **Yang belum terbukti:** berapa banyak video daring yang platnya cukup besar dan jelas untuk dinilai, dan apakah benda bukan plat "yakin" hanya muncul di adegan tertentu (Rencana 21: semua 26 dari 2 video).

**Sesudah K40 (16 Okt):** resolusi kamera dan jarak kamera ke kendaraan menjadi parameter. Keduanya diringkas menjadi tinggi plat dalam piksel. **Yang belum terbukti:** tinggi plat terkecil yang masih terbaca oleh mesin dan oleh manusia, dan berapa banyak plat yang buram karena gerak, bukan karena kecil.

**Sesudah K39 (16 Okt):** rantai mendahulukan kendaraan (usulan owner): kendaraan, lalu tampak depan atau belakang, lalu plat di area kendaraan itu. Di lembar latih, aturan "plat di dalam kendaraan" meloloskan 14 dari 14 plat dan menyaring 92 dari 106 bukan plat. **Yang belum terbukti:**
- apakah angka itu bertahan di set uji;
- berapa plat yang hilang karena kendaraannya tidak ditemukan (jauh, terpotong tepi gambar, malam);
- cara menentukan tampak depan atau belakang tanpa agen melihat plat;
- pencari kendaraan untuk mesin jualan.

**Sesudah K38 (16 Okt):** spec Fase 1 disetujui; Fase 1 dimulai dan dikerjakan mandiri (K37).
**Sesudah K37 (16 Okt):** agen bekerja mandiri di Fase 1 dan hanya berhenti untuk lembar berplat, pembelian, push, dan keputusan
tentang apa yang dijual, keselamatan, atau data pribadi. Spec Fase 1 ditulis
([`specs/2026-10-16-fase-1-mesin-baca-plat.md`](specs/2026-10-16-fase-1-mesin-baca-plat.md)) dan menunggu satu persetujuan owner.
**Sesudah K36 (16 Okt):** tolak ukur Fase 1 adalah video CCTV dari YouTube (gerbang berbagai tempat dan parkiran gedung,
termasuk motor), dan rancangannya lentur terhadap macam-macam kamera dan infrastruktur. **Bagi B2 dan B3:** motor dan malam kini
dicari di video daring (parkiran gedung, CCTV malam), bukan menunggu rekaman owner. **Yang belum terbukti:** berapa banyak video
CCTV daring yang platnya cukup terbaca untuk menjadi set uji per kelompok, dan cara label nomor platnya diperiksa manusia tanpa
menghabiskan waktu owner.
**Sesudah K35 (16 Okt):** plat buatan komputer dibangun di awal Fase 1, dengan huruf yang digambar sendiri. **Fase 0A selesai.**
**Yang belum terbukti:** seberapa jauh plat buatan komputer menaikkan pembaca yang dilatih dari nol (mesin-baca-1: 26–32%), dan
apakah huruf yang digambar sendiri cukup mirip huruf plat resmi. Keduanya diukur di Fase 1, pada set uji nyata yang tidak pernah
dipakai melatih.
**Sesudah K34 (16 Okt):** owner memilih lanjut ke Fase 1 sekarang, bukan Fase 0B dulu. **Bagi K9, B2, B3, dan B5:** tetap belum
terjawab, dan tetap hanya bisa dijawab dari rekaman di posisi gerbang. Fase 1 bisa membangun mesinnya, tetapi tidak bisa
menyatakan lulus tanpa rekaman itu. Spec Fase 1 perlu menyebut kapan dan bagaimana rekaman itu didapat.
**Sesudah Rencana 15 (16 Okt):** laporan Fase 0A ada di [`bukti/2026-10-16-laporan-fase-0a.md`](bukti/2026-10-16-laporan-fase-0a.md).
Yang belum terjawab dari bahan luar dikumpulkan di bagian 4-nya: K9, B2, B3, B5, plat yang terlewat di video, akurasi rantai per
kedatangan, P14, dan izin fast-plate-ocr. Semuanya kecuali P14 dan izin butuh rekaman dari posisi gerbang. Fase 0A selesai bila
owner memutuskan dua hal: sesudah Fase 0A (Fase 0B, Fase 1, atau ubah arah) dan plat buatan komputer (spec 8.7).
**Sesudah K33 (16 Okt):** owner memilih laporan Fase 0A sebagai langkah berikutnya (Rencana 15). **Bagi B2, B3, dan B5:** laporan
akan menulis apa yang sudah terjawab dari bahan luar dan apa yang hanya bisa dijawab dari posisi gerbang (Fase 0B). Memperkuat
pencari plat dengan contoh "bukan plat" dan rekaman HP owner tetap terbuka.
**Sesudah Rencana 14 (16 Okt):** rantai utuh berjalan di 30 video riset: 269 kedatangan, 13 yakin. Dari lembar owner (120
baris): 99 bukan plat, 14 tak terbaca, dan 7 plat dinilai (3 benar-yakin, 2 benar-ragu, 2 salah-ragu, 0 salah-yakin). Dari 10
kedatangan yakin di lembar, 7 bukan plat. **Bagi B5:** di laptop (2 utas) cari plat 17,7 ms per gambar dan baca 13,9 ms per
potongan; taksiran Mini PC sekitar 0,26 detik per gambar berplat, dan bacaan yakin datang median 0,2 detik video sesudah plat
terlihat bila bacaannya konsisten. **Yang belum terbukti:** akurasi per kedatangan (7 plat terlalu sedikit), plat yang
terlewat, dan apakah pencari plat bisa diajari menolak benda bukan plat. Semuanya butuh bahan gerbang yang lebih baik (Fase 0B)
atau contoh "bukan plat" berlabel ([`bukti/2026-10-16-rantai-utuh-video.md`](bukti/2026-10-16-rantai-utuh-video.md)).
**Sesudah K32 (16 Okt):** bacaan rantai utuh di video riset dinilai dari satu lembar yang diperiksa owner di laptop (nomor
baris dan jenis salah saja). **Yang belum terbukti:** berapa kedatangan yang ada di 30 video itu (mungkin terlalu sedikit untuk
disimpulkan per kelompok; semua video bersudut gerbang siang), dan berapa kendaraan yang platnya tidak ditemukan sama sekali,
karena kendaraan seperti itu tidak muncul di lembar.
**Sesudah K31 (16 Okt):** owner memilih YOLOX-Nano-640 sebagai pencari plat di rantai utuh (Rencana 14). **Yang belum
terbukti:** kecepatan rantai utuh di Mini PC, termasuk unggah dan dekode foto (B5), dan apakah angka pencari plat bertahan di
video riset dan kelak di kamera gerbang sungguhan.
**Sesudah Rencana 13 (16 Okt):** empat pencari plat YOLOX buatan sendiri dilatih dengan 393 foto plat-lighting. Di set uji
(84 foto, 102 plat) mereka menemukan 91–96 plat (89–94%), lawan 31 untuk pembanding siap pakai; plat kecil 10–13 dari 16.
**Yang terjawab dari K30:** kode YOLOX @ 4197784 bisa melatih dengan numpy 2.5 dan torch 2.14 (putaran latih sendiri, tanpa
paket baru), dan 393 foto latih cukup untuk angka itu di dataset yang sama. **Bagi B5:** di Mini PC (2 utas, model saja) cari
plat + baca huruf sekitar 0,25 detik per foto dengan YOLOX-Nano-640 dan sekitar 0,64 detik dengan YOLOX-Tiny-640; unggah,
dekode, dan rantai utuh belum diukur. **Yang belum terbukti:** apakah angka ini bertahan di kamera gerbang sungguhan (satu
dataset, sebagian besar bingkai video 1080p, kelompok gelap hanya 3 plat), dan apakah bobot awal COCO YOLOX boleh dipakai untuk
mesin jualan (B12, tetap `BELUM-JELAS`) ([`bukti/2026-10-16-pencari-plat-yolox.md`](bukti/2026-10-16-pencari-plat-yolox.md)).
**Sesudah K30 (16 Okt):** owner memilih melatih YOLOX-Nano dan YOLOX-Tiny sekaligus sebagai pencari plat buatan sendiri.
Pilihan akhirnya ditentukan dari validasi dan kecepatan di Mini PC. **Yang belum terbukti:**
- apakah kode YOLOX @ 4197784 bisa melatih dengan numpy 2.5 dan torch 2.14;
- apakah 393 foto latih plat-lighting cukup;
- apakah bobot awal COCO YOLOX boleh dipakai untuk mesin jualan (izinnya tidak dinyatakan, B12).
**Sesudah Rencana 12 (16 Okt):** di Mini PC (Celeron N5095), satu panggilan model dengan 2 utas butuh sekitar 73 ms untuk
YOLOX-Nano, 251 ms untuk YOLOX-Tiny, 1.403 ms untuk RF-DETR Nano, dan 100 ms untuk pembaca huruf. **Bagi B5:** dengan YOLOX-Nano,
cari plat + baca huruf sekitar 0,17 detik per foto (model saja); dengan RF-DETR Nano sekitar 1,5 detik, sehingga tiga foto per
kedatangan melewati sasaran dua detik. Pembanding siap pakai menemukan hanya 30% plat di foto 1080p karena plat kecil hilang
pada masukan 384 px: ukuran masukan dan pembingkaian kamera menentukan, dan itu baru bisa dijawab dari posisi gerbang (Fase
0B) ([`bukti/2026-10-16-pencari-plat-ukur.md`](bukti/2026-10-16-pencari-plat-ukur.md)).
**Sesudah K29 (15 Okt):** server baca plat bertahap: Mini PC (Celeron N5095, 4 inti, tanpa kartu grafis) di fase awal, lalu
Hostinger KVM 2 sampai KVM 8 (2 sampai 8 vCPU AMD EPYC, tanpa kartu grafis). **Bagi B5:** kecepatan baca huruf diukur di CPU
laptop; Celeron N5095 jauh lebih lemah, jadi angka Mini PC harus diukur di Mini PC sendiri. Pencari plat juga harus jalan di
CPU. **Bagi B8:** biaya server per bulan kini terbaca (KVM 2 sampai KVM 8, promo $8,99 sampai $25,99, perpanjangan $14,99
sampai $49,99), jadi biaya per foto bisa ditaksir sesudah rantai utuh terukur. **Bagi P15:** satu server terpusat berarti
gangguan di sisi server memengaruhi semua gerbang.
**Sesudah Rencana 11 (15 Okt):** fpo-indo-1 kini ada dalam format ONNX yang terbukti membaca sama dengan versi Keras-nya (set
uji 1.422 gambar, beda 0). **Bagi B5:** di CPU mesin ini, membaca satu potongan plat butuh median 23,3 ms dengan satu utas
(10,4 ms dengan empat), ditambah dekode sekitar 9 ms, jadi kira-kira 30 potongan plat per detik per inti. Ini hanya langkah
baca huruf; mencari plat di foto utuh, unggah, dan pencocokan belum terukur. Taksiran untuk server IBE menunggu P16
([`bukti/2026-10-15-fpo-indo-1-onnx.md`](bukti/2026-10-15-fpo-indo-1-onnx.md)).
**Sesudah K28 (15 Okt):** owner memilih urutan berikutnya: mesin baca huruf dibuat siap jalan di server IBE dan diukur
kecepatannya, lalu mencari plat di foto utuh dan video riset, lalu laporan Fase 0A. Model gratis Tiongkok lain (GLM-OCR,
PaddleOCR-VL) dicatat sebagai calon pembanding atau pembantu label yang **belum diukur** (pilihan D, tetap terbuka); izin dan
cara memuatnya belum diperiksa. Pertanyaan baru: P16 (spesifikasi server IBE).
**Sesudah Rencana 10 (15 Okt):** fast-plate-ocr yang dilatih ulang dengan bahan latih INDO-ALPR (fpo-indo-1) membaca benar
79,4% (mobil-terang), 86,0% (mobil-gelap), dan 79,8% (motor-terang) kedatangan pada set uji adil, sedangkan fast-plate-ocr
terbitan 61–79% dan Qwen3-VL 65–68% ([`bukti/2026-10-15-fpo-latih-ulang.md`](bukti/2026-10-15-fpo-latih-ulang.md)). **Belum
terbukti:** seberapa banyak kenaikan itu "keuntungan tuan rumah" (dilatih dengan dataset yang sama dengan set uji), dan
apakah angkanya bertahan di kamera gerbang sungguhan (K9). **Bagi B5:** kecepatan di server belum diukur, karena ekspor ONNX
belum jalan di Keras + torch. **Bagi B12:** tanda mesin tetap `RISET-SAJA` sampai izin tertulis datang (K27).
**Sesudah Rencana 9 dan K27 (15 Okt):** jalur melatih ulang fast-plate-ocr terbukti jalan di image lab tambahan dengan plat
buatan (Keras 3.15.1 di atas torch, bobot `.keras` sama dengan ONNX terbitan, 192/192 tensor termuat). **Bagi B12:** draf
permintaan izin disetujui owner apa adanya dan akan dikirim owner sendiri sebagai issue baru di GitHub fast-plate-ocr, pada
waktu yang owner pilih (K27). Sampai ada jawaban, bobot itu tetap `BELUM-JELAS` dan hasil latih ulang bertanda riset;
pekerjaan tidak menunggu. Jawaban pembuatnya disimpan di `docs/lisensi/ankandrew__fast-plate-ocr/` saat datang.
**Sesudah K25 dan K26 (15 Okt):** owner memutuskan baca plat diproses di server IBE (K25) dan pembaca huruf berangkat dari
fast-plate-ocr yang dilatih ulang (K26). **Artinya bagi B5:** kecepatan yang menentukan adalah unggah + baca di server +
balasan, bukan kotak murah. **Bagi B8:** biaya server per foto dibandingkan dengan langganan perlu dihitung. **Bagi B9:**
foto berplat kini keluar dari lokasi ke server IBE, jadi kewajiban pemrosesan data pribadi membesar dan harus diperiksa
ahli hukum sebelum lokasi pertama. **Bagi B12:** bobot fast-plate-ocr belum berizin tertulis; izin diminta dari pembuatnya.
Pertanyaan baru: P15 (gerbang saat internet atau server putus).

**Sesudah Rencana 8 Fase 0A (14 Okt):** mesin baca huruf buatan sendiri yang pertama (CNN + LSTM + CTC, 909.925 parameter,
dilatih dari nol hanya dengan INDO-ALPR; tanda mesin `BOLEH-PRODUK`) membaca benar 26–32% kedatangan per kelompok pada set
uji yang adil (911 plat tanpa label pilihan pembaca), sedangkan Qwen3-VL 65–68% dan fast-plate-ocr 61–79%; motor-gelap
terlalu sedikit ([`bukti/2026-10-14-mesin-baca-pertama.md`](bukti/2026-10-14-mesin-baca-pertama.md)). Rugi latihan hampir nol sedangkan validasi berhenti di 31,7%: mesin menghafal karena bahannya
sedikit. **Artinya bagi B1:** mesin buatan sendiri belum mendekati pembanding; jalurnya lebih banyak bahan (plat buatan
komputer) atau bobot awal yang izinnya jelas. **Bagi B5:** 0,003 detik per gambar di CPU laptop untuk langkah baca huruf;
kotak murah belum diukur. **Bagi B6:** 2.521 plat (3.954 gambar) tidak cukup untuk melatih dari nol.

**Sesudah Rencana 7 Fase 0A (14 Okt):** bahan latih baca huruf dibersihkan (K24). 22 plat latih dikeluarkan karena
kendaraannya juga ada di set uji: dikenali dari gambar yang nyaris kembar dengan label yang hanya beda 1–2 huruf. Lalu 44
label latih dibetulkan dan 4 plat dikeluarkan. Bahan latih kini 2.824 plat dan set uji 937, tanpa plat atau kendaraan
kembar di kedua sisi ([`bukti/2026-10-14-label-bahan-latih.md`](bukti/2026-10-14-label-bahan-latih.md)). **Temuan:** kedua pembaca bisa sepakat pada bacaan yang salah; label penerbit ternyata
benar pada 27 dari 75 baris yang dicurigai di bahan latih. Jadi label otomatis dari kesepakatan dua pembaca harus
diperiksa manusia. **Artinya bagi B6:** bahan latih pertama untuk mesin buatan sendiri siap; berapa label salah yang
tersisa belum diukur.

**Sesudah K24 (14 Okt):** owner memilih membersihkan label bahan latih dulu dengan cara yang sama (dua pembaca, lalu owner
memeriksa yang dicurigai), sebelum mesin baca huruf pertama dilatih. Ini bukan butir bagian A, jadi dicatat di sini dan di
`SEED.md` §3. **Artinya bagi B6:** bahan latih yang bersih dari kebocoran plat dan dari sebagian label salah baru ada
sesudah Rencana 7; sisa label salah tetap ada karena cara ini hanya menangkap kira-kira separuhnya.

**Sesudah Rencana 6 Fase 0A dan K23 (14 Okt):** label set uji dibetulkan (K22): 31 dari 945 dicurigai, dan owner
membenarkan tulisan kedua pembaca pada 29. Lima plat dikeluarkan karena tulisan benarnya tidak diketahui, dan tiga lagi
karena label barunya ternyata plat di bahan latih (K23). Set uji kini 937 kedatangan, 0 plat di kedua sisi. Terhadap label
yang sudah dibetulkan, Qwen3-VL membaca benar 66–70% dan fast-plate-ocr 62–80% kedatangan per kelompok (motor-gelap
terlalu sedikit); keduanya tidak bisa disebut berbeda ([`bukti/2026-10-14-label-dan-pembaca-kedua.md`](bukti/2026-10-14-label-dan-pembaca-kedua.md)). **Artinya bagi B1:** dua pembanding siap dibandingkan
dengan mesin buatan sendiri, dengan catatan angka keduanya sedikit dimudahkan oleh cara pembetulan label. **Bagi B6:**
sekitar 3% label salah mungkin masih tersisa di set uji (taksiran dari 6 contoh); label bahan latih belum diperiksa, dan
K23 menunjukkan label salah bisa menyembunyikan kebocoran.

**Sesudah K22 (14 Okt):** owner memeriksa 60 contoh label set uji dan menemukan 4 sampai 6 label penerbit yang salah, lalu
memilih cara membetulkannya: hanya label yang dicurigai yang diperiksa owner, yaitu plat yang dibaca sama oleh dua
pembaca berbeda (Qwen3-VL-2B dan satu paket jadi) tetapi berbeda dari labelnya. Ini bukan butir bagian A (tidak pernah
bernomor P), jadi dicatat di sini dan di `SEED.md` §3. **Artinya bagi B6:** set uji baca huruf yang labelnya sudah
dibetulkan baru ada sesudah Rencana 6; sampai itu, angka baca huruf berarti "sama dengan label penerbit". Label salah yang
dibaca salah dengan cara sama oleh kedua pembaca bisa lolos; besarnya ditaksir dari 60 contoh yang sudah diperiksa.

**Sesudah Rencana 5 Fase 0A (14 Okt):** angka pertama Fase 0A ada, baru untuk langkah baca huruf
([`bukti/2026-10-14-baca-huruf-pertama.md`](bukti/2026-10-14-baca-huruf-pertama.md)). INDO-ALPR dibagi ulang per plat
karena pembagian penerbitnya bocor: set uji 945 kedatangan (1.431 gambar), tanpa satu plat pun yang juga ada di bahan
latih. Qwen3-VL-2B lokal, sebagai pembanding AI serba-bisa, membaca sama dengan label penerbit pada 61–65% kedatangan per
kelompok (mobil-terang 414 dari 642, mobil-gelap 39 dari 60, motor-terang 135 dari 221; motor-gelap hanya 22 kedatangan,
terlalu sedikit), 0,277 detik per gambar di RTX 4060. Owner memeriksa 60 contoh label: 4 sampai 6 label penerbit salah (kira-kira 1 dari 10), jadi angka itu dibandingkan dengan
label yang tidak selalu benar. **Artinya bagi B1:** ada angka
pertama untuk satu langkah, pada potongan plat yang sudah rapi, bukan gambar CCTV; belum ada angka mesin buatan sendiri.
**Bagi B2:** motor ada di INDO-ALPR (243 plat di sisi uji menurut nomor urut), tetapi bukan dari sudut kamera gerbang.
**Bagi B3:** "gelap" hanya taksiran dari terang potongan plat, bukan malam. **Bagi B6:** bahan latih baca huruf yang
bersih dari kebocoran ada 2.850 plat (4.467 gambar); labelnya belum diperiksa, dan dari contoh set uji kira-kira 1 dari 10
label penerbit salah.

**Sesudah Rencana 4 Fase 0A (14 Okt):** dua dataset berizin jual tersimpan dan terkunci: INDO-ALPR bagian asli
(6.174 gambar, labelnya nomor plat di nama berkas; tiap berkas cocok dengan SHA-256 penerbit) dan dataset pencahayaan
(561 gambar berkotak plat, tanpa teks plat). Ini bahan pertama yang boleh masuk mesin jualan, dan pemeriksa mesin jualan
terbukti menerimanya sambil tetap menolak video riset. **Yang belum diketahui:** apakah INDO-ALPR berisi potongan plat
atau foto adegan, berapa bagian motornya, berapa yang malam, dan apakah bagian latih dan ujinya memuat plat yang sama;
itu dijawab ikhtisar di Rencana 5. **Bagi B9:** soal data pribadi bersandar pada pernyataan owner (K21).

**Sesudah K21 (14 Okt):** owner memutuskan bahan dari internet boleh melatih model yang dijual selama sumbernya tidak
menyebut larangan dipakai belajar, dan menyampaikan nasihat pihak hukum soal data pribadi (B9). Itu menjawab P13 (bacaan
agen) dan memunculkan P14: arti "larangan" untuk label non-komersial dan syarat situs. B9 kini berisi pernyataan owner,
bukan bukti yang dilihat agen; merekam di lokasi pihak lain tetap butuh izin pengelolanya (`CLAUDE.md` §4).

**Sesudah gelombang kedua dipilah (K20, 13 Okt):** 55 video baru dipilah dengan cara yang sama (K19; owner memeriksa
lembarnya lebih dulu). Seluruh bahan sekarang 100 video: bersudut gerbang 17 (4.176 detik), kamera diam lain 13, kamera
dasbor 14, lain-lain 50, tidak bisa ditentukan 6. **Artinya bagi B2 dan B3: tetap belum terjawab.** Malam dari sudut
gerbang masih nol walau 5 dari 14 pencarian memuat kata "malam", dan motor di sudut gerbang hanya "mungkin" pada tiga
video. Bahan gerbangnya pun timpang: 3.451 dari 4.176 detik berasal dari satu video 640×360, dan hanya 7 dari 17 yang
bersisi terpendek 720 piksel ke atas. Video internet sudah dicoba dua kali; untuk malam dan motor di gerbang yang tersisa
adalah rekaman sendiri (pilihan C) dan Fase 0B.

**Sesudah K20 (13 Okt):** karena bahan bersudut gerbang hanya 6 video, owner memilih unduhan gelombang kedua yang
diarahkan (kamera diam di gerbang, malam, motor). Itu menambah bahan, belum menjawab butir B mana pun. Merekam sendiri
dengan HP (pilihan C) tetap terbuka dan tetap cara paling tepat sasaran untuk B2 dan B3.

**Sesudah Rencana 3 Fase 0A (13 Okt):** isi 45 video kini terpilah (`data-asal/video-riset.json`). Yang bersudut gerbang
hanya 6 video, 239 detik seluruhnya, tak satu pun malam, dan hanya 1 yang bersisi terpendek 720 piksel ke atas. Kamera
diam lain 4 video; kamera dasbor 9 video (3.828 detik, 6 di antaranya malam atau campuran); 23 video berupa layar
perangkat lunak, salindia, atau video promosi; 3 tidak bisa ditentukan. Ini menjawab "bahan apa yang kita punya", bukan
butir B mana pun: apakah platnya terbaca mesin, dan pada kondisi apa, belum diukur. **Artinya bagi B2 dan B3:** dari
bahan ini belum ada satu pun rekaman malam dari sudut gerbang, dan motor di sudut gerbang tidak bisa dipastikan dari
gambar sekecil itu.

**Sesudah Rencana 2 Fase 0A (13 Okt):**

- **B12:** vonis izin kini sah untuk sepuluh komponen di [`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md), dibaca dari
  berkas pada commit yang dikunci. Kode kesepuluhnya berizin permisif. **Tidak ada satu pun bobot bawaan yang bervonis
  `BOLEH-PRODUK`**: enam `BELUM-JELAS` karena izin bobot atau izin bahan latihnya tidak dinyatakan, empat `BELUM-JELAS`
  karena komponennya belum diklon. Ini memunculkan P13.
- **B2 dan warna plat:** [`docs/peraturan-plat.md`](docs/peraturan-plat.md) memuat yang tertulis di Perpol 7/2021. Yang
  diatur di sana: warna (Pasal 45), isi plat (Pasal 44), susunan nomor polisi (Pasal 6), dan alokasi nomor urut per
  jenis kendaraan (Lampiran). Yang tidak diatur di sana: ukuran, bentuk huruf, dan susunan baris; itu diserahkan ke
  Keputusan Kakorlantas yang tidak ditemukan dalam bentuk yang bisa dibaca. Tiga sumber sekunder menyebut tiga ukuran
  berbeda.

| # | Yang belum terbukti | Bukti yang ada hari ini (dan keandalannya) | Dijawab di |
|---|---|---|---|
| B1 | Akurasi mesin baca plat sumber terbuka pada plat Indonesia dari kamera CCTV biasa | Hasil akademik Indonesia 70–87% bacaan utuh (dari ringkasan pencarian; halamannya tidak dibuka) | Fase 0 |
| B2 | Plat motor terbaca dari posisi kamera gerbang (plat lebih kecil dari plat mobil) | **Koreksi 13 Okt:** tadinya tertulis "dua baris". Menurut catatan biaya-bangun, baris kedua adalah masa berlaku dan ada di semua plat; catatan itu tidak menemukan sumber untuk nomor polisi dua baris pada motor. Belum diperiksa ke peraturannya. Tidak ditemukan uji lapangan apa pun. Sekitar 80–85% kendaraan Indonesia adalah motor (halaman sekunder tak bertanggal) | Fase 0 |
| B3 | Malam, hujan, dan silau lampu depan pada kamera biasa tanpa lampu inframerah khusus | Tidak ada. Klaim vendor 96–98,5% berlaku "pada pemasangan dan pencahayaan yang dianjurkan" | Fase 0, lalu Fase 5 |
| B4 | Kamera pembaca plat jadi (Hikvision, Dahua) pada plat Indonesia, sebagai pembanding | Tidak ada uji independen. Dukungan Hikvision untuk plat Indonesia dibaca berbeda oleh dua peneliti | Fase 0, bila owner setuju membeli atau meminjam satu unit |
| B5 | Kotak komputasi murah cukup cepat: gerbang mulai membuka sebelum kendaraan lama menunggu | Tidak ada ukuran. Harga kotak dari listing marketplace yang tidak diperiksa ulang | Fase 0 (ukur), Fase 2 (rantai penuh) |
| B6 | Berapa banyak data plat yang dibutuhkan untuk mencapai angka lulus | Dataset publik plat Indonesia yang ditemukan kecil: 1.000 gambar (Kaggle), 362 foto (Semarang), 49 gambar. Sumbernya satu tesis yang dikutip catatan biaya-bangun | Fase 0 → Fase 1 |
| B7 | Plat tiruan: seberapa mudah menipu, dan seberapa menolong pembanding ciri kendaraan | Tidak ditemukan uji publik pemalsuan plat cetak terhadap kamera gerbang | Fase 3 |
| B8 | Orang mau membayar, dan berapa | Tidak ada survei atau data penjualan. Ruang harga Rp 6–15 juta per jalur = estimasi peneliti. Satu pesaing lokal menjual paket "ANPR untuk Sistem Gate" 2 kamera seharga Rp 11 juta (listing yang tidak diperiksa ulang) | Sebelum Fase 4; caranya belum dirancang |
| B9 | Hukum: plat sebagai data pribadi; apakah gerbang privat termasuk "tempat umum" menurut UU PDP Ps. 17 | PP 33/2026 berlaku 16 Jan 2027 (dari ringkasan; teksnya belum dibaca). vision-seed mencatat konsultan hukum sudah ditemukan (catatan 3 Okt, belum diperiksa ulang). **Owner 14 Okt (K21):** sudah berkonsultasi dengan pihak hukum; selama plat tidak dipublikasikan secara frontal ke masyarakat tanpa izin, tidak menjadi masalah. Agen tidak melihat hasil konsultasinya | Sebelum merekam di lokasi milik pihak lain |
| B10 | Sertifikasi perangkat bila kotak ber-radio dijual dengan merek sendiri | Tarif sekitar Rp 12 juta dari kutipan yang terpotong; lama 8–10 minggu dari artikel 2018 | Fase 5 |
| B11 | Ragam motor gerbang di lapangan dan cara memicunya | Belum diperiksa per merek | Fase 2 (meja uji), Fase 5 |
| B12 | Lisensi komponen baca plat: kode, bobot, dan dataset | **Koreksi 14 Okt: sudah divonis** di Rencana 2 ([`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md)): kode kesepuluh komponen permisif, bobot bawaannya belum ada yang `BOLEH-PRODUK`; dua dataset `BOLEH-PRODUK` sejak Rencana 4. Catatan semula: ~~Belum ada vonis.~~ Catatan biaya-bangun menyebut fast-alpr dan Frigate berlisensi MIT serta RF-DETR Apache-2.0; belum diperiksa sendiri ke berkas LICENSE, dan lisensi bobot serta datasetnya belum dilihat. **15 Okt (K27):** izin tertulis bobot fast-plate-ocr diminta lewat pesan yang disetujui owner; owner mengirimnya sendiri kapan saja; sampai dijawab, bobot itu tetap `BELUM-JELAS` | Fase 0, tugas pertama |
