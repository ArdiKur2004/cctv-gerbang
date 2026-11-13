"""Dataset YOLO satu kelas "kendaraan" untuk pencari kendaraan jualan (Rencana 32, K48).

bangun(sumber, keluar, guru, bahan): untuk tiap gambar sumber,
- kotak berkelas yang diminta (mis. cars, motorcyle, truck) ditulis sebagai kelas 0; kelas lain (plat) dibuang dan dihitung; baris yang
  bukan 5 angka (poligon) dilewati dan dihitung;
- label dilengkapi kotak guru (pencari kendaraan COCO sekarang) yang yakin >= AMBANG_GURU dan IoU < IOU_GURU dengan semua kotak label,
  karena dataset Roboflow praktis melabeli satu kendaraan utama per gambar dan kendaraan lain di gambar yang sama tak berlabel;
- sumber tanpa label kendaraan ("kelas": None, mis. bingkai CCTV) hanya memakai kotak guru;
- "batas_per_kelas" {sisi tujuan: N}: paling banyak N gambar per kelas (kelas kotak label pertama), dipilih menurut SHA-256
  "<awalan>/<sisi sumber>/<nama>" supaya tetap sama tiap kali dibangun;
- nama berkas baru "<awalan>-<16 huruf SHA-256 nama asli>.<akhiran>": nama asli bisa memuat nomor plat dan tidak ditulis ke mana pun.
Susunan sumber: [{"folder", "awalan", "kelas": [nomor kelas] | None, "sisi": {sisi tujuan: [sisi sumber]}, "batas_per_kelas"?}].
ringkasan.json: hitungan per sumber per sisi tujuan, ambang guru, dan bahan (bahan yang diberikan + "bobot-yolox" karena guru ikut
membentuk label). Gambar dan label memuat kendaraan dan plat: agen tidak membukanya.

  bangun: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/dataset_kendaraan.py bangun <susunan.json> <keluar> /kerja/data/keluaran/kendaraan-yolox-coco
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from deteksi import AKHIRAN, iou  # noqa: E402
from kendaraan import PencariKendaraan  # noqa: E402

AMBANG_GURU = 0.4  # lebih tinggi dari ambang rantai 0,25: kotak guru menjadi label, jadi yang meragukan tidak dipakai
IOU_GURU = 0.5
BAHAN_GURU = "bobot-yolox"


def _baca_label(berkas, kelas, lebar, tinggi, hitung):
    """Baris label YOLO -> [(kelas, (x1, y1, x2, y2) piksel)] untuk kelas yang diminta; yang lain dihitung di `hitung`."""
    hasil = []
    if not berkas.exists():
        return hasil
    for baris in berkas.read_text().splitlines():
        angka = baris.split()
        if not angka:
            continue
        if len(angka) != 5:
            hitung["poligon_dilewati"] += 1
            continue
        k, cx, cy, w, h = int(float(angka[0])), *(float(x) for x in angka[1:])
        if k not in kelas:
            hitung["kotak_kelas_lain"] += 1
            continue
        hasil.append((k, ((cx - w / 2) * lebar, (cy - h / 2) * tinggi, (cx + w / 2) * lebar, (cy + h / 2) * tinggi)))
    return hasil


def _baris_yolo(kotak, lebar, tinggi):
    x1, y1, x2, y2 = max(0.0, kotak[0]), max(0.0, kotak[1]), min(float(lebar), kotak[2]), min(float(tinggi), kotak[3])
    if x2 - x1 < 2 or y2 - y1 < 2:
        return None
    return f"0 {(x1 + x2) / 2 / lebar:.6f} {(y1 + y2) / 2 / tinggi:.6f} {(x2 - x1) / lebar:.6f} {(y2 - y1) / tinggi:.6f}"


def _kelas_pertama(berkas, kelas):
    if kelas is None or not berkas.exists():
        return "-"
    for baris in berkas.read_text().splitlines():
        angka = baris.split()
        if len(angka) == 5 and int(float(angka[0])) in kelas:
            return int(float(angka[0]))
    return "-"


def _daftar(s, tujuan):
    """[(sisi sumber, jalur gambar)] untuk satu sisi tujuan, sesudah batas per kelas; dan jumlah yang dibatasi."""
    folder, awalan, kelas = Path(s["folder"]), s["awalan"], s.get("kelas")
    semua = []
    for sisi in s["sisi"][tujuan]:
        folder_gambar = folder / sisi / "images"
        if folder_gambar.exists():
            semua += [(sisi, p) for p in sorted(folder_gambar.iterdir()) if p.suffix.lower() in AKHIRAN]
    batas = (s.get("batas_per_kelas") or {}).get(tujuan)
    if batas is None:
        return semua, 0
    urut = sorted(semua, key=lambda x: hashlib.sha256(f"{awalan}/{x[0]}/{x[1].name}".encode()).hexdigest())
    per_kelas, pilih = {}, []
    for sisi, p in urut:
        k = _kelas_pertama(folder / sisi / "labels" / f"{p.stem}.txt", kelas)
        if per_kelas.get(k, 0) < batas:
            per_kelas[k] = per_kelas.get(k, 0) + 1
            pilih.append((sisi, p))
    return pilih, len(semua) - len(pilih)


def bangun(sumber, keluar, guru, bahan):
    """Kembali: ringkasan (hitungan saja), juga ditulis ke <keluar>/ringkasan.json."""
    if not bahan:
        raise ValueError("bahan dataset harus disebut (untuk manifes mesin jualan)")
    keluar = Path(keluar)
    if keluar.exists():
        raise FileExistsError("folder keluaran sudah ada; dipindah atau dihapus dengan sadar sebelum membangun lagi")
    ringkas = {"sumber": {}, "guru": {"ambang": AMBANG_GURU, "iou": IOU_GURU},
               "bahan": list(bahan) + ([BAHAN_GURU] if BAHAN_GURU not in bahan else [])}
    for s in sumber:
        folder, awalan, kelas = Path(s["folder"]), s["awalan"], s.get("kelas")
        for tujuan in s["sisi"]:
            (keluar / tujuan / "images").mkdir(parents=True, exist_ok=True)
            (keluar / tujuan / "labels").mkdir(parents=True, exist_ok=True)
            daftar, dibatasi = _daftar(s, tujuan)
            h = {"gambar": 0, "kotak_label": 0, "kotak_guru": 0, "poligon_dilewati": 0, "kotak_kelas_lain": 0, "dibatasi": dibatasi,
                 "tak_terbaca": 0}
            for sisi, p in daftar:
                g = cv2.imread(str(p))
                if g is None:
                    h["tak_terbaca"] += 1
                    continue
                tinggi, lebar = g.shape[:2]
                label = [] if kelas is None else _baca_label(folder / sisi / "labels" / f"{p.stem}.txt", kelas, lebar, tinggi, h)
                kotak = [k for _, k in label]
                tambah = [v[:4] for v in guru(g) if v[4] >= AMBANG_GURU and all(iou(v[:4], k) < IOU_GURU for k in kotak)]
                baris = [b for b in (_baris_yolo(k, lebar, tinggi) for k in kotak + tambah) if b]
                nama = f"{awalan}-{hashlib.sha256(f'{sisi}/{p.name}'.encode()).hexdigest()[:16]}"
                shutil.copyfile(p, keluar / tujuan / "images" / f"{nama}{p.suffix.lower()}")
                (keluar / tujuan / "labels" / f"{nama}.txt").write_text("".join(b + "\n" for b in baris))
                h["gambar"] += 1
                h["kotak_label"] += len(kotak)
                h["kotak_guru"] += len(tambah)
            ringkas["sumber"].setdefault(awalan, {})[tujuan] = h
    (keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=1))
    return ringkas


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Dataset pencari kendaraan jualan satu kelas (Rencana 32).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("bangun")
    for nama in ("susunan", "keluar", "folder_guru"):
        b.add_argument(nama)
    b.add_argument("--utas", type=int, default=4)
    p = pengurai.parse_args(argumen)
    try:
        susunan = json.loads(Path(p.susunan).read_text())
        r = bangun(susunan["sumber"], p.keluar, PencariKendaraan(p.folder_guru, utas=p.utas), susunan["bahan"])
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    for awalan, per_sisi in r["sumber"].items():
        for tujuan, h in per_sisi.items():
            print(f"{awalan} -> {tujuan}: {json.dumps(h)}")
    print(f"bahan {r['bahan']}; guru {r['guru']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
