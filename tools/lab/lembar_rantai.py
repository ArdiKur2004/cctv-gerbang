"""Lembar rantai utuh untuk diperiksa OWNER (K32) dan penilaian dari jawabannya (Rencana 14).

Lembar memuat plat yang terbaca, jadi agen TIDAK PERNAH membukanya (CLAUDE.md §7). Tiap baris: nomor, potongan plat terbesar
satu kedatangan, dan bacaan gabungan mesin ("-" bila tidak ada bacaan yang sesuai pola). Owner menyebut nomor baris untuk
empat jenis saja:
- salah: bacaan tidak sama dengan plat di potongan;
- tak terbaca: plat di potongan tidak bisa dibaca manusia (tidak dinilai);
- bukan plat: potongan tidak berisi plat (tidak dinilai);
- motor: kendaraannya sepeda motor.
Baris yang tidak disebut: bacaan benar, mobil. Baris "-" yang tidak disebut tak terbaca atau bukan plat dihitung salah.

Bila kedatangan lebih dari MAKS_BARIS, baris dipilih tetap (bukan acak): per video diurutkan menurut SHA-256 "<video>/<nomor>",
lalu diambil bergiliran antarvideo sampai MAKS_BARIS.

Kelompok: kategori video dari manifes (siang, malam, remang, tak-jelas, campuran) x mobil/motor dari jawaban owner. Per
kelompok: benar-yakin (gerbang membuka bila platnya terdaftar), benar-ragu dan salah-ragu (tidak membuka: gagal-buka bila
terdaftar), salah-yakin (bacaan salah yang yakin: bahaya buka-salah bila bacaan salah itu kebetulan terdaftar).

  lembar: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_rantai.py lembar /kerja/data/keluaran/rantai-video /kerja/data/keluaran/lembar-rantai
  nilai:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_rantai.py nilai /kerja/data/keluaran/lembar-rantai/lembar-rantai.json /kerja/data/keluaran/lembar-rantai/nilai.json --salah <n,...> --tak-terbaca <n,...> --bukan-plat <n,...> --motor <n,...>
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import wilson  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from bagi_set_uji import SEDIKIT  # noqa: E402
from lembar_contoh import PER_LEMBAR, baris  # noqa: E402

MAKS_BARIS = 120


def pilih_baris(kedatangan, maks=MAKS_BARIS, urut="sha"):
    """urut "sha": tetap dan bergiliran antarvideo (untuk mengukur). urut "keyakinan": keyakinan kotak tertinggi lebih dulu
    (untuk melabeli bahan latih: benda paling mengecoh dan plat paling jelas ikut terperiksa; Rencana 19)."""
    if urut == "keyakinan":
        return sorted(kedatangan, key=lambda k: (-k.get("yakin_kotak", 0.0), k["video"], k["nomor"]))[:maks]
    per_video = {}
    for k in kedatangan:
        per_video.setdefault(k["video"], []).append(k)
    antre = [sorted(d, key=lambda k: hashlib.sha256(f"{k['video']}/{k['nomor']}".encode()).hexdigest())
             for _, d in sorted(per_video.items())]
    terpilih = []
    while len(terpilih) < maks and any(antre):
        for d in antre:
            if d and len(terpilih) < maks:
                terpilih.append(d.pop(0))
    return terpilih


def buat_lembar(folder_rantai, keluar, maks=MAKS_BARIS, urut="sha"):
    folder = Path(folder_rantai)
    kedatangan = [json.loads(b) for b in (folder / "kedatangan.jsonl").read_text().splitlines() if b.strip()]
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    barisan, isi = [], []
    for nomor, k in enumerate(pilih_baris(kedatangan, maks, urut), 1):
        barisan.append(baris(nomor, cv2.imread(str(folder / "potongan" / k["potongan"])), k["teks"] or "-"))
        isi.append({"nomor": nomor, "video": k["video"], "kedatangan": k["nomor"], "kategori": k["kategori"],
                    "status": k["status"], "teks": k["teks"]})
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-rantai-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-rantai.json").write_text(json.dumps({"maks_baris": maks, "urut": urut, "kedatangan": len(kedatangan),
                                                           "halaman": halaman, "baris": isi}, indent=1))
    return {"kedatangan": len(kedatangan), "baris": len(isi), "halaman": len(halaman)}


def nilai(lembar, salah=(), tak_terbaca=(), bukan_plat=(), motor=()):
    """Hitungan per kelompok dari jawaban owner (nomor baris per jenis). Kembali: hitungan saja."""
    semua = {b["nomor"]: b for b in lembar["baris"]}
    sebut = {"salah": set(salah), "tak_terbaca": set(tak_terbaca), "bukan_plat": set(bukan_plat), "motor": set(motor)}
    for nama, nomor in sebut.items():
        asing = nomor - set(semua)
        if asing:
            raise ValueError(f"nomor baris {nama} tidak ada di lembar: {sorted(asing)}")
    for a, b in (("salah", "tak_terbaca"), ("salah", "bukan_plat"), ("tak_terbaca", "bukan_plat"), ("motor", "bukan_plat")):
        dua = sebut[a] & sebut[b]
        if dua:
            raise ValueError(f"baris {sorted(dua)} disebut {a} dan {b} sekaligus")
    hasil = {"baris": len(semua), "tak_terbaca": len(sebut["tak_terbaca"]), "bukan_plat": len(sebut["bukan_plat"]),
             "motor": len(sebut["motor"]), "kelompok": {}}
    for nomor, b in sorted(semua.items()):
        if nomor in sebut["tak_terbaca"] or nomor in sebut["bukan_plat"]:
            continue
        jenis = "motor" if nomor in sebut["motor"] else "mobil"
        benar = nomor not in sebut["salah"] and bool(b["teks"])
        for k in ("semua", f"{b['kategori']}-{jenis}"):
            r = hasil["kelompok"].setdefault(k, {"dinilai": 0, "benar_yakin": 0, "benar_ragu": 0, "salah_ragu": 0, "salah_yakin": 0})
            r["dinilai"] += 1
            r[f"{'benar' if benar else 'salah'}_{b['status']}"] += 1
    for r in hasil["kelompok"].values():
        rentang = wilson(r["benar_yakin"], r["dinilai"])
        r["rentang_95_benar_yakin"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["dinilai"] < SEDIKIT
    return hasil


def nomor_baris(teks):
    return [int(x) for x in teks.split(",") if x.strip()] if teks else []


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Lembar rantai utuh untuk owner dan penilaiannya (Rencana 14, K32).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("lembar")
    a.add_argument("folder_rantai")
    a.add_argument("keluar")
    a.add_argument("--maks", type=int, default=MAKS_BARIS)
    a.add_argument("--urut", choices=("sha", "keyakinan"), default="sha")
    b = perintah.add_parser("nilai")
    b.add_argument("lembar")
    b.add_argument("keluar")
    for nama in ("salah", "tak-terbaca", "bukan-plat", "motor"):
        b.add_argument(f"--{nama}", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "lembar":
            r = buat_lembar(p.folder_rantai, p.keluar, p.maks, p.urut)
            print(f"{r['kedatangan']} kedatangan -> {r['baris']} baris di {r['halaman']} lembar. "
                  "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
        else:
            h = nilai(json.loads(Path(p.lembar).read_text()), p.salah, p.tak_terbaca, p.bukan_plat, p.motor)
            Path(p.keluar).write_text(json.dumps(h, indent=1))
            print(f"{h['baris']} baris: tak terbaca {h['tak_terbaca']}, bukan plat {h['bukan_plat']}, motor {h['motor']}")
            for k, r in sorted(h["kelompok"].items()):
                print(f"{k:<16} dinilai {r['dinilai']}: benar-yakin {r['benar_yakin']} (rentang 95% "
                      f"{r['rentang_95_benar_yakin']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}), "
                      f"benar-ragu {r['benar_ragu']}, salah-ragu {r['salah_ragu']}, salah-yakin {r['salah_yakin']}")
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "baris" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
