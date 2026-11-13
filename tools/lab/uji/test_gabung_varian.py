"""Uji tools/lab/gabung_varian.py (Rencana 23 Bagian B): varian penggabungan bacaan per kedatangan (V0 sekarang, V1 gambar paling
tajam, V2 per huruf, V3 keduanya), penilaian dari label lembar, aturan memilih, dan CLI tanpa model."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gabung_varian as gv  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "gabung_varian.py"


def b(teks, ketajaman=100.0, yakin=0.8, gambar=0):
    """Satu bacaan seperti di bacaan.jsonl: [gambar, teks, yakin_baca, ketajaman, tinggi]."""
    return [gambar, teks, yakin, ketajaman, 30]


def test_v0_sama_dengan_gabung_rantai():
    bacaan = [b("B1234XY"), b("B1234XY"), b("B1234XV")]

    assert gv.varian("V0", bacaan) == {"teks": "B1234XY", "status": "yakin"}


def test_v2_per_huruf_membetulkan_satu_huruf_salah_di_posisi_berbeda():
    bacaan = [b("B1234XY"), b("B1294XY"), b("B1234XV")]

    assert gv.varian("V0", bacaan)["status"] == "ragu"  # tiap teks utuh hanya didukung satu bacaan
    assert gv.varian("V2", bacaan) == {"teks": "B1234XY", "status": "yakin"}


def test_v2_ragu_bila_tiap_posisi_tidak_cukup_didukung():
    assert gv.varian("V2", [b("B1234XY"), b("D5678AB"), b("F9012CD")])["status"] == "ragu"
    assert gv.varian("V2", [b("12AB"), b("XYZ")]) == {"teks": "", "status": "ragu"}  # tidak ada bacaan sesuai pola


def test_v1_tajam_memakai_separuh_paling_tajam():
    bacaan = [b("B1234XY", 300), b("B1234XY", 250), b("B1234XV", 20), b("B1284XY", 10)]

    assert gv.varian("V0", bacaan)["status"] == "ragu"  # 2 dari 4 sah = 50% < 60%
    assert gv.varian("V1", bacaan) == {"teks": "B1234XY", "status": "yakin"}
    assert gv.varian("V3", bacaan) == {"teks": "B1234XY", "status": "yakin"}


def lembar_(baris):
    return {"baris": [{"nomor": i, "video": "v.mp4", "kedatangan": i, "teks": t, "status": s} for i, (t, s) in enumerate(baris, 1)]}


def test_nilai_varian_dari_label_lembar():
    bacaan = {("v.mp4", 1): [b("B1234XY"), b("B1294XY"), b("B1234XV")],  # benar, V0 ragu, V2 yakin
              ("v.mp4", 2): [b("D5678AB"), b("D5678AB")],  # bukan plat, yakin di semua varian
              ("v.mp4", 3): [b("F9012CD"), b("F9012CD"), b("F9013CD")]}  # benar, yakin di semua varian
    lembar = lembar_([("B1234XY", "ragu"), ("D5678AB", "yakin"), ("F9012CD", "yakin")])

    h = gv.nilai(bacaan, lembar, bukan_plat={2}, buram=set(), salah=set())

    assert h["V0"] == {"benar": 2, "benar_yakin": 1, "benar_ragu": 1, "berubah": 0, "yakin_bukan_plat": 1, "yakin_buram": 0,
                       "yakin_salah": 0, "salah_berubah": 0}
    assert h["V2"]["benar_yakin"] == 2 and h["V2"]["berubah"] == 0


def test_bacaan_salah_yang_berubah_dipisah_dari_yang_tetap_salah():
    bacaan = {("v.mp4", 1): [b("B1234XY"), b("B1294XY"), b("B1234XV")],  # lembar: salah (teks lama B1294XY)
              ("v.mp4", 2): [b("D5678AB"), b("D5678AB")]}  # lembar: salah, teks tetap dan yakin
    lembar = lembar_([("B1294XY", "ragu"), ("D5678AB", "yakin")])

    h = gv.nilai(bacaan, lembar, bukan_plat=set(), buram=set(), salah={1, 2})

    # V2 mengubah teks baris 1: belum diketahui benar atau salah, jadi tidak dihitung "yakin di salah".
    assert (h["V2"]["salah_berubah"], h["V2"]["yakin_salah"]) == (1, 1)
    assert (h["V0"]["salah_berubah"], h["V0"]["yakin_salah"]) == (1, 1)  # V0 memilih teks pertama di antara yang seri


def test_pilih_menurut_aturan():
    dasar = {"benar": 10, "benar_ragu": 0, "yakin_buram": 0, "yakin_salah": 0}
    hasil = {"V0": {**dasar, "benar_yakin": 5, "berubah": 0, "yakin_bukan_plat": 2},
             "V1": {**dasar, "benar_yakin": 7, "berubah": 0, "yakin_bukan_plat": 3},  # yakin bukan plat bertambah: gugur
             "V2": {**dasar, "benar_yakin": 8, "berubah": 1, "yakin_bukan_plat": 2},  # ada bacaan benar yang berubah: gugur
             "V3": {**dasar, "benar_yakin": 6, "berubah": 0, "yakin_bukan_plat": 2}}

    assert gv.pilih(hasil) == "V3"
    hasil["V3"]["benar_yakin"] = 5
    assert gv.pilih(hasil) == "V0"  # seri dengan V0: V0 tetap


def test_cli_nilai_tanpa_model_dan_tanpa_teks_di_layar(tmp_path):
    (tmp_path / "bacaan.jsonl").write_text(json.dumps({"video": "v.mp4", "kedatangan": 1,
                                                       "bacaan": [b("B1234XY"), b("B1294XY"), b("B1234XV")]}) + "\n")
    (tmp_path / "lembar.json").write_text(json.dumps(lembar_([("B1234XY", "ragu")])))

    hasil = subprocess.run([sys.executable, str(SKRIP), "nilai", str(tmp_path / "bacaan.jsonl"), str(tmp_path / "lembar.json"),
                            str(tmp_path / "keluar.json")], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    isi = json.loads((tmp_path / "keluar.json").read_text())
    assert isi["varian"]["V2"]["benar_yakin"] == 1 and isi["terpilih"] in {"V0", "V1", "V2", "V3"}
    assert "B1234" not in hasil.stdout + hasil.stderr + (tmp_path / "keluar.json").read_text()


def test_terapkan_varian_ke_hasil_rantai_tanpa_teks_di_layar(tmp_path):
    asal = tmp_path / "rantai"
    (asal / "potongan").mkdir(parents=True)
    (asal / "potongan" / "v-1.png").write_bytes(b"png")
    kedatangan = [{"video": "v.mp4", "nomor": 1, "teks": "B1234XY", "status": "ragu", "potongan": "v-1.png", "kategori": "siang"},
                  {"video": "v.mp4", "nomor": 2, "teks": "D5678AB", "status": "yakin", "potongan": "v-1.png", "kategori": "siang"}]
    (asal / "kedatangan.jsonl").write_text("".join(json.dumps(k) + "\n" for k in kedatangan))
    (asal / "bacaan.jsonl").write_text(
        json.dumps({"video": "v.mp4", "kedatangan": 1, "bacaan": [b("B1234XY", 300), b("B1234XY", 250), b("B1234XV", 20),
                                                                     b("B1284XY", 10)]}) + "\n" +
        json.dumps({"video": "v.mp4", "kedatangan": 2, "bacaan": [b("D5678AB"), b("D5678AB")]}) + "\n")

    hasil = subprocess.run([sys.executable, str(SKRIP), "terapkan", str(asal), str(tmp_path / "v1"), "--varian", "V1"],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    baru = [json.loads(x) for x in (tmp_path / "v1" / "kedatangan.jsonl").read_text().splitlines()]
    assert [(k["teks"], k["status"], k["kategori"]) for k in baru] == [("B1234XY", "yakin", "siang"), ("D5678AB", "yakin", "siang")]
    assert (tmp_path / "v1" / "potongan" / "v-1.png").exists()
    ringkas = json.loads((tmp_path / "v1" / "ringkasan-varian.json").read_text())
    assert ringkas == {"varian": "V1", "kedatangan": 2, "teks_berubah": 0, "status_berubah": 1}
    assert "B1234" not in hasil.stdout + hasil.stderr
