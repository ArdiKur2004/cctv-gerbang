"""Uji tools/lab/rapikan.py (Rencana 27, K54): kotak plat dirapikan dengan pencarian kedua di potongan sekitar kotak pertama. Tanpa model:
pencari tiruan yang melihat persegi putih (plat) di gambar masukannya."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rapikan as rp  # noqa: E402

PLAT = (140, 100, 200, 120)  # x1, y1, x2, y2 persegi putih di gambar 300 x 400


def gambar_plat():
    g = np.full((300, 400, 3), 60, np.uint8)
    g[PLAT[1]:PLAT[3], PLAT[0]:PLAT[2]] = 255
    return g


def cari_putih(gambar):
    """Kotak tepat di sekeliling piksel putih di gambar masukan, ditambah satu kotak lemah di pojok."""
    ys, xs = np.where(gambar[:, :, 0] > 200)
    kotak = [(0.0, 0.0, 5.0, 5.0, 0.05)]
    if len(xs):
        kotak.append((float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1), 0.9))
    return kotak


def test_kotak_terlalu_besar_dan_terlalu_kecil_menjadi_pas():
    g = gambar_plat()

    besar = rp.rapikan_kotak(g, (120.0, 90.0, 230.0, 135.0, 0.7, "mobil", (0.0, 0.0, 400.0, 300.0)), cari_putih, 0.25, 1.0)
    kecil = rp.rapikan_kotak(g, (150.0, 104.0, 185.0, 116.0, 0.6), cari_putih, 0.25, 1.0)

    assert besar[:4] == tuple(float(x) for x in PLAT) and kecil[:4] == tuple(float(x) for x in PLAT)
    # Yakin, jenis, dan kotak kendaraan dari kotak pertama dibawa apa adanya.
    assert besar[4:] == (0.7, "mobil", (0.0, 0.0, 400.0, 300.0)) and kecil[4:] == (0.6,)


def test_pencarian_kedua_hanya_di_potongan_sekitar_kotak():
    g = gambar_plat()
    ukuran = []

    def cari(potongan):
        ukuran.append(potongan.shape[:2])
        return cari_putih(potongan)

    rp.rapikan_kotak(g, (150.0, 104.0, 185.0, 116.0, 0.6), cari, 0.25, 1.0)

    assert ukuran == [(36, 105)]  # lebar 35 dan tinggi 12, diperlebar 1 kali di tiap sisi


def test_tanpa_kotak_kedua_di_dalam_kotak_pertama_kotak_lama_dipakai_dan_konteks_nol_mati():
    g = gambar_plat()
    lain = (300.0, 200.0, 340.0, 215.0, 0.8)  # tidak ada plat di sekitarnya
    dipanggil = []

    def cari(potongan):
        dipanggil.append(1)
        return cari_putih(potongan)

    assert rp.rapikan_kotak(g, lain, cari_putih, 0.25, 1.0) == lain
    assert rp.rapikan_kotak(g, (120.0, 90.0, 230.0, 135.0, 0.7), cari, 0.25, 0.0) == (120.0, 90.0, 230.0, 135.0, 0.7)
    assert not dipanggil  # konteks 0: pencari tidak dipanggil sama sekali
    with pytest.raises(ValueError, match="konteks"):
        rp.rapikan_kotak(g, lain, cari_putih, 0.25, -0.5)


def test_kotak_kedua_di_bawah_ambang_tidak_dipakai():
    g = gambar_plat()

    def cari_lemah(potongan):
        return [(*k[:4], 0.1) for k in cari_putih(potongan)]

    assert rp.rapikan_kotak(g, (120.0, 90.0, 230.0, 135.0, 0.7), cari_lemah, 0.25, 1.0) == (120.0, 90.0, 230.0, 135.0, 0.7)
