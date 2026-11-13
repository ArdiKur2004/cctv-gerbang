"""Uji rantai utuh dengan model sungguhan di image lab tambahan (di luar gerbang biasa): fpo-indo-1 ONNX memberi bacaan beserta
keyakinannya, dan baris perintah rantai.py jalan berjalan dari manifes sampai ringkasan dengan YOLOX-Nano-640 dan fpo-indo-1 pada
video buatan, dengan layar tanpa nama berkas. Baris perintah baca_gambar.py (Rencana 24) diuji dengan cara yang sama.

  powershell -NoProfile -File tools\\lab.ps1 -Fpo python -m pytest /kerja/tools/lab/uji_fpo -q -s -p no:cacheprovider
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

AKAR = Path(__file__).resolve().parents[3]
KELUARAN = AKAR / "data" / "keluaran"
UNDUHAN = AKAR / "data" / "unduhan"
for folder in ("tools/lab", "tools/lab/uji", "tools/lab/uji_fpo"):
    sys.path.insert(0, str(AKAR / folder))
import onnx_fpo as of  # noqa: E402
from test_percobaan_fpo import TEKS, plat_buatan  # noqa: E402

BACA = KELUARAN / "fpo-indo-1"
CARI = KELUARAN / "pencari-yolox-nano-640"
SKRIP = AKAR / "tools" / "lab" / "rantai.py"
pytestmark = pytest.mark.skipif(not ((BACA / "mesin.onnx").exists() and (CARI / "mesin.onnx").exists()),
                                reason="fpo-indo-1 atau pencari-yolox-nano-640 belum ada (Rencana 11, 13)")


def test_dengan_yakin_sama_dengan_bacaan_biasa_dan_yakin_di_antara_nol_dan_satu():
    pembaca = of.PembacaOnnxMesin(BACA, UNDUHAN, utas=2)

    for t in TEKS:
        gambar = plat_buatan(t)
        teks, yakin = pembaca.dengan_yakin(gambar)
        assert teks == pembaca(gambar) and 0.0 < yakin <= 1.0


def test_baris_perintah_rantai_dengan_model_sungguhan(tmp_path):
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

    hasil = subprocess.run([sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI),
                            str(BACA), str(UNDUHAN), str(tmp_path / "keluar")], capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    assert "buatan-gerbang" not in layar
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    ambang = json.loads((CARI / "mesin.json").read_text())["ambang_validasi"]
    assert r["video"] == 1 and r["gambar_sampel"] == 10 and r["aturan"]["ambang_kotak"] == ambang


BINGKAI = AKAR / "tools" / "lab" / "lembar_bingkai.py"


def dua_video_dan_pembagian(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    for nama in ("buatan-uji.avi", "buatan-latih.avi"):
        tulis = cv2.VideoWriter(str(folder / nama), cv2.VideoWriter_fourcc(*"MJPG"), 10, (640, 360))
        for _ in range(10):
            tulis.write(np.full((360, 640, 3), 90, np.uint8))
        tulis.release()
    (tmp_path / "manifes.json").write_text(json.dumps({"video": [
        {"berkas": "buatan-uji.avi", "sudut": "parkiran", "kategori": "malam"},
        {"berkas": "buatan-latih.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    (tmp_path / "pembagian.json").write_text(json.dumps({"uji": ["buatan-uji.avi"], "latih": ["buatan-latih.avi"]}))
    return folder


def test_cli_rantai_dengan_pembagian_hanya_sisi_uji(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)
    dasar = [sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI), str(BACA), str(UNDUHAN)]

    dibagi = subprocess.run(dasar + [str(tmp_path / "uji"), "--pembagian", str(tmp_path / "pembagian.json"), "--sisi", "uji"],
                            capture_output=True, text=True)
    semua = subprocess.run(dasar + [str(tmp_path / "semua")], capture_output=True, text=True)

    assert dibagi.returncode == 0 and semua.returncode == 0, (dibagi.stdout + dibagi.stderr + semua.stdout + semua.stderr)[-2000:]
    r = json.loads((tmp_path / "uji" / "ringkasan.json").read_text())
    assert r["video"] == 1 and r["sisi"] == "uji" and r["per_video"][0]["sudut"] == "parkiran"
    # Kontrol: tanpa pembagian kedua video berjalan, jadi uji di atas memang menguji pembatasannya.
    assert json.loads((tmp_path / "semua" / "ringkasan.json").read_text())["video"] == 2


def test_cli_lembar_bingkai_dengan_pencari_sungguhan(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    hasil = subprocess.run([sys.executable, str(BINGKAI), "lembar", str(tmp_path / "manifes.json"), str(folder),
                            str(tmp_path / "pembagian.json"), str(CARI), str(tmp_path / "bingkai")], capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar[-2000:]
    assert "buatan" not in layar
    isi = json.loads((tmp_path / "bingkai" / "lembar-bingkai.json").read_text())
    assert [b["gambar"] for b in isi["baris"]] == [1, 3, 6, 8] and {b["video"] for b in isi["baris"]} == {"buatan-uji.avi"}
    assert (tmp_path / "bingkai" / "lembar-bingkai-1.png").exists()


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


@pytest.mark.skipif(not (KENDARAAN / "mesin.onnx").exists(), reason="pencari kendaraan belum diekspor (Rencana 19 Task 7b)")
def test_cli_lembar_bingkai_dengan_tahap_kendaraan(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    hasil = subprocess.run([sys.executable, str(BINGKAI), "lembar", str(tmp_path / "manifes.json"), str(folder),
                            str(tmp_path / "pembagian.json"), str(CARI), str(tmp_path / "bingkai"), "--kendaraan", str(KENDARAAN)],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    isi = json.loads((tmp_path / "bingkai" / "lembar-bingkai.json").read_text())
    assert isi["ambang_kendaraan"] == json.loads((KENDARAAN / "mesin-onnx.json").read_text())["ambang"]
    assert all("kendaraan" in b and "tersaring" in b for b in isi["baris"]) and len(isi["baris"]) == 4


@pytest.mark.skipif(not (KENDARAAN / "mesin.onnx").exists(), reason="pencari kendaraan belum diekspor (Rencana 19 Task 7b)")
def test_baris_perintah_rantai_cara_potong(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI), str(BACA),
                            str(UNDUHAN), str(tmp_path / "keluar"), "--kendaraan", str(KENDARAAN), "--cara", "potong"],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    assert r["aturan"]["cara_kendaraan"] == "potong" and r["video"] == 2


LEMBAR_KENDARAAN = AKAR / "tools" / "lab" / "lembar_kendaraan.py"
CARI_BARU = KELUARAN / "pencari-yolox-nano-640-cctv1"


@pytest.mark.skipif(not ((KENDARAAN / "mesin.onnx").exists() and (CARI_BARU / "mesin.onnx").exists()),
                    reason="pencari kendaraan atau pencari plat baru belum diekspor (Rencana 19)")
def test_cli_lembar_kendaraan_dan_banding_dengan_model_sungguhan(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    lembar = subprocess.run([sys.executable, str(LEMBAR_KENDARAAN), "lembar", str(tmp_path / "manifes.json"), str(folder),
                             str(tmp_path / "pembagian.json"), str(KENDARAAN), str(tmp_path / "lk")], capture_output=True, text=True)
    banding = subprocess.run([sys.executable, str(LEMBAR_KENDARAAN), "banding", str(tmp_path / "lk" / "lembar-kendaraan.json"),
                              str(folder), str(CARI), str(CARI_BARU), str(tmp_path / "banding.json"), "--terbaca", ""],
                             capture_output=True, text=True)

    layar = lembar.stdout + lembar.stderr + banding.stdout + banding.stderr
    assert lembar.returncode == 0 and banding.returncode == 0, layar[-2000:]
    assert "buatan" not in layar
    isi = json.loads((tmp_path / "lk" / "lembar-kendaraan.json").read_text())
    assert {b["video"] for b in isi["baris"]} == {"buatan-latih.avi"}  # bawaan --sisi latih
    b = json.loads((tmp_path / "banding.json").read_text())
    assert len(b["calon"]) == 12 and b["terpilih"]["nama"] in {c["nama"] for c in b["calon"]}


@pytest.mark.skipif(not (KENDARAAN / "mesin.onnx").exists(), reason="pencari kendaraan belum diekspor (Rencana 19 Task 7b)")
def test_cli_lembar_bingkai_cara_potong(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    hasil = subprocess.run([sys.executable, str(BINGKAI), "lembar", str(tmp_path / "manifes.json"), str(folder),
                            str(tmp_path / "pembagian.json"), str(CARI), str(tmp_path / "bingkai"), "--kendaraan", str(KENDARAAN),
                            "--cara", "potong"], capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    assert json.loads((tmp_path / "bingkai" / "lembar-bingkai.json").read_text())["cara_kendaraan"] == "potong"


def test_cli_lembar_bingkai_ambang_dari_baris_perintah(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    hasil = subprocess.run([sys.executable, str(BINGKAI), "lembar", str(tmp_path / "manifes.json"), str(folder),
                            str(tmp_path / "pembagian.json"), str(CARI), str(tmp_path / "bingkai"), "--ambang", "0.25"],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, (hasil.stdout + hasil.stderr)[-2000:]
    assert json.loads((tmp_path / "bingkai" / "lembar-bingkai.json").read_text())["ambang"] == 0.25


@pytest.mark.skipif(not (KENDARAAN / "mesin.onnx").exists(), reason="pencari kendaraan belum diekspor (Rencana 19 Task 7b)")
def test_cli_rantai_dan_lembar_bingkai_dengan_letak(tmp_path):
    folder = dua_video_dan_pembagian(tmp_path)

    jalan = subprocess.run([sys.executable, str(SKRIP), "jalan", str(tmp_path / "manifes.json"), str(folder), str(CARI), str(BACA),
                            str(UNDUHAN), str(tmp_path / "keluar"), "--kendaraan", str(KENDARAAN), "--cara", "potong",
                            "--letak", "ry0.4"], capture_output=True, text=True)
    lembar = subprocess.run([sys.executable, str(BINGKAI), "lembar", str(tmp_path / "manifes.json"), str(folder),
                             str(tmp_path / "pembagian.json"), str(CARI), str(tmp_path / "bingkai"), "--kendaraan", str(KENDARAAN),
                             "--cara", "potong", "--letak", "ry0.4"], capture_output=True, text=True)

    assert jalan.returncode == 0 and lembar.returncode == 0, (jalan.stdout + jalan.stderr + lembar.stdout + lembar.stderr)[-2000:]
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    assert r["aturan"]["letak"] == "ry0.4" and "tersaring_letak" in r
    assert json.loads((tmp_path / "bingkai" / "lembar-bingkai.json").read_text())["letak"] == "ry0.4"


BACA_GAMBAR = AKAR / "tools" / "lab" / "baca_gambar.py"


@pytest.mark.skipif(not ((KENDARAAN / "mesin.onnx").exists() and (CARI_BARU / "mesin.onnx").exists()),
                    reason="pencari kendaraan atau pencari plat cctv1 belum diekspor (Rencana 19)")
def test_cli_baca_gambar_dengan_model_sungguhan_tanpa_nama_berkas_di_layar(tmp_path):
    folder = tmp_path / "capture" / "capture cctv mobil"
    folder.mkdir(parents=True)
    g = np.full((360, 640, 3), 90, np.uint8)
    g[200:248, 240:400] = cv2.resize(plat_buatan(TEKS[0]), (160, 48))
    cv2.imwrite(str(folder / "rahasia-1.png"), g)
    dasar = [sys.executable, str(BACA_GAMBAR), "jalan", str(tmp_path / "capture")]
    model = [str(CARI_BARU), str(KENDARAAN), str(BACA), str(UNDUHAN), "--ambang", "0.25"]

    jalan = subprocess.run(dasar + [str(tmp_path / "keluar")] + model, capture_output=True, text=True)
    (folder / "rahasia-2.png").write_bytes(b"bukan png")
    rusak = subprocess.run(dasar + [str(tmp_path / "keluar-rusak")] + model, capture_output=True, text=True)

    assert jalan.returncode == 0, (jalan.stdout + jalan.stderr)[-2000:]
    assert rusak.returncode == 1 and "GAGAL: ValueError" in rusak.stdout
    assert "rahasia" not in jalan.stdout + jalan.stderr + rusak.stdout + rusak.stderr
    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    # Tanpa kendaraan di gambar buatan, plat tidak dicari (K39): gambar itu masuk daftar tanpa plat.
    # Rencana 25-27: ringkasan juga mencatat cara pakai tahap kendaraan, varian potongan pembaca, dan rapikan kotak.
    assert r == {"gambar": 1, "plat": 0, "gambar_tanpa_plat": 1, "per_kelompok": {"mobil": 1},
                 "aturan": {"tahap_kendaraan": True, "maks_kendaraan": None, "cadangan_utuh": False, "varian_potong": "v0",
                            "rapikan": 0.0}}
    assert json.loads((tmp_path / "keluar" / "tanpa-plat.json").read_text())[0]["kendaraan"] == []
