"""Uji PembacaKeras.dengan_yakin dan .rincian dengan mesin sungguhan (Rencana 24 Task 8 Step 1, K46; di luar gerbang biasa): bacaan
beserta keyakinannya sama dengan bacaan biasa, dan rincian per posisi memberi huruf pertama yang membentuk teks yang sama,
peluangnya menurun, dan huruf kedua yang berbeda. Masukan plat buatan (teks acak, bukan data pribadi).

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_pembaca_rincian.py -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import pytest

AKAR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import latih_fpo as lf  # noqa: E402
import plat_buatan as pb  # noqa: E402

MESIN = AKAR / "data" / "keluaran" / "fpo-indo-1"
pytestmark = pytest.mark.skipif(not (MESIN / "mesin.keras").exists(), reason="fpo-indo-1 belum ada (Rencana 10)")


def test_dengan_yakin_dan_rincian_per_posisi(tmp_path):
    pb.buat(12, tmp_path / "buatan", benih=46)
    pembaca = lf.PembacaMesinFpo(MESIN, AKAR / "data" / "unduhan")

    for berkas in sorted((tmp_path / "buatan" / "gambar").iterdir()):
        g = cv2.imread(str(berkas))
        teks, yakin = pembaca.dengan_yakin(g)
        rinci = pembaca.rincian(g)
        assert teks == pembaca(g) and 0.0 < yakin <= 1.0
        assert "".join(r[0] for r in rinci) == teks
        assert all(1.0 >= p1 >= p2 >= 0.0 and h1 != h2 for h1, p1, h2, p2 in rinci)
