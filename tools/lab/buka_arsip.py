"""Membuka arsip zip hasil unduhan dengan aman, di lab tanpa jaringan (spec bagian 8.6).

Arsip dari luar diperlakukan sebagai bahan tak tepercaya:
- SHA-256 arsip harus sama dengan yang dikunci; kalau tidak, tidak ada yang dibuka (kode 7);
- seluruh daftar isi diperiksa DULU: jalur mutlak, "..", garis miring terbalik, dan tautan simbolik membatalkan
  semuanya sebelum satu berkas pun ditulis; begitu juga dua butir bernama sama (huruf besar-kecil diabaikan) dengan isi
  berbeda. Butir bernama sama dengan isi identik dibuka sekali (Rencana 28: ekspor Roboflow);
- hanya akhiran di AKHIRAN_BOLEH yang dibuka (gambar, label teks, keterangan); buku catatan dan skrip dilewati;
- jumlah butir dan ukuran total dibatasi;
- folder tujuan harus kosong atau belum ada; bila gagal di tengah jalan, yang sudah ditulis dibersihkan.

Nama berkas TIDAK dicetak: pada dataset plat, nama berkas bisa memuat nomor plat (CLAUDE.md §4). Yang dicetak hanya
jumlah berkas per folder.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/buka_arsip.py daftar <arsip.zip> --sha256 <hex>
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/buka_arsip.py buka <arsip.zip> <folder-tujuan> --sha256 <hex> [--buang-lapis N] [--awalan original/ ...]

Kode keluar: 0 berhasil · 1 arsip ditolak · 2 salah pakai · 7 SHA-256 tidak cocok.
"""
import argparse
import hashlib
import shutil
import stat
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

AKHIRAN_BOLEH = {".jpg", ".jpeg", ".png", ".txt", ".yaml", ".yml", ".md", ".csv", ".json", ".xlsx"}
MAKS_BUTIR = 200_000
MAKS_BYTE = 20 * 1024**3
POTONG = 1 << 20
KEDALAMAN_RINGKAS = 3


class Ditolak(Exception):
    """Arsip yang tidak boleh dibuka."""


def sidik_berkas(jalur):
    sidik = hashlib.sha256()
    with open(jalur, "rb") as berkas:
        for potong in iter(lambda: berkas.read(POTONG), b""):
            sidik.update(potong)
    return sidik.hexdigest()


def jalur_aman(nama, buang_lapis):
    """Jalur relatif di dalam folder tujuan, atau None bila butirnya habis oleh --buang-lapis."""
    if "\\" in nama or nama.startswith("/") or (len(nama) > 1 and nama[1] == ":"):
        raise Ditolak("ada butir berjalur mutlak atau bergaris miring terbalik")
    bagian = PurePosixPath(nama).parts
    if ".." in bagian:
        raise Ditolak('ada butir yang jalurnya memuat ".."')
    sisa = bagian[buang_lapis:]
    return PurePosixPath(*sisa) if sisa else None


def rencana(arsip, buang_lapis=0, awalan=()):
    """Memeriksa seluruh daftar isi: (yang dibuka, yang dilewati). Melempar Ditolak bila ada satu saja yang berbahaya."""
    butir = arsip.infolist()
    if len(butir) > MAKS_BUTIR:
        raise Ditolak(f"{len(butir)} butir, melebihi batas {MAKS_BUTIR}")
    dibuka, dilewati, byte = [], Counter(), 0
    for info in butir:
        if stat.S_ISLNK(info.external_attr >> 16):
            raise Ditolak("arsip memuat tautan simbolik")
        jalur = jalur_aman(info.filename, buang_lapis)
        if info.is_dir() or jalur is None:
            continue
        if awalan and not any(jalur.as_posix().startswith(a) for a in awalan):
            dilewati["di luar awalan yang diminta"] += 1
            continue
        if jalur.suffix.lower() not in AKHIRAN_BOLEH:
            dilewati[f"akhiran {jalur.suffix.lower() or '(tanpa)'}"] += 1
            continue
        byte += info.file_size
        if byte > MAKS_BYTE:
            raise Ditolak(f"ukuran terbuka melebihi batas {MAKS_BYTE} byte")
        dibuka.append((info, jalur))
    return _tanpa_kembar(dibuka, dilewati)


def _tanpa_kembar(dibuka, dilewati):
    """Butir yang jalurnya sama bila huruf besar-kecil diabaikan (disk Windows tidak membedakannya): bila isinya identik (CRC dan
    ukuran), yang pertama dibuka dan sisanya dilewati serta dihitung (ekspor Roboflow memuat data.yaml 2-3 kali, Rencana 28); bila
    isinya berbeda, seluruh arsip ditolak sebelum satu berkas pun ditulis, karena salah satunya akan hilang atau tertimpa."""
    pertama, sisa = {}, []
    for info, jalur in dibuka:
        kunci = jalur.as_posix().lower()
        if kunci not in pertama:
            pertama[kunci] = info
            sisa.append((info, jalur))
        elif (info.CRC, info.file_size) == (pertama[kunci].CRC, pertama[kunci].file_size):
            dilewati["nama kembar berisi identik"] += 1
        else:
            raise Ditolak("ada dua butir bernama sama (huruf besar-kecil diabaikan) dengan isi berbeda")
    return sisa, dilewati


def ringkas(jalur_jalur):
    """Jumlah berkas per folder, paling dalam KEDALAMAN_RINGKAS tingkat. Nama berkas tidak ikut."""
    hitung = Counter()
    for jalur in jalur_jalur:
        hitung["/".join(jalur.parts[:-1][:KEDALAMAN_RINGKAS]) or "(akar)"] += 1
    return hitung


def buka(arsip, dibuka, tujuan):
    tujuan = Path(tujuan)
    if tujuan.exists() and any(tujuan.iterdir()):
        raise Ditolak("folder tujuan tidak kosong")
    tujuan.mkdir(parents=True, exist_ok=True)
    akar = tujuan.resolve()
    tulis = 0
    try:
        for info, jalur in dibuka:
            sasaran = (akar / jalur).resolve()
            if akar not in sasaran.parents:
                raise Ditolak("ada butir yang jalurnya keluar dari folder tujuan")
            if sasaran.exists():
                raise Ditolak("ada dua butir bernama sama")
            sasaran.parent.mkdir(parents=True, exist_ok=True)
            with arsip.open(info) as sumber, open(sasaran, "wb") as keluar:
                while True:
                    potong = sumber.read(POTONG)
                    if not potong:
                        break
                    tulis += len(potong)
                    if tulis > MAKS_BYTE:
                        raise Ditolak("isi yang terbuka melebihi batas: ukuran di daftar isi arsip tidak jujur")
                    keluar.write(potong)
    except BaseException:
        # Tujuan tadi kosong atau belum ada, jadi semua isinya berasal dari sini: bersihkan.
        for sisa in akar.iterdir():
            shutil.rmtree(sisa) if sisa.is_dir() else sisa.unlink()
        raise
    return tulis


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Membuka arsip zip hasil unduhan dengan aman.")
    urai.add_argument("perintah", choices=["daftar", "buka"])
    urai.add_argument("arsip")
    urai.add_argument("tujuan", nargs="?")
    urai.add_argument("--sha256", required=True)
    urai.add_argument("--buang-lapis", type=int, default=0)
    urai.add_argument("--awalan", action="append", default=[])
    p = urai.parse_args(argumen)
    if p.perintah == "buka" and not p.tujuan:
        print("Pakai: buka_arsip.py buka <arsip.zip> <folder-tujuan> --sha256 <hex>")
        return 2
    try:
        hasil = sidik_berkas(p.arsip)
    except OSError as galat:
        print(f"ARSIP TIDAK TERBACA: {type(galat).__name__}")
        return 2
    if hasil != p.sha256:
        print(f"SHA-256 TIDAK COCOK: arsip ber-SHA256 {hasil}, yang dikunci {p.sha256}. Tidak ada yang dibuka.")
        return 7
    try:
        with zipfile.ZipFile(p.arsip) as arsip:
            dibuka, dilewati = rencana(arsip, p.buang_lapis, tuple(p.awalan))
            for folder, jumlah in sorted(ringkas(jalur for _, jalur in dibuka).items()):
                print(f"{jumlah:>7} berkas  {folder}")
            for alasan, jumlah in sorted(dilewati.items()):
                print(f"{jumlah:>7} dilewati ({alasan})")
            if p.perintah == "daftar":
                print(f"{len(dibuka)} berkas akan dibuka, {sum(dilewati.values())} dilewati. Tidak ada yang ditulis.")
                return 0
            byte = buka(arsip, dibuka, p.tujuan)
    except Ditolak as galat:
        print(f"ARSIP DITOLAK: {galat}")
        return 1
    except zipfile.BadZipFile:
        print("ARSIP DITOLAK: bukan zip yang sah, atau isinya rusak")
        return 1
    except OSError as galat:
        # Pesan bawaan memuat jalur berkas, dan pada dataset plat jalur itu memuat nomor plat: jangan dicetak.
        print(f"GAGAL MENULIS: {type(galat).__name__} (errno {galat.errno}). Nama berkas tidak dicetak.")
        return 1
    print(f"{len(dibuka)} berkas dibuka ({byte} byte), {sum(dilewati.values())} dilewati")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
