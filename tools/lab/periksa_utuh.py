"""Memeriksa bahwa tiap video riset benar-benar utuh, bukan hanya "berkasnya ada" (temuan K20, 13 Okt 2026).

Pada gelombang unduhan kedua, satu unduhan berakhir dengan kode 1 tetapi meninggalkan berkas .mp4 yang tidak bisa
dibuka; pencatat yang menilai dari adanya berkas menandainya "utuh". Alat ini membuka tiap berkas: lama berkas
dibandingkan dengan lama yang dicatat sumbernya (.info.json), lalu satu gambar di dekat akhir dibaca ke memori.
Unduhan yang terpotong gagal di salah satunya. Tidak ada gambar yang disimpan atau ditampilkan.

Hasilnya ditulis ke berkas catatan. tools/manifes-video.mjs menolak mencatat video baru yang tidak ada di catatan itu.

Dijalankan di lab tanpa jaringan:
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/periksa_utuh.py /kerja/data/video/riset /kerja/data/keluaran/video-utuh.json
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import av

AKHIRAN_VIDEO = {".mp4", ".webm", ".mkv", ".mov"}
SELISIH_DETIK = 2.0  # selisih lama yang masih dianggap sama
SELISIH_BAGIAN = 0.02  # atau dua persen dari lama video, mana yang lebih besar
DEKAT_AKHIR = 0.95  # letak gambar yang dicoba dibaca, sebagai bagian dari lama video


def periksa(jalur):
    """Mengembalikan (utuh, keterangan, ukuran_gambar) untuk satu video.

    `ukuran_gambar` dibaca dari BERKASNYA ("1280x720"), atau None bila tidak terbaca.

    ⛔ Kenapa ini ikut dibaca di sini: tools/manifes-video.mjs dulu mencatat ukuran dari `.info.json`, yaitu
    resolusi ASLI video di sumbernya. Saat unduhan dibatasi resolusinya, berkas yang ada lebih kecil daripada
    yang tercatat — 26 Okt 2026 satu video satu jam tercatat 1280x720 padahal berkasnya 640x360. Setiap angka
    pengukuran yang memakai catatan itu ikut menyesatkan. Alat ini sudah membuka tiap berkas, jadi di sinilah
    tempat yang benar untuk membacanya.
    """
    jalur = Path(jalur)
    try:
        catat = json.loads(jalur.with_name(jalur.stem + ".info.json").read_text(encoding="utf-8")).get("duration")
    except (OSError, ValueError, AttributeError):
        return False, "berkas .info.json tidak ada atau tidak terbaca", None
    if not isinstance(catat, (int, float)) or catat <= 0:
        return False, "berkas .info.json tidak mencatat lama video", None
    try:
        with av.open(str(jalur)) as wadah:
            if not wadah.streams.video:
                return False, "tidak punya aliran gambar", None
            aliran = wadah.streams.video[0]
            lebar, tinggi = aliran.codec_context.width, aliran.codec_context.height
            gambar = f"{lebar}x{tinggi}" if lebar and tinggi else None
            lama = (wadah.duration or 0) / 1e6
            wadah.seek(int(lama * DEKAT_AKHIR * 1e6))
            akhir = next(wadah.decode(video=0), None) is not None
    except Exception as galat:  # berkas rusak, terpotong, atau bukan video
        return False, f"tidak bisa dibuka ({type(galat).__name__})", None
    if abs(lama - catat) > max(SELISIH_DETIK, SELISIH_BAGIAN * catat):
        return False, f"lama berkas {lama:.1f} detik, catatan sumber {catat} detik", gambar
    if not akhir:
        return False, "gambar di dekat akhir tidak terbaca", gambar
    return True, f"{lama:.1f} detik", gambar


def utama(folder, catatan):
    video = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in AKHIRAN_VIDEO)
    utuh, rusak, gambar = {}, {}, {}
    for jalur in video:
        baik, keterangan, ukuran = periksa(jalur)
        if ukuran:
            gambar[jalur.name] = ukuran
        if baik:
            utuh[jalur.name] = jalur.stat().st_size
        else:
            rusak[jalur.name] = keterangan
            print(f"RUSAK {jalur.name}: {keterangan}")
    catatan = Path(catatan)
    catatan.parent.mkdir(parents=True, exist_ok=True)
    waktu = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # `utuh` SENGAJA tetap "nama -> ukuran bita": tools/manifes-video.mjs membandingkan nilainya dengan ukuran
    # berkas di disk. Ukuran gambar ditaruh di kunci BARU supaya catatan lama tetap terbaca.
    catatan.write_text(json.dumps(
        {"diperiksa": waktu, "utuh": utuh, "rusak": rusak, "gambar": gambar}, indent=2))
    print(f"{len(utuh)} utuh, {len(rusak)} bermasalah, dari {len(video)} video")
    return 1 if rusak else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Pakai: python periksa_utuh.py <folder-video> <berkas-catatan.json>")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2]))
