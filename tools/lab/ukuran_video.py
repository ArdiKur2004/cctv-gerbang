"""Resolusi dan jumlah bingkai sebuah video, dibaca dari wadahnya — TIDAK membuka gambarnya.

Dipakai karena tools/manifes-video.mjs mencatat `ukuran` dari .info.json, yaitu resolusi ASLI video di sumbernya.
Bila unduhan dibatasi resolusinya, berkas yang ada lebih kecil daripada yang tercatat — dan angka pengukuran
yang memakai catatan itu akan menyesatkan. Ditemukan 26 Okt saat video satu jam diunduh di 480.

  powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/ukuran_video.py /kerja/data/video/riset/<nama>.mp4
"""
import sys
from pathlib import Path

import av


def utama(jalur: str) -> int:
    with av.open(jalur) as wadah:
        aliran = wadah.streams.video[0]
        detik = float(wadah.duration) / 1_000_000 if wadah.duration else None
        print(f"berkas    : {Path(jalur).name}")
        print(f"ukuran    : {aliran.codec_context.width}x{aliran.codec_context.height}")
        print(f"laju       : {float(aliran.average_rate):.2f} bingkai/detik" if aliran.average_rate else "laju: tidak diketahui")
        print(f"lama      : {detik:.0f} detik" if detik else "lama: tidak diketahui")
        print(f"bingkai   : {aliran.frames if aliran.frames else 'tidak dicatat wadahnya'}")
        print(f"penyandian: {aliran.codec_context.name}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(utama(sys.argv[1]))
