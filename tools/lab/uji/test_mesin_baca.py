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
