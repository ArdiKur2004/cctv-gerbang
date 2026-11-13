"""Uji baca lokal dengan PLAT DUMMY: teks acak menurut pola Perpol 7/2021, bukan plat orang (K78, owner 13 Nov).

Karena teksnya acak dan labelnya diketahui, hasilnya boleh dibuka agen dan dinilai otomatis tanpa lembar owner. Dua hal diuji:
1. program baca (tools/baca_lokal.py) berjalan dari gambar sampai bacaan, dan seberapa sering ia benar pada plat buatan;
2. jalur penilaian jawaban owner (baca_lokal.nilai): jawaban "salah/tak terbaca" disusun dari label lalu dinilai, dan hasilnya
   harus sama dengan hitungan langsung. Kalau berbeda, penilaian lembar owner tidak boleh dipercaya.

Huruf digambar dari kisi garis yang sama dengan tools/lab/plat_buatan.py (dibaca dari sumbernya, tidak disalin), tanpa OpenCV.
Gambar bergaya tangkapan Bardi: 640x360, latar dan "kendaraan" polos, plat 2 baris (nomor + masa berlaku), dengan buram, derau,
gelap/terang, dan kompresi JPEG acak.

  python tools/uji_dummy.py buat 200 data/keluaran/dummy-1 [--benih 1]
  python tools/uji_dummy.py nilai data/keluaran/dummy-1
"""
import argparse
import ast
import csv
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parent.parent


def _muat(nama, jalur):
    spek = importlib.util.spec_from_file_location(nama, jalur)
    modul = importlib.util.module_from_spec(spek)
    spek.loader.exec_module(modul)
    return modul


bl = _muat("baca_lokal", AKAR / "tools" / "baca_lokal.py")


def baca_huruf():
    """Tabel HURUF dari plat_buatan.py lewat ast (berkas itu mengimpor cv2, jadi tidak bisa diimpor di sini)."""
    pohon = ast.parse((AKAR / "tools" / "lab" / "plat_buatan.py").read_text(encoding="utf-8"))
    for simpul in pohon.body:
        if isinstance(simpul, ast.Assign) and any(getattr(t, "id", None) == "HURUF" for t in simpul.targets):
            return ast.literal_eval(simpul.value)
    raise RuntimeError("HURUF tidak ditemukan di plat_buatan.py")


HURUF = baca_huruf()
ABJAD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WARNA = {"putih": ((235, 235, 235), (20, 20, 20)), "hitam": ((25, 25, 25), (230, 230, 230))}


def teks_acak(rng):
    wilayah = "".join(rng.choice(list(ABJAD), size=int(rng.choice([1, 2], p=[0.6, 0.4]))))
    panjang = int(rng.integers(1, 5))
    nomor = str(int(rng.integers(1, 10))) + "".join(str(int(d)) for d in rng.integers(0, 10, size=panjang - 1))
    seri = "".join(rng.choice(list(ABJAD), size=int(rng.choice([0, 1, 2, 3], p=[0.05, 0.25, 0.45, 0.25]))))
    return wilayah, nomor, seri


def garis(kanvas, x0, y0, x1, y1, tebal, warna):
    """Garis tebal: cakram yang dicap sepanjang ruas."""
    n = max(2, int(np.hypot(x1 - x0, y1 - y0) * 2))
    r = max(0.6, tebal / 2)
    t, l = kanvas.shape[:2]
    for s in np.linspace(0, 1, n):
        cx, cy = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        ya, yb = max(0, int(cy - r)), min(t, int(cy + r) + 1)
        xa, xb = max(0, int(cx - r)), min(l, int(cx + r) + 1)
        if ya >= yb or xa >= xb:
            continue
        yy, xx = np.mgrid[ya:yb, xa:xb]
        kanvas[ya:yb, xa:xb][(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r] = warna


def tulis_baris(kanvas, kelompok, tengah_x, y, tinggi, lebar_maks, warna):
    lebar = 0.55 * tinggi
    jarak, jarak_kel = 0.4 * lebar, 1.0 * lebar
    n = sum(len(k) for k in kelompok)
    total = n * lebar + (n - len(kelompok)) * jarak + (len(kelompok) - 1) * jarak_kel
    if total > lebar_maks:
        s = lebar_maks / total
        y += tinggi * (1 - s) / 2
        tinggi, lebar, jarak, jarak_kel, total = tinggi * s, lebar * s, jarak * s, jarak_kel * s, lebar_maks
    tebal = max(1.0, 0.14 * lebar)
    x = tengah_x - total / 2
    for i, k in enumerate(kelompok):
        for j, h in enumerate(k):
            for ruas in HURUF[h]:
                for (ax, ay), (bx, by) in zip(ruas, ruas[1:]):
                    garis(kanvas, x + ax / 6 * lebar, y + ay / 10 * tinggi, x + bx / 6 * lebar, y + by / 10 * tinggi, tebal, warna)
            x += lebar + (jarak if j < len(k) - 1 else 0)
        if i < len(kelompok) - 1:
            x += jarak_kel


def gambar_plat(wilayah, nomor, seri, lebar, rng):
    tinggi = int(round(lebar / rng.uniform(2.0, 2.6)))  # rasio plat motor
    dasar, tulisan = WARNA[str(rng.choice(list(WARNA), p=[0.6, 0.4]))]
    kanvas = np.full((tinggi, lebar, 3), dasar, np.uint8)
    kanvas[:2], kanvas[-2:], kanvas[:, :2], kanvas[:, -2:] = tulisan, tulisan, tulisan, tulisan
    tulis_baris(kanvas, [k for k in (wilayah, nomor, seri) if k], lebar / 2, 0.11 * tinggi, 0.52 * tinggi, 0.9 * lebar, tulisan)
    masa = f"{int(rng.integers(1, 13)):02d}.{int(rng.integers(24, 31)):02d}"
    tulis_baris(kanvas, [masa], lebar / 2, 0.73 * tinggi, 0.14 * tinggi, 0.4 * lebar, tulisan)
    return kanvas


def buram(g, k):
    if k <= 1:
        return g
    f = g.astype(np.float32)
    pad = np.pad(f, ((k // 2, k // 2), (k // 2, k // 2), (0, 0)), mode="edge")
    c = pad.cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0), (0, 0)))
    t, l = g.shape[:2]
    s = c[k:k + t, k:k + l] - c[:t, k:k + l] - c[k:k + t, :l] + c[:t, :l]
    return (s / (k * k)).clip(0, 255).astype(np.uint8)


def adegan(rng, lebar_gambar=640, tinggi_gambar=360):
    g = np.empty((tinggi_gambar, lebar_gambar, 3), np.uint8)
    g[:] = rng.integers(70, 160, size=3)
    g = (g.astype(np.int16) + rng.integers(-12, 12, size=(tinggi_gambar, lebar_gambar, 1))).clip(0, 255).astype(np.uint8)
    lebar_plat = int(rng.integers(50, 200))
    wilayah, nomor, seri = teks_acak(rng)
    p = gambar_plat(wilayah, nomor, seri, lebar_plat, rng)
    pt, pl = p.shape[:2]
    # "kendaraan": kotak gelap lebih besar di sekitar plat
    vl, vt = min(pl * 3, lebar_gambar - 20), min(pt * 4, tinggi_gambar - 20)
    vx, vy = int(rng.integers(10, lebar_gambar - vl - 9)), int(rng.integers(10, tinggi_gambar - vt - 9))
    g[vy:vy + vt, vx:vx + vl] = rng.integers(20, 120, size=3)
    x, y = vx + (vl - pl) // 2, vy + vt - pt - max(2, (vt - pt) // 6)
    g[y:y + pt, x:x + pl] = p
    kondisi = []
    k = int(rng.choice([1, 1, 3, 5]))
    if k > 1:
        kondisi.append(f"buram{k}")
        g = buram(g, k)
    terang = float(rng.choice([1.0, 1.0, 0.45, 1.35]))
    if terang != 1.0:
        kondisi.append("gelap" if terang < 1 else "terang")
        g = (g.astype(np.float32) * terang).clip(0, 255).astype(np.uint8)
    if rng.random() < 0.4:
        kondisi.append("derau")
        g = (g.astype(np.int16) + rng.normal(0, 10, g.shape)).clip(0, 255).astype(np.uint8)
    return g, f"{wilayah}{nomor}{seri}", [x, y, x + pl, y + pt], "+".join(kondisi) or "bersih"


def simpan_jpg(av, jalur, rgb, mutu):
    cc = av.CodecContext.create("mjpeg", "w")
    cc.width, cc.height, cc.pix_fmt = rgb.shape[1], rgb.shape[0], "yuvj420p"
    cc.time_base = Fraction(1, 25)
    cc.options = {"qmin": str(mutu), "qmax": str(mutu)}
    bingkai = av.VideoFrame.from_ndarray(rgb, format="rgb24").reformat(format="yuvj420p")
    data = b"".join(bytes(p) for p in cc.encode(bingkai)) + b"".join(bytes(p) for p in cc.encode(None))
    jalur.write_bytes(data)


def buat(jumlah, keluar, benih):
    import av
    rng = np.random.default_rng(benih)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    with open(keluar / "label.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["no", "berkas", "teks", "x1", "y1", "x2", "y2", "kondisi", "mutu_jpg"])
        for no in range(1, jumlah + 1):
            g, teks, kotak, kondisi = adegan(rng)
            mutu = int(rng.choice([3, 6, 12]))  # skala mjpeg: kecil = bagus
            nama = f"d{no:04d}.jpg"
            simpan_jpg(av, keluar / "gambar" / nama, g, mutu)
            w.writerow([no, nama, teks, *kotak, kondisi, mutu])
    return {"dibuat": jumlah, "folder": str(keluar / "gambar"), "label": str(keluar / "label.csv"), "benih": benih}


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    return i / float((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)


def nilai(keluar):
    label = {int(r["no"]): r for r in csv.DictReader(open(keluar / "label.csv", encoding="utf-8"))}
    folder_baca = keluar / "baca"
    ringkas_baca = bl.jalan(keluar / "gambar", folder_baca, bl.AMBANG_PENCARI, bl.AMBANG_YAKIN)
    hasil = [json.loads(b) for b in (folder_baca / "hasil.jsonl").read_text(encoding="utf-8").splitlines() if b.strip()]

    # Tiap baris lembar dinilai seperti owner: kotak yang tidak menimpa plat dummy = "bukan plat"; selain itu benar/salah.
    salah, bukan_plat, ketemu = [], [], set()
    per_kondisi = {}
    for b in hasil:
        lab = label[b["gambar"]]
        kotak_lab = [int(lab[k]) for k in ("x1", "y1", "x2", "y2")]
        if iou(b["kotak"], kotak_lab) < 0.3:
            bukan_plat.append(b["baris"])
            continue
        ketemu.add(b["gambar"])
        benar = b["teks"] == lab["teks"]
        if not benar:
            salah.append(b["baris"])
        k = per_kondisi.setdefault(lab["kondisi"], {"n": 0, "benar": 0})
        k["n"] += 1
        k["benar"] += benar

    # Jalur jawaban owner: nomor-nomor di atas dimasukkan ke baca_lokal.nilai, hasilnya harus sama dengan hitungan langsung.
    lewat_owner = bl.nilai(folder_baca, salah, [], bukan_plat)
    dinilai = [b for b in hasil if b["baris"] not in bukan_plat]
    langsung_benar = sum(b["baris"] not in salah for b in dinilai)
    langsung_yakin_salah = sum(b["status"] == "yakin" and b["baris"] in salah for b in dinilai)
    jalur_owner_cocok = (lewat_owner["benar"] == langsung_benar and lewat_owner["yakin_tetapi_salah"] == langsung_yakin_salah)

    huruf_benar = huruf_total = 0
    for b in dinilai:
        t = label[b["gambar"]]["teks"]
        huruf_total += len(t)
        huruf_benar += sum(x == y for x, y in zip(b["teks"], t))
    hasil_uji = {
        "gambar_dummy": len(label),
        "plat_ditemukan": len(ketemu),
        "plat_terlewat": len(label) - len(ketemu),
        "kotak_bukan_plat": len(bukan_plat),
        "dinilai": len(dinilai),
        "benar_utuh": langsung_benar,
        "huruf_benar_persen": round(100 * huruf_benar / huruf_total, 1) if huruf_total else None,
        "yakin": lewat_owner["yakin_dinilai"], "yakin_benar": lewat_owner["yakin_benar"],
        "yakin_tetapi_salah": lewat_owner["yakin_tetapi_salah"],
        "ragu": lewat_owner["ragu_dinilai"], "ragu_benar": lewat_owner["ragu_benar"],
        "per_kondisi": dict(sorted(per_kondisi.items())),
        "ms_per_gambar_median": ringkas_baca["ms_per_gambar_median"],
        "jalur_penilaian_owner_cocok": jalur_owner_cocok,
    }
    (keluar / "nilai-dummy.json").write_text(json.dumps(hasil_uji, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return hasil_uji


def utama(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="perintah", required=True)
    b = sub.add_parser("buat")
    b.add_argument("jumlah", type=int)
    b.add_argument("keluar", type=Path)
    b.add_argument("--benih", type=int, default=1)
    n = sub.add_parser("nilai")
    n.add_argument("keluar", type=Path)
    a = p.parse_args(argv)
    try:
        hasil = buat(a.jumlah, a.keluar, a.benih) if a.perintah == "buat" else nilai(a.keluar)
    except bl.GalatAlat as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return e.kode
    print(json.dumps(hasil, indent=2, ensure_ascii=False))
    if a.perintah == "nilai" and not hasil["jalur_penilaian_owner_cocok"]:
        print("GAGAL: penilaian lewat jawaban owner TIDAK sama dengan hitungan langsung", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
