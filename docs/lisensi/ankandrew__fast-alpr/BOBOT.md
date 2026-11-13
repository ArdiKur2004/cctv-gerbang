# Izin bobot dan bahan latih: fast-alpr @ aca4ecd

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | tidak punya bobot sendiri | `pyproject.toml` |
| Bahan latih bobot | tidak berlaku | — |
| Izin bahan latih | tidak berlaku | — |
| Bergantung pada `ultralytics` | tidak. Dependensi: `fast-plate-ocr>=1.1.0`, `open-image-models>=0.5.1`, `opencv-python-headless>=4.9.0.80` | `pyproject.toml` |
| Format bobot | memakai bobot ONNX milik dua dependensinya | — |
| Unduhan otomatis saat dipakai | lewat dua dependensinya, keduanya tanpa pemeriksaan keutuhan | lihat `BOBOT.md` keduanya |

Keterangan: pembungkus tipis. Dijalankan apa adanya, ia memakai bobot dua dependensinya, yang keduanya bervonis `BELUM-JELAS`.
