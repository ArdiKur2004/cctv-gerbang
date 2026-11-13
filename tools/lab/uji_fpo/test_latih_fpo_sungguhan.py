"""Uji tools/lab/latih_fpo.py yang butuh Keras dan berkas model, di image lab tambahan (di luar gerbang biasa), hanya dengan
plat buatan:

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import sys
from pathlib import Path

import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import latih_fpo as lf  # noqa: E402
from baca_fpo import PembacaFpo  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_latih_fpo import UJI, buat  # noqa: E402
from test_percobaan_fpo import ADA, TEKS, plat_buatan  # noqa: E402

pytestmark = pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")


def test_bobot_terbitan_termuat_utuh_dan_konfigurasi_salah_tertangkap(tmp_path):
    jalur = lf.jalur_terkunci(UNDUHAN)
    lf.siapkan_torch()
    assert lf.bobot_utuh(jalur) == (192, 192)

    asli = Path(jalur["model"]).read_text()
    assert asli.count("\n  layers: 5\n") == 1
    salah = tmp_path / "model_config.yaml"
    salah.write_text(asli.replace("\n  layers: 5\n", "\n  layers: 4\n"))
    sama, semua = lf.bobot_utuh({**jalur, "model": salah})
    assert sama < semua


def test_pembaca_keras_membaca_sama_dengan_pembaca_onnx_terbitan():
    # Perlakuan sama: bobot terbitan lewat PembacaKeras harus memberi bacaan yang sama dengan PembacaFpo (ONNX, Rencana 6).
    jalur = lf.jalur_terkunci(UNDUHAN)
    keras_ = lf.PembacaKeras(jalur["keras"], jalur["plat"])
    onnx_ = PembacaFpo(UNDUHAN)

    assert [keras_(plat_buatan(t)) for t in TEKS] == [onnx_(plat_buatan(t)) for t in TEKS]
    assert lf.SLOT_MAKS == keras_.cfg.max_plate_slots and set(lf.HURUF) < set(keras_.cfg.alphabet)


def test_rantai_siapkan_latih_baca_dengan_plat_buatan(tmp_path):
    pembagian, folder = buat(tmp_path)
    mesin = tmp_path / "mesin"

    lf.siapkan(pembagian, folder, mesin)
    meta = lf.latih(mesin, UNDUHAN, zaman=1)
    ringkasan = lf.baca(pembagian, folder, mesin, UNDUHAN, tmp_path / "baca")

    assert meta["sha256_mesin"] == lf.sha256_berkas(mesin / "mesin.keras")
    assert meta["latihan"]["bobot_termuat"] == "192/192" and meta["latihan"]["zaman_berjalan"] == 1
    assert meta["validasi"]["awal"]["gambar"] == meta["validasi"]["akhir"]["gambar"] > 0
    assert json.loads((mesin / "mesin.json").read_text())["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
    assert ringkasan["per_kelompok"]["mobil-terang"]["kedatangan"] == len(UJI)
    (mesin / "mesin.keras").write_bytes(b"ditukar")
    with pytest.raises(ModelDitolak):
        lf.PembacaMesinFpo(mesin, UNDUHAN)
