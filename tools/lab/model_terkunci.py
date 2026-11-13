"""Gerbang model: folder model Hugging Face harus PERSIS yang dicatat di tools/vendor.lock.json (model_hf), dan berkas
unduhan harus cocok dengan butir "berkas"-nya.

Asal: disalin dari vision-seed @3591530 (inti/deteksi/bobot.py: sha256_berkas, daftar_model_hf,
verifikasi_folder_model) pada 2026-10-14 (K14). Yang diubah: hanya bagian model Hugging Face yang diambil, letak kunci,
nama galat, dan baris perintah untuk memeriksa satu folder. Berkas yang tak terdaftar membuat seluruh folder ditolak,
dan alat lab tidak pernah mengunduh model sendiri.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/model_terkunci.py /kerja/models/qwen3-vl-2b-instruct
"""
import hashlib
import json
import sys
from pathlib import Path

LOKASI_KUNCI = Path(__file__).resolve().parents[1] / "vendor.lock.json"


class ModelDitolak(Exception):
    """Folder model tak boleh dimuat: tak terdaftar, berkasnya lebih atau kurang, atau isinya berubah."""


def sha256_berkas(berkas):
    sidik = hashlib.sha256()
    with Path(berkas).open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            sidik.update(blok)
    return sidik.hexdigest()


def daftar_model_hf(lokasi=LOKASI_KUNCI):
    """Nama folder -> {nama berkas: sha256}, dari daftar model_hf di kunci."""
    isi = json.loads(Path(lokasi).read_text(encoding="utf-8"))
    return {e["nama"]: {n: s.lower() for n, s in e["berkas"].items()} for e in isi.get("model_hf", [])}


def verifikasi_folder_model(folder, daftar):
    folder = Path(folder)
    berkas = daftar.get(folder.name)
    if berkas is None:
        raise ModelDitolak(f"{folder.name}: tidak terdaftar di kunci model (tools/vendor.lock.json, model_hf)")
    ada = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()} if folder.is_dir() else set()
    lebih = sorted(ada - set(berkas))
    if lebih:
        raise ModelDitolak(f"{folder.name}: {len(lebih)} berkas tidak terdaftar di kunci, folder ditolak ({', '.join(lebih[:5])})")
    for nama, sha in berkas.items():
        jalur = folder / nama
        if not jalur.is_file():
            raise ModelDitolak(f"{folder.name}/{nama}: berkas model tidak ada")
        nyata = sha256_berkas(jalur)
        if nyata != sha:
            raise ModelDitolak(f"{folder.name}/{nama}: SHA-256 {nyata} tidak sama dengan yang terdaftar {sha}")
    return folder


def daftar_berkas(lokasi=LOKASI_KUNCI):
    """Nama butir -> (nama berkas jadi, sha256), dari daftar berkas di kunci (yang diambil tools/ambil-berkas.ps1)."""
    isi = json.loads(Path(lokasi).read_text(encoding="utf-8"))
    return {b["nama"]: (b["berkas"], str(b.get("sha256", "")).lower()) for b in isi.get("berkas", [])}


def verifikasi_berkas(jalur, nama, daftar):
    """Berkas unduhan boleh dimuat hanya bila butirnya tercatat, sudah dikunci, bernama sama, dan SHA-256-nya cocok."""
    jalur = Path(jalur)
    butir = daftar.get(nama)
    if butir is None:
        raise ModelDitolak(f"{nama}: tidak terdaftar di daftar berkas kunci (tools/vendor.lock.json, berkas)")
    berkas, sha = butir
    if not sha:
        raise ModelDitolak(f"{nama}: belum dikunci (sha256 kosong), belum boleh dimuat")
    if jalur.name != berkas:
        raise ModelDitolak(f"{nama}: nama berkas {jalur.name} bukan {berkas}")
    if not jalur.is_file():
        raise ModelDitolak(f"{nama}/{berkas}: berkas tidak ada")
    nyata = sha256_berkas(jalur)
    if nyata != sha:
        raise ModelDitolak(f"{nama}/{berkas}: SHA-256 {nyata} tidak sama dengan yang terdaftar {sha}")
    return jalur


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Pakai: python model_terkunci.py <folder-model>")
        sys.exit(2)
    try:
        hasil = verifikasi_folder_model(sys.argv[1], daftar_model_hf())
    except ModelDitolak as galat:
        print(f"DITOLAK: {galat}")
        sys.exit(1)
    print(f"COCOK {hasil.name}: {len(daftar_model_hf()[hasil.name])} berkas sesuai kunci")
    sys.exit(0)
