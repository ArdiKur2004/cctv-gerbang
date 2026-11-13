"""Uji fast-plate-ocr dengan model sungguhan (CPU). Di luar gerbang biasa: butuh berkas model di data/unduhan.

  powershell -NoProfile -File tools\\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu/test_model_baca_fpo.py -q -s -p no:cacheprovider
"""
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_fpo as bf  # noqa: E402

UNDUHAN = Path(__file__).resolve().parents[3] / "data" / "unduhan"


@pytest.mark.skipif(not (UNDUHAN / bf.BUTIR_MODEL).is_dir(), reason="model belum diunduh (Rencana 6 Task 2)")
def test_pembaca_fpo_membaca_plat_buatan():
    # Plat buatan tulisan komputer, bukan plat siapa pun: membuktikan rantainya (gerbang berkas -> muat -> baca -> teks).
    gambar = np.zeros((110, 360, 3), np.uint8)
    cv2.putText(gambar, "B 1234 XYZ", (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 3)

    pembaca = bf.PembacaFpo(UNDUHAN)
    bacaan = bf.bersihkan(pembaca(gambar))

    print(f"\nbacaan plat buatan: {bacaan}; mode warna: {pembaca.mode_warna}; Indonesia di konfigurasi: {pembaca.wilayah_indonesia}")
    assert re.fullmatch(r"[0-9A-Z]{1,10}", bacaan)
