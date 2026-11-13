# Pengenal merek dan warna mobil: survei hanya-baca untuk Fase 3 (K51, 19 Okt 2026)

> **Hanya baca.** Tidak ada repo yang di-clone, bobot atau dataset yang diunduh, paket yang dipasang, atau kode yang dijalankan. Tidak ada
> gambar yang diunggah, dan `data/` tidak dibuka. Disusun agen riset atas permintaan owner (K51), dengan syarat tambahan owner: hanya repo
> GitHub gratis, presisi (akurasi beserta data ujinya), dari sumber resmi atau terpercaya, dan yang terpilih wajib dicek potensi backdoor.
>
> **Diperiksa ulang agen utama (19 Okt), semuanya cocok:**
> - `model.yml` vehicle-attributes-recognition-barrier-0039 memuat `license:` yang menunjuk LICENSE open_model_zoo, dan teks LICENSE itu
>   Apache-2.0.
> - Dokumen PP-Vehicle: *"The training and test phase of vehicle attribute recognition model are both obtained from VeRi dataset."*
> - Mendeley VMID: "CC BY 4.0", 2.072 gambar, 11 merek; Mendeley VTID2: "CC BY 4.0", 4.356 gambar, 5 jenis.
>
> Klaim lain dibaca agen riset dan belum diperiksa ulang (daftarnya di bagian 8). Vonis di sini sementara; vonis tetap ditulis saat
> komponen dikunci ke commit (CLAUDE.md §5, §6).

## 1. Ringkasan

- **Warna dan jenis: ada satu pilihan gratis, resmi, dan boleh dijual.** Model Intel `vehicle-attributes-recognition-barrier-0039` dan
  versi barunya `-0042` mengenal 7 warna dan 4 jenis. Izin bobotnya Apache-2.0, jadi vonis 13 Okt (`BELUM-JELAS`) salah dan sudah dikoreksi.
  Modelnya kecil sekali (2,5 MB), dibuat untuk CPU Intel. Kelemahannya:
  - tidak ada warna perak, coklat, atau krem;
  - dibuat untuk mobil tampak depan;
  - akurasi warna 81–83%, diukur Intel di foto COCO, bukan CCTV malam.
- **Malam inframerah:** tidak ada model yang bisa membaca warna dari gambar hitam-putih. Produk harus menjawab "warna tak terbaca".
- **Merek:** belum ada pengenal siap pakai yang gratis, terpercaya, boleh dijual, dan mengenal Daihatsu atau Wuling.
  - Yang sah: dataset universitas berizin CC BY 4.0 dari Thailand dan Pakistan (logo 11 merek; 48 model termasuk Daihatsu, Suzuki, Toyota;
    jenis kendaraan dari CCTV gerbang kampus).
  - Dataset merek Indonesia yang lengkap ada di Roboflow (sampai 68 merek, termasuk Wuling dan Daihatsu), tetapi pengunggahnya anonim dan
    asal gambarnya tidak disebut, jadi tidak lolos syarat "terpercaya".
- **Tanpa latih:** SigLIP2 (Google, Apache-2.0, safetensors) bisa menebak warna dan merek dari kata ("mobil putih", "Toyota"). Cocok sebagai
  pelabel awal di lab. Angka di CCTV Indonesia belum ada, dan kecepatannya di Mini PC belum diukur.
- **Penangkal plat tiruan (tujuan S3):** jalan paling murah adalah mencocokkan rupa kendaraan dengan kedatangannya sendiri yang dulu. Pembaca
  plat memberi label gratis (plat sama = kendaraan sama). Bobot pencocok rupa siap pakai semuanya dilatih dataset non-komersial, jadi
  kodenya boleh dipakai dan bobotnya dilatih sendiri.

## 2. Koreksi atas catatan 13 Okt (`2026-10-13-catatan-repo-dan-pustaka-baca-plat.md`)

1. **Model Intel 0039:** bobot `BOLEH-PRODUK` (diperiksa ulang, lihat kepala berkas). Ada versi baru, `-0042`.
2. **PP-Vehicle:** bobot `RISET-SAJA` (dilatih dan diuji di VeRi, yang non-komersial), menunggu P14. Diperiksa ulang.
3. **"Dataset mobil pasar Indonesia tidak ditemukan"** kurang tepat: ada di Roboflow, tetapi anonim. Dataset Asia berizin CC BY 4.0 dari
   universitas juga ada (VMID dan VTID2 Thailand, VMMR Pakistan).
4. **VMMRdb:** teks LICENSE-nya MIT untuk "Software", gambarnya dari *"different users"*; push terakhir 2020. Tetap `BELUM-JELAS`.
5. **Qwen3-VL-2B (alat lab):** catatan 13 Okt menulis `BOLEH-PRODUK` dari API Hugging Face, sedangkan `data-asal/bahan.json` dan
   `docs/VONIS-LISENSI.md` menulis bobotnya `BELUM-JELAS` karena teks izinnya belum dibaca dari repo terkunci. Tidak dipakai di pekerjaan
   sekarang; dicatat, tidak diubah.

## 3. Kandidat yang lolos syarat owner (gratis di GitHub, pemilik resmi)

| Komponen | Jenis | Kode | Bobot | Kelas | Akurasi diklaim (data uji) | Ukuran / CPU | Vonis kode / bobot / dataset | Bukti kepercayaan |
|---|---|---|---|---|---|---|---|---|
| **OMZ vehicle-attributes-recognition-barrier-0039** | warna, jenis | Apache-2.0 | Apache-2.0 (`license:` di model.yml); format IR .xml/.bin, SHA-384 di model.yml | 7 warna (putih, abu, kuning, merah, hijau, biru, hitam); 4 jenis (car, bus, truck, van) | Warna 81,15% (kuning 54%), jenis 87,56%; kendaraan COCO val2017 yang dianotasi Intel | 0,626 juta parameter, FP32 2,5 MB, masukan 72×72, "front facing cars"; Mini PC belum diukur | BOLEH / BOLEH / data latih tak diungkap | Intel; 220 kontributor; tag 2024.6.0; OpenSSF Scorecard 7,2; berstatus "maintenance mode" |
| **OMZ …-0042** | warna, jenis | sama | sama | sama | Warna 82,71%, jenis 87,34% (data uji sama) | 11,2 juta parameter, FP32 44,7 MB | sama | sama |
| **SigLIP2 base-patch16-224** | tanpa latih (warna, merek); bahan pencocok rupa | Apache-2.0 | apache-2.0 (organisasi `google`); safetensors, tanpa kode kustom | bebas, ditulis dengan kata | Belum ada angka mobil untuk SigLIP2; SigLIP v1 B/16 di Stanford Cars 90,81% (foto web mobil AS) | 375 juta parameter; Mini PC belum diukur, kemungkinan lambat | BOLEH / BOLEH / WebLI tak dirilis | Google; push 2025-05-19 |
| **DINOv2-small** | pencocok rupa (vektor ciri) | Apache-2.0 | Apache-2.0 ("code and model weights"); safetensors | — | Tidak ada angka kendaraan | 22 juta parameter | BOLEH / BOLEH / LVD-142M tak dirilis | Meta; push 2026-10-06 |
| FastReID | kode latih pencocok rupa | Apache-2.0 | .pth (pickle), dilatih VeRi, VehicleID, VERI-Wild | — | VeRi: Rank@1 97,0%, mAP 81,9% | ResNet-50 | BOLEH / RISET-SAJA (menunggu P14) / RISET-SAJA | JD AI; rilis terakhir 2021; Scorecard 2,7; **tidak dirawat** |
| PP-Vehicle attribute | warna, jenis | Apache-2.0 | izin tak dinyatakan; dilatih dan diuji di VeRi | 10 warna; 9 jenis (sedan, SUV, van, hatchback, MPV, pickup, bus, truk, estate) | mA 90,81 di VeRi | 6,7 MB | BOLEH / RISET-SAJA (menunggu P14) / RISET-SAJA | Baidu; v2.9.0 (2026-03-19); Scorecard 3,7 |
| Runtime OpenVINO | mesin jalan model Intel | Apache-2.0 | — | — | — | wheel 2026.4.1 menarik `openvino-telemetry` | BOLEH, dengan catatan telemetri | Intel; Scorecard 8,5 |

## 4. Dataset

| Dataset | Jenis | Izin | Isi | Merek Indonesia? | Akurasi diklaim | Vonis |
|---|---|---|---|---|---|---|
| **VTID2** (Mendeley; Loei Rajabhat dan Mahasarakham, Data in Brief 2024) | jenis | CC BY 4.0 (diperiksa ulang) | 4.356 gambar, 5 jenis; CCTV gerbang kampus, sudut 45°, siang. **Paling mirip kamera kita** | Thailand | 95,61% (validasi silang, tanpa set uji terpisah) | BOLEH-PRODUK (K21, atribusi) |
| **VMID** (sama) | logo merek | CC BY 4.0 (diperiksa ulang) | 2.072 gambar, 11 merek: Benz, Chevrolet, Ford, Honda, Isuzu, Mazda, MG, Mitsubishi, Nissan, Suzuki, Toyota | sebagian; tanpa Daihatsu dan Wuling | 92,22% (validasi silang) | BOLEH-PRODUK |
| **VMMR Pakistan** (Mendeley; IBA Karachi) | merek, model | CC BY 4.0 | 3.847 gambar, 48 kelas: Daihatsu Cuore/Hijet/Mira, Suzuki Carry/Swift/Wagon R, Toyota Fortuner/Hiace/Vigo, Honda BR-V/City/Civic, dll. | sebagian | tidak ada angka | BOLEH-PRODUK menurut izin; asal gambar tidak disebut |
| InaTRC (BRIN) | golongan tol | CC BY 4.0 | 3.250 gambar CCTV tol Indonesia, 5 golongan menurut gandar | — | — | BOLEH-PRODUK; hanya berguna untuk truk |
| UFPR-VCR / UFPR-VeSV (Brasil) | warna; warna, merek, model | "academic research only … non-commercial" | 10.039 / 24.945 gambar; 21,5% malam inframerah | Brasil | warna 94,6% mikro, 79,7% makro | RISET-SAJA (menunggu P14); syarat akses kemungkinan tidak terpenuhi |
| CompCars | merek, model | "non-commercial research purposes only" | 163 merek, 1.716 model | — | — | RISET-SAJA |
| VeRi-776, VERI-Wild | pencocok rupa | "used for non-commercial purposes" | 50 ribu / 416 ribu gambar | — | — | RISET-SAJA |
| VCoR (Kaggle) | warna | "Data files © Original Authors"; gambar "sourced from google" | 10 ribu lebih, 15 warna | — | — | BELUM-JELAS (menunggu P14). Banyak dataset warna Roboflow adalah salinannya berlabel CC BY 4.0 |
| VMMRdb | merek, model | MIT (Software) | 9.170 kelas, AS 1950–2016 | tidak | — | BELUM-JELAS |
| Stanford Cars | merek, model | halaman asli 404; sumber sekunder: non-komersial | 196 kelas mobil AS | tidak | — | kemungkinan RISET-SAJA, tidak terverifikasi |

## 5. Ditolak, dan alasannya

- **Plate Recognizer MMC** (merek, model, warna): berbayar, $45 per kamera per bulan. Gagal syarat "gratis".
- **NVIDIA VehicleMakeNet:** bukan repo GitHub, hanya untuk TAO/DeepStream/TensorRT (butuh GPU NVIDIA), tanpa Daihatsu atau Suzuki.
- **Roboflow:** all-cars-logo (16.920 gambar, 68 kelas, termasuk Wuling, Daihatsu LCGC, Polytron), "brand" milik akun JMTO (7.339 gambar,
  41 kelas, termasuk Agya, Ayla, Sigra, Wuling), Car Brand (51 kelas), car-type-final-1 (Avanza, Fortuner, Innova). Semuanya berlabel CC BY
  4.0, tetapi pengunggahnya anonim dan asal gambarnya tidak disebut. Gagal syarat "terpercaya". "Car Attributes v2" bahkan memuat kelas
  bernama `compcars`: contoh label CC BY yang menyesatkan.
- **Akun pribadi Hugging Face** (dima806, lamnt2008): dataset latih tidak disebut, merek AS, akurasi 69%.
- **Bobot OpenAI CLIP dan LAION OpenCLIP:** izin MIT, tetapi kartu modelnya menyatakan *"Any deployed use case … out of scope"* dan
  *"surveillance … always out-of-scope"*. Setara riset-saja, menunggu P14. Kode OpenCLIP tetap boleh.
- **Apple MobileCLIP dan DFN:** "exclusively for Research Purposes". **TinyCLIP:** repo diarsipkan. **DINOv3:** lisensi khusus bergerbang.

## 6. Jalan untuk produk yang dijual

**A. Warna dan jenis (disarankan lebih dulu).**
- Model Intel 0039 atau 0042 sebagai titik awal, diukur pada potongan kendaraan tangkapan owner (sisi uji).
- Inframerah: aturan sederhana; bila potongan hampir tanpa warna, jawab "tak terbaca".
- Bila 7 warna kurang (perak, krem, coklat): latih kepala kecil di atas vektor ciri SigLIP2 atau DINOv2 dengan label owner.
- Risiko izin rendah (Apache), walau data latih Intel tidak diungkap.

**B. Merek, lalu nama model.**
- Dari seluruh kendaraan atau dari logo. Data awal yang sah: VMID, VMMR Pakistan, VTID2 (CC BY 4.0).
- Data utama: tangkapan sendiri, dilabeli otomatis di lab (SigLIP2 atau Qwen3-VL-2B) lalu diperiksa manusia, sesuai aturan proyek.
- Periksa dulu ukuran logo pada potongan 2K yang nyata; di jarak gerbang logo mungkin hanya puluhan piksel.
- Merek baru terus masuk pasar (Polytron, VinFast, Jaecoo), jadi perlu latih ulang berkala (sesuai catatan K8).
- Acuan jumlah: sekitar 190 gambar per merek (VMID), sekitar 80 per model (Pakistan).

**C. Pencocokan rupa (penangkal plat tiruan; spec induk 4.2 cara A).**
- Simpan vektor ciri dari kedatangan yang platnya terbaca yakin, lalu bandingkan dengan kedatangan berikutnya.
- Mulai tanpa latih dengan SigLIP2 atau DINOv2, lalu latih sendiri dengan kode FastReID (Apache) atau kode sendiri.
- Kedatangan CCTV pertama lebih aman sebagai "foto daftar" daripada foto HP.
- Vektor ciri yang terkait plat adalah data pribadi, jadi disimpan di `data/`.

## 7. Pemeriksaan backdoor nanti (kandidat teratas, menurut `vision-seed/docs/PROTOKOL-KEAMANAN-REPO.md`)

1. **Model Intel 0039/0042:**
   - Format IR (.xml grafik, .bin bobot mentah), bukan pickle.
   - Ambil 2 berkas per presisi lewat pintu unduh terkunci, bukan `omz_downloader`; cocokkan SHA-384 dari model.yml pada commit yang dikunci.
   - Arsipkan LICENSE dan model.yml.
   - Wheel `openvino` menarik `openvino-telemetry`: periksa OSV untuk `nama==versi`, pastikan telemetri mati, jalankan tanpa jaringan.
2. **SigLIP2** (`google/siglip2-base-patch16-224`, revisi `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2`):
   - Hanya `model.safetensors`, tanpa .py. Tolak `trust_remote_code`.
   - Muat dari folder lokal dengan `HF_HUB_OFFLINE=1` dan SHA-256 berkas dikunci; `tokenizer.model` ikut diperiksa.
   - Untuk Mini PC: ekspor sisi gambar ke ONNX di lab dan bandingkan keluarannya, seperti `mesin.onnx` yang sudah ada.
3. **DINOv2-small:** pakai `model.safetensors` saja, bukan `pytorch_model.bin`. Jangan `torch.hub.load` dari GitHub (menjalankan
   `hubconf.py` dan mengunduh .pth). FastReID, bila dipakai, hanya kodenya.

## 8. Klaim yang belum terverifikasi

- Data latih model Intel; berkas anotasi COCO buatan Intel tidak dibuka.
- Kecepatan semua kandidat di Mini PC (N5095). Keterangan "N5095 tanpa AVX2" dari sumber pihak ketiga.
- Akurasi SigLIP2 pada mobil, dan akurasi tanpa latih pada CCTV Indonesia.
- Asal gambar dataset Pakistan dan Roboflow; apakah akun "JMTO" adalah Jasamarga Tollroad Operator.
- Apakah logo VMID dipotong dari CCTV.
- Syarat asli Stanford Cars dan VehicleID.
- Apakah OpenVINO 2026.4 masih membaca IR model itu, dan cara kerja `openvino-telemetry`.

## 9. Sumber utama

- OMZ: github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/vehicle-attributes-recognition-barrier-0039 (README, model.yml) ·
  …/barrier-0042 · LICENSE · data/dataset_definitions.yml
- PP-Vehicle: github.com/PaddlePaddle/PaddleDetection/blob/release/2.9/deploy/pipeline/docs/tutorials/ppvehicle_attribute_en.md
- Pencocok rupa: github.com/JDAI-CV/VeRidataset · github.com/PKU-IMRE/VERI-Wild · github.com/JDAI-CV/fast-reid/blob/master/MODEL_ZOO.md
- SigLIP2 dan OpenCLIP: huggingface.co/google/siglip2-base-patch16-224 · github.com/google-research/big_vision ·
  github.com/mlfoundations/open_clip/blob/main/docs/openclip_results.csv · huggingface.co/laion/CLIP-ViT-B-32-laion2B-s34B-b79K ·
  huggingface.co/apple/MobileCLIP2-S0/blob/main/LICENSE
- DINOv2: github.com/facebookresearch/dinov2 · huggingface.co/facebook/dinov2-small
- UFPR: github.com/Lima001/UFPR-VCR-Dataset · github.com/Lima001/UFPR-VeSV-Dataset · arxiv.org/abs/2408.11589 · arxiv.org/abs/2604.05271 ·
  arxiv.org/abs/2606.13625
- Dataset lain: mmlab.ie.cuhk.edu.hk/datasets/comp_cars · github.com/faezetta/VMMRdb ·
  kaggle.com/datasets/landrykezebou/vcor-vehicle-color-recognition-dataset
- Mendeley: data.mendeley.com/datasets/8ssr6kptbx (VMID) · /htsngg9tpc (VTID2) · /hj3vvx5946 · /cc5h2j9w68 (VMMR Pakistan) · /kddgphck3b ·
  pmc.ncbi.nlm.nih.gov/articles/PMC10859268
- Roboflow: universe.roboflow.com/zendyyonghero/all-cars-logo-r9pfo · /jmto-9jtua/brand-o0woc · /car-brand/car-brand-6ezl0 ·
  /denis-9sowc/car-attributes-v2 · /skripsi-9y6tk/car-type-final-1
- Ditolak: catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/vehiclemakenet · platerecognizer.com/pricing ·
  huggingface.co/dima806/car_brands_image_detection
- Bintang, kontributor, dan rilis dibaca dengan `gh api`; skor keamanan dari api.securityscorecards.dev.
