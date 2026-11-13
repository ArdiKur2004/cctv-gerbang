"""Lama satu panggilan model ONNX di CPU dengan masukan buatan (tanpa data), untuk 1, 2, dan 4 utas (Rencana 12, K29).

Hanya memakai numpy dan onnxruntime, dan tidak mengimpor apa pun dari repo, supaya bisa dijalankan apa adanya di Mini PC.
Tiap model: PANASKAN panggilan pemanasan, lalu ULANG panggilan diukur. Beban mesin (loadavg) dicatat sebelum dan sesudah.

  python ukur_onnx_cpu.py <berkas.onnx> [<berkas.onnx> ...] --keluar hasil.json
"""
import argparse
import json
import os
import platform
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort

UTAS = (1, 2, 4)
ULANG = 20
PANASKAN = 5
JENIS = {"tensor(uint8)": np.uint8, "tensor(float)": np.float32, "tensor(int64)": np.int64}


def masukan_buatan(sesi, rng):
    hasil = {}
    for m in sesi.get_inputs():
        bentuk = [d if isinstance(d, int) and d > 0 else 1 for d in m.shape]
        jenis = JENIS.get(m.type)
        if jenis is None:
            raise ValueError(f"tipe masukan {m.type} belum didukung")
        hasil[m.name] = (rng.integers(0, 256, bentuk).astype(jenis) if jenis is np.uint8
                         else rng.integers(0, 2, bentuk).astype(jenis) if jenis is np.int64
                         else rng.random(bentuk).astype(jenis))
    return hasil


def ukur(berkas, utas, ulang=ULANG, panaskan=PANASKAN):
    opsi = ort.SessionOptions()
    opsi.intra_op_num_threads = utas
    opsi.inter_op_num_threads = 1
    sesi = ort.InferenceSession(str(berkas), opsi, providers=["CPUExecutionProvider"])
    x = masukan_buatan(sesi, np.random.default_rng(0))
    for _ in range(panaskan):
        sesi.run(None, x)
    lama = []
    for _ in range(ulang):
        mulai = time.perf_counter()
        sesi.run(None, x)
        lama.append(1000 * (time.perf_counter() - mulai))
    return {"median_ms": round(float(np.median(lama)), 1), "p95_ms": round(float(np.percentile(lama, 95)), 1), "ulang": ulang}


def cpu():
    try:
        with open("/proc/cpuinfo") as berkas:
            for baris in berkas:
                if baris.startswith("model name"):
                    return baris.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def beban():
    return [round(x, 2) for x in os.getloadavg()] if hasattr(os, "getloadavg") else None


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Lama model ONNX di CPU dengan masukan buatan.")
    urai.add_argument("berkas", nargs="+")
    urai.add_argument("--keluar", required=True)
    p = urai.parse_args(argumen)
    hasil = {"cpu": cpu(), "cpu_terlihat": os.cpu_count(), "onnxruntime": ort.__version__, "beban_sebelum": beban(),
             "model": []}
    for b in p.berkas:
        per_utas = {str(u): ukur(b, u) for u in UTAS}
        hasil["model"].append({"berkas": Path(b).name, "ukuran_byte": Path(b).stat().st_size, "per_utas": per_utas})
        print(f"{Path(b).name}: " + "; ".join(f"utas {u} median {x['median_ms']} ms (p95 {x['p95_ms']})" for u, x in per_utas.items()))
    hasil["beban_sesudah"] = beban()
    Path(p.keluar).write_text(json.dumps(hasil, indent=1))
    print(f"cpu {hasil['cpu']}; terlihat {hasil['cpu_terlihat']}; beban {hasil['beban_sebelum']} -> {hasil['beban_sesudah']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(utama())
