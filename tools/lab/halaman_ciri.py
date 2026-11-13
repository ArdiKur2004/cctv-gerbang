"""Halaman ciri kendaraan untuk OWNER (Rencana 31, spec Fase 3 tahap 1 bagian 3, K61): jenis, warna, dan merek kendaraan berplat
berlabel di tangkapan owner, tanpa agen melihat gambar.

- buat: untuk tiap gambar di label.json, pencari kendaraan dijalankan (sekarang YOLOX COCO, mesin belajar, hanya untuk usulan). Tiap
  plat berlabel (berteks atau tidak) dipasangkan dengan kendaraan terkecil yang memuat tengah platnya (kendaraan.kendaraan_pemuat). Satu
  kartu per kendaraan; dua plat di kendaraan yang sama menjadi satu kartu. Plat tanpa kendaraan mendapat kotak perkiraan di sekitar
  platnya. Usulan jenis dari kelas pencari; warna dan merek dipilih owner. Keluaran: halaman.html, gambar/ (salinan bernama nomor,
  tanpa nama asli), butir.json. Halaman tidak memuat apa pun dari luar.
- terima: jawaban owner (label-ciri.json dari halaman) harus bertanda halaman yang sama (tanda_halaman), lalu diperiksa terhadap
  KELAS. Nilai di luar daftar, merek motor untuk mobil (dan
  sebaliknya), dan butir yang tidak ada ditolak sebelum apa pun ditulis. Kartu lengkap bila jenis, warna, dan merek terisi, atau bila
  jenisnya "bukan_kendaraan". Keluaran: ciri.json (per kendaraan) dan ringkasan-ciri.json (hitungan saja).

Gambar, halaman, butir.json, dan ciri.json memuat kendaraan dan plat: agen tidak membukanya (CLAUDE.md §4, §7). Layar hanya hitungan.

  buat:   powershell -NoProfile -File tools\\lab.ps1 -Fpo python /kerja/tools/lab/halaman_ciri.py buat /kerja/data/capture /kerja/data/keluaran/tangkapan-owner-baca/peta-berkas.json /kerja/data/keluaran/label-tangkapan/label.json /kerja/data/keluaran/kendaraan-yolox-coco /kerja/data/keluaran/halaman-ciri
  terima: powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/halaman_ciri.py terima /kerja/data/keluaran/halaman-ciri/butir.json <label-ciri.json> /kerja/data/keluaran/label-ciri
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
from kendaraan import PencariKendaraan, kendaraan_pemuat  # noqa: E402

BUKAN_KENDARAAN = "bukan_kendaraan"
TAK_YAKIN = "tak_yakin"
# Spec Fase 3 tahap 1 bagian 1, disetujui owner tanpa perubahan (K61). Halaman dan terima memakai daftar yang sama.
KELAS = {
    "jenis": ["mobil", "pikap", "truk", "bus", "motor"],
    "warna": ["putih", "hitam", "abu_perak", "merah", "biru", "kuning", "hijau", "coklat_krem", "lainnya"],
    "merek_mobil": ["Toyota", "Daihatsu", "Honda", "Mitsubishi", "Suzuki", "Wuling", "Hyundai", "Nissan", "Mazda", "Isuzu", "lainnya"],
    "merek_motor": ["Honda", "Yamaha", "Suzuki", "Kawasaki", "lainnya"],
}
# Kotak perkiraan untuk plat yang kendaraannya tidak ditemukan: kali lebar dan tinggi plat, dari tengah plat ke kiri-kanan, dari atas
# plat ke atas, dan dari bawah plat ke bawah. Hanya untuk tampilan owner; owner menandai bila tidak pas.
PERKIRAAN = {"samping": 2.5, "atas": 6.0, "bawah": 1.5}


class LabelDitolak(ValueError):
    """Pesannya aman dicetak: hanya nomor kartu dan nama isian, tanpa plat atau nama berkas."""


def kotak_perkiraan(plat, lebar, tinggi):
    x1, y1, x2, y2 = plat[:4]
    w, h, cx = x2 - x1, y2 - y1, (x1 + x2) / 2
    return [int(max(0, round(cx - PERKIRAAN["samping"] * w))), int(max(0, round(y1 - PERKIRAAN["atas"] * h))),
            int(min(lebar, round(cx + PERKIRAAN["samping"] * w))), int(min(tinggi, round(y2 + PERKIRAAN["bawah"] * h)))]


def kartu_kendaraan(plat, kendaraan, lebar, tinggi):
    """Plat berlabel satu gambar (urutan label.json) dan kendaraan [(x1, y1, x2, y2, yakin, jenis)] -> kartu, berurutan menurut plat
    pertamanya: {"plat": [nomor plat, mulai 1], "kotak", "perkiraan", "usulan_jenis"}."""
    kartu, per_kendaraan = [], {}
    for n, p in enumerate(plat, 1):
        v = kendaraan_pemuat(p["kotak"], kendaraan)
        if v is None:
            kartu.append({"plat": [n], "kotak": kotak_perkiraan(p["kotak"], lebar, tinggi), "perkiraan": True, "usulan_jenis": None})
            continue
        i = kendaraan.index(v)
        if i in per_kendaraan:
            per_kendaraan[i]["plat"].append(n)
            continue
        k = {"plat": [n], "kotak": [int(round(float(x))) for x in v[:4]], "perkiraan": False,
             "usulan_jenis": v[5] if v[5] in KELAS["jenis"] else None}
        per_kendaraan[i] = k
        kartu.append(k)
    return kartu


def tanda_halaman(butir):
    """Tanda satu halaman: dari nomor kartu, gambar, dan plat tiap kartu. Ikut di kunci penyimpanan peramban dan di berkas jawaban, dan
    diperiksa terima, supaya jawaban dari halaman lain (atau halaman lama) tidak diterima diam-diam."""
    return hashlib.sha256(json.dumps([(b["id"], b["gambar"], b["plat"]) for b in butir]).encode()).hexdigest()[:12]


def buat(folder_capture, peta_label, label_json, cari_kendaraan, keluar):
    """Kembali: hitungan saja."""
    keluar = Path(keluar)
    (keluar / "gambar").mkdir(parents=True, exist_ok=True)
    peta = json.loads(Path(peta_label).read_text())
    label = json.loads(Path(label_json).read_text())["gambar"]
    butir, usulan, perkiraan, gambar_berkartu = [], {}, 0, 0
    for g in sorted(label):
        v = label[g]
        if not v["plat"]:
            continue
        asal = Path(folder_capture) / peta[g]
        gambar = cv2.imread(str(asal))
        if gambar is None:
            raise LabelDitolak("ada gambar yang tak bisa dibuka")
        tinggi, lebar = gambar.shape[:2]
        berkas = f"gambar/{g}{asal.suffix.lower()}"
        shutil.copyfile(asal, keluar / berkas)
        gambar_berkartu += 1
        for k in kartu_kendaraan(v["plat"], list(cari_kendaraan(gambar)), lebar, tinggi):
            butir.append({"id": f"k{len(butir) + 1}", "gambar": g, "sisi": v["sisi"], "kelompok": v["kelompok"], **k,
                          "kotak_plat": [[int(round(float(x))) for x in v["plat"][n - 1]["kotak"][:4]] for n in k["plat"]],
                          "berkas": berkas, "lebar": int(lebar), "tinggi": int(tinggi)})
            perkiraan += int(k["perkiraan"])
            if k["usulan_jenis"]:
                usulan[k["usulan_jenis"]] = usulan.get(k["usulan_jenis"], 0) + 1
    (keluar / "butir.json").write_text(json.dumps({"butir": butir, "kelas": KELAS}, indent=1))
    halaman = (HALAMAN.replace("__TANDA__", tanda_halaman(butir)).replace("__KELAS__", json.dumps(KELAS))
               .replace("__BUTIR__", json.dumps(butir).replace("<", "\\u003c")))
    (keluar / "halaman.html").write_text(halaman, encoding="utf-8")
    return {"kartu": len(butir), "perkiraan": perkiraan, "usulan": dict(sorted(usulan.items())), "gambar": gambar_berkartu}


def _periksa(b, j):
    """(jenis, warna, merek, lengkap) dari jawaban satu kartu; nilai yang terisi di luar daftar menolak seluruh berkas."""
    jenis, warna, merek = (str(j.get(k) or "") for k in ("jenis", "warna", "merek"))
    if jenis and jenis not in KELAS["jenis"] + [BUKAN_KENDARAAN]:
        raise LabelDitolak(f"kartu {b['id']}: jenis di luar daftar")
    if jenis == BUKAN_KENDARAAN:
        return jenis, None, None, True
    if warna and warna not in KELAS["warna"] + [TAK_YAKIN]:
        raise LabelDitolak(f"kartu {b['id']}: warna di luar daftar")
    daftar_merek = KELAS["merek_motor"] if jenis == "motor" else KELAS["merek_mobil"]
    if merek and (not jenis or merek not in daftar_merek + [TAK_YAKIN]):
        raise LabelDitolak(f"kartu {b['id']}: merek di luar daftar untuk jenis itu")
    lengkap = bool(jenis and warna and merek)
    return (jenis or None), (warna or None), (merek or None), lengkap


def terima(butir_json, simpanan, keluar):
    """Kembali: hitungan saja."""
    butir = json.loads(Path(butir_json).read_text())["butir"]
    isi = json.loads(Path(simpanan).read_text())
    if isi.get("tanda") != tanda_halaman(butir):
        raise LabelDitolak("berkas jawaban bukan dari halaman ini (tanda berbeda)")
    jawab = isi["butir"]
    ada = {b["id"] for b in butir}
    if set(jawab) - ada:
        raise LabelDitolak("simpanan memuat nomor kartu yang tidak ada di halaman")
    hasil, hitung = [], {"kartu": len(butir), "lengkap": 0, "kosong": 0, "bukan_kendaraan": 0, "kotak_tidak_pas": 0,
                         "usulan_jenis_sama": {"sama": 0, "berbeda": 0}, "per_sisi": {}}
    for b in butir:
        j = jawab.get(b["id"]) or {}
        jenis, warna, merek, lengkap = _periksa(b, j)
        tidak_pas = bool(j.get("kotak_tidak_pas"))
        hasil.append({k: b[k] for k in ("id", "gambar", "sisi", "kelompok", "kotak", "perkiraan", "plat", "usulan_jenis")}
                     | {"jenis": jenis, "warna": warna, "merek": merek, "kotak_tidak_pas": tidak_pas, "lengkap": lengkap})
        s = hitung["per_sisi"].setdefault(b["sisi"], {"kartu": 0, "lengkap": 0, "jenis": {}, "warna": {}, "merek": {}})
        s["kartu"] += 1
        hitung["kotak_tidak_pas"] += int(tidak_pas)
        if not lengkap:
            hitung["kosong"] += 1
            continue
        hitung["lengkap"] += 1
        s["lengkap"] += 1
        if jenis == BUKAN_KENDARAAN:
            hitung["bukan_kendaraan"] += 1
            continue
        for nama, nilai in (("jenis", jenis), ("warna", warna), ("merek", merek)):
            s[nama][nilai] = s[nama].get(nilai, 0) + 1
        if b["usulan_jenis"]:
            hitung["usulan_jenis_sama"]["sama" if jenis == b["usulan_jenis"] else "berbeda"] += 1
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "ciri.json").write_text(json.dumps({"kelas": KELAS, "kendaraan": hasil}, indent=1))
    hitung["per_sisi"] = {k: {**v, **{n: dict(sorted(v[n].items())) for n in ("jenis", "warna", "merek")}}
                          for k, v in sorted(hitung["per_sisi"].items())}
    (keluar / "ringkasan-ciri.json").write_text(json.dumps(hitung, indent=1))
    return hitung


def utama(argumen=None):
    pengurai = argparse.ArgumentParser(description="Halaman ciri kendaraan untuk owner (Rencana 31).")
    perintah = pengurai.add_subparsers(dest="perintah", required=True)
    a = perintah.add_parser("buat")
    for nama in ("folder_capture", "peta_label", "label_json", "folder_kendaraan", "keluar"):
        a.add_argument(nama)
    a.add_argument("--utas", type=int, default=2)
    b = perintah.add_parser("terima")
    for nama in ("butir_json", "simpanan", "keluar"):
        b.add_argument(nama)
    p = pengurai.parse_args(argumen)
    try:
        if p.perintah == "buat":
            r = buat(p.folder_capture, p.peta_label, p.label_json, PencariKendaraan(p.folder_kendaraan, utas=p.utas), p.keluar)
            print(f"{r['kartu']} kartu dari {r['gambar']} gambar; {r['perkiraan']} kotak perkiraan; usulan jenis {r['usulan']}. "
                  "Halaman memuat kendaraan dan plat: hanya owner yang membukanya.")
        else:
            r = terima(p.butir_json, p.simpanan, p.keluar)
            print(f"{r['kartu']} kartu: {r['lengkap']} lengkap, {r['kosong']} kosong, {r['bukan_kendaraan']} bukan kendaraan, "
                  f"{r['kotak_tidak_pas']} kotak tidak pas; usulan jenis {r['usulan_jenis_sama']}")
    except LabelDitolak as galat:
        print(f"DITOLAK: {galat}")
        return 1
    except (OSError, ValueError, KeyError) as galat:
        print(f"GAGAL: {type(galat).__name__}")
        return 1
    return 0


HALAMAN = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ciri Kendaraan</title>
<link rel="icon" href="data:,">
<style>
  :root { --latar: #f4f5f7; --kartu: #ffffff; --teks: #1b1f24; --redup: #5b6470; --garis: #d5d9de; --utama: #1f6feb;
          --bahaya: #c62828; }
  @media (prefers-color-scheme: dark) {
    :root { --latar: #15181c; --kartu: #1f2328; --teks: #e6e8eb; --redup: #9aa4b0; --garis: #3a4048; --utama: #4c8dff;
            --bahaya: #ff6b6b; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; font: 16px/1.45 system-ui, sans-serif; background: var(--latar); color: var(--teks); }
  header { padding: 12px 16px; background: var(--kartu); border-bottom: 1px solid var(--garis); display: flex; flex-wrap: wrap;
           gap: 8px 16px; align-items: center; }
  h1 { font-size: 18px; margin: 0; }
  main { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 16px; padding: 16px; }
  @media (max-width: 900px) { main { grid-template-columns: 1fr; } }
  .panggung { background: var(--kartu); border: 1px solid var(--garis); border-radius: 8px; overflow: auto; align-self: start;
              max-height: calc(100vh - 120px); }
  #kanvas { display: block; }
  aside { background: var(--kartu); border: 1px solid var(--garis); border-radius: 8px; padding: 14px; display: flex;
          flex-direction: column; gap: 10px; align-self: start; }
  .petunjuk { color: var(--redup); font-size: 14px; }
  #pratinjau { width: 100%; height: 220px; background: #000; border-radius: 6px; }
  label.isian { display: flex; flex-direction: column; gap: 4px; font-weight: 600; }
  .baris { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  label.centang { display: flex; gap: 8px; align-items: flex-start; }
  label.centang input { margin-top: 4px; flex: none; }
  button, select { font: inherit; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--garis); background: var(--latar);
                   color: var(--teks); cursor: pointer; }
  button.utama { background: var(--utama); border-color: var(--utama); color: #fff; }
  .kemajuan { font-weight: 600; }
  .peringatan { color: var(--bahaya); font-size: 14px; min-height: 20px; }
</style>
</head>
<body>
<header>
  <h1>Ciri kendaraan</h1>
  <span class="kemajuan" id="kemajuan"></span>
  <button class="utama" id="simpan">Simpan berkas</button>
</header>
<main>
  <div class="panggung" id="panggung"><canvas id="kanvas"></canvas></div>
  <aside>
    <div><strong id="judul"></strong><div class="petunjuk" id="petunjuk"></div></div>
    <canvas id="pratinjau" width="360" height="220"></canvas>
    <label class="isian">Jenis <select id="jenis"></select></label>
    <label class="isian">Warna badan <select id="warna"></select></label>
    <label class="isian">Merek <select id="merek"></select></label>
    <label class="centang"><input type="checkbox" id="tidak-pas"> <span>Kotak biru tidak pas (memotong kendaraan atau memuat kendaraan
      lain)</span></label>
    <div class="peringatan" id="peringatan"></div>
    <div class="baris"><button id="sebelum">&lsaquo; Sebelumnya</button><button class="utama" id="berikut">Berikutnya &rsaquo;</button></div>
    <label class="isian">Lompat ke kartu <select id="lompat"></select></label>
    <div class="petunjuk">Kemajuan tersimpan otomatis di peramban ini, jadi boleh dicicil. Sesudah selesai, tekan <b>Simpan berkas</b>,
      lalu beri tahu agen letak berkas <code>label-ciri.json</code> yang terunduh. Jangan menulis nomor plat atau ciri kendaraan di
      percakapan.</div>
  </aside>
</main>
<script>
const KELAS = __KELAS__;
const BUTIR = __BUTIR__;
const KUNCI = "cctvgerbang-ciri-__TANDA__";
const NAMA = { abu_perak: "abu-abu atau perak", coklat_krem: "coklat atau krem", tak_yakin: "tak yakin",
               bukan_kendaraan: "bukan kendaraan", lainnya: "lainnya" };
let jawab = {};
try { jawab = JSON.parse(localStorage.getItem(KUNCI) || "{}") || {}; } catch (e) { jawab = {}; }
let i = 0;
const gambar = new Image();
const el = (id) => document.getElementById(id);
const kanvas = el("kanvas"), ctx = kanvas.getContext("2d"), prat = el("pratinjau"), pctx = prat.getContext("2d");

function simpanLokal() {
  try { localStorage.setItem(KUNCI, JSON.stringify(jawab)); } catch (e) { /* ditolak peramban: kemajuan hanya selama halaman terbuka */ }
}
function jwb() {
  const b = BUTIR[i];
  if (!jawab[b.id]) jawab[b.id] = { jenis: b.usulan_jenis || "", warna: "", merek: "", kotak_tidak_pas: false };
  return jawab[b.id];
}
function selesai(b) {
  const a = jawab[b.id];
  return Boolean(a && (a.jenis === "bukan_kendaraan" || (a.jenis && a.warna && a.merek)));
}
function isi(pilih, nilai, terpilih) {
  pilih.innerHTML = "";
  ["", ...nilai].forEach((n) => {
    const o = document.createElement("option");
    o.value = n; o.textContent = n ? (NAMA[n] || n) : "(pilih)"; o.selected = n === terpilih;
    pilih.appendChild(o);
  });
}
function daftarMerek(jenis) { return [...(jenis === "motor" ? KELAS.merek_motor : KELAS.merek_mobil), "tak_yakin"]; }
function gambarUlang() {
  const b = BUTIR[i];
  const s = Math.min(1, (el("panggung").clientWidth - 4) / b.lebar);
  kanvas.width = Math.round(b.lebar * s); kanvas.height = Math.round(b.tinggi * s);
  if (gambar.naturalWidth) ctx.drawImage(gambar, 0, 0, kanvas.width, kanvas.height);
  ctx.lineWidth = 3; ctx.strokeStyle = "#1e64ff";
  const k = b.kotak;
  ctx.strokeRect(k[0] * s, k[1] * s, (k[2] - k[0]) * s, (k[3] - k[1]) * s);
  ctx.lineWidth = 2; ctx.strokeStyle = "#ff2020";
  b.kotak_plat.forEach((p) => ctx.strokeRect(p[0] * s, p[1] * s, (p[2] - p[0]) * s, (p[3] - p[1]) * s));
  pctx.fillStyle = "#000"; pctx.fillRect(0, 0, prat.width, prat.height);
  if (gambar.naturalWidth) {
    const w = k[2] - k[0], h = k[3] - k[1], t = Math.min(prat.width / w, prat.height / h);
    pctx.drawImage(gambar, k[0], k[1], w, h, (prat.width - w * t) / 2, (prat.height - h * t) / 2, w * t, h * t);
  }
}
function perbaruiKemajuan() {
  el("kemajuan").textContent = BUTIR.filter(selesai).length + " dari " + BUTIR.length + " selesai";
  const pilih = el("lompat");
  pilih.innerHTML = "";
  BUTIR.forEach((b, k) => {
    const o = document.createElement("option");
    o.value = k; o.textContent = "Kartu " + (k + 1) + (selesai(b) ? " \\u2713" : ""); o.selected = k === i;
    pilih.appendChild(o);
  });
}
function tampil() {
  const b = BUTIR[i], a = jwb();
  el("judul").textContent = "Kartu " + (i + 1) + " dari " + BUTIR.length;
  el("petunjuk").textContent = b.perkiraan
    ? "Kendaraan tidak ditemukan mesin; kotak biru hanya perkiraan di sekitar plat (kotak merah)."
    : "Kendaraan berkotak biru; kotak merah adalah platnya." + (b.usulan_jenis ? " Jenis diisi usulan mesin; betulkan bila salah." : "");
  isi(el("jenis"), [...KELAS.jenis, "bukan_kendaraan"], a.jenis);
  isi(el("warna"), [...KELAS.warna, "tak_yakin"], a.warna);
  isi(el("merek"), daftarMerek(a.jenis), a.merek);
  const mati = a.jenis === "bukan_kendaraan";
  el("warna").disabled = mati; el("merek").disabled = mati;
  el("tidak-pas").checked = Boolean(a.kotak_tidak_pas);
  el("peringatan").textContent = "";
  perbaruiKemajuan();
  gambar.onload = gambarUlang;
  gambar.src = b.berkas;
  gambarUlang();
}
function ke(k) { if (k >= 0 && k < BUTIR.length) { i = k; tampil(); } }
el("jenis").addEventListener("change", (e) => {
  const a = jwb();
  a.jenis = e.target.value;
  const hapus = Boolean(a.merek && !daftarMerek(a.jenis).includes(a.merek));
  if (hapus) a.merek = "";
  simpanLokal(); tampil();
  if (hapus) el("peringatan").textContent = "Merek dikosongkan karena tidak ada di daftar jenis ini.";  // sesudah tampil(), yang mengosongkan
});
el("warna").addEventListener("change", (e) => { jwb().warna = e.target.value; simpanLokal(); perbaruiKemajuan(); });
el("merek").addEventListener("change", (e) => { jwb().merek = e.target.value; simpanLokal(); perbaruiKemajuan(); });
el("tidak-pas").addEventListener("change", (e) => { jwb().kotak_tidak_pas = e.target.checked; simpanLokal(); });
el("sebelum").addEventListener("click", () => ke(i - 1));
el("berikut").addEventListener("click", () => ke(i + 1));
el("lompat").addEventListener("change", (e) => ke(Number(e.target.value)));
window.addEventListener("resize", gambarUlang);
el("simpan").addEventListener("click", () => {
  const isi = JSON.stringify({ versi: 1, tanda: "__TANDA__", dibuat: new Date().toISOString(), butir: jawab }, null, 1);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([isi], { type: "application/json" }));
  a.download = "label-ciri.json";
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
