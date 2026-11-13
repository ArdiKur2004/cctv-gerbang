# Audit statis: `fast-alpr`

- Commit: `aca4ecdd279350ffdda8dffb0badd70952470c28` · berkas kode dipindai: **19** · dilewati: 0
- TINGGI: **0** · SEDANG: **0** · INFO: 0

## Ringkasan per aturan

| Aturan | Tingkat | Jumlah | Arti |
|---|---|---|---|
| — | — | 0 | tak ada pola yang cocok |

## Domain yang disebut di KODE

- **Perlu dicek (bukan domain umum):** `ankandrew.github.io` (2) · `yamllint.readthedocs.io` (1) · `docs.astral.sh` (1)
- Domain umum: `pypi.org` (1) · `raw.githubusercontent.com` (1) · `github.com` (1)

## Berkas biner / bobot (0)


## Temuan

> Pemindai statis = **petunjuk, bukan vonis**. Tak menemukan pola ≠ terbukti aman (kode bisa disamarkan, dependensi tak ikut
> dipindai, bobot pickle tak dibuka). Temuan SEDANG wajib dibaca konteksnya oleh manusia. Lihat `docs/PROTOKOL-KEAMANAN-REPO.md`.

## Dibaca manual (2026-10-13)

| Temuan | Berkas | Isi sebenarnya | Sikap |
|---|---|---|---|
| tidak ada temuan TINGGI | — | — | — |

**Unduhan otomatis:** tidak ada di paket ini sendiri. Ia memanggil `fast-plate-ocr` dan `open-image-models`, yang keduanya mengunduh
model tanpa pemeriksaan keutuhan (lihat laporan masing-masing).
**Bergantung pada `ultralytics`:** tidak. Dependensinya (`pyproject.toml`): `fast-plate-ocr>=1.1.0`, `open-image-models>=0.5.1`,
`opencv-python-headless>=4.9.0.80`.
**Batas:** pemindai statis hanya petunjuk; 19 berkas, tidak dibaca baris demi baris.
