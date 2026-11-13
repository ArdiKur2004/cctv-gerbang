"""Uji tools/lab/lembar_kendaraan.py (Rencana 20, K39): lembar kendaraan bernomor dari video buatan, jawaban owner, penilaian
calon, aturan memilih, dan banding dari video sampai hitungan, dengan pencari tiruan."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_kendaraan as lk  # noqa: E402


def video(jalur, n=20):
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), 10, (320, 192))
    for _ in range(n):
        tulis.write(np.full((192, 320, 3), 90, np.uint8))
    tulis.release()


TINGGI = (20.0, 20.0, 120.0, 180.0, 0.8, "mobil")
PENDEK = (200.0, 20.0, 260.0, 40.0, 0.7, "motor")  # tinggi 20 < MIN_TINGGI: tidak bernomor


def dua_kendaraan(gambar):
    return [TINGGI, PENDEK]


dua_kendaraan.ambang = 0.25


def test_baca_jawaban_per_bingkai_dan_penolakan():
    assert lk.baca_jawaban("3: 1, 4; 7: 2\n9:") == {3: {1, 4}, 7: {2}, 9: set()}
    assert lk.baca_jawaban("") == {}
    with pytest.raises(ValueError, match="jawaban"):
        lk.baca_jawaban("3 1 4")


def test_buat_lembar_hanya_kendaraan_tinggi_yang_bernomor(tmp_path):
    video(tmp_path / "a.avi")

    r = lk.buat_lembar([{"berkas": "a.avi", "sudut": "gerbang", "kategori": "siang"}], tmp_path, dua_kendaraan,
                       tmp_path / "keluar", per_video=2, maks=5)

    isi = json.loads((tmp_path / "keluar" / "lembar-kendaraan.json").read_text())
    assert r == {"video": 1, "bingkai": 2, "kendaraan_bernomor": 2, "halaman": 1}
    assert [b["gambar"] for b in isi["baris"]] == [5, 15]
    assert isi["baris"][0]["bernomor"] == [list(TINGGI[:4]) + [TINGGI[4], TINGGI[5]]] and len(isi["baris"][0]["kendaraan"]) == 2
    halaman = cv2.imread(str(tmp_path / "keluar" / "lembar-kendaraan-1.png"))
    assert tuple(halaman[40 + 100, 20]) == lk.BIRU


def lembar_satu(bernomor, kendaraan=None, video_="a.avi"):
    return {"baris": [{"nomor": 1, "video": video_, "gambar": 5, "bernomor": bernomor,
                       "kendaraan": kendaraan if kendaraan is not None else bernomor}]}


def test_nilai_calon_menghitung_ditemukan_dan_kotak_salah_tempat():
    a, b = [0, 0, 100, 100, 0.9, "mobil"], [200, 0, 300, 100, 0.9, "motor"]
    lembar = lembar_satu([a, b])
    kotak = {1: [(40, 60, 60, 70, 0.9), (10, 10, 20, 20, 0.5), (240, 60, 260, 70, 0.9), (500, 500, 510, 505, 0.9)]}

    h = lk.nilai_calon(lembar, {1: {1}}, kotak)

    assert h == {"plat_terbaca": 1, "ditemukan": 1, "kotak_lebih": 1, "kotak_kendaraan_lain": 1, "kotak_luar": 1}
    with pytest.raises(ValueError, match="kendaraan"):
        lk.nilai_calon(lembar, {1: {3}}, kotak)
    with pytest.raises(ValueError, match="bingkai"):
        lk.nilai_calon(lembar, {2: {1}}, kotak)


def hasil_(nama, ditemukan, salah, ditemukan_valid):
    return {"nama": nama, "pencari": nama.split("-")[0], "semua": {"ditemukan": ditemukan, "kotak_lebih": salah,
            "kotak_kendaraan_lain": 0, "kotak_luar": 0}, "validasi": {"ditemukan": ditemukan_valid}}


def test_pilih_menurut_aturan_dan_pencari_baru_harus_tidak_kalah_di_validasi():
    calon = [hasil_("lama-potong-0.25", 10, 3, 2), hasil_("lama-saring-0.25", 10, 1, 2), hasil_("baru-potong-0.1", 12, 0, 1)]

    assert lk.pilih(calon)["nama"] == "lama-saring-0.25"  # baru menang di semua, tetapi kalah di validasi (1 < 2)
    calon[2]["validasi"]["ditemukan"] = 2
    assert lk.pilih(calon)["nama"] == "baru-potong-0.1"


def test_banding_dari_video_potong_menemukan_yang_saring_lewatkan(tmp_path):
    video(tmp_path / "a.avi")
    lk.buat_lembar([{"berkas": "a.avi", "sudut": "gerbang", "kategori": "siang"}], tmp_path, dua_kendaraan, tmp_path / "keluar",
                   per_video=1, maks=1)
    lembar = json.loads((tmp_path / "keluar" / "lembar-kendaraan.json").read_text())

    def cari_bawah(gambar):
        """Kotak di 0,45-0,55 lebar dan 0,8-0,9 tinggi MASUKAN: di gambar utuh tengahnya (160, 163) di luar kendaraan;
        di potongan kendaraan tengahnya di dalam."""
        t, l = gambar.shape[:2]
        return [(0.45 * l, 0.8 * t, 0.55 * l, 0.9 * t, 0.3)]

    hasil = lk.banding(lembar, tmp_path, {"lama": cari_bawah}, {1: {1}}, validasi=set())

    per_nama = {h["nama"]: h["semua"] for h in hasil}
    assert len(hasil) == 6  # satu pencari x 2 cara x 3 ambang
    assert per_nama["lama-saring-0.25"]["ditemukan"] == 0 and per_nama["lama-potong-0.25"]["ditemukan"] == 1
    assert per_nama["lama-potong-0.5"]["ditemukan"] == 0  # yakin 0,3 di bawah ambang
