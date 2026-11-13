"""Membandingkan pembaca pada set uji yang sama, dengan dua cara hitung (Rencana 8).

- "semua": seluruh set uji.
- "tanpa-label-pilihan-pembaca": tanpa plat yang labelnya dibetulkan memakai bacaan yang disepakati Qwen3-VL dan
  fast-plate-ocr (Rencana 6; ditandai `label_penerbit`). Pada plat itu kedua pembaca pasti dinilai benar, jadi
  perbandingan yang adil dengan pembaca ketiga memakai cara hitung ini.

Bacaan dibaca dari hasil.jsonl tiap pembaca (tanpa menjalankan model). Keluaran ringkasan.json (hitungan saja).

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/banding_pembaca.py /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/banding-pembaca --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl --hasil mesin-baca-1=/kerja/data/keluaran/baca-mesin-1/hasil.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, ringkas  # noqa: E402
from label_curiga import baca_hasil  # noqa: E402

CARA = ("semua", "tanpa-label-pilihan-pembaca")


def bagian(pembagian):
    return {"semua": pembagian,
            "tanpa-label-pilihan-pembaca": {**pembagian, "uji": [k for k in pembagian["uji"] if "label_penerbit" not in k]}}


def singkat(r):
    n, benar = r["kedatangan"], r["kedatangan_benar"]
    if n == 0:
        return "kosong"
    if r["terlalu_sedikit"]:
        return f"{benar}/{n} (sedikit)"
    bawah, atas = r["rentang_95_kedatangan"]
    return f"{benar}/{n} ({100 * benar / n:.1f}%; {100 * bawah:.1f}-{100 * atas:.1f}%)"


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Membandingkan pembaca dengan dua cara hitung.")
    urai_argumen.add_argument("pembagian")
    urai_argumen.add_argument("keluar")
    urai_argumen.add_argument("--hasil", action="append", required=True, help="nama=jalur hasil.jsonl, boleh berulang")
    p = urai_argumen.parse_args(argumen)
    if not all("=" in h for h in p.hasil):
        print("SALAH PAKAI: --hasil harus nama=jalur")
        return 2
    pembaca = [h.split("=", 1) for h in p.hasil]
    bacaan = {nama: baca_hasil(jalur) for nama, jalur in pembaca}
    ringkasan = {}
    for cara, isi in bagian(json.loads(Path(p.pembagian).read_text())).items():
        ringkasan[cara] = {nama: ringkas(isi, bacaan[nama]) for nama, _ in pembaca}
        print(f"{cara} ({len(isi['uji'])} kedatangan uji)")
        for k in KELOMPOK:
            print(f"  {k:<13} " + " | ".join(f"{nama} {singkat(ringkasan[cara][nama][k])}" for nama, _ in pembaca))
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(utama())
