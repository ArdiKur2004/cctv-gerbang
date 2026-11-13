"""Uji tools/lab/kendaraan.py tanpa model (K39): hanya kelas kendaraan dari keluaran YOLOX COCO, plat diterima bila tengahnya di
dalam kendaraan, pencari menolak ONNX yang berubah, dan ekspor menolak bobot yang bukan COCO 80 kelas."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kendaraan as kd  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_latih_yolox import kunci_sementara  # noqa: E402


def keluaran(*baris):
    """Baris (cx, cy, w, h, objek, kelas_coco, peluang_kelas) -> larik (N, 85) seperti keluaran YOLOX COCO."""
    k = np.zeros((len(baris), 85), np.float32)
    for i, (cx, cy, w, h, objek, kelas, peluang) in enumerate(baris):
        k[i, :5] = cx, cy, w, h, objek
        k[i, 5 + kelas] = peluang
    return k


def test_urai_hanya_kelas_kendaraan_di_atas_ambang_dan_skala_dikembalikan():
    k = keluaran((100, 100, 40, 20, 0.9, 2, 0.9), (300, 100, 40, 80, 0.9, 0, 0.9), (200, 200, 40, 20, 0.9, 3, 0.2),
                 (400, 300, 60, 40, 0.8, 7, 0.9), (500, 300, 40, 40, 0.9, 1, 0.9))

    hasil = kd.urai(k, 0.5, 0.25)

    assert [(round(v[0]), round(v[1]), round(v[2]), round(v[3]), v[5]) for v in hasil] == [
        (160, 180, 240, 220, "mobil"), (740, 560, 860, 640, "truk")]


def test_kendaraan_pemuat_memakai_tengah_kotak_plat_dan_memilih_yang_terkecil():
    truk = (0, 0, 400, 300, 0.9, "truk")
    motor = (100, 100, 200, 250, 0.8, "motor")

    assert kd.kendaraan_pemuat((140, 200, 160, 210), [truk, motor]) == motor
    assert kd.kendaraan_pemuat((390, 290, 450, 320), [truk, motor]) is None  # sebagian di dalam, tengahnya di luar
    assert kd.kendaraan_pemuat((10, 10, 20, 20), []) is None


def test_saring_membuang_plat_di_luar_kendaraan_dan_menambah_jenis_dan_kotak_kendaraan():
    plat = [(140, 200, 160, 210, 0.9), (500, 500, 540, 512, 0.8)]

    terima, buang = kd.saring(plat, [(100, 100, 200, 250, 0.8, "motor")])

    # Rencana 21: kotak kendaraan ikut sebagai unsur ketujuh, untuk ciri letak plat di kendaraannya.
    assert terima == [(140, 200, 160, 210, 0.9, "motor", (100.0, 100.0, 200.0, 250.0))] and buang == 1


def test_pencari_kendaraan_menolak_onnx_yang_berubah(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"bukan onnx")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64, "ukuran": 640, "ambang": 0.25}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        kd.PencariKendaraan(tmp_path)


def mesin_satu_kelas(folder, isi=b"onnx-satu-kelas"):
    """Folder mesin seperti keluaran latih_yolox.ekspor: mesin-onnx.json tanpa "kelas" dan tanpa "ambang"."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "mesin.onnx").write_bytes(isi)
    (folder / "mesin-onnx.json").write_text(json.dumps({"nama": folder.name, "ukuran": 640,
                                                        "sha256_onnx": kd.sha256_berkas(folder / "mesin.onnx")}))


def test_tetapkan_menulis_kendaraan_json_yang_terikat_ke_onnx(tmp_path):
    # Rencana 32: pencari kendaraan jualan satu kelas dari latih_yolox. Ambangnya ditetapkan sesudah dipilih, dan diikat ke SHA-256
    # mesin.onnx supaya ambang untuk mesin lain tidak terpakai diam-diam.
    mesin_satu_kelas(tmp_path / "k")

    r = kd.tetapkan(tmp_path / "k", 0.4, "Rencana 32")

    isi = json.loads((tmp_path / "k" / "kendaraan.json").read_text())
    assert isi == r == {"ambang": 0.4, "jenis": "kendaraan", "sha256_onnx": kd.sha256_berkas(tmp_path / "k" / "mesin.onnx"),
                        "alasan": "Rencana 32"}


@pytest.mark.parametrize("cacat", ["coco", "ambang_nol", "ambang_satu"])
def test_tetapkan_menolak_mesin_coco_dan_ambang_di_luar_nol_satu(tmp_path, cacat):
    mesin_satu_kelas(tmp_path / "k")
    if cacat == "coco":
        meta = json.loads((tmp_path / "k" / "mesin-onnx.json").read_text())
        (tmp_path / "k" / "mesin-onnx.json").write_text(json.dumps({**meta, "kelas": {"2": "mobil"}, "ambang": 0.25}))

    with pytest.raises(ValueError):
        kd.tetapkan(tmp_path / "k", {"coco": 0.4, "ambang_nol": 0.0, "ambang_satu": 1.0}[cacat], "x")
    assert not (tmp_path / "k" / "kendaraan.json").exists()


def test_mesin_satu_kelas_tanpa_ambang_ditolak_sebelum_onnxruntime(tmp_path):
    mesin_satu_kelas(tmp_path / "k")  # isi bukan ONNX: bila onnxruntime sempat dimuat, galatnya bukan ModelDitolak

    with pytest.raises(ModelDitolak, match="ditetapkan"):
        kd.PencariKendaraan(tmp_path / "k")


def test_kendaraan_json_untuk_onnx_lain_ditolak(tmp_path):
    mesin_satu_kelas(tmp_path / "k")
    kd.tetapkan(tmp_path / "k", 0.4, "x")
    mesin_satu_kelas(tmp_path / "k", isi=b"onnx-lain")  # mesin dilatih ulang, kendaraan.json lama tertinggal

    with pytest.raises(ModelDitolak, match="kendaraan.json"):
        kd.PencariKendaraan(tmp_path / "k")


def test_cli_tetapkan_sampai_berkas(tmp_path):
    mesin_satu_kelas(tmp_path / "k")

    kode = kd.utama(["tetapkan", str(tmp_path / "k"), "--ambang", "0.25", "--alasan", "uji"])

    assert kode == 0 and json.loads((tmp_path / "k" / "kendaraan.json").read_text())["ambang"] == 0.25


def test_ekspor_menolak_bobot_yang_bukan_coco_80_kelas(tmp_path):
    unduhan, kunci = kunci_sementara(tmp_path)  # bobot YOLOX 1 kelas yang dikunci sebagai yolox-nano-coco

    with pytest.raises(ModelDitolak, match="tidak termuat"):
        kd.ekspor("nano", unduhan, tmp_path, tmp_path / "kendaraan", ambang=0.25, kunci=kunci)
    assert not (tmp_path / "kendaraan" / "mesin.onnx").exists()


def cari_relatif(gambar):
    """Pencari tiruan: satu kotak di bagian bawah tengah gambar MASUKAN, apa pun ukurannya, ditambah kotak lemah."""
    t, l = gambar.shape[:2]
    return [(0.4 * l, 0.7 * t, 0.6 * l, 0.8 * t, 0.9), (0.0, 0.0, 0.1 * l, 0.1 * t, 0.05)]


def test_cari_dalam_kendaraan_memetakan_kotak_potongan_ke_gambar_utuh():
    gambar = np.zeros((400, 600, 3), np.uint8)
    motor = (100.0, 100.0, 200.0, 300.0, 0.8, "motor")

    hasil = kd.cari_dalam_kendaraan(gambar, [motor], cari_relatif, 0.25, margin=0.1)

    # Potongan x 90..210, y 80..320 (diperlebar 10%): kotak di 0,4-0,6 lebar dan 0,7-0,8 tinggi potongan.
    assert [tuple(round(x) for x in k[:4]) + (k[5],) for k in hasil] == [(138, 248, 162, 272, "motor")]


def test_cari_dalam_kendaraan_melewati_kendaraan_pendek_dan_menyatukan_kotak_kembar():
    gambar = np.zeros((400, 600, 3), np.uint8)
    besar = (100.0, 100.0, 200.0, 300.0, 0.8, "mobil")
    hampir_sama = (101.0, 100.0, 201.0, 300.0, 0.7, "truk")
    pendek = (400.0, 100.0, 500.0, 120.0, 0.9, "mobil")  # tinggi 20 piksel < MIN_TINGGI

    hasil = kd.cari_dalam_kendaraan(gambar, [besar, hampir_sama, pendek], cari_relatif, 0.25, margin=0.0)

    # Dua kotak hampir sama (IoU 0,9) dengan yakin yang sama: satu disimpan, entah dari kendaraan yang mana.
    assert len(hasil) == 1 and hasil[0][5] in {"mobil", "truk"}


def test_cari_dalam_kendaraan_membuang_kotak_yang_tengahnya_di_luar_kendaraannya():
    gambar = np.zeros((400, 600, 3), np.uint8)

    def cari_tepi(potongan):
        t, l = potongan.shape[:2]
        return [(0.0, 0.0, 0.08 * l, 0.08 * t, 0.9)]  # di pojok margin, di luar kotak kendaraan

    assert kd.cari_dalam_kendaraan(gambar, [(100.0, 100.0, 200.0, 300.0, 0.8, "motor")], cari_tepi, 0.25, margin=0.2) == []


def test_cari_dalam_kendaraan_membawa_kotak_kendaraan():
    motor = (100.0, 100.0, 200.0, 300.0, 0.8, "motor")

    hasil = kd.cari_dalam_kendaraan(np.zeros((400, 600, 3), np.uint8), [motor], cari_relatif, 0.25, margin=0.1)

    assert hasil[0][6] == (100.0, 100.0, 200.0, 300.0)


def test_urut_terdekat_dari_tepi_bawah_terendah():
    # K45 (Rencana 25): kendaraan terdekat dari kamera = tepi bawah kotaknya paling rendah di gambar (y2 terbesar).
    jauh = (300.0, 20.0, 400.0, 90.0, 0.9, "mobil")
    dekat = (50.0, 150.0, 250.0, 390.0, 0.6, "mobil")
    tengah = (420.0, 60.0, 560.0, 200.0, 0.8, "motor")

    assert kd.urut_terdekat([jauh, dekat, tengah]) == [dekat, tengah, jauh]
    assert kd.urut_terdekat([]) == []


def test_maks_kendaraan_hanya_mencari_di_kendaraan_terdekat_yang_cukup_tinggi():
    gambar = np.zeros((400, 600, 3), np.uint8)
    dipanggil = []

    def cari(potongan):
        dipanggil.append(potongan.shape[:2])
        return cari_relatif(potongan)

    jauh = (300.0, 20.0, 400.0, 120.0, 0.9, "mobil")
    dekat = (50.0, 150.0, 250.0, 390.0, 0.6, "mobil")
    pendek = (420.0, 370.0, 560.0, 395.0, 0.9, "motor")  # tepi bawah terendah, tetapi tinggi 25 < MIN_TINGGI: tidak dihitung

    satu = kd.cari_dalam_kendaraan(gambar, [jauh, dekat, pendek], cari, 0.25, margin=0.0, maks_kendaraan=1)
    semua = kd.cari_dalam_kendaraan(gambar, [jauh, dekat, pendek], cari, 0.25, margin=0.0)

    assert [k[6] for k in satu] == [dekat[:4]]
    assert dipanggil[0] == (240, 200) and len(dipanggil) == 1 + 2  # satu potongan untuk maks 1, dua untuk tanpa batas
    assert {k[6] for k in semua} == {dekat[:4], jauh[:4]}


def test_cadangan_utuh_mencari_di_gambar_utuh_bila_tak_ada_kendaraan_cukup_tinggi():
    gambar = np.zeros((400, 600, 3), np.uint8)
    pendek = (420.0, 370.0, 560.0, 395.0, 0.9, "motor")

    tanpa = kd.cari_dalam_kendaraan(gambar, [pendek], cari_relatif, 0.25)
    cadangan = kd.cari_dalam_kendaraan(gambar, [pendek], cari_relatif, 0.25, cadangan_utuh=True)
    kosong = kd.cari_dalam_kendaraan(gambar, [], cari_relatif, 0.25, cadangan_utuh=True)

    # Kotak gambar utuh di atas ambang saja (kotak lemah 0,05 dibuang), tanpa jenis dan kotak kendaraan.
    assert tanpa == [] and cadangan == kosong
    assert [tuple(round(x, 3) for x in k) for k in cadangan] == [(240.0, 280.0, 360.0, 320.0, 0.9)]


def test_cadangan_utuh_tidak_dipakai_bila_ada_kendaraan_cukup_tinggi_walau_platnya_tak_ditemukan():
    gambar = np.zeros((400, 600, 3), np.uint8)

    def cari_utuh_saja(potongan):
        return cari_relatif(potongan) if potongan.shape[:2] == (400, 600) else []

    hasil = kd.cari_dalam_kendaraan(gambar, [(50.0, 150.0, 250.0, 390.0, 0.6, "mobil")], cari_utuh_saja, 0.25,
                                    cadangan_utuh=True)

    assert hasil == []
