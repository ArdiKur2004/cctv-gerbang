# Fase 0A, Rencana 1: Bengkel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution` (aturan global dan prompt sesi 2).

**Goal:** Menyiapkan bengkel Fase 0A: satu perintah gerbang uji, alat unduh yang kode keluarnya jujur, daftar bahan
beserta pemeriksa "mesin jualan", dan pintu lab tanpa jaringan.

**Architecture:** Empat alat kecil di `tools/`, masing-masing satu tugas, masing-masing dijaga uji `node:test` di
`tools/uji/`. Pintu ke Docker ditulis PowerShell dan diuji lewat mode `-Kering` (mencetak argumen docker tanpa
menjalankannya) serta lewat "docker tiruan" untuk uji rantai. Daftar bahan dan pemeriksanya ditulis Node tanpa
dependensi. Tidak ada paket yang dipasang dan tidak ada yang diunduh di rencana ini.

**Tech Stack:** Node 24 (`node:test`, tanpa dependensi) · Windows PowerShell 5.1 · Docker (image `vision-seed-lab:v1`
yang sudah ada di mesin, dijaga lewat ID-nya) · git.

**Dasar:** spec [`../specs/2026-10-13-cctv-gerbang-desain-induk.md`](../specs/2026-10-13-cctv-gerbang-desain-induk.md)
bagian 8.1 langkah 1, bagian 2.4, dan bagian 8.6. Keputusan owner K14, K15, K17, K18 di
[`../SEED.md`](../SEED.md) §3.

---

## Kenapa Fase 0A dipecah menjadi empat rencana

Isi rencana berikutnya bergantung pada temuan rencana sebelumnya: komponen mana yang lolos vonis izin, apa isi 45
video, dan seperti apa peraturan platnya. Menulis kode untuk langkah-langkah itu sekarang berarti mengarang. Maka tiap
rencana ditulis saat masukannya sudah ada.

| Rencana | Langkah spec 8.1 | Isi | Ditulis saat |
|---|---|---|---|
| **1 (dokumen ini)** | 1 | Bengkel: gerbang uji, alat unduh jujur, daftar bahan, pemeriksa mesin jualan, pintu lab | Sekarang |
| 2 | 2, 3, sebagian 4 | Vonis izin tiap komponen pada commit terkunci; ringkasan peraturan plat dari teks aslinya; unduhan dataset berizin | Rencana 1 selesai |
| 3 | 4, 5 | Pemilahan 45 video; pembuat plat buatan komputer; set uji pertama | Rencana 2 selesai, dan owner memutuskan cara pemeriksaan label (spec 8.5) |
| 4 | 6, 7, 8, 9 | Pembanding; mesin belajar pertama; taksiran kecepatan; laporan ke `bukti/` | Rencana 3 selesai |

## Aturan eksekusi untuk semua task

- **Satu suite uji pada satu waktu.** Jangan menjalankan dua rentetan uji bersamaan.
- **Jangan `| tail` atau `| head` pada perintah uji.** Jalankan penuh dan baca ringkasan `pass` / `fail`.
- **`exit ≠ 0` belum tentu uji merah.** Kode 3 dari `tools\lab.ps1` berarti bengkel sedang dipakai job lain (misalnya
  vision-seed sedang melatih); ulangi nanti.
- **vision-seed hanya dibaca.** Berkas disalin darinya dengan `cp`; tidak ada yang ditulis ke sana.
- **Tidak ada unduhan dan tidak ada pemasangan paket** di rencana ini.
- Commit dalam Bahasa Indonesia, memuat alasan, diakhiri baris
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Semua perintah dijalankan dari akar repo `D:\Projects\super-team-v1\cctvgerbang-seed` lewat Git Bash, kecuali
  disebut lain.

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `package.json` (baru) | Satu perintah gerbang uji: `npm test` | 1 |
| `tools/ambil-video.ps1` (ubah) | Pintu pengunduh video. Ditambah: kode 8 bila unduhan terpotong | 2 |
| `tools/uji/ambil-video.test.mjs` (ubah) | Uji pintu pengunduh. Ditambah: uji rantai dengan docker tiruan | 2 |
| `data-asal/bahan.json` (baru) | Daftar semua bahan latih dan bahan uji beserta vonisnya | 3 |
| `tools/bahan.mjs` (baru) | Membaca dan memeriksa daftar bahan | 3 |
| `tools/uji/bahan.test.mjs` (baru) | Uji pemeriksa daftar bahan | 3 |
| `tools/periksa-jualan.mjs` (baru) | Menolak "mesin jualan" yang memuat bahan bukan `BOLEH-PRODUK` | 4 |
| `tools/uji/periksa-jualan.test.mjs` (baru) | Uji pemeriksa mesin jualan | 4 |
| `tools/lab.ps1` (baru, disalin lalu disesuaikan) | Pintu lab: container tanpa jaringan | 5 |
| `tools/uji/lab.test.mjs` (baru) | Uji pintu lab | 5 |
| `CLAUDE.md`, `ROADMAP.md` (ubah) | Mencatat gerbang uji dan hasil rencana ini | 6 |

---

### Task 1: Satu perintah gerbang uji

`node --test tools/uji/` gagal di mesin ini (Node 24 menganggap folder itu modul), sehingga alat ukurnya sendiri
terlihat seperti uji merah. Gerbang uji dikunci menjadi satu perintah yang sudah terbukti jalan.

**Files:**
- Create: `package.json`

- [ ] **Step 1: Catat angka sebelum**

Run: `node --test "tools/uji/*.test.mjs"; echo "EXIT=$?"`
Expected: `ℹ tests 29`, `ℹ pass 29`, `ℹ fail 0`, `EXIT=0`

- [ ] **Step 2: Tulis `package.json`**

```json
{
  "name": "cctvgerbang-seed",
  "private": true,
  "description": "CCTV Gerbang: alat bengkel. Gerbang uji: npm test",
  "scripts": {
    "test": "node --test \"tools/uji/*.test.mjs\""
  }
}
```

- [ ] **Step 3: Jalankan gerbang lewat perintah barunya**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 29`, `ℹ pass 29`, `ℹ fail 0`, `EXIT=0`. Angkanya harus sama dengan Step 1; kalau berbeda,
perintahnya tidak menjalankan berkas yang sama.

- [ ] **Step 4: Commit**

```bash
git add package.json
git commit -q -F - <<'EOF'
Gerbang uji satu perintah: npm test

`node --test tools/uji/` gagal di Node 24 karena folder dianggap modul,
sehingga alat ukurnya sendiri terlihat seperti uji merah. Gerbang dikunci
ke pola berkas yang terbukti menjalankan ke-29 uji.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 2: Alat unduh melapor gagal bila unduhan terpotong

Temuan 13 Okt (`ROADMAP.md`, "Temuan di luar lingkup"): `tools\ambil-video.ps1` mengembalikan kode 0 ketika unduhan
terpotong di batas 400 MB dan meninggalkan berkas `.mp4.part`. Perbaikan: sesudah pengunduh keluar 0, pintu memeriksa
folder keluaran; bila ada berkas `.part`, ia keluar dengan kode 8.

Supaya rantainya bisa diuji tanpa internet, pintu menerima dua pengganti lewat variabel lingkungan, sejalan dengan
`VS_ALAT_YTDLP` dan `VS_KUNCI_VENDOR` yang sudah ada: `VS_DOCKER` (program yang dipanggil sebagai docker) dan
`VS_KELUAR` (folder keluaran).

**Files:**
- Modify: `tools/ambil-video.ps1`
- Test: `tools/uji/ambil-video.test.mjs`

- [ ] **Step 1: Tulis uji yang gagal**

Tambahkan di akhir `tools/uji/ambil-video.test.mjs`:

```js
function dockerTiruan() {
  // Pengganti docker untuk uji rantai. Menjawab `image inspect` dengan ID dari TIRUAN_ID; pada `run` ia menulis satu
  // berkas bernama TIRUAN_BERKAS ke folder yang dipasang sebagai /keluar lalu keluar 0, seperti pengunduh yang
  // melapor berhasil.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    "$pasang = $args | Where-Object { $_ -like 'type=bind,source=*,target=/keluar' }",
    "$keluar = ($pasang -replace '^type=bind,source=', '') -replace ',target=/keluar$', ''",
    "Set-Content -LiteralPath (Join-Path $keluar $env:TIRUAN_BERKAS) -Value 'x'",
    'exit 0',
  ].join('\r\n'));
  return berkas;
}

function unduhDenganTiruan(namaBerkas) {
  const { folder, sha } = repoSementara();
  const keluar = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-keluar-'));
  const r = jalankan(['unduh', 'https://youtu.be/abc'], {
    VS_ALAT_YTDLP: folder,
    VS_KUNCI_VENDOR: kunciSementara(sha, { nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' }),
    VS_DOCKER: dockerTiruan(),
    VS_KELUAR: keluar,
    TIRUAN_ID: 'sha256:tiruan',
    TIRUAN_BERKAS: namaBerkas,
  });
  return { ...r, isiKeluar: fs.readdirSync(keluar) };
}

test('unduh yang meninggalkan berkas .part dilaporkan GAGAL (kode 8) walau pengunduhnya keluar 0', () => {
  // Terjadi 13 Okt pada 2 dari 49 video: unduhan terpotong di batas 400 MB, kode keluar 0, video utuhnya tidak ada.
  const r = unduhDenganTiruan('youtube-abc.mp4.part');

  assert.deepEqual(r.isiKeluar, ['youtube-abc.mp4.part'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 8, r.keluar + r.galat);
  assert.match(r.keluar, /UNDUHAN TERPOTONG/);
  assert.match(r.keluar, /youtube-abc\.mp4\.part/);
});

test('unduh yang menghasilkan berkas utuh tetap kode 0', () => {
  const r = unduhDenganTiruan('youtube-abc.mp4');

  assert.deepEqual(r.isiKeluar, ['youtube-abc.mp4'], 'docker tiruan harus benar-benar dipanggil');
  assert.equal(r.kode, 0, r.keluar + r.galat);
});
```

- [ ] **Step 2: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 31`, `ℹ pass 29`, `ℹ fail 2`, `EXIT=1`. Kedua uji baru gagal pada baris `isiKeluar` (folder
keluaran kosong) karena pintu belum mengenal `VS_DOCKER` dan `VS_KELUAR`: ia memanggil docker sungguhan untuk
`image inspect`, mendapat ID yang bukan `sha256:tiruan`, dan berhenti dengan kode 6. Tidak ada container yang jalan.

- [ ] **Step 3: Terapkan perubahan di `tools/ambil-video.ps1`**

(a) Tepat sesudah baris `$kunciVendor = if ($env:VS_KUNCI_VENDOR) ...`, tambahkan:

```powershell
# Untuk uji rantai (tools\uji\ambil-video.test.mjs): program docker dan folder keluaran bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
```

(b) Ganti baris

```powershell
$riset = Join-Path $akar 'data\video\riset'
```

menjadi

```powershell
$riset = if ($env:VS_KELUAR) { $env:VS_KELUAR } else { Join-Path $akar 'data\video\riset' }
```

(c) Ganti baris

```powershell
$idImage = docker image inspect $image --format '{{.Id}}' 2>$null
```

menjadi

```powershell
$idImage = & $docker image inspect $image --format '{{.Id}}' 2>$null
```

(d) Ganti dua baris terakhir berkas

```powershell
& docker @argumen
exit $LASTEXITCODE
```

menjadi

```powershell
& $docker @argumen
$kode = $LASTEXITCODE
if ($kode -eq 0 -and $perintah -eq 'unduh') {
    # Kode 0 dari pengunduh bukan bukti berkasnya utuh: unduhan yang terpotong di --max-filesize keluar 0 dan
    # meninggalkan berkas .part. Yang dinilai adalah berkasnya.
    $terpotong = @(Get-ChildItem -LiteralPath $riset -Filter '*.part' -File)
    if ($terpotong.Count -gt 0) {
        Write-Host ("UNDUHAN TERPOTONG: pengunduh keluar 0, tetapi berkas ini belum utuh: {0}. Hapus berkas itu, lalu ulangi dengan resolusi lebih rendah." -f (($terpotong | ForEach-Object { $_.Name }) -join ', '))
        exit 8
    }
}
exit $kode
```

(e) Di blok komentar atas, tepat sesudah baris `  - Image lab yang ID-nya bukan yang tercatat di kunci TIDAK dijalankan (kode 6).`,
tambahkan:

```
  - Unduhan yang meninggalkan berkas .part dilaporkan gagal (kode 8), walau pengunduhnya keluar 0.
    BELUM tertangani: pengunduh yang menolak sebelum mulai mengunduh (tanpa berkas .part) tetap keluar 0. Pemanggil
    tetap wajib memeriksa bahwa berkas jadinya ada.
```

- [ ] **Step 4: Jalankan uji untuk memastikan lulus**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 31`, `ℹ pass 31`, `ℹ fail 0`, `EXIT=0`

- [ ] **Step 5: Pastikan jalur sungguhan tidak rusak**

Run (PowerShell): `powershell -NoProfile -File tools\ambil-video.ps1 periksa; "EXIT=$LASTEXITCODE"`
Expected: `alat sesuai kunci: D:\Projects\super-team-v1\cctvgerbang-seed\vendor\yt-dlp` dan `EXIT=0`

Run (PowerShell): `powershell -NoProfile -File tools\ambil-video.ps1 cari "palang parkir otomatis baca plat nomor" 3; "EXIT=$LASTEXITCODE"`
Expected: tiga baris berbentuk `id | detik | kanal | tayangan | judul` dan `EXIT=0`. Ini membuktikan docker sungguhan
masih dipanggil bila `VS_DOCKER` tidak diisi.

- [ ] **Step 6: Commit**

```bash
git add tools/ambil-video.ps1 tools/uji/ambil-video.test.mjs
git commit -q -F - <<'EOF'
Alat unduh: lapor gagal (kode 8) bila unduhan terpotong

Pada 13 Okt alat ini melaporkan 42 unduhan berhasil padahal hanya 40
berkas utuh: dua video terpotong di batas 400 MB, kode keluarnya 0, dan
yang tertinggal berkas .part. Sekarang yang dinilai berkasnya, bukan kode
keluar pengunduh.

Rantainya diuji dengan docker tiruan (VS_DOCKER, VS_KELUAR), sejalan
dengan pengganti yang sudah ada untuk alat dan kunci vendor.

Batas yang ditulis di kepala berkas: pengunduh yang menolak sebelum mulai
mengunduh tidak meninggalkan .part dan tetap keluar 0; itu belum
tertangani.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: Daftar bahan dan pemeriksanya

Spec 2.4 dan K15: tiap bahan latih atau bahan uji tercatat asal, izin, dan vonisnya. Bahan yang tak tercatat tidak
boleh dipakai melatih.

**Files:**
- Create: `data-asal/bahan.json`
- Create: `tools/bahan.mjs`
- Test: `tools/uji/bahan.test.mjs`

- [ ] **Step 1: Tulis uji yang gagal**

Buat `tools/uji/bahan.test.mjs`:

```js
// Uji tools/bahan.mjs: daftar bahan latih dan bahan uji (K15). Tiap bahan punya asal, izin, dan vonis; yang cacat
// ditolak, karena daftar inilah yang dibaca tools/periksa-jualan.mjs saat menilai sebuah mesin.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'bahan.mjs');
const BAIK = {
  id: 'dataset-contoh', jenis: 'dataset', nama: 'Dataset contoh', sumber: 'https://contoh.test/data',
  lisensi: 'CC BY 4.0', bukti_lisensi: 'https://contoh.test/lisensi', vonis: 'BOLEH-PRODUK', dicatat: '2026-10-13',
};

function tulis(isi) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-bahan-')), 'bahan.json');
  fs.writeFileSync(berkas, typeof isi === 'string' ? isi : JSON.stringify(isi));
  return berkas;
}

function periksa(...args) {
  const r = spawnSync('node', [SKRIP, 'periksa', ...args], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}

test('daftar yang benar diterima dan diringkas per vonis', () => {
  const r = periksa(tulis({ bahan: [BAIK, { ...BAIK, id: 'video-contoh', jenis: 'video', vonis: 'RISET-SAJA', bukti_lisensi: '' }] }));

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /2 bahan tercatat/);
  assert.match(r.keluar, /BOLEH-PRODUK=1/);
  assert.match(r.keluar, /RISET-SAJA=1/);
});

for (const kolom of ['id', 'jenis', 'nama', 'sumber', 'lisensi', 'vonis', 'dicatat']) {
  test(`bahan tanpa "${kolom}" ditolak (kode 1)`, () => {
    const r = periksa(tulis({ bahan: [{ ...BAIK, [kolom]: '' }] }));

    assert.equal(r.kode, 1, r.keluar);
    assert.match(r.keluar, new RegExp(`"${kolom}" wajib diisi`));
  });
}

test('vonis di luar daftar ditolak: salah ketik tidak boleh lolos sebagai vonis baru', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, vonis: 'BOLEH' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /vonis "BOLEH" tak dikenal/);
});

test('jenis di luar daftar ditolak', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, jenis: 'gambar' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /jenis "gambar" tak dikenal/);
});

test('id yang dipakai dua kali ditolak', () => {
  const r = periksa(tulis({ bahan: [BAIK, BAIK] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /id dipakai dua kali/);
});

test('vonis BOLEH-PRODUK tanpa bukti izin ditolak: yang boleh dijual harus bisa ditunjukkan dasarnya', () => {
  const r = periksa(tulis({ bahan: [{ ...BAIK, bukti_lisensi: '' }] }));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bukti_lisensi/);
});

test('berkas yang tak terbaca ditolak (kode 1), bukan dianggap daftar kosong', () => {
  const r = periksa(tulis('{ ini bukan json'));

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /tak terbaca/);
});

test('perintah selain periksa ditolak (kode 2)', () => {
  const r = spawnSync('node', [SKRIP, 'hapus'], { encoding: 'utf8' });

  assert.equal(r.status, 2, r.stdout + r.stderr);
});

test('rantai: daftar bahan milik repo ini lolos pemeriksaan dan tidak kosong', () => {
  // Tanpa argumen berkas, yang diperiksa adalah data-asal/bahan.json sungguhan. Jumlahnya sengaja tidak dikunci:
  // daftar itu bertambah tiap ada bahan baru.
  const r = periksa();

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /^[1-9]\d* bahan tercatat/);
});
```

- [ ] **Step 2: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `EXIT=1`. Semua uji di `bahan.test.mjs` gagal dengan `Cannot find module ... tools\bahan.mjs`, karena
alatnya belum ada. 31 uji lama tetap lulus.

- [ ] **Step 3: Tulis `tools/bahan.mjs`**

```js
#!/usr/bin/env node
// Daftar bahan latih dan bahan uji (K15, spec bagian 2.4). Tiap bahan punya satu baris di data-asal/bahan.json: asal,
// izin, dan vonisnya. Bahan yang tak tercatat di sana tidak boleh dipakai melatih.
//
// Gagal tertutup: berkas yang tak terbaca, kolom wajib yang kosong, id ganda, atau vonis di luar daftar => exit 1.
// Vonis BOLEH-PRODUK wajib punya bukti_lisensi (alamat halaman izin yang dibaca), supaya "boleh dijual" bisa ditunjukkan
// dasarnya.
//
// Pakai:  node tools/bahan.mjs periksa [berkas-bahan]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AKAR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
export const BERKAS_BAHAN = path.join(AKAR, 'data-asal', 'bahan.json');
export const VONIS = ['BOLEH-PRODUK', 'RISET-SAJA', 'DILARANG', 'BELUM-JELAS'];
export const JENIS = ['video', 'dataset', 'bobot', 'huruf', 'sintetis', 'rekaman'];
const WAJIB = ['id', 'jenis', 'nama', 'sumber', 'lisensi', 'vonis', 'dicatat'];
const terisi = (nilai) => typeof nilai === 'string' && nilai.trim() !== '';

export function muatBahan(berkas = BERKAS_BAHAN) {
  let isi;
  try {
    isi = JSON.parse(fs.readFileSync(berkas, 'utf8'));
  } catch (e) {
    return { bahan: [], galat: [`${berkas}: tak terbaca (${e.message})`] };
  }
  if (!Array.isArray(isi.bahan)) return { bahan: [], galat: [`${berkas}: kunci "bahan" harus berupa daftar`] };

  const galat = [];
  const terlihat = new Set();
  for (const [i, b] of isi.bahan.entries()) {
    const sebut = terisi(b?.id) ? `bahan "${b.id}"` : `bahan ke-${i + 1}`;
    for (const k of WAJIB) if (!terisi(b?.[k])) galat.push(`${sebut}: "${k}" wajib diisi`);
    if (terisi(b?.id)) {
      if (!/^[a-z0-9][a-z0-9-]*$/.test(b.id)) galat.push(`${sebut}: id hanya boleh huruf kecil, angka, dan tanda hubung`);
      if (terlihat.has(b.id)) galat.push(`${sebut}: id dipakai dua kali`);
      terlihat.add(b.id);
    }
    if (terisi(b?.jenis) && !JENIS.includes(b.jenis)) galat.push(`${sebut}: jenis "${b.jenis}" tak dikenal (pilihan: ${JENIS.join(', ')})`);
    if (terisi(b?.vonis) && !VONIS.includes(b.vonis)) galat.push(`${sebut}: vonis "${b.vonis}" tak dikenal (pilihan: ${VONIS.join(', ')})`);
    if (b?.vonis === 'BOLEH-PRODUK' && !terisi(b.bukti_lisensi)) {
      galat.push(`${sebut}: vonis BOLEH-PRODUK wajib punya "bukti_lisensi" (alamat halaman izin yang dibaca)`);
    }
  }
  return { bahan: isi.bahan, galat };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [perintah, berkas] = process.argv.slice(2);
  if (perintah !== 'periksa') {
    console.error('Pakai: node tools/bahan.mjs periksa [berkas-bahan]');
    process.exit(2);
  }
  const { bahan, galat } = muatBahan(berkas ?? BERKAS_BAHAN);
  if (galat.length) {
    for (const g of galat) console.error(`DITOLAK ${g}`);
    console.error(`${galat.length} cacat; daftar bahan tidak sah.`);
    process.exit(1);
  }
  console.log(`${bahan.length} bahan tercatat: ${VONIS.map((v) => `${v}=${bahan.filter((b) => b.vonis === v).length}`).join(', ')}`);
}
```

- [ ] **Step 4: Tulis `data-asal/bahan.json`**

```json
{
  "_tentang": "Daftar bahan latih dan bahan uji (K15). Tiap bahan punya satu baris: asal, izin, dan vonisnya. Bahan yang tak tercatat di sini tidak boleh dipakai melatih. Diperiksa tools/bahan.mjs; dibaca tools/periksa-jualan.mjs untuk menolak mesin jualan yang memuat bahan bukan BOLEH-PRODUK.",
  "bahan": [
    {
      "id": "video-riset-youtube",
      "jenis": "video",
      "nama": "Video riset dari YouTube, gelombang pertama (45 video)",
      "sumber": "data-asal/video-riset.json",
      "lisensi": "tidak dinyatakan sumber (lisensi standar situs)",
      "bukti_lisensi": "",
      "vonis": "RISET-SAJA",
      "dicatat": "2026-10-13",
      "catatan": "Diambil lewat tools/ambil-video.ps1 (K17). Plat di dalamnya data pribadi. Isinya belum dilihat."
    }
  ]
}
```

- [ ] **Step 5: Jalankan uji untuk memastikan lulus**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ fail 0`, `EXIT=0`. Jumlah uji naik dari 31 menjadi 46 (15 uji baru: 1 + 7 + 1 + 1 + 1 + 1 + 1 + 1 + 1).

- [ ] **Step 6: Commit**

```bash
git add tools/bahan.mjs tools/uji/bahan.test.mjs data-asal/bahan.json
git commit -q -F - <<'EOF'
Daftar bahan dan pemeriksanya

K15 mewajibkan tiap bahan latih tercatat asal, izin, dan vonisnya. Daftar
ini menjadi satu-satunya sumber yang dibaca saat sebuah mesin dinilai boleh
dijual atau tidak, jadi pemeriksanya gagal tertutup: berkas tak terbaca,
kolom kosong, id ganda, atau vonis salah ketik semuanya ditolak.

Bahan pertama yang tercatat: 45 video riset dari K17, bervonis RISET-SAJA.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: Pemeriksa mesin jualan

Spec 2.4: pemeriksa otomatis menolak mesin jualan bila daftar bahan latihnya memuat satu saja bahan bukan
`BOLEH-PRODUK`. Tanda bahan menurun ke mesinnya: mesin yang dilatih dengan bahan `RISET-SAJA` ikut bertanda
`RISET-SAJA` (akibat K15).

Tiap mesin terlatih punya manifes JSON berbentuk:

```json
{ "nama": "pembaca-huruf-uji-1", "tujuan": "belajar", "bahan": ["video-riset-youtube"] }
```

`tujuan` adalah `jualan` atau `belajar`. `bahan` memuat **semua** yang ikut membentuk mesin itu: dataset, video,
huruf, dan bobot awal.

**Files:**
- Create: `tools/periksa-jualan.mjs`
- Test: `tools/uji/periksa-jualan.test.mjs`

- [ ] **Step 1: Tulis uji yang gagal**

Buat `tools/uji/periksa-jualan.test.mjs`:

```js
// Uji tools/periksa-jualan.mjs (spec bagian 2.4, K15): mesin jualan tidak boleh memuat bahan bukan BOLEH-PRODUK, dan
// tanda bahan menurun ke mesinnya.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'periksa-jualan.mjs');
const bahanKe = (id, vonis) => ({
  id, jenis: 'dataset', nama: id, sumber: 'https://contoh.test/' + id, lisensi: 'contoh',
  bukti_lisensi: 'https://contoh.test/lisensi', vonis, dicatat: '2026-10-13',
});
const DAFTAR = { bahan: [bahanKe('bersih-a', 'BOLEH-PRODUK'), bahanKe('bersih-b', 'BOLEH-PRODUK'), bahanKe('riset-a', 'RISET-SAJA'), bahanKe('samar-a', 'BELUM-JELAS')] };

function tulis(nama, isi) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-jualan-')), nama);
  fs.writeFileSync(berkas, JSON.stringify(isi));
  return berkas;
}

function periksa(mesin, daftar = DAFTAR) {
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', mesin), tulis('bahan.json', daftar)], { encoding: 'utf8' });
  return { kode: r.status, keluar: r.stdout + r.stderr };
}

test('mesin jualan dari bahan bersih semua diterima dan bertanda BOLEH-PRODUK', () => {
  const r = periksa({ nama: 'm1', tujuan: 'jualan', bahan: ['bersih-a', 'bersih-b'] });

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /tanda mesin = BOLEH-PRODUK/);
});

test('mesin jualan yang memuat satu bahan RISET-SAJA ditolak (kode 1) dan bahannya disebut', () => {
  const r = periksa({ nama: 'm2', tujuan: 'jualan', bahan: ['bersih-a', 'riset-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bahan "riset-a" bervonis RISET-SAJA/);
});

test('mesin jualan yang memuat bahan BELUM-JELAS ditolak: yang belum jelas tidak dianggap boleh', () => {
  const r = periksa({ nama: 'm3', tujuan: 'jualan', bahan: ['samar-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bahan "samar-a" bervonis BELUM-JELAS/);
});

test('bahan yang tak tercatat ditolak, untuk mesin jualan maupun mesin belajar', () => {
  for (const tujuan of ['jualan', 'belajar']) {
    const r = periksa({ nama: 'm4', tujuan, bahan: ['entah-dari-mana'] });

    assert.equal(r.kode, 1, `${tujuan}: ${r.keluar}`);
    assert.match(r.keluar, /bahan "entah-dari-mana" tidak tercatat/);
  }
});

test('mesin tanpa daftar bahan ditolak: asal-usul kosong tidak bisa dinilai', () => {
  const r = periksa({ nama: 'm5', tujuan: 'jualan', bahan: [] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /daftar "bahan" kosong/);
});

test('mesin belajar boleh memuat bahan RISET-SAJA, dan tandanya menurun menjadi RISET-SAJA', () => {
  const r = periksa({ nama: 'm6', tujuan: 'belajar', bahan: ['bersih-a', 'riset-a'] });

  assert.equal(r.kode, 0, r.keluar);
  assert.match(r.keluar, /tanda mesin = RISET-SAJA/);
});

test('tujuan di luar daftar ditolak', () => {
  const r = periksa({ nama: 'm7', tujuan: 'produksi', bahan: ['bersih-a'] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /tujuan "produksi" tak dikenal/);
});

test('daftar bahan yang cacat membuat semua mesin ditolak', () => {
  const r = periksa({ nama: 'm8', tujuan: 'jualan', bahan: ['bersih-a'] }, { bahan: [{ ...bahanKe('bersih-a', 'BOLEH-PRODUK'), bukti_lisensi: '' }] });

  assert.equal(r.kode, 1, r.keluar);
  assert.match(r.keluar, /bukti_lisensi/);
});

test('tanpa argumen: ditolak dengan petunjuk pakai (kode 2)', () => {
  const r = spawnSync('node', [SKRIP], { encoding: 'utf8' });

  assert.equal(r.status, 2, r.stdout + r.stderr);
});

test('rantai: tanpa berkas bahan, yang dibaca adalah daftar bahan repo ini, dan video riset K17 ditolak untuk jualan', () => {
  // Uji ini menelusuri jalannya: manifes mesin -> data-asal/bahan.json sungguhan -> keputusan. Bila pemeriksa tidak
  // benar-benar membaca daftar repo, bahan "video-riset-youtube" akan terbaca "tidak tercatat", bukan "RISET-SAJA".
  const r = spawnSync('node', [SKRIP, tulis('mesin.json', { nama: 'm9', tujuan: 'jualan', bahan: ['video-riset-youtube'] })], { encoding: 'utf8' });

  assert.equal(r.status, 1, r.stdout + r.stderr);
  assert.match(r.stdout + r.stderr, /bahan "video-riset-youtube" bervonis RISET-SAJA/);
});
```

- [ ] **Step 2: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `EXIT=1`. Sepuluh uji di `periksa-jualan.test.mjs` gagal dengan
`Cannot find module ... tools\periksa-jualan.mjs`. 46 uji lama tetap lulus.

- [ ] **Step 3: Tulis `tools/periksa-jualan.mjs`**

```js
#!/usr/bin/env node
// Pemeriksa tanda mesin (spec bagian 2.4, K15).
// - Mesin JUALAN hanya boleh memuat bahan bervonis BOLEH-PRODUK. Satu saja bahan lain => exit 1.
// - Mesin BELAJAR boleh memuat bahan apa pun yang TERCATAT; tandanya menurun: ada satu bahan bukan BOLEH-PRODUK =>
//   mesin itu RISET-SAJA dan angkanya tidak boleh dilaporkan sebagai angka produk.
// - Bahan yang tak tercatat di daftar bahan selalu ditolak: asal yang tak diketahui tidak bisa dinilai.
//
// Manifes mesin: { "nama": "...", "tujuan": "jualan" | "belajar", "bahan": ["id-bahan", ...] }
// "bahan" memuat SEMUA yang ikut membentuk mesin: dataset, video, huruf, dan bobot awal.
//
// Pakai:  node tools/periksa-jualan.mjs <manifes-mesin.json> [berkas-bahan]
import fs from 'node:fs';
import { muatBahan, BERKAS_BAHAN } from './bahan.mjs';

const TUJUAN = ['jualan', 'belajar'];
const [berkasMesin, berkasBahan = BERKAS_BAHAN] = process.argv.slice(2);
if (!berkasMesin) {
  console.error('Pakai: node tools/periksa-jualan.mjs <manifes-mesin.json> [berkas-bahan]');
  process.exit(2);
}

const { bahan, galat } = muatBahan(berkasBahan);
const tolak = [...galat];
let mesin = {};
try {
  mesin = JSON.parse(fs.readFileSync(berkasMesin, 'utf8'));
} catch (e) {
  tolak.push(`${berkasMesin}: tak terbaca (${e.message})`);
}

if (!TUJUAN.includes(mesin.tujuan)) tolak.push(`tujuan "${mesin.tujuan}" tak dikenal (pilihan: ${TUJUAN.join(', ')})`);
const dipakai = Array.isArray(mesin.bahan) ? mesin.bahan : [];
if (dipakai.length === 0) tolak.push('daftar "bahan" kosong: mesin tanpa asal-usul bahan tidak bisa dinilai');

const perId = new Map(bahan.map((b) => [b.id, b]));
let tanda = 'BOLEH-PRODUK';
for (const id of dipakai) {
  const b = perId.get(id);
  if (!b) {
    tolak.push(`bahan "${id}" tidak tercatat di daftar bahan`);
    continue;
  }
  if (b.vonis !== 'BOLEH-PRODUK') {
    tanda = 'RISET-SAJA';
    if (mesin.tujuan === 'jualan') tolak.push(`bahan "${id}" bervonis ${b.vonis}: tidak boleh ada di mesin jualan`);
  }
}

if (tolak.length) {
  for (const t of tolak) console.error(`DITOLAK ${t}`);
  console.error(`mesin "${mesin.nama ?? '?'}" ditolak (${tolak.length} alasan).`);
  process.exit(1);
}
console.log(`mesin "${mesin.nama}" (${mesin.tujuan}): tanda mesin = ${tanda}`);
```

- [ ] **Step 4: Jalankan uji untuk memastikan lulus**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ fail 0`, `EXIT=0`. Jumlah uji naik dari 46 menjadi 56.

- [ ] **Step 5: Commit**

```bash
git add tools/periksa-jualan.mjs tools/uji/periksa-jualan.test.mjs
git commit -q -F - <<'EOF'
Pemeriksa mesin jualan

Spec 2.4 memisahkan mesin belajar dari mesin jualan. Pemeriksa ini yang
menegakkannya: mesin jualan ditolak bila memuat satu saja bahan bukan
BOLEH-PRODUK, dan tanda RISET-SAJA menurun dari bahan ke mesinnya.

Bahan yang tak tercatat selalu ditolak, juga untuk mesin belajar, karena
asal yang tak diketahui tidak bisa dinilai kelak.

Satu uji menelusuri rantainya ke daftar bahan repo yang sungguhan, supaya
pemeriksa yang tidak benar-benar membaca daftar itu tidak lolos hijau.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 5: Pintu lab tanpa jaringan

Spec 8.6 dan U8: repo pihak ketiga dijalankan pertama kali di ruang uji tanpa jaringan. Pintunya disalin dari
vision-seed (K14) lalu disesuaikan: mode `-Kamera`, mode `-Jaringan`, dan gudang aset dibuang karena belum dibutuhkan
Fase 0A; image lab dijaga lewat ID-nya di `tools/vendor.lock.json` (sama dengan `tools/ambil-video.ps1`).

Nama kunci bengkel **sengaja sama** dengan milik vision-seed (`Global\vision-seed-bengkel`): kedua proyek memakai satu
kartu grafis, jadi job lab keduanya harus saling menunggu.

**Files:**
- Create: `tools/lab.ps1`
- Test: `tools/uji/lab.test.mjs`

- [ ] **Step 1: Salin pintu aslinya apa adanya**

Run: `cp "D:/Projects/super-team-v1/vision-seed/tools/lab.ps1" tools/lab.ps1 && git -C "D:/Projects/super-team-v1/vision-seed" log --oneline -1`
Expected: berkas `tools/lab.ps1` ada; commit vision-seed yang tercetak adalah `3591530`. Bila commit-nya lain, catat
commit yang tercetak dan pakai itu di kalimat "Asal" pada Step 4.

- [ ] **Step 2: Tulis uji yang gagal**

Buat `tools/uji/lab.test.mjs`:

```js
// Uji pintu lab tools/lab.ps1. Yang dikunci di sini adalah JANJI bengkel di sisi host: tanpa jaringan, repo read-only,
// image persis yang tercatat, dan "kunci bengkel" (satu job lab pada satu waktu, bersama vision-seed).
//
// Asal: disusun dari vision-seed @3591530 (tools/uji/lab.test.mjs) pada 2026-10-13 (K14). Yang diubah di sini: uji
// mode -Kamera, -Jaringan, dan gudang aset diganti penolakan; uji kunci image diganti penjagaan lewat ID image.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const LAB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'lab.ps1');
const NAMA_KUNCI = 'Global\\vision-seed-bengkel';

function lab(args, env = {}) {
  const r = spawnSync('powershell', ['-NoProfile', '-File', LAB, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
    timeout: 60_000,
  });
  return { kode: r.status, keluar: r.stdout, galat: r.stderr };
}

function argumenDocker(args, env) {
  const r = lab(['-Kering', ...args], env);
  assert.equal(r.kode, 0, `lab.ps1 -Kering gagal: ${r.galat}${r.keluar}`);
  return JSON.parse(r.keluar);
}

const pasangan = (a, kunci) => a.flatMap((x, i) => (x === kunci ? [a[i + 1]] : []));

function dockerTiruan() {
  // Pengganti docker: menjawab `image inspect` dengan ID dari TIRUAN_ID; pada `run` keluar dengan kode TIRUAN_KODE.
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-docker-')), 'docker-tiruan.ps1');
  fs.writeFileSync(berkas, [
    "if ($args[0] -eq 'image') { Write-Output $env:TIRUAN_ID; exit 0 }",
    'exit [int]$env:TIRUAN_KODE',
  ].join('\r\n'));
  return berkas;
}

function kunciSementara(imageLab) {
  const berkas = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-kunci-')), 'vendor.lock.json');
  const kunci = { repo: [] };
  if (imageLab) kunci.image_lab = imageLab;
  fs.writeFileSync(berkas, JSON.stringify(kunci));
  return berkas;
}

test('mode biasa: tanpa jaringan, GPU, repo read-only, hanya data/keluaran yang bisa ditulis', () => {
  const a = argumenDocker(['python', '-V']);

  assert.deepEqual(pasangan(a, '--network'), ['none']);
  assert.ok(a.includes('--gpus') && a.includes('--read-only') && a.includes('no-new-privileges'));
  assert.deepEqual(pasangan(a, '--cap-drop'), ['ALL']);
  const pasang = pasangan(a, '--mount');
  assert.equal(pasang.length, 2, pasang.join(' | '));
  assert.match(pasang[0], /target=\/kerja,readonly$/);
  assert.match(pasang[1], /data\\keluaran,target=\/kerja\/data\/keluaran$/);
  assert.deepEqual(a.slice(-2), ['python', '-V']);
});

for (const mode of ['-Kamera', '-Jaringan']) {
  test(`mode ${mode} tidak ada di repo ini: ditolak (kode 2), lab hanya berjalan tanpa jaringan`, () => {
    const r = lab(['-Kering', mode, 'python', '-V']);

    assert.equal(r.kode, 2, r.keluar + r.galat);
    assert.match(r.keluar, /DITOLAK/);
  });
}

test('tanpa perintah: ditolak dengan petunjuk pakai (kode 2)', () => {
  assert.equal(lab(['-Kering']).kode, 2);
});

test('kunci bengkel sama dengan vision-seed: bila job lab lain memegang kunci, menunggu lalu menyerah dengan kode 3', async () => {
  const pemegang = spawn('powershell', ['-NoProfile', '-Command',
    `$m = New-Object System.Threading.Mutex($false, '${NAMA_KUNCI}'); [void]$m.WaitOne(); 'SIAP'; Start-Sleep -Seconds 30`]);
  try {
    await new Promise((selesai, gagal) => {
      pemegang.stdout.on('data', (d) => String(d).includes('SIAP') && selesai());
      pemegang.on('exit', () => gagal(new Error('pemegang kunci keluar sebelum SIAP')));
    });

    const r = lab(['-Kering', 'python', '-V'], { VS_KUNCI_TUNGGU_DTK: '2' });

    assert.equal(r.kode, 3, `harus kode 3 (bengkel dipakai), dapat ${r.kode}: ${r.keluar}${r.galat}`);
    assert.match(r.keluar + r.galat, /bengkel sedang dipakai/);
  } finally {
    pemegang.kill(); // satu proses powershell tanpa anak: aman dihentikan, mutex otomatis lepas
  }
});

test('kunci bengkel lepas: tanpa pemegang lain, lab.ps1 langsung jalan', () => {
  const r = lab(['-Kering', 'python', '-V'], { VS_KUNCI_TUNGGU_DTK: '2' });

  assert.equal(r.kode, 0, r.galat);
});

test('image lab yang ID-nya bukan yang tercatat di kunci tidak dijalankan (kode 6)', () => {
  const r = lab(['python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:lain' }),
    TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 6, r.keluar + r.galat);
  assert.match(r.keluar, /IMAGE TAK SESUAI KUNCI/);
});

test('kunci tanpa catatan image lab ditolak (kode 6): gagal tertutup', () => {
  const r = lab(['python', '-V'], {
    VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara(), TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: '0', VS_KUNCI_TUNGGU_DTK: '5',
  });

  assert.equal(r.kode, 6, r.keluar + r.galat);
});

for (const kode of ['0', '4']) {
  test(`image sesuai kunci: perintah dijalankan dan kode keluarnya (${kode}) diteruskan apa adanya`, () => {
    const r = lab(['python', '-V'], {
      VS_DOCKER: dockerTiruan(), VS_KUNCI_VENDOR: kunciSementara({ nama: 'vision-seed-lab:v1', id: 'sha256:tiruan' }),
      TIRUAN_ID: 'sha256:tiruan', TIRUAN_KODE: kode, VS_KUNCI_TUNGGU_DTK: '5',
    });

    assert.equal(r.kode, Number(kode), r.keluar + r.galat);
  });
}
```

- [ ] **Step 3: Jalankan uji untuk memastikan gagal**

Run: `npm test; echo "EXIT=$?"`
Expected: `EXIT=1`, dengan **6 uji gagal** di `lab.test.mjs`: dua uji mode (`-Kamera` masih diterima dengan kode 0;
`-Jaringan` menolak tanpa kata `DITOLAK`) dan empat uji image (pintu salinan mencari `_kunci-image.ps1` yang tidak
ada di repo ini, kode 1). Empat uji lain di berkas itu sudah lulus karena perilakunya diwarisi dari salinan.

Bila ada uji yang gagal dengan kode 3, bengkel sedang dipakai job lab lain (vision-seed); itu bukan uji merah. Tunggu
job itu selesai lalu ulangi.

- [ ] **Step 4: Ganti isi `tools/lab.ps1` dengan versi repo ini**

Tulis ulang seluruh berkas menjadi:

```powershell
<#
.SYNOPSIS
  Satu-satunya pintu menjalankan lab CCTV Gerbang: container lab, GPU, TANPA jaringan.

.DESCRIPTION
  Asal: disalin dari vision-seed @3591530 (tools\lab.ps1) pada 2026-10-13 (K14). Yang diubah di sini: mode -Kamera,
  mode -Jaringan, dan gudang aset dibuang (belum dibutuhkan Fase 0A), dan image lab dijaga lewat ID-nya di kunci vendor
  karena repo ini tidak membangun image sendiri.

  Janji pintu ini:
  - Container jalan dengan --network none. Kode pihak ketiga tak bisa "menelepon pulang".
  - Repo di-mount READ-ONLY ke /kerja. Hanya data\keluaran\ yang bisa ditulis.
  - Tak ada berkas host lain (~/.ssh, kredensial proyek lain) yang terlihat dari dalam container.
  - Root filesystem container read-only, semua capability dicabut, tanpa naik hak akses.
  - Image lab yang ID-nya bukan yang tercatat di tools\vendor.lock.json TIDAK dijalankan (kode 6).

  KUNCI BENGKEL (PRINSIP #3, satu job lab pada satu waktu): named mutex Windows yang SENGAJA sama dengan milik
  vision-seed, karena kedua proyek memakai satu kartu grafis. Job lab keduanya saling menunggu, tak pernah jalan
  bersamaan. Mutex otomatis lepas bila prosesnya mati, jadi tak ada kunci basi. Bila menunggu lebih dari
  VS_KUNCI_TUNGGU_DTK (bawaan 1800), keluar dengan kode 3 = bengkel sibuk, BUKAN uji merah.

  Bendera di depan perintah:
    -Kering    cetak argumen docker sebagai JSON tanpa menjalankannya (dipakai tools\uji\lab.test.mjs)

  Catatan: skrip ini sengaja tanpa blok param(). Dengan `powershell -File`, argumen seperti `-m` milik pytest akan
  dianggap parameter PowerShell bila ada blok param().

.EXAMPLE
  powershell -NoProfile -File tools\lab.ps1 python -V
#>
$ErrorActionPreference = 'Stop'
$image = 'vision-seed-lab:v1'
$akar = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
# Untuk uji rantai (tools\uji\lab.test.mjs): program docker bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$sisa = @($args)
$kering = $false
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Kering') { $kering = $true; $sisa = @($sisa | Select-Object -Skip 1) }
if ($sisa.Count -eq 0) { Write-Host 'Pakai: tools\lab.ps1 [-Kering] <perintah...>'; exit 2 }
if ($sisa[0] -in @('-Kamera', '-Jaringan')) {
    Write-Host "DITOLAK: mode $($sisa[0]) tidak ada di repo ini. Lab hanya berjalan tanpa jaringan."
    exit 2
}

$keluaran = Join-Path $akar 'data\keluaran'
New-Item -ItemType Directory -Force $keluaran | Out-Null
$argumen = @('run', '--rm', '--read-only', '--tmpfs', '/tmp:rw,exec,size=4g', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--env', 'MPLCONFIGDIR=/tmp/mpl', '--env', 'HOME=/tmp',
    '--network', 'none', '--gpus', 'all',
    '--mount', "type=bind,source=$akar,target=/kerja,readonly",
    '--mount', "type=bind,source=$keluaran,target=/kerja/data/keluaran",
    $image) + $sisa

if (-not $kering) {
    # Gagal tertutup: yang dijalankan harus image yang persis tercatat. Tak tercatat, tak ada di mesin, atau berbeda =
    # tidak dijalankan.
    $idKunci = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).image_lab.id
    $ErrorActionPreference = 'Continue'
    $idImage = & $docker image inspect $image --format '{{.Id}}' 2>$null
    $ErrorActionPreference = 'Stop'
    if (-not $idKunci -or "$idImage".Trim() -ne $idKunci) {
        Write-Host "IMAGE TAK SESUAI KUNCI: '$image' ber-ID '$idImage', yang tercatat '$idKunci' (tools\vendor.lock.json, image_lab)."
        exit 6
    }
}

$tunggu = if ($env:VS_KUNCI_TUNGGU_DTK) { [int]$env:VS_KUNCI_TUNGGU_DTK } else { 1800 }
$kunci = New-Object System.Threading.Mutex($false, 'Global\vision-seed-bengkel')
try {
    try {
        $dapat = $kunci.WaitOne(0)
        if (-not $dapat) {
            Write-Host "Menunggu job lab lain selesai (maks $tunggu dtk)..."
            $dapat = $kunci.WaitOne([TimeSpan]::FromSeconds($tunggu))
        }
    } catch [System.Threading.AbandonedMutexException] {
        $dapat = $true  # pemegang lama mati tanpa melepas; kunci kini sah milik proses ini
    }
    if (-not $dapat) {
        Write-Host "bengkel sedang dipakai job lab lain selama >$tunggu dtk. Ini BUKAN uji merah; ulangi nanti."
        exit 3
    }
    try {
        if ($kering) {
            ConvertTo-Json -InputObject $argumen -Compress
            $kode = 0
        } else {
            & $docker @argumen
            $kode = $LASTEXITCODE
        }
    } finally {
        $kunci.ReleaseMutex()
    }
} finally {
    $kunci.Dispose()
}
exit $kode
```

- [ ] **Step 5: Jalankan uji untuk memastikan lulus**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ fail 0`, `EXIT=0`. Jumlah uji naik dari 56 menjadi 66 (10 uji di `lab.test.mjs`: 1 + 2 + 1 + 1 + 1 + 1 +
1 + 2).

- [ ] **Step 6: Bukti sungguhan: lab benar-benar jalan dan benar-benar tanpa jaringan**

Run (PowerShell): `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
Expected: satu baris pemakaian memori. Bila sebuah job sedang memakai kartu grafis, tunggu sampai selesai (satu job
GPU pada satu waktu).

Run (PowerShell): `powershell -NoProfile -File tools\lab.ps1 python -V; "EXIT=$LASTEXITCODE"`
Expected: satu baris `Python 3.x.y` dan `EXIT=0`.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python -c "import urllib.request as u; u.urlopen('https://example.com', timeout=5)"; "EXIT=$LASTEXITCODE"`
Expected: galat jaringan dari Python (`URLError`) dan `EXIT=1`. Kode 1 di sini adalah **bukti yang diharapkan**:
container tidak bisa keluar ke internet. Bila perintah ini keluar 0, pintunya bocor: berhenti dan laporkan.

Run (PowerShell):
`powershell -NoProfile -File tools\lab.ps1 python -c "open('/kerja/ROADMAP.md','a').write('x')"; "EXIT=$LASTEXITCODE"`
Expected: galat `Read-only file system` dan `EXIT=1`. Lalu `git status --short` harus kosong: repo tidak berubah.

- [ ] **Step 7: Commit**

```bash
git add tools/lab.ps1 tools/uji/lab.test.mjs
git commit -q -F - <<'EOF'
Pintu lab tanpa jaringan

Spec 8.6 mewajibkan repo pihak ketiga dijalankan pertama kali di ruang uji
tanpa jaringan. Pintunya disalin dari vision-seed @3591530 (K14), lalu
mode berjaringan dan gudang aset dibuang karena belum dibutuhkan Fase 0A:
pintu yang lebih sempit lebih mudah dijaga.

Image lab dijaga lewat ID-nya, sama dengan pintu pengunduh, karena repo
ini tidak membangun image sendiri. Nama kunci bengkel sengaja sama dengan
vision-seed: satu kartu grafis, jadi job lab kedua proyek saling menunggu.

Bukti sungguhan dijalankan: lab hidup, tidak bisa membuka koneksi keluar,
dan tidak bisa menulis ke repo.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 6: Mencatat hasil

**Files:**
- Modify: `CLAUDE.md`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Jalankan gerbang penuh sekali lagi dan catat angkanya**

Run: `npm test; echo "EXIT=$?"`
Expected: `ℹ tests 66`, `ℹ pass 66`, `ℹ fail 0`, `EXIT=0`. Bila angkanya berbeda dari 66, pakai angka yang
tercetak di semua catatan pada langkah berikut dan cari tahu sebabnya sebelum melanjutkan.

- [ ] **Step 2: Catat gerbang uji di `CLAUDE.md`**

Di bagian `## 7. ⚙️ Mesin (Prinsip #3)`, tepat sesudah baris
`- Jangan \`| tail\` / \`| head\` pada perintah gerbang uji (status pipa menyembunyikan exit code).`, tambahkan:

```markdown
- Gerbang uji repo ini: `npm test`. Satu suite pada satu waktu. Kode 3 dari `tools\lab.ps1` berarti bengkel sedang
  dipakai job lab lain (kuncinya dipakai bersama vision-seed); itu bukan uji merah.
- Yang dijalankan lewat Docker hanya lewat pintunya: `tools\ambil-video.ps1` (pengunduh video, berjaringan, hanya
  melihat folder video) dan `tools\lab.ps1` (lab, tanpa jaringan, repo read-only).
```

- [ ] **Step 3: Perbarui `ROADMAP.md`**

(a) Di tabel "Temuan di luar lingkup", pada baris temuan alat unduh (yang berawal
`| 2026-10-13 | \`tools/ambil-video.ps1\` mengembalikan kode 0 ketika unduhan terpotong`), ganti isi kolom Status dari

```
Di vision-seed: **dicatat di sini saja, tidak diperbaiki dari workspace ini**. Di repo ini: **belum diperbaiki**; untuk sementara tiap unduhan diperiksa dari berkasnya. Masuk rencana Fase 0
```

menjadi

```
Di vision-seed: **dicatat di sini saja, tidak diperbaiki dari workspace ini**. Di repo ini: **diperbaiki** (kode 8 bila ada berkas `.part`), dengan uji rantai. Sisa yang belum tertangani: pengunduh yang menolak sebelum mulai mengunduh tetap keluar 0
```

(b) Di daftar "Status", ganti baris

```
- [ ] Rencana 1 Fase 0A dijalankan ← di sini sekarang (menunggu lampu hijau owner)
```

menjadi

```
- [x] Rencana 1 Fase 0A (bengkel) dijalankan. Gerbang uji `npm test`: 29 → 66 uji, semuanya hijau; tiap uji baru pernah merah. Lab dijalankan sungguhan: hidup, tidak bisa keluar ke internet, tidak bisa menulis ke repo
- [ ] Rencana 2 Fase 0A ditulis (vonis izin komponen, peraturan plat, unduhan dataset berizin) ← di sini sekarang
```

(c) Di akhir tabel "Changelog", tambahkan baris:

```
| 2026-10-13 | Rencana 1 Fase 0A (bengkel) dijalankan. Butir rencana dipecah: Rencana 1 dicentang, Rencana 2 menjadi butir berikutnya. Temuan alat unduh diberi status "diperbaiki di repo ini" | Fase 0A dipecah menjadi empat rencana karena isi rencana berikutnya bergantung pada temuan sebelumnya (komponen mana yang lolos vonis izin, isi 45 video, peraturan plat); menulisnya sekaligus berarti mengarang. Rencana 1 menyiapkan yang dibutuhkan semua langkah sesudahnya: gerbang uji satu perintah, alat unduh yang kode keluarnya jujur, daftar bahan dan pemeriksa mesin jualan (spec 2.4), dan pintu lab tanpa jaringan (spec 8.6). Bukti: gerbang 29 → 66 uji hijau, tiap uji baru pernah merah; lab dijalankan sungguhan dan terbukti tidak bisa keluar ke internet maupun menulis ke repo. Batas: belum ada satu pun bahan yang dilatih atau diukur; repo ini tidak punya CI, jadi yang diperiksa hanya gerbang lokal |
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md ROADMAP.md
git commit -q -F - <<'EOF'
Catat hasil Rencana 1 Fase 0A (bengkel)

Gerbang uji dan dua pintu Docker dicatat di aturan proyek supaya sesi
berikutnya tidak mengulang kesalahan alat ukur (node --test pada folder)
dan tidak menjalankan Docker di luar pintunya.

ROADMAP: Rencana 1 dicentang dengan angkanya, Rencana 2 menjadi butir
berikutnya, dan temuan alat unduh diberi status diperbaiki beserta sisa
yang belum tertangani.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
git status --short
```

Expected: `git status --short` tidak mencetak apa pun.

---

## Selesai bila

- [ ] `npm test` mencetak `ℹ fail 0` dengan `EXIT=0`, dan jumlah ujinya disebut di `ROADMAP.md`.
- [ ] Tiap uji baru pernah dilihat merah sebelum hijau (Step "pastikan gagal" di Task 2, 3, 4, 5).
- [ ] `tools\lab.ps1` dijalankan sungguhan: hidup, tidak bisa keluar ke internet, tidak bisa menulis ke repo.
- [ ] `tools\ambil-video.ps1 periksa` dan `cari` masih bekerja dengan docker sungguhan.
- [ ] `git -C "D:/Projects/super-team-v1/vision-seed" status --short` kosong: vision-seed tidak tersentuh.
- [ ] `ROADMAP.md` memuat bukti, batas, dan alasan; temuan alat unduh berstatus diperbaiki.

## Yang sengaja tidak dikerjakan di rencana ini

- Vonis izin komponen, peraturan plat, unduhan dataset: Rencana 2.
- Pemilahan video, pembuat plat buatan komputer, set uji: Rencana 3.
- Pembanding, pelatihan, taksiran kecepatan, laporan: Rencana 4.
- Membangun image lab sendiri. Image `vision-seed-lab:v1` dipakai apa adanya. Bila Rencana 2 menemukan komponen yang
  butuh paket di luar image itu, keputusan membangun image sendiri diambil di sana, karena itu berarti memasang paket.
