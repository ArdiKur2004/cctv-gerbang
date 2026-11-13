"""Uji tools/lab/onnx_fpo.py yang tidak butuh Keras atau pustaka onnx (gerbang lab biasa): pemetaan bobot Keras ke
initializer ONNX (cara cocok dan kebalikannya, lengkap, satu-satu, tanpa pasangan ganda), hitungan beda bacaan tanpa nomor
plat, dan pembaca ONNX yang menolak mesin.onnx yang berubah."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import onnx_fpo as of  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "onnx_fpo.py"


def contoh():
    """Tiga bobot Keras dan initializer ONNX-nya dengan tiga cara berbeda, ditambah satu konstanta yang bukan bobot."""
    rng = np.random.default_rng(0)
    kernel = rng.normal(size=(3, 3, 2, 4)).astype(np.float32)  # konvolusi Keras: tinggi, lebar, masuk, keluar
    padat = rng.normal(size=(5, 6)).astype(np.float32)
    bias = rng.normal(size=(7,)).astype(np.float32)
    init = {"conv": np.transpose(kernel, (3, 2, 0, 1)), "dense": padat.copy(), "bias": bias.reshape(1, 1, 7),
            "bentuk": np.array([1, 2, 3, 4], dtype=np.int64)}
    return [kernel, padat, bias], init


def test_cara_cocok_dan_kebalikannya():
    rng = np.random.default_rng(1)
    w4 = rng.normal(size=(3, 3, 2, 4)).astype(np.float32)
    w2 = rng.normal(size=(5, 6)).astype(np.float32)
    kasus = [(w2, w2.copy(), "sama"), (w2, w2.reshape(3, 10), "bentuk-lain"), (w2, w2.T.copy(), "dibalik"),
             (w4, np.transpose(w4, (3, 2, 0, 1)).copy(), "sumbu:3,2,0,1"),
             (w4, np.transpose(w4, (2, 3, 0, 1)).copy(), "sumbu:2,3,0,1")]

    for w, v, cara in kasus:
        assert of.cara_cocok(w, v) == cara
        assert np.array_equal(of.terapkan(cara, w, v.shape), v)


def test_terapkan_mempertahankan_skalar():
    # Alpha DyT di ONNX terbitan berbentuk () (skalar). np.ascontiguousarray mengubahnya menjadi (1,): nilainya sama dan
    # keluaran ONNX tidak berubah, tetapi berkasnya berbeda (tertangkap pemeriksaan tukar-diri di Rencana 11 Task 2).
    w = np.array(0.5, dtype=np.float32)

    v = of.terapkan(of.cara_cocok(w, w.copy()), w, ())

    assert v.shape == () and v == w


def test_cara_cocok_menolak_nilai_atau_ukuran_lain():
    w = np.arange(12, dtype=np.float32).reshape(3, 4)

    assert of.cara_cocok(w, w + 1) is None
    assert of.cara_cocok(w, w[:2]) is None


def test_peta_lengkap_satu_satu_dan_melewati_konstanta():
    bobot, init = contoh()

    assert of.peta(bobot, init) == [("conv", "sumbu:3,2,0,1"), ("dense", "sama"), ("bias", "bentuk-lain")]


def test_peta_menolak_bobot_tanpa_pasangan():
    bobot, init = contoh()
    del init["dense"]

    with pytest.raises(of.PetaDitolak, match="0 pasangan"):
        of.peta(bobot, init)


def test_peta_menolak_bobot_dengan_dua_pasangan():
    bobot, init = contoh()
    init["dense_salinan"] = init["dense"].copy()

    with pytest.raises(of.PetaDitolak, match="2 pasangan"):
        of.peta(bobot, init)


def test_peta_menolak_dua_bobot_pada_satu_initializer():
    bobot, init = contoh()

    with pytest.raises(of.PetaDitolak, match="initializer yang sama"):
        of.peta([bobot[1], bobot[1].copy()], {"dense": init["dense"]})


def test_samakan_menghitung_beda_tanpa_mencetak_nomor_plat(tmp_path):
    for nama, bacaan in (("a", ["B1234XY", "D5678AB", "F9012Z"]), ("b", ["B1234XY", "D5678AE", "F9012Z"])):
        (tmp_path / f"{nama}.jsonl").write_text("".join(json.dumps({"berkas": f"{i}.jpg", "bacaan": t}) + "\n"
                                                        for i, t in enumerate(bacaan)))

    assert of.beda_bacaan(tmp_path / "a.jsonl", tmp_path / "b.jsonl") == {"gambar": 3, "beda": 1}
    hasil = subprocess.run([sys.executable, str(SKRIP), "samakan", str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl")],
                           capture_output=True, text=True)
    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar
    assert "gambar 3, beda 1" in layar and not any(t in layar for t in ("B1234XY", "D5678A", "F9012Z"))


def test_pembaca_onnx_menolak_mesin_onnx_yang_berubah_sebelum_memuat_apa_pun(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"ditukar")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64}))

    with pytest.raises(of.ModelDitolak, match="SHA-256"):
        of.PembacaOnnxMesin(tmp_path, tmp_path / "unduhan")
