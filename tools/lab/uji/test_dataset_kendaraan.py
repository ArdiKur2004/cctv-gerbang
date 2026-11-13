"""Uji tools/lab/dataset_kendaraan.py (Rencana 32): dataset YOLO satu kelas "kendaraan" untuk pencari kendaraan jualan. Kelas yang
diminta ditulis 0, kelas lain (plat) dan poligon dibuang; label dilengkapi kotak guru (pencari COCO) yang yakin dan tidak menimpa label;
sumber tanpa label memakai kotak guru saja; batas per kelas deterministik; nama asli tidak muncul."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dataset_kendaraan as dk  # noqa: E402

LEBAR, TINGGI = 200, 100
MOBIL_LABEL = "1 0.5 0.5 0.2 0.2"  # kotak piksel (80, 40, 120, 60)
PLAT = "0 0.1 0.1 0.05 0.05"
POLIGON = "0 0.1 0.1 0.2 0.1 0.2 0.2"
GURU = [(82, 41, 121, 61, 0.9, "mobil"),   # menimpa label mobil (IoU tinggi): dilewati
        (150, 10, 190, 40, 0.8, "motor"),  # kendaraan tak berlabel: ditambah
        (5, 5, 20, 20, 0.3, "mobil")]      # yakin < 0,4: dilewati


def guru(gambar):
    return list(GURU)


def gambar(folder, nama, nilai=120):
    folder.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(folder / nama), np.full((TINGGI, LEBAR, 3), nilai, np.uint8))


def dataset(akar, isi):
    """isi: {sisi: {nama_berkas: [baris label]}}."""
    for sisi, daftar in isi.items():
        for nama, baris in daftar.items():
            gambar(akar / sisi / "images", nama)
            (akar / sisi / "labels").mkdir(parents=True, exist_ok=True)
            (akar / sisi / "labels" / f"{Path(nama).stem}.txt").write_text("\n".join(baris) + "\n")


def baca_label(folder):
    return {p.stem: [list(map(float, b.split())) for b in p.read_text().splitlines() if b.strip()]
            for p in sorted((folder / "labels").glob("*.txt"))}


def test_kelas_diminta_jadi_nol_plat_dan_poligon_dibuang_label_dilengkapi_guru(tmp_path):
    dataset(tmp_path / "vlp", {"train": {"B1234XY_jpg.rf.a.jpg": [MOBIL_LABEL, PLAT, POLIGON]}, "test": {"t.jpg": [MOBIL_LABEL]},
                               "valid": {"v.jpg": [MOBIL_LABEL]}})
    sumber = [{"folder": tmp_path / "vlp", "awalan": "v", "kelas": [1, 2, 3], "sisi": {"train": ["train", "test"], "valid": ["valid"]}}]

    r = dk.bangun(sumber, tmp_path / "keluar", guru, ["dataset-roboflow-vehicle-license-plate"])

    latih, valid = baca_label(tmp_path / "keluar" / "train"), baca_label(tmp_path / "keluar" / "valid")
    assert len(latih) == 2 and len(valid) == 1
    for baris in list(latih.values()) + list(valid.values()):
        assert [b[0] for b in baris] == [0, 0]  # label mobil + satu kotak guru (motor), semuanya kelas 0
        assert baris[0][1:] == pytest.approx([0.5, 0.5, 0.2, 0.2])
        assert baris[1][1:] == pytest.approx([170 / LEBAR, 25 / TINGGI, 40 / LEBAR, 30 / TINGGI])
    v = r["sumber"]["v"]
    assert v["train"] == {"gambar": 2, "kotak_label": 2, "kotak_guru": 2, "poligon_dilewati": 1, "kotak_kelas_lain": 1,
                          "dibatasi": 0, "tak_terbaca": 0}
    assert r["bahan"] == ["dataset-roboflow-vehicle-license-plate", "bobot-yolox"]  # guru (YOLOX COCO) ikut membentuk label
    assert r["guru"] == {"ambang": dk.AMBANG_GURU, "iou": dk.IOU_GURU} == {"ambang": 0.4, "iou": 0.5}


def test_nama_baru_dari_sidik_nama_asli_dan_berawalan_sumber(tmp_path):
    dataset(tmp_path / "vlp", {"train": {"B1234XY_jpg.rf.a.jpg": [MOBIL_LABEL]}})
    sumber = [{"folder": tmp_path / "vlp", "awalan": "v", "kelas": [1], "sisi": {"train": ["train"]}}]

    dk.bangun(sumber, tmp_path / "keluar", guru, ["x"])

    nama = [p.name for p in (tmp_path / "keluar").rglob("*") if p.is_file()]
    isi = " ".join(nama) + (tmp_path / "keluar" / "ringkasan.json").read_text()
    assert "B1234XY" not in isi and "rf.a" not in isi
    assert all(n.startswith("v-") for n in nama if n != "ringkasan.json")
    assert sorted(n.rsplit(".", 1)[1] for n in nama if n != "ringkasan.json") == ["jpg", "txt"]


def test_sumber_tanpa_label_memakai_kotak_guru_saja(tmp_path):
    gambar(tmp_path / "cctv" / "train" / "images", "youtube-x-000001.jpg")
    sumber = [{"folder": tmp_path / "cctv", "awalan": "c", "kelas": None, "sisi": {"train": ["train"]}}]

    r = dk.bangun(sumber, tmp_path / "keluar", guru, ["video-riset-youtube"])

    (baris,) = baca_label(tmp_path / "keluar" / "train").values()
    assert len(baris) == 2  # dua kotak guru yang yakin >= 0,4 (tanpa label, tidak ada yang ditimpa)
    assert r["sumber"]["c"]["train"]["kotak_guru"] == 2 and r["sumber"]["c"]["train"]["kotak_label"] == 0


def test_batas_per_kelas_deterministik_per_sisi_tujuan(tmp_path):
    isi = {nama: [f"{k} 0.5 0.5 0.2 0.2"] for k in range(3) for nama in (f"m{k}-{i}.jpg" for i in range(4))}
    dataset(tmp_path / "motor", {"train": isi})
    sumber = [{"folder": tmp_path / "motor", "awalan": "m", "kelas": [0, 1, 2], "sisi": {"train": ["train"]},
               "batas_per_kelas": {"train": 2}}]

    r1 = dk.bangun(sumber, tmp_path / "k1", guru, ["x"])
    r2 = dk.bangun(sumber, tmp_path / "k2", guru, ["x"])

    assert r1["sumber"]["m"]["train"]["gambar"] == 6 and r1["sumber"]["m"]["train"]["dibatasi"] == 6
    assert sorted(p.name for p in (tmp_path / "k1" / "train" / "images").iterdir()) == \
        sorted(p.name for p in (tmp_path / "k2" / "train" / "images").iterdir())


def test_tanpa_bahan_ditolak_dan_keluaran_yang_sudah_ada_tidak_ditimpa(tmp_path):
    dataset(tmp_path / "vlp", {"train": {"a.jpg": [MOBIL_LABEL]}})
    sumber = [{"folder": tmp_path / "vlp", "awalan": "v", "kelas": [1], "sisi": {"train": ["train"]}}]

    with pytest.raises(ValueError, match="bahan"):
        dk.bangun(sumber, tmp_path / "keluar", guru, [])
    dk.bangun(sumber, tmp_path / "keluar2", guru, ["x"])
    with pytest.raises(FileExistsError):
        dk.bangun(sumber, tmp_path / "keluar2", guru, ["x"])


def test_cli_dari_berkas_susunan_sampai_berkas(tmp_path, monkeypatch, capsys):
    dataset(tmp_path / "vlp", {"train": {"B1234XY.jpg": [MOBIL_LABEL]}, "valid": {"v.jpg": [MOBIL_LABEL]}})
    (tmp_path / "susunan.json").write_text(json.dumps({"bahan": ["dataset-roboflow-vehicle-license-plate"], "sumber": [
        {"folder": str(tmp_path / "vlp"), "awalan": "v", "kelas": [1], "sisi": {"train": ["train"], "valid": ["valid"]}}]}))

    class Palsu:
        def __init__(self, folder, utas=None):
            pass

        def __call__(self, g):
            return guru(g)

    monkeypatch.setattr(dk, "PencariKendaraan", Palsu)

    kode = dk.utama(["bangun", str(tmp_path / "susunan.json"), str(tmp_path / "keluar"), str(tmp_path / "guru")])

    layar = capsys.readouterr().out
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    assert kode == 0 and r["sumber"]["v"]["valid"]["gambar"] == 1 and "B1234XY" not in layar
