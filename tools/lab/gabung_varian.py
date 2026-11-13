"""Varian penggabungan bacaan per kedatangan (Rencana 23 Bagian B, K40), dinilai dari bacaan.jsonl tanpa menjalankan model lagi.

- V0: rantai.gabung apa adanya: teks utuh dengan suara terbanyak.
- V1 tajam: bacaan diurutkan menurut ketajaman (varian Laplacian potongan); separuh yang paling tajam dipakai (minimal
  rantai.MIN_SETUJU, atau semua bila lebih sedikit), lalu rantai.gabung.
- V2 per huruf: bacaan sesuai pola dikelompokkan menurut panjang teksnya; kelompok terbanyak dipakai (seri: jumlah yakin_baca);
  tiap posisi mengambil huruf dengan suara terbanyak (seri: jumlah yakin_baca). "Yakin" bila tiap posisi didukung minimal
  MIN_SETUJU bacaan dan minimal BAGIAN_SETUJU dari kelompok itu, dan teks hasilnya sesuai pola plat.
- V3: V1 lalu V2.

nilai: label dari lembar owner (baris yang tidak disebut bukan plat, buram, atau salah = bacaan benar). Hitungan saja; teks plat
tidak pernah ditulis ke layar maupun ke berkas keluaran.

terapkan: hasil rantai disalin ke folder baru dengan teks dan status menurut satu varian (kedatangan dan potongan sama), supaya
lembar_rantai.py membuat lembar yang sama barisnya dan label lama bisa dipakai ulang.

  terapkan: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/gabung_varian.py terapkan /kerja/data/keluaran/rantai-uji-fase1-r23b /kerja/data/keluaran/rantai-uji-fase1-r23b-v1 --varian V1
  nilai: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/gabung_varian.py nilai /kerja/data/keluaran/rantai-latih-fase1-r23b/bacaan.jsonl /kerja/data/keluaran/lembar-latih-fase1-r21/lembar-rantai.json /kerja/data/keluaran/lembar-latih-fase1-r21/varian-gabung.json --bukan-plat <n,...> --buram <n,...> --salah <n,...>
"""
import argparse
import json
import math
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lembar_rantai import nomor_baris  # noqa: E402
from plat import urai  # noqa: E402
from rantai import BAGIAN_SETUJU, MIN_SETUJU, gabung  # noqa: E402

VARIAN = ("V0", "V1", "V2", "V3")


def _tampak(bacaan):
    return [{"teks": x[1], "yakin_baca": x[2]} for x in bacaan]


def _tajam(bacaan):
    if len(bacaan) <= MIN_SETUJU:
        return bacaan
    k = max(MIN_SETUJU, math.ceil(len(bacaan) / 2))
    return sorted(bacaan, key=lambda x: -x[3])[:k]


def _per_huruf(bacaan):
    sah = [(urai(x[1]).teks, x[2]) for x in bacaan if urai(x[1])]
    if not sah:
        return {"teks": "", "status": "ragu"}
    per_panjang, yakin_panjang = Counter(), Counter()
    for teks, yakin in sah:
        per_panjang[len(teks)] += 1
        yakin_panjang[len(teks)] += yakin
    panjang = max(per_panjang, key=lambda n: (per_panjang[n], yakin_panjang[n]))
    kelompok = [(t, y) for t, y in sah if len(t) == panjang]
    huruf, dukungan = [], []
    for i in range(panjang):
        suara, bobot = Counter(), Counter()
        for teks, yakin in kelompok:
            suara[teks[i]] += 1
            bobot[teks[i]] += yakin
        pilih = max(suara, key=lambda c: (suara[c], bobot[c]))
        huruf.append(pilih)
        dukungan.append(suara[pilih])
    hasil = urai("".join(huruf))
    if hasil is None:
        return {"teks": "", "status": "ragu"}
    yakin = min(dukungan) >= MIN_SETUJU and min(dukungan) >= BAGIAN_SETUJU * len(kelompok)
    return {"teks": hasil.teks, "status": "yakin" if yakin else "ragu"}


def varian(nama, bacaan):
    """bacaan: [[gambar, teks, yakin_baca, ketajaman, tinggi], ...] satu kedatangan -> {"teks", "status"}."""
    if nama == "V0":
        g = gabung(_tampak(bacaan))
        return {"teks": g["teks"], "status": g["status"]}
    if nama == "V1":
        g = gabung(_tampak(_tajam(bacaan)))
        return {"teks": g["teks"], "status": g["status"]}
    if nama == "V2":
        return _per_huruf(bacaan)
    if nama == "V3":
        return _per_huruf(_tajam(bacaan))
    raise ValueError(f"varian tidak dikenal: {nama}")


def nilai(bacaan, lembar, bukan_plat, buram, salah):
    """bacaan: {(video, kedatangan): [...]}; label dari nomor baris lembar. Kembali: hitungan per varian."""
    hasil = {}
    for nama in VARIAN:
        h = {"benar": 0, "benar_yakin": 0, "benar_ragu": 0, "berubah": 0, "yakin_bukan_plat": 0, "yakin_buram": 0, "yakin_salah": 0,
             "salah_berubah": 0}
        for baris in lembar["baris"]:
            v = varian(nama, bacaan[(baris["video"], baris["kedatangan"])])
            if baris["nomor"] in bukan_plat:
                h["yakin_bukan_plat"] += int(v["status"] == "yakin")
            elif baris["nomor"] in buram:
                h["yakin_buram"] += int(v["status"] == "yakin")
            elif baris["nomor"] in salah:
                # Teks lama sudah pasti salah. Teks yang berubah belum diketahui benar-salahnya: dihitung terpisah, dan bila varian
                # itu terpilih, baris itu diperiksa owner.
                if v["teks"] != (baris["teks"] or ""):
                    h["salah_berubah"] += 1
                else:
                    h["yakin_salah"] += int(v["status"] == "yakin")
            else:
                h["benar"] += 1
                if v["teks"] != (baris["teks"] or ""):
                    h["berubah"] += 1
                else:
                    h["benar_yakin" if v["status"] == "yakin" else "benar_ragu"] += 1
        hasil[nama] = h
    return hasil


def _yakin_lain(h):
    return h["yakin_bukan_plat"] + h["yakin_buram"] + h["yakin_salah"]


def pilih(hasil):
    """Rencana 23 Task 6 Step 3: benar-yakin terbanyak, asal yakin di bukan plat, buram, dan salah tidak bertambah dibanding V0 dan
    tidak ada bacaan benar yang berubah; seri dengan V0: V0 tetap."""
    dasar = hasil["V0"]
    calon = [n for n in VARIAN if n == "V0" or (hasil[n]["berubah"] == 0 and _yakin_lain(hasil[n]) <= _yakin_lain(dasar))]
    terbaik = max(calon, key=lambda n: (hasil[n]["benar_yakin"], n == "V0"))
    return "V0" if hasil[terbaik]["benar_yakin"] == dasar["benar_yakin"] else terbaik


def _muat_bacaan(jalur):
    bacaan = {}
    for baris in Path(jalur).read_text().splitlines():
        if baris.strip():
            x = json.loads(baris)
            bacaan[(x["video"], x["kedatangan"])] = x["bacaan"]
    return bacaan


def terapkan(folder_rantai, keluar, nama):
    """Hasil rantai (kedatangan.jsonl, bacaan.jsonl, potongan/) -> folder baru dengan teks dan status menurut varian `nama`, untuk
    lembar_rantai.py. Kedatangan, urutan, dan potongan tidak berubah. Kembali: hitungan saja."""
    asal, keluar = Path(folder_rantai), Path(keluar)
    bacaan = _muat_bacaan(asal / "bacaan.jsonl")
    keluar.mkdir(parents=True, exist_ok=True)
    shutil.copytree(asal / "potongan", keluar / "potongan", dirs_exist_ok=True)
    teks_berubah = status_berubah = jumlah = 0
    with open(keluar / "kedatangan.jsonl", "w") as berkas:
        for baris in (asal / "kedatangan.jsonl").read_text().splitlines():
            if not baris.strip():
                continue
            k = json.loads(baris)
            v = varian(nama, bacaan[(k["video"], k["nomor"])])
            teks_berubah += int(v["teks"] != k["teks"])
            status_berubah += int(v["teks"] == k["teks"] and v["status"] != k["status"])
            berkas.write(json.dumps({**k, "teks": v["teks"], "status": v["status"]}) + "\n")
            jumlah += 1
    ringkas = {"varian": nama, "kedatangan": jumlah, "teks_berubah": teks_berubah, "status_berubah": status_berubah}
    (keluar / "ringkasan-varian.json").write_text(json.dumps(ringkas))
    return ringkas


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Varian penggabungan bacaan per kedatangan (Rencana 23 Bagian B).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    n = perintah.add_parser("nilai")
    for nama in ("bacaan", "lembar", "keluar"):
        n.add_argument(nama)
    for nama in ("bukan-plat", "buram", "salah"):
        n.add_argument(f"--{nama}", type=nomor_baris, default=[])
    t = perintah.add_parser("terapkan")
    t.add_argument("folder_rantai")
    t.add_argument("keluar")
    t.add_argument("--varian", choices=VARIAN, required=True)
    p = pengurai.parse_args(argumen)
    if p.perintah == "terapkan":
        try:
            r = terapkan(p.folder_rantai, p.keluar, p.varian)
        except (OSError, ValueError, KeyError) as galat:
            print(f"GAGAL: {type(galat).__name__}")
            return 1
        print(f"{r['varian']}: {r['kedatangan']} kedatangan; teks berubah {r['teks_berubah']}, status berubah {r['status_berubah']}")
        return 0
    try:
        bacaan = _muat_bacaan(p.bacaan)
        lembar = json.loads(Path(p.lembar).read_text())
        asing = sorted((set(p.bukan_plat) | set(p.buram) | set(p.salah)) - {x["nomor"] for x in lembar["baris"]})
        if asing:
            raise ValueError(f"nomor baris {asing} tidak ada di lembar")
        hasil = nilai(bacaan, lembar, set(p.bukan_plat), set(p.buram), set(p.salah))
        terpilih = pilih(hasil)
        Path(p.keluar).write_text(json.dumps({"varian": hasil, "terpilih": terpilih}, indent=1))
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "baris" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{'varian':<7} {'benar':>6} {'benar-yakin':>12} {'benar-ragu':>11} {'berubah':>8} {'yakin bukan/buram/salah':>24} "
          f"{'salah berubah':>14}")
    for nama, h in hasil.items():
        print(f"{nama:<7} {h['benar']:>6} {h['benar_yakin']:>12} {h['benar_ragu']:>11} {h['berubah']:>8} "
              f"{h['yakin_bukan_plat']:>10}/{h['yakin_buram']}/{h['yakin_salah']} {h['salah_berubah']:>14}")
    print(f"terpilih: {terpilih}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
