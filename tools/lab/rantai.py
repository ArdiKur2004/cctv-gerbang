"""Rantai utuh di video riset (Rencana 14, K31, K32): cari plat (YOLOX-Nano-640), potong, baca huruf (fpo-indo-1), cek pola,
lalu gabung per kedatangan (spec 2.1 langkah 1, 3, 4, 5). Langkah 2 (meluruskan) belum ada: potongan dibaca apa adanya.

- Sampel: SAMPEL_PER_DETIK gambar per detik video. Gambar di antaranya dilewati dengan grab() dan tidak dihitung waktunya.
- Cari: kotak dengan keyakinan minimal ambang validasi pencari (dibaca dari mesin.json pencari, tidak disalin).
- Potong: kotak diperlebar MARGIN dari lebar dan tingginya di tiap sisi, dipotong pada batas gambar.
- Baca: (teks, yakin) per potongan; yakin = peluang terendah di semua slot pembaca.
- Lacak: kotak pada gambar sampel berikutnya ikut jalur yang sama bila IoU-nya dengan kotak terakhir jalur minimal IOU_IKUT
  dan jalur itu terakhir terlihat paling lama JEDA_MAKS_DETIK sebelumnya. Jalur yang terlihat minimal MIN_TAMPAK kali = satu
  kedatangan (spec 8.3: plat terlihat berturut-turut dalam satu potongan video); jalur yang terlihat sekali dihitung terpisah.
- Gabung: hanya bacaan yang sesuai pola plat Indonesia (plat.urai) yang dihitung. Teks yang paling sering dipilih (seri:
  jumlah yakin terbesar). Status "yakin" bila teks itu didukung minimal MIN_SETUJU bacaan dan minimal BAGIAN_SETUJU dari bacaan
  yang sah; selain itu "ragu" (ragu = tidak membuka). Semua ambang ditetapkan sebelum hasil dilihat dan tidak disetel dengan
  jawaban owner.
- detik_yakin: detik video dari penampakan pertama sampai bacaan gabungan pertama kali "yakin" bila bacaan diproses berurutan.

Keluaran di <keluar>: kedatangan.jsonl dan potongan/*.png memuat plat (data/; agen tidak membukanya); ringkasan.json hanya
hitungan dan waktu, tanpa nama berkas video. Layar hanya hitungan.

Video yang dijalankan: bersudut SUDUT di manifes; dengan --pembagian (data-asal/pembagian-video-fase1.json, tools/bagi-video.mjs)
hanya video satu sisi (--sisi uji, bawaan, atau latih). Rencana 17: sudut parkiran ikut.

Tahap kendaraan (K39, Rencana 19 Task 7b): dengan --kendaraan <folder pencari kendaraan>, kendaraan dicari di tiap gambar sampel
yang punya kotak plat, dan kotak plat yang tengahnya tidak di dalam kendaraan dibuang sebelum dibaca (tools/lab/kendaraan.py).
Kedatangan mencatat jenis kendaraannya; ringkasan mencatat ambang kendaraan dan jumlah kotak yang dibuang. Dengan --cara potong
(Rencana 20), kendaraan dicari di tiap gambar sampel dan plat dicari di dalam potongan kendaraan (K39 langkah 3). Dengan
--letak <aturan> (Rencana 21, K39 langkah 2), kotak plat yang letaknya di kendaraan tidak lolos aturan (tools/lab/letak.py)
dibuang sebelum dibaca; ringkasan mencatat aturan dan jumlah yang dibuang. Dengan --cara potong, --maks-kendaraan <n> dan
--cadangan-utuh (Rencana 25, K45) mengatur cara pakai tahap kendaraan (kendaraan.cari_dalam_kendaraan); keduanya dicatat di aturan.
--varian-potong v1|v2 (Rencana 26, K51): tiap kotak dibaca dari beberapa potongan lalu dipungut suara (tahan_geser.py); v0 = cara lama.
--rapikan <konteks> (Rencana 27, K54): tiap kotak dirapikan dengan pencarian kedua di sekitarnya (rapikan.py) sebelum saringan letak dan
dibaca; 0 = cara lama.

  jalan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/rantai.py jalan /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/rantai-video [--pembagian /kerja/data-asal/pembagian-video-fase1.json --sisi uji]
"""
import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from deteksi import iou  # noqa: E402
from kendaraan import cari_dalam_kendaraan, saring  # noqa: E402
from letak import ATURAN as ATURAN_LETAK, saring_letak  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from plat import urai  # noqa: E402
from rapikan import rapikan_kotak  # noqa: E402
from tahan_geser import VARIAN, baca_tahan_geser  # noqa: E402

SAMPEL_PER_DETIK = 5
IOU_IKUT = 0.3
JEDA_MAKS_DETIK = 1.0
MIN_TAMPAK = 2
MIN_SETUJU = 2
BAGIAN_SETUJU = 0.6
MARGIN = 0.05
SUDUT = ("gerbang", "parkiran", "kamera-diam-lain")
UTAS = 2
FPS_BAWAAN = 30.0
CARA = ("saring", "potong")


def fps_sah(fps):
    """fps dari video; yang tak terbaca (0, negatif, NaN) dianggap FPS_BAWAAN."""
    return float(fps) if fps and fps == fps and fps > 0 else FPS_BAWAAN


def langkah_sampel(fps, per_detik=SAMPEL_PER_DETIK):
    """Tiap berapa gambar diambil satu sampel."""
    return max(1, round(fps_sah(fps) / per_detik))


def potong(gambar, kotak, margin=MARGIN):
    """Potongan dari kotak (x1, y1, x2, y2, ...) yang diperlebar margin di tiap sisi; None bila kosong sesudah dipotong."""
    tinggi, lebar = gambar.shape[:2]
    x1, y1, x2, y2 = kotak[:4]
    dx, dy = (x2 - x1) * margin, (y2 - y1) * margin
    a, b = max(0, math.floor(x1 - dx)), max(0, math.floor(y1 - dy))
    c, d = min(lebar, math.ceil(x2 + dx)), min(tinggi, math.ceil(y2 + dy))
    return gambar[b:d, a:c].copy() if c > a and d > b else None


def ketajaman(potongan):
    """Varian Laplacian potongan kelabu (Rencana 23, K40): makin besar makin tajam."""
    return float(cv2.Laplacian(cv2.cvtColor(potongan, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())


def luas(p):
    x1, y1, x2, y2 = p["kotak"]
    return (x2 - x1) * (y2 - y1)


class Pelacak:
    """Mengikuti kotak plat dari gambar sampel ke gambar sampel. jalur: daftar jalur; tiap jalur daftar penampakan (dict dengan
    "kotak", "yakin_kotak", "detik", dan isi lain yang dibawa pemanggil). aktif: indeks jalur yang masih bisa disambung."""

    def __init__(self, iou_ikut=IOU_IKUT, jeda_maks=JEDA_MAKS_DETIK):
        self.iou_ikut, self.jeda_maks = iou_ikut, jeda_maks
        self.jalur, self.aktif = [], []

    def tambah(self, detik, penampakan):
        self.aktif = [i for i in self.aktif if detik - self.jalur[i][-1]["detik"] <= self.jeda_maks]
        terpakai = set()
        for p in sorted(penampakan, key=lambda p: -p["yakin_kotak"]):
            nilai, i = max(((iou(p["kotak"], self.jalur[i][-1]["kotak"]), i) for i in self.aktif if i not in terpakai),
                           default=(0.0, None))
            if i is None or nilai < self.iou_ikut:
                self.jalur.append([])
                i = len(self.jalur) - 1
                self.aktif.append(i)
            terpakai.add(i)
            self.jalur[i].append({**p, "detik": detik})


def simpan_potongan_terbesar(jalur):
    """Hanya penampakan dengan kotak terbesar yang menyimpan potongannya (untuk lembar), supaya memori tidak tumbuh."""
    berpotongan = [p for p in jalur if "potongan" in p]
    if len(berpotongan) > 1:
        terbesar = max(berpotongan, key=luas)
        for p in berpotongan:
            if p is not terbesar:
                del p["potongan"]


def gabung(tampak, min_setuju=MIN_SETUJU, bagian_setuju=BAGIAN_SETUJU):
    """Penampakan satu jalur -> satu bacaan (spec 2.1 langkah 4 dan 5): teks, status ("yakin"/"ragu"), jumlah bacaan yang
    mendukung teks itu, jumlah bacaan sesuai pola, jumlah penampakan."""
    sah = [(urai(p["teks"]).teks, p["yakin_baca"]) for p in tampak if urai(p["teks"])]
    if not sah:
        return {"teks": "", "status": "ragu", "setuju": 0, "sah": 0, "tampak": len(tampak)}
    hitung, jumlah_yakin = Counter(), Counter()
    for teks, yakin in sah:
        hitung[teks] += 1
        jumlah_yakin[teks] += yakin
    teks = max(hitung, key=lambda t: (hitung[t], jumlah_yakin[t]))
    setuju = hitung[teks]
    status = "yakin" if setuju >= min_setuju and setuju >= bagian_setuju * len(sah) else "ragu"
    return {"teks": teks, "status": status, "setuju": setuju, "sah": len(sah), "tampak": len(tampak)}


def detik_yakin(tampak, min_setuju=MIN_SETUJU, bagian_setuju=BAGIAN_SETUJU):
    """Detik video dari penampakan pertama sampai bacaan gabungan pertama kali "yakin"; None bila tidak pernah."""
    for k in range(1, len(tampak) + 1):
        if gabung(tampak[:k], min_setuju, bagian_setuju)["status"] == "yakin":
            return round(tampak[k - 1]["detik"] - tampak[0]["detik"], 3)
    return None


def jalankan_video(jalur_video, cari, baca, ambang, per_detik=SAMPEL_PER_DETIK, cari_kendaraan=None, cara="saring", letak=None,
                   maks_kendaraan=None, cadangan_utuh=False, varian="v0", rapikan=0.0):
    """Satu video -> (jalur penampakan, waktu, tersaring). cari(gambar) -> [(x1, y1, x2, y2, yakin)]; baca(potongan) -> (teks,
    yakin). waktu: milidetik dekode dan cari per gambar sampel, kendaraan, dan baca per potongan. tersaring: jumlah kotak plat
    yang dibuang tahap kendaraan ("kendaraan") dan saringan letak ("letak").
    cari_kendaraan (K39): tiap penampakan mencatat jenis kendaraannya. cara "saring" (Rencana 19): kendaraan dicari hanya di gambar
    yang punya kotak plat, dan kotak plat yang tengahnya tidak di dalam kendaraan dibuang. cara "potong" (Rencana 20): kendaraan
    dicari di tiap gambar sampel, dan plat dicari di dalam potongan kendaraan (cari_dalam_kendaraan). letak (Rencana 21): nama
    aturan di letak.ATURAN; kotak yang tidak lolos dibuang sebelum dibaca. maks_kendaraan dan cadangan_utuh (Rencana 25): hanya
    untuk cara "potong" dengan tahap kendaraan, lihat kendaraan.cari_dalam_kendaraan."""
    if cara not in CARA:
        raise ValueError(f"cara harus salah satu dari {CARA}, bukan {cara}")
    if (maks_kendaraan is not None or cadangan_utuh) and not (cari_kendaraan is not None and cara == "potong"):
        raise ValueError("maks_kendaraan dan cadangan_utuh hanya untuk cara potong dengan tahap kendaraan")
    if varian not in VARIAN:
        raise ValueError(f"varian potongan harus salah satu dari {sorted(VARIAN)}, bukan {varian}")
    if rapikan < 0:
        raise ValueError(f"konteks rapikan tidak boleh negatif, bukan {rapikan}")
    if letak is not None and letak not in ATURAN_LETAK:
        raise ValueError(f"aturan letak tidak dikenal: {letak}")
    video = cv2.VideoCapture(str(jalur_video))
    if not video.isOpened():
        raise OSError("video tidak bisa dibuka")
    fps = fps_sah(video.get(cv2.CAP_PROP_FPS))
    langkah = langkah_sampel(fps, per_detik)
    pelacak = Pelacak()
    waktu = {"dekode": [], "kendaraan": [], "cari": [], "baca": []}
    tersaring = {"kendaraan": 0, "letak": 0}
    nomor = 0
    try:
        while True:
            if nomor % langkah:
                if not video.grab():
                    break
                nomor += 1
                continue
            mulai = time.perf_counter()
            ada, gambar = video.read()
            if not ada:
                break
            waktu["dekode"].append(1000 * (time.perf_counter() - mulai))
            if cari_kendaraan is not None and cara == "potong":
                mulai = time.perf_counter()
                kendaraan = cari_kendaraan(gambar)
                waktu["kendaraan"].append(1000 * (time.perf_counter() - mulai))
                mulai = time.perf_counter()
                kotak = cari_dalam_kendaraan(gambar, kendaraan, cari, ambang, maks_kendaraan=maks_kendaraan,
                                             cadangan_utuh=cadangan_utuh)
                waktu["cari"].append(1000 * (time.perf_counter() - mulai))
            else:
                mulai = time.perf_counter()
                kotak = [k for k in cari(gambar) if k[4] >= ambang]
                waktu["cari"].append(1000 * (time.perf_counter() - mulai))
            if cari_kendaraan is not None and cara == "saring" and kotak:
                mulai = time.perf_counter()
                kotak, buang = saring(kotak, cari_kendaraan(gambar))
                waktu["kendaraan"].append(1000 * (time.perf_counter() - mulai))
                tersaring["kendaraan"] += buang
            if rapikan and kotak:
                mulai = time.perf_counter()
                kotak = [rapikan_kotak(gambar, k, cari, ambang, rapikan) for k in kotak]
                waktu["cari"][-1] += 1000 * (time.perf_counter() - mulai)
            if letak is not None and kotak:
                kotak, buang = saring_letak(kotak, letak)
                tersaring["letak"] += buang
            penampakan = []
            for k in kotak:
                mulai = time.perf_counter()
                if varian == "v0":
                    p = potong(gambar, k)
                    if p is None:
                        continue
                    mulai = time.perf_counter()
                    teks, yakin = baca(p)
                else:
                    hasil = baca_tahan_geser(gambar, k, baca, varian)
                    if hasil is None:
                        continue
                    teks, yakin, p = hasil
                waktu["baca"].append(1000 * (time.perf_counter() - mulai))
                penampakan.append({"kotak": tuple(float(x) for x in k[:4]), "yakin_kotak": float(k[4]), "teks": str(teks),
                                   "yakin_baca": float(yakin), "potongan": p, "gambar": nomor, "ketajaman": ketajaman(p),
                                   "tinggi": int(p.shape[0]),
                                   "kendaraan": k[5] if len(k) > 5 else None,
                                   "kotak_kendaraan": k[6] if len(k) > 6 else None})
            pelacak.tambah(nomor / fps, penampakan)
            for i in pelacak.aktif:
                simpan_potongan_terbesar(pelacak.jalur[i])
            nomor += 1
    finally:
        video.release()
    return pelacak.jalur, waktu, tersaring


def daftar_video(manifes, sudut=SUDUT, hanya=None):
    isi = json.loads(Path(manifes).read_text(encoding="utf-8"))
    return [v for v in isi["video"] if v.get("sudut") in sudut and (hanya is None or v["berkas"] in hanya)]


def pilih_berkas(pembagian, sisi):
    """Berkas video satu sisi dari pembagian-video-fase1.json (tools/bagi-video.mjs)."""
    if sisi not in ("uji", "latih"):
        raise ValueError(f"sisi harus uji atau latih, bukan {sisi}")
    return set(json.loads(Path(pembagian).read_text(encoding="utf-8"))[sisi])


def _ms(daftar):
    if not daftar:
        return None
    return {"n": len(daftar), "median": round(float(np.median(daftar)), 2), "p95": round(float(np.percentile(daftar, 95)), 2)}


def jalankan_semua(manifes, folder_video, cari, baca, ambang, keluar, hanya=None, sisi=None, simpan_penampakan=False,
                   cari_kendaraan=None, cara="saring", letak=None, simpan_bacaan=False, maks_kendaraan=None, cadangan_utuh=False,
                   varian="v0", rapikan=0.0, per_detik=SAMPEL_PER_DETIK):
    """Semua video bersudut SUDUT di manifes (dibatasi `hanya` bila ada). Kembali: ringkasan (hitungan dan waktu saja).
    simpan_penampakan: tiap jalur (juga yang terlihat sekali) ditulis ke penampakan.jsonl sebagai nomor gambar dan kotak,
    tanpa teks, untuk dataset pencari plat (Rencana 19), dengan daftar `kendaraan` yang sejajar (kotak dan jenis kendaraan per
    penampakan, atau null; Rencana 21). cari_kendaraan: tahap kendaraan (K39); ambangnya dicatat dari
    atribut `ambang`-nya, dan caranya (saring atau potong, Rencana 20) dicatat bila tahap ini menyala. simpan_bacaan (Rencana 23):
    tiap kedatangan ditulis ke bacaan.jsonl sebagai [gambar, teks, yakin_baca, ketajaman, tinggi potongan] per penampakan, untuk
    menilai varian penggabungan tanpa menjalankan model lagi. Berkas itu memuat plat (data/; agen tidak membukanya)."""
    keluar = Path(keluar)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    semua_waktu = {"dekode": [], "kendaraan": [], "cari": [], "baca": []}
    per_video, baris, tampak_baris, bacaan_baris = [], [], [], []
    for urutan, v in enumerate(daftar_video(manifes, hanya=hanya), 1):
        jalur, waktu, tersaring = jalankan_video(Path(folder_video) / v["berkas"], cari, baca, ambang,
                                                 per_detik=per_detik,
                                                 cari_kendaraan=cari_kendaraan, cara=cara, letak=letak,
                                                 maks_kendaraan=maks_kendaraan, cadangan_utuh=cadangan_utuh, varian=varian,
                                                 rapikan=rapikan)
        tiba = [j for j in jalur if len(j) >= MIN_TAMPAK]
        nomor_jalur = {id(j): n for n, j in enumerate(tiba, 1)}
        for nomor, j in enumerate(tiba, 1):
            nama = f"{Path(v['berkas']).stem}-{nomor}.png"
            cv2.imwrite(str(keluar / "potongan" / nama), next(p["potongan"] for p in j if "potongan" in p))
            baris.append({"video": v["berkas"], "kategori": v["kategori"], "sudut": v["sudut"], "nomor": nomor, **gabung(j),
                          "detik_mulai": round(j[0]["detik"], 3), "detik_yakin": detik_yakin(j), "potongan": nama,
                          "yakin_kotak": round(float(np.mean([p["yakin_kotak"] for p in j])), 3),
                          "kendaraan": Counter(p.get("kendaraan") for p in j).most_common(1)[0][0]})
            if simpan_bacaan:
                bacaan_baris.append({"video": v["berkas"], "kedatangan": nomor,
                                     "bacaan": [[p["gambar"], p["teks"], round(p["yakin_baca"], 4), round(p["ketajaman"], 1),
                                                 p["tinggi"]] for p in j]})
        if simpan_penampakan:
            for i, j in enumerate(jalur):
                tampak_baris.append({"video": v["berkas"], "jalur": i, "kedatangan": nomor_jalur.get(id(j)),
                                     "tampak": [[p["gambar"], *(round(x, 1) for x in p["kotak"])] for p in j],
                                     "kendaraan": [[*(round(x, 1) for x in p["kotak_kendaraan"]), p["kendaraan"]]
                                                   if p.get("kotak_kendaraan") else None for p in j]})
        per_video.append({"urutan": urutan, "kategori": v["kategori"], "sudut": v["sudut"], "gambar_sampel": len(waktu["dekode"]),
                          "penampakan": sum(len(j) for j in jalur), "kedatangan": len(tiba),
                          "tampak_sekali": len(jalur) - len(tiba), "tersaring_kendaraan": tersaring["kendaraan"],
                          "tersaring_letak": tersaring["letak"]})
        for k in semua_waktu:
            semua_waktu[k] += waktu[k]
    with open(keluar / "kedatangan.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    if simpan_penampakan:
        with open(keluar / "penampakan.jsonl", "w") as berkas:
            for t in tampak_baris:
                berkas.write(json.dumps(t) + "\n")
    if simpan_bacaan:
        with open(keluar / "bacaan.jsonl", "w") as berkas:
            for t in bacaan_baris:
                berkas.write(json.dumps(t) + "\n")
    yakin = [b for b in baris if b["status"] == "yakin"]
    ringkasan = {
        # ⛔ Laju yang DIPAKAI, bukan konstantanya. Dulu ini mencatat SAMPEL_PER_DETIK apa adanya, jadi jalan
        # dengan laju lain tetap tercatat 5 — kelas cacat yang sama dengan resolusi video yang tercatat dari
        # sumber: angka pengukuran yang menyesatkan tanpa ada yang tahu sebabnya.
        "aturan": {"sampel_per_detik": per_detik, "ambang_kotak": ambang, "iou_ikut": IOU_IKUT,
                   "jeda_maks_detik": JEDA_MAKS_DETIK, "min_tampak": MIN_TAMPAK, "min_setuju": MIN_SETUJU,
                   "bagian_setuju": BAGIAN_SETUJU, "margin": MARGIN,
                   "ambang_kendaraan": getattr(cari_kendaraan, "ambang", None),
                   "cara_kendaraan": cara if cari_kendaraan is not None else None, "letak": letak,
                   "maks_kendaraan": maks_kendaraan, "cadangan_utuh": bool(cadangan_utuh), "varian_potong": varian,
                   "rapikan": float(rapikan)},
        "sisi": sisi, "video": len(per_video), "gambar_sampel": sum(v["gambar_sampel"] for v in per_video),
        "kedatangan": len(baris), "yakin": len(yakin), "ragu": len(baris) - len(yakin),
        "tampak_sekali": sum(v["tampak_sekali"] for v in per_video),
        "tersaring_kendaraan": sum(v["tersaring_kendaraan"] for v in per_video),
        "tersaring_letak": sum(v["tersaring_letak"] for v in per_video),
        "per_kategori": {k: sum(b["kategori"] == k for b in baris) for k in sorted({b["kategori"] for b in baris})},
        "detik_yakin": _ms([b["detik_yakin"] for b in yakin]),
        "waktu_ms": {k: _ms(x) for k, x in semua_waktu.items()},
        "per_video": per_video,
    }
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=1))
    return ringkasan


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Rantai utuh di video riset (Rencana 14).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    j = perintah.add_parser("jalan")
    for nama in ("manifes", "folder_video", "folder_pencari", "folder_baca", "folder_unduhan", "keluar"):
        j.add_argument(nama)
    j.add_argument("--utas", type=int, default=UTAS)
    j.add_argument("--pembagian")
    j.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    j.add_argument("--ambang", type=float)
    j.add_argument("--simpan-penampakan", action="store_true")
    j.add_argument("--kendaraan", help="folder pencari kendaraan (K39); tanpa ini tahap kendaraan mati")
    j.add_argument("--cara", choices=CARA, default="saring", help="saring (Rencana 19) atau potong (Rencana 20)")
    j.add_argument("--letak", choices=sorted(ATURAN_LETAK), help="aturan letak plat di kendaraan (Rencana 21)")
    j.add_argument("--simpan-bacaan", action="store_true", help="bacaan per gambar ke bacaan.jsonl (Rencana 23)")
    j.add_argument("--maks-kendaraan", type=int, help="cara potong: hanya sekian kendaraan terdekat (Rencana 25, K45)")
    j.add_argument("--cadangan-utuh", action="store_true",
                   help="cara potong: plat dicari di gambar utuh bila tidak ada kendaraan cukup tinggi (Rencana 25)")
    j.add_argument("--varian-potong", choices=sorted(VARIAN), default="v0",
                   help="pembaca tahan geser: v0 cara lama, v1 3 potongan, v2 7 potongan (Rencana 26)")
    j.add_argument("--rapikan", type=float, default=0.0,
                   help="konteks pencarian kedua di sekitar tiap kotak plat, kali ukuran kotak; 0 = mati (Rencana 27)")
    j.add_argument("--sampel-per-detik", type=int, default=SAMPEL_PER_DETIK, dest="sampel_per_detik",
                   help="gambar per detik video yang diperiksa (bawaan %(default)s). Perangkat gerbang yang lemah "
                        "tidak sanggup laju tinggi: di company-ai satu gambar butuh 1 detik, jadi lajunya paling "
                        "banyak sekitar 1 (Rencana T9). Laju yang dipakai dicatat di ringkasan")
    p = pengurai.parse_args(argumen)
    try:
        import onnx_fpo
        from kendaraan import PencariKendaraan
        from pencari_yolox import PencariYolox

        hanya = pilih_berkas(p.pembagian, p.sisi) if p.pembagian else None
        cari = PencariYolox(p.folder_pencari, utas=p.utas)
        cari_kendaraan = PencariKendaraan(p.kendaraan, utas=p.utas) if p.kendaraan else None
        pembaca = onnx_fpo.PembacaOnnxMesin(p.folder_baca, p.folder_unduhan, utas=p.utas)
        ambang = p.ambang if p.ambang is not None else json.loads((Path(p.folder_pencari) / "mesin.json").read_text())["ambang_validasi"]
        r = jalankan_semua(p.manifes, p.folder_video, cari, pembaca.dengan_yakin, ambang, p.keluar, hanya=hanya,
                           sisi=p.sisi if p.pembagian else None, simpan_penampakan=p.simpan_penampakan,
                           cari_kendaraan=cari_kendaraan, cara=p.cara, letak=p.letak, simpan_bacaan=p.simpan_bacaan,
                           maks_kendaraan=p.maks_kendaraan, cadangan_utuh=p.cadangan_utuh, varian=p.varian_potong,
                           rapikan=p.rapikan, per_detik=p.sampel_per_detik)
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"{r['video']} video, {r['gambar_sampel']} gambar sampel; {r['kedatangan']} kedatangan ({r['yakin']} yakin, "
          f"{r['ragu']} ragu); {r['tampak_sekali']} jalur terlihat sekali; {r['tersaring_kendaraan']} kotak plat di luar "
          f"kendaraan dibuang; {r['tersaring_letak']} dibuang aturan letak")
    waktu = ", ".join(f"{k} {v['median']}" for k, v in r["waktu_ms"].items() if v)
    print(f"median ms (utas {p.utas}): {waktu}; detik sampai yakin: {r['detik_yakin']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
