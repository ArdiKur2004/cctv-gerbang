# Audit statis: `trackers`

- Commit: `3666546420b0fd564c8e63157a6621efffdfa01a` · berkas kode dipindai: **160** · dilewati: 0
- TINGGI: **0** · SEDANG: **4** · INFO: 3

## Ringkasan per aturan

| Aturan | Tingkat | Jumlah | Arti |
|---|---|---|---|
| `pustaka-jaringan` | SEDANG | 4 | kode yang bisa membuka koneksi jaringan |
| `unduh-otomatis` | INFO | 3 | mengunduh bobot/berkas saat berjalan (periksa sumber & hash) |

## Domain yang disebut di KODE

- **Perlu dicek (bukan domain umum):** `trackers.roboflow.com` (18) · `storage.googleapis.com` (15) · `docs.astral.sh` (9) · `roboflow.com` (7) · `schema.org` (6) · `example.com` (5) · `twitter.com` (2) · `www.linkedin.com` (2) · `www.youtube.com` (2) · `giscus.app` (2) · `supervision.roboflow.com` (2) · `api.indexnow.org` (1) · `motchallenge.net` (1) · `deeperaction.github.io` (1) · `www.soccer-net.org` (1) · `dancetrack.github.io` (1) · `unpkg.com` (1) · `en.wikipedia.org` (1) · `www.wikidata.org` (1) · `www.crunchbase.com` (1) · `t.ly` (1) · `blog.roboflow.com` (1) · `discuss.roboflow.com` (1) · `universe.roboflow.com` (1) · `inference.roboflow.com` (1) · `maestro.roboflow.com` (1) · `docs.roboflow.com` (1) · `hub.docker.com` (1) · `discord.gg` (1) · `openaccess.thecvf.com` (1) · `dl.fbaipublicfiles.com` (1)
- Domain umum: `github.com` (25) · `arxiv.org` (11) · `pypi.org` (4)

## Berkas biner / bobot (0)


## Temuan

### `pustaka-jaringan` — SEDANG (4)
- `src/trackers/core/mcbyte/masks/cutie.py:14` — `from urllib.parse import urlparse`
- `src/trackers/core/mcbyte/masks/sam.py:14` — `from urllib.parse import urlparse`
- `src/trackers/utils/downloader.py:17` — `import requests`
- `tests/conftest.py:13` — `import urllib.request`

### `unduh-otomatis` — INFO (3)
- `demo/app.py:58` — `LOADED_MODELS[model_id] = AutoModel.from_pretrained(model_id, device=DEVICE)`
- `src/trackers/scripts/track.py:580` — `return AutoModel.from_pretrained(`
- `tests/conftest.py:93` — `urllib.request.urlretrieve(url, zip_path)  # noqa: S310`

> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut
> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.

## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| tidak ada temuan TINGGI | — | — | — |

**Unduhan otomatis:** `src/trackers/utils/downloader.py:65` mengunduh berkas dengan `requests.get` (tidak ditandai pemindai);
`src/trackers/scripts/track.py:580` memuat model lewat `from_pretrained` bila skrip baris-perintahnya dipakai. Inti pelacak tidak
butuh bobot. Di lab tanpa jaringan jalur ini gagal, tidak mengunduh.
**Bergantung pada `ultralytics`:** tidak (`pyproject.toml`).
**Batas:** pemindai statis hanya petunjuk; berkas yang tidak ditandai tidak dibaca baris demi baris.
