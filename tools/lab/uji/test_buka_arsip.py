"""Uji tools/lab/buka_arsip.py: arsip dari luar adalah bahan tak tepercaya, dan nama berkasnya tidak boleh tercetak."""
import hashlib
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import buka_arsip as ba  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "buka_arsip.py"
ISI_WAJAR = {
    "data-abc/original/train/B 1234 XYZ_0001.png": b"gambar-1",
    "data-abc/original/test/D 5678 AB_0002.jpg": b"gambar-2",
    "data-abc/augmentation/rain/train/B 1234 XYZ_0001.png": b"gambar-olahan",
    "data-abc/README.md": b"keterangan",
    "data-abc/a.ipynb": b"{}",
    "data-abc/latih.py": b"print('jangan dijalankan')",
}


def buat_arsip(jalur, isi, tautan=()):
    with zipfile.ZipFile(jalur, "w") as arsip:
        for nama, data in isi.items():
            arsip.writestr(nama, data)
        for nama in tautan:
            info = zipfile.ZipInfo(nama)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            arsip.writestr(info, "/etc/passwd")
    return jalur, hashlib.sha256(jalur.read_bytes()).hexdigest()


def isi_folder(folder):
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()) if folder.exists() else []


def test_daftar_hanya_menghitung_dan_tidak_menulis_apa_pun(tmp_path, capsys):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)

    kode = ba.utama(["daftar", str(arsip), "--sha256", sidik])

    cetak = capsys.readouterr().out
    assert kode == 0
    assert "data-abc/original/train" in cetak and "4 berkas akan dibuka, 2 dilewati" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak, "nama berkas memuat nomor plat; tidak boleh tercetak"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.zip"]


def test_buka_menulis_berkas_yang_boleh_dan_melewati_buku_catatan_serta_skrip(tmp_path, capsys):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    cetak = capsys.readouterr().out
    assert kode == 0, cetak
    assert isi_folder(tujuan) == sorted(n for n in ISI_WAJAR if not n.endswith((".ipynb", ".py")))
    assert (tujuan / "data-abc/original/train/B 1234 XYZ_0001.png").read_bytes() == b"gambar-1"
    assert "dilewati (akhiran .ipynb)" in cetak and "dilewati (akhiran .py)" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak


def test_lapis_teratas_dibuang_dan_hanya_awalan_yang_diminta_yang_dibuka(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik, "--buang-lapis", "1", "--awalan", "original/"])

    assert kode == 0
    assert isi_folder(tujuan) == ["original/test/D 5678 AB_0002.jpg", "original/train/B 1234 XYZ_0001.png"]


def test_sidik_arsip_yang_tidak_cocok_dengan_kunci_tidak_dibuka(tmp_path, capsys):
    arsip, _ = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", "0" * 64])

    assert kode == 7
    assert "TIDAK COCOK" in capsys.readouterr().out
    assert isi_folder(tujuan) == []


def test_butir_yang_memanjat_keluar_folder_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "../luar.txt": b"jahat"})
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    assert kode == 1
    assert isi_folder(tujuan) == [] and not (tmp_path / "luar.txt").exists()


def test_butir_berjalur_mutlak_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "/tmp/luar.txt": b"jahat"})

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_butir_bergaris_miring_terbalik_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "..\\luar.txt": b"jahat"})

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_tautan_simbolik_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x"}, tautan=["tautan.txt"])

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_folder_tujuan_yang_sudah_berisi_tidak_ditimpa(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"baru"})
    tujuan = tmp_path / "keluar"
    tujuan.mkdir()
    (tujuan / "baik.txt").write_bytes(b"lama")

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    assert kode == 1
    assert (tujuan / "baik.txt").read_bytes() == b"lama"


def test_arsip_yang_melebihi_batas_ukuran_ditolak(tmp_path, monkeypatch):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"a.txt": b"x" * 600, "b.txt": b"x" * 600})
    monkeypatch.setattr(ba, "MAKS_BYTE", 1000)

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_dua_butir_bernama_sama_ditolak_dan_yang_sudah_ditulis_dibersihkan(tmp_path):
    jalur = tmp_path / "a.zip"
    with zipfile.ZipFile(jalur, "w") as arsip:
        arsip.writestr("sama.txt", b"satu")
        arsip.writestr("sama.txt", b"dua")
    sidik = hashlib.sha256(jalur.read_bytes()).hexdigest()

    assert ba.utama(["buka", str(jalur), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def arsip_kembar(jalur, isi):
    """Zip dengan butir bernama kembar (zipfile mengizinkannya dengan peringatan)."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with zipfile.ZipFile(jalur, "w") as arsip:
            for nama, data in isi:
                arsip.writestr(nama, data)
    return jalur, hashlib.sha256(jalur.read_bytes()).hexdigest()


def test_nama_kembar_berisi_identik_dibuka_sekali(tmp_path, capsys):
    # Rencana 28: ekspor Roboflow memuat data.yaml 2-3 kali dengan isi identik. Salinan identik tidak bisa menimpa apa pun, jadi dibuka
    # sekali dan sisanya dilewati serta dihitung.
    jalur, sidik = arsip_kembar(tmp_path / "a.zip", [("data.yaml", b"names: [a]"), ("data.yaml", b"names: [a]"),
                                                       ("data.yaml", b"names: [a]"), ("train/images/x.jpg", b"gambar")])

    assert ba.utama(["buka", str(jalur), str(tmp_path / "keluar"), "--sha256", sidik]) == 0
    assert isi_folder(tmp_path / "keluar") == ["data.yaml", "train/images/x.jpg"]
    assert (tmp_path / "keluar" / "data.yaml").read_bytes() == b"names: [a]"
    assert "2 dilewati (nama kembar berisi identik)" in capsys.readouterr().out


def test_nama_yang_hanya_beda_huruf_besar_kecil_dengan_isi_berbeda_ditolak_sebelum_menulis(tmp_path):
    # Disk Windows tidak membedakan huruf besar-kecil, jadi dua butir ini bertabrakan; isinya berbeda, jadi salah satunya akan hilang.
    jalur, sidik = arsip_kembar(tmp_path / "a.zip", [("train/A.jpg", b"satu"), ("train/a.jpg", b"dua")])

    assert ba.utama(["buka", str(jalur), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert not (tmp_path / "keluar").exists()  # ditolak saat memeriksa daftar isi, sebelum folder dibuat


def test_baris_perintah_sampai_ke_berkas_yang_terbuka(tmp_path):
    # Rantainya: baris perintah -> periksa sidik -> periksa daftar isi -> tulis.
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    hasil = subprocess.run([sys.executable, str(SKRIP), "buka", str(arsip), str(tujuan), "--sha256", sidik,
                            "--buang-lapis", "1", "--awalan", "original/"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert len(isi_folder(tujuan)) == 2
    assert "2 berkas dibuka" in hasil.stdout


def test_galat_menulis_tidak_membocorkan_nama_berkas(tmp_path, capsys):
    # Pesan galat bawaan Python memuat jalur berkas; pada dataset plat, jalur itu memuat nomor plat.
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"B 1234 XYZ_0001.png": b"gambar-1"})
    tujuan = tmp_path / "keluar"
    tujuan.mkdir()
    tujuan.chmod(0o500)

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    cetak = capsys.readouterr()
    tujuan.chmod(0o700)
    assert kode == 1
    assert "GAGAL MENULIS" in cetak.out
    assert "1234" not in cetak.out + cetak.err
