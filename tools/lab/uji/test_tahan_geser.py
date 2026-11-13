"""Uji tools/lab/tahan_geser.py (Rencana 26, K51): potongan yang digeser atau diperlebar, pungut suara bacaan yang sesuai pola plat, dan
pembacaan tahan geser. Tanpa model: pembaca tiruan."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rantai  # noqa: E402
import tahan_geser as tg  # noqa: E402


def gambar_x():
    """Gambar 100 x 200 yang nilai pikselnya = koordinat x, supaya letak potongan bisa dibaca dari isinya."""
    return np.tile(np.arange(200, dtype=np.uint8)[None, :, None], (100, 1, 3))


def test_potong_geser_v0_sama_dengan_rantai_potong():
    g = gambar_x()

    for kotak in ((10, 20, 50, 40), (190, 90, 210, 110), (12.4, 30.7, 88.2, 49.9)):
        a, b = tg.potong_geser(g, kotak, tg.MARGIN, 0.0, 0.0), rantai.potong(g, kotak)
        assert a.shape == b.shape and np.array_equal(a, b)
    assert tg.MARGIN == rantai.MARGIN and tg.potong_geser(g, (250, 0, 260, 10), tg.MARGIN, 0, 0) is None


def test_geser_memindahkan_jendela_sebesar_pecahan_kotak():
    g = gambar_x()

    dasar = tg.potong_geser(g, (100, 40, 150, 60), 0.0, 0.0, 0.0)
    kanan = tg.potong_geser(g, (100, 40, 150, 60), 0.0, 0.1, 0.0)  # 10% dari lebar 50 = 5 piksel
    turun = tg.potong_geser(g, (100, 40, 150, 60), 0.0, 0.0, 0.25)  # 25% dari tinggi 20 = 5 piksel

    assert dasar[0, 0, 0] == 100 and kanan[0, 0, 0] == 105 and kanan.shape == dasar.shape
    assert turun.shape == dasar.shape and turun[0, 0, 0] == 100
    gy = np.ascontiguousarray(gambar_x().transpose(1, 0, 2))  # 200 x 100, nilai = koordinat y
    assert tg.potong_geser(gy, (40, 100, 60, 150), 0.0, 0.0, 0.1)[0, 0, 0] == 105  # 10% dari tinggi 50 = 5 piksel


def test_jumlah_potongan_per_varian_dan_varian_tak_dikenal_ditolak():
    g = gambar_x()

    assert [len(tg.potongan_varian(g, (60, 30, 140, 60), v)) for v in ("v0", "v1", "v2")] == [1, 3, 7]
    assert tg.VARIAN["v0"] == [(tg.MARGIN, 0.0, 0.0)] and tg.VARIAN["v1"][0] == tg.VARIAN["v0"][0]
    with pytest.raises(ValueError, match="varian"):
        tg.potongan_varian(g, (60, 30, 140, 60), "v9")


def test_pungut_suara_terbanyak_dari_bacaan_sesuai_pola():
    teks, yakin = tg.pungut_suara([("B1234XY", 0.9), ("b 1234 xy", 0.8), ("B1284XY", 0.95)])

    assert teks == "B1234XY" and yakin == pytest.approx((0.9 + 0.8) / 2 * 2 / 3)


def test_pungut_suara_mengabaikan_bacaan_di_luar_pola_dan_memecah_seri():
    assert tg.pungut_suara([("XXXX", 0.99), ("B1XY", 0.5)]) == ("B1XY", pytest.approx(0.25))
    assert tg.pungut_suara([("B1XY", 0.5), ("B2XY", 0.9)])[0] == "B2XY"  # seri: jumlah yakin
    assert tg.pungut_suara([("B1XY", 0.7), ("B2XY", 0.7)])[0] == "B1XY"  # masih seri: urutan varian


def test_pungut_suara_tanpa_bacaan_sesuai_pola_memakai_potongan_pertama():
    assert tg.pungut_suara([("AB0", 0.3), ("ABC", 0.6)]) == ("AB0", 0.3)


def test_baca_tahan_geser_memulihkan_bacaan_yang_salah_di_potongan_pertama():
    g = gambar_x()
    dibaca = []

    def baca(potongan):
        """Tiruan pembaca yang peka geser: potongan pertama (margin 0,05, tanpa geser) dibaca salah."""
        dibaca.append(potongan.shape)
        return ("B1284XY", 0.9) if len(dibaca) == 1 else ("B1234XY", 0.7)

    teks, yakin, potongan = tg.baca_tahan_geser(g, (60, 30, 140, 60), baca, "v2")
    lama = tg.baca_tahan_geser(g, (60, 30, 140, 60), lambda p: ("B1284XY", 0.9), "v0")

    assert teks == "B1234XY" and len(dibaca) == 7 and yakin == pytest.approx(0.7 * 6 / 7)
    assert np.array_equal(potongan, rantai.potong(g, (60, 30, 140, 60)))  # potongan yang disimpan tetap potongan biasa
    assert lama[:2] == ("B1284XY", 0.9)
