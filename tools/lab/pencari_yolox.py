"""Pencari plat YOLOX dalam ONNX (Rencana 13, K30): bagian yang kelak jalan di server. Hanya numpy, cv2, dan onnxruntime;
tidak memuat torch.

- letterbox: sama dengan praproses YOLOX (vendor/yolox/yolox/data/data_augment.py preproc): gambar BGR diperkecil dengan skala
  min(S/t, S/l), diletakkan di kiri atas kanvas S x S berbantalan 114, tanpa normalisasi.
- urai_keluaran: keluaran YOLOX (N, 6) = cx, cy, w, h, objek, kelas (piksel masukan) -> kotak piksel foto asli dengan yakin =
  objek x kelas, ambang AMBANG_MODEL (ambang sesungguhnya dipilih tools/lab/deteksi.py di validasi), lalu NMS.
- PencariYolox: mesin.onnx yang SHA-256-nya tidak sama dengan mesin-onnx.json ditolak sebelum onnxruntime dimuat.

  nilai: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_yolox.py nilai <folder-mesin> /kerja/data/keluaran/dataset/plat-lighting <keluar.json>
  cepat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_yolox.py cepat <folder-mesin> /kerja/data/keluaran/dataset/plat-lighting <keluar.json>
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
from model_terkunci import ModelDitolak, sha256_berkas  # noqa: E402

BANTAL = 114
NMS_IOU = 0.45
AMBANG_MODEL = 0.01
UTAS = (1, 2, 4)


def letterbox(gambar, ukuran):
    """Gambar BGR -> (masukan uint8 ukuran x ukuran x 3 berbantalan BANTAL di kanan/bawah, skala)."""
    tinggi, lebar = gambar.shape[:2]
    skala = min(ukuran / tinggi, ukuran / lebar)
    kecil = cv2.resize(gambar, (int(lebar * skala), int(tinggi * skala)), interpolation=cv2.INTER_LINEAR)
    kanvas = np.full((ukuran, ukuran, 3), BANTAL, np.uint8)
    kanvas[:kecil.shape[0], :kecil.shape[1]] = kecil
    return kanvas, skala


def nms(kotak, skor, iou_maks=NMS_IOU):
    """Kotak (N, 4) x1y1x2y2 dan skor (N,) -> indeks yang disimpan, urut skor turun."""
    urut = np.argsort(-skor)
    simpan = []
    while urut.size:
        i = int(urut[0])
        simpan.append(i)
        sisa = urut[1:]
        if not sisa.size:
            break
        lebar = (np.minimum(kotak[i, 2], kotak[sisa, 2]) - np.maximum(kotak[i, 0], kotak[sisa, 0])).clip(0)
        tinggi = (np.minimum(kotak[i, 3], kotak[sisa, 3]) - np.maximum(kotak[i, 1], kotak[sisa, 1])).clip(0)
        irisan = lebar * tinggi
        luas_i = (kotak[i, 2] - kotak[i, 0]) * (kotak[i, 3] - kotak[i, 1])
        luas_s = (kotak[sisa, 2] - kotak[sisa, 0]) * (kotak[sisa, 3] - kotak[sisa, 1])
        urut = sisa[irisan / (luas_i + luas_s - irisan + 1e-9) <= iou_maks]
    return simpan


def urai_keluaran(keluaran, skala, ambang=AMBANG_MODEL):
    """Keluaran YOLOX (N, 6) -> daftar (x1, y1, x2, y2, yakin) dalam piksel foto asli."""
    skor = keluaran[:, 4] * keluaran[:, 5]
    pilih = skor >= ambang
    k, s = keluaran[pilih, :4], skor[pilih]
    kotak = np.stack([k[:, 0] - k[:, 2] / 2, k[:, 1] - k[:, 3] / 2, k[:, 0] + k[:, 2] / 2, k[:, 1] + k[:, 3] / 2], 1) / skala
    return [(*(float(x) for x in kotak[i]), float(s[i])) for i in nms(kotak, s)]


def masukan(gambar, ukuran):
    """Gambar BGR -> (larik float32 (1, 3, ukuran, ukuran) 0..255, skala)."""
    lb, skala = letterbox(gambar, ukuran)
    return lb.transpose(2, 0, 1)[None].astype(np.float32), skala


class PencariYolox:
    """Pencari plat dengan mesin.onnx di CPU. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali daftar
    (x1, y1, x2, y2, yakin)."""

    def __init__(self, folder_mesin, utas=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin-onnx.json").read_text())
        if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
            raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
        import onnxruntime as ort

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self.ukuran = int(meta["ukuran"])
        self._sesi = ort.InferenceSession(str(folder / "mesin.onnx"), opsi, providers=["CPUExecutionProvider"])

    def __call__(self, gambar_bgr):
        x, skala = masukan(gambar_bgr, self.ukuran)
        return urai_keluaran(self._sesi.run(None, {"images": x})[0][0], skala)


def cepat(folder_dataset, buat_pencari, utas=UTAS, jumlah=60, panaskan=5):
    """Milidetik per foto utuh (letterbox + model + NMS) di CPU, pada foto validasi. buat_pencari(utas) -> pencari."""
    berkas = sorted(p for p in (Path(folder_dataset) / "valid" / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN)
    gambar = [g for g in (cv2.imread(str(b)) for b in berkas[:jumlah]) if g is not None]
    hasil = {"gambar": len(gambar), "panaskan": panaskan, "per_utas": {}}
    for u in utas:
        cari = buat_pencari(u)
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
    urai = argparse.ArgumentParser(description="Pencari plat YOLOX ONNX: nilai dan cepat (Rencana 13).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    for nama in ("nilai", "cepat"):
        p = perintah.add_parser(nama)
        for a in ("folder_mesin", "folder_dataset", "keluar"):
            p.add_argument(a)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "nilai":
            hasil = deteksi.nilai(p.folder_dataset, PencariYolox(p.folder_mesin))
            for k, r in hasil["uji"].items():
                print(f"uji {k:<7} plat ditemukan {r['plat_ditemukan']} dari {r['plat']} (rentang 95% "
                      f"{r['rentang_95_ditemukan']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}); kotak palsu "
                      f"{r['kotak_palsu']}; gambar {r['gambar']}")
            v = hasil["validasi"]["semua"]
            print(f"ambang dari validasi {hasil['ambang']} (validasi: {v['plat_ditemukan']} dari {v['plat']}, kotak palsu "
                  f"{v['kotak_palsu']}); detik per gambar {hasil['detik_per_gambar']}; tak terbaca {hasil['tak_terbaca']}")
        else:
            hasil = cepat(p.folder_dataset, lambda u: PencariYolox(p.folder_mesin, utas=u))
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
