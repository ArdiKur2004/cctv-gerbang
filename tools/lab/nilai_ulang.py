"""Membetulkan label set uji dari jawaban owner atas lembar label yang dicurigai (K22), lalu menilai ulang tiap pembaca.

Aturan:
- Baris lembar curiga yang tulisan B-nya benar menurut owner: label diganti tulisan B. Golongan dan kelompok mobil atau
  motor dihitung ulang dari label baru (kode wilayah dan nomor urut bisa berubah); terang atau gelap tetap.
- Baris yang tulisan A maupun B-nya salah: platnya dikeluarkan dari set uji (tulisan benarnya tidak diketahui).
- Baris lembar contoh yang labelnya diketahui salah (pemeriksaan owner 14 Okt) dan tidak dibetulkan lewat lembar curiga:
  dikeluarkan juga, karena tulisan benarnya tidak ada di repo (owner tidak diminta mengetik nomor plat).
- Label yang dibetulkan tetapi sama dengan plat di sisi lain: platnya dikeluarkan dari sisi yang dibetulkan, karena satu
  plat hanya boleh ada di satu sisi (spec 8.3). Sisi uji: label baru sama dengan plat latih (K23). Sisi latih (--sisi
  latih): label baru sama dengan plat uji (K24), sehingga set uji yang sudah dibetulkan tetap utuh. Dugaannya kendaraan
  yang sama yang salah dilabeli penerbit.
- --salah-contoh hanya untuk sisi uji, karena lembar contoh berisi plat set uji.
- Kedatangan lain: label penerbit dipakai apa adanya.

Pembaca dinilai ulang dari bacaan yang sudah tersimpan (hasil.jsonl), tanpa menjalankan modelnya lagi.

Keluaran: pembagian-koreksi.json (memuat plat; data/) dan ringkasan-koreksi.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/nilai_ulang.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/lembar-curiga/lembar-curiga.json /kerja/data/keluaran/lembar-contoh/lembar-contoh.json /kerja/data/keluaran/set-uji-koreksi --b-benar <nomor,...> --keduanya-salah <nomor,...> --salah-contoh 19,22,25,35,36,54 --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, ringkas, uraikan  # noqa: E402
from plat import golongan, kelompok_kendaraan, urai  # noqa: E402


class SalahPakai(Exception):
    """Jawaban tidak bisa dipakai apa adanya: nomor baris ganda, di luar lembar, atau tak terbaca."""


def nomor(teks):
    """"3, 7,12" -> {3, 7, 12}; teks kosong -> himpunan kosong."""
    try:
        return {int(x) for x in teks.split(",") if x.strip()}
    except ValueError:
        raise SalahPakai(f"daftar nomor baris tidak terbaca: {teks!r}") from None


def koreksi(pembagian, lembar_curiga, lembar_contoh, b_benar, keduanya_salah, salah_contoh, sisi="uji"):
    """Kembali: (pembagian dengan sisi `sisi` yang sudah dibetulkan, hitungan tanpa nomor plat). Sisi lain tidak diubah."""
    if sisi not in ("uji", "latih"):
        raise SalahPakai(f"sisi tidak dikenal: {sisi}")
    if sisi == "latih" and salah_contoh:
        raise SalahPakai("lembar contoh hanya berisi plat set uji; --salah-contoh tidak berlaku untuk sisi latih")
    lain = "latih" if sisi == "uji" else "uji"
    curiga = {c["nomor"]: c for c in lembar_curiga["contoh"]}
    contoh = {c["nomor"]: c for c in lembar_contoh["contoh"]}
    if b_benar & keduanya_salah:
        raise SalahPakai(f"baris {sorted(b_benar & keduanya_salah)} disebut di dua daftar sekaligus")
    luar = sorted(n for n in b_benar | keduanya_salah if n not in curiga)
    if luar:
        raise SalahPakai(f"baris {luar} tidak ada di lembar label yang dicurigai")
    luar = sorted(n for n in salah_contoh if n not in contoh)
    if luar:
        raise SalahPakai(f"baris {luar} tidak ada di lembar contoh")
    ganti = {curiga[n]["teks"]: curiga[n]["usulan"] for n in b_benar}
    keluar = {curiga[n]["teks"] for n in keduanya_salah}
    keluar |= {contoh[n]["teks"] for n in salah_contoh if contoh[n]["teks"] not in ganti}
    teks_lain = {a["teks"] for a in pembagian[lain]}
    hasil, bocor = [], 0
    for k in pembagian[sisi]:
        if k["teks"] in keluar:
            continue
        if k["teks"] in ganti:
            plat = urai(ganti[k["teks"]])
            if plat.teks in teks_lain:
                # K23 (sisi uji) dan K24 (sisi latih): label baru = plat di sisi lain. Satu plat hanya di satu sisi (spec 8.3).
                bocor += 1
                continue
            cahaya = k["kelompok"].rsplit("-", 1)[1]
            k = {**k, "teks": plat.teks, "label_penerbit": k["teks"], "golongan": golongan(plat),
                 "kelompok": f"{kelompok_kendaraan(plat)}-{cahaya}"}
        hasil.append(k)
    hitung = {"sisi": sisi, "dibetulkan": len(ganti), "dikeluarkan": len(keluar), "dikeluarkan_bocor": bocor,
              "plat_di_kedua_sisi": sum(k["teks"] in teks_lain for k in hasil),
              "kedatangan_per_kelompok": {g: sum(k["kelompok"] == g for k in hasil) for g in KELOMPOK}}
    baru = dict(pembagian)
    baru[sisi] = hasil
    return baru, hitung


def baca_hasil(jalur):
    """berkas -> bacaan bersih, dari hasil.jsonl sebuah pembaca."""
    return {b["berkas"]: b["bacaan"] for b in map(json.loads, Path(jalur).read_text().splitlines())}


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Membetulkan label set uji dan menilai ulang pembaca (K22).")
    for nama in ("pembagian", "lembar_curiga", "lembar_contoh", "keluar"):
        urai_argumen.add_argument(nama)
    urai_argumen.add_argument("--b-benar", default="")
    urai_argumen.add_argument("--keduanya-salah", default="")
    urai_argumen.add_argument("--salah-contoh", default="")
    urai_argumen.add_argument("--hasil", action="append", default=[], help="nama=jalur hasil.jsonl, boleh berulang")
    urai_argumen.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    p = urai_argumen.parse_args(argumen)
    try:
        if not p.hasil or not all("=" in h for h in p.hasil):
            raise SalahPakai("--hasil harus diberi sebagai nama=jalur, paling sedikit satu")
        baru, hitung = koreksi(json.loads(Path(p.pembagian).read_text()), json.loads(Path(p.lembar_curiga).read_text()),
                               json.loads(Path(p.lembar_contoh).read_text()), nomor(p.b_benar),
                               nomor(p.keduanya_salah), nomor(p.salah_contoh), sisi=p.sisi)
    except SalahPakai as galat:
        print(f"SALAH PAKAI: {galat}")
        return 2
    ringkasan = {**hitung, "pembaca": {nama: ringkas(baru, baca_hasil(jalur), p.sisi)
                                       for nama, jalur in (h.split("=", 1) for h in p.hasil)}}
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian-koreksi.json").write_text(json.dumps(baru, indent=1))
    (keluar / "ringkasan-koreksi.json").write_text(json.dumps(ringkasan, indent=2))
    lain = "latih" if p.sisi == "uji" else "uji"
    print(f"dibetulkan {hitung['dibetulkan']}, dikeluarkan {hitung['dikeluarkan']}, "
          f"dikeluarkan karena sama dengan plat {lain} {hitung['dikeluarkan_bocor']}, "
          f"plat di kedua sisi {hitung['plat_di_kedua_sisi']}; kedatangan {p.sisi} {hitung['kedatangan_per_kelompok']}")
    for nama, per_kelompok in ringkasan["pembaca"].items():
        print(nama)
        for k in KELOMPOK:
            print(f"  {k:<13} {uraikan(per_kelompok[k])}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
