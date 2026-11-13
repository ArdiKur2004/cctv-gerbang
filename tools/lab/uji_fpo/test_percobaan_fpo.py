"""Percobaan pertama jalur latih ulang fast-plate-ocr di image lab tambahan (K26), tanpa jaringan dan tanpa data plat (hanya
plat buatan tulisan komputer). Di luar gerbang biasa: butuh image cctvgerbang-lab-fpo:v1 dan berkas model di data/unduhan.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
VENDOR = AKAR / "vendor" / "fast-plate-ocr"
UNDUHAN = AKAR / "data" / "unduhan"
sys.path.insert(0, str(VENDOR))
sys.path.insert(0, str(AKAR / "tools" / "lab"))
from model_terkunci import daftar_berkas, verifikasi_berkas  # noqa: E402

TEKS = ["B1234XY", "D5678AB", "AB12CD", "F9012Z", "H3456KL", "L7890MN", "N2468PQ", "R1357ST"]
BUTIR = {"keras": ("fpo-cct-s-v2-keras", "cct_s_v2_global.keras"), "onnx": ("fpo-cct-s-v2-onnx", "cct_s_v2_global.onnx"),
         "plat": ("fpo-cct-s-v2-config", "cct_s_v2_global_plate_config.yaml"),
         "model": ("fpo-cct-s-v2-model-config", "cct_s_v2_global_model_config.yaml")}
ADA = all((UNDUHAN / b / n).is_file() for b, n in BUTIR.values())


def jalur(kunci):
    butir, nama = BUTIR[kunci]
    return verifikasi_berkas(UNDUHAN / butir / nama, butir, daftar_berkas())


def plat_buatan(teks):
    kanvas = np.full((110, 360, 3), 255, np.uint8)
    cv2.putText(kanvas, teks, (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 0, 0), 3)
    return kanvas


def test_keras_berjalan_di_atas_torch():
    import keras

    assert keras.backend.backend() == "torch" and keras.__version__ == "3.15.1"


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_bobot_keras_sama_dengan_onnx_terbitan():
    # Bobotnya sama: model .keras yang dijalankan Keras di atas torch harus memberi keluaran yang sama dengan ONNX terbitan.
    # TF32 (bawaan torch untuk cuDNN di GPU) dimatikan: dengan TF32 selisihnya sampai 3,98e-3, tanpa TF32 1,13e-6, di CPU
    # 6,62e-6; huruf yang terpilih sama di ketiganya (diukur 15 Okt dengan plat buatan).
    import onnxruntime as ort
    import torch
    from fast_plate_ocr.core.process import resize_image
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur("plat"))
    model = load_keras_model(jalur("keras"), cfg)
    x = np.stack([resize_image(cv2.cvtColor(plat_buatan(t), cv2.COLOR_BGR2RGB), cfg.img_height, cfg.img_width,
                               image_color_mode=cfg.image_color_mode, keep_aspect_ratio=cfg.keep_aspect_ratio,
                               interpolation_method=cfg.interpolation, padding_color=cfg.padding_color) for t in TEKS])
    tf32 = torch.backends.cudnn.allow_tf32, torch.backends.cuda.matmul.allow_tf32
    torch.backends.cudnn.allow_tf32 = torch.backends.cuda.matmul.allow_tf32 = False
    try:
        keluar = model.predict(x.astype(np.float32), verbose=0)
    finally:
        torch.backends.cudnn.allow_tf32, torch.backends.cuda.matmul.allow_tf32 = tf32
    k = keluar["plate"] if isinstance(keluar, dict) else (keluar[0] if isinstance(keluar, (list, tuple)) else keluar)
    sesi = ort.InferenceSession(str(jalur("onnx")), providers=["CPUExecutionProvider"])
    nama = [o.name for o in sesi.get_outputs()]
    o = sesi.run(["plate" if "plate" in nama else nama[0]], {"input": x.astype(np.uint8)})[0]
    k = np.asarray(k).reshape(len(TEKS), cfg.max_plate_slots, -1)
    o = np.asarray(o).reshape(len(TEKS), cfg.max_plate_slots, -1)
    print(f"\nselisih terbesar keras vs onnx: {np.abs(k - o).max():.2e}")
    assert np.allclose(k, o, atol=1e-3)
    assert (k.argmax(-1) == o.argmax(-1)).all()


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_latih_ulang_satu_zaman_pada_plat_buatan(tmp_path):
    # Rantainya: perintah latih fast-plate-ocr (Keras di atas torch, tanpa jaringan) memuat bobot terbitan, melatih, menyimpan.
    # Kernel Triton bawaan torch dicabut lebih dulu (matikan_kernel_triton): image lab tak punya kompiler C, dan tanpa itu
    # latihan di GPU berhenti dengan "Failed to find C compiler" (bmm_outer_product, diukur 15 Okt).
    for sisi in ("latih", "val"):
        folder = tmp_path / sisi
        folder.mkdir()
        with open(folder / "anotasi.csv", "w", newline="") as berkas:
            tulis = csv.writer(berkas)
            tulis.writerow(["image_path", "plate_text", "plate_region"])
            for i, t in enumerate(TEKS * 2):
                cv2.imwrite(str(folder / f"{i}.png"), plat_buatan(t))
                tulis.writerow([f"{i}.png", t, "Indonesia"])

    hasil = subprocess.run(
        [sys.executable, "-c", "from baca_vlm import matikan_kernel_triton; matikan_kernel_triton(); "
         "from fast_plate_ocr.cli.cli import main_cli; main_cli()", "train",
         "--model-config-file", str(jalur("model")), "--plate-config-file", str(jalur("plat")),
         "--annotations", str(tmp_path / "latih/anotasi.csv"), "--val-annotations", str(tmp_path / "val/anotasi.csv"),
         "--weights-path", str(jalur("keras")), "--epochs", "1", "--batch-size", "8", "--seed", "0",
         "--output-dir", str(tmp_path / "keluar")],
        capture_output=True, text=True, cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": os.pathsep.join([str(VENDOR), str(AKAR / "tools" / "lab")])})

    assert hasil.returncode == 0, hasil.stdout[-3000:] + hasil.stderr[-3000:]
    assert list((tmp_path / "keluar").rglob("*.keras"))


def bobot_jalur_latih(berkas_model):
    # Persis langkah perintah latih (cli/train.py): build_model dari konfigurasi model, lalu load_weights(skip_mismatch=True).
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.model.model_builders import build_model
    from fast_plate_ocr.train.model.model_schema import load_model_config_from_yaml

    model = build_model(load_model_config_from_yaml(berkas_model), load_plate_config_from_yaml(jalur("plat")),
                        enable_region_head=True)
    model.load_weights(jalur("keras"), skip_mismatch=True)
    return [np.asarray(w) for w in model.get_weights()]


def bobot_terbitan():
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    return [np.asarray(w) for w in load_keras_model(jalur("keras"), load_plate_config_from_yaml(jalur("plat"))).get_weights()]


def termuat_utuh(a, b):
    return len(a) == len(b) and all(x.shape == y.shape and np.array_equal(x, y) for x, y in zip(a, b))


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_perintah_latih_memuat_bobot_terbitan_utuh():
    # skip_mismatch=True melewati lapisan yang tak cocok tanpa galat. Jadi "latihan jalan" belum berarti mulai dari bobot
    # terbitan: semua tensor (192, diukur 15 Okt) harus sama persis dengan berkas .keras.
    assert termuat_utuh(bobot_jalur_latih(jalur("model")), bobot_terbitan())


@pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")
def test_konfigurasi_salah_dimuat_tanpa_galat_tetapi_tertangkap(tmp_path):
    # Kontrol negatif untuk uji di atas: konfigurasi 4 lapis (terbitan 5) dimuat tanpa galat, sebagian bobot acak.
    asli = Path(jalur("model")).read_text()
    assert asli.count("\n  layers: 5\n") == 1
    salah = tmp_path / "model_config.yaml"
    salah.write_text(asli.replace("\n  layers: 5\n", "\n  layers: 4\n"))

    assert not termuat_utuh(bobot_jalur_latih(salah), bobot_terbitan())
