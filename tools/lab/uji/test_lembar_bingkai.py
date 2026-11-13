"""Uji tools/lab/lembar_bingkai.py: titik ambil tetap, kotak hijau, lembar dari video buatan dengan pencari tiruan (kotak di
bawah ambang dibuang), penilaian dari nomor bingkai, dan CLI yang hanya mencetak jenis galat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_bingkai as lb  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_bingkai.py"


def test_titik_ambil_berjarak_sama_dan_tidak_di_ujung():
    assert lb.titik_ambil(100, 4) == [12, 37, 62, 87]
    assert lb.titik_ambil(0, 4) == []


def test_gambar_kotak_hijau_tanpa_mengubah_asli():
    asli = np.zeros((100, 200, 3), np.uint8)

    hasil = lb.gambar_kotak(asli, [(10, 10, 50, 40, 0.9)])

    assert tuple(hasil[10, 30]) == lb.HIJAU and not asli.any()


def video(jalur, n=40):
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 96))
    for _ in range(n):
        tulis.write(np.full((96, 160, 3), 90, np.uint8))
    tulis.release()


def cari_tiruan(gambar):
    return [(60.0, 40.0, 100.0, 56.0, 0.9), (10.0, 10.0, 30.0, 20.0, 0.1)]


def test_buat_lembar_dari_video_buatan(tmp_path):
    for nama in ("a.avi", "b.avi"):
        video(tmp_path / nama)
    daftar = [{"berkas": "b.avi", "kategori": "malam", "sudut": "parkiran"}, {"berkas": "a.avi", "kategori": "siang", "sudut": "gerbang"}]

    r = lb.buat_lembar(daftar, tmp_path, cari_tiruan, 0.25, tmp_path / "keluar", per_video=2, maks=3)

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert r == {"video": 2, "bingkai": 3, "halaman": 1}
    assert [(b["video"], b["gambar"], b["kotak"]) for b in isi["baris"]] == [("a.avi", 10, 1), ("a.avi", 30, 1), ("b.avi", 10, 1)]
    assert (tmp_path / "keluar" / "lembar-bingkai-1.png").exists()


def lembar_(baris):
    return {"baris": [{"nomor": i, **b} for i, b in enumerate(baris, 1)]}


def test_nilai_dari_nomor_bingkai_dan_penolakan():
    lembar = lembar_([{"sudut": "gerbang", "kategori": "siang"}] * 3 + [{"sudut": "parkiran", "kategori": "malam"}])

    h = lb.nilai(lembar, terlewat=[1, 4], tak_jelas=[2])

    assert (h["bingkai"], h["tak_jelas"]) == (4, 1)
    assert (h["kelompok"]["semua"]["dinilai"], h["kelompok"]["semua"]["ada_terlewat"]) == (3, 2)
    assert h["kelompok"]["gerbang-siang"] == {**h["kelompok"]["gerbang-siang"], "dinilai": 2, "ada_terlewat": 1}
    with pytest.raises(ValueError, match="tidak ada"):
        lb.nilai(lembar, terlewat=[9])
    with pytest.raises(ValueError, match="sekaligus"):
        lb.nilai(lembar, terlewat=[1], tak_jelas=[1])


def test_cli_nilai_dan_lembar_tanpa_model_hanya_jenis_galat(tmp_path):
    (tmp_path / "l.json").write_text(json.dumps(lembar_([{"sudut": "gerbang", "kategori": "siang"}] * 2)))
    a = subprocess.run([sys.executable, str(SKRIP), "nilai", str(tmp_path / "l.json"), str(tmp_path / "n.json"), "--terlewat", "2"],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, str(SKRIP), "lembar", str(tmp_path / "m.json"), str(tmp_path), str(tmp_path / "p.json"),
                        str(tmp_path / "pencari-rahasia"), str(tmp_path / "keluar")], capture_output=True, text=True)

    assert a.returncode == 0, a.stdout + a.stderr
    assert json.loads((tmp_path / "n.json").read_text())["kelompok"]["semua"]["ada_terlewat"] == 1
    assert b.returncode == 1 and "pencari-rahasia" not in b.stdout + b.stderr


def test_lembar_dengan_kendaraan_kotak_biru_dan_plat_di_luar_kendaraan_tidak_digambar(tmp_path):
    video(tmp_path / "a.avi")

    def cari(gambar):
        return [(60.0, 40.0, 100.0, 56.0, 0.9), (120.0, 70.0, 150.0, 86.0, 0.9)]

    def kendaraan(gambar):
        return [(50.0, 30.0, 110.0, 66.0, 0.8, "motor")]

    lb.buat_lembar([{"berkas": "a.avi"}], tmp_path, cari, 0.25, tmp_path / "keluar", per_video=1, maks=1,
                   cari_kendaraan=kendaraan)

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert [(b["kotak"], b["kendaraan"], b["tersaring"]) for b in isi["baris"]] == [(1, 1, 1)]
    halaman = cv2.imread(str(tmp_path / "keluar" / "lembar-bingkai-1.png"))
    assert tuple(halaman[40 + 50, 50]) == lb.BIRU  # tepi kiri kotak kendaraan, di bawah pita nomor


def test_lembar_cara_potong_mencatat_cara_dan_kotak(tmp_path):
    video(tmp_path / "a.avi")

    def cari(gambar):
        t, l = gambar.shape[:2]
        return [(0.4 * l, 0.4 * t, 0.6 * l, 0.6 * t, 0.9)]

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "motor")]

    lb.buat_lembar([{"berkas": "a.avi"}], tmp_path, cari, 0.25, tmp_path / "keluar", per_video=1, maks=1,
                   cari_kendaraan=kendaraan, cara="potong")

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert isi["cara_kendaraan"] == "potong" and [(b["kotak"], b["kendaraan"]) for b in isi["baris"]] == [(1, 1)]


def test_lembar_letak_tidak_menggambar_plat_yang_tidak_lolos(tmp_path):
    video(tmp_path / "a.avi")

    def cari(gambar):
        return [(60.0, 40.0, 100.0, 56.0, 0.9), (120.0, 70.0, 150.0, 86.0, 0.9)]

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "mobil")]

    lb.buat_lembar([{"berkas": "a.avi"}], tmp_path, cari, 0.25, tmp_path / "keluar", per_video=1, maks=1,
                   cari_kendaraan=kendaraan, letak="ry0.6")

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert isi["letak"] == "ry0.6" and [(b["kotak"], b["tersaring"], b["tersaring_letak"]) for b in isi["baris"]] == [(0, 1, 1)]
