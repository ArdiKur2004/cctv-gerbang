"""Uji latih_fpo.latih_lanjut dengan Keras sungguhan di image lab tambahan (Rencana 25 Task 6, di luar gerbang biasa, GPU bila ada):
fpo-indo-1 dilatih lanjut 1 zaman dengan bahan kecil berwilayah. Bobotnya harus termuat utuh lewat jalur perintah latih (dengan
kepala wilayah), validasi diukur per sumber sebelum dan sesudah, zaman dipilih dengan val_plate_acc, manifesnya bertujuan jualan
dengan bahan gabungan, dan pembaca memuat mesin barunya. Bahannya plat buatan (teks acak, bukan data pribadi); fpo-indo-1 hanya
dibaca.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo/test_latih_lanjut.py -q -s -p no:cacheprovider
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import pytest

AKAR = Path(__file__).resolve().parents[3]
KELUARAN = AKAR / "data" / "keluaran"
UNDUHAN = AKAR / "data" / "unduhan"
sys.path.insert(0, str(AKAR / "tools" / "lab"))
import latih_fpo as lf  # noqa: E402
import plat_buatan as pb  # noqa: E402

FPO = KELUARAN / "fpo-indo-1"
pytestmark = pytest.mark.skipif(not (FPO / "mesin.keras").exists(), reason="fpo-indo-1 belum ada (Rencana 10)")


def bahan(tmp_path):
    """48 plat buatan latih, 8 validasi "INDO-ALPR" dan 8 validasi "tangkapan" (berawalan potongan/), semuanya berwilayah."""
    pb.buat(64, tmp_path / "buatan")
    folder = tmp_path / "bahan"
    (folder / "potongan").mkdir(parents=True)
    with open(tmp_path / "buatan" / "label.csv", newline="") as f:
        semua = list(csv.DictReader(f))
    latih = [[f"../buatan/gambar/{b['berkas']}", b["teks"], lf.WILAYAH] for b in semua[:48]]
    validasi = [[f"../buatan/gambar/{b['berkas']}", b["teks"], lf.WILAYAH] for b in semua[48:56]]
    for b in semua[56:]:
        cv2.imwrite(str(folder / "potongan" / b["berkas"]), cv2.imread(str(tmp_path / "buatan" / "gambar" / b["berkas"])))
        validasi.append([f"potongan/{b['berkas']}", b["teks"], lf.WILAYAH])
    for nama, isi in (("latih.csv", latih), ("validasi.csv", validasi), ("validasi-indo.csv", validasi[:8])):
        with open(folder / nama, "w", newline="") as f:
            tulis = csv.writer(f)
            tulis.writerow(["image_path", "plate_text", "plate_region"])
            tulis.writerows(isi)
    (folder / "siapkan.json").write_text(json.dumps({"sumber": {}, "gambar": {"latih": 48, "validasi": 16}, "wilayah": True,
                                                     "bahan": ["plat-buatan"]}))
    return folder


def test_latih_lanjut_dari_fpo_indo_1_satu_zaman(tmp_path):
    folder = bahan(tmp_path)

    meta = lf.latih_lanjut(folder, UNDUHAN, FPO, zaman=1, ukuran_angkatan=16, nama="uji-lanjut", laju=1e-4)

    awal = json.loads((FPO / "mesin.json").read_text())
    assert (meta["nama"], meta["tujuan"], meta["bobot_awal"]) == ("uji-lanjut", "jualan", "fpo-indo-1")
    assert meta["sha256_bobot_awal"] == awal["sha256_mesin"] == lf.sha256_berkas(FPO / "mesin.keras")
    assert meta["bahan"] == ["plat-buatan", "dataset-indo-alpr", "bobot-fast-plate-ocr"]
    assert meta["latihan"]["bobot_termuat"] == "192/192" and meta["latihan"]["metrik_pilih"] == "val_plate_acc"
    # Rencana 30: --lr diterima perintah latih fast-plate-ocr yang asli, dan validasi-indo.csv diukur sebelum dan sesudah.
    assert meta["latihan"]["laju"] == 1e-4 and meta["validasi"]["indo_awal"]["gambar"] == meta["validasi"]["indo_akhir"]["gambar"] == 8
    for saat in ("awal", "akhir"):
        assert meta["validasi"][saat]["indo_alpr"]["gambar"] == 8 and meta["validasi"][saat]["tangkapan"]["gambar"] == 8
    teks = lf.PembacaMesinFpo(folder, UNDUHAN)(cv2.imread(str(tmp_path / "buatan" / "gambar" / "000000.png")))
    assert isinstance(teks, str)
