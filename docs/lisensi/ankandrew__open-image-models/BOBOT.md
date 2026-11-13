# Izin bobot dan bahan latih: open-image-models @ eaeb588

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | tidak dinyatakan. README hanya memuat lencana izin repo | `README.md` baris 13 |
| Bahan latih bobot | tidak dinyatakan. Model bernama `yolo-v9-…-license-plate-end2end`, dan README mengutip makalah YOLOv9 | `README.md` baris 86–91 dan 150 |
| Izin bahan latih | tidak dinyatakan | — |
| Bergantung pada `ultralytics` | tidak | `pyproject.toml` |
| Format bobot | ONNX | `open_image_models/detection/core/hub.py` |
| Unduhan otomatis saat dipakai | ya, dari `https://github.com/ankandrew/open-image-models/releases/download/assets`; **tanpa pemeriksaan keutuhan** | `open_image_models/detection/core/hub.py` baris 135–196 |

Keterangan: di issue #14 repo ini pemelihara menulis "I don't know if GPL applies to weights (not using any actual GPL code)"
(dibaca agen 13 Okt). Menurut catatan survei, di issue #22 ia menyebut bobotnya dilatih dengan turunan `WongKinYiu/yolov9`, yang
berizin GPL-3.0; issue #22 tidak dibaca ulang di sini. Selama pemeliharanya sendiri ragu, bobot ini tidak dianggap boleh.
