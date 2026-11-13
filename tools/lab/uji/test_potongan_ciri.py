"""Uji tools/lab/potongan_ciri.py (Rencana 33): potongan kendaraan beserta label jenis dan warna, dari label owner (ciri.json) dan
dataset Roboflow. Kotak yang owner tandai tidak pas dibuang, "tak yakin" tidak menjadi label, warna dari nama kelas Roboflow
("Biru-Putih" dibuang karena dua warna), kotak terlalu kecil dilewati, dan nama berkas asli tidak muncul."""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import potongan_ciri as pc  # noqa: E402

LEBAR, TINGGI = 400, 300
KOTAK = [100, 100, 220, 220]


def gambar_capture(tmp_path):
    folder = tmp_path / "capture" / "capture cctv mobil"
    folder.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(folder / "B1234XY.png"), np.full((TINGGI, LEBAR, 3), 120, np.uint8))
    (tmp_path / "peta.json").write_text(json.dumps({"g0001": "capture cctv mobil/B1234XY.png"}))


def kartu(nomor, **ubah):
    isi = {"id": f"k{nomor}", "gambar": "g0001", "sisi": "latih", "kelompok": "mobil", "kotak": KOTAK, "perkiraan": False,
           "plat": [nomor], "usulan_jenis": "mobil", "jenis": "mobil", "warna": "putih", "merek": "Toyota",
           "kotak_tidak_pas": False, "lengkap": True}
    return {**isi, **ubah}


def owner(tmp_path, kartu_kartu):
    gambar_capture(tmp_path)
    (tmp_path / "ciri.json").write_text(json.dumps({"kelas": {}, "kendaraan": kartu_kartu}))
    return {"ciri_json": str(tmp_path / "ciri.json"), "peta": str(tmp_path / "peta.json"), "capture": str(tmp_path / "capture")}


def dataset_roboflow(akar, nama_kelas, isi):
    """isi: {sisi: {nama berkas: [(kelas, kotak piksel)]}}."""
    akar.mkdir(parents=True, exist_ok=True)
    (akar / "data.yaml").write_text(yaml.safe_dump({"names": nama_kelas, "nc": len(nama_kelas)}))
    for sisi, daftar in isi.items():
        (akar / sisi / "images").mkdir(parents=True, exist_ok=True)
        (akar / sisi / "labels").mkdir(parents=True, exist_ok=True)
        for nama, kotak in daftar.items():
            cv2.imwrite(str(akar / sisi / "images" / nama), np.full((TINGGI, LEBAR, 3), 90, np.uint8))
            baris = [f"{k} {(x1 + x2) / 2 / LEBAR} {(y1 + y2) / 2 / TINGGI} {(x2 - x1) / LEBAR} {(y2 - y1) / TINGGI}"
                     for k, (x1, y1, x2, y2) in kotak]
            (akar / sisi / "labels" / f"{Path(nama).stem}.txt").write_text("\n".join(baris) + "\n")


def baca_csv(keluar):
    with open(keluar / "ciri.csv", newline="") as f:
        return list(csv.DictReader(f))


def test_potongan_owner_membuang_kotak_tidak_pas_bukan_kendaraan_dan_belum_lengkap(tmp_path):
    kartu_kartu = [kartu(1), kartu(2, kotak_tidak_pas=True), kartu(3, jenis="bukan_kendaraan", warna=None, merek=None),
                   kartu(4, lengkap=False, warna=None)]

    r = pc.bangun(owner(tmp_path, kartu_kartu), [], tmp_path / "keluar", ["tangkapan-owner"])

    baris = baca_csv(tmp_path / "keluar")
    assert len(baris) == 1 and baris[0]["jenis"] == "mobil" and baris[0]["warna"] == "putih"
    assert r["owner"]["dibuang"] == {"kotak_tidak_pas": 1, "bukan_kendaraan": 1, "belum_lengkap": 1, "terlalu_kecil": 0,
                                     "tak_terbaca": 0}
    assert (tmp_path / "keluar" / baris[0]["berkas"]).exists()


def test_tak_yakin_tidak_menjadi_label_tetapi_ciri_lain_tetap_dipakai(tmp_path):
    r = pc.bangun(owner(tmp_path, [kartu(1, warna="tak_yakin"), kartu(2, merek="tak_yakin")]), [], tmp_path / "keluar", ["x"])

    baris = baca_csv(tmp_path / "keluar")
    assert sorted(b["warna"] for b in baris) == ["", "putih"]
    assert sorted(b["merek"] for b in baris) == ["", "Toyota"]
    assert all(b["jenis"] == "mobil" for b in baris)  # tiap ciri dinilai sendiri-sendiri
    assert r["owner"]["tak_yakin"] == {"jenis": 0, "warna": 1, "merek": 1}


def test_merek_owner_masuk_kolom_dan_hitungan(tmp_path):
    r = pc.bangun(owner(tmp_path, [kartu(1), kartu(2, merek="Daihatsu")]), [], tmp_path / "keluar", ["x"])

    assert sorted(b["merek"] for b in baca_csv(tmp_path / "keluar")) == ["Daihatsu", "Toyota"]
    assert r["owner"]["per_kelas"]["merek"] == {"Daihatsu": 1, "Toyota": 1}


def test_merek_dari_nama_kelas_dan_sisa_ke_lainnya(tmp_path):
    nama = ["agya", "honda", "audi"]
    dataset_roboflow(tmp_path / "brand", nama, {"train": {f"b{i}.jpg": [(i, KOTAK)] for i in range(3)}})
    sumber = [{"folder": str(tmp_path / "brand"), "awalan": "b", "jenis_tetap": "mobil",
               "merek_kelas": {"agya": "Toyota", "honda": "Honda"}, "merek_sisa": "lainnya",
               "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["dataset-roboflow-brand"])

    baris = baca_csv(tmp_path / "keluar")
    assert sorted(b["merek"] for b in baris) == ["Honda", "Toyota", "lainnya"]  # audi tidak di daftar kita -> lainnya
    assert all(b["jenis"] == "mobil" for b in baris)
    assert r["sumber"]["b"]["merek_tidak_dipetakan"] == 0
    assert r["sumber"]["b"]["per_kelas"]["merek"] == {"Honda": 1, "Toyota": 1, "lainnya": 1}


def test_tanpa_merek_sisa_kelas_tak_dikenal_dilewati_dan_dihitung(tmp_path):
    dataset_roboflow(tmp_path / "brand", ["agya", "audi"], {"train": {f"b{i}.jpg": [(i, KOTAK)] for i in range(2)}})
    sumber = [{"folder": str(tmp_path / "brand"), "awalan": "b", "merek_kelas": {"agya": "Toyota"}, "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["x"])

    assert [b["merek"] for b in baca_csv(tmp_path / "keluar")] == ["Toyota"]
    assert r["sumber"]["b"]["merek_tidak_dipetakan"] == 1


def test_merek_dari_kata_pertama_nama_kelas(tmp_path):
    nama = ["Honda_Beat_Hitam", "Yamaha_NMAX_Merah"]
    dataset_roboflow(tmp_path / "motor", nama, {"train": {f"m{i}.jpg": [(i, KOTAK)] for i in range(2)}})
    sumber = [{"folder": str(tmp_path / "motor"), "awalan": "m", "jenis_tetap": "motor", "warna_dari_nama": True,
               "merek_kata_pertama": True, "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["x"])

    baris = baca_csv(tmp_path / "keluar")
    assert sorted(b["merek"] for b in baris) == ["Honda", "Yamaha"]
    assert sorted(b["warna"] for b in baris) == ["hitam", "merah"]  # warna dan merek dari nama kelas yang sama
    assert r["sumber"]["m"]["per_kelas"]["merek"] == {"Honda": 1, "Yamaha": 1}


def test_sisi_owner_tetap_dan_kartu_uji_tidak_masuk_latih(tmp_path):
    kartu_kartu = [kartu(i) for i in range(1, 13)] + [kartu(99, sisi="uji")]

    r1 = pc.bangun(owner(tmp_path, kartu_kartu), [], tmp_path / "k1", ["x"])
    r2 = pc.bangun(owner(tmp_path, kartu_kartu), [], tmp_path / "k2", ["x"])

    sisi = {b["berkas"]: b["sisi"] for b in baca_csv(tmp_path / "k1")}
    assert sisi == {b["berkas"]: b["sisi"] for b in baca_csv(tmp_path / "k2")}  # pembagian tetap
    assert set(sisi.values()) == {"latih", "validasi", "uji"}
    assert sum(s == "uji" for s in sisi.values()) == 1
    assert r1["owner"]["per_sisi"]["uji"] == 1 and r1["owner"]["per_sisi"]["validasi"] >= 1


def test_warna_dari_nama_kelas_roboflow_dan_dua_warna_dibuang(tmp_path):
    nama = ["Honda_Beat_Hitam", "Honda_Beat_Silver", "Honda_Beat_Biru-Putih", "Yamaha_NMAX_Merah"]
    dataset_roboflow(tmp_path / "motor", nama, {"train": {f"m{i}.jpg": [(i, KOTAK)] for i in range(4)}})
    sumber = [{"folder": str(tmp_path / "motor"), "awalan": "m", "jenis_tetap": "motor", "warna_dari_nama": True,
               "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["dataset-roboflow-merk-warna-motor"])

    baris = baca_csv(tmp_path / "keluar")
    assert sorted(b["warna"] for b in baris) == ["abu_perak", "hitam", "merah"]  # Biru-Putih dibuang
    assert all(b["jenis"] == "motor" and b["sumber"] == "m" for b in baris)
    assert r["sumber"]["m"]["warna_tidak_dipetakan"] == 1
    assert r["sumber"]["m"]["per_kelas"]["warna"] == {"abu_perak": 1, "hitam": 1, "merah": 1}


def test_jenis_dari_nomor_kelas_roboflow_dan_kelas_lain_dilewati(tmp_path):
    nama = ["License_Plate", "cars", "motorcyle", "truck"]
    dataset_roboflow(tmp_path / "vlp", nama, {"train": {"a.jpg": [(0, KOTAK), (1, KOTAK), (2, KOTAK), (3, KOTAK)]}})
    sumber = [{"folder": str(tmp_path / "vlp"), "awalan": "v", "jenis_kelas": {"1": "mobil", "2": "motor", "3": "truk"},
               "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["dataset-roboflow-vehicle-license-plate"])

    baris = baca_csv(tmp_path / "keluar")
    assert sorted(b["jenis"] for b in baris) == ["mobil", "motor", "truk"]  # kelas plat dilewati
    assert all(b["warna"] == "" for b in baris)
    assert r["sumber"]["v"]["kelas_dilewati"] == 1


def test_kotak_terlalu_kecil_dilewati_dan_dihitung(tmp_path):
    kecil = [10, 10, 10 + pc.MIN_SISI - 1, 10 + pc.MIN_SISI - 1]
    dataset_roboflow(tmp_path / "vlp", ["cars"], {"train": {"a.jpg": [(0, KOTAK), (0, kecil)]}})
    sumber = [{"folder": str(tmp_path / "vlp"), "awalan": "v", "jenis_kelas": {"0": "mobil"}, "sisi": {"latih": ["train"]}}]

    r = pc.bangun(None, sumber, tmp_path / "keluar", ["x"])

    assert len(baca_csv(tmp_path / "keluar")) == 1 and r["sumber"]["v"]["terlalu_kecil"] == 1


def test_batas_per_kelas_deterministik(tmp_path):
    isi = {f"a{k}-{i}.jpg": [(k, KOTAK)] for k in range(2) for i in range(5)}
    dataset_roboflow(tmp_path / "vlp", ["cars", "truck"], {"train": isi})
    sumber = [{"folder": str(tmp_path / "vlp"), "awalan": "v", "jenis_kelas": {"0": "mobil", "1": "truk"},
               "sisi": {"latih": ["train"]}, "batas_per_kelas": {"latih": 2}}]

    r1 = pc.bangun(None, sumber, tmp_path / "k1", ["x"])
    pc.bangun(None, sumber, tmp_path / "k2", ["x"])

    assert r1["sumber"]["v"]["per_kelas"]["jenis"] == {"mobil": 2, "truk": 2} and r1["sumber"]["v"]["dibatasi"] == 6
    assert sorted(b["berkas"] for b in baca_csv(tmp_path / "k1")) == sorted(b["berkas"] for b in baca_csv(tmp_path / "k2"))


def test_nama_asli_tidak_muncul_dan_tanpa_bahan_ditolak(tmp_path):
    dataset_roboflow(tmp_path / "vlp", ["cars"], {"train": {"B9999ZZ_jpg.rf.abc.jpg": [(0, KOTAK)]}})
    sumber = [{"folder": str(tmp_path / "vlp"), "awalan": "v", "jenis_kelas": {"0": "mobil"}, "sisi": {"latih": ["train"]}}]

    with pytest.raises(ValueError, match="bahan"):
        pc.bangun(None, sumber, tmp_path / "keluar", [])
    pc.bangun(owner(tmp_path, [kartu(1)]), sumber, tmp_path / "keluar2", ["x"])

    keluar = tmp_path / "keluar2"
    isi = (keluar / "ciri.csv").read_text() + (keluar / "ringkasan.json").read_text()
    assert "B9999ZZ" not in isi and "B1234XY" not in isi and "rf.abc" not in isi
    assert all("B9999ZZ" not in p.name and "B1234XY" not in p.name for p in (keluar / "potongan").iterdir())


def test_cli_dari_susunan_sampai_berkas(tmp_path, capsys):
    dataset_roboflow(tmp_path / "vlp", ["cars"], {"train": {"a.jpg": [(0, KOTAK)]}})
    susunan = {"bahan": ["tangkapan-owner", "dataset-roboflow-vehicle-license-plate"], "owner": owner(tmp_path, [kartu(1)]),
               "sumber": [{"folder": str(tmp_path / "vlp"), "awalan": "v", "jenis_kelas": {"0": "mobil"},
                           "sisi": {"latih": ["train"]}}]}
    (tmp_path / "susunan.json").write_text(json.dumps(susunan))

    kode = pc.utama(["bangun", str(tmp_path / "susunan.json"), str(tmp_path / "keluar")])

    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    assert kode == 0 and r["bahan"] == susunan["bahan"] and len(baca_csv(tmp_path / "keluar")) == 2
    assert "B1234XY" not in capsys.readouterr().out
