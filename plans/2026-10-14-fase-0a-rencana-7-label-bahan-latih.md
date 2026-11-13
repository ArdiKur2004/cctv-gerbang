# Fase 0A, Rencana 7: Label bahan latih dibersihkan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Bahan latih baca huruf yang (1) bebas dari kendaraan yang juga ada di set uji, dan (2) labelnya dibersihkan dengan
cara K22, sesuai keputusan owner K24. Hasilnya `latih-koreksi/pembagian-koreksi.json`: set uji 937 plat dari Rencana 6
(tidak diubah) dan bahan latih yang sudah dibersihkan, siap untuk mesin baca huruf pertama di rencana berikutnya.

**Architecture:** Empat alat Rencana 5–6 mendapat pilihan sisi (`uji` atau `latih`), dengan uji lebih dulu. Satu alat baru,
`kembar_lintas.py`, mengeluarkan plat latih yang gambarnya nyaris kembar dengan gambar uji dan labelnya hanya beda 1–2
huruf; tanpa model dan tanpa waktu owner. Lalu dua pembaca membaca bahan latih, label yang dicurigai masuk lembar untuk
owner, dan jawaban owner membetulkan label latih. Semua alat hanya mencetak hitungan; berkas yang memuat plat tinggal di
`data/`.

**Tech Stack:** sama dengan Rencana 6. Tidak ada yang dipasang dan tidak ada yang diunduh.

**Dasar:** keputusan owner K22, K23, K24 (`SEED.md` §3); spec
[`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md) bagian 8.3 (satu
plat hanya di satu sisi); laporan Rencana 6
[`../bukti/2026-10-14-label-dan-pembaca-kedua.md`](../bukti/2026-10-14-label-dan-pembaca-kedua.md).

---

## Yang diukur sebelum rencana ini ditulis (14 Okt 2026)

Diukur di lab dengan `data/alat-sementara/ukur_kembar.py` dan `ukur_kembar_2.py`, pada
`set-uji-koreksi/pembagian-koreksi.json` (latih 2.850 plat dan 4.467 gambar; uji 937 plat dan 1.422 gambar). Yang dicetak
hanya hitungan. Sidik gambar = dHash 64 bit (selisih terang mendatar pada gambar kelabu 9×8).

| Hal | Yang terbaca |
|---|---|
| Jarak sidik antar-gambar berplat SAMA (9.660 pasangan) | persentil 5/25/50/75/95 = 1/15/21/26/33; 10,9% berjarak ≤ 4, 15,1% ≤ 8 |
| Jarak sidik antar-gambar berplat BEDA (20.000 sampel acak) | persentil 5/50/95 = 22/32/40; **0** pasangan berjarak ≤ 12 |
| Plat uji yang punya gambar latih berjarak ≤ 0 / ≤ 4 / ≤ 8 | 5 / 20 / 84 dari 937 |
| Pasangan gambar lintas sisi berjarak ≤ 4 | 22; label berjarak sunting 1: **17**, 2: **4**, 3 atau lebih: 1 |
| Pasangan gambar lintas sisi berjarak ≤ 8 | 177; label berjarak sunting 1: **22**, 2: **5**, 3 atau lebih: 150 |
| Pasangan berplat beda di DALAM sisi latih berjarak ≤ 4 / ≤ 8 | 33 / 309 dari 9.966.023 |
| Alat Rencana 5–6 | `baca_vlm.nilai`, `ringkas`, `label_curiga.cari`, dan `nilai_ulang.koreksi` hanya bekerja pada `pembagian["uji"]` |

Bacaan agen:

1. **Ada kendaraan yang sama di kedua sisi, disembunyikan oleh label yang salah ketik.** Gambar yang nyaris kembar dengan
   label yang hanya beda 1–2 huruf hampir pasti kendaraan yang sama: pada jarak ≤ 4, 21 dari 22 pasangan berpola begitu.
   Kemiripan kebetulan tidak menghasilkan label yang nyaris sama sesering itu.
2. **Gambar mirip saja tidak cukup.** Pada jarak ≤ 8, 150 dari 177 pasangan berlabel jauh berbeda; potongan plat memang
   mirip satu sama lain. Jadi aturannya dua syarat: gambar berjarak ≤ 8 **dan** label berjarak sunting ≤ 2.
3. **Pasangan berplat beda di dalam sisi latih bukan alarm palsu murni**: label latih belum diperiksa, jadi sebagian dari 33
   pasangan berjarak ≤ 4 itu kemungkinan juga kendaraan yang sama berlabel salah. Karena itu angka itu tidak dipakai
   sebagai taksiran alarm palsu.
4. **Yang dikeluarkan adalah plat LATIH** (seluruh kedatangannya). Set uji yang sudah dibetulkan di Rencana 6 tetap utuh,
   sama dengan arah K24 untuk kebocoran sesudah label latih dibetulkan. Salah keluarkan hanya membuang beberapa bahan latih;
   salah biarkan membuat angka mesin tampak lebih bagus dari kenyataan.

Taksiran waktu: Qwen3-VL membaca 4.467 gambar latih dalam sekitar 20 menit (0,277 detik per gambar, Rencana 5);
fast-plate-ocr sekitar 1 menit di CPU. Label latih yang dicurigai: sekitar 90-an bila porsinya sama dengan set uji
(31 dari 945). Itu taksiran.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–6 | Bengkel sampai pembetulan label set uji | Selesai 13–14 Okt |
| **7 (dokumen ini)** | Pilihan sisi di empat alat; kendaraan kembar lintas sisi; label bahan latih dibersihkan (K24) | Ditulis |
| 8 | Mesin baca huruf buatan sendiri yang pertama (jenis model, izin, latih, ukur pada set uji yang adil terhadap pembaca ketiga); lalu mencari plat di foto utuh dan video, plat buatan komputer, taksiran kecepatan, laporan Fase 0A | Ditulis saat Rencana 7 selesai; dipecah lagi bila terlalu besar |

## Aturan eksekusi untuk semua task

Sama dengan Rencana 6. Tambahan:
- Agen juga tidak membuka `kembar/pembagian.json`, `latih-koreksi/*`, `label-curiga-latih/curiga.json`, atau
  `lembar-curiga-latih/*`.
- Qwen3-VL di Task 3 adalah job kartu grafis sekitar 20 menit: periksa `nvidia-smi` dulu, jalankan di latar, dan jangan
  menjalankan gerbang lab selama job itu jalan (kunci bengkel akan membuatnya menunggu).

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/baca_vlm.py`, `tools/lab/baca_fpo.py`, `tools/lab/label_curiga.py`, `tools/lab/nilai_ulang.py` dan ujinya (ubah) | Pilihan sisi | 1 |
| `tools/lab/kembar_lintas.py`, `tools/lab/uji/test_kembar_lintas.py` (baru) | Kendaraan kembar lintas sisi | 2 |
| `bukti/2026-10-1x-label-bahan-latih.md` dan ringkasan JSON (baru) | Laporan | 6 |
| `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Catatan | 4, 6 |

Berkas data yang dihasilkan (semuanya di `data/keluaran/`, memuat plat): `kembar/` (Task 2), `baca-vlm-latih/` dan
`baca-fpo-latih/` (Task 3), `label-curiga-latih/` dan `lembar-curiga-latih/` (Task 4), `latih-koreksi/` (Task 5).

---

### Task 1: Pilihan sisi di empat alat

**Files:**
- Modify: `tools/lab/baca_vlm.py`, `tools/lab/baca_fpo.py`, `tools/lab/label_curiga.py`, `tools/lab/nilai_ulang.py`
- Modify: `tools/lab/uji/test_baca_vlm.py`, `test_baca_fpo.py`, `test_label_curiga.py`, `test_nilai_ulang.py`

- [x] **Step 1: Tulis ujinya**

Tambahkan di akhir `tools/lab/uji/test_baca_vlm.py`:

```python
def test_sisi_latih_dibaca_bila_diminta(tmp_path):
    pembagian, jalur, folder = siapkan(tmp_path, [("B1234XYZ", "mobil-terang", 1)])
    jalur.write_text(json.dumps({"latih": pembagian["uji"], "uji": []}))

    kode = bv.utama(jalur, folder, tmp_path / "model-tiruan", tmp_path / "keluar", baca=pembaca(["B1234XYZ"]), sisi="latih")

    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert kode == 0 and r["sisi"] == "latih"
    assert r["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1


def test_baris_perintah_menerima_sisi_latih_sampai_ke_gerbang_model(tmp_path):
    # Rantainya: argumen sisi diterima, lalu gerbang folder model menolak model tiruan (bukan petunjuk pakai).
    lain = tmp_path / "model-lain"
    lain.mkdir()

    hasil = subprocess.run([sys.executable, str(SKRIP), str(tmp_path / "p.json"), str(tmp_path), str(lain),
                            str(tmp_path / "keluar"), "latih"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "DITOLAK" in hasil.stdout, hasil.stdout + hasil.stderr


def test_baris_perintah_menolak_sisi_yang_tidak_dikenal(tmp_path):
    hasil = subprocess.run([sys.executable, str(SKRIP), "p.json", "g", "m", "k", "semua"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "Pakai" in hasil.stdout
```

Tambahkan di akhir `tools/lab/uji/test_baca_fpo.py`:

```python
def test_sisi_latih_dibaca_bila_diminta(tmp_path):
    pembagian, jalur, folder = siapkan(tmp_path)
    jalur.write_text(json.dumps({"latih": pembagian["uji"], "uji": []}))

    kode = bf.utama(jalur, folder, tmp_path / "unduhan", tmp_path / "keluar", baca=lambda g: "B1234XYZ", sisi="latih")

    r = json.loads((tmp_path / "keluar/ringkasan.json").read_text())
    assert kode == 0 and r["sisi"] == "latih" and r["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1


def test_baris_perintah_menerima_sisi_latih_sampai_ke_gerbang_berkas(tmp_path):
    _, jalur, folder = siapkan(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), str(jalur), str(folder), str(tmp_path / "unduhan-kosong"),
                            str(tmp_path / "keluar"), "latih"], capture_output=True, text=True)

    assert hasil.returncode == 2 and "DITOLAK" in hasil.stdout, hasil.stdout + hasil.stderr
```

Tambahkan di akhir `tools/lab/uji/test_label_curiga.py`:

```python
def test_sisi_latih_lewat_baris_perintah(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps({"latih": pembagian("B1234XYZ")["uji"], "uji": []}))
    for nama in ("a.jsonl", "b.jsonl"):
        (tmp_path / nama).write_text(json.dumps({"berkas": "test/B1234XYZ_1.png", "bacaan": "B1234XYE"}) + "\n")

    kode = lcu.utama([str(tmp_path / "pembagian.json"), str(tmp_path / "a.jsonl"), str(tmp_path / "b.jsonl"),
                      str(tmp_path / "keluar"), "--sisi", "latih"])

    assert kode == 0
    assert json.loads((tmp_path / "keluar/curiga.json").read_text())[0]["usulan"] == "B1234XYE"
    assert json.loads((tmp_path / "keluar/ringkasan.json").read_text())["sisi"] == "latih"
```

Tambahkan di akhir `tools/lab/uji/test_nilai_ulang.py`:

```python
PEMBAGIAN_L = {"latih": [k("D9000AB"), k("D9100AB")], "uji": [k("D1500X")]}
CURIGA_L = {"contoh": [{"nomor": 1, "teks": "D9000AB", "usulan": "D9000AC", "kelompok": "mobil-terang", "berkas": "test/D9000AB_1.png"},
                       {"nomor": 2, "teks": "D9100AB", "usulan": "D1500X", "kelompok": "mobil-terang", "berkas": "test/D9100AB_1.png"}]}


def test_sisi_latih_dibetulkan_dan_yang_menjadi_plat_uji_dikeluarkan(tmp_path):
    # K24: label latih yang dibetulkan bisa ternyata plat di set uji; yang dikeluarkan bahan latihnya, set uji tetap.
    for nama, isi in (("pembagian.json", PEMBAGIAN_L), ("curiga.json", CURIGA_L), ("contoh.json", CONTOH)):
        (tmp_path / nama).write_text(json.dumps(isi))
    (tmp_path / "hasil.jsonl").write_text(json.dumps({"berkas": "test/D9000AB_1.png", "bacaan": "D9000AC"}) + "\n")
    argumen = [str(tmp_path / n) for n in ("pembagian.json", "curiga.json", "contoh.json")] + [
        str(tmp_path / "keluar"), "--sisi", "latih", "--b-benar", "1,2", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    assert nu.utama(argumen) == 0

    baru = json.loads((tmp_path / "keluar/pembagian-koreksi.json").read_text())
    assert [x["teks"] for x in baru["latih"]] == ["D9000AC"] and [x["teks"] for x in baru["uji"]] == ["D1500X"]
    r = json.loads((tmp_path / "keluar/ringkasan-koreksi.json").read_text())
    assert (r["dibetulkan"], r["dikeluarkan_bocor"], r["plat_di_kedua_sisi"], r["sisi"]) == (2, 1, 0, "latih")
    assert r["pembaca"]["tiruan"]["mobil-terang"]["kedatangan_benar"] == 1


def test_lembar_contoh_tidak_berlaku_untuk_sisi_latih():
    with pytest.raises(nu.SalahPakai, match="set uji"):
        nu.koreksi(PEMBAGIAN_L, CURIGA_L, CONTOH, {1}, set(), {1}, sisi="latih")
```

- [x] **Step 2: Jalankan, pastikan merah karena pilihan sisi belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `7 failed, 129 passed`, `EXIT=1`. Yang gagal: ketujuh uji baru kecuali `test_baris_perintah_menolak_sisi_yang_tidak_dikenal`
(yang ini langsung hijau karena baris perintah lama sudah menolak enam argumen; ia menjaga sesudah perubahan). Sebabnya:
argumen `sisi` tidak dikenal (`TypeError`, `SystemExit` dari argparse) atau baris perintah mencetak petunjuk pakai alih-alih
sampai ke gerbang.

- [x] **Step 3: Tambahkan pilihan sisi**

`tools/lab/baca_vlm.py`:
- Sesudah `ISIAN = ...`, tambahkan `SISI = ("uji", "latih")`.
- `ringkas(pembagian, bacaan)` menjadi `ringkas(pembagian, bacaan, sisi="uji")`; docstring "...terhadap label sisi `sisi` di
  `pembagian` (bawaan: set uji)."; `for kedatangan in pembagian["uji"]:` menjadi `for kedatangan in pembagian[sisi]:`.
- `nilai(pembagian, folder_gambar, baca)` menjadi `nilai(pembagian, folder_gambar, baca, sisi="uji")`; perulangannya atas
  `pembagian[sisi]`; `ringkas(pembagian, bacaan)` menjadi `ringkas(pembagian, bacaan, sisi)`.
- `utama(..., baca=None)` menjadi `utama(..., baca=None, sisi="uji")`; `nilai(pembagian, folder_gambar, baca)` menjadi
  `nilai(pembagian, folder_gambar, baca, sisi)`; ringkasan menjadi `{"model": ..., "pertanyaan": PERTANYAAN, "sisi": sisi, **ringkasan}`.
- Docstring modul: baris perintah ditambah `[uji|latih]` di akhir.
- Bagian `__main__` menjadi:

```python
if __name__ == "__main__":
    if len(sys.argv) not in (5, 6) or (len(sys.argv) == 6 and sys.argv[5] not in SISI):
        print("Pakai: python baca_vlm.py <pembagian.json> <folder-gambar> <folder-model> <folder-keluaran> [uji|latih]")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:5], sisi=sys.argv[5] if len(sys.argv) == 6 else "uji"))
```

`tools/lab/baca_fpo.py`:
- Impor menjadi `from baca_vlm import KELOMPOK, SISI, nilai, uraikan`.
- `utama(..., baca=None)` menjadi `utama(..., baca=None, sisi="uji")`; `nilai(...)` menerima `sisi`; ringkasan menjadi
  `{"model": ..., "sisi": sisi, **ringkasan}`.
- Docstring dan `__main__` sama polanya dengan `baca_vlm.py` (petunjuk pakai `baca_fpo.py ... <folder-unduhan> <folder-keluaran> [uji|latih]`).

`tools/lab/label_curiga.py`:
- `cari(pembagian, bacaan_a, bacaan_b)` menjadi `cari(pembagian, bacaan_a, bacaan_b, sisi="uji")`, perulangan atas
  `pembagian[sisi]`.
- Di `utama`: `urai_argumen.add_argument("--sisi", choices=("uji", "latih"), default="uji")`; `cari(..., p.sisi)`;
  ringkasan menjadi `{"aturan": ..., "sisi": p.sisi, "kedatangan": len(pembagian[p.sisi]), "dicurigai": ..., "per_kelompok":
  {... atas pembagian[p.sisi] ...}}` (kunci `kedatangan_uji` diganti `kedatangan`); baris layar pertama menjadi
  `print(f"dicurigai: {len(curiga)} dari {len(pembagian[p.sisi])} kedatangan {p.sisi}")`.

`tools/lab/nilai_ulang.py` — `koreksi` menjadi:

```python
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
```

Di `utama`: `urai_argumen.add_argument("--sisi", choices=("uji", "latih"), default="uji")`; panggilan `koreksi(...)`
mendapat `sisi=p.sisi`; `ringkas(baru, baca_hasil(jalur))` menjadi `ringkas(baru, baca_hasil(jalur), p.sisi)`. Docstring
modul: aturan K23 ditulis berlaku dua arah (sisi uji: label baru sama dengan plat latih; sisi latih: label baru sama dengan
plat uji), dan `--salah-contoh` hanya untuk sisi uji.

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `136 passed` (128 + 8 baru) dan `EXIT=0`; uji Rencana 5–6 tetap hijau.

- [x] **Step 5: Bukti tambahan pada data sungguhan (perilaku sisi uji tidak berubah)**

Run (PowerShell): `powershell -NoProfile -File tools\lab.ps1 python -I /kerja/data/alat-sementara/banding_ringkas.py; "EXIT=$LASTEXITCODE"`
Expected: `baca-vlm: sama`, `baca-fpo: sama`, `EXIT=0`.

- [x] **Step 6: Commit**

```bash
git add tools/lab/baca_vlm.py tools/lab/baca_fpo.py tools/lab/label_curiga.py tools/lab/nilai_ulang.py tools/lab/uji/test_baca_vlm.py tools/lab/uji/test_baca_fpo.py tools/lab/uji/test_label_curiga.py tools/lab/uji/test_nilai_ulang.py
git commit -q -F - <<'EOF'
Pilihan sisi uji atau latih di empat alat baca huruf

Alasan: K24 membersihkan label bahan latih dengan cara K22, sedangkan alat
Rencana 5-6 hanya bekerja pada set uji. Sekarang pembaca Qwen3-VL, pembaca
fast-plate-ocr, pencari label curiga, dan penilai ulang menerima sisi
(bawaan: uji, jadi perilaku lama tidak berubah). Aturan K23 kini berlaku dua
arah: label baru yang sama dengan plat di sisi lain dikeluarkan dari sisi
yang dibetulkan, sehingga set uji yang sudah dibetulkan tetap utuh.

Uji ditulis lebih dulu dan terlihat merah (7 gagal; 1 penjaga langsung
hijau). Gerbang lab: 128 -> 136. Pada data sungguhan ringkasan sisi uji
yang dihitung ulang tetap sama persis.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Kendaraan kembar lintas sisi, dikenali dari gambar

**Files:**
- Create: `tools/lab/kembar_lintas.py`
- Create: `tools/lab/uji/test_kembar_lintas.py`

- [x] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_kembar_lintas.py`:

```python
"""Uji tools/lab/kembar_lintas.py: kendaraan yang sama di kedua sisi dikenali dari gambar yang nyaris kembar dan label yang
hanya beda sedikit; yang dikeluarkan bahan latihnya, set uji tidak diubah."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kembar_lintas as kl  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "kembar_lintas.py"


def gambar(folder, nama, benih):
    jalur = folder / nama
    jalur.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(jalur), np.random.default_rng(benih).integers(0, 256, (30, 100), dtype=np.uint8))
    return nama


def siapkan(tmp_path, latih, uji):
    """latih, uji = daftar (teks, benih gambar). Benih sama = gambar kembar persis."""
    folder = tmp_path / "gambar"
    pembagian = {s: [{"teks": t, "kelompok": "mobil-terang", "berkas": [gambar(folder, f"{s}/{t}_1.png", b)]} for t, b in daftar]
                 for s, daftar in (("latih", latih), ("uji", uji))}
    berkas = tmp_path / "pembagian.json"
    berkas.write_text(json.dumps(pembagian))
    return pembagian, berkas, folder


def test_gambar_kembar_berlabel_beda_sedikit_mengeluarkan_plat_latih(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("D1234AE", 1), ("D5555X", 2)], [("D1234AB", 1)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert [x["teks"] for x in baru["latih"]] == ["D5555X"] and [x["teks"] for x in baru["uji"]] == ["D1234AB"]
    assert (hitung["pasangan_mirip"], hitung["pasangan_kembar"], hitung["latih_dikeluarkan"]) == (1, 1, 1)


def test_gambar_kembar_berlabel_jauh_tidak_dikeluarkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("B9876XY", 1)], [("D1234AB", 1)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert len(baru["latih"]) == 1 and (hitung["pasangan_mirip"], hitung["latih_dikeluarkan"]) == (1, 0)


def test_label_beda_sedikit_tetapi_gambar_lain_tidak_dikeluarkan(tmp_path):
    pembagian, _, folder = siapkan(tmp_path, [("D1234AE", 7)], [("D1234AB", 8)])

    baru, hitung = kl.buang_kembar(pembagian, folder)

    assert len(baru["latih"]) == 1 and hitung["pasangan_mirip"] == 0


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    _, berkas, folder = siapkan(tmp_path, [("D1234AE", 1)], [("D1234AB", 1)])

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "1234" not in hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "latih dikeluarkan: 1" in hasil.stdout
    assert json.loads((tmp_path / "keluar/pembagian.json").read_text())["latih"] == []
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'kembar_lintas'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/kembar_lintas.py`:

```python
"""Kendaraan yang sama di kedua sisi, dikenali dari GAMBARNYA (K24): gambar yang nyaris kembar dan label yang hanya beda
sedikit (dugaan salah ketik label pada kendaraan yang sama).

Diukur 14 Okt (Rencana 7): pasangan gambar berplat beda hampir tak pernah berjarak dHash <= 12 (0 dari 20.000 sampel
acak), sedangkan 11% pasangan gambar berplat sama berjarak <= 4. Lintas sisi, dari 177 pasangan berjarak <= 8, 27
berlabel beda 1-2 huruf (dugaan kendaraan yang sama) dan 150 berlabel beda 3 huruf atau lebih (dugaan potongan plat yang
kebetulan mirip). Jadi aturannya dua syarat sekaligus.

Aturan: bila sebuah gambar latih dan sebuah gambar uji berjarak dHash <= BATAS_GAMBAR dan labelnya berjarak sunting
<= BATAS_LABEL, seluruh kedatangan LATIH itu dikeluarkan. Set uji tidak diubah (sudah dibetulkan di Rencana 6). Salah
keluarkan hanya membuang sedikit bahan latih; salah biarkan membuat angka mesin tampak lebih bagus dari kenyataan.

Keluaran: pembagian.json (memuat plat; tinggal di data/) dan ringkasan.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/kembar_lintas.py /kerja/data/keluaran/set-uji-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/kembar
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

# OpenCV mencetak jalur berkas yang tak bisa dibuka ke stderr, dan pada INDO-ALPR jalur itu nomor plat: dibisukan.
cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)

BATAS_GAMBAR = 8
BATAS_LABEL = 2


def dhash(jalur):
    """Sidik gambar 64 bit (selisih terang mendatar pada gambar kelabu 9x8), atau None bila gambar tak terbaca."""
    kelabu = cv2.imread(str(jalur), cv2.IMREAD_GRAYSCALE)
    if kelabu is None:
        return None
    kecil = cv2.resize(kelabu, (9, 8), interpolation=cv2.INTER_AREA).astype(np.int16)
    return int(np.packbits((kecil[:, 1:] > kecil[:, :-1]).flatten()).view(">u8")[0])


def sunting(a, b):
    """Jarak sunting (Levenshtein) antara dua teks."""
    sebelum = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        kini = [i]
        for j, y in enumerate(b, 1):
            kini.append(min(sebelum[j] + 1, kini[j - 1] + 1, sebelum[j - 1] + (x != y)))
        sebelum = kini
    return sebelum[-1]


def buang_kembar(pembagian, folder_gambar):
    """Kembali: (pembagian tanpa plat latih yang kembar dengan plat uji, hitungan tanpa nomor plat)."""
    sidik, tak_terbaca = {}, 0
    for s in ("latih", "uji"):
        sidik[s] = []
        for i, k in enumerate(pembagian[s]):
            for b in k["berkas"]:
                h = dhash(Path(folder_gambar) / b)
                if h is None:
                    tak_terbaca += 1
                else:
                    sidik[s].append((i, h))
    nilai_latih = np.array([h for _, h in sidik["latih"]], dtype=np.uint64)
    indeks_latih = np.array([i for i, _ in sidik["latih"]], dtype=np.int64)
    mirip, kembar, buang = 0, 0, set()
    for j, h in sidik["uji"]:
        jarak = np.unpackbits(np.bitwise_xor(nilai_latih, np.uint64(h)).view(np.uint8).reshape(-1, 8), axis=1).sum(axis=1)
        for i in indeks_latih[jarak <= BATAS_GAMBAR]:
            mirip += 1
            if sunting(pembagian["uji"][j]["teks"], pembagian["latih"][int(i)]["teks"]) <= BATAS_LABEL:
                kembar += 1
                buang.add(int(i))
    baru = {"latih": [k for i, k in enumerate(pembagian["latih"]) if i not in buang], "uji": pembagian["uji"]}
    hitung = {"aturan": {"batas_gambar_dhash": BATAS_GAMBAR, "batas_label_sunting": BATAS_LABEL},
              "gambar_tak_terbaca": tak_terbaca, "pasangan_mirip": mirip, "pasangan_kembar": kembar,
              "latih_dikeluarkan": len(buang), "kedatangan": {s: len(baru[s]) for s in ("latih", "uji")}}
    return baru, hitung


def utama(berkas_pembagian, folder_gambar, keluar):
    baru, hitung = buang_kembar(json.loads(Path(berkas_pembagian).read_text()), folder_gambar)
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian.json").write_text(json.dumps(baru, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(hitung, indent=2))
    print(f"pasangan gambar mirip (dHash <= {BATAS_GAMBAR}): {hitung['pasangan_mirip']}; "
          f"di antaranya berlabel beda <= {BATAS_LABEL} huruf (dugaan kendaraan sama): {hitung['pasangan_kembar']}")
    print(f"latih dikeluarkan: {hitung['latih_dikeluarkan']}; sisa latih {hitung['kedatangan']['latih']}, "
          f"uji {hitung['kedatangan']['uji']}; gambar tak terbaca {hitung['gambar_tak_terbaca']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python kembar_lintas.py <pembagian.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `140 passed` (136 + 4 baru) dan `EXIT=0`.

- [x] **Step 5: Jalankan pada data sungguhan**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/kembar_lintas.py /kerja/data/keluaran/set-uji-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/kembar; "EXIT=$LASTEXITCODE"`
Expected: `pasangan gambar mirip (dHash <= 8): 177; di antaranya berlabel beda <= 2 huruf (dugaan kendaraan sama): 27`
(sama dengan pengukuran sebelum rencana ini ditulis; bila berbeda, **berhenti dan cari sebabnya**), `latih dikeluarkan: N`
dengan N paling banyak 27, `sisa latih 2850 - N, uji 937`, `gambar tak terbaca 0`, `EXIT=0`.

- [x] **Step 6: Commit**

```bash
git add tools/lab/kembar_lintas.py tools/lab/uji/test_kembar_lintas.py
git commit -q -F - <<'EOF'
Kendaraan kembar lintas sisi dikenali dari gambar, bahan latihnya dikeluarkan

Alasan: diukur 14 Okt, gambar latih dan uji yang nyaris kembar dengan label
yang hanya beda 1-2 huruf hampir pasti kendaraan yang sama yang labelnya
salah ketik (21 dari 22 pasangan berjarak dHash <= 4 berpola begitu),
sedangkan pasangan berplat beda acak tak pernah berjarak <= 12. Kebocoran
seperti itu membuat angka mesin buatan sendiri tampak lebih bagus dari
kenyataan, dan tidak terlihat dari label. Yang dikeluarkan plat latih,
supaya set uji yang sudah dibetulkan (Rencana 6) tetap utuh.

Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError:
kembar_lintas). Gerbang lab: 136 -> 140. Pada data sungguhan: <angka Step 5>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Dua pembaca membaca bahan latih

- [x] **Step 1: fast-plate-ocr (CPU)**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_fpo.py /kerja/data/keluaran/kembar/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/unduhan /kerja/data/keluaran/baca-fpo-latih latih; "EXIT=$LASTEXITCODE"`
Expected: empat baris kelompok (terhadap label latih penerbit yang belum dibersihkan), `detik per gambar` sekitar 0,01,
`EXIT=0`.

- [x] **Step 2: Qwen3-VL (kartu grafis, di latar)**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
Expected: tidak ada job vision-seed yang memakai kartu grafis.

Run (PowerShell, di latar; keluaran ke berkas log di folder kerja sementara):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_vlm.py /kerja/data/keluaran/kembar/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/models/qwen3-vl-2b-instruct /kerja/data/keluaran/baca-vlm-latih latih; "EXIT=$LASTEXITCODE"`
Expected sesudah sekitar 20 menit: empat baris kelompok, `detik per gambar` sekitar 0,28, `EXIT=0`. Selama job ini jalan,
gerbang lab tidak dijalankan.

Kedua langkah tidak mengubah kode, jadi tidak ada commit; angkanya dicatat di Task 4.

---

### Task 4: Label latih yang dicurigai dan lembarnya untuk owner

- [x] **Step 1: Cari label latih yang dicurigai**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/label_curiga.py /kerja/data/keluaran/kembar/pembagian.json /kerja/data/keluaran/baca-vlm-latih/hasil.jsonl /kerja/data/keluaran/baca-fpo-latih/hasil.jsonl /kerja/data/keluaran/label-curiga-latih --sisi latih; "EXIT=$LASTEXITCODE"`
Expected: `dicurigai: N dari <sisa latih> kedatangan latih`, empat baris kelompok, `EXIT=0`. Angka dicatat apa adanya.

**Bila N lebih dari 200 (sepuluh lembar), BERHENTI di sini** dan laporkan N ke owner sebelum membuat lembar.

- [x] **Step 2: Buat lembar, tanpa membukanya**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_curiga.py /kerja/data/keluaran/label-curiga-latih/curiga.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-curiga-latih; "EXIT=$LASTEXITCODE"`
Expected: `N baris {...} -> M lembar di /kerja/data/keluaran/lembar-curiga-latih. ... agen tidak membukanya.`, `EXIT=0`.
**Agen tidak membuka berkas-berkas itu.**

- [x] **Step 3: Catat posisi sementara**

`ROADMAP.md` lewat skrip pencatat berkas (jangkar tepat sekali): butir "Rencana 7 dijalankan" dengan anak butir (Task 1–4
selesai dengan angkanya; `- [ ] Owner memeriksa lembar label latih yang dicurigai ← di sini sekarang`; Task 5–6), baris
status, dan satu baris changelog beralasan dengan angka Task 2–4. Kotak langkah rencana ini dicentang sampai Step 3. Commit.

- [x] **Step 4: BERHENTI. Minta owner memeriksa lembar curiga latih**

Minta owner membuka `D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-curiga-latih\lembar-curiga-*.png` (agen
tidak membukanya) dan menjawab **dengan nomor baris saja, tanpa mengetik nomor plat**:

1. nomor baris yang tulisan hijaunya (B) benar;
2. nomor baris yang tulisan biru (A) maupun hijau (B) sama-sama salah.

Baris yang tidak disebut dianggap tulisan biru (A) benar. Bila owner tetap menulis nomor plat, nomor itu tidak disalin ke
berkas mana pun dan barisnya diperlakukan sebagai "keduanya salah" (`CLAUDE.md` §4).

---

### Task 5: Label latih dibetulkan, kebocoran diperiksa ulang

- [x] **Step 1: Jalankan penilai ulang untuk sisi latih**

Run (PowerShell), dengan nomor baris dari jawaban owner:
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/nilai_ulang.py /kerja/data/keluaran/kembar/pembagian.json /kerja/data/keluaran/lembar-curiga-latih/lembar-curiga.json /kerja/data/keluaran/lembar-contoh/lembar-contoh.json /kerja/data/keluaran/latih-koreksi --sisi latih --b-benar <...> --keduanya-salah <...> --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm-latih/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo-latih/hasil.jsonl; "EXIT=$LASTEXITCODE"`
Expected: satu baris hitungan (dibetulkan, dikeluarkan, dikeluarkan karena sama dengan plat uji, `plat di kedua sisi 0`,
kedatangan latih per kelompok), lalu angka kedua pembaca pada bahan latih, `EXIT=0`.

- [x] **Step 2: Periksa ulang kendaraan kembar pada hasil akhir**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/kembar_lintas.py /kerja/data/keluaran/latih-koreksi/pembagian-koreksi.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/kembar-akhir; "EXIT=$LASTEXITCODE"`
Expected: `latih dikeluarkan: 0`, `EXIT=0`. Bila lebih dari 0 (label latih yang baru dibetulkan menjadi nyaris sama dengan
plat uji), hasil `kembar-akhir/pembagian.json` yang dipakai sebagai bahan akhir, dan angkanya dicatat.

- [x] **Step 3: Tidak ada commit kode**

Task ini tidak mengubah kode. Angkanya masuk laporan di Task 6.

---

### Task 6: Laporan, catatan, dan laporan ke owner

- [x] **Step 1: Salin ringkasan ke `bukti/` sesudah dibuktikan tanpa nomor plat (dengan kontrol positif)**

Skrip sekali pakai `data/alat-sementara/periksa-bukti-7.py`, pola `periksa-bukti-6.py`. Larangan: teks plat dan nama
berkas di `set-uji-koreksi/pembagian-koreksi.json`, ditambah `usulan` di `label-curiga/curiga.json` dan
`label-curiga-latih/curiga.json`. Kontrol positif pada `latih-koreksi/pembagian-koreksi.json`. Ringkasan yang diperiksa:
`kembar/ringkasan.json`, `baca-fpo-latih/ringkasan.json`, `baca-vlm-latih/ringkasan.json`,
`label-curiga-latih/ringkasan.json`, `latih-koreksi/ringkasan-koreksi.json`, dan `kembar-akhir/ringkasan.json`.

- [x] **Step 2: Tulis laporan `bukti/<tanggal>-label-bahan-latih.md`**

Isinya: kendaraan kembar lintas sisi (pasangan mirip, kembar, latih dikeluarkan, dengan ukuran kalibrasi); kedua pembaca
pada bahan latih terhadap label penerbit; label latih yang dicurigai; jawaban owner dalam nomor baris; hasil pembetulan;
pemeriksaan ulang kembar; ukuran bahan latih akhir per kelompok. **Batas:** cara K22 menangkap kira-kira separuh label
salah; kembar yang labelnya beda lebih dari 2 huruf, atau gambarnya tidak nyaris kembar, tidak tertangkap; dHash hanya
satu cara sidik gambar; potongan plat, bukan kamera gerbang.

- [x] **Step 3: Perbarui catatan (skrip pencatat berkas; jangkar tepat sekali)**

`data-asal/bahan.json` (INDO-ALPR: ukuran bahan latih akhir); `CLAUDE.md` §7 (bahan baca huruf yang berlaku:
`latih-koreksi/pembagian-koreksi.json`, atau `kembar-akhir/pembagian.json` bila Task 5 Step 2 mengeluarkan sesuatu);
`OPEN-QUESTIONS.md` bagian B (paragraf baru); `ROADMAP.md` (butir dicentang dengan angka; butir baru
`- [ ] Rencana 8 Fase 0A ditulis ← di sini sekarang`; baris status; changelog); rencana ini (kotak dicentang, catatan
pelaksanaan).

- [x] **Step 4: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 101` dan `140 passed`, keduanya `EXIT=0`. `git status --short`: hanya `bukti/` dan berkas catatan.

- [x] **Step 5: Laporkan ke owner**

Ringkasan singkat dalam bahasa sehari-hari dan **satu** pertanyaan untuk langkah berikutnya (Rencana 8: mesin baca huruf
buatan sendiri yang pertama).

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K24:** bahan latih dibersihkan dengan cara K22 → Task 3–5; kebocoran sesudah label latih dibetulkan → aturan
  dua arah di Task 1 dan pemeriksaan ulang di Task 5 Step 2. **Di luar K24 tetapi searah tujuannya:** kendaraan kembar dari
  gambar (Task 2), tanpa waktu owner, diambil dari pengukuran sebelum rencana ini ditulis.
- **Set uji tidak berubah:** tak satu langkah pun menyentuh sisi uji; Task 2 dan Task 5 hanya mengeluarkan dari sisi latih.
- **Data pribadi:** owner menjawab dengan nomor baris; tiap alat baru punya uji "layar tanpa nomor plat"; `kembar_lintas.py`
  membisukan log OpenCV sendiri.
- **Tanpa isian kosong pada kode:** semua kode alat dan uji tertulis lengkap, atau ditulis sebagai penggantian baris yang
  tepat. Isian bersudut hanya pada angka hasil dan nomor baris jawaban owner.
- **Angka gerbang:** Node tetap 101. Lab 128 → 136 → 140.

## Catatan pelaksanaan (14 Okt 2026)

Dijalankan atas lampu hijau owner ("A"). Hasil dan batasnya di
[`../bukti/2026-10-14-label-bahan-latih.md`](../bukti/2026-10-14-label-bahan-latih.md). Yang berbeda dari tulisan di atas:

- **Task 2 Step 5:** 177 dan 27 seperti yang diharapkan; plat latih yang dikeluarkan 22 (sebagian plat punya lebih dari
  satu pasangan).
- **Task 4:** 75 label latih dicurigai (perkiraan di atas 90-an).
- **Jawaban owner:** 11 baris disebut tanpa keterangan (49, 51, 55, 56, 59, 60, 62, 63, 65, 68, 73); dijalankan sebagai
  `--keduanya-salah` (dikeluarkan) supaya tidak menebak. Owner juga menyebut "selain itu B benar", jadi baris yang tidak
  disebut diperlakukan sebagai B benar, kebalikan dari bawaan lembar. **Sesudahnya owner menjelaskan ke-11 baris itu "A benar"**;
  `nilai_ulang.py` dijalankan ulang dengan `--keduanya-salah 6,19,37,41` saja. Hasil akhir: 4 dikeluarkan, bahan latih 2.824 plat.
- **Task 5 Step 1:** layar penilai ulang mencetak "plat latih" dan "kedatangan uji" untuk hitungan sisi latih; diperbaiki
  dengan uji lebih dulu (`test_layar_menyebut_sisi_yang_dibetulkan`). Gerbang lab akhir 141 (tertulis 140).
- **Satu jalan ulang** sempat dipotong dengan `Select-Object -First 1` (pola yang dilarang); diperiksa tanpa sisa container,
  lalu diulang penuh dengan kode keluar 0.
- **Task 6 Step 1:** daftar larangan 9.739; kontrol positif menemukan 9.604.
