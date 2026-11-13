"""Saringan letak plat di dalam kendaraan (Rencana 21, K39 langkah 2: tampak depan atau belakang).

Usulan owner (K39): kendaraan, lalu tampak depan atau belakang, lalu plat di area kendaraan itu. Plat mobil dan motor terlihat di
bagian bawah-tengah kendaraan yang tampak dari depan atau belakang. Benda mirip plat di dalam kotak kendaraan (lampu, stiker,
bagian motor dari atas atau samping) biasanya tidak.
- ciri: tengah plat relatif terhadap kotak kendaraannya (rx, ry; 0..1), rasio lebar/tinggi plat, dan rasio lebar/tinggi
  kendaraan (pengganti "tampak": dari depan atau belakang kendaraan lebih ramping daripada dari samping).
- ATURAN: 24 gabungan syarat yang ditetapkan di Rencana 21 SEBELUM label dilihat (ry minimal 0,4 atau 0,6; |rx - 0,5| paling
  banyak 0,3; rasio plat 1-6; tampak per jenis RASIO_TAMPAK).
- nilai_aturan: satuannya kedatangan berlabel di lembar latih; sebuah kedatangan lolos bila minimal MIN_TAMPAK penampakannya
  lolos, sama seperti rantai.
- pilih_aturan: minimal MIN_BAGIAN_PLAT kedatangan plat lolos; lalu bukan plat lolos tersedikit; lalu syarat tersedikit; lalu nama.
Layar hanya hitungan dan nama aturan.

  banding: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/letak.py banding /kerja/data/keluaran/rantai-latih-fase1-r21/penampakan.jsonl /kerja/data/keluaran/lembar-latih-fase1-r21/lembar-rantai.json /kerja/data/keluaran/lembar-latih-fase1-r21/banding-letak.json --bukan-plat <n,...>
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lembar_rantai import nomor_baris  # noqa: E402

RASIO_TAMPAK = {"mobil": 1.8, "truk": 1.8, "bus": 1.8, "motor": 1.2}  # lebar/tinggi kendaraan paling banyak, tampak depan/belakang
RASIO_PLAT = (1.0, 6.0)
RX_JARAK = 0.3
RY_MIN = (None, 0.4, 0.6)
MIN_BAGIAN_PLAT = 0.9


def ciri(plat, kendaraan):
    """plat (x1, y1, x2, y2), kendaraan [x1, y1, x2, y2, jenis] atau None -> ciri letak."""
    lebar, tinggi = plat[2] - plat[0], plat[3] - plat[1]
    hasil = {"rasio_plat": lebar / tinggi if tinggi > 0 else None, "rx": None, "ry": None, "rasio_kendaraan": None, "jenis": None}
    if kendaraan:
        kl, kt = kendaraan[2] - kendaraan[0], kendaraan[3] - kendaraan[1]
        if kl > 0 and kt > 0:
            hasil.update(rx=((plat[0] + plat[2]) / 2 - kendaraan[0]) / kl, ry=((plat[1] + plat[3]) / 2 - kendaraan[1]) / kt,
                         rasio_kendaraan=kl / kt, jenis=kendaraan[4])
    return hasil


def _aturan():
    hasil = {}
    for ry, rx, rp, tampak in itertools.product(RY_MIN, (False, True), (False, True), (False, True)):
        bagian = ([f"ry{ry}"] if ry else []) + (["rx0.3"] if rx else []) + (["rp"] if rp else []) + (["tampak"] if tampak else [])
        hasil["_".join(bagian) or "tanpa"] = {"ry_min": ry, "rx_jarak": RX_JARAK if rx else None,
                                              "rasio_plat": RASIO_PLAT if rp else None, "tampak": tampak, "syarat": len(bagian)}
    return hasil


ATURAN = _aturan()


def lolos(c, aturan):
    """Semua syarat aktif terpenuhi. Syarat yang butuh kendaraan gagal bila kendaraannya tidak ada."""
    butuh_kendaraan = aturan["ry_min"] is not None or aturan["rx_jarak"] is not None or aturan["tampak"]
    if butuh_kendaraan and c["ry"] is None:
        return False
    if aturan["ry_min"] is not None and c["ry"] < aturan["ry_min"]:
        return False
    if aturan["rx_jarak"] is not None and abs(c["rx"] - 0.5) > aturan["rx_jarak"]:
        return False
    if aturan["rasio_plat"] is not None and (c["rasio_plat"] is None
                                            or not aturan["rasio_plat"][0] <= c["rasio_plat"] <= aturan["rasio_plat"][1]):
        return False
    if aturan["tampak"] and (c["jenis"] not in RASIO_TAMPAK or c["rasio_kendaraan"] > RASIO_TAMPAK[c["jenis"]]):
        return False
    return True


def saring_letak(kotak, nama):
    """Kotak plat dari tahap kendaraan (x1, y1, x2, y2, yakin, jenis, kotak kendaraan) yang tidak lolos ATURAN[nama] dibuang.
    Kotak tanpa kendaraan hanya lolos aturan yang tidak butuh kendaraan. Kembali: (kotak yang lolos, jumlah yang dibuang)."""
    aturan = ATURAN[nama]
    hasil = [k for k in kotak if lolos(ciri(k[:4], [*k[6], k[5]] if len(k) > 6 else None), aturan)]
    return hasil, len(kotak) - len(hasil)


def nilai_aturan(penampakan, lembar, bukan_plat, aturan):
    """Hitungan satu aturan atas kedatangan berlabel di lembar latih (baris yang tidak disebut bukan plat dihitung plat)."""
    from rantai import MIN_TAMPAK  # di dalam fungsi: rantai sendiri mengimpor modul ini

    per_kedatangan = {(t["video"], t["kedatangan"]): t for t in penampakan if t.get("kedatangan") is not None}
    h = {"plat": 0, "plat_lolos": 0, "bukan": 0, "bukan_lolos": 0, "bukan_yakin": 0, "bukan_yakin_lolos": 0}
    for b in lembar["baris"]:
        t = per_kedatangan[(b["video"], b["kedatangan"])]
        kendaraan = t.get("kendaraan") or [None] * len(t["tampak"])
        lewat = sum(lolos(ciri(p[1:5], k), aturan) for p, k in zip(t["tampak"], kendaraan)) >= MIN_TAMPAK
        if b["nomor"] in bukan_plat:
            h["bukan"] += 1
            h["bukan_lolos"] += int(lewat)
            if b.get("status") == "yakin":
                h["bukan_yakin"] += 1
                h["bukan_yakin_lolos"] += int(lewat)
        else:
            h["plat"] += 1
            h["plat_lolos"] += int(lewat)
    return h


def pilih_aturan(hasil):
    """Aturan memilih Rencana 21. hasil: daftar dict dengan nama, syarat, plat, plat_lolos, bukan_lolos."""
    calon = [h for h in hasil if h["plat_lolos"] * 10 >= h["plat"] * round(MIN_BAGIAN_PLAT * 10)]
    return min(calon, key=lambda h: (h["bukan_lolos"], h["syarat"], h["nama"]))


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Saringan letak plat di dalam kendaraan (Rencana 21, K39 langkah 2).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("banding")
    for nama in ("penampakan", "lembar", "keluar"):
        b.add_argument(nama)
    b.add_argument("--bukan-plat", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        penampakan = [json.loads(x) for x in Path(p.penampakan).read_text().splitlines() if x.strip()]
        lembar = json.loads(Path(p.lembar).read_text())
        asing = sorted(set(p.bukan_plat) - {x["nomor"] for x in lembar["baris"]})
        if asing:
            raise ValueError(f"nomor baris bukan plat {asing} tidak ada di lembar")
        hasil = [{"nama": nama, "syarat": a["syarat"], **nilai_aturan(penampakan, lembar, set(p.bukan_plat), a)}
                 for nama, a in ATURAN.items()]
        terpilih = pilih_aturan(hasil)
        Path(p.keluar).write_text(json.dumps({"min_bagian_plat": MIN_BAGIAN_PLAT, "aturan": hasil, "terpilih": terpilih}, indent=1))
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "baris" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{'aturan':<26} {'plat':>9} {'bukan':>9} {'bukan yakin':>11}")
    for h in sorted(hasil, key=lambda h: (h["syarat"], h["nama"])):
        print(f"{h['nama']:<26} {h['plat_lolos']:>4}/{h['plat']:<4} {h['bukan_lolos']:>4}/{h['bukan']:<4} "
              f"{h['bukan_yakin_lolos']:>5}/{h['bukan_yakin']}")
    print(f"terpilih: {terpilih['nama']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
