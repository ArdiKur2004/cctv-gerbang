"""ONNX untuk mesin baca hasil latih ulang fast-plate-ocr (Rencana 11, K25).

Ekspor ONNX bawaan gagal di Keras + torch (Rencana 10). Jalan yang dipakai: ONNX terbitan cct-s-v2-global punya susunan yang
sama persis dengan mesin hasil latih ulang, jadi angka bobotnya ditukar. Pemetaan tiap tensor bobot Keras ke initializer ONNX
dicari dari PASANGAN TERBITAN (.keras dan .onnx dari rilis yang sama) dengan mencocokkan nilainya: apa adanya, bentuk lain,
dibalik, atau sumbu konvolusi disusun ulang. Pemetaan harus lengkap dan satu-satu; bila tidak, ditolak. Konstanta lain
(kernel pemotong petak, bentuk) tidak disentuh.

Perintah, di image lab tambahan lewat tools\\lab.ps1 -Fpo (tanpa jaringan):
- buat: mesin.keras -> mesin.onnx + mesin-onnx.json. Disimpan hanya bila bacaannya sama dengan Keras pada semua gambar
  validasi dan selisih terbesarnya di bawah BATAS_SELISIH.
- baca: set uji dengan mesin.onnx di CPU, lewat LicensePlateRecognizer yang sama dengan pembaca fast-plate-ocr terbitan.
- cepat: milidetik per gambar di CPU dengan 1, 2, dan 4 utas, pada gambar validasi (sisi latih).
- samakan: dua hasil.jsonl dari set yang sama -> jumlah gambar yang bacaannya berbeda.

hasil.jsonl memuat nomor plat: tinggal di data/, agen tidak membukanya. Layar hanya hitungan.

  buat:    powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py buat /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan
  baca:    powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-indo-1-onnx
  cepat:   powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py cepat /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/cepat-fpo-indo-1/ringkasan.json
  samakan: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py samakan /kerja/data/keluaran/baca-fpo-indo-1/hasil.jsonl /kerja/data/keluaran/baca-fpo-indo-1-onnx/hasil.jsonl
"""
import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_fpo import ubah_warna  # noqa: E402
from baca_vlm import KELOMPOK, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from latih_fpo import VENDOR, jalur_terkunci, siapkan_torch  # noqa: E402
from model_terkunci import ModelDitolak, daftar_berkas, sha256_berkas, verifikasi_berkas  # noqa: E402

BUTIR_ONNX = "fpo-cct-s-v2-onnx"
BUTIR_PLAT = "fpo-cct-s-v2-config"
SUMBU = ((3, 2, 0, 1), (2, 3, 0, 1), (3, 0, 1, 2))
BATAS_SELISIH = 1e-4
UTAS = (1, 2, 4)
PANASKAN = 10


class PetaDitolak(ModelDitolak):
    """Pemetaan bobot ke ONNX tidak lengkap, ganda, atau tidak satu-satu; atau hasil tukarnya tidak sama dengan Keras."""


def cara_cocok(w, v):
    """Cara mengubah bobot Keras w menjadi initializer ONNX v, atau None bila nilainya tidak sama."""
    if w.size != v.size or w.size == 0:
        return None
    if w.shape == v.shape and np.array_equal(w, v):
        return "sama"
    if np.array_equal(w.ravel(), v.ravel()):
        return "bentuk-lain"
    if w.ndim == 2 and v.ndim == 2 and np.array_equal(w.T, v):
        return "dibalik"
    if w.ndim == 4 and v.ndim == 4:
        for p in SUMBU:
            t = np.transpose(w, p)
            if t.shape == v.shape and np.array_equal(t, v):
                return "sumbu:" + ",".join(map(str, p))
    return None


def terapkan(cara, w, bentuk):
    """Bobot Keras w -> nilai initializer berbentuk `bentuk`, dengan cara dari cara_cocok."""
    if cara == "sama":
        hasil = w
    elif cara == "bentuk-lain":
        hasil = w.reshape(bentuk)
    elif cara == "dibalik":
        hasil = w.T
    elif cara.startswith("sumbu:"):
        hasil = np.transpose(w, tuple(int(x) for x in cara[len("sumbu:"):].split(",")))
    else:
        raise ValueError(f"cara tak dikenal: {cara}")
    # np.array, bukan np.ascontiguousarray: yang kedua mengubah skalar () menjadi (1,) (alpha DyT, Rencana 11).
    hasil = np.array(hasil, dtype=np.float32, order="C")
    if hasil.shape != tuple(bentuk):
        raise ValueError(f"bentuk {hasil.shape} bukan {tuple(bentuk)}")
    return hasil


def peta(bobot, initializer):
    """bobot: daftar array Keras (urutan model.get_weights()); initializer: {nama: array}. Kembali: daftar (nama, cara) per
    bobot. Ditolak bila ada bobot tanpa pasangan, dengan lebih dari satu pasangan, atau dua bobot berbagi satu initializer."""
    hasil = []
    for i, w in enumerate(bobot):
        cocok = [(n, c) for n, v in initializer.items() if (c := cara_cocok(w, v))]
        if len(cocok) != 1:
            raise PetaDitolak(f"bobot ke-{i} {w.shape}: {len(cocok)} pasangan")
        hasil.append(cocok[0])
    nama = [n for n, _ in hasil]
    if len(set(nama)) != len(nama):
        raise PetaDitolak("dua bobot menunjuk initializer yang sama")
    return hasil


def berkas_terkunci(folder_unduhan, butir):
    """Satu berkas unduhan yang SHA-256-nya diperiksa terhadap kunci."""
    daftar = daftar_berkas()
    return verifikasi_berkas(Path(folder_unduhan) / butir / daftar.get(butir, ("?", ""))[0], butir, daftar)


def tukar(model_onnx, peta_, bobot_baru):
    """Salinan model ONNX dengan initializer di peta diganti bobot_baru (urutan sama dengan peta)."""
    import onnx
    from onnx import numpy_helper

    baru = onnx.ModelProto()
    baru.CopyFrom(model_onnx)
    letak = {init.name: i for i, init in enumerate(baru.graph.initializer)}
    for (nama, cara), w in zip(peta_, bobot_baru, strict=True):
        lama = baru.graph.initializer[letak[nama]]
        baru.graph.initializer[letak[nama]].CopyFrom(numpy_helper.from_array(terapkan(cara, w, tuple(lama.dims)), nama))
    return baru


def masukan(gambar_bgr, cfg):
    """Praproses yang sama dengan LicensePlateRecognizer: satu gambar -> uint8 (1, tinggi, lebar, kanal)."""
    from fast_plate_ocr.core.process import preprocess_image
    from fast_plate_ocr.inference.plate_recognizer import _load_image_from_source

    return preprocess_image(_load_image_from_source(ubah_warna(gambar_bgr, cfg.image_color_mode), cfg))


def banding(model_keras, sesi, cfg, gambar):
    """Keluaran Keras vs ONNX pada gambar yang sama. Kembali: (jumlah gambar, gambar yang semua slotnya sama, selisih terbesar)."""
    x = np.concatenate([masukan(g, cfg) for g in gambar])
    k = np.concatenate([np.asarray(model_keras.predict(x[i:i + 64].astype(np.float32), verbose=0)["plate"])
                        for i in range(0, len(x), 64)]).reshape(len(x), cfg.max_plate_slots, -1)
    o = np.concatenate([sesi.run(["plate"], {"input": x[i:i + 64]})[0]
                        for i in range(0, len(x), 64)]).reshape(len(x), cfg.max_plate_slots, -1)
    return len(x), int((k.argmax(-1) == o.argmax(-1)).all(-1).sum()), float(np.abs(k - o).max())


def gambar_csv(berkas_csv):
    """Jalur gambar satu CSV hasil latih_fpo siapkan, disusun dengan cara fast-plate-ocr (folder CSV + os.sep + jalur)."""
    folder = os.path.dirname(os.path.realpath(berkas_csv))
    with open(berkas_csv, newline="") as berkas:
        jalur = [folder + os.sep + b["image_path"] for b in csv.DictReader(berkas)]
    return jalur


def buat(folder_mesin, folder_unduhan):
    """mesin.keras -> mesin.onnx + mesin-onnx.json, hanya bila bacaannya sama dengan Keras pada semua gambar validasi."""
    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin.json").read_text())
    if sha256_berkas(folder / "mesin.keras") != meta["sha256_mesin"]:
        raise ModelDitolak(f"{folder.name}/mesin.keras: SHA-256 tidak sama dengan yang dicatat di mesin.json")
    jalur = jalur_terkunci(folder_unduhan)
    onnx_terbitan = berkas_terkunci(folder_unduhan, BUTIR_ONNX)
    siapkan_torch()
    import onnx
    import onnxruntime as ort
    from onnx import numpy_helper
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur["plat"])
    terbitan = load_keras_model(jalur["keras"], cfg)
    mesin = load_keras_model(folder / "mesin.keras", cfg)
    if [w.shape for w in terbitan.get_weights()] != [w.shape for w in mesin.get_weights()]:
        raise PetaDitolak("susunan bobot mesin tidak sama dengan terbitan")
    asli = onnx.load(str(onnx_terbitan))
    p = peta(terbitan.get_weights(), {i.name: numpy_helper.to_array(i) for i in asli.graph.initializer})
    sendiri = tukar(asli, p, terbitan.get_weights())
    if not all(np.array_equal(numpy_helper.to_array(a), numpy_helper.to_array(b))
               for a, b in zip(asli.graph.initializer, sendiri.graph.initializer, strict=True)):
        raise PetaDitolak("menukar dengan bobot terbitan sendiri mengubah ONNX terbitan")
    baru = tukar(asli, p, mesin.get_weights())
    onnx.checker.check_model(baru)
    sesi = ort.InferenceSession(baru.SerializeToString(), providers=["CPUExecutionProvider"])
    gambar = [g for g in (cv2.imread(j) for j in gambar_csv(folder / "validasi.csv")) if g is not None]
    jumlah, sama, selisih = banding(mesin, sesi, cfg, gambar) if gambar else (0, 0, float("inf"))
    if jumlah == 0 or sama != jumlah or selisih > BATAS_SELISIH:
        raise PetaDitolak(f"ONNX hasil tukar tidak sama dengan Keras: plat sama {sama} dari {jumlah}, selisih terbesar {selisih:.2e}")
    onnx.save(baru, str(folder / "mesin.onnx"))
    hasil = {"nama": meta["nama"], "tujuan": meta["tujuan"], "bahan": meta["bahan"], "format": "onnx",
             "sha256_onnx": sha256_berkas(folder / "mesin.onnx"), "sha256_mesin": meta["sha256_mesin"],
             "sha256_onnx_terbitan": sha256_berkas(onnx_terbitan), "tensor_ditukar": len(p),
             "cara": dict(Counter(c.split(":")[0] for _, c in p)),
             "pemeriksaan_validasi": {"gambar": jumlah, "plat_sama": sama, "selisih_terbesar": selisih}}
    (folder / "mesin-onnx.json").write_text(json.dumps(hasil, indent=1))
    return hasil


class PembacaOnnxMesin:
    """Pembaca dengan mesin.onnx, lewat LicensePlateRecognizer di CPU (sama dengan pembaca fast-plate-ocr terbitan).
    mesin.onnx yang SHA-256-nya tidak sama dengan mesin-onnx.json ditolak sebelum apa pun dimuat. utas: jumlah utas
    ONNX Runtime (None = bawaan)."""

    def __init__(self, folder_mesin, folder_unduhan, utas=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin-onnx.json").read_text())
        if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
            raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
        plat = berkas_terkunci(folder_unduhan, BUTIR_PLAT)
        if str(VENDOR) not in sys.path:
            sys.path.insert(0, str(VENDOR))
        import onnxruntime as ort
        from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self._model = LicensePlateRecognizer(device="cpu", onnx_model_path=folder / "mesin.onnx", plate_config_path=plat,
                                             sess_options=opsi)
        self.cfg = self._model.config
        self.sesi = self._model.model

    def __call__(self, gambar_bgr):
        return self._model.run_one(ubah_warna(gambar_bgr, self.cfg.image_color_mode)).plate

    def dengan_yakin(self, gambar_bgr):
        """(teks, yakin): yakin = peluang terendah di semua slot, termasuk slot bantalan, jadi keraguan soal panjang plat ikut
        terhitung (Rencana 14)."""
        hasil = self._model.run_one(ubah_warna(gambar_bgr, self.cfg.image_color_mode), return_confidence=True)
        return hasil.plate, float(np.min(hasil.char_probs))


def baca(pembagian, folder_gambar, folder_mesin, folder_unduhan, keluar, pembaca=None):
    """Membaca set uji dengan mesin.onnx di CPU. Kembali: ringkasan (hitungan saja)."""
    pembaca = pembaca or PembacaOnnxMesin(folder_mesin, folder_unduhan)
    baris, ringkasan = nilai(pembagian, folder_gambar, pembaca, "uji")
    ringkasan = {"model": "fpo-indo-1 (onnx, CPU)", "sisi": "uji", **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for x in baris:
            berkas.write(json.dumps(x) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    return ringkasan


def _ms(daftar):
    return {"median": round(1000 * float(np.median(daftar)), 2), "p95": round(1000 * float(np.percentile(daftar, 95)), 2)}


def cepat(folder_mesin, folder_unduhan, utas=UTAS, panaskan=PANASKAN):
    """Milidetik per gambar di CPU pada gambar validasi (sisi latih): dekode berkas, utuh (praproses + model + pascaproses),
    dan model saja. `panaskan` gambar pertama tiap putaran tidak dihitung."""
    jalur = gambar_csv(Path(folder_mesin) / "validasi.csv")
    hasil = {"cpu_terlihat": os.cpu_count(), "gambar": len(jalur), "panaskan": panaskan, "per_utas": {}}
    for u in utas:
        pembaca = PembacaOnnxMesin(folder_mesin, folder_unduhan, utas=u)
        dekode, utuh, model = [], [], []
        for i, j in enumerate(jalur):
            t0 = time.perf_counter()
            g = cv2.imread(j)
            t1 = time.perf_counter()
            if g is None:
                continue
            pembaca(g)
            t2 = time.perf_counter()
            x = masukan(g, pembaca.cfg)
            t3 = time.perf_counter()
            pembaca.sesi.run(["plate"], {"input": x})
            t4 = time.perf_counter()
            if i >= panaskan:
                dekode.append(t1 - t0)
                utuh.append(t2 - t1)
                model.append(t4 - t3)
        hasil["per_utas"][str(u)] = {"diukur": len(utuh), "dekode_ms": _ms(dekode), "utuh_ms": _ms(utuh), "model_ms": _ms(model)}
    return hasil


def beda_bacaan(berkas_a, berkas_b):
    """Dua hasil.jsonl dari set yang sama -> hitungan gambar yang bacaannya berbeda (tanpa nomor plat)."""
    def muat(berkas):
        return {x["berkas"]: x["bacaan"] for x in map(json.loads, Path(berkas).read_text().splitlines()) if x}
    a, b = muat(berkas_a), muat(berkas_b)
    if a.keys() != b.keys():
        raise ValueError("kedua hasil tidak memuat gambar yang sama")
    return {"gambar": len(a), "beda": sum(a[k] != b[k] for k in a)}


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="ONNX fpo-indo-1: buat, baca, cepat, samakan (Rencana 11).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("buat")
    for nama in ("folder_mesin", "folder_unduhan"):
        b.add_argument(nama)
    c = perintah.add_parser("baca")
    for nama in ("pembagian", "folder_gambar", "folder_mesin", "folder_unduhan", "keluar"):
        c.add_argument(nama)
    k = perintah.add_parser("cepat")
    for nama in ("folder_mesin", "folder_unduhan", "keluar"):
        k.add_argument(nama)
    s = perintah.add_parser("samakan")
    for nama in ("hasil_a", "hasil_b"):
        s.add_argument(nama)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "buat":
            m = buat(p.folder_mesin, p.folder_unduhan)
            v = m["pemeriksaan_validasi"]
            print(f"dibuat mesin.onnx: {m['tensor_ditukar']} tensor ditukar ({m['cara']}); validasi plat sama {v['plat_sama']} "
                  f"dari {v['gambar']}; selisih terbesar {v['selisih_terbesar']:.2e}")
        elif p.perintah == "baca":
            r = baca(json.loads(Path(p.pembagian).read_text()), p.folder_gambar, p.folder_mesin, p.folder_unduhan, p.keluar)
            for kel in KELOMPOK:
                print(f"{kel:<13} {uraikan(r['per_kelompok'][kel])}")
            print(f"detik per gambar: {r['detik_per_gambar']}")
        elif p.perintah == "cepat":
            r = cepat(p.folder_mesin, p.folder_unduhan)
            Path(p.keluar).parent.mkdir(parents=True, exist_ok=True)
            Path(p.keluar).write_text(json.dumps(r, indent=1))
            print(f"CPU terlihat {r['cpu_terlihat']}; gambar {r['gambar']}, panaskan {r['panaskan']}")
            for u, x in r["per_utas"].items():
                print(f"utas {u}: utuh median {x['utuh_ms']['median']} ms (p95 {x['utuh_ms']['p95']}); model median "
                      f"{x['model_ms']['median']} ms; dekode median {x['dekode_ms']['median']} ms; diukur {x['diukur']}")
        else:
            r = beda_bacaan(p.hasil_a, p.hasil_b)
            print(f"gambar {r['gambar']}, beda {r['beda']}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
