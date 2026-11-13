"""Uji tools/lab/plat.py: pola nomor polisi Indonesia dan golongan kendaraan menurut nomor urut (Perpol 7/2021)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plat import Plat, golongan, kelompok_kendaraan, urai, urai_nama_indo_alpr  # noqa: E402


def test_plat_dengan_spasi_diurai():
    plat = urai("B 1234 XYZ")

    assert plat == Plat("B", 1234, "XYZ")
    assert plat.teks == "B1234XYZ"


def test_huruf_kecil_dan_seri_kosong_diterima():
    assert urai("ag 12 a") == Plat("AG", 12, "A")
    assert urai("D1") == Plat("D", 1, "")


@pytest.mark.parametrize("teks", ["1234 XYZ", "ABC 12 X", "B 12345 X", "B 0123 X", "B 1234 WXYZ", ""])
def test_bentuk_di_luar_pola_ditolak(teks):
    assert urai(teks) is None


def test_nama_berkas_indo_alpr_diurai():
    assert urai_nama_indo_alpr("B 1234 XYZ_0001.png") == Plat("B", 1234, "XYZ")
    # Empat nama berkas di dataset memuat spasi di dalam seri huruf; dibaca sebagai satu seri.
    assert urai_nama_indo_alpr("D 2345 A B_0007.jpg") == Plat("D", 2345, "AB")


def test_nama_berkas_tanpa_kode_wilayah_atau_tanpa_urutan_ditolak():
    assert urai_nama_indo_alpr("1234 XYZ_12.png") is None
    assert urai_nama_indo_alpr("tanpa-garis-bawah.png") is None


@pytest.mark.parametrize("nomor, nama", [(1999, "mobil"), (2000, "motor"), (6999, "motor"), (7000, "bus"),
                                         (8000, "barang"), (9000, "khusus")])
def test_golongan_di_luar_polda_metro_jaya(nomor, nama):
    assert golongan(Plat("D", nomor, "AB")) == nama


@pytest.mark.parametrize("nomor, nama", [(2999, "mobil"), (3000, "motor"), (8500, "mobil"), (9000, "barang-khusus")])
def test_golongan_di_polda_metro_jaya(nomor, nama):
    assert golongan(Plat("B", nomor, "AB")) == nama


def test_kelompok_kendaraan_hanya_mobil_atau_motor():
    assert kelompok_kendaraan(Plat("D", 2000, "AB")) == "motor"
    assert kelompok_kendaraan(Plat("B", 2500, "AB")) == "mobil"
    assert kelompok_kendaraan(Plat("D", 7500, "AB")) == "mobil"  # bus dihitung kelompok mobil (K9: mobil dan motor)
