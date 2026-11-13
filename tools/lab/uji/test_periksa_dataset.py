"""Uji tools/lab/periksa_dataset.py (Rencana 28, K53): pemeriksa dataset YOLO dari luar (Roboflow) di lab tanpa jaringan. Keamanan: jenis
berkas dari isinya, tanda berkas program, berkas teks berbyte nol, data.yaml dibaca aman. Kebenaran: label rusak, kelas di luar daftar,
koordinat di luar 0-1, kotak berukuran nol, gambar tanpa label dan label tanpa gambar, gambar kembar di dalam dan antarsisi. Nama berkas
tidak pernah keluar. Lembar contoh per kelas untuk owner."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import periksa_dataset as pd  # noqa: E402


def gambar(nilai, ukuran=(120, 200)):
    rng = np.random.default_rng(nilai)
    g = rng.integers(0, 255, (*ukuran, 3), dtype=np.uint8)
    g[40:70, 60:140] = 255
    return g


def tulis(folder, sisi, nama, g, label):
    for sub in ("images", "labels"):
        (folder / sisi / sub).mkdir(parents=True, exist_ok=True)
    if g is not None:
        cv2.imwrite(str(folder / sisi / "images" / f"{nama}.jpg"), g)
    if label is not None:
        (folder / sisi / "labels" / f"{nama}.txt").write_text(label)


def dataset_sehat(tmp_path):
    d = tmp_path / "sehat"
    d.mkdir()
    (d / "data.yaml").write_text("names: ['TOYOTA', 'WULING']\nnc: 2\ntrain: ../train/images\nval: ../valid/images\n")
    (d / "README.dataset.txt").write_text("Dataset contoh\n")
    tulis(d, "train", "B1234XY rahasia", gambar(1), "0 0.5 0.45 0.4 0.25\n")
    tulis(d, "train", "b", gambar(2), "1 0.5 0.45 0.4 0.25\n0 0.2 0.2 0.1 0.1\n")
    tulis(d, "valid", "c", gambar(3), "1 0.5 0.45 0.4 0.25\n")
    return d


def test_dataset_sehat_dihitung_tanpa_masalah(tmp_path):
    r = pd.periksa(dataset_sehat(tmp_path))

    assert r["keamanan"] == {"berkas": 8, "jenis_tidak_cocok": 0, "tanda_program": 0, "teks_tidak_bersih": 0, "gambar_rusak": 0,
                             "yaml_aman": True, "akhiran": {".jpg": 3, ".txt": 4, ".yaml": 1}}
    assert r["kelas"] == ["TOYOTA", "WULING"]
    assert r["sisi"]["train"] == {"gambar": 2, "label": 2, "gambar_tanpa_label": 0, "label_tanpa_gambar": 0, "label_kosong": 0,
                                  "kotak": 3, "baris_rusak": 0, "kelas_di_luar_daftar": 0, "koordinat_di_luar": 0, "kotak_nol": 0}
    assert r["per_kelas"] == {"TOYOTA": {"kotak": 2, "gambar": 2}, "WULING": {"kotak": 2, "gambar": 2}}
    assert r["kembar"] == {"persis_dalam_sisi": 0, "persis_antar_sisi": 0, "mirip_antar_sisi": 0}
    assert r["ukuran_gambar"] == {"lebar": [200, 200, 200], "tinggi": [120, 120, 120]}  # min, median, maks


def test_berkas_menyamar_dan_berkas_teks_kotor_tertangkap(tmp_path):
    d = dataset_sehat(tmp_path)
    (d / "train" / "images" / "jahat.jpg").write_bytes(b"MZ\x90\x00" + b"\x00" * 60)  # program Windows berakhiran .jpg
    (d / "train" / "labels" / "jahat.txt").write_text("0 0.5 0.5 0.1 0.1\n")
    (d / "README.roboflow.txt").write_bytes(b"isi\x00tersembunyi")
    (d / "skrip.txt").write_text("#!/bin/sh\necho hai\n")

    k = pd.periksa(d)["keamanan"]

    assert (k["jenis_tidak_cocok"], k["tanda_program"], k["teks_tidak_bersih"], k["gambar_rusak"]) == (1, 2, 1, 1)


def test_yaml_bertag_python_tidak_dijalankan_dan_ditandai(tmp_path):
    d = dataset_sehat(tmp_path)
    jejak = tmp_path / "dijalankan"
    (d / "data.yaml").write_text(f"names: !!python/object/apply:os.system ['touch {jejak}']\nnc: 2\n")

    r = pd.periksa(d)

    assert r["keamanan"]["yaml_aman"] is False and r["kelas"] is None and not jejak.exists()


def test_label_rusak_dan_pasangan_hilang_dihitung(tmp_path):
    d = dataset_sehat(tmp_path)
    tulis(d, "train", "rusak", gambar(4), "0 0.5 0.5\n5 0.5 0.5 0.1 0.1\n0 1.5 0.5 0.1 0.1\n0 0.5 0.5 0 0.1\n\n")
    tulis(d, "train", "tanpa-label", gambar(5), None)
    tulis(d, "train", "yatim", None, "0 0.5 0.5 0.1 0.1\n")
    tulis(d, "train", "kosong", gambar(6), "")

    s = pd.periksa(d)["sisi"]["train"]

    assert (s["baris_rusak"], s["kelas_di_luar_daftar"], s["koordinat_di_luar"], s["kotak_nol"]) == (1, 1, 1, 1)
    # Gambar latih: 2 dari dataset sehat + rusak, tanpa-label, kosong; "yatim" hanya label.
    assert (s["gambar"], s["gambar_tanpa_label"], s["label_tanpa_gambar"], s["label_kosong"]) == (5, 1, 1, 1)
    assert s["kotak"] == 3  # hanya baris yang sah yang dihitung sebagai kotak (3 dari dataset sehat, 0 dari berkas rusak)


def test_gambar_kembar_dalam_dan_antar_sisi(tmp_path):
    d = dataset_sehat(tmp_path)
    g = cv2.imread(str(d / "train" / "images" / "b.jpg"))
    tulis(d, "valid", "salinan-b", None, "1 0.5 0.45 0.4 0.25\n")
    (d / "valid" / "images" / "salinan-b.jpg").write_bytes((d / "train" / "images" / "b.jpg").read_bytes())  # kembar persis lintas sisi
    tulis(d, "train", "b-lagi", None, "1 0.5 0.45 0.4 0.25\n")
    (d / "train" / "images" / "b-lagi.jpg").write_bytes((d / "train" / "images" / "b.jpg").read_bytes())  # kembar persis dalam sisi
    tulis(d, "valid", "b-mirip", None, "1 0.5 0.45 0.4 0.25\n")
    cv2.imwrite(str(d / "valid" / "images" / "b-mirip.jpg"), g, [cv2.IMWRITE_JPEG_QUALITY, 60])  # disimpan ulang: mirip, bukan persis

    k = pd.periksa(d)["kembar"]

    assert k["persis_dalam_sisi"] == 1 and k["persis_antar_sisi"] == 1 and k["mirip_antar_sisi"] >= 1


def test_nama_berkas_tidak_muncul_di_keluaran_cli(tmp_path):
    d = dataset_sehat(tmp_path)

    kode = pd.utama(["periksa", str(d), str(tmp_path / "ringkasan.json")])

    isi = (tmp_path / "ringkasan.json").read_text()
    assert kode == 0 and "rahasia" not in isi and "B1234XY" not in isi and json.loads(isi)["kelas"] == ["TOYOTA", "WULING"]


def dataset_klasifikasi(tmp_path):
    """Susunan "Folder Structure" Roboflow: <sisi>/<kelas>/<gambar>, tanpa label dan tanpa data.yaml."""
    d = tmp_path / "klasifikasi"
    for sisi, kelas, nama, nilai in (("train", "avanza", "a", 1), ("train", "avanza", "a2", 2), ("train", "innova", "b", 3),
                                     ("valid", "innova", "c", 4)):
        (d / sisi / kelas).mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / sisi / kelas / f"{nama}.jpg"), gambar(nilai))
    (d / "valid" / "avanza").mkdir()
    (d / "valid" / "avanza" / "a-salin.jpg").write_bytes((d / "train" / "avanza" / "a.jpg").read_bytes())  # kembar lintas sisi
    (d / "README.dataset.txt").write_text("contoh\n")
    return d


def test_dataset_klasifikasi_folder_per_kelas(tmp_path):
    # Rencana 28: car-type-final-1 adalah dataset klasifikasi (Folder Structure), bukan deteksi.
    r = pd.periksa(dataset_klasifikasi(tmp_path))

    assert r["jenis_tugas"] == "klasifikasi" and r["kelas"] == ["avanza", "innova"]
    assert r["sisi"] == {"train": {"gambar": 3, "gambar_tanpa_kelas": 0}, "valid": {"gambar": 2, "gambar_tanpa_kelas": 0}}
    assert r["per_kelas"] == {"avanza": {"gambar": 3}, "innova": {"gambar": 2}}
    assert r["kembar"]["persis_antar_sisi"] == 1 and r["keamanan"]["gambar_rusak"] == 0


def test_jenis_tugas_deteksi_untuk_susunan_yolo(tmp_path):
    assert pd.periksa(dataset_sehat(tmp_path))["jenis_tugas"] == "deteksi"


def test_lembar_klasifikasi_gambar_utuh_per_kelas(tmp_path):
    d = dataset_klasifikasi(tmp_path)

    r = pd.buat_lembar(d, tmp_path / "lembar", per_kelas=2)

    isi = json.loads((tmp_path / "lembar" / "lembar.json").read_text())
    assert r == {"baris": 4, "kelas": 2, "halaman": 1}
    assert sorted(b["kelas"] for b in isi["baris"]) == ["avanza", "avanza", "innova", "innova"]
    assert all(b["kotak"] is None for b in isi["baris"])  # klasifikasi: gambar utuh, tanpa kotak


def test_lembar_paling_banyak_tiga_per_kelas_untuk_owner(tmp_path):
    d = dataset_sehat(tmp_path)
    for i in range(5):
        tulis(d, "train", f"t{i}", gambar(10 + i), "0 0.5 0.45 0.4 0.25\n")

    r = pd.buat_lembar(d, tmp_path / "lembar", per_kelas=3)

    isi = json.loads((tmp_path / "lembar" / "lembar.json").read_text())
    per = {}
    for b in isi["baris"]:
        per[b["kelas"]] = per.get(b["kelas"], 0) + 1
    assert per == {"TOYOTA": 3, "WULING": 2} and [b["nomor"] for b in isi["baris"]] == list(range(1, 6))
    assert r == {"baris": 5, "kelas": 2, "halaman": 1} and all((tmp_path / "lembar" / h).exists() for h in isi["halaman"])
