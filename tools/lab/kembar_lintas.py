"""Kendaraan yang sama di kedua sisi, dikenali dari GAMBARNYA (K24): gambar yang nyaris kembar dan label yang hanya beda
sedikit (dugaan salah ketik label pada kendaraan yang sama).

Diukur 14 Okt (Rencana 7): pasangan gambar berplat beda hampir tak pernah berjarak dHash <= 12 (0 dari 20.000 sampel
acak), sedangkan 11% pasangan gambar berplat sama berjarak <= 4. Lintas sisi, dari 177 pasangan berjarak <= 8, 27
berlabel beda 1-2 huruf (dugaan kendaraan yang sama) dan 150 berlabel beda 3 huruf atau lebih (dugaan potongan plat yang
kebetulan mirip). Jadi aturannya dua syarat sekaligus.

Aturan: bila sebuah gambar latih dan sebuah gambar uji berjarak dHash <= BATAS_GAMBAR dan labelnya berjarak sunting
<= BATAS_LABEL, seluruh kedatangan LATIH itu dikeluarkan. Set uji tidak diubah (sudah dibetulkan di Rencana 6). Salah
keluarkan hanya membuang sedikit bahan latih; salah biarkan membuat angka mesin tampak lebih bagus dari kenyataan.

Keluaran: pembagian.json (memuat plat; tinggal di data/) dan ringkasan.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/kembar_lintas.py /kerja/data/keluaran/set-uji-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/kembar
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

# OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr, dan pada INDO-ALPR jalur itu nomor plat: dibisukan.
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

BATAS_GAMBAR = 8
BATAS_LABEL = 2


def dhash(jalur):
    """Sidik gambar 64 bit (selisih terang mendatar pada gambar kelabu 9x8), atau None bila gambar tak terbaca."""
    kelabu = cv2.imread(str(jalur), cv2.IMREAD_GRAYSCALE)
    if kelabu is None:
        return None
    kecil = cv2.resize(kelabu, (9, 8), interpolation=cv2.INTER_AREA).astype(np.int16)
    return int(np.packbits((kecil[:, 1:] > kecil[:, :-1]).flatten()).view(">u8")[0])


def sunting(a, b):
    """Jarak sunting (Levenshtein) antara dua teks."""
    sebelum = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        kini = [i]
        for j, y in enumerate(b, 1):
            kini.append(min(sebelum[j] + 1, kini[j - 1] + 1, sebelum[j - 1] + (x != y)))
        sebelum = kini
    return sebelum[-1]


def buang_kembar(pembagian, folder_gambar):
    """Kembali: (pembagian tanpa plat latih yang kembar dengan plat uji, hitungan tanpa nomor plat)."""
    sidik, tak_terbaca = {}, 0
    for s in ("latih", "uji"):
        sidik[s] = []
        for i, k in enumerate(pembagian[s]):
            for b in k["berkas"]:
                h = dhash(Path(folder_gambar) / b)
                if h is None:
                    tak_terbaca += 1
                else:
                    sidik[s].append((i, h))
    nilai_latih = np.array([h for _, h in sidik["latih"]], dtype=np.uint64)
    indeks_latih = np.array([i for i, _ in sidik["latih"]], dtype=np.int64)
    mirip, kembar, buang = 0, 0, set()
    for j, h in sidik["uji"]:
        jarak = np.unpackbits(np.bitwise_xor(nilai_latih, np.uint64(h)).view(np.uint8).reshape(-1, 8), axis=1).sum(axis=1)
        for i in indeks_latih[jarak <= BATAS_GAMBAR]:
            mirip += 1
            if sunting(pembagian["uji"][j]["teks"], pembagian["latih"][int(i)]["teks"]) <= BATAS_LABEL:
                kembar += 1
                buang.add(int(i))
    baru = {"latih": [k for i, k in enumerate(pembagian["latih"]) if i not in buang], "uji": pembagian["uji"]}
    hitung = {"aturan": {"batas_gambar_dhash": BATAS_GAMBAR, "batas_label_sunting": BATAS_LABEL},
              "gambar_tak_terbaca": tak_terbaca, "pasangan_mirip": mirip, "pasangan_kembar": kembar,
              "latih_dikeluarkan": len(buang), "kedatangan": {s: len(baru[s]) for s in ("latih", "uji")}}
    return baru, hitung


def utama(berkas_pembagian, folder_gambar, keluar):
    baru, hitung = buang_kembar(json.loads(Path(berkas_pembagian).read_text()), folder_gambar)
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian.json").write_text(json.dumps(baru, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(hitung, indent=2))
    print(f"pasangan gambar mirip (dHash <= {BATAS_GAMBAR}): {hitung['pasangan_mirip']}; "
          f"di antaranya berlabel beda <= {BATAS_LABEL} huruf (dugaan kendaraan sama): {hitung['pasangan_kembar']}")
    print(f"latih dikeluarkan: {hitung['latih_dikeluarkan']}; sisa latih {hitung['kedatangan']['latih']}, "
          f"uji {hitung['kedatangan']['uji']}; gambar tak terbaca {hitung['gambar_tak_terbaca']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python kembar_lintas.py <pembagian.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
