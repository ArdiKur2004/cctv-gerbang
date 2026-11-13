"""Tahap kendaraan (K39, Rencana 19 Task 7b): kendaraan dicari lebih dulu, lalu kotak plat hanya diterima bila tengahnya berada
di dalam kotak kendaraan. Usulan owner: (1) kendaraan, (2) tampak depan atau belakang, (3) plat di area kendaraan itu. Langkah 2
belum ada.

- Pencari kendaraan: YOLOX COCO terkunci (80 kelas, tools/vendor.lock.json) dalam ONNX. Yang dipakai hanya KELAS; sepeda tidak
  berplat, jadi tidak ikut. Yakin = objek x peluang kelas terbesar, seperti YOLOX; kotak yang kelas terbesarnya bukan kendaraan
  dibuang.
- Plat di dalam kendaraan: tengah kotak plat di dalam kotak kendaraan (tepi ikut). Bila beberapa kendaraan memuatnya, yang
  terkecil dipilih (motor di depan truk).
- Cara pakai (Rencana 25, K45, K50 butir 1): maks_kendaraan membatasi pencarian plat ke kendaraan terdekat (urut_terdekat: tepi
  bawah terendah), dan cadangan_utuh mencari plat di gambar utuh bila tidak ada kendaraan setinggi MIN_TINGGI (motor yang tidak
  terlihat pencari kendaraan). Keduanya mati bila tidak diminta.
- PencariKendaraan: mesin.onnx yang SHA-256-nya tidak sama dengan mesin-onnx.json ditolak sebelum onnxruntime dimuat. Tidak
  memuat torch. Ambang dibaca dari mesin-onnx.json (dipilih di sisi latih, Rencana 19 Task 7b Step 4).
- ekspor: bobot .pth terkunci -> YOLOX 80 kelas (weights_only; semua tensor harus termuat) -> mesin.onnx, disimpan hanya bila
  keluaran mentah ONNX sama dengan torch (latih_yolox.mentah_sama). Bahan ["bobot-yolox"]: ~~BELUM-JELAS, jadi tanda mesinnya
  RISET-SAJA, hanya untuk mesin belajar~~; sejak K48 (19 Okt, keputusan owner, risiko hukum dicatat di SEED.md §3) BOLEH-PRODUK.
  Tanda mesin dibaca tools/periksa-jualan.mjs dari daftar bahan, jadi bila K48 dibalik tandanya ikut turun.

- tetapkan (Rencana 32): mesin satu kelas dari latih_yolox (pencari kendaraan jualan, K48) mendapat kendaraan.json berisi ambang yang
  dipilih, terikat ke SHA-256 mesin.onnx. PencariKendaraan memuatnya dengan jenis "kendaraan".

  ekspor: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/kendaraan.py ekspor tiny /kerja/data/unduhan /kerja/data/keluaran/dataset/plat-lighting/valid/images /kerja/data/keluaran/kendaraan-yolox-coco --ambang 0.25
  tetapkan: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/kendaraan.py tetapkan <folder mesin> --ambang <a> --alasan "<rencana dan bukti>"
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deteksi  # noqa: E402
import pencari_yolox as pyx  # noqa: E402
from model_terkunci import LOKASI_KUNCI, ModelDitolak, daftar_berkas, sha256_berkas, verifikasi_berkas  # noqa: E402

KELAS = {2: "mobil", 3: "motor", 5: "bus", 7: "truk"}  # nomor kelas COCO
MIN_TINGGI = 40  # piksel gambar utuh; kendaraan yang lebih pendek tidak dicari platnya (plat manusia pun tak terbaca)
MARGIN = 0.1


def urai(keluaran, skala, ambang):
    """Keluaran YOLOX COCO (N, 85) -> [(x1, y1, x2, y2, yakin, jenis)] kendaraan dalam piksel foto asli, sesudah NMS."""
    kelas = keluaran[:, 5:].argmax(1)
    skor = keluaran[:, 4] * keluaran[:, 5:].max(1)
    pilih = (skor >= ambang) & np.isin(kelas, list(KELAS))
    k, s, c = keluaran[pilih, :4], skor[pilih], kelas[pilih]
    kotak = np.stack([k[:, 0] - k[:, 2] / 2, k[:, 1] - k[:, 3] / 2, k[:, 0] + k[:, 2] / 2, k[:, 1] + k[:, 3] / 2], 1) / skala
    return [(*(float(x) for x in kotak[i]), float(s[i]), KELAS[int(c[i])]) for i in pyx.nms(kotak, s)]


def kendaraan_pemuat(kotak, kendaraan):
    """Kendaraan terkecil yang memuat tengah kotak plat (tepi ikut), atau None."""
    cx, cy = (kotak[0] + kotak[2]) / 2, (kotak[1] + kotak[3]) / 2
    muat = [v for v in kendaraan if v[0] <= cx <= v[2] and v[1] <= cy <= v[3]]
    return min(muat, key=lambda v: (v[2] - v[0]) * (v[3] - v[1])) if muat else None


def _kotak(v):
    return tuple(float(x) for x in v[:4])


def saring(kotak, kendaraan):
    """Kotak plat -> (kotak di dalam kendaraan, masing-masing ditambah jenis dan kotak kendaraannya; jumlah yang dibuang).
    Kotak kendaraan (Rencana 21) dipakai untuk ciri letak plat di kendaraannya (tools/lab/letak.py)."""
    terima = []
    for k in kotak:
        v = kendaraan_pemuat(k, kendaraan)
        if v is not None:
            terima.append((*k[:5], v[5], _kotak(v)))
    return terima, len(kotak) - len(terima)


def urut_terdekat(kendaraan):
    """K45 (Rencana 25): kendaraan terdekat dari kamera lebih dulu, yaitu yang tepi bawah kotaknya paling rendah di gambar (y2
    terbesar). Di lembar tanpa plat Rencana 24, kendaraan berplat terbaca adalah yang terendah pada 23 dari 25 gambar."""
    return sorted(kendaraan, key=lambda v: -v[3])


def cari_dalam_kendaraan(gambar, kendaraan, cari, ambang, margin=MARGIN, min_tinggi=MIN_TINGGI, maks_kendaraan=None,
                         cadangan_utuh=False):
    """K39 langkah 3 (Rencana 20): plat dicari di dalam potongan tiap kendaraan setinggi minimal min_tinggi, yang diperlebar margin
    dari lebar dan tingginya. Letterbox pencari memperbesar potongan kecil. Kotak di atas ambang dikembalikan ke koordinat gambar
    utuh dan ditambah jenis dan kotak kendaraannya; yang tengahnya di luar kendaraannya dibuang; kotak kembar dari kendaraan yang
    bertumpuk disatukan dengan NMS. Kembali: [(x1, y1, x2, y2, yakin, jenis, (kx1, ky1, kx2, ky2))].
    Rencana 25: maks_kendaraan = hanya sekian kendaraan terdekat (urut_terdekat) di antara yang cukup tinggi; cadangan_utuh = bila
    tidak ada kendaraan cukup tinggi, kotak di atas ambang dari gambar utuh, tanpa jenis dan kotak kendaraan."""
    if maks_kendaraan is not None and maks_kendaraan < 1:
        raise ValueError(f"maks_kendaraan minimal 1, bukan {maks_kendaraan}")
    tinggi, lebar = gambar.shape[:2]
    cukup = [v for v in kendaraan if v[3] - v[1] >= min_tinggi]
    if not cukup:
        return [k for k in cari(gambar) if k[4] >= ambang] if cadangan_utuh else []
    if maks_kendaraan is not None:
        cukup = urut_terdekat(cukup)[:maks_kendaraan]
    semua = []
    for v in cukup:
        mx, my = margin * (v[2] - v[0]), margin * (v[3] - v[1])
        x1, y1 = max(0, int(v[0] - mx)), max(0, int(v[1] - my))
        x2, y2 = min(lebar, int(np.ceil(v[2] + mx))), min(tinggi, int(np.ceil(v[3] + my)))
        if x2 - x1 < 2 or y2 - y1 < 2:
            continue
        for k in cari(gambar[y1:y2, x1:x2]):
            if k[4] < ambang:
                continue
            utuh = (k[0] + x1, k[1] + y1, k[2] + x1, k[3] + y1, k[4])
            if kendaraan_pemuat(utuh, [v]) is not None:
                semua.append((*utuh, v[5], _kotak(v)))
    if not semua:
        return []
    simpan = pyx.nms(np.array([s[:4] for s in semua], np.float64), np.array([s[4] for s in semua], np.float64))
    return [semua[i] for i in simpan]


BERKAS_KENDARAAN = "kendaraan.json"
JENIS_SATU_KELAS = "kendaraan"


def tetapkan(folder_mesin, ambang, alasan):
    """Rencana 32: mesin satu kelas dari latih_yolox (mesin-onnx.json tanpa "kelas") dijadikan pencari kendaraan dengan ambang yang
    sudah dipilih. kendaraan.json diikat ke SHA-256 mesin.onnx, supaya ambang untuk mesin lain tidak terpakai diam-diam. Kembali: isi
    kendaraan.json."""
    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin-onnx.json").read_text())
    if "kelas" in meta:
        raise ValueError("mesin COCO memakai ambang di mesin-onnx.json; tetapkan hanya untuk mesin satu kelas")
    if not 0 < float(ambang) < 1:
        raise ValueError(f"ambang harus di antara 0 dan 1, bukan {ambang}")
    if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
        raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
    isi = {"ambang": float(ambang), "jenis": JENIS_SATU_KELAS, "sha256_onnx": meta["sha256_onnx"], "alasan": alasan}
    (folder / BERKAS_KENDARAAN).write_text(json.dumps(isi, indent=1))
    return isi


class PencariKendaraan:
    """Pencari kendaraan dengan mesin.onnx di CPU. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali daftar
    (x1, y1, x2, y2, yakin, jenis) dengan yakin minimal ambang.
    - Mesin COCO (mesin-onnx.json berisi "kelas", dari ekspor): ambang di mesin-onnx.json; jenis dari KELAS.
    - Mesin satu kelas dari latih_yolox (Rencana 32, pencari kendaraan jualan): ambang dari argumen `ambang`, atau dari kendaraan.json
      (tetapkan) yang SHA-256 onnx-nya sama; tanpa keduanya ditolak SEBELUM onnxruntime dimuat. Jenis tiap kotak "kendaraan".
    Argumen `ambang` mengganti ambang bawaan keduanya (untuk memilih ambang di sisi latih)."""

    def __init__(self, folder_mesin, utas=None, ambang=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin-onnx.json").read_text())
        if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
            raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
        self.satu_kelas = "kelas" not in meta
        if ambang is None and self.satu_kelas:
            berkas = folder / BERKAS_KENDARAAN
            if not berkas.exists():
                raise ModelDitolak(f"{folder.name}: mesin satu kelas belum ditetapkan sebagai pencari kendaraan (kendaraan.py tetapkan)")
            isi = json.loads(berkas.read_text())
            if isi.get("sha256_onnx") != meta["sha256_onnx"]:
                raise ModelDitolak(f"{folder.name}/kendaraan.json ditetapkan untuk mesin.onnx lain")
            ambang = isi["ambang"]
        import onnxruntime as ort

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self.ukuran = int(meta["ukuran"])
        self.ambang = float(ambang if ambang is not None else meta["ambang"])
        self._sesi = ort.InferenceSession(str(folder / "mesin.onnx"), opsi, providers=["CPUExecutionProvider"])

    def __call__(self, gambar_bgr):
        x, skala = pyx.masukan(gambar_bgr, self.ukuran)
        keluaran = self._sesi.run(None, {"images": x})[0][0]
        if self.satu_kelas:
            return [(*k, JENIS_SATU_KELAS) for k in pyx.urai_keluaran(keluaran, skala, self.ambang)]
        return urai(keluaran, skala, self.ambang)


def buat_model_coco(jenis):
    """YOLOX 80 kelas berukuran `jenis`, dengan BatchNorm seperti YOLOX (eps 1e-3, momentum 0,03)."""
    import torch

    import latih_yolox as ly

    ly.siapkan_yolox()
    from yolox.models import YOLOPAFPN, YOLOX, YOLOXHead

    dalam, lebar, dw = ly.JENIS[jenis]
    model = YOLOX(YOLOPAFPN(dalam, lebar, in_channels=[256, 512, 1024], depthwise=dw),
                  YOLOXHead(80, lebar, in_channels=[256, 512, 1024], depthwise=dw))
    for m in model.modules():
        if isinstance(m, torch.nn.BatchNorm2d):
            m.eps, m.momentum = 1e-3, 0.03
    return model


def ekspor(jenis, folder_unduhan, folder_gambar, keluar, ambang, kunci=LOKASI_KUNCI, ukuran=640, jumlah=20):
    """Bobot COCO terkunci -> mesin.onnx + mesin-onnx.json di `keluar`, hanya bila semua tensor termuat dan keluaran mentah ONNX
    sama dengan torch pada paling banyak `jumlah` gambar di folder_gambar. Butuh pustaka onnx (image lab tambahan)."""
    import torch

    import latih_yolox as ly

    daftar = daftar_berkas(kunci)
    butir = ly.BUTIR_BOBOT[jenis]
    berkas = verifikasi_berkas(Path(folder_unduhan) / butir / daftar.get(butir, ("?", ""))[0], butir, daftar)
    model = buat_model_coco(jenis)
    _, dilewati = ly.muat_bobot_awal(model, berkas)
    if dilewati:
        raise ModelDitolak(f"{butir}: {dilewati} tensor tidak termuat; bukan bobot YOLOX COCO 80 kelas")
    model.eval()
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(model, torch.zeros(1, 3, ukuran, ukuran), str(keluar / "mesin.onnx"), input_names=["images"],
                      output_names=["output"], opset_version=17, dynamo=False)
    import onnxruntime as ort

    sesi = ort.InferenceSession(str(keluar / "mesin.onnx"), providers=["CPUExecutionProvider"])
    gambar, koordinat, peluang = 0, 0.0, 0.0
    for b in sorted(p for p in Path(folder_gambar).iterdir() if p.suffix.lower() in deteksi.AKHIRAN)[:jumlah]:
        g = cv2.imread(str(b))
        if g is None:
            continue
        x, _ = pyx.masukan(g, ukuran)
        with torch.no_grad():
            t = model(torch.from_numpy(x))[0].numpy()
        k, p = ly.selisih_mentah(t, sesi.run(None, {"images": x})[0][0])
        koordinat, peluang = max(koordinat, k), max(peluang, p)
        gambar += 1
    if gambar == 0 or not ly.mentah_sama(koordinat, peluang):
        (keluar / "mesin.onnx").unlink(missing_ok=True)
        raise ModelDitolak(f"ONNX tidak sama dengan torch pada {gambar} gambar: selisih mentah koordinat {koordinat:.2e} piksel, "
                           f"peluang {peluang:.2e}")
    meta = {"nama": keluar.name, "tujuan": "belajar", "bahan": ["bobot-yolox"], "jenis": jenis, "ukuran": ukuran,
            "kelas": {str(k): v for k, v in KELAS.items()}, "ambang": ambang, "sha256_onnx": sha256_berkas(keluar / "mesin.onnx"),
            "sha256_pth": sha256_berkas(berkas),
            "pemeriksaan": {"gambar": gambar, "selisih_koordinat": koordinat, "selisih_peluang": peluang}}
    (keluar / "mesin-onnx.json").write_text(json.dumps(meta, indent=1))
    return meta


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Pencari kendaraan untuk tahap kendaraan rantai (K39).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    e = perintah.add_parser("ekspor")
    e.add_argument("jenis", choices=("nano", "tiny"))
    for nama in ("folder_unduhan", "folder_gambar", "keluar"):
        e.add_argument(nama)
    e.add_argument("--ambang", type=float, required=True)
    t = perintah.add_parser("tetapkan", help="mesin satu kelas (latih_yolox) dijadikan pencari kendaraan (Rencana 32)")
    t.add_argument("folder_mesin")
    t.add_argument("--ambang", type=float, required=True)
    t.add_argument("--alasan", required=True)
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "tetapkan":
            isi = tetapkan(p.folder_mesin, p.ambang, p.alasan)
            print(f"ditetapkan: ambang {isi['ambang']}, jenis {isi['jenis']}, onnx {isi['sha256_onnx'][:12]}")
            return 0
        meta = ekspor(p.jenis, p.folder_unduhan, p.folder_gambar, p.keluar, p.ambang)
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    c = meta["pemeriksaan"]
    print(f"{meta['nama']}: ONNX sama dengan torch pada {c['gambar']} gambar (selisih koordinat {c['selisih_koordinat']:.2e} "
          f"piksel, peluang {c['selisih_peluang']:.2e}); ambang {meta['ambang']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
