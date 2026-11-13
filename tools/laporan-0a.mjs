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
