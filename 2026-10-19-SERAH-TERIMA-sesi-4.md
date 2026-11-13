# SERAH TERIMA — ke sesi berikutnya (ditulis 19 Okt 2026, mencakup 13–19 Okt: Fase 0A, Fase 1, Rencana 1–25, K1–K50)

> Bila berbeda dengan `ROADMAP.md`, **yang berlaku ROADMAP**: butir "Status" dan changelog-nya. Berkas ini menggantikan
> `2026-10-14-SERAH-TERIMA-sesi-3.md`, yang hanya sampai Rencana 5. Isi lama yang masih berlaku dibawa ke sini.

## 1. Posisi dalam satu paragraf

**Produk.** Kamera CCTV membaca plat nomor, lalu gerbang membuka untuk kendaraan terdaftar. Produk ini dijual massal di Indonesia. Arah
paket (K42): Rp 8 juta, berisi CCTV 2K, ESP32 ke server kita, modul pagar, dan pemasangan; baca plat di server IBE (K25, K29).

**Fase.** Fase 0A selesai (laporan `bukti/2026-10-16-laporan-fase-0a.md`). **Fase 1** (S1, mesin baca plat; spec
`specs/2026-10-16-fase-1-mesin-baca-plat.md`, K38) sedang berjalan.

**Rantai sekarang:**
1. kendaraan dicari (YOLOX-Tiny COCO, ambang 0,25; K39);
2. plat dicari di dalam potongan kendaraan (cctv1, YOLOX-Nano-640, ambang 0,25, `--cara potong`);
3. plat dibaca (fpo-indo-1 ONNX);
4. bacaan digabung per kedatangan (`MIN_SETUJU` 2, `BAGIAN_SETUJU` 0,6).

**Izin.** Sejak K44, K47, K48, dan K49, **semua bahan rantai `BOLEH-PRODUK`**. Arah sekarang (K50): **optimalkan yang sudah ada dengan
data owner, bukan mulai dari nol.** **Rencana 25 sudah ditulis dan belum dijalankan.**

## 2. Yang dikerjakan berikutnya, persis

1. Jalankan `plans/2026-10-19-fase-1-rencana-25-optimalkan.md` task demi task. Mandiri (K37, K50): tidak perlu lampu hijau lagi. Berhenti
   di Task 7 Step 3 dengan laporan per bagian: kendaraan, plat, dan baca.
2. Menunggu owner, tidak mendesak:
   - **butir 42** halaman pelabelan (satu kotak plat belum ditarik). Bila owner mengunduh ulang, berkas terbaru di Downloads disalin ke
     `data/capture/label-tangkapan.json` tanpa dibuka, lalu jalankan `halaman_label.py terima`;
   - **6 baris Rencana 23** (19, 30, 42, 58, 65, 94) di `data/keluaran/lembar-uji-fase1-r23b-v1`.

## 3. Urutan baca

1. `ROADMAP.md` sampai habis: status, butir, temuan di luar lingkup, dan changelog beralasan.
2. Berkas ini.
3. `SEED.md`:
   - §3, K1–K50 dengan kata-kata owner dan cara membaliknya. Bagian ini mengikat; ringkasannya ada di §5 di bawah.
   - §6, usulan agen; U6 sudah diubah K46.
4. `OPEN-QUESTIONS.md`: bagian A (P1–P17) dan paragraf "Sesudah …" di bagian B.
5. `CLAUDE.md`: aturan proyek, terutama §3 (K46), §4, §5 (K47–K49), dan §7.
6. `plans/2026-10-19-fase-1-rencana-25-optimalkan.md`, lalu `plans/2026-10-18-fase-1-rencana-24-mesin-jualan.md` (Bagian B ditutup
   sebagian).
7. `bukti/2026-10-18-tangkapan-owner.md`, dan bila perlu riwayat angka, `bukti/2026-10-16-laporan-fase-0a.md`.

## 4. Riwayat ringkas (angka dari butir status ROADMAP; rinciannya di `bukti/`)

**Fase 0A (13–16 Okt):**
- **Rencana 1–3:** alat bengkel dan pintu Docker; 100 video riset YouTube (K17, K20).
- **Rencana 4:** INDO-ALPR (6.174 potongan plat) dan plat-lighting (561 foto adegan), keduanya berizin jual.
- **Rencana 5–7:** set uji baca huruf 937 plat, labelnya dibetulkan (K22, K23); bahan latih 2.824 plat dibersihkan (K24). Pembanding
  Qwen3-VL 66–70%, fast-plate-ocr 62–80%.
- **Rencana 8:** mesin baca buatan sendiri dari nol, 26–32%. Bahannya terlalu sedikit untuk belajar dari nol.
- **Rencana 9–11:** fast-plate-ocr dilatih ulang menjadi **fpo-indo-1**, 79–86% per kelompok (K26). Versi ONNX-nya sekitar 23 ms per
  plat dengan 1 inti CPU.
- **Rencana 12–13:** di Mini PC, pembanding siap pakai hanya menemukan 30% plat. Empat pencari YOLOX buatan sendiri menemukan 89–94%
  (K30); **Nano-640** dipakai di rantai (K31). Di Mini PC, Nano-640 sekitar 150 ms per foto.
- **Rencana 14–15:** rantai utuh di 30 video riset, dinilai dari lembar owner (K32). Hasilnya 99 dari 120 baris bukan plat, dan 7 dari 10
  "yakin" bukan plat. Lalu laporan Fase 0A (K33), lanjut ke Fase 1 (K34), dan plat buatan (K35).

**Fase 1 (16–19 Okt):** K36 (tolok ukur video CCTV daring), K37 (agen mandiri), K38 (spec disetujui).
- **Rencana 16, 18, 17:**
  - 77 video CCTV baru;
  - plat buatan dengan huruf digambar sendiri (fpo-indo-1 membaca 48% tanpa latihan);
  - titik awal di set uji CCTV: 105 dari 120 baris bukan plat.
- **K39, lalu Rencana 19:** tahap kendaraan menurunkan bukan plat dari 105 ke 6. Tetapi pencari yang dilatih ulang, **cctv1**,
  melewatkan plat di 12 dari 13 bingkai.
- **K40, lalu Rencana 20:** plat dicari *di dalam* potongan kendaraan. Lebih banyak plat ditemukan, tetapi bukan plat kembali (46 dari 120).
- **Rencana 21:** saringan letak plat tidak menolong, jadi tidak dijadikan bawaan.
- **K41, lalu Rencana 22:** gelombang keempat; set uji 77 video, latih 68. Pembagiannya per SHA-256 dan tidak boleh diubah.
- **Rencana 23:**
  - Bagian A, titik awal 77 video uji: mobil 11 dari 16 benar-yakin, motor 3 dari 8;
  - analisa bisnis, lalu K42 dan K43;
  - Bagian B: gambar paling tajam (V1) +2 di sisi latih, sama di sisi uji; 6 baris menunggu owner; pembaca salah 27 dari 52 plat CCTV.
- **K44, lalu Rencana 24:**
  - 181 tangkapan owner dibaca dan diberi label lewat dua lembar dan **halaman pelabelan**: 180 kotak dan 159 teks;
  - pembaca benar 98 dari 126 plat yang ditemukan;
  - plat terlewat di 9 dari 74 gambar mobil dan 34 dari 103 motor;
  - K45, K46.
  - Bagian B, mesin dari nol sebagai cadangan:
    - pembaca P3 65% dan P2 60% di validasi (fpo-indo-1 83%, mesin-baca-1 30%);
    - pencari D1 F1 0,845 (cctv1 0,92).
- **K47–K50, lalu Rencana 25:** ditulis 19 Okt.

## 5. Keputusan owner K1–K50 (satu baris; kata-kata owner dan cara membalik ada di `SEED.md` §3)

| K | Isi |
|---|---|
| K1–K3 | Produk harus image processing; yang digarap CCTV gerbang plat (bukan QC pabrik); workspace `cctvgerbang-seed` |
| K4, K10, K11 | Empat kelompok pembeli; perumahan dan gudang/pabrik/kantor lebih dulu; empat jalur jual |
| K5, K6 | Lokasi uji milik owner lalu kenalan, belum ada; perangkat uji tidak dibeli sekarang, semua di laptop |
| K7, K8, K9 | Motor dibaca sejak awal; ciri kendaraan sampai nama model, bertahap; sasaran gagal-buka 99% per kelompok, buka-salah nol |
| K12, K13 | Menyambung ke motor gerbang yang ada (terbuka menjual motor sendiri); harga menurut pembeli (Rp 5.000/bulan untuk perorangan) |
| K14 | Repo mandiri; vision-seed tidak diubah |
| K15, K21 | Bahan riset-saja boleh untuk belajar; bahan internet boleh melatih model yang dijual bila sumbernya tidak melarang |
| K16, K18 | Mesin baca buatan sendiri yang bertingkat; spec induk disetujui |
| K17, K19, K20 | Video riset diunduh agen; agen hanya melihat gambar kecil buram sesudah owner; gelombang kedua diarahkan |
| K22, K23, K24 | Label set uji dibetulkan lewat yang dicurigai; plat kembar lintas sisi dikeluarkan; bahan latih dibersihkan dulu |
| K25, K29 | Baca plat di server IBE; server bertahap: Mini PC, lalu Hostinger KVM 2–8, tanpa kartu grafis |
| K26, K27 | Pembaca dari fast-plate-ocr yang dilatih ulang; draf izin disetujui, owner mengirim sendiri |
| K28, K30, K31 | Urutan sesudah Rencana 10; YOLOX-Nano dan Tiny dilatih; Nano-640 dipakai di rantai |
| K32, K33 | Rantai dinilai dari lembar owner; lalu laporan Fase 0A |
| K34, K35 | Lanjut ke Fase 1 tanpa Fase 0B; plat buatan di awal Fase 1, huruf digambar sendiri |
| K36, K37, K38 | Tolok ukur Fase 1 video CCTV daring; agen bekerja mandiri; spec Fase 1 disetujui |
| K39, K40, K41 | Kendaraan dicari lebih dulu; resolusi dan jarak menjadi parameter; tambah video CCTV dari internet |
| K42, K43 | Paket Rp 8 juta tanpa kamera ANPR; mesin dulu, lalu uji dengan HP owner dan CCTV kantor |
| K44 | 181 tangkapan owner boleh melatih mesin jualan (izin dijamin owner) |
| K45 | Kendaraan terdekat dibaca lebih dulu |
| K46 | Bacaan ragu pada 1–2 posisi diloloskan bila tidak ada plat berstatus sama yang cocok; bila ada, satpam dipanggil; menurut lokasi (perumahan: hanya bila cocok tepat satu plat penghuni) |
| K47 | Bobot fast-plate-ocr boleh dijual (pernyataan pemelihara di GitHub), selama repo aman |
| K48 | Bobot YOLOX COCO boleh dijual bila dimodifikasi (risiko hukum dicatat: UU 28/2014 Pasal 9, disarankan ahli hukum bersama B9) |
| K49 | Video riset boleh dijual (izin verbal, menurut owner) |
| K50 | Optimalkan yang sudah ada: YOLOX COCO untuk kendaraan, cctv1 + data owner untuk plat, fpo-indo-1 + contoh CCTV owner untuk baca |

## 6. Cara kita bekerja dan sampai pada kesimpulan

**Alur keputusan.**
- Agen bertanya satu per satu: pilihan ganda, saran di urutan pertama beserta akibatnya.
- Jawaban owner dicatat di tiga tempat, lalu di-commit lokal:
  - `SEED.md` §3, dengan kata-kata owner apa adanya, bacaan agen, dan cara membaliknya;
  - `OPEN-QUESTIONS.md`;
  - `ROADMAP.md`, sebagai baris changelog yang memuat **alasan**.
- Keputusan yang mengubah keputusan lama diberi catatan di setiap aturan yang bersandar padanya. Contohnya K46 mengubah U6 dan
  `CLAUDE.md` §3, dan K47–K49 mengubah vonis bahan. Teks lama dicoret, tidak dihapus.
- Keputusan tentang **apa yang dijual, keselamatan gerbang, data pribadi, dan uang** selalu milik owner. Agen memberi fakta dan angka,
  menyampaikan risikonya sekali dengan jujur, lalu mencatat keputusan owner sebagai keputusan yang bisa dibalik. Contoh: K48 dan risiko
  hukumnya.

**Alur membangun.**
- Rencana kecil yang lengkap: berkas, uji, angka yang diharapkan, dan **aturan memilih yang ditulis sebelum angka dilihat**.
- TDD: uji terlihat merah *karena fiturnya belum ada*, lalu hijau, lalu gerbang penuh, lalu commit beralasan.
- Uji yang mengunci kebenaran usang **dibalik**, bukan dihapus (K47, K48, K49), dan merahnya dibuktikan terhadap keadaan lama.
- Laporan ke owner memuat angka sebelum dan sesudah, beserta batasnya.

**Cara menilai (lahir di Fase 0A dan 1; wajib).**
- **Agen tidak pernah melihat plat.** Owner memeriksa lembar di laptop dan menjawab dengan nomor baris per jenis.
  - Lembar kedatangan (`lembar_rantai.py`): 120 baris, urut SHA, jenisnya salah, tak terbaca, bukan plat, dan motor.
  - Lembar bingkai (`lembar_bingkai.py`): satu bingkai per video uji, jenisnya plat terlewat yang terbaca, yang buram, dan yang benar.
  - Lembar kendaraan bernomor (`lembar_kendaraan.py`).
  - Halaman pelabelan (`halaman_label.py`): owner menarik kotak dan mengetik teks.
- **Baris yang tidak disebut owner tidak otomatis "benar".** Owner pernah mengoreksi ini (Rencana 21), jadi tanyakan secara eksplisit.
- **Label dikunci dan dipakai ulang antarjalan.** Hanya baris yang teksnya berubah yang ditanyakan lagi. Penilaian owner atas bingkai yang
  sama bisa berbeda antarputaran, jadi jangan meminta penilaian ulang yang tidak perlu.
- **Label yang bertentangan** diselesaikan dengan pilihan yang paling merugikan angka kita, dicatat, dan bisa dibalik.
- **Memilih hanya di sisi latih atau validasi. Set uji diukur sekali.** Pembagian video per SHA-256 (`data-asal/pembagian-video-fase1.json`)
  tidak pernah diubah. Tangkapan dibagi per isi berkas.
- **Angka dilaporkan dengan rentang Wilson 95%.** Kelompok kecil ditandai "terlalu sedikit".
- **Penilai otomatis** `halaman_label.py nilai` dipakai bila label tangkapan sudah ada. Gambar dicocokkan lewat jalur berkas, bukan nomor.
- **Hitungan skrip dicocokkan dengan alat resmi** sebelum dipakai. Satu skrip pernah menghitung dua kali: 252, padahal 126.
- **Pemeriksa yang melapor "0 ditemukan" diuji dengan kontrol positif.** Kontrol merah juga diperiksa: dengan `git diff`, pastikan berkasnya
  memang berubah.

**Aturan bukti.**
- Catatan bukan bukti. Angka dibaca dari sumber, tidak disalin dari ingatan.
- Kode keluar bukan 0 belum tentu uji merah: kode 3 berarti bengkel sibuk; kode 6 berarti image tidak sesuai kunci *atau* Docker Desktop
  belum menyala.
- Angka dari tangkapan atau video internet tidak pernah dilaporkan sebagai "K9 tercapai".
- Temuan di luar lingkup dicatat di ROADMAP. Cacat sepupu dicari.

**Data pribadi.**
- Nomor plat tidak keluar dari laptop. Agen tidak membuka gambar, potongan, lembar, `kedatangan.jsonl`, `bacaan.jsonl`, `label.json`,
  `butir.json`, `peta-berkas.json`, CSV pembaca, atau `pembagian*.json`.
- Agen tidak mencetak nama berkas INDO-ALPR atau nama berkas tangkapan.
- Alat hanya mencetak hitungan. Galat hanya mencetak jenisnya, dan log OpenCV dibisukan.
- Contoh nomor plat yang ditulis owner tidak disalin ke berkas mana pun.

**Pencatatan.**
- Skrip pencatat sekali pakai ditulis sebagai berkas di `data/alat-sementara`, dengan teks di berkas `catatan-*.txt`. Tiap jangkar harus
  ketemu **tepat sekali** sebelum apa pun ditulis.
- Untuk berkas JSON yang formatnya harus tetap, seperti `vendor.lock.json`, penggantian dilakukan sebagai teks.
- `ROADMAP.md` hanya diubah lewat changelog.
- Commit berbahasa Indonesia, memuat alasan, ditulis lewat `git commit -F <berkas>`, dan diakhiri
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Tidak ada push.

## 7. Cara berbicara dengan owner

- Owner bukan orang teknis. Bahasa Indonesia sehari-hari, kalimat pendek, analogi. Analogi yang berhasil: "tiga petugas gerbang", yaitu
  mata yang melihat kendaraan, mata yang mencari plat, dan yang membaca huruf.
- Tiap permintaan ke owner berdiri sendiri: apa yang diminta, pilihannya, dan akibatnya, di awal pesan.
- Satu pertanyaan per giliran. Owner tidak suka ditanya berulang tentang hal yang sudah diputuskannya.
- Owner sering mengusulkan ide produk, misalnya analitik kendaraan atau scan cepat/normal. Ide itu dicatat, diuji dengan data bila
  bisa, dan yang berisiko hukum atau diskriminatif disampaikan jujur. Contoh: "pickup = maling" ditolak karena UU PDP Pasal 10.
- Owner peduli biaya token dan pemakaian laptop. Pelatihan tidak memakai token, dan boleh berjalan selama owner memakai laptop.
- Jawaban singkat atas laporan yang memuat bacaan agen dicatat sebagai "tidak dikoreksi", bukan keputusan baru.
- Uang selalu keputusan owner.

## 8. Mesin dan alat

**Gerbang uji (terakhir):** `npm test` 120, `npm run test:lab` 289, dan image tambahan `uji_fpo` 34. Satu suite pada satu waktu; tanpa
`| tail` atau `| head`.

**Kunci bengkel** (`Global\vision-seed-bengkel`, dipakai bersama vision-seed):
- dipegang tiap job lab, **termasuk pelatihan berjam-jam**;
- selama itu uji lab, dan dua uji `lab.test.mjs` di `npm test`, menunggu 30 menit lalu kode 3 atau gagal. Itu bukan merah;
- jalankan gerbang di antara pelatihan, dan buktikan merah dengan `git stash` atau dengan menyingkirkan modul baru.

**GPU:**
- RTX 4060 8 GB.
- Antrean latih memakai penjaga sisa memori ≥ 4 GB (`data/alat-sementara/antrean-24d.ps1`), karena owner boleh memakai laptop.
- Laju: fast-plate-ocr sekitar 15,3 detik per 1.000 gambar per zaman; YOLOX-Nano-640 sekitar 25 detik per zaman untuk 500 gambar.

**Perangkap perintah:**
- `powershell -File` menolak argumen `-`;
- `^` di `cmd` adalah karakter escape;
- `JSON.stringify` mengubah format berkas;
- tanda kutip ganda di argumen `git commit -m` pecah di PS 5.1;
- `String.Split(string)` di PS 5.1 memecah per huruf;
- Git Bash mengubah `/kerja/...`, jadi perintah lab dijalankan lewat PowerShell;
- Docker Desktop (`D:\Docker\Docker Desktop.exe`) tidak menyala sendiri.

**Alat utama:**

| Bagian | Alat |
|---|---|
| Rantai | `rantai.py` (`--kendaraan`, `--cara`, `--letak`, `--simpan-bacaan`, `--pembagian --sisi`), `kendaraan.py`, `letak.py`, `gabung_varian.py` |
| Gambar diam | `baca_gambar.py` (`jalan`, `lembar-tanpa`, `--tanpa-kendaraan`, `--pembaca-jualan`) |
| Label dan penilaian | `halaman_label.py` (`buat`, `terima`, `nilai`), `lembar_rantai.py`, `lembar_bingkai.py`, `lembar_kendaraan.py`, `lembar_kecil.py` |
| Melatih | `latih_fpo.py` (`latih`, `latih-jualan`, `PembacaKeras.dengan_yakin` dan `.rincian`), `onnx_fpo.py`, `latih_yolox.py` (`--dari-nol`, `--nama`, `--bahan`, `ekspor`), `bahan_pembaca.py`, `dataset_jualan.py`, `dataset_cctv.py`, `plat_buatan.py` |
| Bahan dan izin | `tools/bahan.mjs periksa`, `tools/periksa-jualan.mjs <mesin.json>` |

## 9. Bahan dan mesin yang ada

**Daftar bahan.** `data-asal/bahan.json` mencatat 13 bahan: 7 `BOLEH-PRODUK`, 0 `RISET-SAJA`, dan 6 `BELUM-JELAS`. Yang `BELUM-JELAS`
adalah bobot alat lab yang tidak dipakai rantai.

**Bahan:**
- **Video riset:** 259 video (`data/video/riset`, manifes `data-asal/video-riset.json`), dengan pembagian Fase 1: uji 77, latih 68.
- **Dataset:** INDO-ALPR (`dataset/indo-alpr/original`, pembagian `latih-koreksi/pembagian-koreksi.json`: uji 937, latih 2.824) dan
  plat-lighting.
- **Tangkapan owner:** `data/capture`.
- **Label dan keluaran:** `label-tangkapan/label.json`, `tangkapan-owner-baca/`, `lembar-tangkapan-*`, `lembar-uji-fase1-*`, dan
  `rantai-*`.
- **Dataset turunan:** `dataset/cctv-fase1` (dataset cctv1, termasuk 225 gambar video tanpa kotak) dan `dataset/jualan-d1`.
- **Plat buatan:** `plat-buatan-4k`, `-10k`, dan `-30k`.

**Mesin, di `data/keluaran`:**
- `fpo-indo-1` (keras dan onnx);
- `pencari-yolox-nano-640` (COCO dan plat-lighting);
- `pencari-yolox-nano-640-cctv1`;
- `kendaraan-yolox-coco`;
- `mesin-baca-1`;
- cadangan: `pembaca-jualan-p2`, `pembaca-jualan-p3a`, `pembaca-jualan-p3b`, `pencari-jualan-d1`.

## 10. Yang pernah salah (semua sesi; supaya tidak terulang)

| Kejadian | Pelajaran |
|---|---|
| Unduhan terpotong melapor kode 0; `.mp4` rusak tercatat utuh | Nilai dari berkas; `periksa_utuh.py` sebelum manifes |
| Klaim catatan usang diwariskan ("45 video", "100 video" padahal 259, "plat motor dua baris") | Klaim catatan diperiksa dan dikoreksi di commit yang sama |
| `node -e` dan heredoc kehilangan garis miring terbalik; `grep -c` 0 memutus `&&` | Skrip sebagai berkas; jangan merangkai sesudah `grep -c` |
| Hitungan sisi uji pernah dipakai sebelum owner memeriksa lembarnya (Rencana 19) | Diungkapkan ke owner; sejak itu sisi uji hanya dibaca sesudah label owner ada |
| Baris yang tidak disebut owner dianggap benar (Rencana 21) | Tanyakan secara eksplisit |
| Penilaian owner atas bingkai yang sama berubah antarputaran | Label dikunci dan dipakai ulang |
| `best.keras` tertahan di zaman 1 (model dari nol memantau `val_acc`) | Model dari nol memilih dengan `val_char_acc` |
| D1 dan D2 gagal dalam 0,2 detik karena argumen `-`; kontrol merah keliru karena `^`; `vendor.lock.json` ditulis ulang formatnya | Lihat perangkap perintah di §8 |
| Penjaga GPU satu kali periksa menolak P1 saat owner bermain game | Antrean menunggu memori, tidak menyerah |
| Kode ditulis sebelum uji terlihat merah, karena kunci bengkel | Buktikan merah sesudahnya, dan catat caranya di rencana |

## 11. Batas yang masih terbuka

- **Bahan uji:**
  - K9 tidak bisa dibuktikan dari bahan internet; butuh rekaman gerbang sungguhan (K43: HP owner dan CCTV kantor menyusul).
  - Tangkapan diambil owner saat platnya terlihat; set uji tangkapan kecil (38 gambar, 34 teks).
- **Pencari kendaraan:** melewatkan sebagian motor (7 dari 43 plat terlewat karena itu). Melatih ulang butuh kotak kendaraan yang
  diperiksa owner.
- **Izin:** K47–K49 bersandar pada pernyataan, bukan berkas izin. Risiko hukum K48 dan izin verbal K49 dicatat, dan bisa dibalik.
- **Fitur produk:** rincian per huruf untuk K46 baru ada di pembaca Keras, belum di ONNX. Logika status MASUK/KELUAR K46 ada di server
  (Fase 2).
- **Temuan lama di luar lingkup:**
  - `ambil-video.ps1` kode 8 positif palsu;
  - HEVC belum diuji;
  - nama di `mesin.json` cctv1 sama dengan pencari lama;
  - tidak ada CI;
  - kode wilayah "B" = Polda Metro Jaya masih anggapan.
