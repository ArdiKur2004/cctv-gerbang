"""Pembaca kedua untuk langkah baca huruf: fast-plate-ocr @ 9ce7a5b dengan model cct-s-v2-global, di CPU, tanpa jaringan.

Dipakai untuk membetulkan label set uji (K22): bacaannya dibandingkan dengan bacaan Qwen3-VL (tools/lab/label_curiga.py).
Sekaligus angka pembanding "paket jadi" pertama (spec bagian 8.1 langkah 6, K16).

Kedua berkas model diunduh lewat tools/ambil-berkas.ps1 dan diverifikasi SHA-256-nya terhadap kunci
(tools/lab/model_terkunci.py) SEBELUM onnxruntime dan fast-plate-ocr dimuat. Kode fast-plate-ocr dibaca dari klon yang
dikunci di vendor/fast-plate-ocr; jalur unduh otomatisnya tidak pernah dipakai (model diberi lewat jalur berkas).
Penilaian dan bentuk keluarannya sama dengan tools/lab/baca_vlm.py.

Keluaran:
- hasil.jsonl: bacaan tiap gambar. Memuat nomor plat: tinggal di data/, agen tidak membukanya.
- ringkasan.json: hitungan saja. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/baca_fpo.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/unduhan /kerja/data/keluaran/baca-fpo [uji|latih]
"""
import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, SISI, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from model_terkunci import ModelDitolak, daftar_berkas, verifikasi_berkas  # noqa: E402
from plat import bersihkan  # noqa: E402,F401  (dipakai uji model sungguhan)

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "fast-plate-ocr"
BUTIR_MODEL = "fpo-cct-s-v2-onnx"
BUTIR_KONFIGURASI = "fpo-cct-s-v2-config"


def ubah_warna(gambar_bgr, mode):
    """Gambar OpenCV (biru-hijau-merah) ke mode warna yang diminta konfigurasi model."""
    if mode == "rgb":
        return cv2.cvtColor(gambar_bgr, cv2.COLOR_BGR2RGB)
    if mode == "grayscale":
        return cv2.cvtColor(gambar_bgr, cv2.COLOR_BGR2GRAY)
    raise ValueError(f"mode warna tidak dikenal: {mode}")


class PembacaFpo:
    """Pembaca plat fast-plate-ocr. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali teks mentah."""

    def __init__(self, folder_unduhan):
        daftar = daftar_berkas()
        jalur = {b: verifikasi_berkas(Path(folder_unduhan) / b / daftar.get(b, ("?", ""))[0], b, daftar)
                 for b in (BUTIR_MODEL, BUTIR_KONFIGURASI)}

        sys.path.insert(0, str(VENDOR))
        from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

        self._model = LicensePlateRecognizer(device="cpu", onnx_model_path=jalur[BUTIR_MODEL],
                                             plate_config_path=jalur[BUTIR_KONFIGURASI])
        self.mode_warna = self._model.config.image_color_mode
        self.wilayah_indonesia = "Indonesia" in (self._model.config.plate_regions or [])

    def __call__(self, gambar_bgr):
        return self._model.run_one(ubah_warna(gambar_bgr, self.mode_warna)).plate


def utama(berkas_pembagian, folder_gambar, folder_unduhan, keluar, baca=None, sisi="uji"):
    if baca is None:
        try:
            baca = PembacaFpo(folder_unduhan)
        except ModelDitolak as galat:
            print(f"DITOLAK: {galat}")
            return 2
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    baris, ringkasan = nilai(pembagian, folder_gambar, baca, sisi)
    ringkasan = {"model": "fast-plate-ocr @ 9ce7a5b, cct-s-v2-global, CPU", "sisi": sisi, **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for k in KELOMPOK:
        print(f"{k:<13} {uraikan(ringkasan['per_kelompok'][k])}")
    print(f"detik per gambar: {ringkasan['detik_per_gambar']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (5, 6) or (len(sys.argv) == 6 and sys.argv[5] not in SISI):
        print("Pakai: python baca_fpo.py <pembagian.json> <folder-gambar> <folder-unduhan> <folder-keluaran> [uji|latih]")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:5], sisi=sys.argv[5] if len(sys.argv) == 6 else "uji"))
