"""Uji tools/lab/dataset_cctv.py: label jalur dari lembar owner, pilihan gambar (kotak tak berlabel ditutup), tempel plat buatan,
dan dataset YOLO dari video buatan dengan sisi validasi menurut SHA-256 video."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dataset_cctv as dc  # noqa: E402

V = "gerbang.avi"


def tampak_contoh():
    return [{"video": V, "jalur": 0, "kedatangan": 1, "tampak": [[0, 60, 40, 100, 56], [2, 60, 40, 100, 56], [4, 60, 40, 100, 56]]},
            {"video": V, "jalur": 1, "kedatangan": 2, "tampak": [[2, 10, 10, 30, 20], [4, 10, 10, 30, 20]]},
            {"video": V, "jalur": 2, "kedatangan": None, "tampak": [[4, 120, 70, 140, 80]]}]


def lembar_contoh():
    return {"baris": [{"nomor": 1, "video": V, "kedatangan": 1}, {"nomor": 2, "video": V, "kedatangan": 2}]}


def test_label_jalur_dari_lembar_dan_jawaban_owner():
    assert dc.label_jalur(tampak_contoh(), lembar_contoh(), bukan_plat={2}) == {(V, 0): "plat", (V, 1): "bukan"}


def test_pilih_gambar_plat_jadi_label_dan_kotak_tak_berlabel_ditutup():
    pilih = dc.pilih_gambar(tampak_contoh(), {(V, 0): "plat", (V, 1): "bukan"}, per_jalur=3)

    assert pilih == [(V, 0, [[60, 40, 100, 56]], []), (V, 2, [[60, 40, 100, 56]], []),
                     (V, 4, [[60, 40, 100, 56]], [[120, 70, 140, 80]])]


def test_tempel_plat_buatan_di_dalam_gambar():
    latar = np.full((360, 640, 3), 90, np.uint8)

    hasil, (x1, y1, x2, y2) = dc.tempel(latar, np.random.default_rng(0))

    assert 0 <= x1 < x2 <= 640 and 120 <= y1 < y2 <= 360 and (y2 - y1) >= 0.015 * 360 - 1
    assert not np.array_equal(hasil[y1:y2, x1:x2], latar[y1:y2, x1:x2])
    luar = np.ones(latar.shape[:2], bool)
    luar[y1:y2, x1:x2] = False
    assert np.array_equal(hasil[luar], latar[luar])  # di luar kotak tempelan tidak berubah


def test_bangun_dataset_yolo_dari_video_buatan(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis = cv2.VideoWriter(str(folder / V), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 96))
    for _ in range(40):
        tulis.write(np.full((96, 160, 3), 90, np.uint8))
    tulis.release()
    (tmp_path / "m.json").write_text(json.dumps({"video": [{"berkas": V, "sudut": "gerbang", "kategori": "siang"}]}))
    (tmp_path / "p.json").write_text(json.dumps({"uji": [], "latih": [V]}))
    (tmp_path / "rantai").mkdir()
    (tmp_path / "rantai" / "penampakan.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tampak_contoh()))
    pl = tmp_path / "pl"
    for s in ("train", "valid"):
        (pl / s / "images").mkdir(parents=True)
        (pl / s / "labels").mkdir(parents=True)
        cv2.imwrite(str(pl / s / "images" / f"x-{s}.jpg"), np.zeros((50, 80, 3), np.uint8))
        (pl / s / "labels" / f"x-{s}.txt").write_text("0 0.5 0.5 0.2 0.1\n")

    h = dc.bangun(tmp_path / "m.json", tmp_path / "p.json", tmp_path / "rantai", lembar_contoh(), {2}, folder, pl,
                  tmp_path / "ds", latar_per_video=2)

    sisi = "valid" if dc.sisi_validasi(V) else "train"
    label = sorted((tmp_path / "ds" / sisi / "labels").glob("gerbang-*.txt"))
    assert h[sisi]["gambar_cctv"] == 3 and h[sisi]["kotak_plat"] == 3 and h[sisi]["gambar_tempel"] == 2
    assert (tmp_path / "ds" / sisi / "labels" / "gerbang-000000.txt").read_text() == "0 0.500000 0.500000 0.250000 0.166667\n"
    assert len(label) == 5 and h["train"]["plat_lighting"] == 1 and h["valid"]["plat_lighting"] == 1
