"""Bahan pembaca JUALAN (Rencana 24 Bagian B Task 5): CSV fast-plate-ocr (image_path, plate_text; tanpa kolom wilayah, jadi model
tanpa kepala wilayah) dari tiga bahan BOLEH-PRODUK:
- INDO-ALPR, hanya pembagian["latih"]; inti dan validasi menurut mesin_baca.bagi_validasi (per plat, sama dengan fpo-indo-1);
- tangkapan owner (K44), hanya gambar sisi latih di label.json (halaman_label.terima), hanya plat yang punya teks benar. Potongan
  dibuat dengan rantai.potong dan dinamai nomor gambar; 1 dari BAGIAN_VALIDASI plat menurut SHA-256 masuk validasi;
- plat buatan (plat_buatan.py buat), semuanya masuk latih (bukan bahan memilih calon).
Sisi uji INDO-ALPR dan tangkapan uji tidak pernah dibaca. Keluaran memuat plat: agen tidak membukanya; siapkan.json hitungan saja,
beserta daftar bahan untuk manifes mesin.

Rencana 25 (fpo-indo-1 dilatih lanjut, K50 butir 3): wilayah=True menambah kolom plate_region ("Indonesia"), karena fpo-indo-1
berkepala wilayah dan tanpa kolom itu kepalanya dibuang diam-diam (Rencana 9). ulang_tangkapan=N menulis tiap potongan tangkapan
LATIH N kali, supaya ~100 potongan tidak tenggelam di ~4.000 gambar INDO-ALPR; validasi tidak diulang. uji-tangkapan: potongan
plat berteks sisi UJI (uji-tangkapan.csv), hanya untuk diukur sekali di akhir.

Rencana 30 (pembaca tahan kotak yang kurang pas): rantai=[folder keluaran baca_gambar.py, ...] menambah potongan yang dibuat rantai
sendiri. Untuk tiap plat berteks di gambar sisi latih, baris rantai yang cocok menurut halaman_label.cocokkan (aturan nilai_label)
diambil dan berkas potongannya disalin apa adanya ke potongan/c<i>-<gambar>-<n>.png; teksnya dari label, bukan bacaan rantai. Potongan
yang isinya sama persis dengan potongan lain dari plat yang sama (termasuk potongan kotak label) tidak dimasukkan lagi. Plat latih masuk
latih.csv (diulang), plat validasi validasi.csv, dan per folder rantai validasi-rantai-<i>.csv (lengkap, tanpa melewati kembar), yang
sama dengan rantai itu di plat validasi. geser=True: 6 potongan dari kotak label plat latih dengan isian tahan_geser.VARIAN["v2"] selain
yang pertama (potongan/g<k>-...), sekali saja. validasi_terpisah=True: validasi.csv hanya potongan tangkapan; INDO-ALPR validasi ke
validasi-indo.csv.

  siapkan: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/bahan_pembaca.py siapkan /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json <folder_indo> /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca/peta-berkas.json /kerja/data/keluaran/label-tangkapan/label.json <keluar> [--plat-buatan <folder>] [--wilayah --ulang-tangkapan 5] [--rantai <folder> ... --geser --validasi-terpisah]
  uji-tangkapan: ... bahan_pembaca.py uji-tangkapan /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca/peta-berkas.json /kerja/data/keluaran/label-tangkapan/label.json <keluar> [--wilayah]
"""
import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from halaman_label import baris_rantai, cocokkan  # noqa: E402
from latih_fpo import SLOT_MAKS, WILAYAH, baris_csv  # noqa: E402
from mesin_baca import HURUF, bagi_validasi  # noqa: E402
from rantai import potong  # noqa: E402
from tahan_geser import VARIAN, potong_geser  # noqa: E402

BAGIAN_VALIDASI = 5


def validasi_tangkapan(gambar, nomor):
    """Plat ke-`nomor` di gambar tangkapan `gambar` masuk validasi bila SHA-256 "validasi/<gambar>-<nomor>" habis dibagi 5."""
    return int(hashlib.sha256(f"validasi/{gambar}-{nomor}".encode()).hexdigest()[:8], 16) % BAGIAN_VALIDASI == 0


def _teks_sah(teks):
    if not teks or len(teks) > SLOT_MAKS or any(c not in HURUF for c in teks):
        raise ValueError("label di luar huruf atau panjang yang bisa dibaca model")
    return teks


def _relatif(jalur, folder_csv):
    return os.path.relpath(os.path.realpath(jalur), os.path.realpath(folder_csv))


def _tulis_csv(berkas, isi, wilayah):
    with open(berkas, "w", newline="") as f:
        tulis = csv.writer(f)
        tulis.writerow(["image_path", "plate_text"] + (["plate_region"] if wilayah else []))
        tulis.writerows([*b, WILAYAH] if wilayah else b for b in isi)


def _sidik(gambar):
    """Sidik isi potongan (ukuran dan piksel), untuk melewati potongan kembar dari plat yang sama."""
    return hashlib.sha256(repr(gambar.shape).encode() + gambar.tobytes()).hexdigest()


def siapkan(pembagian, folder_indo, folder_capture, peta_berkas, label_json, keluar, folder_plat_buatan=None,
            latih_hanya_buatan=False, wilayah=False, ulang_tangkapan=1, rantai=(), geser=False, validasi_terpisah=False):
    """Kembali: hitungan per sumber dan daftar bahan (tanpa nomor plat), juga ditulis ke siapkan.json.
    latih_hanya_buatan (tahap 1 calon P3): latih.csv hanya plat buatan; validasi tetap bahan nyata, dan bahan nyata tetap tercatat
    karena ikut memilih zaman terbaik. wilayah dan ulang_tangkapan (Rencana 25), rantai, geser, dan validasi_terpisah (Rencana 30):
    lihat keterangan modul."""
    if latih_hanya_buatan and not folder_plat_buatan:
        raise ValueError("latih hanya plat buatan butuh folder plat buatan")
    if latih_hanya_buatan and (rantai or geser):
        raise ValueError("potongan rantai dan geser adalah bahan latih tangkapan, jadi tidak bisa dipakai dengan latih hanya plat buatan")
    if ulang_tangkapan < 1:
        raise ValueError(f"ulang_tangkapan minimal 1, bukan {ulang_tangkapan}")
    keluar = Path(keluar)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    baris = {"latih": [], "validasi": [], "validasi_indo": []}
    sumber = {"indo_alpr": {}, "tangkapan": {"latih": 0, "validasi": 0}, "plat_buatan": {"latih": 0}, "tak_terbaca": 0,
              "validasi_berteks": 0, "geser": {"latih": 0}, "rantai": []}

    inti, validasi = bagi_validasi(json.loads(Path(pembagian).read_text())["latih"])
    for nama, daftar in (("latih", [] if latih_hanya_buatan else inti), ("validasi", validasi)):
        b, tak = baris_csv(daftar, folder_indo, keluar)
        baris["validasi_indo" if nama == "validasi" and validasi_terpisah else nama] += [x[:2] for x in b]
        sumber["indo_alpr"][nama] = len(b)
        sumber["tak_terbaca"] += tak

    peta = json.loads(Path(peta_berkas).read_text())
    label = json.loads(Path(label_json).read_text())["gambar"]
    folder_rantai = [Path(f) for f in rantai]
    data_rantai = [baris_rantai(f) for f in folder_rantai]
    per_rantai = [{"folder": f"{f.parent.name}/{f.name}", "latih": 0, "validasi": 0, "kembar_dilewati": 0, "validasi_cocok": 0}
                  for f in folder_rantai]
    validasi_rantai = [[] for _ in folder_rantai]
    for g in sorted(label):
        v = label[g]
        calon = [(n, p) for n, p in enumerate(v["plat"], 1)
                 if p["teks"] and (validasi_tangkapan(g, n) or not latih_hanya_buatan)]
        if v["sisi"] != "latih" or not calon:
            continue
        gambar = cv2.imread(str(Path(folder_capture) / peta[g]))
        if gambar is None:
            raise ValueError("ada gambar yang tak bisa dibuka")
        # Per folder rantai: indeks baris yang cocok dengan tiap plat berlabel (semua plat, termasuk yang tanpa teks, seperti
        # nilai_label), lewat jalur berkas karena nomor gambar rantai berbeda dengan nomor di label.
        cocok = []
        for nomor_rantai, tiba in data_rantai:
            b = tiba.get(nomor_rantai.get(peta[g]), [])
            cocok.append((b, cocokkan(v["plat"], b)))
        for n, p in calon:
            s = "validasi" if validasi_tangkapan(g, n) else "latih"
            ulang = ulang_tangkapan if s == "latih" else 1
            teks = _teks_sah(p["teks"])
            sumber["validasi_berteks"] += int(s == "validasi")
            sudah = set()
            potongan = potong(gambar, p["kotak"])
            if potongan is None:
                sumber["tak_terbaca"] += 1
            else:
                nama = f"t-{g}-{n}.png"
                cv2.imwrite(str(keluar / "potongan" / nama), potongan)
                baris[s] += [[f"potongan/{nama}", teks]] * ulang
                sumber["tangkapan"][s] += 1
                sudah.add(_sidik(potongan))
            for i, (b, indeks) in enumerate(cocok):
                if indeks[n - 1] is None:
                    continue
                asal = folder_rantai[i] / "potongan" / b[indeks[n - 1]]["potongan"]
                isi = cv2.imread(str(asal))
                if isi is None:
                    sumber["tak_terbaca"] += 1
                    continue
                nama = f"c{i + 1}-{g}-{n}.png"
                if s == "validasi":
                    shutil.copyfile(asal, keluar / "potongan" / nama)
                    validasi_rantai[i].append([f"potongan/{nama}", teks])
                    per_rantai[i]["validasi_cocok"] += 1
                if _sidik(isi) in sudah:
                    per_rantai[i]["kembar_dilewati"] += 1
                    continue
                sudah.add(_sidik(isi))
                if s == "latih":
                    shutil.copyfile(asal, keluar / "potongan" / nama)
                baris[s] += [[f"potongan/{nama}", teks]] * ulang
                per_rantai[i][s] += 1
            if geser and s == "latih":
                for k, isian in enumerate(VARIAN["v2"][1:], 1):
                    hasil = potong_geser(gambar, p["kotak"], *isian)
                    if hasil is None:
                        continue
                    nama = f"g{k}-{g}-{n}.png"
                    cv2.imwrite(str(keluar / "potongan" / nama), hasil)
                    baris["latih"].append([f"potongan/{nama}", teks])
                    sumber["geser"]["latih"] += 1
    sumber["rantai"] = per_rantai

    if folder_plat_buatan:
        folder = Path(folder_plat_buatan)
        with open(folder / "label.csv", newline="") as berkas:
            for b in csv.DictReader(berkas):
                baris["latih"].append([_relatif(folder / "gambar" / b["berkas"], keluar), _teks_sah(b["teks"])])
                sumber["plat_buatan"]["latih"] += 1

    if not validasi_terpisah:
        del baris["validasi_indo"]
    for nama, isi in baris.items():
        _tulis_csv(keluar / f"{nama.replace('_', '-')}.csv", isi, wilayah)
    for i, isi in enumerate(validasi_rantai, 1):
        _tulis_csv(keluar / f"validasi-rantai-{i}.csv", isi, wilayah)
    bahan = ["dataset-indo-alpr", "tangkapan-owner"] + (["plat-buatan"] if sumber["plat_buatan"]["latih"] else [])
    hasil = {"sumber": sumber, "gambar": {k: len(v) for k, v in baris.items()}, "bahan": bahan,
             "latih_hanya_buatan": bool(latih_hanya_buatan), "wilayah": bool(wilayah), "ulang_tangkapan": ulang_tangkapan,
             "geser": bool(geser), "validasi_terpisah": bool(validasi_terpisah)}
    (keluar / "siapkan.json").write_text(json.dumps(hasil, indent=1))
    return hasil


def siapkan_uji_tangkapan(folder_capture, peta_berkas, label_json, keluar, wilayah=False):
    """Potongan plat berteks sisi UJI tangkapan -> <keluar>/uji-tangkapan.csv dan potongan/u-<kelompok>-<gambar>-<n>.png (kelompok
    di nama supaya mobil dan motor bisa dihitung terpisah). Dipakai sekali untuk mengukur pembaca di akhir (Rencana 25 Task 6
    Step 4). Kembali: hitungan saja."""
    keluar = Path(keluar)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    peta = json.loads(Path(peta_berkas).read_text())
    label = json.loads(Path(label_json).read_text())["gambar"]
    isi, tak, per_kelompok = [], 0, {}
    for g in sorted(label):
        v = label[g]
        calon = [(n, p) for n, p in enumerate(v["plat"], 1) if p["teks"]]
        if v["sisi"] != "uji" or not calon:
            continue
        gambar = cv2.imread(str(Path(folder_capture) / peta[g]))
        if gambar is None:
            raise ValueError("ada gambar yang tak bisa dibuka")
        for n, p in calon:
            potongan = potong(gambar, p["kotak"])
            if potongan is None:
                tak += 1
                continue
            nama = f"u-{v['kelompok']}-{g}-{n}.png"
            cv2.imwrite(str(keluar / "potongan" / nama), potongan)
            isi.append([f"potongan/{nama}", _teks_sah(p["teks"])])
            per_kelompok[v["kelompok"]] = per_kelompok.get(v["kelompok"], 0) + 1
    _tulis_csv(keluar / "uji-tangkapan.csv", isi, wilayah)
    return {"gambar": len(isi), "tak_terbaca": tak, "per_kelompok": per_kelompok}


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Bahan pembaca jualan (Rencana 24 Task 5).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    s = perintah.add_parser("siapkan")
    for nama in ("pembagian", "folder_indo", "folder_capture", "peta_berkas", "label_json", "keluar"):
        s.add_argument(nama)
    s.add_argument("--plat-buatan")
    s.add_argument("--latih-hanya-buatan", action="store_true", help="tahap 1 calon P3 (Rencana 24)")
    s.add_argument("--wilayah", action="store_true", help="kolom plate_region untuk model berkepala wilayah (Rencana 25)")
    s.add_argument("--ulang-tangkapan", type=int, default=1, help="potongan tangkapan latih ditulis N kali (Rencana 25)")
    s.add_argument("--rantai", nargs="+", default=[], help="folder keluaran baca_gambar.py: potongan rantai sendiri (Rencana 30)")
    s.add_argument("--geser", action="store_true", help="6 potongan geser per plat latih (Rencana 30)")
    s.add_argument("--validasi-terpisah", action="store_true", help="INDO-ALPR validasi ke validasi-indo.csv (Rencana 30)")
    u = perintah.add_parser("uji-tangkapan")
    for nama in ("folder_capture", "peta_berkas", "label_json", "keluar"):
        u.add_argument(nama)
    u.add_argument("--wilayah", action="store_true")
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "uji-tangkapan":
            r = siapkan_uji_tangkapan(p.folder_capture, p.peta_berkas, p.label_json, p.keluar, p.wilayah)
            print(f"potongan tangkapan uji {r['gambar']} ({r['per_kelompok']}); tak terbaca {r['tak_terbaca']}")
            return 0
        r = siapkan(p.pembagian, p.folder_indo, p.folder_capture, p.peta_berkas, p.label_json, p.keluar, p.plat_buatan,
                    p.latih_hanya_buatan, p.wilayah, p.ulang_tangkapan, p.rantai, p.geser, p.validasi_terpisah)
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"gambar latih {r['gambar']['latih']}, validasi {r['gambar']['validasi']}; per sumber {json.dumps(r['sumber'])}; "
          f"ulang tangkapan {r['ulang_tangkapan']}; wilayah {r['wilayah']}; bahan {r['bahan']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
