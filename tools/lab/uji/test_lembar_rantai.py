"""Uji tools/lab/lembar_rantai.py: pilihan baris tetap dan bergiliran antarvideo, penilaian dari jawaban owner (nomor baris dan
jenis saja), penolakan jawaban yang tidak cocok dengan lembar, dan rantai CLI lembar lalu nilai dengan layar tanpa teks plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_rantai as lr  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_rantai.py"


def kedatangan(video, nomor, teks="B1234XY", status="yakin", kategori="siang"):
    return {"video": video, "nomor": nomor, "teks": teks, "status": status, "kategori": kategori,
            "potongan": f"{video}-{nomor}.png"}


def test_pilih_baris_tetap_dan_bergiliran_antarvideo():
    semua = [kedatangan("a", n) for n in range(1, 6)] + [kedatangan("b", 1)] + [kedatangan("c", n) for n in (1, 2)]

    pilih = lr.pilih_baris(semua, maks=4)

    assert [k["video"] for k in pilih] == ["a", "b", "c", "a"]
    assert pilih == lr.pilih_baris(list(reversed(semua)), maks=4)
    assert len(lr.pilih_baris(semua, maks=100)) == 8


def lembar_(baris):
    return {"baris": [{"nomor": i, **b} for i, b in enumerate(baris, 1)]}


def test_nilai_dari_nomor_baris_dan_jenis():
    lembar = lembar_([
        {"teks": "B1234XY", "status": "yakin", "kategori": "siang"},  # 1 benar, yakin
        {"teks": "B1234XY", "status": "yakin", "kategori": "siang"},  # 2 salah, yakin
        {"teks": "B1234XY", "status": "ragu", "kategori": "siang"},  # 3 benar, ragu, motor
        {"teks": "", "status": "ragu", "kategori": "siang"},  # 4 tanpa bacaan sah: salah, ragu
        {"teks": "B1234XY", "status": "yakin", "kategori": "malam"},  # 5 tak terbaca: tidak dinilai
        {"teks": "B1234XY", "status": "yakin", "kategori": "malam"},  # 6 bukan plat: tidak dinilai
    ])

    h = lr.nilai(lembar, salah=[2], tak_terbaca=[5], bukan_plat=[6], motor=[3])

    assert (h["baris"], h["tak_terbaca"], h["bukan_plat"], h["motor"]) == (6, 1, 1, 1)
    s = h["kelompok"]["semua"]
    assert (s["dinilai"], s["benar_yakin"], s["benar_ragu"], s["salah_ragu"], s["salah_yakin"]) == (4, 1, 1, 1, 1)
    assert h["kelompok"]["siang-mobil"]["dinilai"] == 3 and h["kelompok"]["siang-motor"]["benar_ragu"] == 1
    assert "malam-mobil" not in h["kelompok"] and s["terlalu_sedikit"] is True


def test_nilai_menolak_nomor_yang_tidak_ada_dan_jenis_yang_bertentangan():
    lembar = lembar_([{"teks": "B1234XY", "status": "yakin", "kategori": "siang"}] * 3)

    with pytest.raises(ValueError, match="tidak ada"):
        lr.nilai(lembar, salah=[4])
    with pytest.raises(ValueError, match="sekaligus"):
        lr.nilai(lembar, salah=[1], bukan_plat=[1])


def test_rantai_cli_lembar_lalu_nilai_tanpa_teks_plat_di_layar(tmp_path):
    folder = tmp_path / "rantai"
    (folder / "potongan").mkdir(parents=True)
    semua = [kedatangan("v1", 1), kedatangan("v1", 2, status="ragu"), kedatangan("v2", 1, teks="")]
    for k in semua:
        cv2.imwrite(str(folder / "potongan" / k["potongan"]), np.full((20, 60, 3), 200, np.uint8))
    (folder / "kedatangan.jsonl").write_text("".join(json.dumps(k) + "\n" for k in semua))

    a = subprocess.run([sys.executable, str(SKRIP), "lembar", str(folder), str(tmp_path / "lembar")],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, str(SKRIP), "nilai", str(tmp_path / "lembar" / "lembar-rantai.json"),
                        str(tmp_path / "lembar" / "nilai.json"), "--salah", "2", "--motor", "1"], capture_output=True, text=True)

    layar = a.stdout + a.stderr + b.stdout + b.stderr
    assert a.returncode == 0 and b.returncode == 0, layar[-2000:]
    assert "B1234" not in layar
    assert (tmp_path / "lembar" / "lembar-rantai-1.png").exists()
    nilai = json.loads((tmp_path / "lembar" / "nilai.json").read_text())
    assert nilai["baris"] == 3 and nilai["kelompok"]["semua"]["dinilai"] == 3
    assert "B1234" not in (tmp_path / "lembar" / "nilai.json").read_text()


def test_pilih_baris_urut_keyakinan_kotak():
    semua = [{**kedatangan("a", n), "yakin_kotak": y} for n, y in ((1, 0.3), (2, 0.9), (3, 0.6))] + [
        {**kedatangan("b", 1), "yakin_kotak": 0.8}]

    pilih = lr.pilih_baris(semua, maks=3, urut="keyakinan")

    assert [(k["video"], k["nomor"]) for k in pilih] == [("a", 2), ("b", 1), ("a", 3)]
