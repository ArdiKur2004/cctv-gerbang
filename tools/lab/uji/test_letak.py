"""Uji tools/lab/letak.py (Rencana 21, K39 langkah 2): ciri letak plat di kendaraan, 24 aturan, penilaian dari label owner sisi
latih, aturan memilih, dan CLI banding tanpa model."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import letak  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "letak.py"
MOBIL_DEPAN = [100, 100, 300, 260, "mobil"]  # lebar/tinggi 1,25: tampak depan atau belakang
MOBIL_SAMPING = [100, 100, 400, 200, "mobil"]  # 3,0: tampak samping


def test_ciri_letak_plat_di_kendaraan():
    f = letak.ciri([180, 220, 220, 236], MOBIL_DEPAN)

    assert {k: f[k] for k in ("rx", "ry", "rasio_plat", "rasio_kendaraan")} == pytest.approx(
        {"rx": 0.5, "ry": 0.8, "rasio_plat": 2.5, "rasio_kendaraan": 1.25}) and f["jenis"] == "mobil"


def test_dua_puluh_empat_aturan_bernama_unik():
    assert len(letak.ATURAN) == 24 and "tanpa" in letak.ATURAN and "ry0.4_rx0.3_rp_tampak" in letak.ATURAN


def test_lolos_per_syarat():
    bawah_tengah = letak.ciri([180, 220, 220, 236], MOBIL_DEPAN)
    atas = letak.ciri([180, 110, 220, 126], MOBIL_DEPAN)
    samping = letak.ciri([230, 170, 270, 186], MOBIL_SAMPING)

    assert letak.lolos(bawah_tengah, letak.ATURAN["ry0.6_rx0.3_rp_tampak"])
    assert not letak.lolos(atas, letak.ATURAN["ry0.4"]) and letak.lolos(atas, letak.ATURAN["tanpa"])
    assert not letak.lolos(samping, letak.ATURAN["tampak"]) and letak.lolos(samping, letak.ATURAN["ry0.6"])
    assert letak.lolos(letak.ciri([180, 220, 220, 236], None), letak.ATURAN["tanpa"])
    assert not letak.lolos(letak.ciri([180, 220, 220, 236], None), letak.ATURAN["ry0.4"])  # tanpa kendaraan: tidak lolos syarat


def penampakan_(nomor, kotak, kendaraan):
    return {"video": "v.mp4", "jalur": nomor, "kedatangan": nomor, "tampak": [[i, *kotak] for i in range(3)],
            "kendaraan": [kendaraan] * 3}


def test_nilai_aturan_per_kedatangan_berlabel():
    tampak = [penampakan_(1, [180, 220, 220, 236], MOBIL_DEPAN), penampakan_(2, [180, 110, 220, 126], MOBIL_DEPAN),
              penampakan_(3, [230, 170, 270, 186], MOBIL_SAMPING)]
    lembar = {"baris": [{"nomor": n, "video": "v.mp4", "kedatangan": n, "status": "yakin"} for n in (1, 2, 3)]}

    h = letak.nilai_aturan(tampak, lembar, bukan_plat={2, 3}, aturan=letak.ATURAN["ry0.6_tampak"])

    assert h == {"plat": 1, "plat_lolos": 1, "bukan": 2, "bukan_lolos": 0, "bukan_yakin": 2, "bukan_yakin_lolos": 0}


def test_pilih_aturan_minimal_90_persen_plat_lalu_bukan_plat_tersedikit_lalu_syarat_tersedikit():
    hasil = [{"nama": "tanpa", "syarat": 0, "plat": 10, "plat_lolos": 10, "bukan_lolos": 20},
             {"nama": "ry0.6", "syarat": 1, "plat": 10, "plat_lolos": 8, "bukan_lolos": 2},  # 80% < 90%
             {"nama": "ry0.4", "syarat": 1, "plat": 10, "plat_lolos": 9, "bukan_lolos": 5},
             {"nama": "ry0.4_tampak", "syarat": 2, "plat": 10, "plat_lolos": 9, "bukan_lolos": 5}]

    assert letak.pilih_aturan(hasil)["nama"] == "ry0.4"


def test_cli_banding_dari_berkas_tanpa_model(tmp_path):
    (tmp_path / "p.jsonl").write_text("\n".join(json.dumps(t) for t in [
        penampakan_(1, [180, 220, 220, 236], MOBIL_DEPAN), penampakan_(2, [180, 110, 220, 126], MOBIL_DEPAN)]))
    (tmp_path / "l.json").write_text(json.dumps({"baris": [
        {"nomor": n, "video": "v.mp4", "kedatangan": n, "status": "ragu"} for n in (1, 2)]}))

    hasil = subprocess.run([sys.executable, str(SKRIP), "banding", str(tmp_path / "p.jsonl"), str(tmp_path / "l.json"),
                            str(tmp_path / "b.json"), "--bukan-plat", "2"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    b = json.loads((tmp_path / "b.json").read_text())
    assert len(b["aturan"]) == 24 and b["terpilih"]["plat_lolos"] == 1 and b["terpilih"]["bukan_lolos"] == 0
    assert "v.mp4" not in hasil.stdout + hasil.stderr
