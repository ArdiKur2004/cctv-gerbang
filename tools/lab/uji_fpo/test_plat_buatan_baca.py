"""Kemiripan plat buatan (Rencana 18 Task 4), di image lab tambahan (di luar gerbang biasa): fpo-indo-1, yang dilatih dengan plat
nyata INDO-ALPR dan tidak pernah melihat huruf buatan, membaca plat buatan bersih dan yang diubah. Angkanya dicetak dan disimpan
untuk laporan. Uji hanya menuntut bacaan bersih lebih baik daripada yang diubah; kemiripan tidak diklaim lulus.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_plat_buatan_baca.py -q -s -p no:cacheprovider
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
KELUARAN = AKAR / "data" / "keluaran"
UNDUHAN = AKAR / "data" / "unduhan"
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import onnx_fpo as of  # noqa: E402
import plat_buatan as pb  # noqa: E402

BACA = KELUARAN / "fpo-indo-1"
JUMLAH = 200
pytestmark = pytest.mark.skipif(not (BACA / "mesin.onnx").exists(), reason="fpo-indo-1 belum ada (Rencana 11)")


def test_fpo_indo_1_membaca_plat_buatan():
    pembaca = of.PembacaOnnxMesin(BACA, UNDUHAN, utas=2)
    benar = {"bersih": 0, "ubah": 0}
    for i in range(JUMLAH):
        rng = np.random.default_rng([18, i])
        teks = pb.teks_acak(rng)
        bersih = pb.plat(teks, "mobil" if i % 3 else "motor", list(pb.WARNA)[i % 5], rng, tinggi=96)
        ubah, _ = pb.ubah(bersih, rng)
        benar["bersih"] += int(pembaca(bersih) == teks)
        benar["ubah"] += int(pembaca(ubah) == teks)
    print(f"\nfpo-indo-1 membaca plat buatan: bersih {benar['bersih']}/{JUMLAH}, diubah {benar['ubah']}/{JUMLAH}")
    (KELUARAN / "plat-buatan-kemiripan.json").write_text(json.dumps({"jumlah": JUMLAH, "benar": benar, "pembaca": "fpo-indo-1"}))
    assert benar["bersih"] > benar["ubah"]
