"""Uji tools/lab/halaman_label.py (Rencana 24 Task 4): halaman pelabelan untuk owner (plat terlewat dan bacaan salah di tangkapan),
lalu jawaban halaman digabung dengan label tetap dari lembar menjadi label.json. Nama berkas asli tidak muncul di halaman, kotak di
luar gambar dan nomor butir asing ditolak, dan teks di luar pola tidak menjadi label."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import halaman_label as hl  # noqa: E402

KEDATANGAN = [
    {"video": "g0001", "nomor": 1, "kategori": "mobil", "sisi": "latih", "teks": "B1234XY", "kotak": [10.0, 10.0, 60.0, 30.0]},
    {"video": "g0001", "nomor": 2, "kategori": "mobil", "sisi": "latih", "teks": "B9999ZZ", "kotak": [100.0, 10.0, 150.0, 30.0]},
    {"video": "g0005", "nomor": 1, "kategori": "motor", "sisi": "uji", "teks": "", "kotak": [5.0, 5.0, 40.0, 20.0]},
    {"video": "g0005", "nomor": 2, "kategori": "motor", "sisi": "uji", "teks": "AB12C", "kotak": [50.0, 50.0, 90.0, 70.0]},
]


def siapkan(tmp_path):
    capture, baca = tmp_path / "capture", tmp_path / "baca"
    peta = {}
    for i, sub in enumerate(("capture cctv mobil", "capture cctv motor", "capture cctv mobil", "capture cctv mobil",
                             "capture cctv motor"), 1):
        (capture / sub).mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(capture / sub / f"rahasia-{i}.png"), np.full((180, 320, 3), 40 * i, np.uint8))
        peta[f"g{i:04d}"] = f"{sub}/rahasia-{i}.png"
    baca.mkdir()
    (baca / "peta-berkas.json").write_text(json.dumps(peta))
    (baca / "kedatangan.jsonl").write_text("".join(json.dumps(k) + "\n" for k in KEDATANGAN))
    (tmp_path / "lembar-plat.json").write_text(json.dumps({"baris": [
        {"nomor": i, "video": k["video"], "kedatangan": k["nomor"], "kategori": k["kategori"], "teks": k["teks"]}
        for i, k in enumerate(KEDATANGAN, 1)]}))
    (tmp_path / "lembar-tanpa.json").write_text(json.dumps({"baris": [
        {"nomor": 1, "gambar": "g0002", "kelompok": "motor", "sisi": "latih", "bernomor": [[0.0, 0.0, 200.0, 150.0, "motor"]]},
        {"nomor": 2, "gambar": "g0003", "kelompok": "mobil", "sisi": "uji", "bernomor": []},
        {"nomor": 3, "gambar": "g0004", "kelompok": "mobil", "sisi": "latih", "bernomor": [[0.0, 0.0, 100.0, 100.0, "mobil"]]}]}))
    (tmp_path / "jawaban-tanpa.json").write_text(json.dumps(
        {"terbaca": {"1": 1}, "terbaca_tanpa_kotak": [2], "luar_indonesia": [3], "dikeluarkan": []}))
    return capture, baca


def buat(tmp_path):
    capture, baca = siapkan(tmp_path)
    return hl.buat(capture, baca, tmp_path / "lembar-plat.json", tmp_path / "lembar-tanpa.json", tmp_path / "jawaban-tanpa.json",
                   tmp_path / "keluar", salah=[2], tak_terbaca=[4], bukan_plat=[3])


def terima(tmp_path, butir):
    (tmp_path / "simpan.json").write_text(json.dumps({"butir": butir}))
    return hl.terima(tmp_path / "keluar" / "butir.json", tmp_path / "simpan.json", tmp_path / "keluar")


def test_buat_halaman_tiga_butir_tanpa_nama_asli_dan_tanpa_sumber_luar(tmp_path):
    r = buat(tmp_path)

    assert r == {"butir": 3, "terlewat": 2, "salah": 1, "dikeluarkan": 1}
    keluar = tmp_path / "keluar"
    isi = json.loads((keluar / "butir.json").read_text())
    assert [(b["id"], b["jenis"], b["gambar"]) for b in isi["butir"]] == [
        ("t1", "terlewat", "g0002"), ("t2", "terlewat", "g0003"), ("s2", "salah", "g0001")]
    assert isi["butir"][0]["kendaraan"] == [0.0, 0.0, 200.0, 150.0] and isi["butir"][1]["kendaraan"] is None
    assert all((keluar / b["berkas"]).exists() and (b["lebar"], b["tinggi"]) == (320, 180) for b in isi["butir"])
    halaman = (keluar / "halaman.html").read_text(encoding="utf-8")
    assert '"t1"' in halaman and "localStorage" in halaman
    assert "rahasia" not in halaman + json.dumps(isi) and "http" not in halaman  # tanpa nama asli, tanpa sumber luar


def test_terima_menggabungkan_label_tetap_dan_jawaban_halaman(tmp_path):
    buat(tmp_path)

    r = terima(tmp_path, {"t1": {"kotak": [20, 30, 80, 50], "teks": "b 1234 xy", "tak_terbaca": False},
                          "s2": {"kotak": None, "teks": "B9999ZX", "tak_terbaca": False}})

    assert (r["butir_terisi"], r["butir_kosong"], r["teks_tak_sesuai_pola"]) == (2, 1, 0)
    label = json.loads((tmp_path / "keluar" / "label.json").read_text())
    g = label["gambar"]
    assert [(p["kotak"], p["teks"], p["asal"]) for p in g["g0001"]["plat"]] == [
        ([10, 10, 60, 30], "B1234XY", "lembar"), ([100, 10, 150, 30], "B9999ZX", "halaman")]
    assert [(p["kotak"], p["teks"]) for p in g["g0002"]["plat"]] == [([20, 30, 80, 50], "B1234XY")]
    assert g["g0003"]["plat"] == [] and g["g0003"]["plat_tanpa_label"] == 1
    assert [(p["teks"], p["tak_terbaca"]) for p in g["g0005"]["plat"]] == [(None, True)]
    assert g["g0005"]["bukan_plat"] == [[5, 5, 40, 20]] and g["g0005"]["sisi"] == "uji"
    assert label["dikeluarkan"] == {"g0004": "luar_indonesia"} and "g0004" not in g


def test_kotak_di_luar_gambar_ditolak(tmp_path):
    buat(tmp_path)

    with pytest.raises(ValueError):
        terima(tmp_path, {"t1": {"kotak": [0, 0, 9999, 50], "teks": "B1234XY", "tak_terbaca": False}})


def test_nomor_butir_asing_ditolak(tmp_path):
    buat(tmp_path)

    with pytest.raises(ValueError):
        terima(tmp_path, {"t99": {"kotak": [20, 30, 80, 50], "teks": "B1234XY", "tak_terbaca": False}})


def bahan_nilai(tmp_path, teks_terbaca):
    """label.json (gambar uji g0001: satu plat berteks, satu tak terbaca, satu kotak bukan plat) dan keluaran baca_gambar baru
    yang nomor gambarnya TERTUKAR (g0001 <-> g0002), supaya pencocokan lewat jalur berkas, bukan lewat nomor, ikut teruji."""
    label = {"gambar": {
        "g0001": {"kelompok": "mobil", "sisi": "uji", "bukan_plat": [[200, 100, 240, 120]], "plat_tanpa_label": 0, "plat": [
            {"kotak": [10, 10, 50, 30], "teks": "B1AB", "tak_terbaca": False, "asal": "lembar"},
            {"kotak": [100, 10, 140, 30], "teks": None, "tak_terbaca": True, "asal": "lembar"}]},
        "g0002": {"kelompok": "mobil", "sisi": "latih", "bukan_plat": [], "plat_tanpa_label": 0, "plat": [
            {"kotak": [10, 10, 50, 30], "teks": "D2CD", "tak_terbaca": False, "asal": "lembar"}]}}, "dikeluarkan": {}}
    (tmp_path / "label.json").write_text(json.dumps(label))
    (tmp_path / "peta-label.json").write_text(json.dumps({"g0001": "a/x.png", "g0002": "a/y.png"}))
    baru = tmp_path / "baru"
    baru.mkdir()
    (baru / "peta-berkas.json").write_text(json.dumps({"g0001": "a/y.png", "g0002": "a/x.png"}))
    tiba = [{"video": "g0002", "nomor": 1, "kategori": "mobil", "teks": teks_terbaca, "kotak": [11.0, 11.0, 50.0, 30.0]},
            {"video": "g0002", "nomor": 2, "kategori": "mobil", "teks": "", "kotak": [200.0, 100.0, 240.0, 120.0]},
            {"video": "g0002", "nomor": 3, "kategori": "mobil", "teks": "", "kotak": [300.0, 100.0, 330.0, 120.0]},
            {"video": "g0001", "nomor": 1, "kategori": "mobil", "teks": "D2CD", "kotak": [10.0, 10.0, 50.0, 30.0]}]
    (baru / "kedatangan.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tiba))
    return baru


def test_nilai_label_mencocokkan_lewat_jalur_berkas_dan_menghitung_per_jenis(tmp_path):
    baru = bahan_nilai(tmp_path, "B1AB")

    r = hl.nilai_label(tmp_path / "label.json", tmp_path / "peta-label.json", baru, sisi="uji")

    assert r["gambar"] == 1  # gambar latih tidak dinilai, dan bacaan di gambar latih tidak terhitung
    assert r["per_kelompok"]["mobil"] == {"plat_berlabel": 2, "ditemukan": 1, "berteks": 1, "dibaca_benar": 1,
                                          "kotak_di_luar_label": 2, "kotak_di_bukan_plat": 1}


def test_nilai_label_bacaan_salah_tidak_dihitung_benar(tmp_path):
    baru = bahan_nilai(tmp_path, "B1AD")

    r = hl.nilai_label(tmp_path / "label.json", tmp_path / "peta-label.json", baru, sisi="uji")

    assert (r["per_kelompok"]["mobil"]["ditemukan"], r["per_kelompok"]["mobil"]["dibaca_benar"]) == (1, 0)


def test_teks_di_luar_pola_tidak_menjadi_label(tmp_path):
    buat(tmp_path)

    r = terima(tmp_path, {"t1": {"kotak": [20, 30, 80, 50], "teks": "12345", "tak_terbaca": False}})

    assert r["teks_tak_sesuai_pola"] == 1
    g = json.loads((tmp_path / "keluar" / "label.json").read_text())["gambar"]
    assert [(p["kotak"], p["teks"]) for p in g["g0002"]["plat"]] == [([20, 30, 80, 50], None)]
