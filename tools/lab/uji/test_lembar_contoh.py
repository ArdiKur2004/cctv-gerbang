"""Uji tools/lab/lembar_contoh.py: contoh dipilih tetap per kelompok dari set uji, dan layar tidak memuat nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_contoh as lc  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_contoh.py"


def siapkan(tmp_path, jumlah):
    """Pembagian tiruan: `jumlah` = {kelompok: banyak kedatangan}, satu gambar per kedatangan."""
    folder = tmp_path / "gambar"
    (folder / "train").mkdir(parents=True)
    uji, n = [], 0
    for kelompok, banyak in jumlah.items():
        for _ in range(banyak):
            n += 1
            nama = f"train/D {1000 + n} AB_0001.png"
            cv2.imwrite(str(folder / nama), np.full((30, 100, 3), 200, np.uint8))
            uji.append({"teks": f"D{1000 + n}AB", "kelompok": kelompok, "berkas": [nama]})
    pembagian = {"latih": [{"teks": "D9999AB", "kelompok": "mobil-terang", "berkas": ["train/x.png"]}], "uji": uji}
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))
    return pembagian, berkas, folder


def test_contoh_dipilih_per_kelompok_tetap_dan_hanya_dari_uji(tmp_path):
    pembagian, _, _ = siapkan(tmp_path, {"mobil-terang": 20, "motor-gelap": 3})

    pertama = lc.pilih(pembagian)

    kelompok = [a["kelompok"] for a in pertama]
    assert kelompok.count("mobil-terang") == lc.PER_KELOMPOK and kelompok.count("motor-gelap") == 3
    assert pertama == lc.pilih(pembagian)
    assert all(a["teks"] != "D9999AB" for a in pertama)


def test_lembar_dan_daftarnya_ditulis(tmp_path):
    _, berkas, folder = siapkan(tmp_path, {"mobil-terang": 20, "motor-gelap": 3})
    keluar = tmp_path / "keluar"

    assert lc.utama(berkas, folder, keluar) == 0

    lembar = cv2.imread(str(keluar / "lembar-contoh-1.png"))
    assert lembar.shape == (18 * (lc.TINGGI + 8), lc.LEBAR_NOMOR + lc.LEBAR_POTONGAN + lc.LEBAR_TEKS, 3)
    daftar = json.loads((keluar / "lembar-contoh.json").read_text())
    assert [c["nomor"] for c in daftar["contoh"]] == list(range(1, 19))
    assert daftar["halaman"] == ["lembar-contoh-1.png"]


def test_keluaran_layar_tanpa_teks_plat(tmp_path, capsys):
    _, berkas, folder = siapkan(tmp_path, {"motor-terang": 2})

    lc.utama(berkas, folder, tmp_path / "keluar")

    cetak = capsys.readouterr().out
    assert "D1001AB" not in cetak and "1001" not in cetak
    assert "agen tidak membukanya" in cetak


def test_gambar_yang_hilang_tidak_membocorkan_nama_berkas(tmp_path):
    # OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr; pada INDO-ALPR jalur itu nomor plat.
    _, berkas, folder = siapkan(tmp_path, {"mobil-gelap": 1})
    (folder / "train/D 1001 AB_0001.png").unlink()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "1001" not in hasil.stdout + hasil.stderr


def test_baris_perintah(tmp_path):
    _, berkas, folder = siapkan(tmp_path, {"mobil-gelap": 1})

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), str(berkas)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/lembar-contoh-1.png").exists()
    assert salah.returncode == 2
