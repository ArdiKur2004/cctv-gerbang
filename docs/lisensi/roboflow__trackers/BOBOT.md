# Izin bobot dan bahan latih: trackers @ 3666546

| Hal | Kalimat persis dari sumber | Sumber (berkas pada commit yang dikunci) |
|---|---|---|
| Izin bobot | Inti pelacak tidak memakai bobot. "Clean-room implementations. Every algorithm is re-implemented from the original paper" | `README.md` baris 14 |
| Bahan latih bobot | tidak berlaku untuk inti pelacak | — |
| Izin bahan latih | tidak berlaku | — |
| Bergantung pada `ultralytics` | tidak | `pyproject.toml` |
| Format bobot | tidak ada bobot bawaan yang wajib | — |
| Unduhan otomatis saat dipakai | hanya bila skrip baris-perintah atau pengunduh utilitasnya dipakai | `src/trackers/scripts/track.py`; `src/trackers/utils/downloader.py` |
