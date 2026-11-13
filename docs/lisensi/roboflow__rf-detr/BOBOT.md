# Izin bobot dan bahan latih: rf-detr @ 45cb80c

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | Tabel model menandai RF-DETR-N, -S, -M, -L "Apache 2.0" dan RF-DETR-XL, -2XL "PML 1.0". Bagian License: "The open-source `rfdetr` package and Apache-designated model weights are licensed under Apache License 2.0." dan "Plus components, including the `rfdetr_plus` extension and RF-DETR-XL / RF-DETR-2XL detection models, are licensed under PML 1.0." | `README.md` baris 63–68 dan bagian "License" |
| Bahan latih bobot | Tolok ukur dilaporkan pada "Microsoft COCO and RF100-VL". Bahan yang melatih tiap bobot tidak dinyatakan per berkas. Daftar bobot memuat berkas bernama `rf-detr-base-o365.pth` | `README.md` baris 50; `src/rfdetr/assets/model_weights.py` |
| Izin bahan latih | tidak dinyatakan | — |
| Bergantung pada `ultralytics` | tidak | `pyproject.toml` |
| Format bobot | pickle (`.pth`) | `src/rfdetr/assets/model_weights.py` |
| Unduhan otomatis saat dipakai | ya, dari `storage.googleapis.com/rfdetr/…`; MD5 diperiksa. Backbone DINOv2 diunduh dari Hugging Face lewat `from_pretrained` | `src/rfdetr/utilities/files.py`; `src/rfdetr/models/backbone/dinov2.py` |

Keterangan: di cabang `develop` (lebih baru dari commit ini) README juga menandai ukuran Atto, Femto, dan Pico sebagai PML 1.0
(dibaca agen 13 Okt). Yang mengikat di sini adalah commit yang dikunci.
