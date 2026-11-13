"""Uji tools/lab/plat_buatan.py: huruf yang digambar sendiri lengkap dan di dalam kisi, teks selalu sesuai pola plat Indonesia,
gambar plat berukuran dan berwarna benar, variasi tetap dengan benih, dan CLI yang menulis gambar dan label."""
import csv
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plat_buatan as pb  # noqa: E402
from plat import urai  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "plat_buatan.py"


def test_huruf_lengkap_dan_di_dalam_kisi():
    assert set(pb.HURUF) == set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.")
    for garis in pb.HURUF.values():
        for g in garis:
            assert len(g) >= 2 and all(0 <= x <= pb.LEBAR_KISI and 0 <= y <= pb.TINGGI_KISI + 0.5 for x, y in g)


def test_teks_acak_selalu_sesuai_pola_dan_beragam():
    teks = [pb.teks_acak(np.random.default_rng(i)) for i in range(500)]

    assert all(urai(t) is not None and urai(t).teks == t for t in teks)
    assert {len(urai(t).seri) for t in teks} == {0, 1, 2, 3}
    assert {len(urai(t).wilayah) for t in teks} == {1, 2}


def test_plat_berukuran_dan_berwarna_benar():
    rng = np.random.default_rng(0)
    gambar = pb.plat("B1234XY", "mobil", "putih", rng, tinggi=96)
    dasar, tulisan = pb.WARNA["putih"]

    assert gambar.shape[0] == 96 and 2.6 * 96 - 1 <= gambar.shape[1] <= 3.4 * 96 + 1
    assert np.abs(gambar[1, gambar.shape[1] // 2].astype(int) - dasar).max() < 40  # dasar di luar bingkai tipis
    assert (np.abs(gambar.astype(int) - tulisan).max(axis=2) < 40).mean() > 0.05  # ada tulisan
    assert not np.array_equal(gambar, pb.plat("D5678AB", "mobil", "putih", np.random.default_rng(0), tinggi=96))


def test_plat_motor_lebih_sempit():
    lebar = [pb.plat("B12AB", "motor", "hitam", np.random.default_rng(i)).shape[1] / 96 for i in range(20)]

    assert all(2.0 - 0.02 <= x <= 2.6 + 0.02 for x in lebar)


def test_huruf_baris_nomor_tidak_saling_menempel():
    # Teks panjang memakai huruf yang lebih kecil dengan bentuk tetap, bukan huruf yang dipersempit sampai menempel
    # (terlihat di lembar contoh pertama, Rencana 18 Task 1 Step 3).
    for teks in ("CJ2229SAK", "RE5661PTN", "B1234XY", "AB12C"):
        g = pb.plat(teks, "mobil", "putih", np.random.default_rng(0), tinggi=128)
        t, l = g.shape[:2]
        _, tulisan = pb.WARNA["putih"]
        tinta = (np.abs(g.astype(int) - tulisan).max(axis=2) < 100).astype(np.uint8)
        n, _ = cv2.connectedComponents(tinta[int(0.08 * t):int(0.68 * t), int(0.05 * l):int(0.95 * l)])
        assert n - 1 == len(teks), teks


def test_ubah_tetap_dengan_benih_dan_inframerah_kelabu():
    bersih = pb.plat("B1234XY", "mobil", "putih", np.random.default_rng(1))
    a, ka = pb.ubah(bersih, np.random.default_rng(5))
    b, kb = pb.ubah(bersih, np.random.default_rng(5))

    assert np.array_equal(a, b) and ka == kb and a.dtype == np.uint8 and a.ndim == 3
    for i in range(60):
        g, kondisi = pb.ubah(bersih, np.random.default_rng(i))
        if "inframerah" in kondisi:
            assert np.array_equal(g[..., 0], g[..., 1]) and np.array_equal(g[..., 1], g[..., 2])
            break
    else:
        raise AssertionError("inframerah tidak pernah terpilih dalam 60 benih")


def test_cli_buat_menulis_gambar_dan_label_yang_tetap(tmp_path):
    jalan = lambda d: subprocess.run([sys.executable, str(SKRIP), "buat", "20", str(d), "--benih", "3"], capture_output=True, text=True)  # noqa: E731
    a, b = jalan(tmp_path / "a"), jalan(tmp_path / "b")

    assert a.returncode == 0 and b.returncode == 0, a.stdout + a.stderr
    baris = list(csv.DictReader(open(tmp_path / "a" / "label.csv", newline="")))
    assert len(baris) == 20 and len(list((tmp_path / "a" / "gambar").glob("*.png"))) == 20
    assert all(urai(r["teks"]) is not None and r["jenis"] in ("mobil", "motor") and r["warna"] in pb.WARNA for r in baris)
    assert (tmp_path / "a" / "label.csv").read_text() == (tmp_path / "b" / "label.csv").read_text()
