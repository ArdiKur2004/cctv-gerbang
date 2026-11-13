"""Uji tools/ambil/ambil_berkas.py. Lab tidak punya jaringan, jadi jaringan diganti peta alamat -> jawaban."""
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ambil"))
import ambil_berkas as ab  # noqa: E402

SKRIP = Path(__file__).resolve().parents[2] / "ambil" / "ambil_berkas.py"
HOST = {"data.contoh.test", "simpan.contoh.test"}
ISI = b"isi arsip " * 1000
SIDIK = hashlib.sha256(ISI).hexdigest()
AWAL = "https://data.contoh.test/a.zip"
SIMPAN = "https://simpan.contoh.test/a.zip?tanda=RAHASIA"
BESAR = 10**9


def jaringan(jawaban):
    """Pengganti jaringan: (fungsi minta, daftar alamat yang benar-benar diminta)."""
    diminta = []

    def minta(alamat):
        diminta.append(alamat)
        status, kepala, badan = jawaban[alamat]
        return status, kepala, io.BytesIO(badan)

    return minta, diminta


def utuh(panjang=None):
    return 200, {"Content-Length": str(len(ISI) if panjang is None else panjang)}, ISI


def test_berkas_tersimpan_dengan_nama_jadinya_dan_tercatat_sidiknya(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    asal = ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert (tmp_path / "a.zip").read_bytes() == ISI
    assert not (tmp_path / "a.zip.part").exists()
    assert asal["sha256"] == SIDIK and asal["byte"] == len(ISI) and asal["host_akhir"] == "data.contoh.test"


def test_pengalihan_ke_host_yang_didaftar_diikuti(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": SIMPAN}, b""), SIMPAN: utuh()})

    asal = ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL, SIMPAN]
    assert asal["host_akhir"] == "simpan.contoh.test"
    assert "RAHASIA" not in json.dumps(asal), "alamat hasil pengalihan memuat tanda tangan sementara; jangan dicatat"


def test_pengalihan_ke_host_di_luar_daftar_ditolak_tanpa_menghubunginya(tmp_path):
    jahat = "https://jahat.contoh.test/a.zip?tanda=RAHASIA"
    minta, diminta = jaringan({AWAL: (302, {"Location": jahat}, b""), jahat: utuh()})

    with pytest.raises(ab.Ditolak) as galat:
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL]
    assert "jahat.contoh.test" in str(galat.value) and "RAHASIA" not in str(galat.value)
    assert list(tmp_path.iterdir()) == []


def test_pengalihan_ke_alamat_bukan_https_ditolak(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": "http://simpan.contoh.test/a.zip"}, b"")})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL]


def test_alamat_awal_bukan_https_ditolak_sebelum_ada_permintaan(tmp_path):
    minta, diminta = jaringan({})

    with pytest.raises(ab.Ditolak):
        ab.unduh("http://data.contoh.test/a.zip", tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == []


def test_sidik_yang_tidak_cocok_dengan_kunci_tidak_menghasilkan_berkas_jadi(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    with pytest.raises(ab.TakCocok):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, sha256="0" * 64, minta=minta)

    assert not (tmp_path / "a.zip").exists()
    assert (tmp_path / "a.zip.part").exists(), "sisa .part adalah tanda bagi pintu bahwa unduhan tidak sah"


def test_unduhan_yang_terpotong_tidak_menghasilkan_berkas_jadi(tmp_path):
    minta, _ = jaringan({AWAL: utuh(panjang=len(ISI) + 500)})

    with pytest.raises(ab.Ditolak) as galat:
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert "terpotong" in str(galat.value)
    assert not (tmp_path / "a.zip").exists()


def test_berkas_yang_mengaku_lebih_besar_dari_batas_ditolak_sebelum_ditulis(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, 100, minta=minta)

    assert list(tmp_path.iterdir()) == []


def test_berkas_tanpa_keterangan_ukuran_dihentikan_di_batas(tmp_path):
    minta, _ = jaringan({AWAL: (200, {}, ISI)})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, 100, minta=minta)

    assert not (tmp_path / "a.zip").exists()


def test_pengalihan_yang_berputar_dihentikan(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": AWAL}, b"")})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert len(diminta) == ab.MAKS_ALIH + 1


def baris_perintah(tmp_path, *tambahan, alamat=AWAL, nama="a.zip"):
    perintah = [sys.executable, str(SKRIP), "--alamat", alamat, "--keluar", str(tmp_path), "--nama", nama,
                "--maks-byte", str(BESAR), "--host", "data.contoh.test", *tambahan]
    return subprocess.run(perintah, capture_output=True, text=True)


def test_baris_perintah_berkas_yang_sudah_ada_dan_cocok_tidak_diunduh_lagi(tmp_path):
    # Rantainya: pintu -> baris perintah -> berkas. Tidak ada jaringan di lab, jadi kode 0 di sini berarti tak ada permintaan.
    (tmp_path / "a.zip").write_bytes(ISI)

    hasil = baris_perintah(tmp_path, "--sha256", SIDIK)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "SUDAH ADA" in hasil.stdout and SIDIK in hasil.stdout


def test_baris_perintah_berkas_yang_sudah_ada_tetapi_sidiknya_beda_ditolak_dengan_kode_7(tmp_path):
    (tmp_path / "a.zip").write_bytes(ISI)

    hasil = baris_perintah(tmp_path, "--sha256", "0" * 64)

    assert hasil.returncode == 7, hasil.stdout + hasil.stderr
    assert "TIDAK COCOK" in hasil.stdout


def test_baris_perintah_alamat_bukan_https_ditolak_dengan_kode_1(tmp_path):
    hasil = baris_perintah(tmp_path, alamat="http://data.contoh.test/a.zip")

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout


def test_baris_perintah_nama_berkas_yang_memuat_folder_ditolak_dengan_kode_2(tmp_path):
    hasil = baris_perintah(tmp_path, nama="../luar.zip")

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
