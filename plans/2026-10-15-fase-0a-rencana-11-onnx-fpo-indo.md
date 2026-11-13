# Fase 0A, Rencana 11: Mesin baca huruf siap server — ONNX fpo-indo-1 dan kecepatannya di CPU (K25, K28) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** fpo-indo-1 tersedia sebagai `mesin.onnx` yang terbukti membaca sama dengan versi Keras-nya, bisa dijalankan
dengan pembaca yang sama dengan fast-plate-ocr terbitan (`LicensePlateRecognizer`, ONNX Runtime, CPU), dan kecepatannya di
CPU terukur dengan 1, 2, dan 4 utas. Ini langkah 8 spec 8.1 untuk baca huruf, dengan arti sesudah K25: kecepatan di server,
bukan di kotak.

**Architecture:** Ekspor ONNX bawaan gagal di Keras + torch (Rencana 10). Jalan yang dipakai: ONNX terbitan `cct_s_v2_global`
punya susunan yang sama persis dengan fpo-indo-1, jadi angka bobotnya ditukar. Alat baru `tools/lab/onnx_fpo.py`:
1. Mencari pemetaan tiap tensor bobot Keras ke initializer ONNX dari **pasangan terbitan** (`.keras` dan `.onnx` dari rilis
   yang sama), dengan mencocokkan nilainya.
2. Menolak pemetaan yang tidak lengkap atau tidak satu-satu.
3. Memasang bobot `mesin.keras` dengan cara yang sama.
4. Menyimpan hasilnya hanya bila keluarannya sama dengan Keras pada 460 gambar validasi.

Pembacanya `LicensePlateRecognizer`, sama dengan pembaca fast-plate-ocr terbitan di Rencana 6.

**Tech Stack:** Python di image `cctvgerbang-lab-fpo:v1` (onnx 1.23.2, onnxruntime 1.30.0, Keras 3.15.1 di atas torch,
fast-plate-ocr @ 9ce7a5b), pytest, PowerShell (pintu lab), Node (pemeriksa mesin jualan).

**Dasar:** K25, K26, K27, K28 (`SEED.md` §3); laporan Rencana 10 (`bukti/2026-10-15-fpo-latih-ulang.md`); spec 8.1
langkah 8; P16 (spesifikasi server IBE, belum dijawab).

---

## Yang diukur sebelum rencana ini ditulis (15 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Pemetaan bobot Keras terbitan ke ONNX terbitan | Ke-192 tensor bobot Keras masing-masing cocok dengan **tepat satu** initializer ONNX, dan tiap initializer dipakai paling banyak sekali. 147 sama persis, 40 sama nilainya dengan bentuk lain, dan 5 kernel konvolusi dengan sumbu disusun ulang (4 dengan urutan `3,2,0,1`, 1 dengan `2,3,0,1`). Semuanya initializer float32; tidak ada yang berupa simpul Constant | `data/alat-sementara/ukur-tukar-bobot.py`, lab `-Fpo` |
| Yang tidak dipetakan | 9 initializer berukuran lebih dari 1: kernel pemotong petak (`patch_extractor_1/convolution__395:0`, 448×112×2×2, bukan bobot latih; bagian yang membuat ekspor torch gagal) dan 8 konstanta bentuk | sama |
| ONNX terbitan | Masukan `input` uint8 (N, 64, 128, 3); keluaran `plate` (N, 10, 37) dan `region` (N, 66); opset 15, IR 8 | sama |
| Pengekspor dynamo torch | `onnxscript` tidak ada di image; menambahnya berarti paket baru, pemeriksaan celah, dan image baru | sama |
| Pembaca terbitan | `LicensePlateRecognizer(device, providers, sess_options, onnx_model_path, plate_config_path)`; `sess_options` diteruskan ke `InferenceSession`, jadi jumlah utas bisa diatur | `fast_plate_ocr/inference/plate_recognizer.py` baris 124–203 |
| Kecepatan pembanding | fast-plate-ocr terbitan (ONNX, CPU, utas bawaan) 0,011 detik per gambar; fpo-indo-1 lewat Keras di kartu grafis 0,044 detik per gambar | `bukti/2026-10-14-baca-fpo-pertama.json`, `bukti/2026-10-15-baca-fpo-indo-1.json` |
| Mesin ini | AMD Ryzen 7 8700F, 8 inti, 16 utas; container lab melihat 12 CPU | `Win32_Processor`, `os.cpu_count()` di lab |

Akibatnya bagi rencana ini:

1. **Tukar bobot, bukan ekspor ulang.** Tidak ada paket baru dan tidak ada image baru. Pemetaan ditemukan dari pasangan
   terbitan, lalu diuji dua arah:
   - menukar dengan bobot terbitan sendiri tidak mengubah ONNX terbitan;
   - menukar dengan bobot yang diubah memberi keluaran yang sama dengan Keras.
2. **Gagal tertutup.** Pemetaan yang tidak lengkap, ganda, atau tidak satu-satu ditolak. `mesin.onnx` disimpan hanya bila
   bacaannya sama dengan Keras pada **semua** gambar validasi dan selisih terbesarnya di bawah 1e-4.
3. **Kecepatan diukur di CPU** dengan 1, 2, dan 4 utas, karena server IBE belum diketahui (P16). Ini taksiran, bukan angka
   server. Yang diukur hanya **baca huruf dari potongan plat**; mencari plat di foto utuh belum ada (Rencana 12).

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–10 | Bengkel sampai fpo-indo-1 | Selesai 13–15 Okt |
| **11 (dokumen ini)** | ONNX fpo-indo-1, kesamaan dengan Keras, angka set uji lewat ONNX, kecepatan CPU | Ditulis dan dijalankan 15 Okt |
| 12 | Mencari plat di foto utuh dan video riset: calon pencari plat (spec 8.1 langkah 7 untuk langkah 1), izinnya, dan bahan berkotak | Sesudahnya |
| 13 | Laporan Fase 0A (langkah 9) dan keputusan owner. Plat buatan komputer (langkah 4) diputuskan di sini: dibuat atau tidak | Sesudahnya |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 8–10. Tambahan:
- **Pengukuran kecepatan saat mesin tenang:** `docker ps` hanya menunjukkan container lain yang diam, tidak ada job lab lain,
  dan tidak ada pekerjaan berat di laptop. Angkanya dicatat bersama jumlah CPU yang terlihat container.
- **Set uji dibaca ulang lewat ONNX hanya untuk membuktikan kesamaan.** Tidak ada pilihan yang diambil dari angka ini. Bila
  ada gambar yang bacaannya berbeda dengan Keras, jumlahnya dilaporkan apa adanya.
- Nama berkas bukti memakai tanggal jalan (`2026-10-16` di bawah). Bila dijalankan pada tanggal lain, tanggal itu diganti.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/onnx_fpo.py` (baru) | Pemetaan dan penukaran bobot; `buat`, `baca`, `cepat`, `samakan`; pembaca ONNX | 1, 2 |
| `tools/lab/uji/test_onnx_fpo.py` (baru) | Uji tanpa Keras dan pustaka onnx (gerbang lab biasa) | 1, 2 |
| `tools/lab/uji_fpo/test_onnx_fpo_sungguhan.py` (baru) | Uji dengan Keras, onnx, dan berkas model; plat buatan (di luar gerbang) | 2 |
| `bukti/2026-10-16-*` (baru) | Ringkasan dan laporan | 3, 4 |

---

### Task 1: Pemetaan bobot Keras ke initializer ONNX

**Files:** Create `tools/lab/onnx_fpo.py`, `tools/lab/uji/test_onnx_fpo.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_onnx_fpo.py`:

```python
"""Uji tools/lab/onnx_fpo.py yang tidak butuh Keras atau pustaka onnx (gerbang lab biasa): pemetaan bobot Keras ke
initializer ONNX (cara cocok dan kebalikannya, lengkap, satu-satu, tanpa pasangan ganda), hitungan beda bacaan tanpa nomor
plat, dan pembaca ONNX yang menolak mesin.onnx yang berubah."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import onnx_fpo as of  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "onnx_fpo.py"


def contoh():
    """Tiga bobot Keras dan initializer ONNX-nya dengan tiga cara berbeda, ditambah satu konstanta yang bukan bobot."""
    rng = np.random.default_rng(0)
    kernel = rng.normal(size=(3, 3, 2, 4)).astype(np.float32)  # konvolusi Keras: tinggi, lebar, masuk, keluar
    padat = rng.normal(size=(5, 6)).astype(np.float32)
    bias = rng.normal(size=(7,)).astype(np.float32)
    init = {"conv": np.transpose(kernel, (3, 2, 0, 1)), "dense": padat.copy(), "bias": bias.reshape(1, 1, 7),
            "bentuk": np.array([1, 2, 3, 4], dtype=np.int64)}
    return [kernel, padat, bias], init


def test_cara_cocok_dan_kebalikannya():
    rng = np.random.default_rng(1)
    w4 = rng.normal(size=(3, 3, 2, 4)).astype(np.float32)
    w2 = rng.normal(size=(5, 6)).astype(np.float32)
    kasus = [(w2, w2.copy(), "sama"), (w2, w2.reshape(3, 10), "bentuk-lain"), (w2, w2.T.copy(), "dibalik"),
             (w4, np.transpose(w4, (3, 2, 0, 1)).copy(), "sumbu:3,2,0,1"),
             (w4, np.transpose(w4, (2, 3, 0, 1)).copy(), "sumbu:2,3,0,1")]

    for w, v, cara in kasus:
        assert of.cara_cocok(w, v) == cara
        assert np.array_equal(of.terapkan(cara, w, v.shape), v)


def test_cara_cocok_menolak_nilai_atau_ukuran_lain():
    w = np.arange(12, dtype=np.float32).reshape(3, 4)

    assert of.cara_cocok(w, w + 1) is None
    assert of.cara_cocok(w, w[:2]) is None


def test_peta_lengkap_satu_satu_dan_melewati_konstanta():
    bobot, init = contoh()

    assert of.peta(bobot, init) == [("conv", "sumbu:3,2,0,1"), ("dense", "sama"), ("bias", "bentuk-lain")]


def test_peta_menolak_bobot_tanpa_pasangan():
    bobot, init = contoh()
    del init["dense"]

    with pytest.raises(of.PetaDitolak, match="0 pasangan"):
        of.peta(bobot, init)


def test_peta_menolak_bobot_dengan_dua_pasangan():
    bobot, init = contoh()
    init["dense_salinan"] = init["dense"].copy()

    with pytest.raises(of.PetaDitolak, match="2 pasangan"):
        of.peta(bobot, init)


def test_peta_menolak_dua_bobot_pada_satu_initializer():
    bobot, init = contoh()

    with pytest.raises(of.PetaDitolak, match="initializer yang sama"):
        of.peta([bobot[1], bobot[1].copy()], {"dense": init["dense"]})
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat koleksi `ModuleNotFoundError: No module named 'onnx_fpo'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis `tools/lab/onnx_fpo.py` bagian pertama**

```python
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
    if hasil.shape != tuple(bentuk):
        raise ValueError(f"bentuk {hasil.shape} bukan {tuple(bentuk)}")
    return np.ascontiguousarray(hasil, dtype=np.float32)


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
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `167 passed` (161 + 6), `EXIT=0`.

- [x] **Step 5: Commit** `tools/lab/onnx_fpo.py` dan ujinya, dengan alasan (ekspor gagal; pemetaan terukur 192/192 satu-satu)
dan angka gerbang 161 → 167.

---

### Task 2: Membuat, membaca, dan mengukur `mesin.onnx`

**Files:** Modify `tools/lab/onnx_fpo.py`, `tools/lab/uji/test_onnx_fpo.py`; Create `tools/lab/uji_fpo/test_onnx_fpo_sungguhan.py`

- [x] **Step 1: Tulis ujinya**

Tambahkan di akhir `tools/lab/uji/test_onnx_fpo.py`:

```python
def test_samakan_menghitung_beda_tanpa_mencetak_nomor_plat(tmp_path):
    for nama, bacaan in (("a", ["B1234XY", "D5678AB", "F9012Z"]), ("b", ["B1234XY", "D5678AE", "F9012Z"])):
        (tmp_path / f"{nama}.jsonl").write_text("".join(json.dumps({"berkas": f"{i}.jpg", "bacaan": t}) + "\n"
                                                        for i, t in enumerate(bacaan)))

    assert of.beda_bacaan(tmp_path / "a.jsonl", tmp_path / "b.jsonl") == {"gambar": 3, "beda": 1}
    hasil = subprocess.run([sys.executable, str(SKRIP), "samakan", str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl")],
                           capture_output=True, text=True)
    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar
    assert "gambar 3, beda 1" in layar and not any(t in layar for t in ("B1234XY", "D5678A", "F9012Z"))


def test_pembaca_onnx_menolak_mesin_onnx_yang_berubah_sebelum_memuat_apa_pun(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"ditukar")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64}))

    with pytest.raises(of.ModelDitolak, match="SHA-256"):
        of.PembacaOnnxMesin(tmp_path, tmp_path / "unduhan")
```

Buat `tools/lab/uji_fpo/test_onnx_fpo_sungguhan.py`:

```python
"""Uji tools/lab/onnx_fpo.py dengan Keras, pustaka onnx, dan berkas model terbitan, di image lab tambahan (di luar gerbang
biasa), hanya dengan plat buatan:

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import sys
from pathlib import Path

import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import latih_fpo as lf  # noqa: E402
import onnx_fpo as of  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from test_latih_fpo import UJI, buat  # noqa: E402
from test_percobaan_fpo import ADA, TEKS, plat_buatan  # noqa: E402

pytestmark = pytest.mark.skipif(not ADA, reason="berkas model belum diunduh (Rencana 9 Task 1)")


def terbitan():
    jalur = lf.jalur_terkunci(UNDUHAN)
    lf.siapkan_torch()
    import onnx
    from onnx import numpy_helper
    from fast_plate_ocr.train.model.config import load_plate_config_from_yaml
    from fast_plate_ocr.train.utilities.utils import load_keras_model

    cfg = load_plate_config_from_yaml(jalur["plat"])
    asli = onnx.load(str(of.berkas_terkunci(UNDUHAN, of.BUTIR_ONNX)))
    init = {i.name: numpy_helper.to_array(i) for i in asli.graph.initializer}
    return cfg, load_keras_model(jalur["keras"], cfg), asli, init


def test_peta_terbitan_lengkap_dan_menukar_bobot_terbitan_tidak_mengubah_onnx():
    from onnx import numpy_helper

    _, model, asli, init = terbitan()
    p = of.peta(model.get_weights(), init)
    sendiri = of.tukar(asli, p, model.get_weights())

    assert len(p) == 192
    assert all(np.array_equal(numpy_helper.to_array(a), numpy_helper.to_array(b))
               for a, b in zip(asli.graph.initializer, sendiri.graph.initializer, strict=True))


def test_onnx_hasil_tukar_sama_dengan_keras_untuk_bobot_yang_diubah():
    import onnxruntime as ort

    cfg, model, asli, init = terbitan()
    p = of.peta(model.get_weights(), init)
    rng = np.random.default_rng(0)
    model.set_weights([w + rng.normal(0, 0.01, w.shape).astype(w.dtype) for w in model.get_weights()])
    baru = ort.InferenceSession(of.tukar(asli, p, model.get_weights()).SerializeToString(), providers=["CPUExecutionProvider"])
    lama = ort.InferenceSession(asli.SerializeToString(), providers=["CPUExecutionProvider"])
    gambar = [plat_buatan(t) for t in TEKS]

    n, sama, selisih = of.banding(model, baru, cfg, gambar)
    _, _, selisih_lama = of.banding(model, lama, cfg, gambar)

    assert n == len(TEKS) and sama == n and selisih < of.BATAS_SELISIH
    # Bobotnya memang berubah: ONNX terbitan tidak lagi sama dengan Keras, jadi uji di atas tidak kosong.
    assert selisih_lama > 100 * of.BATAS_SELISIH


def test_rantai_buat_baca_cepat_dengan_plat_buatan(tmp_path):
    pembagian, folder = buat(tmp_path)
    mesin = tmp_path / "mesin"
    lf.siapkan(pembagian, folder, mesin)
    lf.latih(mesin, UNDUHAN, zaman=1)

    meta = of.buat(mesin, UNDUHAN)
    onnx_ = of.PembacaOnnxMesin(mesin, UNDUHAN)
    keras_ = lf.PembacaMesinFpo(mesin, UNDUHAN)
    ringkasan = of.baca(pembagian, folder, mesin, UNDUHAN, tmp_path / "baca")
    kecepatan = of.cepat(mesin, UNDUHAN, utas=(1,), panaskan=1)

    assert meta["sha256_onnx"] == lf.sha256_berkas(mesin / "mesin.onnx") and meta["tensor_ditukar"] == 192
    assert meta["pemeriksaan_validasi"]["plat_sama"] == meta["pemeriksaan_validasi"]["gambar"] > 0
    assert meta["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"] and meta["tujuan"] == "belajar"
    assert [onnx_(plat_buatan(t)) for t in TEKS] == [keras_(plat_buatan(t)) for t in TEKS]
    assert ringkasan["per_kelompok"]["mobil-terang"]["kedatangan"] == len(UJI)
    assert kecepatan["per_utas"]["1"]["utuh_ms"]["median"] > 0
    (mesin / "mesin.onnx").write_bytes(b"ditukar")
    with pytest.raises(ModelDitolak):
        of.PembacaOnnxMesin(mesin, UNDUHAN)
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `2 failed, 167 passed` (`AttributeError` pada `beda_bacaan` dan `PembacaOnnxMesin`), `EXIT=1`.

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `3 failed, 9 passed` (`AttributeError` pada `berkas_terkunci` di dua uji pertama dan `buat` di uji rantai),
`EXIT=1`.

- [x] **Step 3: Tambahkan bagian ONNX di `tools/lab/onnx_fpo.py`**

Sisipkan sesudah fungsi `peta`:

```python
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
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `169 passed`, `EXIT=0`.

Run (PowerShell): `nvidia-smi --query-gpu=memory.used --format=csv,noheader` lalu
`powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `12 passed`, `EXIT=0`.

- [x] **Step 5: Gerbang Node, lalu commit**

Run: `npm test; echo "EXIT=$?"` (Expected `pass 107`)

Commit `tools/lab/onnx_fpo.py` dan ketiga berkas uji, dengan alasan (gagal tertutup, pembaca sama dengan pembaca terbitan,
uji dua arah), angka gerbang lab 167 → 169, dan uji image tambahan 9 → 12.

---

### Task 3: ONNX fpo-indo-1 sungguhan, kesamaan, dan kecepatan

**Files:** Create `data/alat-sementara/periksa-bukti-11.py` (sekali pakai, di-gitignore), `bukti/2026-10-16-*.json`

- [x] **Step 1: Buat `mesin.onnx`**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py buat /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan; "EXIT=$LASTEXITCODE"`
Expected: `dibuat mesin.onnx: 192 tensor ditukar ({'sama': 147, 'bentuk-lain': 40, 'sumbu': 5}); validasi plat sama 460 dari 460; selisih terbesar ...` dengan selisih di bawah 1e-4, `EXIT=0`.
Bila `DITOLAK`, **berhenti** dan laporkan pesannya.

- [x] **Step 2: Periksa tanda mesin**

Run: `node tools/periksa-jualan.mjs data/keluaran/fpo-indo-1/mesin-onnx.json; echo "EXIT=$?"`
Expected: `mesin "fpo-indo-1" (belajar): tanda mesin = RISET-SAJA`, `EXIT=0`.

- [x] **Step 3: Baca set uji lewat ONNX (pembuktian kesamaan, bukan pemilihan)**

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py baca /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-indo-1-onnx; "EXIT=$LASTEXITCODE"`
Expected: empat baris per kelompok dan `detik per gambar`; `EXIT=0`.

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py samakan /kerja/data/keluaran/baca-fpo-indo-1/hasil.jsonl /kerja/data/keluaran/baca-fpo-indo-1-onnx/hasil.jsonl; "EXIT=$LASTEXITCODE"`
Expected: `gambar 1422, beda 0`, `EXIT=0`. Bila beda lebih dari 0, jumlahnya dan selisih angka per kelompok dicatat apa adanya.

- [x] **Step 4: Ukur kecepatan di CPU (saat mesin tenang)**

Periksa dulu (PowerShell): `docker ps --format '{{.Image}} {{.Status}}'` dan `nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader`.

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 -Fpo python /kerja/tools/lab/onnx_fpo.py cepat /kerja/data/keluaran/fpo-indo-1 /kerja/data/unduhan /kerja/data/keluaran/cepat-fpo-indo-1/ringkasan.json; "EXIT=$LASTEXITCODE"`
Expected: `CPU terlihat 12; gambar 460, panaskan 10`, lalu tiga baris `utas 1`, `utas 2`, `utas 4` dengan median dan p95
dalam milidetik; `EXIT=0`.

- [x] **Step 5: Salin ringkasan ke `bukti/` sesudah dibuktikan tanpa nomor plat (dengan kontrol positif)**

Buat `data/alat-sementara/periksa-bukti-11.py`:

```python
"""Sekali pakai (Rencana 11): menyalin ringkasan ke bukti-siap/ hanya bila tak satu pun teks plat atau nama berkas ada di
dalamnya. Larangan sama dengan Rencana 10. Kontrol positif lebih dulu pada baca-fpo-indo-1-onnx/hasil.jsonl; bila tidak
menemukan apa pun, berhenti. Hanya hitungan yang dicetak. Pakai: python periksa-bukti-11.py <tanggal-jalan>
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


def temuan(teks):
    return sum(1 for t in larangan if t in teks)


kontrol = temuan((K / "baca-fpo-indo-1-onnx/hasil.jsonl").read_text())
print(f"ukuran daftar larangan: {len(larangan)}; kontrol positif (baca-fpo-indo-1-onnx/hasil.jsonl): {kontrol} ditemukan")
if kontrol == 0:
    sys.exit(1)
for asal, tujuan in [("fpo-indo-1/mesin-onnx.json", "fpo-indo-1-onnx.json"),
                     ("baca-fpo-indo-1-onnx/ringkasan.json", "baca-fpo-indo-1-onnx.json"),
                     ("cepat-fpo-indo-1/ringkasan.json", "cepat-fpo-indo-1.json")]:
    n = temuan((K / asal).read_text())
    print(f"{tujuan}: {n} teks plat atau nama berkas ditemukan")
    if n:
        sys.exit(1)
    shutil.copy(K / asal, K / "bukti-siap" / f"{tanggal}-{tujuan}")
```

Run (PowerShell): `powershell -NoProfile -File D:\Projects\super-team-v1\cctvgerbang-seed\tools\lab.ps1 python /kerja/data/alat-sementara/periksa-bukti-11.py 2026-10-16; "EXIT=$LASTEXITCODE"`
Expected: kontrol positif lebih dari 0, ketiga berkas `0 teks plat atau nama berkas ditemukan`, `EXIT=0`.

Run: `cp data/keluaran/bukti-siap/2026-10-16-fpo-indo-1-onnx.json data/keluaran/bukti-siap/2026-10-16-baca-fpo-indo-1-onnx.json data/keluaran/bukti-siap/2026-10-16-cepat-fpo-indo-1.json bukti/`

- [x] **Step 6: Commit** ketiga berkas `bukti/2026-10-16-*`, dengan hasil pemeriksaan validasi, jumlah beda bacaan set uji,
angka kecepatan per utas, CPU yang terlihat, dan tanda mesin.

---

### Task 4: Laporan, catatan, dan pertanyaan ke owner

- [x] **Step 1: Tulis laporan `bukti/2026-10-16-fpo-indo-1-onnx.md`**

Isinya:
- **Cara:** tukar bobot; angka pemetaan; pemeriksaan dua arah.
- **Kesamaan:** validasi 460 gambar, selisih terbesar, beda bacaan set uji.
- **Angka set uji lewat ONNX:** harus sama dengan laporan Rencana 10.
- **Kecepatan:** tabel per utas (dekode, utuh, model; median dan p95), dibandingkan dengan fast-plate-ocr terbitan (0,011
  detik, Rencana 6) dan Keras di kartu grafis (0,044 detik).
- **Taksiran kasar jumlah foto per detik per inti:** dari median utuh, ditulis sebagai taksiran.
- **Batas:**
  - CPU mesin ini, bukan server IBE (P16);
  - hanya baca huruf dari potongan plat, tanpa mencari plat dan tanpa unggah foto;
  - container melihat 12 CPU dan mesin dipakai bersama;
  - tanda `RISET-SAJA`.

- [x] **Step 2: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 11 ditulis" dan "Rencana 11 dijalankan" dicentang dengan angka;
  - butir berikutnya "Rencana 12 Fase 0A ditulis" (mencari plat);
  - status dan changelog.
- `CLAUDE.md` §7: `mesin.onnx` fpo-indo-1 dibuat dengan menukar bobot ke ONNX terbitan (`tools/lab/onnx_fpo.py`) dan hanya
  dimuat lewat `PembacaOnnxMesin` (SHA-256 terhadap `mesin-onnx.json`).
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 11" (B5).
- Rencana ini: kotak dicentang dan catatan pelaksanaan.

- [x] **Step 3: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 107` dan `169 passed`.

- [x] **Step 4: BERHENTI. Laporkan ke owner**

Ringkas dalam bahasa sederhana: mesin sudah dalam format server, bacaannya sama, dan berapa foto per detik di CPU. Lalu
**satu** pertanyaan, yaitu P16: server IBE seperti apa (inti CPU, kartu grafis, sewa atau milik sendiri), dengan saran di
depan. Jawabannya dipakai untuk taksiran biaya di laporan Fase 0A. Rencana 12 ditulis sesudahnya.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K25, K28, dan spec 8.1 langkah 8:** format server (Task 1–3), kesamaan bacaan (Task 3 Step 1 dan 3), kecepatan
  CPU per utas (Task 3 Step 4), laporan (Task 4). Mencari plat dan laporan Fase 0A ada di Rencana 12 dan 13.
- **Gagal tertutup:**
  - pemetaan tidak lengkap, ganda, atau tidak satu-satu ditolak (diuji);
  - tukar-diri harus tidak mengubah ONNX terbitan;
  - `mesin.onnx` disimpan hanya bila 460/460 validasi sama dan selisih < 1e-4;
  - validasi kosong ditolak;
  - `mesin.onnx` yang berubah ditolak sebelum dimuat (diuji).
- **Uji tidak kosong:** uji bobot yang diubah memastikan ONNX terbitan memang berbeda dengan Keras, sebelum menyimpulkan
  ONNX hasil tukar sama.
- **Perlakuan sama:** pembaca ONNX memakai `LicensePlateRecognizer`, kelas yang sama dengan pembaca fast-plate-ocr terbitan.
- **Data pribadi:** layar hanya hitungan; galat hanya jenisnya; `samakan` hanya mencetak jumlah; bukti diperiksa dengan
  kontrol positif.
- **Tanpa paket baru dan image baru.**
- **Angka gerbang:** Node 107 tetap; lab 161 → 167 → 169; uji image tambahan 9 → 12.
- **Nama konsisten:**
  - `cara_cocok`, `terapkan`, `peta`, `PetaDitolak`, `berkas_terkunci`, `tukar`, `masukan`, `banding`, `gambar_csv`,
    `buat`, `PembacaOnnxMesin`, `baca`, `cepat`, `beda_bacaan`, `utama`;
  - kunci `mesin-onnx.json`: `sha256_onnx`, `tensor_ditukar`, `pemeriksaan_validasi.plat_sama`, `.gambar`,
    `.selisih_terbesar`, `bahan`, `tujuan`;
  - kunci `cepat`: `per_utas[utas].utuh_ms.median`.

## Catatan pelaksanaan (15 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Commit: `fec3a44` (Task 1), `d585643` (Task 2), `5a044c1` (Task 3), dan commit
laporan dan catatan (Task 4).

| Task | Hasil | Menyimpang dari rencana |
|---|---|---|
| 1 | Merah dulu (modul belum ada); lab 161 → 167 | — |
| 2 | Merah dulu (2 gagal di gerbang biasa, 3 gagal di image tambahan, semuanya `AttributeError`); lab 170; uji image tambahan 12 | Run hijau pertama: pemeriksaan tukar-diri menolak karena 19 alpha DyT skalar `()` menjadi `(1,)` (`np.ascontiguousarray`). Keluaran tidak berubah; uji fungsional dua arah lulus. Uji skalar ditambahkan (merah dulu), diperbaiki dengan `np.array(..., order="C")` dan pemeriksaan bentuk sesudah konversi. Lab 170, bukan 169 |
| 3 | 192 ditukar; validasi 460/460, selisih 1,30e-5; set uji lewat ONNX 1.422 gambar beda 0; kecepatan 23,3 / 14,3 / 10,4 ms (1 / 2 / 4 utas); tanda `RISET-SAJA`; bukti diperiksa dengan kontrol positif (2.379) | Nama berkas bukti bertanggal 2026-10-15 (tanggal jalan) |
| 4 | Laporan `bukti/2026-10-15-fpo-indo-1-onnx.md`, catatan, gerbang Node 107 dan lab 170 | Laporan bertanggal 2026-10-15 |

**Untuk rencana berikutnya:** kecepatan rantai utuh butuh pencari plat (Rencana 12); taksiran server menunggu P16.
