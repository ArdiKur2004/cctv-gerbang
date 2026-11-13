# Izin bobot dan bahan latih: yolox @ 4197784

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | tidak dinyatakan. README memuat tabel bobot dengan tautan unduh, tanpa keterangan izin | `README.md` baris 30–62 |
| Bahan latih bobot | "Reproduce our results on COCO" | `README.md` baris 106–114 |
| Izin bahan latih | tidak dinyatakan | — |
| Bergantung pada `ultralytics` | tidak | `requirements.txt`, `setup.py` |
| Format bobot | pickle (`.pth`) | `yolox/models/build.py` |
| Unduhan otomatis saat dipakai | ya, lewat `load_state_dict_from_url`; pemeriksaan keutuhan tidak terlihat | `yolox/models/build.py:57` |
