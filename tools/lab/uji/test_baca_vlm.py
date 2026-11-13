"""Uji tools/lab/baca_vlm.py dengan pembaca tiruan: penilaian per gambar dan per kedatangan, dan tanpa nomor plat di
ringkasan maupun layar. Model sungguhan diuji terpisah di tools/lab/uji_gpu/."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_vlm as bv  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "baca_vlm.py"


def siapkan(tmp_path, kedatangan):
    """`kedatangan` = daftar (teks, kelompok, banyak gambar)."""
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    uji = []
    for teks, kelompok, banyak in kedatangan:
        berkas = []
        for i in range(banyak):
            nama = f"test/{teks}_{i}.png"
            cv2.imwrite(str(folder / nama), np.full((30, 100, 3), 200, np.uint8))
            berkas.append(nama)
        uji.append({"teks": teks, "kelompok": kelompok, "berkas": berkas})
    pembagian = {"latih": [], "uji": uji}
    jalur = tmp_path / "pembagian.json"
    jalur.write_text(json.dumps(pembagian))
    return pembagian, jalur, folder


def pembaca(jawaban):
    sisa = iter(jawaban)
    return lambda gambar: next(sisa)


def test_bacaan_dibersihkan_lalu_dibandingkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 1)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["b 1234 xyz."]))

    k = ringkasan["per_kelompok"]["mobil-terang"]
    assert (k["gambar"], k["gambar_benar"], k["kedatangan_benar"]) == (1, 1, 1)


def test_kedatangan_memakai_bacaan_terbanyak(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "motor-gelap", 3)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["B1234XYZ", "B1234XY2", "B1234XYZ"]))

    k = ringkasan["per_kelompok"]["motor-gelap"]
    assert (k["gambar_benar"], k["kedatangan_benar"], k["kedatangan_ragu"]) == (2, 1, 0)


def test_seri_di_puncak_menjadi_ragu_bukan_tebakan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "motor-gelap", 2)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["B1234XYZ", "B1234XY2"]))

    k = ringkasan["per_kelompok"]["motor-gelap"]
    assert (k["kedatangan_benar"], k["kedatangan_ragu"]) == (0, 1)


def test_bacaan_di_luar_pola_dihitung(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-gelap", 1)])

    _, ringkasan = bv.nilai(pembagian, folder, pembaca(["HELLO"]))

    k = ringkasan["per_kelompok"]["mobil-gelap"]
    assert (k["gambar_benar"], k["gambar_luar_pola"]) == (0, 1)


def test_rentang_wilson():
    assert bv.wilson(0, 0) is None
    bawah, atas = bv.wilson(50, 100)
    assert abs(bawah - 0.404) < 0.001 and abs(atas - 0.596) < 0.001


def test_utama_menulis_hasil_dan_ringkasan_tanpa_nomor_plat(tmp_path, capsys):
    _, jalur, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 2), ("D5678AB", "motor-terang", 1)])
    keluar = tmp_path / "keluar"

    kode = bv.utama(jalur, folder, tmp_path / "model-tiruan", keluar, baca=pembaca(["B1234XYZ", "B1234XYZ", "D5678A"]))

    assert kode == 0
    assert len((keluar / "hasil.jsonl").read_text().splitlines()) == 3
    teks = (keluar / "ringkasan.json").read_text()
    for larangan in ("B1234XYZ", "D5678AB", "D5678A", "1234", "5678"):
        assert larangan not in teks
    assert set(json.loads(teks)["per_kelompok"]) == set(bv.KELOMPOK)
    cetak = capsys.readouterr().out
    assert "1234" not in cetak and "5678" not in cetak
    assert "mobil-gelap   kosong" in cetak


def test_gambar_yang_hilang_tidak_membocorkan_nama_berkas(tmp_path):
    # OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr; pada INDO-ALPR jalur itu nomor plat. Proses terpisah
    # supaya yang diuji pembisuan milik baca_vlm sendiri, bukan milik modul lain yang sudah dimuat pytest.
    pembagian, _, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 1)])
    (folder / "test/B1234XYZ_0.png").unlink()
    kode = ("import json, sys; sys.path.insert(0, sys.argv[1]); import baca_vlm as bv; "
            "_, r = bv.nilai(json.loads(sys.argv[2]), sys.argv[3], lambda g: 'X'); "
            "print(r['per_kelompok']['mobil-terang']['gambar'])")

    hasil = subprocess.run([sys.executable, "-c", kode, str(SKRIP.parent), json.dumps(pembagian), str(folder)],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert hasil.stdout.strip() == "1"
    assert "1234" not in hasil.stderr


def test_baris_perintah_menolak_folder_model_tak_terdaftar_dengan_kode_2(tmp_path):
    # Rantainya: baris perintah -> gerbang folder model, SEBELUM torch dimuat atau set uji dibaca.
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path), str(lain),
                            str(tmp_path / "keluar")], capture_output=True, text=True)

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout
    assert not (tmp_path / "keluar").exists()


def test_sisi_latih_dibaca_bila_diminta(tmp_path):
    pembagian, jalur, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 1)])
    jalur.write_text(json.dumps({"latih": pembagian["uji"], "uji": []}))

    kode = bv.utama(jalur, folder, tmp_path / "model-tiruan", tmp_path / "keluar", baca=pembaca(["B1234XYZ"]), sisi="latih")

    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert kode == 0 and r["sisi"] == "latih"
    assert r["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1


def test_baris_perintah_menerima_sisi_latih_sampai_ke_gerbang_model(tmp_path):
    # Rantainya: argumen sisi diterima, lalu gerbang folder model menolak model tiruan (bukan petunjuk pakai).
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "p.json"), str(tmp_path), str(lain),
                            str(tmp_path / "keluar"), "latih"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "DITOLAK" in hasil.stdout, hasil.stdout + hasil.stderr


def test_baris_perintah_menolak_sisi_yang_tidak_dikenal(tmp_path):
    hasil = subprocess.run([sys.executable, str(SKRIP), "p.json", "g", "m", "k", "semua"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "Pakai" in hasil.stdout
