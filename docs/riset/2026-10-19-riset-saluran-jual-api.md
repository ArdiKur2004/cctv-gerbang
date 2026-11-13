# Menjual API baca plat dan ciri kendaraan di Indonesia: saluran, pesaing, syarat, dan server di rumah (19 Okt 2026)

> **Hanya baca.** Disusun agen riset atas pertanyaan owner ("di mana saya bisa jualan API tersebut, terutama market Indonesia"), dengan rencana
> owner: sekitar Rp 3 per panggilan, server Mini PC sendiri di rumah, persetujuan pelanggan lewat formulir, data tidak langsung dipakai
> melatih, dan pemakaian dibatasi. Tidak ada akun yang didaftarkan.
>
> **Diperiksa ulang agen utama (19 Okt), semuanya cocok:**
> - harga Plate Recognizer Snapshot (gratis 2.500 per bulan; $50 untuk 50 ribu; $150 untuk 250 ribu; $250 untuk 500 ribu; merek, model, dan
>   warna +50%; Stream $35 per kamera, $45 dengan merek, model, dan warna);
> - potongan Rapid 25% sejak 15 Nov 2025, dibayar hanya lewat PayPal pada akhir bulan berikutnya;
> - syarat IndiHome: melarang "penjualan kembali (reselling) sebagian Layanan ... tanpa izin tertulis" dan "perubahan terhadap Jaringan termasuk
>   tunneling", dan Telkomsel berhak mengelola serta mengubah IP.
>
> Klaim lain belum diperiksa ulang (bagian 7). Kurs yang dipakai Rp 17.973 per USD (JISDOR 24 Juli 2026, dari hasil pencarian).

## 1. Ringkasan

- **Jual dulu dari situs sendiri dengan saldo prabayar**, isi saldo lewat QRIS atau VA (misalnya Winpay yang sudah owner pakai). Tidak ada
  komisi marketplace, harga dalam rupiah, dan harga kecil seperti Rp 3 bisa dipakai. QRIS (0,7%) jauh lebih murah dari VA (Rp 4.000) untuk isi
  saldo kecil.
- **Pembeli pertama yang realistis: pemasang CCTV atau gerbang dan pengembang kecil**, bukan operator parkir besar. Secure Parking, Parkee, dan
  Telkom (Antares Eazy) sudah punya baca plat sendiri; SPBU dan tol berjalan lewat proyek pemerintah.
- **Rp 3 per panggilan lebih murah dari semua harga publik yang ditemukan.** Paket termurah Plate Recognizer setara sekitar Rp 9 per panggilan.
  Tetapi pada Rp 3, satu gerbang dengan 300 kendaraan per hari hanya menghasilkan sekitar Rp 27 ribu per bulan; untuk pemasang gerbang, harga
  tetap per gerbang mungkin lebih masuk akal.
- **Marketplace cukup sebagai etalase kedua.** Rapid memotong 25% dan hanya membayar lewat PayPal; AWS Marketplace tidak menerima penjual dari
  Indonesia untuk produk berbayar.
- **Sebelum menarik uang:** NIB dengan KBLI yang tepat, TD-PSE Lingkup Privat (gratis lewat OSS), kebijakan privasi, dan perjanjian pemrosesan
  data. PP 33/2026 (aturan teknis UU PDP) berlaku penuh 16 Jan 2027.
- **Server di rumah cukup untuk masa uji gratis**; pindah ke VPS saat pelanggan berbayar pertama butuh layanan yang selalu hidup. Syarat IndiHome
  melarang penjualan kembali tanpa izin tertulis dan "tunneling".

## 2. Saluran jual

| Saluran | Cocok untuk | Biaya atau komisi | Kelebihan | Kekurangan | Sumber |
|---|---|---|---|---|---|
| Situs sendiri + Winpay | Semua, terutama pembeli kecil | VA Rp 4.000; QRIS 0,7%; e-wallet 0,5–3%; kartu 2,2% + Rp 2.000; tanpa biaya aktivasi atau bulanan | Sudah dipakai owner; rupiah; tanpa komisi | Tagihan otomatis berulang dan status PPN tidak disebut | winpay.id/daftar-harga |
| Situs sendiri + Midtrans | Sama | VA Rp 4.000; QRIS 0,7%; GoPay/ShopeePay 2%; kartu 2,9% + Rp 2.000 | Tagihan berulang tersedia | Belum dipakai owner | midtrans.com/id/pricing |
| Situs sendiri + DOKU | Sama | VA Rp 4.000 (BCA Rp 4.500); QRIS 0,7%; direct debit 2% + Rp 2.000 (belum termasuk PPN) | Debit otomatis untuk langganan | Rincian fitur langganan tidak jelas | doku.com/pricing |
| Situs sendiri + Xendit | Sama | VA Rp 4.000; QRIS 0,63–0,7%; kartu 2,9% + Rp 2.000; Subscriptions Rp 2.500 per paket aktif per bulan | Tagihan sesuai pemakaian | Halaman resmi menolak dibuka; angka dari ringkasan | help.xendit.co |
| Mayar | Mulai cepat tanpa membuat sistem bayar | 4% (paket Rp 0) atau 3% (Rp 349 ribu per bulan) ditambah biaya kanal | Ada membership/SaaS | Potongan lebih besar | mayar.id/pricing |
| Rapid (dulu RapidAPI) | Pengembang luar negeri | 25% + biaya PayPal | Banyak pengunjung | USD; potongan besar; hanya PayPal | docs.rapidapi.com |
| Zyla API Hub | Pengembang luar negeri | Owner menerima 80% | Potongan lebih kecil | Pasar kecil | help.zylalabs.com |
| AWS Marketplace | Perusahaan besar | 3% (SaaS) | Pembeli besar | Indonesia tidak ada di daftar negara penjual produk berbayar | docs.aws.amazon.com/marketplace |
| Marketplace API Indonesia | — | — | — | Tidak ditemukan | — |
| Distributor dan pemasang CCTV | Paket gerbang dan API | Bagi hasil | Langsung ke pemasang | Perlu tatap muka | Distributor Hikvision (situs resmi), HiLook, Dahua |
| Gerbang dan aplikasi perumahan | Cluster | Dirundingkan | Sasaran sama dengan paket owner | Bisa menjadi pesaing | ZCluster (palang + aplikasi Rp 10–40 juta), OmahKu |
| Operator parkir | Lebih cocok sebagai pesaing | — | Volume besar | Sudah punya baca plat sendiri | Secure Parking Epsilon, Parkee–Alfabeta, asosiasi PPPI |
| Logistik dan armada | Nanti | Dirundingkan | Baru sekitar 2% dari 62 juta kendaraan komersial terhubung ke sistem armada | Butuh integrasi | Geotab, TransTRACK.ID |
| SPBU dan tol | Bukan untuk awal | Tender | Volume besar | Proyek pemerintah | ESDM (CCTV SPBU dengan Telkom), MLFF Roatex |
| Komunitas pengembang | Pengenalan dan uji gratis | Gratis atau sponsor | Murah | Belum tentu membayar | Dicoding, komunitas ESP32 |

## 3. Pesaing dan harga

| Pesaing | Model | Harga publik | Setara per panggilan |
|---|---|---|---|
| Plate Recognizer Snapshot (mendukung plat Indonesia) | API awan | Gratis 2.500 per bulan; $50 untuk 50 ribu; $150 untuk 250 ribu; $250 untuk 500 ribu; merek/model/warna +50% | Rp 18 / 11 / 9; dengan merek/model/warna sekitar Rp 13,5 |
| Plate Recognizer Stream | Per kamera | $35 per kamera per bulan; $45 dengan merek/model/warna | Sekitar Rp 629 ribu / Rp 809 ribu per kamera per bulan |
| Rekor CarCheck | API awan | $40 untuk 2.500; $125 untuk 25 ribu; $510 untuk 125 ribu | Rp 288 / 90 / 73 |
| Google Cloud Vision (teks umum) | API | 1.000 gratis; $1,50 per 1.000 | Rp 27 |
| AWS Rekognition DetectText (teks umum) | API | $0,001 per gambar | Rp 18 |
| Nodeflux VisionAIre (Indonesia) | Di server pelanggan | Tidak dipublikasikan | — |
| GLAIR Vision (Jakarta) | API plat Indonesia | Tidak dipublikasikan | — |
| Telkom Antares Eazy | CCTV awan dengan baca plat | Tidak dipublikasikan | — |

## 4. Syarat legal, dari yang paling wajib

1. **NIB dengan KBLI yang cocok** (KBLI 2025 berlaku sejak 18 Juni 2026; calon kode 62010 untuk perangkat lunak/SaaS dan 63102 untuk pengolahan
   data/hosting; kode final dan tingkat risiko dicek di OSS).
2. **TD-PSE Lingkup Privat** (Permenkominfo 5/2020 jo. 10/2021): wajib sebelum sistem dipakai pengguna; lewat OSS tanpa biaya resmi; sanksi bila
   tidak mendaftar: akses diblokir.
3. **UU PDP 27/2022 dan PP 33/2026:** saat memproses foto pelanggan, owner adalah prosesor (Pasal 51); kewajiban keamanan berlaku (Pasal 52);
   subprosesor (misalnya Cloudflare) butuh persetujuan tertulis pengendali; memproses di luar perintah, misalnya melatih model, menjadi tanggung
   jawab owner sendiri, jadi formulir persetujuan owner memang diperlukan; perjanjian pemrosesan tertulis; DPIA untuk pemantauan sistematis;
   pemberitahuan kebocoran paling lambat 3×24 jam (Pasal 46); denda maksimal 2% dari pendapatan tahunan.
4. **Pajak:** orang pribadi dengan omzet sampai Rp 500 juta per tahun bebas PPh, di atasnya PPh final 0,5% sampai Rp 4,8 miliar (PP 20/2026);
   PPN wajib dipungut bila omzet di atas Rp 4,8 miliar; pelanggan perusahaan sering meminta faktur pajak, jadi PKP sukarela bisa dipertimbangkan.
5. **Aturan lisensi proyek** (`CLAUDE.md` §5): API hanya memakai komponen `BOLEH-PRODUK`.

## 5. Server di rumah, dan kapan pindah ke VPS

- **Syarat ISP:** IndiHome melarang penjualan kembali tanpa izin tertulis dan "perubahan terhadap Jaringan termasuk tunneling" (diperiksa ulang).
  Syarat ISP lain belum ditemukan. Tanyakan tertulis ke ISP owner sebelum menerima pembayaran.
- **IP:** ISP berhak mengubah IP. Terowongan seperti Cloudflare Tunnel tidak butuh IP publik, tetapi menyentuh klausul "tunneling" di atas, dan
  Cloudflare menjadi subprosesor data pribadi.
- **Listrik dan internet:** rata-rata pelanggan PLN padam 3,23 kali pada 2025 (di luar Jawa sekitar dua kali lipat); perlu UPS; internet rumah
  tetap satu titik gagal; ada kuota pemakaian wajar (contoh 2024: 300 GB untuk paket 10 Mbps; 1 juta foto 200 KB sekitar 200 GB).
- **Keamanan:** foto berplat adalah data pribadi di rumah; perlu jaringan terpisah dari perangkat keluarga, tanpa membuka port, dan penyimpanan
  terenkripsi.
- **Pindah ke VPS bila:** pelanggan berbayar meminta jaminan layanan hidup, ISP tidak memberi izin tertulis, pemakaian mendekati kuota atau batas
  Mini PC, atau gangguan mengenai pelanggan lebih dari sekali sebulan. Hostinger KVM 2 sekitar $16,99–24,49 per bulan (sumber pihak ketiga), ada
  lokasi Jakarta. Pilihan tengah: kunci API dan pembayaran di VPS, mesin baca di Mini PC.

## 6. Usulan langkah awal

1. Tanyakan tertulis ke ISP: bolehkah menjalankan layanan berbayar dan terowongan. Putuskan penjualnya: perorangan atau PT (pajaknya berbeda).
2. Perbarui NIB dengan KBLI 2025, daftar TD-PSE, dan siapkan kebijakan privasi, syarat layanan, dan contoh perjanjian pemrosesan.
3. Halaman API dengan saldo prabayar lewat Winpay (QRIS untuk isi saldo kecil), kuota gratis kecil, batas per kunci API, dan definisi
   "1 panggilan = 1 foto".
4. Uji gratis dengan 3–5 pemasang CCTV atau gerbang: ukur panggilan per gerbang yang sebenarnya, lalu putuskan harga per panggilan atau harga tetap
   per gerbang.
5. Sesudah stabil: etalase di Rapid atau Zyla, dan pindah ke VPS saat pelanggan berbayar pertama datang.

## 7. Klaim yang belum terverifikasi

- Tarif Xendit dan biaya Subscriptions (halaman resmi 403); apakah tarif Winpay termasuk PPN dan mendukung tagihan berulang.
- Kode KBLI 2025 dan tingkat risikonya; apakah perorangan bisa mendaftar TD-PSE.
- Rincian PP 33/2026 dan PP 20/2026 (dari artikel, teks resmi belum dibaca).
- Syarat ISP selain IndiHome; harga IP statis; angka kuota pemakaian wajar terbaru; batas dan lokasi lalu lintas Cloudflare.
- Kurs USD dari data Juli; harga Hostinger dari pihak ketiga; sebagian daftar mitra sudah lama (2017–2018).
- Akurasi pesaing pada plat Indonesia belum diuji. Status nomor plat sebagai data pribadi mengikuti aturan proyek, belum ada pendapat ahli hukum.
- Tidak ditemukan marketplace API Indonesia, tetapi bukan berarti pasti tidak ada.

**Sumber utama:** winpay.id/daftar-harga · midtrans.com/id/pricing · doku.com/pricing · help.xendit.co · mayar.id/pricing ·
docs.rapidapi.com/docs/payouts-and-finance · help.zylalabs.com · docs.aws.amazon.com/marketplace/latest/userguide/seller-eligibility.html ·
platerecognizer.com/pricing · rekor.ai/developers/carcheck · cloud.google.com/vision/pricing · aws.amazon.com/rekognition/pricing ·
nodeflux.ai · docs.glair.ai/vision/plate · telkomsel.com/indihome/syarat-ketentuan · developers.cloudflare.com · pasal.id (UU 27/2022 Pasal 46,
51) · pajak.go.id · databoks.katadata.co.id · hikvision.com/id/Partners.
