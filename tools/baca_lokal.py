"""Baca plat LOKAL di PC tanpa Docker, hanya dengan model publik terkunci dan onnxruntime (K78, owner 13 Nov).

Owner ingin melihat program baca plat berjalan di PC ini. Mesin hasil latihan kita (pencari-cctv2-c1, pembaca-lanjut-r4) dan lab
Docker hanya ada di laptop lama, jadi alat ini memakai DUA MODEL PUBLIK yang sudah tercatat di tools/vendor.lock.json:
  - pencari plat: open-image-models yolo-v9-t-384 (bobot BELUM-JELAS: riset di laptop ini saja, K15);
  - pembaca huruf: fast-plate-ocr cct_s_v2_global (BOLEH-PRODUK, K47) -- titik awal fpo-indo-1, BELUM dilatih dengan plat kita.
Angka dari alat ini karena itu BUKAN angka rantai jualan: ia menunjukkan program berjalan dan memberi pembanding awal.

Tidak ada kode pihak ketiga yang dipasang atau dijalankan: hanya berkas ONNX (data, bukan program) yang dimuat onnxruntime,
dan tiap berkas ditolak bila SHA-256-nya tidak sama dengan kunci. Pra-proses dan penguraian ditulis di sini.

Keluaran di <keluar> memuat plat (data/ di-gitignore, CLAUDE.md §4): hasil.jsonl, potongan/, dan lembar.html hanya dibuka OWNER.
Agen hanya membaca ringkasan.json dan layar, yang berisi hitungan saja. Nama berkas gambar tidak pernah dicetak.

  jalan: python tools/baca_lokal.py jalan <folder gambar> data/keluaran/<nama>
  nilai: python tools/baca_lokal.py nilai data/keluaran/<nama> --salah 3,7 --tak-terbaca 12 --bukan-plat 5
"""
import argparse
import base64
import hashlib
import html
import importlib.util
import json
import statistics
import struct
import sys
import time
import zlib
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parent.parent
UNDUHAN = AKAR / "data" / "unduhan"
PENCARI = ("oim-yolo-v9-t-384-plat", UNDUHAN / "oim-yolo-v9-t-384" / "yolo-v9-t-384-license-plates-end2end.onnx")
PEMBACA = ("fpo-cct-s-v2-onnx", UNDUHAN / "fpo-cct-s-v2" / "cct_s_v2_global.onnx")
KONFIG = ("fpo-cct-s-v2-config", UNDUHAN / "fpo-cct-s-v2" / "cct_s_v2_global_plate_config.yaml")
UKURAN_PENCARI = 384
AMBANG_PENCARI = 0.4  # bawaan fast-alpr untuk pencari ini, ditetapkan sebelum hasil dilihat
AMBANG_YAKIN = 0.8  # yakin = peluang terendah di antara posisi huruf; sama artinya dengan rantai.py

_spek = importlib.util.spec_from_file_location("plat", AKAR / "tools" / "lab" / "plat.py")
plat = importlib.util.module_from_spec(_spek)
_spek.loader.exec_module(plat)


class GalatAlat(Exception):
    def __init__(self, pesan, kode):
        super().__init__(pesan)
        self.kode = kode


def sha256(jalur):
    h = hashlib.sha256()
    with open(jalur, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def berkas_terkunci(nama, jalur):
    """Jalur berkas bila SHA-256-nya sama dengan butir `nama` di vendor.lock.json; selain itu ditolak."""
    kunci = json.loads((AKAR / "tools" / "vendor.lock.json").read_text(encoding="utf-8"))
    butir = [b for b in kunci["berkas"] if b.get("nama") == nama]
    if len(butir) != 1:
        raise GalatAlat(f"butir {nama} tidak ada di kunci", 6)
    if not jalur.is_file():
        raise GalatAlat(f"berkas {nama} belum diunduh ke data/unduhan", 6)
    if sha256(jalur) != butir[0]["sha256"]:
        raise GalatAlat(f"berkas {nama} TIDAK sama dengan kunci: ditolak", 6)
    return jalur


def baca_konfig(teks):
    """Hanya kunci skalar yang dipakai; daftar plate_regions dibaca terpisah. Tidak memakai pemuat YAML."""
    hasil = {}
    for baris in teks.splitlines():
        if ":" in baris and not baris.startswith((" ", "#")):
            k, v = baris.split(":", 1)
            hasil[k.strip()] = v.strip().strip("'\"")
    awal = teks.index("plate_regions:")
    daftar = teks[teks.index("[", awal) + 1:teks.index("]", awal)]
    hasil["plate_regions"] = [w.strip().strip("'\"") for w in daftar.split(",") if w.strip()]
    for k in ("max_plate_slots", "img_height", "img_width"):
        hasil[k] = int(hasil[k])
    return hasil


def ubah_ukuran(av, rgb, lebar, tinggi):
    bingkai = av.VideoFrame.from_ndarray(np.ascontiguousarray(rgb), format="rgb24")
    return bingkai.reformat(width=lebar, height=tinggi, format="rgb24", interpolation="BILINEAR").to_ndarray()


def kotak_surat(av, rgb, ukuran=UKURAN_PENCARI):
    """Letterbox seperti open-image-models: skala sama, sisa diisi 114."""
    t, l = rgb.shape[:2]
    r = min(ukuran / t, ukuran / l)
    lb, tb = int(round(l * r)), int(round(t * r))
    kecil = ubah_ukuran(av, rgb, lb, tb)
    kiri, atas = int(round((ukuran - lb) / 2 - 0.1)), int(round((ukuran - tb) / 2 - 0.1))
    kanvas = np.full((ukuran, ukuran, 3), 114, np.uint8)
    kanvas[atas:atas + tb, kiri:kiri + lb] = kecil
    masukan = kanvas.astype(np.float32).transpose(2, 0, 1)[None] / 255.0
    return masukan, r, kiri, atas


def kotak_plat(keluaran, r, kiri, atas, lebar, tinggi, ambang):
    """keluaran [N,7] = batch, x1, y1, x2, y2, kelas, skor (koordinat letterbox) -> kotak di gambar asli."""
    hasil = []
    for baris in keluaran:
        skor = float(baris[6])
        if not 0.0 <= skor <= 1.0:
            raise GalatAlat("keluaran pencari tidak berbentuk yang diharapkan (skor di luar 0-1)", 7)
        if skor < ambang:
            continue
        x1, y1, x2, y2 = ((float(baris[1]) - kiri) / r, (float(baris[2]) - atas) / r,
                          (float(baris[3]) - kiri) / r, (float(baris[4]) - atas) / r)
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(lebar, int(round(x2))), min(tinggi, int(round(y2)))
        if x2 - x1 >= 4 and y2 - y1 >= 4:
            hasil.append((x1, y1, x2, y2, skor))
    return hasil


def urai_bacaan(peluang, abjad, pengisi):
    """peluang [slot, abjad] -> (teks, yakin). Yakin = peluang terendah di posisi huruf yang terisi."""
    indeks = peluang.argmax(axis=1)
    puncak = peluang.max(axis=1)
    huruf = [abjad[i] for i in indeks]
    terisi = [p for h, p in zip(huruf, puncak) if h != pengisi]
    return "".join(h for h in huruf if h != pengisi), (float(min(terisi)) if terisi else 0.0)


def png(rgb):
    t, l = rgb.shape[:2]
    mentah = b"".join(b"\x00" + rgb[y].tobytes() for y in range(t))

    def potong(jenis, isi):
        return struct.pack(">I", len(isi)) + jenis + isi + struct.pack(">I", zlib.crc32(jenis + isi) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + potong(b"IHDR", struct.pack(">IIBBBBB", l, t, 8, 2, 0, 0, 0))
            + potong(b"IDAT", zlib.compress(mentah, 6)) + potong(b"IEND", b""))


def tulis_lembar(jalur, baris):
    sel = []
    for b in baris:
        gambar = base64.b64encode(b["_png"]).decode()
        sel.append(f'<tr><td class="no">{b["baris"]}</td><td>g{b["gambar"]:04d}</td>'
                   f'<td><img src="data:image/png;base64,{gambar}" alt=""></td>'
                   f'<td class="teks">{html.escape(b["teks"]) or "(kosong)"}</td><td>{b["yakin"]:.2f}</td>'
                   f'<td>{"yakin" if b["status"] == "yakin" else "ragu"}</td><td>{"ya" if b["pola_sah"] else "tidak"}</td></tr>')
    jalur.write_text(f"""<!doctype html><html lang="id"><meta charset="utf-8"><title>Lembar baca lokal</title>
<style>body{{font:14px system-ui;margin:16px}}table{{border-collapse:collapse}}td,th{{border:1px solid #bbb;padding:4px 8px}}
img{{height:72px;image-rendering:pixelated}}.no{{font-weight:700}}.teks{{font:20px monospace}}</style>
<h1>Lembar baca lokal (model publik, belum dilatih plat kita)</h1>
<p>Untuk owner. Jawab dengan NOMOR BARIS saja, jangan menulis nomor plat: salah, tak terbaca (manusia pun tidak bisa membaca),
bukan plat.</p><table><tr><th>Baris</th><th>Gambar</th><th>Potongan</th><th>Bacaan</th><th>Yakin</th><th>Status</th><th>Pola Indonesia</th></tr>
{''.join(sel)}</table></html>""", encoding="utf-8")


def jalan(folder, keluar, ambang_pencari, ambang_yakin):
    import av
    import onnxruntime as ort
    av.logging.set_level(av.logging.PANIC)
    pencari = ort.InferenceSession(str(berkas_terkunci(*PENCARI)), providers=["CPUExecutionProvider"])
    pembaca = ort.InferenceSession(str(berkas_terkunci(*PEMBACA)), providers=["CPUExecutionProvider"])
    konfig = baca_konfig(berkas_terkunci(*KONFIG).read_text(encoding="utf-8"))
    abjad, pengisi = konfig["alphabet"], konfig["pad_char"]
    if pembaca.get_outputs()[0].shape[1:] != [konfig["max_plate_slots"], len(abjad)]:
        raise GalatAlat("bentuk keluaran pembaca tidak cocok dengan konfignya", 7)

    berkas = sorted(x for x in folder.iterdir() if x.is_file() and x.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not berkas:
        raise GalatAlat("tidak ada gambar di folder", 2)
    (keluar / "potongan").mkdir(parents=True, exist_ok=True)
    baris, gagal, tanpa_plat, waktu = [], {}, 0, []
    for no, jalur in enumerate(berkas, 1):
        try:
            with av.open(str(jalur)) as w:
                rgb = next(w.decode(video=0)).to_ndarray(format="rgb24")
        except Exception as e:  # pesan PyAV memuat jalur, dan nama berkas bisa memuat plat
            gagal[type(e).__name__] = gagal.get(type(e).__name__, 0) + 1
            continue
        mulai = time.perf_counter()
        masukan, r, kiri, atas = kotak_surat(av, rgb)
        kotak = kotak_plat(pencari.run(None, {"images": masukan})[0], r, kiri, atas, rgb.shape[1], rgb.shape[0],
                           ambang_pencari)
        if not kotak:
            tanpa_plat += 1
        for k, (x1, y1, x2, y2, skor) in enumerate(kotak, 1):
            potongan = rgb[y1:y2, x1:x2]
            m = ubah_ukuran(av, potongan, konfig["img_width"], konfig["img_height"])[None]
            p_plat, p_wilayah = pembaca.run(None, {"input": m})
            teks, yakin = urai_bacaan(p_plat[0], abjad, pengisi)
            nomor_baris = len(baris) + 1
            data_png = png(np.ascontiguousarray(potongan))
            (keluar / "potongan" / f"b{nomor_baris:04d}.png").write_bytes(data_png)
            baris.append({"baris": nomor_baris, "gambar": no, "plat_ke": k, "kotak": [x1, y1, x2, y2],
                          "skor_pencari": round(skor, 3), "teks": teks, "yakin": round(yakin, 3),
                          "status": "yakin" if yakin >= ambang_yakin else "ragu",
                          "pola_sah": plat.urai(teks) is not None,
                          "wilayah": konfig["plate_regions"][int(p_wilayah[0].argmax())],
                          "lebar_px": x2 - x1, "tinggi_px": y2 - y1, "_png": data_png})
        waktu.append((time.perf_counter() - mulai) * 1000)

    with open(keluar / "hasil.jsonl", "w", encoding="utf-8") as f:
        for b in baris:
            f.write(json.dumps({k: v for k, v in b.items() if k != "_png"}, ensure_ascii=False) + "\n")
    tulis_lembar(keluar / "lembar.html", baris)
    lebar = [b["lebar_px"] for b in baris]
    ringkas = {
        "alat": "tools/baca_lokal.py", "pencari": PENCARI[0], "pembaca": PEMBACA[0],
        "catatan": "model publik, belum dilatih plat kita; bukan angka rantai jualan",
        "ambang_pencari": ambang_pencari, "ambang_yakin": ambang_yakin,
        "gambar": len(berkas), "gambar_gagal_dibuka": gagal, "gambar_tanpa_plat": tanpa_plat,
        "plat_ditemukan": len(baris), "gambar_dengan_plat": len({b["gambar"] for b in baris}),
        "yakin": sum(b["status"] == "yakin" for b in baris), "ragu": sum(b["status"] == "ragu" for b in baris),
        "pola_indonesia_sah": sum(b["pola_sah"] for b in baris),
        "wilayah_tebakan_indonesia": sum(b["wilayah"] == "Indonesia" for b in baris),
        "lebar_plat_px": ({"min": min(lebar), "median": statistics.median(lebar), "maks": max(lebar)} if lebar else None),
        "ms_per_gambar_median": round(statistics.median(waktu), 1) if waktu else None,
    }
    (keluar / "ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ringkas


def daftar_nomor(teks):
    if not teks:
        return []
    try:
        return sorted({int(x) for x in teks.split(",") if x.strip()})
    except ValueError:
        raise GalatAlat("nomor baris harus angka dipisah koma", 2)


def nilai(keluar, salah, tak_terbaca, bukan_plat):
    baris = [json.loads(b) for b in (keluar / "hasil.jsonl").read_text(encoding="utf-8").splitlines() if b.strip()]
    semua = {b["baris"] for b in baris}
    for nama, d in (("salah", salah), ("tak-terbaca", tak_terbaca), ("bukan-plat", bukan_plat)):
        asing = [n for n in d if n not in semua]
        if asing:
            raise GalatAlat(f"--{nama}: nomor di luar lembar ({len(asing)} nomor)", 2)
    for a, b, na, nb in ((salah, tak_terbaca, "salah", "tak-terbaca"), (salah, bukan_plat, "salah", "bukan-plat"),
                         (tak_terbaca, bukan_plat, "tak-terbaca", "bukan-plat")):
        if set(a) & set(b):
            raise GalatAlat(f"nomor yang sama ada di --{na} dan --{nb}", 2)
    dikeluarkan = set(tak_terbaca) | set(bukan_plat)
    dinilai = [b for b in baris if b["baris"] not in dikeluarkan]
    hasil = {"baris_lembar": len(baris), "tak_terbaca": len(tak_terbaca), "bukan_plat": len(bukan_plat),
             "dinilai": len(dinilai), "benar": sum(b["baris"] not in salah for b in dinilai), "salah": len(salah)}
    for s in ("yakin", "ragu"):
        kel = [b for b in dinilai if b["status"] == s]
        hasil[f"{s}_dinilai"] = len(kel)
        hasil[f"{s}_benar"] = sum(b["baris"] not in salah for b in kel)
    hasil["yakin_tetapi_salah"] = hasil["yakin_dinilai"] - hasil["yakin_benar"]
    (keluar / "nilai.json").write_text(json.dumps(hasil, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return hasil


def jawaban_csv(jalur):
    """Kolom periksa_owner di hasil-baca.csv: S = salah, T = tak terbaca, B = bukan plat, kosong = benar."""
    import csv
    golongan = {"S": [], "T": [], "B": []}
    with open(jalur, encoding="utf-8-sig", newline="") as f:
        contoh = f.read(4096)
        f.seek(0)
        for b in csv.DictReader(f, delimiter=";" if contoh.count(";") > contoh.count(",") else ","):
            isi = (b.get("periksa_owner") or "").strip().upper()
            if not isi:
                continue
            if isi not in golongan:
                raise GalatAlat(f"periksa_owner baris {b.get('baris')}: '{isi[:3]}' bukan S, T, atau B", 2)
            golongan[isi].append(int(b["baris"]))
    return golongan["S"], golongan["T"], golongan["B"]


def utama(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="perintah", required=True)
    j = sub.add_parser("jalan")
    j.add_argument("folder", type=Path)
    j.add_argument("keluar", type=Path)
    j.add_argument("--ambang-pencari", type=float, default=AMBANG_PENCARI)
    j.add_argument("--ambang-yakin", type=float, default=AMBANG_YAKIN)
    n = sub.add_parser("nilai")
    n.add_argument("keluar", type=Path)
    n.add_argument("--salah")
    n.add_argument("--tak-terbaca")
    n.add_argument("--bukan-plat")
    n.add_argument("--csv", type=Path, help="hasil-baca.csv yang kolom periksa_owner-nya diisi owner (S/T/B)")
    a = p.parse_args(argv)
    try:
        if a.perintah == "jalan":
            hasil = jalan(a.folder, a.keluar, a.ambang_pencari, a.ambang_yakin)
        elif a.csv:
            if a.salah or a.tak_terbaca or a.bukan_plat:
                raise GalatAlat("pakai --csv ATAU nomor baris, bukan keduanya", 2)
            hasil = nilai(a.keluar, *jawaban_csv(a.csv))
        else:
            hasil = nilai(a.keluar, daftar_nomor(a.salah), daftar_nomor(a.tak_terbaca), daftar_nomor(a.bukan_plat))
    except GalatAlat as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return e.kode
    except OSError as e:  # jalur bisa memuat nama berkas berplat
        print(f"GAGAL: galat berkas ({type(e).__name__})", file=sys.stderr)
        return 3
    print(json.dumps(hasil, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(utama())
