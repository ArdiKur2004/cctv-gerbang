"""Uji tools/lab/baca_gambar.py (Rencana 24, K44): gambar diam dibaca dengan urutan rantai (kendaraan, plat di dalam kendaraan,
baca), keluaran berbentuk kedatangan.jsonl untuk lembar_rantai.py, nama berkas asli tidak muncul di keluaran atau layar, gambar
tanpa plat dicatat terpisah, dan pembagian latih/uji tetap per isi berkas."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_gambar as bg  # noqa: E402


def kendaraan(gambar):
    return [(40.0, 20.0, 200.0, 140.0, 0.8, "mobil")]


kendaraan.ambang = 0.25


def cari(gambar):
    t, l = gambar.shape[:2]
    return [(0.4 * l, 0.7 * t, 0.6 * l, 0.8 * t, 0.9)] if gambar.mean() > 60 else []


def baca(potongan):
    return "B1234XY", 0.9


# Isi "aturan" ringkasan bila tidak ada pilihan yang dinyalakan (Rencana 25: kendaraan; 26: varian potongan; 27: rapikan).
ATURAN_BAWAAN = {"tahap_kendaraan": True, "maks_kendaraan": None, "cadangan_utuh": False, "varian_potong": "v0", "rapikan": 0.0}


def siapkan(tmp_path):
    for sub, nama, terang in (("capture cctv mobil", "B1234XY rahasia.png", 120), ("capture cctv motor", "gelap.png", 10)):
        (tmp_path / "capture" / sub).mkdir(parents=True)
        cv2.imwrite(str(tmp_path / "capture" / sub / nama), np.full((180, 320, 3), terang, np.uint8))
    return tmp_path / "capture"


def test_gambar_dibaca_dan_keluaran_untuk_lembar_rantai(tmp_path):
    r = bg.jalankan(siapkan(tmp_path), tmp_path / "keluar", cari, kendaraan, baca, 0.25)

    assert r == {"gambar": 2, "plat": 1, "gambar_tanpa_plat": 1, "per_kelompok": {"mobil": 1, "motor": 1},
                 "aturan": ATURAN_BAWAAN}
    tiba = [json.loads(x) for x in (tmp_path / "keluar" / "kedatangan.jsonl").read_text().splitlines()]
    assert [(t["kategori"], t["teks"], t["nomor"]) for t in tiba] == [("mobil", "B1234XY", 1)]
    assert (tmp_path / "keluar" / "potongan" / tiba[0]["potongan"]).exists()
    tanpa = json.loads((tmp_path / "keluar" / "tanpa-plat.json").read_text())
    assert [t["kelompok"] for t in tanpa] == ["motor"]


def test_nama_berkas_asli_tidak_muncul_di_keluaran_bersama(tmp_path):
    bg.jalankan(siapkan(tmp_path), tmp_path / "keluar", cari, kendaraan, baca, 0.25)

    for nama in ("kedatangan.jsonl", "ringkasan.json", "tanpa-plat.json"):
        assert "rahasia" not in (tmp_path / "keluar" / nama).read_text()
    assert "rahasia" in (tmp_path / "keluar" / "peta-berkas.json").read_text()  # peta ke berkas asli, hanya untuk lab


def test_gambar_yang_tak_bisa_dibuka_menghentikan_jalan(tmp_path):
    folder = siapkan(tmp_path)
    (folder / "capture cctv mobil" / "rusak.png").write_bytes(b"bukan png")

    with pytest.raises(ValueError):  # tidak dilewati diam-diam: hitungan gambar harus sama dengan yang benar-benar dibaca
        bg.jalankan(folder, tmp_path / "keluar", cari, kendaraan, baca, 0.25)


def test_lembar_tanpa_plat_satu_kartu_per_gambar_dengan_kendaraan_bernomor(tmp_path):
    folder = siapkan(tmp_path)
    bg.jalankan(folder, tmp_path / "keluar", cari, kendaraan, baca, 0.25)

    r = bg.buat_lembar_tanpa(folder, tmp_path / "keluar", tmp_path / "lembar")

    assert r == {"kartu": 1, "kendaraan_bernomor": 1, "halaman": 1}
    isi = json.loads((tmp_path / "lembar" / "lembar-tanpa-plat.json").read_text())
    tanpa = json.loads((tmp_path / "keluar" / "tanpa-plat.json").read_text())
    assert [(b["nomor"], b["gambar"], b["kelompok"]) for b in isi["baris"]] == [(1, tanpa[0]["gambar"], "motor")]
    assert (tmp_path / "lembar" / isi["halaman"][0]).exists() and "rahasia" not in json.dumps(isi)


def test_tanpa_tahap_kendaraan_plat_dicari_di_gambar_utuh_dengan_ambang(tmp_path):
    # Rantai jualan (Rencana 24 Task 11) belum punya pencari kendaraan: plat dicari di gambar utuh, aturan ambangnya sama dengan
    # rantai.py tanpa --kendaraan.
    r = bg.jalankan(siapkan(tmp_path), tmp_path / "keluar", cari, None, baca, 0.25)
    tinggi = bg.jalankan(tmp_path / "capture", tmp_path / "keluar-tinggi", cari, None, baca, 0.95)

    assert (r["plat"], r["gambar_tanpa_plat"]) == (1, 1) and (tinggi["plat"], tinggi["gambar_tanpa_plat"]) == (0, 2)
    tiba = json.loads((tmp_path / "keluar" / "kedatangan.jsonl").read_text().splitlines()[0])
    assert tiba["kotak"] == [128.0, 126.0, 192.0, 144.0]  # kotak cari di gambar utuh 320x180, tanpa potongan kendaraan
    assert json.loads((tmp_path / "keluar" / "tanpa-plat.json").read_text())[0]["kendaraan"] == []


def kendaraan_dua_atau_kosong(gambar):
    """Gambar terang (>110): dua kendaraan, yang dekat di bawah; gambar redup: tidak ada kendaraan."""
    if gambar.mean() > 110:
        return [(180.0, 20.0, 300.0, 100.0, 0.9, "mobil"), (20.0, 60.0, 150.0, 170.0, 0.7, "mobil")]
    return []


def siapkan_dua(tmp_path):
    for sub, nama, terang in (("capture cctv mobil", "dua.png", 120), ("capture cctv motor", "tanpa-kendaraan.png", 100)):
        (tmp_path / "capture" / sub).mkdir(parents=True)
        cv2.imwrite(str(tmp_path / "capture" / sub / nama), np.full((180, 320, 3), terang, np.uint8))
    return tmp_path / "capture"


def test_maks_kendaraan_dan_cadangan_utuh_di_jalankan(tmp_path):
    folder = siapkan_dua(tmp_path)

    lama = bg.jalankan(folder, tmp_path / "lama", cari, kendaraan_dua_atau_kosong, baca, 0.25)
    baru = bg.jalankan(folder, tmp_path / "baru", cari, kendaraan_dua_atau_kosong, baca, 0.25, maks_kendaraan=1,
                       cadangan_utuh=True)

    assert (lama["plat"], lama["gambar_tanpa_plat"]) == (2, 1) and (baru["plat"], baru["gambar_tanpa_plat"]) == (2, 0)
    tiba = [json.loads(x) for x in (tmp_path / "baru" / "kedatangan.jsonl").read_text().splitlines()]
    assert sorted(t["kategori"] for t in tiba) == ["mobil", "motor"]
    assert lama["aturan"] == ATURAN_BAWAAN
    assert baru["aturan"] == {**ATURAN_BAWAAN, "maks_kendaraan": 1, "cadangan_utuh": True}
    for pilihan in ({"maks_kendaraan": 1}, {"cadangan_utuh": True}):  # tanpa tahap kendaraan pilihan ini tidak bermakna
        with pytest.raises(ValueError, match="kendaraan"):
            bg.jalankan(folder, tmp_path / "x", cari, None, baca, 0.25, **pilihan)


class _Tiruan:
    """Kelas model tiruan untuk uji CLI: dibuat dengan argumen apa saja, dipanggil seperti modelnya."""

    def __init__(self, fungsi):
        self.fungsi = fungsi

    def __call__(self, *argumen, **kata):
        f = self.fungsi

        class Model:
            def __call__(self, gambar):
                return f(gambar)

            def dengan_yakin(self, potongan):
                return f(potongan)

        return Model()


def test_cli_maks_kendaraan_dan_cadangan_utuh_sampai_berkas_keluaran(tmp_path, monkeypatch):
    # Uji rantai (Rencana 25 Task 2): bendera CLI -> jalankan -> kedatangan.jsonl dan ringkasan.json, dengan model tiruan.
    import kendaraan as kd
    import onnx_fpo
    import pencari_yolox

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari))
    monkeypatch.setattr(kd, "PencariKendaraan", _Tiruan(kendaraan_dua_atau_kosong))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca))
    folder = siapkan_dua(tmp_path)
    dasar = ["jalan", str(folder), None, "p", "k", "b", "u", "--ambang", "0.25"]

    for nama, tambahan in (("lama", []), ("baru", ["--maks-kendaraan", "1", "--cadangan-utuh"])):
        dasar[2] = str(tmp_path / nama)
        assert bg.utama(dasar + tambahan) == 0

    kelompok = {n: sorted(json.loads(x)["kategori"] for x in (tmp_path / n / "kedatangan.jsonl").read_text().splitlines())
                for n in ("lama", "baru")}
    tanpa = {n: len(json.loads((tmp_path / n / "tanpa-plat.json").read_text())) for n in ("lama", "baru")}
    aturan = {n: json.loads((tmp_path / n / "ringkasan.json").read_text())["aturan"] for n in ("lama", "baru")}
    # Lama: dua plat dari dua kendaraan di gambar mobil, gambar motor tanpa plat. Baru: satu kendaraan terdekat, dan gambar motor
    # tanpa kendaraan dicari utuh.
    assert kelompok == {"lama": ["mobil", "mobil"], "baru": ["mobil", "motor"]} and tanpa == {"lama": 1, "baru": 0}
    assert aturan["lama"]["maks_kendaraan"] is None
    assert aturan["baru"] == {**ATURAN_BAWAAN, "maks_kendaraan": 1, "cadangan_utuh": True}


def test_varian_potong_membaca_tiap_plat_beberapa_kali_dan_v0_sama_dengan_cara_lama(tmp_path):
    # Rencana 26 (K51): tiap plat dibaca dari 1/3/7 potongan lalu dipungut suara; v0 = cara lama.
    folder = siapkan(tmp_path)
    dibaca = []

    def baca_hitung(potongan):
        dibaca.append(potongan.shape)
        return "B1234XY", 0.9

    lama = bg.jalankan(folder, tmp_path / "lama", cari, kendaraan, baca, 0.25)
    v0 = bg.jalankan(folder, tmp_path / "v0", cari, kendaraan, baca, 0.25, varian="v0")
    v2 = bg.jalankan(folder, tmp_path / "v2", cari, kendaraan, baca_hitung, 0.25, varian="v2")

    for n in ("kedatangan.jsonl", "tanpa-plat.json"):
        assert (tmp_path / "lama" / n).read_text() == (tmp_path / "v0" / n).read_text()
    assert lama == v0 and v2["plat"] == 1 and len(dibaca) == 7 and v2["aturan"]["varian_potong"] == "v2"
    tiba = json.loads((tmp_path / "v2" / "kedatangan.jsonl").read_text().splitlines()[0])
    assert tiba["teks"] == "B1234XY" and tiba["yakin_baca"] == 0.9


def test_cli_varian_potong_sampai_berkas_keluaran(tmp_path, monkeypatch):
    import kendaraan as kd
    import onnx_fpo
    import pencari_yolox

    dibaca = []

    def baca_hitung(potongan):
        dibaca.append(1)
        return "B1234XY", 0.9

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari))
    monkeypatch.setattr(kd, "PencariKendaraan", _Tiruan(kendaraan))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca_hitung))
    folder = siapkan(tmp_path)

    kode = bg.utama(["jalan", str(folder), str(tmp_path / "k"), "p", "k", "b", "u", "--ambang", "0.25", "--varian-potong", "v1"])

    r = json.loads((tmp_path / "k" / "ringkasan.json").read_text())
    assert kode == 0 and r["aturan"]["varian_potong"] == "v1" and r["plat"] == 1 and len(dibaca) == 3


def cari_longgar(gambar):
    """Pencari tiruan: kotak di sekeliling piksel putih; di gambar lebar (potongan kendaraan) kotaknya longgar 10 piksel, di potongan
    kecil (pencarian kedua) tepat. Dipakai untuk menguji bahwa kotak rapi yang dipotong dan dibaca."""
    ys, xs = np.where(gambar[:, :, 0] > 200)
    if not len(xs):
        return []
    x1, y1, x2, y2 = float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)
    if gambar.shape[1] > 200:
        x1, y1, x2, y2 = x1 - 10, y1 - 10, x2 + 10, y2 + 10
    return [(x1, y1, x2, y2, 0.9)]


def siapkan_plat_putih(tmp_path):
    folder = tmp_path / "capture" / "capture cctv mobil"
    folder.mkdir(parents=True)
    g = np.full((180, 320, 3), 60, np.uint8)
    g[120:135, 140:180] = 255  # plat di x 140..180, y 120..135
    cv2.imwrite(str(folder / "putih.png"), g)
    return tmp_path / "capture"


def test_rapikan_memakai_kotak_rapi_untuk_dipotong_dan_dibaca(tmp_path):
    # Rencana 27 (K54): pencarian kedua di sekitar kotak pertama; konteks 0 = cara lama.
    folder = siapkan_plat_putih(tmp_path)
    lebar = []

    def baca_ukur(potongan):
        lebar.append(potongan.shape[1])
        return "B1234XY", 0.9

    def kendaraan_besar(gambar):
        return [(40.0, 20.0, 300.0, 170.0, 0.8, "mobil")]

    lama = bg.jalankan(folder, tmp_path / "lama", cari_longgar, kendaraan_besar, baca_ukur, 0.25)
    rapi = bg.jalankan(folder, tmp_path / "rapi", cari_longgar, kendaraan_besar, baca_ukur, 0.25, rapikan=1.0)

    kotak = {n: json.loads((tmp_path / n / "kedatangan.jsonl").read_text().splitlines()[0])["kotak"] for n in ("lama", "rapi")}
    assert kotak == {"lama": [130.0, 110.0, 190.0, 145.0], "rapi": [140.0, 120.0, 180.0, 135.0]}
    assert lebar[1] < lebar[0]  # potongan yang dibaca ikut menyempit
    assert lama["aturan"]["rapikan"] == 0.0 and rapi["aturan"] == {**ATURAN_BAWAAN, "rapikan": 1.0}


def test_cli_rapikan_sampai_berkas_keluaran(tmp_path, monkeypatch):
    import kendaraan as kd
    import onnx_fpo
    import pencari_yolox

    def kendaraan_besar(gambar):
        return [(40.0, 20.0, 300.0, 170.0, 0.8, "mobil")]

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari_longgar))
    monkeypatch.setattr(kd, "PencariKendaraan", _Tiruan(kendaraan_besar))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca))
    folder = siapkan_plat_putih(tmp_path)

    kode = bg.utama(["jalan", str(folder), str(tmp_path / "k"), "p", "k", "b", "u", "--ambang", "0.25", "--rapikan", "1.0"])

    r = json.loads((tmp_path / "k" / "ringkasan.json").read_text())
    tiba = json.loads((tmp_path / "k" / "kedatangan.jsonl").read_text().splitlines()[0])
    assert kode == 0 and r["aturan"]["rapikan"] == 1.0 and tiba["kotak"] == [140.0, 120.0, 180.0, 135.0]


def test_sisi_per_isi_berkas_tetap():
    assert bg.sisi(b"isi-a") == bg.sisi(b"isi-a") and {bg.sisi(bytes([i])) for i in range(64)} == {"uji", "latih"}
