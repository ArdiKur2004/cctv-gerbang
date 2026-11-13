"""Uji tools/lab/bahan_pembaca.py (Rencana 24 Task 5): bahan pembaca jualan dari INDO-ALPR (sisi latih), potongan tangkapan owner
(sisi latih saja), dan plat buatan, dalam format CSV fast-plate-ocr tanpa kolom wilayah. Sisi uji tidak pernah masuk, plat tak
terbaca tidak menjadi label, plat buatan hanya masuk latih, dan nama berkas asli tidak muncul."""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bahan_pembaca as bp  # noqa: E402
from mesin_baca import bagi_validasi  # noqa: E402


def teks_indo(validasi):
    """Teks plat buatan yang jatuh ke sisi validasi (atau inti) menurut mesin_baca.bagi_validasi."""
    return next(t for t in (f"B{i}XY" for i in range(1, 500)) if bool(bagi_validasi([{"teks": t}])[1]) == validasi)


def siapkan_bahan(tmp_path, dengan_buatan=True):
    indo = tmp_path / "indo"
    indo.mkdir()
    pembagian = {"latih": [], "uji": []}
    for sisi, t in (("latih", teks_indo(False)), ("latih", teks_indo(True)), ("uji", "AB1C")):
        cv2.imwrite(str(indo / f"{t}_1.png"), np.full((40, 120, 3), 200, np.uint8))
        pembagian[sisi].append({"teks": t, "berkas": [f"{t}_1.png"], "kelompok": "mobil-terang"})
    (tmp_path / "pembagian.json").write_text(json.dumps(pembagian))
    folder = tmp_path / "capture" / "capture cctv mobil"
    folder.mkdir(parents=True)
    peta, gambar = {}, {}
    for i in range(1, 13):
        g = f"g{i:04d}"
        cv2.imwrite(str(folder / f"rahasia-{i}.png"), np.full((180, 320, 3), 100, np.uint8))
        peta[g] = f"capture cctv mobil/rahasia-{i}.png"
        gambar[g] = {"kelompok": "mobil", "sisi": "uji" if i > 10 else "latih", "bukan_plat": [], "plat_tanpa_label": 0, "plat": [
            {"kotak": [100, 100, 160, 120], "teks": f"D{i}AB", "tak_terbaca": False, "asal": "lembar"},
            {"kotak": [10, 10, 40, 20], "teks": None, "tak_terbaca": True, "asal": "lembar"}]}
    (tmp_path / "peta.json").write_text(json.dumps(peta))
    (tmp_path / "label.json").write_text(json.dumps({"gambar": gambar, "dikeluarkan": {}}))
    if not dengan_buatan:
        return indo, None
    buatan = tmp_path / "buatan"
    (buatan / "gambar").mkdir(parents=True)
    with open(buatan / "label.csv", "w", newline="") as f:
        tulis = csv.writer(f)
        tulis.writerow(["berkas", "teks", "jenis", "warna", "kondisi"])
        for i in range(3):
            cv2.imwrite(str(buatan / "gambar" / f"{i:06d}.png"), np.full((64, 200, 3), 255, np.uint8))
            tulis.writerow([f"{i:06d}.png", f"Z{i + 1}Q", "mobil", "putih", "bersih"])
    return indo, buatan


def baca_csv(berkas):
    with open(berkas, newline="") as f:
        return list(csv.DictReader(f))


def jalankan(tmp_path, dengan_buatan=True):
    indo, buatan = siapkan_bahan(tmp_path, dengan_buatan)
    return bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                      tmp_path / "keluar", buatan)


def test_bahan_dari_tiga_sumber_tanpa_sisi_uji(tmp_path):
    r = jalankan(tmp_path)

    keluar = tmp_path / "keluar"
    latih, validasi = baca_csv(keluar / "latih.csv"), baca_csv(keluar / "validasi.csv")
    assert list(latih[0]) == ["image_path", "plate_text"]  # tanpa kolom wilayah: model tanpa kepala wilayah
    t_latih, t_val = {b["plate_text"] for b in latih}, {b["plate_text"] for b in validasi}
    assert teks_indo(False) in t_latih and teks_indo(True) in t_val and "AB1C" not in t_latih | t_val
    tangkap = {f"D{i}AB" for i in range(1, 11)}
    harap_val = {f"D{i}AB" for i in range(1, 11) if bp.validasi_tangkapan(f"g{i:04d}", 1)}
    assert harap_val and harap_val != tangkap  # bahan uji memang mengisi kedua sisi
    assert t_val & tangkap == harap_val and t_latih & tangkap == tangkap - harap_val
    assert not {"D11AB", "D12AB"} & (t_latih | t_val)  # tangkapan uji tidak pernah masuk
    assert {"Z1Q", "Z2Q", "Z3Q"} <= t_latih and not {"Z1Q", "Z2Q", "Z3Q"} & t_val
    assert all((keluar / b["image_path"]).exists() for b in latih + validasi)
    assert r["bahan"] == ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan"]
    assert r["sumber"]["tangkapan"] == {"latih": 10 - len(harap_val), "validasi": len(harap_val)}
    assert r["sumber"]["plat_buatan"] == {"latih": 3}


def test_tanpa_plat_buatan_bahannya_dua(tmp_path):
    r = jalankan(tmp_path, dengan_buatan=False)

    assert r["bahan"] == ["dataset-indo-alpr", "tangkapan-owner"] and r["sumber"]["plat_buatan"] == {"latih": 0}
    assert json.loads((tmp_path / "keluar" / "siapkan.json").read_text())["bahan"] == r["bahan"]


def test_latih_hanya_buatan_untuk_tahap_pralatih(tmp_path):
    # Calon P3 tahap 1: latih hanya plat buatan; validasi tetap bahan nyata, dan bahan nyata tetap tercatat karena ikut memilih zaman.
    indo, buatan = siapkan_bahan(tmp_path)

    r = bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                   tmp_path / "keluar", buatan, latih_hanya_buatan=True)

    assert {b["plate_text"] for b in baca_csv(tmp_path / "keluar" / "latih.csv")} == {"Z1Q", "Z2Q", "Z3Q"}
    assert teks_indo(True) in {b["plate_text"] for b in baca_csv(tmp_path / "keluar" / "validasi.csv")}
    assert r["bahan"] == ["dataset-indo-alpr", "tangkapan-owner", "plat-buatan"] and r["latih_hanya_buatan"] is True
    assert r["sumber"]["indo_alpr"]["latih"] == 0 and r["sumber"]["tangkapan"]["latih"] == 0


def test_latih_hanya_buatan_tanpa_plat_buatan_ditolak(tmp_path):
    indo, _ = siapkan_bahan(tmp_path, dengan_buatan=False)

    with pytest.raises(ValueError):
        bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                   tmp_path / "keluar", None, latih_hanya_buatan=True)


def test_wilayah_menambah_kolom_plate_region_untuk_model_berkepala_wilayah(tmp_path):
    # Rencana 25 Task 6: fpo-indo-1 berkepala wilayah; tanpa kolom plate_region kepala itu dibuang diam-diam (Rencana 9).
    indo, buatan = siapkan_bahan(tmp_path)

    r = bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                   tmp_path / "keluar", buatan, wilayah=True)

    for nama in ("latih.csv", "validasi.csv"):
        baris = baca_csv(tmp_path / "keluar" / nama)
        assert list(baris[0]) == ["image_path", "plate_text", "plate_region"]
        assert {b["plate_region"] for b in baris} == {"Indonesia"}
    assert r["wilayah"] is True


def test_ulang_tangkapan_hanya_di_latih(tmp_path):
    indo, buatan = siapkan_bahan(tmp_path)

    r = bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                   tmp_path / "keluar", buatan, ulang_tangkapan=5)

    latih = [b["plate_text"] for b in baca_csv(tmp_path / "keluar" / "latih.csv")]
    validasi = [b["plate_text"] for b in baca_csv(tmp_path / "keluar" / "validasi.csv")]
    harap_val = {f"D{i}AB" for i in range(1, 11) if bp.validasi_tangkapan(f"g{i:04d}", 1)}
    for i in range(1, 11):
        t = f"D{i}AB"
        assert (latih.count(t), validasi.count(t)) == ((0, 1) if t in harap_val else (5, 0))
    assert latih.count(teks_indo(False)) == 1 and latih.count("Z1Q") == 1  # INDO-ALPR dan plat buatan tidak diulang
    assert r["ulang_tangkapan"] == 5 and r["sumber"]["tangkapan"]["latih"] == 10 - len(harap_val)
    assert r["gambar"]["latih"] == len(latih)


def test_uji_tangkapan_hanya_plat_berteks_sisi_uji(tmp_path):
    # Potongan tangkapan uji, diukur sekali di akhir (Rencana 25 Task 6 Step 4). Sisi latih dan plat tak terbaca tidak masuk.
    siapkan_bahan(tmp_path)

    r = bp.siapkan_uji_tangkapan(tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json", tmp_path / "uji",
                                 wilayah=True)

    baris = baca_csv(tmp_path / "uji" / "uji-tangkapan.csv")
    assert sorted(b["plate_text"] for b in baris) == ["D11AB", "D12AB"] and {b["plate_region"] for b in baris} == {"Indonesia"}
    assert all((tmp_path / "uji" / b["image_path"]).exists() for b in baris)
    assert all(b["image_path"].startswith("potongan/u-mobil-") for b in baris)  # kelompok di nama, untuk hitungan per kelompok
    assert r == {"gambar": 2, "tak_terbaca": 0, "per_kelompok": {"mobil": 2}}
    isi = (tmp_path / "uji" / "uji-tangkapan.csv").read_text() + " ".join(p.name for p in (tmp_path / "uji" / "potongan").iterdir())
    assert "rahasia" not in isi


def test_cli_wilayah_ulang_dan_uji_tangkapan_sampai_berkas(tmp_path):
    indo, buatan = siapkan_bahan(tmp_path)
    umum = [str(tmp_path / "capture"), str(tmp_path / "peta.json"), str(tmp_path / "label.json")]

    a = bp.utama(["siapkan", str(tmp_path / "pembagian.json"), str(indo), *umum, str(tmp_path / "keluar"), "--plat-buatan",
                  str(buatan), "--wilayah", "--ulang-tangkapan", "5"])
    b = bp.utama(["uji-tangkapan", *umum, str(tmp_path / "uji"), "--wilayah"])

    s = json.loads((tmp_path / "keluar" / "siapkan.json").read_text())
    assert (a, b) == (0, 0) and s["wilayah"] is True and s["ulang_tangkapan"] == 5
    assert list(baca_csv(tmp_path / "uji" / "uji-tangkapan.csv")[0]) == ["image_path", "plate_text", "plate_region"]


def test_nama_berkas_asli_tidak_muncul(tmp_path):
    jalankan(tmp_path)

    keluar = tmp_path / "keluar"
    isi = (keluar / "latih.csv").read_text() + (keluar / "validasi.csv").read_text() + (keluar / "siapkan.json").read_text()
    assert "rahasia" not in isi + " ".join(p.name for p in (keluar / "potongan").iterdir())


# Rencana 30: potongan dari rantai kita sendiri (keluaran baca_gambar.py), potongan geser, dan validasi terpisah.

def rantai_palsu(tmp_path, nama, geser=0, nilai=None, sama_label=False):
    """Keluaran baca_gambar.py palsu: nomor gambar sendiri (urutan dibalik dari label, supaya pencocokan lewat jalur berkas teruji),
    satu kotak per gambar di plat berteks yang digeser `geser` piksel, bacaan "SALAH" (teks harus dari label), dan potongan berisi
    nilai unik per folder dan gambar (atau `nilai`, atau persis potongan kotak label bila `sama_label`). Gambar uji ikut ada."""
    from rantai import potong

    label = json.loads((tmp_path / "label.json").read_text())["gambar"]
    peta = json.loads((tmp_path / "peta.json").read_text())
    folder = tmp_path / nama
    (folder / "potongan").mkdir(parents=True)
    peta_rantai, baris, asal = {}, [], {}
    for i, g in enumerate(sorted(label, reverse=True), 1):
        r = f"g{i:04d}"
        peta_rantai[r] = peta[g]
        x1, y1, x2, y2 = label[g]["plat"][0]["kotak"]
        berkas = f"{r}-1.png"
        if sama_label:
            isi = potong(cv2.imread(str(tmp_path / "capture" / peta[g])), label[g]["plat"][0]["kotak"])
        else:
            isi = np.full((24, 70, 3), nilai if nilai is not None else (geser * 7 + i) % 250, np.uint8)
        cv2.imwrite(str(folder / "potongan" / berkas), isi)
        baris.append({"video": r, "nomor": 1, "kotak": [x1 + geser, y1, x2 + geser, y2], "potongan": berkas, "teks": "SALAH"})
        asal[g] = folder / "potongan" / berkas
    (folder / "peta-berkas.json").write_text(json.dumps(peta_rantai))
    (folder / "kedatangan.jsonl").write_text("".join(json.dumps(b) + "\n" for b in baris))
    return folder, asal


def siapkan_rantai(tmp_path, rantai, **opsi):
    indo, _ = siapkan_bahan(tmp_path, dengan_buatan=False)
    folder = [rantai_palsu(tmp_path, *r) if isinstance(r, tuple) else rantai_palsu(tmp_path, **r) for r in rantai]
    hasil = bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                       tmp_path / "keluar", None, wilayah=True, rantai=[f for f, _ in folder], **opsi)
    return hasil, [a for _, a in folder]


def harap_validasi():
    return {f"g{i:04d}" for i in range(1, 11) if bp.validasi_tangkapan(f"g{i:04d}", 1)}


def test_potongan_rantai_dicocokkan_lewat_jalur_dan_disalin_persis(tmp_path):
    # r1 bergeser 3 piksel (IoU tinggi, cocok); r2 bergeser 50 piksel (IoU < 0,3, tidak cocok). Teks dari label, bukan bacaan rantai.
    r, (asal1, _) = siapkan_rantai(tmp_path, [("r1", 3), ("r2", 50)])

    keluar, val = tmp_path / "keluar", harap_validasi()
    latih, validasi = baca_csv(keluar / "latih.csv"), baca_csv(keluar / "validasi.csv")
    for g in (f"g{i:04d}" for i in range(1, 11)):
        jalur = f"potongan/c1-{g}-1.png"
        assert (keluar / jalur).read_bytes() == asal1[g].read_bytes()  # disalin persis dari potongan rantai
        baris = validasi if g in val else latih
        assert [b["plate_text"] for b in baris if b["image_path"] == jalur] == [f"D{int(g[1:])}AB"]
    assert not any("c2-" in b["image_path"] for b in latih + validasi)
    assert not any(p.name.startswith("c1-g0011") or p.name.startswith("c1-g0012") for p in (keluar / "potongan").iterdir())
    teks = {b["plate_text"] for b in latih + validasi}
    assert "SALAH" not in teks and not {"D11AB", "D12AB"} & teks  # gambar uji di folder rantai tidak disentuh
    assert r["sumber"]["rantai"] == [
        {"folder": f"{tmp_path.name}/r1", "latih": 10 - len(val), "validasi": len(val), "kembar_dilewati": 0,
         "validasi_cocok": len(val)},
        {"folder": f"{tmp_path.name}/r2", "latih": 0, "validasi": 0, "kembar_dilewati": 0, "validasi_cocok": 0}]
    assert r["sumber"]["validasi_berteks"] == len(val)
    assert json.loads((keluar / "siapkan.json").read_text())["sumber"]["rantai"] == r["sumber"]["rantai"]


def test_pencocokan_mengikuti_aturan_nilai_label(tmp_path):
    # Plat A (tanpa teks) di urutan pertama mengambil kotak R1 yang paling cocok; plat B (berteks) mendapat R2, walau IoU B-R1 lebih
    # tinggi dari B-R2. Kalau hanya plat berteks yang dicocokkan, B salah mendapat R1. nilai_label memakai aturan yang sama.
    from halaman_label import nilai_label

    indo, _ = siapkan_bahan(tmp_path, dengan_buatan=False)
    g = next(f"g{i:04d}" for i in range(1, 200) if not bp.validasi_tangkapan(f"g{i:04d}", 2))
    cv2.imwrite(str(tmp_path / "capture" / "capture cctv mobil" / "rahasia-ab.png"), np.full((180, 320, 3), 90, np.uint8))
    (tmp_path / "peta.json").write_text(json.dumps({g: "capture cctv mobil/rahasia-ab.png"}))
    (tmp_path / "label.json").write_text(json.dumps({"dikeluarkan": {}, "gambar": {g: {
        "kelompok": "mobil", "sisi": "latih", "bukan_plat": [], "plat_tanpa_label": 0, "plat": [
            {"kotak": [100, 100, 160, 120], "teks": None, "tak_terbaca": True, "asal": "lembar"},
            {"kotak": [104, 100, 164, 120], "teks": "B7AB", "tak_terbaca": False, "asal": "lembar"}]}}}))
    folder = tmp_path / "r1"
    (folder / "potongan").mkdir(parents=True)
    cv2.imwrite(str(folder / "potongan" / "g0001-1.png"), np.full((20, 60, 3), 11, np.uint8))
    cv2.imwrite(str(folder / "potongan" / "g0001-2.png"), np.full((20, 60, 3), 22, np.uint8))
    (folder / "peta-berkas.json").write_text(json.dumps({"g0001": "capture cctv mobil/rahasia-ab.png"}))
    (folder / "kedatangan.jsonl").write_text(
        json.dumps({"video": "g0001", "nomor": 1, "kotak": [100, 100, 160, 120], "potongan": "g0001-1.png", "teks": "SALAH"}) + "\n"
        + json.dumps({"video": "g0001", "nomor": 2, "kotak": [110, 100, 170, 120], "potongan": "g0001-2.png", "teks": "B7AB"}) + "\n")

    bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
               tmp_path / "keluar", None, wilayah=True, rantai=[folder])

    salinan = tmp_path / "keluar" / "potongan" / f"c1-{g}-2.png"
    assert salinan.read_bytes() == (folder / "potongan" / "g0001-2.png").read_bytes()
    assert not (tmp_path / "keluar" / "potongan" / f"c1-{g}-1.png").exists()  # plat tanpa teks tidak menjadi bahan
    n = nilai_label(tmp_path / "label.json", tmp_path / "peta.json", folder, sisi="latih")
    assert n["per_kelompok"]["mobil"]["dibaca_benar"] == 1  # nilai_label juga memberi B kotak R2


def test_potongan_kembar_dilewati_tetapi_validasi_rantai_per_folder_lengkap(tmp_path):
    # r1 dan r2 berisi potongan yang sama persis (mis. ambang 0,25 dan 0,4 memberi kotak yang sama); r3 sama dengan potongan label.
    r, _ = siapkan_rantai(tmp_path, [{"nama": "r1", "geser": 3, "nilai": 77}, {"nama": "r2", "geser": 3, "nilai": 77},
                                     {"nama": "r3", "sama_label": True}], ulang_tangkapan=2)

    keluar, val = tmp_path / "keluar", harap_validasi()
    latih, validasi = baca_csv(keluar / "latih.csv"), baca_csv(keluar / "validasi.csv")
    for awalan, (n_latih, n_val) in (("potongan/c1-", (2 * (10 - len(val)), len(val))), ("potongan/c2-", (0, 0)),
                                     ("potongan/c3-", (0, 0))):
        assert sum(b["image_path"].startswith(awalan) for b in latih) == n_latih
        assert sum(b["image_path"].startswith(awalan) for b in validasi) == n_val
    for i in (1, 2, 3):
        per_folder = baca_csv(keluar / f"validasi-rantai-{i}.csv")
        assert sorted(b["image_path"] for b in per_folder) == sorted(f"potongan/c{i}-{g}-1.png" for g in val)
        assert all((keluar / b["image_path"]).exists() for b in per_folder)
    assert [x["kembar_dilewati"] for x in r["sumber"]["rantai"]] == [0, 10, 10]
    assert [x["validasi_cocok"] for x in r["sumber"]["rantai"]] == [len(val)] * 3


def test_geser_enam_potongan_per_plat_latih_dari_isian_v2_sekali_saja(tmp_path):
    from tahan_geser import VARIAN, potong_geser

    r, _ = siapkan_rantai(tmp_path, [], geser=True, ulang_tangkapan=5)

    keluar, val = tmp_path / "keluar", harap_validasi()
    latih, validasi = baca_csv(keluar / "latih.csv"), baca_csv(keluar / "validasi.csv")
    geser = [b for b in latih if b["image_path"].startswith("potongan/g")]
    assert len(geser) == 6 * (10 - len(val)) and not any(b["image_path"].startswith("potongan/g") for b in validasi)
    g = next(f"g{i:04d}" for i in range(1, 11) if f"g{i:04d}" not in val)
    gambar = cv2.imread(str(tmp_path / "capture" / "capture cctv mobil" / f"rahasia-{int(g[1:])}.png"))
    for k, isian in enumerate(VARIAN["v2"][1:], 1):
        harap = potong_geser(gambar, [100, 100, 160, 120], *isian)
        assert np.array_equal(cv2.imread(str(keluar / "potongan" / f"g{k}-{g}-1.png")), harap)
        assert [b["plate_text"] for b in geser if b["image_path"] == f"potongan/g{k}-{g}-1.png"] == [f"D{int(g[1:])}AB"]
    assert r["sumber"]["geser"] == {"latih": 6 * (10 - len(val))} and r["geser"] is True


def test_validasi_terpisah_indo_alpr_ke_berkasnya_sendiri(tmp_path):
    r, _ = siapkan_rantai(tmp_path, [("r1", 3)], validasi_terpisah=True)

    keluar = tmp_path / "keluar"
    validasi, indo = baca_csv(keluar / "validasi.csv"), baca_csv(keluar / "validasi-indo.csv")
    assert validasi and all(b["image_path"].startswith("potongan/") for b in validasi)
    assert [b["plate_text"] for b in indo] == [teks_indo(True)] and list(indo[0]) == ["image_path", "plate_text", "plate_region"]
    assert teks_indo(False) in {b["plate_text"] for b in baca_csv(keluar / "latih.csv")}
    assert r["validasi_terpisah"] is True and r["gambar"]["validasi_indo"] == 1
    assert r["gambar"]["validasi"] == len(validasi)


def test_rantai_dan_geser_ditolak_bersama_latih_hanya_buatan(tmp_path):
    indo, buatan = siapkan_bahan(tmp_path)
    folder, _ = rantai_palsu(tmp_path, "r1", 3)

    for opsi in ({"rantai": [folder]}, {"geser": True}):
        with pytest.raises(ValueError):
            bp.siapkan(tmp_path / "pembagian.json", indo, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json",
                       tmp_path / "keluar", buatan, latih_hanya_buatan=True, **opsi)


def test_cli_rantai_geser_dan_validasi_terpisah_sampai_berkas(tmp_path):
    indo, _ = siapkan_bahan(tmp_path, dengan_buatan=False)
    (r1, _), (r2, _) = rantai_palsu(tmp_path, "r1", 3), rantai_palsu(tmp_path, "r2", 5)

    kode = bp.utama(["siapkan", str(tmp_path / "pembagian.json"), str(indo), str(tmp_path / "capture"), str(tmp_path / "peta.json"),
                     str(tmp_path / "label.json"), str(tmp_path / "keluar"), "--wilayah", "--ulang-tangkapan", "5", "--rantai",
                     str(r1), str(r2), "--geser", "--validasi-terpisah"])

    keluar = tmp_path / "keluar"
    s = json.loads((keluar / "siapkan.json").read_text())
    assert kode == 0 and s["geser"] is True and s["validasi_terpisah"] is True and len(s["sumber"]["rantai"]) == 2
    assert (keluar / "validasi-indo.csv").exists() and (keluar / "validasi-rantai-2.csv").exists()
    isi = "".join(p.read_text() for p in keluar.glob("*.csv")) + (keluar / "siapkan.json").read_text()
    assert "rahasia" not in isi + " ".join(p.name for p in (keluar / "potongan").iterdir())
