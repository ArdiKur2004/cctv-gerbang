"""Uji isi image lab tambahan cctvgerbang-lab-fpo:v1 yang tidak terlihat dari Dockerfile saja (di luar gerbang biasa):

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import os
import subprocess
import sys


def test_albumentations_tidak_memeriksa_versi_ke_internet():
    # albumentations memeriksa versi terbaru ke pypi.org saat dimuat (check_version.py). Di lab tanpa jaringan itu gagal
    # dengan peringatan; di server (K25) ia akan benar-benar keluar. Image mematikannya dengan NO_ALBUMENTATIONS_UPDATE=1.
    hasil = subprocess.run([sys.executable, "-W", "always", "-c", "import albumentations"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stderr[-2000:]
    assert os.environ.get("NO_ALBUMENTATIONS_UPDATE") == "1"
    assert "Error fetching version info" not in hasil.stderr
