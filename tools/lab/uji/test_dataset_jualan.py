"""Uji tools/lab/dataset_jualan.py (Rencana 24 Task 9): dataset pencari plat JUALAN dari plat-lighting dan tangkapan owner (label.json),
format YOLO seperti plat-lighting. Tangkapan uji hanya masuk folder ukur, gambar dengan plat tanpa label dikeluarkan, semua kotak plat
(juga yang tak terbaca) menjadi label dan kotak bukan plat tidak, plat buatan hanya ditempel di gambar latih, dan nama berkas asli
tidak muncul."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dataset_jualan as dj  # noqa: E402
from deteksi import baca_label  # noqa: E402

PLAT = [40.0, 100.0, 100.0, 120.0]
TAK_TERBACA = [200.0, 100.0, 240.0, 115.0]
BUKAN = [10.0, 10.0, 50.0, 30.0]


def siapkan(tmp_path, jumlah_latih=12):
    pl = tmp_path / "pl"
    for sisi in ("train", "valid", "test"):
        for sub in ("images", "labels"):
            (pl / sisi / sub).mkdir(parents=True)
        cv2.imwrite(str(pl / sisi / "images" / f"a-{sisi}.jpg"), np.full((360, 640, 3), 90, np.uint8))
        (pl / sisi / "labels" / f"a-{sisi}.txt").write_text("0 0.5 0.5 0.1 0.05\n")
    folder = tmp_path / "capture" / "capture cctv motor"
    folder.mkdir(parents=True)
    peta, gambar = {}, {}
    for i in range(1, jumlah_latih + 4):
        g = f"g{i:04d}"
        cv2.imwrite(str(folder / f"rahasia-{i}.png"), np.full((180, 320, 3), 60 + i, np.uint8))
        peta[g] = f"capture cctv motor/rahasia-{i}.png"
        gambar[g] = {"kelompok": "motor", "sisi": "uji" if i > jumlah_latih + 1 else "latih", "bukan_plat": [BUKAN],
                     "plat_tanpa_label": 1 if i == jumlah_latih + 1 else 0,
                     "plat": [{"kotak": PLAT, "teks": f"D{i}AB", "tak_terbaca": False, "asal": "lembar"},
                              {"kotak": TAK_TERBACA, "teks": None, "tak_terbaca": True, "asal": "lembar"}]}
    (tmp_path / "peta.json").write_text(json.dumps(peta))
    (tmp_path / "label.json").write_text(json.dumps({"gambar": gambar, "dikeluarkan": {}}))
    return pl


def bangun(tmp_path, tempel=0):
    pl = siapkan(tmp_path)
    return dj.bangun(pl, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json", tmp_path / "keluar",
                     tempel_per_gambar=tempel)


def nama_gambar(folder):
    return sorted(p.stem for p in (folder / "images").iterdir())


def test_tangkapan_latih_ke_train_dan_valid_uji_hanya_ke_folder_ukur(tmp_path):
    r = bangun(tmp_path)

    k = tmp_path / "keluar"
    harap_val = {f"t-g{i:04d}" for i in range(1, 13) if dj.validasi_gambar(f"g{i:04d}")}
    assert harap_val and len(harap_val) < 12  # bahan uji mengisi kedua sisi
    assert set(nama_gambar(k / "train")) == {"pl-a-train"} | ({f"t-g{i:04d}" for i in range(1, 13)} - harap_val)
    assert set(nama_gambar(k / "valid")) == {"pl-a-valid"} | harap_val
    assert nama_gambar(k / "ukur-tangkapan" / "test") == ["t-g0014", "t-g0015"]  # g0013: plat tanpa label, dikeluarkan
    assert nama_gambar(k / "ukur-plat-lighting" / "test") == ["pl-a-test"]
    for ukur in ("ukur-tangkapan", "ukur-plat-lighting"):
        assert nama_gambar(k / ukur / "valid") == nama_gambar(k / "valid")  # ambang dipilih di validasi yang sama
    assert r["bahan"] == ["dataset-plat-lighting", "tangkapan-owner"]
    assert r["dikeluarkan_plat_tanpa_label"] == 1


def test_kotak_plat_juga_tak_terbaca_menjadi_label_dan_bukan_plat_tidak(tmp_path):
    bangun(tmp_path)

    sisi = tmp_path / "keluar" / "train"
    nama = next(n for n in nama_gambar(sisi) if n.startswith("t-"))
    kotak = baca_label(sisi / "labels" / f"{nama}.txt", 320, 180)
    assert len(kotak) == 2
    for harap, dapat in zip((PLAT, TAK_TERBACA), kotak):
        assert np.allclose(harap, dapat, atol=0.5)


def test_tempel_plat_buatan_hanya_di_latih(tmp_path):
    r = bangun(tmp_path, tempel=1)

    k = tmp_path / "keluar"
    tempel = [n for n in nama_gambar(k / "train") if n.endswith("-tempel1")]
    assert len(tempel) == r["train"]["gambar_asli"] and r["train"]["gambar_tempel"] == len(tempel)
    assert not any("tempel" in n for n in nama_gambar(k / "valid"))
    asli = len(baca_label(k / "train" / "labels" / "pl-a-train.txt", 640, 360))
    assert len(baca_label(k / "train" / "labels" / "pl-a-train-tempel1.txt", 640, 360)) > asli
    assert r["bahan"] == ["dataset-plat-lighting", "tangkapan-owner", "plat-buatan"]


def siapkan_tambah(tmp_path):
    """Dataset YOLO tambahan seperti cctv-fase1: gambar video berkotak, gambar video tanpa kotak, gambar tempel, dan plat-lighting
    berawalan pl- (sudah ada di dataset utama, jadi tidak boleh kembar)."""
    isi = {"train": {"vid-000001": "0 0.5 0.5 0.1 0.05\n", "vid-000002": "", "vid-tempel-000003": "0 0.3 0.7 0.1 0.05\n",
                     "pl-a-train": "0 0.5 0.5 0.1 0.05\n"},
           "valid": {"vid-000010": "0 0.5 0.5 0.1 0.05\n", "vid-000011": "", "pl-a-valid": "0 0.5 0.5 0.1 0.05\n"}}
    for sisi, gambar in isi.items():
        for sub in ("images", "labels"):
            (tmp_path / "tambah" / sisi / sub).mkdir(parents=True)
        for nama, label in gambar.items():
            cv2.imwrite(str(tmp_path / "tambah" / sisi / "images" / f"{nama}.jpg"), np.full((96, 160, 3), 70, np.uint8))
            (tmp_path / "tambah" / sisi / "labels" / f"{nama}.txt").write_text(label)
    return tmp_path / "tambah"


def bangun_tambah(tmp_path, tanpa_negatif):
    pl = siapkan(tmp_path)
    return dj.bangun(pl, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json", tmp_path / "keluar",
                     tambah=siapkan_tambah(tmp_path), tambah_bahan=["video-riset-youtube", "plat-buatan"],
                     tanpa_negatif_tambah=tanpa_negatif)


def test_dataset_tambahan_disalin_berawalan_x_tanpa_plat_lighting_kembar(tmp_path):
    # Rencana 25 Task 3: cctv1 dilatih lanjut dengan cctv-fase1 utuh ditambah tangkapan latih (calon C1).
    r = bangun_tambah(tmp_path, tanpa_negatif=False)

    k = tmp_path / "keluar"
    train, valid = set(nama_gambar(k / "train")), set(nama_gambar(k / "valid"))
    assert {"x-vid-000001", "x-vid-000002", "x-vid-tempel-000003"} <= train and not any(n.startswith("x-pl-") for n in train)
    assert {"x-vid-000010", "x-vid-000011"} <= valid and not any(n.startswith("x-pl-") for n in valid)
    assert (k / "train" / "labels" / "x-vid-tempel-000003.txt").read_text() == "0 0.3 0.7 0.1 0.05\n"
    assert (k / "train" / "labels" / "x-vid-000002.txt").read_text() == ""
    assert r["tambah"] == {"train": {"gambar": 3, "kotak_plat": 2, "negatif_dilewati": 0},
                           "valid": {"gambar": 2, "kotak_plat": 1, "negatif_dilewati": 0}}
    assert r["bahan"] == ["dataset-plat-lighting", "tangkapan-owner", "video-riset-youtube", "plat-buatan"]
    assert set(nama_gambar(k / "ukur-tangkapan" / "valid")) == valid  # validasi gabungan ikut ke folder ukur


def test_tanpa_negatif_tambah_hanya_membuang_gambar_latih_tanpa_kotak(tmp_path):
    # Calon C2 (Rencana 25): gambar video tanpa kotak bisa menyembunyikan plat yang tak pernah ditemukan (Rencana 19), jadi
    # dibuang dari latih. Validasi TIDAK diubah, supaya C0, C1, dan C2 dinilai di validasi yang sama.
    r = bangun_tambah(tmp_path, tanpa_negatif=True)

    k = tmp_path / "keluar"
    train, valid = set(nama_gambar(k / "train")), set(nama_gambar(k / "valid"))
    assert "x-vid-000002" not in train and {"x-vid-000001", "x-vid-tempel-000003"} <= train
    assert {"x-vid-000010", "x-vid-000011"} <= valid
    assert r["tambah"]["train"] == {"gambar": 2, "kotak_plat": 2, "negatif_dilewati": 1}
    assert r["tambah"]["valid"] == {"gambar": 2, "kotak_plat": 1, "negatif_dilewati": 0} and r["tanpa_negatif_tambah"] is True


def test_dataset_tambahan_tanpa_bahan_ditolak(tmp_path):
    pl = siapkan(tmp_path)

    with pytest.raises(ValueError, match="bahan"):
        dj.bangun(pl, tmp_path / "capture", tmp_path / "peta.json", tmp_path / "label.json", tmp_path / "keluar",
                  tambah=siapkan_tambah(tmp_path))


def test_cli_dataset_tambahan_sampai_ringkasan(tmp_path):
    pl = siapkan(tmp_path)
    tambah = siapkan_tambah(tmp_path)

    kode = dj.utama(["bangun", str(pl), str(tmp_path / "capture"), str(tmp_path / "peta.json"), str(tmp_path / "label.json"),
                     str(tmp_path / "keluar"), "--tambah", str(tambah), "--tambah-bahan", "video-riset-youtube,plat-buatan",
                     "--tanpa-negatif-tambah"])

    r = json.loads((tmp_path / "keluar" / "ringkasan.json").read_text())
    assert kode == 0 and r["tambah"]["train"]["negatif_dilewati"] == 1 and "plat-buatan" in r["bahan"]


def siapkan_roboflow(tmp_path):
    """Dataset YOLOv8 Roboflow: kelas 0 = plat (kotak atau poligon), kelas 1 = mobil; ada gambar tanpa plat."""
    r = tmp_path / "rf"
    isi = {"train": {"p1": "0 0.5 0.5 0.2 0.1\n1 0.5 0.5 0.8 0.8\n", "p2": "0 0.4 0.4 0.6 0.4 0.6 0.5 0.4 0.5\n",
                     "mobil-saja": "1 0.5 0.5 0.8 0.8\n"},
           "valid": {"p3": "0 0.3 0.3 0.1 0.05\n"}, "test": {"p4": "0 0.7 0.7 0.1 0.05\n"}}
    for sisi, gambar in isi.items():
        for sub in ("images", "labels"):
            (r / sisi / sub).mkdir(parents=True)
        for nama, label in gambar.items():
            cv2.imwrite(str(r / sisi / "images" / f"{nama}.jpg"), np.full((64, 64, 3), 80, np.uint8))
            (r / sisi / "labels" / f"{nama}.txt").write_text(label)
    return r


def test_tambah_ke_latih_semua_sisi_hanya_kelas_plat_dan_poligon_menjadi_kotak(tmp_path):
    # Rencana 29 (K56): plat dari "vehicle and license plate" ditambahkan ke latih saja; validasi tetap sama dengan Rencana 25.
    bangun(tmp_path)
    k = tmp_path / "keluar"
    valid_lama = nama_gambar(k / "valid")

    r = dj.tambah_ke_latih(k, siapkan_roboflow(tmp_path), kelas=[0], bahan=["dataset-roboflow-vehicle-license-plate"])

    latih = set(nama_gambar(k / "train"))
    assert {"r-p1", "r-p2", "r-p3", "r-p4"} <= latih and "r-mobil-saja" not in latih  # tanpa kotak plat: dilewati
    assert nama_gambar(k / "valid") == valid_lama
    assert (k / "train" / "labels" / "r-p1.txt").read_text() == "0 0.500000 0.500000 0.200000 0.100000\n"  # mobil dibuang
    assert (k / "train" / "labels" / "r-p2.txt").read_text() == "0 0.500000 0.450000 0.200000 0.100000\n"  # poligon -> kotak
    assert r == {"gambar": 4, "kotak": 4, "poligon": 1, "dilewati_tanpa_kotak": 1}
    ringkas = json.loads((k / "ringkasan.json").read_text())
    assert ringkas["tambah_latih"] == [{"awalan": "r-", "kelas": [0], **r}]
    assert ringkas["bahan"][-1] == "dataset-roboflow-vehicle-license-plate"


def test_tambah_ke_latih_tanpa_bahan_ditolak_dan_cli(tmp_path):
    bangun(tmp_path)
    rf = siapkan_roboflow(tmp_path)

    with pytest.raises(ValueError, match="bahan"):
        dj.tambah_ke_latih(tmp_path / "keluar", rf, kelas=[0], bahan=[])
    kode = dj.utama(["tambah-latih", str(tmp_path / "keluar"), str(rf), "--kelas", "0", "--bahan", "dataset-roboflow-vehicle-license-plate"])

    assert kode == 0 and "r-p4" in nama_gambar(tmp_path / "keluar" / "train")


def test_nama_berkas_asli_tidak_muncul(tmp_path):
    bangun(tmp_path, tempel=1)

    semua = [p.name for p in (tmp_path / "keluar").rglob("*")] + [(tmp_path / "keluar" / "ringkasan.json").read_text()]
    assert not any("rahasia" in x for x in semua)
