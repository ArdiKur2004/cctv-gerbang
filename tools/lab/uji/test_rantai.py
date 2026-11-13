"""Uji tools/lab/rantai.py tanpa model: sampel, potong, lacak, gabung (cek pola), detik sampai yakin, dan rantai dari manifes
sampai berkas keluaran dengan pencari dan pembaca tiruan pada video buatan."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rantai  # noqa: E402

KOTAK = (60, 40, 100, 56)


def test_langkah_sampel_lima_per_detik_dan_fps_tak_terbaca():
    assert [rantai.langkah_sampel(f) for f in (30, 25, 60, 4)] == [6, 5, 12, 1]
    assert rantai.langkah_sampel(0) == rantai.langkah_sampel(float("nan")) == 6


def test_potong_dengan_tepi_dan_batas_gambar():
    gambar = np.zeros((100, 200, 3), np.uint8)

    assert rantai.potong(gambar, (10, 20, 50, 40)).shape == (22, 44, 3)
    assert rantai.potong(gambar, (190, 90, 210, 110)).shape == (11, 11, 3)
    assert rantai.potong(gambar, (250, 0, 260, 10)) is None


def tampak(kotak, yakin=0.9):
    return {"kotak": kotak, "yakin_kotak": yakin}


def test_pelacak_menyambung_kotak_bertumpuk_dan_memutus_sesudah_jeda():
    lacak = rantai.Pelacak()
    lacak.tambah(0.0, [tampak((10, 10, 50, 30))])
    lacak.tambah(0.2, [tampak((12, 10, 52, 30)), tampak((100, 100, 140, 120))])
    lacak.tambah(0.4, [])
    lacak.tambah(1.6, [tampak((12, 10, 52, 30))])

    assert [len(j) for j in lacak.jalur] == [2, 1, 1]
    assert [p["detik"] for p in lacak.jalur[0]] == [0.0, 0.2]


def test_pelacak_dua_kotak_di_satu_gambar_tidak_masuk_jalur_yang_sama():
    lacak = rantai.Pelacak()
    lacak.tambah(0.0, [tampak((10, 10, 50, 30))])
    lacak.tambah(0.2, [tampak((10, 10, 50, 30), 0.5), tampak((11, 10, 51, 30), 0.9)])

    assert [len(j) for j in lacak.jalur] == [2, 1]
    assert lacak.jalur[0][1]["yakin_kotak"] == 0.9


def bacaan(teks, yakin=0.8):
    return {"teks": teks, "yakin_baca": yakin}


def test_gabung_suara_terbanyak_dari_bacaan_sesuai_pola():
    hasil = rantai.gabung([bacaan("B1234XY"), bacaan("b 1234 xy"), bacaan("B1234XV"), bacaan("12AB")])

    assert hasil == {"teks": "B1234XY", "status": "yakin", "setuju": 2, "sah": 3, "tampak": 4}


def test_gabung_ragu_bila_dukungan_kurang_dan_seri_dipecah_dengan_yakin():
    hasil = rantai.gabung([bacaan("B1234XY", 0.5), bacaan("B1234XV", 0.9)])

    assert hasil["teks"] == "B1234XV" and hasil["status"] == "ragu" and hasil["setuju"] == 1
    assert rantai.gabung([bacaan(""), bacaan("??")]) == {"teks": "", "status": "ragu", "setuju": 0, "sah": 0, "tampak": 2}
    # Dua dari empat bacaan sah (50%) kurang dari BAGIAN_SETUJU: ragu walau didukung dua bacaan.
    assert rantai.gabung([bacaan("B1234XY"), bacaan("B1234XY"), bacaan("B1234XV"), bacaan("B1234XW")])["status"] == "ragu"


def test_detik_yakin_saat_bacaan_pertama_kali_cukup():
    jalur = [{**bacaan(t), "detik": d} for t, d in (("B1234XV", 0.0), ("B1234XY", 0.2), ("B1234XY", 0.4))]

    assert rantai.detik_yakin(jalur) == 0.4
    assert rantai.detik_yakin(jalur[:1]) is None


def video_buatan(jalur, terang, fps=10):
    """Video MJPG 160x96; gambar ke-i memuat persegi putih di KOTAK bila terang[i]."""
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"MJPG"), fps, (160, 96))
    for ada in terang:
        g = np.full((96, 160, 3), 40, np.uint8)
        if ada:
            cv2.rectangle(g, KOTAK[:2], KOTAK[2:], (255, 255, 255), -1)
        tulis.write(g)
    tulis.release()


def cari_tiruan(gambar):
    """Kotak di KOTAK bila tengahnya terang, ditambah kotak lemah di bawah ambang yang harus dibuang."""
    kotak = [(10.0, 10.0, 30.0, 20.0, 0.1)]
    if gambar[48, 80].mean() > 128:
        kotak.append((*map(float, KOTAK), 0.9))
    return kotak


def baca_tiruan(potongan):
    return "B1234XY", 0.8


def test_jalankan_video_sampel_lacak_dan_satu_potongan_per_jalur(tmp_path):
    video_buatan(tmp_path / "v.avi", [True] * 10 + [False] * 10)

    jalur, waktu, _ = rantai.jalankan_video(tmp_path / "v.avi", cari_tiruan, baca_tiruan, ambang=0.25)

    assert len(waktu["dekode"]) == len(waktu["cari"]) == 10  # 20 gambar pada 10 fps, 5 sampel per detik
    assert [len(j) for j in jalur] == [5] and len(waktu["baca"]) == 5
    assert [p["detik"] for p in jalur[0]] == [0.0, 0.2, 0.4, 0.6, 0.8]
    assert sum("potongan" in p for p in jalur[0]) == 1


def test_rantai_dari_manifes_sampai_berkas_hanya_sudut_terpilih_dan_tanpa_teks_di_ringkasan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10 + [False] * 10)
    video_buatan(folder / "dasbor.avi", [True] * 20)
    (tmp_path / "manifes.json").write_text(json.dumps({"video": [
        {"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"},
        {"berkas": "dasbor.avi", "sudut": "dasbor", "kategori": "siang"}]}))

    r = rantai.jalankan_semua(tmp_path / "manifes.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "keluar")

    baris = [json.loads(b) for b in (tmp_path / "keluar" / "kedatangan.jsonl").read_text().splitlines()]
    assert [(b["video"], b["teks"], b["status"], b["detik_yakin"]) for b in baris] == [("gerbang.avi", "B1234XY", "yakin", 0.2)]
    assert (tmp_path / "keluar" / "potongan" / baris[0]["potongan"]).exists()
    assert r["video"] == 1 and r["kedatangan"] == r["yakin"] == 1 and r["gambar_sampel"] == 10
    ringkasan = (tmp_path / "keluar" / "ringkasan.json").read_text()
    assert "B1234" not in ringkasan and "gerbang.avi" not in ringkasan


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


def test_cara_potong_mencari_plat_di_dalam_potongan_kendaraan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dipanggil = []

    def cari_ukuran(gambar):
        dipanggil.append(gambar.shape[:2])
        t, l = gambar.shape[:2]
        return [(0.4 * l, 0.4 * t, 0.6 * l, 0.6 * t, 0.9)]

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "mobil")]
    kendaraan.ambang = 0.25

    r = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_ukuran, baca_tiruan, 0.25, tmp_path / "k",
                              cari_kendaraan=kendaraan, cara="potong")

    assert r["kedatangan"] == 1 and r["aturan"]["cara_kendaraan"] == "potong"
    # Hanya potongan kendaraan (x 32..128, y 14..82, diperlebar 10%) yang dicari, tidak pernah gambar utuh 96 x 160.
    assert set(dipanggil) == {(68, 96)}
    assert r["waktu_ms"]["kendaraan"]["n"] == 5


def test_penampakan_mencatat_kotak_kendaraan_sejajar_dengan_tampak(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca_tiruan, 0.25, tmp_path / "k", simpan_penampakan=True,
                          cari_kendaraan=kendaraan_tiruan)

    t = [json.loads(b) for b in (tmp_path / "k" / "penampakan.jsonl").read_text().splitlines()]
    assert len(t) == 1 and len(t[0]["kendaraan"]) == len(t[0]["tampak"]) == 5
    assert t[0]["kendaraan"][0] == [50.0, 30.0, 110.0, 66.0, "motor"] and len(t[0]["tampak"][0]) == 5


def test_letak_membuang_penampakan_yang_tidak_lolos_sebelum_dibaca(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dibaca = []

    def baca(potongan):
        dibaca.append(1)
        return "B1234XY", 0.8

    def kendaraan(gambar):
        return [(40.0, 20.0, 120.0, 76.0, 0.8, "mobil")]  # KOTAK (60..100, 40..56): tengahnya ry 0,5 < 0,6
    kendaraan.ambang = 0.25

    r = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_dua, baca, 0.25, tmp_path / "k", cari_kendaraan=kendaraan,
                              letak="ry0.6")

    assert r["kedatangan"] == 0 and r["tersaring_letak"] == 5 and r["aturan"]["letak"] == "ry0.6" and not dibaca


def kendaraan_dua(gambar):
    """Dua kendaraan cukup tinggi; yang memuat KOTAK (60..100, 40..56) tepi bawahnya lebih rendah (terdekat)."""
    return [(110.0, 10.0, 158.0, 60.0, 0.9, "mobil"), (40.0, 20.0, 120.0, 90.0, 0.7, "mobil")]


kendaraan_dua.ambang = 0.25


def cari_terang(gambar):
    """Selalu satu kotak di tengah bawah gambar masukan, apa pun ukurannya (gambar utuh atau potongan kendaraan): yang diuji di
    sini hanya di mana pencari dipanggil."""
    t, l = gambar.shape[:2]
    return [(0.3 * l, 0.6 * t, 0.7 * l, 0.8 * t, 0.9)]


def test_cara_potong_maks_kendaraan_dan_cadangan_utuh(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    def tanpa_kendaraan(gambar):
        return []
    tanpa_kendaraan.ambang = 0.25

    semua = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_terang, baca_tiruan, 0.25, tmp_path / "semua",
                                  cari_kendaraan=kendaraan_dua, cara="potong", simpan_penampakan=True)
    satu = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_terang, baca_tiruan, 0.25, tmp_path / "satu",
                                 cari_kendaraan=kendaraan_dua, cara="potong", maks_kendaraan=1, simpan_penampakan=True)
    kosong = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_terang, baca_tiruan, 0.25, tmp_path / "kosong",
                                   cari_kendaraan=tanpa_kendaraan, cara="potong")
    cadangan = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_terang, baca_tiruan, 0.25, tmp_path / "cadangan",
                                     cari_kendaraan=tanpa_kendaraan, cara="potong", cadangan_utuh=True)

    assert (semua["kedatangan"], satu["kedatangan"], kosong["kedatangan"], cadangan["kedatangan"]) == (2, 1, 0, 1)
    t = [json.loads(b) for b in (tmp_path / "satu" / "penampakan.jsonl").read_text().splitlines()]
    assert t[0]["kendaraan"][0] == [40.0, 20.0, 120.0, 90.0, "mobil"]
    assert satu["aturan"]["maks_kendaraan"] == 1 and satu["aturan"]["cadangan_utuh"] is False
    assert cadangan["aturan"]["cadangan_utuh"] is True and semua["aturan"]["maks_kendaraan"] is None


def test_maks_kendaraan_dan_cadangan_utuh_ditolak_tanpa_cara_potong(tmp_path):
    video_buatan(tmp_path / "v.avi", [True] * 4)

    for pilihan in ({"maks_kendaraan": 1}, {"cadangan_utuh": True}):
        with pytest.raises(ValueError, match="potong"):
            rantai.jalankan_video(tmp_path / "v.avi", cari_tiruan, baca_tiruan, 0.25, cari_kendaraan=kendaraan_dua, **pilihan)
        with pytest.raises(ValueError, match="potong"):
            rantai.jalankan_video(tmp_path / "v.avi", cari_tiruan, baca_tiruan, 0.25, cara="potong", **pilihan)


class _Tiruan:
    """Kelas model tiruan untuk uji CLI: dibuat dengan argumen apa saja, dipanggil seperti modelnya."""

    def __init__(self, fungsi, ambang=None):
        self.fungsi, self.ambang = fungsi, ambang

    def __call__(self, *argumen, **kata):
        f, ambang = self.fungsi, self.ambang

        class Model:
            def __call__(self, gambar):
                return f(gambar)

            def dengan_yakin(self, potongan):
                return f(potongan)
        m = Model()
        m.ambang = ambang
        return m


def test_cli_maks_kendaraan_dan_cadangan_utuh_sampai_berkas_keluaran(tmp_path, monkeypatch):
    # Uji rantai (Rencana 25 Task 2): bendera CLI -> jalankan_semua -> kedatangan.jsonl dan ringkasan.json, dengan model tiruan.
    import kendaraan as kd
    import onnx_fpo
    import pencari_yolox

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari_terang))
    monkeypatch.setattr(kd, "PencariKendaraan", _Tiruan(kendaraan_dua, ambang=0.25))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca_tiruan))
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dasar = ["jalan", str(tmp_path / "m.json"), str(folder), "p", "b", "u", None, "--ambang", "0.25", "--kendaraan", "k",
             "--cara", "potong"]

    for nama, tambahan in (("lama", []), ("baru", ["--maks-kendaraan", "1", "--cadangan-utuh"])):
        dasar[6] = str(tmp_path / nama)
        assert rantai.utama(dasar + tambahan) == 0

    r = {n: json.loads((tmp_path / n / "ringkasan.json").read_text()) for n in ("lama", "baru")}
    assert (r["lama"]["kedatangan"], r["baru"]["kedatangan"]) == (2, 1)
    assert r["baru"]["aturan"]["maks_kendaraan"] == 1 and r["baru"]["aturan"]["cadangan_utuh"] is True


def test_varian_potong_di_rantai_membaca_tiap_kotak_beberapa_kali_dan_v0_sama_dengan_cara_lama(tmp_path):
    # Rencana 26 (K51): pembaca tahan geser juga tersedia di rantai video.
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))
    dibaca = []

    def baca(potongan):
        dibaca.append(1)
        return "B1234XY", 0.8

    lama = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "lama")
    v0 = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "v0", varian="v0")
    v1 = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca, 0.25, tmp_path / "v1", varian="v1")

    assert (tmp_path / "lama" / "kedatangan.jsonl").read_text() == (tmp_path / "v0" / "kedatangan.jsonl").read_text()
    assert lama["aturan"]["varian_potong"] == v0["aturan"]["varian_potong"] == "v0" and v1["aturan"]["varian_potong"] == "v1"
    assert v1["kedatangan"] == 1 and len(dibaca) == 3 * 5  # 5 gambar sampel berkotak, 3 potongan per kotak
    assert v1["waktu_ms"]["baca"]["n"] == 5  # waktu baca dicatat per kotak, termasuk semua potongannya


def test_cli_rantai_varian_potong_sampai_berkas_keluaran(tmp_path, monkeypatch):
    import onnx_fpo
    import pencari_yolox

    dibaca = []

    def baca(potongan):
        dibaca.append(1)
        return "B1234XY", 0.8

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari_tiruan))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca))
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    kode = rantai.utama(["jalan", str(tmp_path / "m.json"), str(folder), "p", "b", "u", str(tmp_path / "k"), "--ambang", "0.25",
                         "--varian-potong", "v2"])

    r = json.loads((tmp_path / "k" / "ringkasan.json").read_text())
    assert kode == 0 and r["aturan"]["varian_potong"] == "v2" and r["kedatangan"] == 1 and len(dibaca) == 7 * 5


def cari_putih_longgar(gambar):
    """Kotak di sekeliling piksel terang; longgar 10 piksel di gambar utuh 160 lebar, tepat di potongan yang lebih sempit."""
    ys, xs = np.where(gambar[:, :, 0] > 200)
    if not len(xs):
        return []
    x1, y1, x2, y2 = float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)
    if gambar.shape[1] > 150:
        x1, y1, x2, y2 = x1 - 10, y1 - 10, x2 + 10, y2 + 10
    return [(x1, y1, x2, y2, 0.9)]


def luas_kotak(k):
    return (k[2] - k[0]) * (k[3] - k[1])


def test_rapikan_di_rantai_mengecilkan_kotak_longgar_dan_nol_sama_dengan_cara_lama(tmp_path):
    # Rencana 27 (K54): rapikan juga tersedia di rantai video.
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    lama = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_putih_longgar, baca_tiruan, 0.25, tmp_path / "lama",
                                 simpan_penampakan=True)
    nol = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_putih_longgar, baca_tiruan, 0.25, tmp_path / "nol",
                                simpan_penampakan=True, rapikan=0.0)
    rapi = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_putih_longgar, baca_tiruan, 0.25, tmp_path / "rapi",
                                 simpan_penampakan=True, rapikan=0.5)

    tampak = {n: json.loads((tmp_path / n / "penampakan.jsonl").read_text().splitlines()[0])["tampak"][0][1:]
              for n in ("lama", "nol", "rapi")}
    assert (tmp_path / "lama" / "kedatangan.jsonl").read_text() == (tmp_path / "nol" / "kedatangan.jsonl").read_text()
    assert tampak["lama"] == tampak["nol"] and luas_kotak(tampak["rapi"]) < luas_kotak(tampak["lama"])
    assert lama["aturan"]["rapikan"] == nol["aturan"]["rapikan"] == 0.0 and rapi["aturan"]["rapikan"] == 0.5
    assert rapi["kedatangan"] == 1
    with pytest.raises(ValueError, match="konteks"):  # ditolak sebelum video dibuka, walau tak ada kotak yang dirapikan
        rantai.jalankan_video(folder / "gerbang.avi", cari_putih_longgar, baca_tiruan, 0.25, rapikan=-1.0)


def test_cli_rantai_rapikan_sampai_berkas_keluaran(tmp_path, monkeypatch):
    import onnx_fpo
    import pencari_yolox

    monkeypatch.setattr(pencari_yolox, "PencariYolox", _Tiruan(cari_putih_longgar))
    monkeypatch.setattr(onnx_fpo, "PembacaOnnxMesin", _Tiruan(baca_tiruan))
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    kode = rantai.utama(["jalan", str(tmp_path / "m.json"), str(folder), "p", "b", "u", str(tmp_path / "k"), "--ambang", "0.25",
                         "--rapikan", "0.5", "--simpan-penampakan"])

    r = json.loads((tmp_path / "k" / "ringkasan.json").read_text())
    kotak = json.loads((tmp_path / "k" / "penampakan.jsonl").read_text().splitlines()[0])["tampak"][0][1:]
    assert kode == 0 and r["aturan"]["rapikan"] == 0.5 and luas_kotak(kotak) < 60 * 36  # kotak longgar 60 x 36


def test_bacaan_per_gambar_tersimpan_dengan_ketajaman_dan_tinggi(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    video_buatan(folder / "gerbang.avi", [True] * 10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "k", simpan_bacaan=True)

    baris = [json.loads(b) for b in (tmp_path / "k" / "bacaan.jsonl").read_text().splitlines()]
    assert [(b["video"], b["kedatangan"], len(b["bacaan"])) for b in baris] == [("gerbang.avi", 1, 5)]
    gambar, teks, yakin, ketajaman, tinggi = baris[0]["bacaan"][0]
    assert (gambar, teks, yakin) == (0, "B1234XY", 0.8) and ketajaman > 0 and tinggi > 16
    assert "B1234" not in (tmp_path / "k" / "ringkasan.json").read_text()


def test_sampel_per_detik_bisa_diatur_dan_YANG_DIPAKAI_yang_dicatat(tmp_path):
    """Laju contoh bisa diatur, dan ringkasan mencatat yang BENAR-BENAR dipakai.

    Dua sebab, keduanya nyata (27 Okt 2026):
    1. Perangkat gerbang yang lemah tidak sanggup 5 gambar per detik. Di company-ai satu gambar butuh 1 detik,
       jadi lajunya paling banyak sekitar 1 per detik — dan apakah plat masih terbaca pada laju itu HARUS
       diukur, bukan ditebak.
    2. `aturan.sampel_per_detik` di ringkasan dulu mencatat KONSTANTA, bukan nilai yang dipakai. Itu kelas
       cacat yang sama dengan resolusi video yang tercatat dari sumber: angka pengukuran yang menyesatkan
       tanpa ada yang tahu sebabnya.
    """
    folder = tmp_path / "video"
    folder.mkdir()
    # 20 gambar pada 10 fps = 2 detik video.
    video_buatan(folder / "gerbang.avi", [True] * 20, fps=10)
    (tmp_path / "m.json").write_text(json.dumps({"video": [
        {"berkas": "gerbang.avi", "sudut": "gerbang", "kategori": "siang"}]}))

    lima = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "lima",
                                 per_detik=5)
    satu = rantai.jalankan_semua(tmp_path / "m.json", folder, cari_tiruan, baca_tiruan, 0.25, tmp_path / "satu",
                                 per_detik=1)

    # 10 fps / 5 per detik = tiap gambar ke-2 => 10 contoh; / 1 per detik = tiap gambar ke-10 => 2 contoh.
    assert lima["gambar_sampel"] == 10, f"laju 5 memberi {lima['gambar_sampel']} contoh"
    assert satu["gambar_sampel"] == 2, f"laju 1 memberi {satu['gambar_sampel']} contoh"
    assert lima["aturan"]["sampel_per_detik"] == 5
    assert satu["aturan"]["sampel_per_detik"] == 1, "ringkasan mencatat konstanta, bukan laju yang dipakai"
