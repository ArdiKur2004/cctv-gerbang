# Fase 0A, Rencana 4: Bahan berizin jual, diambil dengan aman — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Dua dataset plat Indonesia yang izinnya membolehkan produk dijual tersimpan di laptop ini, terkunci,
terbukti sama dengan terbitan aslinya, dan tercatat di daftar bahan, tanpa satu pun nomor plat terbaca oleh agen.
Sekalian menutup celah "berkas ada belum tentu utuh" yang ditemukan pada K20.

**Architecture:** Satu pintu baru untuk mengunduh berkas besar (`tools\ambil-berkas.ps1`): container berjaringan
yang hanya melihat pengunduhnya sendiri dan satu folder keluaran, hanya ke host yang didaftar, dan hanya berkas yang
tercatat di kunci. Arsip hasil unduhan dibuka di lab tanpa jaringan oleh pembuka yang menolak arsip berbahaya dan
tidak pernah mencetak nama berkas. Untuk INDO-ALPR, tiap berkas hasil buka dicocokkan dengan SHA-256 yang dicatat
penerbitnya sendiri.

**Tech Stack:** PowerShell 5.1 · Node 24 (`node:test`) · Python 3.12 dengan PyAV 19, OpenCV 4.14, dan pytest 9.1
**yang sudah ada di image lab** (diperiksa 13 Okt: sertifikat sistem 150 buah termuat, jadi `urllib` bawaan bisa
https) · `tools\lab.ps1`. Tidak ada yang dipasang.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md)
bagian 8.1 langkah 4 (sebagian) dan bagian 8.6. Keputusan K14, K15, K19 di [`../SEED.md`](../SEED.md) §3. Temuan
"berkas `.mp4` yang ada belum tentu utuh" di [`../ROADMAP.md`](../ROADMAP.md), "Temuan di luar lingkup".

---

## Penyesuaian pembagian rencana

Rencana 3 menulis bahwa Rencana 4 memuat lima hal. Dua di antaranya (pelabel otomatis dan set uji pertama) tidak bisa
ditulis lengkap sebelum isi dataset diketahui, jadi dipecah lagi. Ini pemecahan ketiga; alasannya sama dengan yang
dulu: rencana yang menebak isi bahan yang belum dilihat akan salah.

| Rencana | Isi | Status |
|---|---|---|
| 1 | Bengkel | Selesai 13 Okt |
| 2 | Vonis izin komponen; peraturan plat | Selesai 13 Okt |
| 3 | Perbaikan pemindai; pemilahan video (K19) | Selesai 13 Okt |
| **4 (dokumen ini)** | Pemeriksa keutuhan video; pintu unduh berkas; pembuka arsip; dua dataset berizin jual | Ditulis |
| 5 | Ikhtisar isi dataset tanpa plat terbaca; pelabel otomatis di laptop; lembar contoh untuk owner; set uji pertama | Ditulis saat Rencana 4 selesai |
| 6 | Pembuat plat buatan komputer; pembanding; mesin belajar pertama; taksiran kecepatan; laporan ke `bukti/` | Ditulis saat Rencana 5 selesai dan P13 dijawab |

## Yang sudah dibaca dari sumbernya (13 Okt 2026), dan yang mengoreksi catatan lama

Catatan riset [`../docs/riset/2026-10-13-catatan-bahan-data-plat.md`](../docs/riset/2026-10-13-catatan-bahan-data-plat.md)
menulis tentang INDO-ALPR: "Format anotasi … tidak tertulis. Daftar berkas kosong di halaman." Dibaca langsung dari
API publik Mendeley Data, tanpa mengunduh satu gambar pun:

| Hal | Yang terbaca |
|---|---|
| Jati diri | `j3256db3fz` versi 1, DOI `10.17632/j3256db3fz.1`, terbit 7 Sep 2023, Institut Teknologi Sepuluh Nopember |
| Isi | 67.922 berkas, 7.390 MB. Folder `original/train` 4.712 dan `original/test` 1.462 (jumlahnya 6.174, cocok dengan keterangan dataset). Sepuluh folder `augmentation/…` memuat 61.747 gambar (semula tertulis 61.745, dari jumlah per folder di kepala jawaban API; catatan lengkap penerbit yang diambil 14 Okt menulis 61.747) **olahan** dari yang asli: bukan bahan baru, tidak dipakai |
| Bentuk label | Tidak ada berkas anotasi. Nama berkas berbentuk `A 9999 AAA_9999.png`: **nomor platnya ada di nama berkas**. Maka nama berkas dataset ini tidak pernah dicetak atau disalin ke repo |
| Ukuran gambar | Nilai tengah sekitar 55 KB, terkecil 1,2 KB: kemungkinan besar potongan plat, bukan foto adegan. Baru pasti sesudah dilihat ukurannya (Rencana 5) |
| SHA-256 | Catatan dataset memuat SHA-256 **tiap** berkas. Ini dipakai untuk membuktikan hasil unduhan sama dengan terbitan |
| Cara ambil | Daftar per folder dipotong di 1.000 butir dan tidak bisa dilanjutkan, jadi diambil arsip utuhnya ("Download All"), yang dialihkan ke `prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com` |
| ID folder | `original/train` = `44fd8100-281c-4dea-9ba8-e6469d256ec3` · `original/test` = `b6eab52b-d6d1-43b9-a073-4c13afe0fe19` |

Dataset pencahayaan (`salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset`), dibaca lewat `gh api` pada commit
`e5bfbd8af64541d032c9022eef588e75d9786c6a`: 561 gambar jpg dengan 561 berkas label kotak (393 latih, 84 validasi, 84
uji), 143 MB. Izin "CC BY 4.0" tertulis di tiga tempat (`README.md`, `README.dataset.txt`, `data.yaml`); **tidak ada
berkas LICENSE**. Ada satu buku catatan `a.ipynb`, yang tidak dibuka dan tidak dijalankan.

## Sesudah K21 (14 Okt 2026)

Owner memutuskan K21 sebelum rencana ini dijalankan. Akibatnya di sini kecil: kedua dataset berizin CC BY 4.0, jadi
vonisnya tidak bergantung pada K21. Yang berubah hanya kalimat tentang data pribadi (B9): kini bersandar pada pernyataan
owner bahwa pihak hukum sudah dimintai nasihat. Satu pengaman ditambahkan sebelum dijalankan: pembuka arsip (Task 3)
dan pencocok SHA-256 (Task 4) menangkap galat baca-tulis sendiri, karena pesan galat bawaan Python memuat jalur
berkas, dan pada INDO-ALPR jalur itu memuat nomor plat. Angka gerbang lab ikut naik satu di tiap task itu.

## Aturan eksekusi untuk semua task

- **Agen tidak membuka satu pun gambar dataset, dan tidak mencetak nama berkas INDO-ALPR** (`CLAUDE.md` §4, K19).
  Semua alat di rencana ini hanya mengeluarkan hitungan.
- **Arsip dari luar tidak pernah dibuka di luar lab**, dan tidak dibuka sebelum SHA-256-nya dikunci.
- **Berhasil atau tidaknya unduhan dinilai dari berkasnya**, bukan dari kode keluar.
- **Satu suite uji pada satu waktu.** Tanpa `| tail` atau `| head` pada perintah uji.
- **Dua gerbang uji:** `npm test` (Node, di host) dan `npm run test:lab` (Python, di lab tanpa jaringan). Kode 3 dari
  gerbang lab berarti bengkel sedang dipakai job lain; itu bukan uji merah.
- **Perintah yang memuat jalur `/kerja/...` dijalankan lewat PowerShell.** Git Bash mengubah jalur itu menjadi jalur
  Windows sebelum sampai ke lab (terjadi 13 Okt). `npm run test:lab` aman dari Git Bash.
- **vision-seed hanya dibaca.** Jangan `cd` ke sana; pakai jalur mutlak.
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri baris
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Perintah lain dijalankan dari akar repo `D:\Projects\super-team-v1\cctvgerbang-seed` lewat Git Bash.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/lab/periksa_utuh.py` (baru) | Membuka tiap video dan mencatat yang utuh | 1 |
| `tools/lab/uji/test_periksa_utuh.py` (baru) | Uji: video rusak atau terpotong tertangkap | 1 |
| `tools/manifes-video.mjs` (ubah) | Video baru hanya dicatat bila tercatat utuh | 1 |
| `tools/uji/manifes-video.test.mjs` (ubah) | Uji rantai untuk aturan itu | 1 |
| `tools/ambil/ambil_berkas.py` (baru) | Pengunduh satu berkas: https, daftar host, `.part`, SHA-256 | 2 |
| `tools/lab/uji/test_ambil_berkas.py` (baru) | Uji pengunduh dengan jaringan tiruan | 2 |
| `tools/ambil-berkas.ps1` (baru) | Pintu: container berjaringan yang hanya melihat pengunduh dan satu folder | 2 |
| `tools/uji/ambil-berkas.test.mjs` (baru) | Uji janji pintu dan uji rantai dengan docker tiruan | 2 |
| `tools/lab/buka_arsip.py` (baru) | Membuka zip dengan aman, tanpa mencetak nama berkas | 3 |
| `tools/lab/uji/test_buka_arsip.py` (baru) | Uji: arsip berbahaya ditolak sebelum ada yang ditulis | 3 |
| `tools/lab/catatan_mendeley.py` (baru) | Membaca izin dari catatan penerbit; mencocokkan SHA-256 tiap berkas | 4 |
| `tools/lab/uji/test_catatan_mendeley.py` (baru) | Uji pencocokan | 4 |
| `tools/vendor.lock.json` (ubah) | Daftar `berkas`: alamat, batas ukuran, SHA-256 | 5, 6 |
| `docs/lisensi/dataset__plat-lighting/IZIN.md`, `docs/lisensi/dataset__indo-alpr/IZIN.md` (baru) | Kutipan izin apa adanya | 5, 6 |
| `data-asal/bahan.json`, `docs/VONIS-LISENSI.md` (ubah) | Dua bahan baru beserta vonisnya | 7 |
| `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Pintu ketiga dicatat; hasil dicatat | 7 |

---

### Task 1: Video yang rusak tidak bisa lagi tercatat sebagai bahan

Pada K20 satu unduhan meninggalkan berkas `.mp4` yang tidak bisa dibuka, dan pencatat menandainya utuh karena
berkasnya ada. Pemeriksa sekali pakai yang menangkapnya (`data/alat-sementara/periksa_utuh.py`) dijadikan alat beruji,
dan `tools/manifes-video.mjs` menolak video baru yang belum lulus pemeriksaan itu.

**Files:**
- Create: `tools/lab/periksa_utuh.py`
- Create: `tools/lab/uji/test_periksa_utuh.py`
- Modify: `tools/manifes-video.mjs`
- Modify: `tools/uji/manifes-video.test.mjs`
- Modify: `tools/ambil-video.ps1` (hanya komentar kepala)

- [ ] **Step 1: Tulis uji pemeriksa keutuhan**

Buat `tools/lab/uji/test_periksa_utuh.py`:

```python
"""Uji tools/lab/periksa_utuh.py: video yang ada berkasnya tetapi rusak atau terpotong harus tertangkap (temuan K20)."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import periksa_utuh as pu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "periksa_utuh.py"


def tulis_video(jalur, detik=4):
    """Video uji kecil, 10 gambar per detik, beserta berkas .info.json yang mencatat lamanya."""
    tulis = cv2.VideoWriter(str(jalur), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for i in range(detik * 10):
        tulis.write(np.full((240, 320, 3), i * 6 % 256, np.uint8))
    tulis.release()
    jalur.with_name(jalur.stem + ".info.json").write_text(json.dumps({"duration": detik}))
    return jalur


def test_video_utuh_lulus(tmp_path):
    baik, keterangan = pu.periksa(tulis_video(tmp_path / "youtube-utuh.mp4"))

    assert baik, keterangan


def test_video_terpotong_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-potong.mp4")
    isi = jalur.read_bytes()
    jalur.write_bytes(isi[: len(isi) // 2])

    baik, keterangan = pu.periksa(jalur)

    assert not baik, keterangan


def test_berkas_bernama_mp4_tetapi_bukan_video_tertangkap(tmp_path):
    # Inilah yang terjadi 13 Okt: berkasnya ada, namanya benar, isinya tidak bisa dibuka.
    jalur = tmp_path / "youtube-sampah.mp4"
    jalur.write_bytes(b"bukan video" * 1000)
    jalur.with_name("youtube-sampah.info.json").write_text(json.dumps({"duration": 4}))

    baik, keterangan = pu.periksa(jalur)

    assert not baik
    assert "tidak bisa dibuka" in keterangan


def test_lama_yang_jauh_dari_catatan_sumber_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-pendek.mp4")
    jalur.with_name("youtube-pendek.info.json").write_text(json.dumps({"duration": 60}))

    baik, keterangan = pu.periksa(jalur)

    assert not baik
    assert "lama berkas" in keterangan


def test_video_tanpa_catatan_sumber_tertangkap(tmp_path):
    jalur = tulis_video(tmp_path / "youtube-yatim.mp4")
    jalur.with_name("youtube-yatim.info.json").unlink()

    baik, keterangan = pu.periksa(jalur)

    assert not baik
    assert ".info.json" in keterangan


def test_baris_perintah_menulis_catatan_dan_keluar_1_bila_ada_yang_rusak(tmp_path):
    # Rantainya: baris perintah -> tiap video diperiksa -> berkas catatan yang nanti dibaca tools/manifes-video.mjs.
    folder = tmp_path / "video"
    folder.mkdir()
    utuh = tulis_video(folder / "youtube-utuh.mp4")
    rusak = tulis_video(folder / "youtube-rusak.mp4")
    rusak.write_bytes(rusak.read_bytes()[:2000])
    catatan = tmp_path / "keluar" / "video-utuh.json"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(catatan)], capture_output=True, text=True)

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    isi = json.loads(catatan.read_text())
    assert isi["utuh"] == {"youtube-utuh.mp4": utuh.stat().st_size}
    assert list(isi["rusak"]) == ["youtube-rusak.mp4"]
    assert "RUSAK youtube-rusak.mp4" in hasil.stdout


def test_baris_perintah_keluar_0_bila_semua_utuh(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis_video(folder / "youtube-utuh.mp4")
    catatan = tmp_path / "video-utuh.json"

    hasil = subprocess.run([sys.executable, str(SKRIP), str(folder), str(catatan)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "1 utuh, 0 bermasalah, dari 1 video" in hasil.stdout
```

- [ ] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat saat mengumpulkan uji, `ModuleNotFoundError: No module named 'periksa_utuh'`, dan `EXIT` bukan 0.
pytest berhenti di tahap mengumpulkan, jadi sembilan uji lama tidak dijalankan pada putaran ini; itu wajar. Yang tidak
wajar adalah galat lain selain modul yang belum ada.

- [ ] **Step 3: Tulis pemeriksanya**

Buat `tools/lab/periksa_utuh.py`:

```python
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
    """Mengembalikan (utuh, keterangan) untuk satu video."""
    jalur = Path(jalur)
    try:
        catat = json.loads(jalur.with_name(jalur.stem + ".info.json").read_text(encoding="utf-8")).get("duration")
    except (OSError, ValueError, AttributeError):
        return False, "berkas .info.json tidak ada atau tidak terbaca"
    if not isinstance(catat, (int, float)) or catat <= 0:
        return False, "berkas .info.json tidak mencatat lama video"
    try:
        with av.open(str(jalur)) as wadah:
            if not wadah.streams.video:
                return False, "tidak punya aliran gambar"
            lama = (wadah.duration or 0) / 1e6
            wadah.seek(int(lama * DEKAT_AKHIR * 1e6))
            akhir = next(wadah.decode(video=0), None) is not None
    except Exception as galat:  # berkas rusak, terpotong, atau bukan video
        return False, f"tidak bisa dibuka ({type(galat).__name__})"
    if abs(lama - catat) > max(SELISIH_DETIK, SELISIH_BAGIAN * catat):
        return False, f"lama berkas {lama:.1f} detik, catatan sumber {catat} detik"
    if not akhir:
        return False, "gambar di dekat akhir tidak terbaca"
    return True, f"{lama:.1f} detik"


def utama(folder, catatan):
    video = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in AKHIRAN_VIDEO)
    utuh, rusak = {}, {}
    for jalur in video:
        baik, keterangan = periksa(jalur)
        if baik:
            utuh[jalur.name] = jalur.stat().st_size
        else:
            rusak[jalur.name] = keterangan
            print(f"RUSAK {jalur.name}: {keterangan}")
    catatan = Path(catatan)
    catatan.parent.mkdir(parents=True, exist_ok=True)
    waktu = datetime.now(timezone.utc).isoformat(timespec="seconds")
    catatan.write_text(json.dumps({"diperiksa": waktu, "utuh": utuh, "rusak": rusak}, indent=2))
    print(f"{len(utuh)} utuh, {len(rusak)} bermasalah, dari {len(video)} video")
    return 1 if rusak else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Pakai: python periksa_utuh.py <folder-video> <berkas-catatan.json>")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2]))
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `16 passed` dan `EXIT=0` (9 lama + 7 baru).

- [ ] **Step 5: Tulis uji rantai di sisi manifes**

Di `tools/uji/manifes-video.test.mjs`, ganti fungsi `siapkan` dan `jalankan` (baris 17 sampai 26) dengan:

```js
const jalurUtuh = (folder) => path.join(folder, '..', `${path.basename(folder)}-utuh.json`);

// Catatan keutuhan seperti yang ditulis tools/lab/periksa_utuh.py: nama video -> ukurannya dalam byte.
function catatUtuh(folder, ubah = (daftar) => daftar) {
  const daftar = Object.fromEntries(fs.readdirSync(folder).filter((n) => n.endsWith('.mp4'))
    .map((n) => [n, fs.statSync(path.join(folder, n)).size]));
  fs.writeFileSync(jalurUtuh(folder), JSON.stringify({ utuh: ubah(daftar), rusak: {} }));
}

function siapkan(berkas) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-riset-'));
  for (const [nama, isi] of Object.entries(berkas)) fs.writeFileSync(path.join(folder, nama), typeof isi === 'string' ? isi : JSON.stringify(isi));
  catatUtuh(folder);
  return { folder, manifes: path.join(folder, '..', `${path.basename(folder)}-manifes.json`) };
}

function jalankan(folder, manifes) {
  const r = spawnSync('node', [SKRIP, folder, manifes, jalurUtuh(folder)], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}
```

Di uji `'isian tangan (kategori, isi) bertahan saat manifes dibuat ulang'`, sesudah baris yang menulis
`youtube-baru.info.json` dan sebelum `const r = jalankan(folder, manifes);`, tambahkan satu baris:

```js
  catatUtuh(folder);
```

Lalu tambahkan empat uji ini di akhir berkas:

```js
test('video baru yang tidak tercatat utuh ditolak: manifes tidak ditulis (kode 1)', () => {
  // Temuan K20: satu unduhan meninggalkan .mp4 yang tak bisa dibuka, dan berkas itu nyaris tercatat sebagai bahan.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  catatUtuh(folder, () => ({}));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /belum tercatat utuh/);
  assert.ok(!fs.existsSync(manifes));
});

test('video baru yang ukurannya berbeda dari catatan keutuhan ditolak (kode 1)', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  catatUtuh(folder, (daftar) => ({ 'youtube-abc123.mp4': daftar['youtube-abc123.mp4'] + 1 }));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /belum tercatat utuh/);
});

test('tanpa berkas catatan keutuhan sama sekali, video baru ditolak: gagal tertutup', () => {
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  fs.rmSync(jalurUtuh(folder));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 1, r.keluar);
  assert.ok(!fs.existsSync(manifes));
});

test('video yang sudah tercatat di manifes tidak menuntut catatan keutuhan lagi', () => {
  // Yang sudah tercatat dijaga SHA-256-nya; catatan keutuhan hanya pintu masuk bagi video baru.
  const { folder, manifes } = siapkan({ 'youtube-abc123.mp4': 'isi-video', 'youtube-abc123.info.json': INFO });
  assert.equal(jalankan(folder, manifes).kode, 0);
  fs.rmSync(jalurUtuh(folder));

  const r = jalankan(folder, manifes);

  assert.equal(r.kode, 0, r.keluar);
});
```

- [ ] **Step 6: Jalankan, pastikan merah karena aturannya belum ada**

Run: `node --test tools/uji/manifes-video.test.mjs; echo "EXIT=$?"`
Expected: `EXIT=1`. Tiga uji baru yang pertama gagal (kode 0 padahal diharapkan 1). Uji keempat dan semua uji lama
lulus.

- [ ] **Step 7: Pasang aturannya di manifes**

Di `tools/manifes-video.mjs`:

Ganti baris pakai di kepala berkas:

```js
// Pakai:  node tools/manifes-video.mjs [folder-video] [berkas-manifes]
```

menjadi:

```js
// Video BARU hanya dicatat bila lulus tools/lab/periksa_utuh.py (temuan K20: berkas yang ada belum tentu utuh).
// Urutannya: unduh -> periksa_utuh.py di lab -> alat ini.
//
// Pakai:  node tools/manifes-video.mjs [folder-video] [berkas-manifes] [berkas-catatan-utuh]
```

Sesudah baris `const berkasManifes = ...`, tambahkan:

```js
const berkasUtuh = process.argv[4] ?? path.join(AKAR, 'data', 'keluaran', 'video-utuh.json');
```

Sesudah baris `const lamaPerBerkas = ...`, tambahkan:

```js
// Catatan keutuhan dari tools/lab/periksa_utuh.py. Tanpa catatan yang terbaca, tidak ada video baru yang diterima.
let utuh = {};
try { utuh = JSON.parse(fs.readFileSync(berkasUtuh, 'utf8')).utuh ?? {}; } catch { /* gagal tertutup di bawah */ }
```

Di dalam putaran, ganti tiga baris ini:

```js
  const info = JSON.parse(fs.readFileSync(berkasInfo, 'utf8'));
  const hash = await sha256(path.join(folder, nama));
  const dulu = lamaPerBerkas.get(nama);
```

menjadi:

```js
  const info = JSON.parse(fs.readFileSync(berkasInfo, 'utf8'));
  const dulu = lamaPerBerkas.get(nama);
  if (!dulu && utuh[nama] !== fs.statSync(path.join(folder, nama)).size) {
    galat.push(`${nama}: belum tercatat utuh di ${path.basename(berkasUtuh)}. Jalankan tools/lab/periksa_utuh.py lebih dulu`);
    continue;
  }
  const hash = await sha256(path.join(folder, nama));
```

- [ ] **Step 8: Jalankan kedua gerbang**

Run: `npm test; echo "EXIT=$?"`
Expected: `tests 79`, `pass 79`, `fail 0`, `EXIT=0` (75 lama + 4 baru).

- [ ] **Step 9: Jalankan pada 100 video sungguhan**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/periksa_utuh.py /kerja/data/video/riset /kerja/data/keluaran/video-utuh.json; "EXIT=$LASTEXITCODE"`
Expected: `100 utuh, 0 bermasalah, dari 100 video` dan `EXIT=0`.

Run: `node tools/manifes-video.mjs; echo "EXIT=$?"; git status --short data-asal/`
Expected: `100 video dicatat di ...` dan `EXIT=0`; `git status` kosong (manifes tidak berubah).

- [ ] **Step 10: Perbarui komentar pintu video dan buang pemeriksa sekali pakai**

Di kepala `tools/ambil-video.ps1`, ganti dua baris:

```
    BELUM tertangani: pengunduh yang menolak sebelum mulai mengunduh (tanpa berkas .part) tetap keluar 0. Pemanggil
    tetap wajib memeriksa bahwa berkas jadinya ada.
```

menjadi:

```
    BELUM tertangani di pintu ini: pengunduh yang menolak sebelum mulai mengunduh tetap keluar 0, dan pengunduh yang
    gagal bisa meninggalkan berkas .mp4 yang tidak bisa dibuka (terjadi 13 Okt). Karena itu sesudah mengunduh WAJIB:
    tools\lab.ps1 python /kerja/tools/lab/periksa_utuh.py ... ; tools\manifes-video.mjs menolak video baru tanpa itu.
```

Run: `ls data/alat-sementara/`
Expected: hanya `periksa_utuh.py`. Bila isinya memang hanya itu:

Run: `rm data/alat-sementara/periksa_utuh.py && rmdir data/alat-sementara`

- [ ] **Step 11: Commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu). Expected: `pass 79` dan
`16 passed`, keduanya `EXIT=0`.

```bash
git add tools/lab/periksa_utuh.py tools/lab/uji/test_periksa_utuh.py tools/manifes-video.mjs tools/uji/manifes-video.test.mjs tools/ambil-video.ps1
git commit -q -F - <<'EOF'
Video yang rusak tidak bisa lagi tercatat sebagai bahan

Alasan: pada K20 satu unduhan meninggalkan berkas .mp4 yang tidak bisa
dibuka, dan pencatat menandainya utuh karena berkasnya ada. Manifes pun
akan mencatatnya tanpa keberatan.

Pemeriksa sekali pakai yang menangkapnya dijadikan alat beruji
(tools/lab/periksa_utuh.py), dan manifes sekarang menolak video baru yang
belum lulus pemeriksaan itu. Jadi rantainya yang dijaga, bukan hanya alatnya.

Uji ditulis lebih dulu dan terlihat merah. Gerbang: Node 75 -> 79, lab
9 -> 16. Pada 100 video sungguhan: 100 utuh.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Pintu unduh berkas

**Files:**
- Create: `tools/ambil/ambil_berkas.py`
- Create: `tools/lab/uji/test_ambil_berkas.py`
- Create: `tools/ambil-berkas.ps1`
- Create: `tools/uji/ambil-berkas.test.mjs`

- [ ] **Step 1: Tulis uji pengunduh (jaringan diganti tiruan)**

Buat `tools/lab/uji/test_ambil_berkas.py`:

```python
"""Uji tools/ambil/ambil_berkas.py. Lab tidak punya jaringan, jadi jaringan diganti peta alamat -> jawaban."""
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ambil"))
import ambil_berkas as ab  # noqa: E402

SKRIP = Path(__file__).resolve().parents[2] / "ambil" / "ambil_berkas.py"
HOST = {"data.contoh.test", "simpan.contoh.test"}
ISI = b"isi arsip " * 1000
SIDIK = hashlib.sha256(ISI).hexdigest()
AWAL = "https://data.contoh.test/a.zip"
SIMPAN = "https://simpan.contoh.test/a.zip?tanda=RAHASIA"
BESAR = 10**9


def jaringan(jawaban):
    """Pengganti jaringan: (fungsi minta, daftar alamat yang benar-benar diminta)."""
    diminta = []

    def minta(alamat):
        diminta.append(alamat)
        status, kepala, badan = jawaban[alamat]
        return status, kepala, io.BytesIO(badan)

    return minta, diminta


def utuh(panjang=None):
    return 200, {"Content-Length": str(len(ISI) if panjang is None else panjang)}, ISI


def test_berkas_tersimpan_dengan_nama_jadinya_dan_tercatat_sidiknya(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    asal = ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert (tmp_path / "a.zip").read_bytes() == ISI
    assert not (tmp_path / "a.zip.part").exists()
    assert asal["sha256"] == SIDIK and asal["byte"] == len(ISI) and asal["host_akhir"] == "data.contoh.test"


def test_pengalihan_ke_host_yang_didaftar_diikuti(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": SIMPAN}, b""), SIMPAN: utuh()})

    asal = ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL, SIMPAN]
    assert asal["host_akhir"] == "simpan.contoh.test"
    assert "RAHASIA" not in json.dumps(asal), "alamat hasil pengalihan memuat tanda tangan sementara; jangan dicatat"


def test_pengalihan_ke_host_di_luar_daftar_ditolak_tanpa_menghubunginya(tmp_path):
    jahat = "https://jahat.contoh.test/a.zip?tanda=RAHASIA"
    minta, diminta = jaringan({AWAL: (302, {"Location": jahat}, b""), jahat: utuh()})

    with pytest.raises(ab.Ditolak) as galat:
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL]
    assert "jahat.contoh.test" in str(galat.value) and "RAHASIA" not in str(galat.value)
    assert list(tmp_path.iterdir()) == []


def test_pengalihan_ke_alamat_bukan_https_ditolak(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": "http://simpan.contoh.test/a.zip"}, b"")})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == [AWAL]


def test_alamat_awal_bukan_https_ditolak_sebelum_ada_permintaan(tmp_path):
    minta, diminta = jaringan({})

    with pytest.raises(ab.Ditolak):
        ab.unduh("http://data.contoh.test/a.zip", tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert diminta == []


def test_sidik_yang_tidak_cocok_dengan_kunci_tidak_menghasilkan_berkas_jadi(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    with pytest.raises(ab.TakCocok):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, sha256="0" * 64, minta=minta)

    assert not (tmp_path / "a.zip").exists()
    assert (tmp_path / "a.zip.part").exists(), "sisa .part adalah tanda bagi pintu bahwa unduhan tidak sah"


def test_unduhan_yang_terpotong_tidak_menghasilkan_berkas_jadi(tmp_path):
    minta, _ = jaringan({AWAL: utuh(panjang=len(ISI) + 500)})

    with pytest.raises(ab.Ditolak) as galat:
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert "terpotong" in str(galat.value)
    assert not (tmp_path / "a.zip").exists()


def test_berkas_yang_mengaku_lebih_besar_dari_batas_ditolak_sebelum_ditulis(tmp_path):
    minta, _ = jaringan({AWAL: utuh()})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, 100, minta=minta)

    assert list(tmp_path.iterdir()) == []


def test_berkas_tanpa_keterangan_ukuran_dihentikan_di_batas(tmp_path):
    minta, _ = jaringan({AWAL: (200, {}, ISI)})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, 100, minta=minta)

    assert not (tmp_path / "a.zip").exists()


def test_pengalihan_yang_berputar_dihentikan(tmp_path):
    minta, diminta = jaringan({AWAL: (302, {"Location": AWAL}, b"")})

    with pytest.raises(ab.Ditolak):
        ab.unduh(AWAL, tmp_path / "a.zip", HOST, BESAR, minta=minta)

    assert len(diminta) == ab.MAKS_ALIH + 1


def baris_perintah(tmp_path, *tambahan, alamat=AWAL, nama="a.zip"):
    perintah = [sys.executable, str(SKRIP), "--alamat", alamat, "--keluar", str(tmp_path), "--nama", nama,
                "--maks-byte", str(BESAR), "--host", "data.contoh.test", *tambahan]
    return subprocess.run(perintah, capture_output=True, text=True)


def test_baris_perintah_berkas_yang_sudah_ada_dan_cocok_tidak_diunduh_lagi(tmp_path):
    # Rantainya: pintu -> baris perintah -> berkas. Tidak ada jaringan di lab, jadi kode 0 di sini berarti tak ada permintaan.
    (tmp_path / "a.zip").write_bytes(ISI)

    hasil = baris_perintah(tmp_path, "--sha256", SIDIK)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert "SUDAH ADA" in hasil.stdout and SIDIK in hasil.stdout


def test_baris_perintah_berkas_yang_sudah_ada_tetapi_sidiknya_beda_ditolak_dengan_kode_7(tmp_path):
    (tmp_path / "a.zip").write_bytes(ISI)

    hasil = baris_perintah(tmp_path, "--sha256", "0" * 64)

    assert hasil.returncode == 7, hasil.stdout + hasil.stderr
    assert "TIDAK COCOK" in hasil.stdout


def test_baris_perintah_alamat_bukan_https_ditolak_dengan_kode_1(tmp_path):
    hasil = baris_perintah(tmp_path, alamat="http://data.contoh.test/a.zip")

    assert hasil.returncode == 1, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout


def test_baris_perintah_nama_berkas_yang_memuat_folder_ditolak_dengan_kode_2(tmp_path):
    hasil = baris_perintah(tmp_path, nama="../luar.zip")

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
```

- [ ] **Step 2: Jalankan, pastikan merah karena pengunduhnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat saat mengumpulkan uji, `ModuleNotFoundError: No module named 'ambil_berkas'`, `EXIT` bukan 0.

- [ ] **Step 3: Tulis pengunduhnya**

Buat `tools/ambil/ambil_berkas.py`:

```python
"""Pengunduh satu berkas untuk pintu tools\\ambil-berkas.ps1 (arsip dan catatan dataset, spec bagian 8.6).

Hanya pustaka bawaan Python. Dijalankan di container berjaringan yang hanya melihat folder ini (read-only) dan satu
folder keluaran. Janjinya:
- hanya https dan hanya host yang disebut pintunya; tiap pengalihan diperiksa ulang, tidak diikuti buta;
- berkas ditulis sebagai <nama>.part dan baru diberi nama jadinya sesudah ukurannya cocok dan, bila dikunci,
  SHA-256-nya cocok;
- alamat hasil pengalihan tidak pernah dicetak atau dicatat utuh (bisa memuat tanda tangan sementara): hanya host-nya.

Kode keluar: 0 berhasil · 1 ditolak atau gagal · 2 salah pakai · 7 SHA-256 tidak cocok dengan kunci.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

POTONG = 1 << 20
LAPOR_TIAP = 256 << 20
MAKS_ALIH = 5
ALIH = {301, 302, 303, 307, 308}


class Ditolak(Exception):
    """Permintaan yang tidak boleh atau tidak bisa diteruskan."""


class TakCocok(Exception):
    """SHA-256 berkas yang diterima bukan yang dikunci."""


def periksa_alamat(alamat, host_boleh):
    bagian = urllib.parse.urlsplit(alamat)
    host = (bagian.hostname or "").lower()
    if bagian.scheme != "https":
        raise Ditolak(f"hanya https yang boleh (diberi {bagian.scheme or 'tanpa skema'} ke {host})")
    if bagian.username or bagian.password:
        raise Ditolak(f"alamat memuat nama pengguna ({host})")
    if host not in host_boleh:
        raise Ditolak(f"host di luar daftar: {host}")
    return host


class _TanpaAlih(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *argumen, **pilihan):
        return None


def minta(alamat):
    """Satu permintaan GET tanpa mengikuti pengalihan: (status, kepala, badan)."""
    pembuka = urllib.request.build_opener(_TanpaAlih)
    permintaan = urllib.request.Request(alamat, headers={"User-Agent": "cctvgerbang-ambil-berkas/1"})
    try:
        jawab = pembuka.open(permintaan, timeout=60)
        return jawab.status, jawab.headers, jawab
    except urllib.error.HTTPError as galat:
        return galat.code, galat.headers, galat


def sidik_berkas(jalur):
    sidik = hashlib.sha256()
    with open(jalur, "rb") as berkas:
        for potong in iter(lambda: berkas.read(POTONG), b""):
            sidik.update(potong)
    return sidik.hexdigest()


def unduh(alamat, tujuan, host_boleh, maks_byte, sha256="", minta=minta):
    """Mengunduh satu berkas ke `tujuan`. Mengembalikan catatan asal-usulnya; melempar Ditolak atau TakCocok."""
    tujuan = Path(tujuan)
    sementara = tujuan.with_name(tujuan.name + ".part")
    sekarang = alamat
    for _ in range(MAKS_ALIH + 1):
        host = periksa_alamat(sekarang, host_boleh)
        status, kepala, badan = minta(sekarang)
        if status not in ALIH:
            break
        lokasi = kepala.get("Location")
        if not lokasi:
            raise Ditolak(f"pengalihan tanpa tujuan (HTTP {status} dari {host})")
        sekarang = urllib.parse.urljoin(sekarang, lokasi)
    else:
        raise Ditolak(f"lebih dari {MAKS_ALIH} pengalihan")
    if status != 200:
        raise Ditolak(f"HTTP {status} dari {host}")
    janji = kepala.get("Content-Length")
    janji = int(janji) if janji and janji.isdigit() else None
    if janji is not None and janji > maks_byte:
        raise Ditolak(f"berkas {janji} byte, melebihi batas {maks_byte} byte")
    sidik, terima = hashlib.sha256(), 0
    with open(sementara, "wb") as berkas:
        while True:
            potong = badan.read(POTONG)
            if not potong:
                break
            terima += len(potong)
            if terima > maks_byte:
                raise Ditolak(f"melebihi batas {maks_byte} byte")
            sidik.update(potong)
            berkas.write(potong)
            if terima // LAPOR_TIAP != (terima - len(potong)) // LAPOR_TIAP:
                print(f"... {terima >> 20} MB", flush=True)
    if janji is not None and terima != janji:
        raise Ditolak(f"terpotong: diterima {terima} dari {janji} byte")
    hasil = sidik.hexdigest()
    if sha256 and hasil != sha256:
        raise TakCocok(hasil)
    sementara.replace(tujuan)
    return {"alamat": alamat, "host_akhir": host, "byte": terima, "sha256": hasil,
            "diambil": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Mengunduh satu berkas dari host yang diizinkan.")
    urai.add_argument("--alamat", required=True)
    urai.add_argument("--keluar", required=True, help="folder tujuan")
    urai.add_argument("--nama", required=True, help="nama berkas jadi")
    urai.add_argument("--maks-byte", type=int, required=True)
    urai.add_argument("--host", action="append", required=True)
    urai.add_argument("--sha256", default="")
    p = urai.parse_args(argumen)
    if "/" in p.nama or "\\" in p.nama or p.nama.startswith("."):
        print("DITOLAK: nama berkas tidak boleh memuat pemisah folder atau diawali titik")
        return 2
    tujuan = Path(p.keluar) / p.nama
    try:
        if tujuan.exists():
            hasil = sidik_berkas(tujuan)
            if p.sha256 and hasil != p.sha256:
                raise TakCocok(hasil)
            print(f"SUDAH ADA {p.nama}: {tujuan.stat().st_size} byte, SHA256 {hasil}. Tidak ada yang diunduh.")
            return 0
        asal = unduh(p.alamat, tujuan, {h.lower() for h in p.host}, p.maks_byte, p.sha256)
    except TakCocok as galat:
        print(f"SHA-256 TIDAK COCOK: berkas ber-SHA256 {galat}, yang dikunci {p.sha256}. Berkas tidak dipakai.")
        return 7
    except Ditolak as galat:
        print(f"DITOLAK: {galat}")
        return 1
    except OSError as galat:
        print(f"GAGAL: {type(galat).__name__}: {getattr(galat, 'reason', '')}")
        return 1
    tujuan.with_name(tujuan.name + ".asal.json").write_text(json.dumps(asal, indent=2))
    print(f"TERSIMPAN {p.nama}: {asal['byte']} byte, SHA256 {asal['sha256']}, dari {asal['host_akhir']}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `30 passed` dan `EXIT=0` (16 + 14 baru).

- [ ] **Step 5: Tulis uji pintu (janji isolasi dan uji rantai)**

Buat `tools/uji/ambil-berkas.test.mjs`:

```js
// Uji pintu pengambil berkas tools/ambil-berkas.ps1 (arsip dan catatan dataset, spec bagian 8.6).
// Yang dikunci di sini adalah JANJI di sisi host: container hanya melihat pengunduhnya sendiri (read-only) dan SATU
// folder keluaran; hanya berkas yang tercatat di kunci, hanya https, hanya host yang didaftar pintu; dan berhasil
// atau tidaknya dinilai dari berkasnya, bukan dari kode keluar pengunduh.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'ambil-berkas.ps1');
const BUTIR = { nama: 'contoh', url: 'https://codeload.github.com/a/b/zip/abc', berkas: 'contoh.zip', maks_gb: 1, sha256: '' };
const IMAGE = { nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' };
const HOST = ['data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com'];

function kunci(butir = [BUTIR], imageLab = IMAGE) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  const isi = {};
  if (butir) isi.berkas = butir;
  if (imageLab) isi.image_lab = imageLab;
  fs.writeFileSync(berkas, JSON.stringify(isi));
  return berkas;
}

function jalankan(args, env = {}) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', SKRIP, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
    timeout: 60_000,
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

function argumenDocker(butir = BUTIR) {
  const r = jalankan(['-Kering', butir.nama], { VS_KUNCI_VENDOR: kunci([butir]) });
  assert.equal(r.kode, 0, `ambil-berkas.ps1 -Kering gagal: ${r.galat}${r.keluar}`);
  return JSON.parse(r.keluar);
}

const pasangan = (a, kunciArg) => a.flatMap((x, i) => (x === kunciArg ? [a[i + 1]] : []));

test('container hanya melihat folder pengunduh (read-only) dan satu folder keluaran; tanpa repo, bobot, atau GPU', () => {
  const a = argumenDocker();

  const pasang = pasangan(a, '--mount');
  assert.equal(pasang.length, 2, pasang.join(' | '));
  assert.match(pasang[0], /tools\\ambil,target=\/alat,readonly$/);
  assert.match(pasang[1], /data\\unduhan\\contoh,target=\/keluar$/);
  assert.ok(!a.some((x) => /target=\/kerja/.test(x)), 'repo tak boleh terlihat dari dalam container');
  assert.ok(!a.some((x) => /models|vendor/.test(x)) && !a.includes('--gpus'));
  assert.ok(a.includes('--read-only') && a.includes('no-new-privileges'));
  assert.deepEqual(pasangan(a, '--cap-drop'), ['ALL']);
  assert.deepEqual(pasangan(a, '--network'), ['bridge']);
});

test('yang dijalankan hanya pengunduh bawaan repo, dengan alamat, batas ukuran, dan daftar host dari pintunya', () => {
  const a = argumenDocker();

  const i = a.indexOf('/alat/ambil_berkas.py');
  assert.deepEqual(a.slice(i - 2, i + 1), ['python', '-I', '/alat/ambil_berkas.py']);
  assert.deepEqual(pasangan(a, '--alamat'), [BUTIR.url]);
  assert.deepEqual(pasangan(a, '--keluar'), ['/keluar']);
  assert.deepEqual(pasangan(a, '--nama'), ['contoh.zip']);
  assert.deepEqual(pasangan(a, '--maks-byte'), [String(1024 ** 3)]);
  assert.deepEqual(pasangan(a, '--host'), HOST);
  assert.ok(!a.includes('--sha256'), 'butir yang belum dikunci tidak mengirim sha256');
});

test('butir yang sudah dikunci mengirim SHA-256-nya ke pengunduh', () => {
  const a = argumenDocker({ ...BUTIR, sha256: 'a'.repeat(64) });

  assert.deepEqual(pasangan(a, '--sha256'), ['a'.repeat(64)]);
});

const TOLAK = {
  'nama yang tidak tercatat di kunci': [['lain'], [BUTIR]],
  'nama berhuruf besar atau bertitik': [['../Contoh'], [BUTIR]],
  'nama yang tercatat dua kali': [['contoh'], [BUTIR, BUTIR]],
  'kunci tanpa daftar berkas': [['contoh'], null],
  'alamat bukan https': [['contoh'], [{ ...BUTIR, url: 'http://codeload.github.com/a/b/zip/abc' }]],
  'alamat di host yang mirip tetapi di luar daftar': [['contoh'], [{ ...BUTIR, url: 'https://codeload.github.com.jahat.example/a.zip' }]],
  'nama berkas jadi yang memuat folder': [['contoh'], [{ ...BUTIR, berkas: '..\\luar.zip' }]],
  'sha256 yang bukan 64 huruf heksa': [['contoh'], [{ ...BUTIR, sha256: 'abc' }]],
  'batas ukuran nol': [['contoh'], [{ ...BUTIR, maks_gb: 0 }]],
  'batas ukuran di atas plafon pintu': [['contoh'], [{ ...BUTIR, maks_gb: 999 }]],
};
for (const [judul, [args, butir]] of Object.entries(TOLAK)) {
  test(`ditolak sebelum menyentuh docker (kode 2): ${judul}`, () => {
    const r = jalankan(['-Kering', ...args], { VS_KUNCI_VENDOR: kunci(butir) });

    assert.equal(r.kode, 2, r.keluar + r.galat);
    assert.match(r.keluar, /DITOLAK/);
  });
}

function dockerTiruan() {
  // Pengganti docker untuk uji rantai. Menjawab `image inspect` dengan TIRUAN_ID. Pada `run` ia menulis berkas bernama
  // TIRUAN_BERKAS (bila diisi) ke folder yang dipasang sebagai /keluar, lalu keluar dengan TIRUAN_KODE.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    "$pasang = $args | Where-Object { $_ -like 'type=bind,source=*,target=/keluar' }",
    "$keluar = ($pasang -replace '^type=bind,source=', '') -replace ',target=/keluar$', ''",
    "if ($env:TIRUAN_BERKAS) { Set-Content -LiteralPath (Join-Path $keluar $env:TIRUAN_BERKAS) -Value 'x' }",
    '$kode = [int]$env:TIRUAN_KODE',
    'exit $kode',
  ].join('\r\n'));
  return berkas;
}

function ambilDenganTiruan({ berkas = '', kode = '0', butir = BUTIR, image = IMAGE, idTiruan = IMAGE.id } = {}) {
  const dasar = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-unduhan-'));
  const r = jalankan([butir.nama], {
    VS_KUNCI_VENDOR: kunci([butir], image),
    VS_DOCKER: dockerTiruan(),
    VS_KELUAR: dasar,
    TIRUAN_ID: idTiruan,
    TIRUAN_BERKAS: berkas,
    TIRUAN_KODE: kode,
  });
  const folder = path.join(dasar, butir.nama);
  return { ...r, isi: fs.existsSync(folder) ? fs.readdirSync(folder) : null };
}

test('image lab yang ID-nya bukan yang tercatat di kunci tidak dijalankan (kode 6)', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', idTiruan: 'sha256:lain' });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE/);
  assert.deepEqual(r.isi, [], 'pengunduh tidak boleh sempat berjalan');
});

test('kunci tanpa catatan image lab ditolak (kode 6): gagal tertutup', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', image: null });

  assert.equal(r.kode, 6, r.keluar + r.galat);
});

test('unduhan yang meninggalkan berkas .part dilaporkan GAGAL (kode 8) walau pengunduhnya keluar 0', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip.part' });

  assert.deepEqual(r.isi, ['contoh.zip.part'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 8, r.keluar + r.galat);
  assert.match(r.keluar, /UNDUHAN TERPOTONG/);
});

test('pengunduh yang keluar 0 tanpa meninggalkan berkas jadi dilaporkan GAGAL (kode 9)', () => {
  // Cacat sepupu dari pintu video: pengunduh yang menolak sebelum mulai mengunduh keluar 0 tanpa berkas apa pun.
  const r = ambilDenganTiruan({ berkas: '' });

  assert.deepEqual(r.isi, []);
  assert.equal(r.kode, 9, r.keluar + r.galat);
  assert.match(r.keluar, /TAK ADA BERKAS JADI/);
});

test('berkas jadi yang belum dikunci: kode 0, dengan peringatan bahwa ia belum boleh dibuka', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip' });

  assert.deepEqual(r.isi, ['contoh.zip']);
  assert.equal(r.kode, 0, r.keluar + r.galat);
  assert.match(r.keluar, /BELUM DIKUNCI/);
});

test('berkas jadi yang sudah dikunci: kode 0 tanpa peringatan', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip', butir: { ...BUTIR, sha256: 'a'.repeat(64) } });

  assert.equal(r.kode, 0, r.keluar + r.galat);
  assert.doesNotMatch(r.keluar, /BELUM DIKUNCI/);
});

test('kode 7 dari pengunduh (SHA-256 tidak cocok) diteruskan apa adanya', () => {
  const r = ambilDenganTiruan({ berkas: 'contoh.zip.part', kode: '7' });

  assert.equal(r.kode, 7, r.keluar + r.galat);
});
```

- [ ] **Step 6: Jalankan, pastikan merah karena pintunya belum ada**

Run: `node --test tools/uji/ambil-berkas.test.mjs; echo "EXIT=$?"`
Expected: `EXIT=1`, 20 uji gagal, masing-masing karena `powershell` tidak menemukan `ambil-berkas.ps1` (kode keluar
bukan yang diharapkan). Bukan karena salah ketik di berkas uji.

- [ ] **Step 7: Tulis pintunya**

Buat `tools/ambil-berkas.ps1`:

```powershell
<#
.SYNOPSIS
  Mengambil SATU berkas yang tercatat di kunci (arsip atau catatan dataset), di container terisolasi (spec bagian 8.6).

.DESCRIPTION
  Janji pintu ini:
  - Yang diambil hanya butir yang tercatat di daftar "berkas" pada tools\vendor.lock.json. Pintu ini tidak menerima
    alamat dari baris perintah.
  - Hanya https, dan hanya host di $HOST_BOLEH. Menambah host berarti mengubah berkas ini dan ujinya, bukan sekadar
    menambah baris di kunci. Pengalihan diperiksa ulang oleh pengunduhnya.
  - Container hanya melihat DUA hal dari host: tools\ambil (read-only) dan data\unduhan\<nama> (tempat menulis).
    Repo, bobot model, kunci SSH, dan berkas host lain tidak terlihat. Tanpa GPU, root filesystem read-only, semua
    capability dicabut. Jaringannya terbuka (alat ini memang pengunduh), jadi isolasi berkaslah yang menjaga.
  - Image lab yang ID-nya bukan yang tercatat di kunci TIDAK dijalankan (kode 6).
  - Berhasil atau tidaknya dinilai dari BERKASNYA: sisa .part = gagal (kode 8); pengunduh keluar 0 tanpa berkas jadi
    = gagal (kode 9).
  - Butir yang sha256-nya kosong boleh diunduh sekali untuk diukur, tetapi belum boleh dibuka:
    tools\lab\buka_arsip.py menuntut --sha256.

  Berkas hasil unduhan tinggal di data\ (di-gitignore). Dataset plat memuat data pribadi (CLAUDE.md §4).

  Bendera di depan perintah:
    -Kering    cetak argumen docker sebagai JSON tanpa menjalankannya (dipakai tools\uji\ambil-berkas.test.mjs)

  Kode keluar: 0 berhasil · 2 ditolak atau salah pakai · 6 image tak sesuai kunci · 7 SHA-256 tak cocok ·
  8 unduhan terpotong · 9 tak ada berkas jadi · lainnya = kode dari pengunduh.

.EXAMPLE
  powershell -NoProfile -File tools\ambil-berkas.ps1 plat-lighting
#>
$ErrorActionPreference = 'Stop'
$image = 'vision-seed-lab:v1'
$akar = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$alat = Join-Path $PSScriptRoot 'ambil'
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
# Untuk uji rantai (tools\uji\ambil-berkas.test.mjs): program docker dan folder dasar keluaran bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$dasarKeluar = if ($env:VS_KELUAR) { $env:VS_KELUAR } else { Join-Path $akar 'data\unduhan' }
$HOST_BOLEH = @('data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com')
$MAKS_GB = 20
$PAKAI = 'Pakai: tools\ambil-berkas.ps1 [-Kering] <nama>   (nama dari daftar "berkas" di tools\vendor.lock.json)'

$sisa = @($args)
$kering = $false
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Kering') { $kering = $true; $sisa = @($sisa | Select-Object -Skip 1) }
if ($sisa.Count -ne 1) { Write-Host $PAKAI; exit 2 }
$nama = [string]$sisa[0]
if ($nama -cnotmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Host "DITOLAK: nama '$nama' hanya boleh huruf kecil, angka, dan tanda hubung."
    exit 2
}

$butir = @((Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).berkas | Where-Object { $_.nama -eq $nama })
if ($butir.Count -ne 1) { Write-Host "DITOLAK: '$nama' tidak tercatat tepat sekali di daftar berkas pada kunci vendor."; exit 2 }
$b = $butir[0]
$u = $null
if (-not [System.Uri]::TryCreate([string]$b.url, [System.UriKind]::Absolute, [ref]$u) -or $u.Scheme -ne 'https' -or
    ($HOST_BOLEH -notcontains $u.Host.ToLowerInvariant())) {
    Write-Host "DITOLAK: alamat '$nama' harus https di host yang didaftar ($($HOST_BOLEH -join ', '))."
    exit 2
}
$berkasJadi = [string]$b.berkas
if ($berkasJadi -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') { Write-Host "DITOLAK: nama berkas jadi '$berkasJadi' tidak sah."; exit 2 }
$sha = [string]$b.sha256
if ($sha -and $sha -cnotmatch '^[0-9a-f]{64}$') { Write-Host "DITOLAK: sha256 '$nama' di kunci bukan 64 huruf heksa kecil."; exit 2 }
$gb = 0.0
$angka = [System.Globalization.NumberStyles]::Float
$budaya = [System.Globalization.CultureInfo]::InvariantCulture
if (-not [double]::TryParse([string]$b.maks_gb, $angka, $budaya, [ref]$gb) -or $gb -le 0 -or $gb -gt $MAKS_GB) {
    Write-Host "DITOLAK: maks_gb '$nama' harus angka di atas 0 dan paling banyak $MAKS_GB."
    exit 2
}
$maksByte = [long]($gb * 1GB)

$keluar = Join-Path $dasarKeluar $nama
$argumen = @('run', '--rm', '--read-only', '--tmpfs', '/tmp:rw,size=64m', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--network', 'bridge',
    '--env', 'HOME=/tmp', '--env', 'PYTHONDONTWRITEBYTECODE=1',
    '--mount', "type=bind,source=$alat,target=/alat,readonly",
    '--mount', "type=bind,source=$keluar,target=/keluar",
    '--workdir', '/keluar', $image, 'python', '-I', '/alat/ambil_berkas.py',
    '--alamat', [string]$b.url, '--keluar', '/keluar', '--nama', $berkasJadi, '--maks-byte', "$maksByte")
foreach ($h in $HOST_BOLEH) { $argumen += @('--host', $h) }
if ($sha) { $argumen += @('--sha256', $sha) }

if ($kering) { ConvertTo-Json -InputObject $argumen -Compress; exit 0 }

New-Item -ItemType Directory -Force $keluar | Out-Null
# Image lab dijaga lewat ID-nya di kunci vendor: tak tercatat, tak ada di mesin, atau berbeda = tidak dijalankan.
$idKunci = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).image_lab.id
$ErrorActionPreference = 'Continue'
$idImage = & $docker image inspect $image --format '{{.Id}}' 2>$null
$ErrorActionPreference = 'Stop'
if (-not $idKunci -or "$idImage".Trim() -ne $idKunci) {
    Write-Host "IMAGE TAK SESUAI KUNCI: '$image' ber-ID '$idImage', yang tercatat '$idKunci' (tools\vendor.lock.json, image_lab)."
    exit 6
}

& $docker @argumen
$kode = $LASTEXITCODE
if ($kode -ne 0) { exit $kode }
# Kode 0 dari pengunduh bukan bukti. Yang dinilai adalah berkasnya.
$terpotong = @(Get-ChildItem -LiteralPath $keluar -Filter '*.part' -File)
if ($terpotong.Count -gt 0) {
    Write-Host ("UNDUHAN TERPOTONG: pengunduh keluar 0, tetapi berkas ini belum utuh: {0}." -f (($terpotong | ForEach-Object { $_.Name }) -join ', '))
    exit 8
}
if (-not (Test-Path -LiteralPath (Join-Path $keluar $berkasJadi) -PathType Leaf)) {
    Write-Host "TAK ADA BERKAS JADI: pengunduh keluar 0, tetapi '$berkasJadi' tidak ada di $keluar."
    exit 9
}
if (-not $sha) {
    Write-Host "BELUM DIKUNCI: catat SHA256 di atas pada butir '$nama' di tools\vendor.lock.json, lalu jalankan lagi. Berkas yang belum dikunci tidak boleh dibuka."
}
exit 0
```

- [ ] **Step 8: Jalankan kedua gerbang**

Run: `npm test; echo "EXIT=$?"`
Expected: `tests 99`, `pass 99`, `fail 0`, `EXIT=0` (79 + 20 baru).

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `30 passed` dan `EXIT=0`.

- [ ] **Step 9: Commit**

```bash
git add tools/ambil/ambil_berkas.py tools/lab/uji/test_ambil_berkas.py tools/ambil-berkas.ps1 tools/uji/ambil-berkas.test.mjs
git commit -q -F - <<'EOF'
Pintu unduh berkas untuk arsip dataset

Alasan: spec bagian 8.6 menuntut tiap unduhan dataset dikunci, dicatat, dan
dihitung SHA-256-nya. Sampai sekarang repo ini hanya punya pintu untuk
video.

Pintu ini hanya mengambil butir yang tercatat di kunci, hanya https ke tiga
host yang didaftar, di container yang hanya melihat pengunduhnya sendiri dan
satu folder keluaran. Pengalihan diperiksa ulang, dan alamat hasil
pengalihan tidak pernah dicatat utuh karena memuat tanda tangan sementara.

Berhasil atau tidaknya dinilai dari berkasnya: sisa .part = kode 8, dan
pengunduh yang keluar 0 tanpa berkas jadi = kode 9. Yang terakhir itu cacat
yang masih terbuka di pintu video.

Uji ditulis lebih dulu dan terlihat merah. Gerbang: Node 79 -> 99, lab
16 -> 30.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Pembuka arsip yang aman

**Files:**
- Create: `tools/lab/buka_arsip.py`
- Create: `tools/lab/uji/test_buka_arsip.py`

- [ ] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_buka_arsip.py`:

```python
"""Uji tools/lab/buka_arsip.py: arsip dari luar adalah bahan tak tepercaya, dan nama berkasnya tidak boleh tercetak."""
import hashlib
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import buka_arsip as ba  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "buka_arsip.py"
ISI_WAJAR = {
    "data-abc/original/train/B 1234 XYZ_0001.png": b"gambar-1",
    "data-abc/original/test/D 5678 AB_0002.jpg": b"gambar-2",
    "data-abc/augmentation/rain/train/B 1234 XYZ_0001.png": b"gambar-olahan",
    "data-abc/README.md": b"keterangan",
    "data-abc/a.ipynb": b"{}",
    "data-abc/latih.py": b"print('jangan dijalankan')",
}


def buat_arsip(jalur, isi, tautan=()):
    with zipfile.ZipFile(jalur, "w") as arsip:
        for nama, data in isi.items():
            arsip.writestr(nama, data)
        for nama in tautan:
            info = zipfile.ZipInfo(nama)
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            arsip.writestr(info, "/etc/passwd")
    return jalur, hashlib.sha256(jalur.read_bytes()).hexdigest()


def isi_folder(folder):
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()) if folder.exists() else []


def test_daftar_hanya_menghitung_dan_tidak_menulis_apa_pun(tmp_path, capsys):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)

    kode = ba.utama(["daftar", str(arsip), "--sha256", sidik])

    cetak = capsys.readouterr().out
    assert kode == 0
    assert "data-abc/original/train" in cetak and "4 berkas akan dibuka, 2 dilewati" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak, "nama berkas memuat nomor plat; tidak boleh tercetak"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.zip"]


def test_buka_menulis_berkas_yang_boleh_dan_melewati_buku_catatan_serta_skrip(tmp_path, capsys):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    cetak = capsys.readouterr().out
    assert kode == 0, cetak
    assert isi_folder(tujuan) == sorted(n for n in ISI_WAJAR if not n.endswith((".ipynb", ".py")))
    assert (tujuan / "data-abc/original/train/B 1234 XYZ_0001.png").read_bytes() == b"gambar-1"
    assert "dilewati (akhiran .ipynb)" in cetak and "dilewati (akhiran .py)" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak


def test_lapis_teratas_dibuang_dan_hanya_awalan_yang_diminta_yang_dibuka(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik, "--buang-lapis", "1", "--awalan", "original/"])

    assert kode == 0
    assert isi_folder(tujuan) == ["original/test/D 5678 AB_0002.jpg", "original/train/B 1234 XYZ_0001.png"]


def test_sidik_arsip_yang_tidak_cocok_dengan_kunci_tidak_dibuka(tmp_path, capsys):
    arsip, _ = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", "0" * 64])

    assert kode == 7
    assert "TIDAK COCOK" in capsys.readouterr().out
    assert isi_folder(tujuan) == []


def test_butir_yang_memanjat_keluar_folder_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "../luar.txt": b"jahat"})
    tujuan = tmp_path / "keluar"

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    assert kode == 1
    assert isi_folder(tujuan) == [] and not (tmp_path / "luar.txt").exists()


def test_butir_berjalur_mutlak_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "/tmp/luar.txt": b"jahat"})

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_butir_bergaris_miring_terbalik_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x", "..\\luar.txt": b"jahat"})

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_tautan_simbolik_membatalkan_seluruh_arsip(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"x"}, tautan=["tautan.txt"])

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_folder_tujuan_yang_sudah_berisi_tidak_ditimpa(tmp_path):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"baik.txt": b"baru"})
    tujuan = tmp_path / "keluar"
    tujuan.mkdir()
    (tujuan / "baik.txt").write_bytes(b"lama")

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    assert kode == 1
    assert (tujuan / "baik.txt").read_bytes() == b"lama"


def test_arsip_yang_melebihi_batas_ukuran_ditolak(tmp_path, monkeypatch):
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"a.txt": b"x" * 600, "b.txt": b"x" * 600})
    monkeypatch.setattr(ba, "MAKS_BYTE", 1000)

    assert ba.utama(["buka", str(arsip), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_dua_butir_bernama_sama_ditolak_dan_yang_sudah_ditulis_dibersihkan(tmp_path):
    jalur = tmp_path / "a.zip"
    with zipfile.ZipFile(jalur, "w") as arsip:
        arsip.writestr("sama.txt", b"satu")
        arsip.writestr("sama.txt", b"dua")
    sidik = hashlib.sha256(jalur.read_bytes()).hexdigest()

    assert ba.utama(["buka", str(jalur), str(tmp_path / "keluar"), "--sha256", sidik]) == 1
    assert isi_folder(tmp_path / "keluar") == []


def test_baris_perintah_sampai_ke_berkas_yang_terbuka(tmp_path):
    # Rantainya: baris perintah -> periksa sidik -> periksa daftar isi -> tulis.
    arsip, sidik = buat_arsip(tmp_path / "a.zip", ISI_WAJAR)
    tujuan = tmp_path / "keluar"

    hasil = subprocess.run([sys.executable, str(SKRIP), "buka", str(arsip), str(tujuan), "--sha256", sidik,
                            "--buang-lapis", "1", "--awalan", "original/"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert len(isi_folder(tujuan)) == 2
    assert "2 berkas dibuka" in hasil.stdout


def test_galat_menulis_tidak_membocorkan_nama_berkas(tmp_path, capsys):
    # Pesan galat bawaan Python memuat jalur berkas; pada dataset plat, jalur itu memuat nomor plat.
    arsip, sidik = buat_arsip(tmp_path / "a.zip", {"B 1234 XYZ_0001.png": b"gambar-1"})
    tujuan = tmp_path / "keluar"
    tujuan.mkdir()
    tujuan.chmod(0o500)

    kode = ba.utama(["buka", str(arsip), str(tujuan), "--sha256", sidik])

    cetak = capsys.readouterr()
    tujuan.chmod(0o700)
    assert kode == 1
    assert "GAGAL MENULIS" in cetak.out
    assert "1234" not in cetak.out + cetak.err
```

- [ ] **Step 2: Jalankan, pastikan merah karena pembukanya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat saat mengumpulkan uji, `ModuleNotFoundError: No module named 'buka_arsip'`, `EXIT` bukan 0.

- [ ] **Step 3: Tulis pembukanya**

Buat `tools/lab/buka_arsip.py`:

```python
"""Membuka arsip zip hasil unduhan dengan aman, di lab tanpa jaringan (spec bagian 8.6).

Arsip dari luar diperlakukan sebagai bahan tak tepercaya:
- SHA-256 arsip harus sama dengan yang dikunci; kalau tidak, tidak ada yang dibuka (kode 7);
- seluruh daftar isi diperiksa DULU: jalur mutlak, "..", garis miring terbalik, dan tautan simbolik membatalkan
  semuanya sebelum satu berkas pun ditulis;
- hanya akhiran di AKHIRAN_BOLEH yang dibuka (gambar, label teks, keterangan); buku catatan dan skrip dilewati;
- jumlah butir dan ukuran total dibatasi;
- folder tujuan harus kosong atau belum ada; bila gagal di tengah jalan, yang sudah ditulis dibersihkan.

Nama berkas TIDAK dicetak: pada dataset plat, nama berkas bisa memuat nomor plat (CLAUDE.md §4). Yang dicetak hanya
jumlah berkas per folder.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/buka_arsip.py daftar <arsip.zip> --sha256 <hex>
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/buka_arsip.py buka <arsip.zip> <folder-tujuan> --sha256 <hex> [--buang-lapis N] [--awalan original/ ...]

Kode keluar: 0 berhasil · 1 arsip ditolak · 2 salah pakai · 7 SHA-256 tidak cocok.
"""
import argparse
import hashlib
import shutil
import stat
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

AKHIRAN_BOLEH = {".jpg", ".jpeg", ".png", ".txt", ".yaml", ".yml", ".md", ".csv", ".json", ".xlsx"}
MAKS_BUTIR = 200_000
MAKS_BYTE = 20 * 1024**3
POTONG = 1 << 20
KEDALAMAN_RINGKAS = 3


class Ditolak(Exception):
    """Arsip yang tidak boleh dibuka."""


def sidik_berkas(jalur):
    sidik = hashlib.sha256()
    with open(jalur, "rb") as berkas:
        for potong in iter(lambda: berkas.read(POTONG), b""):
            sidik.update(potong)
    return sidik.hexdigest()


def jalur_aman(nama, buang_lapis):
    """Jalur relatif di dalam folder tujuan, atau None bila butirnya habis oleh --buang-lapis."""
    if "\\" in nama or nama.startswith("/") or (len(nama) > 1 and nama[1] == ":"):
        raise Ditolak("ada butir berjalur mutlak atau bergaris miring terbalik")
    bagian = PurePosixPath(nama).parts
    if ".." in bagian:
        raise Ditolak('ada butir yang jalurnya memuat ".."')
    sisa = bagian[buang_lapis:]
    return PurePosixPath(*sisa) if sisa else None


def rencana(arsip, buang_lapis=0, awalan=()):
    """Memeriksa seluruh daftar isi: (yang dibuka, yang dilewati). Melempar Ditolak bila ada satu saja yang berbahaya."""
    butir = arsip.infolist()
    if len(butir) > MAKS_BUTIR:
        raise Ditolak(f"{len(butir)} butir, melebihi batas {MAKS_BUTIR}")
    dibuka, dilewati, byte = [], Counter(), 0
    for info in butir:
        if stat.S_ISLNK(info.external_attr >> 16):
            raise Ditolak("arsip memuat tautan simbolik")
        jalur = jalur_aman(info.filename, buang_lapis)
        if info.is_dir() or jalur is None:
            continue
        if awalan and not any(jalur.as_posix().startswith(a) for a in awalan):
            dilewati["di luar awalan yang diminta"] += 1
            continue
        if jalur.suffix.lower() not in AKHIRAN_BOLEH:
            dilewati[f"akhiran {jalur.suffix.lower() or '(tanpa)'}"] += 1
            continue
        byte += info.file_size
        if byte > MAKS_BYTE:
            raise Ditolak(f"ukuran terbuka melebihi batas {MAKS_BYTE} byte")
        dibuka.append((info, jalur))
    return dibuka, dilewati


def ringkas(jalur_jalur):
    """Jumlah berkas per folder, paling dalam KEDALAMAN_RINGKAS tingkat. Nama berkas tidak ikut."""
    hitung = Counter()
    for jalur in jalur_jalur:
        hitung["/".join(jalur.parts[:-1][:KEDALAMAN_RINGKAS]) or "(akar)"] += 1
    return hitung


def buka(arsip, dibuka, tujuan):
    tujuan = Path(tujuan)
    if tujuan.exists() and any(tujuan.iterdir()):
        raise Ditolak("folder tujuan tidak kosong")
    tujuan.mkdir(parents=True, exist_ok=True)
    akar = tujuan.resolve()
    tulis = 0
    try:
        for info, jalur in dibuka:
            sasaran = (akar / jalur).resolve()
            if akar not in sasaran.parents:
                raise Ditolak("ada butir yang jalurnya keluar dari folder tujuan")
            if sasaran.exists():
                raise Ditolak("ada dua butir bernama sama")
            sasaran.parent.mkdir(parents=True, exist_ok=True)
            with arsip.open(info) as sumber, open(sasaran, "wb") as keluar:
                while True:
                    potong = sumber.read(POTONG)
                    if not potong:
                        break
                    tulis += len(potong)
                    if tulis > MAKS_BYTE:
                        raise Ditolak("isi yang terbuka melebihi batas: ukuran di daftar isi arsip tidak jujur")
                    keluar.write(potong)
    except BaseException:
        # Tujuan tadi kosong atau belum ada, jadi semua isinya berasal dari sini: bersihkan.
        for sisa in akar.iterdir():
            shutil.rmtree(sisa) if sisa.is_dir() else sisa.unlink()
        raise
    return tulis


def utama(argumen=None):
    urai = argparse.ArgumentParser(description="Membuka arsip zip hasil unduhan dengan aman.")
    urai.add_argument("perintah", choices=["daftar", "buka"])
    urai.add_argument("arsip")
    urai.add_argument("tujuan", nargs="?")
    urai.add_argument("--sha256", required=True)
    urai.add_argument("--buang-lapis", type=int, default=0)
    urai.add_argument("--awalan", action="append", default=[])
    p = urai.parse_args(argumen)
    if p.perintah == "buka" and not p.tujuan:
        print("Pakai: buka_arsip.py buka <arsip.zip> <folder-tujuan> --sha256 <hex>")
        return 2
    try:
        hasil = sidik_berkas(p.arsip)
    except OSError as galat:
        print(f"ARSIP TIDAK TERBACA: {type(galat).__name__}")
        return 2
    if hasil != p.sha256:
        print(f"SHA-256 TIDAK COCOK: arsip ber-SHA256 {hasil}, yang dikunci {p.sha256}. Tidak ada yang dibuka.")
        return 7
    try:
        with zipfile.ZipFile(p.arsip) as arsip:
            dibuka, dilewati = rencana(arsip, p.buang_lapis, tuple(p.awalan))
            for folder, jumlah in sorted(ringkas(jalur for _, jalur in dibuka).items()):
                print(f"{jumlah:>7} berkas  {folder}")
            for alasan, jumlah in sorted(dilewati.items()):
                print(f"{jumlah:>7} dilewati ({alasan})")
            if p.perintah == "daftar":
                print(f"{len(dibuka)} berkas akan dibuka, {sum(dilewati.values())} dilewati. Tidak ada yang ditulis.")
                return 0
            byte = buka(arsip, dibuka, p.tujuan)
    except Ditolak as galat:
        print(f"ARSIP DITOLAK: {galat}")
        return 1
    except zipfile.BadZipFile:
        print("ARSIP DITOLAK: bukan zip yang sah, atau isinya rusak")
        return 1
    except OSError as galat:
        # Pesan bawaan memuat jalur berkas, dan pada dataset plat jalur itu memuat nomor plat: jangan dicetak.
        print(f"GAGAL MENULIS: {type(galat).__name__} (errno {galat.errno}). Nama berkas tidak dicetak.")
        return 1
    print(f"{len(dibuka)} berkas dibuka ({byte} byte), {sum(dilewati.values())} dilewati")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `43 passed` dan `EXIT=0` (30 + 13 baru).

- [ ] **Step 5: Commit**

```bash
git add tools/lab/buka_arsip.py tools/lab/uji/test_buka_arsip.py
git commit -q -F - <<'EOF'
Pembuka arsip yang aman untuk dataset hasil unduhan

Alasan: arsip dari luar adalah bahan tak tepercaya, dan pada dataset plat
nama berkasnya memuat nomor plat. Membukanya dengan alat biasa berarti
percaya pada daftar isinya dan mencetak nama-nama itu ke layar.

Pembuka ini berjalan di lab tanpa jaringan, menuntut SHA-256 yang dikunci,
memeriksa seluruh daftar isi sebelum menulis satu berkas pun, melewati buku
catatan dan skrip, dan hanya mencetak jumlah berkas per folder.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 30 -> 43.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Pembaca catatan penerbit dan pencocok SHA-256

Mendeley Data mencatat SHA-256 tiap berkas. Alat ini membaca catatan itu (berkas JSON yang nanti diambil lewat pintu)
di lab: mencetak izinnya apa adanya, dan memastikan tiap berkas hasil buka arsip sama dengan terbitan.

**Files:**
- Create: `tools/lab/catatan_mendeley.py`
- Create: `tools/lab/uji/test_catatan_mendeley.py`

- [ ] **Step 1: Tulis ujinya**

Buat `tools/lab/uji/test_catatan_mendeley.py`:

```python
"""Uji tools/lab/catatan_mendeley.py: hasil buka arsip harus sama dengan yang dicatat penerbit, tanpa nama berkas tercetak."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catatan_mendeley as cm  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "catatan_mendeley.py"
ISI = {"B 1234 XYZ_0001.png": b"gambar-1", "D 5678 AB_0002.jpg": b"gambar-2"}
ID_LATIH = "id-folder-latih"


def siapkan(tmp_path, isi_folder=ISI):
    """Catatan penerbit yang mencatat ISI di folder ID_LATIH, dan folder hasil buka berisi `isi_folder`."""
    butir = [{"filename": nama, "folder_id": ID_LATIH, "size": len(data),
              "content_details": {"sha256_hash": hashlib.sha256(data).hexdigest()}} for nama, data in ISI.items()]
    butir.append({"filename": "Keterangan.xlsx", "size": 5, "content_details": {"sha256_hash": "f" * 64}})
    catatan = tmp_path / "catatan-dataset.json"
    catatan.write_text(json.dumps({
        "id": "abc123", "name": "DATASET-CONTOH", "version": 1, "doi": {"id": "10.0000/abc123.1"},
        "publish_date": "2023-09-07T16:39:37.68Z", "institutions": [{"name": "Lembaga Contoh"}],
        "contributors": [{"first_name": "Nama", "last_name": "Pembuat"}],
        "data_licence": {"short_name": "CC BY 4.0", "url": "https://contoh.test/by/4.0", "description": "Boleh dipakai dengan menyebut sumber."},
        "files": butir,
    }))
    terbuka = tmp_path / "terbuka"
    (terbuka / "original" / "train").mkdir(parents=True)
    for nama, data in isi_folder.items():
        (terbuka / "original" / "train" / nama).write_bytes(data)
    return catatan, terbuka


def test_izin_dicetak_apa_adanya_beserta_jumlah_berkas_per_folder(tmp_path, capsys):
    catatan, _ = siapkan(tmp_path)

    kode = cm.utama(["izin", str(catatan)])

    cetak = capsys.readouterr().out
    assert kode == 0
    assert "DATASET-CONTOH" in cetak and "10.0000/abc123.1" in cetak and "Lembaga Contoh" in cetak
    assert "CC BY 4.0" in cetak and "Boleh dipakai dengan menyebut sumber." in cetak
    assert "berkas tercatat: 3" in cetak and ID_LATIH in cetak
    assert "1234" not in cetak and "XYZ" not in cetak, "nama berkas memuat nomor plat; tidak boleh tercetak"


def test_folder_yang_persis_sama_dengan_catatan_penerbit_dinyatakan_cocok(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    cetak = capsys.readouterr().out
    assert kode == 0, cetak
    assert "COCOK original/train: penerbit mencatat 2, di folder 2, sama 2, kurang 0, lebih 0" in cetak
    assert "1234" not in cetak and "XYZ" not in cetak


def test_berkas_yang_hilang_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {"B 1234 XYZ_0001.png": b"gambar-1"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "kurang 1, lebih 0" in capsys.readouterr().out


def test_berkas_yang_isinya_berbeda_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {**ISI, "D 5678 AB_0002.jpg": b"ditukar"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "sama 1, kurang 1, lebih 1" in capsys.readouterr().out


def test_berkas_tambahan_yang_tidak_dicatat_penerbit_tertangkap(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path, {**ISI, "selundupan.png": b"lain"})

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    assert kode == 1
    assert "kurang 0, lebih 1" in capsys.readouterr().out


def test_folder_yang_tidak_ada_atau_id_yang_tidak_dikenal_bukan_cocok(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)

    assert cm.utama(["cocok", str(catatan), str(terbuka), f"original/test={ID_LATIH}"]) == 1
    assert cm.utama(["cocok", str(catatan), str(terbuka), "original/train=id-yang-tidak-ada"]) == 1


def test_baris_perintah_sampai_ke_putusan(tmp_path):
    # Rantainya: baris perintah -> catatan penerbit -> SHA-256 tiap berkas di folder -> kode keluar.
    catatan, terbuka = siapkan(tmp_path)

    cocok = subprocess.run([sys.executable, str(SKRIP), "cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"], capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), "cocok", str(catatan), str(terbuka)], capture_output=True, text=True)

    assert cocok.returncode == 0, cocok.stdout + cocok.stderr
    assert salah.returncode == 2, salah.stdout + salah.stderr


def test_galat_membaca_tidak_membocorkan_nama_berkas(tmp_path, capsys):
    catatan, terbuka = siapkan(tmp_path)
    berkas = terbuka / "original" / "train" / "B 1234 XYZ_0001.png"
    berkas.chmod(0o000)

    kode = cm.utama(["cocok", str(catatan), str(terbuka), f"original/train={ID_LATIH}"])

    cetak = capsys.readouterr()
    berkas.chmod(0o600)
    assert kode == 1
    assert "GAGAL MEMBACA" in cetak.out
    assert "1234" not in cetak.out + cetak.err
```

- [ ] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: galat saat mengumpulkan uji, `ModuleNotFoundError: No module named 'catatan_mendeley'`, `EXIT` bukan 0.

- [ ] **Step 3: Tulis alatnya**

Buat `tools/lab/catatan_mendeley.py`:

```python
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
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `51 passed` dan `EXIT=0` (43 + 8 baru).

- [ ] **Step 5: Commit**

```bash
git add tools/lab/catatan_mendeley.py tools/lab/uji/test_catatan_mendeley.py
git commit -q -F - <<'EOF'
Pembaca catatan penerbit dan pencocok SHA-256 untuk dataset Mendeley

Alasan: arsip INDO-ALPR tidak punya SHA-256 terbitan, jadi kuncinya hanya
"apa yang kita terima pertama kali". Tetapi penerbitnya mencatat SHA-256
tiap berkas. Dengan mencocokkan tiap berkas hasil buka arsip ke catatan itu,
"sama dengan terbitan" menjadi sesuatu yang dibuktikan, bukan dipercaya.

Alat yang sama mencetak teks izin dataset apa adanya, sebagai dasar vonis.
Nama berkas tidak pernah dicetak karena memuat nomor plat.

Uji ditulis lebih dulu dan terlihat merah. Gerbang lab: 43 -> 51.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 5: Mengambil dataset pencahayaan (yang kecil lebih dulu)

Dataset kecil dikerjakan lebih dulu supaya pintu dan pembuka terbukti pada bahan sungguhan sebelum unduhan 7 GB.

**Files:**
- Modify: `tools/vendor.lock.json`
- Create: `docs/lisensi/dataset__plat-lighting/IZIN.md`

- [ ] **Step 1: Catat ketiga butir di kunci**

Di `tools/vendor.lock.json`, sesudah butir `"image_lab": { ... }` (butir terakhir), tambahkan koma lalu dua kunci ini:

```json
  "_berkas": "Berkas yang diambil tools/ambil-berkas.ps1 (arsip dan catatan dataset). Yang tak tercatat di sini tidak diambil. sha256 kosong = belum dikunci: boleh diunduh sekali untuk diukur, tetapi tools/lab/buka_arsip.py menolak membuka arsip tanpa sha256. Alamat dan angka dibaca dari sumbernya pada tanggal 'dibaca'.",
  "berkas": [
    {
      "nama": "plat-lighting",
      "url": "https://codeload.github.com/salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset/zip/e5bfbd8af64541d032c9022eef588e75d9786c6a",
      "berkas": "plat-lighting-e5bfbd8.zip",
      "maks_gb": 1,
      "sha256": "",
      "sumber": "https://github.com/salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset",
      "commit": "e5bfbd8af64541d032c9022eef588e75d9786c6a",
      "isi_dibaca": "API pohon GitHub pada commit itu: 561 jpg, 561 label txt, 2 README txt, 1 md, 1 yaml, 1 ipynb; 143 MB",
      "dibaca": "2026-10-13"
    },
    {
      "nama": "indo-alpr-catatan",
      "url": "https://data.mendeley.com/public-api/datasets/j3256db3fz",
      "berkas": "catatan-dataset.json",
      "maks_gb": 0.2,
      "sha256": "",
      "kunci": "sengaja tidak dikunci: catatan ini memuat hitungan kunjungan yang berubah tiap hari. Dipakai sebagai daftar SHA-256 penerbit untuk tiap berkas dan sebagai bukti izin",
      "dibaca": "2026-10-13"
    },
    {
      "nama": "indo-alpr",
      "url": "https://data.mendeley.com/public-api/zip/j3256db3fz/download/1",
      "berkas": "indo-alpr-v1.zip",
      "maks_gb": 12,
      "sha256": "",
      "sumber": "https://data.mendeley.com/datasets/j3256db3fz/1",
      "doi": "10.17632/j3256db3fz.1",
      "isi_dibaca": "catatan API: 67.922 berkas, 7.390 MB. original/train 4.712 (folder 44fd8100-281c-4dea-9ba8-e6469d256ec3); original/test 1.462 (folder b6eab52b-d6d1-43b9-a073-4c13afe0fe19)",
      "dibaca": "2026-10-13"
    }
  ]
```

Run: `node -e "const k=JSON.parse(require('fs').readFileSync('tools/vendor.lock.json','utf8'));console.log(k.berkas.map(b=>b.nama).join(','), '| repo', k.repo.length, '| image', !!k.image_lab.id)"`
Expected: `plat-lighting,indo-alpr-catatan,indo-alpr | repo 11 | image true`

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 99`, `EXIT=0` (alat lain tetap bisa membaca kuncinya).

- [ ] **Step 2: Unduh arsipnya**

Run (PowerShell): `powershell -NoProfile -File tools\ambil-berkas.ps1 plat-lighting; "EXIT=$LASTEXITCODE"`
Expected: baris `TERSIMPAN plat-lighting-e5bfbd8.zip: <byte> byte, SHA256 <64 huruf>, dari codeload.github.com`,
baris `BELUM DIKUNCI: ...`, dan `EXIT=0`.

Run (PowerShell): `Get-ChildItem data\unduhan\plat-lighting | ForEach-Object { "{0} {1}" -f $_.Name, $_.Length }; Get-Content data\unduhan\plat-lighting\plat-lighting-e5bfbd8.zip.asal.json`
Expected: dua berkas (`.zip` dan `.zip.asal.json`), tanpa `.part`. Ukuran zip di sekitar 143 MB.

Bila `EXIT` bukan 0: baca pesannya. Kode 1 dengan `HTTP 4xx/5xx` atau `GAGAL` = gangguan jaringan atau sumber; ulangi
sekali. Bila tetap gagal, berhenti dan laporkan, jangan mencari jalan lain di luar pintu.

- [ ] **Step 3: Kunci SHA-256-nya, lalu buktikan kuncinya bekerja**

Salin nilai `sha256` dari `plat-lighting-e5bfbd8.zip.asal.json` ke kolom `"sha256"` butir `plat-lighting` di
`tools/vendor.lock.json` (nilai dibaca dari berkas itu, tidak diketik dari layar).

Run (PowerShell): `powershell -NoProfile -File tools\ambil-berkas.ps1 plat-lighting; "EXIT=$LASTEXITCODE"`
Expected: `SUDAH ADA plat-lighting-e5bfbd8.zip: ... Tidak ada yang diunduh.`, tanpa baris `BELUM DIKUNCI`, `EXIT=0`.

- [ ] **Step 4: Lihat daftar isinya di lab, tanpa membuka**

Ganti `<SHA>` dengan nilai yang baru dikunci.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/buka_arsip.py daftar /kerja/data/unduhan/plat-lighting/plat-lighting-e5bfbd8.zip --sha256 <SHA> --buang-lapis 1; "EXIT=$LASTEXITCODE"`

Expected (angka dari API pohon GitHub, dibaca 13 Okt):

```
      4 berkas  (akar)
     84 berkas  test/images
     84 berkas  test/labels
    393 berkas  train/images
    393 berkas  train/labels
     84 berkas  valid/images
     84 berkas  valid/labels
      1 dilewati (akhiran .ipynb)
1126 berkas akan dibuka, 1 dilewati. Tidak ada yang ditulis.
```

Bila angkanya berbeda, berhenti: arsip bukan yang dibaca pada 13 Okt. Catat selisihnya dan laporkan.

- [ ] **Step 5: Buka ke folder dataset**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/buka_arsip.py buka /kerja/data/unduhan/plat-lighting/plat-lighting-e5bfbd8.zip /kerja/data/keluaran/dataset/plat-lighting --sha256 <SHA> --buang-lapis 1; "EXIT=$LASTEXITCODE"`
Expected: baris jumlah yang sama, lalu `1126 berkas dibuka (<byte> byte), 1 dilewati`, `EXIT=0`.

Run: `git status --short`
Expected: hanya ` M tools/vendor.lock.json`. Dataset ada di `data/`, yang tidak masuk git.

- [ ] **Step 6: Tulis bukti izinnya**

Baca ulang tiga berkas teks dari folder yang baru dibuka (ketiganya keterangan, bukan gambar, dan tidak memuat nomor
plat): `data/keluaran/dataset/plat-lighting/README.md`, `README.dataset.txt`, `data.yaml`.

Buat `docs/lisensi/dataset__plat-lighting/IZIN.md`:

```markdown
# Izin: Indonesian License Plate Lighting Dataset

- **Sumber:** https://github.com/salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset
- **Commit yang dikunci:** `e5bfbd8af64541d032c9022eef588e75d9786c6a` (`tools/vendor.lock.json`, butir `plat-lighting`)
- **Dibaca:** 2026-10-13, dari berkas hasil buka arsip pada commit itu.

## Yang tertulis, apa adanya

| Berkas | Kutipan |
|---|---|
| `README.md` | "**Lisensi:** CC BY 4.0" |
| `README.md` | "Seluruh data gambar diambil sendiri oleh ([GitHub: rocmind](https://github.com/salsabilaputri95))." |
| `README.dataset.txt` | "License: CC BY 4.0" |
| `data.yaml` | "license: CC BY 4.0" |

## Yang tidak ada

- Tidak ada berkas `LICENSE`. Kolom lisensi repo di GitHub kosong (dibaca lewat `gh api`, 13 Okt).
- Cermin di Kaggle menandainya "Other (specified in description)" tanpa teks izin (catatan riset 13 Okt, tidak dibaca ulang).

## Bacaan agen

Izin hak ciptanya dinyatakan konsisten di tiga tempat sebagai CC BY 4.0, yang membolehkan pemakaian komersial dengan
menyebut sumber. Kelemahannya: tanpa berkas LICENSE, dan pernyataannya datang dari ekspor Roboflow. **Soal data
pribadi** (gambarnya memuat plat kendaraan orang lain): owner menyatakan sudah berkonsultasi dengan pihak hukum (K21,
14 Okt; `OPEN-QUESTIONS.md` B9). Agen tidak melihat hasil konsultasinya.
```

Sebelum menyimpan, cocokkan tiap kutipan dengan berkas yang baru dibaca; bila ada yang berbeda, tulis yang terbaca.

- [ ] **Step 7: Commit**

```bash
git add tools/vendor.lock.json docs/lisensi/dataset__plat-lighting/IZIN.md
git commit -q -F - <<'EOF'
Dataset pencahayaan plat Indonesia: diambil, dikunci, dibuka di lab

Alasan: ini satu dari dua dataset plat Indonesia yang izinnya (CC BY 4.0)
membolehkan produk dijual, dan satu-satunya yang menyebut malam secara
eksplisit. Dikerjakan lebih dulu karena kecil: pintu unduh dan pembuka arsip
dibuktikan pada bahan sungguhan sebelum unduhan 7 GB.

Arsipnya diambil pada commit yang dikunci, SHA-256-nya dicatat, dan jumlah
berkas per folder sama dengan yang dibaca dari GitHub. Buku catatan di
dalamnya tidak dibuka. Gambarnya tidak dilihat agen.

Batas: tanpa berkas LICENSE. Soal data pribadi bersandar pada pernyataan
owner (K21), bukan bukti yang dilihat agen.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 6: Mengambil INDO-ALPR dan membuktikannya sama dengan terbitan

**Files:**
- Modify: `tools/vendor.lock.json`
- Create: `docs/lisensi/dataset__indo-alpr/IZIN.md`

- [ ] **Step 1: Ambil catatan penerbit dan baca izinnya**

Run (PowerShell): `powershell -NoProfile -File tools\ambil-berkas.ps1 indo-alpr-catatan; "EXIT=$LASTEXITCODE"`
Expected: `TERSIMPAN catatan-dataset.json: <sekitar 50 juta> byte, ... dari data.mendeley.com`, `BELUM DIKUNCI`
(memang tidak dikunci, lihat kolom `kunci` di butirnya), `EXIT=0`.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/catatan_mendeley.py izin /kerja/data/unduhan/indo-alpr-catatan/catatan-dataset.json; "EXIT=$LASTEXITCODE"`
Expected: `nama    : INDO-ALPR`, `doi     : 10.17632/j3256db3fz.1`, blok `izin, apa adanya:` berisi teks izin
selengkapnya, `berkas tercatat: 67922, ...`, dan di antara barisnya:

```
    4712 berkas ... folder_id 44fd8100-281c-4dea-9ba8-e6469d256ec3
    1462 berkas ... folder_id b6eab52b-d6d1-43b9-a073-4c13afe0fe19
```

Bila dua angka itu berbeda, penerbit mengubah datasetnya: pakai angka yang terbaca, dan catat perubahannya di Task 7.

- [ ] **Step 2: Tulis bukti izinnya**

Buat `docs/lisensi/dataset__indo-alpr/IZIN.md`, dengan blok izin disalin **utuh** dari keluaran Step 1:

```markdown
# Izin: INDO-ALPR

- **Sumber:** https://data.mendeley.com/datasets/j3256db3fz/1
- **DOI:** 10.17632/j3256db3fz.1 · versi 1 · terbit 7 September 2023
- **Pembuat:** <nama-nama dari baris "pembuat">, <lembaga dari baris "lembaga">
- **Dibaca:** 2026-10-13, dari catatan API publik (`https://data.mendeley.com/public-api/datasets/j3256db3fz`) yang
  diambil lewat `tools\ambil-berkas.ps1 indo-alpr-catatan` dan dibaca `tools/lab/catatan_mendeley.py izin`.

## Izin, apa adanya

<blok JSON `data_licence` dari keluaran Step 1, tanpa dipotong>

## Yang dipakai dan yang tidak

| Bagian | Jumlah | Dipakai |
|---|---|---|
| `original/train` | <angka dari Step 1> | Ya |
| `original/test` | <angka dari Step 1> | Ya |
| `augmentation/…` (sepuluh olahan) | sisanya | Tidak: turunan dari gambar asli, bukan bahan baru |

## Bacaan agen

<Tiga sampai lima kalimat: apa yang dibolehkan teks izin itu, syaratnya (menyebut sumber, menautkan izin, menandai
perubahan), dan kalimat mana di teks izin yang membatasi (misalnya soal isi milik pihak ketiga). Tutup dengan:>
**Soal data pribadi:** nama berkasnya adalah nomor plat kendaraan orang lain. Owner menyatakan sudah berkonsultasi
dengan pihak hukum (K21, `OPEN-QUESTIONS.md` B9); nama berkas itu tetap tidak pernah disalin ke repo (`CLAUDE.md` §4).
```

Bagian bersudut (`<...>`) diisi dari keluaran Step 1; tidak ada yang diisi dari ingatan.

- [ ] **Step 3: Periksa mesin sebelum unduhan besar**

Run (PowerShell): `"D: bebas {0:N1} GB" -f ((Get-PSDrive D).Free/1GB)`
Expected: di atas 30 GB (arsipnya sekitar 7,4 GB; hasil bukanya di bawah 1 GB).

- [ ] **Step 4: Unduh arsipnya (lama: jalankan di latar)**

Run (PowerShell, di latar): `powershell -NoProfile -File tools\ambil-berkas.ps1 indo-alpr; "EXIT=$LASTEXITCODE"`
Expected: baris `... 256 MB`, `... 512 MB`, dan seterusnya; di akhir `TERSIMPAN indo-alpr-v1.zip: <byte> byte,
SHA256 <64 huruf>, dari prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com`, `BELUM DIKUNCI`, `EXIT=0`.

Sesudah selesai, **nilai dari berkasnya**, bukan dari kode keluar:

Run (PowerShell): `Get-ChildItem data\unduhan\indo-alpr | ForEach-Object { "{0} {1}" -f $_.Name, $_.Length }`
Expected: `indo-alpr-v1.zip` berukuran beberapa GB dan `indo-alpr-v1.zip.asal.json`; tanpa `.part`.

Bila gagal di tengah jalan (kode 1 atau 8): hapus sisa `.part`, ulangi sekali. Bila gagal lagi, berhenti dan laporkan
beserta pesannya. Jangan mengambil gambar satu per satu sebagai jalan pintas: daftar per folder dipotong di 1.000.

- [ ] **Step 5: Kunci SHA-256-nya, lalu buktikan kuncinya bekerja**

Salin `sha256` dari `indo-alpr-v1.zip.asal.json` ke butir `indo-alpr` di `tools/vendor.lock.json`.

Run (PowerShell): `powershell -NoProfile -File tools\ambil-berkas.ps1 indo-alpr; "EXIT=$LASTEXITCODE"`
Expected: `SUDAH ADA indo-alpr-v1.zip: ...`, tanpa `BELUM DIKUNCI`, `EXIT=0`.

- [ ] **Step 6: Lihat daftar isinya, tentukan lapis yang dibuang**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/buka_arsip.py daftar /kerja/data/unduhan/indo-alpr/indo-alpr-v1.zip --sha256 <SHA>; "EXIT=$LASTEXITCODE"`
Expected: `EXIT=0`, baris-baris jumlah per folder yang memuat `original/train` dan `original/test`, dan di akhir
`<sekitar 67922> berkas akan dibuka`. (Ringkasan hanya menampilkan tiga tingkat folder, jadi bila arsip punya satu
folder pembungkus, bagian `train` dan `test` di dalam `augmentation/…` tampil tergabung. Itu bukan masalah.)

Baca baris-barisnya:

| Yang terlihat | Nilai `--buang-lapis` |
|---|---|
| `original/train` dan `original/test` langsung di depan | `0` |
| Satu nama folder di depannya, misalnya `INDO-ALPR/original/train` | `1` |
| Dua nama folder di depannya | `2` |
| Tidak ada folder bernama `original` | Berhenti dan laporkan: susunan arsip bukan yang dicatat API |

- [ ] **Step 7: Buka hanya bagian `original/`**

Ganti `<N>` dengan nilai dari Step 6.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/buka_arsip.py buka /kerja/data/unduhan/indo-alpr/indo-alpr-v1.zip /kerja/data/keluaran/dataset/indo-alpr --sha256 <SHA> --buang-lapis <N> --awalan original/; "EXIT=$LASTEXITCODE"`
Expected:

```
   1462 berkas  original/test
   4712 berkas  original/train
<sisanya> dilewati (di luar awalan yang diminta)
6174 berkas dibuka (<byte> byte), <sisanya> dilewati
```

dan `EXIT=0`.

- [ ] **Step 8: Buktikan tiap berkas sama dengan terbitan**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/catatan_mendeley.py cocok /kerja/data/unduhan/indo-alpr-catatan/catatan-dataset.json /kerja/data/keluaran/dataset/indo-alpr original/train=44fd8100-281c-4dea-9ba8-e6469d256ec3 original/test=b6eab52b-d6d1-43b9-a073-4c13afe0fe19; "EXIT=$LASTEXITCODE"`
Expected:

```
COCOK original/train: penerbit mencatat 4712, di folder 4712, sama 4712, kurang 0, lebih 0
COCOK original/test: penerbit mencatat 1462, di folder 1462, sama 1462, kurang 0, lebih 0
```

dan `EXIT=0`. Bila ada `BEDA`: hasil buka **tidak** dipakai. Catat angkanya apa adanya dan laporkan.

- [ ] **Step 9: Commit**

Run: `git status --short`
Expected: ` M tools/vendor.lock.json` dan `?? docs/lisensi/dataset__indo-alpr/`. Tidak ada berkas dari `data/`.

```bash
git add tools/vendor.lock.json docs/lisensi/dataset__indo-alpr/IZIN.md
git commit -q -F - <<'EOF'
INDO-ALPR: diambil, dikunci, dan dibuktikan sama dengan terbitan

Alasan: inilah dataset plat Indonesia berizin jual yang terbesar (6.174
gambar asli, CC BY 4.0), dan labelnya sudah ada: nomor plat di nama berkas.

Yang dibuka hanya bagian original. Sepuluh folder augmentation berisi
olahan dari gambar yang sama, jadi bukan bahan baru. Tiap berkas hasil buka
dicocokkan dengan SHA-256 yang dicatat penerbitnya: tak ada yang kurang,
lebih, atau berbeda.

Karena nama berkasnya nomor plat, tidak satu pun nama berkas dicetak atau
disalin ke repo. Gambarnya tidak dilihat agen.

Batas: soal data pribadi bersandar pada pernyataan owner (K21), bukan
bukti yang dilihat agen.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

Bila angka di pesan commit (6.174) berbeda dari yang terbaca di Step 8, pakai angka yang terbaca.

---

### Task 7: Vonis, daftar bahan, dan catatan

**Files:**
- Modify: `data-asal/bahan.json`
- Modify: `docs/VONIS-LISENSI.md`
- Modify: `CLAUDE.md`
- Modify: `OPEN-QUESTIONS.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Catat dua bahan baru**

Di `data-asal/bahan.json`, tambahkan dua butir di akhir daftar `bahan` (angka jumlah gambar diambil dari keluaran Task
5 Step 5 dan Task 6 Step 8):

```json
    {
      "id": "dataset-indo-alpr",
      "jenis": "dataset",
      "nama": "INDO-ALPR (ITS), bagian original: 6174 gambar",
      "sumber": "https://data.mendeley.com/datasets/j3256db3fz/1",
      "lisensi": "CC BY 4.0 (catatan API Mendeley Data, dibaca 2026-10-13)",
      "bukti_lisensi": "docs/lisensi/dataset__indo-alpr/IZIN.md",
      "vonis": "BOLEH-PRODUK",
      "dicatat": "2026-10-13",
      "catatan": "Tersimpan di data/keluaran/dataset/indo-alpr (original/train 4712, original/test 1462). Arsip dikunci di tools/vendor.lock.json; tiap berkas cocok dengan SHA-256 penerbit. Label = nomor plat di nama berkas, jadi nama berkas tidak pernah disalin ke repo. Folder augmentation tidak dipakai. SYARAT: menyebut sumber dan menautkan izin di produk. BATAS: vonis ini soal hak cipta. Soal data pribadi (plat orang lain): owner menyatakan sudah berkonsultasi dengan pihak hukum (K21, B9)."
    },
    {
      "id": "dataset-plat-lighting",
      "jenis": "dataset",
      "nama": "Indonesian License Plate Lighting Dataset: 561 gambar berkotak plat",
      "sumber": "https://github.com/salsabilaputri95/Indonesian-License-Plate-Lighting-Dataset",
      "lisensi": "CC BY 4.0 (README.md, README.dataset.txt, data.yaml pada commit e5bfbd8; tanpa berkas LICENSE)",
      "bukti_lisensi": "docs/lisensi/dataset__plat-lighting/IZIN.md",
      "vonis": "BOLEH-PRODUK",
      "dicatat": "2026-10-13",
      "catatan": "Tersimpan di data/keluaran/dataset/plat-lighting (latih 393, validasi 84, uji 84). Arsip dikunci di tools/vendor.lock.json. Label = kotak letak plat, tanpa teks plat. Buku catatan a.ipynb tidak dibuka. SYARAT: menyebut sumber. BATAS: tanpa berkas LICENSE. Soal data pribadi (plat orang lain): owner menyatakan sudah berkonsultasi dengan pihak hukum (K21, B9)."
    }
```

Run: `node tools/bahan.mjs periksa; echo "EXIT=$?"`
Expected: `11 bahan tercatat: BOLEH-PRODUK=2, RISET-SAJA=1, DILARANG=0, BELUM-JELAS=8` dan `EXIT=0`.

- [ ] **Step 2: Buktikan pemeriksa mesin jualan menerima keduanya dan tetap menolak video**

Run:

```bash
mkdir -p data/keluaran/coba-manifes
printf '{"nama":"coba-bersih","tujuan":"jualan","bahan":["dataset-indo-alpr","dataset-plat-lighting"]}' > data/keluaran/coba-manifes/bersih.json
printf '{"nama":"coba-campur","tujuan":"jualan","bahan":["dataset-indo-alpr","video-riset-youtube"]}' > data/keluaran/coba-manifes/campur.json
node tools/periksa-jualan.mjs data/keluaran/coba-manifes/bersih.json; echo "EXIT bersih=$?"
node tools/periksa-jualan.mjs data/keluaran/coba-manifes/campur.json; echo "EXIT campur=$?"
```

Expected: `EXIT bersih=0`; `EXIT campur=1` dengan pesan yang menyebut `video-riset-youtube`. Ini bukti rantai: vonis
yang baru dicatat benar-benar sampai ke pemeriksa.

Run: `rm data/keluaran/coba-manifes/bersih.json data/keluaran/coba-manifes/campur.json && rmdir data/keluaran/coba-manifes`

- [ ] **Step 3: Tambahkan bagian dataset di `docs/VONIS-LISENSI.md`**

Di akhir berkas, tambahkan:

```markdown
## Dataset (Rencana 4, 13 Okt 2026)

Vonis di bawah ini soal **hak cipta**. Plat kendaraan orang lain adalah data pribadi; soal itu owner menyatakan sudah
berkonsultasi dengan pihak hukum (K21, 14 Okt; `OPEN-QUESTIONS.md` B9). Agen tidak melihat hasil konsultasinya.

| Bahan | Izin yang tertulis | Bukti | Vonis | Syarat dan batas |
|---|---|---|---|---|
| INDO-ALPR, bagian `original` | CC BY 4.0 | [`lisensi/dataset__indo-alpr/IZIN.md`](lisensi/dataset__indo-alpr/IZIN.md) | `BOLEH-PRODUK` | Menyebut sumber, menautkan izin, menandai perubahan. Folder `augmentation` tidak dipakai |
| Indonesian License Plate Lighting Dataset | CC BY 4.0, tanpa berkas LICENSE | [`lisensi/dataset__plat-lighting/IZIN.md`](lisensi/dataset__plat-lighting/IZIN.md) | `BOLEH-PRODUK` | Menyebut sumber. Pernyataan izin hanya di README dan `data.yaml` |
```

- [ ] **Step 4: Catat pintu ketiga di `CLAUDE.md`**

Di `CLAUDE.md` §7, ganti butir terakhir:

```markdown
- Yang dijalankan lewat Docker hanya lewat pintunya: `tools\ambil-video.ps1` (pengunduh video, berjaringan, hanya
  melihat folder video) dan `tools\lab.ps1` (lab, tanpa jaringan, repo read-only).
```

menjadi:

```markdown
- Yang dijalankan lewat Docker hanya lewat pintunya: `tools\ambil-video.ps1` (pengunduh video, berjaringan, hanya
  melihat folder video), `tools\ambil-berkas.ps1` (pengunduh arsip dataset, berjaringan, hanya butir yang tercatat di
  kunci dan hanya melihat satu folder unduhan), dan `tools\lab.ps1` (lab, tanpa jaringan, repo read-only).
- Sesudah mengunduh video: `tools/lab/periksa_utuh.py` di lab, baru `tools/manifes-video.mjs`. Arsip dataset hanya
  dibuka di lab oleh `tools/lab/buka_arsip.py`, sesudah SHA-256-nya dikunci.
- Nama berkas dataset INDO-ALPR adalah nomor plat: tidak dicetak, tidak disalin ke repo, tidak didaftar dengan `ls`.
```

- [ ] **Step 5: Catat hasil di `OPEN-QUESTIONS.md`**

Di bagian B, tepat di atas paragraf `**Sesudah K21 (14 Okt):**`, tambahkan (angka bersudut
diisi dari keluaran Task 5 dan Task 6):

```markdown
**Sesudah Rencana 4 Fase 0A (<tanggal>):** dua dataset berizin jual tersimpan dan terkunci: INDO-ALPR bagian asli
(<jumlah> gambar, labelnya nomor plat di nama berkas) dan dataset pencahayaan (<jumlah> gambar berkotak plat, tanpa
teks plat). Ini bahan pertama yang boleh masuk mesin jualan. **Yang belum diketahui:** apakah INDO-ALPR berisi potongan
plat atau foto adegan, berapa bagian motornya, dan apakah bagian latih dan ujinya memuat plat yang sama; itu dijawab
ikhtisar di Rencana 5. **Bagi B9:** soal data pribadi bersandar pada pernyataan owner (K21).
```

- [ ] **Step 6: Catat di `ROADMAP.md`**

Tulis skrip pencatat sebagai **berkas** di folder kerja sementara (bukan `node -e`), dengan pola yang sama seperti
pencatat sebelumnya: baca berkas dengan `\r\n` diseragamkan, periksa tiap jangkar ketemu tepat sekali sebelum menulis.
Perubahannya:

1. Baris status keseluruhan: ganti `— RENCANA 4 SEDANG DIJALANKAN.`
   dengan `· RENCANA 4 FASE 0A SELESAI: DUA DATASET BERIZIN JUAL TERSIMPAN — BERIKUTNYA: MENULIS RENCANA 5.`
2. Butir `- [ ] Rencana 4 Fase 0A dijalankan ← di sini sekarang (lampu hijau owner 14 Okt: "lanjutkan")` diganti dua butir:
   - `- [x] Rencana 4 Fase 0A dijalankan <tanggal>: <ringkasan satu kalimat dengan angka>. Gerbang uji: Node 75 → <angka>, lab 9 → <angka>, semuanya hijau`
   - `- [ ] Rencana 5 Fase 0A ditulis (ikhtisar isi dataset, pelabel otomatis di laptop, lembar contoh untuk owner, set uji pertama) ← di sini sekarang`
3. Di "Temuan di luar lingkup", baris "Berkas `.mp4` yang ada belum tentu utuh": kolom Status diganti
   `**Diperbaiki di repo ini** (Rencana 4 Task 1): pemeriksa menjadi alat beruji, dan manifes menolak video baru yang belum lulus`.
4. Di baris pertama tabel itu (pengunduh keluar 0 saat terpotong), kalimat "Sisa yang belum tertangani: ..." ditambah
   `Di pintu berkas yang baru, keadaan itu dilaporkan gagal (kode 9); di pintu video belum.`
5. Satu baris changelog baru di akhir, memuat: apa yang berubah · hasil dengan angka yang terbaca · alasan pemecahan
   rencana · batas (gambar belum dilihat; isi dataset belum diketahui; B9 bersandar pada pernyataan owner; tidak ada CI).

- [ ] **Step 7: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 99` dan `51 passed`, keduanya `EXIT=0`.

Run: `git status --short`
Expected: hanya berkas catatan dan `data-asal/bahan.json`. Tidak ada berkas dari `data/`.

```bash
git add data-asal/bahan.json docs/VONIS-LISENSI.md CLAUDE.md OPEN-QUESTIONS.md ROADMAP.md plans/2026-10-13-fase-0a-rencana-4-bahan-berizin.md
git commit -q -F - <<'EOF'
Catat hasil Rencana 4 Fase 0A (dua dataset berizin jual)

Alasan: daftar bahan sampai hari ini tidak punya satu pun butir yang boleh
masuk mesin jualan. Dua dataset ini yang pertama, jadi vonis, syarat, dan
batasnya harus tertulis sebelum dipakai.

Vonisnya soal hak cipta. Soal data pribadi (plat orang lain) bersandar
pada pernyataan owner bahwa pihak hukum sudah dimintai nasihat (K21).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

- [ ] **Step 8: Laporkan ke owner, dengan dua hal yang menjadi keputusannya**

1. **Vonis `BOLEH-PRODUK` untuk kedua dataset** adalah bacaan agen atas izin hak ciptanya. Cara membaliknya: ubah
   kolom `vonis` di `data-asal/bahan.json`; pemeriksa mesin jualan langsung menolaknya.
2. **P14** (arti "larangan" menurut K21) belum perlu dijawab untuk kedua dataset ini, karena keduanya CC BY 4.0. Ia
   ditanyakan saat bahan mesin jualan dipilih.

---

## Pemeriksaan diri atas rencana ini

- **Cakupan spec:** 8.1 langkah 4 "mengambil dua dataset berizin jual" → Task 5 dan 6. "Tiap unduhan tercatat asal,
  izin, dan SHA-256-nya" (8.6) → kunci vendor, `IZIN.md`, `bahan.json`. "Dataset riset lain" dan "pembuat plat buatan
  komputer" dari langkah yang sama **tidak** ada di rencana ini: dataset riset menunggu ikhtisar dua dataset ini
  (Rencana 5), plat buatan menunggu P13 (Rencana 6).
- **Tanpa isian kosong pada kode:** semua kode alat dan uji tertulis lengkap. Isian bersudut hanya ada pada angka dan
  kutipan yang baru ada sesudah unduhan, dan tiap isian menyebut dari keluaran langkah mana ia dibaca.
- **Nama yang konsisten:** `Ditolak` dan `TakCocok` (pengunduh), `Ditolak` (pembuka), `sidik_berkas` di tiga alat,
  `utama(argumen=None)` di tiga alat lab yang diuji langsung.
- **Angka gerbang:** Node 75 → 79 → 99. Lab 9 → 16 → 30 → 43 → 51.
