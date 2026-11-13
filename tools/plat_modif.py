"""Plat motor MODIFIKASI buatan komputer (K79, owner 13 Nov): bahan agar pembaca belajar MEMBACA plat modif.

Owner memilih dua ciri modif: (1) huruf rapat / jarak aneh, (2) font beda: tebal, miring, hias. Teksnya acak menurut pola
Perpol 7/2021 (tools/uji_dummy.teks_acak), jadi bukan plat orang dan boleh dibuka agen (CLAUDE.md §7, plat buatan).
Huruf dasarnya kisi garis yang sama dengan tools/lab/plat_buatan.py; modif adalah ubahan atas kisi itu, tanpa font pihak ketiga.

Tiap plat mendapat SATU modif jarak dan SATU-DUA modif font:
  jarak : rapat | menempel (seri menempel ke nomor) | renggang | acak (jarak tiap huruf berbeda)
  font  : tebal | miring | hias (sudut dibulatkan) | sempit | lebar | goyang (huruf naik-turun)

Keluaran <keluar>/:
  potongan/pNNNN.png  potongan plat saja (bahan latih pembaca), sudah dibuat kecil/buram seperti kamera
  gambar/dNNNN.jpg    adegan 640x360 bergaya tangkapan Bardi (untuk uji rantai lewat tools/uji_dummy.py nilai)
  label.csv           no, berkas, teks, x1..y2, kondisi (= modif, supaya uji_dummy nilai menghitung per modif),
                      gambar_kondisi, mutu_jpg, berkas_potongan, jarak, font
  contoh.png          lembar 40 contoh pertama, untuk diperiksa mata
  ringkasan.json

  python tools/plat_modif.py buat 500 data/keluaran/plat-modif-1 [--benih 79]
  python tools/uji_dummy.py nilai data/keluaran/plat-modif-1      (bacaan pembaca sekarang = garis dasar)

Acuan dari foto kamera sungguhan (owner 13 Nov: "sesuai dengan realtime"). Dari foto Bardi hanya ANGKA yang diambil — letak
dan lebar kotak plat relatif terhadap gambar, bentuknya, terang plat dan cincin kendaraan di sekelilingnya, ketajaman, derau,
mode IR — tanpa membuka gambar dan tanpa nama berkas (CLAUDE.md §4). Kotaknya dari hasil-baca.csv.
  acuan  <hasil-baca.csv> <folder|zip foto> <keluar>   -> acuan.json (angka saja; boleh dibaca agen)
  buat N <keluar> --acuan acuan.json                     -> adegan buatan yang meniru letak, ukuran, terang, kabur foto Bardi
  tempel <hasil-baca.csv> <folder|zip foto> <keluar>     -> plat buatan ditempel di FOTO SUNGGUHAN menutup plat aslinya
         (kotak dilebarkan 12% ke samping, 18% atas-bawah). gambar/ di sini memuat foto owner: agen tidak membukanya.
"""
import argparse
import csv
import importlib.util
import json
import io
import statistics
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parent.parent


def _muat(nama, jalur):
    spek = importlib.util.spec_from_file_location(nama, jalur)
    modul = importlib.util.module_from_spec(spek)
    spek.loader.exec_module(modul)
    return modul


ud = _muat("uji_dummy", AKAR / "tools" / "uji_dummy.py")
HURUF, WARNA = ud.HURUF, ud.WARNA

JARAK = ["rapat", "menempel", "renggang", "acak"]
FONT = ["tebal", "miring", "hias", "sempit", "lebar", "goyang"]
EKS = (".jpg", ".jpeg", ".png")
# Kotak pencari yang dipakai sebagai acuan/tempat tempel harus berbentuk plat: lebar/tinggi 1,3-3,5. Di foto Bardi 13 Nov, 34 dari
# 174 kotak hampir persegi (aspek < 1,3) — itu bukan plat motor utuh, dan meniru atau menempel di sana membuat label bohong.
ASPEK_PLAT = (1.3, 3.5)


def haluskan(ruas, putaran):
    """Chaikin: sudut garis dipotong berulang, huruf kotak jadi membulat (gaya 'hias')."""
    for _ in range(putaran):
        if len(ruas) < 3:
            return ruas
        baru = [ruas[0]]
        for (ax, ay), (bx, by) in zip(ruas, ruas[1:]):
            baru += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        baru.append(ruas[-1])
        ruas = baru
    return ruas


def gaya_acak(rng):
    jarak = str(rng.choice(JARAK))
    font = sorted({str(f) for f in rng.choice(FONT, size=int(rng.choice([1, 2], p=[0.5, 0.5])), replace=False)})
    if "sempit" in font and "lebar" in font:
        font.remove("lebar")
    g = {"jarak_nama": jarak, "font": font,
         "lebar": 0.55, "jarak": 0.4, "jarak_kel": 1.0, "tebal": 0.14, "miring": 0.0, "halus": 0, "goyang": 0.0}
    if jarak == "rapat":
        g["jarak"], g["jarak_kel"] = rng.uniform(0.0, 0.12), rng.uniform(0.15, 0.4)
    elif jarak == "menempel":
        g["jarak"], g["jarak_kel"] = rng.uniform(0.1, 0.3), -1  # -1: seri menempel ke nomor, hanya wilayah yang terpisah
    elif jarak == "renggang":
        g["jarak"], g["jarak_kel"] = rng.uniform(0.6, 0.9), rng.uniform(1.6, 2.4)
    else:
        g["jarak"], g["jarak_kel"] = "acak", rng.uniform(0.3, 1.6)
    if "tebal" in font:
        g["tebal"] = rng.uniform(0.22, 0.32)
    if "miring" in font:
        g["miring"] = rng.uniform(0.15, 0.35) * rng.choice([1, 1, 1, -1])
    if "hias" in font:
        g["halus"] = int(rng.choice([2, 3]))
    if "sempit" in font:
        g["lebar"] = rng.uniform(0.36, 0.45)
    if "lebar" in font:
        g["lebar"] = rng.uniform(0.68, 0.8)
    if "goyang" in font:
        g["goyang"] = rng.uniform(0.06, 0.14)
    return g


def tulis_baris_modif(kanvas, kelompok, tengah_x, y, tinggi, lebar_maks, warna, g, rng):
    if g["jarak_kel"] == -1 and len(kelompok) == 3:
        kelompok = [kelompok[0], kelompok[1] + kelompok[2]]
    lebar = g["lebar"] * tinggi
    n = sum(len(k) for k in kelompok)
    jarak = [(rng.uniform(0.0, 0.9) if g["jarak"] == "acak" else g["jarak"]) * lebar for _ in range(n)]
    jarak_kel = max(0.0, g["jarak_kel"]) * lebar
    sela = []
    for i, k in enumerate(kelompok):
        for j in range(len(k)):
            sela.append(jarak[len(sela)] if j < len(k) - 1 else (jarak_kel if i < len(kelompok) - 1 else 0.0))
    miring_px = abs(g["miring"]) * tinggi
    total = n * lebar + sum(sela) + miring_px
    s = min(1.0, lebar_maks / total)
    y += tinggi * (1 - s) / 2
    tinggi, lebar, total, miring_px = tinggi * s, lebar * s, total * s, miring_px * s
    sela = [v * s for v in sela]
    tebal = max(1.0, g["tebal"] * lebar)
    # Miring: puncak huruf bergeser miring*tinggi, kaki tetap. Miring negatif menggeser ke kiri, jadi awal baris digeser kanan.
    x = tengah_x - total / 2 + (miring_px if g["miring"] < 0 else 0)
    huruf_urut = [h for k in kelompok for h in k]
    for idx, h in enumerate(huruf_urut):
        dy = rng.uniform(-g["goyang"], g["goyang"]) * tinggi
        for ruas in HURUF[h]:
            r = haluskan(ruas, g["halus"])
            titik = [(x + ax / 6 * lebar + g["miring"] * (1 - ay / 10) * tinggi, y + dy + ay / 10 * tinggi) for ax, ay in r]
            for (ax, ay), (bx, by) in zip(titik, titik[1:]):
                ud.garis(kanvas, ax, ay, bx, by, tebal, warna)
        x += lebar + sela[idx]


def gambar_plat_modif(wilayah, nomor, seri, lebar, g, rng, tinggi=None, warna_paksa=None):
    if tinggi is None:
        tinggi = int(round(lebar / rng.uniform(2.0, 2.6)))  # rasio plat motor
    if warna_paksa is None:
        nama_warna = str(rng.choice(list(WARNA), p=[0.6, 0.4]))
        dasar, tulisan = WARNA[nama_warna]
    else:
        nama_warna, dasar, tulisan = warna_paksa
    kanvas = np.full((tinggi, lebar, 3), dasar, np.uint8)
    kanvas[:2], kanvas[-2:], kanvas[:, :2], kanvas[:, -2:] = tulisan, tulisan, tulisan, tulisan
    tulis_baris_modif(kanvas, [k for k in (wilayah, nomor, seri) if k], lebar / 2, 0.11 * tinggi, 0.52 * tinggi, 0.92 * lebar,
                      tulisan, g, rng)
    masa = f"{int(rng.integers(1, 13)):02d}.{int(rng.integers(24, 31)):02d}"
    ud.tulis_baris(kanvas, [masa], lebar / 2, 0.73 * tinggi, 0.14 * tinggi, 0.4 * lebar, tulisan)
    return kanvas, nama_warna


def kecilkan(gambar, lebar_baru):
    """Perkecil dengan rata-rata blok lalu kembalikan ke ukuran semula (meniru plat kecil di kamera), tanpa OpenCV."""
    t, l = gambar.shape[:2]
    f = l / max(8, lebar_baru)
    if f <= 1.05:
        return gambar
    tk, lk = max(4, int(t / f)), max(8, int(l / f))
    ys = (np.arange(tk + 1) * t / tk).astype(int)
    xs = (np.arange(lk + 1) * l / lk).astype(int)
    kecil = np.empty((tk, lk, 3), np.float32)
    for i in range(tk):
        for j in range(lk):
            kecil[i, j] = gambar[ys[i]:ys[i + 1], xs[j]:xs[j + 1]].reshape(-1, 3).mean(0)
    yi = np.minimum((np.arange(t) * tk / t).astype(int), tk - 1)
    xi = np.minimum((np.arange(l) * lk / l).astype(int), lk - 1)
    return kecil[yi][:, xi].clip(0, 255).astype(np.uint8)


def adegan_modif(rng, lebar_gambar=640, tinggi_gambar=360, acuan=None):
    """acuan: satu baris `kotak` dari acuan.json (angka dari foto Bardi, tanpa gambar): letak, ukuran, bentuk, terang plat dan
    kendaraan, ketajaman, derau, dan mode IR ditiru dari sana. Tanpa acuan: adegan acak seperti semula."""
    wilayah, nomor, seri = ud.teks_acak(rng)
    gaya = gaya_acak(rng)
    if acuan is None:
        g = np.empty((tinggi_gambar, lebar_gambar, 3), np.uint8)
        g[:] = rng.integers(70, 160, size=3)
        g = (g.astype(np.int16) + rng.integers(-12, 12, size=(tinggi_gambar, lebar_gambar, 1))).clip(0, 255).astype(np.uint8)
        lebar_plat = int(rng.integers(60, 200))
        p, warna = gambar_plat_modif(wilayah, nomor, seri, lebar_plat, gaya, rng)
        pt, pl = p.shape[:2]
        vl, vt = min(pl * 3, lebar_gambar - 20), min(pt * 4, tinggi_gambar - 20)
        vx, vy = int(rng.integers(10, lebar_gambar - vl - 9)), int(rng.integers(10, tinggi_gambar - vt - 9))
        g[vy:vy + vt, vx:vx + vl] = rng.integers(20, 120, size=3)
        x, y = vx + (vl - pl) // 2, vy + vt - pt - max(2, (vt - pt) // 6)
    else:
        lebar_gambar, tinggi_gambar = int(acuan["lebar_gambar"]), int(acuan["tinggi_gambar"])
        g = np.full((tinggi_gambar, lebar_gambar, 3), int(acuan["luma_latar"]), np.uint8)
        g = (g.astype(np.int16) + rng.integers(-8, 8, size=(tinggi_gambar, lebar_gambar, 1))).clip(0, 255).astype(np.uint8)
        lebar_plat = max(24, int(round(acuan["lebar"] * lebar_gambar * rng.uniform(0.92, 1.08))))
        tinggi_plat = max(12, int(round(lebar_plat / acuan["aspek"])))
        p, warna = gambar_plat_modif(wilayah, nomor, seri, lebar_plat, gaya, rng, tinggi=tinggi_plat,
                                     warna_paksa=warna_dari_acuan(acuan))
        pt, pl = p.shape[:2]
        x = min(max(0, int(round(acuan["cx"] * lebar_gambar - pl / 2))), lebar_gambar - pl)
        y = min(max(0, int(round(acuan["cy"] * tinggi_gambar - pt / 2))), tinggi_gambar - pt)
        vl, vt = min(pl * 3, lebar_gambar), min(pt * 4, tinggi_gambar)
        vx = min(max(0, x + pl // 2 - vl // 2), lebar_gambar - vl)
        vy = min(max(0, y + pt - vt + max(2, (vt - pt) // 6)), tinggi_gambar - vt)
        g[vy:vy + vt, vx:vx + vl] = int(acuan["luma_kendaraan"])
    g[y:y + pt, x:x + pl] = p

    # Potongan latih: plat bersih yang dirusak sendiri (kecil, buram, gelap, derau), terpisah dari adegan.
    pot, kond_pot = p.copy(), []
    if acuan is None and rng.random() < 0.6:
        lebar_k = int(rng.integers(40, 110))
        kond_pot.append(f"kecil{lebar_k}")
        pot = kecilkan(pot, lebar_k)
    k = int(rng.choice([1, 1, 3]))
    if k > 1:
        kond_pot.append(f"buram{k}")
        pot = ud.buram(pot, k)
    if rng.random() < 0.3:
        terang = float(rng.choice([0.5, 1.3]))
        kond_pot.append("gelap" if terang < 1 else "terang")
        pot = (pot.astype(np.float32) * terang).clip(0, 255).astype(np.uint8)
    if rng.random() < 0.4:
        kond_pot.append("derau")
        pot = (pot.astype(np.int16) + rng.normal(0, 10, pot.shape)).clip(0, 255).astype(np.uint8)

    kondisi = []
    if acuan is None:
        k = int(rng.choice([1, 1, 3, 5]))
        if k > 1:
            kondisi.append(f"buram{k}")
            g = ud.buram(g, k)
        terang = float(rng.choice([1.0, 1.0, 0.45, 1.35]))
        if terang != 1.0:
            kondisi.append("gelap" if terang < 1 else "terang")
            g = (g.astype(np.float32) * terang).clip(0, 255).astype(np.uint8)
        if rng.random() < 0.4:
            kondisi.append("derau")
            g = (g.astype(np.int16) + rng.normal(0, 10, g.shape)).clip(0, 255).astype(np.uint8)
    else:
        k = cocokkan_kabur(p, acuan["ketajaman_plat"])
        if k > 1:
            kondisi.append(f"buram{k}")
            g = ud.buram(g, k)
        if acuan["derau"] > 0.5:
            kondisi.append("derau")
            g = (g.astype(np.float32) + rng.normal(0, acuan["derau"], g.shape)).clip(0, 255).astype(np.uint8)
        if acuan["mode"] == "ir":
            kondisi.append("ir")
            g = np.repeat(luma_dari(g).clip(0, 255).astype(np.uint8)[..., None], 3, axis=2)
        pot, kond_pot = g[y:y + pt, x:x + pl].copy(), ["acuan"] + kondisi  # potongan = apa adanya dari adegan beracuan
    return {"adegan": g, "potongan": pot, "teks": f"{wilayah}{nomor}{seri}", "kotak": [x, y, x + pl, y + pt],
            "gaya": gaya, "warna": warna, "kondisi": "+".join(kondisi) or "bersih",
            "kondisi_potongan": "+".join(kond_pot) or "bersih", "bersih": p}


# ---- Acuan dari foto kamera sungguhan: hanya ANGKA yang diambil (CLAUDE.md §4). Nama berkas dan isi gambar tidak dicetak. ----

def luma_dari(rgb):
    return rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def ketajaman_luma(l):
    if l.shape[0] < 3 or l.shape[1] < 3:
        return 0.0
    lap = l[:-2, 1:-1] + l[2:, 1:-1] + l[1:-1, :-2] + l[1:-1, 2:] - 4 * l[1:-1, 1:-1]
    return float(lap.var())


def rata3(l):
    pad = np.pad(l, 1, mode="edge")
    t, w = l.shape
    return sum(pad[i:i + t, j:j + w] for i in range(3) for j in range(3)) / 9.0


def mode_dari(rgb):
    return "ir" if float((rgb.max(2).astype(np.int16) - rgb.min(2)).mean()) < 6 else "warna"


def ukur_kotak(l, kotak):
    """Angka di sekitar satu kotak plat: terang dan kontras plat, terang cincin kendaraan di sekelilingnya, ketajaman, derau."""
    t, w = l.shape
    x1, y1, x2, y2 = (int(v) for v in kotak)
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(t, y2)
    pw, ph = x2 - x1, y2 - y1
    plat = l[y1:y2, x1:x2]
    X1, Y1, X2, Y2 = max(0, x1 - pw // 2), max(0, y1 - ph // 2), min(w, x2 + pw // 2), min(t, y2 + ph // 2)
    sekitar = l[Y1:Y2, X1:X2]
    topeng = np.ones(sekitar.shape, bool)
    topeng[y1 - Y1:y2 - Y1, x1 - X1:x2 - X1] = False
    cincin = sekitar[topeng]
    sisa = (sekitar - rata3(sekitar))[topeng]
    return {"luma_plat": round(float(plat.mean()), 1), "kontras_plat": round(float(plat.std()), 1),
            "luma_kendaraan": round(float(cincin.mean() if cincin.size else plat.mean()), 1),
            "ketajaman_plat": round(ketajaman_luma(plat), 1), "derau": round(float(sisa.std()) if sisa.size else 0.0, 2)}


def warna_dari_acuan(a):
    """Dasar dan tulisan plat (kelabu netral) supaya rata-rata dan simpangan luma-nya menyamai plat sungguhan.
    Plat ~75% dasar, 25% tulisan: rata = 0,75d + 0,25t; simpangan ~ 0,433|d-t|. Plat lebih terang dari kendaraan = plat putih."""
    m, s = float(a["luma_plat"]), float(a["kontras_plat"])
    beda = min(200.0, max(40.0, s / 0.433))
    tanda = 1 if m >= float(a["luma_kendaraan"]) else -1
    d = int(np.clip(m + 0.25 * beda * tanda, 0, 255))
    u = int(np.clip(m - 0.75 * beda * tanda, 0, 255))
    return ("putih" if tanda > 0 else "hitam", (d, d, d), (u, u, u))


def cocokkan_kabur(p, target):
    """Lebar kotak buram (1 = tanpa) yang membuat ketajaman potongan buatan paling dekat dengan plat sungguhan."""
    terbaik = None
    for k in (1, 3, 5, 7, 9):
        q = ud.buram(p, k) if k > 1 else p
        jarak = abs(np.log1p(ketajaman_luma(luma_dari(q))) - np.log1p(max(0.0, float(target))))
        if terbaik is None or jarak < terbaik[0]:
            terbaik = (jarak, k)
    return terbaik[1]


def muat_gambar_sumber(sumber):
    """(nama, rgb) urut nama, dari folder atau zip. Nama hanya dipakai mencocokkan dengan CSV, tidak pernah dicetak."""
    import av
    av.logging.set_level(av.logging.PANIC)

    def satu(bacaan):
        with av.open(bacaan) as w:
            for f in w.decode(video=0):
                return f.to_ndarray(format="rgb24")
        raise ValueError("tanpa bingkai")

    if sumber.suffix.lower() == ".zip":
        with zipfile.ZipFile(sumber) as z:
            daftar = sorted((i for i in z.infolist() if i.filename.lower().endswith(EKS)), key=lambda i: Path(i.filename).name)
            for i in daftar:
                yield Path(i.filename).name, satu(io.BytesIO(z.read(i)))
    else:
        for p in sorted(x for x in sumber.iterdir() if x.is_file() and x.suffix.lower() in EKS):
            yield p.name, satu(str(p))


def baca_kotak_csv(jalur):
    """{nama berkas: [(x1, y1, x2, y2), ...]} dari hasil-baca.csv (pemisah ; atau ,). Kolom teks tidak dibaca."""
    kotak = {}
    with open(jalur, encoding="utf-8-sig", newline="") as f:
        contoh = f.read(4096)
        f.seek(0)
        for b in csv.DictReader(f, delimiter=";" if contoh.count(";") > contoh.count(",") else ","):
            kotak.setdefault(b["berkas"], []).append(tuple(int(float(b[k])) for k in ("x1", "y1", "x2", "y2")))
    return kotak


def ukur_acuan(csv_jalur, sumber, keluar):
    """acuan.json: satu baris angka per kotak plat sungguhan (letak relatif, lebar relatif, bentuk, terang, ketajaman, derau, mode)."""
    kotak_per = baca_kotak_csv(csv_jalur)
    baris, gambar, tanpa_kotak = [], 0, 0
    for nama, rgb in muat_gambar_sumber(sumber):
        daftar = kotak_per.get(nama)
        if not daftar:
            tanpa_kotak += 1
            continue
        gambar += 1
        l = luma_dari(rgb)
        t, w = l.shape
        mode = mode_dari(rgb)
        for (x1, y1, x2, y2) in daftar:
            u = ukur_kotak(l, (x1, y1, x2, y2))
            u.update({"cx": round((x1 + x2) / 2 / w, 4), "cy": round((y1 + y2) / 2 / t, 4), "lebar": round((x2 - x1) / w, 4),
                      "aspek": round((x2 - x1) / max(1, y2 - y1), 3), "luma_latar": round(float(l.mean()), 1),
                      "lebar_gambar": w, "tinggi_gambar": t, "mode": mode})
            baris.append(u)
    if not baris:
        raise ud.bl.GalatAlat("tidak ada kotak yang cocok antara CSV dan sumber gambar", 5)
    angka = [k for k in baris[0] if isinstance(baris[0][k], (int, float))]
    ringkas = {k: {"min": min(b[k] for b in baris), "median": statistics.median(b[k] for b in baris), "maks": max(b[k] for b in baris)}
               for k in angka}
    ringkas["mode"] = dict(Counter(b["mode"] for b in baris))
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "acuan.json").write_text(json.dumps({"alat": "tools/plat_modif.py acuan", "gambar": gambar, "tanpa_kotak": tanpa_kotak,
                                                   "kotak": baris, "ringkas": ringkas}, indent=1, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    return {"gambar": gambar, "kotak": len(baris), "tanpa_kotak": tanpa_kotak, "ringkas": ringkas, "berkas": str(keluar / "acuan.json")}


def lebarkan(kotak, bentuk, sisi=0.12, atas_bawah=0.18):
    """Kotak pencari sering lebih sempit dari plat aslinya: dilebarkan supaya plat sungguhan tertutup SELURUHNYA."""
    t, w = bentuk[:2]
    x1, y1, x2, y2 = kotak
    mx, my = int(round((x2 - x1) * sisi)), int(round((y2 - y1) * atas_bawah))
    return max(0, x1 - mx), max(0, y1 - my), min(w, x2 + mx), min(t, y2 + my)


def tempel(csv_jalur, sumber, keluar, benih, ulang=1):
    """Plat modif buatan ditempel di FOTO SUNGGUHAN menutup plat aslinya (kotak dari hasil-baca.csv, dilebarkan).
    Keluaran memuat foto owner (kendaraan, latar): tinggal di data/, agen tidak membukanya. label.csv hanya teks acak dan angka.
    Foto dengan lebih dari satu kotak dilewati (uji_dummy menilai satu plat per gambar)."""
    import av
    if keluar.exists() and any(keluar.iterdir()):
        raise ud.bl.GalatAlat("folder keluaran sudah berisi, tidak ditimpa", 2)
    rng = np.random.default_rng(benih)
    kotak_per = baca_kotak_csv(csv_jalur)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    no, lewat_multi, tanpa_kotak, lewat_bentuk = 0, 0, 0, 0
    hitung_jarak, hitung_font, teks_semua = Counter(), Counter(), set()
    with open(keluar / "label.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["no", "berkas", "teks", "x1", "y1", "x2", "y2", "kondisi", "gambar_kondisi", "mutu_jpg",
                    "berkas_potongan", "potongan_kondisi", "jarak", "font", "warna"])
        for nama, rgb in muat_gambar_sumber(sumber):
            daftar = kotak_per.get(nama)
            if not daftar:
                tanpa_kotak += 1
                continue
            if len(daftar) > 1:
                lewat_multi += 1
                continue
            bx1, by1, bx2, by2 = daftar[0]
            if not (ASPEK_PLAT[0] <= (bx2 - bx1) / max(1, by2 - by1) <= ASPEK_PLAT[1]):
                lewat_bentuk += 1
                continue
            l = luma_dari(rgb)
            mode = mode_dari(rgb)
            x1, y1, x2, y2 = lebarkan(daftar[0], rgb.shape)
            stat = ukur_kotak(l, daftar[0])
            for _ in range(ulang):
                no += 1
                wilayah, nomor, seri = ud.teks_acak(rng)
                gaya = gaya_acak(rng)
                p, warna = gambar_plat_modif(wilayah, nomor, seri, x2 - x1, gaya, rng, tinggi=y2 - y1, warna_paksa=warna_dari_acuan(stat))
                kond = []
                k = cocokkan_kabur(p, stat["ketajaman_plat"])
                if k > 1:
                    kond.append(f"buram{k}")
                    p = ud.buram(p, k)
                if stat["derau"] > 0.5:
                    kond.append("derau")
                    p = (p.astype(np.float32) + rng.normal(0, stat["derau"], p.shape)).clip(0, 255).astype(np.uint8)
                if mode == "ir":
                    kond.append("ir")
                    p = np.repeat(luma_dari(p).clip(0, 255).astype(np.uint8)[..., None], 3, axis=2)
                g = rgb.copy()
                g[y1:y2, x1:x2] = p
                modif = gaya["jarak_nama"] + "+" + "+".join(gaya["font"])
                nama_g, nama_p = f"t{no:04d}.jpg", f"p{no:04d}.png"
                ud.simpan_jpg(av, keluar / "gambar" / nama_g, g, 6)
                (keluar / "potongan" / nama_p).write_bytes(ud.bl.png(np.ascontiguousarray(p)))
                teks = f"{wilayah}{nomor}{seri}"
                w.writerow([no, nama_g, teks, x1, y1, x2, y2, modif, "tempel+" + ("+".join(kond) or "bersih"), 6, nama_p,
                            "+".join(kond) or "bersih", gaya["jarak_nama"], "+".join(gaya["font"]), warna])
                hitung_jarak[gaya["jarak_nama"]] += 1
                hitung_font.update(gaya["font"])
                teks_semua.add(teks)
    if no == 0:
        raise ud.bl.GalatAlat("tidak ada foto yang kotaknya cocok dengan CSV", 5)
    ringkas = {"alat": "tools/plat_modif.py tempel", "keputusan": "K79", "dibuat": no, "benih": benih, "ulang_per_foto": ulang,
               "foto_dilewati_lebih_dari_satu_kotak": lewat_multi, "foto_dilewati_bentuk_kotak_bukan_plat": lewat_bentuk,
               "foto_tanpa_kotak": tanpa_kotak, "foto_dipakai": no // max(1, ulang), "teks_unik": len(teks_semua),
               "jarak": dict(hitung_jarak), "font": dict(hitung_font), "csv_fpo": tulis_csv_fpo(keluar),
               "catatan": "gambar/ memuat foto owner (latar dan kendaraan sungguhan) dengan plat asli DITUTUP plat buatan; "
                          "agen tidak membukanya. potongan/ hanya plat buatan. Teks acak, bukan plat orang."}
    (keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ringkas


def lembar_contoh(contoh, jalur):
    """Grid potongan BERSIH (sebelum dirusak) supaya bentuk modif terlihat jelas: 4 kolom, tinggi baris 60 px."""
    T, L, kol = 60, 160, 4
    baris = (len(contoh) + kol - 1) // kol
    kanvas = np.full((baris * (T + 8) + 8, kol * (L + 8) + 8, 3), 255, np.uint8)
    for i, c in enumerate(contoh):
        t, l = c.shape[:2]
        s = min(T / t, L / l)
        yi = np.minimum((np.arange(int(t * s)) / s).astype(int), t - 1)
        xi = np.minimum((np.arange(int(l * s)) / s).astype(int), l - 1)
        kecil = c[yi][:, xi]
        r, k = divmod(i, kol)
        y0, x0 = 8 + r * (T + 8), 8 + k * (L + 8)
        kanvas[y0:y0 + kecil.shape[0], x0:x0 + kecil.shape[1]] = kecil
    jalur.write_bytes(ud.bl.png(np.ascontiguousarray(kanvas)))


def tulis_csv_fpo(keluar, porsi_validasi=0.1):
    """CSV fast-plate-ocr (image_path, plate_text) untuk latih_fpo.py latih-lanjut. Validasi = tiap baris ke-10, tetap dan
    terlihat dari nomornya, supaya pembagiannya tidak berubah bila alat dijalankan ulang."""
    baris = list(csv.DictReader(open(keluar / "label.csv", encoding="utf-8", newline="")))
    tiap = max(2, round(1 / porsi_validasi))
    sisi = {"fpo-latih.csv": [b for b in baris if int(b["no"]) % tiap], "fpo-validasi.csv": [b for b in baris if not int(b["no"]) % tiap]}
    for nama, isi in sisi.items():
        with open(keluar / nama, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["image_path", "plate_text"])
            w.writerows([f"potongan/{b['berkas_potongan']}", b["teks"]] for b in isi)
    return {k: len(v) for k, v in sisi.items()}


def buat(jumlah, keluar, benih, acuan=None):
    import av
    if keluar.exists() and any(keluar.iterdir()):
        raise ud.bl.GalatAlat("folder keluaran sudah berisi, tidak ditimpa", 2)
    rng = np.random.default_rng(benih)
    acuan_semua = json.loads(Path(acuan).read_text(encoding="utf-8"))["kotak"] if acuan else []
    acuan_baris = [a for a in acuan_semua if ASPEK_PLAT[0] <= a["aspek"] <= ASPEK_PLAT[1]] or None
    if acuan and not acuan_baris:
        raise ud.bl.GalatAlat("tidak ada kotak acuan berbentuk plat", 5)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    hitung_jarak, hitung_font, contoh, teks_semua = Counter(), Counter(), [], set()
    with open(keluar / "label.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["no", "berkas", "teks", "x1", "y1", "x2", "y2", "kondisi", "gambar_kondisi", "mutu_jpg",
                    "berkas_potongan", "potongan_kondisi", "jarak", "font", "warna"])
        for no in range(1, jumlah + 1):
            a = adegan_modif(rng, acuan=acuan_baris[int(rng.integers(len(acuan_baris)))] if acuan_baris else None)
            gy = a["gaya"]
            modif = gy["jarak_nama"] + "+" + "+".join(gy["font"])
            mutu = int(rng.choice([3, 6, 12]))
            nama, nama_pot = f"d{no:04d}.jpg", f"p{no:04d}.png"
            ud.simpan_jpg(av, keluar / "gambar" / nama, a["adegan"], mutu)
            (keluar / "potongan" / nama_pot).write_bytes(ud.bl.png(np.ascontiguousarray(a["potongan"])))
            w.writerow([no, nama, a["teks"], *a["kotak"], modif, a["kondisi"], mutu, nama_pot, a["kondisi_potongan"],
                        gy["jarak_nama"], "+".join(gy["font"]), a["warna"]])
            hitung_jarak[gy["jarak_nama"]] += 1
            hitung_font.update(gy["font"])
            teks_semua.add(a["teks"])
            if len(contoh) < 40:
                contoh.append(a["bersih"])
    lembar_contoh(contoh, keluar / "contoh.png")
    ringkas = {"alat": "tools/plat_modif.py", "keputusan": "K79", "dibuat": jumlah, "benih": benih,
               "acuan": str(acuan) if acuan else None, "acuan_kotak_dipakai": len(acuan_baris) if acuan_baris else 0,
               "acuan_kotak_dibuang_bentuk": len(acuan_semua) - (len(acuan_baris) if acuan_baris else 0),
               "csv_fpo": tulis_csv_fpo(keluar),
               "teks_unik": len(teks_semua), "jarak": dict(hitung_jarak), "font": dict(hitung_font),
               "asal": "buatan komputer, teks acak pola Perpol 7/2021, huruf kisi sendiri (plat_buatan.HURUF); bukan plat orang",
               "folder_potongan": str(keluar / "potongan"), "folder_adegan": str(keluar / "gambar")}
    (keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ringkas


def utama(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="perintah", required=True)
    b = sub.add_parser("buat")
    b.add_argument("jumlah", type=int)
    b.add_argument("keluar", type=Path)
    b.add_argument("--benih", type=int, default=79)
    b.add_argument("--acuan", type=Path, help="acuan.json dari `acuan`: letak, ukuran, terang, dan kabur ditiru dari foto kamera")
    u = sub.add_parser("acuan", help="ukur ANGKA dari foto kamera sungguhan (tanpa membuka gambar): acuan.json")
    u.add_argument("csv", type=Path, help="hasil-baca.csv (kolom berkas, x1, y1, x2, y2)")
    u.add_argument("sumber", type=Path, help="folder atau zip foto yang sama dengan CSV")
    u.add_argument("keluar", type=Path)
    t = sub.add_parser("tempel", help="tempel plat modif buatan di foto sungguhan, menutup plat aslinya")
    t.add_argument("csv", type=Path)
    t.add_argument("sumber", type=Path)
    t.add_argument("keluar", type=Path)
    t.add_argument("--benih", type=int, default=79)
    t.add_argument("--ulang", type=int, default=1, help="berapa plat buatan berbeda per foto")
    c = sub.add_parser("csv-fpo", help="tulis ulang fpo-latih.csv dan fpo-validasi.csv dari label.csv yang sudah ada")
    c.add_argument("keluar", type=Path)
    a = p.parse_args(argv)
    try:
        if a.perintah == "acuan":
            print(json.dumps(ukur_acuan(a.csv, a.sumber, a.keluar), indent=2, ensure_ascii=False))
            return 0
        if a.perintah == "tempel":
            print(json.dumps(tempel(a.csv, a.sumber, a.keluar, a.benih, a.ulang), indent=2, ensure_ascii=False))
            return 0
    except ud.bl.GalatAlat as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return e.kode
    except OSError as e:  # jalur berkas bisa memuat nama berplat: hanya jenis galatnya
        print(f"GAGAL: galat berkas ({type(e).__name__})", file=sys.stderr)
        return 3
    if a.perintah == "csv-fpo":
        print(json.dumps(tulis_csv_fpo(a.keluar), ensure_ascii=False))
        return 0
    if a.jumlah < 1:
        print("GAGAL: jumlah harus 1 atau lebih", file=sys.stderr)
        return 2
    try:
        hasil = buat(a.jumlah, a.keluar, a.benih, a.acuan)
    except ud.bl.GalatAlat as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return e.kode
    print(json.dumps(hasil, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(utama())
