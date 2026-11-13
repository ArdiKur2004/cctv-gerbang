"""Uji dengan model sungguhan di image lab tambahan (di luar gerbang biasa): pembanding YOLOv9-t-384 mengembalikan kotak
dengan bentuk yang diharapkan, dan tools/ukur_onnx_cpu.py jalan berdiri sendiri (tanpa impor dari repo).

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
UKUR = AKAR / "tools" / "ukur_onnx_cpu.py"
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import pencari_oim as po  # noqa: E402

ADA_OIM = (UNDUHAN / po.BUTIR).is_dir()


@pytest.mark.skipif(not ADA_OIM, reason="model pembanding belum diunduh (Rencana 12 Task 2)")
def test_pembanding_mengembalikan_kotak_dengan_keyakinan():
    cari = po.PencariOim(UNDUHAN, utas=1)
    gambar = np.full((1080, 1920, 3), 128, np.uint8)

    hasil = cari(gambar)

    assert isinstance(hasil, list)
    assert all(len(t) == 5 and 0.0 <= t[4] <= 1.0 and t[0] <= t[2] and t[1] <= t[3] for t in hasil)


def test_ukur_onnx_cpu_berdiri_sendiri(tmp_path):
    import onnx
    from onnx import TensorProto, helper

    masuk = helper.make_tensor_value_info("input", TensorProto.UINT8, [1, 8])
    keluar = helper.make_tensor_value_info("keluar", TensorProto.FLOAT, [1, 8])
    satu = helper.make_tensor("satu", TensorProto.FLOAT, [1], [1.0])
    graf = helper.make_graph([helper.make_node("Cast", ["input"], ["f"], to=TensorProto.FLOAT),
                              helper.make_node("Add", ["f", "satu"], ["keluar"])], "kecil", [masuk], [keluar], [satu])
    model = helper.make_model(graf, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 8
    onnx.save(model, tmp_path / "kecil.onnx")

    # -I: tanpa folder skrip di sys.path, jadi impor apa pun dari repo pasti gagal.
    hasil = subprocess.run([sys.executable, "-I", str(UKUR), str(tmp_path / "kecil.onnx"), "--keluar", str(tmp_path / "h.json")],
                           capture_output=True, text=True, cwd=tmp_path)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    data = json.loads((tmp_path / "h.json").read_text())
    assert set(data["model"][0]["per_utas"]) == {"1", "2", "4"}
    assert data["model"][0]["per_utas"]["1"]["median_ms"] >= 0 and data["cpu_terlihat"] >= 1
