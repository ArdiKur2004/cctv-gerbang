"""Uji tools/lab/periksa_utuh.py: video yang ada berkasnya tetapi rusak atau terpotong harus tertangkap (temuan K20)."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import periksa_utuh as pu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "periksa_utuh.py"


def tulis_video(jalur, detik=4):
    """Video uji kecil, 10 gambar per detik, beserta berkas .info.json yang mencatat lamanya."""
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for i in range(detik * 10):
        tulis.write(np.full((240, 320, 3), i * 6 % 256, np.uint8))
    tulis.release()
    jalur.with_name(jalur.stem + ".info.json").write_text(json.dumps({"duration": detik}))
    return jalur


def test_video_utuh_lulus(tmp_path):
    baik, keterangan, _ukuran = pu.periksa(tulis_video(tmp_path / "youtube-utuh.mp4"))

    assert baik, keterangan


def test_video_terpotong_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-potong.mp4")
    isi = jalur.read_bytes()
    jalur.write_bytes(isi[: len(isi) // 2])

    baik, keterangan, _ukuran = pu.periksa(jalur)

    assert not baik, keterangan


def test_berkas_bernama_mp4_tetapi_bukan_video_tertangkap(tmp_path):
    # Inilah yang terjadi 13 Okt: berkasnya ada, namanya benar, isinya tidak bisa dibuka.
    jalur = tmp_path / "youtube-sampah.mp4"
    jalur.write_bytes(b"bukan video" * 1000)
    jalur.with_name("youtube-sampah.info.json").write_text(json.dumps({"duration": 4}))

    baik, keterangan, _ukuran = pu.periksa(jalur)

    assert not baik
    assert "tidak bisa dibuka" in keterangan


def test_lama_yang_jauh_dari_catatan_sumber_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-pendek.mp4")
    jalur.with_name("youtube-pendek.info.json").write_text(json.dumps({"duration": 60}))

    baik, keterangan, _ukuran = pu.periksa(jalur)

    assert not baik
    assert "lama berkas" in keterangan


def test_video_tanpa_catatan_sumber_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-yatim.mp4")
    jalur.with_name("youtube-yatim.info.json").unlink()

    baik, keterangan, _ukuran = pu.periksa(jalur)

    assert not baik
    assert ".info.json" in keterangan


def test_baris_perintah_menulis_catatan_dan_keluar_1_bila_ada_yang_rusak(tmp_path):
    # Rantainya: baris perintah -> tiap video diperiksa -> berkas catatan yang nanti dibaca tools/manifes-video.mjs.
    folder = tmp_path / "video"
    folder.mkdir()
    utuh = tulis_video(folder / "youtube-utuh.mp4")
    rusak = tulis_video(folder / "youtube-rusak.mp4")
    rusak.write_bytes(rusak.read_bytes()[:2000])
    catatan = tmp_path / "keluar" / "video-utuh.json"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(catatan)], capture_output=True, text=True)

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    isi = json.loads(catatan.read_text())
    assert isi["utuh"] == {"youtube-utuh.mp4": utuh.stat().st_size}
    assert list(isi["rusak"]) == ["youtube-rusak.mp4"]
    assert "RUSAK youtube-rusak.mp4" in hasil.stdout


def test_baris_perintah_keluar_0_bila_semua_utuh(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-utuh.mp4")
    catatan = tmp_path / "video-utuh.json"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(catatan)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "1 utuh, 0 bermasalah, dari 1 video" in hasil.stdout


def test_ukuran_gambar_dibaca_dari_berkasnya(tmp_path):
    """Resolusi yang dikembalikan harus resolusi BERKASNYA, bukan apa pun yang dicatat sumbernya.

    Cacat nyata 27 Okt 2026: tools/manifes-video.mjs mencatat resolusi dari .info.json, yaitu resolusi ASLI
    video di sumbernya. Unduhan yang dibatasi resolusinya menghasilkan berkas 640x360 yang tercatat 1280x720,
    dan setiap angka pengukuran yang memakai catatan itu ikut menyesatkan. Alat ini sudah membuka tiap berkas,
    jadi di sinilah tempat yang benar untuk membacanya.
    """
    jalur = tulis_video(tmp_path / "youtube-ukuran.mp4")
    # .info.json sengaja menyatakan resolusi yang BERBEDA dari berkasnya.
    jalur.with_name(jalur.stem + ".info.json").write_text(
        json.dumps({"duration": 4, "width": 1280, "height": 720}))

    baik, _keterangan, ukuran = pu.periksa(jalur)
    assert baik
    assert ukuran == "320x240", f"resolusi berkas salah dibaca: {ukuran}"


def test_catatan_memuat_ukuran_gambar_tiap_video(tmp_path):
    """Rantainya: `utama()` harus menulis kunci `gambar`, karena itu yang dibaca manifes."""
    tulis_video(tmp_path / "youtube-satu.mp4")
    tulis_video(tmp_path / "youtube-dua.mp4")
    catatan = tmp_path / "catatan.json"

    assert pu.utama(str(tmp_path), str(catatan)) == 0
    isi = json.loads(catatan.read_text())
    assert isi["gambar"] == {"youtube-satu.mp4": "320x240", "youtube-dua.mp4": "320x240"}
    # `utuh` SENGAJA tetap "nama -> ukuran bita": manifes membandingkan nilainya dengan ukuran berkas di disk.
    assert all(isinstance(n, int) for n in isi["utuh"].values()), "bentuk `utuh` berubah; manifes akan rusak"
