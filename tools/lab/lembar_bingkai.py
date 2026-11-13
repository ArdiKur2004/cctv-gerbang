"""Lembar bingkai untuk diperiksa OWNER (Rencana 17; spec Fase 1 bagian 3): mengukur plat yang terlewat.

Dari tiap video diambil PER_VIDEO gambar pada jarak waktu yang sama (tetap, bukan acak), sampai MAKS gambar. Kotak yang ditemukan
pencari plat (keyakinan minimal ambang validasinya) digambar hijau. Owner menyebut nomor bingkai yang memuat plat yang bisa ia baca
tetapi TIDAK berkotak hijau (terlewat), dan nomor bingkai yang terlalu buram untuk dinilai (tak jelas). Lembar memuat plat yang
terbaca: agen TIDAK PERNAH membukanya (CLAUDE.md §7). Layar hanya hitungan.

Dengan --kendaraan (K39, Rencana 19 Task 7b), kendaraan yang ditemukan digambar biru, dan kotak plat yang tengahnya di luar
kendaraan tidak digambar, sama dengan yang dibuang rantai.

  lembar: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_bingkai.py lembar /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data-asal/pembagian-video-fase1.json /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/lembar-bingkai
  nilai:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_bingkai.py nilai /kerja/data/keluaran/lembar-bingkai/lembar-bingkai.json /kerja/data/keluaran/lembar-bingkai/nilai.json --terlewat <n,...> --tak-jelas <n,...>
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import wilson  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from bagi_set_uji import SEDIKIT  # noqa: E402
from kendaraan import cari_dalam_kendaraan, saring  # noqa: E402
from letak import ATURAN as ATURAN_LETAK, saring_letak  # noqa: E402
from lembar_rantai import nomor_baris  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from rantai import CARA, daftar_video, pilih_berkas  # noqa: E402

PER_VIDEO = 4
MAKS = 60
LEBAR = 960  # lebar bingkai di lembar; tidak diperbesar, supaya plat yang terbaca di video tetap terbaca di lembar
PER_HALAMAN = 4
HIJAU = (0, 200, 0)
BIRU = (200, 0, 0)  # urutan warna OpenCV: kotak kendaraan (K39)


def titik_ambil(jumlah_gambar, per_video=PER_VIDEO):
    """Nomor gambar pada jarak yang sama, tidak di ujung video."""
    return [int((i + 0.5) * jumlah_gambar / per_video) for i in range(per_video)] if jumlah_gambar > 0 else []


def gambar_kotak(gambar, kotak, kendaraan=()):
    """Salinan gambar dengan kotak biru untuk tiap kendaraan lalu kotak hijau untuk tiap kotak plat (x1, y1, x2, y2, ...)."""
    hasil = gambar.copy()
    tebal = max(2, gambar.shape[1] // 400)
    for warna, daftar in ((BIRU, kendaraan), (HIJAU, kotak)):
        for k in daftar:
            cv2.rectangle(hasil, (int(k[0]), int(k[1])), (int(k[2]), int(k[3])), warna, tebal)
    return hasil


def kartu(nomor, gambar):
    """Bingkai selebar paling banyak LEBAR (diperkecil bila lebih), dengan nomor di pita atas."""
    skala = min(1.0, LEBAR / gambar.shape[1])
    kecil = cv2.resize(gambar, (max(1, round(gambar.shape[1] * skala)), max(1, round(gambar.shape[0] * skala))),
                       interpolation=cv2.INTER_AREA)
    kanvas = np.full((kecil.shape[0] + 40, LEBAR, 3), 255, np.uint8)
    kanvas[40:, :kecil.shape[1]] = kecil
    cv2.putText(kanvas, f"bingkai {nomor}", (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    return kanvas


def buat_lembar(daftar, folder_video, cari, ambang, keluar, per_video=PER_VIDEO, maks=MAKS, cari_kendaraan=None, cara="saring",
                letak=None):
    """daftar: video dari manifes (berkas, kategori, sudut), diurutkan menurut nama berkas. Kembali: hitungan saja.
    cari_kendaraan (K39): kendaraan digambar biru. cara "saring": kotak plat yang tengahnya di luar kendaraan tidak digambar.
    cara "potong" (Rencana 20): plat dicari di dalam potongan kendaraan, seperti rantai. letak (Rencana 21): kotak plat yang tidak
    lolos aturan letak tidak digambar, seperti rantai."""
    if cara not in CARA:
        raise ValueError(f"cara harus salah satu dari {CARA}, bukan {cara}")
    if letak is not None and letak not in ATURAN_LETAK:
        raise ValueError(f"aturan letak tidak dikenal: {letak}")
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    kartu_, baris = [], []
    for v in sorted(daftar, key=lambda x: x["berkas"]):
        if len(baris) >= maks:
            break
        video = cv2.VideoCapture(str(Path(folder_video) / v["berkas"]))
        jumlah = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else 0
        for g in titik_ambil(jumlah, per_video):
            if len(baris) >= maks:
                break
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            kendaraan, tersaring = [], 0
            if cari_kendaraan is not None and cara == "potong":
                kendaraan = cari_kendaraan(gambar)
                kotak = cari_dalam_kendaraan(gambar, kendaraan, cari, ambang)
            else:
                kotak = [k for k in cari(gambar) if k[4] >= ambang]
                if cari_kendaraan is not None:
                    kendaraan = cari_kendaraan(gambar)
                    kotak, tersaring = saring(kotak, kendaraan)
            tersaring_letak = 0
            if letak is not None:
                kotak, tersaring_letak = saring_letak(kotak, letak)
            nomor = len(baris) + 1
            kartu_.append(kartu(nomor, gambar_kotak(gambar, kotak, kendaraan)))
            baris.append({"nomor": nomor, "video": v["berkas"], "gambar": g, "kotak": len(kotak),
                          "kendaraan": len(kendaraan), "tersaring": tersaring, "tersaring_letak": tersaring_letak,
                          "kategori": v.get("kategori", ""), "sudut": v.get("sudut", "")})
        video.release()
    halaman = []
    for awal in range(0, len(kartu_), PER_HALAMAN):
        nama = f"lembar-bingkai-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(kartu_[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    (keluar / "lembar-bingkai.json").write_text(json.dumps({"per_video": per_video, "maks": maks, "ambang": ambang,
                                                           "ambang_kendaraan": getattr(cari_kendaraan, "ambang", None),
                                                           "cara_kendaraan": cara if cari_kendaraan is not None else None,
                                                           "letak": letak,
                                                           "halaman": halaman, "baris": baris}, indent=1))
    return {"video": len({b["video"] for b in baris}), "bingkai": len(baris), "halaman": len(halaman)}


def nilai(lembar, terlewat=(), tak_jelas=()):
    """Hitungan per kelompok (sudut-kategori) dari jawaban owner (nomor bingkai per jenis)."""
    semua = {b["nomor"]: b for b in lembar["baris"]}
    sebut = {"terlewat": set(terlewat), "tak_jelas": set(tak_jelas)}
    for nama, nomor in sebut.items():
        asing = nomor - set(semua)
        if asing:
            raise ValueError(f"nomor bingkai {nama} tidak ada di lembar: {sorted(asing)}")
    dua = sebut["terlewat"] & sebut["tak_jelas"]
    if dua:
        raise ValueError(f"bingkai {sorted(dua)} disebut terlewat dan tak jelas sekaligus")
    hasil = {"bingkai": len(semua), "tak_jelas": len(sebut["tak_jelas"]), "kelompok": {}}
    for nomor, b in sorted(semua.items()):
        if nomor in sebut["tak_jelas"]:
            continue
        for k in ("semua", f"{b['sudut']}-{b['kategori']}"):
            r = hasil["kelompok"].setdefault(k, {"dinilai": 0, "ada_terlewat": 0})
            r["dinilai"] += 1
            r["ada_terlewat"] += int(nomor in sebut["terlewat"])
    for r in hasil["kelompok"].values():
        rentang = wilson(r["ada_terlewat"], r["dinilai"])
        r["rentang_95_ada_terlewat"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["dinilai"] < SEDIKIT
    return hasil


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Lembar bingkai untuk owner: plat yang terlewat (Rencana 17).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("lembar")
    for nama in ("manifes", "folder_video", "pembagian", "folder_pencari", "keluar"):
        a.add_argument(nama)
    a.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    a.add_argument("--per-video", type=int, default=PER_VIDEO)
    a.add_argument("--maks", type=int, default=MAKS)
    a.add_argument("--kendaraan", help="folder pencari kendaraan (K39): kendaraan digambar biru")
    a.add_argument("--cara", choices=CARA, default="saring", help="saring (Rencana 19) atau potong (Rencana 20)")
    a.add_argument("--ambang", type=float, help="mengganti ambang_validasi pencari, seperti rantai.py jalan --ambang")
    a.add_argument("--letak", choices=sorted(ATURAN_LETAK), help="aturan letak plat di kendaraan (Rencana 21)")
    b = perintah.add_parser("nilai")
    b.add_argument("lembar")
    b.add_argument("keluar")
    b.add_argument("--terlewat", type=nomor_baris, default=[])
    b.add_argument("--tak-jelas", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "lembar":
            from kendaraan import PencariKendaraan
            from pencari_yolox import PencariYolox

            cari = PencariYolox(p.folder_pencari)
            cari_kendaraan = PencariKendaraan(p.kendaraan) if p.kendaraan else None
            ambang = p.ambang if p.ambang is not None else json.loads((Path(p.folder_pencari) / "mesin.json").read_text())["ambang_validasi"]
            daftar = daftar_video(p.manifes, hanya=pilih_berkas(p.pembagian, p.sisi))
            r = buat_lembar(daftar, p.folder_video, cari, ambang, p.keluar, p.per_video, p.maks, cari_kendaraan, p.cara, p.letak)
            print(f"{r['video']} video, {r['bingkai']} bingkai di {r['halaman']} lembar. Lembar ini memuat plat yang terbaca: "
                  "agen tidak membukanya.")
        else:
            h = nilai(json.loads(Path(p.lembar).read_text()), p.terlewat, p.tak_jelas)
            Path(p.keluar).write_text(json.dumps(h, indent=1))
            print(f"{h['bingkai']} bingkai: tak jelas {h['tak_jelas']}")
            for k, r in sorted(h["kelompok"].items()):
                print(f"{k:<28} dinilai {r['dinilai']}: ada plat terlewat {r['ada_terlewat']} (rentang 95% "
                      f"{r['rentang_95_ada_terlewat']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''})")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "bingkai" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
