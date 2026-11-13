"""Penilaian pencari plat (langkah 1, spec 2.1) pada foto utuh berlabel kotak format YOLO (Rencana 12).

- Kebenaran: label YOLO (kelas cx cy w h, ternormalisasi). Baris yang bukan lima angka dilewati (README Roboflow ikut
  berakhiran .txt).
- Cocok: tebakan diurutkan menurut keyakinan; tiap tebakan dipasangkan ke kebenaran yang belum terpakai dengan IoU terbesar,
  minimal IOU_MIN. Kebenaran yang tak terpasangkan = plat terlewat; tebakan yang tak terpasangkan = kotak palsu.
- Ambang keyakinan dipilih pada sisi validasi (F1 terbesar; bila seri, yang terendah, karena plat terlewat berarti gerbang
  tidak membuka), lalu dipakai sekali pada sisi uji.
- Kelompok: gambar terang/gelap (rerata kelabu < AMBANG_GELAP, sama dengan set uji baca huruf) dan plat kecil/besar (tinggi
  kotak < BAGIAN_KECIL x tinggi gambar).
Ringkasan hanya hitungan; nama berkas tidak pernah masuk ringkasan.
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bagi_set_uji import AMBANG_GELAP, SEDIKIT  # noqa: E402
from baca_vlm import wilson  # noqa: E402

IOU_MIN = 0.5
BAGIAN_KECIL = 0.03
CALON_AMBANG = tuple(round(0.05 * i, 2) for i in range(1, 20))
KELOMPOK = ("semua", "terang", "gelap", "kecil", "besar")
AKHIRAN = (".jpg", ".jpeg", ".png")


def baca_label(berkas, lebar, tinggi):
    """Label YOLO -> daftar kotak (x1, y1, x2, y2) dalam piksel."""
    kotak = []
    for baris in Path(berkas).read_text().splitlines():
        bagian = baris.split()
        if len(bagian) != 5:
            continue
        try:
            _, cx, cy, w, h = (float(x) for x in bagian)
        except ValueError:
            continue
        kotak.append(((cx - w / 2) * lebar, (cy - h / 2) * tinggi, (cx + w / 2) * lebar, (cy + h / 2) * tinggi))
    return kotak


def iou(a, b):
    lebar = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    tinggi = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    irisan = lebar * tinggi
    gabung = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - irisan
    return irisan / gabung if gabung > 0 else 0.0


def cocokkan(tebakan, kebenaran, iou_min=IOU_MIN):
    """tebakan: (x1, y1, x2, y2, yakin); kebenaran: (x1, y1, x2, y2). Kembali: (indeks kebenaran yang ditemukan, kotak palsu)."""
    terpakai, palsu = set(), 0
    for t in sorted(tebakan, key=lambda t: -t[4]):
        nilai_iou, i = max(((iou(t[:4], k), i) for i, k in enumerate(kebenaran) if i not in terpakai), default=(0.0, None))
        if i is not None and nilai_iou >= iou_min:
            terpakai.add(i)
        else:
            palsu += 1
    return terpakai, palsu


def ringkas(per_gambar, ambang):
    """per_gambar: daftar {"gelap", "tinggi", "kebenaran", "tebakan"}. Kembali: hitungan per kelompok."""
    hasil = {k: {"plat": 0, "plat_ditemukan": 0, "kotak_palsu": 0, "gambar": 0} for k in KELOMPOK}
    for g in per_gambar:
        ketemu, palsu = cocokkan([t for t in g["tebakan"] if t[4] >= ambang], g["kebenaran"])
        cahaya = "gelap" if g["gelap"] else "terang"
        for k in ("semua", cahaya):
            hasil[k]["gambar"] += 1
            hasil[k]["kotak_palsu"] += palsu
        for i, kotak in enumerate(g["kebenaran"]):
            ukuran = "kecil" if (kotak[3] - kotak[1]) < BAGIAN_KECIL * g["tinggi"] else "besar"
            for k in ("semua", cahaya, ukuran):
                hasil[k]["plat"] += 1
                hasil[k]["plat_ditemukan"] += int(i in ketemu)
    for r in hasil.values():
        rentang = wilson(r["plat_ditemukan"], r["plat"])
        r["rentang_95_ditemukan"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["plat"] < SEDIKIT
    return hasil


def f1(per_gambar, ambang):
    s = ringkas(per_gambar, ambang)["semua"]
    benar, terlewat, palsu = s["plat_ditemukan"], s["plat"] - s["plat_ditemukan"], s["kotak_palsu"]
    return 2 * benar / (2 * benar + palsu + terlewat) if benar else 0.0


def pilih_ambang(per_gambar, calon=CALON_AMBANG):
    """Ambang dengan F1 terbesar pada sisi validasi; bila seri, yang terendah."""
    return max(calon, key=lambda a: (f1(per_gambar, a), -a))


def kumpulkan(folder_sisi, cari):
    """folder_sisi berisi images/ dan labels/ (YOLO Roboflow). cari(gambar_bgr) -> daftar (x1, y1, x2, y2, yakin).
    Kembali: (per_gambar, detik per gambar median, gambar tak terbaca)."""
    per_gambar, detik, tak = [], [], 0
    for berkas in sorted(p for p in (Path(folder_sisi) / "images").iterdir() if p.suffix.lower() in AKHIRAN):
        g = cv2.imread(str(berkas))
        if g is None:
            tak += 1
            continue
        tinggi, lebar = g.shape[:2]
        label = Path(folder_sisi) / "labels" / f"{berkas.stem}.txt"
        mulai = time.perf_counter()
        tebakan = cari(g)
        detik.append(time.perf_counter() - mulai)
        per_gambar.append({"gelap": float(cv2.cvtColor(g, cv2.COLOR_BGR2GRAY).mean()) < AMBANG_GELAP, "tinggi": tinggi,
                           "kebenaran": baca_label(label, lebar, tinggi) if label.exists() else [],
                           "tebakan": [tuple(float(x) for x in t) for t in tebakan]})
    return per_gambar, (round(float(np.median(detik)), 4) if detik else None), tak


def nilai(folder_dataset, cari):
    """Ambang dipilih di valid, lalu dipakai sekali di test. Kembali: ringkasan tanpa nama berkas."""
    val, detik_val, tak_val = kumpulkan(Path(folder_dataset) / "valid", cari)
    ambang = pilih_ambang(val)
    uji, detik_uji, tak_uji = kumpulkan(Path(folder_dataset) / "test", cari)
    return {"ambang": ambang, "iou_min": IOU_MIN, "validasi": ringkas(val, ambang), "uji": ringkas(uji, ambang),
            "detik_per_gambar": {"validasi": detik_val, "uji": detik_uji}, "tak_terbaca": tak_val + tak_uji}
