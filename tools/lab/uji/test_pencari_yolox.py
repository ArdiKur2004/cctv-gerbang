"""Uji tools/lab/pencari_yolox.py tanpa model sungguhan: letterbox seperti YOLOX, NMS, penguraian keluaran ke piksel foto asli,
dan pencari ONNX yang menolak berkas yang berubah sebelum onnxruntime dimuat."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pencari_yolox as pyx  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402


def test_letterbox_kiri_atas_dengan_bantalan_114():
    gambar = np.full((100, 200, 3), 7, np.uint8)

    hasil, skala = pyx.letterbox(gambar, 64)

    assert hasil.shape == (64, 64, 3) and skala == 0.32
    assert (hasil[:32, :64] == 7).all() and (hasil[32:, :] == 114).all()


def test_nms_menyimpan_yang_terkuat_dan_yang_tidak_bertumpuk():
    kotak = np.array([[0, 0, 10, 10], [1, 1, 10, 10], [50, 50, 60, 60]], np.float32)
    skor = np.array([0.6, 0.9, 0.5], np.float32)

    assert pyx.nms(kotak, skor) == [1, 2]
    assert pyx.nms(np.zeros((0, 4), np.float32), np.zeros(0, np.float32)) == []


def test_urai_keluaran_ke_piksel_asli_dan_ambang():
    keluaran = np.array([[32, 16, 20, 10, 0.9, 0.9],    # skor 0,81
                         [33, 16, 20, 10, 0.8, 0.8],    # bertumpuk dan lebih lemah: dibuang NMS
                         [5, 5, 2, 2, 0.05, 0.1]],      # skor 0,005, di bawah ambang model
                        np.float32)

    hasil = pyx.urai_keluaran(keluaran, 0.5)

    assert len(hasil) == 1
    x1, y1, x2, y2, yakin = hasil[0]
    assert (x1, y1, x2, y2) == (44.0, 22.0, 84.0, 42.0) and abs(yakin - 0.81) < 1e-6


def test_pencari_onnx_menolak_berkas_yang_berubah_sebelum_memuat_apa_pun(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"ditukar")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64, "ukuran": 64}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        pyx.PencariYolox(tmp_path)
