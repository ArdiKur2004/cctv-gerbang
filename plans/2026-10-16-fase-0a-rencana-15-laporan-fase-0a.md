# Fase 0A, Rencana 15: Laporan Fase 0A dan keputusan owner (K33) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`.

**Goal:** Fase 0A ditutup sesuai spec 8.1 langkah 9 dan 8.7.
- **Laporan tertulis di `bukti/`**, berisi:
  - angka per kelompok;
  - status kesembilan langkah;
  - yang belum terjawab;
  - risiko;
  - saran agen.
- **Owner mengambil dua keputusan**, satu per satu, yang lalu dicatat di `ROADMAP.md`:
  - lanjut, tunggu lokasi, atau ubah arah;
  - plat buatan komputer.

**Architecture:**
- **`tools/laporan-0a.mjs`**: tabel angka laporan dibaca langsung dari JSON di `bukti/` dan ditulis di antara dua penanda di
  laporan. Tidak ada angka tabel yang diketik tangan.
  - Kunci yang tidak ada membuat alat gagal (gagal tertutup).
  - Perintah `periksa` menangkap laporan yang menyimpang dari sumbernya.
- **Laporan** (`bukti/2026-10-16-laporan-fase-0a.md`): teks untuk owner dalam bahasa sederhana, dengan tabel dari alat itu.
  Angka di luar tabel hanya angka yang sudah ada di laporan rencana sebelumnya, dengan tautan ke laporannya.

**Tech Stack:** Node (gerbang `npm test`), Markdown.

**Dasar:** K5, K6, K9, K15, K21, K25–K33 (`SEED.md` §3); spec 2.4, 2.5, 8.1, 8.3, 8.4, 8.7; laporan Rencana 5–14 di `bukti/`;
`OPEN-QUESTIONS.md` bagian B; `CLAUDE.md` §4, §5.

---

## Yang diukur sebelum rencana ini ditulis (16 Okt 2026)

| Hal | Yang terbaca | Dari mana |
|---|---|---|
| Langkah spec 8.1 | 1 bengkel (Rencana 1); 2 vonis izin (Rencana 2, `docs/VONIS-LISENSI.md`); 3 peraturan plat (`docs/peraturan-plat.md`); 4 bahan: 100 video dipilah, INDO-ALPR dan plat-lighting tersimpan, **pembuat plat buatan komputer belum dibangun**; 5 set uji: 937 plat baca huruf (dikelompokkan **terang/gelap** dari potongan, bukan siang/malam dari video) dan 84 foto cari plat; 6 pembanding: Qwen3-VL, fast-plate-ocr, YOLOv9-t; 7 mesin belajar: dua pembaca (mesin-baca-1, fpo-indo-1), empat pencari (YOLOX), rantai utuh; 8 kecepatan: laptop dan Mini PC | `ROADMAP.md` bagian Status |
| Bukti berangka | 45 berkas JSON di `bukti/`, isinya hitungan saja | `bukti/*.json` |
| Angka baca huruf per kelompok | `2026-10-15-banding-pembaca-10.json`, bagian `tanpa-label-pilihan-pembaca` (set uji adil); model `fpo-indo-1`, `fast-plate-ocr`, `qwen3-vl`, `mesin-baca-1`; kunci `kedatangan_benar`, `kedatangan`, `rentang_95_kedatangan` | dibaca dengan Node |
| Angka cari plat | `2026-10-16-pencari-yolox-*-nilai.json` dan `2026-10-16-pencari-oim.json`: `uji.semua` dan `uji.kecil` dengan `plat_ditemukan`, `plat`, `kotak_palsu`, `rentang_95_ditemukan` | sama |
| Angka rantai utuh | `2026-10-16-rantai-video-ulang-ringkasan.json` (`video`, `gambar_sampel`, `kedatangan`, `yakin`, `ragu`, `waktu_ms`, `aturan`) dan `2026-10-16-rantai-video-nilai.json` (`baris`, `bukan_plat`, `tak_terbaca`, `kelompok.semua`) | sama |
| Angka kecepatan | Laptop: `2026-10-16-pencari-yolox-nano-640-cepat.json` (`per_utas.2.median_ms`), `2026-10-15-cepat-fpo-indo-1.json` (`per_utas.2.utuh_ms.median`). Mini PC: daftar `model` di `2026-10-16-cepat-yolox-640-minipc.json` (`acak-yolox-nano-640.onnx`) dan `2026-10-16-cepat-calon-minipc.json` (`cct_s_v2_global.onnx`, ONNX terbitan bersusunan sama dengan fpo-indo-1), `per_utas.2.median_ms` | sama |
| Kode rencana ini | Keempat uji Task 1 lulus pada salinan sementara (dengan salinan JSON `bukti/`), dan keempat tabel terbaca utuh dari bukti sungguhan, misalnya fpo-indo-1 496 dari 625 (79,4%) dan YOLOX-Nano-640 96 dari 102. Saat dijalankan, uji tetap harus terlihat merah dulu di repo | `data/alat-sementara/cek-r15/` (dihapus sesudahnya) |
| Yang masih terbuka | P14 (arti larangan untuk label non-komersial); izin fast-plate-ocr (K27, owner mengirimnya sendiri); bobot awal YOLOX dan fast-plate-ocr `BELUM-JELAS`, jadi semua mesin hasil latih `RISET-SAJA`; B2, B3, B5 dari posisi gerbang (spec 8.4) | `OPEN-QUESTIONS.md`, `data-asal/bahan.json` |

Akibatnya bagi rencana ini:

1. **Angka tabel dibaca alat dari JSON bukti** (honest-slice aturan 6). `periksa` dijalankan di gerbang akhir, jadi laporan yang
   menyimpang dari sumbernya tertangkap.
2. **Laporan menulis jujur yang berbeda dari spec:**
   - kelompok baca huruf terang/gelap, bukan siang/malam;
   - plat buatan komputer belum dibangun;
   - pencari plat menemukan banyak benda bukan plat di video riset;
   - semua mesin `RISET-SAJA`, jadi belum ada yang boleh dijual.
3. **Dua keputusan owner ditanyakan satu per satu** (`CLAUDE.md` §1), masing-masing dengan saran di depan dan cara membaliknya.

## Penyesuaian pembagian rencana

| Rencana | Isi | Status |
|---|---|---|
| 1–14 | Bengkel sampai rantai utuh di video riset | Selesai 13–16 Okt |
| **15 (dokumen ini)** | Laporan Fase 0A dan keputusan owner | Ditulis |
| Berikutnya | Menurut keputusan owner: Fase 1, Fase 0B, atau arah baru | Sesudahnya |

## Peta berkas

| Berkas | Tugasnya | Task |
|---|---|---|
| `tools/laporan-0a.mjs` (baru) | Tabel angka dari `bukti/*.json`; CLI `tulis` dan `periksa` | 1 |
| `tools/uji/laporan-0a.test.mjs` (baru) | Uji gerbang Node | 1 |
| `bukti/2026-10-16-laporan-fase-0a.md` (baru) | Laporan Fase 0A | 2 |
| `ROADMAP.md`, `OPEN-QUESTIONS.md`, `CLAUDE.md`, `SEED.md` (ubah) | Catatan dan keputusan owner | 3, 4 |

---

### Task 1: Tabel angka dibaca dari bukti

**Files:** Create `tools/laporan-0a.mjs`, `tools/uji/laporan-0a.test.mjs`

- [x] **Step 1: Tulis ujinya**

```js
// Uji tools/laporan-0a.mjs (Rencana 15): angka laporan dibaca dari JSON bukti, gagal tertutup bila kuncinya tidak ada, dan
// laporan yang menyimpang dari sumbernya tertangkap.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { AKHIR, BUKTI, MULAI, TABEL, baca, isi, sel } from '../laporan-0a.mjs';

const SKRIP = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'laporan-0a.mjs');
const CONTOH = {
  'a.json': {
    uji: { semua: { benar: 496, jumlah: 625, rentang: [0.76, 0.823] } }, besar: 33906, waktu: 17.73,
    model: [{ berkas: 'x.onnx', ms: 149.9 }, { berkas: 'y.onnx', ms: 544 }],
  },
};

function folder(isiBerkas) {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'vs-laporan-'));
  for (const [nama, x] of Object.entries(isiBerkas)) fs.writeFileSync(path.join(d, nama), JSON.stringify(x));
  return d;
}

test('baca mengikuti kunci bersarang dan memilih elemen daftar menurut isinya', () => {
  const d = folder(CONTOH);
  assert.equal(baca(d, 'a.json', ['uji', 'semua', 'benar']), 496);
  assert.equal(baca(d, 'a.json', ['model', { berkas: 'y.onnx' }, 'ms']), 544);
});

test('baca gagal tertutup: kunci tidak ada, atau elemen daftar tidak cocok tepat sekali', () => {
  const d = folder(CONTOH);
  assert.throws(() => baca(d, 'a.json', ['uji', 'semua', 'hilang']), /hilang/);
  assert.throws(() => baca(d, 'a.json', ['model', { berkas: 'z.onnx' }, 'ms']), /0 kali/);
});

test('sel menulis bagian dengan persen dan rentang, ribuan, dan milidetik dengan koma', () => {
  const d = folder(CONTOH);
  assert.equal(sel(d, { dari: ['a.json', ['uji', 'semua']], benar: 'benar', jumlah: 'jumlah', rentang: 'rentang' }),
    '496 dari 625 (79,4%) [76–82%]');
  assert.equal(sel(d, { n: ['a.json', ['besar']] }), '33.906');
  assert.equal(sel(d, { ms: ['a.json', ['waktu']] }), '17,7 ms');
  assert.equal(sel(d, 'belum diukur'), 'belum diukur');
});

test('rantai: tulis dari bukti sungguhan, periksa sama; laporan yang diubah tangan atau tanpa penanda tertangkap', () => {
  const laporan = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vs-laporan-')), 'laporan.md');
  fs.writeFileSync(laporan, `# Laporan\n\n${MULAI}\nlama\n${AKHIR}\n\nPenutup.\n`);
  const jalan = (perintah) => spawnSync('node', [SKRIP, perintah, laporan], { encoding: 'utf8' });

  assert.equal(jalan('tulis').status, 0);
  const tertulis = fs.readFileSync(laporan, 'utf8');
  assert.ok(tertulis.includes(isi(BUKTI, TABEL)) && tertulis.endsWith('Penutup.\n') && !tertulis.includes('lama'));
  assert.equal(jalan('periksa').status, 0);

  fs.writeFileSync(laporan, tertulis.replace(' dari ', ' dari 1'));
  const r = jalan('periksa');
  assert.equal(r.status, 1);
  assert.match(r.stdout + r.stderr, /tidak sama/);

  fs.writeFileSync(laporan, '# tanpa penanda\n');
  assert.equal(jalan('tulis').status, 1);
});
```

- [x] **Step 2: Jalankan, pastikan merah**

Run: `npm test; echo "EXIT=$?"`
Expected: berkas uji baru gagal dimuat (`Cannot find module` untuk `laporan-0a.mjs`), `fail` lebih dari 0, `EXIT=1`.

- [x] **Step 3: Tulis `tools/laporan-0a.mjs`**

```js
// Tabel angka laporan Fase 0A (Rencana 15), dibaca langsung dari JSON di bukti/ dan tidak pernah diketik tangan.
// - tulis <laporan.md>: isi di antara MULAI dan AKHIR diganti dengan tabel dari bukti/.
// - periksa <laporan.md>: keluar 1 bila isi itu tidak sama dengan tabel dari bukti/ (laporan menyimpang dari sumbernya).
// Kunci yang tidak ada di sumber membuat alat gagal (gagal tertutup), bukan menulis sel kosong.
// Pakai: node tools/laporan-0a.mjs tulis|periksa <laporan.md> [--bukti <folder>]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const MULAI = '<!-- angka:mulai (ditulis tools/laporan-0a.mjs; jangan diubah tangan) -->';
export const AKHIR = '<!-- angka:akhir -->';
export const BUKTI = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'bukti');

export function baca(folder, berkas, kunci) {
  let nilai = JSON.parse(fs.readFileSync(path.join(folder, berkas), 'utf8'));
  for (const k of kunci) {
    if (k !== null && typeof k === 'object') {
      const cocok = Array.isArray(nilai) ? nilai.filter((x) => Object.entries(k).every(([a, b]) => x?.[a] === b)) : [];
      if (cocok.length !== 1) throw new Error(`${berkas}: ${JSON.stringify(k)} cocok ${cocok.length} kali, bukan sekali`);
      [nilai] = cocok;
    } else if (nilai !== null && typeof nilai === 'object' && Object.hasOwn(nilai, k)) {
      nilai = nilai[k];
    } else {
      throw new Error(`${berkas}: kunci "${k}" tidak ada`);
    }
  }
  return nilai;
}

const desimal = (x, d) => x.toFixed(d).replace('.', ',');
export const ribuan = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

export function sel(folder, s) {
  if (typeof s === 'string') return s;
  if (s.n) return ribuan(baca(folder, ...s.n));
  if (s.ms) return `${desimal(baca(folder, ...s.ms), 1)} ms`;
  if (s.dari) {
    const [berkas, dasar] = s.dari;
    const benar = baca(folder, berkas, [...dasar, s.benar]);
    const jumlah = baca(folder, berkas, [...dasar, s.jumlah]);
    let teks = `${ribuan(benar)} dari ${ribuan(jumlah)}`;
    if (jumlah > 0) teks += ` (${desimal((100 * benar) / jumlah, 1)}%)`;
    if (s.rentang) {
      const r = baca(folder, berkas, [...dasar, s.rentang]);
      if (r) teks += ` [${Math.round(100 * r[0])}–${Math.round(100 * r[1])}%]`;
    }
    return teks;
  }
  throw new Error(`sel tidak dikenal: ${JSON.stringify(s)}`);
}

const B10 = '2026-10-15-banding-pembaca-10.json';
const KELOMPOK = ['mobil-terang', 'mobil-gelap', 'motor-terang', 'motor-gelap'];
const RV = '2026-10-16-rantai-video-ulang-ringkasan.json';
const NV = '2026-10-16-rantai-video-nilai.json';
const pembaca = (nama, model) => [nama, ...KELOMPOK.map((k) => ({
  dari: [B10, ['tanpa-label-pilihan-pembaca', model, k]], benar: 'kedatangan_benar', jumlah: 'kedatangan',
  rentang: 'rentang_95_kedatangan',
}))];
const pencari = (nama, berkas) => [nama,
  { dari: [berkas, ['uji', 'semua']], benar: 'plat_ditemukan', jumlah: 'plat', rentang: 'rentang_95_ditemukan' },
  { n: [berkas, ['uji', 'semua', 'kotak_palsu']] },
  { dari: [berkas, ['uji', 'kecil']], benar: 'plat_ditemukan', jumlah: 'plat' }];
const miniPc = (berkas, model) => ({ ms: [berkas, ['model', { berkas: model }, 'per_utas', '2', 'median_ms']] });

export const TABEL = [
  {
    judul: 'Baca huruf: kedatangan terbaca benar pada set uji adil (potongan plat INDO-ALPR; dalam kurung siku rentang 95%)',
    kolom: ['Pembaca', 'Mobil terang', 'Mobil gelap', 'Motor terang', 'Motor gelap'],
    baris: [pembaca('fpo-indo-1 (fast-plate-ocr dilatih ulang, K26)', 'fpo-indo-1'),
      pembaca('fast-plate-ocr terbitan', 'fast-plate-ocr'), pembaca('Qwen3-VL-2B', 'qwen3-vl'),
      pembaca('mesin-baca-1 (dari nol)', 'mesin-baca-1')],
    catatan: 'Sumber: `2026-10-15-banding-pembaca-10.json`, set uji tanpa plat yang labelnya dipilih dari bacaan pembaca. '
      + 'Kelompok motor gelap kurang dari 30 kedatangan.',
  },
  {
    judul: 'Cari plat di foto utuh (set uji plat-lighting; plat ditemukan bila IoU minimal 0,5)',
    kolom: ['Pencari', 'Plat ditemukan', 'Kotak palsu', 'Plat kecil ditemukan'],
    baris: [pencari('YOLOX-Nano-640 (dipakai, K31)', '2026-10-16-pencari-yolox-nano-640-nilai.json'),
      pencari('YOLOX-Tiny-640', '2026-10-16-pencari-yolox-tiny-640-nilai.json'),
      pencari('YOLOX-Tiny-416', '2026-10-16-pencari-yolox-tiny-416-nilai.json'),
      pencari('YOLOX-Nano-416', '2026-10-16-pencari-yolox-nano-416-nilai.json'),
      pencari('Pembanding siap pakai YOLOv9-t-384', '2026-10-16-pencari-oim.json')],
    catatan: 'Ambang keyakinan dipilih di validasi; set uji dibaca sekali per pencari. Plat kecil: tingginya kurang dari 3% '
      + 'tinggi foto.',
  },
  {
    judul: 'Rantai utuh di video riset (cari plat, potong, baca, gabung per kedatangan), dinilai dari lembar owner',
    kolom: ['Hal', 'Angka'],
    baris: [
      ['Video', { n: [RV, ['video']] }],
      ['Gambar sampel per detik video', { n: [RV, ['aturan', 'sampel_per_detik']] }],
      ['Gambar sampel', { n: [RV, ['gambar_sampel']] }],
      ['Kedatangan', { n: [RV, ['kedatangan']] }],
      ['Kedatangan "yakin"', { n: [RV, ['yakin']] }],
      ['Kedatangan "ragu" (gerbang tidak dibuka)', { n: [RV, ['ragu']] }],
      ['Baris lembar yang diperiksa owner', { n: [NV, ['baris']] }],
      ['Bukan plat, menurut owner', { n: [NV, ['bukan_plat']] }],
      ['Plat tak terbaca, juga oleh owner', { n: [NV, ['tak_terbaca']] }],
      ['Plat yang dinilai', { n: [NV, ['kelompok', 'semua', 'dinilai']] }],
      ['Benar dan yakin', { dari: [NV, ['kelompok', 'semua']], benar: 'benar_yakin', jumlah: 'dinilai',
        rentang: 'rentang_95_benar_yakin' }],
      ['Benar tetapi ragu', { n: [NV, ['kelompok', 'semua', 'benar_ragu']] }],
      ['Salah dan ragu', { n: [NV, ['kelompok', 'semua', 'salah_ragu']] }],
      ['Salah dan yakin (bahaya buka-salah)', { n: [NV, ['kelompok', 'semua', 'salah_yakin']] }],
    ],
    catatan: 'Sumber: `2026-10-16-rantai-video-ulang-ringkasan.json` dan `2026-10-16-rantai-video-nilai.json`.',
  },
  {
    judul: 'Kecepatan: median per panggilan dengan 2 utas',
    kolom: ['Bagian', 'Laptop (Ryzen 7 8700F)', 'Mini PC (Celeron N5095), model saja'],
    baris: [
      ['Cari plat, YOLOX-Nano-640', { ms: ['2026-10-16-pencari-yolox-nano-640-cepat.json', ['per_utas', '2', 'median_ms']] },
        miniPc('2026-10-16-cepat-yolox-640-minipc.json', 'acak-yolox-nano-640.onnx')],
      ['Baca huruf, per potongan plat', { ms: ['2026-10-15-cepat-fpo-indo-1.json', ['per_utas', '2', 'utuh_ms', 'median']] },
        miniPc('2026-10-16-cepat-calon-minipc.json', 'cct_s_v2_global.onnx')],
      ['Rantai di video: cari plat per gambar sampel', { ms: [RV, ['waktu_ms', 'cari', 'median']] }, 'belum diukur'],
      ['Rantai di video: baca per potongan', { ms: [RV, ['waktu_ms', 'baca', 'median']] }, 'belum diukur'],
    ],
    catatan: 'Laptop: foto utuh atau potongan sungguhan, termasuk praproses. Mini PC: model saja, masukan buatan, bobot acak '
      + 'bersusunan sama (model hasil latih tidak dibawa ke sana, K15); pembacanya ONNX terbitan fast-plate-ocr yang susunannya '
      + 'sama dengan fpo-indo-1.',
  },
];

export function tabel(folder, t) {
  const baris = [`**${t.judul}**`, '', `| ${t.kolom.join(' | ')} |`, `|${t.kolom.map(() => '---').join('|')}|`];
  for (const b of t.baris) baris.push(`| ${b.map((s) => sel(folder, s)).join(' | ')} |`);
  if (t.catatan) baris.push('', t.catatan);
  return baris.join('\n');
}

export function isi(folder = BUKTI, daftar = TABEL) {
  return daftar.map((t) => tabel(folder, t)).join('\n\n');
}

export function ganti(teks, blok) {
  const a = teks.split(MULAI).length - 1;
  const b = teks.split(AKHIR).length - 1;
  if (a !== 1 || b !== 1 || teks.indexOf(MULAI) > teks.indexOf(AKHIR)) {
    throw new Error('penanda angka harus ada tepat sekali, MULAI sebelum AKHIR');
  }
  return `${teks.slice(0, teks.indexOf(MULAI) + MULAI.length)}\n\n${blok}\n\n${teks.slice(teks.indexOf(AKHIR))}`;
}

function utama(argumen) {
  const [perintah, laporan, ...lain] = argumen;
  const i = lain.indexOf('--bukti');
  const folder = i >= 0 ? lain[i + 1] : BUKTI;
  if (!['tulis', 'periksa'].includes(perintah) || !laporan) {
    console.error('Pakai: node tools/laporan-0a.mjs tulis|periksa <laporan.md> [--bukti <folder>]');
    return 2;
  }
  try {
    const lama = fs.readFileSync(laporan, 'utf8').replace(/\r\n/g, '\n');
    const baru = ganti(lama, isi(folder));
    if (perintah === 'tulis') {
      fs.writeFileSync(laporan, baru);
      console.log(`ditulis: ${TABEL.length} tabel dari ${folder}`);
      return 0;
    }
    if (baru !== lama) {
      console.error('laporan tidak sama dengan bukti/: jalankan "tulis" lagi, atau periksa sumbernya');
      return 1;
    }
    console.log(`sama dengan bukti/: ${TABEL.length} tabel`);
    return 0;
  } catch (galat) {
    console.error(`GAGAL: ${galat.message}`);
    return 1;
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) process.exit(utama(process.argv.slice(2)));
```

- [x] **Step 4: Jalankan, pastikan hijau**

Run: `npm test; echo "EXIT=$?"`
Expected: `pass 111` (107 + 4), `fail 0`, `EXIT=0`.

- [x] **Step 5: Commit** `tools/laporan-0a.mjs` dan ujinya, dengan alasan (angka laporan dibaca dari bukti, gagal tertutup,
penyimpangan tertangkap) dan angka gerbang Node 107 → 111.

---

### Task 2: Laporan Fase 0A

**Files:** Create `bukti/2026-10-16-laporan-fase-0a.md`

- [x] **Step 1: Tulis laporan dengan penanda tabel**

Bagian-bagiannya, dalam bahasa sederhana untuk owner:
1. **Ringkasan untuk owner** (setengah halaman):
   - yang sudah dibangun dan diukur;
   - yang paling kuat: baca huruf dari potongan plat;
   - yang paling lemah: pencari plat di video, bahan yang terlalu kecil untuk dibaca, dan tidak ada bahan malam atau motor
     dari sudut gerbang;
   - yang dibutuhkan berikutnya.
2. **Kesembilan langkah spec 8.1:** satu baris per langkah dengan status dan tautan bukti. Yang berbeda dari spec ditulis apa
   adanya: kelompok terang/gelap (bukan siang/malam), dan plat buatan komputer yang belum dibangun.
3. **Angka:** penanda `<!-- angka:mulai (ditulis tools/laporan-0a.mjs; jangan diubah tangan) -->` dan `<!-- angka:akhir -->`,
   diisi alat.
4. **Yang belum terjawab:**
   - K9, karena hanya bisa dibuktikan dari kamera gerbang (spec 8.4);
   - B2 (motor dari sudut gerbang), B3 (malam, hujan, silau), dan B5 (kecepatan di server sungguhan, termasuk unggah dan
     dekode);
   - P14;
   - izin fast-plate-ocr (K27);
   - plat yang terlewat di video (tidak terukur);
   - pemungutan suara per huruf (belum diuji).
5. **Risiko dan batas:**
   - semua mesin hasil latih `RISET-SAJA`, karena bobot awalnya `BELUM-JELAS`, jadi belum ada mesin yang boleh dijual;
   - di rantai utuh, 7 dari 10 "yakin" bukan plat, sehingga penahan buka-salah sekarang hanya daftar izin;
   - angka dari bahan luar berstatus sementara.
6. **Saran agen dan pilihan keputusan.** Saran ditulis dari angka, dengan alasan.
   - **Keputusan 1:** lanjut ke Fase 1, tunggu lokasi (Fase 0B), atau ubah arah, masing-masing dengan akibatnya. **Usulan
     agen (bacaan sekarang): Fase 0B dulu di lokasi owner sendiri (K5).** Rekaman dari posisi gerbang dibuat dengan HP atau
     CCTV yang sudah ada, tanpa pembelian (K6), karena kelemahan terbesar tidak bisa diperbaiki dengan bahan luar.
   - **Keputusan 2:** plat buatan komputer dibangun sekarang atau ditunda, dengan akibat masing-masing bagi mesin jualan
     (spec 2.4) dan bagi bahan motor dan malam.

- [x] **Step 2: Isi tabel dari bukti, lalu periksa**

Run: `node tools/laporan-0a.mjs tulis bukti/2026-10-16-laporan-fase-0a.md; echo "EXIT=$?"` lalu
`node tools/laporan-0a.mjs periksa bukti/2026-10-16-laporan-fase-0a.md; echo "EXIT=$?"`
Expected: `ditulis: 4 tabel ...`, `EXIT=0`; lalu `sama dengan bukti/: 4 tabel`, `EXIT=0`.

- [x] **Step 3: Baca ulang laporan**

Tiap angka di luar tabel harus ada di laporan rencana yang ditautkan. Laporan tidak memuat nomor plat apa pun, termasuk yang
pernah ditulis owner di percakapan.

- [x] **Step 4: Commit** laporan, dengan alasan (spec 8.1 langkah 9 dan 8.7) dan daftar isinya.

---

### Task 3: Catatan dan gerbang

- [x] **Step 1: Perbarui catatan** (skrip pencatat berkas; jangkar tepat sekali)

- `ROADMAP.md`:
  - butir "Rencana 15 ditulis" dan "Rencana 15 dijalankan" dicentang;
  - butir berikutnya "Owner memutuskan akhir Fase 0A";
  - status dan changelog.
- `CLAUDE.md` §7: tabel angka laporan dibuat `tools/laporan-0a.mjs` dan diperiksa dengan `periksa`.
- `OPEN-QUESTIONS.md`: paragraf "Sesudah Rencana 15".
- Rencana ini: kotak Task 1–3 dicentang dan catatan pelaksanaan.

- [x] **Step 2: Gerbang penuh, lalu commit**

Run: `npm test; echo "EXIT=$?"` lalu `npm run test:lab; echo "EXIT=$?"` lalu
`node tools/laporan-0a.mjs periksa bukti/2026-10-16-laporan-fase-0a.md; echo "EXIT=$?"` (satu per satu)
Expected: `pass 111`, `203 passed`, `sama dengan bukti/: 4 tabel`.

---

### Task 4: Keputusan owner (spec 8.7)

- [x] **Step 1: BERHENTI. Tanyakan keputusan 1** dengan satu pertanyaan pilihan ganda: lanjut ke Fase 1, Fase 0B dulu, atau
ubah arah. Saran di depan, akibat tiap pilihan, dan cara membaliknya disebut.

- [x] **Step 2: Catat keputusan 1** di `SEED.md` §3 (K berikutnya), `OPEN-QUESTIONS.md`, dan `ROADMAP.md` (changelog dengan
alasan), lalu commit.

- [x] **Step 3: Tanyakan keputusan 2** (plat buatan komputer) dengan satu pertanyaan pilihan ganda, lalu catat dengan cara yang
sama dan commit. **Fase 0A selesai** bila kedua keputusan tercatat di `ROADMAP.md` (spec 8.7).

---

## Pemeriksaan diri atas rencana ini

- **Cakupan spec 8.1 langkah 9 dan 8.7:**
  - laporan di `bukti/`;
  - angka per kelompok (tabel baca huruf per kelompok; cari plat per kelompok ukuran; rantai dari lembar);
  - daftar yang belum terjawab;
  - saran;
  - keputusan owner tercatat di `ROADMAP.md`.
- **Angka dibaca, tidak disalin:**
  - tabel ditulis alat dari JSON bukti;
  - `periksa` di gerbang akhir;
  - kunci yang hilang membuat alat gagal (diuji).
- **Uji rantai:** CLI `tulis` lalu `periksa` dengan `bukti/` sungguhan; laporan yang diubah tangan dan laporan tanpa penanda
  tertangkap.
- **Data pribadi:** laporan hanya memuat hitungan; nomor plat yang pernah ditulis owner tidak disalin.
- **Angka gerbang:** Node 107 → 111; lab tetap 203.
- **Nama konsisten:** `baca`, `sel`, `ribuan`, `tabel`, `isi`, `ganti`, `TABEL`, `MULAI`, `AKHIR`, `BUKTI`; bentuk sel `n`,
  `ms`, `dari` (dengan `benar`, `jumlah`, `rentang`).

## Catatan pelaksanaan (16 Okt)

- Dijalankan atas lampu hijau owner ("A. Jalankan sekarang"). Laporan:
  [`bukti/2026-10-16-laporan-fase-0a.md`](../bukti/2026-10-16-laporan-fase-0a.md).
- Task 1–3 sesuai rencana: uji alat angka terlihat merah dulu (`ERR_MODULE_NOT_FOUND`), lalu Node 107 → 111. Tabel ditulis alat,
  dan `periksa` menyatakan sama.
- Laporan diperiksa tidak memuat nomor plat, termasuk yang pernah ditulis owner di percakapan (Rencana 14).
- Task 4 (dua keputusan owner) dicentang saat keputusannya tercatat.
