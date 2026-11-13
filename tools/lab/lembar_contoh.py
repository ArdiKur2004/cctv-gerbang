"""Lembar contoh label untuk diperiksa OWNER (K19): potongan plat dari set uji beserta label penerbitnya.

Lembar ini memuat plat yang terbaca, jadi agen TIDAK PERNAH membukanya (CLAUDE.md §7). Owner membuka berkas PNG-nya di
laptop dan menyebut nomor baris yang labelnya tidak sama dengan platnya. Dari situ terukur seberapa sering label
penerbit salah.

Contoh dipilih tetap, bukan acak: per kelompok, kedatangan diurutkan menurut SHA-256 teks platnya, lalu diambil
PER_KELOMPOK yang pertama; satu gambar per kedatangan (yang pertama). Kelompok yang lebih kecil diambil semuanya.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_contoh.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-contoh
"""
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

# OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr, dan pada INDO-ALPR jalur itu nomor plat: dibisukan.
# Gambar yang tak terbaca tetap terlihat di lembar sebagai "gambar tak terbaca".
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
PER_KELOMPOK = 15
PER_LEMBAR = 20
TINGGI = 72  # tinggi potongan plat di lembar, piksel
LEBAR_NOMOR = 70
LEBAR_POTONGAN = 320
LEBAR_TEKS = 300


def pilih(pembagian):
    terpilih = []
    for kelompok in KELOMPOK:
        anggota = [a for a in pembagian["uji"] if a["kelompok"] == kelompok]
        anggota.sort(key=lambda a: hashlib.sha256(a["teks"].encode()).hexdigest())
        terpilih += anggota[:PER_KELOMPOK]
    return terpilih


def tulisan(teks):
    """Label dengan spasi, seperti tertulis di plat: "B 1234 XYZ"."""
    plat = urai(teks)
    return f"{plat.wilayah} {plat.nomor} {plat.seri}".strip() if plat else teks


def baris(nomor, gambar, teks, usulan=None):
    kanvas = np.full((TINGGI + 8, LEBAR_NOMOR + LEBAR_POTONGAN + LEBAR_TEKS, 3), 255, np.uint8)
    if gambar is None:
        cv2.putText(kanvas, "gambar tak terbaca", (LEBAR_NOMOR + 8, TINGGI // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
    else:
        tinggi, lebar = gambar.shape[:2]
        skala = min(TINGGI / tinggi, LEBAR_POTONGAN / lebar)
        cara = cv2.INTER_AREA if skala < 1 else cv2.INTER_CUBIC
        kecil = cv2.resize(gambar, (max(1, round(lebar * skala)), max(1, round(tinggi * skala))), interpolation=cara)
        kanvas[4:4 + kecil.shape[0], LEBAR_NOMOR:LEBAR_NOMOR + kecil.shape[1]] = kecil
    cv2.putText(kanvas, str(nomor), (6, TINGGI // 2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    x = LEBAR_NOMOR + LEBAR_POTONGAN + 12
    if usulan is None:
        cv2.putText(kanvas, tulisan(teks), (x, TINGGI // 2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (160, 0, 0), 2)
    else:
        # A = label penerbit (biru), B = teks yang disepakati dua pembaca (hijau). Lembar label yang dicurigai (K22).
        cv2.putText(kanvas, f"A {tulisan(teks)}", (x, TINGGI // 2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (160, 0, 0), 2)
        cv2.putText(kanvas, f"B {tulisan(usulan)}", (x, TINGGI - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 120, 0), 2)
    return kanvas


def utama(berkas_pembagian, folder_gambar, keluar):
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    barisan, contoh = [], []
    for nomor, kedatangan in enumerate(pilih(pembagian), 1):
        berkas = kedatangan["berkas"][0]
        barisan.append(baris(nomor, cv2.imread(str(Path(folder_gambar) / berkas)), kedatangan["teks"]))
        contoh.append({"nomor": nomor, "kelompok": kedatangan["kelompok"], "berkas": berkas, "teks": kedatangan["teks"]})
    if not barisan:
        print("Set uji kosong: tidak ada lembar yang dibuat.")
        return 1
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-contoh-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-contoh.json").write_text(json.dumps({"per_kelompok": PER_KELOMPOK, "halaman": halaman, "contoh": contoh}, indent=1))
    jumlah = {k: sum(c["kelompok"] == k for c in contoh) for k in KELOMPOK}
    print(f"{len(contoh)} contoh {jumlah} -> {len(halaman)} lembar di {keluar}. "
          "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python lembar_contoh.py <pembagian.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
