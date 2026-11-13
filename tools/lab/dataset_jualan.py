"""Dataset pencari plat JUALAN (Rencana 24 Bagian B Task 9), format YOLO seperti plat-lighting, untuk tools/lab/latih_yolox.py.

Bahan BOLEH-PRODUK saja:
- plat-lighting: train ke train, valid ke valid; test hanya ke folder ukur;
- tangkapan owner (K44, label.json dari halaman_label.terima): gambar sisi latih ke train, atau ke valid bila validasi_gambar
  (1 dari BAGIAN_VALIDASI gambar menurut SHA-256). Semua kotak plat menjadi label, juga yang tak terbaca, karena itu tetap plat.
  Kotak bukan plat tidak berlabel (contoh negatif). Gambar yang masih punya plat tanpa label dikeluarkan, supaya plat itu tidak
  diajarkan sebagai latar. Gambar sisi uji hanya masuk folder ukur;
- plat buatan (tempel_per_gambar > 0): tiap gambar train mendapat salinan bernama "-tempel<n>" dengan 1-3 plat buatan
  (dataset_cctv.tempel) yang tidak menimpa kotak plat yang ada.

- dataset tambahan (Rencana 25, tambah=<folder YOLO>, mis. cctv-fase1 untuk melatih lanjut cctv1): gambar train dan valid
  disalin ke sisi yang sama dengan awalan "x-", labelnya apa adanya, kecuali yang berawalan "pl-" (plat-lighting sudah masuk
  dari folder plat-lighting; jangan kembar). Bahannya wajib disebut (tambah_bahan) dan digabung ke daftar bahan. Dengan
  tanpa_negatif_tambah, gambar tambahan TANPA KOTAK di train dilewati (Rencana 19: gambar itu bisa menyembunyikan plat yang tak
  pernah ditemukan, sehingga plat diajarkan sebagai latar). Valid tidak pernah dikurangi, supaya calon dengan dan tanpa gambar
  itu dinilai di validasi yang sama.

Folder ukur-plat-lighting/ dan ukur-tangkapan/ masing-masing berisi valid/ (salinan valid gabungan, untuk memilih ambang) dan test/,
untuk deteksi.nilai. Gambar dinamai nomor gambar (t-g0001), tidak pernah nama asli. Keluaran memuat plat: agen tidak membukanya;
ringkasan.json hitungan saja, beserta daftar bahan untuk manifes mesin.

  bangun: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/dataset_jualan.py bangun /kerja/data/keluaran/dataset/plat-lighting /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca/peta-berkas.json /kerja/data/keluaran/label-tangkapan/label.json /kerja/data/keluaran/dataset/jualan-d1 [--tempel 1]
  lanjutan cctv1 (Rencana 25): ... /kerja/data/keluaran/dataset/cctv2-c1 --tambah /kerja/data/keluaran/dataset/cctv-fase1 --tambah-bahan video-riset-youtube,plat-buatan [--tanpa-negatif-tambah]
  tambah-latih (Rencana 29): powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/dataset_jualan.py tambah-latih /kerja/data/keluaran/dataset/cctv3 /kerja/data/keluaran/dataset/roboflow-vehicle-license-plate-v3 --kelas 0 --bahan dataset-roboflow-vehicle-license-plate
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
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from dataset_cctv import tempel, tulis  # noqa: E402
from deteksi import AKHIRAN, baca_label, iou  # noqa: E402

BAGIAN_VALIDASI = 5
COBA_TEMPEL = 10


def validasi_gambar(gambar):
    """Gambar tangkapan latih masuk valid bila SHA-256 "valid/<gambar>" habis dibagi BAGIAN_VALIDASI."""
    return int(hashlib.sha256(f"valid/{gambar}".encode()).hexdigest()[:8], 16) % BAGIAN_VALIDASI == 0


def _siapkan_folder(folder):
    for sub in ("images", "labels"):
        (folder / sub).mkdir(parents=True, exist_ok=True)


def _salin_pl(asal, tujuan):
    """Gambar plat-lighting satu sisi disalin dengan awalan "pl-". Kembali: [(nama, gambar, kotak)] untuk tempel."""
    _siapkan_folder(tujuan)
    hasil = []
    for g in sorted(p for p in (asal / "images").iterdir() if p.suffix.lower() in AKHIRAN):
        label = asal / "labels" / f"{g.stem}.txt"
        shutil.copy(g, tujuan / "images" / f"pl-{g.name}")
        (tujuan / "labels" / f"pl-{g.stem}.txt").write_text(label.read_text() if label.exists() else "")
        hasil.append((f"pl-{g.stem}", g, label))
    return hasil


def _tempel_salinan(gambar, kotak, rng):
    """Salinan dengan 1-3 plat buatan yang tidak menimpa kotak yang ada. Kembali: (gambar, kotak lama + baru)."""
    kotak = list(kotak)
    for _ in range(int(rng.integers(1, 4))):
        for _ in range(COBA_TEMPEL):
            hasil, k = tempel(gambar, rng)
            if all(iou(k, x) == 0 for x in kotak):
                gambar = hasil
                kotak.append(k)
                break
    return gambar, kotak


def _salin_tambah(asal, tujuan, tanpa_negatif):
    """Satu sisi dataset tambahan -> tujuan dengan awalan "x-", tanpa gambar "pl-". Kembali: hitungan."""
    _siapkan_folder(tujuan)
    h = {"gambar": 0, "kotak_plat": 0, "negatif_dilewati": 0}
    for g in sorted(p for p in (asal / "images").iterdir() if p.suffix.lower() in AKHIRAN):
        if g.name.startswith("pl-"):
            continue
        label = asal / "labels" / f"{g.stem}.txt"
        isi = label.read_text() if label.exists() else ""
        kotak = len(baca_label(label, 1, 1)) if label.exists() else 0
        if tanpa_negatif and kotak == 0:
            h["negatif_dilewati"] += 1
            continue
        shutil.copy(g, tujuan / "images" / f"x-{g.name}")
        (tujuan / "labels" / f"x-{g.stem}.txt").write_text(isi)
        h["gambar"] += 1
        h["kotak_plat"] += kotak
    return h


def bangun(folder_plat_lighting, folder_capture, peta_berkas, label_json, keluar, tempel_per_gambar=0, benih=0, tambah=None,
           tambah_bahan=(), tanpa_negatif_tambah=False):
    """Kembali: hitungan saja, juga ditulis ke ringkasan.json."""
    if tambah is not None and not tambah_bahan:
        raise ValueError("dataset tambahan wajib menyebut bahannya (tambah_bahan), supaya tanda mesin benar")
    pl, keluar = Path(folder_plat_lighting), Path(keluar)
    peta = json.loads(Path(peta_berkas).read_text())
    label = json.loads(Path(label_json).read_text())["gambar"]
    hitung = {s: {"gambar_asli": 0, "kotak_plat": 0, "gambar_tempel": 0} for s in ("train", "valid")}
    hitung.update({"ukur_tangkapan": 0, "ukur_plat_lighting": 0, "dikeluarkan_plat_tanpa_label": 0})
    rng = np.random.default_rng(benih)

    latar = {"train": [], "valid": []}
    for s in ("train", "valid"):
        for nama, g, lb in _salin_pl(pl / s, keluar / s):
            gambar = cv2.imread(str(g))
            kotak = baca_label(lb, gambar.shape[1], gambar.shape[0]) if lb.exists() else []
            latar[s].append((nama, gambar, kotak))
    _siapkan_folder(keluar / "ukur-tangkapan" / "test")
    for g in sorted(label):
        v = label[g]
        if v["plat_tanpa_label"]:
            hitung["dikeluarkan_plat_tanpa_label"] += 1
            continue
        gambar = cv2.imread(str(Path(folder_capture) / peta[g]))
        if gambar is None:
            raise ValueError("ada gambar yang tak bisa dibuka")
        kotak = [tuple(float(x) for x in p["kotak"]) for p in v["plat"]]
        if v["sisi"] == "uji":
            tulis(gambar, kotak, keluar / "ukur-tangkapan" / "test", f"t-{g}")
            hitung["ukur_tangkapan"] += 1
            continue
        s = "valid" if validasi_gambar(g) else "train"
        tulis(gambar, kotak, keluar / s, f"t-{g}")
        latar[s].append((f"t-{g}", gambar, kotak))

    for s in ("train", "valid"):
        hitung[s]["gambar_asli"] = len(latar[s])
        hitung[s]["kotak_plat"] = sum(len(k) for _, _, k in latar[s])
    for nama, gambar, kotak in latar["train"]:
        for n in range(1, tempel_per_gambar + 1):
            hasil, semua = _tempel_salinan(gambar, kotak, rng)
            tulis(hasil, semua, keluar / "train", f"{nama}-tempel{n}")
            hitung["train"]["gambar_tempel"] += 1

    tambahan = None
    if tambah is not None:
        tambahan = {s: _salin_tambah(Path(tambah) / s, keluar / s, tanpa_negatif_tambah and s == "train")
                    for s in ("train", "valid")}

    hitung["ukur_plat_lighting"] = len(_salin_pl(pl / "test", keluar / "ukur-plat-lighting" / "test"))
    for ukur in ("ukur-tangkapan", "ukur-plat-lighting"):
        if (keluar / ukur / "valid").exists():
            shutil.rmtree(keluar / ukur / "valid")
        shutil.copytree(keluar / "valid", keluar / ukur / "valid")
    bahan = ["dataset-plat-lighting", "tangkapan-owner"] + (["plat-buatan"] if hitung["train"]["gambar_tempel"] else [])
    bahan += [b for b in dict.fromkeys(tambah_bahan) if b not in bahan]
    hasil = {**hitung, "tempel_per_gambar": tempel_per_gambar, "benih": benih, "bahan": bahan}
    if tambahan is not None:
        hasil.update({"tambah": tambahan, "tanpa_negatif_tambah": bool(tanpa_negatif_tambah)})
    (keluar / "ringkasan.json").write_text(json.dumps(hasil, indent=1))
    return hasil


def _kotak_dipakai(baris, kelas):
    """Satu baris label YOLO -> ((cx, cy, w, h), poligon?) bila kelasnya dipakai, selain itu None. Poligon (kelas + pasangan x y)
    diubah menjadi kotak pembungkusnya."""
    try:
        angka = [float(x) for x in baris.split()]
    except ValueError:
        return None
    if not angka or angka[0] != int(angka[0]) or int(angka[0]) not in kelas:
        return None
    if len(angka) == 5:
        cx, cy, w, h = angka[1:]
        poligon = False
    elif len(angka) >= 7 and len(angka) % 2 == 1:
        xs, ys = angka[1::2], angka[2::2]
        x1, x2, y1, y2 = max(0.0, min(xs)), min(1.0, max(xs)), max(0.0, min(ys)), min(1.0, max(ys))
        cx, cy, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
        poligon = True
    else:
        return None
    if w <= 0 or h <= 0 or not all(0 <= v <= 1 for v in (cx, cy, w, h)):
        return None
    return (cx, cy, w, h), poligon


def tambah_ke_latih(folder_dataset, folder_tambah, kelas, bahan, awalan="r-"):
    """Rencana 29 (K56): gambar dari SEMUA sisi dataset YOLO tambahan masuk `train` berawalan `awalan`, hanya dengan kotak berkelas di
    `kelas` (ditulis sebagai kelas 0; poligon menjadi kotak pembungkus). Gambar tanpa kotak terpakai dilewati, karena bisa menyembunyikan
    plat tak berlabel. `valid` tidak disentuh, supaya soal memilih tetap sama. Kembali: hitungan, juga dicatat di ringkasan.json."""
    if not bahan:
        raise ValueError("dataset tambahan wajib menyebut bahannya, supaya tanda mesin benar")
    folder_dataset, folder_tambah, kelas = Path(folder_dataset), Path(folder_tambah), set(kelas)
    tujuan = folder_dataset / "train"
    if not (tujuan / "images").exists():
        raise ValueError("folder dataset tanpa train/images")
    if any(p.name.startswith(awalan) for p in (tujuan / "images").iterdir()):
        raise ValueError(f"train sudah memuat gambar berawalan {awalan}; tidak ditambah dua kali")
    h = {"gambar": 0, "kotak": 0, "poligon": 0, "dilewati_tanpa_kotak": 0}
    for sisi in ("train", "valid", "test"):
        if not (folder_tambah / sisi / "images").exists():
            continue
        for g in sorted(p for p in (folder_tambah / sisi / "images").iterdir() if p.suffix.lower() in AKHIRAN):
            label = folder_tambah / sisi / "labels" / f"{g.stem}.txt"
            pakai = [k for k in (_kotak_dipakai(b, kelas) for b in (label.read_text().splitlines() if label.exists() else []))
                     if k is not None]
            if not pakai:
                h["dilewati_tanpa_kotak"] += 1
                continue
            shutil.copy(g, tujuan / "images" / f"{awalan}{g.name}")
            (tujuan / "labels" / f"{awalan}{g.stem}.txt").write_text(
                "".join(f"0 {cx:.6f} {cy:.6f} {w:.6f} {hh:.6f}\n" for (cx, cy, w, hh), _ in pakai))
            h["gambar"] += 1
            h["kotak"] += len(pakai)
            h["poligon"] += sum(p for _, p in pakai)
    ringkas = json.loads((folder_dataset / "ringkasan.json").read_text())
    ringkas.setdefault("tambah_latih", []).append({"awalan": awalan, "kelas": sorted(kelas), **h})
    ringkas["bahan"] = ringkas["bahan"] + [b for b in dict.fromkeys(bahan) if b not in ringkas["bahan"]]
    (folder_dataset / "ringkasan.json").write_text(json.dumps(ringkas, indent=1))
    return h


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Dataset pencari plat jualan (Rencana 24 Task 9).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("bangun")
    for nama in ("folder_plat_lighting", "folder_capture", "peta_berkas", "label_json", "keluar"):
        b.add_argument(nama)
    b.add_argument("--tempel", type=int, default=0)
    b.add_argument("--benih", type=int, default=0)
    b.add_argument("--tambah", help="dataset YOLO tambahan (Rencana 25), mis. cctv-fase1")
    b.add_argument("--tambah-bahan", type=lambda t: [x for x in t.split(",") if x], default=[])
    b.add_argument("--tanpa-negatif-tambah", action="store_true", help="gambar tambahan tanpa kotak di train dilewati")
    t = perintah.add_parser("tambah-latih", help="dataset YOLO tambahan ke train saja, kelas tertentu (Rencana 29)")
    t.add_argument("folder_dataset")
    t.add_argument("folder_tambah")
    t.add_argument("--kelas", type=lambda x: [int(v) for v in x.split(",") if v], required=True)
    t.add_argument("--bahan", type=lambda x: [v for v in x.split(",") if v], required=True)
    t.add_argument("--awalan", default="r-")
    p = pengurai.parse_args(argumen)
    if p.perintah == "tambah-latih":
        try:
            r = tambah_ke_latih(p.folder_dataset, p.folder_tambah, p.kelas, p.bahan, p.awalan)
        except (OSError, ValueError, KeyError) as galat:
            print(f"GAGAL: {type(galat).__name__}")
            return 1
        print(f"ditambahkan ke train: {r}")
        return 0
    try:
        r = bangun(p.folder_plat_lighting, p.folder_capture, p.peta_berkas, p.label_json, p.keluar, p.tempel, p.benih,
                   tambah=p.tambah, tambah_bahan=p.tambah_bahan, tanpa_negatif_tambah=p.tanpa_negatif_tambah)
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    print(f"train {r['train']}; valid {r['valid']}; ukur tangkapan {r['ukur_tangkapan']}, plat-lighting {r['ukur_plat_lighting']}; "
          f"dikeluarkan (plat tanpa label) {r['dikeluarkan_plat_tanpa_label']}; tambahan {r.get('tambah')}; bahan {r['bahan']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
