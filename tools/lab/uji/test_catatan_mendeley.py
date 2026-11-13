"""Uji tools/lab/catatan_mendeley.py: hasil buka arsip harus sama dengan yang dicatat penerbit, tanpa nama berkas tercetak."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catatan_mendeley as cm  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "catatan_mendeley.py"
ISI = {"B 1234 XYZ_0001.png": b"gambar-1", "D 5678 AB_0002.jpg": b"gambar-2"}
ID_LATIH = "id-folder-latih"


def siapkan(tmp_path, isi_folder=ISI):
    """Catatan penerbit yang mencatat ISI di folder ID_LATIH, dan folder hasil buka berisi `isi_folder`."""
    butir = [{"filename": nama, "folder_id": ID_LATIH, "size": len(data),
              "content_details": {"sha256_hash": hashlib.sha256(data).hexdigest()}} for nama, data in ISI.items()]
    butir.append({"filename": "Keterangan.xlsx", "size": 5, "content_details": {"sha256_hash": "f" * 64}})
    catatan = tmp_path / "catatan-dataset.json"
    catatan.write_text(json.dumps({
        "id": "abc123", "name": "DATASET-CONTOH", "version": 1, "doi": {"id": "10.0000/abc123.1"},
        "publish_date": "2023-09-07T16:39:37.68Z", "institutions": [{"name": "Lembaga Contoh"}],
        "contributors": [{"first_name": "Nama", "last_name": "Pembuat"}],
        "data_licence": {"short_name": "CC BY 4.0", "url": "https://contoh.test/by/4.0", "description": "Boleh dipakai dengan menyebut sumber."},
        "files": butir,
    }))
    terbuka = tmp_path / "terbuka"
    (terbuka / "original" / "train").mkdir(parents=True)
    for nama, data in isi_folder.items():
        (terbuka / "original" / "train" / nama).write_bytes(data)
    return catatan, terbuka


def test_izin_dicetak_apa_adanya_beserta_jumlah_berkas_per_folder(tmp_path, capsys):
    catatan, _ = siapkan(tmp_path)

    kode = cm.utama(["izin", str(catatan)])

    cetak = capsys.readouterr().out
    assert kode == 0
    assert "DATASET-CONTOH" in cetak and "10.0000/abc123.1" in cetak and "Lembaga Contoh" in cetak
    assert "CC BY 4.0" in cetak and "Boleh dipakai dengan menyebut sumber." in cetak
    assert "berkas tercatat: 3" in cetak and ID_LATIH in cetak
    assert "1234" not in cetak and "XYZ" not in cetak, "nama berkas memuat nomor plat; tidak boleh tercetak"


def test_folder_yang_persis_sama_dengan_catatan_penerbit_dinyatakan_cocok(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    cetak = capsys.readouterr().out
    assert kode == 0, cetak
    assert "COCOK original/train: penerbit mencatat 2, di folder 2, sama 2, kurang 0, lebih 0" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak


def test_berkas_yang_hilang_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {"B 1234 XYZ_0001.png": b"gambar-1"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "kurang 1, lebih 0" in capsys.readouterr().out


def test_berkas_yang_isinya_berbeda_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {**ISI, "D 5678 AB_0002.jpg": b"ditukar"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "sama 1, kurang 1, lebih 1" in capsys.readouterr().out


def test_berkas_tambahan_yang_tidak_dicatat_penerbit_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {**ISI, "selundupan.png": b"lain"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "kurang 0, lebih 1" in capsys.readouterr().out


def test_folder_yang_tidak_ada_atau_id_yang_tidak_dikenal_bukan_cocok(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)

    assert cm.utama(["cocok", str(catatan), str(terbuka), f"original/test={ID_LATIH}"]) == 1
    assert cm.utama(["cocok", str(catatan), str(terbuka), "original/train=id-yang-tidak-ada"]) == 1


def test_baris_perintah_sampai_ke_putusan(tmp_path):
    # Rantainya: baris perintah -> catatan penerbit -> SHA-256 tiap berkas di folder -> kode keluar.
    catatan, terbuka = siapkan(tmp_path)

    cocok = subprocess.run([sys.executable, str(SKRIP), "cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"], capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), "cocok", str(catatan), str(terbuka)], capture_output=True, text=True)

    assert cocok.returncode == 0, cocok.stdout + cocok.stderr
    assert salah.returncode == 2, salah.stdout + salah.stderr


def test_galat_membaca_tidak_membocorkan_nama_berkas(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)
    berkas = terbuka / "original" / "train" / "B 1234 XYZ_0001.png"
    berkas.chmod(0o000)

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    cetak = capsys.readouterr()
    berkas.chmod(0o600)
    assert kode == 1
    assert "GAGAL MEMBACA" in cetak.out
    assert "1234" not in cetak.out + cetak.err
