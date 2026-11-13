"""Pengunduh satu berkas untuk pintu tools\\ambil-berkas.ps1 (arsip dan catatan dataset, spec bagian 8.6).

Hanya pustaka bawaan Python. Dijalankan di container berjaringan yang hanya melihat folder ini (read-only) dan satu
folder keluaran. Janjinya:
- hanya https dan hanya host yang disebut pintunya; tiap pengalihan diperiksa ulang, tidak diikuti buta;
- berkas ditulis sebagai <nama>.part dan baru diberi nama jadinya sesudah ukurannya cocok dan, bila dikunci,
  SHA-256-nya cocok;
- alamat hasil pengalihan tidak pernah dicetak atau dicatat utuh (bisa memuat tanda tangan sementara): hanya host-nya.

Kode keluar: 0 berhasil · 1 ditolak atau gagal · 2 salah pakai · 7 SHA-256 tidak cocok dengan kunci.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

POTONG = 1 << 20
LAPOR_TIAP = 256 << 20
MAKS_ALIH = 5
ALIH = {301, 302, 303, 307, 308}


class Ditolak(Exception):
    """Permintaan yang tidak boleh atau tidak bisa diteruskan."""


class TakCocok(Exception):
    """SHA-256 berkas yang diterima bukan yang dikunci."""


def periksa_alamat(alamat, host_boleh):
    bagian = urllib.parse.urlsplit(alamat)
    host = (bagian.hostname or "").lower()
    if bagian.scheme != "https":
        raise Ditolak(f"hanya https yang boleh (diberi {bagian.scheme or 'tanpa skema'} ke {host})")
    if bagian.username or bagian.password:
        raise Ditolak(f"alamat memuat nama pengguna ({host})")
    if host not in host_boleh:
        raise Ditolak(f"host di luar daftar: {host}")
    return host


class _TanpaAlih(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *argumen, **pilihan):
        return None


def minta(alamat):
    """Satu permintaan GET tanpa mengikuti pengalihan: (status, kepala, badan)."""
    pembuka = urllib.request.build_opener(_TanpaAlih)
    permintaan = urllib.request.Request(alamat, headers={"User-Agent": "cctvgerbang-ambil-berkas/1"})
    try:
        jawab = pembuka.open(permintaan, timeout=60)
        return jawab.status, jawab.headers, jawab
    except urllib.error.HTTPError as galat:
        return galat.code, galat.headers, galat


def sidik_berkas(jalur):
    sidik = hashlib.sha256()
    with open(jalur, "rb") as berkas:
        for potong in iter(lambda: berkas.read(POTONG), b""):
            sidik.update(potong)
    return sidik.hexdigest()


def unduh(alamat, tujuan, host_boleh, maks_byte, sha256="", minta=minta):
    """Mengunduh satu berkas ke `tujuan`. Mengembalikan catatan asal-usulnya; melempar Ditolak atau TakCocok."""
    tujuan = Path(tujuan)
    sementara = tujuan.with_name(tujuan.name + ".part")
    sekarang = alamat
    for _ in range(MAKS_ALIH + 1):
        host = periksa_alamat(sekarang, host_boleh)
        status, kepala, badan = minta(sekarang)
        if status not in ALIH:
            break
        lokasi = kepala.get("Location")
        if not lokasi:
            raise Ditolak(f"pengalihan tanpa tujuan (HTTP {status} dari {host})")
        sekarang = urllib.parse.urljoin(sekarang, lokasi)
    else:
        raise Ditolak(f"lebih dari {MAKS_ALIH} pengalihan")
    if status != 200:
        raise Ditolak(f"HTTP {status} dari {host}")
    janji = kepala.get("Content-Length")
    janji = int(janji) if janji and janji.isdigit() else None
    if janji is not None and janji > maks_byte:
        raise Ditolak(f"berkas {janji} byte, melebihi batas {maks_byte} byte")
    sidik, terima = hashlib.sha256(), 0
    with open(sementara, "wb") as berkas:
        while True:
            potong = badan.read(POTONG)
            if not potong:
                break
            terima += len(potong)
            if terima > maks_byte:
                raise Ditolak(f"melebihi batas {maks_byte} byte")
            sidik.update(potong)
            berkas.write(potong)
            if terima // LAPOR_TIAP != (terima - len(potong)) // LAPOR_TIAP:
                print(f"... {terima >> 20} MB", flush=True)
    if janji is not None and terima != janji:
        raise Ditolak(f"terpotong: diterima {terima} dari {janji} byte")
    hasil = sidik.hexdigest()
    if sha256 and hasil != sha256:
        raise TakCocok(hasil)
    sementara.replace(tujuan)
    return {"alamat": alamat, "host_akhir": host, "byte": terima, "sha256": hasil,
            "diambil": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Mengunduh satu berkas dari host yang diizinkan.")
    urai.add_argument("--alamat", required=True)
    urai.add_argument("--keluar", required=True, help="folder tujuan")
    urai.add_argument("--nama", required=True, help="nama berkas jadi")
    urai.add_argument("--maks-byte", type=int, required=True)
    urai.add_argument("--host", action="append", required=True)
    urai.add_argument("--sha256", default="")
    p = urai.parse_args(argumen)
    if "/" in p.nama or "\\" in p.nama or p.nama.startswith("."):
        print("DITOLAK: nama berkas tidak boleh memuat pemisah folder atau diawali titik")
        return 2
    tujuan = Path(p.keluar) / p.nama
    try:
        if tujuan.exists():
            hasil = sidik_berkas(tujuan)
            if p.sha256 and hasil != p.sha256:
                raise TakCocok(hasil)
            print(f"SUDAH ADA {p.nama}: {tujuan.stat().st_size} byte, SHA256 {hasil}. Tidak ada yang diunduh.")
            return 0
        asal = unduh(p.alamat, tujuan, {h.lower() for h in p.host}, p.maks_byte, p.sha256)
    except TakCocok as galat:
        print(f"SHA-256 TIDAK COCOK: berkas ber-SHA256 {galat}, yang dikunci {p.sha256}. Berkas tidak dipakai.")
        return 7
    except Ditolak as galat:
        print(f"DITOLAK: {galat}")
        return 1
    except OSError as galat:
        print(f"GAGAL: {type(galat).__name__}: {getattr(galat, 'reason', '')}")
        return 1
    tujuan.with_name(tujuan.name + ".asal.json").write_text(json.dumps(asal, indent=2))
    print(f"TERSIMPAN {p.nama}: {asal['byte']} byte, SHA256 {asal['sha256']}, dari {asal['host_akhir']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
