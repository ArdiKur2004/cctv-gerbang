# Fase 0A, Rencana 3: Perbaikan pemindai dan pemilahan 45 video — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Menutup lubang pemindai yang ditemukan di Rencana 2, lalu mengetahui apa isi 45 video riset (sudut kamera,
siang atau malam, jenis kendaraan) tanpa satu pun plat yang terbaca keluar dari laptop.

**Architecture:** Pemindai statis diberi pola unduhan yang selama ini lolos. Untuk pemilahan, satu skrip Python
dijalankan di lab tanpa jaringan: tiap video dicuplik delapan gambar, tiap gambar dikecilkan menjadi 48 piksel dan
dikaburkan, lalu semuanya disusun menjadi tiga lembar ikhtisar. Owner memeriksa lembar itu lebih dulu; baru sesudah
owner menyatakan platnya tidak terbaca, agen membukanya dan mengisi kolom pemilahan di manifes video (K19).

**Tech Stack:** Node 24 (`node:test`) untuk pemindai · Python 3.12 dengan OpenCV 4.14 dan pytest 9.1 **yang sudah ada
di image lab** (diperiksa 13 Okt) · `tools\lab.ps1`. Tidak ada yang dipasang dan tidak ada yang diunduh.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md)
bagian 8.1 langkah 4 (sebagian) dan bagian 8.5. Keputusan K17 dan K19 di [`../SEED.md`](../SEED.md) §3. Temuan
pemindai di [`../ROADMAP.md`](../ROADMAP.md), "Temuan di luar lingkup".

---

## Penyesuaian pembagian rencana

Rencana 2 menulis bahwa Rencana 3 memuat lima hal sekaligus. Itu terlalu besar untuk ditulis lengkap dalam satu
rencana, jadi dipecah. Urutannya mendahulukan yang paling tidak diketahui: isi 45 video.

| Rencana | Isi | Status |
|---|---|---|
| 1 | Bengkel | Selesai 13 Okt |
| 2 | Vonis izin komponen; peraturan plat | Selesai 13 Okt |
| **3 (dokumen ini)** | Perbaikan pemindai; pemilahan 45 video (K19) | Ditulis |
| 4 | Pintu unduh berkas; dataset berizin; pelabel otomatis di laptop; lembar contoh untuk owner; set uji pertama | Ditulis saat Rencana 3 selesai |
| 5 | Pembuat plat buatan komputer; pembanding; mesin belajar pertama; taksiran kecepatan; laporan ke `bukti/` | Ditulis saat Rencana 4 selesai dan P13 dijawab |

## Aturan eksekusi untuk semua task

- **Agen tidak membuka satu pun lembar ikhtisar sebelum owner menyatakan platnya tidak terbaca** (K19). Ini berlaku
  juga untuk berkas gambar lain di `data/`: agen tidak pernah membuka gambar atau video riset apa adanya.
- **Satu suite uji pada satu waktu.** Tanpa `| tail` atau `| head` pada perintah uji.
- **Dua gerbang uji:** `npm test` (Node, di host) dan `npm run test:lab` (Python, di lab tanpa jaringan). Kode 3 dari
  gerbang lab berarti bengkel sedang dipakai job lain (misalnya vision-seed); itu bukan uji merah.
- **Satu job lab pada satu waktu:** periksa `nvidia-smi` sebelum pekerjaan lab yang lama.
- **vision-seed hanya dibaca.**
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri baris
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Semua perintah dijalankan dari akar repo `D:\Projects\super-team-v1\cctvgerbang-seed` lewat Git Bash, kecuali
  disebut lain.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/audit-repo.mjs` (ubah) | Aturan `unduh-otomatis` ditambah tiga pola yang lolos | 1 |
| `tools/uji/audit-repo.test.mjs` (ubah) | Uji untuk pola-pola itu | 1 |
| `tools/lab/lembar_kecil.py` (baru) | Membuat lembar ikhtisar: gambar dikecilkan dan dikaburkan | 2 |
| `tools/lab/uji/test_lembar_kecil.py` (baru) | Uji bahwa goresan huruf hilang dan bentuk besar bertahan | 2 |
| `package.json` (ubah) | Perintah `npm run test:lab` | 2 |
| `data-asal/video-riset.json` (ubah) | Kolom `sudut`, `kategori`, `isi` tiap video diisi | 3 |
| `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Gerbang lab dicatat; hasil pemilahan dicatat | 4 |

---

### Task 1: Pemindai mengenali unduhan yang selama ini lolos

Rencana 2 menemukan lima jalur unduhan di enam komponen yang tidak ditandai `tools/audit-repo.mjs`: dua lewat
`urllib.request.urlopen`, dua lewat `requests.get(..., stream=True)`, dan satu lewat
`torch.hub.load_state_dict_from_url`.

**Files:**
- Modify: `tools/audit-repo.mjs`
- Test: `tools/uji/audit-repo.test.mjs`

- [ ] **Step 1: Catat angka sebelum pada komponen nyata**

Run:

```bash
for n in fast-plate-ocr open-image-models yolox trackers rf-detr; do
  node tools/audit-repo.mjs "vendor/$n" --json "$TEMP/sebelum-$n.json" > /dev/null
  node -e 'const h=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));console.log(process.argv[2].padEnd(18), h.temuan.filter(t=>t.aturan==="unduh-otomatis").length)' "$TEMP/sebelum-$n.json" "$n"
done
```

Expected: `fast-plate-ocr 1`, `open-image-models 0`, `yolox 0`, `trackers 3`, `rf-detr 14`. Angka ini dibandingkan lagi
di Step 5.

- [ ] **Step 2: Tulis uji yang gagal**

Tambahkan di akhir `tools/uji/audit-repo.test.mjs`:

```js
// Celah nyata 2026-10-13 (Rencana 2 Fase 0A): lima jalur unduhan di enam komponen calon tidak ditandai, karena aturan
// unduh-otomatis hanya mengenal urlretrieve, wget, curl, dan pustaka Hugging Face. Tiap pola di bawah HARUS tertangkap.
test('unduh-otomatis: urlopen, requests ber-stream, dan torch.hub.load_state_dict_from_url tertangkap per berkas', () => {
  const pengunduh = {
    'hub_urlopen.py': 'with urllib.request.urlopen(url) as response:\n    data = response.read()',
    'unduh_requests.py': 'response = requests.get(url, stream=True, timeout=timeout)',
    'bobot_torch.py': 'ckpt = load_state_dict_from_url(weights_url, map_location="cpu")',
  };
  const h = pindai(buatRepo(pengunduh));
  for (const berkas of Object.keys(pengunduh)) {
    assert.ok(h.temuan.some((t) => t.aturan === 'unduh-otomatis' && t.berkas === berkas), `unduhan di ${berkas} seharusnya tertangkap`);
  }
});

test('unduh-otomatis: panggilan requests biasa tanpa stream TIDAK dituduh mengunduh berkas', () => {
  // Panggilan jaringan biasa sudah ditandai aturan pustaka-jaringan; menandainya dua kali hanya menambah derau.
  const h = pindai(buatRepo({ 'api.py': 'r = requests.get("https://github.com/org/repo/releases", timeout=5)' }));

  assert.ok(!h.temuan.some((t) => t.aturan === 'unduh-otomatis'), 'requests.get tanpa stream bukan unduh-otomatis');
});
```

- [ ] **Step 3: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 75`, `ℹ fail 1`, `EXIT=1`. Uji pertama gagal dengan pesan
`unduhan di hub_urlopen.py seharusnya tertangkap`. Uji kedua sudah lulus (perilaku itu memang sudah begitu) dan menjaga
supaya perbaikan tidak kebablasan.

- [ ] **Step 4: Perluas aturan `unduh-otomatis`**

Di `tools/audit-repo.mjs`, ganti baris

```js
    cocok: (b) => /\bhf_hub_download\b|\bsnapshot_download\b|\.from_pretrained\s*\(|\bgdown\b|\burlretrieve\s*\(|\bwget\s+['"]?https?:|\bcurl\s+[^\n]*https?:\/\//.test(b) },
```

menjadi

```js
    cocok: (b) => /\bhf_hub_download\b|\bsnapshot_download\b|\.from_pretrained\s*\(|\bgdown\b|\burlretrieve\s*\(|\bwget\s+['"]?https?:|\bcurl\s+[^\n]*https?:\/\//.test(b)
      // Ditambah 2026-10-13: tiga pola yang lolos pada komponen calon (lihat uji).
      || /\burlopen\s*\(/.test(b) || /\bload_state_dict_from_url\b/.test(b) || /\brequests\.get\s*\([^)\n]*\bstream\s*=\s*True/.test(b) },
```

Lalu ganti baris asal-usul di kepala berkas

```js
// Asal: disalin apa adanya dari vision-seed @3591530 (tools/audit-repo.mjs) pada 2026-10-13 (K14).
```

menjadi

```js
// Asal: disalin dari vision-seed @3591530 (tools/audit-repo.mjs) pada 2026-10-13 (K14). Yang diubah di sini: aturan
// unduh-otomatis ditambah urlopen, requests ber-stream, dan torch.hub.load_state_dict_from_url.
```

- [ ] **Step 5: Jalankan uji, lalu buktikan pada komponen nyata**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 75`, `ℹ pass 75`, `ℹ fail 0`, `EXIT=0`

Run:

```bash
for n in fast-plate-ocr open-image-models yolox trackers rf-detr; do
  node tools/audit-repo.mjs "vendor/$n" --json "$TEMP/sesudah-$n.json" > /dev/null
  node -e 'const h=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));const u=h.temuan.filter(t=>t.aturan==="unduh-otomatis");console.log(process.argv[2].padEnd(18), u.length);for(const t of u.filter(t=>/hub\.py|build\.py|downloader\.py|utilities\/files\.py/.test(t.berkas)))console.log("   ", t.berkas+":"+t.baris)' "$TEMP/sesudah-$n.json" "$n"
done
```

Expected: tiap angka **naik** dibanding Step 1, dan lima jalur yang dulu ditemukan dengan tangan kini tercetak:
`fast_plate_ocr/inference/hub.py`, `open_image_models/detection/core/hub.py`, `yolox/models/build.py`,
`src/trackers/utils/downloader.py`, dan `src/rfdetr/utilities/files.py`. Bila salah satu tidak tercetak, polanya belum
menutup jalur itu: perbaiki polanya, jangan lanjut.

Laporan di `docs/audit/` **tidak ditulis ulang**: bagian "Dibaca manual"-nya sudah memuat kelima jalur itu.

- [ ] **Step 6: Commit**

```bash
git add tools/audit-repo.mjs tools/uji/audit-repo.test.mjs
git commit -q -F - <<'EOF'
Pemindai: kenali unduhan lewat urlopen, requests ber-stream, dan torch.hub

Rencana 2 menemukan lima jalur unduhan di enam komponen calon yang tidak
ditandai pemindai, dan semuanya baru ketemu lewat pencarian tangan. Aturan
unduh-otomatis hanya mengenal urlretrieve, wget, curl, dan pustaka Hugging
Face.

Tiga pola ditambahkan. Panggilan requests biasa tanpa stream sengaja tidak
ikut ditandai: itu sudah tugas aturan pustaka-jaringan, dan menandainya dua
kali hanya menambah derau. Ada uji yang menjaga batas itu.

Dibuktikan pada komponen nyata: kelima jalur yang dulu lolos kini tercetak.
Cacat yang sama masih ada di vision-seed; dicatat di ROADMAP, tidak
diperbaiki dari workspace ini.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Alat pembuat lembar ikhtisar

Tiap gambar dikecilkan sampai sisi terpanjangnya 48 piksel, lalu dikaburkan. Angkanya bukan tebakan bebas: dengan
anggapan terburuk bahwa sebuah plat berisi delapan huruf memenuhi lebar layar, tiap huruf mendapat enam piksel, dan
kabur Gauss bersimpangan baku 1,5 piksel menyisakan kurang dari sepersepuluh kontras pada rincian sehalus goresan
huruf. Bentuk besar (langit gelap atau terang, mobil atau motor, kamera diam atau bergerak) tetap terlihat.

**Itu hitungan, bukan bukti.** Buktinya ada dua: uji di bawah, dan mata owner di Task 3.

**Files:**
- Create: `tools/lab/lembar_kecil.py`
- Test: `tools/lab/uji/test_lembar_kecil.py`
- Modify: `package.json`

- [ ] **Step 1: Tambahkan perintah gerbang lab**

Ganti isi `package.json` menjadi:

```json
{
  "name": "cctvgerbang-seed",
  "private": true,
  "description": "CCTV Gerbang: alat bengkel. Gerbang uji: npm test (Node) dan npm run test:lab (Python, di lab tanpa jaringan)",
  "scripts": {
    "test": "node --test \"tools/uji/*.test.mjs\"",
    "test:lab": "powershell -NoProfile -File tools/lab.ps1 python -m pytest /kerja/tools/lab/uji -q -p no:cacheprovider"
  }
}
```

- [ ] **Step 2: Tulis uji yang gagal**

Buat `tools/lab/uji/test_lembar_kecil.py`:

```python
"""Uji tools/lab/lembar_kecil.py (K19): gambar untuk agen harus terlalu kasar untuk membaca plat, tetapi masih cukup
untuk memilah sudut kamera, siang atau malam, dan jenis kendaraan."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_kecil as lk  # noqa: E402


def garis_tegak(siklus, lebar=1920, tinggi=1080):
    """Gambar garis hitam-putih tegak: `siklus` pasang garis selebar layar."""
    x = np.arange(lebar)
    baris = np.where((x * siklus * 2 // lebar) % 2 == 0, 255, 0).astype(np.uint8)
    return np.repeat(np.tile(baris, (tinggi, 1))[:, :, None], 3, axis=2)


def kontras(gambar):
    """Selisih terang-gelap di tengah gambar, 0 sampai 1."""
    abu = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY).astype(np.float32)
    t, l = abu.shape
    tengah = abu[t // 2, l // 4: 3 * l // 4]
    return float(tengah.max() - tengah.min()) / 255.0


def test_sisi_terpanjang_menjadi_48_piksel():
    kecil = lk.kecilkan(np.zeros((1080, 1920, 3), np.uint8))

    assert max(kecil.shape[:2]) == 48
    assert kecil.shape[:2] == (27, 48)


def test_video_tegak_juga_dikecilkan_dari_sisi_terpanjangnya():
    kecil = lk.kecilkan(np.zeros((1920, 1080, 3), np.uint8))

    assert kecil.shape[:2] == (48, 27)


def test_rincian_sehalus_goresan_huruf_hilang():
    # Anggapan terburuk: plat delapan huruf memenuhi lebar layar. Membedakan huruf butuh rincian sekitar satu setengah
    # pasang garis per huruf, yaitu 12 pasang garis selebar layar. Sesudah dikecilkan dan dikaburkan, kontrasnya harus
    # hampir habis.
    assert kontras(lk.kecilkan(garis_tegak(12))) < 0.15


def test_bentuk_besar_tetap_terlihat():
    # Dua pasang garis selebar layar mewakili bentuk besar: kendaraan, langit, jalan. Ini harus bertahan, kalau tidak
    # lembarnya tidak berguna untuk memilah.
    assert kontras(lk.kecilkan(garis_tegak(2))) > 0.5


def test_satu_video_menjadi_satu_baris_berisi_delapan_gambar(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    tulis = cv2.VideoWriter(str(folder / "youtube-contoh.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for i in range(40):
        tulis.write(np.full((240, 320, 3), i * 6, np.uint8))
    tulis.release()
    keluar = tmp_path / "keluar"

    kode = lk.utama(str(folder), str(keluar))

    assert kode == 0
    lembar = cv2.imread(str(keluar / "ikhtisar-1.png"))
    sisi = lk.SISI * lk.PERBESAR
    assert lembar.shape == (sisi, lk.LEBAR_NOMOR + lk.PER_VIDEO * sisi, 3)
    daftar = json.loads((keluar / "ikhtisar.json").read_text())
    assert daftar["sisi"] == 48 and daftar["halaman"] == ["ikhtisar-1.png"]
    assert daftar["video"] == [{"nomor": 1, "berkas": "youtube-contoh.mp4", "gambar": 8}]


def test_berkas_yang_bukan_video_dilewati(tmp_path):
    folder = tmp_path / "video"
    folder.mkdir()
    (folder / "youtube-contoh.info.json").write_text("{}")
    keluar = tmp_path / "keluar"

    kode = lk.utama(str(folder), str(keluar))

    assert kode == 0
    assert json.loads((keluar / "ikhtisar.json").read_text())["video"] == []
```

- [ ] **Step 3: Jalankan uji untuk memastikan gagal**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
Expected: satu baris pemakaian memori. Bila sebuah job sedang melatih, tunggu sampai selesai.

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `EXIT` bukan 0, dengan galat `ModuleNotFoundError: No module named 'lembar_kecil'`. Itu merah karena alatnya
belum ada. Bila yang tercetak `bengkel sedang dipakai job lab lain` dengan kode 3, itu bukan uji merah: tunggu dan
ulangi.

- [ ] **Step 4: Tulis `tools/lab/lembar_kecil.py`**

```python
"""Lembar ikhtisar gambar kecil untuk memilah video riset (keputusan owner K19).

Agen hanya boleh melihat gambar yang platnya tidak terbaca. Tiap video dicuplik beberapa gambar; tiap gambar dikecilkan
sampai sisi terpanjangnya SISI piksel lalu dikaburkan; hasilnya disusun satu baris per video. Yang tersisa cukup untuk
memilah sudut kamera, siang atau malam, dan jenis kendaraan.

Hitungan di balik angkanya (anggapan terburuk: plat delapan huruf memenuhi lebar layar): pada 48 piksel tiap huruf
mendapat 6 piksel, dan kabur Gauss bersimpangan baku 1,5 piksel menyisakan kurang dari sepersepuluh kontras pada rincian
sehalus goresan huruf. Itu hitungan, bukan bukti: owner memeriksa lembarnya sebelum agen membukanya.

Dijalankan di lab tanpa jaringan:
  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

SISI = 48  # sisi terpanjang tiap gambar, piksel
KABUR = 1.5  # simpangan baku kabur Gauss, piksel, diterapkan SESUDAH gambar dikecilkan
PERBESAR = 3  # tiap gambar diperbesar tanpa menambah rincian, supaya enak dilihat
PER_VIDEO = 8  # jumlah gambar per video
PER_HALAMAN = 15  # jumlah video per lembar
LEBAR_NOMOR = 60  # lebar kolom nomor urut di kiri tiap baris, piksel
AKHIRAN_VIDEO = {".mp4", ".webm", ".mkv", ".mov"}


def kecilkan(gambar):
    """Mengecilkan gambar sampai sisi terpanjangnya SISI piksel, lalu mengaburkannya."""
    tinggi, lebar = gambar.shape[:2]
    skala = SISI / max(tinggi, lebar)
    ukuran = (max(1, round(lebar * skala)), max(1, round(tinggi * skala)))
    kecil = cv2.resize(gambar, ukuran, interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(kecil, (0, 0), KABUR)


def cuplik(jalur, jumlah=PER_VIDEO):
    """Mengambil `jumlah` gambar yang tersebar rata dari satu video, masing-masing sudah dikecilkan."""
    baca = cv2.VideoCapture(str(jalur))
    total = int(baca.get(cv2.CAP_PROP_FRAME_COUNT))
    hasil = []
    if total > 0:
        for i in range(jumlah):
            baca.set(cv2.CAP_PROP_POS_FRAMES, int((i + 0.5) * total / jumlah))
            ada, gambar = baca.read()
            if ada:
                hasil.append(kecilkan(gambar))
    baca.release()
    if len(hasil) < jumlah:
        # Sebagian berkas tidak bisa diloncati (aliran HLS di dalam mp4). Baca berurutan dan ambil tiap selang tetap.
        hasil = []
        baca = cv2.VideoCapture(str(jalur))
        selang = max(1, total // jumlah) if total > 0 else 30
        nomor = 0
        while len(hasil) < jumlah:
            ada, gambar = baca.read()
            if not ada:
                break
            if nomor % selang == selang // 2:
                hasil.append(kecilkan(gambar))
            nomor += 1
        baca.release()
    return hasil


def petak(gambar):
    """Menaruh satu gambar kecil di tengah petak bujur sangkar berukuran tetap."""
    besar = cv2.resize(gambar, None, fx=PERBESAR, fy=PERBESAR, interpolation=cv2.INTER_NEAREST)
    sisi = SISI * PERBESAR
    kanvas = np.zeros((sisi, sisi, 3), np.uint8)
    tinggi, lebar = besar.shape[:2]
    atas, kiri = (sisi - tinggi) // 2, (sisi - lebar) // 2
    kanvas[atas:atas + tinggi, kiri:kiri + lebar] = besar
    return kanvas


def baris(nomor, gambar):
    """Satu baris lembar: nomor urut video di kiri, lalu PER_VIDEO petak."""
    sisi = SISI * PERBESAR
    kolom_nomor = np.zeros((sisi, LEBAR_NOMOR, 3), np.uint8)
    cv2.putText(kolom_nomor, str(nomor), (4, sisi // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    kosong = [np.zeros((sisi, sisi, 3), np.uint8)] * (PER_VIDEO - len(gambar))
    return np.hstack([kolom_nomor] + [petak(g) for g in gambar] + kosong)


def utama(folder, keluar):
    folder, keluar = Path(folder), Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    video = sorted(p for p in folder.iterdir() if p.suffix.lower() in AKHIRAN_VIDEO)
    daftar, barisan = [], []
    for nomor, jalur in enumerate(video, 1):
        gambar = cuplik(jalur)
        daftar.append({"nomor": nomor, "berkas": jalur.name, "gambar": len(gambar)})
        barisan.append(baris(nomor, gambar))
    halaman = []
    for awal in range(0, len(barisan), PER_HALAMAN):
        nama = f"ikhtisar-{awal // PER_HALAMAN + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_HALAMAN]))
        halaman.append(nama)
    catatan = {"sisi": SISI, "kabur": KABUR, "perbesar": PERBESAR, "per_video": PER_VIDEO, "halaman": halaman, "video": daftar}
    (keluar / "ikhtisar.json").write_text(json.dumps(catatan, indent=2))
    print(f"{len(video)} video -> {len(halaman)} lembar di {keluar}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Pakai: python lembar_kecil.py <folder-video> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(sys.argv[1], sys.argv[2]))
```

- [ ] **Step 5: Jalankan kedua gerbang untuk memastikan lulus**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `6 passed` dan `EXIT=0`

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 75`, `ℹ fail 0`, `EXIT=0`

Run: `git status --short`
Expected: hanya `package.json`, `tools/lab/lembar_kecil.py`, dan `tools/lab/uji/test_lembar_kecil.py`. Tidak boleh ada
`__pycache__` atau `.pytest_cache`: repo dipasang read-only di lab.

- [ ] **Step 6: Commit**

```bash
git add package.json tools/lab/lembar_kecil.py tools/lab/uji/test_lembar_kecil.py
git commit -q -F - <<'EOF'
Alat pembuat lembar ikhtisar gambar kecil (K19)

Owner memutuskan agen hanya boleh melihat gambar yang platnya tidak
terbaca. Alat ini mengecilkan tiap gambar menjadi 48 piksel lalu
mengaburkannya, dan menyusun satu baris per video.

Angkanya dari hitungan dengan anggapan terburuk (plat delapan huruf
memenuhi lebar layar), dan dijaga dua uji yang saling menahan: rincian
sehalus goresan huruf harus hilang, bentuk besar harus bertahan. Hitungan
itu bukan bukti; owner memeriksa lembarnya sebelum agen membukanya.

Uji Python dijalankan di lab tanpa jaringan lewat gerbang kedua,
`npm run test:lab`, dengan pustaka yang sudah ada di image lab.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Membuat ikhtisar, diperiksa owner, lalu dipilah

**Files:**
- Modify: `data-asal/video-riset.json`

- [ ] **Step 1: Buat lembar ikhtisar dari 45 video**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_kecil.py /kerja/data/video/riset /kerja/data/keluaran/lembar-kecil; "EXIT=$LASTEXITCODE"`
Expected: `45 video -> 3 lembar di /kerja/data/keluaran/lembar-kecil` dan `EXIT=0`.

Run: `node -e 'const d=JSON.parse(require("fs").readFileSync("data/keluaran/lembar-kecil/ikhtisar.json","utf8"));console.log(d.video.length, d.halaman.join(","), d.video.filter(v=>v.gambar<8).map(v=>v.berkas+":"+v.gambar).join(" ")||"semua 8 gambar")'`
Expected: `45 ikhtisar-1.png,ikhtisar-2.png,ikhtisar-3.png semua 8 gambar`. Bila ada video dengan kurang dari delapan
gambar, catat namanya; video dengan nol gambar tidak bisa dipilah dan ditulis begitu di Step 4.

Run: `git status --short`
Expected: kosong. Lembar ada di `data/`, yang tidak masuk git.

- [ ] **Step 2: BERHENTI. Minta owner memeriksa lembarnya**

Agen **tidak membuka** berkas `ikhtisar-*.png`. Minta owner membuka tiga berkas ini di laptop:

```
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-kecil\ikhtisar-1.png
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-kecil\ikhtisar-2.png
D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-kecil\ikhtisar-3.png
```

dan menjawab satu hal: adakah satu saja plat nomor, atau tulisan nomor plat di layar, yang masih bisa dibaca?

| Jawaban owner | Lanjutannya |
|---|---|
| "Tidak ada yang terbaca" | Lanjut ke Step 3 |
| "Ada yang terbaca" (owner menyebut nomor barisnya) | Agen tetap tidak membuka lembarnya. Turunkan `SISI` di `tools/lab/lembar_kecil.py` dari 48 ke 32, sesuaikan angka 48 dan `(27, 48)` / `(48, 27)` di ujinya menjadi 32 dan `(18, 32)` / `(32, 18)`, jalankan `npm run test:lab` sampai hijau, ulangi Step 1, lalu minta owner memeriksa lagi. Bila pada 32 pun masih terbaca, berhenti dan laporkan: cara ini tidak cukup, dan pemilahan dikerjakan owner (pilihan C di K19) |

- [ ] **Step 3: Agen membuka ketiga lembar dan memilah**

Hanya sesudah owner menjawab "tidak ada yang terbaca". Buka ketiga lembar dengan alat baca berkas. Tiap baris diawali
nomor urut; padankan nomor itu dengan nama berkas lewat `data/keluaran/lembar-kecil/ikhtisar.json`.

Untuk tiap video, tentukan tiga hal dari delapan gambarnya:

| Kolom | Pilihan | Cara menentukan |
|---|---|---|
| `sudut` | `gerbang` · `kamera-diam-lain` · `dasbor` · `lain` | `gerbang`: kamera diam, kendaraan mendekat ke arah kamera di depan gerbang atau palang. `kamera-diam-lain`: kamera diam, tetapi jalan atau parkiran. `dasbor`: latar bergerak dari gambar ke gambar. `lain`: layar perangkat lunak, orang berbicara, peragaan miniatur, atau tidak ada kendaraan |
| `kategori` | `siang` · `malam` · `remang` · `campuran` · `tak-jelas` | Sesuai spec 8.3: malam bila langit gelap dan penerangan utamanya lampu; campuran bila gambarnya memuat keduanya |
| `isi` | Teks pendek | Apa yang tampak: misalnya "mobil", "motor", "mobil dan motor", "truk", "layar perangkat lunak", "tidak tampak kendaraan" |

**Bila sebuah baris tidak bisa ditentukan dari gambar sekecil itu, tulis apa adanya:** `sudut` dikosongkan, `kategori`
diisi `tak-jelas`, dan `isi` diisi "tidak bisa ditentukan dari gambar kecil". Jangan menebak dari judul videonya:
kolom ini mencatat yang terlihat, dan judul sudah tercatat di kolom `judul`.

- [ ] **Step 4: Tulis hasil pemilahan ke manifes**

Susun berkas `data/keluaran/lembar-kecil/pilah.json` berbentuk daftar, satu butir per video, dengan `berkas` persis
seperti di `ikhtisar.json`:

```json
[
  { "berkas": "youtube-XXXXXXXXXXX.mp4", "sudut": "gerbang", "kategori": "siang", "isi": "mobil dan motor" }
]
```

Lalu terapkan ke manifes:

```bash
node -e '
const fs=require("fs");
const pilah=JSON.parse(fs.readFileSync("data/keluaran/lembar-kecil/pilah.json","utf8"));
const m=JSON.parse(fs.readFileSync("data-asal/video-riset.json","utf8"));
const per=new Map(pilah.map(p=>[p.berkas,p]));
let terisi=0;
for(const v of m.video){const p=per.get(v.berkas); if(!p) continue; v.sudut=p.sudut; v.kategori=p.kategori; v.isi=p.isi; terisi++;}
const takDikenal=pilah.filter(p=>!m.video.some(v=>v.berkas===p.berkas)).map(p=>p.berkas);
if(takDikenal.length){console.error("berkas tak ada di manifes: "+takDikenal.join(", "));process.exit(1);}
fs.writeFileSync("data-asal/video-riset.json",JSON.stringify(m,null,2)+"\n");
console.log(terisi+" dari "+m.video.length+" video terisi");
'
```

Expected: `45 dari 45 video terisi`

Run: `node tools/manifes-video.mjs; echo "EXIT=$?"`
Expected: `45 video dicatat di ...video-riset.json` dan `EXIT=0`. Alat itu menolak nilai `sudut` di luar daftar dan
menolak video yang isinya berubah sejak dicatat, jadi keluarnya 0 berarti isian sah dan videonya utuh.

- [ ] **Step 5: Ringkas hasilnya dengan angka**

Run:

```bash
node -e '
const m=JSON.parse(require("fs").readFileSync("data-asal/video-riset.json","utf8")).video;
const hitung=(k)=>JSON.stringify(m.reduce((a,v)=>(a[v[k]||"(kosong)"]=(a[v[k]||"(kosong)"]||0)+1,a),{}));
console.log("sudut   :",hitung("sudut"));
console.log("kategori:",hitung("kategori"));
const g=m.filter(v=>v.sudut==="gerbang");
console.log("sudut gerbang:",g.length,"video,",g.reduce((a,v)=>a+(v.detik||0),0),"detik; malam:",g.filter(v=>v.kategori==="malam"||v.kategori==="campuran").length);
'
```

Expected: tiga baris angka. Angka inilah yang dilaporkan ke owner dan dicatat di Task 4; berapa pun hasilnya, ia
ditulis apa adanya.

- [ ] **Step 6: Commit**

```bash
git add data-asal/video-riset.json
git commit -q -F - <<'EOF'
Pemilahan 45 video riset: sudut kamera, siang atau malam, isi

Sejak diunduh (K17) isi video belum dilihat; yang diketahui hanya judulnya.
Kini tiap video punya tiga isian dari yang benar-benar terlihat: sudut
kamera, siang atau malam, dan jenis kendaraan.

Sesuai K19, agen hanya melihat lembar ikhtisar berisi gambar 48 piksel yang
dikaburkan, dan baru membukanya sesudah owner memeriksa lembar itu dan
menyatakan tidak ada plat yang terbaca.

Batas: dari gambar sekecil itu yang bisa dinilai hanya bentuk besar. Yang
tidak bisa ditentukan ditulis "tak-jelas", tidak ditebak dari judul. Apakah
platnya terbaca oleh mesin belum diketahui; itu pekerjaan Rencana 4.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Mencatat hasil

**Files:**
- Modify: `CLAUDE.md`
- Modify: `OPEN-QUESTIONS.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Jalankan kedua gerbang sekali lagi**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 75`, `ℹ fail 0`, `EXIT=0`

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `6 passed`, `EXIT=0`

- [ ] **Step 2: Catat gerbang kedua di `CLAUDE.md`**

Di bagian `## 7. ⚙️ Mesin (Prinsip #3)`, ganti baris

```markdown
- Gerbang uji repo ini: `npm test`. Satu suite pada satu waktu. Kode 3 dari `tools\lab.ps1` berarti bengkel sedang
  dipakai job lab lain (kuncinya dipakai bersama vision-seed); itu bukan uji merah.
```

menjadi

```markdown
- Gerbang uji repo ini ada dua: `npm test` (Node, di host) dan `npm run test:lab` (Python, di lab tanpa jaringan). Satu
  suite pada satu waktu. Kode 3 dari `tools\lab.ps1` berarti bengkel sedang dipakai job lab lain (kuncinya dipakai
  bersama vision-seed); itu bukan uji merah.
- Agen tidak pernah membuka gambar atau video riset apa adanya. Yang boleh dibuka hanya lembar ikhtisar dari
  `tools/lab/lembar_kecil.py`, dan baru sesudah owner memeriksanya (K19).
```

- [ ] **Step 3: Perbarui `OPEN-QUESTIONS.md`**

Di bagian B, tepat sebelum paragraf yang berawal `**Sesudah Rencana 2 Fase 0A (13 Okt):**`, tambahkan paragraf:

```markdown
**Sesudah Rencana 3 Fase 0A (13 Okt):** isi 45 video kini terpilah (`data-asal/video-riset.json`). <tiga baris angka
dari Task 3 Step 5, dalam kalimat>. Ini menjawab "bahan apa yang kita punya", bukan butir B mana pun: apakah platnya
terbaca mesin, dan pada kondisi apa, belum diukur.
```

Bagian dalam kurung sudut diisi dengan angka yang sebenarnya.

- [ ] **Step 4: Perbarui `ROADMAP.md`**

(a) Di daftar "Status", ganti baris

```
- [ ] Rencana 3 Fase 0A dijalankan ← di sini sekarang (menunggu lampu hijau owner)
```

menjadi

```
- [x] Rencana 3 Fase 0A dijalankan: pemindai diperbaiki (lima jalur unduhan yang dulu lolos kini tertangkap); 45 video dipilah dari lembar ikhtisar yang lebih dulu diperiksa owner (K19): <angka sudut dan kategori>. Gerbang uji: Node 73 → 75, lab 0 → 6, semuanya hijau
- [ ] Rencana 4 Fase 0A ditulis (pintu unduh berkas, dataset berizin, pelabel otomatis di laptop, lembar contoh untuk owner, set uji pertama) ← di sini sekarang
```

(b) Di tabel "Temuan di luar lingkup", pada baris temuan pemindai (yang berawal
`| 2026-10-13 | \`tools/audit-repo.mjs\` tidak menandai sebagian unduhan otomatis`), ganti
`Di repo ini: **belum diperbaiki**; untuk sementara tiap komponen yang dipindai juga dicari dengan tangan. Masuk Rencana 3`
menjadi
`Di repo ini: **diperbaiki** di Rencana 3 (tiga pola ditambahkan, dibuktikan pada lima jalur nyata)`.

(c) Di akhir tabel "Changelog", tambahkan satu baris bertanggal `2026-10-13` yang memuat: apa yang berubah di ROADMAP;
angka pemilahan apa adanya dan **artinya bagi bahan uji** (berapa video bersudut gerbang, berapa yang malam); angka
kedua gerbang uji sebelum dan sesudah; dan **batas**: pemilahan dari gambar 48 piksel hanya menilai bentuk besar,
video bertanda `tak-jelas` disebut jumlahnya, dan keterbacaan plat belum diukur.

(d) Perbarui kalimat status di kepala berkas menjadi
`· RENCANA 1 SAMPAI 3 FASE 0A SELESAI — BERIKUTNYA: MENULIS RENCANA 4 FASE 0A. P13 MASIH MENUNGGU OWNER.**`

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md OPEN-QUESTIONS.md ROADMAP.md
git commit -q -F - <<'EOF'
Catat hasil Rencana 3 Fase 0A (pemindai dan pemilahan video)

Gerbang uji kedua (lab) dan larangan membuka gambar riset apa adanya
dicatat di aturan proyek, supaya sesi berikutnya bekerja di dalam K19.

ROADMAP memuat angka pemilahan apa adanya dan artinya bagi bahan uji,
beserta batasnya: pemilahan dari gambar 48 piksel hanya menilai bentuk
besar, dan keterbacaan plat belum diukur.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
git status --short
```

Expected: `git status --short` tidak mencetak apa pun.

---

## Selesai bila

- [ ] `npm test` mencetak `ℹ tests 75`, `ℹ fail 0`; `npm run test:lab` mencetak `6 passed`.
- [ ] Kelima jalur unduhan yang dulu lolos tercetak oleh pemindai pada komponen nyata.
- [ ] Owner sudah memeriksa lembar ikhtisar **sebelum** agen membukanya, dan jawabannya dikutip di laporan.
- [ ] Ke-45 video punya isian `sudut`, `kategori`, dan `isi`, dan `node tools/manifes-video.mjs` keluar 0.
- [ ] `git status --short` kosong, dan tidak ada gambar atau video yang masuk git.
- [ ] `git -C "D:/Projects/super-team-v1/vision-seed" status --short` kosong.

## Yang sengaja tidak dikerjakan di rencana ini

- Membaca plat di video, dengan mesin maupun dengan mata: Rencana 4 (pelabel otomatis di laptop, lalu owner memeriksa
  lembar contoh).
- Mengunduh dataset atau bobot: Rencana 4, lewat pintu unduh berkas.
- Mengunduh video tambahan. Bila pemilahan menunjukkan bahan bersudut gerbang terlalu sedikit, itu dilaporkan ke owner
  sebagai temuan; gelombang unduhan kedua diputuskan sesudahnya.
