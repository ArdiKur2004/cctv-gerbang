"""Uji dengan Qwen3-VL sungguhan. Di luar gerbang biasa karena memuat model 4 GB ke kartu grafis. Dijalankan dengan tangan:

  powershell -NoProfile -File tools\\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_vlm as bv  # noqa: E402

MODEL = Path(__file__).resolve().parents[3] / "models" / "qwen3-vl-2b-instruct"


@pytest.mark.skipif(not MODEL.is_dir(), reason="folder model belum disalin (Rencana 5 Task 4)")
def test_pembaca_qwen_membaca_plat_buatan():
    # Plat buatan tulisan komputer, bukan plat siapa pun: membuktikan rantainya (gerbang model -> muat -> tanya -> teks).
    gambar = np.zeros((110, 360, 3), np.uint8)
    cv2.putText(gambar, "B 1234 XYZ", (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 3)

    bacaan = bv.bersihkan(bv.PembacaQwen(MODEL)(gambar))

    assert bacaan == "B1234XYZ"
