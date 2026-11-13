"""Uji tools/lab/layanan_baca.py: satu gambar masuk, plat dan jenis keluar (Rencana T6 Task 2).

Uji di berkas ini TIDAK memuat mesin sungguhan: ia memakai rantai tiruan, supaya yang diuji adalah susunan
hasilnya, penanganan galat, dan janji "jalur berkas tidak pernah ikut tercetak". Uji dengan mesin sungguhan ada
di tools/lab/uji_fpo, di luar gerbang ini.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from layanan_baca import baca_satu, jaga_sekali, SUSUNAN_HASIL  # noqa: E402


class CariTiruan:
    """Pencari tiruan: mengembalikan kotak tetap. Bentuk kotak sama dengan pencari sungguhan: x1,y1,x2,y2,yakin."""

    def __init__(self, kotak=None):
        self.kotak = kotak if kotak is not None else [(10.0, 10.0, 60.0, 30.0, 0.9)]

    def __call__(self, gambar):
        return list(self.kotak)


def baca_tiruan(potongan):
    return "L1234AB", 0.95


def jenis_tiruan(potongan):
    return "mobil", 0.88


def gambar_contoh():
    return np.zeros((120, 200, 3), dtype=np.uint8)


# ─── Susunan hasil ──────────────────────────────────────────────────────────────────────────────────

def test_hasil_bersusunan_tetap():
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan, kenali_jenis=jenis_tiruan,
                  ambang=0.25)
    assert set(h) == set(SUSUNAN_HASIL), "susunan hasil berubah; sisi Node membacanya menurut nama kunci"
    assert h["plat"] == "L1234AB"
    assert h["jenis"] == "mobil"
    assert 0 <= h["yakin"] <= 1
    assert isinstance(h["ragu"], list)
    assert h["ms"] >= 0


def test_gambar_tanpa_kendaraan_menghasilkan_hasil_kosong_yang_sah():
    """Bukan galat: kamera sering menangkap jalan kosong."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(kotak=[]), cari_kendaraan=None, baca=baca_tiruan,
                  kenali_jenis=jenis_tiruan, ambang=0.25)
    assert set(h) == set(SUSUNAN_HASIL)
    assert h["plat"] is None
    assert h["jenis"] is None
    assert h["ragu"] == []


def test_kotak_di_bawah_ambang_dibuang():
    h = baca_satu(gambar_contoh(), cari=CariTiruan(kotak=[(10.0, 10.0, 60.0, 30.0, 0.10)]), cari_kendaraan=None,
                  baca=baca_tiruan, kenali_jenis=jenis_tiruan, ambang=0.25)
    assert h["plat"] is None


def test_plat_dirapikan_seperti_sisi_node():
    """Plat yang dikirim ke TGT harus sudah berbentuk baku: huruf besar, tanpa spasi."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=None, baca=lambda p: ("l 1234 ab", 0.9),
                  kenali_jenis=jenis_tiruan, ambang=0.25)
    assert h["plat"] == "L1234AB"


def test_jenis_tak_yakin_menjadi_kosong():
    """TGT memperlakukan jenis kosong sebagai "tidak terbaca", bukan sebagai ketidakcocokan."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan,
                  kenali_jenis=lambda p: ("tak_yakin", 0.4), ambang=0.25)
    assert h["jenis"] is None


def test_plat_dengan_huruf_meragukan_memberi_posisi_ragu():
    """Pembaca yang tidak yakin pada satu huruf menandai posisinya, supaya aturan K46 bisa bekerja."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=None, baca=lambda p: ("L123?AB", 0.5),
                  kenali_jenis=jenis_tiruan, ambang=0.25)
    assert h["ragu"] == [4]
    assert h["plat"] == "L123AB" or "?" not in h["plat"]


# ─── Antrean berkas ─────────────────────────────────────────────────────────────────────────────────

def test_antrean_memproses_gambar_dan_menulis_hasil(tmp_path):
    masuk, keluar = tmp_path / "masuk", tmp_path / "keluar"
    masuk.mkdir()
    keluar.mkdir()
    import cv2

    cv2.imwrite(str(masuk / "abc123.png"), gambar_contoh())
    (masuk / "abc123.json").write_text(json.dumps({"gerbangId": 1, "arah": "masuk"}))

    jumlah = jaga_sekali(masuk, keluar, cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan,
                         kenali_jenis=jenis_tiruan, ambang=0.25)

    assert jumlah == 1
    hasil = json.loads((keluar / "abc123.json").read_text())
    assert hasil["plat"] == "L1234AB"
    assert hasil["gerbangId"] == 1, "keterangan dari sisi Node harus ikut kembali"
    assert hasil["arah"] == "masuk"
    assert not (masuk / "abc123.png").exists(), "gambar harus dibuang sesudah diproses; ia memuat plat"


def test_gambar_yang_sama_tidak_diproses_dua_kali(tmp_path):
    masuk, keluar = tmp_path / "masuk", tmp_path / "keluar"
    masuk.mkdir()
    keluar.mkdir()
    import cv2

    cv2.imwrite(str(masuk / "abc123.png"), gambar_contoh())
    jaga_sekali(masuk, keluar, cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan, kenali_jenis=jenis_tiruan,
                ambang=0.25)
    assert jaga_sekali(masuk, keluar, cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan,
                       kenali_jenis=jenis_tiruan, ambang=0.25) == 0


def test_berkas_rusak_tidak_menghentikan_antrean(tmp_path):
    """Satu berkas rusak tidak boleh membuat gerbang berhenti membaca kendaraan berikutnya."""
    masuk, keluar = tmp_path / "masuk", tmp_path / "keluar"
    masuk.mkdir()
    keluar.mkdir()
    import cv2

    (masuk / "rusak.png").write_bytes(b"ini bukan gambar")
    cv2.imwrite(str(masuk / "baik.png"), gambar_contoh())

    jumlah = jaga_sekali(masuk, keluar, cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan,
                         kenali_jenis=jenis_tiruan, ambang=0.25)

    assert jumlah == 1, "yang baik harus tetap terbaca"
    rusak = json.loads((keluar / "rusak.json").read_text())
    assert rusak["galat"], "yang rusak harus melapor, bukan hilang diam-diam"
    assert rusak["plat"] is None


def test_galat_tidak_pernah_memuat_jalur_berkas(tmp_path):
    """Nama berkas bisa memuat nomor plat (aturan yang sama dengan alat berplat lain di repo ini)."""
    masuk, keluar = tmp_path / "masuk", tmp_path / "keluar"
    masuk.mkdir()
    keluar.mkdir()
    (masuk / "L1234AB-rahasia.png").write_bytes(b"bukan gambar")

    jaga_sekali(masuk, keluar, cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan, kenali_jenis=jenis_tiruan,
                ambang=0.25)

    teks = (keluar / "L1234AB-rahasia.json").read_text()
    isi = json.loads(teks)
    assert "rahasia" not in isi["galat"], "pesan galat membocorkan nama berkas"
    assert str(masuk) not in isi["galat"], "pesan galat membocorkan jalur folder"


def test_ambang_jenis_wajib_disebut():
    """Ambang "tak yakin" tidak boleh tersembunyi di mesin (aturan Rencana 33)."""
    import layanan_baca

    with pytest.raises(TypeError):
        layanan_baca.muat_mesin(folder_akar="/kerja/data/keluaran")  # tanpa ambang_jenis


def test_tahap_kendaraan_yang_tidak_menemukan_apa_pun_TIDAK_menebak_jenis():
    """Cacat nyata yang ketemu saat bukti 26 Okt: jalan cadangan menebak "motor" dengan keyakinan 0,95 dari
    gambar yang tidak memuat kendaraan sama sekali. Tebakan meyakinkan atas gambar yang salah lebih berbahaya
    daripada tidak menjawab — di TGT ia muncul sebagai ketidakcocokan jenis, dan satpam dipanggil untuk
    sesuatu yang tidak pernah terjadi."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=lambda g: [], baca=baca_tiruan,
                  kenali_jenis=lambda p: ("motor", 0.95), ambang=0.25)
    assert h["plat"] == "L1234AB", "platnya tetap terbaca"
    assert h["jenis"] is None, "jenis ditebak dari gambar utuh padahal tahap kendaraan tidak menemukan apa pun"
    assert h["kendaraan"] == 0


def test_tanpa_tahap_kendaraan_jenis_boleh_dari_gambar_utuh():
    """Bila memang tidak ada tahap kendaraan, gambar utuh adalah satu-satunya yang ada."""
    h = baca_satu(gambar_contoh(), cari=CariTiruan(), cari_kendaraan=None, baca=baca_tiruan,
                  kenali_jenis=lambda p: ("mobil", 0.9), ambang=0.25)
    assert h["jenis"] == "mobil"
