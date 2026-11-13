"""Pelabel otomatis dan pembanding pertama untuk langkah "baca huruf": Qwen3-VL-2B lokal, tanpa jaringan.

Membaca tiap gambar set uji (tools/lab/bagi_set_uji.py) lalu membandingkannya dengan label penerbit: per gambar, dan
per kedatangan (bacaan terbanyak dari gambar-gambar berplat sama; seri di puncak = "ragu", bukan tebakan). Hasilnya
mengukur dua hal: seberapa bisa dipercaya pelabel otomatis untuk bahan tanpa label teks (video, dataset pencahayaan),
dan angka pembanding pertama "AI serba-bisa" untuk langkah baca huruf (spec bagian 8.1 langkah 6).

Folder model diverifikasi (tools/lab/model_terkunci.py) SEBELUM torch dan transformers diimpor. Kelas model bawaan
transformers, tanpa trust_remote_code. Jawaban deterministik (tanpa sampling). Angka per kelompok disertai rentang
ketidakpastian 95% (Wilson); kelompok di bawah 30 kedatangan ditulis "terlalu sedikit untuk disimpulkan" (spec 8.3).

Keluaran:
- hasil.jsonl: bacaan tiap gambar. Memuat nomor plat: tinggal di data/, agen tidak membukanya.
- ringkasan.json: hitungan saja. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/baca_vlm.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/models/qwen3-vl-2b-instruct /kerja/data/keluaran/baca-vlm [uji|latih]
"""
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_terkunci import ModelDitolak, daftar_model_hf, verifikasi_folder_model  # noqa: E402
from plat import bersihkan, urai  # noqa: E402

# OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr, dan pada INDO-ALPR jalur itu nomor plat: dibisukan.
# Gambar yang tak terbaca dinilai sebagai bacaan kosong.
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")
SEDIKIT = 30
PERTANYAAN = ("This image shows one Indonesian vehicle license plate. Read the registration number on it and ignore "
              "the small expiry date row. Reply with only the letters and digits of the registration number, "
              "without spaces.")
TOKEN_MAKS = 16
SISI_MAKS = 448
ISIAN = ("kedatangan", "kedatangan_benar", "kedatangan_ragu", "gambar", "gambar_benar", "gambar_luar_pola")
SISI = ("uji", "latih")


def perkecil(gambar, sisi_maks=SISI_MAKS):
    """Perkecil sampai sisi terpanjang <= sisi_maks (tak pernah memperbesar)."""
    tinggi, lebar = gambar.shape[:2]
    skala = sisi_maks / max(tinggi, lebar)
    if skala >= 1.0:
        return gambar
    return cv2.resize(gambar, (max(1, round(lebar * skala)), max(1, round(tinggi * skala))), interpolation=cv2.INTER_AREA)


def matikan_kernel_triton():
    """Asal: vision-seed @3591530 inti/mesin/kernel.py (K14). Image lab tidak punya kompiler C, sedangkan torch mengganti
    beberapa operasi dengan kernel Triton yang dikompilasi saat pertama dipakai. Override itu dicabut lewat jalur resmi
    torch; hasil hitungnya sama."""
    try:
        from torch._native import registry
    except ImportError:
        return False
    registry.deregister_op_overrides(disable_dsl_names="triton")
    return True


class PembacaQwen:
    """Pembaca plat dengan Qwen3-VL. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali teks mentah."""

    def __init__(self, folder_model):
        folder = verifikasi_folder_model(Path(folder_model), daftar_model_hf())

        import torch
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        matikan_kernel_triton()
        self._torch = torch
        self._prosesor = AutoProcessor.from_pretrained(str(folder), local_files_only=True)
        self._model = Qwen3VLForConditionalGeneration.from_pretrained(str(folder), local_files_only=True, dtype=torch.float16)
        self._model.to("cuda").eval()

    def __call__(self, gambar_bgr):
        from PIL import Image

        gambar = Image.fromarray(np.ascontiguousarray(perkecil(gambar_bgr)[..., ::-1]))
        pesan = [{"role": "user", "content": [{"type": "image", "image": gambar}, {"type": "text", "text": PERTANYAAN}]}]
        masukan = self._prosesor.apply_chat_template(pesan, tokenize=True, add_generation_prompt=True, return_dict=True,
                                                     return_tensors="pt").to(self._model.device)
        with self._torch.inference_mode():
            keluar = self._model.generate(**masukan, max_new_tokens=TOKEN_MAKS, do_sample=False)
        return self._prosesor.batch_decode(keluar[:, masukan["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip()


def suara_terbanyak(bacaan):
    """Bacaan yang paling sering; "" (ragu) bila tak ada bacaan atau ada seri di puncak."""
    hitung = Counter(b for b in bacaan if b)
    if not hitung:
        return ""
    urut = hitung.most_common()
    if len(urut) > 1 and urut[1][1] == urut[0][1]:
        return ""
    return urut[0][0]


def wilson(benar, jumlah, z=1.96):
    """Rentang ketidakpastian 95% (Wilson) untuk benar/jumlah; None bila jumlah nol."""
    if jumlah == 0:
        return None
    p = benar / jumlah
    penyebut = 1 + z * z / jumlah
    tengah = (p + z * z / (2 * jumlah)) / penyebut
    lebar = z * math.sqrt(p * (1 - p) / jumlah + z * z / (4 * jumlah * jumlah)) / penyebut
    return max(0.0, tengah - lebar), min(1.0, tengah + lebar)


def ringkas(pembagian, bacaan, sisi="uji"):
    """Hitungan per kelompok dari bacaan bersih per berkas (berkas -> teks), terhadap label sisi `sisi` di `pembagian`
    (bawaan: set uji)."""
    hitung = {k: Counter() for k in KELOMPOK}
    for kedatangan in pembagian[sisi]:
        c = hitung[kedatangan["kelompok"]]
        semua = [bacaan.get(b, "") for b in kedatangan["berkas"]]
        for b in semua:
            c["gambar"] += 1
            c["gambar_benar"] += b == kedatangan["teks"]
            c["gambar_luar_pola"] += urai(b) is None
        akhir = suara_terbanyak(semua)
        c["kedatangan"] += 1
        c["kedatangan_benar"] += akhir == kedatangan["teks"]
        c["kedatangan_ragu"] += akhir == ""
    per_kelompok = {}
    for k in KELOMPOK:
        rentang = wilson(hitung[k]["kedatangan_benar"], hitung[k]["kedatangan"])
        per_kelompok[k] = {**{n: hitung[k][n] for n in ISIAN},
                           "rentang_95_kedatangan": [round(rentang[0], 3), round(rentang[1], 3)] if rentang else None,
                           "terlalu_sedikit": hitung[k]["kedatangan"] < SEDIKIT}
    return per_kelompok


def nilai(pembagian, folder_gambar, baca, sisi="uji"):
    """Membaca semua gambar satu sisi pembagian (bawaan: set uji). Kembali: (baris per gambar, ringkasan tanpa nomor plat)."""
    baris, bacaan, detik = [], {}, 0.0
    for kedatangan in pembagian[sisi]:
        for berkas in kedatangan["berkas"]:
            gambar = cv2.imread(str(Path(folder_gambar) / berkas))
            mulai = time.perf_counter()
            mentah = baca(gambar) if gambar is not None else ""
            detik += time.perf_counter() - mulai
            bacaan[berkas] = bersihkan(mentah)
            baris.append({"berkas": berkas, "kelompok": kedatangan["kelompok"], "label": kedatangan["teks"],
                          "bacaan": bacaan[berkas], "mentah": mentah})
    return baris, {"per_kelompok": ringkas(pembagian, bacaan, sisi),
                   "detik_per_gambar": round(detik / len(baris), 3) if baris else None}


def uraikan(r):
    n, benar = r["kedatangan"], r["kedatangan_benar"]
    if n == 0:
        return "kosong"
    if r["terlalu_sedikit"]:
        kedatangan = f"kedatangan benar {benar} dari {n} (terlalu sedikit untuk disimpulkan)"
    else:
        bawah, atas = r["rentang_95_kedatangan"]
        kedatangan = f"kedatangan benar {benar} dari {n} ({100 * benar / n:.1f}%, rentang 95% {100 * bawah:.1f}-{100 * atas:.1f}%)"
    return (f"{kedatangan}; ragu {r['kedatangan_ragu']}; gambar benar {r['gambar_benar']} dari {r['gambar']}; "
            f"di luar pola {r['gambar_luar_pola']}")


def utama(berkas_pembagian, folder_gambar, folder_model, keluar, baca=None, sisi="uji"):
    if baca is None:
        try:
            baca = PembacaQwen(folder_model)
        except ModelDitolak as galat:
            print(f"DITOLAK: {galat}")
            return 2
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    baris, ringkasan = nilai(pembagian, folder_gambar, baca, sisi)
    ringkasan = {"model": Path(folder_model).name, "pertanyaan": PERTANYAAN, "sisi": sisi, **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for k in KELOMPOK:
        print(f"{k:<13} {uraikan(ringkasan['per_kelompok'][k])}")
    print(f"detik per gambar: {ringkasan['detik_per_gambar']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (5, 6) or (len(sys.argv) == 6 and sys.argv[5] not in SISI):
        print("Pakai: python baca_vlm.py <pembagian.json> <folder-gambar> <folder-model> <folder-keluaran> [uji|latih]")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:5], sisi=sys.argv[5] if len(sys.argv) == 6 else "uji"))
