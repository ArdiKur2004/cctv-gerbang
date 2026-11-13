"""KONTROL POSITIF: bandingkan QR kita dengan QR rujukan OpenCV, keduanya digambar dengan cara yang SAMA.
Kalau rujukan pun gagal terbaca, yang salah alat ujinya, bukan QR kita."""
import json
import cv2
import numpy as np

SKALA = 8
SUNYI = 4


def gambar(baris_bit, skala=SKALA, sunyi=SUNYI):
    kecil = np.array([[0 if c == "1" else 255 for c in b] for b in baris_bit], dtype=np.uint8)
    besar = np.kron(kecil, np.ones((skala, skala), dtype=np.uint8))
    t, l = besar.shape
    g = np.full((t + 2 * sunyi * skala, l + 2 * sunyi * skala), 255, dtype=np.uint8)
    g[sunyi * skala:sunyi * skala + t, sunyi * skala:sunyi * skala + l] = besar
    return g


pembaca = cv2.QRCodeDetector()

print("=== KONTROL POSITIF: QR rujukan buatan OpenCV, digambar dengan cara kita ===")
for teks in ["A", "TAMU-7PD7HQ"]:
    p = cv2.QRCodeEncoder_Params()
    p.correction_level = cv2.QRCodeEncoder_CORRECT_LEVEL_M
    p.mode = cv2.QRCodeEncoder_MODE_BYTE
    mentah = cv2.QRCodeEncoder_create(p).encode(teks)
    bit = (mentah < 128).astype(np.uint8)
    baris = ["".join(str(int(v)) for v in bit[y]) for y in range(bit.shape[0])]
    terbaca, titik, _ = pembaca.detectAndDecode(gambar(baris))
    print(f"  rujukan {teks!r} ({bit.shape[0]}x{bit.shape[0]}): "
          f"{'TERBACA' if terbaca == teks else 'GAGAL'} -> {terbaca!r}")

print("\n=== QR BUATAN KITA, digambar dengan cara yang sama ===")
with open("/kerja/data/alat-sementara/qr-matriks.json", encoding="utf-8") as f:
    for butir in json.load(f):
        terbaca, titik, _ = pembaca.detectAndDecode(gambar(butir["baris"]))
        print(f"  kita {butir['teks'][:18]!r} (v{butir['versi']}): "
              f"{'TERBACA' if terbaca == butir['teks'] else 'GAGAL'} -> {terbaca!r}")
