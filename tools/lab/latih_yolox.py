"""Pencari plat buatan sendiri: YOLOX-Nano dan YOLOX-Tiny (vendor/yolox @ 4197784, Apache-2.0) yang dilatih ulang dengan
plat-lighting (K30, Rencana 13).

- Model dibangun dari klon terkunci. loguru dan thop yang dimuat yolox.utils diganti tiruan bila pustaka aslinya tidak ada:
  keduanya hanya untuk log dan menghitung FLOPs, tidak dipakai saat menghitung (diukur sebelum Rencana 13).
- Bobot awal COCO (.pth, pickle) hanya dimuat dengan torch.load(weights_only=True); pickle yang membawa kode ditolak. Tensor
  yang bentuknya lain (kepala kelas COCO 80 -> 1 kelas plat) dilewati dan dihitung.
- Masukan dan keluaran sama dengan tools/lab/pencari_yolox.py (letterbox YOLOX; target kelas, cx, cy, w, h dalam piksel
  masukan).
- Latihan: putaran sendiri (SGD nesterov, pemanasan kuadrat, kosinus, EMA dari yolox.utils) dengan variasi sederhana (balik
  horizontal, skala, geser, terang-gelap). Zaman terbaik dipilih dengan F1 di sisi valid (tools/lab/deteksi.py), tidak
  pernah sisi test. Bobot EMA terbaik disimpan sebagai safetensors (bukan pickle) dengan SHA-256 di mesin.json, yang sekaligus
  manifes untuk tools/periksa-jualan.mjs (bahan: plat-lighting dan bobot awal YOLOX).
- ekspor: mesin.onnx disimpan hanya bila deteksinya sama dengan torch pada gambar valid (butuh onnx: image lab tambahan).
Layar hanya hitungan; nama berkas tidak dicetak.

  latih:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/latih_yolox.py latih nano 416 /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan /kerja/data/keluaran/pencari-yolox-nano-416
  lanjut (Rencana 25): ... latih nano 640 /kerja/data/keluaran/dataset/cctv2-c1 /kerja/data/tidak-dipakai /kerja/data/keluaran/pencari-cctv2-c1 --bobot-awal-mesin /kerja/data/keluaran/pencari-yolox-nano-640-cctv1 --jualan --nama pencari-cctv2-c1 --zaman 60
  ekspor: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/latih_yolox.py ekspor /kerja/data/keluaran/pencari-yolox-nano-416 /kerja/data/keluaran/dataset/plat-lighting
"""
import argparse
import importlib.machinery
import importlib.util
import json
import logging
import math
import pickle
import sys
import types
from pathlib import Path

import cv2
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deteksi  # noqa: E402
import pencari_yolox as pyx  # noqa: E402
from baca_vlm import matikan_kernel_triton  # noqa: E402
from model_terkunci import LOKASI_KUNCI, ModelDitolak, daftar_berkas, sha256_berkas, verifikasi_berkas  # noqa: E402

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "yolox"
JENIS = {"nano": (0.33, 0.25, True), "tiny": (0.33, 0.375, False)}
BUTIR_BOBOT = {"nano": "yolox-nano-coco", "tiny": "yolox-tiny-coco"}
BAHAN = ["dataset-plat-lighting", "bobot-yolox"]
MAKS_LABEL = 50
ZAMAN = 100
UKURAN_ANGKATAN = 16
LAJU = 0.01  # per 64 gambar, seperti YOLOX
PEMANASAN = 3
BENIH = 0
BATAS_EKSPOR = 0.5  # piksel; deteksi torch dan ONNX harus sama dalam batas ini, juga koordinat mentah (piksel masukan)
BATAS_PELUANG = 1e-3  # selisih peluang objek dan kelas mentah terbesar; sama dengan batas yakin di pemeriksaan deteksi


def _tidak_dipakai(*a, **k):
    raise NotImplementedError("tiruan: hanya untuk menghitung FLOPs, tidak dipakai di sini")


def siapkan_yolox():
    """Tiruan loguru/thop bila pustaka aslinya tidak ada, lalu klon terkunci di sys.path."""
    for nama, isi in (("loguru", {"logger": logging.getLogger("yolox")}), ("thop", {"profile": _tidak_dipakai})):
        if nama not in sys.modules and importlib.util.find_spec(nama) is None:
            m = types.ModuleType(nama)
            m.__spec__ = importlib.machinery.ModuleSpec(nama, None)
            m.__dict__.update(isi)
            sys.modules[nama] = m
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))


def buat_model(jenis):
    """YOLOX 1 kelas dengan inisialisasi bawaan YOLOX (BatchNorm eps 1e-3, momentum 0,03; bias kelas prior 0,01)."""
    siapkan_yolox()
    from yolox.models import YOLOPAFPN, YOLOX, YOLOXHead

    dalam, lebar, dw = JENIS[jenis]
    model = YOLOX(YOLOPAFPN(dalam, lebar, in_channels=[256, 512, 1024], depthwise=dw),
                  YOLOXHead(1, lebar, in_channels=[256, 512, 1024], depthwise=dw))
    for m in model.modules():
        if isinstance(m, torch.nn.BatchNorm2d):
            m.eps, m.momentum = 1e-3, 0.03
    model.head.initialize_biases(1e-2)
    return model


def muat_bobot_awal(model, berkas):
    """Bobot COCO (.pth) -> model, hanya lewat torch.load(weights_only=True). Kembali: (dimuat, dilewati)."""
    try:
        ckpt = torch.load(str(berkas), map_location="cpu", weights_only=True)
    except (pickle.UnpicklingError, RuntimeError) as galat:
        raise ModelDitolak(f"{Path(berkas).name}: tidak bisa dimuat tanpa menjalankan kode pickle ({type(galat).__name__})") from None
    sd = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    milik = model.state_dict()
    cocok = {k: v for k, v in sd.items() if k in milik and tuple(v.shape) == tuple(milik[k].shape)}
    model.load_state_dict(cocok, strict=False)
    return len(cocok), len(milik) - len(cocok)


def ke_target(kotak, skala, maks=MAKS_LABEL):
    """Kotak (x1, y1, x2, y2) piksel asli -> larik (maks, 5): kelas 0, cx, cy, w, h dalam piksel masukan. Kotak yang lebar atau
    tingginya kurang dari 2 piksel masukan dibuang."""
    t = np.zeros((maks, 5), np.float32)
    i = 0
    for x1, y1, x2, y2 in kotak:
        w, h = (x2 - x1) * skala, (y2 - y1) * skala
        if w < 2 or h < 2 or i >= maks:
            continue
        t[i] = (0, (x1 + x2) / 2 * skala, (y1 + y2) / 2 * skala, w, h)
        i += 1
    return t


def balik(gambar, kotak):
    """Balik horizontal; kotak ikut."""
    lebar = gambar.shape[1]
    return gambar[:, ::-1].copy(), [(float(lebar - x2), float(y1), float(lebar - x1), float(y2)) for x1, y1, x2, y2 in kotak]


def ubah_acak(gambar, kotak, rng):
    """Variasi untuk latihan: balik horizontal, skala 0,7-1,3 dan geser di kanvas seukuran semula, terang-gelap. Kotak ikut
    berubah; bagian di luar kanvas dipotong, dan kotak yang tersisa kurang dari separuh luasnya dibuang."""
    tinggi, lebar = gambar.shape[:2]
    if rng.random() < 0.5:
        gambar, kotak = balik(gambar, kotak)
    s = rng.uniform(0.7, 1.3)
    dx, dy = rng.uniform(-0.15, 0.15) * lebar, rng.uniform(-0.15, 0.15) * tinggi
    m = np.float32([[s, 0, (1 - s) * lebar / 2 + dx], [0, s, (1 - s) * tinggi / 2 + dy]])
    g = cv2.warpAffine(gambar, m, (lebar, tinggi), borderValue=(pyx.BANTAL,) * 3)
    k = np.array(kotak, np.float32).reshape(-1, 4) * s + np.float32([m[0, 2], m[1, 2], m[0, 2], m[1, 2]])
    luas = (k[:, 2] - k[:, 0]) * (k[:, 3] - k[:, 1])
    k[:, [0, 2]] = k[:, [0, 2]].clip(0, lebar)
    k[:, [1, 3]] = k[:, [1, 3]].clip(0, tinggi)
    sisa = (k[:, 2] - k[:, 0]).clip(0) * (k[:, 3] - k[:, 1]).clip(0)
    g = np.clip(g.astype(np.float32) * rng.uniform(0.6, 1.4) + rng.uniform(-30, 30), 0, 255).astype(np.uint8)
    return g, [tuple(float(x) for x in b) for b in k[sisa >= 0.5 * luas]]


def baca_sisi(folder_sisi):
    """Satu sisi plat-lighting -> (jalur gambar, kotak piksel asli per gambar)."""
    jalur, kotak = [], []
    for berkas in sorted(p for p in (Path(folder_sisi) / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN):
        g = cv2.imread(str(berkas))
        if g is None:
            continue
        label = Path(folder_sisi) / "labels" / f"{berkas.stem}.txt"
        jalur.append(berkas)
        kotak.append(deteksi.baca_label(label, g.shape[1], g.shape[0]) if label.exists() else [])
    return jalur, kotak


def angkatan(jalur, kotak, ukuran, rng):
    gambar, target = [], []
    for j, k in zip(jalur, kotak):
        g, k = ubah_acak(cv2.imread(str(j)), k, rng)
        lb, skala = pyx.letterbox(g, ukuran)
        gambar.append(lb.transpose(2, 0, 1))
        target.append(ke_target(k, skala))
    return torch.from_numpy(np.stack(gambar).astype(np.float32)), torch.from_numpy(np.stack(target))


def cari_torch(model, ukuran, perangkat):
    """Pencari dengan model torch (mode eval); penguraian sama dengan pencari ONNX."""
    def cari(gambar_bgr):
        x, skala = pyx.masukan(gambar_bgr, ukuran)
        with torch.no_grad():
            keluar = model(torch.from_numpy(x).to(perangkat))[0].float().cpu().numpy()
        return pyx.urai_keluaran(keluar, skala)
    return cari


def kelompok_parameter(model):
    """Seperti YOLOX: peluruhan bobot hanya untuk bobot non-BatchNorm."""
    bn, bobot, bias = [], [], []
    for m in model.modules():
        if isinstance(getattr(m, "bias", None), torch.nn.Parameter):
            bias.append(m.bias)
        if isinstance(m, torch.nn.BatchNorm2d):
            bn.append(m.weight)
        elif isinstance(getattr(m, "weight", None), torch.nn.Parameter):
            bobot.append(m.weight)
    return [{"params": bn, "weight_decay": 0.0}, {"params": bobot, "weight_decay": 5e-4}, {"params": bias, "weight_decay": 0.0}]


def model_dari_mesin(jenis, folder_mesin):
    """Mesin sendiri (mesin.safetensors lewat muat_mesin, yang menolak bobot yang SHA-256-nya berubah) sebagai titik berangkat
    melatih lanjut (Rencana 25). Kembali: (model, {"mesin", "folder", "sha256"}); folder ikut dicatat karena nama di mesin.json
    cctv1 sama dengan pencari lama."""
    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin.json").read_text())
    if meta["jenis"] != jenis:
        raise ValueError(f"jenis mesin awal {meta['jenis']} tidak sama dengan jenis yang dilatih {jenis}")
    model = muat_mesin(folder)
    return model, {"mesin": meta["nama"], "folder": folder.name, "sha256": meta["sha256_bobot"]}


def latih(jenis, ukuran, folder_dataset, folder_unduhan, keluar, zaman=ZAMAN, benih=BENIH, perangkat=None, kunci=LOKASI_KUNCI,
          bahan=None, dari_nol=False, nama=None, bobot_awal_mesin=None, jualan=False):
    """Melatih dari sisi train; memilih zaman dengan F1 di sisi valid; sisi test tidak dibaca. Kembali: isi mesin.json.
    bahan: semua id bahan yang membentuk mesin (data-asal/bahan.json); bawaan BAHAN. Rencana 19: dataset CCTV memuat video riset
    dan plat buatan, jadi keduanya harus tercatat supaya tanda mesin benar. Bobot COCO yang dimuat selalu tercatat sebagai
    "bobot-yolox", juga bila --bahan melupakannya.
    dari_nol (Rencana 24, mesin jualan): bobot COCO dan kuncinya tidak dibaca sama sekali; bahan bawaannya daftar bahan di
    ringkasan.json dataset (dataset_jualan.py), dan tujuan mesinnya "jualan".
    bobot_awal_mesin (Rencana 25, K50): berangkat dari mesin sendiri (model_dari_mesin), tanpa membaca bobot COCO; bahan bawaannya
    bahan mesin awal ditambah bahan di ringkasan.json dataset. jualan: tujuan "jualan" (tools/periksa-jualan.mjs tetap memeriksa
    bahannya); tanpa itu "belajar", kecuali dari nol."""
    if dari_nol and bobot_awal_mesin is not None:
        raise ValueError("bobot_awal_mesin tidak bisa digabung dengan dari nol")
    matikan_kernel_triton()
    perangkat = perangkat or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(benih)
    rng = np.random.default_rng(benih)
    if bobot_awal_mesin is not None:
        model, awal = model_dari_mesin(jenis, bobot_awal_mesin)
        if not bahan:
            dari_awal = json.loads((Path(bobot_awal_mesin) / "mesin.json").read_text())["bahan"]
            dari_dataset = json.loads((Path(folder_dataset) / "ringkasan.json").read_text())["bahan"]
            bahan = list(dict.fromkeys([*dari_awal, *dari_dataset]))
        bahan = list(bahan)
    elif dari_nol:
        bahan = list(bahan or json.loads((Path(folder_dataset) / "ringkasan.json").read_text())["bahan"])
        if "bobot-yolox" in bahan:
            raise ValueError("mesin dari nol tidak memuat bobot-yolox; daftar bahannya keliru")
        model, awal = buat_model(jenis), None
    else:
        bahan = list(bahan or BAHAN)
        if "bobot-yolox" not in bahan:
            bahan.append("bobot-yolox")
        daftar = daftar_berkas(kunci)
        butir = BUTIR_BOBOT[jenis]
        berkas_awal = verifikasi_berkas(Path(folder_unduhan) / butir / daftar.get(butir, ("?", ""))[0], butir, daftar)
        model = buat_model(jenis)
        dimuat, dilewati = muat_bobot_awal(model, berkas_awal)
        awal = {"butir": butir, "sha256": sha256_berkas(berkas_awal), "dimuat": dimuat, "dilewati": dilewati}
    model.to(perangkat)
    from yolox.utils import ModelEMA

    ema = ModelEMA(model, 0.9998)
    jalur, kotak = baca_sisi(Path(folder_dataset) / "train")
    langkah = max(1, math.ceil(len(jalur) / UKURAN_ANGKATAN))
    dasar = LAJU * UKURAN_ANGKATAN / 64
    optim = torch.optim.SGD(kelompok_parameter(model), lr=dasar, momentum=0.9, nesterov=True)
    total, panas = zaman * langkah, PEMANASAN * langkah

    def laju(it):
        if it < panas:
            return dasar * (it / panas) ** 2
        return dasar * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * (it - panas) / max(1, total - panas))))

    terbaik, catatan, it = None, [], 0
    for z in range(1, zaman + 1):
        model.train()
        urutan, rugi_total = rng.permutation(len(jalur)), 0.0
        for a in range(0, len(jalur), UKURAN_ANGKATAN):
            pilih = urutan[a:a + UKURAN_ANGKATAN]
            x, y = angkatan([jalur[i] for i in pilih], [kotak[i] for i in pilih], ukuran, rng)
            for g in optim.param_groups:
                g["lr"] = laju(it)
            rugi = model(x.to(perangkat), y.to(perangkat))["total_loss"]
            optim.zero_grad()
            rugi.backward()
            optim.step()
            ema.update(model)
            it += 1
            rugi_total += float(rugi.detach()) * len(pilih)
        ema.ema.eval()
        val, _, _ = deteksi.kumpulkan(Path(folder_dataset) / "valid", cari_torch(ema.ema, ukuran, perangkat))
        ambang = deteksi.pilih_ambang(val)
        f1 = deteksi.f1(val, ambang)
        catatan.append({"zaman": z, "rugi": round(rugi_total / max(1, len(jalur)), 4), "f1_validasi": round(f1, 4),
                        "ambang": ambang})
        print(f"zaman {z}: rugi {catatan[-1]['rugi']}, F1 validasi {f1:.4f} (ambang {ambang})", flush=True)
        if terbaik is None or f1 > terbaik[0]:
            terbaik = (f1, z, ambang, {k: v.detach().cpu().clone().contiguous() for k, v in ema.ema.state_dict().items()})
    from safetensors.torch import save_file

    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    save_file(terbaik[3], str(keluar / "mesin.safetensors"))
    meta = {"nama": nama or f"pencari-yolox-{jenis}-{ukuran}", "tujuan": "jualan" if dari_nol or jualan else "belajar",
            "bahan": bahan,
            "jenis": jenis, "ukuran": int(ukuran),
            "sha256_bobot": sha256_berkas(keluar / "mesin.safetensors"), "zaman": zaman, "zaman_terbaik": terbaik[1],
            "f1_validasi_terbaik": round(terbaik[0], 4), "ambang_validasi": terbaik[2], "benih": benih, "perangkat": perangkat,
            "bobot_awal": awal, "gambar_latih": len(jalur), "catatan": catatan}
    (keluar / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def muat_mesin(folder_mesin):
    """mesin.safetensors -> model eval di CPU; bobot yang SHA-256-nya tidak sama dengan mesin.json ditolak."""
    from safetensors.torch import load_file

    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin.json").read_text())
    if sha256_berkas(folder / "mesin.safetensors") != meta["sha256_bobot"]:
        raise ModelDitolak(f"{folder.name}/mesin.safetensors: SHA-256 tidak sama dengan yang dicatat di mesin.json")
    model = buat_model(meta["jenis"])
    model.load_state_dict(load_file(str(folder / "mesin.safetensors")))
    return model.eval()


def selisih_mentah(t, o):
    """Keluaran mentah torch dan ONNX (N, 6) -> (selisih koordinat terbesar dalam piksel masukan, selisih peluang terbesar).
    Dipisah karena satuannya beda: koordinat sampai ratusan piksel, peluang 0..1. Satu batas mutlak 1e-2 untuk keduanya
    menolak nano-640 karena 0,038 piksel, padahal peluangnya hanya beda 1,0e-4 (Rencana 13)."""
    d = np.abs(np.asarray(t, np.float64) - np.asarray(o, np.float64))
    return float(d[:, :4].max()), float(d[:, 4:].max())


def mentah_sama(koordinat, peluang):
    """Keluaran mentah dianggap sama bila koordinat dalam BATAS_EKSPOR piksel dan peluang dalam BATAS_PELUANG."""
    return koordinat < BATAS_EKSPOR and peluang < BATAS_PELUANG


def ekspor(folder_mesin, folder_dataset, jumlah=20):
    """mesin.safetensors -> mesin.onnx + mesin-onnx.json, hanya bila deteksi ONNX sama dengan torch (kotak dalam BATAS_EKSPOR
    piksel, yakin dalam 1e-3) pada semua gambar valid yang diperiksa DAN keluaran mentah semua kotak, termasuk yang di bawah
    ambang, sama menurut mentah_sama (tidak bisa lolos kosong walau belum ada deteksi). Butuh pustaka onnx (image lab
    tambahan)."""
    import onnxruntime as ort

    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin.json").read_text())
    model = muat_mesin(folder)
    ukuran = int(meta["ukuran"])
    torch.onnx.export(model, torch.zeros(1, 3, ukuran, ukuran), str(folder / "mesin.onnx"), input_names=["images"],
                      output_names=["output"], opset_version=17, dynamo=False)
    sesi = ort.InferenceSession(str(folder / "mesin.onnx"), providers=["CPUExecutionProvider"])
    berkas = sorted(p for p in (Path(folder_dataset) / "valid" / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN)
    gambar = sama = 0
    koordinat = peluang = 0.0
    for b in berkas[:jumlah]:
        g = cv2.imread(str(b))
        if g is None:
            continue
        x, skala = pyx.masukan(g, ukuran)
        with torch.no_grad():
            t = model(torch.from_numpy(x))[0].numpy()
        o = sesi.run(None, {"images": x})[0][0]
        k, p = selisih_mentah(t, o)
        koordinat, peluang = max(koordinat, k), max(peluang, p)
        a, d = pyx.urai_keluaran(t, skala), pyx.urai_keluaran(o, skala)
        gambar += 1
        sama += int(len(a) == len(d) and all(max(abs(p - q) for p, q in zip(u[:4], v[:4])) < BATAS_EKSPOR
                                             and abs(u[4] - v[4]) < 1e-3 for u, v in zip(a, d)))
    if gambar == 0 or sama != gambar or not mentah_sama(koordinat, peluang):
        (folder / "mesin.onnx").unlink(missing_ok=True)
        raise ModelDitolak(f"ONNX tidak sama dengan torch: deteksi sama {sama} dari {gambar} gambar, selisih mentah koordinat "
                           f"{koordinat:.2e} piksel, peluang {peluang:.2e}")
    hasil = {"nama": meta["nama"], "tujuan": meta["tujuan"], "bahan": meta["bahan"], "jenis": meta["jenis"], "ukuran": ukuran,
             "sha256_onnx": sha256_berkas(folder / "mesin.onnx"), "sha256_bobot": meta["sha256_bobot"],
             "pemeriksaan": {"gambar": gambar, "sama": sama, "selisih_koordinat": koordinat, "selisih_peluang": peluang}}
    (folder / "mesin-onnx.json").write_text(json.dumps(hasil, indent=1))
    return hasil


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Melatih pencari plat YOLOX (Rencana 13).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("latih")
    a.add_argument("jenis", choices=sorted(JENIS))
    a.add_argument("ukuran", type=int)
    for nama in ("folder_dataset", "folder_unduhan", "keluar"):
        a.add_argument(nama)
    a.add_argument("--zaman", type=int, default=ZAMAN)
    a.add_argument("--benih", type=int, default=BENIH)
    a.add_argument("--perangkat", choices=("cpu", "cuda"))
    a.add_argument("--kunci", default=str(LOKASI_KUNCI))
    a.add_argument("--bahan", type=lambda t: [x for x in t.split(",") if x], default=None)
    a.add_argument("--dari-nol", action="store_true", help="tanpa bobot COCO; mesin jualan (Rencana 24)")
    a.add_argument("--nama", help="nama mesin di mesin.json; bawaan pencari-yolox-<jenis>-<ukuran>")
    a.add_argument("--bobot-awal-mesin", help="folder mesin sendiri sebagai titik berangkat; bobot COCO tidak dibaca (Rencana 25)")
    a.add_argument("--jualan", action="store_true", help="tujuan mesin jualan (bahan tetap diperiksa periksa-jualan.mjs)")
    e = perintah.add_parser("ekspor")
    for nama in ("folder_mesin", "folder_dataset"):
        e.add_argument(nama)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "latih":
            m = latih(p.jenis, p.ukuran, p.folder_dataset, p.folder_unduhan, p.keluar, p.zaman, p.benih, p.perangkat, p.kunci,
                      p.bahan, p.dari_nol, p.nama, p.bobot_awal_mesin, p.jualan)
            awal = m["bobot_awal"]
            if awal is None:
                asal = "tidak ada (dari nol)"
            elif "folder" in awal:
                asal = f"mesin {awal['folder']}"
            else:
                asal = f"dimuat {awal['dimuat']}, dilewati {awal['dilewati']}"
            print(f"selesai {m['nama']} ({m['tujuan']}): zaman terbaik {m['zaman_terbaik']} dari {m['zaman']}, F1 validasi "
                  f"{m['f1_validasi_terbaik']} (ambang {m['ambang_validasi']}); bobot awal {asal}; gambar latih {m['gambar_latih']}")
        else:
            m = ekspor(p.folder_mesin, p.folder_dataset)
            v = m["pemeriksaan"]
            print(f"diekspor mesin.onnx: deteksi sama {v['sama']} dari {v['gambar']} gambar; selisih mentah terbesar: koordinat "
                  f"{v['selisih_koordinat']:.2e} piksel, peluang {v['selisih_peluang']:.2e}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
