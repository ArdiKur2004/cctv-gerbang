"""Layanan baca: satu gambar masuk, plat dan jenis kendaraan keluar. Rencana T6, permintaan owner 26 Okt.

Batas antara mesin dan aplikasi (spec induk 2.2): gambar masuk, bacaan keluar.

⛔ JEMBATANNYA LEWAT FOLDER, BUKAN JARINGAN. Lab berjalan dengan `--network none` (tools/lab.ps1), dan pagar itu
TIDAK dicabut: justru ia yang membuat bobot model dari luar aman dijalankan. Jadi:

    data/keluaran/baca-masuk/<id>.png    ← ditulis TGT (atau kotak gerbang)
    data/keluaran/baca-masuk/<id>.json   ← keterangan: gerbang, arah, waktu
    data/keluaran/baca-keluar/<id>.json  ← ditulis berkas ini: plat, ragu, yakin, jenis

Ini juga bentuk yang benar untuk produk: kotak di gerbang menaruh gambar, mesin memungutnya; tidak ada port
terbuka di antara keduanya.

⛔ Folder masuk dan keluar memuat gambar kendaraan dan nomor plat. Agen tidak membukanya; yang dibaca agen hanya
angka ringkasannya. Pesan galat TIDAK PERNAH memuat jalur atau nama berkas, karena nama berkas bisa memuat
nomor plat — aturan yang sama dengan alat berplat lain di repo ini.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baca_vlm  # noqa: E402,F401  (membisukan log OpenCV, yang mencetak jalur berkas yang tak terbaca)
from kendaraan import cari_dalam_kendaraan  # noqa: E402
from plat import urai  # noqa: E402
from rantai import potong  # noqa: E402

# Susunan hasil yang dibaca sisi Node. Diubah hanya bersama tgt/jembatan.mjs.
SUSUNAN_HASIL = ("plat", "ragu", "yakin", "pola_sah", "jenis", "yakin_jenis", "kendaraan", "ms")

# Huruf yang dipakai pembaca untuk menandai posisi yang tidak ia yakini.
TANDA_RAGU = "?"

AKHIRAN_GAMBAR = {".png", ".jpg", ".jpeg", ".webp"}


def _ke_plat_dan_ragu(teks):
    """Pisahkan teks bacaan menjadi plat baku dan daftar posisi yang diragukan.

    Posisi ragu dihitung pada plat yang SUDAH dirapikan, karena di situlah aturan K46 bekerja (lihat
    tgt/putusan.mjs). Mengembalikan (plat, ragu) atau (None, []) bila tidak ada yang terbaca.
    """
    bersih = "".join(c for c in str(teks or "").upper() if c.isalnum() or c == TANDA_RAGU)
    if not bersih:
        return None, []
    ragu = [i for i, c in enumerate(bersih) if c == TANDA_RAGU]
    plat = bersih.replace(TANDA_RAGU, "")
    # Posisi ragu menunjuk ke plat yang masih memuat tandanya; sesudah tanda dibuang, posisinya tetap sah
    # karena tanda menempati satu huruf. Yang di luar jangkauan dibuang, supaya sisi Node tidak menolaknya.
    ragu = [i for i in ragu if i < len(bersih)]
    return (plat or None), ragu


def baca_satu(gambar, *, cari, cari_kendaraan, baca, kenali_jenis, ambang, cadangan_utuh=True):
    """Satu gambar -> satu hasil. Mengembalikan dict bersusunan SUSUNAN_HASIL.

    Gambar tanpa kendaraan atau tanpa plat BUKAN galat: kamera sering menangkap jalan kosong.
    """
    mulai = time.monotonic()
    if cari_kendaraan is None:
        kendaraan = []
        kotak = [k for k in cari(gambar) if k[4] >= ambang]
    else:
        kendaraan = cari_kendaraan(gambar)
        kotak = cari_dalam_kendaraan(gambar, kendaraan, cari, ambang, cadangan_utuh=cadangan_utuh)

    hasil = {
        "plat": None, "ragu": [], "yakin": 0.0, "pola_sah": False, "jenis": None, "yakin_jenis": 0.0,
        "kendaraan": len(kendaraan), "ms": 0,
    }

    # Plat dengan kotak paling meyakinkan yang dipakai: satu gambar, satu kendaraan yang lewat gerbang.
    terbaik = None
    for k in sorted(kotak, key=lambda b: -float(b[4])):
        potongan = potong(gambar, k)
        if potongan is None or potongan.size == 0:
            continue
        teks, yakin = baca(potongan)
        # Posisi ragu dihitung dari bacaan MENTAH: pengurai pola plat membuang tanda ragunya, jadi ia
        # dijalankan sesudahnya dan hanya untuk menilai bentuknya, bukan untuk membuang bacaannya.
        plat, ragu = _ke_plat_dan_ragu(teks)
        if plat:
            terbaik = (plat, ragu, float(yakin), k, urai(plat) is not None)
            break

    if terbaik:
        hasil["plat"], hasil["ragu"], hasil["yakin"] = terbaik[0], terbaik[1], round(terbaik[2], 4)
        # Bentuk plat yang tidak sesuai pola Indonesia TIDAK dibuang — satpam justru perlu melihatnya — tetapi
        # ditandai, supaya layar bisa menyebutnya.
        hasil["pola_sah"] = bool(terbaik[4])

    # Jenis dibaca dari potongan KENDARAANNYA, bukan dari potongan platnya.
    if kenali_jenis is not None and kendaraan:
        v = max(kendaraan, key=lambda b: (b[3] - b[1]) * (b[2] - b[0]))
        potongan = gambar[max(0, int(v[1])):int(v[3]), max(0, int(v[0])):int(v[2])]
        if potongan.size:
            jenis, yakin_jenis = kenali_jenis(potongan)
            # "tak yakin" dikirim sebagai kosong: TGT memperlakukannya sebagai tidak terbaca, bukan sebagai
            # ketidakcocokan. Mesin yang ragu tidak boleh menjadi penuduh.
            hasil["jenis"] = None if jenis in (None, "", "tak_yakin") else jenis
            hasil["yakin_jenis"] = round(float(yakin_jenis), 4)
    elif kenali_jenis is not None and cari_kendaraan is None and hasil["plat"]:
        # HANYA bila memang tidak ada tahap kendaraan sama sekali: jenis dikenali dari gambar utuh.
        #
        # ⛔ Kalau tahap kendaraan ADA tetapi tidak menemukan apa-apa, jenis dibiarkan KOSONG. Pada uji bukti
        # 26 Okt, jalan cadangan ini menebak "motor" dengan keyakinan 0,95 dari gambar yang tidak memuat
        # kendaraan sama sekali. Tebakan yang meyakinkan atas gambar yang salah lebih berbahaya daripada
        # tidak menjawab: di TGT ia akan muncul sebagai ketidakcocokan jenis, dan satpam dipanggil
        # untuk sesuatu yang tidak pernah terjadi.
        jenis, yakin_jenis = kenali_jenis(gambar)
        hasil["jenis"] = None if jenis in (None, "", "tak_yakin") else jenis
        hasil["yakin_jenis"] = round(float(yakin_jenis), 4)

    hasil["ms"] = int((time.monotonic() - mulai) * 1000)
    return hasil


def jaga_sekali(masuk, keluar, **mesin):
    """Proses semua gambar yang sedang menunggu. Mengembalikan jumlah yang BERHASIL dibaca.

    Satu berkas rusak tidak menghentikan yang lain: gerbang tidak boleh berhenti membaca kendaraan berikutnya
    hanya karena satu gambar cacat.
    """
    masuk, keluar = Path(masuk), Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    berhasil = 0

    for berkas in sorted(p for p in masuk.iterdir() if p.suffix.lower() in AKHIRAN_GAMBAR):
        nama = berkas.stem
        keterangan = {}
        sisi_json = berkas.with_suffix(".json")
        try:
            if sisi_json.exists():
                keterangan = json.loads(sisi_json.read_text())
        except Exception:
            keterangan = {}

        try:
            gambar = cv2.imread(str(berkas))
            if gambar is None:
                raise ValueError("gambar tidak bisa dibuka")
            hasil = baca_satu(gambar, **mesin)
            berhasil += 1
            hasil["galat"] = None
        except Exception as e:
            # Hanya JENIS galatnya, tanpa pesan bawaannya: pesan bawaan sering memuat jalur berkas.
            hasil = {k: (None if k in ("plat", "jenis") else ([] if k == "ragu" else (False if k == "pola_sah" else 0)))
                 for k in SUSUNAN_HASIL}
            hasil["galat"] = f"gagal dibaca ({type(e).__name__})"

        (keluar / f"{nama}.json").write_text(json.dumps({**keterangan, **hasil}))
        # Gambar dibuang sesudah diproses: ia memuat plat, dan masa simpannya bukan di folder antrean.
        berkas.unlink(missing_ok=True)
        sisi_json.unlink(missing_ok=True)

    return berhasil


def muat_mesin(folder_akar, ambang_jenis, *, ambang_plat=0.25, utas=None, folder_unduhan="/kerja/data/unduhan"):
    """Muat rantai jualan: kendaraan -> plat -> baca, ditambah pengenal jenis.

    `ambang_jenis` WAJIB disebut pemanggil: tidak ada ambang "tak yakin" yang tersembunyi di mesin
    (aturan Rencana 33).
    """
    from ciri import PengenalCiri
    from kendaraan import PencariKendaraan
    from onnx_fpo import PembacaOnnxMesin
    from pencari_yolox import PencariYolox

    akar = Path(folder_akar)
    cari_kendaraan = PencariKendaraan(akar / "kendaraan-jualan-k1", utas=utas)
    cari = PencariYolox(akar / "pencari-cctv2-c1", utas=utas)
    # .dengan_yakin: (teks, yakin), bentuk yang sama dengan yang dipakai baca_gambar.py.
    baca = PembacaOnnxMesin(akar / "pembaca-lanjut-r4", folder_unduhan, utas=utas).dengan_yakin
    kenali_jenis = PengenalCiri(akar / "ciri-jenis-j1", ambang=ambang_jenis, utas=utas)
    return {"cari": cari, "cari_kendaraan": cari_kendaraan, "baca": baca, "kenali_jenis": kenali_jenis,
            "ambang": ambang_plat}


def utama(argumen=None):
    p = argparse.ArgumentParser(description="Layanan baca TGT: gambar masuk, plat dan jenis keluar (Rencana T6).")
    p.add_argument("--masuk", default="/kerja/data/keluaran/baca-masuk")
    p.add_argument("--keluar", default="/kerja/data/keluaran/baca-keluar")
    p.add_argument("--akar-mesin", default="/kerja/data/keluaran")
    p.add_argument("--ambang-jenis", type=float, default=0.0,
                   help="ambang tak yakin pengenal jenis; 0 menurut Rencana 33")
    p.add_argument("--ambang-plat", type=float, default=0.25)
    p.add_argument("--utas", type=int, default=None)
    p.add_argument("--sekali", action="store_true", help="proses yang menunggu lalu berhenti")
    p.add_argument("--jeda", type=float, default=0.5, help="jeda antarputaran, detik")
    a = p.parse_args(argumen)

    Path(a.masuk).mkdir(parents=True, exist_ok=True)
    mesin = muat_mesin(a.akar_mesin, a.ambang_jenis, ambang_plat=a.ambang_plat, utas=a.utas)
    print(f"layanan baca siap; masuk={a.masuk} keluar={a.keluar} ambang_jenis={a.ambang_jenis}", file=sys.stderr)

    if a.sekali:
        print(json.dumps({"dibaca": jaga_sekali(a.masuk, a.keluar, **mesin)}))
        return 0

    while True:
        jaga_sekali(a.masuk, a.keluar, **mesin)
        time.sleep(a.jeda)


if __name__ == "__main__":
    raise SystemExit(utama())
