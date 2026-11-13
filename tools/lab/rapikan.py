"""Kotak plat dirapikan dengan pencarian kedua (Rencana 27, K54).

Di Rencana 26, dari empat bacaan yang rusak di tangkapan uji, dua kotak pencari C1 jauh lebih besar dari plat (1,15 dan 1,48 kali lebar),
dan satu lebih sempit (0,88). rapikan_kotak memotong gambar di sekitar kotak pertama (diperlebar `konteks` kali lebar dan tinggi kotak di
tiap sisi, dipotong pada batas gambar) dan menjalankan pencari yang sama sekali lagi. Letterbox pencari memperbesar potongan, jadi plat
terlihat lebih besar dan kotaknya lebih rinci. Dari kotak di atas ambang yang tengahnya berada di dalam kotak pertama, dipilih yang yakinnya
terbesar; koordinatnya dikembalikan ke gambar utuh. Unsur kotak pertama yang lain (yakin, jenis, dan kotak kendaraan) dibawa apa adanya,
karena kotak itu diterima dengan yakin itu. Tanpa kotak seperti itu, kotak pertama dipakai. konteks 0 = mati.
Tidak memuat model; pencari diberikan sebagai fungsi cari(gambar) -> [(x1, y1, x2, y2, yakin)].
"""
import math


def rapikan_kotak(gambar, kotak, cari, ambang, konteks):
    """Kotak (x1, y1, x2, y2, yakin, ...) -> kotak yang dirapikan, dengan unsur lain kotak pertama."""
    if konteks < 0:
        raise ValueError(f"konteks rapikan tidak boleh negatif, bukan {konteks}")
    if konteks == 0:
        return kotak
    tinggi, lebar = gambar.shape[:2]
    x1, y1, x2, y2 = kotak[:4]
    w, h = x2 - x1, y2 - y1
    a, b = max(0, math.floor(x1 - konteks * w)), max(0, math.floor(y1 - konteks * h))
    c, d = min(lebar, math.ceil(x2 + konteks * w)), min(tinggi, math.ceil(y2 + konteks * h))
    if c - a < 2 or d - b < 2:
        return kotak
    calon = []
    for k in cari(gambar[b:d, a:c]):
        if k[4] < ambang:
            continue
        u = (float(k[0]) + a, float(k[1]) + b, float(k[2]) + a, float(k[3]) + b)
        cx, cy = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            calon.append((float(k[4]), u))
    if not calon:
        return kotak
    return (*max(calon, key=lambda z: z[0])[1], *kotak[4:])
