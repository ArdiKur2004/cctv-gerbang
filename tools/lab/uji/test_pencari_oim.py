"""Uji tools/lab/pencari_oim.py tanpa model sungguhan: berkas yang tidak sama dengan kunci ditolak sebelum onnxruntime dan
open-image-models dimuat."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pencari_oim as po  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402


def test_berkas_yang_berubah_ditolak_sebelum_memuat_apa_pun(tmp_path):
    folder = tmp_path / "unduhan" / po.BUTIR
    folder.mkdir(parents=True)
    (folder / "model.onnx").write_bytes(b"ditukar")
    kunci = tmp_path / "kunci.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": po.BUTIR, "berkas": "model.onnx",
                                             "sha256": hashlib.sha256(b"asli").hexdigest()}]}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        po.PencariOim(tmp_path / "unduhan", kunci=kunci)
