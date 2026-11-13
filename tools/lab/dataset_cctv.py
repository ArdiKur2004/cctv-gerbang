"""Dataset pencari plat CCTV Fase 1 (Rencana 19), format YOLO seperti plat-lighting, untuk tools/lab/latih_yolox.py.

- Label kotak: penampakan.jsonl (rantai.py --simpan-penampakan, video SISI LATIH) + lembar-rantai.json + jawaban owner (nomor
  baris bukan plat; baris lain di lembar = plat). Jalur di luar lembar tidak berlabel.
- Gambar: paling banyak PER_JALUR gambar per jalur berlabel, berjarak sama. Kotak plat menjadi label; kotak bukan plat menjadi
  latar (contoh negatif); kotak tak berlabel DITUTUP dengan buram kuat, supaya tidak menjadi contoh negatif yang salah.
- Gambar tempel: gambar sampel tanpa kotak sama sekali (pada ambang rantai), LATAR_PER_VIDEO per video, diberi 1-3 plat buatan
  (tools/lab/plat_buatan.py) setinggi TINGGI_PLAT dari tinggi gambar, di dua pertiga bawah gambar.
- Sisi validasi: video latih yang SHA-256 "valid/<berkas>"-nya berawal 0-3 (sekitar seperempat), ditambah valid plat-lighting.
  Sisi uji Fase 1 tidak pernah dibaca.
Keluaran berisi gambar berplat: tinggal di data/, agen tidak membukanya. Layar hanya hitungan.

  bangun: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/dataset_cctv.py bangun /kerja/data-asal/video-riset.json /kerja/data-asal/pembagian-video-fase1.json /kerja/data/keluaran/rantai-latih-fase1 /kerja/data/keluaran/lembar-latih-fase1/lembar-rantai.json /kerja/data/video/riset /kerja/data/keluaran/dataset/plat-lighting /kerja/data/keluaran/dataset/cctv-fase1 --bukan-plat <n,...>
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV)
import plat_buatan as pb  # noqa: E402
from deteksi import AKHIRAN  # noqa: E402
from lembar_rantai import nomor_baris  # noqa: E402
from rantai import daftar_video, fps_sah, langkah_sampel, pilih_berkas  # noqa: E402

PER_JALUR = 3
LATAR_PER_VIDEO = 6
TINGGI_PLAT = (0.015, 0.08)


def sisi_validasi(berkas):
    return hashlib.sha256(f"valid/{berkas}".encode()).hexdigest()[0] in "0123"


def label_jalur(tampak, lembar, bukan_plat):
    """(video, jalur) -> "plat" | "bukan" untuk jalur yang kedatangannya ada di lembar."""
    di_lembar = {(b["video"], b["kedatangan"]): ("bukan" if b["nomor"] in bukan_plat else "plat") for b in lembar["baris"]}
    return {(t["video"], t["jalur"]): di_lembar[(t["video"], t["kedatangan"])] for t in tampak
            if t["kedatangan"] is not None and (t["video"], t["kedatangan"]) in di_lembar}


def pilih_gambar(tampak, label, per_jalur=PER_JALUR):
    """[(video, nomor_gambar, [kotak plat], [kotak ditutup])], urut video lalu gambar."""
    per_gambar = {}
    for t in tampak:
        for g, *kotak in t["tampak"]:
            per_gambar.setdefault((t["video"], g), []).append(((t["video"], t["jalur"]), kotak))
    calon = set()
    for t in tampak:
        if (t["video"], t["jalur"]) in label:
            g = [x[0] for x in t["tampak"]]
            calon.update((t["video"], g[int(round(i))]) for i in np.linspace(0, len(g) - 1, min(per_jalur, len(g))))
    return [(v, g, [k for j, k in per_gambar[(v, g)] if label.get(j) == "plat"],
             [k for j, k in per_gambar[(v, g)] if j not in label]) for v, g in sorted(calon)]


def tutup(gambar, kotak):
    """Kotak tak berlabel dibuat buram kuat (tidak terbaca, tidak berbentuk plat)."""
    hasil = gambar.copy()
    for x1, y1, x2, y2 in kotak:
        a, b, c, d = max(0, int(x1)), max(0, int(y1)), min(gambar.shape[1], int(x2) + 1), min(gambar.shape[0], int(y2) + 1)
        if c > a and d > b:
            hasil[b:d, a:c] = cv2.blur(hasil[b:d, a:c], (max(3, (c - a) // 2 * 2 + 1), max(3, (d - b) // 2 * 2 + 1)))
    return hasil


def tempel(gambar, rng):
    """Satu plat buatan ditempel ke salinan gambar, di dua pertiga bawah. Kembali: (gambar, (x1, y1, x2, y2))."""
    t, l = gambar.shape[:2]
    jenis = "mobil" if rng.random() < 0.6 else "motor"
    warna = str(rng.choice(list(pb.PELUANG_WARNA), p=list(pb.PELUANG_WARNA.values())))
    plat = pb.plat(pb.teks_acak(rng), jenis, warna, rng, tinggi=96)
    tinggi = max(6, int(t * rng.uniform(*TINGGI_PLAT)))
    lebar = min(l - 2, max(8, int(tinggi * plat.shape[1] / plat.shape[0])))
    kecil = cv2.resize(plat, (lebar, tinggi), interpolation=cv2.INTER_AREA)
    x = int(rng.integers(0, l - lebar))
    y = int(rng.integers(t // 3, t - tinggi))
    hasil = gambar.copy()
    hasil[y:y + tinggi, x:x + lebar] = kecil
    return hasil, (x, y, x + lebar, y + tinggi)


def tulis(gambar, kotak, folder, nama):
    t, l = gambar.shape[:2]
    cv2.imwrite(str(folder / "images" / f"{nama}.jpg"), gambar)
    baris = [f"0 {(x1 + x2) / 2 / l:.6f} {(y1 + y2) / 2 / t:.6f} {(x2 - x1) / l:.6f} {(y2 - y1) / t:.6f}" for x1, y1, x2, y2 in kotak]
    (folder / "labels" / f"{nama}.txt").write_text("".join(b + "\n" for b in baris))


def bangun(manifes, pembagian, folder_rantai, lembar, bukan_plat, folder_video, folder_plat_lighting, keluar, benih=0,
           latar_per_video=LATAR_PER_VIDEO):
    """Kembali: hitungan per sisi (train/valid)."""
    tampak = [json.loads(b) for b in (Path(folder_rantai) / "penampakan.jsonl").read_text().splitlines() if b.strip()]
    pilihan = pilih_gambar(tampak, label_jalur(tampak, lembar, set(bukan_plat)))
    keluar = Path(keluar)
    for s in ("train", "valid"):
        for sub in ("images", "labels"):
            (keluar / s / sub).mkdir(parents=True, exist_ok=True)
    hitung = {s: {"gambar_cctv": 0, "kotak_plat": 0, "gambar_negatif": 0, "kotak_ditutup": 0, "gambar_tempel": 0,
                  "plat_lighting": 0} for s in ("train", "valid")}
    rng = np.random.default_rng(benih)
    terdeteksi = {}
    for t in tampak:
        terdeteksi.setdefault(t["video"], set()).update(x[0] for x in t["tampak"])
    for v in sorted(daftar_video(manifes, hanya=pilih_berkas(pembagian, "latih")), key=lambda x: x["berkas"]):
        berkas, s = v["berkas"], ("valid" if sisi_validasi(v["berkas"]) else "train")
        stem = Path(berkas).stem
        video = cv2.VideoCapture(str(Path(folder_video) / berkas))
        jumlah = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else 0
        for _, g, plat, ditutup in [p for p in pilihan if p[0] == berkas]:
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            tulis(tutup(gambar, ditutup), plat, keluar / s, f"{stem}-{g:06d}")
            h = hitung[s]
            h["gambar_cctv"] += 1
            h["kotak_plat"] += len(plat)
            h["gambar_negatif"] += int(not plat)
            h["kotak_ditutup"] += len(ditutup)
        langkah = langkah_sampel(fps_sah(video.get(cv2.CAP_PROP_FPS)))
        kosong = [g for g in range(0, jumlah, langkah) if g not in terdeteksi.get(berkas, set())]
        for g in [kosong[int(i)] for i in np.linspace(0, len(kosong) - 1, min(latar_per_video, len(kosong)))] if kosong else []:
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            kotak = []
            for _ in range(int(rng.integers(1, 4))):
                gambar, k = tempel(gambar, rng)
                kotak.append(k)
            tulis(gambar, kotak, keluar / s, f"{stem}-tempel-{g:06d}")
            hitung[s]["gambar_tempel"] += 1
        video.release()
    for s in ("train", "valid"):
        for gambar in sorted((Path(folder_plat_lighting) / s / "images").iterdir()):
            if gambar.suffix.lower() not in AKHIRAN:
                continue
            label = Path(folder_plat_lighting) / s / "labels" / f"{gambar.stem}.txt"
            shutil.copy(gambar, keluar / s / "images" / f"pl-{gambar.name}")
            if label.exists():
                shutil.copy(label, keluar / s / "labels" / f"pl-{gambar.stem}.txt")
            else:
                (keluar / s / "labels" / f"pl-{gambar.stem}.txt").write_text("")
            hitung[s]["plat_lighting"] += 1
    (keluar / "ringkasan.json").write_text(json.dumps(hitung, indent=1))
    return hitung


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Dataset pencari plat CCTV Fase 1 (Rencana 19).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("bangun")
    for nama in ("manifes", "pembagian", "folder_rantai", "lembar", "folder_video", "folder_plat_lighting", "keluar"):
        b.add_argument(nama)
    b.add_argument("--bukan-plat", type=nomor_baris, default=[])
    b.add_argument("--benih", type=int, default=0)
    p = pengurai.parse_args(argumen)
    try:
        lembar = json.loads(Path(p.lembar).read_text())
        h = bangun(p.manifes, p.pembagian, p.folder_rantai, lembar, p.bukan_plat, p.folder_video, p.folder_plat_lighting,
                   p.keluar, p.benih)
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    for s, x in h.items():
        print(f"{s}: {x}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
