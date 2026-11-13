"""Plat buatan komputer (Rencana 18, K35): plat nomor Indonesia yang digambar sendiri, untuk melatih pembaca (dan kelak pencari)
dengan bahan BOLEH-PRODUK (data-asal/bahan.json butir plat-buatan).

- HURUF: 36 huruf dan angka (dan titik) yang DIGAMBAR SENDIRI sebagai garis di kisi 6 x 10 (K35, spec 2.7), ditebalkan saat
  digambar. Bentuknya meniru huruf tegak tebal pada plat; kemiripannya diukur dari hasil pembaca, tidak diklaim.
- Isi: pola Perpol 7/2021 (tools/lab/plat.py): kode wilayah 1-2 huruf (acak), nomor urut 1-9999, seri 0-3 huruf; baris kecil
  masa berlaku "MM.YY".
- Warna (docs/peraturan-plat.md): putih/hitam, kuning/hitam, merah/putih, hijau/hitam, ditambah hitam/putih (plat lama).
- Bentuk: lebar/tinggi mobil 2,6-3,4 dan motor 2,0-2,6, dari kuantil kotak plat-lighting (10% 1,97; 50% 2,49; 90% 3,25).
- Variasi (ubah): miring dan perspektif dengan sedikit latar, kecil (tinggi 12-60 px lalu dibesarkan lagi), buram, derau,
  kompresi JPEG, gelap/malam dengan silau, inframerah (kelabu), kotoran.

  buat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/plat_buatan.py buat <jumlah> <keluar> [--benih N]
Keluaran: <keluar>/gambar/NNNNNN.png dan <keluar>/label.csv (berkas, teks, jenis, warna, kondisi). Teksnya acak, bukan plat orang.
"""
import argparse
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

LEBAR_KISI, TINGGI_KISI = 6, 10
HURUF = {
    "0": [[(1, 0), (5, 0), (6, 1), (6, 9), (5, 10), (1, 10), (0, 9), (0, 1), (1, 0)]],
    "1": [[(1.5, 2), (3.5, 0), (3.5, 10)]],
    "2": [[(0, 2), (1, 0), (5, 0), (6, 1), (6, 4), (0, 10), (6, 10)]],
    "3": [[(0, 1), (1, 0), (5, 0), (6, 1), (6, 4), (5, 5), (2, 5)], [(5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "4": [[(5, 10), (5, 0), (0, 7), (6, 7)]],
    "5": [[(6, 0), (0, 0), (0, 5), (5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "6": [[(5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9), (6, 6), (5, 5), (0, 5)]],
    "7": [[(0, 0), (6, 0), (2, 10)]],
    "8": [[(1, 5), (0, 4), (0, 1), (1, 0), (5, 0), (6, 1), (6, 4), (5, 5), (1, 5), (0, 6), (0, 9), (1, 10), (5, 10), (6, 9),
           (6, 6), (5, 5)]],
    "9": [[(6, 5), (1, 5), (0, 4), (0, 1), (1, 0), (5, 0), (6, 1), (6, 9), (5, 10), (1, 10)]],
    "A": [[(0, 10), (0, 2), (2, 0), (4, 0), (6, 2), (6, 10)], [(0, 6), (6, 6)]],
    "B": [[(0, 0), (0, 10), (5, 10), (6, 9), (6, 6), (5, 5), (0, 5)], [(0, 0), (5, 0), (6, 1), (6, 4), (5, 5)]],
    "C": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9)]],
    "D": [[(0, 0), (0, 10), (4, 10), (6, 8), (6, 2), (4, 0), (0, 0)]],
    "E": [[(6, 0), (0, 0), (0, 10), (6, 10)], [(0, 5), (5, 5)]],
    "F": [[(6, 0), (0, 0), (0, 10)], [(0, 5), (5, 5)]],
    "G": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 9), (1, 10), (5, 10), (6, 9), (6, 5), (3, 5)]],
    "H": [[(0, 0), (0, 10)], [(6, 0), (6, 10)], [(0, 5), (6, 5)]],
    "I": [[(3, 0), (3, 10)], [(1, 0), (5, 0)], [(1, 10), (5, 10)]],
    "J": [[(6, 0), (6, 9), (5, 10), (1, 10), (0, 9), (0, 7)]],
    "K": [[(0, 0), (0, 10)], [(6, 0), (0, 6)], [(2, 4.5), (6, 10)]],
    "L": [[(0, 0), (0, 10), (6, 10)]],
    "M": [[(0, 10), (0, 0), (3, 5), (6, 0), (6, 10)]],
    "N": [[(0, 10), (0, 0), (6, 10), (6, 0)]],
    "O": [[(2, 0), (4, 0), (6, 2), (6, 8), (4, 10), (2, 10), (0, 8), (0, 2), (2, 0)]],
    "P": [[(0, 10), (0, 0), (5, 0), (6, 1), (6, 4), (5, 5), (0, 5)]],
    "Q": [[(2, 0), (4, 0), (6, 2), (6, 8), (4, 10), (2, 10), (0, 8), (0, 2), (2, 0)], [(3.5, 7), (6, 10.5)]],
    "R": [[(0, 10), (0, 0), (5, 0), (6, 1), (6, 4), (5, 5), (0, 5)], [(3, 5), (6, 10)]],
    "S": [[(6, 1), (5, 0), (1, 0), (0, 1), (0, 4), (1, 5), (5, 5), (6, 6), (6, 9), (5, 10), (1, 10), (0, 9)]],
    "T": [[(0, 0), (6, 0)], [(3, 0), (3, 10)]],
    "U": [[(0, 0), (0, 9), (1, 10), (5, 10), (6, 9), (6, 0)]],
    "V": [[(0, 0), (3, 10), (6, 0)]],
    "W": [[(0, 0), (1.5, 10), (3, 4), (4.5, 10), (6, 0)]],
    "X": [[(0, 0), (6, 10)], [(6, 0), (0, 10)]],
    "Y": [[(0, 0), (3, 5), (6, 0)], [(3, 5), (3, 10)]],
    "Z": [[(0, 0), (6, 0), (0, 10), (6, 10)]],
    ".": [[(2.6, 9.6), (3.4, 9.6)]],
}
WARNA = {  # nama: (dasar, tulisan), BGR
    "putih": ((235, 235, 235), (20, 20, 20)),
    "hitam": ((25, 25, 25), (230, 230, 230)),
    "kuning": ((40, 200, 235), (20, 20, 20)),
    "merah": ((40, 40, 190), (235, 235, 235)),
    "hijau": ((60, 150, 40), (20, 20, 20)),
}
PELUANG_WARNA = {"putih": 0.45, "hitam": 0.3, "kuning": 0.15, "merah": 0.05, "hijau": 0.05}
RASIO = {"mobil": (2.6, 3.4), "motor": (2.0, 2.6)}
ABJAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def teks_acak(rng):
    """Teks plat acak menurut pola Perpol 7/2021: wilayah 1-2 huruf, nomor 1-9999 tanpa nol di depan, seri 0-3 huruf."""
    wilayah = "".join(rng.choice(list(ABJAD), size=int(rng.choice([1, 2], p=[0.6, 0.4]))))
    panjang = int(rng.integers(1, 5))
    nomor = str(int(rng.integers(1, 10))) + "".join(str(int(d)) for d in rng.integers(0, 10, size=panjang - 1))
    seri = "".join(rng.choice(list(ABJAD), size=int(rng.choice([0, 1, 2, 3], p=[0.05, 0.25, 0.45, 0.25]))))
    return f"{wilayah}{nomor}{seri}"


def gambar_huruf(kanvas, huruf, x, y, lebar, tinggi, tebal, warna):
    for garis in HURUF[huruf]:
        titik = np.array([[x + gx / LEBAR_KISI * lebar, y + gy / TINGGI_KISI * tinggi] for gx, gy in garis], np.float32)
        cv2.polylines(kanvas, [np.round(titik * 16).astype(np.int32)], False, warna, tebal, cv2.LINE_AA, shift=4)


def gambar_baris(kanvas, kelompok, tengah_x, y, tinggi_huruf, lebar_maks, tebal_bagian, warna):
    """Kelompok teks (misalnya ["B", "1234", "XY"]) berjarak antarkelompok, di tengah tengah_x. Bila terlalu lebar, seluruh
    baris diperkecil dengan bentuk huruf tetap dan tetap di tengah tinggi semula, tidak dipersempit sampai menempel (lembar
    contoh pertama Rencana 18)."""
    lebar_huruf = 0.55 * tinggi_huruf
    jarak, jarak_kelompok = 0.4 * lebar_huruf, 1.0 * lebar_huruf  # celah tetap terlihat sesudah garis ditebalkan
    huruf_total = sum(len(k) for k in kelompok)
    lebar_total = huruf_total * lebar_huruf + (huruf_total - len(kelompok)) * jarak + (len(kelompok) - 1) * jarak_kelompok
    if lebar_total > lebar_maks:
        s = lebar_maks / lebar_total
        y += tinggi_huruf * (1 - s) / 2
        tinggi_huruf, lebar_huruf, jarak, jarak_kelompok = tinggi_huruf * s, lebar_huruf * s, jarak * s, jarak_kelompok * s
        lebar_total = lebar_maks
    tebal = max(1, round(tebal_bagian * lebar_huruf))
    x = tengah_x - lebar_total / 2
    for i, k in enumerate(kelompok):
        for j, h in enumerate(k):
            gambar_huruf(kanvas, h, x, y, lebar_huruf, tinggi_huruf, tebal, warna)
            x += lebar_huruf + (jarak if j < len(k) - 1 else 0)
        if i < len(kelompok) - 1:
            x += jarak_kelompok


def plat(teks, jenis, warna, rng, tinggi=96):
    """Satu plat bersih: dasar berwarna, bingkai tipis, baris nomor, dan baris kecil masa berlaku."""
    p = urai(teks)
    if p is None:
        raise ValueError("teks tidak sesuai pola plat")
    lebar = round(tinggi * rng.uniform(*RASIO[jenis]))
    dasar, tulisan = WARNA[warna]
    kanvas = np.full((tinggi, lebar, 3), dasar, np.uint8)
    tepi = max(1, round(0.04 * tinggi))
    cv2.rectangle(kanvas, (tepi, tepi), (lebar - 1 - tepi, tinggi - 1 - tepi), tulisan, max(1, tepi // 2), cv2.LINE_AA)
    kelompok = [k for k in (p.wilayah, str(p.nomor), p.seri) if k]
    gambar_baris(kanvas, kelompok, lebar / 2, 0.11 * tinggi, 0.52 * tinggi, 0.9 * lebar, 0.14, tulisan)
    masa = f"{int(rng.integers(1, 13)):02d}.{int(rng.integers(24, 31)):02d}"
    gambar_baris(kanvas, [masa], lebar / 2, 0.73 * tinggi, 0.14 * tinggi, 0.4 * lebar, 0.14, tulisan)
    return kanvas


def ubah(gambar, rng):
    """Variasi acak untuk satu plat. Kembali: (gambar, kondisi "a+b+..."). Selalu ada sedikit latar dan kemiringan."""
    kondisi = []
    t, l = gambar.shape[:2]
    pinggir = int(0.12 * t)
    latar = tuple(int(x) for x in rng.integers(30, 200, size=3))
    kanvas = cv2.copyMakeBorder(gambar, pinggir, pinggir, pinggir, pinggir, cv2.BORDER_CONSTANT, value=latar)
    T, L = kanvas.shape[:2]
    asal = np.float32([[pinggir, pinggir], [L - pinggir, pinggir], [L - pinggir, T - pinggir], [pinggir, T - pinggir]])
    goyang = rng.uniform(-0.06, 0.06, size=(4, 2)) * [l, t]
    m = cv2.getPerspectiveTransform(asal, (asal + goyang).astype(np.float32))
    g = cv2.warpPerspective(kanvas, m, (L, T), borderMode=cv2.BORDER_CONSTANT, borderValue=latar)
    if rng.random() < 0.5:
        kondisi.append("kecil")
        tinggi_kecil = int(rng.integers(12, 61))
        s = tinggi_kecil / T
        g = cv2.resize(cv2.resize(g, (max(1, round(L * s)), tinggi_kecil), interpolation=cv2.INTER_AREA), (L, T),
                       interpolation=cv2.INTER_LINEAR)
    if rng.random() < 0.4:
        kondisi.append("buram")
        k = int(rng.choice([3, 5, 7]))
        g = cv2.GaussianBlur(g, (k, k), 0)
    if rng.random() < 0.25:
        kondisi.append("malam")
        g = np.clip(g.astype(np.float32) * rng.uniform(0.2, 0.5), 0, 255).astype(np.uint8)
        if rng.random() < 0.5:
            kondisi.append("silau")
            pusat = (int(rng.integers(0, L)), int(rng.integers(0, T)))
            silau = np.zeros((T, L), np.float32)
            cv2.circle(silau, pusat, int(rng.integers(T // 4, T)), 1.0, -1)
            silau = cv2.GaussianBlur(silau, (0, 0), T / 4)[..., None]
            g = np.clip(g + silau * 200, 0, 255).astype(np.uint8)
    if rng.random() < 0.15:
        kondisi.append("inframerah")
        abu = cv2.cvtColor(g, cv2.COLOR_BGR2GRAY)
        abu = cv2.normalize(abu, None, 0, 255, cv2.NORM_MINMAX)
        g = cv2.cvtColor(abu, cv2.COLOR_GRAY2BGR)
    if rng.random() < 0.2:
        kondisi.append("kotor")
        for _ in range(int(rng.integers(3, 15))):
            abu = int(rng.integers(40, 120))  # kelabu, supaya gambar inframerah tetap kelabu
            cv2.circle(g, (int(rng.integers(0, L)), int(rng.integers(0, T))), int(rng.integers(1, max(2, T // 12))),
                       (abu, abu, abu), -1, cv2.LINE_AA)
    if rng.random() < 0.5:
        kondisi.append("derau")
        g = np.clip(g.astype(np.float32) + rng.normal(0, rng.uniform(3, 12), g.shape), 0, 255).astype(np.uint8)
        if "inframerah" in kondisi:
            g = cv2.cvtColor(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    if rng.random() < 0.6:
        kondisi.append("jpeg")
        _, isi = cv2.imencode(".jpg", g, [cv2.IMWRITE_JPEG_QUALITY, int(rng.integers(20, 91))])
        g = cv2.imdecode(isi, cv2.IMREAD_COLOR)
        if "inframerah" in kondisi:
            g = cv2.cvtColor(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    return g, "+".join(kondisi) or "bersih"


def buat(jumlah, keluar, benih=0):
    """Menulis `jumlah` plat buatan ke keluar/gambar/ dan keluar/label.csv. Kembali: hitungan per jenis dan warna."""
    keluar = Path(keluar)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    hitung = {"jenis": {}, "warna": {}}
    with open(keluar / "label.csv", "w", newline="") as berkas:
        tulis = csv.writer(berkas)
        tulis.writerow(["berkas", "teks", "jenis", "warna", "kondisi"])
        for i in range(jumlah):
            rng = np.random.default_rng([benih, i])
            jenis = "mobil" if rng.random() < 0.6 else "motor"
            warna = str(rng.choice(list(PELUANG_WARNA), p=list(PELUANG_WARNA.values())))
            teks = teks_acak(rng)
            g, kondisi = ubah(plat(teks, jenis, warna, rng, tinggi=int(rng.integers(64, 129))), rng)
            nama = f"{i:06d}.png"
            cv2.imwrite(str(keluar / "gambar" / nama), g)
            tulis.writerow([nama, teks, jenis, warna, kondisi])
            hitung["jenis"][jenis] = hitung["jenis"].get(jenis, 0) + 1
            hitung["warna"][warna] = hitung["warna"].get(warna, 0) + 1
    return hitung


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Plat buatan komputer (Rencana 18, K35).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("buat")
    b.add_argument("jumlah", type=int)
    b.add_argument("keluar")
    b.add_argument("--benih", type=int, default=0)
    p = pengurai.parse_args(argumen)
    try:
        h = buat(p.jumlah, p.keluar, p.benih)
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{p.jumlah} plat buatan: jenis {h['jenis']}, warna {h['warna']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
