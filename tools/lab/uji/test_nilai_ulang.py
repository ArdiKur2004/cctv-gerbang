"""Uji tools/lab/nilai_ulang.py: label dibetulkan dari jawaban owner, plat yang tak pasti dikeluarkan, pembaca dinilai
ulang dari bacaan tersimpan, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nilai_ulang as nu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "nilai_ulang.py"


def k(teks):
    return {"teks": teks, "golongan": "mobil", "kelompok": "mobil-terang", "berkas": [f"test/{teks}_1.png"]}


PEMBAGIAN = {"latih": [k("D9000AB")], "uji": [k("D1500X"), k("D1600X"), k("D1700X"), k("D1800X")]}
CURIGA = {"contoh": [{"nomor": 1, "teks": "D1500X", "usulan": "D2500X", "kelompok": "mobil-terang", "berkas": "test/D1500X_1.png"},
                     {"nomor": 2, "teks": "D1600X", "usulan": "D1600Y", "kelompok": "mobil-terang", "berkas": "test/D1600X_1.png"}]}
CONTOH = {"contoh": [{"nomor": 1, "teks": "D1700X", "kelompok": "mobil-terang", "berkas": "test/D1700X_1.png"},
                     {"nomor": 2, "teks": "D1500X", "kelompok": "mobil-terang", "berkas": "test/D1500X_1.png"}]}


def test_tulisan_b_yang_benar_mengganti_label_dan_kelompoknya():
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, {1}, set(), set())

    ganti = next(x for x in baru["uji"] if x.get("label_penerbit") == "D1500X")
    assert (ganti["teks"], ganti["kelompok"], ganti["golongan"]) == ("D2500X", "motor-terang", "motor")
    assert (hitung["dibetulkan"], hitung["dikeluarkan"]) == (1, 0)


def test_baris_yang_kedua_tulisannya_salah_dikeluarkan():
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, set(), {2}, set())

    assert "D1600X" not in [x["teks"] for x in baru["uji"]]
    assert hitung["dikeluarkan"] == 1


def test_label_salah_dari_lembar_contoh_dikeluarkan_kecuali_sudah_dibetulkan():
    # Baris 1 lembar contoh salah dan tak dibetulkan: keluar. Baris 2 salah tetapi dibetulkan lewat tulisan B.
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, {1}, set(), {1, 2})

    teks = [x["teks"] for x in baru["uji"]]
    assert "D1700X" not in teks and "D2500X" in teks
    assert hitung["dikeluarkan"] == 1


def test_label_baru_yang_sama_dengan_plat_latih_dikeluarkan():
    # K23: satu plat hanya di satu sisi (spec 8.3). Label yang dibetulkan bisa ternyata plat yang sudah ada di bahan latih.
    curiga = {"contoh": [{"nomor": 1, "teks": "D1500X", "usulan": "D9000AB", "kelompok": "mobil-terang", "berkas": "test/D1500X_1.png"}]}

    baru, hitung = nu.koreksi(PEMBAGIAN, curiga, CONTOH, {1}, set(), set())

    assert "D9000AB" not in [x["teks"] for x in baru["uji"]] and len(baru["uji"]) == 3
    assert (hitung["dibetulkan"], hitung["dikeluarkan_bocor"], hitung["plat_di_kedua_sisi"]) == (1, 1, 0)


@pytest.mark.parametrize("b_benar, keduanya, salah", [({1}, {1}, set()), ({9}, set(), set()), (set(), set(), {9})])
def test_jawaban_yang_tak_bisa_dipakai_ditolak(b_benar, keduanya, salah):
    with pytest.raises(nu.SalahPakai):
        nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, b_benar, keduanya, salah)


def tulis(tmp_path):
    for nama, isi in (("pembagian.json", PEMBAGIAN), ("curiga.json", CURIGA), ("contoh.json", CONTOH)):
        (tmp_path / nama).write_text(json.dumps(isi))
    bacaan = (("D1500X", "D2500X"), ("D1600X", "D1600X"), ("D1700X", "D1700X"), ("D1800X", "D1800Y"))
    (tmp_path / "hasil.jsonl").write_text("".join(json.dumps({"berkas": f"test/{t}_1.png", "bacaan": b}) + "\n" for t, b in bacaan))
    return [str(tmp_path / n) for n in ("pembagian.json", "curiga.json", "contoh.json")] + [str(tmp_path / "keluar")]


def test_pembaca_dinilai_ulang_terhadap_label_baru(tmp_path):
    argumen = tulis(tmp_path) + ["--b-benar", "1", "--salah-contoh", "1", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    assert nu.utama(argumen) == 0

    r = json.loads((tmp_path / "keluar/ringkasan-koreksi.json").read_text())["pembaca"]["tiruan"]
    assert r["motor-terang"]["kedatangan_benar"] == 1  # label dibetulkan menjadi bacaan yang benar
    assert (r["mobil-terang"]["kedatangan"], r["mobil-terang"]["kedatangan_benar"]) == (2, 1)  # satu dikeluarkan


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    argumen = tulis(tmp_path) + ["--b-benar", "1", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    hasil = subprocess.run([sys.executable, str(SKRIP), *argumen], capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), *argumen, "--keduanya-salah", "1"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    for larangan in ("1500", "2500", "1600", "1800"):
        assert larangan not in hasil.stdout + (tmp_path / "keluar/ringkasan-koreksi.json").read_text()
    assert salah.returncode == 2 and "SALAH PAKAI" in salah.stdout


PEMBAGIAN_L = {"latih": [k("D9000AB"), k("D9100AB")], "uji": [k("D1500X")]}
CURIGA_L = {"contoh": [{"nomor": 1, "teks": "D9000AB", "usulan": "D9000AC", "kelompok": "mobil-terang", "berkas": "test/D9000AB_1.png"},
                       {"nomor": 2, "teks": "D9100AB", "usulan": "D1500X", "kelompok": "mobil-terang", "berkas": "test/D9100AB_1.png"}]}


def test_sisi_latih_dibetulkan_dan_yang_menjadi_plat_uji_dikeluarkan(tmp_path):
    # K24: label latih yang dibetulkan bisa ternyata plat di set uji; yang dikeluarkan bahan latihnya, set uji tetap.
    for nama, isi in (("pembagian.json", PEMBAGIAN_L), ("curiga.json", CURIGA_L), ("contoh.json", CONTOH)):
        (tmp_path / nama).write_text(json.dumps(isi))
    (tmp_path / "hasil.jsonl").write_text(json.dumps({"berkas": "test/D9000AB_1.png", "bacaan": "D9000AC"}) + "\n")
    argumen = [str(tmp_path / n) for n in ("pembagian.json", "curiga.json", "contoh.json")] + [
        str(tmp_path / "keluar"), "--sisi", "latih", "--b-benar", "1,2", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    assert nu.utama(argumen) == 0

    baru = json.loads((tmp_path / "keluar/pembagian-koreksi.json").read_text())
    assert [x["teks"] for x in baru["latih"]] == ["D9000AC"] and [x["teks"] for x in baru["uji"]] == ["D1500X"]
    r = json.loads((tmp_path / "keluar/ringkasan-koreksi.json").read_text())
    assert (r["dibetulkan"], r["dikeluarkan_bocor"], r["plat_di_kedua_sisi"], r["sisi"]) == (2, 1, 0, "latih")
    assert r["pembaca"]["tiruan"]["mobil-terang"]["kedatangan_benar"] == 1


def test_layar_menyebut_sisi_yang_dibetulkan(tmp_path, capsys):
    # Ditemukan saat Rencana 7 dijalankan: hitungan sisi latih dicetak dengan tulisan "plat latih" dan "kedatangan uji".
    for nama, isi in (("pembagian.json", PEMBAGIAN_L), ("curiga.json", CURIGA_L), ("contoh.json", CONTOH)):
        (tmp_path / nama).write_text(json.dumps(isi))
    (tmp_path / "hasil.jsonl").write_text(json.dumps({"berkas": "test/D9000AB_1.png", "bacaan": "D9000AC"}) + "\n")
    argumen = [str(tmp_path / n) for n in ("pembagian.json", "curiga.json", "contoh.json")] + [
        str(tmp_path / "keluar"), "--sisi", "latih", "--b-benar", "1,2", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    nu.utama(argumen)

    cetak = capsys.readouterr().out
    assert "sama dengan plat uji 1" in cetak and "kedatangan latih {" in cetak


def test_lembar_contoh_tidak_berlaku_untuk_sisi_latih():
    with pytest.raises(nu.SalahPakai, match="set uji"):
        nu.koreksi(PEMBAGIAN_L, CURIGA_L, CONTOH, {1}, set(), {1}, sisi="latih")
