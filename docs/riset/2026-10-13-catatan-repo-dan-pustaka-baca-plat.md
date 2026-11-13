# Catatan sumber: repo dan pustaka gratis untuk baca plat (13 Okt 2026)

> **Apa ini.** Hasil survei hanya-baca lewat web, dikerjakan sub-agen riset pada 13 Okt 2026 atas permintaan owner
> (K16: "cari yang gratis-gratis saja di repo"). Tidak ada yang di-clone, dipasang, atau dijalankan.
>
> **Pemeriksaan acak oleh agen utama (13 Okt).** Dua klaim dibuka ulang dan cocok: (1) README RF-DETR: pendeteksi
> Nano, Small, Medium, Large berlisensi Apache 2.0; Atto, Femto, Pico, XL, 2XL berlisensi PML 1.0. Kalimat "butuh
> akun Roboflow" **tidak** ada di README itu. (2) Issue #14 open-image-models: pemelihara menulis "I don't know if
> GPL applies to weights (not using any actual GPL code)". Pernyataan soal fork YOLOv9 (issue #22) tidak dibuka
> ulang.
>
> **Keandalannya.** Selain dua klaim di atas, agen utama **belum memeriksa ulang** baris di bawah. Tiap vonis berstatus
> **sementara** sampai diperiksa pada commit yang dikunci di Fase 0 (`OPEN-QUESTIONS.md` B12). Isi halaman
> diterima sub-agen lewat peringkas alat baca web, yang memotong kutipan di atas 125 karakter. Kutipan Frigate
> versi sekarang cocok di dua sumber; kutipan lain hanya dari satu pembacaan. Semua angka akurasi adalah klaim
> pemilik repo. Perkiraan VRAM adalah hitungan dari jumlah parameter, bukan ukuran.
>
> **Efek samping.** Alat baca web menyimpan otomatis satu berkas pengaturan 1,7 KB (konfigurasi plat
> fast-plate-ocr, bukan bobot) ke folder sementara sesi, di luar repo.
>
> **Singkatan URL:** `gh:` = https://github.com/ · `raw:` = https://raw.githubusercontent.com/ ·
> `api:` = https://api.github.com/repos/ (lisensi SPDX + `pushed_at`) · `hf:` = https://huggingface.co/ ·
> `hfapi:` = https://huggingface.co/api/models/
>
> **Arti vonis:** `BOLEH-PRODUK` = lisensinya mengizinkan produk tertutup yang dijual · `RISET-SAJA` = hanya untuk
> belajar di lab (K15) · `DILARANG` = tidak boleh masuk produk (GPL, AGPL, bergantung ultralytics, non-komersial
> untuk produksi) · `BELUM-JELAS` = lisensi tidak dinyatakan atau tidak berhasil dibuka.

## Koreksi atas catatan lama

1. **fast-plate-ocr dan Indonesia:** README dan dokumentasinya memang tidak menyebut negara. Tetapi berkas
   `cct_s_v2_global_plate_config.yaml` (aset rilis, dibuka) memuat **"Indonesia"** di `plate_regions` (65 negara +
   "Unknown"), `max_plate_slots: 10`, alfabet `0-9A-Z_`, masukan 64×128 RGB. Akurasi pada plat Indonesia tidak
   disebut di mana pun.
2. **Frigate "tidak membaca kendaraan berhenti":** kalimat itu hanya ada di dokumentasi v0.16.0; dokumentasi
   sekarang berkata sebaliknya (bagian C).
3. **RF-DETR:** selain XL/2XL, varian kecil **Atto/Femto/Pico (7,4–8,4 juta parameter) juga PML 1.0**, bukan
   Apache. Yang Apache hanya N/S/M/L (30,5–33,9 juta parameter).
4. **Pendeteksi plat YOLOv9 (open-image-models, fast-alpr, Frigate):** pemeliharanya sendiri menyatakan dilatih
   dengan fork `WongKinYiu/yolov9` (GPL-3.0) dan tidak tahu apakah GPL berlaku pada bobot.
5. Sisanya (MIT/Apache/AGPL pada butir catatan lama) terkonfirmasi.

## A. Verifikasi butir catatan lama

| Nama + repo | Lisensi kode (bukti) | Lisensi bobot (bukti) | Dataset pelatih & lisensi | Aktivitas terakhir | ultralytics? | Vonis | Catatan |
|---|---|---|---|---|---|---|---|
| fast-alpr · gh:ankandrew/fast-alpr | MIT · raw:ankandrew/fast-alpr/master/LICENSE | Tak punya bobot sendiri; memakai dua paket di bawah | — | push 2026-03-16 (api), v0.4.0 | Tidak (pyproject dibuka: fast-plate-ocr, open-image-models, opencv) | Kode `BOLEH-PRODUK`; bawaan `BELUM-JELAS` | Pembungkus tipis; detektor bawaannya YOLOv9 bermasalah. |
| fast-plate-ocr · gh:ankandrew/fast-plate-ocr | MIT · raw:ankandrew/fast-plate-ocr/master/LICENSE | Tak ada berkas lisensi bobot. Pemelihara (8 Jun 2026): "everything is MIT and you can use commercially… any of the models/weights of fast-plate-ocr. No restrictions." · gh:ankandrew/open-image-models/issues/20. Issue #98 (12 Okt 2026) yang menanyakan hal ini belum dijawab | "custom dataset + synthetic data" (issue #89); tidak dipublikasikan, lisensi tak disebut | push 2026-03-14 (api), v1.1.0 | Tidak disebut di README | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Arsitektur CCT (XS/S), Keras 3, ekspor ONNX/TFLite/CoreML, latih ulang dari CSV. |
| open-image-models · gh:ankandrew/open-image-models | MIT · raw:ankandrew/open-image-models/main/LICENSE | Tidak dinyatakan. Pemelihara (14 Jun 2026): "I used [ankandrew/yolov9] (based on `WongKinYiu/yolov9`) with some modifications" · issues/22; (16 Des 2025): "I don't know if GPL applies to weights" · issues/14 | ~11–15 ribu gambar "scrapped from the web (mostly from free/open datasets)", anotasi manual (issues/3, /14); lisensi tak disebut | push 2026-07-27 (api), v0.6.0 | Tidak disebut di README (pyproject tidak dibuka) | Kode `BOLEH-PRODUK`; bobot YOLOv9 `BELUM-JELAS` (perlakukan dilarang) | Kode latih induk GPL-3.0 (raw:WongKinYiu/yolov9/main/LICENSE.md). Kini juga memuat ONNX RF-DETR COCO. |
| Frigate LPR · gh:blakeblackshear/frigate | MIT · raw:blakeblackshear/frigate/dev/LICENSE | Detektor: `yolov9-256-license-plates.onnx` dari gh:hawkeye217/yolov9-license-plates (label MIT; README: "Originally obtained from …ankandrew/open-image-models"). OCR: ONNX PaddleOCR (det v3/v5, cls, rec v4) dari gh:hawkeye217/paddleocr-onnx (Apache-2.0) | Detektor: sama dengan baris di atas. OCR: tak disebut | push 2026-10-12 (api), rilis 0.18.0 | Tidak terlihat di berkas LPR | Acuan; detektor `BELUM-JELAS` | Catatan lama benar: detektor YOLOv9 + OCR PaddleOCR. |
| PaddleOCR · gh:PaddlePaddle/PaddleOCR | Apache-2.0 · raw:PaddlePaddle/PaddleOCR/main/LICENSE | apache-2.0 · hf:PaddlePaddle/PP-OCRv5_mobile_rec | Tidak disebut | push 2026-09-16, v3.7.0 (11 Jun 2026) | Tidak | `BOLEH-PRODUK` | Data pelatih bobot tidak diungkap. |
| EasyOCR · gh:JaidedAI/EasyOCR | Apache-2.0 · raw:JaidedAI/EasyOCR/master/LICENSE | TIDAK DITEMUKAN pernyataan terpisah | Tidak dibuka | push 2025-12-05 (api) | Tidak | Kode `BOLEH-PRODUK` | Aktivitas melambat. |
| OpenALPR · gh:openalpr/openalpr | AGPL-3.0 · raw:openalpr/openalpr/master/LICENSE | — | — | push 2024-01-11 (api) | Tidak | `DILARANG` | Terkonfirmasi AGPL dan tidak aktif. |
| RF-DETR · gh:roboflow/rf-detr | Apache-2.0 · raw:roboflow/rf-detr/develop/LICENSE | N/S/M/L Apache-2.0; A/F/P/XL/2XL "PML 1.0" lewat `rfdetr_plus`, butuh akun Roboflow · raw:roboflow/rf-detr/develop/README.md · https://rfdetr.roboflow.com/latest/ | README hanya menyebut "COCO-pretrained"; Objects365 tak disebut. Backbone DINOv2: kode + bobot Apache-2.0 (gh:facebookresearch/dinov2) | push 2026-10-13 (api), 1.12.0.dev | Tidak (pyproject dibuka) | N–L `BOLEH-PRODUK`; A/F/P/XL/2XL `DILARANG` | https://roboflow.com/licensing: lisensi komersial berlaku "as long as you maintain your plan". |
| D-FINE · gh:Peterande/D-FINE | Apache-2.0 · raw:Peterande/D-FINE/master/LICENSE | apache-2.0 · hfapi:ustc-community/dfine-nano-coco (safetensors, 3,8 juta parameter) | COCO; ada varian Objects365. README: "Checkpoints trained or pretrained on Objects365 (*_obj365, *_obj2coco) may be subject to the Objects365 dataset terms" | push 2026-10-05 (api) | Tidak disebut | `BOLEH-PRODUK` (varian COCO saja) | N 4 juta, S 10 juta parameter; ekspor ONNX. |
| RT-DETR/v2 · gh:lyuwenyu/RT-DETR | Apache-2.0 · raw:lyuwenyu/RT-DETR/main/LICENSE | apache-2.0 · hfapi:PekingU/rtdetr_v2_r18vd (safetensors, 20,2 juta parameter) | COCO; ada varian COCO+Objects365 | push 2026-10-09 (api) | Tidak disebut | `BOLEH-PRODUK` | Varian terkecil 20 juta parameter, berat untuk N100. |
| YOLOX · gh:Megvii-BaseDetection/YOLOX | Apache-2.0 · raw:Megvii-BaseDetection/YOLOX/main/LICENSE | Tak ada pernyataan terpisah; `.pth` di GitHub Releases | COCO (tersirat di README) | push 2025-06-08 (api) | Tidak disebut | `BOLEH-PRODUK` | Nano 0,91 juta, Tiny 5,06 juta, S 9,0 juta parameter; ONNX/ncnn/OpenVINO. |

Syarat dataset: Objects365 "available for the academic purpose only", anotasi CC BY 4.0
(https://www.objects365.org/download.html). Syarat COCO: TIDAK DIBUKA (halaman tidak menampilkan isinya).

## C. Frigate dan kendaraan berhenti

- **Dokumentasi sekarang** (https://docs.frigate.video/configuration/license_plate_recognition; sama di
  raw:blakeblackshear/frigate/dev/docs/docs/configuration/license_plate_recognition.md): **"When a vehicle becomes
  stationary, LPR continues to run for a short time after to attempt recognition."**
- **Dokumentasi v0.16.0**
  (raw:blakeblackshear/frigate/v0.16.0/docs/docs/configuration/license_plate_recognition.md): **"However, LPR does
  not run on stationary vehicles."**
- Kalimat sebelumnya di keduanya: "For moving vehicles, Frigate continuously refines the recognition process,
  keeping the most confident result."

Catatan lama memakai kalimat versi lama; perilaku Frigate sudah berubah.

## B1. Mesin baca plat lain yang masih hidup

| Nama + repo | Lisensi kode | Lisensi bobot | Dataset pelatih | Aktivitas | ultralytics? | Vonis | Catatan |
|---|---|---|---|---|---|---|---|
| open-lpr · gh:faisalthaheem/open-lpr | Apache-2.0 (halaman repo + api) | apache-2.0 · hf:faisalthaheem/open-lpr-models | Detektor YOLOX-tiny dari `yolox_tiny.pth` COCO, dilatih pada "Simanno annotated plate corpus" + gambar komunitas yang dilabeli guru Qwen3-VL 8B; lisensi data tak disebut. Pembaca PP-OCRv5 dari hulu, bukan dilatih proyek | push 2026-10-06 | Tidak; kartu model: "Ultralytics YOLO weights are AGPL-3.0 and are not used anywhere in this project" | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Acuan terdekat rencana kita. Recall detektor 0,926; akurasi teks "not measured"; Indonesia tak disebut. |
| PP-Vehicle · gh:PaddlePaddle/PaddleDetection | Apache-2.0 (README) | Tidak disebut terpisah | Tidak disebut | berita terakhir 2024.10.1 | Tidak | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Plat lewat PP-OCRv3 (plat Tiongkok), atribut "10 vehicle colors and 9 models", suara terbanyak antar-frame. |
| HyperLPR · gh:szad670401/HyperLPR | Apache-2.0 (halaman repo) | Tidak disebut | Privat ("cannot be provided") | commit 2024-07-27 | Tidak | `BELUM-JELAS` | Hanya plat Tiongkok. |
| PlateRecognition · gh:pcb9382/PlateRecognition | MIT (halaman repo + api; berkas LICENSE gagal dibuka, 503) | Tidak disebut | Tidak disebut; data dijual 30 yuan | push 2026-09-02 | Folder yolov5/yolov7/yolov8; merujuk yolov5-face, yolov7-face, yolov8-face | `BELUM-JELAS` | Mengklaim mendukung Indonesia; 98,9–99,56% pada 72 ribu gambar uji milik sendiri. C++/TensorRT. |
| deep-license-plate-recognition · gh:parkpow/deep-license-plate-recognition | MIT (klien) | — | — | push 2026-09-04 | — | Di luar kategori | README: "does not contain the recognition models themselves"; butuh token/SDK Plate Recognizer berbayar. |
| NVIDIA TAO LPRNet · https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/lprnet | — | Syarat NGC (tak dibuka); "ready for commercial use" | 310 ribu plat AS (proprietary) + CCPD | — | Tidak | `BELUM-JELAS` | Hanya AS/Tiongkok; terenkripsi; wajib TAO/DeepStream/TensorRT. |
| CodeProject.AI-ALPR · gh:codeproject/CodeProject.AI-ALPR | TIDAK DITEMUKAN di halaman | — | — | tak terlihat | Tak terkonfirmasi | `BELUM-JELAS` | Memakai PP-OCRv3/v4. |
| ultimateALPR-SDK · gh:DoubangoTelecom/ultimateALPR-SDK | "Other" (api); teks tak dibuka | — | — | push 2025-11-05 | — | `BELUM-JELAS` | Tampak biner siap pakai. |
| Chinese_license_plate_detection_recognition · gh:we0091234/… | GPL-3.0 (api saja) | — | — | push 2026-06-05 | YOLOv5 | `DILARANG` | TIDAK DIBUKA (hanya hasil API). |
| main-gate-alpr · gh:TDiblik/main-gate-alpr | AGPL-3.0 (api saja) | — | — | diarsipkan | YOLOv8 | `DILARANG` | Kasus gerbang + kamera Hikvision; TIDAK DIBUKA. |

## B2. Repo dan model khusus Indonesia

| Nama | Lisensi | Bobot/dataset disertakan | Akurasi yang diklaim | Aktivitas | ultralytics? | Vonis | Catatan |
|---|---|---|---|---|---|---|---|
| hf:carlravel/indonesian-plate-recognizer-yolo11 (+ `-detector-`) | MIT (kartu) | `.pt` + `.onnx`; data Kaggle "Indonesian License Plate Dataset" (Juan Thomas Wijaya), lisensi tak terverifikasi | mAP50 98,40%, P 96,24%, R 96,34% pada split validasi (deteksi karakter, bukan akurasi plat utuh) | dibuat 2026-08-28 | Ya (YOLO11n) | `DILARANG` | Pembanding lab. |
| hf:wuriyanto/yolo8-indonesian-license-plate-detection | MIT (kartu) | `model.pt`; Kaggle "Indonesian Plate Number from Multi Sources" | Tak ada angka | 2025-09-03 | Ya (YOLOv8) | `DILARANG` | — |
| gh:rzr06/Indonesia-ALPR | GPL-3.0 (README) | Bobot `.pt`/`.pth` di Google Drive; dataset tak ada | Tak ada angka | push 2026-06-27 | Ya (YOLOv8-OBB) | `DILARANG` | Ide: kotak miring + luruskan perspektif + CRNN-CTC + pelacak centroid. |
| gh:xzars-git/plate-recognition | "MIT" di README; berkas lisensi tak terlihat | ONNX/`.pt` disebut; 4.396 latih / 1.104 validasi, sumber tak disebut | mAP50 81,6% (data uji tak dinyatakan) | push 2026-03-24 | Ya (YOLOv11n) | `DILARANG` | Pengklasifikasi warna plat 3 kelas masih dikerjakan. |
| gh:Grimorst/indonesian-plate-detector | Tanpa lisensi (dinyatakan README) | `.pt` disertakan | Tak ada | push 2026-09-22 | Ya (YOLO26) + PaddleOCR | `DILARANG` | — |
| gh:MayumiMi/indonesian-automatic-license-plate-recognition | Tak terlihat | Folder model ada, isi tak terbaca | Tak ada | push 2025-08-05 | Tak terkonfirmasi | `BELUM-JELAS` | fast-plate-ocr + akses gerbang servo; belum selesai. |
| gh:CallmeSetia/ALPR-Rpi-HousingArea | Apache-2.0 (README) | Tak dijelaskan | Tak ada | push 2023-06-07 | Tidak ("Yolo Tiny" + PyTesseract) | Acuan | Kasus sama: gerbang perumahan, Raspberry Pi 4, sensor jarak, servo. |
| gh:muchlisinadi/ALPR-Indonesia | MIT | Data KNN disertakan | Tak ada | diarsipkan 6 Okt 2024 | Tidak (OpenCV + KNN) | Acuan usang | Hanya plat hitam. |
| gh:img88/ALPR_IndonesiaPlateNumber_ComputerVision | MIT | `dataset.zip` karakter, asal tak disebut | "58/60 plates detected", siang, jarak ±1 m | push 2021-03-07 | Tidak (kontur + CNN) | Acuan usang | — |
| gh:Veran-35/Indonesian-License-plate-recognition | MIT | `dataset.zip` | Tak ada | push 2025-09-20 | Tidak (CNN TensorFlow) | Acuan | — |
| gh:Refrillygt/plat-id | MIT | Bukan model | — | push 2026-09-17 | — | `BOLEH-PRODUK` | Pustaka TS/JS validasi, urai, dan cari kode wilayah; sumber data wilayah tak dikutip. |
| hf:ziyadazz/OCR-PLAT-NOMOR-INDONESIA | Tanpa lisensi, kartu kosong | safetensors 0,3 miliar parameter | Tak ada | 2023-12-10 | Tidak | `BELUM-JELAS` | — |
| Dataset INDO-ALPR · https://data.mendeley.com/datasets/j3256db3fz/1 | CC BY 4.0 | 6.174 gambar (ITS, 7 Sep 2023) | — | — | — | `BOLEH-PRODUK` (atribusi) | Jenis anotasi, warna plat, dan siang/malam tidak disebut. |
| Dataset Roboflow License-Plate-Indonesia · https://public.roboflow.com/object-detection/license-plate-indonesia | CC BY 4.0 | Jumlah gambar tak disebut | — | — | — | `BELUM-JELAS` | Ringkasan pencarian menyebut ekspornya belum publik. |

- Hanya terlihat di daftar API pencarian GitHub (TIDAK DIBUKA): ukayaj620/monopol (MIT, 2022),
  Firdauzfan/AutomaticLicensePlateRecognition (MIT, 2018), iqbalpurba26/Indonesia-ALPR-Using-YOLOv8,
  MohPras/YOLOv8-Indonesian_Plate_Reader, lejar14/Deteksi-Plat-Nomor, ade-m/DeteksiPlatNomorYOLO, dan dua proyek
  kuliah yang memakai VLM lewat LM Studio.
- Makalah JIKI 2025 (https://jiki.cs.ui.ac.id/index.php/jiki/article/view/1320, Gaussian YOLOv7 + STN): recall
  rektifikasi 83,8%; tanpa tautan kode atau dataset.
- Tidak ada repo Indonesia yang sekaligus permisif, bebas ultralytics, menyertakan bobot, dan melaporkan akurasi
  pada set uji yang jelas (motor + mobil, hitam + putih, siang + malam).

## B3. OCR ringan yang bisa dilatih ulang

| Nama | Lisensi kode | Lisensi bobot | Dataset pelatih | Ukuran | ONNX? | Vonis | Catatan |
|---|---|---|---|---|---|---|---|
| fast-plate-ocr (CCT) | MIT | lihat A | lihat A | XS/S; jumlah parameter tak tertulis | Ya (juga TFLite, CoreML) | Kode `BOLEH-PRODUK` | Khusus plat, keluaran slot tetap. |
| PP-OCRv5/v4 rec · https://www.paddleocr.ai/latest/en/version3.x/module_usage/text_recognition.html | Apache-2.0 | apache-2.0 (hf:PaddlePaddle/PP-OCRv5_mobile_rec) | Tidak disebut | v5 mobile 16 MB; `en_` v5 7,5 MB; `latin_` v5 14 MB; v4 mobile 10,5 MB | Ya, lewat panduan PaddleX | `BOLEH-PRODUK` | Latih ulang dengan `tools/train.py`. |
| RapidOCR · gh:RapidAI/RapidOCR | Apache-2.0 | README: model "derived from official PaddleOCR models"; "Copyright in the upstream model weights is held by Baidu…" | ikut hulu | — | Ya (ONNX Runtime, OpenVINO, dll.) | `BOLEH-PRODUK` | commit 2026-10-13. |
| SVTRv2 / OpenOCR · gh:Topdu/OpenOCR | Apache-2.0 (halaman repo) | Tak disebut terpisah | Union14M-L-Filter (data nyata; lisensi tak disebut) | model mobile/server; ukuran tak tertulis | Ya (sejak 2025.03.23) | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Ada panduan fine-tune; pembaruan 2026.09.21. |
| PARSeq · gh:baudm/parseq | Apache-2.0 (bagian ABINet BSD, CRNN MIT) | Tak disebut terpisah | Tidak dinyatakan per bobot; repo memakai campuran data sintetis + data nyata | parseq 23,8 juta parameter; ada varian tiny | "Yes, see Issue #12" | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | commit 2024-04-24. |
| docTR · gh:mindee/doctr · OnnxTR · gh:felixdittrich92/OnnxTR | Apache-2.0 (keduanya) | Tak disebut | Tak disebut | CRNN, SAR, MASTER, ViTSTR, PARSeq, VIPTR | OnnxTR berjalan tanpa PyTorch/TF | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | docTR v1.1.0, commit 2026-10-09; OnnxTR v0.9.0. |
| TrOCR · gh:microsoft/unilm/tree/master/trocr | MIT (raw:microsoft/unilm/master/LICENSE) | Tanpa tag lisensi (hfapi:microsoft/trocr-small-printed) | SROIE (varian printed) | small 62 juta, base 334 juta parameter | Tidak diperiksa | `BELUM-JELAS` | Menurut sub-agen terlalu berat untuk N100. |

## B4. Pendeteksi permisif selain RF-DETR

| Nama | Lisensi kode | Lisensi bobot | Dataset | Aktivitas | Vonis | Catatan |
|---|---|---|---|---|---|---|
| DEIM v1 · gh:Intellindust-AI-Lab/DEIM | Apache-2.0 · raw:…/DEIM/main/LICENSE ("DEIM is licensed under the Apache License") | Tak terpisah; `.pth` di Google Drive | COCO; hanya varian X yang Objects365 | push 2026-03-24 | `BOLEH-PRODUK` | N ~4 juta, S ~10 juta parameter. |
| **DEIMv2** · gh:Intellindust-AI-Lab/DEIMv2 | "DEIMv2 License" · raw:…/DEIMv2/main/LICENSE.md: "Commercial Use of the DEIMv2 Materials is **not permitted** under this License." | sama | COCO; backbone DINOv3 | push 2026-08-24 | `RISET-SAJA` | Atto 0,5 juta sampai S 9,7 juta parameter; menarik tapi non-komersial. |
| RT-DETRv4 · gh:RT-DETRs/RT-DETRv4 | Apache-2.0 (api + README) | Tak terpisah; Google Drive | COCO; guru distilasi DINOv3 ViT-B/16 | push 2026-07-06 | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | DINOv3 berlisensi "DINOv3 License" dan ber-gerbang; teksnya tidak dibuka. |
| NanoDet-Plus · gh:RangiLyu/nanodet | Apache-2.0 | Tak terpisah | COCO | berita terakhir 2023.01.20 | `BOLEH-PRODUK` | 1,17 juta parameter, 2,3 MB (FP16). |
| DAMO-YOLO · gh:tinyvision/DAMO-YOLO | Apache-2.0 | Tak terpisah | COCO | v0.3.1, 2023/04/12 | `BOLEH-PRODUK` | Ns 1,41 juta, Nm 2,71 juta, Nl 5,69 juta parameter. |
| PP-YOLOE+ / PP-PicoDet · gh:PaddlePaddle/PaddleDetection | Apache-2.0 | Tak terpisah | COCO | 2024.10.1 | `BOLEH-PRODUK` | — |
| YOLO (MIT) v7/v9 · gh:MultimediaTechLab/YOLO | MIT ("official YOLO model implementation with an MIT License") | Tidak dibahas | Tidak dibahas | tak terlihat | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Jalur arsitektur YOLOv9 tanpa kode GPL. |
| LW-DETR · gh:Atten4Vis/LW-DETR | Apache-2.0 (api saja) | TIDAK DIBUKA | — | push 2025-02-18 | `BELUM-JELAS` | Hanya metadata API. |
| YOLO-NAS · raw:Deci-AI/super-gradients/master/LICENSE.YOLONAS.md | — | "you may not use the Software for any commercial use, including in connection with any models used in a production" | — | — | `DILARANG` | — |
| YOLOv9 asli · gh:WongKinYiu/yolov9 | GPL-3.0 | — | — | — | `DILARANG` | — |

## B5. Pelacak

| Nama | Lisensi (bukti) | Aktivitas | ultralytics? | Vonis | Catatan |
|---|---|---|---|---|---|
| roboflow/trackers · gh:roboflow/trackers | Apache-2.0 · raw:roboflow/trackers/main/LICENSE; README: "Apache 2.0, no copyleft. Ship it inside closed-source products." | commit 2026-10-12 | Tidak disebut | `BOLEH-PRODUK` | SORT, ByteTrack, OC-SORT, BoT-SORT, C-BIoU, McByte; "re-implemented from the original paper"; inti tanpa torch. |
| ByteTrack · gh:ifzhang/ByteTrack | MIT · raw:ifzhang/ByteTrack/main/LICENSE | commit 2022-12-11 | Tidak | `BOLEH-PRODUK` | Tidak dirawat. |
| OC-SORT · gh:noahcao/OC_SORT | MIT (README) | berita 03/19/2026 | Tidak | `BOLEH-PRODUK` | Berbasis YOLOX + ByteTrack. |
| norfair · gh:tryolabs/norfair | BSD-3-Clause | commit 2025-04-30 (v2.3.0) | Tidak | `BOLEH-PRODUK` | — |
| supervision · gh:roboflow/supervision | MIT (halaman repo; teks tak dibuka) | — | Konektor opsional | `BOLEH-PRODUK` | — |
| BoT-SORT · gh:NirAharon/BoT-SORT | MIT (halaman repo) | — | Tidak | `BELUM-JELAS` | README: meminjam dari YOLOv7 (GPL) dan FastReID. |
| BoxMOT · gh:mikel-brostrom/boxmot | AGPL-3.0 | — | Tak terkonfirmasi | `DILARANG` | — |
| SORT asli · raw:abewley/sort/master/LICENSE · DeepSORT · raw:nwojke/deep_sort/master/LICENSE | GPL-3.0 (keduanya) | — | — | `DILARANG` | — |

## B6. Ciri kendaraan, pencocok rupa (re-ID), dan dataset

| Nama | Lisensi kode | Lisensi bobot / syarat | Dataset | Vonis | Catatan |
|---|---|---|---|---|---|
| FastReID · gh:JDAI-CV/fast-reid | Apache-2.0 (README) | Tak dinyatakan; `.pth` di rilis v0.1.1 | VeRi, VehicleID, VERI-Wild (semua non-komersial) | Kode `BOLEH-PRODUK`; bobot `RISET-SAJA` | commit 2024-07-15; ekspor ONNX/TensorRT. |
| torchreid · gh:KaiyangZhou/deep-person-reid | MIT · raw:…/deep-person-reid/master/LICENSE | Tak dinyatakan; Google Drive / Hugging Face | Dataset orang | Kode `BOLEH-PRODUK`; bobot `RISET-SAJA` | Fokus orang, bukan kendaraan. |
| OpenVINO vehicle-attributes-recognition-barrier-0039 · gh:openvinotoolkit/open_model_zoo | Apache-2.0 (repo) | ~~Tak dinyatakan di halaman model~~ Dikoreksi 19 Okt: Apache-2.0 (`license:` di model.yml menunjuk LICENSE repo) | Tak disebut | ~~`BELUM-JELAS`~~ `BOLEH-PRODUK` (19 Okt, [`2026-10-19-catatan-merek-warna-mobil.md`](2026-10-19-catatan-merek-warna-mobil.md)) | 7 warna, 4 jenis; warna 81,15%, jenis 87,56%; 0,626 juta parameter. Repo "in maintenance mode". |
| PP-Vehicle attribute | Apache-2.0 | Tak dinyatakan | ~~Tak disebut~~ VeRi, non-komersial (dikoreksi 19 Okt) | ~~`BELUM-JELAS`~~ bobot `RISET-SAJA`, menunggu P14 (19 Okt) | 10 warna, 9 jenis. |
| SigLIP2 · hfapi:google/siglip2-base-patch16-224 | — | apache-2.0, safetensors | — | `BOLEH-PRODUK` | Pelabel tanpa contoh (zero-shot) di lab; 375 juta parameter. |
| CompCars · https://mmlab.ie.cuhk.edu.hk/datasets/comp_cars/index.html | — | "available for non-commercial research purposes only" | 163 merek, 1.716 model | `RISET-SAJA` | — |
| VeRi-776 · gh:JDAI-CV/VeRidataset | — | Non-komersial; minta lewat email | 50 ribu+ gambar, 776 kendaraan | `RISET-SAJA` | — |
| PKU VehicleID · https://www.pkuml.org/resources/pku-vehicleid.html | — | "NO COMERCIAL USE is allowed"; hanya email institusi | 221.763 gambar | `RISET-SAJA` | Kita mungkin tak memenuhi syarat akses. |
| VMMRdb · gh:faezetta/VMMRdb | "MIT" di halaman repo (teks tak dibuka) | — | 9.170 kelas, 291.752 gambar, AS 1950–2016 | `BELUM-JELAS` | Hak atas gambar tak jelas; pasar AS. |
| Stanford Cars | — | TIDAK TERVERIFIKASI (situs asli tak dibuka; salinan di Hugging Face tanpa lisensi; ringkasan pencarian: non-komersial) | — | `BELUM-JELAS` | — |
| Dataset mobil pasar Indonesia | — | — | ~~**TIDAK DITEMUKAN**~~ Dikoreksi 19 Okt: ada di Roboflow, tetapi pengunggahnya anonim dan asal gambarnya tidak disebut; dataset Asia berizin CC BY 4.0 dari universitas ada (VMID, VTID2, VMMR Pakistan) | — | Yang muncul hanya Pakistan dan India. |

## B7. Model bahasa-gambar lokal untuk pelabelan otomatis

Perkiraan VRAM adalah hitungan dari jumlah parameter (BF16, 2 byte per parameter), bukan pengukuran.

| Model | Lisensi bobot (bukti) | Parameter | Muat di 8 GB? | `trust_remote_code`? | Vonis | Catatan |
|---|---|---|---|---|---|---|
| Qwen3-VL-2B-Instruct | apache-2.0 · hfapi:Qwen/Qwen3-VL-2B-Instruct | 2,13 miliar (~4,3 GB) | Ya | Tidak | `BOLEH-PRODUK` (alat lab) | safetensors; OCR "32 languages", bahasa Indonesia tak disebut. |
| Qwen3-VL-4B / 8B-Instruct | apache-2.0 · hfapi | 4,44 / 8,77 miliar | 4B perlu kuantisasi; 8B sempit walau 4-bit | Tidak | `BOLEH-PRODUK` (alat lab) | — |
| Qwen3.5-2B / 4B (Feb–Mar 2026) | apache-2.0 · hfapi:Qwen/Qwen3.5-2B, /Qwen3.5-4B | 2,27 / 4,66 miliar | 2B ya; 4B perlu kuantisasi | Tidak | `BOLEH-PRODUK` (alat lab) | Butuh transformers dari cabang main; "201 languages". |
| Gemma 4 E2B-it (Mar 2026) | apache-2.0, tanpa gerbang · hfapi:google/gemma-4-E2B-it | 5,12 miliar | Perlu kuantisasi (GGUF q4_0 resmi ada) | Tidak | `BOLEH-PRODUK` (alat lab) | — |
| Florence-2-base | MIT · hfapi:microsoft/Florence-2-base (tag `custom_code`, ada `pytorch_model.bin`); hfapi:florence-community/Florence-2-base (tanpa kode kustom, safetensors saja) | 0,23 miliar | Ya | Asli: ya; versi komunitas: tidak | Pakai versi komunitas | — |
| InternVL3_5-2B-HF | apache-2.0 · hfapi:OpenGVLab/InternVL3_5-2B-HF | 2,35 miliar | Ya | Tag `custom_code` ada tapi tak ada berkas `.py` | `BELUM-JELAS` | Perlu dicek ulang. InternVL3-2B-hf berlisensi "other" (qwen). |
| SmolVLM2-2.2B | apache-2.0 · hfapi | 2,25 miliar | Ya | Tidak | `BOLEH-PRODUK` (alat lab) | — |
| Qwen2.5-VL-7B | apache-2.0 · hfapi | 8,29 miliar | Hanya 4-bit | Tidak | `BOLEH-PRODUK` (alat lab) | — |
| **Qwen2.5-VL-3B** | "Qwen RESEARCH LICENSE AGREEMENT", "FOR NON-COMMERCIAL PURPOSES ONLY" · hf:Qwen/Qwen2.5-VL-3B-Instruct/raw/main/LICENSE | 3,75 miliar | Ya | Tidak | `RISET-SAJA` | — |
| PaliGemma2-3b-pt-448 · Gemma 3 4b-it | lisensi "gemma", gerbang manual · hfapi | 3,03 / 4,30 miliar | Ya / perlu kuantisasi | Tidak | `BELUM-JELAS` | Syarat Gemma tak dibuka. |
| MiniCPM-V 4.5 / 2.6 | 4.5: apache-2.0; 2.6: tanpa tag lisensi, ber-gerbang · hfapi | 8,7 / 8,1 miliar | Hanya 4-bit | **Ya** (7 berkas `.py`) | Terlarang aturan repo | — |
| moondream2 · PaddleOCR-VL · DeepSeek-OCR | apache-2.0 / apache-2.0 / mit · hfapi (DeepSeek-OCR hanya dari daftar) | 1,93 / 0,96 miliar / tak diperiksa | Ya | **Ya** (kode kustom) | Terlarang aturan repo | — |

## Temuan terpenting untuk keputusan desain

1. **Detektor plat siap pakai dari fast-alpr, open-image-models, dan Frigate berasal dari kode latih GPL-3.0**, dan
   pemeliharanya sendiri ragu. Detektor produk harus dilatih sendiri di atas basis permisif.
2. **Untuk kotak N100, pilihan Apache yang ringan adalah YOLOX-Nano/Tiny, NanoDet-Plus, DAMO-YOLO-N, dan D-FINE-N /
   DEIM v1-N.** RF-DETR yang Apache mulai dari 30,5 juta parameter; varian kecilnya PML dan terikat langganan
   Roboflow.
3. **DEIMv2 non-komersial**, dan bobot berlabel Objects365 terikat syarat "academic purpose only". Pakai checkpoint
   COCO saja atau latih dari awal.
4. **fast-plate-ocr adalah kandidat OCR terkuat:** kode MIT, bisa dilatih ulang, ekspor ONNX, dan Indonesia ada di
   daftar wilayah model global v2. Namun lisensi bobot hanya pernyataan di issue, data pelatih tidak diungkap, dan
   akurasi pada plat kita belum diukur. Cadangannya PP-OCRv5 mobile rec (Apache, 7,5–16 MB).
5. **Frigate kini tetap membaca sebentar setelah kendaraan berhenti.** Ini relevan untuk gerbang, karena kendaraan
   memang berhenti di depannya.
6. **Pelacak:** roboflow/trackers paling bersih (Apache, implementasi ulang dari makalah, aktif). Hindari BoxMOT
   (AGPL) serta SORT dan DeepSORT asli (GPL-3.0).
7. **Tidak ada repo Indonesia yang layak jadi komponen produk.** Hampir semua memakai ultralytics, tanpa lisensi,
   atau visi komputer klasik. Yang berguna: dataset INDO-ALPR (CC BY 4.0), pustaka aturan format `plat-id` (MIT),
   dan repo gerbang perumahan sebagai acuan.
8. **Merek/model/warna dan pencocok rupa:** semua dataset besar non-komersial dan tidak ada dataset mobil pasar
   Indonesia, jadi pengenal produk harus dari data sendiri. Qwen3-VL-2B atau Qwen3.5-2B (Apache, tanpa kode kustom,
   muat di 8 GB) bisa jadi pelabel otomatis di lab.

## Yang tidak berhasil diverifikasi

- Syarat COCO, teks PML 1.0, teks DINOv3 License, syarat Gemma, dan syarat asli Stanford Cars.
- Lisensi bobot EasyOCR, bobot YOLOX (tak ada pernyataan terpisah), dan model Intel di Open Model Zoo.
- Lisensi dataset Kaggle Indonesia (halaman Kaggle tak terbaca).
- Berkas LICENSE pcb9382 (503), lisensi CodeProject.AI-ALPR dan ultimateALPR-SDK.
- Dependensi open-image-models, D-FINE, RT-DETR, dan YOLOX: hanya README yang dibaca, bukan berkas dependensinya.
- Dataset pelatih RF-DETR di luar "COCO-pretrained", serta isi dan lisensi "Simanno corpus" milik open-lpr.
- Tahun pada beberapa tanggal rilis tidak ditampilkan (fast-alpr v0.4.0 "15 Mar", Frigate 0.18.0 "12 Sep"); tahun
  disimpulkan dari `pushed_at`.
- Repo Indonesia di daftar "TIDAK DIBUKA" dan baris bertanda "api saja".
- Qwen2.5-VL-3B: satu daftar agregat menampilkannya "apache-2.0", tetapi API model dan berkas LICENSE-nya
  menyatakan lisensi riset; yang dipegang adalah yang kedua.

## Bendera rantai pasok

- **Unduhan otomatis tanpa checksum:** `hub.py` di open-image-models dan fast-plate-ocr mengambil ONNX dari aset
  rilis GitHub saat pertama dipakai, hanya memeriksa HTTP 200, lalu menyimpan di `~/.cache/…`. Frigate mengunduh
  model LPR dari `hawkeye217/*` di `refs/heads/master`, tidak dikunci ke commit.
- **Bobot format pickle:** `.pth` YOLOX, D-FINE, DEIM, RT-DETRv4, FastReID; `checkpoints/best_ckpt.pth` di
  open-lpr-models; `pytorch_model.bin` di TrOCR dan Florence-2 asli; `.pt` semua model Indonesia berbasis
  ultralytics.
- **Bobot di Google Drive / Quark tanpa jaminan keutuhan:** DEIM, DEIMv2, RT-DETRv4, model zoo torchreid, rzr06.
- **Kode jarak jauh:** tag `custom_code` pada Florence-2 asli, MiniCPM-V, moondream2, PaddleOCR-VL, DeepSeek-OCR;
  `torch.hub.load('baudm/parseq', …)` menjalankan `hubconf.py` dari repo.
- **Terikat akun atau gerbang:** RF-DETR Plus (akun Roboflow), PaliGemma2 dan Gemma 3 (persetujuan manual), DINOv3
  (permintaan akses), TAO LPRNet (terenkripsi).
- **Contoh baik:** open-lpr mengunci revisi Hugging Face dan memeriksa checksum. Repo safetensors saja tanpa kode
  kustom: Qwen3-VL, Qwen3.5, `ustc-community/dfine-*`, `PekingU/rtdetr_v2_*`, `florence-community/Florence-2-base`.
