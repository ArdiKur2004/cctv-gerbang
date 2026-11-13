# Fase 0A, Rencana 8: Mesin baca huruf buatan sendiri yang pertama — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Angka pertama mesin baca huruf buatan sendiri (langkah 3, spec 2.1), dilatih dari nol hanya dengan bahan latih
INDO-ALPR yang sudah dibersihkan (Rencana 7), dipilih dengan potongan validasi dari bahan latih, lalu dinilai SEKALI pada set
uji 937 plat. Angkanya dibandingkan dengan Qwen3-VL dan fast-plate-ocr dengan dua cara hitung: semua plat, dan tanpa plat
yang labelnya dipilih dari bacaan kedua pembaca itu (cara yang adil, lihat laporan Rencana 6 bagian 6).

**Architecture:** Satu modul `tools/lab/mesin_baca.py`: sandi huruf, penyiapan gambar, variasi acak untuk latihan, model
kecil CNN + LSTM dua arah + CTC (ditulis sendiri dengan torch), latihan yang hanya menerima sisi latih, penyimpanan bobot
berformat safetensors (bukan pickle) dengan SHA-256 di `mesin.json`, dan pembaca yang memeriksa SHA-256 itu sebelum memuat.
Satu alat `tools/lab/banding_pembaca.py` membandingkan pembaca dengan dua cara hitung. `mesin.json` sekaligus manifes untuk
pemeriksa mesin jualan (`tools/periksa-jualan.mjs`).

**Tech Stack:** torch 2.14.1 + CUDA, safetensors 0.8.0, OpenCV 4.14, NumPy, pytest **yang sudah ada di image lab**. Tidak ada
yang dipasang, tidak ada yang diunduh, tidak ada bobot awal.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md) 2.1
(langkah 3), 2.3 (bobot dilatih sendiri), 2.4 (dua mesin dan pemeriksa), 8.1 langkah 7 (mesin belajar pertama), 8.3 (aturan
ukur); K16, K21, K24; laporan [`../bukti/2026-10-14-label-bahan-latih.md`](../bukti/2026-10-14-label-bahan-latih.md) dan
[`../bukti/2026-10-14-label-dan-pembaca-kedua.md`](../bukti/2026-10-14-label-dan-pembaca-kedua.md).

---

## Yang diukur sebelum rencana ini ditulis (14 Okt 2026)

Dua skrip sekali pakai di lab (`data/alat-sementara/ukur_lab_latih.py`, `ukur_bahan_latih.py`); hanya hitungan.

| Hal | Yang terbaca |
|---|---|
| Pustaka di image lab | torch 2.14.1+cu130, torchvision 0.29.1, safetensors 0.8.0, onnxruntime 1.30.0, OpenCV 4.14.0, NumPy 2.5.3. **Tidak ada** timm, onnx, albumentations |
| Kartu grafis dari dalam lab | RTX 4060, 8.187 MB; konvolusi + CTC + backward berjalan; safetensors simpan-muat berjalan |
| Bahan (`latih-koreksi/pembagian-koreksi.json`) | Latih 2.824 plat, 4.414 gambar; uji 937 plat, 26 di antaranya berlabel pilihan dua pembaca (`label_penerbit`) |
| Panjang label | Latih: 3 (2), 4 (5), 5 (39), 6 (92), 7 (881), 8 (1.700), 9 (105). Uji: 4–9, kebanyakan 7–8 |
| Huruf | 36 jenis (10 angka, 26 huruf), semuanya muncul di kedua sisi |
| Gambar per plat (latih) | 1: 1.935, 2: 604, 3: 130, 4: 81, … |
| Ukuran potongan latih | tinggi persentil 5/50/95 = 30/112/297 titik; lebar 73/374/718; lebar/tinggi 1,83/2,97/4,40 |
| Pemeriksa mesin jualan | Manifes `{"nama", "tujuan": "jualan" atau "belajar", "bahan": [id...]}`; bahan dibaca dari `data-asal/bahan.json` |
| Andaian kode (`coba_andaian_r8.py`) | safetensors menyimpan dan memuat tensor tanpa dimensi (`num_batches_tracked` BatchNorm); CTC di kartu grafis menerima target disambung yang ada di kartu grafis |

Akibatnya bagi rencana ini:

1. **Model ditulis sendiri dengan torch** (tidak ada timm), **dilatih dari nol** (spec 2.3), dari INDO-ALPR saja, yang
   bervonis `BOLEH-PRODUK`. Jadi tanda mesinnya bisa `BOLEH-PRODUK`, dan itu diperiksa dengan pemeriksa yang sudah ada.
2. Masukan kelabu 48×160 (perbandingan 3,3:1, dekat median 2,97); deret keluaran 40 langkah, jauh di atas label terpanjang
   (9) sehingga CTC tidak kekurangan langkah.
3. **Set uji hanya dipakai sekali, di akhir.** Model dipilih dengan 1 dari 10 plat latih (validasi, per plat, menurut SHA-256
   teks yang diberi awalan supaya tidak berkorelasi dengan pembagian Rencana 5).
4. Perbandingan yang adil memakai 911 plat (tanpa 26 label pilihan pembaca); angka pada 937 plat ikut dilaporkan.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–7 | Bengkel sampai bahan latih dibersihkan | Selesai 13–14 Okt |
| **8 (dokumen ini)** | Mesin baca huruf buatan sendiri yang pertama; perbandingan adil dengan dua pembaca; tanda mesin | Ditulis |
| 9 | Mencari plat di foto utuh dan video (langkah 1); plat buatan komputer; taksiran kecepatan di kotak; laporan Fase 0A. Perbaikan mesin baca huruf bila angka Rencana 8 menuntutnya | Ditulis saat Rencana 8 selesai |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 7. Tambahan:
- **Set uji tidak pernah dipakai untuk memilih apa pun** (zaman, ukuran model, variasi acak). Bila angka uji membuat ingin
  mengubah sesuatu, itu dicatat untuk Rencana 9, bukan diubah lalu diukur ulang pada set uji yang sama.
- Latihan sungguhan adalah job kartu grafis: periksa `nvidia-smi`, jalankan di latar, jangan menjalankan gerbang lab selama
  job jalan.
- Bobot disimpan hanya sebagai safetensors; tidak ada `torch.save` (pickle).

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/mesin_baca.py`, `tools/lab/uji/test_mesin_baca.py` (baru) | Mesin baca huruf: sandi, gambar, model, latihan, pembaca | 1 |
| `tools/lab/banding_pembaca.py`, `tools/lab/uji/test_banding_pembaca.py` (baru) | Perbandingan dengan dua cara hitung | 2 |
| `bukti/2026-10-1x-mesin-baca-pertama.md` dan ringkasan JSON (baru) | Laporan | 4 |
| `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Catatan | 4 |

Berkas data (di `data/keluaran/`): `mesin-baca-1/` (bobot dan `mesin.json`, tanpa plat), `baca-mesin-1/` dan
`baca-mesin-1-cpu/` (bacaan; `hasil.jsonl` memuat plat), `banding-pembaca/` (hitungan).

---

### Task 1: Mesin baca huruf

**Files:**
- Create: `tools/lab/mesin_baca.py`
- Create: `tools/lab/uji/test_mesin_baca.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_mesin_baca.py`:

```python
"""Uji tools/lab/mesin_baca.py: sandi huruf, gambar, model, latihan kecil di CPU, penyimpanan tanpa pickle, pembaca yang
memeriksa bobot, dan rantai baris perintah (latihan tidak menyentuh set uji; layar tanpa nomor plat)."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mesin_baca as mb  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "mesin_baca.py"
TEKS = ["B1234XY", "D5678AB", "AB12CD", "F9012Z", "H3456KL", "L7890MN", "N2468PQ", "R1357ST"]


def gambar_plat(teks):
    kanvas = np.full((60, 200), 255, np.uint8)
    cv2.putText(kanvas, teks, (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
    return kanvas


def siapkan(tmp_path, sisi_latih=TEKS, sisi_uji=("B1234XY",)):
    folder = tmp_path / "gambar"
    pembagian = {}
    for sisi, daftar in (("latih", sisi_latih), ("uji", sisi_uji)):
        pembagian[sisi] = []
        for t in daftar:
            berkas = []
            for i in range(3):
                nama = f"{sisi}/{t}_{i}.png"
                (folder / sisi).mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(folder / nama), gambar_plat(t))
                berkas.append(nama)
            pembagian[sisi].append({"teks": t, "kelompok": "mobil-terang", "berkas": berkas})
    jalur = tmp_path / "pembagian.json"
    jalur.write_text(json.dumps(pembagian))
    return pembagian, jalur, folder


def test_sandi_dan_urai_sandi():
    assert mb.sandi("B1") == [12, 2]
    # CTC: ulangan berturut-turut digabung, kosong (0) dibuang, ulangan yang dipisah kosong tetap dua huruf.
    assert mb.urai_sandi([0, 12, 12, 0, 2, 0, 2, 3, 3]) == "B112"


def test_sandi_menolak_huruf_di_luar_daftar_tanpa_mencetak_teksnya():
    with pytest.raises(ValueError) as galat:
        mb.sandi("B-1234")

    assert "1234" not in str(galat.value)


def test_bentuk_keluaran_mesin():
    keluar = mb.MesinBaca()(torch.zeros(2, 1, mb.TINGGI, mb.LEBAR))

    assert tuple(keluar.shape) == (2, mb.PANJANG_DERET, len(mb.HURUF) + 1)


def test_bagi_validasi_per_plat_dan_tetap():
    latih = [{"teks": f"D{n}AB", "berkas": []} for n in range(1, 401)]

    inti, validasi = mb.bagi_validasi(latih)

    assert 20 < len(validasi) < 70 and len(inti) + len(validasi) == 400
    assert not {k["teks"] for k in inti} & {k["teks"] for k in validasi}
    assert (inti, validasi) == mb.bagi_validasi(latih)


def test_ubah_acak_tetap_dengan_benih_dan_ukurannya_sama():
    g = mb.siapkan(gambar_plat("B1234XY"))

    a = mb.ubah_acak(g, np.random.default_rng(7))
    b = mb.ubah_acak(g, np.random.default_rng(7))

    assert a.shape == (mb.TINGGI, mb.LEBAR) and a.dtype == np.uint8 and np.array_equal(a, b)


def test_latihan_kecil_menurunkan_rugi_dan_menyimpan_tanpa_pickle(tmp_path):
    pembagian, _, folder = siapkan(tmp_path)

    meta = mb.latih_mesin(pembagian["latih"], folder, tmp_path / "mesin", zaman=30, perangkat="cpu")

    assert meta["catatan"][-1]["rugi"] < meta["catatan"][0]["rugi"]
    assert sorted(p.name for p in (tmp_path / "mesin").iterdir()) == ["mesin.json", "mesin.safetensors"]
    simpan = json.loads((tmp_path / "mesin/mesin.json").read_text())
    assert (simpan["tujuan"], simpan["bahan"], len(simpan["sha256_bobot"])) == ("belajar", ["dataset-indo-alpr"], 64)


def test_pembaca_menolak_bobot_yang_berubah(tmp_path):
    pembagian, _, folder = siapkan(tmp_path)
    mb.latih_mesin(pembagian["latih"], folder, tmp_path / "mesin", zaman=1, perangkat="cpu")
    bacaan = mb.PembacaMesin(tmp_path / "mesin", perangkat="cpu")(cv2.cvtColor(gambar_plat("B1234XY"), cv2.COLOR_GRAY2BGR))
    assert set(bacaan) <= set(mb.HURUF)

    with open(tmp_path / "mesin/mesin.safetensors", "ab") as berkas:
        berkas.write(b"x")

    with pytest.raises(ModelDitolak, match="SHA-256"):
        mb.PembacaMesin(tmp_path / "mesin", perangkat="cpu")


def test_baris_perintah_latih_tidak_menyentuh_uji_lalu_baca_tanpa_nomor_plat(tmp_path):
    _, jalur, folder = siapkan(tmp_path)
    latih = subprocess.run([sys.executable, str(SKRIP), "latih", str(jalur), str(folder), str(tmp_path / "mesin"),
                            "--zaman", "2", "--perangkat", "cpu"], capture_output=True, text=True)
    assert latih.returncode == 0, latih.stdout + latih.stderr
    meta = json.loads((tmp_path / "mesin/mesin.json").read_text())
    # Rantainya: hanya gambar latih yang dimuat (8 plat x 3 gambar); gambar uji tidak pernah dibaca saat latihan.
    assert meta["gambar"]["inti"] + meta["gambar"]["validasi"] == len(TEKS) * 3 and meta["tak_terbaca"] == 0

    baca = subprocess.run([sys.executable, str(SKRIP), "baca", str(jalur), str(folder), str(tmp_path / "mesin"),
                           str(tmp_path / "keluar"), "--perangkat", "cpu"], capture_output=True, text=True)

    assert baca.returncode == 0, baca.stdout + baca.stderr
    assert len((tmp_path / "keluar/hasil.jsonl").read_text().splitlines()) == 3
    for larangan in ("1234", "5678"):
        assert larangan not in latih.stdout + baca.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'mesin_baca'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/mesin_baca.py`:

```python
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
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `149 passed` (141 + 8 baru) dan `EXIT=0`. Lama jalan gerbang bertambah karena tiga latihan kecil di CPU; dicatat.

- [x] **Step 5: Commit**

```bash
git add tools/lab/mesin_baca.py tools/lab/uji/test_mesin_baca.py
git commit -q -F - <<'EOF'
Mesin baca huruf buatan sendiri: model, latihan, pembaca

Alasan: spec 8.1 langkah 7 (mesin belajar pertama) dan spec 2.3 (bobot
dilatih sendiri). CNN kecil + LSTM dua arah + CTC, ditulis sendiri dengan
torch yang sudah ada di image lab, dilatih dari nol tanpa bobot awal. Latihan
hanya menerima sisi latih; zaman terbaik dipilih dengan 1 dari 10 plat latih,
tidak pernah dengan set uji. Bobot disimpan sebagai safetensors (bukan
pickle) dengan SHA-256 di mesin.json, dan pembaca menolak bobot yang
berubah. mesin.json sekaligus manifes untuk pemeriksa mesin jualan.

Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError:
mesin_baca). Gerbang lab: 141 -> 149.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Perbandingan pembaca dengan dua cara hitung

**Files:**
- Create: `tools/lab/banding_pembaca.py`
- Create: `tools/lab/uji/test_banding_pembaca.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_banding_pembaca.py`:

```python
"""Uji tools/lab/banding_pembaca.py: plat berlabel pilihan pembaca dipisah, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import banding_pembaca as bp  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "banding_pembaca.py"


def k(teks, **lain):
    return {"teks": teks, "kelompok": "mobil-terang", "berkas": [f"test/{teks}_1.png"], **lain}


PEMBAGIAN = {"latih": [], "uji": [k("D1500X"), k("D1600Y", label_penerbit="D1600X"), k("D1700X")]}


def test_label_pilihan_pembaca_dipisah():
    bagian = bp.bagian(PEMBAGIAN)

    assert [len(bagian[c]["uji"]) for c in bp.CARA] == [3, 2]


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps(PEMBAGIAN))
    (tmp_path / "a.jsonl").write_text("".join(json.dumps({"berkas": x["berkas"][0], "bacaan": x["teks"]}) + "\n"
                                              for x in PEMBAGIAN["uji"]))

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path / "keluar"),
                            "--hasil", f"tiruan={tmp_path / 'a.jsonl'}"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    teks = hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "1500" not in teks and "1600" not in teks
    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert r["tanpa-label-pilihan-pembaca"]["tiruan"]["mobil-terang"]["kedatangan"] == 2
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'banding_pembaca'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/banding_pembaca.py`:

```python
"""Membandingkan pembaca pada set uji yang sama, dengan dua cara hitung (Rencana 8).

- "semua": seluruh set uji.
- "tanpa-label-pilihan-pembaca": tanpa plat yang labelnya dibetulkan memakai bacaan yang disepakati Qwen3-VL dan
  fast-plate-ocr (Rencana 6; ditandai `label_penerbit`). Pada plat itu kedua pembaca pasti dinilai benar, jadi
  perbandingan yang adil dengan pembaca ketiga memakai cara hitung ini.

Bacaan dibaca dari hasil.jsonl tiap pembaca (tanpa menjalankan model). Keluaran ringkasan.json (hitungan saja).

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/banding_pembaca.py /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/banding-pembaca --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl --hasil mesin-baca-1=/kerja/data/keluaran/baca-mesin-1/hasil.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, ringkas  # noqa: E402
from label_curiga import baca_hasil  # noqa: E402

CARA = ("semua", "tanpa-label-pilihan-pembaca")


def bagian(pembagian):
    return {"semua": pembagian,
            "tanpa-label-pilihan-pembaca": {**pembagian, "uji": [k for k in pembagian["uji"] if "label_penerbit" not in k]}}


def singkat(r):
    n, benar = r["kedatangan"], r["kedatangan_benar"]
    if n == 0:
        return "kosong"
    if r["terlalu_sedikit"]:
        return f"{benar}/{n} (sedikit)"
    bawah, atas = r["rentang_95_kedatangan"]
    return f"{benar}/{n} ({100 * benar / n:.1f}%; {100 * bawah:.1f}-{100 * atas:.1f}%)"


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Membandingkan pembaca dengan dua cara hitung.")
    urai_argumen.add_argument("pembagian")
    urai_argumen.add_argument("keluar")
    urai_argumen.add_argument("--hasil", action="append", required=True, help="nama=jalur hasil.jsonl, boleh berulang")
    p = urai_argumen.parse_args(argumen)
    if not all("=" in h for h in p.hasil):
        print("SALAH PAKAI: --hasil harus nama=jalur")
        return 2
    pembaca = [h.split("=", 1) for h in p.hasil]
    bacaan = {nama: baca_hasil(jalur) for nama, jalur in pembaca}
    ringkasan = {}
    for cara, isi in bagian(json.loads(Path(p.pembagian).read_text())).items():
        ringkasan[cara] = {nama: ringkas(isi, bacaan[nama]) for nama, _ in pembaca}
        print(f"{cara} ({len(isi['uji'])} kedatangan uji)")
        for k in KELOMPOK:
            print(f"  {k:<13} " + " | ".join(f"{nama} {singkat(ringkasan[cara][nama][k])}" for nama, _ in pembaca))
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `151 passed` (149 + 2 baru) dan `EXIT=0`.

- [x] **Step 5: Commit**

```bash
git add tools/lab/banding_pembaca.py tools/lab/uji/test_banding_pembaca.py
git commit -q -F - <<'EOF'
Perbandingan pembaca dengan dua cara hitung

Alasan: 26 label set uji dipilih dari bacaan yang disepakati Qwen3-VL dan
fast-plate-ocr (Rencana 6), jadi pada plat itu kedua pembaca pasti dinilai
benar. Perbandingan yang adil dengan mesin buatan sendiri memakai set uji
tanpa plat itu; angka pada seluruh set uji tetap dilaporkan.

Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError:
banding_pembaca). Gerbang lab: 149 -> 151.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Latih, nilai sekali, bandingkan, periksa tanda mesin

- [x] **Step 1: Latih di kartu grafis (di latar)**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
Expected: tidak ada job vision-seed.

Run (PowerShell, di latar; log di folder kerja sementara):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/mesin_baca.py latih /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/mesin-baca-1; "EXIT=$LASTEXITCODE"`
Expected: 80 baris `zaman N: rugi ..., validasi benar ... dari ... gambar`, lalu `selesai: zaman terbaik ...`, `gambar tak
terbaca 0`, `EXIT=0`. **Berhenti dan laporkan** bila rugi menjadi `nan` atau validasi benar tetap 0 sampai akhir.

- [x] **Step 2: Nilai sekali pada set uji (kartu grafis, lalu CPU untuk kecepatan)**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/mesin_baca.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/mesin-baca-1 /kerja/data/keluaran/baca-mesin-1; "EXIT=$LASTEXITCODE"`
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/mesin_baca.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/mesin-baca-1 /kerja/data/keluaran/baca-mesin-1-cpu --perangkat cpu; "EXIT=$LASTEXITCODE"`
Expected: masing-masing empat baris kelompok dan `detik per gambar`, `EXIT=0`. Bacaan kedua jalan harus sama (beda hanya
perangkat); bila berbeda di lebih dari sedikit gambar, dicatat.

- [x] **Step 3: Bandingkan dengan dua pembaca**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/banding_pembaca.py /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/banding-pembaca --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl --hasil mesin-baca-1=/kerja/data/keluaran/baca-mesin-1/hasil.jsonl; "EXIT=$LASTEXITCODE"`
Expected: dua tabel (937 dan 911 kedatangan uji), `EXIT=0`. Catatan: hasil Qwen3-VL dan fast-plate-ocr dibaca pada set uji
Rencana 5 (945 plat); `ringkas` hanya menghitung berkas milik 937 plat yang ada sekarang.

- [x] **Step 4: Periksa tanda mesin**

Run: `node tools/periksa-jualan.mjs data/keluaran/mesin-baca-1/mesin.json; echo "EXIT=$?"`
Expected: tanda `BOLEH-PRODUK` (satu-satunya bahan `dataset-indo-alpr`), `EXIT=0`. Tanda itu soal asal bahan, bukan soal
mutu mesin.

---

### Task 4: Laporan, catatan, dan laporan ke owner

- [x] **Step 1: Salin ringkasan ke `bukti/` sesudah dibuktikan tanpa nomor plat (dengan kontrol positif)**

Skrip sekali pakai `data/alat-sementara/periksa-bukti-8.py`, pola `periksa-bukti-7.py`. Larangan sama dengan Rencana 7
ditambah teks plat di `latih-koreksi/pembagian-koreksi.json`; kontrol positif pada `baca-mesin-1/hasil.jsonl`. Yang diperiksa
dan disalin: `mesin-baca-1/mesin.json`, `baca-mesin-1/ringkasan.json`, `baca-mesin-1-cpu/ringkasan.json`,
`banding-pembaca/ringkasan.json`.

- [x] **Step 2: Tulis laporan `bukti/<tanggal>-mesin-baca-pertama.md`**

Isinya: model (bentuk, jumlah parameter dari `mesin.json` bila dicatat, atau dihitung di lab), bahan (plat dan gambar inti
dan validasi), jalannya latihan (rugi awal dan akhir, zaman terbaik, validasi benar), angka set uji per kelompok dengan
rentang 95%, perbandingan dengan dua pembaca pada kedua cara hitung, kecepatan di kartu grafis dan di CPU laptop, tanda
mesin. **Batas:** potongan plat, bukan kamera gerbang (K9 tidak terbukti); satu kali latihan dengan satu benih; set uji
masih memuat label salah sekitar 3% (taksiran); label latih yang salah tersisa belum diukur; kecepatan CPU laptop bukan
kotak murah (B5).

- [x] **Step 3: Perbarui catatan (skrip pencatat berkas; jangkar tepat sekali)**

`data-asal/bahan.json` (INDO-ALPR: dipakai melatih mesin-baca-1); `CLAUDE.md` §7 (mesin di `data/keluaran/mesin-baca-1/`,
bobot safetensors dengan SHA-256 di `mesin.json`, dimuat hanya lewat `PembacaMesin`); `OPEN-QUESTIONS.md` bagian B
(paragraf baru: angka mesin pertama dan artinya bagi B1, B5, B6); `ROADMAP.md` (butir dicentang dengan angka; butir baru
`- [ ] Rencana 9 Fase 0A ditulis ← di sini sekarang`; baris status; changelog); rencana ini (kotak dicentang, catatan
pelaksanaan).

- [x] **Step 4: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 101` dan `151 passed`, keduanya `EXIT=0`. `git status --short`: hanya `bukti/` dan berkas catatan.

- [x] **Step 5: Laporkan ke owner**

Ringkasan singkat dalam bahasa sehari-hari: angka mesin kita dibanding dua pembaca (cara hitung yang adil), kecepatannya,
artinya, batasnya; lalu **satu** pertanyaan untuk langkah berikutnya.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan spec 8.1 langkah 7** (mesin belajar pertama, diukur per kelompok) → Task 1 dan 3; "dua atau tiga calon per
  langkah" belum: satu calon dulu, calon lain di Rencana 9 bila angka menuntutnya (dicatat sebagai batas).
- **Set uji dipakai sekali:** latihan hanya menerima sisi latih (diuji lewat baris perintah: hanya gambar latih yang dimuat);
  pemilihan zaman memakai validasi dari bahan latih.
- **Rantai pasok dan izin:** tanpa bobot awal, tanpa unduhan; bobot safetensors dengan SHA-256; tanda mesin diperiksa
  pemeriksa yang sudah ada.
- **Data pribadi:** `sandi()` menolak tanpa mencetak teks; layar dan ringkasan tanpa nomor plat (diuji); `mesin.json` hanya
  hitungan.
- **Tanpa isian kosong pada kode:** semua kode alat dan uji tertulis lengkap. Isian bersudut hanya pada angka hasil.
- **Angka gerbang:** Node tetap 101. Lab 141 → 149 → 151.

## Catatan pelaksanaan (14 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Hasil dan batasnya di
[`../bukti/2026-10-14-mesin-baca-pertama.md`](../bukti/2026-10-14-mesin-baca-pertama.md). Yang berbeda dari tulisan di atas:

- **Angka gerbang** sama dengan rencana (lab 141 → 149 → 151). Lama jalan gerbang lab naik dari sekitar 9 menjadi 25 detik.
- **Task 3 Step 1:** syarat berhenti tidak terpenuhi (rugi tidak `nan`, validasi tidak nol), tetapi validasi hanya 31,7%:
  mesin menghafal. Baris "zaman 1" di log tertimpa pembungkus stderr PowerShell; ke-80 zaman tercatat di `mesin.json`.
- **Task 3 Step 2:** bacaan di CPU dan di kartu grafis sama persis.
- **Task 4 Step 1:** kontrol positif menemukan 2.381 larangan di bacaan mesin; jumlah parameter dihitung di lab (909.925).
