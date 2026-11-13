"""Uji tools/lab/ciri.py dengan ONNX sungguhan di image lab tambahan (di luar gerbang biasa; butuh onnx): mesin ciri dilatih, diekspor,
lalu dibaca PengenalCiri dengan hasil yang sama dengan torch, dan ambang "tak yakin" bekerja.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_ciri_sungguhan.py -q -s -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import pytest

AKAR = Path(__file__).resolve().parents[3]
for folder in ("tools/lab", "tools/lab/uji"):
    sys.path.insert(0, str(AKAR / folder))
import ciri as cr  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_ciri import dataset_potongan  # noqa: E402


def test_ekspor_onnx_sama_dengan_torch_dan_ambang_tak_yakin(tmp_path):
    folder = dataset_potongan(tmp_path)
    cr.latih(folder, "jenis", tmp_path / "mesin", zaman=3, perangkat="cpu", nama="uji-jenis")

    hasil = cr.ekspor(tmp_path / "mesin", folder)

    assert hasil["pemeriksaan"]["kelas_sama"] == hasil["pemeriksaan"]["gambar"] > 0
    assert hasil["pemeriksaan"]["selisih_peluang"] < cr.BATAS_EKSPOR
    assert hasil["kelas"] == ["mobil", "motor"] and hasil["ciri"] == "jenis" and hasil["tujuan"] == "jualan"
    baris = [b for b in cr.baris_ciri(folder, "jenis") if b["sisi"] == "validasi"][:8]
    for b in baris:
        b["_label"] = b["jenis"]
    gambar, label, _ = cr.muat(baris, folder)
    mesin, meta = cr.muat_mesin(tmp_path / "mesin")

    lewat_torch = cr.ramal(mesin, gambar, meta["kelas"], "cpu")
    pengenal = cr.PengenalCiri(tmp_path / "mesin", ambang=0.0)
    lewat_onnx = [pengenal(cv2.imread(str(folder / b["berkas"]))) for b in baris]

    assert [k for k, _ in lewat_onnx] == [k for k, _ in lewat_torch]
    assert all(abs(a - b) < cr.BATAS_EKSPOR for (_, a), (_, b) in zip(lewat_onnx, lewat_torch))
    semua_tak_yakin = cr.PengenalCiri(tmp_path / "mesin", ambang=1.0)
    assert {semua_tak_yakin(cv2.imread(str(folder / b["berkas"])))[0] for b in baris} == {cr.TAK_YAKIN}
    with pytest.raises(ValueError):
        cr.PengenalCiri(tmp_path / "mesin", ambang=1.5)


def test_ukuran_bukan_bawaan_mengalir_dari_latih_sampai_pengenal(tmp_path):
    # Uji RANTAI (Rencana 35): ukuran yang diminta saat melatih harus sampai ke bentuk masukan ONNX dan ke pengenal. Tanpa uji ini,
    # latih bisa mencatat 192 sementara ekspor dan pemakaian diam-diam tetap 96, dan gerbangnya tetap hijau.
    import onnxruntime as ort

    folder = dataset_potongan(tmp_path)
    meta = cr.latih(folder, "jenis", tmp_path / "mesin", zaman=1, perangkat="cpu", ukuran=64, nama="uji-ukuran")

    hasil = cr.ekspor(tmp_path / "mesin", folder)
    pengenal = cr.PengenalCiri(tmp_path / "mesin", ambang=0.0)

    assert meta["ukuran"] == 64 and hasil["ukuran"] == 64
    sesi = ort.InferenceSession(str(tmp_path / "mesin" / "mesin.onnx"), providers=["CPUExecutionProvider"])
    assert list(sesi.get_inputs()[0].shape)[1:] == [3, 64, 64]
    assert pengenal.ukuran == 64
    baris = [b for b in cr.baris_ciri(folder, "jenis") if b["sisi"] == "validasi"][:4]
    for b in baris:
        b["_label"] = b["jenis"]
    gambar, _, _ = cr.muat(baris, folder, ukuran=64)
    mesin, m = cr.muat_mesin(tmp_path / "mesin")
    lewat_torch = cr.ramal(mesin, gambar, m["kelas"], "cpu")
    lewat_onnx = [pengenal(cv2.imread(str(folder / b["berkas"]))) for b in baris]
    assert [k for k, _ in lewat_onnx] == [k for k, _ in lewat_torch]


def test_ekspor_menolak_bobot_yang_berubah(tmp_path):
    folder = dataset_potongan(tmp_path)
    cr.latih(folder, "jenis", tmp_path / "mesin", zaman=1, perangkat="cpu")
    (tmp_path / "mesin" / "mesin.safetensors").write_bytes(b"ditukar")

    with pytest.raises(ModelDitolak, match="SHA-256"):
        cr.ekspor(tmp_path / "mesin", folder)
    assert not (tmp_path / "mesin" / "mesin-onnx.json").exists()
