# Analisa bisnis CCTV Gerbang: harga pasar, posisi produk, dan alasan orang membeli

> Untuk owner, 17 Okt 2026. Disusun atas pertanyaan owner: berapa harga kamera LPR/ANPR di Indonesia, apakah kita masih perlu
> melatih model sendiri, berapa biayanya, dan mengapa orang mau membeli produk ini.
>
> **Dasar:**
> - riset pasar 13 Okt ([`2026-10-13-catatan-pasar-dan-harga-gerbang-plat.md`](2026-10-13-catatan-pasar-dan-harga-gerbang-plat.md),
>   sumber lengkap ada di sana);
> - pencarian ulang 17 Okt;
> - angka mesin kita di 77 video uji (Rencana 23).
>
> **Batas penting:** harga diambil dari marketplace dan situs vendor, sebagian hanya dari ringkasan hasil pencarian, dan bisa
> berubah. Sebelum dipakai untuk menawar, minta penawaran resmi dari 2–3 distributor.

## 1. Jawaban singkat

1. **Kamera ANPR/LPR jadi di Indonesia: sekitar Rp 8–17,5 juta per kamera.** Contohnya Hikvision DS-TCG405/406 dan merek lain.
   - Kamera ini sudah membaca plat sendiri dan menyimpan daftar izin sampai 100.000 plat.
   - Ia juga bisa membuka palang lewat relay, walau tanpa server dan tanpa internet.
   - Dahua mencantumkan Indonesia di daftar negara yang platnya dikenali.
   - Kamera CCTV biasa: Rp 1,3–1,7 juta.
2. **Fungsi "baca plat lalu buka palang" sudah menjadi barang jadi.** Kita tidak bisa menjual hanya itu kepada pembeli yang memang
   akan membeli kamera baru.
3. **Pembeli juga punya pilihan yang jauh lebih murah: UHF RFID.** Pembacanya Rp 1,4–2,9 juta, dan stiker kaca Rp 1.500–4.500
   per mobil. Untuk rumah pribadi, remote pagar cukup Rp 215 ribu.
4. **Ruang kita ada di empat tempat:**
   - memakai CCTV yang sudah terpasang, sehingga pembeli hemat Rp 6–15 juta per jalur;
   - plat motor, yang tidak didokumentasikan oleh kamera jadi;
   - aplikasi pengelolaan warga, tamu, dan iuran, yang bisa dibayar bulanan;
   - pencocokan ciri kendaraan dengan plat untuk menangkap plat palsu.
5. **Melatih model sendiri masih berguna, tetapi bukan satu-satunya jalan.** Saran agen: jadikan **aplikasi pengelolaan** sebagai
   produk inti yang bisa memakai kamera ANPR jadi **atau** mesin kita. Mesin kita diteruskan terutama untuk motor dan kamera
   biasa. Lalu beli satu kamera ANPR untuk diuji berdampingan di gerbang nyata. Pembelian ini keputusan owner.

## 2. Harga pasar (Indonesia, Oktober 2026)

| Barang | Harga | Catatan |
|---|---|---|
| Kamera ANPR jadi (Hikvision DS-TCG405/406, Cardteck, tanpa merek) | Rp 8–17,5 juta | Baca plat di kamera, daftar izin, relay ke palang, jalan tanpa server. Bhinneka 17 Okt: DS-TCG406-E Rp 8,9 juta (tertulis tidak tersedia) |
| Kamera ANPR kelas tilang (Hikvision 9 MP) | Rp 99 juta | Untuk persimpangan jalan, bukan gerbang |
| Kamera CCTV IP biasa (Hikvision 2–4 MP, luar ruang) | Rp 1,3–1,7 juta | Tokopedia 17 Okt; belum termasuk NVR dan pemasangan |
| Paket parkir LPR (perangkat lunak + kamera LPR) | Rp 38,3 juta | Nale |
| Paket parkir 1 masuk / 1 keluar dengan pembaca plat | Rp 89,9 juta | SistemParkir.com; perangkat lunak pembaca plat gratis, tanpa iuran bulanan |
| Paket 2 masuk / 2 keluar (palang, ANPR, perangkat lunak) | Rp 108 juta | MSM; pemasangan terpisah; sewa palang Rp 3,7 juta per bulan |
| Paket palang + RFID kartu untuk perumahan | Rp 7,5 juta (Tokopedia) / "mulai Rp 18 juta" (paket cluster) | Kartu RFID 200 lembar ikut di paket Tokopedia |
| Pembaca UHF RFID jarak jauh (stiker kaca) | Rp 1,4–2,9 juta per pembaca | Stiker Rp 1.500–4.500 per mobil; jarak baca 5–15 m |
| Motor pagar geser (rumah) | Rp 1,5–5,4 juta | Remote tambahan Rp 215 ribu |
| Perangkat lunak LPR luar negeri (Plate Recognizer Stream) | USD 35 per kamera per bulan (≈ Rp 627 ribu) | + USD 10 per gerbang untuk membuka gerbang; per tahun ≈ Rp 9,7 juta per kamera |
| Aplikasi iuran RT/RW (RTPINTAR) | Rp 120 ribu per bulan (100 rumah), Rp 300 ribu (600 rumah) | Pembanding harga aplikasi pengelolaan |
| Komputer kecil di lokasi (Intel N100) | **Perkiraan** Rp 3–5 juta | Belum ada harga Rupiah yang terverifikasi. Pembanding: USD 156 ke atas (2023) |

**Biaya orang (pembanding):**
- UMP Jakarta 2026: Rp 5.729.876 per bulan.
- Satpam perumahan sekitar Rp 3–6 juta per orang per bulan.
- Cluster 200 rumah dengan IPL Rp 500 ribu per rumah memungut sekitar Rp 100 juta per bulan. Empat satpamnya menghabiskan
  sekitar Rp 15–25 juta per bulan.

## 3. Hitungan untuk satu gerbang cluster (1 jalur masuk + 1 jalur keluar)

Palang tidak dihitung, karena sama untuk semua pilihan.

| Pilihan | Biaya awal | Biaya bulanan | Kelebihan | Kekurangan |
|---|---|---|---|---|
| **UHF RFID** (2 pembaca + 300 stiker) | ≈ Rp 4,7 juta | – | Paling murah dan andal | Stiker harus dibagikan dan dikelola; tamu tetap manual |
| **Kamera ANPR jadi** (2 kamera) | ≈ Rp 18–35 juta | – | Jalan tanpa server; ada garansi merek | Plat motor tidak terbukti; daftar izin diatur di kamera, tanpa aplikasi warga |
| **Kamera biasa + perangkat lunak luar negeri** | 2 × Rp 1,5 juta + komputer | ≈ Rp 1,6 juta (2 kamera × USD 45) | Akurat menurut vendor | Iuran per kamera mahal; dalam 1–2 tahun lebih mahal daripada kamera ANPR |
| **Produk kita** (CCTV yang ada atau 2 kamera biasa + komputer kecil + relay) | ≈ Rp 6–9 juta, atau ≈ Rp 3–5 juta bila CCTV sudah ada | Langganan aplikasi (harga belum ditetapkan) | Murah, memakai CCTV yang ada, plat motor bisa diperkuat, aplikasi warga dan tamu | Akurasi belum siap jual; butuh pemasangan yang benar |

**Kesimpulan angka:**
- **Selisih yang bisa kita tawarkan dibanding kamera ANPR jadi sekitar Rp 6–15 juta per jalur,** sekali bayar. Pembeli hanya
  mau pindah bila mesin kita sama andalnya.
- **Melawan RFID, kita kalah harga.** Yang kita jual adalah kenyamanan tanpa stiker atau kartu, catatan foto kendaraan, dan
  aplikasi.

## 4. Kondisi mesin kita sekarang (jujur)

Diukur di 77 video CCTV daring (Rencana 23) dari lembar owner: 120 baris kedatangan dan 77 bingkai.

| Ukuran | Hasil | Sasaran (K9) |
|---|---|---|
| Plat mobil yang bisa dinilai: benar dan yakin | 11 dari 16 (5 lainnya benar tetapi ragu, **0 salah**) | 99%, salah-yakin nol |
| Plat motor yang bisa dinilai: benar dan yakin | 3 dari 8 (4 salah-ragu, **1 salah-yakin**) | 99%, salah-yakin nol |
| Benda bukan plat di lembar | 51 dari 120 baris | – |
| Bingkai berplat terbaca yang platnya terlewat | 5 dari 9 | – |

**Artinya:**
- **Mesin kita belum siap dijual.** Untuk mobil di siang hari ia sudah tidak salah membaca, tetapi masih sering ragu dan sering
  melewatkan plat.
- **Motor masih lemah.** Malam belum terukur.
- **Video daring bukan kamera gerbang yang dipasang benar.** Di gerbang nyata dengan kamera yang dipasang menghadap plat,
  angkanya bisa jauh lebih baik. Ini baru terbukti di Fase 0B dan Fase 5.

## 5. Mengapa orang mau membeli (alasan pembeli, per kelompok)

**Cluster, perumahan, dan apartemen** (K10: digarap lebih dulu). Pembelinya pengelola, developer, atau RT/RW; uangnya dari IPL.
- **Tanpa kartu, stiker, atau remote.** Kartu tidak hilang, tidak dipinjamkan, tidak digandakan. Ini alasan owner sendiri
  (P1: "tidak perlu lagi kartu-kartu yang bisa membuat lupa").
- **Catatan keluar-masuk kendaraan dengan foto.** Berguna saat ada kehilangan atau kejadian.
- **Tamu didaftarkan warga lewat aplikasi,** sehingga satpam tidak perlu menelepon.
- **Warga yang menunggak iuran bisa dibatasi.** Ini sudah dijual di Indonesia (ZCluster), jadi terbukti dicari.
- **Satpam tidak lagi membuka-tutup untuk warga** dan bisa fokus ke tamu, kurir, dan ojek. Produk ini **tidak menggantikan
  satpam**, jadi jangan dijual sebagai pemotong gaji satpam.
- **Ciri kendaraan dicocokkan dengan plat** (K8). Mobil berplat palsu atau plat curian yang tidak cocok dengan merek dan warna
  terdaftar ditandai. Korlantas mencatat 16.812 pelanggaran plat palsu atau tanpa plat dalam Januari–Juli 2026.

**Gudang, pabrik, dan kantor.**
- **Catatan jam masuk dan keluar truk** dan kendaraan pemasok, untuk audit dan penagihan.
- **Analisa dan proyeksi kedatangan** (K13: paket perusahaan).
- **Menyambung ke sistem lain,** misalnya data karyawan dan tamu.

**Pemasang CCTV dan integrator** (jalur jual K11 nomor 4).
- Mereka ingin menjual "CCTV pintar" tanpa kamera mahal.
- Kita menjual lisensi per jalur. Mereka yang mengurus survei, pemasangan, dan servis, yaitu bagian yang tidak bisa dikerjakan
  satu orang di banyak tempat.

**Kost, apartemen kecil, dan rumah pribadi.**
- Penggantinya remote Rp 215 ribu, dan kemauan membayarnya rendah.
- Tidak ditemukan produk konsumen pembaca plat untuk rumah di Indonesia. Pasar ini belum terbukti, dan sebaiknya menyusul.

## 6. Apakah masih perlu melatih model sendiri? Tiga jalan

| Jalan | Isi | Untung | Rugi |
|---|---|---|---|
| **A. Pakai kamera ANPR jadi** | Aplikasi kita di atas kamera Hikvision/Dahua; pelatihan model dihentikan | Cepat ke pasar; akurasi dan garansi dari merek | Bergantung merek; harga perangkat tinggi; plat motor Indonesia belum terbukti; pembeda kita hanya aplikasi |
| **B. Teruskan mesin sendiri saja** | Kamera biasa + mesin kita | Murah untuk pembeli; bisa memakai CCTV yang ada; motor bisa dikuatkan | Jalan ke 99% masih panjang; risiko teknis tinggi |
| **C. Gabungan (saran agen)** | Aplikasi pengelolaan menjadi produk inti, dengan pembaca yang bisa dipilih: kamera ANPR jadi, UHF, atau mesin kita. Mesin kita diteruskan untuk motor dan kamera biasa | Bisa mulai menjual lebih cepat dengan kamera jadi, sambil mesin kita matang; pembeli memilih sesuai anggaran | Dua jalur yang harus dirawat |

**Langkah murah sebelum memutuskan lebih jauh:**
1. **Beli satu kamera ANPR jadi (≈ Rp 9 juta; keputusan owner) dan uji berdampingan** dengan mesin kita di gerbang owner, mobil
   dan motor, siang dan malam. Bila kamera jadi sudah 98% untuk plat Indonesia termasuk motor, tenaga dipindah ke aplikasi.
2. **Wawancarai 5–10 pengelola cluster atau pengurus RT, dan 3–5 pemasang CCTV.** Tanyakan berapa yang mereka bayar sekarang (RFID,
   satpam, aplikasi), masalah apa yang paling mengganggu, dan berapa mereka mau bayar per bulan.
3. **Minta penawaran resmi** dari 2–3 distributor (Hikvision, Dahua, integrator lokal) untuk satu gerbang cluster.

## 6b. Rancangan owner ditimbang ulang (17 Okt, sesudah jawaban owner)

Owner menolak kamera ANPR karena terlalu mahal untuk sasaran harganya. Jawabannya: "kamera ANPR ini terlalu mahal untuk mencapai
harga tersebut, sehingga belum menjadi pilihan". Rancangannya sendiri:
- **paket dijual Rp 8 juta, dengan modal sekitar Rp 5 juta** (untung sekitar Rp 3 juta);
- **isinya:** kamera CCTV 2K, ESP32 yang tersambung WiFi ke server kita, satu paket modul pagar elektrik, dan pemasangan.

Kekhawatiran owner: pencahayaan malam dan letak kamera.

**Rincian modal paket owner, dengan harga yang ditemukan:**

| Barang | Harga | Sumber |
|---|---|---|
| Kamera CCTV 3 MP (2K) luar ruang, PoE | Rp 0,83 juta (TP-Link VIGI C330, garansi 2 tahun) sampai sekitar Rp 2 juta (merek lain, temuan owner) | Bhinneka |
| ESP32 dengan relay | Rp 67 ribu (ESP32 saja, relay terpisah) sampai sekitar Rp 320 ribu (ESP32-S3 relay industri, USD 17,99) | Tokopedia, Waveshare |
| Mesin pagar geser | Rp 1,5–5,4 juta (mesin saja) | Riset 13 Okt |
| Pemasangan | CCTV Rp 100–380 ribu per titik; pemasangan pagar dihitung per survei oleh vendor | Riset 13 Okt |
| **Pembanding: pagar otomatis terpasang dari vendor lain** | **Rp 7,85–9 juta** (tanpa sensor), "mulai Rp 8,5 juta" | Riset 13 Okt |

**Bacaan agen:**
1. **Harga jual Rp 8 juta masuk akal dan menarik.** Pagar otomatis terpasang dari vendor lain sudah sekitar Rp 8–9 juta, tanpa
   kamera dan tanpa buka dengan plat. Paket owner bisa dijual sebagai "harga pagar otomatis biasa, sudah termasuk CCTV dan buka
   dengan plat".
2. **Modal Rp 5 juta hanya tercapai bila mesin pagar yang murah** (sekitar Rp 1,5–2,5 juta). Bila mesinnya Rp 5 juta, modal
   menjadi sekitar Rp 6,5–8 juta.
   - **Saran: dua varian.**
     - **Paket lengkap** untuk rumah yang belum punya pagar otomatis.
     - **Paket tambahan** untuk pagar otomatis yang sudah terpasang: kamera, ESP32, dan pemasangan, dengan modal sekitar
       Rp 1,5–2,5 juta. Pasar varian ini adalah semua rumah yang sudah memakai pagar otomatis.
   - Bila dijual lewat pemasang atau distributor (jalur K11), mereka juga butuh bagian dari untung.
3. **Server kita adalah biaya bulanan yang tidak berhenti.**
   - **Harga sewa:** Hostinger KVM 2 (2 CPU, 8 GB) sekitar USD 17–24.5 per bulan (≈ Rp 300–440 ribu).
   - **Video terus-menerus terlalu mahal:** mesin kita sekarang butuh kira-kira satu inti CPU per kamera, jadi satu server
     hanya cukup untuk sekitar 2 kamera.
   - **Server harus bekerja hanya saat ada kendaraan:** ESP32 atau kamera memberi tanda, lalu beberapa foto dikirim. Dengan begitu
     satu server bisa melayani ratusan rumah.
   - **Biaya server ditutup langganan bulanan kecil** per lokasi (K13). Penjualan sekali saja akan menggerus untung dari tahun ke
     tahun.
4. **Kekhawatiran malam benar, dan inilah risiko teknis terbesar.**
   - **Silau inframerah:** plat Indonesia memantulkan cahaya. Kamera CCTV biasa dengan lampu inframerah sering membuat plat putih
     menjadi silau di malam hari. Kamera ANPR mahal karena mengatur penyinaran khusus untuk plat.
   - **Penangkalnya yang murah:**
     - kamera dipasang dekat tempat kendaraan **berhenti**, sehingga plat besar dan tidak buram;
     - kecepatan rana diatur di malam hari (pedoman pemasang: sekitar 1/250–1/1000 detik untuk kendaraan yang bergerak; boleh
       lebih lambat bila kendaraan berhenti);
     - dipakai kamera "full color" dengan lampu putih, bukan hanya inframerah;
     - dicoba di lokasi.
   - **Pedoman pemasangan dari pemasang ANPR:** tinggi sekitar 1,8–3 m, jarak 5–10 m, sudut ke plat di bawah 30°, dan plat minimal
     sekitar 40–50 piksel tingginya. Angka 40–50 piksel ini sama dengan ukuran yang dipakai K40.
   - Semua ini bisa dibakukan menjadi **resep pemasangan**. Dengan resep itu, satu produk bisa dipasang berulang tanpa banyak
     penyesuaian (K1–K4 "jual massal").
5. **Koreksi kecil soal RFID.** RFID **kartu** memang harus berhenti dan menempel kartu. RFID **UHF dengan stiker kaca** dibaca
   dari 5–15 m tanpa berhenti (Rp 1,4–2,9 juta per pembaca).
   - **Keunggulan kita atas UHF:** tidak perlu stiker per kendaraan, tamu bisa didaftarkan lewat aplikasi, dan kameranya
     sekaligus CCTV yang merekam.
   - UHF tetap pesaing untuk pembeli yang hanya ingin "tidak berhenti".
6. **Ketergantungan internet.** Bila internet lokasi mati, pagar tidak terbuka dengan plat. Remote bawaan paket pagar tetap
   menjadi cadangan; ini sesuai aturan "ragu = tidak membuka".
7. **Data pribadi.** Foto berplat dikirim ke server kita, jadi kita menjadi pemroses data menurut UU PDP. Aturan pelaksananya
   (PP 33/2026) berlaku 16 Januari 2027. Perjanjian dengan pembeli dan aturan penyimpanan foto dibutuhkan sebelum dijual.

**Akibat untuk pekerjaan teknis:**
- **Mesin baca sendiri tetap dibutuhkan,** karena rancangan owner tidak memakai kamera ANPR.
- **Soal ujinya berubah menjadi lebih mudah:** kamera yang dipasang dengan resep, menghadap kendaraan yang berhenti. Video YouTube
  yang dipakai selama ini jauh lebih sulit.
- **Langkah paling berguna berikutnya:** satu kamera 3 MP dipasang di gerbang owner menurut resep, merekam siang dan malam, mobil
  dan motor (Fase 0B). Rekaman itu menjawab langsung kekhawatiran malam dan menunjukkan seberapa jauh mesin kita dari sasaran.

Sumber tambahan 17 Okt:
- https://bhinneka.com/tp-link-vigi-c330-3mp-outdoor-full-color-bullet-network-camera-4mm-sku3340842767
- https://www.tokopedia.com/aisyahrobot/iot-esp32-esp-32-module-wifi-bluetooth-type-c-ch340-bbad1
- https://www.waveshare.com/esp32-s3-relay-1ch.htm?sku=32152
- https://www.vpsbenchmarks.com/hosters/hostinger/plans/kvm-2
- https://videos.cctvcamerapros.com/v/lpr-anpr-camera-night.html
- https://home-security-guide.readthedocs.io/en/latest/cctv/17-anpr-camera-installation-guide-uk/
- https://cornick.helpjuice.com/619886-vsipnp-2birm-i-anpr-camera-setup

## 7. Yang belum diketahui

- Jumlah cluster bergerbang di Indonesia, dan berapa yang sudah memakai RFID.
- Kemauan membayar pengelola dan warga untuk sistem tanpa kartu. Belum ada survei.
- Akurasi kamera ANPR jadi pada plat Indonesia, terutama motor, plat dua baris, dan plat hitam lama. Tidak ditemukan uji
  independen.
- Harga komputer kecil N100 dalam Rupiah. Angka di atas masih perkiraan.

## Sumber utama

- Kamera ANPR, paket parkir, UHF, perangkat lunak, IPL, gaji, dan hukum: riset 13 Okt
  ([`2026-10-13-catatan-pasar-dan-harga-gerbang-plat.md`](2026-10-13-catatan-pasar-dan-harga-gerbang-plat.md)), dengan tautan per
  angka.
- Pencarian ulang 17 Okt:
  - Hikvision DS-TCG406-E di Bhinneka: https://bhinneka.com/hikvision-4mp-access-anpr-camera-2-8-to-12-mm-ds-tcg406-e-sku3341767856
  - Paket perangkat lunak parkir + kamera LPR, Nale: https://kerinci.nale.co.id/produk/software-parkir-cashless-camera-lpr
  - Paket palang + RFID, Tokopedia: https://www.tokopedia.com/solusi-parking/paket-barrier-gate-1-mesin-e10-ac-dan-2-rfid
  - Kamera CCTV IP Hikvision, Tokopedia: https://www.tokopedia.com/find/kamera-cctv-ip-hikvision
  - Kamera ANPR membuka palang tanpa server: https://apsardze24.lv/en/produkti/hikvision-ids-2cd7a46g2-p-izhsy-4mp-anpr-smart-ip-camera-2-8-12mm-lens-deepinview-lpr/
  - Harga Plate Recognizer: https://platerecognizer.com/pricing/
  - UMP Jakarta 2026: https://databoks.katadata.co.id/en/employment/statistics/695206d6675b6/indonesias-2026-provincial-minimum-wage-highest-in-jakarta
  - Mini PC N100 (USD): https://www.cnx-software.com/2023/03/01/intel-processor-n100-mini-pc-8gb-lpddr5-memory-low-cost/
