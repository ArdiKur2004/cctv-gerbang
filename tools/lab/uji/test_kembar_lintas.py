"""Uji tools/lab/kembar_lintas.py: kendaraan yang sama di kedua sisi dikenali dari gambar yang nyaris kembar dan label yang
hanya beda sedikit; yang dikeluarkan bahan latihnya, set uji tidak diubah."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kembar_lintas as kl  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "kembar_lintas.py"


def gambar(folder, nama, benih):
    jalur = folder / nama
    jalur.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(jalur), np.random.default_rng(benih).integers(0, 256, (30, 100), dtype=np.uint8))
    return nama


def siapkan(tmp_path, latih, uji):
    """latih, uji = daftar (teks, benih gambar). Benih sama = gambar kembar persis."""
    folder = tmp_path / "gambar"
    pembagian = {s: [{"teks": t, "kelompok": "mobil-terang", "berkas": [gambar(folder, f"{s}/{t}_1.png", b)]} for t, b in daftar]
                 for s, daftar in (("latih", latih), ("uji", uji))}
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))
    return pembagian, berkas, folder


def test_gambar_kembar_berlabel_beda_sedikit_mengeluarkan_plat_latih(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("D1234AE", 1), ("D5555X", 2)], [("D1234AB", 1)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert [x["teks"] for x in baru["latih"]] == ["D5555X"] and [x["teks"] for x in baru["uji"]] == ["D1234AB"]
    assert (hitung["pasangan_mirip"], hitung["pasangan_kembar"], hitung["latih_dikeluarkan"]) == (1, 1, 1)


def test_gambar_kembar_berlabel_jauh_tidak_dikeluarkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B9876XY", 1)], [("D1234AB", 1)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert len(baru["latih"]) == 1 and (hitung["pasangan_mirip"], hitung["latih_dikeluarkan"]) == (1, 0)


def test_label_beda_sedikit_tetapi_gambar_lain_tidak_dikeluarkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("D1234AE", 7)], [("D1234AB", 8)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert len(baru["latih"]) == 1 and hitung["pasangan_mirip"] == 0


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    _, berkas, folder = siapkan(tmp_path, [("D1234AE", 1)], [("D1234AB", 1)])

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "1234" not in hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "latih dikeluarkan: 1" in hasil.stdout
    assert json.loads((tmp_path / "keluar/pembagian.json").read_text())["latih"] == []
