"""Lembar ikhtisar gambar kecil untuk memilah video riset (keputusan owner K19).

Agen hanya boleh melihat gambar yang platnya tidak terbaca. Tiap video dicuplik beberapa gambar; tiap gambar dikecilkan
sampai sisi terpanjangnya SISI piksel lalu dikaburkan; hasilnya disusun satu baris per video. Yang tersisa cukup untuk
memilah sudut kamera, siang atau malam, dan jenis kendaraan.

Hitungan di balik angkanya (anggapan terburuk: plat delapan huruf memenuhi lebar layar): pada 48 piksel tiap huruf
mendapat 6 piksel, dan kabur Gauss bersimpangan baku 1,5 piksel menyisakan kurang dari sepersepuluh kontras pada rincian
sehalus goresan huruf. Itu hitungan, bukan bukti: owner memeriksa lembarnya sebelum agen membukanya.

Dijalankan di lab tanpa jaringan:
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil

Gelombang unduhan berikutnya (K20): sebutkan catatan lembar terdahulu di belakangnya, maka video yang sudah pernah
dibuatkan lembar dilewati dan owner hanya memeriksa yang baru:
  ... lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil-2 /kerja/data/keluaran/lembar-kecil/ikhtisar.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

SISI = 48  # sisi terpanjang tiap gambar, piksel
KABUR = 1.5  # simpangan baku kabur Gauss, piksel, diterapkan SESUDAH gambar dikecilkan
PERBESAR = 3  # tiap gambar diperbesar tanpa menambah rincian, supaya enak dilihat
PER_VIDEO = 8  # jumlah gambar per video
PER_HALAMAN = 15  # jumlah video per lembar
LEBAR_NOMOR = 60  # lebar kolom nomor urut di kiri tiap baris, piksel
AKHIRAN_VIDEO = {".mp4", ".webm", ".mkv", ".mov"}


def kecilkan(gambar):
    """Mengecilkan gambar sampai sisi terpanjangnya SISI piksel, lalu mengaburkannya."""
    tinggi, lebar = gambar.shape[:2]
    skala = SISI / max(tinggi, lebar)
    ukuran = (max(1, round(lebar * skala)), max(1, round(tinggi * skala)))
    kecil = cv2.resize(gambar, ukuran, interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(kecil, (0, 0), KABUR)


def cuplik(jalur, jumlah=PER_VIDEO):
    """Mengambil `jumlah` gambar yang tersebar rata dari satu video, masing-masing sudah dikecilkan."""
    baca = cv2.VideoCapture(str(jalur))
    total = int(baca.get(cv2.CAP_PROP_FRAME_COUNT))
    hasil = []
    if total > 0:
        for i in range(jumlah):
            baca.set(cv2.CAP_PROP_POS_FRAMES, int((i + 0.5) * total / jumlah))
            ada, gambar = baca.read()
            if ada:
                hasil.append(kecilkan(gambar))
    baca.release()
    if len(hasil) < jumlah:
        # Sebagian berkas tidak bisa diloncati (aliran HLS di dalam mp4). Baca berurutan dan ambil tiap selang tetap.
        hasil = []
        baca = cv2.VideoCapture(str(jalur))
        selang = max(1, total // jumlah) if total > 0 else 30
        nomor = 0
        while len(hasil) < jumlah:
            ada, gambar = baca.read()
            if not ada:
                break
            if nomor % selang == selang // 2:
                hasil.append(kecilkan(gambar))
            nomor += 1
        baca.release()
    return hasil


def petak(gambar):
    """Menaruh satu gambar kecil di tengah petak bujur sangkar berukuran tetap."""
    besar = cv2.resize(gambar, None, fx=PERBESAR, fy=PERBESAR, interpolation=cv2.INTER_NEAREST)
    sisi = SISI * PERBESAR
    kanvas = np.zeros((sisi, sisi, 3), np.uint8)
    tinggi, lebar = besar.shape[:2]
    atas, kiri = (sisi - tinggi) // 2, (sisi - lebar) // 2
    kanvas[atas:atas + tinggi, kiri:kiri + lebar] = besar
    return kanvas


def baris(nomor, gambar):
    """Satu baris lembar: nomor urut video di kiri, lalu PER_VIDEO petak."""
    sisi = SISI * PERBESAR
    kolom_nomor = np.zeros((sisi, LEBAR_NOMOR, 3), np.uint8)
    cv2.putText(kolom_nomor, str(nomor), (4, sisi // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    kosong = [np.zeros((sisi, sisi, 3), np.uint8)] * (PER_VIDEO - len(gambar))
    return np.hstack([kolom_nomor] + [petak(g) for g in gambar] + kosong)


def sudah_dilembarkan(lembar_lama):
    """Nama video yang sudah ada di catatan lembar terdahulu (berkas ikhtisar.json)."""
    nama = set()
    for jalur in lembar_lama:
        nama.update(v["berkas"] for v in json.loads(Path(jalur).read_text())["video"])
    return nama


def utama(folder, keluar, lembar_lama=()):
    folder, keluar = Path(folder), Path(keluar)
    try:
        lama = sudah_dilembarkan(lembar_lama)
    except (OSError, ValueError, KeyError, TypeError) as galat:
        # Gagal tertutup: tanpa daftar ini, lembar baru akan diam-diam memuat semua video lagi.
        print(f"LEMBAR LAMA TAK TERBACA: {galat!r}. Tidak ada lembar yang dibuat.")
        return 2
    keluar.mkdir(parents=True, exist_ok=True)
    semua = sorted(p for p in folder.iterdir() if p.suffix.lower() in AKHIRAN_VIDEO)
    video = [p for p in semua if p.name not in lama]
    daftar, barisan = [], []
    for nomor, jalur in enumerate(video, 1):
        gambar = cuplik(jalur)
        daftar.append({"nomor": nomor, "berkas": jalur.name, "gambar": len(gambar)})
        barisan.append(baris(nomor, gambar))
    halaman = []
    for awal in range(0, len(barisan), PER_HALAMAN):
        nama = f"ikhtisar-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    catatan = {"sisi": SISI, "kabur": KABUR, "perbesar": PERBESAR, "per_video": PER_VIDEO, "halaman": halaman,
               "dilewati": len(semua) - len(video), "video": daftar}
    (keluar / "ikhtisar.json").write_text(json.dumps(catatan, indent=2))
    print(f"{len(video)} video -> {len(halaman)} lembar di {keluar} ({len(semua) - len(video)} dilewati karena sudah ada di lembar lama)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Pakai: python lembar_kecil.py <folder-video> <folder-keluaran> [ikhtisar-lama.json ...]")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2], sys.argv[3:]))
