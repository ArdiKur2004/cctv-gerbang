"""Lembar kendaraan untuk diperiksa OWNER, lalu banding calon cara mencari plat (Rencana 20, K39 langkah 3).

Label "kendaraan yang platnya terbaca" diambil di sisi LATIH, supaya cara mencari plat dipilih tanpa menyentuh set uji.
- lembar: dari tiap video diambil PER_VIDEO gambar pada jarak waktu yang sama (lembar_bingkai.titik_ambil). Tiap kendaraan setinggi
  minimal kendaraan.MIN_TINGGI piksel diberi kotak biru bernomor. Owner menyebut, per bingkai, nomor kendaraan yang platnya bisa
  ia baca ("3: 1, 4; 7: 2"), dan nomor bingkai yang memuat kendaraan berplat terbaca tanpa kotak biru. Lembar memuat plat yang
  terbaca: agen TIDAK PERNAH membukanya (CLAUDE.md §7).
- banding: tiap calon (pencari x cara saring/potong x ambang AMBANG_CALON) dinilai di bingkai yang sama, tanpa kerja owner
  tambahan: kendaraan berplat terbaca yang mendapat kotak plat (ditemukan), kotak berikutnya di kendaraan yang sama (lebih),
  kotak di kendaraan bernomor lain, dan kotak di luar kendaraan bernomor. Juga dihitung pada video validasi saja
  (dataset_cctv.sisi_validasi), yang tidak dipakai melatih pencari baru.
- pilih: aturan Rencana 20 yang ditetapkan sebelum angka dilihat.
Layar hanya hitungan dan nama calon.

  lembar:  powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/lembar_kendaraan.py lembar /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data-asal/pembagian-video-fase1.json /kerja/data/keluaran/kendaraan-yolox-coco /kerja/data/keluaran/lembar-kendaraan-latih
  banding: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/lembar_kendaraan.py banding /kerja/data/keluaran/lembar-kendaraan-latih/lembar-kendaraan.json /kerja/data/video/riset /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/pencari-yolox-nano-640-cctv1 /kerja/data/keluaran/lembar-kendaraan-latih/banding.json --terbaca @/kerja/data/alat-sementara/jawaban-20-kendaraan.txt
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from kendaraan import MIN_TINGGI, cari_dalam_kendaraan, saring  # noqa: E402
from lembar_bingkai import kartu, titik_ambil  # noqa: E402
from lembar_rantai import nomor_baris  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from rantai import daftar_video, pilih_berkas  # noqa: E402

PER_VIDEO = 2
MAKS = 80
PER_HALAMAN = 4
BIRU = (200, 0, 0)  # urutan warna OpenCV
PUTIH = (255, 255, 255)
AMBANG_CALON = (0.1, 0.25, 0.5)
CARA = ("saring", "potong")


def gambar_bernomor(gambar, bernomor):
    """Salinan gambar dengan kotak biru dan nomornya (1, 2, ...) di pita biru di pojok kiri atas tiap kotak."""
    hasil = gambar.copy()
    tebal = max(2, gambar.shape[1] // 400)
    skala = max(0.6, gambar.shape[1] / 1200)
    for i, v in enumerate(bernomor, 1):
        x1, y1, x2, y2 = (int(x) for x in v[:4])
        cv2.rectangle(hasil, (x1, y1), (x2, y2), BIRU, tebal)
        (lebar, tinggi), _ = cv2.getTextSize(str(i), cv2.FONT_HERSHEY_SIMPLEX, skala, tebal)
        cv2.rectangle(hasil, (x1, y1), (x1 + lebar + 6, y1 + tinggi + 8), BIRU, -1)
        cv2.putText(hasil, str(i), (x1 + 3, y1 + tinggi + 4), cv2.FONT_HERSHEY_SIMPLEX, skala, PUTIH, tebal)
    return hasil


def _daftar(v):
    return [float(x) for x in v[:5]] + [v[5]]


def baca_gambar(folder_video, berkas, nomor):
    video = cv2.VideoCapture(str(Path(folder_video) / berkas))
    try:
        video.set(cv2.CAP_PROP_POS_FRAMES, nomor)
        ada, gambar = video.read()
    finally:
        video.release()
    return gambar if ada else None


def buat_lembar(daftar, folder_video, cari_kendaraan, keluar, per_video=PER_VIDEO, maks=MAKS):
    """daftar: video dari manifes (berkas, kategori, sudut), diurutkan menurut nama berkas. Kembali: hitungan saja."""
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    kartu_, baris = [], []
    for v in sorted(daftar, key=lambda x: x["berkas"]):
        if len(baris) >= maks:
            break
        video = cv2.VideoCapture(str(Path(folder_video) / v["berkas"]))
        jumlah = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else 0
        video.release()
        for g in titik_ambil(jumlah, per_video):
            if len(baris) >= maks:
                break
            gambar = baca_gambar(folder_video, v["berkas"], g)
            if gambar is None:
                continue
            kendaraan = cari_kendaraan(gambar)
            bernomor = [k for k in kendaraan if k[3] - k[1] >= MIN_TINGGI]
            nomor = len(baris) + 1
            kartu_.append(kartu(nomor, gambar_bernomor(gambar, bernomor)))
            baris.append({"nomor": nomor, "video": v["berkas"], "gambar": g, "sudut": v.get("sudut", ""),
                          "kategori": v.get("kategori", ""), "kendaraan": [_daftar(k) for k in kendaraan],
                          "bernomor": [_daftar(k) for k in bernomor]})
    halaman = []
    for awal in range(0, len(kartu_), PER_HALAMAN):
        nama = f"lembar-kendaraan-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(kartu_[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    (keluar / "lembar-kendaraan.json").write_text(json.dumps({
        "per_video": per_video, "maks": maks, "ambang_kendaraan": getattr(cari_kendaraan, "ambang", None),
        "min_tinggi": MIN_TINGGI, "halaman": halaman, "baris": baris}, indent=1))
    return {"video": len({b["video"] for b in baris}), "bingkai": len(baris),
            "kendaraan_bernomor": sum(len(b["bernomor"]) for b in baris), "halaman": len(halaman)}


def baca_jawaban(teks):
    """"<bingkai>: <nomor>, <nomor>; ..." (baris baru juga pemisah) -> {bingkai: {nomor kendaraan}}."""
    hasil = {}
    for butir in teks.replace("\n", ";").split(";"):
        if not butir.strip():
            continue
        if ":" not in butir:
            raise ValueError("butir jawaban tanpa titik dua")
        kiri, kanan = butir.split(":", 1)
        hasil.setdefault(int(kiri), set()).update(int(x) for x in kanan.split(",") if x.strip())
    return hasil


def _pemuat(kotak, bernomor):
    """Nomor (mulai 1) kendaraan bernomor terkecil yang memuat tengah kotak, atau None."""
    cx, cy = (kotak[0] + kotak[2]) / 2, (kotak[1] + kotak[3]) / 2
    muat = [(((v[2] - v[0]) * (v[3] - v[1])), i) for i, v in enumerate(bernomor, 1)
            if v[0] <= cx <= v[2] and v[1] <= cy <= v[3]]
    return min(muat)[1] if muat else None


def nilai_calon(lembar, terbaca, kotak_per_bingkai):
    """Hitungan satu calon dari jawaban owner (bingkai -> nomor kendaraan berplat terbaca) dan kotak plat per bingkai."""
    semua = {b["nomor"]: b for b in lembar["baris"]}
    for n, nomor in terbaca.items():
        if n not in semua:
            raise ValueError(f"nomor bingkai {n} tidak ada di lembar")
        asing = sorted(k for k in nomor if not 1 <= k <= len(semua[n]["bernomor"]))
        if asing:
            raise ValueError(f"nomor kendaraan {asing} tidak ada di bingkai {n}")
    h = {"plat_terbaca": 0, "ditemukan": 0, "kotak_lebih": 0, "kotak_kendaraan_lain": 0, "kotak_luar": 0}
    for n, b in semua.items():
        label = terbaca.get(n, set())
        h["plat_terbaca"] += len(label)
        kena = Counter()
        for k in kotak_per_bingkai.get(n, []):
            i = _pemuat(k, b["bernomor"])
            if i is None:
                h["kotak_luar"] += 1
            elif i in label:
                kena[i] += 1
            else:
                h["kotak_kendaraan_lain"] += 1
        h["ditemukan"] += len(kena)
        h["kotak_lebih"] += sum(c - 1 for c in kena.values())
    return h


def banding(lembar, folder_video, pencari, terbaca, validasi):
    """pencari: nama -> fungsi cari. validasi: nama berkas video yang tidak dipakai melatih pencari baru. Kembali: daftar calon
    dengan hitungan di semua bingkai dan di bingkai video validasi saja."""
    kotak = {}
    for b in lembar["baris"]:
        gambar = baca_gambar(folder_video, b["video"], b["gambar"])
        if gambar is None:
            raise OSError("gambar lembar tidak terbaca dari video")
        kendaraan = [tuple(v) for v in b["kendaraan"]]
        for nama, cari in pencari.items():
            utuh = cari(gambar)
            dalam = cari_dalam_kendaraan(gambar, kendaraan, cari, min(AMBANG_CALON))
            for a in AMBANG_CALON:
                kotak.setdefault((nama, "saring", a), {})[b["nomor"]] = saring([k for k in utuh if k[4] >= a], kendaraan)[0]
                kotak.setdefault((nama, "potong", a), {})[b["nomor"]] = [k for k in dalam if k[4] >= a]
    sub = {"baris": [b for b in lembar["baris"] if b["video"] in validasi]}
    nomor_sub = {b["nomor"] for b in sub["baris"]}
    terbaca_sub = {n: k for n, k in terbaca.items() if n in nomor_sub}
    hasil = []
    for nama in pencari:
        for cara in CARA:
            for a in AMBANG_CALON:
                k = kotak.get((nama, cara, a), {})
                hasil.append({"nama": f"{nama}-{cara}-{a}", "pencari": nama, "cara": cara, "ambang": a,
                              "semua": nilai_calon(lembar, terbaca, k), "validasi": nilai_calon(sub, terbaca_sub, k)})
    return hasil


def _salah_tempat(s):
    return s["kotak_lebih"] + s["kotak_kendaraan_lain"] + s["kotak_luar"]


def pilih(hasil):
    """Aturan Rencana 20: ditemukan terbanyak, lalu kotak salah tempat tersedikit, lalu nama. Calon pencari baru hanya boleh
    menang bila di video validasi ia tidak menemukan lebih sedikit daripada calon pencari lama teratas."""
    urut = sorted(hasil, key=lambda h: (-h["semua"]["ditemukan"], _salah_tempat(h["semua"]), h["nama"]))
    atas = urut[0]
    if atas["pencari"] == "baru":
        lama = [h for h in urut if h["pencari"] == "lama"]
        if lama and atas["validasi"]["ditemukan"] < lama[0]["validasi"]["ditemukan"]:
            return {**lama[0], "alasan": f"{atas['nama']} teratas, tetapi di video validasi menemukan lebih sedikit daripada "
                                         f"{lama[0]['nama']}"}
    return {**atas, "alasan": "teratas menurut aturan"}


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Lembar kendaraan latih dan banding calon cara mencari plat (Rencana 20).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("lembar")
    for nama in ("manifes", "folder_video", "pembagian", "folder_kendaraan", "keluar"):
        a.add_argument(nama)
    a.add_argument("--sisi", choices=("uji", "latih"), default="latih")
    a.add_argument("--per-video", type=int, default=PER_VIDEO)
    a.add_argument("--maks", type=int, default=MAKS)
    b = perintah.add_parser("banding")
    for nama in ("lembar", "folder_video", "folder_pencari_lama", "folder_pencari_baru", "keluar"):
        b.add_argument(nama)
    b.add_argument("--terbaca", required=True, help="jawaban owner, atau @berkas yang berisi jawaban")
    b.add_argument("--biru-terlewat", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "lembar":
            from kendaraan import PencariKendaraan

            daftar = daftar_video(p.manifes, hanya=pilih_berkas(p.pembagian, p.sisi))
            r = buat_lembar(daftar, p.folder_video, PencariKendaraan(p.folder_kendaraan), p.keluar, p.per_video, p.maks)
            print(f"{r['video']} video, {r['bingkai']} bingkai, {r['kendaraan_bernomor']} kendaraan bernomor di {r['halaman']} "
                  "lembar. Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
            return 0
        from dataset_cctv import sisi_validasi
        from pencari_yolox import PencariYolox

        lembar = json.loads(Path(p.lembar).read_text())
        teks = Path(p.terbaca[1:]).read_text() if p.terbaca.startswith("@") else p.terbaca
        terbaca = baca_jawaban(teks)
        asing = sorted(set(p.biru_terlewat) - {x["nomor"] for x in lembar["baris"]})
        if asing:
            raise ValueError(f"nomor bingkai biru terlewat {asing} tidak ada di lembar")
        validasi = {x["video"] for x in lembar["baris"] if sisi_validasi(x["video"])}
        pencari = {"lama": PencariYolox(p.folder_pencari_lama), "baru": PencariYolox(p.folder_pencari_baru)}
        hasil = banding(lembar, p.folder_video, pencari, terbaca, validasi)
        terpilih = pilih(hasil)
        Path(p.keluar).write_text(json.dumps({"bingkai": len(lembar["baris"]), "video_validasi": len(validasi),
                                              "bingkai_biru_terlewat": len(p.biru_terlewat), "calon": hasil,
                                              "terpilih": terpilih}, indent=1))
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except ValueError as galat:
        print(f"GAGAL: {galat}" if any(k in str(galat) for k in ("bingkai", "kendaraan", "jawaban")) else
              f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    s = hasil[0]["semua"]
    print(f"{len(lembar['baris'])} bingkai, {s['plat_terbaca']} kendaraan berplat terbaca, {len(validasi)} video validasi, "
          f"{len(p.biru_terlewat)} bingkai dengan kendaraan berplat terbaca tanpa kotak biru")
    print(f"{'calon':<20} {'ditemukan':>9} {'lebih':>6} {'lain':>5} {'luar':>5} {'valid':>9}")
    for h in hasil:
        s, v = h["semua"], h["validasi"]
        print(f"{h['nama']:<20} {s['ditemukan']:>4}/{s['plat_terbaca']:<4} {s['kotak_lebih']:>6} {s['kotak_kendaraan_lain']:>5} "
              f"{s['kotak_luar']:>5} {v['ditemukan']:>4}/{v['plat_terbaca']:<4}")
    print(f"terpilih: {terpilih['nama']} ({terpilih['alasan']})")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
