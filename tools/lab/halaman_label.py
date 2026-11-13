"""Halaman pelabelan untuk OWNER: plat terlewat dan bacaan salah di tangkapan owner (Rencana 24 Task 4, K44).

- buat: dari keluaran baca_gambar.py dan jawaban owner atas dua lembar tangkapan, membuat <keluar>/halaman.html, gambar/ (salinan
  gambar bernama nomor, tanpa nama asli), dan butir.json. Butir halaman:
  - "terlewat" (t<kartu>): gambar yang platnya terbaca owner tetapi tidak ditemukan mesin; owner menarik kotak plat dan mengetik
    teksnya;
  - "salah" (s<baris>): bacaan mesin yang salah; owner mengetik teks yang benar dan boleh menarik ulang kotaknya.
  butir.json juga memuat label tetap dari lembar plat (benar, tak terbaca, bukan plat), kelompok dan sisi tiap gambar, dan gambar
  yang dikeluarkan owner.
- terima: menggabungkan label tetap dengan berkas yang diunduh dari halaman (label-tangkapan.json) menjadi label.json dan
  ringkasan-label.json (hitungan saja).

Halaman dibuka owner di laptop dan tidak memuat apa pun dari luar. butir.json, halaman, gambar, dan label.json memuat plat: agen
tidak membukanya (CLAUDE.md §7).

  buat:   powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/halaman_label.py buat /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca /kerja/data/keluaran/lembar-tangkapan-plat/lembar-rantai.json /kerja/data/keluaran/lembar-tangkapan-tanpa-plat/lembar-tanpa-plat.json /kerja/data/alat-sementara/jawaban-24-tanpa-plat.json /kerja/data/keluaran/label-tangkapan --salah <n,...> --tak-terbaca <n,...> --bukan-plat <n,...>
  terima: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/halaman_label.py terima /kerja/data/keluaran/label-tangkapan/butir.json /kerja/data/capture/label-tangkapan.json /kerja/data/keluaran/label-tangkapan
  nilai:  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/halaman_label.py nilai /kerja/data/keluaran/label-tangkapan/label.json /kerja/data/keluaran/tangkapan-owner-baca/peta-berkas.json <folder keluaran baca_gambar> <hasil.json>
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from lembar_rantai import nomor_baris  # noqa: E402
from plat import bersihkan, urai  # noqa: E402

MIN_SISI = 4  # piksel; kotak lebih kecil dianggap salah tarik
IOU_RANTAI = 0.3  # kotak tangkapan ditarik owner dengan tangan, jadi lebih longgar dari IOU_MIN 0,5 di deteksi.py (Rencana 24)


class LabelDitolak(ValueError):
    """Pesannya aman dicetak: hanya nomor butir atau baris, tanpa teks plat."""


def _kotak(k):
    return [int(round(float(x))) for x in k[:4]]


def buat(folder_capture, folder_baca, lembar_plat, lembar_tanpa, jawaban_tanpa, keluar, salah=(), tak_terbaca=(), bukan_plat=()):
    """Kembali: hitungan saja."""
    folder_baca, keluar = Path(folder_baca), Path(keluar)
    peta = json.loads((folder_baca / "peta-berkas.json").read_text())
    tiba = {}
    for b in (folder_baca / "kedatangan.jsonl").read_text().splitlines():
        if b.strip():
            k = json.loads(b)
            tiba[(k["video"], k["nomor"])] = k
    baris_plat = json.loads(Path(lembar_plat).read_text())["baris"]
    kartu = {b["nomor"]: b for b in json.loads(Path(lembar_tanpa).read_text())["baris"]}
    jawab = json.loads(Path(jawaban_tanpa).read_text())
    salah, tak_terbaca, bukan_plat = set(salah), set(tak_terbaca), set(bukan_plat)
    asing = (salah | tak_terbaca | bukan_plat) - {b["nomor"] for b in baris_plat}
    if asing:
        raise LabelDitolak(f"nomor baris tidak ada di lembar plat: {sorted(asing)}")
    if salah & tak_terbaca or salah & bukan_plat or tak_terbaca & bukan_plat:
        raise LabelDitolak("ada baris yang disebut di dua jenis sekaligus")
    disebut = [int(n) for n in jawab["terbaca"]] + list(jawab["terbaca_tanpa_kotak"]) + list(jawab["luar_indonesia"]) + list(
        jawab["dikeluarkan"])
    if len(set(disebut)) != len(disebut) or set(disebut) - set(kartu):
        raise LabelDitolak("jawaban lembar tanpa plat menyebut kartu dua kali atau kartu yang tidak ada")

    info = {k["video"]: {"kelompok": k["kategori"], "sisi": k["sisi"]} for k in tiba.values()}
    info.update({b["gambar"]: {"kelompok": b["kelompok"], "sisi": b["sisi"]} for b in kartu.values()})
    dikeluarkan = {kartu[n]["gambar"]: "luar_indonesia" for n in jawab["luar_indonesia"]}
    dikeluarkan.update({kartu[n]["gambar"]: "owner" for n in jawab["dikeluarkan"]})

    tetap, butir = {}, []
    for n in sorted([int(x) for x in jawab["terbaca"]] + list(jawab["terbaca_tanpa_kotak"])):
        b = kartu[n]
        v = jawab["terbaca"].get(str(n))
        kendaraan = None
        if v is not None:
            if not 1 <= v <= len(b["bernomor"]):
                raise LabelDitolak(f"kartu {n}: kendaraan {v} tidak ada")
            kendaraan = [float(x) for x in b["bernomor"][v - 1][:4]]
        butir.append({"id": f"t{n}", "jenis": "terlewat", "gambar": b["gambar"], "kendaraan": kendaraan})
    for b in sorted(baris_plat, key=lambda x: x["nomor"]):
        k = tiba[(b["video"], b["kedatangan"])]
        if b["nomor"] in bukan_plat:
            jenis = "bukan_plat"
        elif b["nomor"] in tak_terbaca:
            jenis = "tak_terbaca"
        elif b["nomor"] in salah or not k["teks"]:  # baris "-" yang tidak disebut dihitung salah, seperti lembar_rantai.nilai
            jenis = "salah"
        else:
            jenis = "benar"
        tetap.setdefault(b["video"], []).append({"baris": b["nomor"], "jenis": jenis, "kotak": _kotak(k["kotak"]),
                                                  "teks": k["teks"] if jenis == "benar" else None})
        if jenis == "salah":
            butir.append({"id": f"s{b['nomor']}", "jenis": "salah", "gambar": b["video"], "kotak": _kotak(k["kotak"]),
                          "bacaan": k["teks"] or "-"})

    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    salinan = {}
    for b in butir:
        g = b["gambar"]
        if g not in salinan:
            asal = Path(folder_capture) / peta[g]
            gambar = cv2.imread(str(asal))
            if gambar is None:
                raise LabelDitolak("ada gambar yang tak bisa dibuka")
            tujuan = keluar / "gambar" / f"{g}{asal.suffix.lower()}"
            shutil.copyfile(asal, tujuan)
            salinan[g] = (f"gambar/{tujuan.name}", int(gambar.shape[1]), int(gambar.shape[0]))
        b["berkas"], b["lebar"], b["tinggi"] = salinan[g]
        b.update(info[g])
    (keluar / "butir.json").write_text(json.dumps({"butir": butir, "tetap": tetap, "info": info, "dikeluarkan": dikeluarkan},
                                                  indent=1))
    tanda = hashlib.sha256(json.dumps([b["id"] for b in butir]).encode()).hexdigest()[:12]
    halaman = HALAMAN.replace("__TANDA__", tanda).replace("__BUTIR__", json.dumps(butir).replace("<", "\\u003c"))
    (keluar / "halaman.html").write_text(halaman, encoding="utf-8")
    return {"butir": len(butir), "terlewat": sum(b["jenis"] == "terlewat" for b in butir),
            "salah": sum(b["jenis"] == "salah" for b in butir), "dikeluarkan": len(dikeluarkan)}


def terima(butir_json, simpanan, keluar):
    """Kembali: hitungan saja."""
    isi = json.loads(Path(butir_json).read_text())
    jawab = json.loads(Path(simpanan).read_text())["butir"]
    butir = {b["id"]: b for b in isi["butir"]}
    if set(jawab) - set(butir):
        raise LabelDitolak("simpanan memuat nomor butir yang tidak ada di halaman")
    hitung = {"butir_terisi": 0, "butir_kosong": 0, "teks_tak_sesuai_pola": 0}

    def kotak_sah(b, k):
        k = _kotak(k)
        if len(k) != 4 or not (0 <= k[0] < k[2] <= b["lebar"] and 0 <= k[1] < k[3] <= b["tinggi"]) or min(
                k[2] - k[0], k[3] - k[1]) < MIN_SISI:
            raise LabelDitolak(f"kotak butir {b['id']} tidak sah")
        return k

    def teks_sah(t):
        t = bersihkan(t or "")
        if not t:
            return None
        plat = urai(t)
        if plat is None:
            hitung["teks_tak_sesuai_pola"] += 1
            return None
        return plat.teks

    def jawaban(b):
        """(kotak atau None, teks atau None, tak_terbaca, terisi)."""
        j = jawab.get(b["id"]) or {}
        tak = bool(j.get("tak_terbaca"))
        kotak = kotak_sah(b, j["kotak"]) if j.get("kotak") else None
        teks = None if tak else teks_sah(j.get("teks"))
        terisi = bool(kotak or tak or bersihkan(j.get("teks") or ""))
        hitung["butir_terisi" if terisi else "butir_kosong"] += 1
        return kotak, teks, tak, terisi

    dikeluarkan = isi["dikeluarkan"]
    gambar = {g: {**v, "plat": [], "bukan_plat": [], "plat_tanpa_label": 0} for g, v in sorted(isi["info"].items())
              if g not in dikeluarkan}
    for g, daftar in isi["tetap"].items():
        if g in dikeluarkan:
            continue
        for t in daftar:
            if t["jenis"] == "bukan_plat":
                gambar[g]["bukan_plat"].append(t["kotak"])
            elif t["jenis"] == "salah":
                kotak, teks, tak, terisi = jawaban(butir[f"s{t['baris']}"])
                gambar[g]["plat"].append({"kotak": kotak or t["kotak"], "teks": teks, "tak_terbaca": tak,
                                          "asal": "halaman" if terisi else "lembar"})
            else:
                gambar[g]["plat"].append({"kotak": t["kotak"], "teks": t["teks"], "tak_terbaca": t["jenis"] == "tak_terbaca",
                                          "asal": "lembar"})
    for b in isi["butir"]:
        if b["jenis"] != "terlewat" or b["gambar"] in dikeluarkan:
            continue
        kotak, teks, tak, _ = jawaban(b)
        if kotak:
            gambar[b["gambar"]]["plat"].append({"kotak": kotak, "teks": teks, "tak_terbaca": tak, "asal": "halaman"})
        else:
            gambar[b["gambar"]]["plat_tanpa_label"] += 1

    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "label.json").write_text(json.dumps({"gambar": gambar, "dikeluarkan": dikeluarkan}, indent=1))
    per_sisi = {}
    for v in gambar.values():
        r = per_sisi.setdefault(v["sisi"], {"gambar": 0, "plat_kotak": 0, "plat_teks": 0, "tak_terbaca": 0, "plat_tanpa_label": 0,
                                            "bukan_plat": 0})
        r["gambar"] += 1
        r["plat_kotak"] += len(v["plat"])
        r["plat_teks"] += sum(p["teks"] is not None for p in v["plat"])
        r["tak_terbaca"] += sum(p["tak_terbaca"] for p in v["plat"])
        r["plat_tanpa_label"] += v["plat_tanpa_label"]
        r["bukan_plat"] += len(v["bukan_plat"])
    ringkas = {**hitung, "dikeluarkan": len(dikeluarkan), "per_sisi": dict(sorted(per_sisi.items()))}
    (keluar / "ringkasan-label.json").write_text(json.dumps(ringkas, indent=1))
    return ringkas


def cocokkan(plat, baris, iou_min=IOU_RANTAI):
    """Aturan cocok nilai_label (juga dipakai bahan_pembaca, Rencana 30): plat berlabel, berurutan seperti di label.json termasuk
    yang tanpa teks, masing-masing mendapat baris rantai ber-IoU tertinggi yang belum dipakai plat lain, bila IoU-nya minimal
    iou_min. Kembali: daftar indeks baris (None = tidak ditemukan), sejajar dengan plat."""
    from deteksi import iou

    pakai, hasil = set(), []
    for p in plat:
        calon = max(((iou(p["kotak"], b["kotak"]), i) for i, b in enumerate(baris) if i not in pakai), default=(0.0, None))
        if calon[1] is None or calon[0] < iou_min:
            hasil.append(None)
            continue
        pakai.add(calon[1])
        hasil.append(calon[1])
    return hasil


def baris_rantai(folder_baru):
    """Keluaran baca_gambar.py -> ({jalur berkas: nomor gambar rantai}, {nomor gambar rantai: [baris kedatangan]})."""
    folder_baru = Path(folder_baru)
    nomor_baru = {jalur: g for g, jalur in json.loads((folder_baru / "peta-berkas.json").read_text()).items()}
    tiba = {}
    for b in (folder_baru / "kedatangan.jsonl").read_text().splitlines():
        if b.strip():
            k = json.loads(b)
            tiba.setdefault(k["video"], []).append(k)
    return nomor_baru, tiba


def nilai_label(label_json, peta_label, folder_baru, sisi="uji", iou_min=IOU_RANTAI):
    """Penilai otomatis rantai di tangkapan (Rencana 24 Task 11): keluaran baca_gambar.py (folder_baru: kedatangan.jsonl dan
    peta-berkas.json) terhadap label.json. Gambar dicocokkan lewat jalur berkas di kedua peta, bukan lewat nomor gambar, karena
    nomor bergeser bila gambar ditambah. Plat berlabel "ditemukan" bila satu kotak, yang belum dipakai plat lain, ber-IoU minimal
    iou_min; "dibaca benar" bila platnya berteks dan bacaan kotak itu sama. Kotak yang tidak cocok dengan plat berlabel dihitung
    "di luar label" (bisa bukan plat, bisa plat yang tidak pernah dilabeli). Kembali: hitungan saja."""
    from deteksi import iou

    label = json.loads(Path(label_json).read_text())["gambar"]
    jalur_label = json.loads(Path(peta_label).read_text())
    nomor_baru, tiba = baris_rantai(folder_baru)
    per, gambar = {}, 0
    for g, v in sorted(label.items()):
        if v["sisi"] != sisi:
            continue
        gambar += 1
        r = per.setdefault(v["kelompok"], {"plat_berlabel": 0, "ditemukan": 0, "berteks": 0, "dibaca_benar": 0,
                                           "kotak_di_luar_label": 0, "kotak_di_bukan_plat": 0})
        baris = tiba.get(nomor_baru.get(jalur_label[g]), [])
        cocok = cocokkan(v["plat"], baris, iou_min)
        pakai = {i for i in cocok if i is not None}
        for p, i in zip(v["plat"], cocok):
            r["plat_berlabel"] += 1
            r["berteks"] += int(p["teks"] is not None)
            if i is None:
                continue
            r["ditemukan"] += 1
            r["dibaca_benar"] += int(p["teks"] is not None and baris[i]["teks"] == p["teks"])
        for i, b in enumerate(baris):
            if i not in pakai:
                r["kotak_di_luar_label"] += 1
                r["kotak_di_bukan_plat"] += int(any(iou(b["kotak"], x) >= iou_min for x in v["bukan_plat"]))
    return {"sisi": sisi, "iou_min": iou_min, "gambar": gambar, "per_kelompok": dict(sorted(per.items()))}


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Halaman pelabelan tangkapan owner (Rencana 24 Task 4).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("buat")
    for nama in ("folder_capture", "folder_baca", "lembar_plat", "lembar_tanpa", "jawaban_tanpa", "keluar"):
        a.add_argument(nama)
    for nama in ("salah", "tak-terbaca", "bukan-plat"):
        a.add_argument(f"--{nama}", type=nomor_baris, default=[])
    b = perintah.add_parser("terima")
    for nama in ("butir_json", "simpanan", "keluar"):
        b.add_argument(nama)
    n = perintah.add_parser("nilai")
    for nama in ("label_json", "peta_label", "folder_baru", "keluar_json"):
        n.add_argument(nama)
    n.add_argument("--sisi", choices=("uji", "latih"), default="uji")
    p = pengurai.parse_args(argumen)
    if p.perintah == "nilai":
        try:
            r = nilai_label(p.label_json, p.peta_label, p.folder_baru, p.sisi)
        except (OSError, ValueError, KeyError) as galat:
            print(f"GAGAL: {type(galat).__name__}")
            return 1
        Path(p.keluar_json).write_text(json.dumps(r, indent=1))
        print(f"{r['gambar']} gambar sisi {r['sisi']} (IoU {r['iou_min']}): {json.dumps(r['per_kelompok'])}")
        return 0
    try:
        if p.perintah == "buat":
            r = buat(p.folder_capture, p.folder_baca, p.lembar_plat, p.lembar_tanpa, p.jawaban_tanpa, p.keluar, p.salah,
                     p.tak_terbaca, p.bukan_plat)
            print(f"{r['butir']} butir ({r['terlewat']} plat terlewat, {r['salah']} bacaan salah); {r['dikeluarkan']} gambar "
                  "dikeluarkan. Halaman memuat plat: hanya owner yang membukanya.")
        else:
            r = terima(p.butir_json, p.simpanan, p.keluar)
            print(f"butir terisi {r['butir_terisi']}, kosong {r['butir_kosong']}, teks di luar pola {r['teks_tak_sesuai_pola']}; "
                  f"dikeluarkan {r['dikeluarkan']}; per sisi {json.dumps(r['per_sisi'])}")
    except LabelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 2
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


HALAMAN = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Label Tangkapan</title>
<style>
  :root { --latar: #f4f5f7; --kartu: #ffffff; --teks: #1b1f24; --redup: #5b6470; --garis: #d5d9de; --utama: #1f6feb;
          --bahaya: #c62828; --baik: #1e7e34; }
  @media (prefers-color-scheme: dark) {
    :root { --latar: #15181c; --kartu: #1f2328; --teks: #e6e8eb; --redup: #9aa4b0; --garis: #3a4048; --utama: #4c8dff;
            --bahaya: #ff6b6b; --baik: #4cc36b; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; font: 16px/1.45 system-ui, sans-serif; background: var(--latar); color: var(--teks); }
  header { padding: 12px 16px; background: var(--kartu); border-bottom: 1px solid var(--garis); display: flex; flex-wrap: wrap;
           gap: 8px 16px; align-items: center; }
  h1 { font-size: 18px; margin: 0; }
  main { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; padding: 16px; }
  @media (max-width: 900px) { main { grid-template-columns: 1fr; } }
  .panggung { background: var(--kartu); border: 1px solid var(--garis); border-radius: 8px; overflow: auto; align-self: start;
              max-height: calc(100vh - 120px); }
  #kanvas { display: block; cursor: crosshair; touch-action: none; }
  aside { background: var(--kartu); border: 1px solid var(--garis); border-radius: 8px; padding: 14px; display: flex;
          flex-direction: column; gap: 12px; align-self: start; }
  .petunjuk { color: var(--redup); font-size: 14px; }
  #pratinjau { width: 100%; height: 110px; background: #000; border-radius: 6px; }
  #teks { width: 100%; font: 600 26px/1.2 ui-monospace, monospace; letter-spacing: 2px; padding: 8px 10px;
          border: 2px solid var(--garis); border-radius: 6px; background: var(--latar); color: var(--teks); text-transform: uppercase; }
  .peringatan { color: var(--bahaya); font-size: 14px; min-height: 20px; }
  .baris { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  button, select { font: inherit; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--garis); background: var(--latar);
                   color: var(--teks); cursor: pointer; }
  button.utama { background: var(--utama); border-color: var(--utama); color: #fff; }
  .kemajuan { font-weight: 600; }
</style>
</head>
<body>
<header>
  <h1>Label tangkapan CCTV</h1>
  <span class="kemajuan" id="kemajuan"></span>
  <div class="baris"><span>Perbesar:</span><button data-skala="pas">Pas</button>
    <button data-skala="1">1&times;</button><button data-skala="2">2&times;</button><button data-skala="3">3&times;</button></div>
  <button class="utama" id="simpan">Simpan berkas</button>
</header>
<main>
  <div class="panggung" id="panggung"><canvas id="kanvas"></canvas></div>
  <aside>
    <div><strong id="judul"></strong><div class="petunjuk" id="petunjuk"></div></div>
    <canvas id="pratinjau" width="320" height="110"></canvas>
    <label for="teks">Nomor plat (tanpa spasi)</label>
    <input id="teks" type="text" autocomplete="off" spellcheck="false">
    <div class="peringatan" id="peringatan"></div>
    <label class="baris"><input type="checkbox" id="tak-terbaca"> Plat tidak bisa dibaca</label>
    <div class="baris"><button id="sebelum">&lsaquo; Sebelumnya</button><button class="utama" id="berikut">Berikutnya &rsaquo;</button></div>
    <label for="lompat">Lompat ke butir</label>
    <select id="lompat"></select>
    <div class="petunjuk">Kemajuan tersimpan otomatis di peramban ini, jadi boleh dicicil. Sesudah selesai, tekan
      <b>Simpan berkas</b>, lalu beri tahu agen letak berkas <code>label-tangkapan.json</code> yang terunduh.
      Jangan menulis nomor plat di percakapan.</div>
  </aside>
</main>
<script>
const BUTIR = __BUTIR__;
const KUNCI = "cctvgerbang-label-tangkapan-__TANDA__";
const POLA = /^[A-Z]{1,2}[1-9][0-9]{0,3}[A-Z]{0,3}$/;
let jawab = {};
try { jawab = JSON.parse(localStorage.getItem(KUNCI) || "{}") || {}; } catch (e) { jawab = {}; }
let i = 0, mode = "pas", skala = 1, tarik = null;
const gambar = new Image();
const el = (id) => document.getElementById(id);
const kanvas = el("kanvas"), ctx = kanvas.getContext("2d"), prat = el("pratinjau"), pctx = prat.getContext("2d");

function simpanLokal() {
  try { localStorage.setItem(KUNCI, JSON.stringify(jawab)); } catch (e) { /* ditolak peramban: kemajuan hanya selama halaman terbuka */ }
}
function rapikan(t) { return String(t || "").toUpperCase().replace(/[^A-Z0-9]/g, ""); }
function jwb() {
  const id = BUTIR[i].id;
  if (!jawab[id]) jawab[id] = { kotak: null, teks: "", tak_terbaca: false };
  return jawab[id];
}
function kotakTampil() {
  const b = BUTIR[i], a = jawab[b.id];
  if (a && a.kotak) return a.kotak;
  return b.jenis === "salah" ? b.kotak : null;
}
function selesai(b) {
  const a = jawab[b.id];
  if (!a) return false;
  const isi = a.tak_terbaca || POLA.test(rapikan(a.teks));
  return b.jenis === "salah" ? isi : Boolean(a.kotak) && isi;
}
function kotakDari(t) {
  const b = BUTIR[i];
  const x1 = Math.max(0, Math.min(t.x0, t.x1)), y1 = Math.max(0, Math.min(t.y0, t.y1));
  const x2 = Math.min(b.lebar, Math.max(t.x0, t.x1)), y2 = Math.min(b.tinggi, Math.max(t.y0, t.y1));
  return [Math.round(x1), Math.round(y1), Math.round(x2), Math.round(y2)];
}
function garis(k, warna) {
  ctx.strokeStyle = warna; ctx.lineWidth = 2;
  ctx.strokeRect(k[0] * skala, k[1] * skala, (k[2] - k[0]) * skala, (k[3] - k[1]) * skala);
}
function gambarUlang() {
  const b = BUTIR[i];
  skala = mode === "pas" ? Math.min(1, (el("panggung").clientWidth - 4) / b.lebar) : Number(mode);
  kanvas.width = Math.round(b.lebar * skala); kanvas.height = Math.round(b.tinggi * skala);
  ctx.imageSmoothingEnabled = skala <= 1;
  if (gambar.naturalWidth) ctx.drawImage(gambar, 0, 0, kanvas.width, kanvas.height);
  if (b.kendaraan) garis(b.kendaraan, "#1e64ff");
  const k = tarik ? kotakDari(tarik) : kotakTampil();
  if (k) garis(k, "#ff2020");
  pctx.fillStyle = "#000"; pctx.fillRect(0, 0, prat.width, prat.height);
  if (k && k[2] - k[0] >= 2 && k[3] - k[1] >= 2 && gambar.naturalWidth) {
    const w = k[2] - k[0], h = k[3] - k[1], s = Math.min(prat.width / w, prat.height / h);
    pctx.imageSmoothingEnabled = false;
    pctx.drawImage(gambar, k[0], k[1], w, h, (prat.width - w * s) / 2, (prat.height - h * s) / 2, w * s, h * s);
  }
}
function periksaTeks() {
  const t = rapikan(el("teks").value);
  el("peringatan").textContent = t && !POLA.test(t)
    ? "Pola plat tidak biasa (1-2 huruf, angka, 0-3 huruf). Periksa lagi, atau biarkan bila memang begitu." : "";
}
function perbaruiKemajuan() {
  el("kemajuan").textContent = BUTIR.filter(selesai).length + " dari " + BUTIR.length + " selesai";
  const pilih = el("lompat");
  pilih.innerHTML = "";
  BUTIR.forEach((b, k) => {
    const o = document.createElement("option");
    o.value = k;
    o.textContent = (k + 1) + ". " + (b.jenis === "salah" ? "bacaan salah" : "plat terlewat") + (selesai(b) ? " \\u2713" : "");
    o.selected = k === i;
    pilih.appendChild(o);
  });
}
function tampil() {
  const b = BUTIR[i], a = jwb();
  el("judul").textContent = "Butir " + (i + 1) + " dari " + BUTIR.length + " \\u00b7 "
    + (b.jenis === "salah" ? "bacaan salah" : "plat terlewat") + " \\u00b7 " + b.kelompok;
  el("petunjuk").textContent = b.jenis === "salah"
    ? "Bacaan mesin (salah): " + b.bacaan + ". Ketik nomor plat yang benar. Kotak merah adalah plat yang ditemukan mesin; tarik ulang bila kurang pas."
    : (b.kendaraan ? "Tarik kotak tepat di sekeliling plat kendaraan berkotak biru, lalu ketik nomornya."
                   : "Kendaraannya tidak ditemukan mesin. Tarik kotak tepat di sekeliling plat kendaraan terdekat, lalu ketik nomornya.");
  el("teks").value = a.teks || "";
  el("tak-terbaca").checked = Boolean(a.tak_terbaca);
  periksaTeks();
  perbaruiKemajuan();
  gambar.onload = gambarUlang;
  gambar.src = b.berkas;
  gambarUlang();
  el("teks").focus();
}
function ke(k) { if (k >= 0 && k < BUTIR.length) { i = k; tarik = null; tampil(); } }
function titik(e) {
  const r = kanvas.getBoundingClientRect(), b = BUTIR[i];
  return { x: (e.clientX - r.left) * b.lebar / r.width, y: (e.clientY - r.top) * b.tinggi / r.height };
}
kanvas.addEventListener("pointerdown", (e) => {
  const p = titik(e);
  tarik = { x0: p.x, y0: p.y, x1: p.x, y1: p.y };
  try { kanvas.setPointerCapture(e.pointerId); } catch (err) { /* tanpa tangkapan pointer, tarikan tetap jalan di atas kanvas */ }
  gambarUlang();
});
kanvas.addEventListener("pointermove", (e) => {
  if (!tarik) return;
  const p = titik(e);
  tarik.x1 = p.x; tarik.y1 = p.y;
  gambarUlang();
});
kanvas.addEventListener("pointerup", () => {
  if (!tarik) return;
  const k = kotakDari(tarik);
  tarik = null;
  if (k[2] - k[0] >= 4 && k[3] - k[1] >= 4) { jwb().kotak = k; simpanLokal(); perbaruiKemajuan(); }
  gambarUlang();
  el("teks").focus();
});
el("teks").addEventListener("input", () => {
  const t = rapikan(el("teks").value);
  if (el("teks").value !== t) el("teks").value = t;
  jwb().teks = t; periksaTeks(); simpanLokal(); perbaruiKemajuan();
});
el("teks").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); ke(i + 1); } });
el("tak-terbaca").addEventListener("change", (e) => { jwb().tak_terbaca = e.target.checked; simpanLokal(); perbaruiKemajuan(); });
el("sebelum").addEventListener("click", () => ke(i - 1));
el("berikut").addEventListener("click", () => ke(i + 1));
el("lompat").addEventListener("change", (e) => ke(Number(e.target.value)));
document.querySelectorAll("[data-skala]").forEach((t) => t.addEventListener("click", () => { mode = t.dataset.skala; gambarUlang(); }));
window.addEventListener("resize", () => { if (mode === "pas") gambarUlang(); });
el("simpan").addEventListener("click", () => {
  const isi = JSON.stringify({ versi: 1, tanda: "__TANDA__", dibuat: new Date().toISOString(), butir: jawab }, null, 1);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([isi], { type: "application/json" }));
  a.download = "label-tangkapan.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
});
const pertama = BUTIR.findIndex((b) => !selesai(b));
ke(pertama < 0 ? 0 : pertama);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(utama())
