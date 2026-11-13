"""Melatih ulang fast-plate-ocr (cct-s-v2-global) dengan bahan latih INDO-ALPR (K26, Rencana 10).

Tiga perintah, dijalankan di image lab tambahan lewat tools\\lab.ps1 -Fpo (tanpa jaringan):
- siapkan: kedatangan LATIH -> latih.csv dan validasi.csv. Dibagi per plat dengan bagi_validasi dari Rencana 8, jadi
  validasinya sama dengan validasi mesin-baca-1. Set uji tidak pernah dibaca. Jalur gambar relatif terhadap folder CSV,
  karena fast-plate-ocr menyambung folder CSV + os.sep + jalur gambar. Kolom plate_region selalu ada (tanpa kolom itu
  kepala wilayah dibuang tanpa galat, Rencana 9). Gambar yang tak terbaca dilewati dan hanya dihitung.
- latih: memastikan bobot terbitan termuat utuh lewat jalur perintah latih (load_weights(skip_mismatch=True) melewati
  lapisan tak cocok tanpa galat), mengukur validasi dengan bobot terbitan, menjalankan perintah latih fast-plate-ocr, lalu
  menyalin best.keras (dipilih dengan validasi, bukan set uji) menjadi mesin.keras dan menulis mesin.json.
- baca: membaca set uji dengan mesin.keras (SHA-256 diperiksa terhadap mesin.json); praproses dan pascaproses sama dengan
  LicensePlateRecognizer.

Kernel Triton bawaan torch dicabut dan TF32 dimatikan di seluruh proses (Rencana 9: image lab tanpa kompiler C; dengan TF32
keluaran Keras berselisih sampai 3,98e-3 dari ONNX). mesin.json sekaligus manifes untuk tools/periksa-jualan.mjs: bahannya
INDO-ALPR dan bobot terbitan fast-plate-ocr. ~~Bobot itu BELUM-JELAS, jadi tanda mesinnya RISET-SAJA sampai izin tertulis (K26,
K27).~~ Sejak K47 (19 Okt) bobot itu BOLEH-PRODUK (pernyataan pemelihara di GitHub diterima owner), dan tetap tercatat sebagai
bahan, sehingga bila K47 dibalik tanda mesinnya ikut turun.

Perintah keempat, latih-jualan (Rencana 24 Bagian B): pembaca JUALAN dari nol. Arsitekturnya cct_s_v2 dari kode fast-plate-ocr
(vendor, MIT) dan konfigurasi platnya fpo-jualan-plat.yaml milik sendiri; tidak ada berkas rilis yang dibaca. Bahannya CSV dari
bahan_pembaca.py, dan mesin.json bertujuan "jualan" dengan bahan dari siapkan.json. --bobot-awal hanya menerima mesin jualan sendiri
(tahap kedua calon P3), yang bahannya ikut tercatat.

Perintah kelima, latih-lanjut (Rencana 25, K47, K50 butir 3): fpo-indo-1 dilatih lanjut dengan bahan berwilayah dari
bahan_pembaca.py (INDO-ALPR latih inti + potongan tangkapan latih yang diulang, dan bila diminta plat buatan). Konfigurasi model dan
plat terbitan (BOLEH-PRODUK sejak K47) dipakai karena fpo-indo-1 dilatih dengannya; bobotnya harus termuat utuh lewat jalur perintah
latih; zaman dipilih dengan val_plate_acc; validasi diukur per sumber (INDO-ALPR dan tangkapan) sebelum dan sesudah. mesin.json
bertujuan "jualan", bahannya bahan siapkan.json ditambah bahan fpo-indo-1, dan tools/periksa-jualan.mjs tetap memeriksanya.

CSV dan hasil.jsonl memuat nomor plat: tinggal di data/, agen tidak membukanya. Layar hanya hitungan.

  latih-jualan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py latih-jualan /kerja/data/keluaran/pembaca-jualan-p1 --zaman <n> --nama pembaca-jualan-p1

  latih-lanjut: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py latih-lanjut /kerja/data/keluaran/pembaca-lanjut-r1 /kerja/data/unduhan --bobot-awal /kerja/data/keluaran/fpo-indo-1 --zaman 40 --nama pembaca-lanjut-r1

  siapkan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py siapkan /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1
  latih:   powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py latih /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan
  baca:    powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_fpo.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-indo-1
"""
import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_fpo import ubah_warna  # noqa: E402
from baca_vlm import KELOMPOK, matikan_kernel_triton, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from mesin_baca import HURUF, bagi_validasi  # noqa: E402
from model_terkunci import ModelDitolak, daftar_berkas, sha256_berkas, verifikasi_berkas  # noqa: E402
from plat import bersihkan  # noqa: E402

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "fast-plate-ocr"
NAMA = "fpo-indo-1"
BAHAN = ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
BUTIR = {"keras": "fpo-cct-s-v2-keras", "plat": "fpo-cct-s-v2-config", "model": "fpo-cct-s-v2-model-config"}
SLOT_MAKS = 10  # max_plate_slots konfigurasi plat terbitan; dicocokkan uji di tools/lab/uji_fpo
WILAYAH = "Indonesia"
ZAMAN = 150
UKURAN_ANGKATAN = 64
BENIH = 0
NAMA_JUALAN = "pembaca-jualan"
NAMA_LANJUT = "pembaca-lanjut"
MODEL_JUALAN = VENDOR / "models" / "cct_s_v2.yaml"  # arsitektur dari kode fast-plate-ocr @ 9ce7a5b (MIT), bukan berkas rilis
PLAT_JUALAN = Path(__file__).resolve().parent / "fpo-jualan-plat.yaml"


def baris_csv(kedatangan, folder_gambar, folder_csv):
    """Kedatangan -> (baris CSV [jalur relatif, teks, wilayah], jumlah gambar tak terbaca). Label yang tak bisa dibaca model
    (huruf di luar HURUF, kosong, atau lebih dari SLOT_MAKS) ditolak tanpa mencetak teksnya."""
    baris, tak = [], 0
    for k in kedatangan:
        if not k["teks"] or len(k["teks"]) > SLOT_MAKS or any(c not in HURUF for c in k["teks"]):
            raise ValueError("label di luar huruf atau panjang yang bisa dibaca model")
        for b in k["berkas"]:
            jalur = Path(folder_gambar) / b
            if cv2.imread(str(jalur)) is None:
                tak += 1
                continue
            baris.append([os.path.relpath(os.path.realpath(jalur), os.path.realpath(folder_csv)), k["teks"], WILAYAH])
    return baris, tak


def siapkan(pembagian, folder_gambar, keluar):
    """Hanya pembagian["latih"]; set uji tidak dibaca. Kembali: hitungan (tanpa nomor plat), juga ditulis ke siapkan.json."""
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    inti, validasi = bagi_validasi(pembagian["latih"])
    hitung = {"plat": {"latih": len(inti), "validasi": len(validasi)}, "gambar": {}, "tak_terbaca": 0}
    for nama, daftar in (("latih", inti), ("validasi", validasi)):
        baris, tak = baris_csv(daftar, folder_gambar, keluar)
        with open(keluar / f"{nama}.csv", "w", newline="") as berkas:
            tulis = csv.writer(berkas)
            tulis.writerow(["image_path", "plate_text", "plate_region"])
            tulis.writerows(baris)
        hitung["gambar"][nama] = len(baris)
        hitung["tak_terbaca"] += tak
    (keluar / "siapkan.json").write_text(json.dumps(hitung, indent=1))
    return hitung


def manifes(hitung, sha_mesin, sha_awal, latihan, validasi):
    """Isi mesin.json. Sekaligus manifes untuk tools/periksa-jualan.mjs: bobot awal terbitan ikut tercatat sebagai bahan."""
    return {"nama": NAMA, "tujuan": "belajar", "bahan": BAHAN,
            "keterangan": "fast-plate-ocr @ 9ce7a5b, cct-s-v2-global, dilatih ulang dengan bahan latih INDO-ALPR (K26)",
            "sha256_mesin": sha_mesin, "sha256_bobot_awal": sha_awal, **hitung, "latihan": latihan, "validasi": validasi}


def manifes_jualan(hitung, sha_mesin, latihan, validasi, nama=NAMA_JUALAN, awal=None):
    """Isi mesin.json mesin JUALAN (Rencana 24): dari nol, tanpa bobot terbitan. Bahan = bahan siapkan.json (bahan_pembaca),
    ditambah bahan mesin sendiri yang menjadi bobot awal (calon P3) bila ada."""
    bahan = list(hitung["bahan"])
    if awal:
        bahan += [b for b in awal["bahan"] if b not in bahan]
    return {"nama": nama, "tujuan": "jualan", "bahan": bahan,
            "keterangan": "cct_s_v2 dari kode fast-plate-ocr @ 9ce7a5b (MIT) dengan fpo-jualan-plat.yaml, dilatih dari nol tanpa "
                          "bobot terbitan (Rencana 24)",
            "sha256_mesin": sha_mesin, "bobot_awal": awal["nama"] if awal else None,
            "sha256_bobot_awal": awal["sha256_mesin"] if awal else None,
            **{k: v for k, v in hitung.items() if k != "bahan"}, "latihan": latihan, "validasi": validasi}


def bobot_awal_sendiri(folder):
    """Bobot awal tahap kedua: hanya mesin JUALAN sendiri yang mesin.keras-nya sama dengan mesin.json. Kembali: (jalur, meta)."""
    folder = Path(folder)
    meta = json.loads((folder / "mesin.json").read_text())
    if meta.get("tujuan") != "jualan":
        raise ModelDitolak(f"{folder.name}: bobot awal harus mesin jualan sendiri, bukan bertujuan {meta.get('tujuan')}")
    jalur = folder / "mesin.keras"
    if sha256_berkas(jalur) != meta["sha256_mesin"]:
        raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
    return jalur, meta


def mesin_awal_lanjut(folder):
    """Mesin awal latih lanjut (Rencana 25; fpo-indo-1): mesin.keras harus sama dengan mesin.json, diperiksa SEBELUM Keras dimuat.
    Tujuannya tidak disyaratkan "jualan" (fpo-indo-1 dilatih sebagai mesin belajar); yang menentukan boleh dijual adalah bahannya,
    yang ikut tercatat dan diperiksa tools/periksa-jualan.mjs. Kembali: (jalur, meta)."""
    folder = Path(folder)
    meta = json.loads((folder / "mesin.json").read_text())
    jalur = folder / "mesin.keras"
    if sha256_berkas(jalur) != meta["sha256_mesin"]:
        raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
    return jalur, meta


def manifes_lanjut(hitung, sha_mesin, latihan, validasi, nama, awal):
    """Isi mesin.json pembaca latih lanjut (Rencana 25): tujuan jualan; bahan = bahan siapkan.json + bahan mesin awal."""
    bahan = list(hitung["bahan"]) + [b for b in awal["bahan"] if b not in hitung["bahan"]]
    return {"nama": nama, "tujuan": "jualan", "bahan": bahan,
            "keterangan": f"{awal['nama']} (fast-plate-ocr cct-s-v2-global, K26) dilatih lanjut dengan bahan berwilayah dari "
                          "bahan_pembaca.py (Rencana 25, K50)",
            "sha256_mesin": sha_mesin, "bobot_awal": awal["nama"], "sha256_bobot_awal": awal["sha256_mesin"],
            **{k: v for k, v in hitung.items() if k != "bahan"}, "latihan": latihan, "validasi": validasi}


def siapkan_torch():
    """Sebelum Keras dimuat: cabut kernel Triton (image lab tanpa kompiler C), matikan TF32 (Rencana 9), dan pakai klon
    fast-plate-ocr yang terkunci."""
    matikan_kernel_triton()
    import torch

    torch.backends.cudnn.allow_tf32 = torch.backends.cuda.matmul.allow_tf32 = False
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))


def jalur_terkunci(folder_unduhan):
    """Bobot .keras, konfigurasi plat, dan konfigurasi model terbitan, masing-masing diperiksa SHA-256-nya terhadap kunci."""
    daftar = daftar_berkas()
    return {k: verifikasi_berkas(Path(folder_unduhan) / b / daftar.get(b, ("?", ""))[0], b, daftar) for k, b in BUTIR.items()}


def bobot_utuh(jalur, kepala_wilayah=True):
    """Bobot (terbitan, atau mesin sendiri untuk tahap kedua) dimuat lewat jalur perintah latih (build_model +
    load_weights(skip_mismatch=True)) lalu dibandingkan dengan model .keras utuh. Kembali: (tensor yang sama persis, tensor
    di .keras)."""
    import numpy as np
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.model.model_builders import build_model
    from fast_plate_ocr.train.model.model_schema import load_model_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur["plat"])
    model = build_model(load_model_config_from_yaml(jalur["model"]), cfg, enable_region_head=kepala_wilayah)
    model.load_weights(jalur["keras"], skip_mismatch=True)
    a = [np.asarray(w) for w in model.get_weights()]
    b = [np.asarray(w) for w in load_keras_model(jalur["keras"], cfg).get_weights()]
    sama = sum(x.shape == y.shape and np.array_equal(x, y) for x, y in zip(a, b)) if len(a) == len(b) else 0
    return int(sama), len(b)


class PembacaKeras:
    """Membaca dengan model .keras fast-plate-ocr. Praproses dan pascaproses sama dengan LicensePlateRecognizer, tetapi
    modelnya dijalankan Keras (ekspor ONNX belum jalan di Keras + torch). Dipanggil dengan satu gambar urutan warna OpenCV."""

    def __init__(self, berkas_keras, berkas_plat):
        siapkan_torch()
        from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
        from fast_plate_ocr.train.utilities.utils import load_keras_model

        self.cfg = load_plate_config_from_yaml(berkas_plat)
        self._model = load_keras_model(berkas_keras, self.cfg)

    def _peluang(self, gambar_bgr):
        """Keluaran kepala plat untuk satu gambar: larik (slot, huruf) berisi peluang."""
        import numpy as np
        from fast_plate_ocr.core.process import preprocess_image
        from fast_plate_ocr.inference.plate_recognizer import _load_image_from_source

        x = preprocess_image(_load_image_from_source(ubah_warna(gambar_bgr, self.cfg.image_color_mode), self.cfg))
        keluar = self._model.predict(x.astype(np.float32), verbose=0)["plate"]
        return np.asarray(keluar).reshape(-1, self.cfg.max_plate_slots, len(self.cfg.alphabet))

    def __call__(self, gambar_bgr):
        return self.dengan_yakin(gambar_bgr)[0]

    def dengan_yakin(self, gambar_bgr):
        """(teks, yakin): yakin = peluang terendah di semua slot, termasuk bantalan, seperti onnx_fpo.PembacaOnnxMesin (Rencana 14)."""
        from fast_plate_ocr.core.process import postprocess_output

        hasil = postprocess_output(self._peluang(gambar_bgr), self.cfg.max_plate_slots, self.cfg.alphabet,
                                   pad_char=self.cfg.pad_char, return_confidence=True)[0]
        return hasil.plate, float(min(hasil.char_probs))

    def rincian(self, gambar_bgr):
        """K46: per slot yang bukan bantalan, (huruf, peluang, huruf kedua, peluang kedua), supaya posisi yang ragu dan
        kemungkinan keduanya terbaca."""
        import numpy as np

        p = self._peluang(gambar_bgr)[0]
        urut = np.argsort(-p, axis=-1)
        abjad, hasil = self.cfg.alphabet, []
        for s in range(p.shape[0]):
            a, b = int(urut[s, 0]), int(urut[s, 1])
            if abjad[a] != self.cfg.pad_char:
                hasil.append((abjad[a], float(p[s, a]), abjad[b], float(p[s, b])))
        return hasil


class PembacaMesinFpo(PembacaKeras):
    """Pembaca dengan mesin hasil latih ulang. mesin.keras yang SHA-256-nya tidak sama dengan mesin.json ditolak SEBELUM
    Keras dimuat. Konfigurasi platnya berkas terbitan yang terkunci (model dilatih dengan konfigurasi itu)."""

    def __init__(self, folder_mesin, folder_unduhan):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin.json").read_text())
        if sha256_berkas(folder / "mesin.keras") != meta["sha256_mesin"]:
            raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
        super().__init__(folder / "mesin.keras", jalur_terkunci(folder_unduhan)["plat"])


class PembacaMesinJualan(PembacaKeras):
    """Pembaca dengan mesin JUALAN (Rencana 24): konfigurasi platnya fpo-jualan-plat.yaml, tanpa berkas rilis apa pun. mesin.keras
    yang SHA-256-nya tidak sama dengan mesin.json ditolak SEBELUM Keras dimuat."""

    def __init__(self, folder_mesin):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin.json").read_text())
        if sha256_berkas(folder / "mesin.keras") != meta["sha256_mesin"]:
            raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
        super().__init__(folder / "mesin.keras", PLAT_JUALAN)


def ketepatan(baca, berkas_csv):
    """Membaca semua gambar satu CSV (jalur seperti fast-plate-ocr: folder CSV + os.sep + jalur). Kembali: hitungan."""
    folder = os.path.dirname(os.path.realpath(berkas_csv))
    gambar = benar = 0
    with open(berkas_csv, newline="") as berkas:
        for b in csv.DictReader(berkas):
            g = cv2.imread(folder + os.sep + b["image_path"])
            gambar += 1
            benar += int(g is not None and bersihkan(baca(g)) == b["plate_text"])
    return {"gambar": gambar, "benar": benar}


PECAHAN_TANGKAPAN = {"potongan/t-": "tangkapan_label", "potongan/c": "tangkapan_rantai", "potongan/g": "tangkapan_geser"}


def ketepatan_per_sumber(baca, berkas_csv):
    """Seperti ketepatan, dipecah per sumber: jalur berawalan "potongan/" = tangkapan owner (bahan_pembaca.py), selain itu
    INDO-ALPR. Aturan pecahnya sama dengan banding-pembaca-24.py, jadi angkanya bisa dicocokkan. Rencana 30: tangkapan juga dipecah
    menurut PECAHAN_TANGKAPAN (kotak label, potongan rantai, potongan geser); pecahan tidak ikut dijumlah ke "semua". Kembali: hitungan."""
    folder = os.path.dirname(os.path.realpath(berkas_csv))
    hasil = {k: {"gambar": 0, "benar": 0} for k in ("indo_alpr", "tangkapan", *PECAHAN_TANGKAPAN.values())}
    with open(berkas_csv, newline="") as berkas:
        for b in csv.DictReader(berkas):
            g = cv2.imread(folder + os.sep + b["image_path"])
            benar = int(g is not None and bersihkan(baca(g)) == b["plate_text"])
            jalur = b["image_path"]
            kunci = ["tangkapan" if jalur.startswith("potongan/") else "indo_alpr"]
            kunci += [k for awalan, k in PECAHAN_TANGKAPAN.items() if jalur.startswith(awalan)]
            for k in kunci:
                hasil[k]["gambar"] += 1
                hasil[k]["benar"] += benar
    hasil["semua"] = {k: hasil["indo_alpr"][k] + hasil["tangkapan"][k] for k in ("gambar", "benar")}
    return hasil


def latih(folder, folder_unduhan, zaman=ZAMAN, benih=BENIH, ukuran_angkatan=UKURAN_ANGKATAN):
    """Melatih dari latih.csv dan validasi.csv hasil siapkan (set uji tidak pernah diberikan). Kembali: isi mesin.json."""
    folder = Path(folder)
    hitung = json.loads((folder / "siapkan.json").read_text())
    jalur = jalur_terkunci(folder_unduhan)
    siapkan_torch()
    sama, semua = bobot_utuh(jalur)
    if sama != semua:
        raise ModelDitolak(f"bobot terbitan tidak termuat utuh lewat jalur perintah latih: {sama} dari {semua} tensor sama")
    awal = ketepatan(PembacaKeras(jalur["keras"], jalur["plat"]), folder / "validasi.csv")
    print(f"validasi dengan bobot terbitan: benar {awal['benar']} dari {awal['gambar']} gambar", flush=True)
    latihan = _jalankan_latih(folder, jalur["model"], jalur["plat"], jalur["keras"], zaman, benih, ukuran_angkatan)
    akhir = ketepatan(PembacaKeras(folder / "mesin.keras", jalur["plat"]), folder / "validasi.csv")
    latihan["bobot_termuat"] = f"{sama}/{semua}"
    meta = manifes(hitung, sha256_berkas(folder / "mesin.keras"), sha256_berkas(jalur["keras"]), latihan,
                   {"awal": awal, "akhir": akhir})
    (folder / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def _jalankan_latih(folder, berkas_model, berkas_plat, bobot, zaman, benih, ukuran_angkatan, metrik="val_plate_acc", laju=None):
    """Perintah latih fast-plate-ocr (bobot None = dari nol), lalu best.keras -> mesin.keras. metrik: yang dipantau checkpoint dan
    henti dini (--early-stopping-metric; bawaan pembuatnya val_plate_acc). laju: --lr (None = bawaan pembuatnya). Kembali: catatan
    latihan."""
    latihan = folder / "latihan"
    if latihan.exists():
        raise FileExistsError("folder latihan sudah ada; dipindah atau dihapus dengan sadar sebelum melatih lagi")

    import torch
    from fast_plate_ocr.cli.cli import main_cli

    perintah = ["train", "--model-config-file", str(berkas_model), "--plate-config-file", str(berkas_plat),
                "--annotations", str(folder / "latih.csv"), "--val-annotations", str(folder / "validasi.csv"),
                "--epochs", str(zaman), "--batch-size", str(ukuran_angkatan), "--seed", str(benih), "--output-dir", str(latihan),
                "--early-stopping-metric", metrik]
    perintah += ["--lr", str(laju)] if laju is not None else []
    main_cli(perintah + (["--weights-path", str(bobot)] if bobot else []), standalone_mode=False)
    (hasil,) = [p for p in latihan.iterdir() if p.is_dir()]
    shutil.copy(hasil / "best.keras", folder / "mesin.keras")
    with open(hasil / "training_log.csv", newline="") as berkas:
        log = list(csv.DictReader(berkas))
    # Tanpa kepala wilayah fast-plate-ocr membuang awalan "plate_" dari nama metrik (cli/train.py baris 91-98).
    wilayah = "val_plate_acc" in log[0]
    kolom = metrik if wilayah else {"val_plate_acc": "val_acc", "val_plate_char_acc": "val_char_acc"}[metrik]
    kolom_plat = "val_plate_acc" if wilayah else "val_acc"
    # ModelCheckpoint menyimpan best.keras hanya bila metrik itu naik, jadi zaman terbaik adalah nilai tertinggi PERTAMA.
    terbaik = max(range(len(log)), key=lambda i: (float(log[i][kolom]), -i))
    return {"zaman": zaman, "zaman_berjalan": len(log), "zaman_terbaik": terbaik + 1, "benih": benih, "laju": laju,
            "ukuran_angkatan": ukuran_angkatan, "metrik_pilih": kolom, "nilai_metrik_terbaik": round(float(log[terbaik][kolom]), 4),
            "val_plate_acc_terbaik": round(float(log[terbaik][kolom_plat]), 4),
            "perangkat": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"}


def latih_dari_nol(folder, zaman=ZAMAN, benih=BENIH, ukuran_angkatan=UKURAN_ANGKATAN, bobot_awal=None, nama=NAMA_JUALAN):
    """Pembaca JUALAN (Rencana 24 Task 6): cct_s_v2 dari kode MIT dan fpo-jualan-plat.yaml, tanpa berkas rilis fast-plate-ocr apa
    pun. bobot_awal: folder mesin jualan sendiri (calon P3), diperiksa SHA-256-nya dan harus termuat utuh. Kembali: isi mesin.json."""
    folder = Path(folder)
    hitung = json.loads((folder / "siapkan.json").read_text())
    jalur_awal, awal = bobot_awal_sendiri(bobot_awal) if bobot_awal else (None, None)
    siapkan_torch()
    termuat = None
    if jalur_awal:
        sama, semua = bobot_utuh({"model": MODEL_JUALAN, "plat": PLAT_JUALAN, "keras": jalur_awal}, kepala_wilayah=False)
        if sama != semua:
            raise ModelDitolak(f"bobot awal sendiri tidak termuat utuh: {sama} dari {semua} tensor sama")
        termuat = f"{sama}/{semua}"
    # Dari nol, ketepatan plat utuh di validasi bisa 0 selama puluhan zaman (P1 jalan pertama, Rencana 24), sehingga checkpoint
    # dengan val_acc tertahan di zaman 1. Ketepatan per huruf naik sejak awal, jadi itu yang memilih zaman.
    latihan = _jalankan_latih(folder, MODEL_JUALAN, PLAT_JUALAN, jalur_awal, zaman, benih, ukuran_angkatan,
                              metrik="val_plate_char_acc")
    latihan["bobot_termuat"] = termuat
    akhir = ketepatan(PembacaKeras(folder / "mesin.keras", PLAT_JUALAN), folder / "validasi.csv")
    meta = manifes_jualan(hitung, sha256_berkas(folder / "mesin.keras"), latihan, {"akhir": akhir}, nama, awal)
    (folder / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def latih_lanjut(folder, folder_unduhan, bobot_awal, zaman=ZAMAN, benih=BENIH, ukuran_angkatan=UKURAN_ANGKATAN, nama=NAMA_LANJUT,
                 laju=None):
    """fpo-indo-1 (atau mesin berkepala wilayah lain yang dilatih dengan konfigurasi terbitan) dilatih lanjut (Rencana 25). Bahan
    harus berwilayah; mesin awal diperiksa SHA-256-nya dan harus termuat utuh; validasi diukur per sumber sebelum dan sesudah.
    Rencana 30: laju = --lr (None = bawaan pembuatnya); bila ada validasi-indo.csv (bahan_pembaca --validasi-terpisah), INDO-ALPR
    validasi diukur sebelum dan sesudah sebagai penjaga, tanpa ikut memilih zaman. Kembali: isi mesin.json."""
    folder = Path(folder)
    hitung = json.loads((folder / "siapkan.json").read_text())
    if not hitung.get("wilayah"):
        raise ValueError("bahan latih lanjut harus berwilayah (bahan_pembaca.py --wilayah): mesin awal berkepala wilayah")
    jalur_awal, awal = mesin_awal_lanjut(bobot_awal)
    jalur = jalur_terkunci(folder_unduhan)
    siapkan_torch()
    sama, semua = bobot_utuh({**jalur, "keras": jalur_awal})
    if sama != semua:
        raise ModelDitolak(f"mesin awal tidak termuat utuh lewat jalur perintah latih: {sama} dari {semua} tensor sama")
    indo = folder / "validasi-indo.csv"
    baca_awal = PembacaKeras(jalur_awal, jalur["plat"])
    validasi = {"awal": ketepatan_per_sumber(baca_awal, folder / "validasi.csv")}
    if indo.exists():
        validasi["indo_awal"] = ketepatan(baca_awal, indo)
    print(f"validasi dengan {awal['nama']}: {json.dumps(validasi)}", flush=True)
    latihan = _jalankan_latih(folder, jalur["model"], jalur["plat"], jalur_awal, zaman, benih, ukuran_angkatan, laju=laju)
    latihan["bobot_termuat"] = f"{sama}/{semua}"
    baca_akhir = PembacaKeras(folder / "mesin.keras", jalur["plat"])
    validasi["akhir"] = ketepatan_per_sumber(baca_akhir, folder / "validasi.csv")
    if indo.exists():
        validasi["indo_akhir"] = ketepatan(baca_akhir, indo)
    meta = manifes_lanjut(hitung, sha256_berkas(folder / "mesin.keras"), latihan, validasi, nama, awal)
    (folder / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def baca(pembagian, folder_gambar, folder_mesin, folder_unduhan, keluar, pembaca=None):
    """Membaca set uji dengan mesin hasil latih ulang. Kembali: ringkasan (hitungan saja)."""
    pembaca = pembaca or PembacaMesinFpo(folder_mesin, folder_unduhan)
    baris, ringkasan = nilai(pembagian, folder_gambar, pembaca, "uji")
    ringkasan = {"model": NAMA, "sisi": "uji", **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for x in baris:
            berkas.write(json.dumps(x) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    return ringkasan


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Melatih ulang fast-plate-ocr dengan bahan latih INDO-ALPR (Rencana 10).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    s = perintah.add_parser("siapkan")
    for nama in ("pembagian", "folder_gambar", "keluar"):
        s.add_argument(nama)
    a = perintah.add_parser("latih")
    for nama in ("folder", "folder_unduhan"):
        a.add_argument(nama)
    a.add_argument("--zaman", type=int, default=ZAMAN)
    a.add_argument("--benih", type=int, default=BENIH)
    b = perintah.add_parser("baca")
    for nama in ("pembagian", "folder_gambar", "folder_mesin", "folder_unduhan", "keluar"):
        b.add_argument(nama)
    j = perintah.add_parser("latih-jualan")
    j.add_argument("folder")
    j.add_argument("--zaman", type=int, default=ZAMAN)
    j.add_argument("--benih", type=int, default=BENIH)
    j.add_argument("--ukuran-angkatan", type=int, default=UKURAN_ANGKATAN)
    j.add_argument("--bobot-awal", help="folder mesin jualan sendiri (calon P3, Rencana 24)")
    j.add_argument("--nama", default=NAMA_JUALAN)
    n = perintah.add_parser("latih-lanjut")
    for nama in ("folder", "folder_unduhan"):
        n.add_argument(nama)
    n.add_argument("--bobot-awal", required=True, help="folder mesin awal berkepala wilayah, mis. fpo-indo-1 (Rencana 25)")
    n.add_argument("--zaman", type=int, default=ZAMAN)
    n.add_argument("--benih", type=int, default=BENIH)
    n.add_argument("--ukuran-angkatan", type=int, default=UKURAN_ANGKATAN)
    n.add_argument("--nama", default=NAMA_LANJUT)
    n.add_argument("--laju", type=float, help="laju belajar (--lr fast-plate-ocr); tanpa ini bawaan pembuatnya (Rencana 30)")
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "siapkan":
            h = siapkan(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.keluar)
            print(f"plat latih {h['plat']['latih']}, validasi {h['plat']['validasi']}; gambar latih {h['gambar']['latih']}, "
                  f"validasi {h['gambar']['validasi']}; tak terbaca {h['tak_terbaca']}")
        elif p.perintah == "latih":
            m = latih(p.folder, p.folder_unduhan, p.zaman, p.benih)
            print(f"selesai: zaman terbaik {m['latihan']['zaman_terbaik']} dari {m['latihan']['zaman_berjalan']}; validasi benar "
                  f"{m['validasi']['awal']['benar']} -> {m['validasi']['akhir']['benar']} dari {m['validasi']['akhir']['gambar']} "
                  f"gambar; bobot termuat {m['latihan']['bobot_termuat']}")
        elif p.perintah == "latih-lanjut":
            m = latih_lanjut(p.folder, p.folder_unduhan, p.bobot_awal, p.zaman, p.benih, p.ukuran_angkatan, p.nama, laju=p.laju)
            v = m["validasi"]
            a, b = (v["indo_awal"], v["indo_akhir"]) if "indo_awal" in v else (v["awal"]["indo_alpr"], v["akhir"]["indo_alpr"])
            print(f"selesai {m['nama']} ({m['tujuan']}, bahan {m['bahan']}): zaman terbaik {m['latihan']['zaman_terbaik']} dari "
                  f"{m['latihan']['zaman_berjalan']}; bobot termuat {m['latihan']['bobot_termuat']}; validasi INDO-ALPR "
                  f"{a['benar']} -> {b['benar']} dari {b['gambar']}, "
                  f"tangkapan {v['awal']['tangkapan']['benar']} -> {v['akhir']['tangkapan']['benar']} dari "
                  f"{v['akhir']['tangkapan']['gambar']}")
        elif p.perintah == "latih-jualan":
            m = latih_dari_nol(p.folder, p.zaman, p.benih, p.ukuran_angkatan, p.bobot_awal, p.nama)
            print(f"selesai {m['nama']} ({m['tujuan']}, bahan {m['bahan']}): zaman terbaik {m['latihan']['zaman_terbaik']} dari "
                  f"{m['latihan']['zaman_berjalan']}; validasi benar {m['validasi']['akhir']['benar']} dari "
                  f"{m['validasi']['akhir']['gambar']} gambar")
        else:
            r = baca(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.folder_mesin, p.folder_unduhan, p.keluar)
            for k in KELOMPOK:
                print(f"{k:<13} {uraikan(r['per_kelompok'][k])}")
            print(f"detik per gambar: {r['detik_per_gambar']}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
