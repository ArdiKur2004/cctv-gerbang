"""Uji tools/lab/baca_fpo.py dengan pembaca tiruan. Model sungguhan diuji terpisah di tools/lab/uji_gpu/."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_fpo as bf  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "baca_fpo.py"


def siapkan(tmp_path):
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    cv2.imwrite(str(folder / "test/B1234XYZ_0.png"), np.full((30, 100, 3), 200, np.uint8))
    pembagian = {"latih": [], "uji": [{"teks": "B1234XYZ", "kelompok": "mobil-terang", "berkas": ["test/B1234XYZ_0.png"]}]}
    jalur = tmp_path / "pembagian.json"
    jalur.write_text(json.dumps(pembagian))
    return pembagian, jalur, folder


def test_warna_mengikuti_konfigurasi_model():
    gambar = np.array([[[10, 20, 30]]], np.uint8)  # satu titik, urutan warna OpenCV (biru, hijau, merah)

    assert bf.ubah_warna(gambar, "rgb").tolist() == [[[30, 20, 10]]]
    assert bf.ubah_warna(gambar, "grayscale").shape == (1, 1)


def test_mode_warna_lain_ditolak():
    with pytest.raises(ValueError, match="mode warna"):
        bf.ubah_warna(np.zeros((1, 1, 3), np.uint8), "hsv")


def test_utama_menulis_hasil_dan_ringkasan_tanpa_nomor_plat(tmp_path, capsys):
    _, jalur, folder = siapkan(tmp_path)
    keluar = tmp_path / "keluar"

    kode = bf.utama(jalur, folder, tmp_path / "unduhan", keluar, baca=lambda gambar: "B 1234 XYZ")

    assert kode == 0
    assert json.loads((keluar / "hasil.jsonl").read_text())["bacaan"] == "B1234XYZ"
    teks = (keluar / "ringkasan.json").read_text()
    assert "1234" not in teks
    assert json.loads(teks)["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1
    assert "1234" not in capsys.readouterr().out


def test_baris_perintah_menolak_model_yang_belum_ada_dengan_kode_2(tmp_path):
    # Rantainya: baris perintah -> gerbang berkas terkunci, SEBELUM onnxruntime dimuat atau set uji dibaca.
    _, jalur, folder = siapkan(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), str(jalur), str(folder), str(tmp_path / "unduhan-kosong"),
                            str(tmp_path / "keluar")], capture_output=True, text=True)

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout
    assert not (tmp_path / "keluar").exists()


def test_gambar_yang_hilang_tidak_membocorkan_nama_berkas(tmp_path):
    # Proses terpisah: yang diuji pembisuan log OpenCV yang ikut termuat lewat baca_fpo sendiri.
    pembagian, _, folder = siapkan(tmp_path)
    (folder / "test/B1234XYZ_0.png").unlink()
    kode = ("import json, sys; sys.path.insert(0, sys.argv[1]); import baca_fpo as bf; "
            "_, r = bf.nilai(json.loads(sys.argv[2]), sys.argv[3], lambda g: 'X'); "
            "print(r['per_kelompok']['mobil-terang']['gambar'])")

    hasil = subprocess.run([sys.executable, "-c", kode, str(SKRIP.parent), json.dumps(pembagian), str(folder)],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert hasil.stdout.strip() == "1"
    assert "1234" not in hasil.stderr


def test_sisi_latih_dibaca_bila_diminta(tmp_path):
    pembagian, jalur, folder = siapkan(tmp_path)
    jalur.write_text(json.dumps({"latih": pembagian["uji"], "uji": []}))

    kode = bf.utama(jalur, folder, tmp_path / "unduhan", tmp_path / "keluar", baca=lambda g: "B1234XYZ", sisi="latih")

    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert kode == 0 and r["sisi"] == "latih" and r["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1


def test_baris_perintah_menerima_sisi_latih_sampai_ke_gerbang_berkas(tmp_path):
    _, jalur, folder = siapkan(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), str(jalur), str(folder), str(tmp_path / "unduhan-kosong"),
                            str(tmp_path / "keluar"), "latih"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "DITOLAK" in hasil.stdout, hasil.stdout + hasil.stderr
