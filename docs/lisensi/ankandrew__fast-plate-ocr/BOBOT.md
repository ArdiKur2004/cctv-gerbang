# Izin bobot dan bahan latih: fast-plate-ocr @ 9ce7a5b

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | tidak dinyatakan. Repo tidak punya berkas izin untuk bobot, dan README tidak menyebutnya | `README.md` |
| Bahan latih bobot | tidak dinyatakan | `README.md` |
| Izin bahan latih | tidak dinyatakan | — |
| Bergantung pada `ultralytics` | tidak | `pyproject.toml` |
| Format bobot | ONNX | `fast_plate_ocr/inference/hub.py` |
| Unduhan otomatis saat dipakai | ya, dari `https://github.com/ankandrew/cnn-ocr-lp/releases/download` ke `~/.cache`; hanya kode HTTP yang diperiksa, **tanpa pemeriksaan keutuhan** | `fast_plate_ocr/inference/hub.py` baris 80–150 |

Keterangan:
- **Indonesia tercantum** di daftar wilayah konfigurasi plat Latin: `'Gibraltar', 'Greece', 'Guernsey', 'Hungary', 'Iceland',
  'Indonesia', 'Ireland', …` (`config/latin_plate_config_v2.yaml` baris 22). Konfigurasi itu juga menetapkan `max_plate_slots: 10`,
  alfabet `0-9A-Z_`, dan masukan 64×128. Akurasi pada plat Indonesia tidak dinyatakan di mana pun.
- Menurut catatan survei 13 Okt, pemelihara menulis di sebuah issue repo lain bahwa bobotnya boleh dipakai komersial. Itu
  keterangan, bukan berkas izin, dan tidak dibaca ulang di sini.
- **Dibaca ulang 15 Okt 2026 (Rencana 9), dari GitHub:** pernyataan pemelihara ada di
  [open-image-models#20](https://github.com/ankandrew/open-image-models/issues/20#issuecomment-4653891541) (komentar
  `ankandrew`, OWNER, 8 Jun 2026): "Hi, from my end everything is MIT and you can use commercially, that includes source
  code here and any of the models/weights of https://github.com/ankandrew/fast-plate-ocr. No restrictions." Issue
  [fast-plate-ocr#98](https://github.com/ankandrew/fast-plate-ocr/issues/98) (12 Okt) yang menanyakan izin bobot belum
  dijawab. Rilis `arg-plates` juga memuat bobot `.keras` (dikunci di `tools/vendor.lock.json`). Permintaan izin
  tertulis: `docs/izin/2026-10-15-draf-izin-fast-plate-ocr.md` (draf, belum dikirim).
