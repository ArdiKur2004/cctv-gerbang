"""Potongan kendaraan beserta label jenis dan warna, untuk pengenal ciri (Rencana 33, spec Fase 3 tahap 1).

bangun(owner, sumber, keluar, bahan) menulis `<keluar>/potongan/*.png`, `<keluar>/ciri.csv` (berkas, sumber, sisi, lalu satu kolom per
ciri di CIRI: jenis, warna, merek), dan `<keluar>/ringkasan.json` (hitungan saja).

- **Label owner** (`data/keluaran/label-ciri/ciri.json`, dari halaman ciri Rencana 31): satu potongan per kartu. Dibuang dan dihitung:
  kartu yang owner tandai "kotak tidak pas" (potongannya tidak mewakili satu kendaraan), kartu yang belum lengkap, dan kartu
  "bukan kendaraan". Ciri yang dijawab "tak yakin" ditulis kosong, dan ciri lain di kartu itu tetap dipakai. Kartu sisi latih dibagi tetap
  menurut SHA-256 id kartu (1 dari BAGIAN_VALIDASI ke validasi); kartu sisi uji menjadi sisi uji.
- **Dataset Roboflow:** satu potongan per kotak. "jenis_kelas" memetakan nomor kelas ke jenis (kelas lain, mis. plat, dilewati dan
  dihitung); "jenis_tetap" memberi jenis yang sama untuk semua kotak; "warna_dari_nama" mengambil kata terakhir nama kelas di data.yaml
  dan memetakannya lewat WARNA_DARI_KATA (nama dua warna seperti "Biru-Putih" tidak dipetakan, dibuang dan dihitung). Merek (Rencana 34)
  dari "merek_kelas" {nama kelas: merek}, lalu "merek_kata_pertama" (mis. "Honda_Beat_Hitam" -> Honda), lalu "merek_sisa" untuk kelas yang
  tidak dipetakan (mis. "lainnya"); tanpa "merek_sisa" barisnya dibuang dan dihitung, sama seperti warna.
- Kotak yang sisinya kurang dari MIN_SISI piksel dilewati: warna dan jenis tidak bisa dinilai dari potongan sekecil itu.
- "batas_per_kelas" {sisi: N}: paling banyak N potongan per nomor kelas, dipilih menurut SHA-256 supaya tetap sama tiap kali dibangun.
- Nama berkas baru dari SHA-256 asal potongan: nama berkas tangkapan dan dataset bisa memuat nomor plat.

Potongan memuat kendaraan dan plat: agen tidak membukanya (`CLAUDE.md` §4). Layar hanya hitungan.

  bangun: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/potongan_ciri.py bangun <susunan.json> <keluar>
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import cv2
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from deteksi import AKHIRAN  # noqa: E402

MIN_SISI = 24  # piksel
BAGIAN_VALIDASI = 4
TAK_YAKIN = "tak_yakin"
BUKAN_KENDARAAN = "bukan_kendaraan"
CIRI = ("jenis", "warna", "merek")
WARNA_DARI_KATA = {"hitam": "hitam", "merah": "merah", "putih": "putih", "kuning": "kuning", "hijau": "hijau", "silver": "abu_perak"}


def sisi_owner(id_kartu, sisi_kartu):
    """Kartu sisi uji tetap uji; kartu sisi latih dibagi tetap menjadi latih dan validasi."""
    if sisi_kartu == "uji":
        return "uji"
    acak = int(hashlib.sha256(f"validasi-ciri/{id_kartu}".encode()).hexdigest()[:8], 16)
    return "validasi" if acak % BAGIAN_VALIDASI == 0 else "latih"


def warna_dari_kelas(nama_kelas):
    """Nama kelas Roboflow (mis. "Honda_Beat_Silver") -> warna, atau None bila katanya tidak dikenal (mis. "Biru-Putih")."""
    return WARNA_DARI_KATA.get(str(nama_kelas).rsplit("_", 1)[-1].strip().lower())


def merek_dari_kelas(nama_kelas, peta=None, kata_pertama=False, sisa=None):
    """Nama kelas Roboflow -> merek (Rencana 34). Urutannya: peta nama kelas (mis. {"agya": "Toyota"}), lalu kata pertama nama kelas
    (mis. "Honda_Beat_Hitam" -> "Honda"), lalu `sisa` (mis. "lainnya"). None berarti tidak terpetakan."""
    nama = str(nama_kelas).strip()
    if peta and nama in peta:
        return peta[nama]
    if kata_pertama and nama:
        return nama.split("_", 1)[0]
    return sisa


class _Penulis:
    """Menulis potongan dan baris CSV, dan menghitung per sisi dan per kelas."""

    def __init__(self, keluar):
        self.keluar = Path(keluar)
        (self.keluar / "potongan").mkdir(parents=True, exist_ok=True)
        self.baris = []

    def tulis(self, gambar, kotak, asal, awalan, sisi, nilai):
        """nilai: {ciri: label atau None}. Kembali: True bila potongannya cukup besar dan ditulis."""
        tinggi, lebar = gambar.shape[:2]
        x1, y1 = max(0, int(kotak[0])), max(0, int(kotak[1]))
        x2, y2 = min(lebar, int(kotak[2])), min(tinggi, int(kotak[3]))
        if x2 - x1 < MIN_SISI or y2 - y1 < MIN_SISI:
            return False
        nama = f"potongan/{awalan}-{hashlib.sha256(asal.encode()).hexdigest()[:16]}.png"
        cv2.imwrite(str(self.keluar / nama), gambar[y1:y2, x1:x2])
        self.baris.append({"berkas": nama, "sumber": awalan, "sisi": sisi, **{c: nilai.get(c) or "" for c in CIRI}})
        return True

    def simpan(self):
        with open(self.keluar / "ciri.csv", "w", newline="") as f:
            tulis = csv.DictWriter(f, ["berkas", "sumber", "sisi", *CIRI])
            tulis.writeheader()
            tulis.writerows(self.baris)


def _hitung_baru():
    return {"potongan": 0, "per_sisi": {}, "per_kelas": {c: {} for c in CIRI}}


def _catat(hitung, sisi, nilai):
    hitung["potongan"] += 1
    hitung["per_sisi"][sisi] = hitung["per_sisi"].get(sisi, 0) + 1
    for ciri in CIRI:
        if nilai.get(ciri):
            hitung["per_kelas"][ciri][nilai[ciri]] = hitung["per_kelas"][ciri].get(nilai[ciri], 0) + 1


def _dari_owner(owner, penulis):
    hitung = {**_hitung_baru(), "dibuang": {"kotak_tidak_pas": 0, "bukan_kendaraan": 0, "belum_lengkap": 0, "terlalu_kecil": 0,
                                            "tak_terbaca": 0},
              "tak_yakin": {c: 0 for c in CIRI}}
    peta = json.loads(Path(owner["peta"]).read_text())
    kendaraan = json.loads(Path(owner["ciri_json"]).read_text())["kendaraan"]
    simpanan = {}
    for k in kendaraan:
        if k.get("kotak_tidak_pas"):
            hitung["dibuang"]["kotak_tidak_pas"] += 1
            continue
        if not k.get("lengkap"):
            hitung["dibuang"]["belum_lengkap"] += 1
            continue
        if k.get("jenis") == BUKAN_KENDARAAN:
            hitung["dibuang"]["bukan_kendaraan"] += 1
            continue
        nilai = {}
        for ciri in CIRI:
            v = k.get(ciri)
            if v == TAK_YAKIN:
                hitung["tak_yakin"][ciri] += 1
                v = None
            nilai[ciri] = v
        if k["gambar"] not in simpanan:
            simpanan[k["gambar"]] = cv2.imread(str(Path(owner["capture"]) / peta[k["gambar"]]))
        gambar = simpanan[k["gambar"]]
        if gambar is None:
            hitung["dibuang"]["tak_terbaca"] += 1
            continue
        sisi = sisi_owner(k["id"], k["sisi"])
        if penulis.tulis(gambar, k["kotak"], f"owner/{k['id']}", "o", sisi, nilai):
            _catat(hitung, sisi, nilai)
        else:
            hitung["dibuang"]["terlalu_kecil"] += 1
    return hitung


def _kotak_sumber(s, tujuan):
    """[(kunci urut, sisi sumber, jalur gambar, nomor kelas, kotak piksel)] untuk satu sisi tujuan; ukuran gambar dibaca saat memotong."""
    folder = Path(s["folder"])
    hasil = []
    for sisi in s["sisi"][tujuan]:
        folder_gambar = folder / sisi / "images"
        if not folder_gambar.exists():
            continue
        for p in sorted(folder_gambar.iterdir()):
            if p.suffix.lower() not in AKHIRAN:
                continue
            berkas_label = folder / sisi / "labels" / f"{p.stem}.txt"
            if not berkas_label.exists():
                continue
            for i, b in enumerate(berkas_label.read_text().splitlines()):
                angka = b.split()
                if len(angka) != 5:
                    continue
                asal = f"{s['awalan']}/{sisi}/{p.name}#{i}"
                hasil.append((hashlib.sha256(asal.encode()).hexdigest(), asal, p, int(float(angka[0])),
                              [float(x) for x in angka[1:]]))
    return sorted(hasil)


def _dari_sumber(s, penulis):
    folder = Path(s["folder"])
    nama_kelas = []
    if (folder / "data.yaml").exists():
        nama_kelas = yaml.safe_load((folder / "data.yaml").read_text()).get("names") or []
    jenis_kelas = {int(k): v for k, v in (s.get("jenis_kelas") or {}).items()}
    hitung = {**_hitung_baru(), "kelas_dilewati": 0, "warna_tidak_dipetakan": 0, "merek_tidak_dipetakan": 0, "terlalu_kecil": 0,
              "dibatasi": 0, "tak_terbaca": 0}
    for tujuan in s["sisi"]:
        batas = (s.get("batas_per_kelas") or {}).get(tujuan)
        per_kelas = {}
        for _, asal, p, kelas, (cx, cy, w, h) in _kotak_sumber(s, tujuan):
            jenis = jenis_kelas.get(kelas, s.get("jenis_tetap")) if jenis_kelas else s.get("jenis_tetap")
            if jenis_kelas and kelas not in jenis_kelas:
                hitung["kelas_dilewati"] += 1
                continue
            nama_k = nama_kelas[kelas] if kelas < len(nama_kelas) else ""
            warna = None
            if s.get("warna_dari_nama"):
                warna = warna_dari_kelas(nama_k)
                if warna is None:
                    hitung["warna_tidak_dipetakan"] += 1
                    continue
            merek = None
            if s.get("merek_kelas") or s.get("merek_kata_pertama"):
                merek = merek_dari_kelas(nama_k, s.get("merek_kelas"), s.get("merek_kata_pertama"), s.get("merek_sisa"))
                if merek is None:
                    hitung["merek_tidak_dipetakan"] += 1
                    continue
            if batas is not None and per_kelas.get(kelas, 0) >= batas:
                hitung["dibatasi"] += 1
                continue
            gambar = cv2.imread(str(p))
            if gambar is None:
                hitung["tak_terbaca"] += 1
                continue
            tinggi, lebar = gambar.shape[:2]
            kotak = [(cx - w / 2) * lebar, (cy - h / 2) * tinggi, (cx + w / 2) * lebar, (cy + h / 2) * tinggi]
            nilai = {"jenis": jenis, "warna": warna, "merek": merek}
            if not penulis.tulis(gambar, kotak, asal, s["awalan"], tujuan, nilai):
                hitung["terlalu_kecil"] += 1
                continue
            per_kelas[kelas] = per_kelas.get(kelas, 0) + 1
            _catat(hitung, tujuan, nilai)
    return hitung


def bangun(owner, sumber, keluar, bahan):
    """Kembali: ringkasan (hitungan saja), juga ditulis ke <keluar>/ringkasan.json."""
    if not bahan:
        raise ValueError("bahan harus disebut (untuk manifes mesin jualan)")
    penulis = _Penulis(keluar)
    ringkas = {"bahan": list(bahan), "min_sisi": MIN_SISI, "bagian_validasi": BAGIAN_VALIDASI, "sumber": {}}
    if owner:
        ringkas["owner"] = _dari_owner(owner, penulis)
    for s in sumber or []:
        ringkas["sumber"][s["awalan"]] = _dari_sumber(s, penulis)
    penulis.simpan()
    (Path(keluar) / "ringkasan.json").write_text(json.dumps(ringkas, indent=1))
    return ringkas


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Potongan kendaraan beserta label jenis dan warna (Rencana 33).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("bangun")
    b.add_argument("susunan")
    b.add_argument("keluar")
    p = pengurai.parse_args(argumen)
    try:
        susunan = json.loads(Path(p.susunan).read_text())
        r = bangun(susunan.get("owner"), susunan.get("sumber"), p.keluar, susunan["bahan"])
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    if "owner" in r:
        print(f"owner: {json.dumps(r['owner'])}")
    for awalan, h in r["sumber"].items():
        print(f"{awalan}: {json.dumps(h)}")
    print(f"bahan {r['bahan']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
