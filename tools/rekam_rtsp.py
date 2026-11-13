"""Merekam kamera RTSP (atau berkas video) dan mengukur mutu gambarnya per detik (Rencana 36, K78).

Untuk kamera rumahan seperti Bardi PTZ (Tuya), yang shutter dan exposure-nya tidak bisa diatur: alat ini membuktikan
dengan angka apakah setelan dan lampu tambahan benar-benar menstabilkan gambar, bukan dengan perkiraan.

Per detik dicatat (tanpa gambar, jadi CSV-nya bebas plat):
  kecerahan        rata-rata luma 0-255
  kecerahan_goyang lompatan kecerahan terbesar antara dua ukuran berturutan dalam detik itu; besar = exposure "berburu"
  jenuh_persen     piksel luma >= 250 (pantulan IR dan lampu kendaraan memutihkan plat)
  gelap_persen     piksel luma <= 5
  ketajaman        median variansi Laplacian; turun = kabur (gerak, kompresi, atau fokus)
  ketajaman_min    yang paling kabur dalam detik itu
  mode             warna / ir / campur (berpindah di dalam detik itu)

Video disalin apa adanya (tanpa dikodekan ulang) bila --simpan-video. Videonya memuat plat: tempatnya hanya di data/
(di-gitignore, CLAUDE.md §4) dan agen tidak membukanya.

Alamat RTSP biasanya memuat sandi, jadi alamat dibaca dari peubah lingkungan (bawaan CCTV_RTSP_URL) dan TIDAK PERNAH
dicetak; pesan galat hanya menyebut jenisnya.

  $env:CCTV_RTSP_URL = "rtsp://..."   # PowerShell
  python tools/rekam_rtsp.py --label tanpa-lampu --detik 120 [--simpan-video] [--daerah 0.3,0.5,0.4,0.4]
  python tools/rekam_rtsp.py --berkas contoh.mp4 --label uji
"""
import argparse
import csv
import hashlib
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parent.parent
KELUAR_BAWAAN = AKAR / "data" / "video" / "riset" / "bardi"
KOLOM = ["detik", "bingkai", "diukur", "kecerahan", "kecerahan_goyang", "jenuh_persen", "gelap_persen",
         "ketajaman", "ketajaman_min", "mode"]
AMBANG_JENUH = 250
AMBANG_GELAP = 5
AMBANG_IR = 4.0  # rata-rata (maks RGB - min RGB) di bawah ini = gambar tanpa warna = mode IR malam


class GalatAlat(Exception):
    def __init__(self, pesan, kode):
        super().__init__(pesan)
        self.kode = kode


def parse_daerah(teks):
    """'x,y,l,t' dalam pecahan 0-1 dari lebar dan tinggi bingkai."""
    if not teks:
        return None
    try:
        nilai = [float(b) for b in teks.split(",")]
    except ValueError:
        raise GalatAlat("--daerah harus empat angka x,y,lebar,tinggi", 2)
    if len(nilai) != 4:
        raise GalatAlat("--daerah harus empat angka x,y,lebar,tinggi", 2)
    x, y, l, t = nilai
    if not (0 <= x < 1 and 0 <= y < 1 and 0 < l <= 1 and 0 < t <= 1 and x + l <= 1 and y + t <= 1):
        raise GalatAlat("--daerah di luar bingkai (pecahan 0-1, x+lebar dan y+tinggi paling besar 1)", 2)
    return nilai


def potong(luma, daerah):
    if daerah is None:
        return luma
    tinggi, lebar = luma.shape
    x, y, l, t = daerah
    x0, y0 = int(x * lebar), int(y * tinggi)
    x1, y1 = max(x0 + 3, int((x + l) * lebar)), max(y0 + 3, int((y + t) * tinggi))
    return luma[y0:y1, x0:x1]


def ketajaman(luma):
    """Variansi Laplacian 4-tetangga. Gambar tajam bertepi kuat, jadi variansinya besar."""
    g = luma.astype(np.float32)
    lap = (g[1:-1, :-2] + g[1:-1, 2:] + g[:-2, 1:-1] + g[2:, 1:-1]) - 4.0 * g[1:-1, 1:-1]
    return float(lap.var())


def ukur_luma(luma):
    jumlah = luma.size
    return {
        "kecerahan": float(luma.mean()),
        "jenuh": 100.0 * float(np.count_nonzero(luma >= AMBANG_JENUH)) / jumlah,
        "gelap": 100.0 * float(np.count_nonzero(luma <= AMBANG_GELAP)) / jumlah,
        "ketajaman": ketajaman(luma),
    }


def mode_warna(rgb_kecil):
    rgb = rgb_kecil.astype(np.int16)
    rentang = rgb.max(axis=2) - rgb.min(axis=2)
    return "ir" if float(rentang.mean()) < AMBANG_IR else "warna"


def ringkas_detik(detik, bingkai, ukuran):
    """ukuran: daftar dict per bingkai yang diukur dalam detik itu, berurutan."""
    baris = {"detik": detik, "bingkai": bingkai, "diukur": len(ukuran)}
    if not ukuran:
        baris.update({k: "" for k in KOLOM[3:]})
        return baris
    terang = [u["kecerahan"] for u in ukuran]
    tajam = [u["ketajaman"] for u in ukuran]
    mode = {u["mode"] for u in ukuran}
    baris.update({
        "kecerahan": round(statistics.fmean(terang), 2),
        "kecerahan_goyang": round(max((abs(b - a) for a, b in zip(terang, terang[1:])), default=0.0), 2),
        "jenuh_persen": round(statistics.fmean(u["jenuh"] for u in ukuran), 3),
        "gelap_persen": round(statistics.fmean(u["gelap"] for u in ukuran), 3),
        "ketajaman": round(statistics.median(tajam), 2),
        "ketajaman_min": round(min(tajam), 2),
        "mode": mode.pop() if len(mode) == 1 else "campur",
    })
    return baris


def ringkasan_akhir(baris_detik, info):
    berisi = [b for b in baris_detik if b["diukur"]]
    hasil = dict(info)
    hasil["detik_tercatat"] = len(baris_detik)
    hasil["bingkai_total"] = sum(b["bingkai"] for b in baris_detik)
    hasil["bingkai_diukur"] = sum(b["diukur"] for b in baris_detik)
    if not berisi:
        return hasil
    urut_mode = [b["mode"] for b in berisi]
    hasil.update({
        "ketajaman_median": round(statistics.median(b["ketajaman"] for b in berisi), 2),
        "ketajaman_terendah": round(min(b["ketajaman_min"] for b in berisi), 2),
        "kecerahan_median": round(statistics.median(b["kecerahan"] for b in berisi), 2),
        "kecerahan_goyang_maks": round(max(b["kecerahan_goyang"] for b in berisi), 2),
        "jenuh_persen_median": round(statistics.median(b["jenuh_persen"] for b in berisi), 3),
        "detik_ir_persen": round(100.0 * sum(m == "ir" for m in urut_mode) / len(urut_mode), 1),
        # Perpindahan warna<->IR (termasuk detik "campur"): kamera yang bolak-balik di senja atau saat lampu menyorot.
        "perpindahan_mode": sum(1 for a, b in zip(urut_mode, urut_mode[1:]) if a != b),
    })
    return hasil


def sha256_berkas(jalur):
    h = hashlib.sha256()
    with open(jalur, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def buka_sumber(av, sumber, rtsp, batas_detik):
    opsi = {"rtsp_transport": "tcp"} if rtsp else {}
    try:
        return av.open(sumber, options=opsi, timeout=(batas_detik, batas_detik))
    except Exception as e:  # pesan PyAV memuat alamat (dan sandinya) atau jalur berkas: hanya jenisnya yang dicetak
        raise GalatAlat(f"sumber tidak bisa dibuka ({type(e).__name__})", 4) from None


def rekam(sumber, rtsp, keluar, label, detik_maks, per_detik, daerah, simpan_video, batas_buka=10):
    import av  # diimpor di sini supaya fungsi ukur bisa diuji tanpa PyAV

    av.logging.set_level(av.logging.PANIC)  # log FFmpeg bisa mencetak alamat RTSP lengkap
    stempel = datetime.now().strftime("%Y%m%d-%H%M%S")
    nama = f"{stempel}-{label}"
    keluar.mkdir(parents=True, exist_ok=True)
    jalur_csv = keluar / f"{nama}-ukur.csv"
    jalur_video = keluar / f"{nama}.mp4"
    jalur_ringkasan = keluar / f"{nama}-ringkasan.json"

    masuk = buka_sumber(av, sumber, rtsp, batas_buka)
    try:
        if not masuk.streams.video:
            raise GalatAlat("sumber tidak punya aliran video", 5)
        aliran = masuk.streams.video[0]
        aliran.thread_type = "AUTO"
        info = {
            "label": label, "sumber": "rtsp" if rtsp else "berkas", "codec": aliran.codec_context.name,
            "fps_dinyatakan": float(aliran.average_rate) if aliran.average_rate else None,
            "daerah": daerah, "ukur_per_detik": per_detik, "dibuat": stempel,
            "ambang": {"jenuh": AMBANG_JENUH, "gelap": AMBANG_GELAP, "ir_rentang_warna": AMBANG_IR},
        }
        wadah = aliran_keluar = None
        video_galat = None
        if simpan_video:
            wadah = av.open(str(jalur_video), "w")
            aliran_keluar = wadah.add_stream_from_template(aliran)

        baris_detik, ukuran_detik, bingkai_detik = [], [], 0
        detik_kini, t0, t_ukur_akhir = 0, None, None
        resolusi, mulai_dinding, sudah_kunci = None, time.monotonic(), False
        selang = 1.0 / per_detik
        selesai = False
        try:
            for paket in masuk.demux(aliran):
                # Paket kosong terakhir (dts None) JANGAN dilewati: ia yang mengeluarkan bingkai sisa dari pengurai.
                # Melewatinya membuang 6 dari 50 bingkai video uji.
                for bingkai in paket.decode():
                    t = bingkai.time if bingkai.time is not None else time.monotonic() - mulai_dinding
                    if t0 is None:
                        t0 = t
                    t -= t0
                    if t >= detik_maks:
                        selesai = True
                        break
                    while int(t) > detik_kini:
                        baris_detik.append(ringkas_detik(detik_kini, bingkai_detik, ukuran_detik))
                        detik_kini, ukuran_detik, bingkai_detik = detik_kini + 1, [], 0
                    bingkai_detik += 1
                    if resolusi is None:
                        resolusi = [bingkai.width, bingkai.height]
                    if t_ukur_akhir is None or t - t_ukur_akhir >= selang - 1e-6:
                        t_ukur_akhir = t
                        luma = bingkai.to_ndarray(format="gray")
                        u = ukur_luma(potong(luma, daerah))
                        kecil = bingkai.reformat(width=max(16, bingkai.width // 4), height=max(16, bingkai.height // 4),
                                                 format="rgb24").to_ndarray()
                        u["mode"] = mode_warna(kecil)
                        ukuran_detik.append(u)
                if selesai:
                    break
                if wadah is not None and video_galat is None and paket.dts is not None:
                    if not sudah_kunci and not paket.is_keyframe:
                        continue  # video yang disimpan dimulai dari bingkai kunci supaya bisa dibuka
                    sudah_kunci = True
                    try:
                        paket.stream = aliran_keluar
                        wadah.mux(paket)
                    except Exception as e:
                        video_galat = type(e).__name__
        except KeyboardInterrupt:
            info["dihentikan_tangan"] = True
        except GalatAlat:
            raise
        except Exception as e:
            info["aliran_putus"] = type(e).__name__
        if bingkai_detik or ukuran_detik:
            baris_detik.append(ringkas_detik(detik_kini, bingkai_detik, ukuran_detik))
        if wadah is not None:
            try:
                wadah.close()
            except Exception as e:
                video_galat = video_galat or type(e).__name__
    finally:
        masuk.close()

    if not baris_detik:
        if simpan_video and jalur_video.exists():
            jalur_video.unlink()
        raise GalatAlat("tidak ada bingkai yang terbaca", 5)

    with open(jalur_csv, "w", newline="", encoding="utf-8") as f:
        tulis = csv.DictWriter(f, fieldnames=KOLOM)
        tulis.writeheader()
        tulis.writerows(baris_detik)
    info["resolusi"] = resolusi
    if simpan_video:
        info["video"] = jalur_video.name if video_galat is None else None
        info["video_galat"] = video_galat
        if video_galat is None:
            info["video_sha256"] = sha256_berkas(jalur_video)
    hasil = ringkasan_akhir(baris_detik, info)
    hasil["fps_nyata"] = round(hasil["bingkai_total"] / max(1, hasil["detik_tercatat"]), 2)
    jalur_ringkasan.write_text(json.dumps(hasil, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return hasil, jalur_ringkasan


def utama(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sumber = p.add_mutually_exclusive_group()
    sumber.add_argument("--env", default="CCTV_RTSP_URL", help="peubah lingkungan berisi alamat RTSP (bawaan CCTV_RTSP_URL)")
    sumber.add_argument("--berkas", help="berkas video sebagai pengganti kamera (untuk uji)")
    p.add_argument("--alamat-berkas", type=Path, default=AKAR / "catatan-lokal" / "kamera-bardi.txt",
                   help="dipakai bila peubah lingkungan kosong; folder catatan-lokal/ di-gitignore")
    p.add_argument("--label", required=True, help="nama percobaan, misalnya tanpa-lampu atau lampu-ir-mati")
    p.add_argument("--detik", type=float, default=60.0)
    p.add_argument("--ukur-per-detik", type=float, default=5.0)
    p.add_argument("--daerah", help="x,y,lebar,tinggi dalam pecahan 0-1: hanya daerah ini yang diukur (misalnya jalur berhenti)")
    p.add_argument("--simpan-video", action="store_true", help="salin videonya apa adanya ke folder keluaran")
    p.add_argument("--keluar", type=Path, default=KELUAR_BAWAAN)
    a = p.parse_args(argv)
    try:
        if not all(c.isalnum() or c in "-_" for c in a.label):
            raise GalatAlat("--label hanya huruf, angka, - dan _", 2)
        if a.detik <= 0 or a.ukur_per_detik <= 0:
            raise GalatAlat("--detik dan --ukur-per-detik harus lebih dari 0", 2)
        daerah = parse_daerah(a.daerah)
        if a.berkas:
            sumber_nyata, rtsp = a.berkas, False
            if not Path(a.berkas).is_file():
                raise GalatAlat("--berkas tidak ada", 2)
        else:
            sumber_nyata, rtsp = os.environ.get(a.env, "").strip(), True
            if not sumber_nyata and a.alamat_berkas.is_file():
                # Peubah lingkungan di terminal owner tidak sampai ke proses agen, jadi alamat juga bisa ditaruh di
                # berkas yang di-gitignore. Baris pertama yang tidak diawali '#'.
                baris = [b.strip() for b in a.alamat_berkas.read_text(encoding="utf-8").splitlines()]
                sumber_nyata = next((b for b in baris if b and not b.startswith("#")), "")
            if not sumber_nyata.startswith(("rtsp://", "rtsps://")):
                raise GalatAlat(f"alamat kamera kosong atau bukan rtsp:// (peubah {a.env} atau {a.alamat_berkas.name})", 2)
        hasil, jalur = rekam(sumber_nyata, rtsp, a.keluar, a.label, a.detik, a.ukur_per_detik, daerah, a.simpan_video)
    except GalatAlat as e:
        print(f"GAGAL: {e}", file=sys.stderr)
        return e.kode
    except OSError as e:  # jalur keluaran bisa memuat nama yang tidak ingin tercetak
        print(f"GAGAL: galat berkas ({type(e).__name__})", file=sys.stderr)
        return 3
    tampil = {k: hasil.get(k) for k in ("label", "resolusi", "fps_nyata", "detik_tercatat", "ketajaman_median",
                                         "ketajaman_terendah", "kecerahan_median", "kecerahan_goyang_maks",
                                         "jenuh_persen_median", "detik_ir_persen", "perpindahan_mode", "video",
                                         "video_galat", "aliran_putus")}
    print(json.dumps({k: v for k, v in tampil.items() if v is not None}, ensure_ascii=False))
    print(f"ringkasan: {jalur.name}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
