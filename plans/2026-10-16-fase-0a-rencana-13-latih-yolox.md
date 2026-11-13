# Fase 0A, Rencana 13: Melatih pencari plat YOLOX-Nano dan YOLOX-Tiny (K30) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Empat calon pencari plat buatan sendiri dilatih dengan sisi latih plat-lighting (393 foto) dari bobot awal COCO:
YOLOX-Nano dan YOLOX-Tiny, masing-masing pada 416 dan 640 piksel. Zaman terbaik dan ambang dipilih di validasi. Keempatnya
diekspor ke ONNX, dinilai sekali pada set uji yang sama dengan pembanding Rencana 12, dan diukur kecepatannya di CPU laptop dan
Mini PC. Hasilnya dipakai owner untuk memilih pencari plat yang dipakai di rantai utuh (Rencana 14).

**Architecture:**
- **`tools/lab/pencari_yolox.py`**: bagian yang kelak jalan di server, hanya numpy, cv2, dan onnxruntime. Isinya letterbox
  seperti YOLOX, NMS, penguraian keluaran ke piksel foto asli, dan `PencariYolox` (ONNX, CPU, SHA-256 diperiksa).
- **`tools/lab/latih_yolox.py`**: bagian lab.
  - Model dibangun dari klon `vendor/yolox` @ 4197784 (Apache-2.0).
  - Bobot awal dimuat hanya dengan `torch.load(weights_only=True)`.
  - Putaran latih buatan sendiri memakai rugi bawaan kepala YOLOX, EMA, dan variasi sederhana.
  - Zaman terbaik dipilih dengan F1 validasi (`tools/lab/deteksi.py`).
  - Bobot disimpan sebagai safetensors.
  - Ekspor ONNX disimpan hanya bila deteksinya sama dengan torch.
- **Tanpa paket baru:** `loguru` dan `thop` yang dimuat `yolox.utils` diganti tiruan, karena keduanya hanya untuk log dan
  menghitung FLOPs.

**Tech Stack:** Python di image lab (torch 2.14.1, numpy 2.5.3, safetensors, onnxruntime 1.30.0) dan image tambahan (onnx, untuk
ekspor), PowerShell, Node, SSH ke Mini PC.

**Dasar:** K15, K29, K30 (`SEED.md` §3); laporan Rencana 12 (`bukti/2026-10-16-pencari-plat-ukur.md`); spec 2.1 langkah 1,
2.3 (format tanpa kode, bukan pickle), 2.6, 8.1 langkah 7; `CLAUDE.md` §4, §6, §7.

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Melatih YOLOX di image lab | **Jalan** dengan putaran latih sendiri (numpy 2.5, torch 2.14), 1 kelas, gambar dan kotak acak. Tiga langkah latih per varian tanpa galat; keluaran latih `total_loss`, `iou_loss`, `l1_loss`, `conf_loss`, `cls_loss`, `num_fg`; inferensi `(1, 3549, 6)` di 416 px dan `(1, 8400, 6)` di 640 px (cx, cy, w, h, objek, kelas). Memori puncak 844–2.284 MiB pada angkatan 8. Hanya peringatan "akan usang" `torch.cuda.amp.autocast` | `data/alat-sementara/ukur-latih-yolox.py` |
| Paket | Membangun model dan melatih hanya butuh tiruan `loguru` dan `thop`. `tabulate` dan `pycocotools` hanya dipakai pemuat data dan penilai COCO bawaan YOLOX, yang tidak dipakai di sini | sama; `vendor/yolox/yolox/utils`, `yolox/data` |
| Bobot awal COCO | Rilis `0.1.1rc0`: `yolox_nano.pth` 7.694.953 byte, `yolox_tiny.pth` 40.755.013 byte, diunggah 2021-08-18, **tanpa digest** dari GitHub; format pickle; izin bobot tidak dinyatakan (`BELUM-JELAS`, `docs/lisensi/Megvii-BaseDetection__YOLOX/BOBOT.md`) | API rilis GitHub |
| Praproses YOLOX | Letterbox ke kiri atas dengan bantalan 114, skala `min(S/t, S/l)`, BGR 0–255 tanpa normalisasi | `yolox/data/data_augment.py` baris 142–156 |
| Bagian YOLOX yang dipakai ulang | `ModelEMA(model, decay)`; `YOLOXHead.initialize_biases(prior_prob)`; BatchNorm eps 1e-3 dan momentum 0,03 (`init_yolo`) | `yolox/utils/ema.py`, `yolox/models/yolo_head.py`, `yolox/exp/yolox_base.py` |
| Kecepatan di Mini PC (Rencana 12, 416 px, 2 utas) | YOLOX-Nano 73 ms, YOLOX-Tiny 251 ms. 640 px belum diukur | `bukti/2026-10-16-cepat-calon-minipc.json` |

Akibatnya bagi rencana ini:

1. **Tanpa paket baru dan tanpa image baru.** Tiruan `loguru`/`thop` dipasang hanya bila pustaka aslinya tidak ada, dan
   dijelaskan di kode.
2. **Bobot awal pickle hanya lewat `weights_only=True`.** Bila cara itu gagal untuk bobot terbitan, **berhenti** dan laporkan;
   jangan memuat dengan pickle penuh.
3. **SHA-256 bobot awal dipercaya pada unduhan pertama** (tanpa digest), seperti pembanding Rencana 12.
4. **Tanda mesin `RISET-SAJA`:** bahannya plat-lighting (`BOLEH-PRODUK`) dan bobot awal YOLOX (`BELUM-JELAS`).
5. **Model hasil latih tidak dibawa ke Mini PC** (K15: bahan bertanda riset dipakai di laptop ini). Kecepatan 640 px di Mini
   PC diukur dengan ONNX berbobot acak berukuran sama, seperti Rencana 12.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–12 | Bengkel sampai pembanding pencari plat dan kecepatan calon di Mini PC | Selesai 13–16 Okt |
| **13 (dokumen ini)** | Melatih empat calon YOLOX, ekspor ONNX, nilai, kecepatan | Ditulis |
| 14 | Rantai utuh di video riset (cari → potong → baca → gabung per kedatangan) dan kecepatannya | Sesudahnya |
| 15 | Laporan Fase 0A dan keputusan owner; plat buatan komputer diputuskan di sini | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8–12. Tambahan:
- **Latihan empat varian berurutan** dalam satu job GPU di latar, keluaran ke berkas log. Jangan menunggu dengan `sleep`.
  Lama latihan dicatat; taksiran tidak dipercaya (Rencana 10 meleset 3,5 kali).
- **Set uji plat-lighting dibaca sekali per calon**, sesudah zaman dan ambang dipilih di validasi. Pilihan calon diusulkan
  dari validasi dan kecepatan, **tidak dari angka uji**.
- **Mini PC:** prosedur sama dengan Rencana 12 Task 4 (`CLAUDE.md` §7), hanya ONNX berbobot acak dan masukan buatan.
- Nama berkas bukti memakai tanggal jalan (`2026-10-16` di bawah). Bila dijalankan pada tanggal lain, tanggal itu diganti.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/vendor.lock.json` (ubah) | Butir `yolox-nano-coco`, `yolox-tiny-coco` | 1 |
| `tools/lab/pencari_yolox.py` (baru) | Letterbox, NMS, penguraian keluaran, `PencariYolox` (ONNX), `cepat`, CLI `nilai`/`cepat` | 2 |
| `tools/lab/uji/test_pencari_yolox.py` (baru) | Uji gerbang biasa | 2 |
| `tools/lab/latih_yolox.py` (baru) | Model, bobot awal aman, variasi, latih, safetensors, ekspor ONNX | 3, 4 |
| `tools/lab/uji/test_latih_yolox.py` (baru) | Uji gerbang biasa (CPU), termasuk rantai latih kecil | 3 |
| `tools/lab/uji_fpo/test_yolox_sungguhan.py` (baru) | Bobot COCO sungguhan dan ekspor ONNX (di luar gerbang) | 4 |
| `bukti/2026-10-16-*` (baru) | Ringkasan dan laporan | 5, 6 |

---

### Task 1: Bobot awal COCO YOLOX terkunci dan bisa dimuat dengan aman

**Files:** Modify `tools/vendor.lock.json`; Create `data/alat-sementara/kunci-yolox.mjs` (sekali pakai)

- [x] **Step 1: Catat dua butir di kunci (tanpa SHA dulu)**

`data/alat-sementara/kunci-yolox.mjs`:

```js
// Sekali pakai (Rencana 13 Task 1): menambah butir bobot awal COCO YOLOX nano dan tiny ke kunci. Ukuran dibaca dari API rilis
// GitHub (tag 0.1.1rc0); sha256 kosong dulu (aset 2021 tanpa digest), lalu diisi dari berkas unduhan dengan "isi". Teks
// disisipkan pada jangkar yang harus ketemu TEPAT SEKALI.
// Pakai: node data/alat-sementara/kunci-yolox.mjs tambah | node data/alat-sementara/kunci-yolox.mjs isi
import fs from 'node:fs';
import crypto from 'node:crypto';

const KUNCI = 'tools/vendor.lock.json';
const BUTIR = [['yolox-nano-coco', 'yolox_nano.pth', 0.02], ['yolox-tiny-coco', 'yolox_tiny.pth', 0.06]];
let teks = fs.readFileSync(KUNCI, 'utf8').replace(/\r\n/g, '\n');
const kunci = JSON.parse(teks);
if (process.argv[2] === 'tambah') {
  const r = await fetch('https://api.github.com/repos/Megvii-BaseDetection/YOLOX/releases/tags/0.1.1rc0',
    { headers: { 'User-Agent': 'cctvgerbang-baca', Accept: 'application/vnd.github+json' } });
  const aset = (await r.json()).assets;
  const isi = [];
  for (const [nama, berkas, maks] of BUTIR) {
    if (kunci.berkas.some((b) => b.nama === nama)) { console.error(`${nama} sudah ada`); process.exit(1); }
    const a = aset.find((x) => x.name === berkas);
    if (!a) { console.error(`${berkas} tidak ada di rilis`); process.exit(1); }
    isi.push({ nama, url: a.browser_download_url, berkas, maks_gb: maks, sha256: '',
      sumber: 'https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0', ukuran_byte: a.size,
      isi_dibaca: `API rilis GitHub 0.1.1rc0: ${a.size} byte, diunggah ${a.updated_at}, TANPA digest dari GitHub; sha256 diisi dari unduhan pertama (dipercaya pada pemakaian pertama). Format pickle: hanya dimuat dengan torch.load(weights_only=True)`,
      peran: 'bobot awal COCO untuk melatih pencari plat sendiri (K30, Rencana 13). Izin bobot tidak dinyatakan (BELUM-JELAS): mesin hasilnya RISET-SAJA',
      dibaca: new Date().toLocaleDateString('sv-SE') });
  }
  const jangkar = '\n    }\n  ],\n  "_model_hf"';
  if (teks.split(jangkar).length - 1 !== 1) { console.error('jangkar penutup daftar berkas tidak ketemu tepat sekali'); process.exit(1); }
  const blok = isi.map((b) => JSON.stringify(b, null, 2).split('\n').map((x) => `    ${x}`).join('\n')).join(',\n');
  teks = teks.replace(jangkar, () => `\n    },\n${blok}\n  ],\n  "_model_hf"`);
} else if (process.argv[2] === 'isi') {
  for (const [nama, berkas] of BUTIR) {
    const b = kunci.berkas.find((x) => x.nama === nama);
    const data = fs.readFileSync(`data/unduhan/${nama}/${berkas}`);
    if (!b || b.sha256) { console.error(`${nama}: tidak ada atau sha256 sudah terisi`); process.exit(1); }
    if (data.length !== b.ukuran_byte) { console.error(`${nama}: ukuran ${data.length} bukan ${b.ukuran_byte}`); process.exit(1); }
    const awal = teks.indexOf(`"nama": "${nama}"`);
    const kosong = teks.indexOf('"sha256": ""', awal);
    const berikut = teks.indexOf('"nama": ', awal + 1);
    if (awal < 0 || kosong < 0 || (berikut > 0 && kosong > berikut)) { console.error(`${nama}: sha256 tidak ketemu`); process.exit(1); }
    teks = `${teks.slice(0, kosong)}"sha256": "${crypto.createHash('sha256').update(data).digest('hex')}"${teks.slice(kosong + '"sha256": ""'.length)}`;
  }
} else { console.error('Pakai: tambah | isi'); process.exit(2); }
JSON.parse(teks);
fs.writeFileSync(KUNCI, teks);
console.log(`${process.argv[2]}: ${BUTIR.map((b) => b[0]).join(', ')}`);
```

Run: `node data/alat-sementara/kunci-yolox.mjs tambah; echo "EXIT=$?"` lalu `git diff --stat tools/vendor.lock.json`
Expected: `tambah: yolox-nano-coco, yolox-tiny-coco`, `EXIT=0`; diff hanya menambah kedua butir.

- [x] **Step 2: Unduh lewat pintu, kunci SHA-256, gerbang Node**

Run (PowerShell, satu per satu): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\ambil-berkas.ps1 yolox-nano-coco; "EXIT=$LASTEXITCODE"` lalu sama untuk `yolox-tiny-coco`.
Expected: `TERSIMPAN ...` dengan ukuran sama dengan kunci dan peringatan belum dikunci, `EXIT=0`.

Run: `node data/alat-sementara/kunci-yolox.mjs isi; echo "EXIT=$?"` lalu `npm test; echo "EXIT=$?"`
Expected: `isi: yolox-nano-coco, yolox-tiny-coco`; `pass 107`. SHA-256 yang tercatat sama dengan yang dicetak pintu.

- [x] **Step 3: Pastikan keduanya bisa dimuat dengan `weights_only=True`**

Berkas sekali pakai `data/alat-sementara/cek-bobot-yolox.py`:

```python
"""Sekali pakai (Rencana 13 Task 1): bobot awal COCO YOLOX bisa dimuat dengan torch.load(weights_only=True)? Mencetak kunci
tingkat atas dan jumlah tensor; tidak pernah memuat dengan pickle penuh.
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/data/alat-sementara/cek-bobot-yolox.py
"""
import torch

for nama, berkas in (("yolox-nano-coco", "yolox_nano.pth"), ("yolox-tiny-coco", "yolox_tiny.pth")):
    try:
        ckpt = torch.load(f"/kerja/data/unduhan/{nama}/{berkas}", map_location="cpu", weights_only=True)
        sd = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
        print(f"{nama}: dimuat aman; kunci tingkat atas {sorted(ckpt)[:6] if isinstance(ckpt, dict) else type(ckpt).__name__}; "
              f"tensor {len(sd)}")
    except Exception as e:  # noqa: BLE001
        print(f"{nama}: TIDAK BISA dimuat aman: {type(e).__name__}: {str(e)[:200]}")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/cek-bobot-yolox.py; "EXIT=$LASTEXITCODE"`
Expected: dua baris `dimuat aman`. Bila salah satu `TIDAK BISA`, **berhenti** dan laporkan ke owner. Pilihannya: latih dari
nol, bobot awal lain, atau keputusan lain. Jangan memuat dengan pickle penuh.

- [x] **Step 4: Commit** kunci, dengan alasan (bobot awal K30), ukuran, SHA-256 dari unduhan pertama (batas: tanpa digest), dan
hasil pemuatan aman.

---

### Task 2: Pencari ONNX YOLOX (bagian yang kelak jalan di server)

**Files:** Create `tools/lab/pencari_yolox.py`, `tools/lab/uji/test_pencari_yolox.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji tools/lab/pencari_yolox.py tanpa model sungguhan: letterbox seperti YOLOX, NMS, penguraian keluaran ke piksel foto asli,
dan pencari ONNX yang menolak berkas yang berubah sebelum onnxruntime dimuat."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pencari_yolox as pyx  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402


def test_letterbox_kiri_atas_dengan_bantalan_114():
    gambar = np.full((100, 200, 3), 7, np.uint8)

    hasil, skala = pyx.letterbox(gambar, 64)

    assert hasil.shape == (64, 64, 3) and skala == 0.32
    assert (hasil[:32, :64] == 7).all() and (hasil[32:, :] == 114).all()


def test_nms_menyimpan_yang_terkuat_dan_yang_tidak_bertumpuk():
    kotak = np.array([[0, 0, 10, 10], [1, 1, 10, 10], [50, 50, 60, 60]], np.float32)
    skor = np.array([0.6, 0.9, 0.5], np.float32)

    assert pyx.nms(kotak, skor) == [1, 2]
    assert pyx.nms(np.zeros((0, 4), np.float32), np.zeros(0, np.float32)) == []


def test_urai_keluaran_ke_piksel_asli_dan_ambang():
    keluaran = np.array([[32, 16, 20, 10, 0.9, 0.9],    # skor 0,81
                         [33, 16, 20, 10, 0.8, 0.8],    # bertumpuk dan lebih lemah: dibuang NMS
                         [5, 5, 2, 2, 0.05, 0.1]],      # skor 0,005, di bawah ambang model
                        np.float32)

    hasil = pyx.urai_keluaran(keluaran, 0.5)

    assert len(hasil) == 1
    x1, y1, x2, y2, yakin = hasil[0]
    assert (x1, y1, x2, y2) == (44.0, 22.0, 84.0, 42.0) and abs(yakin - 0.81) < 1e-6


def test_pencari_onnx_menolak_berkas_yang_berubah_sebelum_memuat_apa_pun(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"ditukar")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64, "ukuran": 64}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        pyx.PencariYolox(tmp_path)
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'pencari_yolox'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/pencari_yolox.py`**

```python
"""Pencari plat YOLOX dalam ONNX (Rencana 13, K30): bagian yang kelak jalan di server. Hanya numpy, cv2, dan onnxruntime;
tidak memuat torch.

- letterbox: sama dengan praproses YOLOX (vendor/yolox/yolox/data/data_augment.py preproc): gambar BGR diperkecil dengan skala
  min(S/t, S/l), diletakkan di kiri atas kanvas S x S berbantalan 114, tanpa normalisasi.
- urai_keluaran: keluaran YOLOX (N, 6) = cx, cy, w, h, objek, kelas (piksel masukan) -> kotak piksel foto asli dengan yakin =
  objek x kelas, ambang AMBANG_MODEL (ambang sesungguhnya dipilih tools/lab/deteksi.py di validasi), lalu NMS.
- PencariYolox: mesin.onnx yang SHA-256-nya tidak sama dengan mesin-onnx.json ditolak sebelum onnxruntime dimuat.

  nilai: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_yolox.py nilai <folder-mesin> /kerja/data/keluaran/dataset/plat-lighting <keluar.json>
  cepat: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/pencari_yolox.py cepat <folder-mesin> /kerja/data/keluaran/dataset/plat-lighting <keluar.json>
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
import deteksi  # noqa: E402
from model_terkunci import ModelDitolak, sha256_berkas  # noqa: E402

BANTAL = 114
NMS_IOU = 0.45
AMBANG_MODEL = 0.01
UTAS = (1, 2, 4)


def letterbox(gambar, ukuran):
    """Gambar BGR -> (masukan uint8 ukuran x ukuran x 3 berbantalan BANTAL di kanan/bawah, skala)."""
    tinggi, lebar = gambar.shape[:2]
    skala = min(ukuran / tinggi, ukuran / lebar)
    kecil = cv2.resize(gambar, (int(lebar * skala), int(tinggi * skala)), interpolation=cv2.INTER_LINEAR)
    kanvas = np.full((ukuran, ukuran, 3), BANTAL, np.uint8)
    kanvas[:kecil.shape[0], :kecil.shape[1]] = kecil
    return kanvas, skala


def nms(kotak, skor, iou_maks=NMS_IOU):
    """Kotak (N, 4) x1y1x2y2 dan skor (N,) -> indeks yang disimpan, urut skor turun."""
    urut = np.argsort(-skor)
    simpan = []
    while urut.size:
        i = int(urut[0])
        simpan.append(i)
        sisa = urut[1:]
        if not sisa.size:
            break
        lebar = (np.minimum(kotak[i, 2], kotak[sisa, 2]) - np.maximum(kotak[i, 0], kotak[sisa, 0])).clip(0)
        tinggi = (np.minimum(kotak[i, 3], kotak[sisa, 3]) - np.maximum(kotak[i, 1], kotak[sisa, 1])).clip(0)
        irisan = lebar * tinggi
        luas_i = (kotak[i, 2] - kotak[i, 0]) * (kotak[i, 3] - kotak[i, 1])
        luas_s = (kotak[sisa, 2] - kotak[sisa, 0]) * (kotak[sisa, 3] - kotak[sisa, 1])
        urut = sisa[irisan / (luas_i + luas_s - irisan + 1e-9) <= iou_maks]
    return simpan


def urai_keluaran(keluaran, skala, ambang=AMBANG_MODEL):
    """Keluaran YOLOX (N, 6) -> daftar (x1, y1, x2, y2, yakin) dalam piksel foto asli."""
    skor = keluaran[:, 4] * keluaran[:, 5]
    pilih = skor >= ambang
    k, s = keluaran[pilih, :4], skor[pilih]
    kotak = np.stack([k[:, 0] - k[:, 2] / 2, k[:, 1] - k[:, 3] / 2, k[:, 0] + k[:, 2] / 2, k[:, 1] + k[:, 3] / 2], 1) / skala
    return [(*(float(x) for x in kotak[i]), float(s[i])) for i in nms(kotak, s)]


def masukan(gambar, ukuran):
    """Gambar BGR -> (larik float32 (1, 3, ukuran, ukuran) 0..255, skala)."""
    lb, skala = letterbox(gambar, ukuran)
    return lb.transpose(2, 0, 1)[None].astype(np.float32), skala


class PencariYolox:
    """Pencari plat dengan mesin.onnx di CPU. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali daftar
    (x1, y1, x2, y2, yakin)."""

    def __init__(self, folder_mesin, utas=None):
        folder = Path(folder_mesin)
        meta = json.loads((folder / "mesin-onnx.json").read_text())
        if sha256_berkas(folder / "mesin.onnx") != meta["sha256_onnx"]:
            raise ModelDitolak(f"{folder.name}/mesin.onnx: SHA-256 tidak sama dengan yang dicatat di mesin-onnx.json")
        import onnxruntime as ort

        opsi = ort.SessionOptions()
        if utas:
            opsi.intra_op_num_threads = utas
            opsi.inter_op_num_threads = 1
        self.ukuran = int(meta["ukuran"])
        self._sesi = ort.InferenceSession(str(folder / "mesin.onnx"), opsi, providers=["CPUExecutionProvider"])

    def __call__(self, gambar_bgr):
        x, skala = masukan(gambar_bgr, self.ukuran)
        return urai_keluaran(self._sesi.run(None, {"images": x})[0][0], skala)


def cepat(folder_dataset, buat_pencari, utas=UTAS, jumlah=60, panaskan=5):
    """Milidetik per foto utuh (letterbox + model + NMS) di CPU, pada foto validasi. buat_pencari(utas) -> pencari."""
    berkas = sorted(p for p in (Path(folder_dataset) / "valid" / "images").iterdir() if p.suffix.lower() in deteksi.AKHIRAN)
    gambar = [g for g in (cv2.imread(str(b)) for b in berkas[:jumlah]) if g is not None]
    hasil = {"gambar": len(gambar), "panaskan": panaskan, "per_utas": {}}
    for u in utas:
        cari = buat_pencari(u)
        lama = []
        for i, g in enumerate(gambar):
            mulai = time.perf_counter()
            cari(g)
            if i >= panaskan:
                lama.append(1000 * (time.perf_counter() - mulai))
        hasil["per_utas"][str(u)] = {"median_ms": round(float(np.median(lama)), 1),
                                     "p95_ms": round(float(np.percentile(lama, 95)), 1)}
    return hasil


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Pencari plat YOLOX ONNX: nilai dan cepat (Rencana 13).")
    perintah = urai.add_subparsers(dest="perintah", required=True)
    for nama in ("nilai", "cepat"):
        p = perintah.add_parser(nama)
        for a in ("folder_mesin", "folder_dataset", "keluar"):
            p.add_argument(a)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "nilai":
            hasil = deteksi.nilai(p.folder_dataset, PencariYolox(p.folder_mesin))
            for k, r in hasil["uji"].items():
                print(f"uji {k:<7} plat ditemukan {r['plat_ditemukan']} dari {r['plat']} (rentang 95% "
                      f"{r['rentang_95_ditemukan']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''}); kotak palsu "
                      f"{r['kotak_palsu']}; gambar {r['gambar']}")
            v = hasil["validasi"]["semua"]
            print(f"ambang dari validasi {hasil['ambang']} (validasi: {v['plat_ditemukan']} dari {v['plat']}, kotak palsu "
                  f"{v['kotak_palsu']}); detik per gambar {hasil['detik_per_gambar']}; tak terbaca {hasil['tak_terbaca']}")
        else:
            hasil = cepat(p.folder_dataset, lambda u: PencariYolox(p.folder_mesin, utas=u))
            for u, x in hasil["per_utas"].items():
                print(f"utas {u}: median {x['median_ms']} ms (p95 {x['p95_ms']}) per foto utuh; gambar {hasil['gambar']}")
        Path(p.keluar).parent.mkdir(parents=True, exist_ok=True)
        Path(p.keluar).write_text(json.dumps(hasil, indent=1))
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `182 passed` (178 + 4), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/pencari_yolox.py` dan ujinya, dengan alasan (bagian server tanpa torch, sama dengan
praproses YOLOX) dan angka gerbang 178 → 182.

---

### Task 3: Melatih YOLOX dengan bobot awal aman dan bobot tanpa pickle

**Files:** Create `tools/lab/latih_yolox.py`, `tools/lab/uji/test_latih_yolox.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji tools/lab/latih_yolox.py di gerbang biasa (CPU): target YOLOX, variasi acak, bobot awal hanya lewat weights_only (kode
pickle ditolak), dan rantai latih kecil dengan plat buatan sampai bobot safetensors dan mesin.json, dengan layar tanpa nama
berkas."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import latih_yolox as ly  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "latih_yolox.py"


def test_ke_target_piksel_masukan_dan_membuang_kotak_kecil():
    t = ly.ke_target([(10, 20, 50, 40), (0, 0, 2, 2)], 0.5)

    assert t.shape == (ly.MAKS_LABEL, 5)
    assert t[0].tolist() == [0.0, 15.0, 15.0, 20.0, 10.0] and not t[1].any()


def test_balik_horizontal():
    gambar = np.zeros((10, 20, 3), np.uint8)
    gambar[:, :5] = 255

    hasil, kotak = ly.balik(gambar, [(1, 2, 5, 6)])

    assert (hasil[:, 15:] == 255).all() and kotak == [(15.0, 2.0, 19.0, 6.0)]


def test_ubah_acak_tetap_dengan_benih_dan_kotak_di_dalam_gambar():
    gambar = np.full((100, 200, 3), 128, np.uint8)
    kotak = [(80, 40, 120, 60)]
    a = ly.ubah_acak(gambar, kotak, np.random.default_rng(1))
    b = ly.ubah_acak(gambar, kotak, np.random.default_rng(1))

    assert np.array_equal(a[0], b[0]) and a[1] == b[1]
    for benih in range(20):
        hasil, k = ly.ubah_acak(gambar, kotak, np.random.default_rng(benih))
        assert hasil.shape == gambar.shape and len(k) <= 1
        assert all(0 <= x1 <= x2 <= 200 and 0 <= y1 <= y2 <= 100 for x1, y1, x2, y2 in k)


def test_bobot_awal_lewat_weights_only_dan_kepala_lain_dilewati(tmp_path):
    sd = ly.buat_model("nano").state_dict()
    sd["head.cls_preds.0.weight"] = torch.zeros(80, *sd["head.cls_preds.0.weight"].shape[1:])  # kepala COCO 80 kelas
    torch.save({"model": sd}, tmp_path / "coco.pth")

    dimuat, dilewati = ly.muat_bobot_awal(ly.buat_model("nano"), tmp_path / "coco.pth")

    assert dilewati == 1 and dimuat == len(sd) - 1


class Jahat:
    def __reduce__(self):
        return (print, ("kode pickle dijalankan",))


def test_bobot_awal_berisi_kode_pickle_ditolak(tmp_path):
    torch.save({"model": {"x": Jahat()}}, tmp_path / "jahat.pth")

    with pytest.raises(ModelDitolak, match="pickle"):
        ly.muat_bobot_awal(ly.buat_model("nano"), tmp_path / "jahat.pth")


def buat_dataset(tmp_path):
    for sisi, n in (("train", 4), ("valid", 2), ("test", 2)):
        for sub in ("images", "labels"):
            (tmp_path / "ds" / sisi / sub).mkdir(parents=True)
        for i in range(n):
            g = np.full((96, 160, 3), 90, np.uint8)
            cv2.rectangle(g, (60, 40), (100, 56), (255, 255, 255), -1)
            cv2.imwrite(str(tmp_path / "ds" / sisi / "images" / f"B{1200 + i}AB_{sisi}.jpg"), g)
            (tmp_path / "ds" / sisi / "labels" / f"B{1200 + i}AB_{sisi}.txt").write_text("0 0.5 0.5 0.25 0.1666667\n")
    return tmp_path / "ds"


def kunci_sementara(tmp_path):
    folder = tmp_path / "unduhan" / ly.BUTIR_BOBOT["nano"]
    folder.mkdir(parents=True)
    torch.save({"model": ly.buat_model("nano").state_dict()}, folder / "yolox_nano.pth")
    kunci = tmp_path / "kunci.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": ly.BUTIR_BOBOT["nano"], "berkas": "yolox_nano.pth",
                                             "sha256": hashlib.sha256((folder / "yolox_nano.pth").read_bytes()).hexdigest()}]}))
    return tmp_path / "unduhan", kunci


def test_rantai_latih_kecil_sampai_safetensors_dan_layar_tanpa_nama_berkas(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(unduhan), str(tmp_path / "mesin"),
                            "--zaman", "1", "--perangkat", "cpu", "--kunci", str(kunci)], capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    assert "B120" not in layar
    meta = json.loads((tmp_path / "mesin" / "mesin.json").read_text())
    assert meta["sha256_bobot"] == hashlib.sha256((tmp_path / "mesin" / "mesin.safetensors").read_bytes()).hexdigest()
    assert meta["bahan"] == ["dataset-plat-lighting", "bobot-yolox"] and meta["bobot_awal"]["dilewati"] == 0
    assert ly.muat_mesin(tmp_path / "mesin").training is False
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'latih_yolox'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/latih_yolox.py`**

```python
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
BATAS_EKSPOR = 0.5  # piksel; deteksi torch dan ONNX harus sama dalam batas ini
BATAS_MENTAH = 1e-2  # selisih keluaran mentah terbesar (piksel dan peluang); tidak bisa lolos kosong walau belum ada deteksi


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


def latih(jenis, ukuran, folder_dataset, folder_unduhan, keluar, zaman=ZAMAN, benih=BENIH, perangkat=None, kunci=LOKASI_KUNCI):
    """Melatih dari sisi train; memilih zaman dengan F1 di sisi valid; sisi test tidak dibaca. Kembali: isi mesin.json."""
    matikan_kernel_triton()
    perangkat = perangkat or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(benih)
    rng = np.random.default_rng(benih)
    daftar = daftar_berkas(kunci)
    butir = BUTIR_BOBOT[jenis]
    berkas_awal = verifikasi_berkas(Path(folder_unduhan) / butir / daftar.get(butir, ("?", ""))[0], butir, daftar)
    model = buat_model(jenis)
    dimuat, dilewati = muat_bobot_awal(model, berkas_awal)
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
    meta = {"nama": f"pencari-yolox-{jenis}-{ukuran}", "tujuan": "belajar", "bahan": BAHAN, "jenis": jenis, "ukuran": int(ukuran),
            "sha256_bobot": sha256_berkas(keluar / "mesin.safetensors"), "zaman": zaman, "zaman_terbaik": terbaik[1],
            "f1_validasi_terbaik": round(terbaik[0], 4), "ambang_validasi": terbaik[2], "benih": benih, "perangkat": perangkat,
            "bobot_awal": {"butir": butir, "sha256": sha256_berkas(berkas_awal), "dimuat": dimuat, "dilewati": dilewati},
            "gambar_latih": len(jalur), "catatan": catatan}
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
    e = perintah.add_parser("ekspor")
    for nama in ("folder_mesin", "folder_dataset"):
        e.add_argument(nama)
    p = urai.parse_args(argumen)
    try:
        if p.perintah == "latih":
            m = latih(p.jenis, p.ukuran, p.folder_dataset, p.folder_unduhan, p.keluar, p.zaman, p.benih, p.perangkat, p.kunci)
            print(f"selesai {m['nama']}: zaman terbaik {m['zaman_terbaik']} dari {m['zaman']}, F1 validasi "
                  f"{m['f1_validasi_terbaik']} (ambang {m['ambang_validasi']}); bobot awal dimuat {m['bobot_awal']['dimuat']}, "
                  f"dilewati {m['bobot_awal']['dilewati']}; gambar latih {m['gambar_latih']}")
        else:
            m = ekspor(p.folder_mesin, p.folder_dataset)
            v = m["pemeriksaan"]
            print(f"diekspor mesin.onnx: deteksi sama {v['sama']} dari {v['gambar']} gambar; selisih keluaran terbesar "
                  f"{v['selisih_terbesar']:.2e}")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

`ekspor` ditambahkan di Task 4; sampai saat itu baris perintah `ekspor` belum dipakai.

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `188 passed` (182 + 6), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/latih_yolox.py` dan ujinya, dengan alasan (tanpa paket baru, bobot awal hanya
`weights_only`, safetensors, zaman dari validasi) dan angka gerbang 182 → 188.

---

### Task 4: Ekspor ONNX yang terbukti sama dengan torch

**Files:** Modify `tools/lab/latih_yolox.py`; Create `tools/lab/uji_fpo/test_yolox_sungguhan.py`

- [x] **Step 1: Tulis ujinya**

```python
"""Uji tools/lab/latih_yolox.py dan pencari_yolox.py di image lab tambahan (di luar gerbang biasa; butuh onnx): bobot COCO
sungguhan dimuat aman, dan ekspor ONNX memberi deteksi yang sama dengan torch, juga lewat PencariYolox.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import sys
from pathlib import Path

import cv2
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji"):
    sys.path.insert(0, str(AKAR / folder))
import latih_yolox as ly  # noqa: E402
import pencari_yolox as pyx  # noqa: E402
from test_latih_yolox import buat_dataset, kunci_sementara  # noqa: E402


@pytest.mark.parametrize("jenis", ["nano", "tiny"])
def test_bobot_coco_sungguhan_dimuat_aman_dan_hanya_kepala_kelas_dilewati(jenis):
    butir = ly.BUTIR_BOBOT[jenis]
    berkas = UNDUHAN / butir / f"yolox_{jenis}.pth"
    if not berkas.exists():
        pytest.skip("bobot awal belum diunduh (Rencana 13 Task 1)")
    model = ly.buat_model(jenis)

    dimuat, dilewati = ly.muat_bobot_awal(model, berkas)

    # Kepala kelas COCO (80 kelas) di tiga tingkat: bobot dan bias = 6 tensor.
    assert dilewati == 6 and dimuat == len(model.state_dict()) - 6


def test_ekspor_onnx_sama_dengan_torch_dan_pencari_onnx_membaca_sama(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)
    ly.latih("nano", 128, ds, unduhan, tmp_path / "mesin", zaman=1, perangkat="cpu", kunci=kunci)

    meta = ly.ekspor(tmp_path / "mesin", ds)

    assert meta["pemeriksaan"]["sama"] == meta["pemeriksaan"]["gambar"] > 0
    # Model satu zaman mungkin belum punya deteksi di atas ambang; keluaran mentah tetap harus sama (tidak bisa lolos kosong).
    assert meta["pemeriksaan"]["selisih_terbesar"] < ly.BATAS_MENTAH
    gambar = cv2.imread(str(sorted((ds / "valid" / "images").iterdir())[0]))
    lewat_onnx = pyx.PencariYolox(tmp_path / "mesin")(gambar)
    lewat_torch = ly.cari_torch(ly.muat_mesin(tmp_path / "mesin"), 128, "cpu")(gambar)
    assert len(lewat_onnx) == len(lewat_torch)
    assert all(max(abs(a - b) for a, b in zip(u[:4], v[:4])) < ly.BATAS_EKSPOR for u, v in zip(lewat_onnx, lewat_torch))
```

- [x] **Step 2: Jalankan, pastikan merah**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `1 failed, 16 passed`. Uji ekspor gagal dengan `AttributeError: ... 'ekspor'`; uji bobot COCO lulus (bobot sudah
diunduh di Task 1). `EXIT=1`.

- [x] **Step 3: Tambahkan `ekspor` di `tools/lab/latih_yolox.py`**

Sisipkan sesudah fungsi `muat_mesin`:

```python
def ekspor(folder_mesin, folder_dataset, jumlah=20):
    """mesin.safetensors -> mesin.onnx + mesin-onnx.json, hanya bila deteksi ONNX sama dengan torch (kotak dalam BATAS_EKSPOR
    piksel, yakin dalam 1e-3) pada semua gambar valid yang diperiksa DAN selisih keluaran mentah terbesar di bawah BATAS_MENTAH.
    Butuh pustaka onnx (image lab tambahan)."""
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
    selisih = 0.0
    for b in berkas[:jumlah]:
        g = cv2.imread(str(b))
        if g is None:
            continue
        x, skala = pyx.masukan(g, ukuran)
        with torch.no_grad():
            t = model(torch.from_numpy(x))[0].numpy()
        o = sesi.run(None, {"images": x})[0][0]
        selisih = max(selisih, float(np.abs(t - o).max()))
        a, d = pyx.urai_keluaran(t, skala), pyx.urai_keluaran(o, skala)
        gambar += 1
        sama += int(len(a) == len(d) and all(max(abs(p - q) for p, q in zip(u[:4], v[:4])) < BATAS_EKSPOR
                                             and abs(u[4] - v[4]) < 1e-3 for u, v in zip(a, d)))
    if gambar == 0 or sama != gambar or selisih > BATAS_MENTAH:
        (folder / "mesin.onnx").unlink(missing_ok=True)
        raise ModelDitolak(f"ONNX tidak sama dengan torch: deteksi sama {sama} dari {gambar} gambar, selisih mentah {selisih:.2e}")
    hasil = {"nama": meta["nama"], "tujuan": meta["tujuan"], "bahan": meta["bahan"], "jenis": meta["jenis"], "ukuran": ukuran,
             "sha256_onnx": sha256_berkas(folder / "mesin.onnx"), "sha256_bobot": meta["sha256_bobot"],
             "pemeriksaan": {"gambar": gambar, "sama": sama, "selisih_terbesar": selisih}}
    (folder / "mesin-onnx.json").write_text(json.dumps(hasil, indent=1))
    return hasil
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run (PowerShell): sama dengan Step 2.
Expected: `17 passed`, `EXIT=0`.

Run: `npm run test:lab; echo "EXIT=$?"` (Expected `188 passed`) lalu `npm test; echo "EXIT=$?"` (Expected `pass 107`).

- [x] **Step 5: Commit** `tools/lab/latih_yolox.py` dan `tools/lab/uji_fpo/test_yolox_sungguhan.py`, dengan alasan (ONNX
untuk server, gagal tertutup) dan angka uji image tambahan 14 → 17.

---

### Task 5: Latih empat calon, ekspor, nilai, dan ukur kecepatannya

**Files:** Create `data/alat-sementara/latih-empat-yolox.ps1`, `data/alat-sementara/ekspor-yolox-640-acak.py`,
`data/alat-sementara/periksa-bukti-13.py` (sekali pakai); `bukti/2026-10-16-*.json`

- [x] **Step 1: Latih empat calon berurutan (satu job GPU, di latar)**

`data/alat-sementara/latih-empat-yolox.ps1`:

```powershell
# Sekali pakai (Rencana 13 Task 5): empat latihan berurutan dalam satu job; tiap varian ke folder sendiri. Berhenti pada
# kegagalan pertama. Pakai: powershell -NoProfile -File data\alat-sementara\latih-empat-yolox.ps1
$lab = 'D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1'
foreach ($v in @(@('nano', 416), @('nano', 640), @('tiny', 416), @('tiny', 640))) {
    $mulai = Get-Date
    & powershell -NoProfile -File $lab python /kerja/tools/lab/latih_yolox.py latih $v[0] $v[1] /kerja/data/keluaran/dataset/plat-lighting /kerja/data/unduhan "/kerja/data/keluaran/pencari-yolox-$($v[0])-$($v[1])"
    $kode = $LASTEXITCODE
    "VARIAN $($v[0])-$($v[1]) EXIT=$kode LAMA_MENIT=$([math]::Round(((Get-Date) - $mulai).TotalMinutes, 1))"
    if ($kode -ne 0) { exit $kode }
}
exit 0
```

Periksa dulu (PowerShell): `nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader` dan `docker ps`.

Run (PowerShell, `run_in_background`, keluaran ke `<folder sementara sesi>\latih-empat-yolox.txt`):
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\data\alat-sementara\latih-empat-yolox.ps1 *> <log>; "EXIT=$LASTEXITCODE"`
Expected: empat baris `selesai pencari-yolox-...` dan empat baris `VARIAN ... EXIT=0 LAMA_MENIT=...`; `EXIT=0`.

- [x] **Step 2: Periksa tanda mesin**

Run: `node tools/periksa-jualan.mjs data/keluaran/pencari-yolox-nano-416/mesin.json; echo "EXIT=$?"` (dan tiga lainnya)
Expected: `tanda mesin = RISET-SAJA`, `EXIT=0`.

- [x] **Step 3: Ekspor keempatnya ke ONNX**

Run (PowerShell), untuk tiap varian: `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/latih_yolox.py ekspor /kerja/data/keluaran/pencari-yolox-<varian> /kerja/data/keluaran/dataset/plat-lighting; "EXIT=$LASTEXITCODE"`
Expected: `diekspor mesin.onnx: deteksi sama 20 dari 20 gambar ...`, `EXIT=0`. Bila `DITOLAK`, **berhenti** dan laporkan.

- [x] **Step 4: Nilai keempatnya (ambang dari validasi, uji sekali) dan kecepatan foto utuh di laptop**

Run (PowerShell), untuk tiap varian:
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/tools/lab/pencari_yolox.py nilai /kerja/data/keluaran/pencari-yolox-<varian> /kerja/data/keluaran/dataset/plat-lighting /kerja/data/keluaran/pencari-yolox-<varian>/nilai.json; "EXIT=$LASTEXITCODE"`
lalu, saat mesin tenang, `... pencari_yolox.py cepat ... /kerja/data/keluaran/pencari-yolox-<varian>/cepat.json`.
Expected: lima baris kelompok uji, ambang dan angka validasi; tiga baris kecepatan; `EXIT=0` untuk tiap perintah.

- [x] **Step 5: Kecepatan 640 px di Mini PC (ONNX berbobot acak, prosedur Rencana 12)**

`data/alat-sementara/ekspor-yolox-640-acak.py`:

```python
"""Sekali pakai (Rencana 13 Task 5): ONNX berbobot acak YOLOX-Nano dan YOLOX-Tiny 640 px, untuk mengukur kecepatan di Mini PC.
Model hasil latih tidak dibawa ke Mini PC (K15). Tanpa data plat dan tanpa jaringan.
  powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/data/alat-sementara/ekspor-yolox-640-acak.py /kerja/data/keluaran/cepat-calon-640
"""
import sys
from pathlib import Path

sys.path.insert(0, "/kerja/tools/lab")
import torch  # noqa: E402
import latih_yolox as ly  # noqa: E402

keluar = Path(sys.argv[1])
keluar.mkdir(parents=True, exist_ok=True)
torch.manual_seed(0)
for jenis in ("nano", "tiny"):
    model = ly.buat_model(jenis).eval()
    torch.onnx.export(model, torch.zeros(1, 3, 640, 640), str(keluar / f"acak-yolox-{jenis}-640.onnx"), input_names=["images"],
                      output_names=["output"], opset_version=17, dynamo=False)
for b in sorted(keluar.glob("*.onnx")):
    print(f"{b.name}: {b.stat().st_size} byte")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/data/alat-sementara/ekspor-yolox-640-acak.py /kerja/data/keluaran/cepat-calon-640; "EXIT=$LASTEXITCODE"`

Lalu langkah-langkah Rencana 12 Task 4 Step 3, dengan berkas yang dikirim:
- `tools/ukur_onnx_cpu.py`;
- `data/alat-sementara/minipc/requirements.txt` dan `jalan.sh`;
- kedua ONNX 640.

Urutannya: periksa beban dan folder; `mkdir`; `scp`; `bash jalan.sh`; ambil `hasil.json` ke
`data/keluaran/cepat-calon-640/minipc.json`; `rm -rf`; periksa sisa proses dengan `pgrep -af "[u]kur_onnx_cpu"`.
Expected: dua baris model dengan median per utas; `bersih`; `tanpa proses ukur`.

- [x] **Step 6: Salin ringkasan ke `bukti/` sesudah diperiksa tanpa nomor plat (dengan kontrol positif)**

`data/alat-sementara/periksa-bukti-13.py`:

```python
"""Sekali pakai (Rencana 13): menyalin ringkasan ke bukti-siap/ hanya bila tak satu pun teks plat atau nama berkas ada di
dalamnya. Larangan dan kontrol positif sama dengan periksa-bukti-12.py. Pakai: python periksa-bukti-13.py <tanggal-jalan>
"""
import json
import shutil
import sys
from pathlib import Path

K = Path("/kerja/data/keluaran")
tanggal = sys.argv[1]
larangan = set()
for berkas in ("set-uji-koreksi/pembagian-koreksi.json", "latih-koreksi/pembagian-koreksi.json"):
    p = json.loads((K / berkas).read_text())
    larangan |= {a["teks"] for s in p.values() for a in s}
    larangan |= {Path(b).stem for s in p.values() for a in s for b in a["berkas"]}
for berkas in ("label-curiga/curiga.json", "label-curiga-latih/curiga.json"):
    larangan |= {c["usulan"] for c in json.loads((K / berkas).read_text())}
stem = {b.stem for b in (K / "dataset/plat-lighting").rglob("*") if b.suffix.lower() in (".jpg", ".jpeg", ".png")}
larangan |= stem


def temuan(teks):
    return sum(1 for t in larangan if t in teks)


sementara = K / "bukti-siap" / "kontrol-13.tmp"
sementara.write_text("\n".join(sorted(stem)))
kontrol = temuan(sementara.read_text())
sementara.unlink()
print(f"ukuran daftar larangan: {len(larangan)}; kontrol positif (stem plat-lighting): {kontrol} ditemukan")
if kontrol == 0:
    sys.exit(1)
salin = [("cepat-calon-640/minipc.json", "cepat-yolox-640-minipc.json")]
for varian in ("nano-416", "nano-640", "tiny-416", "tiny-640"):
    salin += [(f"pencari-yolox-{varian}/mesin.json", f"pencari-yolox-{varian}.json"),
              (f"pencari-yolox-{varian}/mesin-onnx.json", f"pencari-yolox-{varian}-onnx.json"),
              (f"pencari-yolox-{varian}/nilai.json", f"pencari-yolox-{varian}-nilai.json"),
              (f"pencari-yolox-{varian}/cepat.json", f"pencari-yolox-{varian}-cepat.json")]
for asal, tujuan in salin:
    n = temuan((K / asal).read_text())
    print(f"{tujuan}: {n} teks plat atau nama berkas ditemukan")
    if n:
        sys.exit(1)
    shutil.copy(K / asal, K / "bukti-siap" / f"{tanggal}-{tujuan}")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/periksa-bukti-13.py 2026-10-16; "EXIT=$LASTEXITCODE"`
Expected: kontrol positif lebih dari 0; ketujuh belas berkas 0 temuan; `EXIT=0`. Lalu salin ketujuh belasnya ke `bukti/`.

- [x] **Step 7: Commit** ketujuh belas berkas bukti, dengan untuk tiap varian:
- F1 validasi dan zaman terbaik;
- angka uji per kelompok;
- kecepatan laptop dan Mini PC;
- lama latihan;
- tanda mesin.

---

### Task 6: Laporan, catatan, dan pertanyaan ke owner

- [x] **Step 1: Tulis laporan `bukti/2026-10-16-pencari-plat-yolox.md`**

Isinya:
- **Keempat calon:**
  - bobot awal dimuat dan dilewati;
  - F1 validasi, zaman terbaik, dan lama latihan;
  - angka uji per kelompok dengan rentang 95%, berdampingan dengan pembanding Rencana 12.
- **Kecepatan:** foto utuh di laptop dan model saja di Mini PC (416 dari Rencana 12, 640 dari Task 5), serta taksiran cari
  plat + baca huruf per foto dan per kedatangan terhadap sasaran dua detik.
- **Usulan agen:** calon yang dipakai di Rencana 14, dipilih dari validasi dan kecepatan, bukan dari angka uji.
- **Batas:**
  - satu dataset dengan 393 foto latih, 84 uji;
  - satu benih;
  - bobot awal `BELUM-JELAS`, jadi tanda `RISET-SAJA`;
  - kecepatan Mini PC dari bobot acak dan masukan buatan;
  - variasi latihan sederhana (tanpa mosaic).

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 13 ditulis" dan "Rencana 13 dijalankan" dicentang dengan angka;
  - butir berikutnya "Owner memilih pencari plat untuk rantai utuh (Rencana 14)";
  - status dan changelog.
- `CLAUDE.md` §7: pencari YOLOX di `data/keluaran/pencari-yolox-*/`, hanya dimuat lewat `PencariYolox` (ONNX) atau
  `muat_mesin` (safetensors); bobot awal hanya `weights_only=True`.
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 13".
- `data-asal/bahan.json`:
  - butir `bobot-yolox`: diunduh dan dikunci;
  - butir `dataset-plat-lighting`: sisi latih dipakai.
- Rencana ini: kotak dicentang dan catatan pelaksanaan.

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `188 passed`.

- [x] **Step 4: BERHENTI. Laporkan ke owner**

Ringkas dalam bahasa sederhana, lalu **satu** pertanyaan pilihan ganda dengan saran di depan: calon mana yang dipakai di
Rencana 14. Bila tidak ada calon yang cukup baik, pilihannya: menambah bahan latih (dataset UI, label video riset), menyetel
latihan, atau tetap lanjut dengan batas tertulis.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K30, spec 2.3, 2.6, dan 8.1 langkah 7:**
  - empat calon dari dua jenis dan dua ukuran;
  - bobot tanpa pickle (safetensors, ONNX);
  - kecepatan di server fase awal;
  - pilihan ke owner.
- **Rantai pasok:**
  - tanpa paket baru;
  - bobot awal terkunci SHA-256 (dipercaya pada unduhan pertama, dicatat);
  - pickle hanya lewat `weights_only=True`, dengan uji kode pickle ditolak;
  - ONNX disimpan hanya bila sama dengan torch.
- **Set uji tidak bocor:** zaman dan ambang dipilih di validasi; uji dibaca sekali per calon; usulan calon dari validasi dan
  kecepatan.
- **Data pribadi:**
  - layar tanpa nama berkas (diuji di proses terpisah);
  - model hasil latih dan foto tidak dibawa ke Mini PC;
  - bukti diperiksa dengan kontrol positif.
- **Uji rantai:**
  - CLI latih sampai safetensors dan `mesin.json` (gerbang biasa);
  - latih, ekspor, lalu `PencariYolox` dibandingkan dengan torch (image tambahan).
- **Angka gerbang:** Node 107 tetap; lab 178 → 182 → 188; uji image tambahan 14 → 17.
- **Nama konsisten:**
  - `letterbox`, `nms`, `urai_keluaran`, `masukan`, `PencariYolox`, `cepat`;
  - `siapkan_yolox`, `buat_model`, `muat_bobot_awal`, `ke_target`, `balik`, `ubah_acak`, `baca_sisi`, `angkatan`,
    `cari_torch`, `kelompok_parameter`, `latih`, `muat_mesin`, `ekspor`;
  - kunci `mesin.json`: `sha256_bobot`, `bobot_awal.dimuat` dan `.dilewati`, `f1_validasi_terbaik`, `ambang_validasi`;
  - kunci `mesin-onnx.json`: `sha256_onnx`, `ukuran`, `pemeriksaan.sama` dan `.gambar`.

## Catatan pelaksanaan (16 Okt)

- Dijalankan atas lampu hijau owner ("A", termasuk Mini PC). Laporan:
  [`bukti/2026-10-16-pencari-plat-yolox.md`](../bukti/2026-10-16-pencari-plat-yolox.md).
- **Menyimpang dari rencana, dengan alasan:**
  - **Penjaga ekspor ONNX ditimbang per satuan.** `BATAS_MENTAH` (satu batas mutlak 1e-2 untuk koordinat dan peluang) menolak
    Nano-640 karena selisih koordinat 0,038 piksel, padahal deteksinya sama 20 dari 20 dan peluangnya hanya beda 1,0e-4. Kode
    Task 3 dan Task 4 di atas yang memuat `BATAS_MENTAH` dan `selisih_terbesar` sudah diganti dengan `selisih_mentah`,
    `mentah_sama`, `BATAS_PELUANG` (1e-3), serta `pemeriksaan.selisih_koordinat` dan `.selisih_peluang` (commit 092cbaf).
    Karena itu gerbang lab berakhir di 190, bukan 188.
  - **Kecepatan laptop diukur tiga putaran bergiliran.** Putaran tunggal di Task 5 Step 4 jatuh bersamaan dengan uji mutasi
    milik sesi lain. Diukur ulang sesudahnya dengan `data/alat-sementara/cepat-tiga-putaran-13.ps1`, lalu digabung
    `data/alat-sementara/gabung-cepat-13.mjs`: `cepat.json` tiap calon berisi median tiga putaran dan ketiga putarannya.
  - Diagnosis selisih ONNX per kolom memakai `data/alat-sementara/diagnosa-ekspor-yolox.py` (ONNX ditulis ke `/tmp` kontainer,
    `mesin.onnx` tidak disentuh).
- **Gerbang:** Node 107; lab 178 → 182 → 188 → 190; uji image tambahan 14 → 17.
- **Lama latihan:** 30,5 / 36,3 / 32,3 / 48,7 menit (Nano-416, Nano-640, Tiny-416, Tiny-640).
