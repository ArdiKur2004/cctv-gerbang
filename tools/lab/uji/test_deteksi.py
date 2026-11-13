"""Uji tools/lab/deteksi.py: IoU, label YOLO, pencocokan tebakan dengan kebenaran, kelompok, ambang dari validasi, dan
ringkasan tanpa nama berkas."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deteksi as dt  # noqa: E402


def test_iou():
    assert dt.iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert dt.iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert abs(dt.iou((0, 0, 10, 10), (5, 0, 15, 10)) - 50 / 150) < 1e-9


def test_baca_label_ke_piksel_dan_melewati_baris_bukan_kotak(tmp_path):
    berkas = tmp_path / "a.txt"
    # Pecahan biner (0,25; 0,5) supaya hasilnya tepat tanpa galat pembulatan desimal.
    berkas.write_text("0 0.5 0.5 0.25 0.5\nThis dataset was exported via roboflow.com\n1 2 3\n")

    assert dt.baca_label(berkas, 200, 100) == [(75.0, 25.0, 125.0, 75.0)]


def test_cocokkan_satu_kebenaran_paling_banyak_satu_tebakan():
    kebenaran = [(0, 0, 10, 10)]

    assert dt.cocokkan([(0, 0, 10, 10, 0.9), (1, 1, 10, 10, 0.8)], kebenaran) == ({0}, 1)
    assert dt.cocokkan([(50, 50, 60, 60, 0.9)], kebenaran) == (set(), 1)


def test_cocokkan_mendahulukan_keyakinan_tertinggi():
    kebenaran = [(0, 0, 10, 10), (100, 0, 110, 10)]

    ketemu, palsu = dt.cocokkan([(1, 0, 11, 10, 0.3), (0, 0, 10, 10, 0.9)], kebenaran)

    assert ketemu == {0} and palsu == 1


def gambar(gelap, kebenaran, tebakan, tinggi=1000):
    return {"gelap": gelap, "tinggi": tinggi, "kebenaran": kebenaran, "tebakan": tebakan}


def test_ringkas_per_kelompok_dan_ambang():
    per_gambar = [gambar(False, [(0, 0, 100, 50)], [(0, 0, 100, 50, 0.9)]),
                  gambar(True, [(0, 0, 100, 20)], [(0, 0, 100, 20, 0.4), (500, 500, 600, 550, 0.8)])]

    r = dt.ringkas(per_gambar, 0.5)

    assert (r["semua"]["plat"], r["semua"]["plat_ditemukan"], r["semua"]["kotak_palsu"]) == (2, 1, 1)
    assert (r["gelap"]["plat"], r["gelap"]["plat_ditemukan"]) == (1, 0)
    assert (r["kecil"]["plat"], r["besar"]["plat"]) == (1, 1)
    assert r["semua"]["terlalu_sedikit"] and r["terang"]["gambar"] == 1


def test_pilih_ambang_f1_terbesar_dan_terendah_bila_seri():
    per_gambar = [gambar(False, [(0, 0, 100, 50)], [(0, 0, 100, 50, 0.9), (500, 500, 600, 550, 0.2)])]

    assert dt.pilih_ambang(per_gambar) == 0.25


def test_nilai_ambang_dari_validasi_lalu_uji_tanpa_nama_berkas(tmp_path):
    for sisi in ("valid", "test"):
        (tmp_path / sisi / "images").mkdir(parents=True)
        (tmp_path / sisi / "labels").mkdir(parents=True)
        for i in range(3):
            cv2.imwrite(str(tmp_path / sisi / "images" / f"B{1000 + i}XY_{sisi}.jpg"), np.full((100, 200, 3), 200, np.uint8))
            (tmp_path / sisi / "labels" / f"B{1000 + i}XY_{sisi}.txt").write_text("0 0.5 0.5 0.2 0.2\n")

    def cari(_):
        return [(80, 40, 120, 60, 0.9), (0, 0, 10, 10, 0.2)]

    hasil = dt.nilai(tmp_path, cari)

    assert hasil["ambang"] == 0.25
    assert hasil["uji"]["semua"]["plat_ditemukan"] == hasil["uji"]["semua"]["plat"] == 3
    assert hasil["uji"]["semua"]["kotak_palsu"] == 0
    assert "B100" not in json.dumps(hasil)
