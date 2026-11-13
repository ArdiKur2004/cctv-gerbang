"""Uji tools/lab/latih_yolox.py, pencari_yolox.py, dan kendaraan.py di image lab tambahan (di luar gerbang biasa; butuh onnx):
bobot COCO sungguhan dimuat aman, ekspor ONNX memberi deteksi yang sama dengan torch, juga lewat PencariYolox, dan pencari
kendaraan (K39) diekspor dari bobot COCO sungguhan.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji"):
    sys.path.insert(0, str(AKAR / folder))
import kendaraan as kd  # noqa: E402
import latih_yolox as ly  # noqa: E402
import pencari_yolox as pyx  # noqa: E402
from test_latih_yolox import buat_dataset, kunci_sementara  # noqa: E402


@pytest.mark.parametrize("jenis", ["nano", "tiny"])
def test_bobot_coco_sungguhan_dimuat_aman_dan_hanya_kepala_kelas_dilewati(jenis):
    butir = ly.BUTIR_BOBOT[jenis]
    berkas = UNDUHAN / butir / f"yolox_{jenis}.pth"
    if not berkas.exists():
        pytest.skip("bobot awal belum diunduh (Rencana 13 Task 1)")
    model = ly.buat_model(jenis)

    dimuat, dilewati = ly.muat_bobot_awal(model, berkas)

    # Kepala kelas COCO (80 kelas) di tiga tingkat: bobot dan bias = 6 tensor.
    assert dilewati == 6 and dimuat == len(model.state_dict()) - 6


def test_ekspor_onnx_sama_dengan_torch_dan_pencari_onnx_membaca_sama(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)
    ly.latih("nano", 128, ds, unduhan, tmp_path / "mesin", zaman=1, perangkat="cpu", kunci=kunci)

    meta = ly.ekspor(tmp_path / "mesin", ds)

    assert meta["pemeriksaan"]["sama"] == meta["pemeriksaan"]["gambar"] > 0
    # Model satu zaman mungkin belum punya deteksi di atas ambang; keluaran mentah tetap harus sama (tidak bisa lolos kosong).
    assert meta["pemeriksaan"]["selisih_koordinat"] < ly.BATAS_EKSPOR and meta["pemeriksaan"]["selisih_peluang"] < ly.BATAS_PELUANG
    gambar = cv2.imread(str(sorted((ds / "valid" / "images").iterdir())[0]))
    lewat_onnx = pyx.PencariYolox(tmp_path / "mesin")(gambar)
    lewat_torch = ly.cari_torch(ly.muat_mesin(tmp_path / "mesin"), 128, "cpu")(gambar)
    assert len(lewat_onnx) == len(lewat_torch)
    assert all(max(abs(a - b) for a, b in zip(u[:4], v[:4])) < ly.BATAS_EKSPOR for u, v in zip(lewat_onnx, lewat_torch))


def test_pencari_kendaraan_satu_kelas_dari_latih_yolox_sampai_baca_gambar(tmp_path):
    # Rencana 32: mesin satu kelas dari latih_yolox dimuat PencariKendaraan sesudah ambangnya ditetapkan, memberi jenis "kendaraan",
    # sama dengan PencariYolox di atas ambang itu, dan berjalan lewat baris perintah baca_gambar sebagai tahap kendaraan.
    import json
    import subprocess
    import sys

    from model_terkunci import ModelDitolak

    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)
    ly.latih("nano", 128, ds, unduhan, tmp_path / "mesin", zaman=1, perangkat="cpu", kunci=kunci)
    ly.ekspor(tmp_path / "mesin", ds)
    with pytest.raises(ModelDitolak, match="ditetapkan"):
        kd.PencariKendaraan(tmp_path / "mesin")
    kd.tetapkan(tmp_path / "mesin", 0.02, "uji")
    gambar = cv2.imread(str(sorted((ds / "valid" / "images").iterdir())[0]))

    hasil = kd.PencariKendaraan(tmp_path / "mesin")(gambar)
    tinggi = kd.PencariKendaraan(tmp_path / "mesin", ambang=0.5)

    assert [h[:5] for h in hasil] == [k for k in pyx.PencariYolox(tmp_path / "mesin")(gambar) if k[4] >= 0.02]
    assert all(h[5] == "kendaraan" for h in hasil)
    assert tinggi.ambang == 0.5 and all(h[4] >= 0.5 for h in tinggi(gambar))  # ambang argumen mengalahkan kendaraan.json
    baca = AKAR / "data" / "keluaran" / "fpo-indo-1"
    if not (baca / "mesin.onnx").exists():
        pytest.skip("fpo-indo-1 ONNX belum ada (Rencana 11)")
    folder = tmp_path / "capture" / "capture cctv mobil"
    folder.mkdir(parents=True)
    cv2.imwrite(str(folder / "a.png"), np.full((360, 640, 3), 90, np.uint8))
    jalan = subprocess.run([sys.executable, str(AKAR / "tools" / "lab" / "baca_gambar.py"), "jalan", str(tmp_path / "capture"),
                            str(tmp_path / "keluar"), str(tmp_path / "mesin"), str(tmp_path / "mesin"), str(baca), str(UNDUHAN),
                            "--ambang", "0.25", "--cadangan-utuh"], capture_output=True, text=True)
    assert jalan.returncode == 0, (jalan.stdout + jalan.stderr)[-2000:]
    assert json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())["aturan"]["tahap_kendaraan"] is True


def test_ekspor_kendaraan_coco_sungguhan_sama_dengan_torch(tmp_path):
    if not (UNDUHAN / "yolox-nano-coco" / "yolox_nano.pth").exists():
        pytest.skip("bobot awal belum diunduh (Rencana 13 Task 1)")
    (tmp_path / "gambar").mkdir()
    rng = np.random.default_rng(0)
    for i in range(3):
        cv2.imwrite(str(tmp_path / "gambar" / f"{i}.png"), rng.integers(0, 255, (360, 640, 3), dtype=np.uint8))

    meta = kd.ekspor("nano", UNDUHAN, tmp_path / "gambar", tmp_path / "kendaraan", ambang=0.25)

    assert meta["tujuan"] == "belajar" and meta["bahan"] == ["bobot-yolox"] and meta["ambang"] == 0.25
    assert meta["pemeriksaan"]["gambar"] == 3
    assert kd.PencariKendaraan(tmp_path / "kendaraan")(np.full((360, 640, 3), 90, np.uint8)) == []
