"""Pembaca tahan geser (Rencana 26, K51): tiap plat dibaca dari beberapa potongan yang sedikit diperlebar atau digeser, lalu dipungut
suara. Di Rencana 25, di tangkapan uji, 4 plat yang dulu dibaca benar menjadi salah dengan pembaca yang sama, karena kotak pencari
baru bergeser (rasio ukuran 0,98-1,08, IoU median 0,84-0,88 terhadap kotak label).

- potong_geser: kotak diperlebar `margin` dari lebar dan tingginya di tiap sisi, lalu digeser `geser_x` lebar dan `geser_y` tinggi
  kotak; dipotong pada batas gambar. Pada (MARGIN, 0, 0) sama persis dengan rantai.potong.
- VARIAN (ditetapkan sebelum angka dilihat, dari ukuran Rencana 25): v0 = cara lama (1 potongan); v1 = ditambah margin 0 dan 0,12
  (3); v2 = v1 ditambah geser +-0,06 lebar dan +-0,10 tinggi (7). Potongan pertama selalu potongan cara lama.
- pungut_suara: hanya bacaan yang sesuai pola plat (plat.urai) yang dihitung. Teks terbanyak menang; seri dipecah dengan jumlah yakin,
  lalu urutan varian. Tanpa bacaan yang sesuai pola, bacaan potongan pertama dipakai apa adanya (sama dengan cara lama). Yakin =
  rata-rata yakin suara pemenang x (suara pemenang / jumlah potongan yang dibaca).
Tidak memuat model; pembaca diberikan sebagai fungsi baca(potongan) -> (teks, yakin).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

MARGIN = 0.05  # sama dengan rantai.MARGIN (diperiksa uji)
_V1 = [(MARGIN, 0.0, 0.0), (0.0, 0.0, 0.0), (0.12, 0.0, 0.0)]
VARIAN = {
    "v0": [(MARGIN, 0.0, 0.0)],
    "v1": _V1,
    "v2": _V1 + [(MARGIN, 0.06, 0.0), (MARGIN, -0.06, 0.0), (MARGIN, 0.0, 0.10), (MARGIN, 0.0, -0.10)],
}


def potong_geser(gambar, kotak, margin=MARGIN, geser_x=0.0, geser_y=0.0):
    """Potongan kotak (x1, y1, x2, y2, ...) yang diperlebar dan digeser; None bila kosong sesudah dipotong pada batas gambar."""
    tinggi, lebar = gambar.shape[:2]
    x1, y1, x2, y2 = kotak[:4]
    w, h = x2 - x1, y2 - y1
    ox, oy, dx, dy = w * geser_x, h * geser_y, w * margin, h * margin
    a, b = max(0, math.floor(x1 + ox - dx)), max(0, math.floor(y1 + oy - dy))
    c, d = min(lebar, math.ceil(x2 + ox + dx)), min(tinggi, math.ceil(y2 + oy + dy))
    return gambar[b:d, a:c].copy() if c > a and d > b else None


def potongan_varian(gambar, kotak, varian):
    """Potongan per isian VARIAN[varian], potongan kosong dilewati. Potongan pertama (bila ada) adalah potongan cara lama."""
    if varian not in VARIAN:
        raise ValueError(f"varian potongan harus salah satu dari {sorted(VARIAN)}, bukan {varian}")
    return [p for p in (potong_geser(gambar, kotak, *v) for v in VARIAN[varian]) if p is not None]


def pungut_suara(bacaan):
    """[(teks, yakin)] berurutan seperti varian -> (teks, yakin). Lihat keterangan modul."""
    suara = {}
    for i, (teks, yakin) in enumerate(bacaan):
        plat = urai(teks)
        if plat is not None:
            s = suara.setdefault(plat.teks, {"n": 0, "yakin": 0.0, "pertama": i})
            s["n"] += 1
            s["yakin"] += float(yakin)
    if not suara:
        return bacaan[0][0], float(bacaan[0][1])
    teks, s = max(suara.items(), key=lambda x: (x[1]["n"], x[1]["yakin"], -x[1]["pertama"]))
    return teks, s["yakin"] / len(bacaan)  # = rata-rata yakin pemenang x bagian suaranya


def baca_tahan_geser(gambar, kotak, baca, varian):
    """(teks, yakin, potongan cara lama), atau None bila potongan cara lama kosong (kotak itu dilewati, seperti cara lama)."""
    if potong_geser(gambar, kotak, *VARIAN["v0"][0]) is None:
        return None
    potongan = potongan_varian(gambar, kotak, varian)
    teks, yakin = pungut_suara([baca(p) for p in potongan])
    return teks, yakin, potongan[0]
