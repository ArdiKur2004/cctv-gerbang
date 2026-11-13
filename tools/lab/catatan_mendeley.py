"""Membaca catatan dataset dari API publik Mendeley Data, di lab tanpa jaringan.

Catatannya berupa satu berkas JSON yang diambil lewat tools\\ambil-berkas.ps1. Ia memuat izin dataset dan SHA-256 tiap
berkas menurut penerbitnya. Dua perintah:

  izin  <catatan.json>
        mencetak jati diri dataset, teks izinnya apa adanya, dan jumlah berkas per folder
  cocok <catatan.json> <folder-terbuka> <jalur>=<id-folder> [...]
        memastikan isi <folder-terbuka>/<jalur> persis sama dengan yang dicatat penerbit untuk folder ber-ID itu:
        tak ada yang kurang, tak ada yang lebih, tak ada yang isinya berbeda

Nama berkas TIDAK dicetak: pada INDO-ALPR nama berkas memuat nomor plat (CLAUDE.md §4). Yang dicetak hanya hitungan.

Kode keluar: 0 berhasil atau semuanya cocok · 1 ada yang tidak cocok atau berkas tak terbaca · 2 salah pakai.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

POTONG = 1 << 20
PAKAI = "Pakai: catatan_mendeley.py izin <catatan.json> | cocok <catatan.json> <folder-terbuka> <jalur>=<id-folder> [...]"


def muat(jalur):
    return json.loads(Path(jalur).read_text(encoding="utf-8"))


def sidik_berkas(jalur):
    sidik = hashlib.sha256()
    with open(jalur, "rb") as berkas:
        for potong in iter(lambda: berkas.read(POTONG), b""):
            sidik.update(potong)
    return sidik.hexdigest()


def izin(catatan):
    d = muat(catatan)
    berkas = d.get("files") or []
    print(f"id      : {d.get('id')}")
    print(f"nama    : {d.get('name')}")
    print(f"versi   : {d.get('version')}")
    print(f"doi     : {(d.get('doi') or {}).get('id')}")
    print(f"terbit  : {d.get('publish_date')}")
    print(f"lembaga : {', '.join(i.get('name', '') for i in d.get('institutions') or [])}")
    print(f"pembuat : {', '.join((k.get('first_name', '') + ' ' + k.get('last_name', '')).strip() for k in d.get('contributors') or [])}")
    print("izin, apa adanya:")
    print(json.dumps(d.get("data_licence"), indent=2, ensure_ascii=False))
    jumlah, byte = Counter(), Counter()
    for b in berkas:
        folder = b.get("folder_id") or "(akar)"
        jumlah[folder] += 1
        byte[folder] += b.get("size") or 0
    print(f"berkas tercatat: {len(berkas)}, {sum(byte.values())} byte")
    for folder in sorted(jumlah):
        print(f"  {jumlah[folder]:>6} berkas {byte[folder]:>12} byte  folder_id {folder}")
    return 0


def cocok(catatan, terbuka, pasangan):
    berkas = muat(catatan).get("files") or []
    buruk = 0
    for jalur, id_folder in pasangan:
        janji = Counter((b.get("content_details") or {}).get("sha256_hash") for b in berkas if b.get("folder_id") == id_folder)
        folder = Path(terbuka) / jalur
        nyata = Counter(sidik_berkas(p) for p in sorted(folder.iterdir()) if p.is_file()) if folder.is_dir() else Counter()
        sama = sum((janji & nyata).values())
        kurang, lebih = sum((janji - nyata).values()), sum((nyata - janji).values())
        beres = bool(janji) and kurang == 0 and lebih == 0
        buruk += not beres
        print(f"{'COCOK' if beres else 'BEDA '} {jalur}: penerbit mencatat {sum(janji.values())}, di folder {sum(nyata.values())}, sama {sama}, kurang {kurang}, lebih {lebih}")
    return 1 if buruk else 0


def utama(argumen=None):
    argumen = sys.argv[1:] if argumen is None else argumen
    try:
        if len(argumen) == 2 and argumen[0] == "izin":
            return izin(argumen[1])
        if len(argumen) >= 4 and argumen[0] == "cocok" and all("=" in a for a in argumen[3:]):
            return cocok(argumen[1], argumen[2], [tuple(a.split("=", 1)) for a in argumen[3:]])
    except OSError as galat:
        # Pesan bawaan memuat jalur berkas, dan pada INDO-ALPR jalur itu memuat nomor plat: jangan dicetak.
        print(f"GAGAL MEMBACA: {type(galat).__name__} (errno {galat.errno}). Nama berkas tidak dicetak.")
        return 1
    print(PAKAI)
    return 2


if __name__ == "__main__":
    sys.exit(utama())
