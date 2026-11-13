"""Uji tools/lab/label_curiga.py: hanya plat yang dibantah dua pembaca yang SEPAKAT yang dicurigai (K22)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import label_curiga as lcu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "label_curiga.py"


def pembagian(*teks):
    return {"latih": [], "uji": [{"teks": t, "kelompok": "mobil-terang", "berkas": [f"test/{t}_1.png"]} for t in teks]}


def test_dua_pembaca_sepakat_berbeda_dari_label_dicurigai():
    b = "test/B1234XYZ_1.png"

    curiga = lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYE"})

    assert curiga == [{"teks": "B1234XYZ", "usulan": "B1234XYE", "kelompok": "mobil-terang", "berkas": b}]


def test_satu_pembaca_saja_atau_dua_pembaca_tak_sepakat_tidak_dicurigai():
    b = "test/B1234XYZ_1.png"

    assert lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYZ"}) == []
    assert lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYF"}) == []


def test_sepakat_di_luar_pola_atau_kosong_tidak_dicurigai():
    b = "test/B1234XYZ_1.png"

    assert lcu.cari(pembagian("B1234XYZ"), {b: "HELLO"}, {b: "HELLO"}) == []
    assert lcu.cari(pembagian("B1234XYZ"), {b: ""}, {b: ""}) == []


def test_cara_dinilai_pada_contoh_yang_sudah_diperiksa_owner():
    curiga = [{"teks": "D1001AB"}, {"teks": "D1003AB"}]
    lembar = {"contoh": [{"nomor": 1, "teks": "D1001AB"}, {"nomor": 2, "teks": "D1002AB"}, {"nomor": 3, "teks": "D1003AB"}]}

    assert lcu.nilai_cara(curiga, lembar, {1, 2}) == {"label_salah_diketahui": 2, "tertangkap": 1,
                                                       "label_benar_diketahui": 1, "ikut_dicurigai": 1}


def test_baris_perintah_menulis_berkas_tanpa_nomor_plat_di_layar(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps(pembagian("B1234XYZ", "D5678AB")))
    for nama in ("a.jsonl", "b.jsonl"):
        (tmp_path / nama).write_text(json.dumps({"berkas": "test/B1234XYZ_1.png", "bacaan": "B1234XYE"}) + "\n")
    (tmp_path / "lembar.json").write_text(json.dumps({"contoh": [{"nomor": 1, "teks": "B1234XYZ"}, {"nomor": 2, "teks": "D5678AB"}]}))
    perintah = [sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path / "a.jsonl"),
                str(tmp_path / "b.jsonl"), str(tmp_path / "keluar"), "--periksa", str(tmp_path / "lembar.json")]

    hasil = subprocess.run(perintah + ["--salah", "1"], capture_output=True, text=True)
    salah = subprocess.run(perintah + ["--salah", "9"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    for larangan in ("1234", "5678"):
        assert larangan not in hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "tertangkap 1 dari 1 label salah" in hasil.stdout
    assert json.loads((tmp_path / "keluar/curiga.json").read_text())[0]["usulan"] == "B1234XYE"
    assert salah.returncode == 2 and "SALAH PAKAI" in salah.stdout


def test_sisi_latih_lewat_baris_perintah(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps({"latih": pembagian("B1234XYZ")["uji"], "uji": []}))
    for nama in ("a.jsonl", "b.jsonl"):
        (tmp_path / nama).write_text(json.dumps({"berkas": "test/B1234XYZ_1.png", "bacaan": "B1234XYE"}) + "\n")

    kode = lcu.utama([str(tmp_path / "pembagian.json"), str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl"),
                      str(tmp_path / "keluar"), "--sisi", "latih"])

    assert kode == 0
    assert json.loads((tmp_path / "keluar/curiga.json").read_text())[0]["usulan"] == "B1234XYE"
    assert json.loads((tmp_path / "keluar/ringkasan.json").read_text())["sisi"] == "latih"
