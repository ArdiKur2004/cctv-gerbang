"""Uji jalur DUMMY pembaca plat (K79): bobot publik cct-s-v2 dilatih lanjut dengan plat modif sintetis saja.
Bukan model jualan; hasilnya hanya membuktikan jalur latih -> nilai di laptop ini. Layar hanya hitungan, tanpa teks plat.

  python tools/lab/pembaca_dummy.py siapkan|latih|nilai <repo>   (venv: data/alat-sementara/venv-fpo, ZAMAN=60 LAJU=0.0001)
"""
import csv, json, os, sys
from pathlib import Path

REPO = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO / "tools" / "lab"))
os.environ.setdefault("KERAS_BACKEND", "torch")
os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

import cv2  # noqa: E402
import latih_fpo as L  # noqa: E402
from plat import bersihkan  # noqa: E402

K = REPO / "data" / "keluaran"
OUT = K / "pembaca-dummy-1"
SET = ["plat-modif-1", "plat-modif-acuan-1", "plat-tempel-1"]
AMBANG_YAKIN = 0.8  # sama dengan baca_lokal.py


def siapkan():
    OUT.mkdir(parents=True, exist_ok=True)
    hit = {"bahan": ["plat-modif-sintetis"], "wilayah": True, "gambar": {}, "per_set": {}}
    for sisi, nama in (("latih", "latih"), ("validasi", "validasi")):
        baris, tolak = [], 0
        for s in SET:
            n = 0
            for r in csv.DictReader(open(K / s / f"fpo-{sisi}.csv", encoding="utf-8")):
                t = r["plate_text"]
                if not t or len(t) > L.SLOT_MAKS or any(c not in L.HURUF for c in t):
                    tolak += 1
                    continue
                jalur = os.path.relpath(K / s / r["image_path"], OUT)
                baris.append([jalur, t, L.WILAYAH]); n += 1
            hit["per_set"][f"{s}/{sisi}"] = n
        with open(OUT / f"{nama}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["image_path", "plate_text", "plate_region"]); w.writerows(baris)
        hit["gambar"][nama] = len(baris); hit[f"tolak_{nama}"] = tolak
    # set nilai: (1) plat polos dummy-1 dipotong dari kotaknya, (2) Bardi 'yakin' (label SEMENTARA = tebakan pembaca publik)
    polos = OUT / "nilai-polos"; polos.mkdir(exist_ok=True)
    bp = []
    for r in csv.DictReader(open(K / "dummy-1" / "label.csv", encoding="utf-8")):
        g = cv2.imread(str(K / "dummy-1" / "gambar" / Path(r["berkas"]).name))
        if g is None:
            continue
        x1, y1, x2, y2 = (int(float(r[k])) for k in ("x1", "y1", "x2", "y2"))
        p = polos / f"{int(r['no']):04d}.png"; cv2.imwrite(str(p), g[max(0, y1):y2, max(0, x1):x2])
        bp.append([os.path.relpath(p, OUT), bersihkan(r["teks"]), r["kondisi"]])
    with open(OUT / "nilai-polos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["image_path", "plate_text", "kondisi"]); w.writerows(bp)
    bb = []
    bardi = REPO / "data" / "cctv bardi"
    for r in csv.DictReader(open(bardi / "hasil-baca.csv", encoding="utf-8-sig"), delimiter=";"):
        if r["status"] == "yakin" and r["teks"].strip():
            p = bardi / "potongan" / Path(r["potongan"]).name
            bb.append([os.path.relpath(p, OUT), bersihkan(r["teks"]), r["tipe"]])
    with open(OUT / "nilai-bardi-yakin.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["image_path", "plate_text", "kondisi"]); w.writerows(bb)
    hit["nilai"] = {"polos": len(bp), "bardi_yakin": len(bb)}
    (OUT / "siapkan.json").write_text(json.dumps(hit, indent=1))
    print(json.dumps(hit))


def latih(zaman, laju):
    jalur = L.jalur_terkunci(REPO / "data" / "unduhan")
    L.siapkan_torch()
    sama, semua = L.bobot_utuh(jalur)
    if sama != semua:
        raise L.ModelDitolak(f"bobot terbitan tidak termuat utuh: {sama}/{semua}")
    lat = L._jalankan_latih(OUT, jalur["model"], jalur["plat"], jalur["keras"], zaman, L.BENIH, L.UKURAN_ANGKATAN, laju=laju)
    lat["bobot_termuat"] = f"{sama}/{semua}"
    meta = {"nama": "pembaca-dummy-1", "tujuan": "uji-jalur", "bahan": ["plat-modif-sintetis", "bobot-fast-plate-ocr"],
            "keterangan": "cct-s-v2-global publik dilatih lanjut dengan plat modif sintetis saja (K79). BUKAN untuk rantai.",
            "sha256_mesin": L.sha256_berkas(OUT / "mesin.keras"), "sha256_bobot_awal": L.sha256_berkas(jalur["keras"]),
            "latihan": lat}
    (OUT / "mesin.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(lat))


def nilai_satu(baca, berkas_csv):
    folder = os.path.dirname(os.path.realpath(berkas_csv))
    h = {"gambar": 0, "benar": 0, "yakin": 0, "yakin_salah": 0, "per_kondisi": {}}
    for r in csv.DictReader(open(berkas_csv, encoding="utf-8")):
        g = cv2.imread(folder + os.sep + r["image_path"])
        teks, yk = baca.dengan_yakin(g) if g is not None else ("", 0.0)
        b = int(bersihkan(teks) == r["plate_text"]); y = int(yk >= AMBANG_YAKIN)
        h["gambar"] += 1; h["benar"] += b; h["yakin"] += y; h["yakin_salah"] += int(y and not b)
        kk = r.get("kondisi") or Path(r["image_path"]).parts[1]
        d = h["per_kondisi"].setdefault(kk, {"gambar": 0, "benar": 0}); d["gambar"] += 1; d["benar"] += b
    return h


def nilai():
    jalur = L.jalur_terkunci(REPO / "data" / "unduhan")
    hasil = {}
    for nama, keras in (("publik", jalur["keras"]), ("dummy", OUT / "mesin.keras")):
        baca = L.PembacaKeras(keras, jalur["plat"])
        hasil[nama] = {s: nilai_satu(baca, OUT / f"{c}.csv") for s, c in
                       (("validasi_sintetis", "validasi"), ("polos", "nilai-polos"), ("bardi_yakin", "nilai-bardi-yakin"))}
    (OUT / "nilai.json").write_text(json.dumps(hasil, indent=1))
    for s in ("validasi_sintetis", "polos", "bardi_yakin"):
        a, b = hasil["publik"][s], hasil["dummy"][s]
        print(f"{s:<18} publik {a['benar']}/{a['gambar']} (yakin-salah {a['yakin_salah']}/{a['yakin']})  ->  "
              f"dummy {b['benar']}/{b['gambar']} (yakin-salah {b['yakin_salah']}/{b['yakin']})")


if __name__ == "__main__":
    {"siapkan": siapkan, "latih": lambda: latih(int(os.environ.get("ZAMAN", 60)), float(os.environ.get("LAJU", 1e-4))),
     "nilai": nilai}[sys.argv[1]]()
