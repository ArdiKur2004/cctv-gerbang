"""Uji tools/lab/ciri.py (Rencana 33): aturan warna tanpa latihan, saringan inframerah (K52), variasi latihan yang tidak mengubah
warna, hitungan benar/salah/tak yakin per ambang, jenis dari pencari COCO, dan pengenal CNN yang menolak bobot yang berubah."""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ciri as cr  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402

WARNA_BGR = {"merah": (30, 30, 200), "kuning": (30, 210, 220), "hijau": (40, 160, 40), "biru": (190, 60, 30),
             "putih": (235, 235, 235), "hitam": (25, 25, 25), "abu_perak": (140, 140, 140)}


def tampalan(bgr, sisi=120):
    return np.full((sisi, sisi, 3), bgr, np.uint8)


@pytest.mark.parametrize("warna", sorted(WARNA_BGR))
def test_aturan_warna_mengenali_tampalan_warna_dasar(warna):
    assert cr.warna_aturan(tampalan(WARNA_BGR[warna])) == warna


def test_aturan_warna_memakai_bagian_tengah_bukan_tepi():
    # Kendaraan ada di tengah potongan; tepi sering latar (jalan, tanaman).
    g = tampalan(WARNA_BGR["hijau"], 120)
    g[40:80, 40:80] = WARNA_BGR["merah"]

    assert cr.warna_aturan(g) == "merah"


def test_nyaris_tanpa_warna_hanya_untuk_gambar_kelabu():
    kelabu = np.repeat(np.random.default_rng(0).integers(0, 255, (80, 80, 1), dtype=np.uint8), 3, axis=2)

    assert cr.nyaris_tanpa_warna(kelabu) is True
    assert cr.nyaris_tanpa_warna(tampalan(WARNA_BGR["merah"])) is False
    assert cr.nyaris_tanpa_warna(tampalan(WARNA_BGR["hitam"])) is True  # hitam memang tanpa warna: itu sebabnya dipakai gambar penuh


def test_saringan_inframerah_memakai_gambar_penuh(tmp_path):
    kelabu = np.repeat(np.random.default_rng(1).integers(0, 255, (80, 80, 1), dtype=np.uint8), 3, axis=2)

    assert cr.saring_inframerah("hitam", kelabu) == cr.TAK_YAKIN
    assert cr.saring_inframerah("hitam", tampalan(WARNA_BGR["hijau"])) == "hitam"
    assert cr.saring_inframerah("hitam", None) == "hitam"  # tanpa gambar penuh, saringan tidak berlaku


@pytest.mark.parametrize("warna", ["merah", "hijau", "biru", "kuning"])
def test_variasi_latihan_tidak_mengubah_warna(warna):
    rng = np.random.default_rng(3)
    g = tampalan(WARNA_BGR[warna])

    hasil = {cr.warna_aturan(cr.ubah_acak(g, rng)) for _ in range(20)}

    assert hasil == {warna}


def test_nilai_ambang_menghitung_benar_salah_dan_tak_yakin():
    ramalan = [("mobil", 0.9), ("motor", 0.4), ("mobil", 0.8), ("truk", 0.95)]
    benar = ["mobil", "mobil", "motor", "truk"]

    assert cr.nilai_ambang(ramalan, benar, 0.0) == {"benar": 2, "salah": 2, "tak_yakin": 0, "nilai": 0}
    assert cr.nilai_ambang(ramalan, benar, 0.5) == {"benar": 2, "salah": 1, "tak_yakin": 1, "nilai": 1}
    assert cr.nilai_ambang(ramalan, benar, 0.99) == {"benar": 0, "salah": 0, "tak_yakin": 4, "nilai": 0}


def test_jenis_coco_memakai_kotak_terbesar_dan_tak_yakin_bila_kosong():
    def cari(gambar):
        return [(0, 0, 10, 10, 0.95, "motor"), (0, 0, 80, 80, 0.6, "mobil")]

    assert cr.jenis_coco(tampalan(WARNA_BGR["biru"]), cari) == ("mobil", 0.6)
    assert cr.jenis_coco(tampalan(WARNA_BGR["biru"]), lambda g: []) == (cr.TAK_YAKIN, 0.0)


def dataset_potongan(tmp_path, kelas=("mobil", "motor"), per_kelas=8):
    """ciri.csv kecil: tiap kelas satu warna tetap, supaya CNN bisa belajar memisahkannya dalam beberapa zaman."""
    keluar = tmp_path / "potongan-ciri"
    (keluar / "potongan").mkdir(parents=True)
    baris = []
    rng = np.random.default_rng(5)
    bgr = {kelas[0]: WARNA_BGR["merah"], kelas[1]: WARNA_BGR["biru"]}
    for k in kelas:
        for i in range(per_kelas):
            for sisi, sumber in (("latih", "o"), ("latih", "v"), ("validasi", "o"), ("uji", "o")):
                nama = f"potongan/{sumber}-{sisi}-{k}-{i}.png"
                g = np.clip(tampalan(bgr[k], 60).astype(np.int16) + rng.integers(-15, 15), 0, 255).astype(np.uint8)
                cv2.imwrite(str(keluar / nama), g)
                baris.append({"berkas": nama, "sumber": sumber, "sisi": sisi, "jenis": k, "warna": ""})
    with open(keluar / "ciri.csv", "w", newline="") as f:
        t = csv.DictWriter(f, ["berkas", "sumber", "sisi", "jenis", "warna"])
        t.writeheader()
        t.writerows(baris)
    (keluar / "ringkasan.json").write_text(json.dumps({"bahan": ["tangkapan-owner"]}))
    return keluar


def test_latih_memilih_zaman_dari_validasi_owner_dan_mencatat_kelas(tmp_path):
    folder = dataset_potongan(tmp_path)

    meta = cr.latih(folder, "jenis", tmp_path / "mesin", zaman=2, perangkat="cpu", nama="uji-jenis")

    assert meta["nama"] == "uji-jenis" and meta["ciri"] == "jenis" and meta["kelas"] == ["mobil", "motor"]
    assert meta["bahan"] == ["tangkapan-owner"] and meta["tujuan"] == "jualan"
    assert 1 <= meta["zaman_terbaik"] <= 2 and len(meta["catatan"]) == 2
    assert meta["gambar"]["latih"] == 32 and meta["gambar"]["validasi_owner"] == 16  # validasi hanya dari sumber owner
    assert meta["validasi_owner"]["gambar"] == 16
    assert (tmp_path / "mesin" / "mesin.safetensors").exists()


def test_latih_hanya_memakai_sumber_yang_diminta(tmp_path):
    folder = dataset_potongan(tmp_path)

    meta = cr.latih(folder, "jenis", tmp_path / "mesin", zaman=1, perangkat="cpu", sumber=["o"])

    assert meta["gambar"]["latih"] == 16 and meta["sumber_latih"] == ["o"]


def test_latih_menolak_ciri_tanpa_label(tmp_path):
    folder = dataset_potongan(tmp_path)

    with pytest.raises(ValueError, match="warna"):
        cr.latih(folder, "warna", tmp_path / "mesin", zaman=1, perangkat="cpu")


def dataset_dua_jenis(tmp_path):
    """ciri.csv dengan dua jenis dan label merek: mobil selalu Toyota/Daihatsu, motor selalu Honda. Untuk menguji saringan jenis."""
    keluar = tmp_path / "potongan-jenis"
    (keluar / "potongan").mkdir(parents=True)
    rng = np.random.default_rng(7)
    baris = []
    isi = {("mobil", "Toyota"): WARNA_BGR["merah"], ("mobil", "Daihatsu"): WARNA_BGR["biru"],
           ("motor", "Honda"): WARNA_BGR["hijau"]}
    for (jenis, merek), bgr in isi.items():
        for sisi in ("latih", "validasi", "uji"):
            for i in range(6):
                nama = f"potongan/o-{jenis}-{merek}-{sisi}-{i}.png"
                g = np.clip(tampalan(bgr, 70).astype(np.int16) + rng.integers(-12, 12), 0, 255).astype(np.uint8)
                cv2.imwrite(str(keluar / nama), g)
                baris.append({"berkas": nama, "sumber": "o", "sisi": sisi, "jenis": jenis, "warna": "", "merek": merek})
    with open(keluar / "ciri.csv", "w", newline="") as f:
        t = csv.DictWriter(f, ["berkas", "sumber", "sisi", "jenis", "warna", "merek"])
        t.writeheader()
        t.writerows(baris)
    (keluar / "ringkasan.json").write_text(json.dumps({"bahan": ["tangkapan-owner"]}))
    return keluar


def test_siapkan_memakai_ukuran_yang_diminta():
    g = tampalan(WARNA_BGR["merah"], 300)

    assert cr.siapkan(g).shape == (cr.UKURAN, cr.UKURAN, 3)  # bawaan tidak berubah
    assert cr.siapkan(g, 64).shape == (64, 64, 3)
    assert cr.siapkan(g, 192).shape == (192, 192, 3)


def test_latih_mencatat_ukuran_yang_dipakai(tmp_path):
    # Rencana 35: ukuran masukan dicatat di mesin.json, supaya ekspor dan pemakaian tidak bisa memakai ukuran lain diam-diam.
    folder = dataset_potongan(tmp_path)

    bawaan = cr.latih(folder, "jenis", tmp_path / "m96", zaman=1, perangkat="cpu")
    besar = cr.latih(folder, "jenis", tmp_path / "m64", zaman=1, perangkat="cpu", ukuran=64)

    assert bawaan["ukuran"] == cr.UKURAN and besar["ukuran"] == 64


def test_latih_jenis_hanya_memakai_potongan_jenis_itu(tmp_path):
    folder = dataset_dua_jenis(tmp_path)

    semua = cr.latih(folder, "merek", tmp_path / "semua", zaman=1, perangkat="cpu")
    mobil = cr.latih(folder, "merek", tmp_path / "mobil", zaman=1, perangkat="cpu", jenis="mobil")

    assert semua["kelas"] == ["Daihatsu", "Honda", "Toyota"] and semua["gambar"]["latih"] == 18
    assert mobil["kelas"] == ["Daihatsu", "Toyota"] and mobil["gambar"]["latih"] == 12
    assert mobil["gambar"]["validasi_owner"] == 12 and mobil["jenis"] == "mobil"  # validasi ikut disaring


def test_latih_jenis_yang_tidak_ada_ditolak(tmp_path):
    folder = dataset_dua_jenis(tmp_path)

    with pytest.raises(ValueError, match="merek"):
        cr.latih(folder, "merek", tmp_path / "m", zaman=1, perangkat="cpu", jenis="bus")


# Bahwa `PengenalCiri` memakai ukuran dari mesin-onnx.json (bukan tetapan modul) dijaga uji RANTAI di
# uji_fpo/test_ciri_sungguhan.py, karena hanya di sana ada ONNX sungguhan untuk dibuktikan.


def test_pengenal_menolak_onnx_yang_berubah(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"bukan onnx")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64, "kelas": ["mobil"], "ukuran": cr.UKURAN}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        cr.PengenalCiri(tmp_path, ambang=0.5)
