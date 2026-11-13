# Audit statis: `fast-plate-ocr`

- Commit: `9ce7a5b64a939aa421c243b331d42e6bc25ffd44` · berkas kode dipindai: **74** · dilewati: 0
- TINGGI: **0** · SEDANG: **2** · INFO: 1

## Ringkasan per aturan

| Aturan | Tingkat | Jumlah | Arti |
|---|---|---|---|
| `pustaka-jaringan` | SEDANG | 2 | kode yang bisa membuka koneksi jaringan |
| `unduh-otomatis` | INFO | 1 | mengunduh bobot/berkas saat berjalan (periksa sumber & hash) |

## Domain yang disebut di KODE

- **Perlu dicek (bukan domain umum):** `keras.io` (3) · `yamllint.readthedocs.io` (1) · `docs.astral.sh` (1) · `upload.wikimedia.org` (1) · `docs.python.org` (1) · `typing-extensions.readthedocs.io` (1) · `ankandrew.github.io` (1)
- Domain umum: `github.com` (8) · `arxiv.org` (4) · `pypi.org` (2) · `raw.githubusercontent.com` (1)

## Berkas biner / bobot (0)


## Temuan

### `pustaka-jaringan` — SEDANG (2)
- `fast_plate_ocr/inference/hub.py:8` — `import urllib.request`
- `test/fast_lp_ocr/inference/test_hub.py:8` — `import requests`

### `unduh-otomatis` — INFO (1)
- `examples/tutorial_fine_tune_plate_model.ipynb:sel 39` — `!wget https://upload.wikimedia.org/wikipedia/commons/7/71/2020_Renault_Logan_Intens_%28Colombia%29_front_view_02.png \`

> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut
> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.

## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| tidak ada temuan TINGGI | — | — | — |

**Unduhan otomatis:** `fast_plate_ocr/inference/hub.py` (`download_model`, baris 98–150) mengunduh model ONNX dan berkas
konfigurasinya dari `https://github.com/ankandrew/cnn-ocr-lp/releases/download` (repo lain milik pemelihara yang sama) ke
`~/.cache/<nama-model>` saat model pertama dipakai. Yang diperiksa hanya kode HTTP 200; **tidak ada pemeriksaan keutuhan**.
**Pemindai tidak menandai jalur ini**, karena polanya tidak mengenal `urllib.request.urlopen`. Di lab tanpa jaringan jalur ini
gagal; bila kelak dipakai, modelnya harus diunduh lewat pintu unduh berkas dengan SHA-256 yang dicatat.
**Bergantung pada `ultralytics`:** tidak (`pyproject.toml`).
**Batas:** pemindai statis hanya petunjuk; berkas yang tidak ditandai tidak dibaca baris demi baris.
