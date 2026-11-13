"""Uji tools/lab/lembar_kecil.py (K19): gambar untuk agen harus terlalu kasar untuk membaca plat, tetapi masih cukup
untuk memilah sudut kamera, siang atau malam, dan jenis kendaraan."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_kecil as lk  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_kecil.py"


def tulis_video(jalur):
    """Video uji kecil: 40 gambar kelabu yang makin terang."""
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for i in range(40):
        tulis.write(np.full((240, 320, 3), i * 6, np.uint8))
    tulis.release()


def lembar_lama(jalur, berkas):
    """Catatan lembar dari pemilahan sebelumnya: nama video yang sudah pernah dibuatkan lembar."""
    jalur.write_text(json.dumps({"video": [{"nomor": i, "berkas": b, "gambar": 8} for i, b in enumerate(berkas, 1)]}))
    return jalur


def garis_tegak(siklus, lebar=1920, tinggi=1080):
    """Gambar garis hitam-putih tegak: `siklus` pasang garis selebar layar."""
    x = np.arange(lebar)
    baris = np.where((x * siklus * 2 // lebar) % 2 == 0, 255, 0).astype(np.uint8)
    return np.repeat(np.tile(baris, (tinggi, 1))[:, :, None], 3, axis=2)


def kontras(gambar):
    """Selisih terang-gelap di tengah gambar, 0 sampai 1."""
    abu = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY).astype(np.float32)
    t, l = abu.shape
    tengah = abu[t // 2, l // 4: 3 * l // 4]
    return float(tengah.max() - tengah.min()) / 255.0


def test_sisi_terpanjang_menjadi_48_piksel():
    kecil = lk.kecilkan(np.zeros((1080, 1920, 3), np.uint8))

    assert max(kecil.shape[:2]) == 48
    assert kecil.shape[:2] == (27, 48)


def test_video_tegak_juga_dikecilkan_dari_sisi_terpanjangnya():
    kecil = lk.kecilkan(np.zeros((1920, 1080, 3), np.uint8))

    assert kecil.shape[:2] == (48, 27)


def test_rincian_sehalus_goresan_huruf_hilang():
    # Anggapan terburuk: plat delapan huruf memenuhi lebar layar. Membedakan huruf butuh rincian sekitar satu setengah
    # pasang garis per huruf, yaitu 12 pasang garis selebar layar. Sesudah dikecilkan dan dikaburkan, kontrasnya harus
    # hampir habis.
    assert kontras(lk.kecilkan(garis_tegak(12))) < 0.15


def test_bentuk_besar_tetap_terlihat():
    # Dua pasang garis selebar layar mewakili bentuk besar: kendaraan, langit, jalan. Ini harus bertahan, kalau tidak
    # lembarnya tidak berguna untuk memilah.
    assert kontras(lk.kecilkan(garis_tegak(2))) > 0.5


def test_satu_video_menjadi_satu_baris_berisi_delapan_gambar(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-contoh.mp4")
    keluar = tmp_path / "keluar"

    kode = lk.utama(str(folder), str(keluar))

    assert kode == 0
    lembar = cv2.imread(str(keluar / "ikhtisar-1.png"))
    sisi = lk.SISI * lk.PERBESAR
    assert lembar.shape == (sisi, lk.LEBAR_NOMOR + lk.PER_VIDEO * sisi, 3)
    daftar = json.loads((keluar / "ikhtisar.json").read_text())
    assert daftar["sisi"] == 48 and daftar["halaman"] == ["ikhtisar-1.png"]
    assert daftar["video"] == [{"nomor": 1, "berkas": "youtube-contoh.mp4", "gambar": 8}]


def test_berkas_yang_bukan_video_dilewati(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    (folder / "youtube-contoh.info.json").write_text("{}")
    keluar = tmp_path / "keluar"

    kode = lk.utama(str(folder), str(keluar))

    assert kode == 0
    assert json.loads((keluar / "ikhtisar.json").read_text())["video"] == []


def test_video_yang_sudah_ada_di_lembar_lama_dilewati(tmp_path):
    # Gelombang unduhan berikutnya (K20): lembar baru hanya memuat video yang belum pernah dibuatkan lembar, supaya owner
    # tidak memeriksa ulang yang sudah diperiksanya.
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-lama.mp4")
    tulis_video(folder / "youtube-baru.mp4")
    lama = lembar_lama(tmp_path / "ikhtisar-lama.json", ["youtube-lama.mp4"])
    keluar = tmp_path / "keluar"

    kode = lk.utama(str(folder), str(keluar), [str(lama)])

    assert kode == 0
    daftar = json.loads((keluar / "ikhtisar.json").read_text())
    assert daftar["video"] == [{"nomor": 1, "berkas": "youtube-baru.mp4", "gambar": 8}]
    assert daftar["dilewati"] == 1
    assert cv2.imread(str(keluar / "ikhtisar-1.png")).shape[0] == lk.SISI * lk.PERBESAR  # satu baris saja


def test_baris_perintah_meneruskan_lembar_lama(tmp_path):
    # Rantainya: baris perintah -> utama -> lembar. Tanpa uji ini, melewati video lama bisa benar di dalam fungsi tetapi
    # tidak pernah sampai dari baris perintah, dan lembar baru diam-diam memuat semua video lagi.
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-lama.mp4")
    tulis_video(folder / "youtube-baru.mp4")
    lama = lembar_lama(tmp_path / "ikhtisar-lama.json", ["youtube-lama.mp4"])
    keluar = tmp_path / "keluar"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(keluar), str(lama)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    daftar = json.loads((keluar / "ikhtisar.json").read_text())
    assert [v["berkas"] for v in daftar["video"]] == ["youtube-baru.mp4"]


def test_lembar_lama_yang_tak_terbaca_menghentikan_pekerjaan(tmp_path):
    # Kalau daftar yang harus dilewati tidak bisa dibaca, jangan diam-diam membuat lembar untuk semua video.
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-baru.mp4")
    keluar = tmp_path / "keluar"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(keluar), str(tmp_path / "tidak-ada.json")], capture_output=True, text=True)

    assert hasil.returncode == 2
    assert "LEMBAR LAMA TAK TERBACA" in hasil.stdout + hasil.stderr
    assert not (keluar / "ikhtisar.json").exists()
