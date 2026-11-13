"""Lembar label yang DICURIGAI, untuk diperiksa OWNER (K19, K22).

Tiap baris: nomor, potongan plat, A = label penerbit (biru), B = teks yang disepakati dua pembaca (hijau). Owner menyebut
nomor baris yang tulisan B-nya benar, dan nomor baris yang tulisan A maupun B salah; baris yang tidak disebut dianggap
tulisan A benar. Owner tidak perlu mengetik nomor plat. Lembar memuat plat yang terbaca, jadi agen TIDAK PERNAH
membukanya.

Urutan baris tetap: menurut kelompok, lalu SHA-256 teks label.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_curiga.py /kerja/data/keluaran/label-curiga/curiga.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-curiga
"""
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lembar_contoh import KELOMPOK, PER_LEMBAR, baris  # noqa: E402  (lembar_contoh juga membisukan log OpenCV)


def urutkan(curiga):
    return sorted(curiga, key=lambda c: (KELOMPOK.index(c["kelompok"]), hashlib.sha256(c["teks"].encode()).hexdigest()))


def utama(berkas_curiga, folder_gambar, keluar):
    curiga = urutkan(json.loads(Path(berkas_curiga).read_text()))
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    if not curiga:
        print("Tidak ada label yang dicurigai: tidak ada lembar yang dibuat.")
        return 0
    barisan, contoh = [], []
    for nomor, c in enumerate(curiga, 1):
        barisan.append(baris(nomor, cv2.imread(str(Path(folder_gambar) / c["berkas"])), c["teks"], usulan=c["usulan"]))
        contoh.append({"nomor": nomor, **c})
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-curiga-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-curiga.json").write_text(json.dumps({"halaman": halaman, "contoh": contoh}, indent=1))
    jumlah = {k: sum(c["kelompok"] == k for c in contoh) for k in KELOMPOK}
    print(f"{len(contoh)} baris {jumlah} -> {len(halaman)} lembar di {keluar}. "
          "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python lembar_curiga.py <curiga.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
