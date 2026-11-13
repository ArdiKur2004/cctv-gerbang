"""Membagi ulang INDO-ALPR menjadi bahan latih dan set uji per PLAT, bukan per gambar (spec bagian 8.3).

Pembagian dari penerbitnya bocor: diukur 14 Okt, 713 dari 1.462 gambar uji memuat plat yang juga ada di bagian latih.
Di sini semua gambar berplat sama masuk ke satu sisi saja. Satu plat = satu "kedatangan" (taksiran: gambar berplat sama
dianggap kendaraan yang sama; spec mendefinisikan kedatangan dari video, yang tidak ada di dataset ini).

Sisi tiap plat ditentukan dari SHA-256 teks platnya (UJI_DARI_EMPAT dari empat bagian), jadi pembagiannya tetap setiap
kali dijalankan tanpa angka acak. Gambar yang nama berkasnya tidak sesuai pola plat dikecualikan dan dihitung.

Kelompok per kedatangan: "mobil" atau "motor" dari nomor urut (tools/lab/plat.py), dan "terang" atau "gelap" dari terang
rata-rata gambarnya (di bawah AMBANG_GELAP = gelap). Terang-gelap ini taksiran dari potongan plat, BUKAN siang-malam
menurut spec bagian 8.3, yang ditentukan dari langit dan sumber cahaya pada gambar utuh.

Keluaran di folder keluaran:
- pembagian.json: daftar kedatangan per sisi, beserta teks plat dan nama berkas. Memuat nomor plat: tinggal di data/.
- ringkasan.json: hitungan saja, tanpa teks plat atau nama berkas. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/bagi_set_uji.py /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/set-uji-baca
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import golongan, kelompok_kendaraan, urai_nama_indo_alpr  # noqa: E402

AKHIRAN_GAMBAR = {".png", ".jpg", ".jpeg"}
KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
UJI_DARI_EMPAT = 1
AMBANG_GELAP = 60
SEDIKIT = 30  # kelompok dengan kedatangan lebih sedikit dari ini: "terlalu sedikit untuk disimpulkan" (spec 8.3)


def sisi(teks):
    """"uji" untuk kira-kira UJI_DARI_EMPAT dari empat plat, selain itu "latih". Selalu sama untuk teks yang sama."""
    return "uji" if int(hashlib.sha256(teks.encode()).hexdigest()[:8], 16) % 4 < UJI_DARI_EMPAT else "latih"


def terang(jalur):
    """Terang rata-rata 0-255 sesudah gambar dikecilkan menjadi 32x32 kelabu."""
    with Image.open(jalur) as gambar:
        return float(np.asarray(gambar.convert("L").resize((32, 32))).mean())


def kumpulkan(folder):
    """Gambar dari semua subfolder, dikelompokkan per plat. Kembali: (plat -> daftar jalur, jumlah dikecualikan)."""
    per_plat, dikecualikan = defaultdict(list), 0
    for jalur in sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in AKHIRAN_GAMBAR):
        plat = urai_nama_indo_alpr(jalur.name)
        if plat is None:
            dikecualikan += 1
        else:
            per_plat[plat].append(jalur)
    return per_plat, dikecualikan


def utama(folder, keluar):
    try:
        return bagi(Path(folder), Path(keluar))
    except OSError as galat:
        # Pesan bawaan memuat jalur berkas, dan pada INDO-ALPR jalur itu memuat nomor plat: jangan dicetak.
        print(f"GAGAL MEMBACA: {type(galat).__name__} (errno {galat.errno}). Nama berkas tidak dicetak.")
        return 1


def bagi(folder, keluar):
    per_plat, dikecualikan = kumpulkan(folder)
    pembagian = {"latih": [], "uji": []}
    hitung = {s: {k: Counter() for k in KELOMPOK} for s in pembagian}
    golongan_sisi = {s: Counter() for s in pembagian}
    for plat in sorted(per_plat, key=lambda p: p.teks):
        jalur = per_plat[plat]
        cahaya = float(np.mean([terang(j) for j in jalur]))
        kelompok = f"{kelompok_kendaraan(plat)}-{'gelap' if cahaya < AMBANG_GELAP else 'terang'}"
        s = sisi(plat.teks)
        pembagian[s].append({"teks": plat.teks, "golongan": golongan(plat), "kelompok": kelompok,
                             "terang": round(cahaya, 1), "berkas": [j.relative_to(folder).as_posix() for j in jalur]})
        hitung[s][kelompok]["kedatangan"] += 1
        hitung[s][kelompok]["gambar"] += len(jalur)
        golongan_sisi[s][golongan(plat)] += 1
    bocor = len({a["teks"] for a in pembagian["latih"]} & {a["teks"] for a in pembagian["uji"]})
    ringkasan = {
        "sumber": "INDO-ALPR bagian original: train dan test penerbit digabung, lalu dibagi ulang per plat",
        "aturan": {"uji_dari_empat": UJI_DARI_EMPAT, "ambang_gelap": AMBANG_GELAP, "sedikit": SEDIKIT},
        "dikecualikan_tak_sesuai_pola": dikecualikan,
        "plat_di_kedua_sisi": bocor,
        "sisi": {s: {"kedatangan": len(pembagian[s]), "gambar": sum(len(a["berkas"]) for a in pembagian[s]),
                     "per_kelompok": {k: {"kedatangan": hitung[s][k]["kedatangan"], "gambar": hitung[s][k]["gambar"],
                                          "terlalu_sedikit": hitung[s][k]["kedatangan"] < SEDIKIT} for k in KELOMPOK},
                     "per_golongan": dict(sorted(golongan_sisi[s].items()))}
                 for s in pembagian},
    }
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian.json").write_text(json.dumps(pembagian, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for s in ("latih", "uji"):
        r = ringkasan["sisi"][s]
        print(f"{s}: {r['kedatangan']} kedatangan, {r['gambar']} gambar")
        for k in KELOMPOK:
            n = r["per_kelompok"][k]
            catatan = "  (terlalu sedikit untuk disimpulkan)" if n["terlalu_sedikit"] else ""
            print(f"  {k:<13}{n['kedatangan']:>6} kedatangan{n['gambar']:>7} gambar{catatan}")
        print(f"  golongan: {r['per_golongan']}")
    print(f"dikecualikan (nama berkas tak sesuai pola plat): {dikecualikan}")
    print(f"plat di kedua sisi: {bocor}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Pakai: python bagi_set_uji.py <folder-original> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2]))
