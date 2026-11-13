# Audit statis: `open-image-models`

- Commit: `eaeb5880681695dcafb470c1d2b9ba7dc6de9a49` · berkas kode dipindai: **45** · dilewati: 0
- TINGGI: **0** · SEDANG: **2** · INFO: 0

## Ringkasan per aturan

| Aturan | Tingkat | Jumlah | Arti |
|---|---|---|---|
| `pustaka-jaringan` | SEDANG | 2 | kode yang bisa membuka koneksi jaringan |

## Domain yang disebut di KODE

- **Perlu dicek (bukan domain umum):** `yamllint.readthedocs.io` (1) · `docs.astral.sh` (1)
- Domain umum: `github.com` (4) · `raw.githubusercontent.com` (2) · `pypi.org` (1)

## Berkas biner / bobot (0)


## Temuan

### `pustaka-jaringan` — SEDANG (2)
- `open_image_models/detection/core/hub.py:8` — `import urllib.request`
- `test/open_image_models/detection/core/test_hub.py:9` — `import requests`

> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut
> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.

## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| tidak ada temuan TINGGI | — | — | — |

**Unduhan otomatis:** `open_image_models/detection/core/hub.py` (`download_model`, baris 154–196) mengunduh model ONNX dari
`https://github.com/ankandrew/open-image-models/releases/download/assets` saat pertama dipakai. **Tidak ada pemeriksaan keutuhan**,
dan **pemindai tidak menandai jalur ini** (pola yang sama: `urllib.request.urlopen`).
**Bergantung pada `ultralytics`:** tidak (`pyproject.toml`).
**Batas:** pemindai statis hanya petunjuk; berkas yang tidak ditandai tidak dibaca baris demi baris.
