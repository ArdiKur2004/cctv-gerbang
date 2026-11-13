"""Pengenal ciri kendaraan: jenis dan warna dari potongan kendaraan (Rencana 33, spec Fase 3 tahap 1).

Isi modul:
- `warna_aturan` (calon tanpa latihan): warna dari piksel bagian TENGAH potongan (tepi sering latar). Jenuh rendah -> hitam, abu_perak,
  atau putih menurut terang; selain itu dari rona.
- `nyaris_tanpa_warna` dan `saring_inframerah` (K52): warna tidak bisa dibaca dari gambar yang nyaris tanpa warna. Pemeriksaannya dipakai
  pada GAMBAR PENUH, bukan potongan: kendaraan hitam atau putih juga nyaris tanpa warna, jadi potongannya sendiri tidak bisa membedakan
  inframerah dari kendaraan tanpa warna.
- `ubah_acak`: variasi latihan yang TIDAK mengubah rona maupun jenuh (terang dikalikan, bukan ditambah), supaya label warna tetap benar.
- `MesinCiri`, `latih`, `ekspor`, `PengenalCiri`: CNN kecil UKURAN x UKURAN (urutan warna OpenCV) dengan satu kepala kelas. Zaman dipilih
  dengan benar terbanyak di validasi OWNER saja; sumber lain hanya menambah bahan latih.
- `nilai_ambang`: benar, salah, dan tak yakin pada satu ambang, beserta `nilai` = benar - salah. Spec Fase 3: ciri salah berarti satpam
  dipanggil untuk kendaraan yang sah, jadi benar saja bukan ukuran yang benar.
- `jenis_coco` (calon tanpa latihan): jenis dari pencari kendaraan COCO yang dijalankan pada potongan.

Ambang "tak yakin" TIDAK disimpan di mesin: `PengenalCiri` menuntutnya sebagai argumen, supaya tidak ada ambang tersembunyi.
Potongan memuat kendaraan dan plat: agen tidak membukanya. Layar hanya hitungan.

  latih:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/ciri.py latih <folder potongan> jenis <keluar> --zaman 30 --nama ciri-jenis-j1
  ekspor: powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/ciri.py ekspor <folder mesin> <folder potongan>
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from safetensors.torch import save_file
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from baca_vlm import matikan_kernel_triton  # noqa: E402
from model_terkunci import ModelDitolak, sha256_berkas  # noqa: E402

UKURAN = 96
TENGAH = 0.4  # bagian tengah potongan yang dipakai aturan warna
AMBANG_ABU = 20  # jenuh (0..255); persentil 95 di bawah ini = gambar nyaris tanpa warna
AMBANG_JENUH = 60  # jenuh tengah di bawah ini = tanpa warna (hitam, abu_perak, putih)
GELAP, TERANG = 70, 180  # batas terang untuk hitam / abu_perak / putih
TAK_YAKIN = "tak_yakin"
SUMBER_OWNER = "o"
UKURAN_ANGKATAN = 64
ZAMAN = 30
BENIH = 0
BATAS_EKSPOR = 1e-4  # selisih peluang terbesar antara ONNX dan torch
# Rona OpenCV (0..179) -> warna. Batasnya dipilih dari roda warna, bukan dari angka hasil; mutunya diukur, tidak diklaim.
RONA = ((10, "merah"), (19, "coklat_krem"), (34, "kuning"), (85, "hijau"), (130, "biru"), (169, "lainnya"), (179, "merah"))


def siapkan(gambar, ukuran=UKURAN):
    """Potongan BGR berukuran apa pun -> uint8 ukuran x ukuran x 3."""
    cara = cv2.INTER_AREA if gambar.shape[1] > ukuran else cv2.INTER_LINEAR
    return cv2.resize(gambar, (ukuran, ukuran), interpolation=cara)


def _tengah(gambar):
    tinggi, lebar = gambar.shape[:2]
    dy, dx = int(tinggi * (1 - TENGAH) / 2), int(lebar * (1 - TENGAH) / 2)
    potong = gambar[dy:tinggi - dy, dx:lebar - dx]
    return potong if potong.size else gambar


def nyaris_tanpa_warna(gambar):
    """True bila hampir tidak ada piksel berwarna (gambar inframerah atau kelabu). Dipakai pada gambar PENUH."""
    jenuh = cv2.cvtColor(gambar, cv2.COLOR_BGR2HSV)[:, :, 1]
    return bool(np.percentile(jenuh, 95) < AMBANG_ABU)


def warna_aturan(potongan):
    """Warna badan kendaraan dari piksel bagian tengah potongan. Selalu memberi satu kelas warna (bukan "tak yakin")."""
    hsv = cv2.cvtColor(_tengah(potongan), cv2.COLOR_BGR2HSV).reshape(-1, 3)
    rona, jenuh, terang = (float(np.median(hsv[:, i])) for i in range(3))
    if jenuh < AMBANG_JENUH:
        return "hitam" if terang < GELAP else ("abu_perak" if terang < TERANG else "putih")
    return next(w for batas, w in RONA if rona <= batas)


def saring_inframerah(warna, gambar_penuh):
    """K52: warna dari gambar yang nyaris tanpa warna selalu "tak yakin". gambar_penuh None = saringan tidak berlaku."""
    if gambar_penuh is not None and nyaris_tanpa_warna(gambar_penuh):
        return TAK_YAKIN
    return warna


def ubah_acak(gambar, rng):
    """Variasi latihan: cermin, putar dan geser kecil, terang DIKALIKAN (rona dan jenuh tetap), kabur, derau kecil."""
    tinggi, lebar = gambar.shape[:2]
    g = gambar[:, ::-1] if rng.random() < 0.5 else gambar
    m = cv2.getRotationMatrix2D((lebar / 2, tinggi / 2), rng.uniform(-8, 8), rng.uniform(0.9, 1.1))
    m[:, 2] += (rng.uniform(-0.04, 0.04) * lebar, rng.uniform(-0.04, 0.04) * tinggi)
    g = cv2.warpAffine(g, m, (lebar, tinggi), borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    g = g * rng.uniform(0.95, 1.05)
    if rng.random() < 0.3:
        g = cv2.GaussianBlur(g, (3, 3), 0)
    g = g + rng.normal(0, 4, g.shape)
    return np.clip(g, 0, 255).astype(np.uint8)


def nilai_ambang(ramalan, benar, ambang):
    """[(kelas, yakin)] dan label benar -> {"benar", "salah", "tak_yakin", "nilai"}; nilai = benar - salah. Kelas TAK_YAKIN dan yakin di
    bawah ambang tidak dihitung benar maupun salah (tidak memanggil satpam)."""
    h = {"benar": 0, "salah": 0, "tak_yakin": 0}
    for (kelas, yakin), b in zip(ramalan, benar):
        if kelas == TAK_YAKIN or float(yakin) < ambang:
            h["tak_yakin"] += 1
        else:
            h["benar" if kelas == b else "salah"] += 1
    return {**h, "nilai": h["benar"] - h["salah"]}


def jenis_coco(potongan, cari):
    """Calon tanpa latihan: pencari kendaraan COCO pada potongan; jenis dari kotak terbesar. Tanpa kotak -> tak yakin."""
    kotak = list(cari(potongan))
    if not kotak:
        return TAK_YAKIN, 0.0
    k = max(kotak, key=lambda v: (v[2] - v[0]) * (v[3] - v[1]))
    return str(k[5]), float(k[4])


def _blok(masuk, keluar):
    return [nn.Conv2d(masuk, keluar, 3, padding=1), nn.BatchNorm2d(keluar), nn.ReLU(inplace=True), nn.MaxPool2d(2)]


class MesinCiri(nn.Module):
    """UKURAN x UKURAN x 3 (urutan warna OpenCV) -> (N, jumlah kelas)."""

    def __init__(self, jumlah_kelas):
        super().__init__()
        self.cnn = nn.Sequential(*_blok(3, 32), *_blok(32, 64), *_blok(64, 128), *_blok(128, 128),
                                 nn.AdaptiveAvgPool2d(1), nn.Flatten())
        self.kepala = nn.Linear(128, jumlah_kelas)

    def forward(self, x):
        return self.kepala(self.cnn(x))


def ke_tensor(gambar_uint8):
    return torch.from_numpy(np.ascontiguousarray(gambar_uint8).astype(np.float32) / 255.0).permute(0, 3, 1, 2)


def baris_ciri(folder_potongan, ciri):
    """ciri.csv -> baris yang punya label untuk `ciri`."""
    with open(Path(folder_potongan) / "ciri.csv", newline="") as f:
        return [b for b in csv.DictReader(f) if b[ciri]]


def muat(baris, folder_potongan, ukuran=UKURAN):
    """Baris (yang sudah punya "_label") -> (gambar uint8 N x ukuran x ukuran x 3, label, jumlah tak terbaca)."""
    gambar, label, tak = [], [], 0
    for b in baris:
        g = cv2.imread(str(Path(folder_potongan) / b["berkas"]))
        if g is None:
            tak += 1
            continue
        gambar.append(siapkan(g, ukuran))
        label.append(b["_label"])
    return (np.stack(gambar) if gambar else np.zeros((0, ukuran, ukuran, 3), np.uint8)), label, tak


def ramal(mesin, gambar, kelas, perangkat):
    """Gambar siap -> [(kelas, yakin)] dengan yakin = peluang kelas terbesar."""
    mesin.eval()
    hasil = []
    with torch.no_grad():
        for awal in range(0, len(gambar), 256):
            p = mesin(ke_tensor(gambar[awal:awal + 256]).to(perangkat)).softmax(1).cpu().numpy()
            hasil += [(kelas[int(i)], float(p[n, i])) for n, i in enumerate(p.argmax(1))]
    return hasil


def latih(folder_potongan, ciri, keluar, sumber=None, zaman=ZAMAN, benih=BENIH, perangkat=None, nama=None, ukuran=UKURAN,
          jenis=None):
    """Melatih dari sisi latih (sumber boleh dibatasi); zaman dipilih dengan benar terbanyak di validasi OWNER. Sisi uji tidak pernah
    dibaca. ukuran: masukan mesin, dicatat di mesin.json supaya ekspor dan pemakaian memakai ukuran yang sama (Rencana 35). jenis:
    hanya potongan berjenis itu yang dipakai, di sisi latih maupun validasi. Kembali: isi mesin.json."""
    folder_potongan = Path(folder_potongan)
    semua = baris_ciri(folder_potongan, ciri)
    if jenis is not None:
        semua = [b for b in semua if b.get("jenis") == jenis]
    for b in semua:
        b["_label"] = b[ciri]
    baris_latih = [b for b in semua if b["sisi"] == "latih" and (sumber is None or b["sumber"] in sumber)]
    baris_validasi = [b for b in semua if b["sisi"] == "validasi" and b["sumber"] == SUMBER_OWNER]
    if not baris_latih:
        raise ValueError(f"tidak ada potongan berlabel {ciri} di sisi latih")
    if not baris_validasi:
        raise ValueError(f"tidak ada potongan berlabel {ciri} di validasi owner: zaman tidak bisa dipilih")
    matikan_kernel_triton()
    perangkat = perangkat or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(benih)
    rng = np.random.default_rng(benih)
    kelas = sorted({b["_label"] for b in baris_latih})
    gl, ll, tak_l = muat(baris_latih, folder_potongan, ukuran)
    gv, lv, tak_v = muat(baris_validasi, folder_potongan, ukuran)
    nomor = torch.tensor([kelas.index(t) for t in ll], dtype=torch.long)
    mesin = MesinCiri(len(kelas)).to(perangkat)
    langkah = max(1, math.ceil(len(gl) / UKURAN_ANGKATAN))
    optim = torch.optim.AdamW(mesin.parameters(), lr=1e-3, weight_decay=1e-4)
    jadwal = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=2e-3, total_steps=zaman * langkah)
    rugi_fn = nn.CrossEntropyLoss(label_smoothing=0.05)
    terbaik, catatan = None, []
    for z in range(1, zaman + 1):
        mesin.train()
        urutan, jumlah_rugi = rng.permutation(len(gl)), 0.0
        for awal in range(0, len(gl), UKURAN_ANGKATAN):
            pilih = urutan[awal:awal + UKURAN_ANGKATAN]
            x = ke_tensor(np.stack([ubah_acak(gl[i], rng) for i in pilih])).to(perangkat)
            rugi = rugi_fn(mesin(x), nomor[pilih].to(perangkat))
            optim.zero_grad()
            rugi.backward()
            optim.step()
            jadwal.step()
            jumlah_rugi += float(rugi.detach()) * len(pilih)
        h = nilai_ambang(ramal(mesin, gv, kelas, perangkat), lv, 0.0)
        catatan.append({"zaman": z, "rugi": round(jumlah_rugi / max(1, len(gl)), 4), **h})
        print(f"zaman {z}: rugi {catatan[-1]['rugi']}, validasi owner benar {h['benar']} dari {len(gv)}", flush=True)
        if terbaik is None or h["benar"] > terbaik[0]:  # tertinggi PERTAMA, supaya pilihannya tetap
            terbaik = (h["benar"], z, h, {n: v.detach().cpu().clone().contiguous() for n, v in mesin.state_dict().items()})
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    save_file(terbaik[3], str(keluar / "mesin.safetensors"))
    meta = {"nama": nama or f"ciri-{ciri}", "tujuan": "jualan",
            "bahan": json.loads((folder_potongan / "ringkasan.json").read_text())["bahan"],
            "keterangan": "CNN kecil dari nol pada potongan kendaraan; zaman dipilih dari validasi owner (Rencana 33)",
            "ciri": ciri, "kelas": kelas, "ukuran": int(ukuran), "jenis": jenis,
            "sumber_latih": sorted(sumber) if sumber else None,
            "sha256_bobot": sha256_berkas(keluar / "mesin.safetensors"), "zaman": zaman, "zaman_terbaik": terbaik[1],
            "benih": benih, "perangkat": perangkat, "gambar": {"latih": len(gl), "validasi_owner": len(gv)},
            "tak_terbaca": tak_l + tak_v, "validasi_owner": {"gambar": len(gv), **terbaik[2]}, "catatan": catatan}
    (keluar / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


def muat_mesin(folder_mesin):
    """mesin.safetensors -> (model eval di CPU, isi mesin.json); bobot yang SHA-256-nya berubah ditolak."""
    from safetensors.torch import load_file

    folder = Path(folder_mesin)
    meta = json.loads((folder / "mesin.json").read_text())
    if sha256_berkas(folder / "mesin.safetensors") != meta["sha256_bobot"]:
        raise ModelDitolak(f"{folder.name}/mesin.safetensors: SHA-256 tidak sama dengan yang dicatat di mesin.json")
    mesin = MesinCiri(len(meta["kelas"]))
    mesin.load_state_dict(load_file(str(folder / "mesin.safetensors")))
    return mesin.eval(), meta


def ekspor(folder_mesin, folder_potongan, jumlah=40):
    """mesin.safetensors -> mesin.onnx + mesin-onnx.json, hanya bila peluang ONNX sama dengan torch pada gambar validasi."""
    import onnxruntime as ort

    folder = Path(folder_mesin)
    mesin, meta = muat_mesin(folder)
    ukuran = int(meta["ukuran"])  # ukuran saat melatih, bukan tetapan modul (Rencana 35)
    torch.onnx.export(mesin, torch.zeros(1, 3, ukuran, ukuran), str(folder / "mesin.onnx"), input_names=["gambar"],
                      output_names=["keluaran"], dynamic_axes={"gambar": {0: "n"}, "keluaran": {0: "n"}}, opset_version=17,
                      dynamo=False)
    sesi = ort.InferenceSession(str(folder / "mesin.onnx"), providers=["CPUExecutionProvider"])
    baris = [b for b in baris_ciri(folder_potongan, meta["ciri"]) if b["sisi"] == "validasi"][:jumlah]
    for b in baris:
        b["_label"] = b[meta["ciri"]]
    gambar, _, _ = muat(baris, folder_potongan, ukuran)
    if len(gambar) == 0:
        (folder / "mesin.onnx").unlink(missing_ok=True)
        raise ModelDitolak("tidak ada gambar validasi untuk memeriksa ONNX")
    x = ke_tensor(gambar)
    with torch.no_grad():
        t = mesin(x).softmax(1).numpy()
    o = torch.from_numpy(sesi.run(None, {"gambar": x.numpy()})[0]).softmax(1).numpy()
    selisih = float(np.abs(t - o).max())
    sama = int((t.argmax(1) == o.argmax(1)).sum())
    if sama != len(gambar) or selisih > BATAS_EKSPOR:
        (folder / "mesin.onnx").unlink(missing_ok=True)
        raise ModelDitolak(f"ONNX tidak sama dengan torch: kelas sama {sama} dari {len(gambar)}, selisih peluang {selisih:.2e}")
    hasil = {"nama": meta["nama"], "tujuan": meta["tujuan"], "bahan": meta["bahan"], "ciri": meta["ciri"], "kelas": meta["kelas"],
             "ukuran": ukuran, "jenis": meta.get("jenis"), "sha256_onnx": sha256_berkas(folder / "mesin.onnx"),
             "sha256_bobot": meta["sha256_bobot"],
             "pemeriksaan": {"gambar": len(gambar), "kelas_sama": sama, "selisih_peluang": selisih}}
    (folder / "mesin-onnx.json").write_text(json.dumps(hasil, indent=1))
    return hasil


class PengenalCiri:
    """Pengenal ciri dengan mesin.onnx di CPU. mesin.onnx yang SHA-256-nya tidak sama dengan mesin-onnx.json ditolak sebelum
    onnxruntime dimuat. `ambang` wajib disebut pemanggil: tidak ada ambang "tak yakin" yang tersembunyi di mesin."""

    def __init__(self, folder_mesin, ambang, utas=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin-onnx.json").read_text())
        if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
            raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
        if not 0 <= float(ambang) <= 1:
            raise ValueError(f"ambang harus di antara 0 dan 1, bukan {ambang}")
        import onnxruntime as ort

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self.kelas, self.ciri, self.ambang = meta["kelas"], meta["ciri"], float(ambang)
        self.ukuran = int(meta["ukuran"])  # ukuran yang dicatat mesin, bukan tetapan modul (Rencana 35)
        self._sesi = ort.InferenceSession(str(folder / "mesin.onnx"), opsi, providers=["CPUExecutionProvider"])

    def __call__(self, potongan):
        """(kelas, yakin); kelas TAK_YAKIN bila yakin di bawah ambang."""
        x = ke_tensor(siapkan(potongan, self.ukuran)[None]).numpy()
        keluar = self._sesi.run(None, {"gambar": x})[0][0]
        p = np.exp(keluar - keluar.max())
        p = p / p.sum()
        i = int(p.argmax())
        return (self.kelas[i], float(p[i])) if p[i] >= self.ambang else (TAK_YAKIN, float(p[i]))


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Pengenal ciri kendaraan: jenis dan warna (Rencana 33).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("latih")
    for nama in ("folder_potongan", "ciri", "keluar"):
        a.add_argument(nama)
    a.add_argument("--zaman", type=int, default=ZAMAN)
    a.add_argument("--benih", type=int, default=BENIH)
    a.add_argument("--perangkat", choices=("cpu", "cuda"))
    a.add_argument("--sumber", type=lambda t: [x for x in t.split(",") if x], default=None)
    a.add_argument("--nama")
    a.add_argument("--ukuran", type=int, default=UKURAN, help="ukuran masukan mesin; dicatat di mesin.json (Rencana 35)")
    a.add_argument("--jenis", help="hanya potongan berjenis ini yang dipakai melatih dan memvalidasi (Rencana 35)")
    e = perintah.add_parser("ekspor")
    for nama in ("folder_mesin", "folder_potongan"):
        e.add_argument(nama)
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "latih":
            m = latih(p.folder_potongan, p.ciri, p.keluar, p.sumber, p.zaman, p.benih, p.perangkat, p.nama, p.ukuran, p.jenis)
            v = m["validasi_owner"]
            print(f"selesai {m['nama']} ({m['tujuan']}, bahan {m['bahan']}): zaman terbaik {m['zaman_terbaik']} dari {m['zaman']}; "
                  f"ukuran {m['ukuran']}; jenis {m['jenis']}; kelas {m['kelas']}; validasi owner benar {v['benar']} salah "
                  f"{v['salah']} dari {v['gambar']}")
        else:
            h = ekspor(p.folder_mesin, p.folder_potongan)
            c = h["pemeriksaan"]
            print(f"diekspor mesin.onnx: kelas sama {c['kelas_sama']} dari {c['gambar']} gambar; selisih peluang "
                  f"{c['selisih_peluang']:.2e}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
