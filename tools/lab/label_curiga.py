"""Label set uji yang dicurigai salah (K22): plat yang dibaca SAMA oleh dua pembaca berbeda tetapi berbeda dari labelnya.

Per gambar dibandingkan bacaan pembaca A dan B (hasil.jsonl keduanya). Sebuah kedatangan dicurigai bila pada paling
sedikit satu gambarnya kedua pembaca sepakat pada teks yang sesuai pola plat dan tidak sama dengan label. Usulannya teks
yang paling sering disepakati (seri: urutan abjad). Kedatangan yang hanya dibantah satu pembaca, atau dibantah dua
pembaca yang tidak sepakat, TIDAK dicurigai: itu batas cara ini (K22). Bawaannya set uji; --sisi latih untuk bahan latih
(K24).

Bila --periksa (lembar-contoh.json) dan --salah (nomor baris yang labelnya diketahui salah) diberi, cara ini dinilai pada
contoh yang sudah diperiksa owner: berapa label salah yang tertangkap, dan berapa label benar yang ikut dicurigai.

Keluaran: curiga.json (memuat plat; tinggal di data/) dan ringkasan.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/label_curiga.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/baca-vlm/hasil.jsonl /kerja/data/keluaran/baca-fpo/hasil.jsonl /kerja/data/keluaran/label-curiga --periksa /kerja/data/keluaran/lembar-contoh/lembar-contoh.json --salah 19,22,25,35,36,54
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")


def baca_hasil(jalur):
    """berkas -> bacaan bersih, dari hasil.jsonl sebuah pembaca."""
    return {b["berkas"]: b["bacaan"] for b in map(json.loads, Path(jalur).read_text().splitlines())}


def cari(pembagian, bacaan_a, bacaan_b, sisi="uji"):
    curiga = []
    for kedatangan in pembagian[sisi]:
        sepakat, gambar = Counter(), {}
        for berkas in kedatangan["berkas"]:
            a = bacaan_a.get(berkas, "")
            if a and a == bacaan_b.get(berkas, "") and a != kedatangan["teks"] and urai(a) is not None:
                sepakat[a] += 1
                gambar.setdefault(a, berkas)
        if sepakat:
            usulan = min(sepakat, key=lambda t: (-sepakat[t], t))
            curiga.append({"teks": kedatangan["teks"], "usulan": usulan, "kelompok": kedatangan["kelompok"],
                           "berkas": gambar[usulan]})
    return curiga


def nilai_cara(curiga, lembar_contoh, salah):
    dicurigai = {c["teks"] for c in curiga}
    diketahui_salah = [c for c in lembar_contoh["contoh"] if c["nomor"] in salah]
    diketahui_benar = [c for c in lembar_contoh["contoh"] if c["nomor"] not in salah]
    return {"label_salah_diketahui": len(diketahui_salah),
            "tertangkap": sum(c["teks"] in dicurigai for c in diketahui_salah),
            "label_benar_diketahui": len(diketahui_benar),
            "ikut_dicurigai": sum(c["teks"] in dicurigai for c in diketahui_benar)}


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Label set uji yang dicurigai salah (K22).")
    for nama in ("pembagian", "hasil_a", "hasil_b", "keluar"):
        urai_argumen.add_argument(nama)
    urai_argumen.add_argument("--periksa")
    urai_argumen.add_argument("--salah", default="")
    urai_argumen.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    p = urai_argumen.parse_args(argumen)
    pembagian = json.loads(Path(p.pembagian).read_text())
    curiga = cari(pembagian, baca_hasil(p.hasil_a), baca_hasil(p.hasil_b), p.sisi)
    ringkasan = {"aturan": "dua pembaca sepakat pada teks berpola plat yang berbeda dari label (K22)",
                 "sisi": p.sisi, "kedatangan": len(pembagian[p.sisi]), "dicurigai": len(curiga),
                 "per_kelompok": {k: {"kedatangan": sum(x["kelompok"] == k for x in pembagian[p.sisi]),
                                      "dicurigai": sum(c["kelompok"] == k for c in curiga)} for k in KELOMPOK}}
    if p.periksa:
        lembar = json.loads(Path(p.periksa).read_text())
        salah = {int(x) for x in p.salah.split(",") if x.strip()}
        luar = sorted(salah - {c["nomor"] for c in lembar["contoh"]})
        if luar:
            print(f"SALAH PAKAI: baris {luar} tidak ada di lembar contoh")
            return 2
        ringkasan["penilaian_cara"] = nilai_cara(curiga, lembar, salah)
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "curiga.json").write_text(json.dumps(curiga, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    print(f"dicurigai: {len(curiga)} dari {len(pembagian[p.sisi])} kedatangan {p.sisi}")
    for k in KELOMPOK:
        n = ringkasan["per_kelompok"][k]
        print(f"  {k:<13}{n['dicurigai']:>5} dari {n['kedatangan']}")
    if "penilaian_cara" in ringkasan:
        n = ringkasan["penilaian_cara"]
        print(f"pada contoh yang sudah diperiksa owner: tertangkap {n['tertangkap']} dari {n['label_salah_diketahui']} "
              f"label salah; ikut dicurigai {n['ikut_dicurigai']} dari {n['label_benar_diketahui']} label benar")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
