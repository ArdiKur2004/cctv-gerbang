"""Mesin baca huruf buatan sendiri (langkah 3, spec 2.1): CNN kecil + LSTM dua arah + CTC, dilatih dari nol (spec 2.3).

Masukan: potongan plat kelabu, diubah ukurannya menjadi TINGGI x LEBAR. Keluaran: PANJANG_DERET langkah, tiap langkah
peluang 36 huruf/angka + "kosong"; dibaca dengan cara CTC rakus (ulangan digabung, kosong dibuang).

Latihan HANYA menerima kedatangan latih. Pemilihan zaman terbaik memakai 1 dari BAGIAN_VALIDASI plat latih (per plat,
menurut SHA-256 teks berawalan "validasi:"), tidak pernah set uji. Bobot disimpan sebagai safetensors (bukan pickle) dengan
SHA-256-nya di mesin.json; pembaca menolak bobot yang tidak cocok. mesin.json sekaligus manifes untuk pemeriksa mesin
jualan (tools/periksa-jualan.mjs): bahannya hanya INDO-ALPR, tanpa bobot awal.

  latih: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/mesin_baca.py latih /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/mesin-baca-1
  baca:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/mesin_baca.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/mesin-baca-1 /kerja/data/keluaran/baca-mesin-1
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from safetensors.torch import load_file, save_file
from torch import nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, matikan_kernel_triton, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from model_terkunci import ModelDitolak, sha256_berkas  # noqa: E402

HURUF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TINGGI, LEBAR = 48, 160
PANJANG_DERET = 40
UKURAN_ANGKATAN = 64
ZAMAN = 80
BAGIAN_VALIDASI = 10
NAMA = "mesin-baca-1"
BAHAN = ["dataset-indo-alpr"]


def sandi(teks):
    """Teks plat -> daftar indeks 1..36 (0 = kosong CTC). Huruf di luar daftar ditolak tanpa mencetak teksnya."""
    try:
        return [HURUF.index(c) + 1 for c in teks]
    except ValueError:
        raise ValueError("teks memuat huruf di luar daftar HURUF") from None


def urai_sandi(indeks):
    """Bacaan CTC rakus: ulangan berturut-turut digabung, kosong dibuang."""
    hasil, sebelum = [], 0
    for i in indeks:
        if i != sebelum and i != 0:
            hasil.append(HURUF[i - 1])
        sebelum = i
    return "".join(hasil)


def siapkan(kelabu):
    """Gambar kelabu uint8 berukuran apa pun -> uint8 TINGGI x LEBAR."""
    cara = cv2.INTER_AREA if kelabu.shape[1] > LEBAR else cv2.INTER_LINEAR
    return cv2.resize(kelabu, (LEBAR, TINGGI), interpolation=cara)


def ubah_acak(gambar, rng):
    """Variasi acak untuk latihan saja: miring dan geser sedikit, terang-gelap, kabur, derau, warna terbalik."""
    tinggi, lebar = gambar.shape
    m = cv2.getRotationMatrix2D((lebar / 2, tinggi / 2), rng.uniform(-4, 4), rng.uniform(0.9, 1.05))
    m[:, 2] += (rng.uniform(-4, 4), rng.uniform(-2, 2))
    g = cv2.warpAffine(gambar, m, (lebar, tinggi), borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    g = g * rng.uniform(0.7, 1.3) + rng.uniform(-30, 30)
    if rng.random() < 0.3:
        g = cv2.GaussianBlur(g, (3, 3), 0)
    g = g + rng.normal(0, rng.uniform(0, 8), g.shape)
    if rng.random() < 0.3:
        g = 255 - g
    return np.clip(g, 0, 255).astype(np.uint8)


def _blok(masuk, keluar, kumpul):
    return [nn.Conv2d(masuk, keluar, 3, padding=1), nn.BatchNorm2d(keluar), nn.ReLU(inplace=True), nn.MaxPool2d(kumpul)]


class MesinBaca(nn.Module):
    """48x160 kelabu -> (N, PANJANG_DERET, 37)."""

    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(*_blok(1, 32, (2, 2)), *_blok(32, 64, (2, 2)), *_blok(64, 128, (2, 1)),
                                 *_blok(128, 128, (2, 1)), nn.AdaptiveAvgPool2d((1, PANJANG_DERET)))
        self.rnn = nn.LSTM(128, 128, num_layers=2, bidirectional=True, batch_first=True)
        self.kepala = nn.Linear(256, len(HURUF) + 1)

    def forward(self, x):
        fitur = self.cnn(x).squeeze(2).transpose(1, 2)
        return self.kepala(self.rnn(fitur)[0])


def ke_tensor(gambar_uint8):
    return torch.from_numpy(gambar_uint8.astype(np.float32) / 255.0).unsqueeze(1)


def baca_banyak(mesin, gambar_uint8, perangkat):
    """Gambar siap (N x TINGGI x LEBAR) -> daftar bacaan."""
    mesin.eval()
    hasil = []
    with torch.no_grad():
        for awal in range(0, len(gambar_uint8), 256):
            keluar = mesin(ke_tensor(gambar_uint8[awal:awal + 256]).to(perangkat)).argmax(2).cpu().numpy()
            hasil += [urai_sandi(baris) for baris in keluar]
    return hasil


def bagi_validasi(latih):
    """Kedatangan latih -> (inti, validasi), per PLAT dan tetap: 1 dari BAGIAN_VALIDASI plat menurut SHA-256."""
    def ke_validasi(k):
        return int(hashlib.sha256(f"validasi:{k['teks']}".encode()).hexdigest()[:8], 16) % BAGIAN_VALIDASI == 0
    return [k for k in latih if not ke_validasi(k)], [k for k in latih if ke_validasi(k)]


def muat(kedatangan, folder_gambar):
    """Kedatangan -> (gambar uint8 N x TINGGI x LEBAR, teks per gambar, jumlah gambar tak terbaca)."""
    gambar, teks, tak = [], [], 0
    for k in kedatangan:
        for b in k["berkas"]:
            g = cv2.imread(str(Path(folder_gambar) / b), cv2.IMREAD_GRAYSCALE)
            if g is None:
                tak += 1
                continue
            gambar.append(siapkan(g))
            teks.append(k["teks"])
    return (np.stack(gambar) if gambar else np.zeros((0, TINGGI, LEBAR), np.uint8)), teks, tak


def latih_mesin(latih, folder_gambar, keluar, zaman=ZAMAN, benih=0, perangkat=None):
    """Melatih dari kedatangan LATIH saja (set uji tidak pernah diberikan ke fungsi ini). Kembali: isi mesin.json."""
    matikan_kernel_triton()
    perangkat = perangkat or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(benih)
    rng = np.random.default_rng(benih)
    inti, validasi = bagi_validasi(latih)
    gi, ti, tak_i = muat(inti, folder_gambar)
    gv, tv, tak_v = muat(validasi, folder_gambar)
    sandi_i = [sandi(t) for t in ti]
    mesin = MesinBaca().to(perangkat)
    langkah = max(1, math.ceil(len(gi) / UKURAN_ANGKATAN))
    optim = torch.optim.AdamW(mesin.parameters(), lr=1e-3, weight_decay=1e-4)
    jadwal = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=2e-3, total_steps=zaman * langkah)
    ctc = nn.CTCLoss(blank=0, zero_infinity=True)
    terbaik, catatan = None, []
    for z in range(1, zaman + 1):
        mesin.train()
        urutan, jumlah_rugi = rng.permutation(len(gi)), 0.0
        for awal in range(0, len(gi), UKURAN_ANGKATAN):
            pilih = urutan[awal:awal + UKURAN_ANGKATAN]
            x = ke_tensor(np.stack([ubah_acak(gi[i], rng) for i in pilih])).to(perangkat)
            target = torch.tensor([c for i in pilih for c in sandi_i[i]], dtype=torch.long, device=perangkat)
            panjang_target = torch.tensor([len(sandi_i[i]) for i in pilih], dtype=torch.long, device=perangkat)
            log_p = mesin(x).log_softmax(2).permute(1, 0, 2)
            panjang_masuk = torch.full((len(pilih),), log_p.shape[0], dtype=torch.long, device=perangkat)
            rugi = ctc(log_p, target, panjang_masuk, panjang_target)
            optim.zero_grad()
            rugi.backward()
            nn.utils.clip_grad_norm_(mesin.parameters(), 5.0)
            optim.step()
            jadwal.step()
            jumlah_rugi += float(rugi.detach()) * len(pilih)
        benar_v = sum(b == t for b, t in zip(baca_banyak(mesin, gv, perangkat), tv))
        catatan.append({"zaman": z, "rugi": round(jumlah_rugi / max(1, len(gi)), 4), "validasi_benar": int(benar_v)})
        print(f"zaman {z}: rugi {catatan[-1]['rugi']}, validasi benar {benar_v} dari {len(gv)} gambar", flush=True)
        if terbaik is None or benar_v >= terbaik[0]:
            terbaik = (benar_v, z, {n: v.detach().cpu().clone().contiguous() for n, v in mesin.state_dict().items()})
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    save_file(terbaik[2], str(keluar / "mesin.safetensors"))
    meta = {"nama": NAMA, "tujuan": "belajar", "bahan": BAHAN,
            "keterangan": "CNN + LSTM dua arah + CTC, dilatih dari nol; tanpa bobot awal",
            "huruf": HURUF, "tinggi": TINGGI, "lebar": LEBAR, "panjang_deret": PANJANG_DERET,
            "sha256_bobot": sha256_berkas(keluar / "mesin.safetensors"), "zaman": zaman, "zaman_terbaik": terbaik[1],
            "benih": benih, "perangkat": perangkat, "plat": {"inti": len(inti), "validasi": len(validasi)},
            "gambar": {"inti": len(gi), "validasi": len(gv)}, "tak_terbaca": tak_i + tak_v,
            "validasi_benar_terbaik": int(terbaik[0]), "catatan": catatan}
    (keluar / "mesin.json").write_text(json.dumps(meta, indent=1))
    return meta


class PembacaMesin:
    """Pembaca dengan mesin yang sudah dilatih. Bobot yang SHA-256-nya tidak sama dengan mesin.json ditolak."""

    def __init__(self, folder_mesin, perangkat=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin.json").read_text())
        if sha256_berkas(folder / "mesin.safetensors") != meta["sha256_bobot"]:
            raise ModelDitolak(f"{folder.name}/mesin.safetensors: SHA-256 tidak sama dengan yang dicatat di mesin.json")
        if (meta["huruf"], meta["tinggi"], meta["lebar"], meta["panjang_deret"]) != (HURUF, TINGGI, LEBAR, PANJANG_DERET):
            raise ModelDitolak(f"{folder.name}: bentuk mesin di mesin.json tidak cocok dengan kode ini")
        matikan_kernel_triton()
        self.perangkat = perangkat or ("cuda" if torch.cuda.is_available() else "cpu")
        self._mesin = MesinBaca()
        self._mesin.load_state_dict(load_file(str(folder / "mesin.safetensors")))
        self._mesin.to(self.perangkat).eval()

    def __call__(self, gambar_bgr):
        return baca_banyak(self._mesin, siapkan(cv2.cvtColor(gambar_bgr, cv2.COLOR_BGR2GRAY))[None], self.perangkat)[0]


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Mesin baca huruf buatan sendiri (Rencana 8).")
    perintah = urai_argumen.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("latih")
    for nama in ("pembagian", "folder_gambar", "keluar"):
        a.add_argument(nama)
    a.add_argument("--zaman", type=int, default=ZAMAN)
    a.add_argument("--benih", type=int, default=0)
    a.add_argument("--perangkat", choices=("cpu", "cuda"))
    b = perintah.add_parser("baca")
    for nama in ("pembagian", "folder_gambar", "folder_mesin", "keluar"):
        b.add_argument(nama)
    b.add_argument("--perangkat", choices=("cpu", "cuda"))
    p = urai_argumen.parse_args(argumen)
    pembagian = json.loads(Path(p.pembagian).read_text())
    if p.perintah == "latih":
        meta = latih_mesin(pembagian["latih"], p.folder_gambar, p.keluar, p.zaman, p.benih, p.perangkat)
        print(f"selesai: zaman terbaik {meta['zaman_terbaik']} dari {meta['zaman']}, validasi benar "
              f"{meta['validasi_benar_terbaik']} dari {meta['gambar']['validasi']} gambar; plat inti {meta['plat']['inti']}, "
              f"validasi {meta['plat']['validasi']}; gambar tak terbaca {meta['tak_terbaca']}")
        return 0
    try:
        pembaca = PembacaMesin(p.folder_mesin, p.perangkat)
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    baris, ringkasan = nilai(pembagian, p.folder_gambar, pembaca, "uji")
    ringkasan = {"model": NAMA, "sisi": "uji", "perangkat": pembaca.perangkat, **ringkasan}
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for x in baris:
            berkas.write(json.dumps(x) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for k in KELOMPOK:
        print(f"{k:<13} {uraikan(ringkasan['per_kelompok'][k])}")
    print(f"detik per gambar: {ringkasan['detik_per_gambar']} ({pembaca.perangkat})")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
