"""Uji tools/lab/latih_fpo.py yang tidak butuh Keras (gerbang lab biasa): bahan CSV hanya dari sisi latih, validasi sama
dengan Rencana 8, jalur gambar mengikuti cara fast-plate-ocr, kolom wilayah selalu ada, label di luar jangkauan model
ditolak tanpa mencetak teksnya, manifes mencatat bobot awal, dan layar tanpa nomor plat."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import latih_fpo as lf  # noqa: E402
from mesin_baca import bagi_validasi  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "latih_fpo.py"
BAHAN = Path(__file__).resolve().parents[3] / "data-asal" / "bahan.json"
LATIH = [f"B{1000 + i}AB" for i in range(40)]  # 2 di antaranya jatuh ke validasi (B1011AB, B1017AB)
UJI = ["D7777XY", "F8888ZZ"]


def gambar_plat(teks):
    kanvas = np.full((60, 200, 3), 255, np.uint8)
    cv2.putText(kanvas, teks, (8, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    return kanvas


def buat(tmp_path, latih=LATIH, uji=UJI):
    folder = tmp_path / "gambar"
    pembagian = {}
    for sisi, daftar in (("latih", latih), ("uji", uji)):
        pembagian[sisi] = []
        for t in daftar:
            berkas = []
            for i in range(2):
                nama = f"{sisi}/{t}_{i}.png"
                (folder / sisi).mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(folder / nama), gambar_plat(t))
                berkas.append(nama)
            pembagian[sisi].append({"teks": t, "kelompok": "mobil-terang", "berkas": berkas})
    return pembagian, folder


def baca_csv(berkas):
    with open(berkas, newline="") as f:
        return list(csv.DictReader(f))


def test_bahan_hanya_dari_sisi_latih_dan_validasinya_sama_dengan_rencana_8(tmp_path):
    pembagian, folder = buat(tmp_path)

    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    latih = {b["plate_text"] for b in baca_csv(tmp_path / "keluar/latih.csv")}
    validasi = {b["plate_text"] for b in baca_csv(tmp_path / "keluar/validasi.csv")}
    inti, val = bagi_validasi(pembagian["latih"])
    assert latih == {k["teks"] for k in inti} and validasi == {k["teks"] for k in val}
    assert validasi and not (latih | validasi) & set(UJI)


def test_jalur_gambar_mengikuti_cara_fast_plate_ocr(tmp_path):
    # fast-plate-ocr (train/data/dataset.py baris 36-38) menyambung folder CSV + os.sep + jalur gambar.
    pembagian, folder = buat(tmp_path)
    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    for nama in ("latih.csv", "validasi.csv"):
        berkas = tmp_path / "keluar" / nama
        for b in baca_csv(berkas):
            assert not os.path.isabs(b["image_path"])
            assert os.path.isfile(os.path.dirname(os.path.realpath(berkas)) + os.sep + b["image_path"])


def test_kolom_wilayah_selalu_ada(tmp_path):
    # Tanpa kolom plate_region, kepala wilayah model dibuang tanpa galat (Rencana 9: 170 dari 192 tensor).
    pembagian, folder = buat(tmp_path)
    lf.siapkan(pembagian, folder, tmp_path / "keluar")

    baris = baca_csv(tmp_path / "keluar/latih.csv")
    assert list(baris[0]) == ["image_path", "plate_text", "plate_region"]
    assert {b["plate_region"] for b in baris} == {"Indonesia"}


def test_gambar_tak_terbaca_dilewati_dan_dihitung(tmp_path):
    pembagian, folder = buat(tmp_path)
    (folder / pembagian["latih"][0]["berkas"][0]).write_bytes(b"bukan gambar")

    hitung = lf.siapkan(pembagian, folder, tmp_path / "keluar")

    assert hitung["tak_terbaca"] == 1
    assert hitung["gambar"]["latih"] + hitung["gambar"]["validasi"] == 2 * len(LATIH) - 1


@pytest.mark.parametrize("teks", ["B1234567890X", "B-1234"])
def test_label_di_luar_jangkauan_model_ditolak_tanpa_mencetak_teksnya(tmp_path, teks):
    pembagian, folder = buat(tmp_path, latih=LATIH[:3] + [teks])

    with pytest.raises(ValueError) as galat:
        lf.siapkan(pembagian, folder, tmp_path / "keluar")

    assert teks not in str(galat.value) and "1234" not in str(galat.value)


def test_manifes_mencatat_bobot_awal_dan_vonisnya_mengikuti_k47():
    # Dibalik 19 Okt (K47): dulu uji ini mengunci "bobot terbitan bukan BOLEH-PRODUK, jadi mesinnya RISET-SAJA". Owner menerima
    # pernyataan pemelihara di GitHub sebagai izin bobot. Bobot awal TETAP tercatat sebagai bahan, sehingga bila K47 dibalik, tanda
    # mesin ikut turun lewat tools/periksa-jualan.mjs.
    meta = lf.manifes({"plat": {}, "gambar": {}, "tak_terbaca": 0}, "a" * 64, "b" * 64, {}, {})
    bahan = {b["id"]: b for b in json.loads(BAHAN.read_text())["bahan"]}

    assert meta["tujuan"] == "belajar" and meta["bahan"] == ["dataset-indo-alpr", "bobot-fast-plate-ocr"]
    assert bahan["dataset-indo-alpr"]["vonis"] == "BOLEH-PRODUK" and bahan["bobot-fast-plate-ocr"]["vonis"] == "BOLEH-PRODUK"
    assert "K47" in bahan["bobot-fast-plate-ocr"]["bukti_lisensi"]


def test_manifes_jualan_dari_nol_hanya_bahan_boleh_produk():
    # Rencana 24 Task 6: tanpa bobot terbitan, bahan mesin = bahan dari siapkan.json (bahan_pembaca), semuanya BOLEH-PRODUK.
    hitung = {"sumber": {}, "gambar": {}, "bahan": ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan"]}
    meta = lf.manifes_jualan(hitung, "a" * 64, {}, {}, "pembaca-jualan-p2")
    vonis = {b["id"]: b["vonis"] for b in json.loads(BAHAN.read_text())["bahan"]}

    assert (meta["nama"], meta["tujuan"], meta["sha256_bobot_awal"], meta["bobot_awal"]) == ("pembaca-jualan-p2", "jualan", None, None)
    assert meta["bahan"] == hitung["bahan"] and all(vonis[b] == "BOLEH-PRODUK" for b in meta["bahan"])


def mesin_sendiri(folder, tujuan="jualan", sha=None):
    folder.mkdir()
    (folder / "mesin.keras").write_bytes(b"bobot-sendiri")
    (folder / "mesin.json").write_text(json.dumps({"nama": "pembaca-jualan-p3a", "tujuan": tujuan, "bahan": ["plat-buatan"],
                                                   "sha256_mesin": sha or lf.sha256_berkas(folder / "mesin.keras")}))


def test_bobot_awal_sendiri_diperiksa_dan_bahannya_ikut_tercatat(tmp_path):
    mesin_sendiri(tmp_path / "awal")

    jalur, awal = lf.bobot_awal_sendiri(tmp_path / "awal")
    meta = lf.manifes_jualan({"bahan": ["dataset-indo-alpr", "tangkapan-owner"]}, "c" * 64, {}, {}, "pembaca-jualan-p3", awal)

    assert jalur == tmp_path / "awal" / "mesin.keras"
    assert meta["bahan"] == ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan"]
    assert meta["bobot_awal"] == "pembaca-jualan-p3a" and meta["sha256_bobot_awal"] == lf.sha256_berkas(jalur)


@pytest.mark.parametrize("cacat", ["belajar", "berubah"])
def test_bobot_awal_sendiri_ditolak_bila_bukan_mesin_jualan_atau_berubah(tmp_path, cacat):
    from model_terkunci import ModelDitolak

    mesin_sendiri(tmp_path / "awal", tujuan="belajar" if cacat == "belajar" else "jualan",
                  sha="0" * 64 if cacat == "berubah" else None)

    with pytest.raises(ModelDitolak):
        lf.bobot_awal_sendiri(tmp_path / "awal")


def test_baris_perintah_siapkan_tanpa_nomor_plat_di_layar(tmp_path):
    pembagian, folder = buat(tmp_path)
    (folder / pembagian["latih"][0]["berkas"][0]).unlink()
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))

    hasil = subprocess.run([sys.executable, str(SKRIP), "siapkan", str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    layar = hasil.stdout + hasil.stderr
    assert hasil.returncode == 0, layar
    assert "tak terbaca 1" in layar
    assert not any(t in layar for t in LATIH + UJI)


def test_ketepatan_per_sumber_memisah_tangkapan_dari_indo_alpr(tmp_path):
    # Rencana 25 Task 6: aturan memilih menilai potongan tangkapan dan INDO-ALPR terpisah; "potongan/" = tangkapan, seperti
    # banding-pembaca-24.py.
    for nama in ("a.png", "potongan/t-g0001-1.png", "potongan/t-g0002-1.png"):
        (tmp_path / nama).parent.mkdir(exist_ok=True)
        cv2.imwrite(str(tmp_path / nama), np.full((20, 60, 3), 200, np.uint8))
    with open(tmp_path / "validasi.csv", "w", newline="") as f:
        csv.writer(f).writerows([["image_path", "plate_text", "plate_region"], ["a.png", "B1XY", "Indonesia"],
                                 ["potongan/t-g0001-1.png", "B1XY", "Indonesia"], ["potongan/t-g0002-1.png", "D2AB", "Indonesia"]])

    r = lf.ketepatan_per_sumber(lambda g: "B1XY", tmp_path / "validasi.csv")

    # Rencana 30: "tangkapan" tetap semua "potongan/", ditambah pecahannya (label t-, rantai c, geser g).
    assert r == {"indo_alpr": {"gambar": 1, "benar": 1}, "tangkapan": {"gambar": 2, "benar": 1},
                 "tangkapan_label": {"gambar": 2, "benar": 1}, "tangkapan_rantai": {"gambar": 0, "benar": 0},
                 "tangkapan_geser": {"gambar": 0, "benar": 0}, "semua": {"gambar": 3, "benar": 2}}


def test_ketepatan_per_sumber_memecah_label_rantai_dan_geser_tanpa_menghitung_dua_kali(tmp_path):
    nama = ["a.png", "potongan/t-g0001-1.png", "potongan/c1-g0001-1.png", "potongan/g3-g0001-1.png", "potongan/000056.png"]
    for n in nama:
        (tmp_path / n).parent.mkdir(exist_ok=True)
        cv2.imwrite(str(tmp_path / n), np.full((20, 60, 3), 200, np.uint8))
    with open(tmp_path / "validasi.csv", "w", newline="") as f:
        csv.writer(f).writerows([["image_path", "plate_text", "plate_region"]] + [[n, "B1XY", "Indonesia"] for n in nama])

    r = lf.ketepatan_per_sumber(lambda g: "B1XY", tmp_path / "validasi.csv")

    assert r["tangkapan"] == {"gambar": 4, "benar": 4} and r["indo_alpr"] == {"gambar": 1, "benar": 1}
    assert [r[k]["gambar"] for k in ("tangkapan_label", "tangkapan_rantai", "tangkapan_geser")] == [1, 1, 1]
    assert r["semua"] == {"gambar": 5, "benar": 5}  # pecahan tidak ikut dijumlah lagi


def tulis_csv(berkas, isi):
    with open(berkas, "w", newline="") as f:
        csv.writer(f).writerows([["image_path", "plate_text", "plate_region"]] + [[*b, "Indonesia"] for b in isi])


def latih_lanjut_palsu(tmp_path, monkeypatch, ada_indo):
    """latih_lanjut dengan perintah latih fast-plate-ocr dan Keras dipalsukan (gerbang lab biasa tanpa Keras): perintah yang sampai ke
    main_cli dicatat, best.keras dan training_log.csv palsu ditulis, dan pembaca selalu membaca "B1XY"."""
    import types

    mesin_fpo(tmp_path / "fpo")
    bahan = tmp_path / "bahan"
    (bahan / "potongan").mkdir(parents=True)
    for n in ("a.png", "potongan/t-g0001-1.png"):
        cv2.imwrite(str(bahan / n), np.full((20, 60, 3), 200, np.uint8))
    tulis_csv(bahan / "latih.csv", [["a.png", "B1XY"]])
    tulis_csv(bahan / "validasi.csv", [["potongan/t-g0001-1.png", "B1XY"]])
    if ada_indo:
        tulis_csv(bahan / "validasi-indo.csv", [["a.png", "B1XY"], ["a.png", "D2AB"]])
    (bahan / "siapkan.json").write_text(json.dumps({"bahan": ["dataset-indo-alpr", "tangkapan-owner"], "wilayah": True}))
    perintah = []

    def main_cli(argumen, standalone_mode):
        perintah.append(list(argumen))
        jalan = Path(argumen[argumen.index("--output-dir") + 1]) / "jalan"
        jalan.mkdir(parents=True)
        (jalan / "best.keras").write_bytes(b"bobot-baru")
        (jalan / "training_log.csv").write_text("epoch,val_plate_acc,val_plate_char_acc\n0,0.5,0.6\n1,0.7,0.8\n")

    cli = types.ModuleType("fast_plate_ocr.cli.cli")
    cli.main_cli = main_cli
    for nama, modul in (("fast_plate_ocr", types.ModuleType("fast_plate_ocr")), ("fast_plate_ocr.cli",
                        types.ModuleType("fast_plate_ocr.cli")), ("fast_plate_ocr.cli.cli", cli)):
        monkeypatch.setitem(sys.modules, nama, modul)
    monkeypatch.setattr(lf, "jalur_terkunci", lambda u: {"model": tmp_path / "m.yaml", "plat": tmp_path / "p.yaml",
                                                          "keras": tmp_path / "x.keras"})
    monkeypatch.setattr(lf, "siapkan_torch", lambda: None)
    monkeypatch.setattr(lf, "bobot_utuh", lambda jalur: (192, 192))
    monkeypatch.setattr(lf, "PembacaKeras", lambda keras, plat: (lambda g: "B1XY"))
    return bahan, perintah


@pytest.mark.parametrize("laju,ada_indo", [(1e-4, True), (None, False)])
def test_latih_lanjut_meneruskan_laju_ke_perintah_latih_dan_mengukur_validasi_indo(tmp_path, monkeypatch, laju, ada_indo):
    # Rencana 30: laju belajar 0,0001 untuk melatih lanjut (Rencana 25 memakai bawaan 0,001); INDO-ALPR validasi di berkas terpisah
    # hanya menjadi penjaga, diukur sebelum dan sesudah. Tanpa laju: perintah latih memakai bawaan pembuatnya, seperti Rencana 25.
    bahan, perintah = latih_lanjut_palsu(tmp_path, monkeypatch, ada_indo)

    meta = lf.latih_lanjut(bahan, tmp_path / "unduhan", tmp_path / "fpo", zaman=3, laju=laju, nama="uji-r3")

    (argumen,) = perintah
    if laju is None:
        assert "--lr" not in argumen and meta["latihan"]["laju"] is None
    else:
        assert argumen[argumen.index("--lr") + 1] == "0.0001" and meta["latihan"]["laju"] == 0.0001
    assert argumen[argumen.index("--val-annotations") + 1] == str(bahan / "validasi.csv")
    assert meta["validasi"]["akhir"]["tangkapan_label"] == {"gambar": 1, "benar": 1}
    if ada_indo:
        assert meta["validasi"]["indo_awal"] == meta["validasi"]["indo_akhir"] == {"gambar": 2, "benar": 1}
    else:
        assert "indo_awal" not in meta["validasi"]
    assert (bahan / "mesin.keras").read_bytes() == b"bobot-baru" and meta["latihan"]["zaman_terbaik"] == 2


def test_cli_latih_lanjut_laju_sampai_ke_latih_lanjut(tmp_path, monkeypatch):
    dipanggil = {}

    def palsu(folder, unduhan, bobot_awal, zaman, benih, ukuran_angkatan, nama, laju=None):
        dipanggil.update(zaman=zaman, nama=nama, laju=laju)
        v = {"gambar": 1, "benar": 1}
        return {"nama": nama, "tujuan": "jualan", "bahan": [], "latihan": {"zaman_terbaik": 1, "zaman_berjalan": 1,
                                                                            "bobot_termuat": "192/192"},
                "validasi": {"awal": {"indo_alpr": v, "tangkapan": v}, "akhir": {"indo_alpr": v, "tangkapan": v},
                             "indo_awal": v, "indo_akhir": v}}

    monkeypatch.setattr(lf, "latih_lanjut", palsu)

    kode = lf.utama(["latih-lanjut", str(tmp_path / "bahan"), str(tmp_path / "unduhan"), "--bobot-awal", str(tmp_path / "fpo"),
                     "--zaman", "30", "--laju", "0.0001", "--nama", "pembaca-lanjut-r3"])

    assert kode in (0, None) and dipanggil == {"zaman": 30, "nama": "pembaca-lanjut-r3", "laju": 0.0001}


def mesin_fpo(folder, sha=None):
    folder.mkdir()
    (folder / "mesin.keras").write_bytes(b"bobot-fpo-indo")
    (folder / "mesin.json").write_text(json.dumps({"nama": "fpo-indo-1", "tujuan": "belajar",
                                                   "bahan": ["dataset-indo-alpr", "bobot-fast-plate-ocr"],
                                                   "sha256_mesin": sha or lf.sha256_berkas(folder / "mesin.keras")}))


def test_mesin_awal_lanjut_diperiksa_dan_manifesnya_jualan_dengan_bahan_gabungan(tmp_path):
    mesin_fpo(tmp_path / "fpo")

    jalur, awal = lf.mesin_awal_lanjut(tmp_path / "fpo")
    meta = lf.manifes_lanjut({"bahan": ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan"], "wilayah": True}, "c" * 64, {}, {},
                             "pembaca-lanjut-r1", awal)
    vonis = {b["id"]: b["vonis"] for b in json.loads(BAHAN.read_text())["bahan"]}

    assert jalur == tmp_path / "fpo" / "mesin.keras"
    assert (meta["nama"], meta["tujuan"], meta["bobot_awal"]) == ("pembaca-lanjut-r1", "jualan", "fpo-indo-1")
    assert meta["sha256_bobot_awal"] == lf.sha256_berkas(jalur)
    assert meta["bahan"] == ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan", "bobot-fast-plate-ocr"]
    assert all(vonis[b] == "BOLEH-PRODUK" for b in meta["bahan"])  # sejak K47; bila dibalik, periksa-jualan menolak


def test_mesin_awal_lanjut_yang_berubah_ditolak(tmp_path):
    from model_terkunci import ModelDitolak

    mesin_fpo(tmp_path / "fpo", sha="0" * 64)

    with pytest.raises(ModelDitolak, match="SHA-256"):
        lf.mesin_awal_lanjut(tmp_path / "fpo")


def test_latih_lanjut_menolak_bahan_tanpa_wilayah_sebelum_memuat_apa_pun(tmp_path):
    # fpo-indo-1 berkepala wilayah: bahan tanpa kolom plate_region akan membuang kepala itu diam-diam.
    mesin_fpo(tmp_path / "fpo")
    (tmp_path / "bahan").mkdir()
    (tmp_path / "bahan" / "siapkan.json").write_text(json.dumps({"bahan": ["tangkapan-owner"], "wilayah": False}))

    with pytest.raises(ValueError, match="wilayah"):
        lf.latih_lanjut(tmp_path / "bahan", tmp_path / "tidak-ada", tmp_path / "fpo", zaman=1)


def test_pembaca_menolak_mesin_yang_berubah_sebelum_memuat_keras(tmp_path):
    from model_terkunci import ModelDitolak

    (tmp_path / "mesin.keras").write_bytes(b"ditukar")
    (tmp_path / "mesin.json").write_text(json.dumps({"sha256_mesin": "0" * 64}))

    with pytest.raises(ModelDitolak, match="SHA-256"):
        lf.PembacaMesinFpo(tmp_path, tmp_path / "unduhan")
