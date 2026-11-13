"""Uji tools/lab/halaman_ciri.py (Rencana 31, spec Fase 3 tahap 1 bagian 3): halaman untuk OWNER yang melabeli jenis, warna, dan merek
kendaraan berplat berlabel di tangkapan. Satu kartu per kendaraan pemuat plat, usulan jenis dari pencari kendaraan, kotak perkiraan bila
kendaraannya tidak ditemukan, daftar kelas yang sama di halaman dan di terima, nilai di luar daftar ditolak sebelum menulis, dan nama
berkas asli tidak pernah muncul."""
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import halaman_ciri as hc  # noqa: E402

PLAT_A1, PLAT_A2 = [120, 150, 160, 162], [130, 120, 150, 130]  # dua plat di kendaraan A (mis. motor berboncengan dua plat terbaca)
PLAT_B, PLAT_TANPA = [420, 200, 470, 214], [600, 300, 640, 312]
MOBIL_A = (100, 60, 220, 190, 0.9, "motor")
MOBIL_B = (380, 100, 520, 230, 0.8, "mobil")
BESAR = (0, 0, 560, 400, 0.3, "bus")  # memuat plat A dan B (yang terkecil yang dipilih), tidak memuat PLAT_TANPA


def kendaraan_palsu(gambar):
    return [BESAR, MOBIL_A, MOBIL_B] if gambar.shape[1] == 700 else []


def siapkan(tmp_path):
    folder = tmp_path / "capture" / "capture cctv motor"
    folder.mkdir(parents=True)
    peta, gambar = {}, {}
    for i, (lebar, sisi) in enumerate(((700, "latih"), (700, "uji"), (320, "latih")), 1):
        g = f"g{i:04d}"
        cv2.imwrite(str(folder / f"rahasia-B{i}XY.png"), np.full((400, lebar, 3), 120, np.uint8))
        peta[g] = f"capture cctv motor/rahasia-B{i}XY.png"
        plat = [{"kotak": PLAT_A1, "teks": "B1XY", "tak_terbaca": False, "asal": "lembar"},
                {"kotak": PLAT_A2, "teks": None, "tak_terbaca": True, "asal": "lembar"},
                {"kotak": PLAT_B, "teks": "D2AB", "tak_terbaca": False, "asal": "halaman"},
                {"kotak": PLAT_TANPA, "teks": "F3CD", "tak_terbaca": False, "asal": "lembar"}] if lebar == 700 else []
        gambar[g] = {"kelompok": "motor", "sisi": sisi, "bukan_plat": [], "plat_tanpa_label": 0, "plat": plat}
    (tmp_path / "peta.json").write_text(json.dumps(peta))
    (tmp_path / "label.json").write_text(json.dumps({"gambar": gambar, "dikeluarkan": {}}))


def buat(tmp_path):
    siapkan(tmp_path)
    return hc.buat(tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json", kendaraan_palsu, tmp_path / "halaman")


def test_kartu_per_kendaraan_pemuat_plat_dan_kotak_perkiraan_untuk_plat_tanpa_kendaraan():
    plat = [{"kotak": PLAT_A1}, {"kotak": PLAT_A2}, {"kotak": PLAT_B}, {"kotak": PLAT_TANPA}]

    kartu = hc.kartu_kendaraan(plat, [BESAR, MOBIL_A, MOBIL_B][1:], 700, 400)

    assert [k["plat"] for k in kartu] == [[1, 2], [3], [4]]  # dua plat di kendaraan yang sama = satu kartu
    assert [k["usulan_jenis"] for k in kartu] == ["motor", "mobil", None]
    assert [k["perkiraan"] for k in kartu] == [False, False, True]
    assert kartu[0]["kotak"] == [100, 60, 220, 190] and kartu[1]["kotak"] == [380, 100, 520, 230]
    x1, y1, x2, y2 = kartu[2]["kotak"]
    assert 0 <= x1 < 600 and 0 <= y1 < 300 and 640 < x2 <= 700 and 312 < y2 <= 400  # memuat platnya, di dalam gambar


def test_kendaraan_terkecil_yang_memuat_plat_yang_dipilih():
    kartu = hc.kartu_kendaraan([{"kotak": PLAT_A1}], [BESAR, MOBIL_A], 700, 400)

    assert kartu[0]["kotak"] == [100, 60, 220, 190] and kartu[0]["usulan_jenis"] == "motor"


def test_buat_menulis_halaman_gambar_bernomor_dan_butir_tanpa_nama_asli(tmp_path):
    r = buat(tmp_path)

    keluar = tmp_path / "halaman"
    butir = json.loads((keluar / "butir.json").read_text())["butir"]
    assert r == {"kartu": 6, "perkiraan": 2, "usulan": {"mobil": 2, "motor": 2}, "gambar": 2}
    assert [b["id"] for b in butir] == [f"k{i}" for i in range(1, 7)]
    assert {b["gambar"] for b in butir} == {"g0001", "g0002"} and {b["sisi"] for b in butir} == {"latih", "uji"}
    assert all((keluar / b["berkas"]).exists() and b["berkas"].startswith("gambar/g000") for b in butir)
    assert all(set(b) >= {"kotak", "perkiraan", "plat", "usulan_jenis", "kelompok", "lebar", "tinggi"} for b in butir)
    isi = (keluar / "halaman.html").read_text(encoding="utf-8") + (keluar / "butir.json").read_text()
    assert "rahasia" not in isi + " ".join(p.name for p in (keluar / "gambar").iterdir())
    assert "http://" not in isi and "https://" not in isi  # halaman tidak memuat apa pun dari luar


def test_halaman_memakai_daftar_kelas_yang_sama_dengan_terima(tmp_path):
    buat(tmp_path)

    halaman = (tmp_path / "halaman" / "halaman.html").read_text(encoding="utf-8")
    kelas = json.loads(re.search(r"const KELAS = (\{.*?\});", halaman).group(1))
    assert kelas == hc.KELAS
    assert hc.KELAS["jenis"] == ["mobil", "pikap", "truk", "bus", "motor"]  # spec Fase 3 bagian 1 (K61)
    assert hc.KELAS["merek_motor"] == ["Honda", "Yamaha", "Suzuki", "Kawasaki", "lainnya"]
    assert len(hc.KELAS["warna"]) == 9 and len(hc.KELAS["merek_mobil"]) == 11
    butir = json.loads(re.search(r"const BUTIR = (\[.*?\]);\n", halaman).group(1))
    assert [b["id"] for b in butir] == [f"k{i}" for i in range(1, 7)]


def test_peringatan_merek_ditulis_sesudah_tampil_yang_mengosongkannya(tmp_path):
    # Ditemukan saat halaman buatan dibuka di peramban (Rencana 31 Task 2): pesan "merek dikosongkan" ditulis sebelum tampil(), yang
    # mengosongkan pesan, jadi owner tidak pernah melihatnya. Penjaga ini membaca urutan di skrip halaman.
    buat(tmp_path)

    halaman = (tmp_path / "halaman" / "halaman.html").read_text(encoding="utf-8")
    ubah_jenis = halaman[halaman.index('el("jenis").addEventListener("change"'):]
    ubah_jenis = ubah_jenis[:ubah_jenis.index("});")]
    assert ubah_jenis.index("tampil();") < ubah_jenis.index("Merek dikosongkan")


def simpan(tmp_path, jawab, tanda=None):
    """Berkas jawaban seperti yang diunduh halaman: tanda halaman ikut (bawaan: tanda halaman di tmp_path/halaman)."""
    if tanda is None:
        tanda = hc.tanda_halaman(json.loads((tmp_path / "halaman" / "butir.json").read_text())["butir"])
    (tmp_path / "label-ciri.json").write_text(json.dumps({"versi": 1, "tanda": tanda, "butir": jawab}))


@pytest.mark.parametrize("tanda", ["000000000000", ""])
def test_terima_menolak_berkas_dari_halaman_lain(tmp_path, tanda):
    # Owner bisa menyimpan beberapa kali (label-ciri (1).json, (2).json) atau memakai berkas dari halaman lain (mis. halaman buatan
    # Rencana 31 Task 2). Tanda halaman di berkas harus sama dengan tanda halaman yang dibuat dari butir.json ini.
    buat(tmp_path)
    simpan(tmp_path, {"k1": {"jenis": "motor", "warna": "hitam", "merek": "Honda"}}, tanda=tanda)

    with pytest.raises(hc.LabelDitolak, match="tanda"):
        hc.terima(tmp_path / "halaman" / "butir.json", tmp_path / "label-ciri.json", tmp_path / "ciri")

    assert not (tmp_path / "ciri" / "ciri.json").exists()


def test_tanda_di_halaman_sama_dengan_tanda_halaman(tmp_path):
    buat(tmp_path)

    halaman = (tmp_path / "halaman" / "halaman.html").read_text(encoding="utf-8")
    butir = json.loads((tmp_path / "halaman" / "butir.json").read_text())["butir"]
    assert f'tanda: "{hc.tanda_halaman(butir)}"' in halaman and f'"cctvgerbang-ciri-{hc.tanda_halaman(butir)}"' in halaman


def test_terima_jawaban_sah_menjadi_ciri_dan_ringkasan(tmp_path):
    buat(tmp_path)
    simpan(tmp_path, {
        "k1": {"jenis": "motor", "warna": "hitam", "merek": "Honda", "kotak_tidak_pas": False},
        "k2": {"jenis": "pikap", "warna": "putih", "merek": "Suzuki", "kotak_tidak_pas": True},
        "k3": {"jenis": "bukan_kendaraan", "warna": "", "merek": ""},
        "k4": {"jenis": "mobil", "warna": "tak_yakin", "merek": ""},  # belum lengkap
    })

    r = hc.terima(tmp_path / "halaman" / "butir.json", tmp_path / "label-ciri.json", tmp_path / "ciri")

    ciri = {k["id"]: k for k in json.loads((tmp_path / "ciri" / "ciri.json").read_text())["kendaraan"]}
    assert (ciri["k1"]["jenis"], ciri["k1"]["warna"], ciri["k1"]["merek"], ciri["k1"]["lengkap"]) == ("motor", "hitam", "Honda", True)
    assert ciri["k2"]["kotak_tidak_pas"] is True and ciri["k2"]["usulan_jenis"] == "mobil"
    assert (ciri["k3"]["jenis"], ciri["k3"]["warna"], ciri["k3"]["merek"], ciri["k3"]["lengkap"]) == ("bukan_kendaraan", None, None, True)
    assert ciri["k4"]["lengkap"] is False and ciri["k6"]["lengkap"] is False
    assert ciri["k1"]["plat"] == [1, 2] and ciri["k1"]["gambar"] == "g0001"
    assert r["kartu"] == 6 and r["lengkap"] == 3 and r["kosong"] == 3 and r["bukan_kendaraan"] == 1 and r["kotak_tidak_pas"] == 1
    assert r["usulan_jenis_sama"] == {"sama": 1, "berbeda": 1}  # k1 motor = usulan motor; k2 pikap != usulan mobil
    assert r["per_sisi"]["latih"]["jenis"] == {"motor": 1, "pikap": 1}


@pytest.mark.parametrize("jawab", [
    {"k1": {"jenis": "motor", "warna": "ungu", "merek": "Honda"}},
    {"k1": {"jenis": "mobil", "warna": "putih", "merek": "Yamaha"}},  # merek motor untuk mobil
    {"k1": {"jenis": "motor", "warna": "putih", "merek": "Toyota"}},  # merek mobil untuk motor
    {"k1": {"jenis": "sedan", "warna": "putih", "merek": "Toyota"}},
    {"k999": {"jenis": "motor", "warna": "hitam", "merek": "Honda"}},
])
def test_terima_menolak_nilai_di_luar_daftar_sebelum_menulis(tmp_path, jawab):
    buat(tmp_path)
    simpan(tmp_path, jawab)

    with pytest.raises(hc.LabelDitolak):
        hc.terima(tmp_path / "halaman" / "butir.json", tmp_path / "label-ciri.json", tmp_path / "ciri")

    assert not (tmp_path / "ciri" / "ciri.json").exists()


def test_cli_buat_dan_terima_sampai_berkas_tanpa_nama_asli_di_layar(tmp_path, monkeypatch, capsys):
    siapkan(tmp_path)

    class Palsu:
        def __init__(self, folder, utas=None):
            self.folder = folder

        def __call__(self, gambar):
            return kendaraan_palsu(gambar)

    monkeypatch.setattr(hc, "PencariKendaraan", Palsu)

    a = hc.utama(["buat", str(tmp_path / "capture"), str(tmp_path / "peta.json"), str(tmp_path / "label.json"),
                  str(tmp_path / "kendaraan"), str(tmp_path / "halaman")])
    simpan(tmp_path, {"k1": {"jenis": "motor", "warna": "hitam", "merek": "Honda"}})
    b = hc.utama(["terima", str(tmp_path / "halaman" / "butir.json"), str(tmp_path / "label-ciri.json"), str(tmp_path / "ciri")])
    c = hc.utama(["terima", str(tmp_path / "halaman" / "butir.json"), str(tmp_path / "tidak-ada.json"), str(tmp_path / "ciri2")])

    layar = capsys.readouterr()
    assert (a, b, c) == (0, 0, 1)
    assert (tmp_path / "halaman" / "halaman.html").exists() and (tmp_path / "ciri" / "ringkasan-ciri.json").exists()
    assert "rahasia" not in layar.out + layar.err and "6 kartu" in layar.out
