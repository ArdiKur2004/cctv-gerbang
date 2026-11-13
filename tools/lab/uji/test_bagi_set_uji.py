"""Uji tools/lab/bagi_set_uji.py: tidak ada plat di dua sisi, pembagian tetap, dan ringkasan tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bagi_set_uji as bs  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "bagi_set_uji.py"


def gambar(jalur, terang=150):
    jalur.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.full((10, 30), terang, np.uint8)).save(jalur)
    return jalur


def cari(pembagian, teks):
    return next(a for s in ("latih", "uji") for a in pembagian[s] if a["teks"] == teks)


def jalankan(tmp_path):
    keluar = tmp_path / "keluar"
    assert bs.utama(tmp_path / "original", keluar) == 0
    return json.loads((keluar / "pembagian.json").read_text()), json.loads((keluar / "ringkasan.json").read_text())


def test_plat_yang_sama_di_latih_dan_uji_penerbit_masuk_satu_sisi(tmp_path):
    # Inilah kebocoran yang terukur 14 Okt: 500 plat ada di latih dan uji penerbit sekaligus.
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")
    gambar(tmp_path / "original/test/D 2345 AB_0002.png")

    pembagian, ringkasan = jalankan(tmp_path)

    semua = pembagian["latih"] + pembagian["uji"]
    assert [a["teks"] for a in semua] == ["D2345AB"]
    assert sorted(semua[0]["berkas"]) == ["test/D 2345 AB_0002.png", "train/D 2345 AB_0001.png"]
    assert ringkasan["plat_di_kedua_sisi"] == 0


def test_pembagian_tetap_bila_dijalankan_ulang(tmp_path):
    for n in range(1, 40):
        gambar(tmp_path / f"original/train/D {n} AB_0001.png")

    bs.utama(tmp_path / "original", tmp_path / "satu")
    bs.utama(tmp_path / "original", tmp_path / "dua")

    assert (tmp_path / "satu/pembagian.json").read_text() == (tmp_path / "dua/pembagian.json").read_text()


def test_sekitar_seperempat_plat_masuk_uji(tmp_path):
    for n in range(1, 401):
        gambar(tmp_path / f"original/train/D {n} AB_0001.png")

    _, ringkasan = jalankan(tmp_path)

    bagian = ringkasan["sisi"]["uji"]["kedatangan"] / 400
    assert 0.18 < bagian < 0.32, bagian


def test_nama_tak_sesuai_pola_dikecualikan_dan_dihitung(tmp_path):
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")
    gambar(tmp_path / "original/train/2345 AB_0002.png")

    pembagian, ringkasan = jalankan(tmp_path)

    assert ringkasan["dikecualikan_tak_sesuai_pola"] == 1
    assert len(pembagian["latih"] + pembagian["uji"]) == 1


def test_kelompok_dari_nomor_urut_dan_terang(tmp_path):
    gambar(tmp_path / "original/train/D 1500 X_0001.png", terang=200)
    gambar(tmp_path / "original/train/D 3000 X_0001.png", terang=20)

    pembagian, _ = jalankan(tmp_path)

    assert cari(pembagian, "D1500X")["kelompok"] == "mobil-terang"
    assert cari(pembagian, "D3000X")["kelompok"] == "motor-gelap"


def test_ringkasan_tanpa_teks_plat_dan_kelompok_kosong_tetap_ditulis(tmp_path):
    gambar(tmp_path / "original/train/D 1500 X_0001.png")
    gambar(tmp_path / "original/test/D 3000 X_0001.png")

    jalankan(tmp_path)

    teks = (tmp_path / "keluar/ringkasan.json").read_text()
    for larangan in ("D1500X", "D3000X", "1500", "3000", ".png"):
        assert larangan not in teks
    ringkasan = json.loads(teks)
    for s in ("latih", "uji"):
        assert set(ringkasan["sisi"][s]["per_kelompok"]) == set(bs.KELOMPOK)


def test_galat_membaca_tidak_membocorkan_nama_berkas(tmp_path, capsys):
    # Pesan galat bawaan Python memuat jalur berkas; pada INDO-ALPR jalur itu memuat nomor plat.
    rusak = tmp_path / "original/train/D 2345 AB_0001.png"
    rusak.parent.mkdir(parents=True)
    rusak.write_bytes(b"bukan gambar")

    kode = bs.utama(tmp_path / "original", tmp_path / "keluar")

    cetak = capsys.readouterr()
    assert kode == 1
    assert "GAGAL MEMBACA" in cetak.out
    assert "2345" not in cetak.out + cetak.err
    assert not (tmp_path / "keluar/pembagian.json").exists()


def test_baris_perintah_sampai_ke_berkas_tanpa_mencetak_plat(tmp_path):
    gambar(tmp_path / "original/train/D 2345 AB_0001.png")

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "original"), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/pembagian.json").exists() and (tmp_path / "keluar/ringkasan.json").exists()
    assert "plat di kedua sisi: 0" in hasil.stdout
    assert "2345" not in hasil.stdout
