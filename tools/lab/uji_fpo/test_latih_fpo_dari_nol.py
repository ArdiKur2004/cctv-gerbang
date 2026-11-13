"""Uji latih_fpo.latih_dari_nol dengan Keras sungguhan di image lab tambahan (Rencana 24 Task 6, di luar gerbang biasa, GPU bila
ada): pembaca jualan dilatih tanpa berkas rilis fast-plate-ocr apa pun (arsitektur dari kode MIT, konfigurasi plat sendiri),
manifesnya bertujuan jualan, pembacanya memuat, dan tahap kedua (P3) melanjutkan bobot mesin sendiri dengan bahan yang ikut
tercatat. Bahannya 64 plat buatan (teks acak, bukan data pribadi).

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_latih_fpo_dari_nol.py -q -s -p no:cacheprovider
"""
import csv
import json
import sys
from pathlib import Path

import cv2

AKAR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import latih_fpo as lf  # noqa: E402
import plat_buatan as pb  # noqa: E402


def bahan(tmp_path, nama, sumber):
    folder = tmp_path / nama
    folder.mkdir()
    with open(sumber / "label.csv", newline="") as f:
        baris = [[f"../buatan/gambar/{b['berkas']}", b["teks"]] for b in csv.DictReader(f)]
    for berkas, isi in (("latih.csv", baris[:48]), ("validasi.csv", baris[48:])):
        with open(folder / berkas, "w", newline="") as f:
            tulis = csv.writer(f)
            tulis.writerow(["image_path", "plate_text"])
            tulis.writerows(isi)
    (folder / "siapkan.json").write_text(json.dumps({"sumber": {}, "gambar": {"latih": 48, "validasi": 16},
                                                     "bahan": ["plat-buatan"]}))
    return folder


def test_latih_dari_nol_tanpa_berkas_rilis_lalu_tahap_kedua(tmp_path, monkeypatch):
    def dilarang(*_):
        raise AssertionError("berkas rilis fast-plate-ocr tidak boleh dibaca saat melatih dari nol")

    monkeypatch.setattr(lf, "jalur_terkunci", dilarang)
    pb.buat(64, tmp_path / "buatan")

    satu = lf.latih_dari_nol(bahan(tmp_path, "tahap1", tmp_path / "buatan"), zaman=1, ukuran_angkatan=16, nama="uji-tahap1")

    assert (satu["tujuan"], satu["bahan"], satu["sha256_bobot_awal"]) == ("jualan", ["plat-buatan"], None)
    teks = lf.PembacaMesinJualan(tmp_path / "tahap1")(cv2.imread(str(tmp_path / "buatan" / "gambar" / "000000.png")))
    assert isinstance(teks, str)

    dua = lf.latih_dari_nol(bahan(tmp_path, "tahap2", tmp_path / "buatan"), zaman=1, ukuran_angkatan=16, nama="uji-tahap2",
                            bobot_awal=tmp_path / "tahap1")

    assert dua["bobot_awal"] == "uji-tahap1" and dua["sha256_bobot_awal"] == satu["sha256_mesin"]
    assert dua["latihan"]["zaman_berjalan"] == 1


def test_zaman_terbaik_dari_dari_nol_dipilih_dengan_ketepatan_per_huruf(tmp_path):
    # Dari nol, ketepatan plat utuh di validasi bisa 0 selama puluhan zaman (P1 jalan pertama: 0 sampai zaman 47), sehingga
    # checkpoint dengan val_acc tertahan di zaman 1. Mesin dari nol memilih zaman dengan val_char_acc.
    pb.buat(64, tmp_path / "buatan")

    meta = lf.latih_dari_nol(bahan(tmp_path, "pilih", tmp_path / "buatan"), zaman=3, ukuran_angkatan=16, nama="uji-pilih")

    (log,) = list((tmp_path / "pilih" / "latihan").rglob("training_log.csv"))
    with open(log, newline="") as f:
        nilai = [float(b["val_char_acc"]) for b in csv.DictReader(f)]
    assert meta["latihan"]["metrik_pilih"] == "val_char_acc"
    assert meta["latihan"]["zaman_terbaik"] == nilai.index(max(nilai)) + 1
