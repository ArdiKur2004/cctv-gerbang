"""Pemeriksa dataset YOLO dari luar (Rencana 28, K53), di lab tanpa jaringan, sesudah arsipnya dibuka buka_arsip.py.

periksa: keamanan dan kebenaran, hitungan saja.
- Keamanan:
  - jenis tiap gambar dicek dari isinya (JPEG FF D8 FF, PNG 89 50 4E 47), bukan dari akhirannya;
  - tanda berkas program (MZ, ELF, #!, arsip PK, PDF, Mach-O) di awal berkas apa pun dihitung;
  - berkas teks harus UTF-8 tanpa byte nol;
  - data.yaml dibaca dengan yaml.safe_load: tag Python ditolak dan tidak pernah dijalankan;
  - tiap gambar didekode utuh.
- Kebenaran: daftar kelas dari data.yaml. Per sisi (train, valid, test): gambar, label, gambar tanpa label, label tanpa gambar, label
  kosong, kotak sah (hanya dari label yang punya gambar), baris rusak (bukan 5 angka), kelas di luar daftar, koordinat di luar 0-1, kotak
  berukuran nol (cacat diperiksa di semua label). Kotak dan gambar per kelas. Gambar kembar persis (SHA-256 isi) di dalam sisi dan antarsisi, dan gambar mirip (dHash 64 bit sama) antarsisi, yang berarti
  kebocoran latih/uji. Ukuran gambar (terkecil, tengah, terbesar).
- Dua susunan dikenali (jenis_tugas): "deteksi" (<sisi>/images dan <sisi>/labels, YOLO) dan "klasifikasi" (<sisi>/<kelas>/<gambar>,
  "Folder Structure" Roboflow, tanpa label). Untuk klasifikasi, kelas dari nama folder; per sisi dihitung gambar dan gambar di luar folder
  kelas.
lembar: untuk OWNER, paling banyak `per_kelas` potongan kotak (deteksi) atau gambar utuh (klasifikasi) per kelas, bernomor baris dan bertulis nama kelasnya. Owner menyebut nomor
baris yang labelnya salah. lembar.json memetakan nomor baris ke berkas; berkas itu dan gambar lembar memuat kendaraan dan plat orang, jadi
agen tidak membukanya (CLAUDE.md §4, §7).

Nama berkas TIDAK pernah dicetak atau ditulis ke ringkasan (bisa memuat nomor plat). Yang dicetak hanya hitungan dan nama kelas.

  periksa: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/periksa_dataset.py periksa <folder dataset> <ringkasan.json>
  lembar:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/periksa_dataset.py lembar <folder dataset> <folder lembar> [--per-kelas 3]
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)

SISI = ("train", "valid", "test")
GAMBAR = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png"}
TEKS = {".txt", ".yaml", ".yml", ".md", ".csv", ".json"}
TANDA_PROGRAM = (b"MZ", b"\x7fELF", b"#!", b"PK\x03\x04", b"%PDF", b"\xca\xfe\xba\xbe", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf")
BATAS = 1e-6
MARGIN_LEMBAR = 0.1
TINGGI_POTONGAN = 96
LEBAR_KARTU = 640
PER_HALAMAN = 24


def jenis_isi(kepala):
    """Jenis berkas dari byte awalnya: jpeg, png, program, atau lain."""
    if kepala.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if kepala.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if kepala.startswith(TANDA_PROGRAM):
        return "program"
    return "lain"


def dhash(gambar):
    """dHash 64 bit dari gambar kelabu yang dikecilkan ke 9 x 8."""
    kecil = cv2.resize(cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY), (9, 8), interpolation=cv2.INTER_AREA)
    bit = (kecil[:, 1:] > kecil[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bit), 2)


def baca_kelas(folder):
    """(daftar nama kelas atau None, yaml aman). data.yaml dibaca dengan safe_load; tag Python membuatnya ditolak."""
    berkas = Path(folder) / "data.yaml"
    if not berkas.exists():
        return None, True
    try:
        isi = yaml.safe_load(berkas.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError):
        return None, False
    nama = isi.get("names") if isinstance(isi, dict) else None
    if isinstance(nama, dict):
        nama = [nama[k] for k in sorted(nama)]
    return ([str(n) for n in nama] if isinstance(nama, list) else None), True


def baris_label(teks, nc):
    """Satu baris label YOLO -> ("sah", kelas, (cx, cy, w, h)) atau (jenis cacat, None, None)."""
    bagian = teks.split()
    try:
        angka = [float(x) for x in bagian]
    except ValueError:
        return "baris_rusak", None, None
    if len(angka) != 5:
        return "baris_rusak", None, None
    kelas = angka[0]
    if kelas != int(kelas) or kelas < 0 or (nc is not None and kelas >= nc):
        return "kelas_di_luar_daftar", None, None
    if any(v < -BATAS or v > 1 + BATAS for v in angka[1:]):
        return "koordinat_di_luar", None, None
    if angka[3] <= 0 or angka[4] <= 0:
        return "kotak_nol", None, None
    return "sah", int(kelas), tuple(angka[1:])


def jenis_tugas(folder):
    """"deteksi" bila ada <sisi>/images atau <sisi>/labels; "klasifikasi" bila <sisi> berisi folder kelas; selain itu "tak_dikenal"."""
    folder = Path(folder)
    if any((folder / s / "images").exists() or (folder / s / "labels").exists() for s in SISI):
        return "deteksi"
    if any((folder / s).is_dir() and any(p.is_dir() for p in (folder / s).iterdir()) for s in SISI):
        return "klasifikasi"
    return "tak_dikenal"


def _gambar_klasifikasi(folder):
    """{sisi: {kelas: [jalur gambar]}} dan {sisi: jumlah gambar langsung di bawah folder sisi (di luar folder kelas)}."""
    per, lepas = {}, {}
    for s in SISI:
        if not (folder / s).is_dir():
            continue
        per[s] = {k.name: [p for p in sorted(k.iterdir()) if p.suffix.lower() in GAMBAR]
                  for k in sorted(x for x in (folder / s).iterdir() if x.is_dir())}
        lepas[s] = sum(1 for p in (folder / s).iterdir() if p.is_file() and p.suffix.lower() in GAMBAR)
    return per, lepas


def _pasangan(folder, sisi):
    gambar = {p.stem: p for p in sorted((folder / sisi / "images").glob("*")) if p.suffix.lower() in GAMBAR} \
        if (folder / sisi / "images").exists() else {}
    label = {p.stem: p for p in sorted((folder / sisi / "labels").glob("*.txt"))} if (folder / sisi / "labels").exists() else {}
    return gambar, label


def periksa(folder):
    """Kembali: ringkasan (hitungan dan nama kelas saja)."""
    folder = Path(folder)
    kelas, yaml_aman = baca_kelas(folder)
    nc = len(kelas) if kelas is not None else None
    aman = {"berkas": 0, "jenis_tidak_cocok": 0, "tanda_program": 0, "teks_tidak_bersih": 0, "gambar_rusak": 0, "yaml_aman": yaml_aman}
    akhiran = Counter()
    for p in sorted(x for x in folder.rglob("*") if x.is_file()):
        aman["berkas"] += 1
        akhiran[p.suffix.lower()] += 1
        isi = p.read_bytes()
        jenis = jenis_isi(isi[:16])
        aman["tanda_program"] += int(jenis == "program")
        if p.suffix.lower() in GAMBAR and jenis != GAMBAR[p.suffix.lower()]:
            aman["jenis_tidak_cocok"] += 1
        if p.suffix.lower() in TEKS:
            try:
                isi.decode("utf-8")
                bersih = b"\x00" not in isi
            except UnicodeDecodeError:
                bersih = False
            aman["teks_tidak_bersih"] += int(not bersih)
    aman["akhiran"] = dict(sorted(akhiran.items()))
    tugas = jenis_tugas(folder)
    if tugas == "klasifikasi":
        return _periksa_klasifikasi(folder, aman)

    nama_kelas = (lambda i: kelas[i]) if kelas is not None else str
    per_kelas = {k: {"kotak": 0, "gambar": 0} for k in (kelas or [])}
    sisi_hasil, lebar, tinggi = {}, [], []
    sha, dh = {}, {}
    for s in SISI:
        gambar, label = _pasangan(folder, s)
        if not gambar and not label:
            continue
        r = {"gambar": len(gambar), "label": len(label), "gambar_tanpa_label": len(set(gambar) - set(label)),
             "label_tanpa_gambar": len(set(label) - set(gambar)), "label_kosong": 0, "kotak": 0, "baris_rusak": 0,
             "kelas_di_luar_daftar": 0, "koordinat_di_luar": 0, "kotak_nol": 0}
        for stem, berkas in label.items():
            baris = [b for b in berkas.read_text(encoding="utf-8", errors="replace").splitlines() if b.strip()]
            r["label_kosong"] += int(not baris)
            kelas_gambar = set()
            for b in baris:
                jenis, k, _ = baris_label(b, nc)
                if jenis != "sah":
                    r[jenis] += 1
                    continue
                if stem not in gambar:  # kotak tanpa gambar tidak bisa dipakai: cacatnya tetap diperiksa, tetapi tidak dihitung
                    continue
                r["kotak"] += 1
                pk = per_kelas.setdefault(nama_kelas(k), {"kotak": 0, "gambar": 0})
                pk["kotak"] += 1
                kelas_gambar.add(nama_kelas(k))
            for n in kelas_gambar:
                per_kelas[n]["gambar"] += 1
        for berkas in gambar.values():
            g = cv2.imread(str(berkas))
            if g is None:
                aman["gambar_rusak"] += 1
                continue
            tinggi.append(int(g.shape[0]))
            lebar.append(int(g.shape[1]))
            sha.setdefault(hashlib.sha256(berkas.read_bytes()).hexdigest(), []).append(s)
            dh.setdefault(dhash(g), set()).add(s)
        sisi_hasil[s] = r
    return {"jenis_tugas": tugas, "keamanan": aman, "kelas": kelas, "sisi": sisi_hasil, "per_kelas": per_kelas,
            "kembar": _kembar(sha, dh), "ukuran_gambar": {"lebar": _ringkas(lebar), "tinggi": _ringkas(tinggi)}}


def _ringkas(x):
    return [min(x), int(np.median(x)), max(x)] if x else None


def _kembar(sha, dh):
    """sha: {sha256: [sisi tiap salinan]}; dh: {dHash: {sisi}}."""
    return {"persis_dalam_sisi": sum(n - 1 for daftar in sha.values() for n in Counter(daftar).values() if n > 1),
            "persis_antar_sisi": sum(len(set(daftar)) > 1 for daftar in sha.values()),
            "mirip_antar_sisi": sum(len(v) > 1 for v in dh.values())}


def _periksa_klasifikasi(folder, aman):
    """Susunan klasifikasi: kelas dari nama folder (gabungan semua sisi). aman sudah dihitung, gambar_rusak diisi di sini."""
    per, lepas = _gambar_klasifikasi(folder)
    kelas = sorted({k for d in per.values() for k in d})
    per_kelas = {k: {"gambar": 0} for k in kelas}
    sisi_hasil, lebar, tinggi, sha, dh = {}, [], [], {}, {}
    for s, d in per.items():
        sisi_hasil[s] = {"gambar": sum(len(v) for v in d.values()), "gambar_tanpa_kelas": lepas[s]}
        for k, daftar in d.items():
            per_kelas[k]["gambar"] += len(daftar)
            for berkas in daftar:
                g = cv2.imread(str(berkas))
                if g is None:
                    aman["gambar_rusak"] += 1
                    continue
                tinggi.append(int(g.shape[0]))
                lebar.append(int(g.shape[1]))
                sha.setdefault(hashlib.sha256(berkas.read_bytes()).hexdigest(), []).append(s)
                dh.setdefault(dhash(g), set()).add(s)
    return {"jenis_tugas": "klasifikasi", "keamanan": aman, "kelas": kelas, "sisi": sisi_hasil, "per_kelas": per_kelas,
            "kembar": _kembar(sha, dh), "ukuran_gambar": {"lebar": _ringkas(lebar), "tinggi": _ringkas(tinggi)}}


def _kartu(nomor, nama, potongan):
    kartu = np.full((TINGGI_POTONGAN + 24, LEBAR_KARTU, 3), 255, np.uint8)
    cv2.putText(kartu, f"{nomor}. {nama}", (8, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    if potongan is not None and potongan.size:
        skala = TINGGI_POTONGAN / potongan.shape[0]
        lebar = min(LEBAR_KARTU - 260, max(1, int(potongan.shape[1] * skala)))
        kecil = cv2.resize(potongan, (lebar, TINGGI_POTONGAN), interpolation=cv2.INTER_AREA)
        kartu[12:12 + TINGGI_POTONGAN, 250:250 + lebar] = kecil
    cv2.line(kartu, (0, kartu.shape[0] - 1), (LEBAR_KARTU, kartu.shape[0] - 1), (180, 180, 180), 1)
    return kartu


def buat_lembar(folder, keluar, per_kelas=3, benih=0):
    """Lembar contoh per kelas untuk owner: potongan kotak (deteksi) atau gambar utuh (klasifikasi). Kembali: hitungan saja."""
    folder, keluar = Path(folder), Path(keluar)
    if jenis_tugas(folder) == "klasifikasi":
        per, _ = _gambar_klasifikasi(folder)
        kelas = sorted({k for d in per.values() for k in d})
        kotak = {i: [(s, b, None) for s, d in per.items() for b in d.get(k, [])] for i, k in enumerate(kelas)}
    else:
        kelas, yaml_aman = baca_kelas(folder)
        if not yaml_aman or kelas is None:
            raise ValueError("data.yaml tidak bisa dibaca dengan aman; lembar tidak dibuat")
        kotak = {i: [] for i in range(len(kelas))}
        for s in SISI:
            gambar, label = _pasangan(folder, s)
            for stem, berkas in label.items():
                if stem not in gambar:
                    continue
                for b in berkas.read_text(encoding="utf-8", errors="replace").splitlines():
                    jenis, k, kt = baris_label(b, len(kelas)) if b.strip() else ("kosong", None, None)
                    if jenis == "sah":
                        kotak[k].append((s, gambar[stem], kt))
    rng = np.random.default_rng(benih)
    baris, kartu = [], []
    for k, daftar in kotak.items():
        pilih = sorted(rng.choice(len(daftar), size=min(per_kelas, len(daftar)), replace=False)) if daftar else []
        for i in pilih:
            s, berkas, kt = daftar[i]
            g = cv2.imread(str(berkas))
            potongan = g
            if g is not None and kt is not None:
                cx, cy, w, h = kt
                t, l = g.shape[:2]
                x1, x2 = int(max(0, (cx - w * (0.5 + MARGIN_LEMBAR)) * l)), int(min(l, (cx + w * (0.5 + MARGIN_LEMBAR)) * l))
                y1, y2 = int(max(0, (cy - h * (0.5 + MARGIN_LEMBAR)) * t)), int(min(t, (cy + h * (0.5 + MARGIN_LEMBAR)) * t))
                potongan = g[y1:max(y1 + 1, y2), x1:max(x1 + 1, x2)]
            nomor = len(baris) + 1
            kartu.append(_kartu(nomor, kelas[k], potongan))
            baris.append({"nomor": nomor, "kelas": kelas[k], "sisi": s, "berkas": str(berkas.relative_to(folder)),
                          "kotak": [round(v, 6) for v in kt] if kt is not None else None})
    keluar.mkdir(parents=True, exist_ok=True)
    halaman = []
    for awal in range(0, len(kartu), PER_HALAMAN):
        nama = f"lembar-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(kartu[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    (keluar / "lembar.json").write_text(json.dumps({"per_kelas": per_kelas, "benih": benih, "halaman": halaman, "baris": baris},
                                                   indent=1, ensure_ascii=False))
    return {"baris": len(baris), "kelas": sum(1 for d in kotak.values() if d), "halaman": len(halaman)}


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Pemeriksa dataset YOLO dari luar (Rencana 28).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("periksa")
    a.add_argument("folder")
    a.add_argument("keluar_json")
    b = perintah.add_parser("lembar")
    b.add_argument("folder")
    b.add_argument("keluar")
    b.add_argument("--per-kelas", type=int, default=3)
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "periksa":
            r = periksa(p.folder)
            Path(p.keluar_json).write_text(json.dumps(r, indent=1, ensure_ascii=False))
            print(f"keamanan {json.dumps(r['keamanan'])}")
            print(f"kelas ({len(r['kelas']) if r['kelas'] else 0}): {r['kelas']}")
            print(f"sisi {json.dumps(r['sisi'])}")
            print(f"kembar {json.dumps(r['kembar'])}; ukuran gambar {json.dumps(r['ukuran_gambar'])}")
        else:
            r = buat_lembar(p.folder, p.keluar, p.per_kelas)
            print(f"{r['baris']} baris dari {r['kelas']} kelas, {r['halaman']} halaman. Lembar memuat kendaraan dan plat: hanya owner "
                  "yang membukanya.")
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
