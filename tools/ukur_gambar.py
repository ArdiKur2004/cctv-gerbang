"""Mengukur mutu SEKUMPULAN gambar JPG kamera (satu gambar per baris), tanpa mencetak nama berkas (K78).

Nama berkas dan isi gambar bisa memuat plat (CLAUDE.md §4): yang tercetak hanya angka dan nomor urut berkas
(urutan nama). CSV-nya tidak memuat nama, jadi bebas plat. Memakai ukuran yang sama dengan rekam_rtsp.py.

  python tools/ukur_gambar.py <folder> --keluar <folder keluaran> [--daerah x,y,l,t]
"""
import argparse
import csv
import importlib.util
import json
import statistics
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
_spek = importlib.util.spec_from_file_location("rekam_rtsp", AKAR / "tools" / "rekam_rtsp.py")
rr = importlib.util.module_from_spec(_spek)
_spek.loader.exec_module(rr)

KOLOM = ["no", "lebar", "tinggi", "ukuran_kb", "kecerahan", "jenuh_persen", "gelap_persen", "ketajaman", "mode"]


def baca_gambar(av, jalur):
    with av.open(str(jalur)) as wadah:
        for bingkai in wadah.decode(video=0):
            luma = bingkai.to_ndarray(format="gray")
            kecil = bingkai.reformat(width=max(16, bingkai.width // 4), height=max(16, bingkai.height // 4),
                                     format="rgb24").to_ndarray()
            return bingkai.width, bingkai.height, luma, kecil
    raise ValueError("tanpa bingkai")


def persentil(nilai, p):
    s = sorted(nilai)
    return s[min(len(s) - 1, int(p * len(s)))]


def utama(argv=None):
    import av
    av.logging.set_level(av.logging.PANIC)
    p = argparse.ArgumentParser()
    p.add_argument("folder", type=Path)
    p.add_argument("--keluar", type=Path, required=True)
    p.add_argument("--daerah")
    a = p.parse_args(argv)
    try:
        daerah = rr.parse_daerah(a.daerah)
        berkas = sorted(x for x in a.folder.iterdir() if x.is_file() and x.suffix.lower() in (".jpg", ".jpeg"))
        a.keluar.mkdir(parents=True, exist_ok=True)
        baris, gagal = [], {}
        for no, jalur in enumerate(berkas, 1):
            try:
                l, t, luma, kecil = baca_gambar(av, jalur)
                u = rr.ukur_luma(rr.potong(luma, daerah))
                baris.append({"no": no, "lebar": l, "tinggi": t, "ukuran_kb": round(jalur.stat().st_size / 1024, 1),
                              "kecerahan": round(u["kecerahan"], 2), "jenuh_persen": round(u["jenuh"], 3),
                              "gelap_persen": round(u["gelap"], 3), "ketajaman": round(u["ketajaman"], 2),
                              "mode": rr.mode_warna(kecil)})
            except Exception as e:  # pesan PyAV memuat jalur berkas: hanya jenisnya yang dicatat
                gagal[type(e).__name__] = gagal.get(type(e).__name__, 0) + 1
        with open(a.keluar / "ukur-gambar.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=KOLOM)
            w.writeheader()
            w.writerows(baris)
    except OSError as e:
        print(f"GAGAL: galat berkas ({type(e).__name__})", file=sys.stderr)
        return 3
    if not baris:
        print("GAGAL: tidak ada gambar terbaca", gagal, file=sys.stderr)
        return 5
    taj = [b["ketajaman"] for b in baris]
    ter = [b["kecerahan"] for b in baris]
    ringkas = {
        "gambar_dicoba": len(berkas), "terbaca": len(baris), "gagal_per_jenis": gagal,
        "resolusi": {f"{k[0]}x{k[1]}": sum(1 for b in baris if (b["lebar"], b["tinggi"]) == k)
                     for k in sorted({(b["lebar"], b["tinggi"]) for b in baris})},
        "mode": {m: sum(1 for b in baris if b["mode"] == m) for m in ("warna", "ir")},
        "ukuran_kb_median": round(statistics.median(b["ukuran_kb"] for b in baris), 1),
        "ketajaman": {"min": min(taj), "p10": persentil(taj, .1), "median": statistics.median(taj),
                      "p90": persentil(taj, .9), "maks": max(taj)},
        "kecerahan": {"min": min(ter), "p10": persentil(ter, .1), "median": statistics.median(ter),
                      "p90": persentil(ter, .9), "maks": max(ter)},
        "jenuh_lebih_5persen": sum(1 for b in baris if b["jenuh_persen"] > 5),
        "gelap_lebih_50persen": sum(1 for b in baris if b["gelap_persen"] > 50),
    }
    # Apakah ketajaman bergantung pada terang-gelapnya gambar (exposure) atau mode?
    def kelompok(nama, fungsi):
        g = {}
        for b in baris:
            g.setdefault(fungsi(b), []).append(b["ketajaman"])
        return {k: {"n": len(v), "median": round(statistics.median(v), 1)} for k, v in sorted(g.items())}
    ringkas["ketajaman_menurut_kecerahan"] = kelompok("kecerahan", lambda b: "gelap<60" if b["kecerahan"] < 60 else "sedang" if b["kecerahan"] < 150 else "terang>=150")
    ringkas["ketajaman_menurut_mode"] = kelompok("mode", lambda b: b["mode"])
    (a.keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(ringkas, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(utama())
