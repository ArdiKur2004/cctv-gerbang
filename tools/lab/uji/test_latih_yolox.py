"""Uji tools/lab/latih_yolox.py di gerbang biasa (CPU): target YOLOX, variasi acak, bobot awal hanya lewat weights_only (kode
pickle ditolak), dan rantai latih kecil dengan plat buatan sampai bobot safetensors dan mesin.json, dengan layar tanpa nama
berkas."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import latih_yolox as ly  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "latih_yolox.py"


def test_ke_target_piksel_masukan_dan_membuang_kotak_kecil():
    t = ly.ke_target([(10, 20, 50, 40), (0, 0, 2, 2)], 0.5)

    assert t.shape == (ly.MAKS_LABEL, 5)
    assert t[0].tolist() == [0.0, 15.0, 15.0, 20.0, 10.0] and not t[1].any()


def test_balik_horizontal():
    gambar = np.zeros((10, 20, 3), np.uint8)
    gambar[:, :5] = 255

    hasil, kotak = ly.balik(gambar, [(1, 2, 5, 6)])

    assert (hasil[:, 15:] == 255).all() and kotak == [(15.0, 2.0, 19.0, 6.0)]


def test_ubah_acak_tetap_dengan_benih_dan_kotak_di_dalam_gambar():
    gambar = np.full((100, 200, 3), 128, np.uint8)
    kotak = [(80, 40, 120, 60)]
    a = ly.ubah_acak(gambar, kotak, np.random.default_rng(1))
    b = ly.ubah_acak(gambar, kotak, np.random.default_rng(1))

    assert np.array_equal(a[0], b[0]) and a[1] == b[1]
    for benih in range(20):
        hasil, k = ly.ubah_acak(gambar, kotak, np.random.default_rng(benih))
        assert hasil.shape == gambar.shape and len(k) <= 1
        assert all(0 <= x1 <= x2 <= 200 and 0 <= y1 <= y2 <= 100 for x1, y1, x2, y2 in k)


def test_bobot_awal_lewat_weights_only_dan_kepala_lain_dilewati(tmp_path):
    sd = ly.buat_model("nano").state_dict()
    sd["head.cls_preds.0.weight"] = torch.zeros(80, *sd["head.cls_preds.0.weight"].shape[1:])  # kepala COCO 80 kelas
    torch.save({"model": sd}, tmp_path / "coco.pth")

    dimuat, dilewati = ly.muat_bobot_awal(ly.buat_model("nano"), tmp_path / "coco.pth")

    assert dilewati == 1 and dimuat == len(sd) - 1


class Jahat:
    def __reduce__(self):
        return (print, ("kode pickle dijalankan",))


def test_bobot_awal_berisi_kode_pickle_ditolak(tmp_path):
    torch.save({"model": {"x": Jahat()}}, tmp_path / "jahat.pth")

    with pytest.raises(ModelDitolak, match="pickle"):
        ly.muat_bobot_awal(ly.buat_model("nano"), tmp_path / "jahat.pth")


def test_selisih_mentah_dipisah_per_satuan():
    torch_ = np.zeros((3, 6))
    torch_[:, :4], torch_[:, 4:] = 600.0, 0.5
    onnx = torch_.copy()
    onnx[1, 2] += 0.04
    onnx[2, 5] += 0.002

    assert ly.selisih_mentah(torch_, onnx) == pytest.approx((0.04, 0.002), abs=1e-9)


def test_pemeriksaan_mentah_menimbang_koordinat_dalam_piksel_dan_peluang_tersendiri():
    # Nano-640 sungguhan (Rencana 13): koordinat beda 0,038 piksel masukan, peluang 1,0e-4. ONNX-nya sama dengan torch.
    assert ly.mentah_sama(0.038, 1.0e-4)
    assert not ly.mentah_sama(0.6, 0.0)
    # Peluang yang bergeser 5e-3 lolos dari batas campuran lama (1e-2), tetapi tidak boleh lolos.
    assert not ly.mentah_sama(0.0, 5e-3)


def buat_dataset(tmp_path):
    for sisi, n in (("train", 4), ("valid", 2), ("test", 2)):
        for sub in ("images", "labels"):
            (tmp_path / "ds" / sisi / sub).mkdir(parents=True)
        for i in range(n):
            g = np.full((96, 160, 3), 90, np.uint8)
            cv2.rectangle(g, (60, 40), (100, 56), (255, 255, 255), -1)
            cv2.imwrite(str(tmp_path / "ds" / sisi / "images" / f"B{1200 + i}AB_{sisi}.jpg"), g)
            (tmp_path / "ds" / sisi / "labels" / f"B{1200 + i}AB_{sisi}.txt").write_text("0 0.5 0.5 0.25 0.1666667\n")
    return tmp_path / "ds"


def kunci_sementara(tmp_path):
    folder = tmp_path / "unduhan" / ly.BUTIR_BOBOT["nano"]
    folder.mkdir(parents=True)
    torch.save({"model": ly.buat_model("nano").state_dict()}, folder / "yolox_nano.pth")
    kunci = tmp_path / "kunci.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": ly.BUTIR_BOBOT["nano"], "berkas": "yolox_nano.pth",
                                             "sha256": hashlib.sha256((folder / "yolox_nano.pth").read_bytes()).hexdigest()}]}))
    return tmp_path / "unduhan", kunci


def test_rantai_latih_kecil_sampai_safetensors_dan_layar_tanpa_nama_berkas(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(unduhan), str(tmp_path / "mesin"),
                            "--zaman", "1", "--perangkat", "cpu", "--kunci", str(kunci)], capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    assert "B120" not in layar
    meta = json.loads((tmp_path / "mesin" / "mesin.json").read_text())
    assert meta["sha256_bobot"] == hashlib.sha256((tmp_path / "mesin" / "mesin.safetensors").read_bytes()).hexdigest()
    assert meta["bahan"] == ["dataset-plat-lighting", "bobot-yolox"] and meta["bobot_awal"]["dilewati"] == 0
    assert ly.muat_mesin(tmp_path / "mesin").training is False


def test_rantai_latih_mencatat_bahan_dari_baris_perintah(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)
    bahan = "dataset-plat-lighting,bobot-yolox,video-riset-youtube,plat-buatan"

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(unduhan), str(tmp_path / "mesin"),
                            "--zaman", "1", "--perangkat", "cpu", "--kunci", str(kunci), "--bahan", bahan],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    assert json.loads((tmp_path / "mesin" / "mesin.json").read_text())["bahan"] == bahan.split(",")


def test_rantai_latih_dari_nol_tanpa_berkas_coco_dan_manifes_jualan(tmp_path):
    # Rencana 24 Task 10: folder unduhan dan kunci yang tidak ada membuktikan bobot COCO tidak dibaca sama sekali.
    ds = buat_dataset(tmp_path)
    (ds / "ringkasan.json").write_text(json.dumps({"bahan": ["dataset-plat-lighting", "tangkapan-owner"]}))

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(tmp_path / "tidak-ada"),
                            str(tmp_path / "mesin"), "--zaman", "1", "--perangkat", "cpu", "--kunci", str(tmp_path / "tidak-ada.json"),
                            "--dari-nol", "--nama", "pencari-jualan-uji"], capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    meta = json.loads((tmp_path / "mesin" / "mesin.json").read_text())
    assert (meta["nama"], meta["tujuan"], meta["bobot_awal"]) == ("pencari-jualan-uji", "jualan", None)
    assert meta["bahan"] == ["dataset-plat-lighting", "tangkapan-owner"]
    assert ly.muat_mesin(tmp_path / "mesin").training is False


def mesin_awal(tmp_path):
    """Mesin kecil dari nol (CPU, 1 zaman) sebagai mesin awal, dengan bahan seperti cctv1."""
    ds = buat_dataset(tmp_path)
    (ds / "ringkasan.json").write_text(json.dumps({"bahan": ["dataset-plat-lighting", "video-riset-youtube"]}))
    ly.latih("nano", 128, ds, tmp_path / "tidak-ada", tmp_path / "awal", zaman=1, perangkat="cpu",
             kunci=tmp_path / "tidak-ada.json", dari_nol=True, nama="pencari-awal")
    meta = json.loads((tmp_path / "awal" / "mesin.json").read_text())
    meta["bahan"] = ["dataset-plat-lighting", "bobot-yolox", "video-riset-youtube"]  # seperti cctv1: berangkat dari COCO
    (tmp_path / "awal" / "mesin.json").write_text(json.dumps(meta))
    (ds / "ringkasan.json").write_text(json.dumps({"bahan": ["dataset-plat-lighting", "tangkapan-owner", "plat-buatan"]}))
    return ds, tmp_path / "awal"


def test_model_dari_mesin_memuat_bobot_utuh_dan_menolak_yang_berubah(tmp_path):
    # Rencana 25 Task 4: melatih lanjut dari mesin sendiri (cctv1), bukan dari bobot COCO.
    from safetensors.torch import load_file

    _, awal = mesin_awal(tmp_path)

    model, info = ly.model_dari_mesin("nano", awal)

    asli = load_file(str(awal / "mesin.safetensors"))
    assert set(asli) == set(model.state_dict()) and all(torch.equal(asli[k], v) for k, v in model.state_dict().items())
    assert info == {"mesin": "pencari-awal", "folder": "awal",
                    "sha256": hashlib.sha256((awal / "mesin.safetensors").read_bytes()).hexdigest()}
    with pytest.raises(ValueError, match="jenis"):
        ly.model_dari_mesin("tiny", awal)
    (awal / "mesin.safetensors").write_bytes((awal / "mesin.safetensors").read_bytes() + b"x")  # kontrol: mesin awal berubah
    with pytest.raises(ModelDitolak, match="SHA-256"):
        ly.model_dari_mesin("nano", awal)


def test_rantai_latih_dari_mesin_sendiri_tanpa_coco_dan_manifes_jualan(tmp_path):
    # Folder unduhan dan kunci yang tidak ada membuktikan bobot COCO tidak dibaca; bahan = bahan mesin awal + bahan dataset.
    ds, awal = mesin_awal(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(tmp_path / "tidak-ada"),
                            str(tmp_path / "lanjut"), "--zaman", "1", "--perangkat", "cpu", "--kunci",
                            str(tmp_path / "tidak-ada.json"), "--bobot-awal-mesin", str(awal), "--jualan", "--nama", "cctv2-uji"],
                           capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    meta = json.loads((tmp_path / "lanjut" / "mesin.json").read_text())
    assert (meta["nama"], meta["tujuan"]) == ("cctv2-uji", "jualan")
    assert meta["bahan"] == ["dataset-plat-lighting", "bobot-yolox", "video-riset-youtube", "tangkapan-owner", "plat-buatan"]
    assert meta["bobot_awal"]["mesin"] == "pencari-awal" and meta["bobot_awal"]["folder"] == "awal"
    assert "B120" not in layar and ly.muat_mesin(tmp_path / "lanjut").training is False


def test_latih_dari_mesin_sendiri_tujuan_belajar_bila_jualan_tidak_diminta_dan_bukan_dari_nol(tmp_path):
    ds, awal = mesin_awal(tmp_path)

    meta = ly.latih("nano", 128, ds, tmp_path / "tidak-ada", tmp_path / "lanjut", zaman=1, perangkat="cpu",
                    kunci=tmp_path / "tidak-ada.json", bobot_awal_mesin=awal)

    assert meta["tujuan"] == "belajar" and meta["bobot_awal"]["folder"] == "awal"
    with pytest.raises(ValueError, match="dari nol"):
        ly.latih("nano", 128, ds, tmp_path / "tidak-ada", tmp_path / "x", zaman=1, perangkat="cpu",
                 kunci=tmp_path / "tidak-ada.json", bobot_awal_mesin=awal, dari_nol=True)


def test_bobot_coco_selalu_tercatat_walau_bahan_baris_perintah_melupakannya(tmp_path):
    # Kontrol: tanpa --dari-nol bobot COCO dimuat, jadi "bobot-yolox" harus ada di manifes walau --bahan tidak menyebutnya.
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(unduhan), str(tmp_path / "mesin"),
                            "--zaman", "1", "--perangkat", "cpu", "--kunci", str(kunci), "--bahan", "dataset-plat-lighting"],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    meta = json.loads((tmp_path / "mesin" / "mesin.json").read_text())
    assert meta["bahan"] == ["dataset-plat-lighting", "bobot-yolox"] and meta["tujuan"] == "belajar"
