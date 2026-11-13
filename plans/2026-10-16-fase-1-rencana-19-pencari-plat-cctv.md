# Fase 1, Rencana 19: Pencari plat dilatih ulang dengan gambar CCTV (K36, K37) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Berhenti dua kali untuk owner: lembar latih (Task 5) dan dua lembar ukur (Task 8).

**Goal:** Pencari plat YOLOX-Nano-640 dilatih ulang dengan gambar dari video **sisi latih** Fase 1, supaya di CCTV ia berhenti
menangkap benda bukan plat dan lebih jarang melewatkan plat. Titik awal (Rencana 17): 105 dari 120 baris bukan plat, 11 dari 14
"yakin" bukan plat, dan plat terlewat di 4 dari 10 bingkai. Hasilnya diukur lagi di set uji yang sama dengan lembar yang sama.

**Architecture:**
- **`tools/lab/rantai.py`:**
  - tiap penampakan mencatat nomor gambarnya;
  - `--simpan-penampakan` menulis `penampakan.jsonl` (kotak per gambar per jalur, tanpa teks);
  - `--ambang` mengganti ambang kotak;
  - tiap kedatangan mencatat rerata keyakinan kotaknya.
- **`tools/lab/lembar_rantai.py`:** `--urut keyakinan` memilih baris dengan keyakinan kotak tertinggi, supaya benda yang paling
  mengecoh dan plat yang paling jelas ikut terperiksa.
- **`tools/lab/dataset_cctv.py` (baru):** dataset format YOLO yang berisi:
  - gambar latih dengan kotak yang dipilah owner;
  - kotak yang belum dipilah ditutup dengan buram kuat, supaya tidak menjadi contoh negatif yang salah;
  - gambar latar yang ditempeli 1–3 plat buatan;
  - plat-lighting.

  Sisi validasinya seperempat video latih, ditentukan dari SHA-256 masing-masing, ditambah valid plat-lighting.
- **`tools/lab/latih_yolox.py`:** `--bahan` mencatat semua bahan di `mesin.json` (video riset dan plat buatan ikut).
- **`tools/lab/kendaraan.py` (baru, K39, ditambahkan sesudah Task 6):** tahap kendaraan. Kendaraan dicari lebih dulu dengan YOLOX
  COCO terkunci dalam ONNX, lalu kotak plat diterima hanya bila tengahnya di dalam kotak kendaraan. Rantai dan lembar bingkai
  mendapat `--kendaraan`.

**Tech Stack:** Python di lab dan image tambahan, GPU untuk melatih (satu job).

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Qwen3-VL-2B lokal sebagai pemilah "plat atau bukan" | Terhadap 240 baris yang sudah dinilai owner (Rencana 14 dan 17): tp 10, fp 5, fn 26, tn 199. Presisi "plat" 0,67, ingatan 0,28. **Tidak cukup untuk menjadi pelabel**, jadi label tetap dari owner | `data/alat-sementara/qwen-plat-atau-bukan.py` (hanya hitungan) |
| Label owner yang bisa dipakai ulang | Lembar Rencana 14 tidak menyimpan kotak per gambar, jadi labelnya tidak bisa dipetakan ke gambar. Lembar Rencana 17 berasal dari sisi uji, jadi tidak boleh dipakai melatih | `rantai.py` (Rencana 14), spec 8.3 |
| Video sisi latih | 39 video (gerbang 18, parkiran 9, kamera diam lain 12, menurut lapis) | `data-asal/pembagian-video-fase1.json` |

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/rantai.py`, `tools/lab/uji/test_rantai.py` (ubah) | Penampakan per gambar, ambang, keyakinan kotak | 1 |
| `tools/lab/lembar_rantai.py`, `tools/lab/uji/test_lembar_rantai.py` (ubah) | Urut keyakinan | 2 |
| `tools/lab/dataset_cctv.py`, `tools/lab/uji/test_dataset_cctv.py` (baru) | Dataset YOLO CCTV | 3 |
| `tools/lab/latih_yolox.py`, `tools/lab/uji/test_latih_yolox.py` (ubah) | `--bahan` | 4 |
| `tools/lab/kendaraan.py`, `tools/lab/uji/test_kendaraan.py` (baru); `rantai.py`, `lembar_bingkai.py`, ujinya, dan `uji_fpo` (ubah) | Tahap kendaraan (K39, ditambahkan sesudah Task 6) | 7b |
| `bukti/<tanggal>-pencari-plat-cctv*` | Hitungan dan laporan | 9 |

---

### Task 1: Penampakan per gambar

- [x] **Step 1: Uji merah**, ditambahkan di `tools/lab/uji/test_rantai.py`:

```python
def test_penampakan_tersimpan_dengan_nomor_gambar_dan_keyakinan_kotak(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10 + [False] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "k", simpan_penampakan=True)

    tampak = [json.loads(b) for b in (tmp_path / "k" / "penampakan.jsonl").read_text().splitlines()]
    assert [(t["video"], t["jalur"], t["kedatangan"], [x[0] for x in t["tampak"]]) for t in tampak] == [
        ("gerbang.avi", 0, 1, [0, 2, 4, 6, 8])]
    assert tampak[0]["tampak"][0][1:] == [60.0, 40.0, 100.0, 56.0]
    assert json.loads((tmp_path / "k" / "kedatangan.jsonl").read_text().splitlines()[0])["yakin_kotak"] == 0.9
    assert "B1234" not in (tmp_path / "k" / "penampakan.jsonl").read_text()
```

Run `npm run test:lab; echo "EXIT=$?"` → Expected: 1 gagal (`TypeError: ... simpan_penampakan`), `EXIT=1`.

- [x] **Step 2: Ubah `tools/lab/rantai.py`:**
  - Di `jalankan_video`, tiap penampakan diberi `"gambar": nomor`.
  - `jalankan_semua(..., sisi=None, simpan_penampakan=False)`. Kedatangan yang terlihat minimal dua kali diberi nomor menurut
    urutan `tiba`. Tiap baris kedatangan diberi `"yakin_kotak": round(float(np.mean([p["yakin_kotak"] for p in j])), 3)`.
    Bila `simpan_penampakan`, tiap jalur (termasuk yang terlihat sekali) ditulis ke `penampakan.jsonl` sebagai
    `{"video", "jalur" (urutan di video), "kedatangan" (nomor atau null), "tampak": [[gambar, x1, y1, x2, y2], ...]}` dengan
    koordinat dibulatkan satu desimal.
  - CLI `jalan`: `--ambang` (float; bila ada, mengganti `ambang_validasi` dari `mesin.json`) dan `--simpan-penampakan`.

Run → Expected: `218 passed`.

- [x] **Step 3: Commit.**

### Task 2: Urut keyakinan di lembar

- [x] **Step 1: Uji merah**, ditambahkan di `tools/lab/uji/test_lembar_rantai.py`:

```python
def test_pilih_baris_urut_keyakinan_kotak():
    semua = [{**kedatangan("a", n), "yakin_kotak": y} for n, y in ((1, 0.3), (2, 0.9), (3, 0.6))] + [
        {**kedatangan("b", 1), "yakin_kotak": 0.8}]

    pilih = lr.pilih_baris(semua, maks=3, urut="keyakinan")

    assert [(k["video"], k["nomor"]) for k in pilih] == [("a", 2), ("b", 1), ("a", 3)]
```

- [x] **Step 2:**
  - `pilih_baris(kedatangan, maks=MAKS_BARIS, urut="sha")`: bila `urut == "keyakinan"`, kembalikan
    `sorted(kedatangan, key=lambda k: (-k.get("yakin_kotak", 0.0), k["video"], k["nomor"]))[:maks]`;
  - `buat_lembar(..., urut="sha")` meneruskannya;
  - CLI `lembar --urut sha|keyakinan` (bawaan `sha`);
  - `lembar-rantai.json` mencatat `urut`.

  Run → Expected: `219 passed`. Commit.

### Task 3: Dataset CCTV

- [x] **Step 1: Uji merah** `tools/lab/uji/test_dataset_cctv.py`:

```python
"""Uji tools/lab/dataset_cctv.py: label jalur dari lembar owner, pilihan gambar (kotak tak berlabel ditutup), tempel plat buatan,
dan dataset YOLO dari video buatan dengan sisi validasi menurut SHA-256 video."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dataset_cctv as dc  # noqa: E402

V = "gerbang.avi"


def tampak_contoh():
    return [{"video": V, "jalur": 0, "kedatangan": 1, "tampak": [[0, 60, 40, 100, 56], [2, 60, 40, 100, 56], [4, 60, 40, 100, 56]]},
            {"video": V, "jalur": 1, "kedatangan": 2, "tampak": [[2, 10, 10, 30, 20], [4, 10, 10, 30, 20]]},
            {"video": V, "jalur": 2, "kedatangan": None, "tampak": [[4, 120, 70, 140, 80]]}]


def lembar_contoh():
    return {"baris": [{"nomor": 1, "video": V, "kedatangan": 1}, {"nomor": 2, "video": V, "kedatangan": 2}]}


def test_label_jalur_dari_lembar_dan_jawaban_owner():
    assert dc.label_jalur(tampak_contoh(), lembar_contoh(), bukan_plat={2}) == {(V, 0): "plat", (V, 1): "bukan"}


def test_pilih_gambar_plat_jadi_label_dan_kotak_tak_berlabel_ditutup():
    pilih = dc.pilih_gambar(tampak_contoh(), {(V, 0): "plat", (V, 1): "bukan"}, per_jalur=3)

    assert pilih == [(V, 0, [[60, 40, 100, 56]], []), (V, 2, [[60, 40, 100, 56]], []),
                     (V, 4, [[60, 40, 100, 56]], [[120, 70, 140, 80]])]


def test_tempel_plat_buatan_di_dalam_gambar():
    latar = np.full((360, 640, 3), 90, np.uint8)

    hasil, (x1, y1, x2, y2) = dc.tempel(latar, np.random.default_rng(0))

    assert 0 <= x1 < x2 <= 640 and 120 <= y1 < y2 <= 360 and (y2 - y1) >= 0.015 * 360 - 1
    assert not np.array_equal(hasil[y1:y2, x1:x2], latar[y1:y2, x1:x2])
    luar = np.ones(latar.shape[:2], bool)
    luar[y1:y2, x1:x2] = False
    assert np.array_equal(hasil[luar], latar[luar])  # di luar kotak tempelan tidak berubah


def test_bangun_dataset_yolo_dari_video_buatan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis = cv2.VideoWriter(str(folder / V), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 96))
    for _ in range(40):
        tulis.write(np.full((96, 160, 3), 90, np.uint8))
    tulis.release()
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": V, "sudut": "gerbang", "kategori": "siang"}]}))
    (tmp_path / "p.json").write_text(json.dumps({"uji": [], "latih": [V]}))
    (tmp_path / "rantai").mkdir()
    (tmp_path / "rantai" / "penampakan.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tampak_contoh()))
    pl = tmp_path / "pl"
    for s in ("train", "valid"):
        (pl / s / "images").mkdir(parents=True)
        (pl / s / "labels").mkdir(parents=True)
        cv2.imwrite(str(pl / s / "images" / f"x-{s}.jpg"), np.zeros((50, 80, 3), np.uint8))
        (pl / s / "labels" / f"x-{s}.txt").write_text("0 0.5 0.5 0.2 0.1\n")

    h = dc.bangun(tmp_path / "m.json", tmp_path / "p.json", tmp_path / "rantai", lembar_contoh(), {2}, folder, pl,
                  tmp_path / "ds", latar_per_video=2)

    sisi = "valid" if dc.sisi_validasi(V) else "train"
    label = sorted((tmp_path / "ds" / sisi / "labels").glob("gerbang-*.txt"))
    assert h[sisi]["gambar_cctv"] == 3 and h[sisi]["kotak_plat"] == 3 and h[sisi]["gambar_tempel"] == 2
    assert (tmp_path / "ds" / sisi / "labels" / "gerbang-000000.txt").read_text() == "0 0.500000 0.500000 0.250000 0.166667\n"
    assert len(label) == 5 and h["train"]["plat_lighting"] == 1 and h["valid"]["plat_lighting"] == 1
```

Run → Expected: `ModuleNotFoundError: No module named 'dataset_cctv'`.

- [x] **Step 2: Tulis `tools/lab/dataset_cctv.py`:**

```python
"""Dataset pencari plat CCTV Fase 1 (Rencana 19), format YOLO seperti plat-lighting, untuk tools/lab/latih_yolox.py.

- Label kotak: penampakan.jsonl (rantai.py --simpan-penampakan, video SISI LATIH) + lembar-rantai.json + jawaban owner (nomor
  baris bukan plat; baris lain di lembar = plat). Jalur di luar lembar tidak berlabel.
- Gambar: paling banyak PER_JALUR gambar per jalur berlabel, berjarak sama. Kotak plat menjadi label; kotak bukan plat menjadi
  latar (contoh negatif); kotak tak berlabel DITUTUP dengan buram kuat, supaya tidak menjadi contoh negatif yang salah.
- Gambar tempel: gambar sampel tanpa kotak sama sekali (pada ambang rantai), LATAR_PER_VIDEO per video, diberi 1-3 plat buatan
  (tools/lab/plat_buatan.py) setinggi TINGGI_PLAT dari tinggi gambar, di dua pertiga bawah gambar.
- Sisi validasi: video latih yang SHA-256 "valid/<berkas>"-nya berawal 0-3 (sekitar seperempat), ditambah valid plat-lighting.
  Sisi uji Fase 1 tidak pernah dibaca.
Keluaran berisi gambar berplat: tinggal di data/, agen tidak membukanya. Layar hanya hitungan.

  bangun: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/dataset_cctv.py bangun /kerja/data-asal/video-riset.json /kerja/data-asal/pembagian-video-fase1.json /kerja/data/keluaran/rantai-latih-fase1 /kerja/data/keluaran/lembar-latih-fase1/lembar-rantai.json /kerja/data/video/riset /kerja/data/keluaran/dataset/plat-lighting /kerja/data/keluaran/dataset/cctv-fase1 --bukan-plat <n,...>
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV)
import plat_buatan as pb  # noqa: E402
from deteksi import AKHIRAN  # noqa: E402
from lembar_rantai import nomor_baris  # noqa: E402
from rantai import daftar_video, fps_sah, langkah_sampel, pilih_berkas  # noqa: E402

PER_JALUR = 3
LATAR_PER_VIDEO = 6
TINGGI_PLAT = (0.015, 0.08)


def sisi_validasi(berkas):
    return hashlib.sha256(f"valid/{berkas}".encode()).hexdigest()[0] in "0123"


def label_jalur(tampak, lembar, bukan_plat):
    """(video, jalur) -> "plat" | "bukan" untuk jalur yang kedatangannya ada di lembar."""
    di_lembar = {(b["video"], b["kedatangan"]): ("bukan" if b["nomor"] in bukan_plat else "plat") for b in lembar["baris"]}
    return {(t["video"], t["jalur"]): di_lembar[(t["video"], t["kedatangan"])] for t in tampak
            if t["kedatangan"] is not None and (t["video"], t["kedatangan"]) in di_lembar}


def pilih_gambar(tampak, label, per_jalur=PER_JALUR):
    """[(video, nomor_gambar, [kotak plat], [kotak ditutup])], urut video lalu gambar."""
    per_gambar = {}
    for t in tampak:
        for g, *kotak in t["tampak"]:
            per_gambar.setdefault((t["video"], g), []).append(((t["video"], t["jalur"]), kotak))
    calon = set()
    for t in tampak:
        if (t["video"], t["jalur"]) in label:
            g = [x[0] for x in t["tampak"]]
            calon.update((t["video"], g[int(round(i))]) for i in np.linspace(0, len(g) - 1, min(per_jalur, len(g))))
    return [(v, g, [k for j, k in per_gambar[(v, g)] if label.get(j) == "plat"],
             [k for j, k in per_gambar[(v, g)] if j not in label]) for v, g in sorted(calon)]


def tutup(gambar, kotak):
    """Kotak tak berlabel dibuat buram kuat (tidak terbaca, tidak berbentuk plat)."""
    hasil = gambar.copy()
    for x1, y1, x2, y2 in kotak:
        a, b, c, d = max(0, int(x1)), max(0, int(y1)), min(gambar.shape[1], int(x2) + 1), min(gambar.shape[0], int(y2) + 1)
        if c > a and d > b:
            hasil[b:d, a:c] = cv2.blur(hasil[b:d, a:c], (max(3, (c - a) // 2 * 2 + 1), max(3, (d - b) // 2 * 2 + 1)))
    return hasil


def tempel(gambar, rng):
    """Satu plat buatan ditempel ke salinan gambar, di dua pertiga bawah. Kembali: (gambar, (x1, y1, x2, y2))."""
    t, l = gambar.shape[:2]
    jenis = "mobil" if rng.random() < 0.6 else "motor"
    warna = str(rng.choice(list(pb.PELUANG_WARNA), p=list(pb.PELUANG_WARNA.values())))
    plat = pb.plat(pb.teks_acak(rng), jenis, warna, rng, tinggi=96)
    tinggi = max(6, int(t * rng.uniform(*TINGGI_PLAT)))
    lebar = min(l - 2, max(8, int(tinggi * plat.shape[1] / plat.shape[0])))
    kecil = cv2.resize(plat, (lebar, tinggi), interpolation=cv2.INTER_AREA)
    x = int(rng.integers(0, l - lebar))
    y = int(rng.integers(t // 3, t - tinggi))
    hasil = gambar.copy()
    hasil[y:y + tinggi, x:x + lebar] = kecil
    return hasil, (x, y, x + lebar, y + tinggi)


def tulis(gambar, kotak, folder, nama):
    t, l = gambar.shape[:2]
    cv2.imwrite(str(folder / "images" / f"{nama}.jpg"), gambar)
    baris = [f"0 {(x1 + x2) / 2 / l:.6f} {(y1 + y2) / 2 / t:.6f} {(x2 - x1) / l:.6f} {(y2 - y1) / t:.6f}" for x1, y1, x2, y2 in kotak]
    (folder / "labels" / f"{nama}.txt").write_text("".join(b + "\n" for b in baris))


def bangun(manifes, pembagian, folder_rantai, lembar, bukan_plat, folder_video, folder_plat_lighting, keluar, benih=0,
           latar_per_video=LATAR_PER_VIDEO):
    """Kembali: hitungan per sisi (train/valid)."""
    tampak = [json.loads(b) for b in (Path(folder_rantai) / "penampakan.jsonl").read_text().splitlines() if b.strip()]
    pilihan = pilih_gambar(tampak, label_jalur(tampak, lembar, set(bukan_plat)))
    keluar = Path(keluar)
    for s in ("train", "valid"):
        for sub in ("images", "labels"):
            (keluar / s / sub).mkdir(parents=True, exist_ok=True)
    hitung = {s: {"gambar_cctv": 0, "kotak_plat": 0, "gambar_negatif": 0, "kotak_ditutup": 0, "gambar_tempel": 0,
                  "plat_lighting": 0} for s in ("train", "valid")}
    rng = np.random.default_rng(benih)
    terdeteksi = {}
    for t in tampak:
        terdeteksi.setdefault(t["video"], set()).update(x[0] for x in t["tampak"])
    for v in sorted(daftar_video(manifes, hanya=pilih_berkas(pembagian, "latih")), key=lambda x: x["berkas"]):
        berkas, s = v["berkas"], ("valid" if sisi_validasi(v["berkas"]) else "train")
        stem = Path(berkas).stem
        video = cv2.VideoCapture(str(Path(folder_video) / berkas))
        jumlah = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else 0
        for _, g, plat, ditutup in [p for p in pilihan if p[0] == berkas]:
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            tulis(tutup(gambar, ditutup), plat, keluar / s, f"{stem}-{g:06d}")
            h = hitung[s]
            h["gambar_cctv"] += 1
            h["kotak_plat"] += len(plat)
            h["gambar_negatif"] += int(not plat)
            h["kotak_ditutup"] += len(ditutup)
        langkah = langkah_sampel(fps_sah(video.get(cv2.CAP_PROP_FPS)))
        kosong = [g for g in range(0, jumlah, langkah) if g not in terdeteksi.get(berkas, set())]
        for g in [kosong[int(i)] for i in np.linspace(0, len(kosong) - 1, min(latar_per_video, len(kosong)))] if kosong else []:
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            kotak = []
            for _ in range(int(rng.integers(1, 4))):
                gambar, k = tempel(gambar, rng)
                kotak.append(k)
            tulis(gambar, kotak, keluar / s, f"{stem}-tempel-{g:06d}")
            hitung[s]["gambar_tempel"] += 1
        video.release()
    for s in ("train", "valid"):
        for gambar in sorted((Path(folder_plat_lighting) / s / "images").iterdir()):
            if gambar.suffix.lower() not in AKHIRAN:
                continue
            label = Path(folder_plat_lighting) / s / "labels" / f"{gambar.stem}.txt"
            shutil.copy(gambar, keluar / s / "images" / f"pl-{gambar.name}")
            if label.exists():
                shutil.copy(label, keluar / s / "labels" / f"pl-{gambar.stem}.txt")
            else:
                (keluar / s / "labels" / f"pl-{gambar.stem}.txt").write_text("")
            hitung[s]["plat_lighting"] += 1
    (keluar / "ringkasan.json").write_text(json.dumps(hitung, indent=1))
    return hitung


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Dataset pencari plat CCTV Fase 1 (Rencana 19).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    b = perintah.add_parser("bangun")
    for nama in ("manifes", "pembagian", "folder_rantai", "lembar", "folder_video", "folder_plat_lighting", "keluar"):
        b.add_argument(nama)
    b.add_argument("--bukan-plat", type=nomor_baris, default=[])
    b.add_argument("--benih", type=int, default=0)
    p = pengurai.parse_args(argumen)
    try:
        lembar = json.loads(Path(p.lembar).read_text())
        h = bangun(p.manifes, p.pembagian, p.folder_rantai, lembar, p.bukan_plat, p.folder_video, p.folder_plat_lighting,
                   p.keluar, p.benih)
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    for s, x in h.items():
        print(f"{s}: {x}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

Run → Expected: `223 passed` (219 + 4). Commit.

### Task 4: `--bahan` saat melatih

- [x] **Step 1: Uji merah**, ditambahkan di `tools/lab/uji/test_latih_yolox.py`:

```python
def test_rantai_latih_mencatat_bahan_dari_baris_perintah(tmp_path):
    ds = buat_dataset(tmp_path)
    unduhan, kunci = kunci_sementara(tmp_path)
    bahan = "dataset-plat-lighting,bobot-yolox,video-riset-youtube,plat-buatan"

    hasil = subprocess.run([sys.executable, str(SKRIP), "latih", "nano", "128", str(ds), str(unduhan), str(tmp_path / "mesin"),
                            "--zaman", "1", "--perangkat", "cpu", "--kunci", str(kunci), "--bahan", bahan],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    assert json.loads((tmp_path / "mesin" / "mesin.json").read_text())["bahan"] == bahan.split(",")
```

Expected merah: argparse menolak `--bahan` (keluar 2).

- [x] **Step 2:** di `tools/lab/latih_yolox.py`:
  - `latih(..., kunci=LOKASI_KUNCI, bahan=None)` menulis `"bahan": list(bahan or BAHAN)` ke `mesin.json`;
  - CLI `latih` mendapat `a.add_argument("--bahan", type=lambda t: [x for x in t.split(",") if x], default=None)`, yang
    diteruskan sebagai `bahan=p.bahan`.

  Expected `224 passed`. Commit.

### Task 5: Kandidat di sisi latih dan lembar latih

- [x] **Step 1:** Mesin tenang, lalu rantai di sisi latih, di latar dengan perekam proses:
  `rantai.py jalan ... /kerja/data/keluaran/rantai-latih-fase1 --pembagian ... --sisi latih --ambang 0.1 --simpan-penampakan`.
- [x] **Step 2:** `lembar_rantai.py lembar /kerja/data/keluaran/rantai-latih-fase1 /kerja/data/keluaran/lembar-latih-fase1
  --urut keyakinan`.
- [x] **Step 3: BERHENTI.** Owner memeriksa lembar latih: nomor baris bukan plat. Baris yang bukan "bukan plat" dihitung plat.
  Owner tidak mengetik nomor plat.

  *Hasil (16 Okt):* rantai di 39 video latih: 29.970 gambar sampel, 559 kedatangan (41 yakin), 424 jalur terlihat sekali. Lembar
  latih 120 baris (urut keyakinan): owner menyebut 14 plat; 106 sisanya bukan plat. Owner hanya memilah plat dan bukan plat,
  tidak memeriksa bacaannya, jadi hitungan benar dan salah dari `nilai` untuk lembar ini tidak bermakna dan tidak dilaporkan.
  Bersama jawabannya owner mengusulkan rantai yang mendahulukan kendaraan (K39), lihat Task 7b.

### Task 6: Dataset

- [x] **Step 1:** `lembar_rantai.py nilai`, untuk hitungan lembar latih.
- [x] **Step 2:** `dataset_cctv.py bangun ... --bukan-plat <jawaban owner>`, lalu catat hitungan per sisi.

  *Hasil (16 Okt), dari `ringkasan.json`:*

  | Sisi | Gambar CCTV | Kotak plat | Gambar tanpa plat | Kotak ditutup buram | Gambar tempel plat buatan | Plat-lighting |
  |---|---|---|---|---|---|---|
  | train | 269 | 44 | 225 | 151 | 202 | 393 |
  | valid | 64 | 3 | 61 | 10 | 24 | 84 |

  **Batas:** validasi hanya memuat 3 kotak plat CCTV. Pemilihan zaman di validasi praktis ditentukan plat-lighting dan
  gambar tanpa plat.

### Task 7: Latih ulang dan ekspor

- [x] **Step 1:** `nvidia-smi` dan mesin tenang. `latih_yolox.py latih nano 640 /kerja/data/keluaran/dataset/cctv-fase1
  /kerja/data/unduhan /kerja/data/keluaran/pencari-yolox-nano-640-cctv1 --bahan
  dataset-plat-lighting,bobot-yolox,video-riset-youtube,plat-buatan` di latar dengan log. Lama latihan dicatat.

  *Hasil (16 Okt), dari `mesin.json`:*
  - 864 gambar latih; zaman terbaik 67 dari 100; F1 validasi 0,9236 pada ambang 0,5; lama 68,4 menit (15.19–16.28).
  - F1 ini tidak bisa dibandingkan dengan pencari lama (0,917). Validasinya kini memuat plat-lighting, 61 gambar CCTV tanpa
    plat, dan hanya 3 kotak plat CCTV.
  - **Temuan kecil:** `mesin.json` memberi nama `pencari-yolox-nano-640`, sama dengan pencari lama, karena nama diturunkan
    dari jenis dan ukuran. Yang membedakan keduanya hanya folder dan SHA-256. Ini dicatat, tidak diperbaiki di rencana ini.
- [x] **Step 2:** `latih_yolox.py ekspor` di image tambahan (penjaga ONNX per satuan), dan `periksa-jualan` (harus `RISET-SAJA`).

  *Hasil:* deteksi ONNX sama dengan torch pada 20 dari 20 gambar. Selisih mentah: koordinat 1,93e-02 piksel, peluang
  3,01e-05. `periksa-jualan`: `RISET-SAJA`.

### Task 7b: Tahap kendaraan (K39, ditambahkan 16 Okt sesudah Task 6)

Usulan owner (K39): kendaraan, lalu tampak depan atau belakang, lalu plat di area kendaraan itu. Yang dipasang di sini adalah
langkah 1 dan 3: kotak plat diterima hanya bila tengahnya berada di dalam kotak kendaraan. Langkah 2 belum ada (lihat batas di
Task 9).

**Diukur sebelum task ini ditulis** (`data/alat-sementara/gerbang-kendaraan-19.py`, sisi latih saja, hanya hitungan): pencari
kendaraannya YOLOX-Tiny COCO terkunci (torch), dengan kelas mobil, motor, bus, truk, dan sepeda. Penampakan yang dipakai adalah
yang di tengah tiap kedatangan dari 120 baris lembar latih. Hasilnya:

| Ambang kendaraan | Plat lolos (dari 14) | Bukan plat lolos (dari 106) |
|---|---|---|
| 0,15 | 14 | 24 |
| 0,25 | 14 | 14 |
| 0,4 | 12 | 10 |

**Berkas:**
- Baru: `tools/lab/kendaraan.py` dan `tools/lab/uji/test_kendaraan.py`.
- Ubah: `tools/lab/rantai.py`, `tools/lab/lembar_bingkai.py`, dan uji keduanya.
- Ubah: `tools/lab/uji_fpo/test_rantai_sungguhan.py`.

- [x] **Step 1: Uji merah** `tools/lab/uji/test_kendaraan.py`:

```python
def keluaran(*baris):
    """Baris (cx, cy, w, h, objek, kelas_coco, peluang_kelas) -> larik (N, 85) seperti keluaran YOLOX COCO."""
    k = np.zeros((len(baris), 85), np.float32)
    for i, (cx, cy, w, h, objek, kelas, peluang) in enumerate(baris):
        k[i, :5] = cx, cy, w, h, objek
        k[i, 5 + kelas] = peluang
    return k


def test_urai_hanya_kelas_kendaraan_di_atas_ambang_dan_skala_dikembalikan():
    k = keluaran((100, 100, 40, 20, 0.9, 2, 0.9), (300, 100, 40, 80, 0.9, 0, 0.9), (200, 200, 40, 20, 0.9, 3, 0.2),
                 (400, 300, 60, 40, 0.8, 7, 0.9), (500, 300, 40, 40, 0.9, 1, 0.9))

    hasil = kd.urai(k, 0.5, 0.25)

    assert [(round(v[0]), round(v[1]), round(v[2]), round(v[3]), v[5]) for v in hasil] == [
        (160, 180, 240, 220, "mobil"), (740, 560, 860, 640, "truk")]


def test_kendaraan_pemuat_memakai_tengah_kotak_plat_dan_memilih_yang_terkecil():
    truk = (0, 0, 400, 300, 0.9, "truk")
    motor = (100, 100, 200, 250, 0.8, "motor")

    assert kd.kendaraan_pemuat((140, 200, 160, 210), [truk, motor]) == motor
    assert kd.kendaraan_pemuat((390, 290, 450, 320), [truk, motor]) is None  # sebagian di dalam, tengahnya di luar
    assert kd.kendaraan_pemuat((10, 10, 20, 20), []) is None


def test_saring_membuang_plat_di_luar_kendaraan_dan_menambah_jenis():
    plat = [(140, 200, 160, 210, 0.9), (500, 500, 540, 512, 0.8)]

    terima, buang = kd.saring(plat, [(100, 100, 200, 250, 0.8, "motor")])

    assert terima == [(140, 200, 160, 210, 0.9, "motor")] and buang == 1


def test_pencari_kendaraan_menolak_onnx_yang_berubah(tmp_path):
    (tmp_path / "mesin.onnx").write_bytes(b"bukan onnx")
    (tmp_path / "mesin-onnx.json").write_text(json.dumps({"sha256_onnx": "0" * 64, "ukuran": 640, "ambang": 0.25}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        kd.PencariKendaraan(tmp_path)


def test_ekspor_menolak_bobot_yang_bukan_coco_80_kelas(tmp_path):
    unduhan, kunci = kunci_sementara(tmp_path)  # bobot YOLOX 1 kelas yang dikunci sebagai yolox-nano-coco

    with pytest.raises(ModelDitolak, match="tidak termuat"):
        kd.ekspor("nano", unduhan, tmp_path, tmp_path / "kendaraan", ambang=0.25, kunci=kunci)
    assert not (tmp_path / "kendaraan" / "mesin.onnx").exists()
```

Ditambahkan di `tools/lab/uji/test_rantai.py`:

```python
def cari_dua(gambar):
    return [(*map(float, KOTAK), 0.9), (110.0, 70.0, 150.0, 86.0, 0.9)] if gambar[48, 80].mean() > 128 else []


def kendaraan_tiruan(gambar):
    return [(50.0, 30.0, 110.0, 66.0, 0.8, "motor")]


def test_tahap_kendaraan_membuang_plat_di_luar_kendaraan_dan_mencatat_jenisnya(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    kendaraan_tiruan.ambang = 0.25

    tanpa = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca_tiruan, 0.25, tmp_path / "tanpa")
    dengan = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca_tiruan, 0.25, tmp_path / "dengan",
                                   cari_kendaraan=kendaraan_tiruan)

    baris = [json.loads(b) for b in (tmp_path / "dengan" / "kedatangan.jsonl").read_text().splitlines()]
    assert tanpa["kedatangan"] == 2 and tanpa["tersaring_kendaraan"] == 0 and tanpa["aturan"]["ambang_kendaraan"] is None
    assert dengan["kedatangan"] == 1 and dengan["tersaring_kendaraan"] == 5 and dengan["aturan"]["ambang_kendaraan"] == 0.25
    assert baris[0]["kendaraan"] == "motor" and dengan["waktu_ms"]["kendaraan"]["n"] == 5
```

Ditambahkan di `tools/lab/uji/test_lembar_bingkai.py`:

```python
def test_lembar_dengan_kendaraan_kotak_biru_dan_plat_di_luar_kendaraan_tidak_digambar(tmp_path):
    video(tmp_path / "a.avi")

    def cari(gambar):
        return [(60.0, 40.0, 100.0, 56.0, 0.9), (120.0, 70.0, 150.0, 86.0, 0.9)]

    def kendaraan(gambar):
        return [(50.0, 30.0, 110.0, 66.0, 0.8, "motor")]

    lb.buat_lembar([{"berkas": "a.avi"}], tmp_path, cari, 0.25, tmp_path / "keluar", per_video=1, maks=1,
                   cari_kendaraan=kendaraan)

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert [(b["kotak"], b["kendaraan"], b["tersaring"]) for b in isi["baris"]] == [(1, 1, 1)]
    halaman = cv2.imread(str(tmp_path / "keluar" / "lembar-bingkai-1.png"))
    assert tuple(halaman[40 + 50, 50]) == lb.BIRU  # tepi kiri kotak kendaraan, di bawah pita nomor
```

Ditambahkan di `tools/lab/uji_fpo/test_rantai_sungguhan.py` (rantai dari baris perintah, uji rantai, aturan 4b). Di video
buatan hanya ada plat di latar abu-abu, tanpa kendaraan. Dengan `--ambang 0.01`, pencari plat pasti memberi kotak, dan dengan
`--kendaraan` semua kotak itu harus tersaring:

```python
KENDARAAN = KELUARAN / "kendaraan-yolox-coco"


@pytest.mark.skipif(not (KENDARAAN / "mesin.onnx").exists(), reason="pencari kendaraan belum diekspor (Rencana 19 Task 7b)")
def test_baris_perintah_rantai_dengan_tahap_kendaraan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis = cv2.VideoWriter(str(folder / "buatan-gerbang.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 10, (640, 360))
    plat = cv2.resize(plat_buatan(TEKS[0]), (160, 48))
    for _ in range(20):
        g = np.full((360, 640, 3), 90, np.uint8)
        g[200:248, 240:400] = plat
        tulis.write(g)
    tulis.release()
    (tmp_path / "manifes.json").write_text(json.dumps({"video": [
        {"berkas": "buatan-gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dasar = [sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI), str(BACA), str(UNDUHAN)]

    tanpa = subprocess.run(dasar + [str(tmp_path / "tanpa"), "--ambang", "0.01"], capture_output=True, text=True)
    dengan = subprocess.run(dasar + [str(tmp_path / "dengan"), "--ambang", "0.01", "--kendaraan", str(KENDARAAN)],
                            capture_output=True, text=True)

    assert tanpa.returncode == 0 and dengan.returncode == 0, (tanpa.stdout + tanpa.stderr + dengan.stdout + dengan.stderr)[-2000:]
    r_tanpa = json.loads((tmp_path / "tanpa" / "ringkasan.json").read_text())
    r = json.loads((tmp_path / "dengan" / "ringkasan.json").read_text())
    assert r_tanpa["kedatangan"] >= 1  # kontrol: tanpa tahap kendaraan kotak plat memang ada
    assert r["kedatangan"] == 0 and r["tersaring_kendaraan"] > 0
    assert r["aturan"]["ambang_kendaraan"] == json.loads((KENDARAAN / "mesin-onnx.json").read_text())["ambang"]
```

Ditambahkan di `tools/lab/uji_fpo/test_yolox_sungguhan.py`: ekspor bobot COCO sungguhan.

```python
def test_ekspor_kendaraan_coco_sungguhan_sama_dengan_torch(tmp_path):
    if not (UNDUHAN / "yolox-nano-coco" / "yolox_nano.pth").exists():
        pytest.skip("bobot awal belum diunduh (Rencana 13 Task 1)")
    (tmp_path / "gambar").mkdir()
    rng = np.random.default_rng(0)
    for i in range(3):
        cv2.imwrite(str(tmp_path / "gambar" / f"{i}.png"), rng.integers(0, 255, (360, 640, 3), dtype=np.uint8))

    meta = kd.ekspor("nano", UNDUHAN, tmp_path / "gambar", tmp_path / "kendaraan", ambang=0.25)

    assert meta["tujuan"] == "belajar" and meta["bahan"] == ["bobot-yolox"] and meta["ambang"] == 0.25
    assert meta["pemeriksaan"]["gambar"] == 3
    assert kd.PencariKendaraan(tmp_path / "kendaraan")(np.full((360, 640, 3), 90, np.uint8)) == []
```

Merah yang diharapkan: `ModuleNotFoundError: kendaraan` di gerbang biasa; `jalankan_semua() got an unexpected keyword argument
'cari_kendaraan'`; `buat_lembar() got an unexpected keyword argument 'cari_kendaraan'`. Di image tambahan: `ModuleNotFoundError`
dan `--kendaraan` ditolak argparse.

*Hasil (16 Okt):*
- **Merah di gerbang biasa, dilihat:** pengumpulan berhenti di `ModuleNotFoundError: No module named 'kendaraan'`. Dua uji lain
  dijalankan per berkas, dan keduanya gagal dengan `TypeError` yang diharapkan (`2 failed, 17 passed`).
- **Ditambahkan saat menulis kode:** satu uji rantai di image tambahan untuk `lembar_bingkai.py lembar --kendaraan`. Jalur baris
  perintahnya baru, dan tanpa uji ini jalur itu bisa mati senyap. Jadi uji image tambahan menjadi 22 + 3.

- [x] **Step 2: Tulis `tools/lab/kendaraan.py`:**
  - `KELAS = {2: "mobil", 3: "motor", 5: "bus", 7: "truk"}`. Sepeda tidak berplat, jadi tidak ikut; Step 4 mengukur apakah
    sepeda perlu ikut karena motor tertangkap sebagai sepeda.
  - `urai(keluaran, skala, ambang)`: skornya objek x peluang kelas terbesar, seperti YOLOX. Baris yang kelas terbesarnya bukan
    `KELAS`, atau skornya di bawah ambang, dibuang. Kotak dikembalikan ke piksel foto asli lalu melewati
    `pencari_yolox.nms`. Hasilnya `[(x1, y1, x2, y2, yakin, jenis)]`.
  - `kendaraan_pemuat(kotak, kendaraan)`: kendaraan terkecil yang memuat tengah kotak plat (tepi ikut), atau `None`.
  - `saring(kotak, kendaraan)`: `(kotak di dalam kendaraan, masing-masing ditambah jenisnya; jumlah yang dibuang)`.
  - `PencariKendaraan(folder, utas=None)`: SHA-256 `mesin.onnx` dicocokkan dengan `mesin-onnx.json` **sebelum** onnxruntime dimuat.
    `ukuran` dan `ambang` dibaca dari `mesin-onnx.json`. Kelas ini tidak memuat torch.
  - `ekspor(jenis, folder_unduhan, folder_gambar, keluar, ambang, kunci=LOKASI_KUNCI, ukuran=640, jumlah=20)`:
    1. Bobot `.pth` diverifikasi terhadap kunci, lalu dimuat ke YOLOX 80 kelas lewat `latih_yolox.muat_bobot_awal`
       (`weights_only`). Bila ada tensor yang dilewati, ekspor ditolak dengan `ModelDitolak("... tidak termuat ...")`,
       sebelum ada berkas yang ditulis.
    2. `torch.onnx.export` (opset 17), lalu keluaran mentah dibandingkan dengan `latih_yolox.selisih_mentah` dan
       `mentah_sama` pada paling banyak `jumlah` gambar. Bila beda, atau tidak ada gambar, `mesin.onnx` dihapus dan ekspor
       ditolak.
    3. `mesin-onnx.json` berisi: `nama`, `tujuan: "belajar"`, `bahan: ["bobot-yolox"]`, `jenis`, `ukuran`, `kelas`, `ambang`,
       `sha256_onnx`, `sha256_pth`, dan `pemeriksaan`.
    4. torch dan `latih_yolox` dimuat di dalam fungsi saja.
  - CLI `ekspor jenis folder_unduhan folder_gambar keluar --ambang <f>`. Layar hanya jenis galat dan hitungan.
- [x] **Step 3: Ubah `rantai.py` dan `lembar_bingkai.py`:**
  - **`jalankan_video(..., cari_kendaraan=None)`**:
    - kembaliannya kini `(jalur, waktu, tersaring)`;
    - bila ada kotak plat di atas ambang, kendaraan dicari dan kotak plat disaring dengan `saring`;
    - waktunya masuk `waktu["kendaraan"]`;
    - tiap penampakan mendapat `"kendaraan": jenis` (`None` tanpa tahap kendaraan).
  - **`jalankan_semua(..., cari_kendaraan=None)`**:
    - tiap kedatangan mendapat `"kendaraan"`, yaitu jenis terbanyak dari penampakannya;
    - ringkasan mendapat `aturan.ambang_kendaraan` (`getattr(cari_kendaraan, "ambang", None)`), `tersaring_kendaraan`, dan
      `per_video[].tersaring_kendaraan`.
  - **CLI `jalan --kendaraan <folder>`:** memuat `PencariKendaraan(folder, utas)`.
  - Uji lama `test_jalankan_video_sampel_lacak_dan_satu_potongan_per_jalur` membongkar tiga nilai.
  - **`lembar_bingkai.buat_lembar(..., cari_kendaraan=None)`**:
    - kotak kendaraan digambar `BIRU = (200, 0, 0)` lebih dulu;
    - kotak plat yang tersaring tidak digambar;
    - baris mendapat `"kendaraan"` (jumlah kendaraan) dan `"tersaring"`;
    - `lembar-bingkai.json` mencatat `ambang_kendaraan`.
  - **CLI `lembar --kendaraan <folder>`.**

  Run gerbang lab → Expected `231 passed` (224 + 7). *Hasil:* `231 passed` (`EXIT=0`).
- [x] **Step 4: Ekspor dan pilih di sisi latih.**
  1. Mesin tenang. `kendaraan.py ekspor nano ...` dan `ekspor tiny ...` di image tambahan, ke
     `data/keluaran/kendaraan-yolox-{nano,tiny}-coco`. Gambar pembanding: `dataset/plat-lighting/valid/images`.
  2. Ukur ulang lewat ONNX dengan skrip sekali pakai (`gerbang-kendaraan-19b.py`, hanya hitungan, sisi latih saja). Yang
     dibandingkan: nano dan tiny × ambang 0,15/0,25/0,4 × dengan dan tanpa sepeda. Hitungannya sama dengan pengukuran torch di
     atas: plat lolos (dari 14) dan bukan plat lolos (dari 106). Ditambah ms per gambar.
  3. Aturan memilih, ditetapkan sebelum melihat angkanya: semua 14 plat harus lolos. Di antara yang lolos, pilih yang paling
     sedikit meloloskan bukan plat; bila seri, pilih yang lebih cepat.
  4. Yang terpilih disalin ke `data/keluaran/kendaraan-yolox-coco`, dengan `ambang` yang terpilih (ekspor ulang dengan
     `--ambang`).
  5. `periksa-jualan` pada `mesin-onnx.json`-nya harus memberi `RISET-SAJA`.

  *Hasil (16 Okt):*
  - **Ekspor:** ONNX sama dengan torch pada 20 gambar. Selisih mentah nano: koordinat 2,37e-02 piksel, peluang 3,52e-05.
    Tiny: koordinat 5,62e-03 piksel, peluang 1,03e-05.
  - **Sisi latih**, 120 contoh terbaca (14 plat, 106 bukan plat):

    | Pencari | Ambang | Plat lolos (dari 14) | Bukan plat lolos (dari 106) |
    |---|---|---|---|
    | nano | 0,15 | 12 | 21 |
    | nano | 0,25 | 12 | 19 |
    | nano | 0,4 | 9 | 9 |
    | **tiny** | 0,15 | 14 | 24 |
    | **tiny** | **0,25** | **14** | **14** |
    | tiny | 0,4 | 12 | 10 |

  - **Tiny lewat ONNX sama persis dengan pengukuran torch** sebelum task ini ditulis.
  - **Sepeda:** menambahkan kelas sepeda tidak mengubah satu angka pun. `KELAS` tetap tanpa sepeda.
  - **Terpilih menurut aturan:** tiny pada ambang 0,25. Nano gugur karena kehilangan 2 plat.
  - **Kecepatan:** median nano 19,5 ms dan tiny 72,2 ms per gambar (2 utas). Angka ini **tercemar**, karena uji vitest sesi lain
    sedang berjalan. Ia tidak dipakai memilih, karena pilihannya tidak seri. Kecepatan diukur ulang saat mesin tenang di Rencana
    21.
  - `data/keluaran/kendaraan-yolox-coco` diekspor ulang dari tiny dengan `--ambang 0.25`. `periksa-jualan`: `RISET-SAJA`, begitu
    juga pencari plat baru.
- [x] **Step 5:** Uji image tambahan → Expected `25 passed` (22 + 3). Commit.

  *Hasil:* `25 passed`, tanpa yang dilewati (`EXIT=0`). Dijalankan sesudah uji vitest sesi lain selesai.
  - **Batas jujur:** ketiga uji baru di image tambahan tidak dilihat merah sebelum kode ditulis; yang dilihat merah hanya uji
    gerbang biasa.
  - **Daya bedanya ada di dalam uji itu sendiri.** Uji rantai menjalankan kontrol tanpa `--kendaraan`, yang harus punya
    kedatangan; jalan dengan `--kendaraan` harus nol kedatangan. Uji lembar bingkai menuntut `ambang_kendaraan` dari
    `mesin-onnx.json`, padahal tanpa sambungan nilainya `null`.

### Task 8: Ukur ulang di set uji

- [x] **Step 1:** Rantai di sisi uji dengan pencari baru **dan `--kendaraan /kerja/data/keluaran/kendaraan-yolox-coco`**
  (`rantai-uji-fase1-cctv1`). Ringkasan mencatat berapa kotak plat yang tersaring tahap kendaraan.

  *Hasil (16 Okt, 16.42–17.06), dari `ringkasan.json`:*

  | | Titik awal (Rencana 17) | Sesudah |
  |---|---|---|
  | Video, gambar sampel | 41, 48.068 | sama |
  | Ambang kotak plat | 0,25 | 0,5 (ambang validasi pencari baru) |
  | Kedatangan (yakin) | 416 (41) | 198 (22) |
  | Siang / campuran / malam / remang / tak jelas | 326 / 33 / 31 / 21 / 5 | 197 / 1 / 0 / 0 / 0 |
  | Kotak plat dibuang tahap kendaraan | – | 2.505 |

  - **Kecepatan (median, 2 utas):** cari 16,7 ms, kendaraan 69,0 ms (hanya gambar yang punya kotak plat), baca 14,4 ms.
  - Uji sesi lain menyala di 22 dari 142 rekaman proses, jadi angka kecepatan ini tidak dipakai.
- [x] **Step 2:** Dua lembar untuk owner:
  - lembar kedatangan (`--urut sha`, 120 baris);
  - lembar bingkai `--per-video 1 --kendaraan ...`, yang gambarnya sama dengan Rencana 17, sehingga bisa dibandingkan langsung.
    Kotak biru adalah kendaraan; kotak hijau adalah plat yang diterima.

  **Batas pembanding:** pencari plat baru dan tahap kendaraan berubah bersama. Lembar latih (Task 7b) menunjukkan bagian tahap
  kendaraan untuk pencari lama; di set uji yang dilaporkan adalah keduanya bersama.

  *Hasil:*
  - Lembar kedatangan: 120 baris dari 198, di 6 halaman.
  - Lembar bingkai: 41 bingkai di 11 halaman. Video dan nomor gambarnya sama dengan Rencana 17 pada 41 dari 41 (dicek dengan
    `banding-bingkai-19.mjs`).

  **Yang terlihat agen sebelum owner memeriksa** (hitungan saja; dicatat karena sebagian memakai label sisi uji):
  - Di 41 bingkai, kotak plat turun dari 13 ke 1. Tahap kendaraan hanya membuang 2 kotak. Kendaraan ditemukan di 29 bingkai.
  - Bingkai yang menurut jawaban owner Rencana 17 berisi plat adalah 2, 5, 12, 17, 38, dan 41. Kendaraan ditemukan di keenamnya.
    Tetapi kotak plat kini hanya ada di bingkai 38. Di bingkai 41, plat yang dulu ditemukan pencari lama kini tidak berkotak.
  - Kedatangan malam dan remang hilang semua. Di video uji malam, tahap kendaraan hanya membuang 11 kotak, jadi hilangnya
    terutama dari pencari plat pada ambang 0,5.
  - **Dugaan penyebab, belum terbukti:**
    1. Ambang 0,5 dipilih di validasi yang isinya terutama plat-lighting (plat dari dekat).
    2. Gambar CCTV "tanpa plat" di dataset bisa memuat plat yang tidak pernah ditemukan pencari lama. Plat seperti itu tidak
       ditutup buram, jadi pencari baru belajar bahwa plat kecil adalah latar.
  - **Agar set uji tidak dipakai memilih:** pembetulan berikutnya dipilih di sisi latih, dan alasan memilihnya ditulis.
    Pengamatan di atas hanya menjadi pemicu pemeriksaan.
- [x] **Step 3: BERHENTI.** Owner memeriksa kedua lembar.
- [x] **Step 4:** `nilai` keduanya, lalu `status-per-jenis` (berapa "yakin" yang bukan plat).

  *Hasil (16 Okt).* Jawaban owner dipecah dari rentang oleh `jawaban-19-uji.mjs`. Isinya hanya nomor baris; owner melampirkan satu
  gambar berplat, dan nomornya tidak disalin.
  - **Lembar kedatangan:**
    - tak terbaca 91 (motor 85, semuanya tak terbaca);
    - bukan plat 6;
    - dinilai 23: 14 benar-yakin, 6 benar-ragu, 1 salah-ragu, 2 salah-yakin;
    - 20 baris tidak disebut, jadi dihitung benar dan mobil sesuai petunjuk lembar;
    - "yakin" di lembar 19: 14 benar, 2 salah (parkiran), 1 bukan plat, 2 tak terbaca.
  - **Lembar bingkai:**
    - owner menyebut terlewat di 12 bingkai, juga untuk plat yang buram atau tak terbaca;
    - bingkai 38 benar;
    - sisanya tak jelas.
    - Dua hitungan disimpan: `nilai.json` (dinilai 13, terlewat 12) dan `nilai-ketat.json` (hanya plat terbaca seperti titik
      awal: dinilai 4, terlewat 3).
    - Owner tidak menyebut kendaraan yang terlewat.

### Task 9: Bukti, laporan, catatan

- [x] **Step 1:** Pemeriksa bukti dengan kontrol positif (larangan ditambah bacaan rantai baru), lalu salin hitungan.

  *Hasil:* `periksa-bukti-19.py`. Larangan 11.106 (bacaan rantai 629, nama video 177). Kontrol positif menemukan 1.371 dari
  minimal 1.367. Delapan berkas hitungan bersih, lalu disalin ke `bukti/`. Nilai lembar latih tidak disalin, karena hitungan
  benar dan salahnya tidak bermakna.
- [x] **Step 2:** Laporan `bukti/<tanggal>-pencari-plat-cctv.md`, berisi:
  - dataset (hitungan per sisi);
  - latihan (zaman, F1 validasi, lama);
  - titik awal lawan sesudah: bukan plat di lembar, "yakin" yang bukan plat, plat terlewat di bingkai yang sama;
  - batas.
- [x] **Step 3:** ROADMAP, `CLAUDE.md` §7 (`dataset_cctv`, penutupan kotak tak berlabel), gerbang penuh, commit. Lanjut ke
  Rencana 20.

  *Hasil:*
  - Gerbang penuh saat mesin tenang: Node 117 pass dan 0 fail; lab `231 passed`; uji image tambahan `25 passed` (Task 7b).
  - **Urutan diubah menurut angka:** Rencana 20 kini menangani plat yang terlewat, yaitu plat dicari di dalam potongan kendaraan
    (K39 langkah 3). Pembaca pindah ke Rencana 21. Spec Fase 1 bagian 6 dan ROADMAP mencatat alasannya.
