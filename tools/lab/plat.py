"""Pola nomor polisi Indonesia dan golongan kendaraan menurut nomor urut (spec bagian 2.1 langkah 4).

Dasar: Perpol 7/2021 (docs/peraturan-plat.md). NRKB = kode wilayah (1-2 huruf) + nomor urut (1-9999) + seri huruf
(0-3 huruf). Golongan menurut nomor urut, Lampiran hlm. 93: di luar Polda Metro Jaya 1-1999 mobil penumpang,
2000-6999 sepeda motor, 7000-7999 bus, 8000-8999 mobil barang, 9000-9999 kendaraan khusus; di wilayah Polda Metro Jaya
1-2999 mobil penumpang, 3000-6999 sepeda motor, 7000-7999 bus, 8000-8999 mobil penumpang, 9000-9999 mobil barang dan
kendaraan khusus.

Anggapan agen yang belum diperiksa ke lampiran kode wilayah: kode "B" = wilayah Polda Metro Jaya. Golongan dari nomor
urut adalah taksiran dari peraturan, bukan jenis kendaraan yang terlihat. Plat berpola lain (CD, CC, dinas) belum
dikenali dan dianggap di luar pola.
"""
import re
from dataclasses import dataclass

POLA = re.compile(r"^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$")
KODE_METRO = {"B"}
BATAS_UMUM = ((1999, "mobil"), (6999, "motor"), (7999, "bus"), (8999, "barang"), (9999, "khusus"))
BATAS_METRO = ((2999, "mobil"), (6999, "motor"), (7999, "bus"), (8999, "mobil"), (9999, "barang-khusus"))


@dataclass(frozen=True)
class Plat:
    wilayah: str
    nomor: int
    seri: str

    @property
    def teks(self):
        return f"{self.wilayah}{self.nomor}{self.seri}"


def bersihkan(teks):
    """Huruf besar, hanya huruf dan angka."""
    return re.sub(r"[^A-Z0-9]", "", str(teks).upper())


def urai(teks):
    """Plat bila `teks` (sesudah dibersihkan) sesuai pola nomor polisi Indonesia, selain itu None."""
    cocok = POLA.match(bersihkan(teks))
    if not cocok or cocok[2].startswith("0"):
        return None
    return Plat(cocok[1], int(cocok[2]), cocok[3])


def urai_nama_indo_alpr(nama_berkas):
    """Plat dari nama berkas INDO-ALPR ("<plat>_<urutan>.<akhiran>"), atau None bila bagian platnya tidak sesuai pola."""
    batang = nama_berkas.rsplit(".", 1)[0]
    depan, garis, _ = batang.rpartition("_")
    return urai(depan) if garis else None


def golongan(plat):
    """Jenis kendaraan menurut nomor urut: mobil, motor, bus, barang, khusus, atau barang-khusus (Polda Metro Jaya)."""
    batas = BATAS_METRO if plat.wilayah in KODE_METRO else BATAS_UMUM
    return next(nama for atas, nama in batas if plat.nomor <= atas)


def kelompok_kendaraan(plat):
    """Kelompok K9: "motor" untuk nomor urut sepeda motor, "mobil" untuk selainnya."""
    return "motor" if golongan(plat) == "motor" else "mobil"
