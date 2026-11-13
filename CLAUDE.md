# CCTV Gerbang — aturan proyek (dibaca otomatis tiap sesi di workspace ini)

> Workspace: `D:\Projects\super-team-v1\CCTVGerbang.code-workspace` · Status & antrean: [`ROADMAP.md`](ROADMAP.md)
> (**sumber tunggal**) · Visi, lingkup, keputusan: [`SEED.md`](SEED.md) · Dibuat 2026-10-13.
>
> Disusun agen dari aturan yang sudah berlaku: `~/.claude/CLAUDE.md`,
> `agent-sandbox/docs/megatron-workflow-standard.md` (Prinsip #0–#3), dan `vision-seed/CLAUDE.md`.
> Butir bertanda **(USULAN)** berlaku sebagai default sampai owner mengubahnya di `SEED.md` §6.

## 1. Urutan baca tiap sesi
`ROADMAP.md` → dokumen serah terima terbaru yang ditunjuk ROADMAP → `SEED.md` → `OPEN-QUESTIONS.md` → spec atau rencana
yang ditunjuk ROADMAP. Lanjutkan dari butir
pertama yang belum dicentang. **Tanya owner satu per satu, jangan menebak.** Tidak ada kode sebelum spec
disetujui owner. Satu-satunya pengecualian (owner, K17, 13 Okt): alat pengambil video riset di `tools/` dan
pengumpulan video mentah ke `data/video/riset/`.

## 2. ⛔ Lingkup — jangan melebar
- Yang dikerjakan dan yang tidak ada di `SEED.md` §5. **QC pabrik dan produk tanpa image processing bukan
  bagian workspace ini** (K1, K2).
- Temuan di luar lingkup **dicatat** di `ROADMAP.md` ("Temuan di luar lingkup"), tidak diselundupkan ke pekerjaan.
- **Bukan MVP, bukan demo** (Prinsip #0). Memecah pembangunan menjadi fase berurutan boleh; berhenti di
  setengah jadi tidak.

## 3. ⛔ Keselamatan gerbang (USULAN)
- Produk **hanya memberi perintah buka**. Tidak pernah perintah tutup, dan tidak menggantikan pengaman gerbang
  (fotosel, pembatas gaya).
- **Ragu = tidak membuka**, dengan pengecualian K46 (owner, 18 Okt): bacaan yang ragu pada 1–2 posisi boleh membuka bila tidak ada
  plat berstatus sama (misalnya sama-sama MASUK) yang cocok di posisi yang yakin; bila ada, satpam dipanggil. Di perumahan hanya bila
  cocok tepat satu plat penghuni. Lebih dari 2 posisi ragu tidak pernah menyalakan relay.
- Ciri kendaraan (jenis, merek, warna) yang tidak cocok dengan data pendaftaran hanya memberi peringatan ke satpam, tidak menahan gerbang
  (K55, owner, 19 Okt), sampai pengenal ciri terbukti akurat dan owner memutuskan lain. **Ditunda K63 (owner, 24 Okt):** untuk sekarang
  ciri hanya **dicatat**, tanpa peringatan sama sekali, karena di uji Rencana 33 sekitar 5 dari 37 kendaraan sah akan memicu peringatan
  palsu. Menyalakan peringatan adalah keputusan owner.
- Sampai Fase 5, relay hanya menyalakan lampu atau penanda di meja uji. **Agen tidak pernah menggerakkan
  gerbang sungguhan** tanpa owner hadir dan menyetujuinya saat itu.

## 4. ⛔ Data plat = data pribadi (UU PDP 27/2022)
- Foto dan rekaman plat, apalagi yang terkait nama penghuni dan jam keluar-masuk, tinggal di `data/`
  (di-gitignore). **Tak pernah** di-commit, di-push, atau diunggah ke layanan AI, pelabelan, atau playground
  pihak ketiga tanpa izin owner.
- Merekam di lokasi mana pun butuh izin pengelola lokasi. Yang dicatat di repo hanya asal-usul data, bukan datanya.
- Tanpa pengenalan wajah atau identitas orang (USULAN U3).
- Saat owner memeriksa lembar contoh, mintalah nomor baris dan jenis salahnya saja (misalnya "huruf seri ke-2 salah"),
  bukan nomor plat lengkap: jawaban di percakapan ikut terkirim ke layanan AI. Bila owner tetap menulis nomor plat, nomor
  itu tidak disalin ke berkas mana pun (14 Okt).

## 5. ⛔ Lisensi — produk ini akan DIJUAL (USULAN U7)
- Lisensi kode ≠ lisensi bobot model ≠ lisensi dataset. Ketiganya diperiksa terpisah dan diberi vonis sebelum
  dipakai. Acuan format: `vision-seed/docs/RISET-REPO.md`.
- Ultralytics YOLO (AGPL-3.0) tidak masuk produk tanpa keputusan owner tertulis.
- Vonis komponen baca plat ada di `docs/VONIS-LISENSI.md` (B12, Rencana 2). Yang vonisnya bukan `BOLEH-PRODUK` tidak
  masuk build yang dijual.
- **Bahan riset-saja (owner, K15, 13 Okt):** video, dataset, dan bobot berizin "bukan untuk dijual" boleh dipakai di
  laptop ini untuk belajar. Wajib dicatat asalnya dan ditandai `RISET-SAJA`; model hasil latihnya ikut bertanda.
  ~~Tak pernah masuk build yang dijual: sebelum dijual, mesin dilatih ulang hanya dengan bahan yang boleh dijual.~~
  Diubah K21.
- **Bahan dari internet untuk model yang dijual (owner, K21, 14 Okt):** boleh, selama sumbernya tidak menyebut larangan
  dipakai belajar. Asal tiap bahan tetap wajib dicatat. Yang menunggu owner (P14): apakah label non-komersial atau
  "riset saja", dan syarat situs yang melarang mengunduh, dihitung larangan. Sampai dijawab, bahan berlabel begitu
  tidak masuk mesin jualan.
- **Bobot fast-plate-ocr (owner, K47, 19 Okt):** pernyataan pemeliharanya di GitHub diterima sebagai izin, selama repo aman. Bobot
  itu `BOLEH-PRODUK`, dan pembaca jualan berangkat dari fpo-indo-1 yang dioptimalkan dengan data owner. Bobot lain, termasuk YOLOX
  COCO, tetap mengikuti aturan ketat sampai owner memutuskan.
- **Bobot YOLOX COCO (owner, K48, 19 Okt):** boleh menjadi dasar mesin jualan bila dimodifikasi (dilatih ulang), atas keputusan owner;
  risiko hukumnya dicatat di `SEED.md` §3 K48. ~~Mesin yang dilatih dengan video riset (cctv1) tetap `RISET-SAJA` karena bahannya.~~
- **Video riset (owner, K49, 19 Okt):** izinnya didapat owner secara verbal, jadi `video-riset-youtube` `BOLEH-PRODUK` dan cctv1 boleh
  dijual. Batas: izin tidak tertulis. Arah kerja sejak K50: optimalkan yang sudah ada (YOLOX COCO, cctv1, fpo-indo-1) dengan data owner.
- **Dataset Roboflow (owner, K56, 19 Okt):** lima dataset dari Roboflow Universe boleh menjadi bahan latih mesin jualan; label izin di halamannya
  (MIT, CC BY 4.0) diterima. Model jadi Roboflow tidak dipakai (gambar berplat tidak dikirim ke layanan luar). CC BY 4.0 wajib atribusi.

## 6. ⛔ Rantai pasok (USULAN U8)
Protokol `vision-seed/docs/PROTOKOL-KEAMANAN-REPO.md` berlaku di sini: repo dikunci ke commit · clone ≠
jalankan · bobot berformat pickle dipindai · `trust_remote_code=True` dilarang · percobaan pertama repo baru
di container tanpa jaringan.

## 7. ⚙️ Mesin (Prinsip #3)
- Diperiksa 2026-10-13: GPU RTX 4060 8 GB · `uv` 0.11.18 · Docker 29.5.3 · `python` di PATH hanyalah alias
  Microsoft Store, jadi pakai `uv`.
- **Satu job GPU pada satu waktu.** GPU ini dipakai bersama vision-seed: cek `nvidia-smi` sebelum melatih.
- Jangan bunuh paksa proses yang punya anak. Kalau terpaksa, periksa sisa prosesnya sebelum menyalakan job lain.
- Jangan `| tail` / `| head` pada perintah gerbang uji (status pipa menyembunyikan exit code).
- Gerbang uji repo ini ada dua: `npm test` (Node, di host) dan `npm run test:lab` (Python, di lab tanpa jaringan). Satu
  suite pada satu waktu. Kode 3 dari `tools\lab.ps1` berarti bengkel sedang dipakai job lab lain (kuncinya dipakai
  bersama vision-seed); itu bukan uji merah.
- Agen tidak pernah membuka gambar atau video riset apa adanya. Yang boleh dibuka hanya lembar ikhtisar dari
  `tools/lab/lembar_kecil.py`, dan baru sesudah owner memeriksanya (K19).
- Yang dijalankan lewat Docker hanya lewat pintunya: `tools\ambil-video.ps1` (pengunduh video, berjaringan, hanya
  melihat folder video), `tools\ambil-berkas.ps1` (pengunduh arsip dataset, berjaringan, hanya butir yang tercatat di
  kunci dan hanya melihat satu folder unduhan), dan `tools\lab.ps1` (lab, tanpa jaringan, repo read-only).
- Image lab tambahan `cctvgerbang-lab-fpo:v1` (K26, untuk melatih ulang fast-plate-ocr) dibangun hanya lewat
  `tools\image-lab-fpo.ps1` dan dijalankan hanya lewat `tools\lab.ps1 -Fpo`, dengan janji yang sama (ID dikunci di
  `image_lab_fpo`). Paket tambahan hanya lewat `tools/lab-fpo/requirements.txt` ber-SHA-256, sesudah diperiksa di OSV
  dengan `nama==versi` yang bersih. Kode torch di GPU memanggil `matikan_kernel_triton()` lebih dulu, karena image lab
  tidak punya kompiler C.
- Sesudah mengunduh video: `tools/lab/periksa_utuh.py` di lab, baru `tools/manifes-video.mjs`. Arsip dataset hanya
  dibuka di lab oleh `tools/lab/buka_arsip.py`, sesudah SHA-256-nya dikunci.
- Nama berkas dataset INDO-ALPR adalah nomor plat: tidak dicetak, tidak disalin ke repo, tidak didaftar dengan `ls`.
- Docker Desktop ada di `D:\Docker\Docker Desktop.exe` dan tidak menyala sendiri sesudah laptop dinyalakan ulang. Kode 6
  dari pintu mana pun bisa berarti Docker belum menyala: periksa `docker version` sebelum menyimpulkan image berubah.
- Git Bash mengubah jalur `/kerja/...` menjadi jalur Windows: perintah lab yang memuatnya dijalankan lewat PowerShell.
- Skrip sekali pakai (pencatat, pengukur) ditulis sebagai berkas, bukan `node -e` atau heredoc: garis miring terbalik
  pernah hilang tiga kali. Pencatat memeriksa tiap jangkar ketemu tepat sekali sebelum menulis apa pun.
- Agen tidak membuka `pembagian.json`, `lembar-contoh*`, atau `hasil.jsonl` di `data/keluaran/`: semuanya memuat nomor
  plat. Yang dibaca agen hanya `ringkasan.json` dan keluaran layar alat. Model ada di `models/` (di-gitignore) dan hanya
  dimuat lewat `tools/lab/model_terkunci.py`. Uji dengan model sungguhan ada di `tools/lab/uji_gpu/`, di luar gerbang
  `npm run test:lab`, dan dijalankan dengan tangan.
- Alat yang membuka berkas berplat tidak boleh membiarkan pesan galat mencetak jalurnya: `utama` menangkap `OSError` dan
  hanya mencetak jenis galatnya, dan log OpenCV dibisukan (`cv2.imread` mencetak jalur berkas yang tidak bisa dibuka).
  Uji kebocorannya dijalankan di proses terpisah. Ini terlewat saat Rencana 5 ditulis dan baru tertangkap saat dijalankan.
- Pemeriksa yang melapor "0 ditemukan" diuji dulu dengan kontrol positif (berkas yang pasti memuat yang dicari), supaya
  daftar larangan yang kosong tidak terbaca sebagai bersih.
- Pintu unduh berkas juga menerima rilis GitHub (`github.com`, `release-assets.githubusercontent.com`), tetap hanya untuk
  butir yang tercatat di kunci. Model fast-plate-ocr ada di `data/unduhan/fpo-*` dan hanya dimuat lewat gerbang berkas
  terkunci (`tools/lab/model_terkunci.py`).
- Bahan baca huruf yang berlaku adalah `data/keluaran/latih-koreksi/pembagian-koreksi.json`: set uji 937 plat (label
  dibetulkan, K22, K23) dan bahan latih 2.824 plat (dibersihkan, K24). Berkas pembagian yang lebih lama (`set-uji-baca/`,
  `set-uji-koreksi/`, `kembar/`) sudah usang. Semuanya memuat nomor plat: agen tidak membukanya.
- Label otomatis dari kesepakatan dua pembaca tidak dipakai tanpa diperiksa manusia: di bahan latih, label penerbit
  ternyata benar pada 27 dari 75 baris yang dicurigai (Rencana 7).
- Mesin baca huruf buatan sendiri ada di `data/keluaran/mesin-baca-1/` (bobot safetensors, SHA-256 dan catatan latihan di
  `mesin.json`) dan hanya dimuat lewat `PembacaMesin` di `tools/lab/mesin_baca.py`, yang menolak bobot yang berubah. Set uji
  tidak pernah dipakai untuk memilih apa pun; perbaikan mesin diputuskan dari validasi bahan latih.
- Mesin baca huruf `fpo-indo-1` (fast-plate-ocr yang dilatih ulang, K26) ada di `data/keluaran/fpo-indo-1/` (`mesin.keras`;
  SHA-256, bahan, dan catatan latihan di `mesin.json`; tanda `RISET-SAJA`). Ia hanya dimuat lewat `PembacaMesinFpo` di
  `tools/lab/latih_fpo.py`, di image lab tambahan (`lab.ps1 -Fpo`), yang menolak `mesin.keras` yang berubah. Ekspor ONNX
  belum jalan di Keras + torch. Latihan penuh dengan bawaan pembuatnya butuh sekitar 3 jam (76–81 detik per zaman):
  jalankan di latar dengan keluaran ke berkas log, dan jangan percaya taksiran dari plat buatan (Rencana 10 meleset 3,5 kali).
- `mesin.onnx` fpo-indo-1 dibuat `tools/lab/onnx_fpo.py buat` dengan menukar bobot ke ONNX terbitan (ekspor bawaan gagal di
  Keras + torch). Ia disimpan hanya bila tukar-diri tidak mengubah ONNX terbitan dan semua gambar validasi sama dengan Keras.
  Ia hanya dimuat lewat `PembacaOnnxMesin` (SHA-256 terhadap `mesin-onnx.json`), yang memakai `LicensePlateRecognizer` di
  CPU seperti pembaca fast-plate-ocr terbitan. Pengukuran kecepatan dijalankan saat mesin tenang (`docker ps`, `nvidia-smi`).
- Kecepatan model di mesin lain diukur dengan `tools/ukur_onnx_cpu.py` (hanya numpy dan onnxruntime, masukan buatan). Di Mini
  PC (`mini-megatron`, menjalankan layanan hidup) agen hanya bekerja di `/tmp/cctvgerbang-ukur`:
  - venv sementara dengan paket ber-hash yang sudah diperiksa OSV;
  - `nice -n 19` dan `timeout`;
  - folder dihapus sesudahnya, dan sisa proses diperiksa dengan pola yang tidak cocok dengan dirinya sendiri
    (`pgrep -af "[u]kur_onnx_cpu"`);
  - beban dan RAM dicatat sebelum dan sesudah; bila beban satu menit 3 atau lebih, tunggu;
  - hanya model publik atau berbobot acak; foto plat tidak pernah dibawa ke sana.
- Pencari plat YOLOX buatan sendiri (K30, Rencana 13) ada di `data/keluaran/pencari-yolox-<jenis>-<ukuran>/`: `mesin.safetensors`
  dan `mesin.onnx`, dengan SHA-256, bahan, dan catatan latihan di `mesin.json` dan `mesin-onnx.json`; tanda `RISET-SAJA`. Ia hanya
  dimuat lewat `PencariYolox` di `tools/lab/pencari_yolox.py` (ONNX, tanpa torch) atau `muat_mesin` di `tools/lab/latih_yolox.py`
  (safetensors); keduanya menolak berkas yang berubah. Bobot awal COCO (pickle) hanya lewat `torch.load(weights_only=True)`.
  Melatih satu calon butuh 30–49 menit di GPU ini: jalankan di latar dengan log. Ekspor ONNX menimbang keluaran mentah per
  satuan: koordinat dalam piksel, peluang tersendiri.
- Rantai utuh (Rencana 14) ada di `tools/lab/rantai.py` dan dijalankan di image tambahan (`lab.ps1 -Fpo`), karena pembacanya.
  Keluarannya di `data/keluaran/rantai-video/`: `kedatangan.jsonl` dan `potongan/` memuat plat, jadi agen hanya membaca
  `ringkasan.json`. Lembar dari `tools/lab/lembar_rantai.py` hanya dibuka owner; jawabannya nomor baris per jenis (salah, tak
  terbaca, bukan plat, motor) dan diteruskan ke `lembar_rantai.py nilai`. Jalan panjang yang mengukur kecepatan disertai
  perekam proses (`data/alat-sementara/jalan-rantai-14.ps1`): di Rencana 14 uji sesi lain menyala di tengah jalan pertama, jadi
  rantai dijalankan ulang saat tenang, dan hasilnya identik.
- Tabel angka laporan Fase 0A (`bukti/2026-10-16-laporan-fase-0a.md`) ditulis `node tools/laporan-0a.mjs tulis <laporan>` langsung
  dari JSON di `bukti/`, dan tidak diubah tangan. `node tools/laporan-0a.mjs periksa <laporan>` keluar 1 bila laporan menyimpang
  dari sumbernya; jalankan sesudah mengubah laporan atau bukti.
- Fase 1 (Rencana 16–18): manifes video mengenal `sudut` parkiran. Set uji dan latih Fase 1 adalah
  `data-asal/pembagian-video-fase1.json` dari `node tools/bagi-video.mjs`; tiap video ditentukan dari SHA-256-nya sendiri, jadi
  jangan membagi ulang dengan cara lain, karena video uji tidak boleh pindah ke latih. `rantai.py jalan --pembagian ... --sisi uji`
  hanya menjalankan sisi itu. Lembar bingkai (`tools/lab/lembar_bingkai.py`) hanya dibuka owner. Plat buatan
  (`tools/lab/plat_buatan.py`, butir bahan `plat-buatan`) berteks acak, jadi agen boleh melihat contohnya.
- Mesin tenang untuk mengukur kecepatan di laptop berarti juga tidak ada uji milik sesi lain (vitest, uji mutasi) dan
  pemindaian Defender yang ikut menyala: `docker ps` dan `nvidia-smi` saja tidak cukup. Ukur beberapa putaran bergiliran
  antarcalon dan pakai mediannya. Di Rencana 13, uji mutasi sesi lain melipatkan angka 4 utas Tiny-640 dari 43 ms ke 114 ms.
- Rencana 19 (K39): dataset pencari plat CCTV dibuat `tools/lab/dataset_cctv.py` dari `penampakan.jsonl` rantai sisi latih
  (`--simpan-penampakan`) dan jawaban lembar latih owner. Kotak yang tidak dipilah owner ditutup buram, tetapi plat yang tidak
  pernah ditemukan pencari lama tetap ada di gambar "tanpa plat": gambar tanpa label tidak boleh dianggap bebas plat.
- Tahap kendaraan (K39) ada di `tools/lab/kendaraan.py`. Pencari kendaraannya YOLOX-Tiny COCO di
  `data/keluaran/kendaraan-yolox-coco/`: ONNX, ambang 0,25 dipilih di sisi latih, tanda `RISET-SAJA`. Ia hanya dimuat lewat
  `PencariKendaraan`, yang menolak `mesin.onnx` yang berubah. `rantai.py jalan` dan `lembar_bingkai.py lembar` menyalakannya
  dengan `--kendaraan`; di lembar bingkai, kendaraan berkotak biru. Pencari plat yang dilatih ulang ada di
  `data/keluaran/pencari-yolox-nano-640-cctv1/`. Nama di `mesin.json`-nya sama dengan pencari lama, jadi bedakan dari folder dan
  SHA-256.
- Rencana 20 (K39 langkah 3): `rantai.py jalan` dan `lembar_bingkai.py lembar` mendapat `--cara saring|potong`. Cara `potong`
  mencari plat di dalam potongan kendaraan (`kendaraan.cari_dalam_kendaraan`). `lembar_bingkai.py lembar --ambang` mengganti
  ambang validasi pencari, seperti rantai; tanpa itu lembar tidak menggambarkan rantai yang diukur. Lembar kendaraan
  (`tools/lab/lembar_kendaraan.py`) hanya dibuka owner: kendaraan bernomor, dan owner menyebut nomor kendaraan yang platnya
  terbaca. `banding` menilai calon dari jawaban itu; "ditemukan" berarti ada kotak di kendaraan itu, belum tentu di platnya.
- Rencana 21 (K39 langkah 2): kotak plat dari tahap kendaraan membawa kotak kendaraannya sebagai unsur ketujuh, dan
  `penampakan.jsonl` mendapat daftar `kendaraan` yang sejajar dengan `tampak`. Daftar `tampak` sendiri tidak diubah, karena
  `dataset_cctv.py` membongkarnya sebagai `g, *kotak`. Saringan letak ada di `tools/lab/letak.py` (24 aturan, `banding` dari label
  owner sisi latih). `--letak` di rantai dan lembar bingkai memakai `letak.saring_letak`. Saringan ini tidak dijadikan bawaan,
  karena di set uji ia membuang plat sungguhan.
- Rencana 25 (K50): rantai jualan memakai kendaraan dengan `--cadangan-utuh` (dikoreksi 19 Okt: tahap kendaraannya masih
  `kendaraan-yolox-coco`, YOLOX COCO apa adanya bertujuan "belajar"; menurut K48 belum boleh dijual sampai dilatih ulang; sejak Rencana 32:
  `kendaraan-jualan-k1`) (plat dicari di gambar utuh bila tidak ada kendaraan
  setinggi `MIN_TINGGI`), pencari plat `data/keluaran/pencari-cctv2-c1` (cctv1 dilatih lanjut lewat `latih_yolox.py --bobot-awal-mesin
  --jualan`; ambang rantai 0,25 dipilih di sisi latih tangkapan), dan pembaca fpo-indo-1 (sejak Rencana 30: `pembaca-lanjut-r4`).
  `--maks-kendaraan` ada, tetapi tidak dipakai:
  membatasi ke kendaraan terdekat membuang plat. `bahan_pembaca.py --wilayah --ulang-tangkapan` dan `latih_fpo.py latih-lanjut` melatih
  lanjut fpo-indo-1; calon R1 dan R2 tidak terpilih. Keluaran rencana ini di `data/keluaran/rencana-25/`; `kedatangan.jsonl`,
  `hasil.jsonl`, CSV, dan potongan di sana memuat plat. Uji image tambahan `test_rantai_sungguhan.py` ikut menuntut isi ringkasan
  `baca_gambar`, jadi jalankan `uji_fpo` sesudah mengubah keluaran alat rantai.
- Rencana 26 (K51): `tools/lab/tahan_geser.py` dan `--varian-potong v0|v1|v2` di `baca_gambar.py` dan `rantai.py` (pembaca membaca 1/3/7
  potongan lalu memungut suara). Bawaannya v0, lewat kode lama yang sama persis. v2 tidak dijadikan bawaan: di tangkapan uji tidak menolong
  dan 6,5 kali lebih lambat. Keluaran rencana ini di `data/keluaran/rencana-26/`; `kedatangan.jsonl` dan potongan di sana memuat plat.
- Rencana 27 (K54): `tools/lab/rapikan.py` dan `--rapikan <konteks>` di `baca_gambar.py` dan `rantai.py` (pencarian kedua di sekitar tiap
  kotak plat). Bawaannya 0. Tidak dipakai: pencari C1 memberi kotak yang lebih pendek saat plat diperbesar, jadi bacaan turun. Uji
  `test_baca_gambar.py` memakai konstanta `ATURAN_BAWAAN` untuk isi aturan ringkasan; tambahkan kunci baru di sana dan di
  `uji_fpo/test_rantai_sungguhan.py`.
- Rencana 28 (K53): dataset dari luar diperiksa dengan `tools/lab/periksa_dataset.py` (`periksa`: jenis berkas dari isinya, tanda program,
  `yaml.safe_load`, label, kembar; `lembar`: contoh per kelas untuk owner; mengenal susunan deteksi YOLO dan klasifikasi Folder Structure)
  sesudah Windows Defender dengan kontrol positif EICAR dan `buka_arsip.py`. Lima dataset Roboflow ada di
  `data/keluaran/dataset/roboflow-*` (zip di `data/unduhan/roboflow-*`, dikunci di `tools/vendor.lock.json`), bervonis ~~`BELUM-JELAS`~~
  `BOLEH-PRODUK` sejak K56.
  Gambar, lembar, dan `lembar.json` memuat kendaraan dan plat: agen tidak membukanya. Roboflow mewajibkan akun, jadi owner yang mengunduh.
- Rencana 31 (Fase 3, K61): `tools/lab/halaman_ciri.py buat` membuat halaman ciri untuk owner (satu kartu per kendaraan pemuat plat
  berlabel; usulan jenis dari pencari kendaraan) di `data/keluaran/halaman-ciri/`, dan `terima` mengubah `label-ciri.json` dari owner
  menjadi `ciri.json` dan `ringkasan-ciri.json`. Daftar kelas spec Fase 3 adalah `halaman_ciri.KELAS`; ubah kelas hanya di sana. Halaman,
  `gambar/`, `butir.json`, dan `ciri.json` memuat kendaraan dan plat: agen hanya membaca `ringkasan-ciri.json` dan layar alat. Uji halaman
  di peramban hanya dengan gambar buatan (`data/alat-sementara/halaman-buatan-31.py`), lewat server lokal 127.0.0.1. `terima` menolak
  berkas jawaban yang tanda halamannya berbeda.
- Rencana 32 (Fase 3, K48): pencari kendaraan rantai jualan adalah `data/keluaran/kendaraan-jualan-k1` (YOLOX-Tiny-640 satu kelas dari
  `latih_yolox.py`, dilatih ulang dari bobot COCO, tujuan jualan). Ambangnya di `kendaraan.json` (`kendaraan.py tetapkan`), terikat ke
  SHA-256 `mesin.onnx`; `PencariKendaraan` menolak mesin satu kelas tanpa ambang. Jenis tiap kotak "kendaraan", jadi usulan jenis tidak
  datang dari pencari ini. Dataset pencari kendaraan dibangun `tools/lab/dataset_kendaraan.py` (label dilengkapi kotak guru pencari COCO,
  nama berkas baru dari SHA-256). `latih_yolox.py latih` dari bobot COCO tidak membaca bahan dataset: berikan `--bahan` dari `ringkasan.json`
  dataset, karena tanpa itu daftar bahan bawaan pencari plat yang tercatat. Keluaran di `data/keluaran/rencana-32/`; folder rantai di sana
  memuat plat.
- Rencana 29 (K56): `dataset_jualan.py tambah-latih --kelas <n> --bahan <butir>` memasukkan semua sisi dataset YOLO tambahan ke `train`
  saja (berawalan `r-`, poligon menjadi kotak pembungkus, `valid` tidak disentuh). Pencari C3 ada di `data/keluaran/pencari-cctv3-c3/`
  (C1 dilatih lanjut dengan plat "vehicle and license plate"; tujuan jualan). C3 menemukan lebih banyak plat, tetapi kotaknya kurang pas,
  jadi rantai bawaan tetap C1 ambang 0,25. Menambah plat dari luar menaikkan angka menemukan, bukan membaca: periksa juga IoU kotak terhadap
  label (`data/alat-sementara/ukuran-kotak-25.mjs`) sebelum menyimpulkan pencari baru menolong rantai. Keluaran di
  `data/keluaran/rencana-29/`; `kedatangan.jsonl` dan potongan di sana memuat plat.
- Rencana 30: pembaca rantai jualan adalah `data/keluaran/pembaca-lanjut-r4` (fpo-indo-1 dilatih lanjut; ONNX lewat `PembacaOnnxMesin`,
  `mesin-onnx.json`; tujuan jualan). Bahannya dari `bahan_pembaca.py siapkan --rantai <folder baca_gambar> ... --geser
  --validasi-terpisah`: potongan rantai dicocokkan dengan `halaman_label.cocokkan`, aturan yang sama dengan `nilai_label`; ubah aturan cocok
  hanya di sana. Latih lanjut memakai `latih_fpo.py latih-lanjut --laju 0.0001`: laju bawaan 0,001 membuat latihan lanjut Rencana 25 gagal.
  Zaman dipilih dari potongan tangkapan; INDO-ALPR di `validasi-indo.csv` hanya penjaga. `onnx_fpo.py buat` hanya memeriksa
  `validasi.csv`, jadi untuk bahan bervalidasi terpisah periksa juga ONNX lawan Keras di potongan lain (temuan 19 Okt di ROADMAP).
  Keluaran di `data/keluaran/rencana-30/`; `kedatangan.jsonl`, `hasil.jsonl`, CSV, dan potongan di sana memuat plat.
- Rencana 33 (Fase 3): potongan kendaraan berlabel jenis dan warna dibuat `tools/lab/potongan_ciri.py` (dari `label-ciri/ciri.json` dan
  dataset Roboflow) ke `data/keluaran/potongan-ciri/`; kotak yang owner tandai "kotak tidak pas" dibuang, dan "tak yakin" tidak menjadi
  label. Pengenalnya `tools/lab/ciri.py`: `ciri-jenis-j1` dan `ciri-warna-w1` di `data/keluaran/` (ONNX, tujuan jualan). **Ambang "tak
  yakin" tidak disimpan di mesin:** `PengenalCiri` menuntutnya sebagai argumen (jenis 0, warna 0,7 menurut Rencana 33). Saringan
  inframerah (`saring_inframerah`, K52) dipakai pada **gambar penuh**, bukan potongan: kendaraan hitam atau putih juga nyaris tanpa warna.
  Variasi latihan di `ciri.py` tidak boleh mengubah rona atau jenuh, karena itu merusak label warna. Ciri dinilai dengan **benar − salah**
  (`nilai_ambang`), bukan benar saja. `ciri.csv`, potongan, dan folder `data/keluaran/rencana-33/` memuat kendaraan dan plat.
- Rencana 34 (Fase 3): `potongan_ciri.py` mengenal ciri ketiga, `merek` (`merek_kelas` {nama kelas: merek}, `merek_kata_pertama`,
  `merek_sisa`); `CIRI` menentukan kolom `ciri.csv`, jadi menambah ciri cukup di sana. Potongan Rencana 34 ada di
  `data/keluaran/potongan-ciri-2/` (folder baru, supaya bahan Rencana 33 tetap persis seperti saat diukur). Mesin `ciri-merek-m1` ada,
  tetapi **merek belum berguna**: di uji semua bacaan benarnya Honda, nol benar di luar Honda. Jangan memasangnya di rantai tanpa
  keputusan owner. Saat menilai pengenal ciri, hitung juga **benar di luar kelas terbanyak**: nilai benar − salah saja bisa terlihat baik
  padahal mesin hanya menebak kelas mayoritas.
- Rencana 35 (Fase 3): `ciri.py latih --ukuran --jenis` mengatur ukuran masukan mesin dan menyaring jenis. Ukuran dicatat di `mesin.json`
  dan `mesin-onnx.json`, lalu dibaca kembali `ekspor` dan `PengenalCiri`, jadi tidak ada ukuran tersembunyi; uji rantainya di
  `uji_fpo/test_ciri_sungguhan.py`. **Merek mobil tidak bekerja** pada masukan 96, 192, maupun 256 (`bukti/2026-10-26-merek-mobil-resolusi.md`):
  mesin `ciri-merek-mobil-c*` tersimpan tetapi tidak dipasang di rantai. Dua dugaan agen (logo terlalu kecil, masukan terlalu kecil)
  keduanya tidak terbukti; dugaan ketiga yang belum diuji adalah bahannya (3.274 dari 3.309 potongan mobil latih berasal dari dataset
  brand, bukan CCTV). Validasi owner mobil hanya 17 potongan dan uji 13, jadi percobaan ciri untuk mobil berdaya rendah: jangan
  menyimpulkan sebab dari angka sekecil itu.

- TGT (platform, Rencana T1) ada di `tgt/`, bukan di `tools/`: `tools/` tetap bengkel, `tgt/` produk. Ia memakai
  **Node 24 dengan `node:sqlite` dan `node:http` bawaan, tanpa satu pun dependensi baru** — repo ini nol dependensi, dan tiap
  paket baru masuk aturan rantai pasok (§6). `node:sqlite` masih fitur percobaan di Node, jadi ia mencetak
  ExperimentalWarning; itu batas, bukan galat. Berkas basis datanya memuat plat dan jam keluar masuk, jadi tempatnya
  `data/tgt/` yang di-gitignore (§4), dan uji tidak pernah menyentuhnya: semuanya di memori atau folder sementara sistem.
  `npm test` sudah diperluas ke `tgt/uji/*.test.mjs`; tanpa itu uji TGT tidak akan pernah jalan.
- Aturan TGT yang ditegakkan di lapisan data, bukan hanya di layar: **jenis kendaraan adalah daftar putih**
  (`JENIS_KENDARAAN` di `tgt/layanan.mjs`: mobil, pikap, truk, bus — K65), jadi motor dan jenis yang belum dikenal
  ditolak; **plat dinormalkan** jadi huruf besar tanpa spasi (`normalkanPlat`) untuk disimpan dan dibandingkan, dan unik
  **per gerbang**; **arah kejadian** juga daftar putih. **Waktu kejadian wajib berbentuk `2026-10-26T08:00:00` jam
  setempat**, karena `ringkasanJam` memotong huruf ke-12 dan ke-13 sebagai jam — bentuk lain dulu diterima dan membuat
  angka dashboard salah diam-diam. Migrasi skema ada di `tgt/basis.mjs` (`MIGRASI`), tiap langkah punya naik DAN turun,
  dan diuji bolak-balik.

- TGT, tempat simpan (K70, owner 26 Okt): data TGT tinggal di **PC milik IBE sendiri, bukan VPS sewaan**. Karena itu **jalur
  simpan foto dan catatan wajib bisa diatur**, tidak dipaku di kode — NAS akan dibeli nanti dan harus bisa dipasang tanpa
  membongkar kode. **Sampai NAS ada, belum ada cadangan sama sekali:** itu batas yang disebut saat demo, bukan hal yang
  dianggap beres. Letak PC-nya ("seperti Yanmar") belum dipastikan dan perlu ditanyakan sebelum Rencana T4 dan T6.

- TGT Rencana T2: aplikasinya ada di `tgt/` dengan susunan berlapis yang **tidak boleh ditembus**:
  `layanan.mjs` (data mentah, tanpa hak akses, dipakai mesin gerbang yang tidak punya pengguna) → `akun.mjs`
  (akun, sandi scrypt, keanggotaan grup) → **`akses.mjs` (satu-satunya pintu untuk lapisan web; memeriksa peran)**
  → `server.mjs` (`node:http`) → `web/` (halaman). **`server.mjs` DILARANG mengimpor `layanan.mjs`**: ada uji
  rantai di `tgt/uji/server.test.mjs` yang membaca sumbernya dan gagal bila impor itu muncul (sudah dibuktikan bisa
  merah). Jalankan dengan `npm run tgt`; jalur basis data, foto, cadangan, porta, dan alamat dari pengaturan
  (`tgt/pengaturan.mjs`, peubah lingkungan `TGT_*`), tidak dipaku di kode (K70).
- Pagar hak akses TGT: peran **selalu dibaca dari basis data**, tidak pernah dari apa yang dikirim pemanggil;
  tanpa sesi, sesi ke pengguna tak ada, peran tak dikenal, dan grup tak cocok semuanya **ditolak**; pesan "tidak ada"
  dan "bukan milik Anda" **sengaja sama**, supaya tidak bisa dipakai menebak isi grup lain; kode undangan hanya
  terlihat oleh pengelola. Menyembunyikan tombol di layar **bukan** pengamanan — yang menolak adalah server.
- Layar TGT (`tgt/web/`): gaya disalin apa adanya dari `docs/tgt/konsep-ui.html` yang disetujui owner (K68); jangan
  mengubah warna atau jarak tanpa alasan. **`[hidden] { display: none !important }` wajib ada di akhir `gaya.css`**
  (tanpa itu `display: grid/flex` mengalahkan atribut `hidden` dan layar masuk tampil bersamaan dengan cangkang).
  **Jangan merantai `append()`**: `Node.append()` mengembalikan `undefined`, jadi `a.append(b).append(c)` melempar
  galat dan seluruh halaman gagal digambar. Keduanya cacat nyata yang ditemukan 26 Okt saat halaman dibuka di
  peramban, ketika 220 uji sudah hijau; penjaganya di `tgt/uji/web.test.mjs`, yang hanya membaca sumber dan
  **tidak** menggantikan pembuktian di peramban. Halaman yang belum dibangun ditandai "belum dikerjakan", tidak
  diisi data karangan.

- TGT, tempat pasang (K71, owner 26 Okt): TGT akan dipasang di **PC IBE lewat Tailscale**, bersebelahan dengan server
  MES Yanmar. Diperiksa 26 Okt: mesin Tailscale bernama `ibe` **mati sejak 27 Agustus (60 hari)**, `company-ai` hidup,
  dan `DESKTOP-07FJHUU` adalah laptop ini sendiri — jadi mesin MES-nya **belum dipastikan**. Mesin itu menjalankan
  layanan yang dipakai orang sungguhan: berlaku Prinsip #3, jadi apa pun yang dipasang di sana **tidak boleh**
  menghabiskan penyimpanan atau mengganggu MES, dan **kredensial tidak ditebak** — tanyakan owner.
- **⛔ SEMUA DATA WAJIB DISIMPAN (K74, owner 26 Okt) — ini MENGOREKSI K71, bukan menambahnya.**
  Kalimat owner di K71 ("data tidak boleh di simpan semua") dibaca sesi sebelumnya sebagai "simpan seminimal
  mungkin lalu hapus", dan tebakan itu dibangun jadi penghapus (T3) lalu disambungkan sampai benar-benar
  menghapus (T10). **Maksud owner kebalikannya: tidak ada yang boleh dihapus.** Arah gagalnya sekarang:
  bawaan `SELAMANYA`, dan apa pun yang tidak terbaca sebagai jumlah hari (kosong, salah ketik, "0", negatif)
  berarti **simpan** — bukan galat, bukan bawaan yang menghapus. Pagarnya di tiga lapis: `pengaturan.mjs`
  (`SELAMANYA`), `bersihkan()` (per jenis data, supaya pemanggil yang lupa memeriksa tidak bisa menghapus),
  dan `jadwalkanBersih()` (tidak menyala sama sekali bila tidak ada masa simpan yang disetel sengaja).
  Masa simpan dibaca **sekali saat penjadwal dibuat**, bukan tiap putaran: keputusan "menyala atau tidak"
  dan "berapa harinya" harus datang dari pembacaan yang sama, kalau tidak kalimat di layar saat start-up
  berhenti menggambarkan apa yang dilakukan putaran berikutnya. Satu bahaya yang hampir lolos:
  `Date.now() - null * 86400000` sama dengan **sekarang**, jadi masa simpan yang tidak terbaca akan
  menghapus **seluruh isi folder foto** — itu diperiksa di `bersihkanFoto` dan di pemanggilnya.
  Kodenya **tidak dicabut**: masa simpan mungkin kembali sesudah ahli hukum memeriksa (spec §8, B9), dan ada
  uji yang membuktikan jalur itu masih utuh bila `TGT_SIMPAN_*` disetel sengaja.
- **⛔ Jangan mengganggu MES Yanmar (K74).** TGT dipasang di `company-ai`, yang menjalankan perangkat lunak
  yang dipakai orang sungguhan. **Diukur 26 Okt:** basis data tumbuh **190 bita per kejadian** = 10 MB/tahun
  pada 150 kendaraan/hari, 100 MB dalam 10 tahun — aman. Yang besar adalah **foto bukti, 4–42 GB/tahun per
  gerbang**, dan foto itu **belum ditulis apa pun** (folder `data/tgt/foto` belum pernah ada; jembatan kamera
  hanya menulis gambar sementara lalu membuangnya). Pagarnya `tgt/ruang.mjs`: di bawah 5 GB sisa, TGT
  **berhenti menulis gambar baru** dan berteriak, dan **tidak pernah menghapus** (K74). Arah gagalnya
  berbeda dari gerbang uang: ruang yang **tidak bisa dibaca dianggap cukup**, karena gerbang yang berhenti
  mencatat kehilangan catatan yang tidak bisa dibuat ulang, sementara disk penuh masih memberi tanda lain.
  Server menyebut sisa ruang saat menyala, supaya tidak ditemukan saat disk sudah penuh.
- ~~**"Data tidak boleh disimpan semua" (K71).** Mengikat rancangan: simpan sesedikit mungkin, dan **masa simpan
  ditegakkan di dalam kode**, bukan hanya tertulis di spec §8.~~ **Dikoreksi K74 — lihat di atas.** Pembersihnya `tgt/simpan.mjs` (`bersihkan()`), dengan
  masa simpan dari `tgt/pengaturan.mjs` (`TGT_SIMPAN_*`) supaya bisa diubah tanpa menyentuh kode. Yang menghapus diuji
  dua arah: yang lewat masa simpan **hilang**, yang masih di dalamnya **tetap ada**.

- TGT Rencana T3: kendaraan, tamu, masa simpan, dan QR undangan. **Masa simpan ditegakkan di kode**
  (`tgt/simpan.mjs`, `bersihkan()`), bukan hanya tertulis di spec §8 — K71 "data tidak boleh disimpan semua".
  Angkanya dari `tgt/pengaturan.mjs` (`TGT_SIMPAN_FOTO|KEJADIAN|TAMU`), dan nilai yang tidak masuk akal ditolak,
  bukan diganti bawaan diam-diam. Yang **tidak pernah** dihapus: kendaraan terdaftar (itu daftar izin), dan tamu
  yang kunjungannya **masih terbuka** walau sudah lama (satpam butuh catatan siapa di dalam). Saat tamu dihapus,
  **tautan ke kejadiannya diputus, kejadiannya tetap** — masa simpan tamu lebih pendek daripada kejadian.
  ~~`bersihkan()` **belum dijadwalkan otomatis**; penjadwalannya ikut pemasangan di PC IBE (K71).~~
  **Dikoreksi Rencana T10:** ternyata `bersihkan()` tidak dipanggil SIAPA PUN selain ujinya sendiri selama tujuh
  rencana, jadi masa simpan K71 "yang ditegakkan di kode" tidak menghapus apa pun — foto dan catatan plat
  menumpuk selamanya, sementara 23 uji terus hijau. Sejak T10 `jalankan()` memanggil `jadwalkanBersih()`
  (`SELANG_BERSIH_MS`, 6 jam, **jalan sekali saat server menyala**, pewaktunya `unref()`, galatnya dicatat
  bukan ditelan). ⛔ `buatServer()` TIDAK menjadwalkan apa pun, dan itu bukan kerapian: ia dipakai 50-an uji
  dan `pengaturan()` bawaan menunjuk ke `data/tgt/foto` yang sungguhan, jadi penjadwal di sana akan menghapus
  foto owner tiap `npm test`. Penjadwalan di tingkat sistem operasi tetap ikut pemasangan di PC IBE (K71);
  pembersih ini hidup di dalam proses server, jadi server yang mati berarti tidak ada yang membersihkan.
- **⛔ Pembuat QR `tgt/web/qr.js`: jangan percaya `bacaKembali()` di berkas itu sebagai bukti.** Ia memakai peta,
  topeng, dan urutan bit yang SAMA dengan pembuatnya, jadi kesalahan yang konsisten tidak terlihat olehnya — ia
  lulus melewati **empat** cacat berturut-turut yang membuat QR mustahil dibaca pemindai mana pun (telusur kolom
  data sesudah kolom pola waktu · bit ke-7 keterangan format hilang · polinom generator Reed-Solomon terbalik ·
  urutan bit keterangan format terbalik). Pembuktian yang sah memakai pembaca di luar kode ini:
  `tools/lab/uji_qr/kontrol_positif.py` lewat `tools\lab.ps1`, yang **selalu menyertakan kontrol positif** (QR
  rujukan buatan OpenCV digambar dengan cara yang sama). Tanpa kontrol itu, kegagalan alat uji terlihat persis
  seperti kegagalan QR kita — dan itu sempat terjadi. Penjaga di gerbang Node hanya mengunci nilai baku
  keterangan format (diturunkan ulang dengan BCH, bukan disalin); bahwa pemindai sungguhan membacanya **tidak**
  bisa dijamin gerbang Node.
- Halaman undangan tamu (`tgt/web/undangan.html`) dibuka **tanpa akun**, hanya dengan kodenya. Isinya disaring
  `akses.undangan()`, dan ada uji yang memastikan nomor WhatsApp maupun nomor dalam basis data tidak ikut keluar.
  Pilihan "Motor" di layar kendaraan **ada tetapi dimatikan** bertuliskan "menyusul di versi 2" (K65): batas versi 1
  harus terlihat jujur oleh calon pembeli, bukan disembunyikan.
- Penjaga berkas layar (`tgt/uji/web.test.mjs`) memindai **semua** berkas `.js` di `tgt/web`, bukan `app.js` saja:
  berkas layar yang baru ditulis justru yang paling mungkin memuat cacat yang sama.

- **⛔ `tgt/putusan.mjs` adalah kode paling menyangkut keselamatan di produk ini.** Aturan §3 berlaku penuh dan
  dijaga uji: tidak ada jalan mana pun yang menghasilkan perintah **tutup** (ada uji yang memindai sumber server,
  dengan kontrol positif); berkas itu **tidak menggerakkan apa pun** — sampai Fase 5 tidak ada keluaran relay sama
  sekali, dan menyambungkannya butuh keputusan owner; masukan yang tidak dikenal bentuknya **tidak pernah membuka**.
  Pemeriksaan "lebih dari 2 posisi ragu" sengaja diletakkan **sebelum** mencari calon: kalau diperiksa belakangan,
  calon tunggal yang meyakinkan akan menggoda siapa pun untuk melonggarkannya.
- Bacaan agen atas K46 yang sudah dikodekan dan **menunggu koreksi owner**: (a) pembatasan "hanya plat penghuni" di
  perumahan berlaku untuk bacaan yang **ragu** saja — tamu yang terbaca yakin tetap dibukakan; (b) plat yang terbaca
  yakin tetapi statusnya janggal (terbaca masuk padahal tercatat sudah di dalam) **tetap dibuka**, hanya ditandai,
  karena kamera bisa melewatkan satu kejadian dan menahan orang karena catatan kita sendiri meleset menimpa orang
  yang tidak bersalah.
- Daftar izin untuk kotak di gerbang (`layanan.daftarIzin`) memuat **plat, jenis, dan status saja** — tanpa nama dan
  tanpa nomor WhatsApp. Perangkat di gerbang tidak membutuhkan data pribadi siapa pun untuk memutuskan membuka, dan
  ada ujinya di dua lapisan.
- Mode luring (`tgt/web/luring.js`): kejadian yang gagal terkirim **diantrekan di perangkat** dan disusulkan saat
  tersambung. Penyusulan **berhenti pada kegagalan pertama** supaya urutan kejadian tidak melompat, dan tiap kejadian
  membawa `penanda` unik yang dibuat UNIQUE di basis data lewat indeks parsial — kirim ulang aman karena server
  mengembalikan kejadian yang sudah ada alih-alih membuat yang baru. ~~**Batas yang diketahui:** sesi masih disimpan di
  memori server, jadi server yang dinyalakan ulang membuat satpam harus masuk lagi, dan antrean baru tersusul
  sesudah ia masuk.~~ **Ditutup Rencana T8:** sesi tersimpan di basis data, jadi server yang dinyalakan ulang
  tidak lagi melempar satpam keluar dan antrean tersusul tanpa ia masuk lagi. Batas lamanya terbukti saat uji
  cabut internet 26 Okt, dan penutupannya dibuktikan dengan benar-benar mematikan lalu menyalakan server.
- Layar satpam menampilkan putusan dengan **kata dan bentuk, bukan warna saja** (dipakai malam hari, oleh orang yang
  berganti sif). Tombol buka manual **tidak menggerakkan apa pun** dan tulisannya menyebut itu; kejadiannya dicatat
  sebagai `dibuka_satpam`, bukan sebagai putusan mesin, supaya siapa yang memutuskan selalu bisa dibedakan.

- **⛔ Status janggal (K73, owner 26 Okt): MASUK dibuka, KELUAR tidak.** Plat terbaca yakin dan terdaftar, tetapi
  catatan mengatakan ia tidak sedang di dalam saat hendak keluar ⇒ **panggil satpam, jangan dibuka**: bisa jadi plat
  tiruan. Arah masuk tetap dibuka beserta notifikasi. Alasannya yang harus diingat sebelum melonggarkannya: yang
  hilang bila mesin salah menahan hanyalah waktu, sementara yang hilang bila mesin salah meloloskan adalah barang
  orang.

- **⛔ Notifikasi dorong menuntut HTTPS — dibuktikan di HP, bukan dibaca dari dokumen (26 Okt).** Diuji di HP OPPO
  lewat Mini PC: halaman TGT dibuka di `http://localhost:8797` (adb reverse, jadi konteksnya AMAN dan
  `pushManager.subscribe()` berhasil). Yang terjadi: **langganannya hilang lagi beberapa detik kemudian** —
  `getSubscription()` mengembalikan null walau service worker aktif dan izin sudah diberikan, dan kiriman
  berikutnya dijawab `410 push subscription has unsubscribed or expired`. Jadi **konteks aman saja tidak cukup**;
  Chrome Android tidak mempertahankan langganan dorong di `http://localhost`. **Yang SUDAH terbukti:** tanda tangan
  VAPID benar dan kiriman diterima layanan dorong (FCM menjawab **201** untuk kiriman berisi maupun tanpa isi).
  **Yang BELUM terbukti:** penyandian isi pesan, karena tidak ada perangkat yang pernah membukanya. Jangan menyebut
  notifikasi sudah jalan sampai ia terlihat muncul di layar HP lewat HTTPS sungguhan.
- Untuk membuktikannya dan untuk memasang di PC IBE (K71), TGT butuh HTTPS. Tailscale menyediakan sertifikat sah
  untuk nama mesin di tailnet tanpa biaya (`tailscale cert` / `tailscale serve`), jadi ini **bukan** keputusan
  uang — tetapi ia mengubah apa yang terbuka di jaringan mesin itu, jadi **tanyakan owner lebih dulu**.

- **HTTPS untuk TGT lewat Tailscale Serve (izin owner, 26 Okt).** Di Mini PC: `sudo tailscale serve --bg
  --https=8444 http://127.0.0.1:8797` menghasilkan `https://mini-megatron.{tailnet}.ts.net:8444` dengan
  sertifikat sah, **tailnet saja, bukan Funnel**. ⛔ Mesin itu SUDAH memakai Serve untuk layanan lain milik owner,
  dan porta 443 serta 8443 di sana **terbuka ke internet (Funnel on)** — jangan menyentuh keduanya; pakai porta
  yang belum dipakai dan jangan pernah menyalakan Funnel tanpa diminta. Mencabut: `sudo tailscale serve
  --https=8444 off`.
- **Notifikasi dorong di HP uji OPPO: TIDAK BISA DIBUKTIKAN, dan sebabnya ada di HP-nya, bukan di kode.** Sesudah
  HTTPS sah dipakai, service worker aktif, izin granted, dan konteks aman, `pushManager.subscribe()` sempat
  memberi alamat FCM sungguhan — tetapi **langganannya hilang dari perangkat dalam hitungan detik**
  (`getSubscription()` null), dan percobaan berlangganan berikutnya **menggantung**. Play Services terpasang dan
  ada akun Google, jadi dugaan terkuat adalah pengelolaan latar belakang OPPO/ColorOS. **Yang tetap terbukti:**
  tanda tangan VAPID benar dan FCM menjawab 201 untuk kiriman berisi maupun tanpa isi. **Yang belum:** pesan
  sampai dan terbuka di HP. Untuk membuktikannya, pakai HP lain — dan jangan menyebutnya jalan sebelum itu.

- TGT Rencana T6: **jenis kendaraan masuk ke rantai, dan kamera menyalakan status.** Jalurnya:
  layar satpam → `POST /api/gerbang/:id/kamera` → `tgt/jembatan.mjs` (folder) → `tools/lab/layanan_baca.py`
  (di lab, tanpa jaringan) → kembali → `akses.bacaanGerbang`. **Jembatannya folder, bukan port**, karena lab
  berjalan `--network none` dan pagar itu tidak dicabut: justru ia yang membuat bobot model dari luar aman
  dijalankan. Jalur dan folder diatur `tgt/pengaturan.mjs` (`TGT_BACA_MASUK`, `TGT_BACA_KELUAR`), bawaannya di
  `data/keluaran/` karena hanya folder itu yang bisa ditulis dari dalam lab.
- **⛔ Jenis kendaraan TIDAK PERNAH menahan gerbang.** Jenis benar pada 12 dari 14 mobil — sekitar 1 dari 7 salah
  — jadi menahan berarti menahan penghuni yang tidak bersalah tiap hari (K55). Ia hanya menandai `ciriJanggal`
  dan memanggil notifikasi. Ada uji yang menjalankan tiga keadaan tidak-buka dengan tiga nilai jenis dan menuntut
  putusannya **tidak bergeser sama sekali**: ciri boleh menambah catatan, tidak pernah melonggarkan. Ini
  **berbeda dari K73** (status janggal saat keluar ditahan), dan bedanya disengaja: status berasal dari catatan
  kita sendiri yang jarang meleset, jenis dari tebakan mesin yang sering meleset.
- **⛔ Bila tahap kendaraan ADA tetapi tidak menemukan apa pun, jenis dibiarkan KOSONG** — jangan pernah menebak
  dari gambar utuh. Pada bukti 26 Okt, jalan cadangan itu menjawab "motor" dengan keyakinan 0,95 atas gambar yang
  tidak memuat kendaraan sama sekali; di TGT itu muncul sebagai ketidakcocokan jenis, dan satpam dipanggil untuk
  sesuatu yang tidak pernah terjadi. Tebakan meyakinkan atas gambar yang salah lebih berbahaya daripada tidak
  menjawab. Dikunci dua uji di `tools/lab/uji/test_layanan_baca.py`.
- Folder `data/keluaran/baca-masuk/` dan `baca-keluar/` memuat gambar kendaraan dan nomor plat: **agen tidak
  membukanya**. `layanan_baca.py` menjaga janji yang sama dengan alat berplat lain: **pesan galat tidak pernah
  memuat jalur atau nama berkas**, karena nama berkas bisa memuat nomor plat.
- **Daftar batas untuk demo ada di `docs/tgt/batas-demo.md`** — apa yang boleh dijanjikan, apa yang tidak, dan
  angka yang harus disebut bila ditanya. Perbarui berkas itu tiap kali ada angka baru, dan baca sebelum
  menyiapkan peragaan apa pun.

- TGT Rencana T7: **beranda jam keluar masuk.** `layanan.ubinBeranda` menghitung "di dalam sekarang" dari
  **status plat** (kejadian terakhir), BUKAN dari selisih masuk dikurangi keluar: selisih akan salah begitu satu
  kejadian terlewat kamera, dan angka salah di beranda lebih buruk daripada tidak ada angka, karena ia terlihat
  seperti kebenaran. Angka beranda hanya untuk satpam dan pengelola. Tanggal dikirim peramban, bukan server: jam
  sibuk sebuah gerbang adalah jam setempatnya.
- Grafik jam memakai bentuk dan warna dari konsep UI yang disetujui (K68). **Tangga sumbunya wajib bilangan
  bulat** (`tgt/web/tangga.js`, dipisah supaya bisa diuji): yang dihitung adalah kendaraan, dan "3,75 kendaraan"
  membuat orang berhenti mempercayai grafiknya — sempat terjadi saat beranda pertama dibuka di peramban. Angkanya
  selalu bisa dibuka sebagai tabel, supaya grafik tidak pernah menjadi satu-satunya cara membacanya.

- TGT (Rencana T8): cara masuk utama adalah **tautan undangan per orang**, bukan email + OTP. Pengelola membuat
  anggota (cukup nama; email tidak wajib) lalu menyalin tautannya dan mengirimnya sendiri lewat WhatsApp.
  Tautan dan sesi sama-sama **kunci masuk**: tandanya 32 bita acak, tersimpan ter-hash (`undangan_masuk.tanda_hash`,
  `sesi.tanda_hash`), tautan **sekali pakai** dan berlaku 14 hari, dan hanya pengelola yang boleh membuatnya.
  Tanda dibawa **setelah `#`** di alamat, bukan sebagai `?tanda=`: bagian setelah `#` tidak dikirim ke server,
  jadi ia tidak masuk catatan server maupun proksi. Halaman `undang.html` **tidak boleh** mendapat jalur
  "mengintip" tanda tanpa memakainya — jalur seperti itu bisa dipakai menebak tanda tanpa jejak; ada uji rantai
  yang menjaganya. Sesi tersimpan di basis data (`tgt/sesi.mjs`, 90 hari), jadi server yang dinyalakan ulang
  tidak melempar orang keluar; uji rantainya menyalakan **server kedua** atas basis yang sama, karena isi
  `sesi.mjs` bisa hijau seluruhnya sementara server masih memakai Map di memori.
- Kunci rahasia P-256 dari `node:crypto` dikembalikan sebagai **bilangan, tanpa nol di depan**: sekitar 1 dari 256
  kunci hanya 31 bita. Kode yang menyusun DER dari panjang tetap wajib melapisinya (`rahasia32` di
  `tgt/dorong.mjs`), dan melapisinya sekali saat kunci dibuat **tidak cukup** — `getPrivateKey()` memotong nolnya
  lagi tiap kali. Uji yang memeriksa satu kunci akan terlihat hijau pada hari ia ditulis: paksa kuncinya
  berawalan nol (`setPrivateKey` dengan bita pertama 0).

- **⛔ Pola cacat yang paling sering di TGT: jalur atau fungsi yang BENAR, DIUJI, dan tidak dipanggil siapa pun.**
  Ketemu empat kali dalam dua rencana: `POST /api/grup/:id/anggota` tanpa layar (T8) · `DELETE /api/langganan`
  tanpa tombol (T10) · `bersihkan()` tanpa pemanggil produksi (T10, yang terburuk: ia penghapus data pribadi) ·
  `cariTamuPlat()` yang bahkan tak punya uji dan mengunci aturan yang sudah terbukti salah (dicabut T10).
  Dari luar, semuanya terlihat persis seperti kode yang bekerja, dan gerbang uji tetap hijau karena ujinya
  memanggil fungsinya LANGSUNG. Karena itu: **tiap fitur baru butuh satu uji yang menelusuri jalannya** dari
  jalur yang dipakai produksi (lewat `jalankan()`, lewat HTTP, lewat layar), bukan dari fungsinya saja.
  Penjaganya di `tgt/uji/web.test.mjs` (tiap jalur DELETE punya pemanggil di layar; mengenal **dua** bentuk
  penulisan jalur, karena versi pertamanya hanya mengenal satu dan melaporkan bersih sambil tidak melihat
  jalur yatimnya) dan `tgt/uji/bersih-berkala.test.mjs`. Sapuan kasarnya ada di
  `data/alat-sementara/sepupu-t8.mjs` (jalur HTTP) dan `sepupu-t10.mjs` (fungsi yang diekspor); keduanya
  memakai kontrol positif, karena pemeriksa yang melapor "0 ketemu" karena polanya salah tidak bisa dibedakan
  dari yang melapor bersih.

- **⛔ Satu kendaraan = SATU KEDATANGAN (K75, owner 26 Okt).** Kamera gerbang menghasilkan belasan bingkai per
  kendaraan. Sebelum Rencana T9 tiap bingkai menjadi kejadian tersendiri, dan akibatnya **setiap mobil yang
  keluar menahan gerbang di bingkai keduanya**: bingkai pertama membuat catatan "sudah keluar", jadi bingkai
  kedua terlihat janggal dan aturan K73 menahannya. Semua uji sebelumnya mengirim SATU bacaan per kendaraan,
  jadi tidak ada yang pernah menyentuh keadaan ini — ini contoh paling jelas kenapa **uji harus menelusuri
  keadaan yang sebenarnya terjadi di lapangan**, bukan keadaan yang mudah ditulis.
  Pengelompokannya: `layanan.kedatanganBerjalan` (gerbang + plat + arah, dalam `jendelaKedatangan()` detik,
  bawaan 20), dan `kejadian.kedatangan_id` menunjuk kejadian pertama kedatangan itu.
  ⛔ Pencarian kedatangan dilakukan **SEBELUM** barisnya disisipkan: kalau sesudah, ia menemukan baris itu
  sendiri dan bingkai sebelumnya tidak pernah terlihat. ⛔ `akses.bacaanGerbang` **menyalin putusan bingkai
  pertama**, tidak menghitung ulang — jadi tidak ada jalan yang bisa melonggarkan `panggil_satpam` menjadi
  `buka`, dan ada ujinya. ⛔ Waktunya dinormalkan dengan `layanan.waktuBaku` yang SAMA dengan yang dipakai saat
  menyimpan; jalur kamera tidak mengirim waktu sama sekali, dan penormalan yang berbeda membuat pengelompokan
  rusak diam-diam (jalur kamera sempat menjawab 500 tanpa satu pun uji kedatangan merah).
  Beranda dan grafik jam memakai `count(DISTINCT kedatangan_id)`, dan kedatangan dihitung menurut jam
  **bingkai pertamanya** supaya kendaraan yang menyeberang pergantian jam tidak terhitung dua kali.
  **Batas yang owner setujui sadar:** di dalam jendela itu mesin tidak bisa membedakan mobil yang sama dari
  plat tiruan. **Batas lain:** bacaan tanpa plat tidak digabung.

- **`company-ai` ({ip-company-ai}), mesin tempat TGT akan dipasang — diperiksa 26 Okt, hanya-melihat.**
  Masuk lewat **Tailscale SSH sebagai `{pengguna-ssh-company-ai}`** (owner memberikannya; tanpa sandi, kebijakan tailnet yang
  mengizinkan). **MES Yanmar = Odoo di porta 8069** dengan PostgreSQL 16 di 127.0.0.1:5432. Mesin itu juga
  menjalankan Next.js, Docker, Chrome ber-remote-debugging (9222), VNC (5900/5901, 6080), Tailscale Serve
  (443), dan sesuatu di 4400. **Odoo sehat: `/web/login` 18–57 ms, beban satu menit 0,10** — itu angka
  pembanding yang harus diukur ulang sesudah TGT jalan.
  Mesinnya **lapang di memori dan disk, LEMAH di prosesor**: Celeron J4025 **2 inti**, RAM 7,3 GB dengan 5,8 GB
  tersisa, Node **v22.23.2**, Docker 29.1.3. ⛔ **TGT di `/srv/tgt`, JANGAN di `/home/{pengguna-ssh-company-ai}`**: folder rumah
  ada di `/` yang sudah **65% penuh** dan ditempati sistem operasi serta Odoo, sementara `/srv` adalah volume
  logis tersendiri dengan **37 GB kosong** — pemisahan volume itu pagar yang lebih kuat daripada pagar mana pun
  di dalam kode kami. `{pengguna-ssh-company-ai}` butuh `sudo` (bersandi) untuk menulis di `/srv`. Porta 8787 kosong.
  ⛔ Jangan menyentuh porta 8069, 5432, 443, 4400, 6080, 9222; jangan menyalakan Funnel; jangan menyalin
  `data/` dari laptop ini (isinya nomor plat, §4).
  **Node 22 cukup untuk TGT, dan itu DIBUKTIKAN di sana, bukan diasumsikan** (`node:sqlite` masuk sejak 22.5):
  `lastInsertRowid`/`changes` sebagai angka, `ALTER TABLE ADD/DROP COLUMN` untuk migrasi dua arah, kunci asing,
  `fs.statfsSync`, `strftime`, dan `count(DISTINCT)` semuanya bisa.
  **Yang BELUM dijawab:** kecepatan mesin baca plat di Celeron itu, dan apakah TGT benar-benar tidak mengganggu
  Odoo saat jalan — keduanya butuh menulis berkas ke mesin produksi, yaitu **izin owner**. Runbook dan daftar
  larangannya di [`docs/tgt/pasang-di-company-ai.md`](docs/tgt/pasang-di-company-ai.md).

- **⛔ Resolusi video dicatat dari BERKASNYA, bukan dari `.info.json`.** `tools/lab/periksa_utuh.py` mencatatnya
  (kunci `gambar`), dan `tools/manifes-video.mjs` memakainya; yang dinyatakan sumber disimpan terpisah sebagai
  `ukuran_sumber`. Sebabnya, 27 Okt: unduhan yang dibatasi resolusinya menghasilkan berkas 640x360 yang
  tercatat 1280x720, yaitu resolusi aslinya di YouTube — dan setiap angka pengukuran yang memakai catatan itu
  ikut menyesatkan tanpa ada yang tahu sebabnya. Perbaikannya langsung menemukan **4 video lain** yang tercatat
  1080p padahal berkasnya 720p. **Sesudah mengunduh, periksa `ukuran` di manifes, jangan percaya resolusi yang
  diminta.** Batas ukuran pintu unduh kini **1 GB** (dinaikkan dari 400m, 27 Okt): video satu jam di 720p adalah
  420–770 MB. Pagar manifes **menolak berkas yang isinya berubah sejak dicatat**, jadi mengganti berkas dengan
  resolusi lain menuntut catatannya dicabut dengan sengaja — jangan memaksa manifes menerima perubahan isi,
  itu mencabut pagar yang sama untuk semua video.

- **Rencana T9 bagian 2 (K76):** rantai jualan dijalankan di rekaman gerbang satu jam
  ([`bukti/2026-10-27-rantai-gerbang-satu-jam.md`](bukti/2026-10-27-rantai-gerbang-satu-jam.md)).
  `rantai.py --sampel-per-detik` mengatur laju contoh, dan ringkasan mencatat laju yang **dipakai** (dulu ia
  mencatat konstantanya — kelas cacat yang sama dengan resolusi video yang tercatat dari sumber).
  ⛔ **Laju contoh mengubah hasil dengan cara yang tidak intuitif:** pada 5 gambar/detik bagian yang yakin 34%,
  pada 1 gambar/detik justru **52%**. Sebabnya ambang `min_tampak = 2`: pada laju tinggi ia cuma menuntut benda
  bertahan 0,4 detik, jadi salah-deteksi sekejap ikut menjadi "kedatangan". **Jangan menyimpulkan laju tinggi
  lebih baik.** `tools/sebaran-penampakan.mjs` mencetak sebaran bingkai per jalur dari `penampakan.jsonl`
  (berkas itu tanpa teks plat; alat itu berhenti bila kelak memuatnya, dan hanya mencetak angka ringkas).
  **Di `company-ai`, 1 gambar/detik adalah BATAS, bukan pilihan:** 3.597 gambar × 1,023 detik = 3.679 detik
  untuk video 3.597 detik — 102% waktu nyata, tanpa margin. Jalan yang menambah margin tanpa menukar ketelitian
  adalah **melewati gambar yang tidak ada geraknya** (pencari kendaraan 70% dari biaya dan berjalan pada semua
  gambar); mencabut tahap kendaraan memang 3,3× lebih cepat tetapi menemukan lebih sedikit plat.

- **⛔ Repo ini ada di GitHub sejak 6 Nov 2026 (K77): `ibe-vision/cctv-gerbang`, PRIVAT, dibagikan ke partner bisnis owner.**
  Sebelum TIAP push, jalankan dua pemeriksa dan pastikan keduanya keluar 0:
  `node tools/periksa-sebelum-push.mjs` (jalur terlarang, gambar, berkas besar, rahasia, rincian server) dan
  `node tools/cocokkan-plat-riwayat.mjs` (pola mirip plat di seluruh riwayat dicocokkan dengan plat sungguhan di
  `data/`; hanya jumlah yang dicetak). Mengunggah = menerbitkan, dan riwayat yang sudah tersalin ke komputer partner
  tidak bisa ditarik kembali.
  **Rincian server tidak masuk repo** (keputusan owner): IP Tailscale, pengguna SSH, dan nama berkas kunci tertulis
  sebagai tanda `{ip-company-ai}`, `{pengguna-ssh-company-ai}`, `{ip-mini-pc}`, `{kunci-ssh-mini-pc}`,
  `{ip-mesin-ibe}`, `{tailnet}`. Artinya ada di **`catatan-lokal/server.md`** (di-gitignore); di komputer lain berkas itu
  harus dibuat ulang atau ditanyakan ke owner. Jangan menulis alamat atau nama pengguna aslinya kembali ke berkas yang
  ter-commit — pemeriksa membaca daftar larangannya dari `catatan-lokal/ganti.json` dan akan menolaknya.
  Riwayat **ditulis ulang** 6 Nov untuk membuangnya, jadi **semua hash commit sebelum tanggal itu berubah**; cadangan
  riwayat lama yang utuh ada di `data/cadangan-git/sebelum-bersih-2026-11-06.bundle`.
  ⛔ Email partner yang diundang tidak pernah ditulis ke berkas mana pun di repo: itu data pribadi orang lain.

- **K78–K79 (13 Nov), alat baca plat motor di PC-3050-mekanik (tanpa Docker, tanpa lab):** `tools/baca_lokal.py` membaca foto
  dengan model publik yang dikunci SHA-256 di `vendor.lock.json` (pencari `oim-yolo-v9-t-384`, pembaca `fpo-cct-s-v2`; **bukan**
  mesin jualan, angkanya bukan angka rantai); dijalankan lewat venv `data/alat-sementara/venv-rtsp` dengan `-I`. `nilai` menerima
  jawaban owner lewat nomor baris atau kolom `periksa_owner` (S/T/B) di CSV, dan jalur CSV terbukti sama dengan jalur nomor baris.
  `tools/uji_dummy.py` menguji alat itu dengan plat dummy berlabel (teks acak, boleh dibuka agen) dan memastikan penilaian lewat
  jawaban owner sama dengan hitungan langsung. **Hasil baca foto Bardi ada di `data/cctv bardi/`** (CSV, JSON, potongan, lembar:
  semuanya memuat plat, agen hanya membaca `ringkasan.json`); hasil lama diarsipkan di `arsip-227-foto/`, tidak dihapus.
- **Plat modif buatan (K79):** `tools/plat_modif.py buat` membuat plat motor modif berteks acak (jarak rapat/menempel/renggang/acak;
  font tebal/miring/hias/sempit/lebar/goyang). `acuan` mengambil **hanya angka** dari foto kamera (letak, lebar, bentuk, terang,
  ketajaman, derau, mode) ke `acuan.json`; `buat --acuan` meniru angka itu; `tempel` menempel plat buatan di **foto asli** menutup
  plat aslinya — `gambar/` keluaran `tempel` memuat foto owner, **agen tidak membukanya**; `potongan/`-nya plat buatan saja.
  ⛔ **Kotak pencari disaring bentuknya (`ASPEK_PLAT` 1,3–3,5) sebelum dipakai sebagai acuan atau tempat tempel:** 34 dari 174 kotak
  di foto Bardi hampir persegi, bukan plat utuh. ⛔ Angka tidak bisa membuktikan plat asli tertutup penuh oleh tempelan; itu dicek
  mata owner pada nomor yang disebut agen. Nilai pembaca pada plat modif selalu disebut **bersama yakin-tetapi-salah**: pada plat
  modif 30% bacaan yakin ternyata salah, pada plat polos 8% — itulah yang berbahaya bagi gerbang, bukan angka benarnya.

## 8. Uang
Membeli kamera, kotak komputasi, relay, lisensi, atau layanan berbayar = keputusan owner. Agen menyusun daftar
dan membaca harganya dari sumber; owner yang membeli.

## 9. Git
- Commit dalam Bahasa Indonesia dan memuat **alasan**. ~~Repo ini lokal: membuat repo GitHub atau push **hanya
  dengan konfirmasi owner eksplisit** (tujuan, nama, visibility).~~ **Dikoreksi 6 Nov (K77):** repo ini ada di
  GitHub — `ibe-vision/cctv-gerbang`, **privat** — dan dibagikan ke partner bisnis owner. Push tetap **hanya dengan
  konfirmasi owner**, dan **sebelum tiap push** kedua pemeriksa (`tools/periksa-sebelum-push.mjs`,
  `tools/cocokkan-plat-riwayat.mjs`) wajib keluar 0. Membuat repo baru di organisasi itu tetap butuh konfirmasi owner
  atas nama dan visibilitasnya.
- `ROADMAP.md` diubah lewat changelog-nya, tidak ditulis ulang dari ingatan (Prinsip #1).
