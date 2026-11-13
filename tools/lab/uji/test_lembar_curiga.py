"""Uji tools/lab/lembar_curiga.py: urutan tetap, dua tulisan per baris, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_contoh as lc  # noqa: E402
import lembar_curiga as lk  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_curiga.py"
CURIGA = [{"teks": "D3001AB", "usulan": "D3001AE", "kelompok": "motor-terang", "berkas": "test/D3001AB_1.png"},
          {"teks": "D1001AB", "usulan": "D1001AE", "kelompok": "mobil-terang", "berkas": "test/D1001AB_1.png"}]


def siapkan(tmp_path, curiga):
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    for c in curiga:
        cv2.imwrite(str(folder / c["berkas"]), np.full((30, 100, 3), 200, np.uint8))
    berkas = tmp_path / "curiga.json"
    berkas.write_text(json.dumps(curiga))
    return berkas, folder


def test_lembar_dan_daftarnya_ditulis_menurut_kelompok(tmp_path):
    berkas, folder = siapkan(tmp_path, CURIGA)

    assert lk.utama(berkas, folder, tmp_path / "keluar") == 0

    lembar = cv2.imread(str(tmp_path / "keluar/lembar-curiga-1.png"))
    assert lembar.shape == (2 * (lc.TINGGI + 8), lc.LEBAR_NOMOR + lc.LEBAR_POTONGAN + lc.LEBAR_TEKS, 3)
    daftar = json.loads((tmp_path / "keluar/lembar-curiga.json").read_text())
    assert [(c["nomor"], c["kelompok"]) for c in daftar["contoh"]] == [(1, "mobil-terang"), (2, "motor-terang")]
    assert daftar["contoh"][0]["usulan"] == "D1001AE"


def test_layar_tanpa_teks_plat(tmp_path, capsys):
    berkas, folder = siapkan(tmp_path, CURIGA)

    lk.utama(berkas, folder, tmp_path / "keluar")

    cetak = capsys.readouterr().out
    assert "1001" not in cetak and "3001" not in cetak
    assert "agen tidak membukanya" in cetak


def test_baris_perintah(tmp_path):
    berkas, folder = siapkan(tmp_path, CURIGA)
    kosong = tmp_path / "kosong.json"
    kosong.write_text("[]")

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)
    tanpa = subprocess.run([sys.executable, str(SKRIP), str(kosong), str(folder), str(tmp_path / "keluar-kosong")],
                           capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), str(berkas)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/lembar-curiga-1.png").exists()
    assert tanpa.returncode == 0 and "Tidak ada label" in tanpa.stdout
    assert salah.returncode == 2
