"""Uji tools/lab/onnx_fpo.py dengan Keras, pustaka onnx, dan berkas model terbitan, di image lab tambahan (di luar gerbang
biasa), hanya dengan plat buatan:

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import sys
from pathlib import Path

import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import latih_fpo as lf  # noqa: E402
import onnx_fpo as of  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_latih_fpo import UJI, buat  # noqa: E402
from test_percobaan_fpo import ADA, TEKS, plat_buatan  # noqa: E402

pytestmark = pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")


def terbitan():
    jalur = lf.jalur_terkunci(UNDUHAN)
    lf.siapkan_torch()
    import onnx
    from onnx import numpy_helper
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur["plat"])
    asli = onnx.load(str(of.berkas_terkunci(UNDUHAN, of.BUTIR_ONNX)))
    init = {i.name: numpy_helper.to_array(i) for i in asli.graph.initializer}
    return cfg, load_keras_model(jalur["keras"], cfg), asli, init


def test_peta_terbitan_lengkap_dan_menukar_bobot_terbitan_tidak_mengubah_onnx():
    from onnx import numpy_helper

    _, model, asli, init = terbitan()
    p = of.peta(model.get_weights(), init)
    sendiri = of.tukar(asli, p, model.get_weights())

    assert len(p) == 192
    assert all(np.array_equal(numpy_helper.to_array(a), numpy_helper.to_array(b))
               for a, b in zip(asli.graph.initializer, sendiri.graph.initializer, strict=True))


def test_onnx_hasil_tukar_sama_dengan_keras_untuk_bobot_yang_diubah():
    import onnxruntime as ort

    cfg, model, asli, init = terbitan()
    p = of.peta(model.get_weights(), init)
    rng = np.random.default_rng(0)
    model.set_weights([w + rng.normal(0, 0.01, w.shape).astype(w.dtype) for w in model.get_weights()])
    baru = ort.InferenceSession(of.tukar(asli, p, model.get_weights()).SerializeToString(), providers=["CPUExecutionProvider"])
    lama = ort.InferenceSession(asli.SerializeToString(), providers=["CPUExecutionProvider"])
    gambar = [plat_buatan(t) for t in TEKS]

    n, sama, selisih = of.banding(model, baru, cfg, gambar)
    _, _, selisih_lama = of.banding(model, lama, cfg, gambar)

    assert n == len(TEKS) and sama == n and selisih < of.BATAS_SELISIH
    # Bobotnya memang berubah: ONNX terbitan tidak lagi sama dengan Keras, jadi uji di atas tidak kosong.
    assert selisih_lama > 100 * of.BATAS_SELISIH


def test_rantai_buat_baca_cepat_dengan_plat_buatan(tmp_path):
    pembagian, folder = buat(tmp_path)
    mesin = tmp_path / "mesin"
    lf.siapkan(pembagian, folder, mesin)
    lf.latih(mesin, UNDUHAN, zaman=1)

    meta = of.buat(mesin, UNDUHAN)
    onnx_ = of.PembacaOnnxMesin(mesin, UNDUHAN)
    keras_ = lf.PembacaMesinFpo(mesin, UNDUHAN)
    ringkasan = of.baca(pembagian, folder, mesin, UNDUHAN, tmp_path / "baca")
    kecepatan = of.cepat(mesin, UNDUHAN, utas=(1,), panaskan=1)

    assert meta["sha256_onnx"] == lf.sha256_berkas(mesin / "mesin.onnx") and meta["tensor_ditukar"] == 192
    assert meta["pemeriksaan_validasi"]["plat_sama"] == meta["pemeriksaan_validasi"]["gambar"] > 0
    assert meta["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"] and meta["tujuan"] == "belajar"
    assert [onnx_(plat_buatan(t)) for t in TEKS] == [keras_(plat_buatan(t)) for t in TEKS]
    assert ringkasan["per_kelompok"]["mobil-terang"]["kedatangan"] == len(UJI)
    assert kecepatan["per_utas"]["1"]["utuh_ms"]["median"] > 0
    (mesin / "mesin.onnx").write_bytes(b"ditukar")
    with pytest.raises(ModelDitolak):
        of.PembacaOnnxMesin(mesin, UNDUHAN)
