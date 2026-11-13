"""Uji tools/lab/banding_pembaca.py: plat berlabel pilihan pembaca dipisah, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import banding_pembaca as bp  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "banding_pembaca.py"


def k(teks, **lain):
    return {"teks": teks, "kelompok": "mobil-terang", "berkas": [f"test/{teks}_1.png"], **lain}


PEMBAGIAN = {"latih": [], "uji": [k("D1500X"), k("D1600Y", label_penerbit="D1600X"), k("D1700X")]}


def test_label_pilihan_pembaca_dipisah():
    bagian = bp.bagian(PEMBAGIAN)

    assert [len(bagian[c]["uji"]) for c in bp.CARA] == [3, 2]


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps(PEMBAGIAN))
    (tmp_path / "a.jsonl").write_text("".join(json.dumps({"berkas": x["berkas"][0], "bacaan": x["teks"]}) + "\n"
                                              for x in PEMBAGIAN["uji"]))

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path / "keluar"),
                            "--hasil", f"tiruan={tmp_path / 'a.jsonl'}"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    teks = hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "1500" not in teks and "1600" not in teks
    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert r["tanpa-label-pilihan-pembaca"]["tiruan"]["mobil-terang"]["kedatangan"] == 2
