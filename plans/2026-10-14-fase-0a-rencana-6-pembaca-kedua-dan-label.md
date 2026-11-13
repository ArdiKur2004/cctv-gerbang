# Fase 0A, Rencana 6: Pembaca kedua dan pembetulan label set uji — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Set uji baca huruf yang labelnya sudah dibetulkan dengan cara yang dipilih owner (K22): pembaca kedua
(fast-plate-ocr, paket jadi) dijalankan di samping Qwen3-VL-2B; plat yang dibaca SAMA oleh kedua pembaca tetapi berbeda
dari label penerbit masuk lembar untuk diperiksa owner; jawaban owner membetulkan label; kedua pembaca dinilai ulang
terhadap label yang sudah dibetulkan.

**Architecture:** Pintu unduh berkas menerima dua host rilis GitHub. Dua berkas model fast-plate-ocr dikunci ke SHA-256
yang diterbitkan GitHub, diunduh lewat pintu itu, dan diperiksa lagi oleh gerbang berkas terkunci sebelum dimuat. Empat
alat lab baru: pembaca fast-plate-ocr (`baca_fpo.py`), pencari label yang dicurigai (`label_curiga.py`), lembar curiga
untuk owner (`lembar_curiga.py`), dan penilai ulang (`nilai_ulang.py`). Semua alat hanya mencetak hitungan; berkas
yang memuat nomor plat tinggal di `data/`.

**Tech Stack:** Python 3.12, OpenCV 4.14, NumPy, onnxruntime 1.30.0, pyyaml, rich, tqdm, dan pytest **yang sudah ada di
image lab** · kode fast-plate-ocr dari klon terkunci `vendor/fast-plate-ocr` @ `9ce7a5b` · Node untuk pintu dan kunci.
Tidak ada yang dipasang. Yang diunduh hanya dua berkas model (5,3 MB) lewat pintu unduh berkas.

**Dasar:** keputusan owner K22 (`SEED.md` §3), spec
[`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md) bagian 8.1
langkah 5 dan 6, 8.3. Laporan Rencana 5:
[`../bukti/2026-10-14-baca-huruf-pertama.md`](../bukti/2026-10-14-baca-huruf-pertama.md). Vonis izin:
[`../docs/VONIS-LISENSI.md`](../docs/VONIS-LISENSI.md).

---

## Yang diukur sebelum rencana ini ditulis (14 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Model fast-plate-ocr | 10 model di `fast_plate_ocr/inference/hub.py`. Dipilih `cct-s-v2-global-model`: versi 2 terbaru, ukuran S, berkepala wilayah | Klon terkunci @ `9ce7a5b` |
| Indonesia | Tercantum di daftar wilayah `config/latin_plate_config_v2.yaml` baris 22. Konfigurasi itu: 10 slot, alfabet `0-9A-Z_`, masukan 64×128, warna `rgb`. Konfigurasi terbitan untuk model itu baru dibaca sesudah diunduh | Klon terkunci |
| Asal bobot | Kode menunjuk `github.com/ankandrew/cnn-ocr-lp/releases/download/arg-plates/`. Repo itu sudah berganti nama menjadi `ankandrew/fast-plate-ocr` | API GitHub (`/repos/ankandrew/cnn-ocr-lp` → `ankandrew/fast-plate-ocr`) |
| Dua berkas | `cct_s_v2_global.onnx` 5.262.230 byte, digest `sha256:384bbbd2…`; `cct_s_v2_global_plate_config.yaml` 1.725 byte, digest `sha256:0335c74a…`; keduanya diunggah 2026-03-14 | API rilis GitHub, tag `arg-plates` |
| Rantai pengalihan | `github.com` (301, ganti nama) → `github.com/ankandrew/fast-plate-ocr/...` (302) → `release-assets.githubusercontent.com` (200, panjang 5.262.230) | Permintaan HEAD satu lompatan demi satu; hanya host yang dicetak |
| Pintu unduh berkas | Hanya `data.mendeley.com`, host S3 Mendeley, dan `codeload.github.com`. Tiap pengalihan diperiksa ulang ke daftar itu. Uji Node mengunci daftarnya persis | `tools/ambil-berkas.ps1` baris 39, `tools/ambil/ambil_berkas.py`, `tools/uji/ambil-berkas.test.mjs` |
| Image lab | onnxruntime 1.30.0 (penyedia TensorRT, CUDA, CPU), yaml, rich, tqdm, numpy, cv2 ada | Lab |
| Percobaan pertama kode | `from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer` berhasil di lab tanpa jaringan (tanpa model) | `data/alat-sementara/coba_fpo_impor.py` |
| Cara pakai | `LicensePlateRecognizer(device="cpu", onnx_model_path=..., plate_config_path=...)`; `run_one(gambar)` → `.plate`. Gambar NumPy harus sudah dalam mode warna konfigurasi | `plate_recognizer.py` baris 124–203, 298–385 |
| Izin | Kode MIT; bobot `BELUM-JELAS` (izin bobot tidak dinyatakan); mengunduh modelnya sendiri tanpa pemeriksaan keutuhan | `docs/VONIS-LISENSI.md`, `docs/audit/fast-plate-ocr@9ce7a5b.md` |

Akibatnya bagi rencana ini:

1. Pintu unduh berkas harus menerima `github.com` dan `release-assets.githubusercontent.com` (Task 1), dengan uji.
2. Bobot diambil lewat pintu dan dikunci ke digest GitHub (dibaca dengan skrip, tidak diketik), lalu diperiksa lagi di
   lab sebelum dimuat (Task 2). Jalur unduh otomatis fast-plate-ocr tidak pernah dipakai.
3. fast-plate-ocr dijalankan di CPU: cukup cepat untuk 1.431 gambar, dan kartu grafis tetap bebas.
4. Bobotnya `BELUM-JELAS`, jadi ia **alat lab**, bukan bagian produk (K15, K21; P13 dan P14 tidak tersentuh).

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–4 | Bengkel; vonis izin; pemilahan video; bahan berizin | Selesai 13–14 Okt |
| 5 | Pola plat; set uji baca huruf; lembar contoh; Qwen3-VL-2B | Selesai 14 Okt; owner memeriksa 60 contoh |
| **6 (dokumen ini)** | Pembaca kedua fast-plate-ocr; label yang dicurigai; pembetulan label (K22); penilaian ulang | Ditulis |
| 7 | Mesin belajar pertama untuk baca huruf; mencari plat di foto utuh dan video; plat buatan komputer; taksiran kecepatan; laporan Fase 0A | Ditulis saat Rencana 6 selesai; dipecah lagi bila terlalu besar |

## Aturan eksekusi untuk semua task

- **Nomor plat tidak keluar dari laptop** (`CLAUDE.md` §4, K19). Agen tidak membuka gambar dataset, lembar contoh, lembar
  curiga, `pembagian*.json`, `curiga.json`, `lembar-*.json`, atau `hasil.jsonl`. Yang dibaca agen hanya `ringkasan*.json`
  dan keluaran layar alat.
- **Owner menjawab dengan nomor baris saja**, tanpa mengetik nomor plat (`CLAUDE.md` §4).
- **Satu suite uji pada satu waktu.** Tanpa `| tail` atau `| head` pada perintah uji.
- **Dua gerbang uji:** `npm test` (Node) dan `npm run test:lab` (Python, di lab). Kode 3 = bengkel dipakai job lain; kode
  6 bisa berarti Docker Desktop belum menyala. Keduanya bukan uji merah.
- **Satu job kartu grafis pada satu waktu.** Rencana ini tidak memakai kartu grafis kecuali uji Qwen3-VL di `uji_gpu/`.
- **Perintah yang memuat `/kerja/...` dijalankan lewat PowerShell.** Perintah lain dari akar repo lewat Git Bash, dengan
  jalur mutlak, tanpa `cd` ke folder lain.
- **vision-seed hanya dibaca.** Skrip sekali pakai ditulis sebagai **berkas**.
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/ambil-berkas.ps1`, `tools/uji/ambil-berkas.test.mjs` (ubah) | Dua host rilis GitHub | 1 |
| `tools/lab/model_terkunci.py`, `tools/lab/uji/test_model_terkunci.py` (ubah) | Gerbang berkas unduhan terkunci | 2 |
| `tools/vendor.lock.json` (ubah) | Dua butir `berkas` model fast-plate-ocr | 2 |
| `tools/lab/baca_fpo.py`, `tools/lab/uji/test_baca_fpo.py` (baru) | Pembaca fast-plate-ocr | 3 |
| `tools/lab/uji_gpu/test_model_baca_fpo.py` (baru) | Uji model sungguhan, di luar gerbang | 3 |
| `tools/lab/label_curiga.py`, `tools/lab/uji/test_label_curiga.py` (baru) | Label yang dicurigai, dan penilaian caranya | 4 |
| `tools/lab/lembar_curiga.py`, `tools/lab/uji/test_lembar_curiga.py` (baru); `tools/lab/lembar_contoh.py` (ubah) | Lembar curiga untuk owner | 4 |
| `tools/lab/baca_vlm.py` (ubah: `ringkas` dipisah dari `nilai`) | Penilaian dari bacaan tersimpan | 5 |
| `tools/lab/nilai_ulang.py`, `tools/lab/uji/test_nilai_ulang.py` (baru) | Pembetulan label dan penilaian ulang | 5 |
| `bukti/2026-10-1x-label-dan-pembaca-kedua.md` dan ringkasan JSON (baru) | Laporan | 6 |
| `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md` (ubah) | Catatan | 4, 6 |

---

### Task 1: Pintu unduh berkas menerima rilis GitHub

**Files:**
- Modify: `tools/uji/ambil-berkas.test.mjs`
- Modify: `tools/ambil-berkas.ps1`

- [x] **Step 1: Ubah ujinya**

Di `tools/uji/ambil-berkas.test.mjs`, ganti baris `const HOST = [...]` menjadi:

```js
const HOST = ['data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com',
  'github.com', 'release-assets.githubusercontent.com'];
```

Sisipkan uji ini sesudah uji `'butir yang sudah dikunci mengirim SHA-256-nya ke pengunduh'`:

```js
test('berkas rilis GitHub diterima: alamat github.com sampai ke pengunduh apa adanya', () => {
  const rilis = { ...BUTIR, url: 'https://github.com/a/b/releases/download/t/model.onnx', berkas: 'model.onnx', maks_gb: 0.1 };

  const a = argumenDocker(rilis);

  assert.deepEqual(pasangan(a, '--alamat'), [rilis.url]);
  assert.deepEqual(pasangan(a, '--nama'), ['model.onnx']);
});
```

Tambahkan satu butir di objek `TOLAK`, sesudah `'alamat di host yang mirip tetapi di luar daftar'`:

```js
  'alamat di host GitHub yang mirip tetapi di luar daftar': [['contoh'], [{ ...BUTIR, url: 'https://github.com.jahat.example/a/b/releases/download/t/m.onnx' }]],
```

- [x] **Step 2: Jalankan, pastikan merah karena host belum didaftar**

Run: `npm test; echo "EXIT=$?"`
Expected: `fail 2`, `EXIT=1`. Yang gagal: uji daftar host (`--host` tidak sama) dan uji rilis GitHub (pintu menolak dengan
kode 2). Uji `TOLAK` yang baru langsung hijau, karena ia menjaga perilaku yang sudah ada (host tiruan tetap ditolak).

- [x] **Step 3: Tambah dua host**

Di `tools/ambil-berkas.ps1`:
- `.SYNOPSIS`: `(arsip atau catatan dataset)` menjadi `(arsip atau catatan dataset, atau berkas model untuk alat lab)`.
- Baris `$HOST_BOLEH` menjadi:

```powershell
$HOST_BOLEH = @('data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com',
    'github.com', 'release-assets.githubusercontent.com')
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 101`, `EXIT=0`.

- [x] **Step 5: Commit**

```bash
git add tools/ambil-berkas.ps1 tools/uji/ambil-berkas.test.mjs
git commit -q -F - <<'EOF'
Pintu unduh berkas menerima rilis GitHub

Alasan: K22 butuh pembaca kedua, dan bobot fast-plate-ocr hanya terbit
sebagai aset rilis GitHub. Diukur 14 Okt: unduhannya dialihkan
github.com -> github.com (repo berganti nama) -> release-assets.
githubusercontent.com, dan pengunduh memeriksa tiap pengalihan ke daftar
host pintu. Jadi dua host itu ditambahkan; yang diambil tetap hanya butir
yang tercatat di kunci.

Uji daftar host diubah dengan sadar (bukan dihapus), satu uji baru untuk
alamat rilis, dan satu penjaga untuk host tiruan yang mirip GitHub.
Uji ditulis lebih dulu dan terlihat merah (2 gagal). Gerbang Node: 99 -> 101.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Gerbang berkas terkunci, kunci, dan unduhan model fast-plate-ocr

**Files:**
- Modify: `tools/lab/model_terkunci.py`
- Modify: `tools/lab/uji/test_model_terkunci.py`
- Modify: `tools/vendor.lock.json`

- [x] **Step 1: Tulis ujinya**

Tambahkan di akhir `tools/lab/uji/test_model_terkunci.py`:

```python
def siapkan_berkas(tmp_path, sha=None):
    jalur = tmp_path / "unduhan" / "model.onnx"
    jalur.parent.mkdir(parents=True)
    jalur.write_bytes(b"onnx")
    kunci = tmp_path / "kunci-berkas.json"
    kunci.write_text(json.dumps({"berkas": [{"nama": "model-contoh", "berkas": "model.onnx",
                                             "sha256": hashlib.sha256(b"onnx").hexdigest() if sha is None else sha}]}))
    return jalur, mt.daftar_berkas(kunci)


def test_berkas_unduhan_yang_terkunci_diterima(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)

    assert mt.verifikasi_berkas(jalur, "model-contoh", daftar) == jalur


def test_berkas_unduhan_yang_belum_dikunci_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path, sha="")

    with pytest.raises(mt.ModelDitolak, match="belum dikunci"):
        mt.verifikasi_berkas(jalur, "model-contoh", daftar)


def test_berkas_unduhan_yang_berubah_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)
    jalur.write_bytes(b"ditukar")

    with pytest.raises(mt.ModelDitolak, match="SHA-256"):
        mt.verifikasi_berkas(jalur, "model-contoh", daftar)


def test_berkas_unduhan_bernama_lain_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)
    lain = jalur.with_name("lain.onnx")
    lain.write_bytes(b"onnx")

    with pytest.raises(mt.ModelDitolak, match="bukan model.onnx"):
        mt.verifikasi_berkas(lain, "model-contoh", daftar)


def test_butir_berkas_yang_tak_terdaftar_ditolak(tmp_path):
    jalur, daftar = siapkan_berkas(tmp_path)

    with pytest.raises(mt.ModelDitolak, match="tidak terdaftar"):
        mt.verifikasi_berkas(jalur, "lain", daftar)


def test_kunci_repo_mencatat_model_fast_plate_ocr():
    # Rantainya: kunci repo -> daftar yang dibaca alat lab. Tanpa kedua butir ini pembaca kedua tidak bisa dimuat.
    daftar = mt.daftar_berkas()

    assert daftar["fpo-cct-s-v2-onnx"][0] == "cct_s_v2_global.onnx" and len(daftar["fpo-cct-s-v2-onnx"][1]) == 64
    assert daftar["fpo-cct-s-v2-config"][0] == "cct_s_v2_global_plate_config.yaml"
    assert len(daftar["fpo-cct-s-v2-config"][1]) == 64
```

- [x] **Step 2: Jalankan, pastikan merah karena fungsinya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `6 failed, 100 passed`, `EXIT=1`; semuanya `AttributeError: module 'model_terkunci' has no attribute
'daftar_berkas'`.

- [x] **Step 3: Tulis gerbangnya**

Di `tools/lab/model_terkunci.py`, kalimat pertama docstring menjadi `Gerbang model: folder model Hugging Face harus PERSIS
yang dicatat di tools/vendor.lock.json (model_hf), dan berkas unduhan harus cocok dengan butir "berkas"-nya.`, lalu
tambahkan sesudah `verifikasi_folder_model`:

```python
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
```

- [x] **Step 4: Jalankan; lima lulus, satu tetap merah**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `1 failed, 105 passed`, `EXIT=1`. Yang gagal hanya `test_kunci_repo_mencatat_model_fast_plate_ocr` dengan
`KeyError: 'fpo-cct-s-v2-onnx'`: kuncinya belum memuat butir itu.

- [x] **Step 5: Kunci kedua berkas ke digest GitHub (dibaca dengan skrip, tidak diketik)**

Tulis berkas sekali pakai `data/alat-sementara/kunci-fpo.mjs`:

```js
// Sekali pakai: menambah dua butir "berkas" model fast-plate-ocr ke tools/vendor.lock.json. Alamat, ukuran, dan SHA-256
// dibaca dari API rilis GitHub (digest diterbitkan GitHub), tidak diketik. Disisipkan sebelum akhir daftar berkas,
// supaya bagian lain kunci tidak berubah bentuk.
import fs from 'node:fs';

const KITA = 'tools/vendor.lock.json';
const API = 'https://api.github.com/repos/ankandrew/fast-plate-ocr/releases/tags/arg-plates';
const UNDUH = 'https://github.com/ankandrew/fast-plate-ocr/releases/download/arg-plates/';
const BUTIR = [['fpo-cct-s-v2-onnx', 'cct_s_v2_global.onnx', 0.1], ['fpo-cct-s-v2-config', 'cct_s_v2_global_plate_config.yaml', 0.01]];

const r = await fetch(API, { headers: { 'User-Agent': 'cctvgerbang-kunci', Accept: 'application/vnd.github+json' } });
if (!r.ok) { console.error(`API rilis: HTTP ${r.status}`); process.exit(1); }
const rilis = await r.json();
let teks = fs.readFileSync(KITA, 'utf8');
const kunci = JSON.parse(teks);
const baru = BUTIR.map(([nama, berkas, maks]) => {
  if (kunci.berkas.some((b) => b.nama === nama)) { console.error(`${nama} sudah ada di kunci; tidak ditimpa`); process.exit(1); }
  const a = rilis.assets.find((x) => x.name === berkas);
  if (!a || !/^sha256:[0-9a-f]{64}$/.test(a.digest || '')) { console.error(`${berkas}: tidak ada di rilis atau tanpa digest`); process.exit(1); }
  return {
    nama, url: UNDUH + berkas, berkas, maks_gb: maks, sha256: a.digest.slice(7), sumber: rilis.html_url, ukuran_byte: a.size,
    isi_dibaca: `API rilis GitHub ${rilis.tag_name}: ${a.size} byte, digest sha256 diterbitkan GitHub, diunggah ${a.updated_at}. Kode fast-plate-ocr @ 9ce7a5b menunjuk github.com/ankandrew/cnn-ocr-lp, repo yang sama sebelum berganti nama`,
    peran: 'alat lab: pembaca kedua untuk membetulkan label set uji (K22). BUKAN bagian produk; izin bobot tidak dinyatakan (BELUM-JELAS)',
    dibaca: new Date().toISOString().slice(0, 10),
  };
});
const jangkar = '    }\n  ],\n  "_model_hf"';
if (teks.split(jangkar).length !== 2) { console.error('jangkar akhir daftar berkas tidak ketemu tepat sekali'); process.exit(1); }
const sisip = baru.map((b) => JSON.stringify(b, null, 2).replace(/^/gm, '    ')).join(',\n');
teks = teks.replace(jangkar, () => `    },\n${sisip}\n  ],\n  "_model_hf"`);
const lama = '(arsip dan catatan dataset)';
if (teks.split(lama).length !== 2) { console.error('keterangan _berkas tidak ketemu tepat sekali'); process.exit(1); }
teks = teks.replace(lama, '(arsip dan catatan dataset, dan berkas model untuk alat lab)');
fs.writeFileSync(KITA, teks);
const hasil = JSON.parse(fs.readFileSync(KITA, 'utf8'));
console.log(hasil.berkas.slice(-2).map((b) => `${b.nama}: ${b.berkas}, ${b.ukuran_byte} byte, sha256 ${b.sha256.slice(0, 12)}`).join('\n'));
```

Run: `node data/alat-sementara/kunci-fpo.mjs; echo "EXIT=$?"`
Expected: dua baris, `fpo-cct-s-v2-onnx: cct_s_v2_global.onnx, 5262230 byte, sha256 384bbbd2cea3` dan
`fpo-cct-s-v2-config: cct_s_v2_global_plate_config.yaml, 1725 byte, sha256 0335c74a3051`; `EXIT=0`. Bila angkanya lain
dari yang diukur 14 Okt (penerbit mengganti asetnya), **berhenti dan laporkan**, jangan lanjut.

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 101`, `EXIT=0`.

- [x] **Step 6: Unduh lewat pintu (SHA-256 diperiksa pengunduh)**

Run (PowerShell, satu per satu):
`powershell -NoProfile -File tools\ambil-berkas.ps1 fpo-cct-s-v2-onnx; "EXIT=$LASTEXITCODE"`
`powershell -NoProfile -File tools\ambil-berkas.ps1 fpo-cct-s-v2-config; "EXIT=$LASTEXITCODE"`
Expected: masing-masing `TERSIMPAN ...: <byte> byte, SHA256 <sama dengan kunci>, dari release-assets.githubusercontent.com`
dan `EXIT=0`. Kode 7 = SHA-256 tidak cocok: **berhenti**.

Run (PowerShell): `Get-ChildItem data\unduhan\fpo-cct-s-v2-onnx, data\unduhan\fpo-cct-s-v2-config -File | ForEach-Object { "{0} {1}" -f $_.Name, $_.Length }`
Expected: `cct_s_v2_global.onnx 5262230` dan `cct_s_v2_global_plate_config.yaml 1725`, tanpa berkas `.part`.

- [x] **Step 7: Jalankan gerbang, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `106 passed`, `EXIT=0`.

- [x] **Step 8: Commit**

```bash
git add tools/lab/model_terkunci.py tools/lab/uji/test_model_terkunci.py tools/vendor.lock.json
git commit -q -F - <<'EOF'
Model fast-plate-ocr dikunci ke digest GitHub dan diunduh lewat pintu

Alasan: pembaca kedua untuk K22. fast-plate-ocr mengunduh modelnya sendiri
tanpa memeriksa keutuhan (docs/VONIS-LISENSI.md butir 4), jadi jalur itu
tidak dipakai: dua berkas model diambil lewat tools/ambil-berkas.ps1,
dikunci ke SHA-256 yang diterbitkan GitHub (dibaca dari API dengan skrip,
tidak diketik), dan diperiksa lagi oleh gerbang berkas terkunci sebelum
dimuat. Bobotnya BELUM-JELAS: alat lab, bukan bagian produk.

Uji ditulis lebih dulu dan terlihat merah (6 gagal, lalu 1 uji rantai
tetap merah sampai butir kunci ditambahkan). Gerbang lab: 100 -> 106.
Unduhan: <angka dari Step 6>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Pembaca fast-plate-ocr pada set uji

**Files:**
- Create: `tools/lab/baca_fpo.py`
- Create: `tools/lab/uji/test_baca_fpo.py`
- Create: `tools/lab/uji_gpu/test_model_baca_fpo.py`

- [x] **Step 1: Pastikan klon yang dijalankan adalah yang dikunci**

Run: `git -C /d/Projects/super-team-v1/cctvgerbang-seed/vendor/fast-plate-ocr rev-parse HEAD; git -C /d/Projects/super-team-v1/cctvgerbang-seed/vendor/fast-plate-ocr status --short | wc -l`
Expected: `9ce7a5b64a939aa421c243b331d42e6bc25ffd44` dan `0`.

- [x] **Step 2: Tulis ujinya**

Buat `tools/lab/uji/test_baca_fpo.py`:

```python
"""Uji tools/lab/baca_fpo.py dengan pembaca tiruan. Model sungguhan diuji terpisah di tools/lab/uji_gpu/."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_fpo as bf  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "baca_fpo.py"


def siapkan(tmp_path):
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    cv2.imwrite(str(folder / "test/B1234XYZ_0.png"), np.full((30, 100, 3), 200, np.uint8))
    pembagian = {"latih": [], "uji": [{"teks": "B1234XYZ", "kelompok": "mobil-terang", "berkas": ["test/B1234XYZ_0.png"]}]}
    jalur = tmp_path / "pembagian.json"
    jalur.write_text(json.dumps(pembagian))
    return pembagian, jalur, folder


def test_warna_mengikuti_konfigurasi_model():
    gambar = np.array([[[10, 20, 30]]], np.uint8)  # satu titik, urutan warna OpenCV (biru, hijau, merah)

    assert bf.ubah_warna(gambar, "rgb").tolist() == [[[30, 20, 10]]]
    assert bf.ubah_warna(gambar, "grayscale").shape == (1, 1)


def test_mode_warna_lain_ditolak():
    with pytest.raises(ValueError, match="mode warna"):
        bf.ubah_warna(np.zeros((1, 1, 3), np.uint8), "hsv")


def test_utama_menulis_hasil_dan_ringkasan_tanpa_nomor_plat(tmp_path, capsys):
    _, jalur, folder = siapkan(tmp_path)
    keluar = tmp_path / "keluar"

    kode = bf.utama(jalur, folder, tmp_path / "unduhan", keluar, baca=lambda gambar: "B 1234 XYZ")

    assert kode == 0
    assert json.loads((keluar / "hasil.jsonl").read_text())["bacaan"] == "B1234XYZ"
    teks = (keluar / "ringkasan.json").read_text()
    assert "1234" not in teks
    assert json.loads(teks)["per_kelompok"]["mobil-terang"]["kedatangan_benar"] == 1
    assert "1234" not in capsys.readouterr().out


def test_baris_perintah_menolak_model_yang_belum_ada_dengan_kode_2(tmp_path):
    # Rantainya: baris perintah -> gerbang berkas terkunci, SEBELUM onnxruntime dimuat atau set uji dibaca.
    _, jalur, folder = siapkan(tmp_path)

    hasil = subprocess.run([sys.executable, str(SKRIP), str(jalur), str(folder), str(tmp_path / "unduhan-kosong"),
                            str(tmp_path / "keluar")], capture_output=True, text=True)

    assert hasil.returncode == 2, hasil.stdout + hasil.stderr
    assert "DITOLAK" in hasil.stdout
    assert not (tmp_path / "keluar").exists()


def test_gambar_yang_hilang_tidak_membocorkan_nama_berkas(tmp_path):
    # Proses terpisah: yang diuji pembisuan log OpenCV yang ikut termuat lewat baca_fpo sendiri.
    pembagian, _, folder = siapkan(tmp_path)
    (folder / "test/B1234XYZ_0.png").unlink()
    kode = ("import json, sys; sys.path.insert(0, sys.argv[1]); import baca_fpo as bf; "
            "_, r = bf.nilai(json.loads(sys.argv[2]), sys.argv[3], lambda g: 'X'); "
            "print(r['per_kelompok']['mobil-terang']['gambar'])")

    hasil = subprocess.run([sys.executable, "-c", kode, str(SKRIP.parent), json.dumps(pembagian), str(folder)],
                           capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert hasil.stdout.strip() == "1"
    assert "1234" not in hasil.stderr
```

- [x] **Step 3: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'baca_fpo'`, `EXIT` bukan 0.

- [x] **Step 4: Tulis alatnya**

Buat `tools/lab/baca_fpo.py`:

```python
"""Pembaca kedua untuk langkah baca huruf: fast-plate-ocr @ 9ce7a5b dengan model cct-s-v2-global, di CPU, tanpa jaringan.

Dipakai untuk membetulkan label set uji (K22): bacaannya dibandingkan dengan bacaan Qwen3-VL (tools/lab/label_curiga.py).
Sekaligus angka pembanding "paket jadi" pertama (spec bagian 8.1 langkah 6, K16).

Kedua berkas model diunduh lewat tools/ambil-berkas.ps1 dan diverifikasi SHA-256-nya terhadap kunci
(tools/lab/model_terkunci.py) SEBELUM onnxruntime dan fast-plate-ocr dimuat. Kode fast-plate-ocr dibaca dari klon yang
dikunci di vendor/fast-plate-ocr; jalur unduh otomatisnya tidak pernah dipakai (model diberi lewat jalur berkas).
Penilaian dan bentuk keluarannya sama dengan tools/lab/baca_vlm.py.

Keluaran:
- hasil.jsonl: bacaan tiap gambar. Memuat nomor plat: tinggal di data/, agen tidak membukanya.
- ringkasan.json: hitungan saja. Boleh disalin ke bukti/.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/baca_fpo.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/unduhan /kerja/data/keluaran/baca-fpo
"""
import json
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, nilai, uraikan  # noqa: E402  (baca_vlm juga membisukan log OpenCV)
from model_terkunci import ModelDitolak, daftar_berkas, verifikasi_berkas  # noqa: E402
from plat import bersihkan  # noqa: E402,F401  (dipakai uji model sungguhan)

VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "fast-plate-ocr"
BUTIR_MODEL = "fpo-cct-s-v2-onnx"
BUTIR_KONFIGURASI = "fpo-cct-s-v2-config"


def ubah_warna(gambar_bgr, mode):
    """Gambar OpenCV (biru-hijau-merah) ke mode warna yang diminta konfigurasi model."""
    if mode == "rgb":
        return cv2.cvtColor(gambar_bgr, cv2.COLOR_BGR2RGB)
    if mode == "grayscale":
        return cv2.cvtColor(gambar_bgr, cv2.COLOR_BGR2GRAY)
    raise ValueError(f"mode warna tidak dikenal: {mode}")


class PembacaFpo:
    """Pembaca plat fast-plate-ocr. Dipanggil dengan satu gambar (urutan warna OpenCV); kembali teks mentah."""

    def __init__(self, folder_unduhan):
        daftar = daftar_berkas()
        jalur = {b: verifikasi_berkas(Path(folder_unduhan) / b / daftar.get(b, ("?", ""))[0], b, daftar)
                 for b in (BUTIR_MODEL, BUTIR_KONFIGURASI)}

        sys.path.insert(0, str(VENDOR))
        from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

        self._model = LicensePlateRecognizer(device="cpu", onnx_model_path=jalur[BUTIR_MODEL],
                                             plate_config_path=jalur[BUTIR_KONFIGURASI])
        self.mode_warna = self._model.config.image_color_mode
        self.wilayah_indonesia = "Indonesia" in (self._model.config.plate_regions or [])

    def __call__(self, gambar_bgr):
        return self._model.run_one(ubah_warna(gambar_bgr, self.mode_warna)).plate


def utama(berkas_pembagian, folder_gambar, folder_unduhan, keluar, baca=None):
    if baca is None:
        try:
            baca = PembacaFpo(folder_unduhan)
        except ModelDitolak as galat:
            print(f"DITOLAK: {galat}")
            return 2
    pembagian = json.loads(Path(berkas_pembagian).read_text())
    baris, ringkasan = nilai(pembagian, folder_gambar, baca)
    ringkasan = {"model": "fast-plate-ocr @ 9ce7a5b, cct-s-v2-global, CPU", **ringkasan}
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    with open(keluar / "hasil.jsonl", "w") as berkas:
        for b in baris:
            berkas.write(json.dumps(b) + "\n")
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    for k in KELOMPOK:
        print(f"{k:<13} {uraikan(ringkasan['per_kelompok'][k])}")
    print(f"detik per gambar: {ringkasan['detik_per_gambar']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Pakai: python baca_fpo.py <pembagian.json> <folder-gambar> <folder-unduhan> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
```

- [x] **Step 5: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `111 passed` (106 + 5 baru) dan `EXIT=0`.

- [x] **Step 6: Uji dengan model sungguhan (di luar gerbang biasa)**

Buat `tools/lab/uji_gpu/test_model_baca_fpo.py`:

```python
"""Uji fast-plate-ocr dengan model sungguhan (CPU). Di luar gerbang biasa: butuh berkas model di data/unduhan.

  powershell -NoProfile -File tools\\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu/test_model_baca_fpo.py -q -s -p no:cacheprovider
"""
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import baca_fpo as bf  # noqa: E402

UNDUHAN = Path(__file__).resolve().parents[3] / "data" / "unduhan"


@pytest.mark.skipif(not (UNDUHAN / bf.BUTIR_MODEL).is_dir(), reason="model belum diunduh (Rencana 6 Task 2)")
def test_pembaca_fpo_membaca_plat_buatan():
    # Plat buatan tulisan komputer, bukan plat siapa pun: membuktikan rantainya (gerbang berkas -> muat -> baca -> teks).
    gambar = np.zeros((110, 360, 3), np.uint8)
    cv2.putText(gambar, "B 1234 XYZ", (12, 75), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 3)

    pembaca = bf.PembacaFpo(UNDUHAN)
    bacaan = bf.bersihkan(pembaca(gambar))

    print(f"\nbacaan plat buatan: {bacaan}; mode warna: {pembaca.mode_warna}; Indonesia di konfigurasi: {pembaca.wilayah_indonesia}")
    assert re.fullmatch(r"[0-9A-Z]{1,10}", bacaan)
```

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python -m pytest /kerja/tools/lab/uji_gpu/test_model_baca_fpo.py -q -s -p no:cacheprovider; "EXIT=$LASTEXITCODE"`
Expected: `1 passed`, `EXIT=0`, dan satu baris `bacaan plat buatan: ...`. Bacaan, mode warna, dan ada-tidaknya Indonesia di
konfigurasi terbitan **dicatat apa adanya** (plat buatan, bukan data pribadi). Bacaan yang bukan `B1234XYZ` adalah temuan
tentang model, bukan alasan mengubah ujinya.

- [x] **Step 7: Jalankan pada set uji sungguhan**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_fpo.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/unduhan /kerja/data/keluaran/baca-fpo; "EXIT=$LASTEXITCODE"`
Expected: empat baris kelompok, `detik per gambar: <angka>`, `EXIT=0`. Angkanya dibandingkan dengan **label penerbit
yang belum dibetulkan**; dicatat apa adanya.

Run: `git status --short`
Expected: hanya berkas alat dan uji baru.

- [x] **Step 8: Commit**

```bash
git add tools/lab/baca_fpo.py tools/lab/uji/test_baca_fpo.py tools/lab/uji_gpu/test_model_baca_fpo.py
git commit -q -F - <<'EOF'
Pembaca kedua fast-plate-ocr untuk langkah baca huruf

Alasan: K22 membetulkan label set uji dengan dua pembaca berbeda; ini
pembaca kedua, sekaligus angka pembanding "paket jadi" pertama (spec 8.1
langkah 6, K16). Berjalan di CPU dari klon terkunci @ 9ce7a5b; kedua berkas
model diperiksa SHA-256-nya sebelum onnxruntime dimuat, dan jalur unduh
otomatisnya tidak dipakai.

Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError: baca_fpo).
Gerbang lab: 106 -> 111. Uji model sungguhan di luar gerbang:
<hasil Step 6>. Pada set uji, dibandingkan dengan label penerbit yang belum
dibetulkan: <angka Step 7>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Label yang dicurigai dan lembarnya untuk owner

**Files:**
- Create: `tools/lab/label_curiga.py`, `tools/lab/uji/test_label_curiga.py`
- Create: `tools/lab/lembar_curiga.py`, `tools/lab/uji/test_lembar_curiga.py`
- Modify: `tools/lab/lembar_contoh.py`

- [x] **Step 1: Tulis uji pencari label yang dicurigai**

Buat `tools/lab/uji/test_label_curiga.py`:

```python
"""Uji tools/lab/label_curiga.py: hanya plat yang dibantah dua pembaca yang SEPAKAT yang dicurigai (K22)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import label_curiga as lcu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "label_curiga.py"


def pembagian(*teks):
    return {"latih": [], "uji": [{"teks": t, "kelompok": "mobil-terang", "berkas": [f"test/{t}_1.png"]} for t in teks]}


def test_dua_pembaca_sepakat_berbeda_dari_label_dicurigai():
    b = "test/B1234XYZ_1.png"

    curiga = lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYE"})

    assert curiga == [{"teks": "B1234XYZ", "usulan": "B1234XYE", "kelompok": "mobil-terang", "berkas": b}]


def test_satu_pembaca_saja_atau_dua_pembaca_tak_sepakat_tidak_dicurigai():
    b = "test/B1234XYZ_1.png"

    assert lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYZ"}) == []
    assert lcu.cari(pembagian("B1234XYZ"), {b: "B1234XYE"}, {b: "B1234XYF"}) == []


def test_sepakat_di_luar_pola_atau_kosong_tidak_dicurigai():
    b = "test/B1234XYZ_1.png"

    assert lcu.cari(pembagian("B1234XYZ"), {b: "HELLO"}, {b: "HELLO"}) == []
    assert lcu.cari(pembagian("B1234XYZ"), {b: ""}, {b: ""}) == []


def test_cara_dinilai_pada_contoh_yang_sudah_diperiksa_owner():
    curiga = [{"teks": "D1001AB"}, {"teks": "D1003AB"}]
    lembar = {"contoh": [{"nomor": 1, "teks": "D1001AB"}, {"nomor": 2, "teks": "D1002AB"}, {"nomor": 3, "teks": "D1003AB"}]}

    assert lcu.nilai_cara(curiga, lembar, {1, 2}) == {"label_salah_diketahui": 2, "tertangkap": 1,
                                                       "label_benar_diketahui": 1, "ikut_dicurigai": 1}


def test_baris_perintah_menulis_berkas_tanpa_nomor_plat_di_layar(tmp_path):
    (tmp_path / "pembagian.json").write_text(json.dumps(pembagian("B1234XYZ", "D5678AB")))
    for nama in ("a.jsonl", "b.jsonl"):
        (tmp_path / nama).write_text(json.dumps({"berkas": "test/B1234XYZ_1.png", "bacaan": "B1234XYE"}) + "\n")
    (tmp_path / "lembar.json").write_text(json.dumps({"contoh": [{"nomor": 1, "teks": "B1234XYZ"}, {"nomor": 2, "teks": "D5678AB"}]}))
    perintah = [sys.executable, str(SKRIP), str(tmp_path / "pembagian.json"), str(tmp_path / "a.jsonl"),
                str(tmp_path / "b.jsonl"), str(tmp_path / "keluar"), "--periksa", str(tmp_path / "lembar.json")]

    hasil = subprocess.run(perintah + ["--salah", "1"], capture_output=True, text=True)
    salah = subprocess.run(perintah + ["--salah", "9"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    for larangan in ("1234", "5678"):
        assert larangan not in hasil.stdout + (tmp_path / "keluar/ringkasan.json").read_text()
    assert "tertangkap 1 dari 1 label salah" in hasil.stdout
    assert json.loads((tmp_path / "keluar/curiga.json").read_text())[0]["usulan"] == "B1234XYE"
    assert salah.returncode == 2 and "SALAH PAKAI" in salah.stdout
```

- [x] **Step 2: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'label_curiga'`, `EXIT` bukan 0.

- [x] **Step 3: Tulis alatnya**

Buat `tools/lab/label_curiga.py`:

```python
"""Label set uji yang dicurigai salah (K22): plat yang dibaca SAMA oleh dua pembaca berbeda tetapi berbeda dari labelnya.

Per gambar dibandingkan bacaan pembaca A dan B (hasil.jsonl keduanya). Sebuah kedatangan dicurigai bila pada paling
sedikit satu gambarnya kedua pembaca sepakat pada teks yang sesuai pola plat dan tidak sama dengan label. Usulannya teks
yang paling sering disepakati (seri: urutan abjad). Kedatangan yang hanya dibantah satu pembaca, atau dibantah dua
pembaca yang tidak sepakat, TIDAK dicurigai: itu batas cara ini (K22).

Bila --periksa (lembar-contoh.json) dan --salah (nomor baris yang labelnya diketahui salah) diberi, cara ini dinilai pada
contoh yang sudah diperiksa owner: berapa label salah yang tertangkap, dan berapa label benar yang ikut dicurigai.

Keluaran: curiga.json (memuat plat; tinggal di data/) dan ringkasan.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/label_curiga.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/baca-vlm/hasil.jsonl /kerja/data/keluaran/baca-fpo/hasil.jsonl /kerja/data/keluaran/label-curiga --periksa /kerja/data/keluaran/lembar-contoh/lembar-contoh.json --salah 19,22,25,35,36,54
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plat import urai  # noqa: E402

KELOMPOK = ("mobil-terang", "mobil-gelap", "motor-terang", "motor-gelap")


def baca_hasil(jalur):
    """berkas -> bacaan bersih, dari hasil.jsonl sebuah pembaca."""
    return {b["berkas"]: b["bacaan"] for b in map(json.loads, Path(jalur).read_text().splitlines())}


def cari(pembagian, bacaan_a, bacaan_b):
    curiga = []
    for kedatangan in pembagian["uji"]:
        sepakat, gambar = Counter(), {}
        for berkas in kedatangan["berkas"]:
            a = bacaan_a.get(berkas, "")
            if a and a == bacaan_b.get(berkas, "") and a != kedatangan["teks"] and urai(a) is not None:
                sepakat[a] += 1
                gambar.setdefault(a, berkas)
        if sepakat:
            usulan = min(sepakat, key=lambda t: (-sepakat[t], t))
            curiga.append({"teks": kedatangan["teks"], "usulan": usulan, "kelompok": kedatangan["kelompok"],
                           "berkas": gambar[usulan]})
    return curiga


def nilai_cara(curiga, lembar_contoh, salah):
    dicurigai = {c["teks"] for c in curiga}
    diketahui_salah = [c for c in lembar_contoh["contoh"] if c["nomor"] in salah]
    diketahui_benar = [c for c in lembar_contoh["contoh"] if c["nomor"] not in salah]
    return {"label_salah_diketahui": len(diketahui_salah),
            "tertangkap": sum(c["teks"] in dicurigai for c in diketahui_salah),
            "label_benar_diketahui": len(diketahui_benar),
            "ikut_dicurigai": sum(c["teks"] in dicurigai for c in diketahui_benar)}


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Label set uji yang dicurigai salah (K22).")
    for nama in ("pembagian", "hasil_a", "hasil_b", "keluar"):
        urai_argumen.add_argument(nama)
    urai_argumen.add_argument("--periksa")
    urai_argumen.add_argument("--salah", default="")
    p = urai_argumen.parse_args(argumen)
    pembagian = json.loads(Path(p.pembagian).read_text())
    curiga = cari(pembagian, baca_hasil(p.hasil_a), baca_hasil(p.hasil_b))
    ringkasan = {"aturan": "dua pembaca sepakat pada teks berpola plat yang berbeda dari label (K22)",
                 "kedatangan_uji": len(pembagian["uji"]), "dicurigai": len(curiga),
                 "per_kelompok": {k: {"kedatangan": sum(x["kelompok"] == k for x in pembagian["uji"]),
                                      "dicurigai": sum(c["kelompok"] == k for c in curiga)} for k in KELOMPOK}}
    if p.periksa:
        lembar = json.loads(Path(p.periksa).read_text())
        salah = {int(x) for x in p.salah.split(",") if x.strip()}
        luar = sorted(salah - {c["nomor"] for c in lembar["contoh"]})
        if luar:
            print(f"SALAH PAKAI: baris {luar} tidak ada di lembar contoh")
            return 2
        ringkasan["penilaian_cara"] = nilai_cara(curiga, lembar, salah)
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "curiga.json").write_text(json.dumps(curiga, indent=1))
    (keluar / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2))
    print(f"dicurigai: {len(curiga)} dari {len(pembagian['uji'])} kedatangan uji")
    for k in KELOMPOK:
        n = ringkasan["per_kelompok"][k]
        print(f"  {k:<13}{n['dicurigai']:>5} dari {n['kedatangan']}")
    if "penilaian_cara" in ringkasan:
        n = ringkasan["penilaian_cara"]
        print(f"pada contoh yang sudah diperiksa owner: tertangkap {n['tertangkap']} dari {n['label_salah_diketahui']} "
              f"label salah; ikut dicurigai {n['ikut_dicurigai']} dari {n['label_benar_diketahui']} label benar")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `116 passed` (111 + 5 baru) dan `EXIT=0`.

- [x] **Step 5: Tulis uji lembar curiga**

Buat `tools/lab/uji/test_lembar_curiga.py`:

```python
"""Uji tools/lab/lembar_curiga.py: urutan tetap, dua tulisan per baris, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lembar_contoh as lc  # noqa: E402
import lembar_curiga as lk  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "lembar_curiga.py"
CURIGA = [{"teks": "D3001AB", "usulan": "D3001AE", "kelompok": "motor-terang", "berkas": "test/D3001AB_1.png"},
          {"teks": "D1001AB", "usulan": "D1001AE", "kelompok": "mobil-terang", "berkas": "test/D1001AB_1.png"}]


def siapkan(tmp_path, curiga):
    folder = tmp_path / "gambar"
    (folder / "test").mkdir(parents=True)
    for c in curiga:
        cv2.imwrite(str(folder / c["berkas"]), np.full((30, 100, 3), 200, np.uint8))
    berkas = tmp_path / "curiga.json"
    berkas.write_text(json.dumps(curiga))
    return berkas, folder


def test_lembar_dan_daftarnya_ditulis_menurut_kelompok(tmp_path):
    berkas, folder = siapkan(tmp_path, CURIGA)

    assert lk.utama(berkas, folder, tmp_path / "keluar") == 0

    lembar = cv2.imread(str(tmp_path / "keluar/lembar-curiga-1.png"))
    assert lembar.shape == (2 * (lc.TINGGI + 8), lc.LEBAR_NOMOR + lc.LEBAR_POTONGAN + lc.LEBAR_TEKS, 3)
    daftar = json.loads((tmp_path / "keluar/lembar-curiga.json").read_text())
    assert [(c["nomor"], c["kelompok"]) for c in daftar["contoh"]] == [(1, "mobil-terang"), (2, "motor-terang")]
    assert daftar["contoh"][0]["usulan"] == "D1001AE"


def test_layar_tanpa_teks_plat(tmp_path, capsys):
    berkas, folder = siapkan(tmp_path, CURIGA)

    lk.utama(berkas, folder, tmp_path / "keluar")

    cetak = capsys.readouterr().out
    assert "1001" not in cetak and "3001" not in cetak
    assert "agen tidak membukanya" in cetak


def test_baris_perintah(tmp_path):
    berkas, folder = siapkan(tmp_path, CURIGA)
    kosong = tmp_path / "kosong.json"
    kosong.write_text("[]")

    hasil = subprocess.run([sys.executable, str(SKRIP), str(berkas), str(folder), str(tmp_path / "keluar")],
                           capture_output=True, text=True)
    tanpa = subprocess.run([sys.executable, str(SKRIP), str(kosong), str(folder), str(tmp_path / "keluar-kosong")],
                           capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), str(berkas)], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    assert (tmp_path / "keluar/lembar-curiga-1.png").exists()
    assert tanpa.returncode == 0 and "Tidak ada label" in tanpa.stdout
    assert salah.returncode == 2
```

- [x] **Step 6: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'lembar_curiga'`, `EXIT` bukan 0.

- [x] **Step 7: Dua tulisan per baris, lalu alatnya**

Di `tools/lab/lembar_contoh.py`, ganti fungsi `baris` menjadi (perilaku tanpa `usulan` tidak berubah):

```python
def baris(nomor, gambar, teks, usulan=None):
    kanvas = np.full((TINGGI + 8, LEBAR_NOMOR + LEBAR_POTONGAN + LEBAR_TEKS, 3), 255, np.uint8)
    if gambar is None:
        cv2.putText(kanvas, "gambar tak terbaca", (LEBAR_NOMOR + 8, TINGGI // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
    else:
        tinggi, lebar = gambar.shape[:2]
        skala = min(TINGGI / tinggi, LEBAR_POTONGAN / lebar)
        cara = cv2.INTER_AREA if skala < 1 else cv2.INTER_CUBIC
        kecil = cv2.resize(gambar, (max(1, round(lebar * skala)), max(1, round(tinggi * skala))), interpolation=cara)
        kanvas[4:4 + kecil.shape[0], LEBAR_NOMOR:LEBAR_NOMOR + kecil.shape[1]] = kecil
    cv2.putText(kanvas, str(nomor), (6, TINGGI // 2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    x = LEBAR_NOMOR + LEBAR_POTONGAN + 12
    if usulan is None:
        cv2.putText(kanvas, tulisan(teks), (x, TINGGI // 2 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (160, 0, 0), 2)
    else:
        # A = label penerbit (biru), B = teks yang disepakati dua pembaca (hijau). Lembar label yang dicurigai (K22).
        cv2.putText(kanvas, f"A {tulisan(teks)}", (x, TINGGI // 2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (160, 0, 0), 2)
        cv2.putText(kanvas, f"B {tulisan(usulan)}", (x, TINGGI - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 120, 0), 2)
    return kanvas
```

Buat `tools/lab/lembar_curiga.py`:

```python
"""Lembar label yang DICURIGAI, untuk diperiksa OWNER (K19, K22).

Tiap baris: nomor, potongan plat, A = label penerbit (biru), B = teks yang disepakati dua pembaca (hijau). Owner menyebut
nomor baris yang tulisan B-nya benar, dan nomor baris yang tulisan A maupun B salah; baris yang tidak disebut dianggap
tulisan A benar. Owner tidak perlu mengetik nomor plat. Lembar memuat plat yang terbaca, jadi agen TIDAK PERNAH
membukanya.

Urutan baris tetap: menurut kelompok, lalu SHA-256 teks label.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/lembar_curiga.py /kerja/data/keluaran/label-curiga/curiga.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-curiga
"""
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lembar_contoh import KELOMPOK, PER_LEMBAR, baris  # noqa: E402  (lembar_contoh juga membisukan log OpenCV)


def urutkan(curiga):
    return sorted(curiga, key=lambda c: (KELOMPOK.index(c["kelompok"]), hashlib.sha256(c["teks"].encode()).hexdigest()))


def utama(berkas_curiga, folder_gambar, keluar):
    curiga = urutkan(json.loads(Path(berkas_curiga).read_text()))
    keluar = Path(keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    if not curiga:
        print("Tidak ada label yang dicurigai: tidak ada lembar yang dibuat.")
        return 0
    barisan, contoh = [], []
    for nomor, c in enumerate(curiga, 1):
        barisan.append(baris(nomor, cv2.imread(str(Path(folder_gambar) / c["berkas"])), c["teks"], usulan=c["usulan"]))
        contoh.append({"nomor": nomor, **c})
    halaman = []
    for awal in range(0, len(barisan), PER_LEMBAR):
        nama = f"lembar-curiga-{awal // PER_LEMBAR + 1}.png"
        cv2.imwrite(str(keluar / nama), np.vstack(barisan[awal:awal + PER_LEMBAR]))
        halaman.append(nama)
    (keluar / "lembar-curiga.json").write_text(json.dumps({"halaman": halaman, "contoh": contoh}, indent=1))
    jumlah = {k: sum(c["kelompok"] == k for c in contoh) for k in KELOMPOK}
    print(f"{len(contoh)} baris {jumlah} -> {len(halaman)} lembar di {keluar}. "
          "Lembar ini memuat plat yang terbaca: agen tidak membukanya.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Pakai: python lembar_curiga.py <curiga.json> <folder-gambar> <folder-keluaran>")
        sys.exit(2)
    sys.exit(utama(*sys.argv[1:]))
```

- [x] **Step 8: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `119 passed` (116 + 3 baru) dan `EXIT=0`; uji `lembar_contoh` lama tetap hijau.

- [x] **Step 9: Cari label yang dicurigai pada set uji sungguhan, dan nilai caranya**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/label_curiga.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/baca-vlm/hasil.jsonl /kerja/data/keluaran/baca-fpo/hasil.jsonl /kerja/data/keluaran/label-curiga --periksa /kerja/data/keluaran/lembar-contoh/lembar-contoh.json --salah 19,22,25,35,36,54; "EXIT=$LASTEXITCODE"`
Expected: `dicurigai: N dari 945 kedatangan uji`, empat baris kelompok, satu baris penilaian cara, `EXIT=0`. Angka dicatat apa
adanya. Tertangkap berapa dari 6 adalah taksiran pertama berapa label salah yang lolos dengan cara ini (K22).

**Bila N lebih dari 200 (sepuluh lembar), BERHENTI di sini** dan laporkan N ke owner sebelum membuat lembar: waktu owner
adalah keputusan owner.

- [x] **Step 10: Buat lembar curiga, tanpa membukanya**

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_curiga.py /kerja/data/keluaran/label-curiga/curiga.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-curiga; "EXIT=$LASTEXITCODE"`
Expected: `N baris {...} -> M lembar di /kerja/data/keluaran/lembar-curiga. ... agen tidak membukanya.` dan `EXIT=0`.
**Agen tidak membuka berkas-berkas itu.**

- [x] **Step 11: Commit alat, lalu catat posisi sementara**

```bash
git add tools/lab/label_curiga.py tools/lab/uji/test_label_curiga.py tools/lab/lembar_curiga.py tools/lab/uji/test_lembar_curiga.py tools/lab/lembar_contoh.py
git commit -q -F - <<'EOF'
Label set uji yang dicurigai dan lembarnya untuk owner (K22)

Alasan: owner memilih membetulkan label dengan memeriksa yang dicurigai
saja (K22): plat yang dibaca sama oleh Qwen3-VL dan fast-plate-ocr tetapi
berbeda dari label penerbit. Lembarnya menampilkan A (label) dan B (bacaan
yang disepakati), jadi owner cukup menyebut nomor baris, tanpa mengetik
nomor plat. Cara ini juga dinilai pada 60 contoh yang sudah diperiksa
owner.

Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError
label_curiga, lalu lembar_curiga). Gerbang lab: 111 -> 116 -> 119.
Pada set uji: <angka Step 9 dan 10>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

Lalu perbarui `ROADMAP.md` lewat skrip pencatat berkas (jangkar tepat sekali): butir `- [ ] Rencana 6 Fase 0A
dijalankan` diberi keterangan "Task 1–4 selesai; menunggu owner memeriksa lembar curiga", butir baru `- [ ] Owner
memeriksa lembar label yang dicurigai ← di sini sekarang`, baris status di kepala berkas, dan satu baris changelog beralasan
dengan angka Task 2–4. Commit.

- [x] **Step 12: BERHENTI. Minta owner memeriksa lembar curiga**

Minta owner membuka `D:\Projects\super-team-v1\cctvgerbang-seed\data\keluaran\lembar-curiga\lembar-curiga-*.png` (agen
tidak membukanya) dan menjawab, **dengan nomor baris saja, tanpa mengetik nomor plat**:

1. nomor baris yang tulisan hijaunya (B) benar;
2. nomor baris yang tulisan biru (A) maupun hijau (B) sama-sama salah.

Baris yang tidak disebut dianggap tulisan biru (A) benar. Jawaban owner dicatat apa adanya di `ROADMAP.md` (changelog),
lalu Task 5 dijalankan.

---

### Task 5: Label dibetulkan, pembaca dinilai ulang

**Files:**
- Modify: `tools/lab/baca_vlm.py`
- Create: `tools/lab/nilai_ulang.py`, `tools/lab/uji/test_nilai_ulang.py`

- [x] **Step 1: Pisahkan penilaian dari pembacaan (uji lama menjaga)**

Di `tools/lab/baca_vlm.py`, ganti fungsi `nilai` dengan dua fungsi ini (perilaku `nilai` tidak berubah; `ringkas`
dipakai juga oleh penilai ulang, yang menilai dari bacaan tersimpan tanpa menjalankan model):

```python
def ringkas(pembagian, bacaan):
    """Hitungan per kelompok dari bacaan bersih per berkas (berkas -> teks), terhadap label di `pembagian`."""
    hitung = {k: Counter() for k in KELOMPOK}
    for kedatangan in pembagian["uji"]:
        c = hitung[kedatangan["kelompok"]]
        semua = [bacaan.get(b, "") for b in kedatangan["berkas"]]
        for b in semua:
            c["gambar"] += 1
            c["gambar_benar"] += b == kedatangan["teks"]
            c["gambar_luar_pola"] += urai(b) is None
        akhir = suara_terbanyak(semua)
        c["kedatangan"] += 1
        c["kedatangan_benar"] += akhir == kedatangan["teks"]
        c["kedatangan_ragu"] += akhir == ""
    per_kelompok = {}
    for k in KELOMPOK:
        rentang = wilson(hitung[k]["kedatangan_benar"], hitung[k]["kedatangan"])
        per_kelompok[k] = {**{n: hitung[k][n] for n in ISIAN},
                           "rentang_95_kedatangan": [round(rentang[0], 3), round(rentang[1], 3)] if rentang else None,
                           "terlalu_sedikit": hitung[k]["kedatangan"] < SEDIKIT}
    return per_kelompok


def nilai(pembagian, folder_gambar, baca):
    """Membaca semua gambar set uji. Kembali: (baris per gambar, ringkasan tanpa nomor plat)."""
    baris, bacaan, detik = [], {}, 0.0
    for kedatangan in pembagian["uji"]:
        for berkas in kedatangan["berkas"]:
            gambar = cv2.imread(str(Path(folder_gambar) / berkas))
            mulai = time.perf_counter()
            mentah = baca(gambar) if gambar is not None else ""
            detik += time.perf_counter() - mulai
            bacaan[berkas] = bersihkan(mentah)
            baris.append({"berkas": berkas, "kelompok": kedatangan["kelompok"], "label": kedatangan["teks"],
                          "bacaan": bacaan[berkas], "mentah": mentah})
    return baris, {"per_kelompok": ringkas(pembagian, bacaan),
                   "detik_per_gambar": round(detik / len(baris), 3) if baris else None}
```

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `119 passed`, `EXIT=0` (pemisahan tanpa perubahan perilaku).

- [x] **Step 2: Tulis uji penilai ulang**

Buat `tools/lab/uji/test_nilai_ulang.py`:

```python
"""Uji tools/lab/nilai_ulang.py: label dibetulkan dari jawaban owner, plat yang tak pasti dikeluarkan, pembaca dinilai
ulang dari bacaan tersimpan, dan layar tanpa nomor plat."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nilai_ulang as nu  # noqa: E402

SKRIP = Path(__file__).resolve().parents[1] / "nilai_ulang.py"


def k(teks):
    return {"teks": teks, "golongan": "mobil", "kelompok": "mobil-terang", "berkas": [f"test/{teks}_1.png"]}


PEMBAGIAN = {"latih": [k("D9000AB")], "uji": [k("D1500X"), k("D1600X"), k("D1700X"), k("D1800X")]}
CURIGA = {"contoh": [{"nomor": 1, "teks": "D1500X", "usulan": "D2500X", "kelompok": "mobil-terang", "berkas": "test/D1500X_1.png"},
                     {"nomor": 2, "teks": "D1600X", "usulan": "D1600Y", "kelompok": "mobil-terang", "berkas": "test/D1600X_1.png"}]}
CONTOH = {"contoh": [{"nomor": 1, "teks": "D1700X", "kelompok": "mobil-terang", "berkas": "test/D1700X_1.png"},
                     {"nomor": 2, "teks": "D1500X", "kelompok": "mobil-terang", "berkas": "test/D1500X_1.png"}]}


def test_tulisan_b_yang_benar_mengganti_label_dan_kelompoknya():
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, {1}, set(), set())

    ganti = next(x for x in baru["uji"] if x.get("label_penerbit") == "D1500X")
    assert (ganti["teks"], ganti["kelompok"], ganti["golongan"]) == ("D2500X", "motor-terang", "motor")
    assert (hitung["dibetulkan"], hitung["dikeluarkan"]) == (1, 0)


def test_baris_yang_kedua_tulisannya_salah_dikeluarkan():
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, set(), {2}, set())

    assert "D1600X" not in [x["teks"] for x in baru["uji"]]
    assert hitung["dikeluarkan"] == 1


def test_label_salah_dari_lembar_contoh_dikeluarkan_kecuali_sudah_dibetulkan():
    # Baris 1 lembar contoh salah dan tak dibetulkan: keluar. Baris 2 salah tetapi dibetulkan lewat tulisan B.
    baru, hitung = nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, {1}, set(), {1, 2})

    teks = [x["teks"] for x in baru["uji"]]
    assert "D1700X" not in teks and "D2500X" in teks
    assert hitung["dikeluarkan"] == 1


@pytest.mark.parametrize("b_benar, keduanya, salah", [({1}, {1}, set()), ({9}, set(), set()), (set(), set(), {9})])
def test_jawaban_yang_tak_bisa_dipakai_ditolak(b_benar, keduanya, salah):
    with pytest.raises(nu.SalahPakai):
        nu.koreksi(PEMBAGIAN, CURIGA, CONTOH, b_benar, keduanya, salah)


def tulis(tmp_path):
    for nama, isi in (("pembagian.json", PEMBAGIAN), ("curiga.json", CURIGA), ("contoh.json", CONTOH)):
        (tmp_path / nama).write_text(json.dumps(isi))
    bacaan = (("D1500X", "D2500X"), ("D1600X", "D1600X"), ("D1700X", "D1700X"), ("D1800X", "D1800Y"))
    (tmp_path / "hasil.jsonl").write_text("".join(json.dumps({"berkas": f"test/{t}_1.png", "bacaan": b}) + "\n" for t, b in bacaan))
    return [str(tmp_path / n) for n in ("pembagian.json", "curiga.json", "contoh.json")] + [str(tmp_path / "keluar")]


def test_pembaca_dinilai_ulang_terhadap_label_baru(tmp_path):
    argumen = tulis(tmp_path) + ["--b-benar", "1", "--salah-contoh", "1", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    assert nu.utama(argumen) == 0

    r = json.loads((tmp_path / "keluar/ringkasan-koreksi.json").read_text())["pembaca"]["tiruan"]
    assert r["motor-terang"]["kedatangan_benar"] == 1  # label dibetulkan menjadi bacaan yang benar
    assert (r["mobil-terang"]["kedatangan"], r["mobil-terang"]["kedatangan_benar"]) == (2, 1)  # satu dikeluarkan


def test_baris_perintah_tanpa_nomor_plat_di_layar(tmp_path):
    argumen = tulis(tmp_path) + ["--b-benar", "1", "--hasil", f"tiruan={tmp_path / 'hasil.jsonl'}"]

    hasil = subprocess.run([sys.executable, str(SKRIP), *argumen], capture_output=True, text=True)
    salah = subprocess.run([sys.executable, str(SKRIP), *argumen, "--keduanya-salah", "1"], capture_output=True, text=True)

    assert hasil.returncode == 0, hasil.stdout + hasil.stderr
    for larangan in ("1500", "2500", "1600", "1800"):
        assert larangan not in hasil.stdout + (tmp_path / "keluar/ringkasan-koreksi.json").read_text()
    assert salah.returncode == 2 and "SALAH PAKAI" in salah.stdout
```

- [x] **Step 3: Jalankan, pastikan merah karena alatnya belum ada**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `ModuleNotFoundError: No module named 'nilai_ulang'`, `EXIT` bukan 0.

- [x] **Step 4: Tulis alatnya**

Buat `tools/lab/nilai_ulang.py`:

```python
"""Membetulkan label set uji dari jawaban owner atas lembar label yang dicurigai (K22), lalu menilai ulang tiap pembaca.

Aturan:
- Baris lembar curiga yang tulisan B-nya benar menurut owner: label diganti tulisan B. Golongan dan kelompok mobil atau
  motor dihitung ulang dari label baru (kode wilayah dan nomor urut bisa berubah); terang atau gelap tetap.
- Baris yang tulisan A maupun B-nya salah: platnya dikeluarkan dari set uji (tulisan benarnya tidak diketahui).
- Baris lembar contoh yang labelnya diketahui salah (pemeriksaan owner 14 Okt) dan tidak dibetulkan lewat lembar curiga:
  dikeluarkan juga, karena tulisan benarnya tidak ada di repo (owner tidak diminta mengetik nomor plat).
- Kedatangan lain: label penerbit dipakai apa adanya.

Pembaca dinilai ulang dari bacaan yang sudah tersimpan (hasil.jsonl), tanpa menjalankan modelnya lagi.

Keluaran: pembagian-koreksi.json (memuat plat; data/) dan ringkasan-koreksi.json (hitungan saja). Layar hanya hitungan.

  powershell -NoProfile -File tools\\lab.ps1 python /kerja/tools/lab/nilai_ulang.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/lembar-curiga/lembar-curiga.json /kerja/data/keluaran/lembar-contoh/lembar-contoh.json /kerja/data/keluaran/set-uji-koreksi --b-benar <nomor,...> --keduanya-salah <nomor,...> --salah-contoh 19,22,25,35,36,54 --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baca_vlm import KELOMPOK, ringkas, uraikan  # noqa: E402
from plat import golongan, kelompok_kendaraan, urai  # noqa: E402


class SalahPakai(Exception):
    """Jawaban tidak bisa dipakai apa adanya: nomor baris ganda, di luar lembar, atau tak terbaca."""


def nomor(teks):
    """"3, 7,12" -> {3, 7, 12}; teks kosong -> himpunan kosong."""
    try:
        return {int(x) for x in teks.split(",") if x.strip()}
    except ValueError:
        raise SalahPakai(f"daftar nomor baris tidak terbaca: {teks!r}") from None


def koreksi(pembagian, lembar_curiga, lembar_contoh, b_benar, keduanya_salah, salah_contoh):
    """Kembali: (pembagian dengan sisi uji yang sudah dibetulkan, hitungan tanpa nomor plat)."""
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
    uji = []
    for k in pembagian["uji"]:
        if k["teks"] in keluar:
            continue
        if k["teks"] in ganti:
            plat = urai(ganti[k["teks"]])
            cahaya = k["kelompok"].rsplit("-", 1)[1]
            k = {**k, "teks": plat.teks, "label_penerbit": k["teks"], "golongan": golongan(plat),
                 "kelompok": f"{kelompok_kendaraan(plat)}-{cahaya}"}
        uji.append(k)
    latih = {a["teks"] for a in pembagian["latih"]}
    hitung = {"dibetulkan": len(ganti), "dikeluarkan": len(keluar),
              "plat_di_kedua_sisi": sum(k["teks"] in latih for k in uji),
              "kedatangan_per_kelompok": {g: sum(k["kelompok"] == g for k in uji) for g in KELOMPOK}}
    return {"latih": pembagian["latih"], "uji": uji}, hitung


def baca_hasil(jalur):
    """berkas -> bacaan bersih, dari hasil.jsonl sebuah pembaca."""
    return {b["berkas"]: b["bacaan"] for b in map(json.loads, Path(jalur).read_text().splitlines())}


def utama(argumen=None):
    urai_argumen = argparse.ArgumentParser(description="Membetulkan label set uji dan menilai ulang pembaca (K22).")
    for nama in ("pembagian", "lembar_curiga", "lembar_contoh", "keluar"):
        urai_argumen.add_argument(nama)
    urai_argumen.add_argument("--b-benar", default="")
    urai_argumen.add_argument("--keduanya-salah", default="")
    urai_argumen.add_argument("--salah-contoh", default="")
    urai_argumen.add_argument("--hasil", action="append", default=[], help="nama=jalur hasil.jsonl, boleh berulang")
    p = urai_argumen.parse_args(argumen)
    try:
        if not p.hasil or not all("=" in h for h in p.hasil):
            raise SalahPakai("--hasil harus diberi sebagai nama=jalur, paling sedikit satu")
        baru, hitung = koreksi(json.loads(Path(p.pembagian).read_text()), json.loads(Path(p.lembar_curiga).read_text()),
                               json.loads(Path(p.lembar_contoh).read_text()), nomor(p.b_benar),
                               nomor(p.keduanya_salah), nomor(p.salah_contoh))
    except SalahPakai as galat:
        print(f"SALAH PAKAI: {galat}")
        return 2
    ringkasan = {**hitung, "pembaca": {nama: ringkas(baru, baca_hasil(jalur))
                                       for nama, jalur in (h.split("=", 1) for h in p.hasil)}}
    keluar = Path(p.keluar)
    keluar.mkdir(parents=True, exist_ok=True)
    (keluar / "pembagian-koreksi.json").write_text(json.dumps(baru, indent=1))
    (keluar / "ringkasan-koreksi.json").write_text(json.dumps(ringkasan, indent=2))
    print(f"dibetulkan {hitung['dibetulkan']}, dikeluarkan {hitung['dikeluarkan']}, "
          f"plat di kedua sisi {hitung['plat_di_kedua_sisi']}; kedatangan uji {hitung['kedatangan_per_kelompok']}")
    for nama, per_kelompok in ringkasan["pembaca"].items():
        print(nama)
        for k in KELOMPOK:
            print(f"  {k:<13} {uraikan(per_kelompok[k])}")
    return 0


if __name__ == "__main__":
    sys.exit(utama())
```

- [x] **Step 5: Jalankan, pastikan hijau**

Run: `npm run test:lab; echo "EXIT=$?"`
Expected: `127 passed` (119 + 8 baru) dan `EXIT=0`.

- [x] **Step 6: Jalankan dengan jawaban owner**

Run (PowerShell), dengan nomor baris dari jawaban owner (bila sebuah daftar kosong, `--b-benar ""` atau
`--keduanya-salah ""`):
`powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/nilai_ulang.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/lembar-curiga/lembar-curiga.json /kerja/data/keluaran/lembar-contoh/lembar-contoh.json /kerja/data/keluaran/set-uji-koreksi --b-benar <...> --keduanya-salah <...> --salah-contoh 19,22,25,35,36,54 --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl; "EXIT=$LASTEXITCODE"`
Expected: satu baris hitungan (dibetulkan, dikeluarkan, `plat di kedua sisi 0`, kedatangan per kelompok), lalu empat
baris kelompok untuk tiap pembaca, `EXIT=0`. `plat di kedua sisi` lebih dari 0 berarti label baru sama dengan plat di
bahan latih: **berhenti dan laporkan**.

- [x] **Step 7: Commit**

```bash
git add tools/lab/baca_vlm.py tools/lab/nilai_ulang.py tools/lab/uji/test_nilai_ulang.py
git commit -q -F - <<'EOF'
Label set uji dibetulkan dari jawaban owner, pembaca dinilai ulang

Alasan: langkah terakhir K22. Label penerbit salah pada kira-kira 1 dari 10
contoh, jadi angka pembaca dibaca ulang terhadap label yang sudah
dibetulkan. Plat yang tulisan benarnya tidak diketahui dikeluarkan dari set
uji, bukan ditebak; label dan kelompoknya dihitung ulang dari tulisan yang
dipilih owner.

ringkas() dipisah dari nilai() di baca_vlm.py tanpa mengubah perilaku (uji
lama tetap 119 hijau), supaya penilaian ulang tidak perlu menjalankan model.
Uji ditulis lebih dulu dan terlihat merah (ModuleNotFoundError:
nilai_ulang). Gerbang lab: 119 -> 127. Jawaban owner: <nomor baris>.
Hasil: <angka Step 6>.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 6: Laporan, catatan, dan laporan ke owner

**Files:**
- Create: `bukti/<tanggal>-label-dan-pembaca-kedua.md` dan empat ringkasan JSON
- Modify: `data-asal/bahan.json`, `CLAUDE.md`, `OPEN-QUESTIONS.md`, `ROADMAP.md`, rencana ini

- [x] **Step 1: Salin ringkasan ke `bukti/`, sesudah dibuktikan tanpa nomor plat (dengan kontrol positif)**

Tulis berkas sekali pakai `data/alat-sementara/periksa-bukti-6.py`, dengan pola `periksa-bukti.py` Rencana 5. Daftar
larangannya: teks plat dan nama berkas di `pembagian.json`, ditambah `usulan` di `label-curiga/curiga.json`. Sebelum
memeriksa ringkasan, pemeriksa dijalankan pada `pembagian-koreksi.json` dan harus menemukan larangan (kontrol positif);
bila tidak, berhenti. Ringkasan yang diperiksa dan disalin ke `data/keluaran/bukti-siap/`:
`baca-fpo/ringkasan.json`, `label-curiga/ringkasan.json`, `set-uji-koreksi/ringkasan-koreksi.json`.

Expected: kontrol positif menemukan lebih dari 0; ketiga ringkasan `0 teks plat atau nama berkas ditemukan`; `EXIT=0`.
Lalu salin ke `bukti/` dari Git Bash.

- [x] **Step 2: Tulis laporan**

`bukti/<tanggal>-label-dan-pembaca-kedua.md`. Semua angka dibaca dari JSON di `bukti/` dan keluaran Task 2–5:

1. **Apa yang diukur:** pembaca kedua (fast-plate-ocr) pada set uji yang sama; label yang dicurigai; pembetulan label
   menurut K22; kedua pembaca dinilai ulang.
2. **Model dan unduhan:** dua berkas, cocok dengan digest GitHub; bacaan plat buatan; ada-tidaknya Indonesia di
   konfigurasi terbitan.
3. **fast-plate-ocr terhadap label penerbit:** per kelompok, dengan rentang 95%; detik per gambar di CPU laptop.
4. **Label yang dicurigai:** N dari 945; per kelompok; penilaian cara pada 60 contoh (tertangkap X dari 6, ikut dicurigai
   Y dari 54).
5. **Jawaban owner, dalam nomor baris dan jumlah:** dibetulkan, dikeluarkan.
6. **Kedua pembaca terhadap label yang sudah dibetulkan:** per kelompok, dengan rentang 95%, dibandingkan dengan angka
   sebelum dibetulkan.
7. **Batas:** label salah yang dibaca salah dengan cara sama oleh kedua pembaca bisa lolos (taksiran dari langkah 4);
   label bahan latih belum diperiksa; potongan plat, bukan kamera gerbang (K9 tidak terbukti dari sini); terang-gelap
   taksiran; fast-plate-ocr dan Qwen3-VL alat lab, bukan produk; satu model fast-plate-ocr saja yang dicoba.

- [x] **Step 3: Perbarui catatan (skrip pencatat berkas; jangkar tepat sekali)**

1. `data-asal/bahan.json`, butir `bobot-fast-plate-ocr`: catatan "Model cct-s-v2-global diunduh <tanggal> lewat pintu
   unduh berkas, cocok dengan digest GitHub, dikunci di tools/vendor.lock.json (berkas fpo-cct-s-v2-onnx dan
   fpo-cct-s-v2-config). Alat lab (K22), bukan bagian produk." Butir `dataset-indo-alpr`: hasil pembetulan label.
2. `CLAUDE.md` §7: pintu unduh berkas kini juga menerima rilis GitHub (`github.com`, `release-assets.githubusercontent.com`);
   model fast-plate-ocr ada di `data/unduhan/fpo-*` dan hanya dimuat lewat gerbang berkas terkunci.
3. `OPEN-QUESTIONS.md` bagian B: paragraf baru di atas "Sesudah K22", dengan angka dan artinya bagi B1 dan B6.
4. `ROADMAP.md`: butir pemeriksaan owner dan "Rencana 6 dijalankan" dicentang dengan angka; butir baru
   `- [ ] Rencana 7 Fase 0A ditulis ← di sini sekarang`; baris status; satu baris changelog dengan hasil, alasan, dan batas.
5. Rencana ini: kotak langkah dicentang, dan "Catatan pelaksanaan" di akhir bila ada yang berbeda dari tulisan di atas.

- [x] **Step 4: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` (satu per satu)
Expected: `pass 101` dan `127 passed`, keduanya `EXIT=0`.

Run: `git status --short`
Expected: hanya `bukti/` dan berkas catatan. Tidak ada berkas dari `data/` atau `models/`.

Commit dengan pesan beralasan (angka pembaca sebelum dan sesudah label dibetulkan, dan kenapa itu belum angka produk).

- [x] **Step 5: Laporkan ke owner**

Ringkasan singkat dalam bahasa sehari-hari: angka kedua pembaca sesudah label dibetulkan, berapa label penerbit yang
salah, batasnya, lalu **satu** pertanyaan untuk langkah berikutnya (Rencana 7).

---

## Pemeriksaan diri atas rencana ini

- **Cakupan K22:** pembaca kedua → Task 2–3; label yang dicurigai dan lembarnya → Task 4; pembetulan dan penilaian ulang
  → Task 5. Batas K22 (label salah yang lolos) ditaksir di Task 4 Step 9 dari 60 contoh yang sudah diperiksa owner.
- **Cakupan spec:** 8.1 langkah 5 (label diperiksa manusia) dan langkah 6 (pembanding paket jadi) → Task 3–5. 8.3 (angka
  dengan jumlah dan rentang, kelompok di bawah 30, kelompok kosong) → `ringkas` dan `uraikan` yang sama dengan Rencana 5.
  Yang **tidak** dicakup: mesin belajar, foto utuh, plat buatan, kecepatan (Rencana 7).
- **Data pribadi:** owner menjawab dengan nomor baris; tiap alat baru punya uji "layar tanpa nomor plat"; alat yang
  membuka gambar berplat memuat modul yang membisukan log OpenCV, dan uji `baca_fpo` membuktikannya di proses terpisah.
- **Rantai pasok:** bobot lewat pintu, dikunci ke digest penerbit, diperiksa lagi sebelum dimuat; kode dari klon terkunci
  yang diperiksa commit-nya; jalur unduh otomatis tidak dipakai; percobaan pertama sudah di lab tanpa jaringan.
- **Tanpa isian kosong pada kode:** semua kode alat dan uji tertulis lengkap. Isian bersudut hanya pada angka hasil,
  nomor baris jawaban owner, dan tanggal; tiap isian menyebut langkah asalnya.
- **Nama yang konsisten:** `daftar_berkas`, `verifikasi_berkas` (model_terkunci); `ubah_warna`, `PembacaFpo`,
  `BUTIR_MODEL`, `BUTIR_KONFIGURASI` (baca_fpo); `cari`, `nilai_cara`, `baca_hasil` (label_curiga); `urutkan`
  (lembar_curiga); `ringkas` (baca_vlm); `koreksi`, `nomor`, `SalahPakai` (nilai_ulang). `KELOMPOK` sama di semua alat.
- **Angka gerbang:** Node 99 → 101. Lab 100 → 106 → 111 → 116 → 119 → 119 → 127; dua uji model sungguhan di luar gerbang.

## Catatan pelaksanaan (14 Okt 2026)

Dijalankan atas lampu hijau owner ("a"). Hasil dan batasnya di [`../bukti/2026-10-14-label-dan-pembaca-kedua.md`](../bukti/2026-10-14-label-dan-pembaca-kedua.md).
Yang berbeda dari tulisan di atas:

- **Task 5 Step 6 berhenti** seperti yang ditetapkan: "plat di kedua sisi 3". Owner memilih mengeluarkan ketiganya dari
  set uji (K23). Satu uji ditambahkan (`test_label_baru_yang_sama_dengan_plat_latih_dikeluarkan`, merah dulu) dan
  `koreksi()` kini menghitungnya sebagai `dikeluarkan_bocor`. Gerbang lab akhir 128 (tertulis 127).
- **Jawaban owner atas lembar curiga:** B benar pada 29 baris; baris 7 dan 12 salah. Owner menuliskan tulisan yang benar
  untuk kedua baris itu di percakapan; karena nomor plat dari percakapan tidak disalin ke berkas (`CLAUDE.md` §4), kedua
  baris dijalankan sebagai `--keduanya-salah` (dikeluarkan).
- **Task 5 Step 1:** selain uji lama, `ringkas()` dibuktikan sama persis dengan ringkasan lama pada data sungguhan untuk
  kedua pembaca (skrip sekali pakai, hanya mencetak "sama" atau "beda").
- **Task 6 Step 1:** daftar larangan 9.718; kontrol positif menemukan 9.699; nama berkas di `bukti/`:
  `2026-10-14-baca-fpo-pertama.json`, `2026-10-14-label-curiga.json`, `2026-10-14-set-uji-koreksi.json`; laporan
  `2026-10-14-label-dan-pembaca-kedua.md`.
- **Batas yang tidak diperkirakan rencana:** angka "sesudah" memihak kedua pembaca (lihat laporan bagian 6).
