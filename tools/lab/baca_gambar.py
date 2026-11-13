"""Membaca gambar diam (tangkapan layar CCTV dari owner, K44) dengan urutan rantai: kendaraan, plat di dalam potongan kendaraan
(kendaraan.cari_dalam_kendaraan), lalu baca (Rencana 24).

Keluaran di <keluar> berbentuk keluaran rantai, supaya lembar_rantai.py bisa langsung membuat lembar dan menilainya:
- kedatangan.jsonl: satu baris per plat ("video" = nomor gambar g0001, "nomor" = urutan plat di gambar, "kategori" = kelompok
  dari nama subfolder "capture cctv <kelompok>", "status" = "ragu" karena satu gambar tidak bisa dipungut suaranya);
- potongan/: potongan plat bernama g0001-1.png;
- tanpa-plat.json: gambar yang tidak menghasilkan plat (untuk lembar plat terlewat);
- peta-berkas.json: nomor gambar -> jalur berkas asli. Nama berkas bisa memuat nomor plat, jadi peta ini hanya untuk lab, dan nama
  asli tidak ditulis ke berkas lain maupun ke layar;
- ringkasan.json: hitungan saja.
Gambar diurutkan menurut SHA-256 isinya, dan tiap gambar dibagi latih/uji menurut sisi() dari isinya sendiri, sehingga pembagian
tetap bila gambar ditambah atau diganti nama. Berkas memuat plat: agen tidak membukanya (CLAUDE.md §7).

  jalan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/baca_gambar.py jalan /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca /kerja/data/keluaran/pencari-yolox-nano-640-cctv1 /kerja/data/keluaran/kendaraan-yolox-coco /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan --ambang 0.25
  rantai jualan (Rencana 24): ... jalan /kerja/data/capture <keluar> <folder_pencari_jualan> /kerja/data/tidak-dipakai <folder_pembaca_jualan> /kerja/data/tidak-dipakai --ambang <a> --tanpa-kendaraan --pembaca-jualan
  cara pakai kendaraan (Rencana 25): tambah --maks-kendaraan <n> (kendaraan terdekat saja) dan/atau --cadangan-utuh
  pembaca tahan geser (Rencana 26): tambah --varian-potong v1|v2
  rapikan kotak plat (Rencana 27): tambah --rapikan <konteks>, mis. 1.0
  (jangan memakai "-" sebagai pengisi: powershell -File menolaknya sebelum lab.ps1 berjalan)
  lembar-tanpa: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/baca_gambar.py lembar-tanpa /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca /kerja/data/keluaran/lembar-tangkapan-tanpa-plat
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from deteksi import AKHIRAN  # noqa: E402
from kendaraan import MIN_TINGGI, cari_dalam_kendaraan  # noqa: E402
from lembar_bingkai import PER_HALAMAN, kartu  # noqa: E402
from lembar_kendaraan import gambar_bernomor  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from plat import urai  # noqa: E402
from rantai import potong  # noqa: E402
from rapikan import rapikan_kotak  # noqa: E402
from tahan_geser import VARIAN, baca_tahan_geser  # noqa: E402


def sisi(isi):
    """Sisi latih/uji satu gambar dari isinya: huruf heksadesimal pertama SHA-256 "capture/"+isi 0-3 = uji."""
    return "uji" if hashlib.sha256(b"capture/" + isi).hexdigest()[0] in "0123" else "latih"


def jalankan(folder_capture, keluar, cari, cari_kendaraan, baca, ambang, maks_kendaraan=None, cadangan_utuh=False, varian="v0",
             rapikan=0.0):
    """Kembali: hitungan saja. maks_kendaraan dan cadangan_utuh (Rencana 25): cara pakai tahap kendaraan, lihat
    kendaraan.cari_dalam_kendaraan. varian (Rencana 26): potongan pembaca tahan geser (tahan_geser.VARIAN); v0 = cara lama, lewat
    kode yang sama persis. rapikan (Rencana 27): konteks pencarian kedua di sekitar tiap kotak (rapikan.rapikan_kotak); 0 = mati.
    Keempatnya dicatat di ringkasan sebagai "aturan"."""
    if cari_kendaraan is None and (maks_kendaraan is not None or cadangan_utuh):
        raise ValueError("maks_kendaraan dan cadangan_utuh hanya berlaku dengan tahap kendaraan")
    if varian not in VARIAN:
        raise ValueError(f"varian potongan harus salah satu dari {sorted(VARIAN)}, bukan {varian}")
    if rapikan < 0:
        raise ValueError(f"konteks rapikan tidak boleh negatif, bukan {rapikan}")
    keluar = Path(keluar)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    daftar = []
    for sub in sorted(p for p in Path(folder_capture).iterdir() if p.is_dir()):
        kelompok = sub.name.split()[-1]
        for berkas in sub.rglob("*"):
            if berkas.is_file() and berkas.suffix.lower() in AKHIRAN:
                isi = berkas.read_bytes()
                daftar.append((hashlib.sha256(isi).hexdigest(), kelompok, berkas, isi))
    baris, tanpa, peta, per_kelompok = [], [], {}, {}
    for urutan, (_, kelompok, berkas, isi) in enumerate(sorted(daftar, key=lambda x: x[0]), 1):
        nama = f"g{urutan:04d}"
        peta[nama] = str(berkas.relative_to(folder_capture))
        per_kelompok[kelompok] = per_kelompok.get(kelompok, 0) + 1
        gambar = cv2.imread(str(berkas))
        if gambar is None:
            raise ValueError("ada gambar yang tak bisa dibuka")  # tanpa jalur: nama berkas bisa memuat nomor plat
        if cari_kendaraan is None:  # rantai jualan tanpa pencari kendaraan (Rencana 24): gambar utuh, seperti rantai.py
            kendaraan, kotak = [], [k for k in cari(gambar) if k[4] >= ambang]
        else:
            kendaraan = cari_kendaraan(gambar)
            kotak = cari_dalam_kendaraan(gambar, kendaraan, cari, ambang, maks_kendaraan=maks_kendaraan,
                                         cadangan_utuh=cadangan_utuh)
        if rapikan:
            kotak = [rapikan_kotak(gambar, k, cari, ambang, rapikan) for k in kotak]
        nomor = 0
        for k in kotak:
            if varian == "v0":
                p = potong(gambar, k)
                if p is None:
                    continue
                teks, yakin = baca(p)
            else:
                hasil = baca_tahan_geser(gambar, k, baca, varian)
                if hasil is None:
                    continue
                teks, yakin, p = hasil
            nomor += 1
            plat = urai(teks)
            potongan = f"{nama}-{nomor}.png"
            cv2.imwrite(str(keluar / "potongan" / potongan), p)
            baris.append({"video": nama, "nomor": nomor, "kategori": kelompok, "sudut": "tangkapan", "sisi": sisi(isi),
                          "teks": plat.teks if plat else "", "status": "ragu", "potongan": potongan,
                          "yakin_kotak": round(float(k[4]), 3), "yakin_baca": round(float(yakin), 4),
                          "kotak": [round(float(x), 1) for x in k[:4]]})
        if nomor == 0:
            tanpa.append({"gambar": nama, "kelompok": kelompok, "sisi": sisi(isi),
                          "kendaraan": [[round(float(x), 1) for x in v[:4]] + [v[5]] for v in kendaraan]})
    with open(keluar / "kedatangan.jsonl", "w") as f:
        for b in baris:
            f.write(json.dumps(b) + "\n")
    (keluar / "tanpa-plat.json").write_text(json.dumps(tanpa, indent=1))
    (keluar / "peta-berkas.json").write_text(json.dumps(peta, indent=1, ensure_ascii=False))
    ringkas = {"gambar": len(daftar), "plat": len(baris), "gambar_tanpa_plat": len(tanpa), "per_kelompok": per_kelompok,
               "aturan": {"tahap_kendaraan": cari_kendaraan is not None, "maks_kendaraan": maks_kendaraan,
                          "cadangan_utuh": bool(cadangan_utuh), "varian_potong": varian, "rapikan": float(rapikan)}}
    (keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=1))
    return ringkas


def buat_lembar_tanpa(folder_capture, folder_baca, keluar):
    """Lembar gambar yang tidak menghasilkan plat, untuk OWNER: satu kartu per gambar, kendaraan setinggi minimal MIN_TINGGI
    diberi kotak biru bernomor. Owner menyebut kartu yang memuat plat terbaca ("3: 1" = kartu 3, kendaraan 1; "5:" bila platnya
    terbaca tetapi kendaraannya tanpa kotak). Lembar memuat plat: agen tidak membukanya. Kembali: hitungan saja."""
    folder_baca, keluar = Path(folder_baca), Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    tanpa = json.loads((folder_baca / "tanpa-plat.json").read_text())
    peta = json.loads((folder_baca / "peta-berkas.json").read_text())
    kartu_, baris = [], []
    for nomor, t in enumerate(tanpa, 1):
        gambar = cv2.imread(str(Path(folder_capture) / peta[t["gambar"]]))
        if gambar is None:
            raise ValueError("ada gambar yang tak bisa dibuka")
        bernomor = [v for v in t["kendaraan"] if v[3] - v[1] >= MIN_TINGGI]
        kartu_.append(kartu(nomor, gambar_bernomor(gambar, bernomor)))
        baris.append({"nomor": nomor, "gambar": t["gambar"], "kelompok": t["kelompok"], "sisi": t["sisi"], "bernomor": bernomor})
    halaman = []
    for awal in range(0, len(kartu_), PER_HALAMAN):
        nama = f"lembar-tanpa-plat-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(kartu_[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    (keluar / "lembar-tanpa-plat.json").write_text(json.dumps({"min_tinggi": MIN_TINGGI, "halaman": halaman, "baris": baris},
                                                              indent=1))
    return {"kartu": len(baris), "kendaraan_bernomor": sum(len(b["bernomor"]) for b in baris), "halaman": len(halaman)}


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Membaca gambar diam (tangkapan owner) dengan urutan rantai (Rencana 24).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    j = perintah.add_parser("jalan")
    for nama in ("folder_capture", "keluar", "folder_pencari", "folder_kendaraan", "folder_baca", "folder_unduhan"):
        j.add_argument(nama)
    j.add_argument("--ambang", type=float, required=True)
    j.add_argument("--utas", type=int, default=2)
    j.add_argument("--tanpa-kendaraan", action="store_true", help="plat dicari di gambar utuh; folder_kendaraan diabaikan")
    j.add_argument("--pembaca-jualan", action="store_true",
                   help="folder_baca berisi mesin jualan (latih_fpo latih-jualan); folder_unduhan diabaikan")
    j.add_argument("--maks-kendaraan", type=int, help="hanya sekian kendaraan terdekat yang dicari platnya (Rencana 25, K45)")
    j.add_argument("--cadangan-utuh", action="store_true",
                   help="plat dicari di gambar utuh bila tidak ada kendaraan setinggi MIN_TINGGI (Rencana 25)")
    j.add_argument("--varian-potong", choices=sorted(VARIAN), default="v0",
                   help="pembaca tahan geser: v0 cara lama, v1 3 potongan, v2 7 potongan (Rencana 26)")
    j.add_argument("--rapikan", type=float, default=0.0,
                   help="konteks pencarian kedua di sekitar tiap kotak plat, kali ukuran kotak; 0 = mati (Rencana 27)")
    t = perintah.add_parser("lembar-tanpa")
    for nama in ("folder_capture", "folder_baca", "keluar"):
        t.add_argument(nama)
    p = pengurai.parse_args(argumen)
    if p.perintah == "lembar-tanpa":
        try:
            r = buat_lembar_tanpa(p.folder_capture, p.folder_baca, p.keluar)
        except (OSError, ValueError, KeyError) as galat:
            print(f"GAGAL: {type(galat).__name__}")
            return 1
        print(f"{r['kartu']} kartu, {r['kendaraan_bernomor']} kendaraan bernomor, {r['halaman']} halaman. "
              "Lembar memuat plat: hanya owner yang membukanya.")
        return 0
    try:
        import onnx_fpo
        from kendaraan import PencariKendaraan
        from pencari_yolox import PencariYolox

        cari = PencariYolox(p.folder_pencari, utas=p.utas)
        cari_kendaraan = None if p.tanpa_kendaraan else PencariKendaraan(p.folder_kendaraan, utas=p.utas)
        if p.pembaca_jualan:
            from latih_fpo import PembacaMesinJualan

            pembaca = PembacaMesinJualan(p.folder_baca)
        else:
            pembaca = onnx_fpo.PembacaOnnxMesin(p.folder_baca, p.folder_unduhan, utas=p.utas)
        r = jalankan(p.folder_capture, p.keluar, cari, cari_kendaraan, pembaca.dengan_yakin, p.ambang,
                     maks_kendaraan=p.maks_kendaraan, cadangan_utuh=p.cadangan_utuh, varian=p.varian_potong, rapikan=p.rapikan)
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{r['gambar']} gambar ({r['per_kelompok']}); {r['plat']} plat; {r['gambar_tanpa_plat']} gambar tanpa plat. "
          "Keluaran memuat plat: agen tidak membukanya.")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
