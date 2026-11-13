# Fase 1, Rencana 17: Titik awal rantai di set uji CCTV (K36) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.
> Dikerjakan mandiri (K37). Berhenti hanya di Task 5: dua lembar berplat diperiksa owner.

**Goal:** Mengukur mesin yang sekarang (YOLOX-Nano-640 + fpo-indo-1, mesin belajar) pada sisi uji video CCTV Fase 1 (Rencana 16),
sebagai titik awal Fase 1. Ukurannya per kedatangan (benar-yakin, ragu, salah-yakin) dan **plat yang terlewat** (lembar bingkai),
per kelompok.

**Architecture:**
- **`tools/lab/rantai.py` diubah:** sudut `parkiran` ikut, dan pilihan `--pembagian` dengan `--sisi` membatasi video ke satu
  sisi `data-asal/pembagian-video-fase1.json`.
- **`tools/lab/lembar_bingkai.py` (baru):**
  - empat gambar per video pada jarak yang sama;
  - kotak temuan pencari digambar hijau;
  - owner menyebut nomor bingkai yang memuat plat terbaca tanpa kotak (terlewat) atau yang terlalu buram (tak jelas);
  - penilaian per kelompok.
- **Lembar kedatangan** memakai `tools/lab/lembar_rantai.py` (Rencana 14) apa adanya.

**Tech Stack:** Python di lab (numpy, cv2, onnxruntime), image tambahan untuk rantai (pembaca fpo-indo-1).

---

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/rantai.py`, `tools/lab/uji/test_rantai.py` (ubah) | Sudut parkiran; pilih video dari pembagian | 1 |
| `tools/lab/lembar_bingkai.py`, `tools/lab/uji/test_lembar_bingkai.py` (baru) | Lembar bingkai dan penilaiannya | 2 |
| `tools/lab/uji_fpo/test_rantai_sungguhan.py` (ubah) | CLI rantai dengan pembagian dan CLI lembar bingkai, model sungguhan | 3 |
| `bukti/<tanggal>-titik-awal-cctv*.json`, laporan | Hitungan saja | 6 |

---

### Task 1: Rantai memilih video dari pembagian

- [x] **Step 1: Uji merah.** Tambahkan di `tools/lab/uji/test_rantai.py`:

```python
def test_daftar_video_parkiran_ikut_dan_dibatasi_pembagian(tmp_path):
    (tmp_path / "m.json").write_text(json.dumps({"video": [
        {"berkas": "a.mp4", "sudut": "gerbang"}, {"berkas": "b.mp4", "sudut": "parkiran"},
        {"berkas": "c.mp4", "sudut": "kamera-diam-lain"}, {"berkas": "d.mp4", "sudut": "dasbor"}]}))

    assert [v["berkas"] for v in rantai.daftar_video(tmp_path / "m.json")] == ["a.mp4", "b.mp4", "c.mp4"]
    assert [v["berkas"] for v in rantai.daftar_video(tmp_path / "m.json", hanya={"a.mp4", "b.mp4", "d.mp4"})] == ["a.mp4", "b.mp4"]


def test_pilih_berkas_dari_pembagian_satu_sisi(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({"uji": ["a.mp4"], "latih": ["b.mp4"]}))

    assert rantai.pilih_berkas(tmp_path / "p.json", "uji") == {"a.mp4"}
    assert rantai.pilih_berkas(tmp_path / "p.json", "latih") == {"b.mp4"}
    with pytest.raises(ValueError, match="sisi"):
        rantai.pilih_berkas(tmp_path / "p.json", "semua")
```

(`import pytest` ditambahkan di kepala berkas uji.) Run `npm run test:lab; echo "EXIT=$?"` → Expected: 2 gagal
(`TypeError` untuk `hanya`, `AttributeError` untuk `pilih_berkas`), `EXIT=1`.

- [x] **Step 2: Ubah `tools/lab/rantai.py`.**

```python
SUDUT = ("gerbang", "parkiran", "kamera-diam-lain")


def daftar_video(manifes, sudut=SUDUT, hanya=None):
    isi = json.loads(Path(manifes).read_text(encoding="utf-8"))
    return [v for v in isi["video"] if v.get("sudut") in sudut and (hanya is None or v["berkas"] in hanya)]


def pilih_berkas(pembagian, sisi):
    """Berkas video satu sisi dari pembagian-video-fase1.json (tools/bagi-video.mjs)."""
    if sisi not in ("uji", "latih"):
        raise ValueError(f"sisi harus uji atau latih, bukan {sisi}")
    return set(json.loads(Path(pembagian).read_text(encoding="utf-8"))[sisi])
```

Lalu:
- `jalankan_semua(manifes, folder_video, cari, baca, ambang, keluar, hanya=None)` memakai `daftar_video(manifes, hanya=hanya)`
  dan menulis `"sisi"` ke ringkasan (`None` bila semua);
- CLI `jalan` mendapat `--pembagian` (bawaan tidak ada) dan `--sisi` (`uji` atau `latih`, bawaan `uji`), lalu meneruskan
  `hanya=pilih_berkas(p.pembagian, p.sisi) if p.pembagian else None`;
- docstring kepala menyebut pilihan itu.

Run → Expected: `205 passed` (203 + 2), `EXIT=0`.

- [x] **Step 3: Commit** dengan alasan (set uji Fase 1 per video; parkiran K36) dan angka gerbang.

### Task 2: Lembar bingkai

- [x] **Step 1: Uji merah** `tools/lab/uji/test_lembar_bingkai.py`:

```python
"""Uji tools/lab/lembar_bingkai.py: titik ambil tetap, kotak hijau, lembar dari video buatan dengan pencari tiruan (kotak di
bawah ambang dibuang), penilaian dari nomor bingkai, dan CLI yang hanya mencetak jenis galat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_bingkai as lb  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_bingkai.py"


def test_titik_ambil_berjarak_sama_dan_tidak_di_ujung():
    assert lb.titik_ambil(100, 4) == [12, 37, 62, 87]
    assert lb.titik_ambil(0, 4) == []


def test_gambar_kotak_hijau_tanpa_mengubah_asli():
    asli = np.zeros((100, 200, 3), np.uint8)

    hasil = lb.gambar_kotak(asli, [(10, 10, 50, 40, 0.9)])

    assert tuple(hasil[10, 30]) == lb.HIJAU and not asli.any()


def video(jalur, n=40):
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 96))
    for _ in range(n):
        tulis.write(np.full((96, 160, 3), 90, np.uint8))
    tulis.release()


def cari_tiruan(gambar):
    return [(60.0, 40.0, 100.0, 56.0, 0.9), (10.0, 10.0, 30.0, 20.0, 0.1)]


def test_buat_lembar_dari_video_buatan(tmp_path):
    for nama in ("a.avi", "b.avi"):
        video(tmp_path / nama)
    daftar = [{"berkas": "b.avi", "kategori": "malam", "sudut": "parkiran"}, {"berkas": "a.avi", "kategori": "siang", "sudut": "gerbang"}]

    r = lb.buat_lembar(daftar, tmp_path, cari_tiruan, 0.25, tmp_path / "keluar", per_video=2, maks=3)

    isi = json.loads((tmp_path / "keluar" / "lembar-bingkai.json").read_text())
    assert r == {"video": 2, "bingkai": 3, "halaman": 1}
    assert [(b["video"], b["gambar"], b["kotak"]) for b in isi["baris"]] == [("a.avi", 10, 1), ("a.avi", 30, 1), ("b.avi", 10, 1)]
    assert (tmp_path / "keluar" / "lembar-bingkai-1.png").exists()


def lembar_(baris):
    return {"baris": [{"nomor": i, **b} for i, b in enumerate(baris, 1)]}


def test_nilai_dari_nomor_bingkai_dan_penolakan():
    lembar = lembar_([{"sudut": "gerbang", "kategori": "siang"}] * 3 + [{"sudut": "parkiran", "kategori": "malam"}])

    h = lb.nilai(lembar, terlewat=[1, 4], tak_jelas=[2])

    assert (h["bingkai"], h["tak_jelas"]) == (4, 1)
    assert (h["kelompok"]["semua"]["dinilai"], h["kelompok"]["semua"]["ada_terlewat"]) == (3, 2)
    assert h["kelompok"]["gerbang-siang"] == {**h["kelompok"]["gerbang-siang"], "dinilai": 2, "ada_terlewat": 1}
    with pytest.raises(ValueError, match="tidak ada"):
        lb.nilai(lembar, terlewat=[9])
    with pytest.raises(ValueError, match="sekaligus"):
        lb.nilai(lembar, terlewat=[1], tak_jelas=[1])


def test_cli_nilai_dan_lembar_tanpa_model_hanya_jenis_galat(tmp_path):
    (tmp_path / "l.json").write_text(json.dumps(lembar_([{"sudut": "gerbang", "kategori": "siang"}] * 2)))
    a = subprocess.run([sys.executable, str(SKRIP), "nilai", str(tmp_path / "l.json"), str(tmp_path / "n.json"), "--terlewat", "2"],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, str(SKRIP), "lembar", str(tmp_path / "m.json"), str(tmp_path), str(tmp_path / "p.json"),
                        str(tmp_path / "pencari-rahasia"), str(tmp_path / "keluar")], capture_output=True, text=True)

    assert a.returncode == 0, a.stdout + a.stderr
    assert json.loads((tmp_path / "n.json").read_text())["kelompok"]["semua"]["ada_terlewat"] == 1
    assert b.returncode == 1 and "pencari-rahasia" not in b.stdout + b.stderr
```

Run `npm run test:lab; echo "EXIT=$?"` → Expected: galat koleksi `ModuleNotFoundError: No module named 'lembar_bingkai'`,
`EXIT` bukan 0.

- [x] **Step 2: Tulis `tools/lab/lembar_bingkai.py`.**

```python
"""Lembar bingkai untuk diperiksa OWNER (Rencana 17; spec Fase 1 bagian 3): mengukur plat yang terlewat.

Dari tiap video diambil PER_VIDEO gambar pada jarak waktu yang sama (tetap, bukan acak), sampai MAKS gambar. Kotak yang ditemukan
pencari plat (keyakinan minimal ambang validasinya) digambar hijau. Owner menyebut nomor bingkai yang memuat plat yang bisa ia baca
tetapi TIDAK berkotak hijau (terlewat), dan nomor bingkai yang terlalu buram untuk dinilai (tak jelas). Lembar memuat plat yang
terbaca: agen TIDAK PERNAH membukanya (CLAUDE.md §7). Layar hanya hitungan.

  lembar: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_bingkai.py lembar /kerja/data-asal/video-riset.json /kerja/data/video/riset /kerja/data-asal/pembagian-video-fase1.json /kerja/data/keluaran/pencari-yolox-nano-640 /kerja/data/keluaran/lembar-bingkai
  nilai:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_bingkai.py nilai /kerja/data/keluaran/lembar-bingkai/lembar-bingkai.json /kerja/data/keluaran/lembar-bingkai/nilai.json --terlewat <n,...> --tak-jelas <n,...>
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import wilson  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from bagi_set_uji import SEDIKIT  # noqa: E402
from lembar_rantai import nomor_baris  # noqa: E402
from model_terkunci import ModelDitolak  # noqa: E402
from rantai import daftar_video, pilih_berkas  # noqa: E402

PER_VIDEO = 4
MAKS = 60
LEBAR = 960  # lebar bingkai di lembar; tidak diperbesar, supaya plat yang terbaca di video tetap terbaca di lembar
PER_HALAMAN = 4
HIJAU = (0, 200, 0)


def titik_ambil(jumlah_gambar, per_video=PER_VIDEO):
    """Nomor gambar pada jarak yang sama, tidak di ujung video."""
    return [int((i + 0.5) * jumlah_gambar / per_video) for i in range(per_video)] if jumlah_gambar > 0 else []


def gambar_kotak(gambar, kotak):
    """Salinan gambar dengan kotak hijau untuk tiap kotak (x1, y1, x2, y2, ...)."""
    hasil = gambar.copy()
    tebal = max(2, gambar.shape[1] // 400)
    for k in kotak:
        cv2.rectangle(hasil, (int(k[0]), int(k[1])), (int(k[2]), int(k[3])), HIJAU, tebal)
    return hasil


def kartu(nomor, gambar):
    """Bingkai selebar paling banyak LEBAR (diperkecil bila lebih), dengan nomor di pita atas."""
    skala = min(1.0, LEBAR / gambar.shape[1])
    kecil = cv2.resize(gambar, (max(1, round(gambar.shape[1] * skala)), max(1, round(gambar.shape[0] * skala))),
                       interpolation=cv2.INTER_AREA)
    kanvas = np.full((kecil.shape[0] + 40, LEBAR, 3), 255, np.uint8)
    kanvas[40:, :kecil.shape[1]] = kecil
    cv2.putText(kanvas, f"bingkai {nomor}", (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    return kanvas


def buat_lembar(daftar, folder_video, cari, ambang, keluar, per_video=PER_VIDEO, maks=MAKS):
    """daftar: video dari manifes (berkas, kategori, sudut), diurutkan menurut nama berkas. Kembali: hitungan saja."""
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    kartu_, baris = [], []
    for v in sorted(daftar, key=lambda x: x["berkas"]):
        if len(baris) >= maks:
            break
        video = cv2.VideoCapture(str(Path(folder_video) / v["berkas"]))
        jumlah = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else 0
        for g in titik_ambil(jumlah, per_video):
            if len(baris) >= maks:
                break
            video.set(cv2.CAP_PROP_POS_FRAMES, g)
            ada, gambar = video.read()
            if not ada:
                continue
            kotak = [k for k in cari(gambar) if k[4] >= ambang]
            nomor = len(baris) + 1
            kartu_.append(kartu(nomor, gambar_kotak(gambar, kotak)))
            baris.append({"nomor": nomor, "video": v["berkas"], "gambar": g, "kotak": len(kotak),
                          "kategori": v.get("kategori", ""), "sudut": v.get("sudut", "")})
        video.release()
    halaman = []
    for awal in range(0, len(kartu_), PER_HALAMAN):
        nama = f"lembar-bingkai-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(kartu_[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    (keluar / "lembar-bingkai.json").write_text(json.dumps({"per_video": per_video, "maks": maks, "ambang": ambang,
                                                           "halaman": halaman, "baris": baris}, indent=1))
    return {"video": len({b["video"] for b in baris}), "bingkai": len(baris), "halaman": len(halaman)}


def nilai(lembar, terlewat=(), tak_jelas=()):
    """Hitungan per kelompok (sudut-kategori) dari jawaban owner (nomor bingkai per jenis)."""
    semua = {b["nomor"]: b for b in lembar["baris"]}
    sebut = {"terlewat": set(terlewat), "tak_jelas": set(tak_jelas)}
    for nama, nomor in sebut.items():
        asing = nomor - set(semua)
        if asing:
            raise ValueError(f"nomor bingkai {nama} tidak ada di lembar: {sorted(asing)}")
    dua = sebut["terlewat"] & sebut["tak_jelas"]
    if dua:
        raise ValueError(f"bingkai {sorted(dua)} disebut terlewat dan tak jelas sekaligus")
    hasil = {"bingkai": len(semua), "tak_jelas": len(sebut["tak_jelas"]), "kelompok": {}}
    for nomor, b in sorted(semua.items()):
        if nomor in sebut["tak_jelas"]:
            continue
        for k in ("semua", f"{b['sudut']}-{b['kategori']}"):
            r = hasil["kelompok"].setdefault(k, {"dinilai": 0, "ada_terlewat": 0})
            r["dinilai"] += 1
            r["ada_terlewat"] += int(nomor in sebut["terlewat"])
    for r in hasil["kelompok"].values():
        rentang = wilson(r["ada_terlewat"], r["dinilai"])
        r["rentang_95_ada_terlewat"] = [round(x, 3) for x in rentang] if rentang else None
        r["terlalu_sedikit"] = r["dinilai"] < SEDIKIT
    return hasil


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Lembar bingkai untuk owner: plat yang terlewat (Rencana 17).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("lembar")
    for nama in ("manifes", "folder_video", "pembagian", "folder_pencari", "keluar"):
        a.add_argument(nama)
    a.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    a.add_argument("--per-video", type=int, default=PER_VIDEO)
    a.add_argument("--maks", type=int, default=MAKS)
    b = perintah.add_parser("nilai")
    b.add_argument("lembar")
    b.add_argument("keluar")
    b.add_argument("--terlewat", type=nomor_baris, default=[])
    b.add_argument("--tak-jelas", type=nomor_baris, default=[])
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "lembar":
            from pencari_yolox import PencariYolox

            cari = PencariYolox(p.folder_pencari)
            ambang = json.loads((Path(p.folder_pencari) / "mesin.json").read_text())["ambang_validasi"]
            daftar = daftar_video(p.manifes, hanya=pilih_berkas(p.pembagian, p.sisi))
            r = buat_lembar(daftar, p.folder_video, cari, ambang, p.keluar, p.per_video, p.maks)
            print(f"{r['video']} video, {r['bingkai']} bingkai di {r['halaman']} lembar. Lembar ini memuat plat yang terbaca: "
                  "agen tidak membukanya.")
        else:
            h = nilai(json.loads(Path(p.lembar).read_text()), p.terlewat, p.tak_jelas)
            Path(p.keluar).write_text(json.dumps(h, indent=1))
            print(f"{h['bingkai']} bingkai: tak jelas {h['tak_jelas']}")
            for k, r in sorted(h["kelompok"].items()):
                print(f"{k:<28} dinilai {r['dinilai']}: ada plat terlewat {r['ada_terlewat']} (rentang 95% "
                      f"{r['rentang_95_ada_terlewat']}{', terlalu sedikit' if r['terlalu_sedikit'] else ''})")
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except ValueError as galat:
        print(f"GAGAL: {galat}" if "bingkai" in str(galat) else f"GAGAL: {type(galat).__name__}")
        return 1
    except (OSError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

Run → Expected: `210 passed` (205 + 5), `EXIT=0`.

- [x] **Step 3: Commit** dengan alasan (plat terlewat belum terukur di Rencana 14; owner hanya menyebut nomor bingkai) dan angka
gerbang.

### Task 3: Model sungguhan (image tambahan)

- [x] **Step 1:** Tambahkan di `tools/lab/uji_fpo/test_rantai_sungguhan.py`:
  - CLI rantai `--pembagian` dengan `--sisi uji`, di mana hanya video buatan di sisi uji yang dijalankan (`ringkasan["video"] == 1`
    dari manifes berisi dua video);
  - CLI lembar bingkai dengan YOLOX-Nano-640 pada video buatan (`EXIT=0`; berkas lembar dan json ada; layar tanpa nama video).

  Lihat merah dulu, karena `--pembagian` belum diteruskan bila Task 1 Step 2 belum lengkap, lalu hijau. Expected `21 passed`.
- [x] **Step 2: Commit.**

### Task 4: Jalankan

- [x] **Step 1:** Pastikan mesin tenang (`CLAUDE.md` §7).
- [x] **Step 2: Rantai di sisi uji** (di latar, dengan perekam proses seperti Rencana 14), keluaran
  `data/keluaran/rantai-uji-fase1/`.
- [x] **Step 3: Lembar kedatangan:**
  `lembar_rantai.py lembar /kerja/data/keluaran/rantai-uji-fase1 /kerja/data/keluaran/lembar-uji-fase1`.
- [x] **Step 4: Lembar bingkai:** `lembar_bingkai.py lembar ...` ke `data/keluaran/lembar-bingkai-fase1`, paling banyak 60
  bingkai.

### Task 5: Owner memeriksa dua lembar

- [x] **Step 1: BERHENTI.** Sebut letak kedua lembar. Lembar kedatangan dijawab dengan nomor baris untuk salah, tak terbaca, bukan
  plat, dan motor. Lembar bingkai dijawab dengan nomor bingkai untuk terlewat dan tak jelas. Tanpa nomor plat.
- [x] **Step 2:** `lembar_rantai.py nilai` dan `lembar_bingkai.py nilai` dengan jawaban owner.

### Task 6: Bukti dan laporan

- [x] **Step 1:** Pemeriksa bukti dengan kontrol positif, yang larangannya ditambah bacaan rantai baru, lalu salin `ringkasan.json`
  dan kedua `nilai.json`.
- [x] **Step 2:** Laporan `bukti/<tanggal>-titik-awal-cctv.md`, berisi:
  - angka per kelompok;
  - plat terlewat;
  - salah-yakin;
  - kecepatan;
  - perbandingan dengan Rencana 14;
  - batas.
- [x] **Step 3:** ROADMAP dan `CLAUDE.md` §7 (lembar bingkai), gerbang penuh, commit. Lanjut ke Rencana 18 (K37).
