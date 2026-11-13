"""Uji tools/lab/model_terkunci.py: folder model hanya boleh dimuat bila isinya persis yang dikunci."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model_terkunci as mt  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "model_terkunci.py"


def siapkan(tmp_path):
    folder = tmp_path / "model-contoh"
    folder.mkdir()
    isi = {"config.json": b"{}", "model.safetensors": b"bobot"}
    for nama, data in isi.items():
        (folder / nama).write_bytes(data)
    kunci = tmp_path / "vendor.lock.json"
    kunci.write_text(json.dumps({"model_hf": [{"nama": "model-contoh",
                                               "berkas": {n: hashlib.sha256(d).hexdigest() for n, d in isi.items()}}]}))
    return folder, mt.daftar_model_hf(kunci)


def test_folder_yang_persis_sama_dengan_kunci_diterima(tmp_path):
    folder, daftar = siapkan(tmp_path)

    assert mt.verifikasi_folder_model(folder, daftar) == folder


def test_berkas_tambahan_membuat_folder_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "selundupan.py").write_text("import os")

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar"):
        mt.verifikasi_folder_model(folder, daftar)


def test_berkas_yang_berubah_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "model.safetensors").write_bytes(b"ditukar")

    with pytest.raises(mt.ModelDitolak, match="SHA-256"):
        mt.verifikasi_folder_model(folder, daftar)


def test_berkas_yang_hilang_ditolak(tmp_path):
    folder, daftar = siapkan(tmp_path)
    (folder / "config.json").unlink()

    with pytest.raises(mt.ModelDitolak, match="tidak ada"):
        mt.verifikasi_folder_model(folder, daftar)


def test_folder_yang_tidak_terdaftar_ditolak(tmp_path):
    _, daftar = siapkan(tmp_path)
    lain = tmp_path / "model-lain"
    lain.mkdir()

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar di kunci model"):
        mt.verifikasi_folder_model(lain, daftar)


def test_kunci_repo_mencatat_pelabel_qwen3_vl():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa butir ini pelabel tidak bisa dimuat sama sekali.
    berkas = mt.daftar_model_hf()["qwen3-vl-2b-instruct"]

    assert "model.safetensors" in berkas and len(berkas) == 11


def test_baris_perintah_menolak_folder_tak_terdaftar_dengan_kode_1(tmp_path):
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(lain)], capture_output=True, text=True)

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout


def siapkan_berkas(tmp_path, sha=None):
    jalur = tmp_path / "unduhan" / "model.onnx"
    jalur.parent.mkdir(parents=True)
    jalur.write_bytes(b"onnx")
    kunci = tmp_path / "kunci-berkas.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": "model-contoh", "berkas": "model.onnx",
                                             "sha256": hashlib.sha256(b"onnx").hexdigest() if sha is None else sha}]}))
    return jalur, mt.daftar_berkas(kunci)


def test_berkas_unduhan_yang_terkunci_diterima(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)

    assert mt.verifikasi_berkas(jalur, "model-contoh", daftar) == jalur


def test_berkas_unduhan_yang_belum_dikunci_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path, sha="")

    with pytest.raises(mt.ModelDitolak, match="belum dikunci"):
        mt.verifikasi_berkas(jalur, "model-contoh", daftar)


def test_berkas_unduhan_yang_berubah_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)
    jalur.write_bytes(b"ditukar")

    with pytest.raises(mt.ModelDitolak, match="SHA-256"):
        mt.verifikasi_berkas(jalur, "model-contoh", daftar)


def test_berkas_unduhan_bernama_lain_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)
    lain = jalur.with_name("lain.onnx")
    lain.write_bytes(b"onnx")

    with pytest.raises(mt.ModelDitolak, match="bukan model.onnx"):
        mt.verifikasi_berkas(lain, "model-contoh", daftar)


def test_butir_berkas_yang_tak_terdaftar_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar"):
        mt.verifikasi_berkas(jalur, "lain", daftar)


def test_kunci_repo_mencatat_model_fast_plate_ocr():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa kedua butir ini pembaca kedua tidak bisa dimuat.
    daftar = mt.daftar_berkas()

    assert daftar["fpo-cct-s-v2-onnx"][0] == "cct_s_v2_global.onnx" and len(daftar["fpo-cct-s-v2-onnx"][1]) == 64
    assert daftar["fpo-cct-s-v2-config"][0] == "cct_s_v2_global_plate_config.yaml"
    assert len(daftar["fpo-cct-s-v2-config"][1]) == 64


def test_kunci_repo_mencatat_bobot_keras_fast_plate_ocr():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa butir ini fast-plate-ocr tidak bisa dilatih ulang (K26).
    daftar = mt.daftar_berkas()

    for butir, nama in (("fpo-cct-s-v2-keras", "cct_s_v2_global.keras"),
                        ("fpo-cct-s-v2-model-config", "cct_s_v2_global_model_config.yaml"),
                        ("fpo-cct-s-v2-val", "cct_s_v2_global_val_results.json")):
        assert daftar[butir][0] == nama and len(daftar[butir][1]) == 64
