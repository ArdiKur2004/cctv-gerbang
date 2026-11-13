"""Pembanding pencari plat siap pakai (Rencana 12): open-image-models @ eaeb588, yolo-v9-t-384-license-plate-end2end (ONNX,
CPU). Bobotnya BELUM-JELAS (docs/VONIS-LISENSI.md; kode latih induknya GPL-3.0): hanya pembanding, tidak masuk produk.

Berkas model diunduh lewat tools/ambil-berkas.ps1 dan diverifikasi SHA-256-nya sebelum onnxruntime dan open-image-models
dimuat. Kode open-image-models dibaca dari klon terkunci di vendor/open-image-models; jalur unduh otomatisnya tidak pernah
dipakai (model diberi lewat jalur berkas). Ambang keyakinan dipilih tools/lab/deteksi.py di validasi, jadi model dijalankan
dengan ambang rendah (AMBANG_MODEL) supaya semua calon kotak ikut dinilai.

  nilai: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_oim.py nilai /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/ringkasan.json
  cepat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_oim.py cepat /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-oim/cepat.json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
import deteksi  # noqa: E402
from model_terkunci import LOKASI_KUNCI, ModelDitolak, daftar_berkas, verifikasi_berkas  # noqa: E402

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "open-image-models"
BUTIR = "oim-yolo-v9-t-384-plat"
AMBANG_MODEL = 0.01
UTAS = (1, 2, 4)


class PencariOim:
    """Pencari plat pembanding. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali daftar (x1, y1, x2, y2, yakin)."""

    def __init__(self, folder_unduhan, utas=None, kunci=LOKASI_KUNCI):
        daftar = daftar_berkas(kunci)
        jalur = verifikasi_berkas(Path(folder_unduhan) / BUTIR / daftar.get(BUTIR, ("?", ""))[0], BUTIR, daftar)
        if str(VENDOR) not in sys.path:
            sys.path.insert(0, str(VENDOR))
        import onnxruntime as ort
        from open_image_models.detection.factory import create_detector

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self._d = create_detector(jalur, backend="yolo_v9", class_labels=["license_plate"], conf_thresh=AMBANG_MODEL,
                                  providers=["CPUExecutionProvider"], sess_options=opsi)

    def __call__(self, gambar_bgr):
        return [(d.bounding_box.x1, d.bounding_box.y1, d.bounding_box.x2, d.bounding_box.y2, float(d.confidence))
                for d in self._d.predict(gambar_bgr)]


def cepat(folder_dataset, folder_unduhan, utas=UTAS, jumlah=60, panaskan=5):
    """Milidetik per foto utuh (praproses + model + pascaproses) di CPU, pada foto validasi."""
    berkas = sorted(p for p in (Path(folder_dataset) / "valid" / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN)
    gambar = [g for g in (cv2.imread(str(b)) for b in berkas[:jumlah]) if g is not None]
    hasil = {"gambar": len(gambar), "panaskan": panaskan, "per_utas": {}}
    for u in utas:
        cari = PencariOim(folder_unduhan, utas=u)
        lama = []
        for i, g in enumerate(gambar):
            mulai = time.perf_counter()
            cari(g)
            if i >= panaskan:
                lama.append(1000 * (time.perf_counter() - mulai))
        hasil["per_utas"][str(u)] = {"median_ms": round(float(np.median(lama)), 1),
                                     "p95_ms": round(float(np.percentile(lama, 95)), 1)}
    return hasil


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Pembanding pencari plat YOLOv9-t-384 (Rencana 12).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    for nama in ("nilai", "cepat"):
        p = perintah.add_parser(nama)
        for a in ("folder_dataset", "folder_unduhan", "keluar"):
            p.add_argument(a)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "nilai":
            hasil = deteksi.nilai(p.folder_dataset, PencariOim(p.folder_unduhan))
            for k, r in hasil["uji"].items():
                print(f"uji {k:<7} plat ditemukan {r['plat_ditemukan']} dari {r['plat']} (rentang 95% "
                      f"{r['rentang_95_ditemukan']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}); kotak palsu "
                      f"{r['kotak_palsu']}; gambar {r['gambar']}")
            print(f"ambang dari validasi {hasil['ambang']}; detik per gambar {hasil['detik_per_gambar']}; tak terbaca "
                  f"{hasil['tak_terbaca']}")
        else:
            hasil = cepat(p.folder_dataset, p.folder_unduhan)
            for u, x in hasil["per_utas"].items():
                print(f"utas {u}: median {x['median_ms']} ms (p95 {x['p95_ms']}) per foto utuh; gambar {hasil['gambar']}")
        Path(p.keluar).parent.mkdir(parents=True, exist_ok=True)
        Path(p.keluar).write_text(json.dumps(hasil, indent=1))
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
