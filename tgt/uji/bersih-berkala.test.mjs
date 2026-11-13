// Uji penjadwal pembersih masa simpan (Rencana T10 Task 1).
//
// ⛔ KENAPA BERKAS INI ADA, padahal simpan.test.mjs sudah punya 23 uji yang hijau sejak T3.
// Semua uji itu memanggil `bersihkan()` LANGSUNG. Ternyata tidak ada satu pun kode produksi yang
// memanggilnya — jadi masa simpan yang menurut K71 "ditegakkan di dalam kode" tidak menghapus apa pun selama
// tujuh rencana, sementara 23 uji terus hijau. Foto kendaraan dan catatan plat beserta jam keluar masuk
// menumpuk selamanya; itu data pribadi menurut UU PDP 27/2022 (CLAUDE.md §4).
//
// Karena itu uji di berkas ini menelusuri RANTAINYA, lewat `jalankan()` — jalur yang benar-benar dipakai
// produksi — bukan lewat fungsi penjadwalnya saja.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { buka } from '../basis.mjs';
import { buatGrup, buatGerbang, catatKejadian } from '../layanan.mjs';
import { SELANG_BERSIH_MS, jadwalkanBersih } from '../simpan.mjs';
import { jalankan } from '../server.mjs';

/** Waktu dalam bentuk yang dipakai kejadian: ISO jam setempat, n hari yang lalu. */
function hariLalu(n, jam = 8) {
  const t = new Date(Date.now() - n * 24 * 60 * 60 * 1000);
  const dua = (x) => String(x).padStart(2, '0');
  return `${t.getFullYear()}-${dua(t.getMonth() + 1)}-${dua(t.getDate())}T${dua(jam)}:00:00`;
}

/**
 * Siapkan satu basis data BERKAS (bukan di memori) berisi satu kejadian tua dan satu kejadian baru, plus satu
 * foto tua dan satu foto baru. Semuanya di folder sementara sistem: uji TIDAK PERNAH menyentuh data/tgt/.
 */
function siapkanDunia() {
  const akar = fs.mkdtempSync(path.join(os.tmpdir(), 'tgt-t10-'));
  const jalurBasis = path.join(akar, 'tgt.sqlite');
  const jalurFoto = path.join(akar, 'foto');
  fs.mkdirSync(jalurFoto, { recursive: true });

  const db = buka(jalurBasis);
  const grup = buatGrup(db, { nama: 'PT Contoh', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id, nama: 'Gate Contoh', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });
  catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(200), arah: 'masuk', plat: 'L1111AA' });
  catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(1), arah: 'masuk', plat: 'L2222BB' });
  db.close();

  const fotoTua = path.join(jalurFoto, 'tua.jpg');
  const fotoBaru = path.join(jalurFoto, 'baru.jpg');
  fs.writeFileSync(fotoTua, 'bukan foto sungguhan');
  fs.writeFileSync(fotoBaru, 'bukan foto sungguhan');
  const lamaMs = Date.now() - 200 * 24 * 60 * 60 * 1000;
  fs.utimesSync(fotoTua, lamaMs / 1000, lamaMs / 1000);

  return { akar, jalurBasis, jalurFoto, fotoTua, fotoBaru };
}

function bersihkanDunia(dunia) {
  fs.rmSync(dunia.akar, { recursive: true, force: true });
}

/**
 * Masa simpan yang disetel SENGAJA untuk uji di berkas ini.
 *
 * ⛔ Sejak K74 (owner, 26 Okt) bawaannya SIMPAN SELAMANYA — semua data wajib disimpan, dan penjadwal tidak
 * menyala sama sekali kecuali ada masa simpan yang disetel dengan sengaja. Uji di berkas ini menguji MESIN
 * penghapusnya, jadi ia menyetel angkanya sendiri. Bahwa bawaannya tidak menghapus apa pun dijaga di
 * tgt/uji/simpan-semua.test.mjs — jangan pindahkan salah satunya ke berkas yang lain.
 */
const SIMPAN_UJI = { TGT_SIMPAN_KEJADIAN: '90', TGT_SIMPAN_FOTO: '7', TGT_SIMPAN_TAMU: '30' };

/**
 * Jalankan satu fungsi dengan peubah lingkungan TGT_* tertentu, lalu kembalikan seperti semula.
 *
 * SINKRON dengan sengaja: uji penjadwal memanggilnya tanpa `await`, dan versi async akan mengembalikan Promise
 * yang terlihat seperti objek penjadwal — `jadwal.pewaktu` menjadi undefined tanpa satu pun uji mengeluh.
 * Pemanggil yang butuh async tetap bisa memakainya karena ia meneruskan nilai kembalian apa adanya.
 */
function denganLingkungan(nilai, kerja) {
  const semula = {};
  for (const [k, v] of Object.entries(nilai)) {
    semula[k] = process.env[k];
    process.env[k] = v;
  }
  try {
    return kerja();
  } finally {
    for (const [k, v] of Object.entries(semula)) {
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
  }
}

// ─── Rantai: lewat jalankan(), jalur yang dipakai produksi ──────────────────────────────────────────

test('⛔ RANTAI: menyalakan server dengan jalankan() benar-benar MENGHAPUS data yang lewat masa simpan', async () => {
  const dunia = siapkanDunia();
  try {
    const server = await denganLingkungan({
      TGT_BASIS: dunia.jalurBasis,
      TGT_FOTO: dunia.jalurFoto,
      TGT_PORTA: '0',
      TGT_ALAMAT: '127.0.0.1',
      TGT_SIMPAN_KEJADIAN: '90',
      TGT_SIMPAN_FOTO: '7',
      TGT_SIMPAN_TAMU: '30',
    }, () => jalankan());

    try {
      const db = buka(dunia.jalurBasis);
      try {
        const plat = db.prepare('SELECT plat FROM kejadian ORDER BY id').all().map((k) => k.plat);
        assert.deepEqual(plat, ['L2222BB'],
          'kejadian 200 hari masih ada: pembersih masa simpan tidak pernah dipanggil jalur produksi');
      } finally {
        db.close();
      }
      assert.equal(fs.existsSync(dunia.fotoTua), false, 'foto 200 hari masih ada');
      assert.equal(fs.existsSync(dunia.fotoBaru), true, 'foto baru ikut terhapus: pembersihnya terlalu rakus');
    } finally {
      await new Promise((selesai) => server.close(selesai));
    }
  } finally {
    bersihkanDunia(dunia);
  }
});

test('⛔ RANTAI: jalankan() memberi tahu di layar berapa yang dihapus', async () => {
  // Pembersih yang bekerja diam-diam tidak bisa dibedakan dari pembersih yang tidak jalan.
  const dunia = siapkanDunia();
  const dicatat = [];
  const aslinya = console.error;
  console.error = (...a) => dicatat.push(a.join(' '));
  try {
    const server = await denganLingkungan({
      TGT_BASIS: dunia.jalurBasis, TGT_FOTO: dunia.jalurFoto, TGT_PORTA: '0', TGT_ALAMAT: '127.0.0.1',
      ...SIMPAN_UJI,
    }, () => jalankan());
    await new Promise((selesai) => server.close(selesai));
  } finally {
    console.error = aslinya;
    bersihkanDunia(dunia);
  }
  const semua = dicatat.join('\n');
  assert.match(semua, /masa simpan|dibersihkan|dihapus/i,
    `tidak ada kabar pembersihan di layar server; yang tercatat: ${JSON.stringify(dicatat)}`);
  assert.match(semua, /\b1\b/, 'jumlah yang dihapus tidak disebut');
});

// ─── Penjadwalnya sendiri ───────────────────────────────────────────────────────────────────────────

test('penjadwal berjalan SEKALI saat menyala, bukan hanya menunggu selang berikutnya', () => {
  // Gerbang yang dinyalakan ulang tiap hari, dengan selang 6 jam, tidak boleh berarti tidak pernah bersih.
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    const jadwal = denganLingkungan(SIMPAN_UJI, () => jadwalkanBersih(db, { jalurFoto: dunia.jalurFoto }));
    try {
      assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 1,
        'penjadwal tidak membersihkan apa pun saat dinyalakan');
    } finally {
      jadwal.berhenti();
    }
  } finally {
    db.close();
    bersihkanDunia(dunia);
  }
});

test('penjadwal berjalan LAGI pada selang berikutnya', async () => {
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    // Selang sengaja sangat pendek, supaya ujinya tidak menunggu 6 jam.
    const jadwal = denganLingkungan(SIMPAN_UJI, () => jadwalkanBersih(db, {
      jalurFoto: dunia.jalurFoto, selangMs: 20,
    }));
    try {
      // Kejadian tua BARU disisipkan sesudah jalan pertama: kalau penjadwal hanya jalan sekali, ia akan tetap ada.
      db.prepare(
        "INSERT INTO kejadian (gerbang_id, waktu, arah, plat) VALUES (1, ?, 'masuk', 'L3333CC')",
      ).run(hariLalu(300));
      assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 2);

      await new Promise((selesai) => setTimeout(selesai, 120));
      assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 1,
        'penjadwal tidak jalan lagi pada selang berikutnya');
    } finally {
      jadwal.berhenti();
    }
  } finally {
    db.close();
    bersihkanDunia(dunia);
  }
});

test('⛔ pewaktunya di-unref: proses tidak pernah tertahan hidup karena penjadwal ini', () => {
  // Prinsip #3: perkakas yang kita jalankan tidak boleh membunuh mesin yang menjalankannya. Pewaktu yang
  // tidak di-unref membuat `node` tidak bisa keluar, dan proses yatim seperti itu yang pernah membekukan
  // laptop ini selama 7 jam (insiden 2026-09-03).
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    const jadwal = denganLingkungan(SIMPAN_UJI, () => jadwalkanBersih(db, { jalurFoto: dunia.jalurFoto }));
    try {
      assert.equal(typeof jadwal.pewaktu?.hasRef, 'function', 'penjadwal tidak membuka pewaktunya untuk diperiksa');
      assert.equal(jadwal.pewaktu.hasRef(), false, 'pewaktu penjadwal tidak di-unref: proses akan tertahan hidup');
    } finally {
      jadwal.berhenti();
    }
  } finally {
    db.close();
    bersihkanDunia(dunia);
  }
});

test('⛔ pembersih yang melempar galat TIDAK mematikan server, tetapi galatnya tercatat', () => {
  // Basis data yang terkunci atau disk penuh tidak boleh menjatuhkan gerbang. Tetapi galat yang ditelan diam-diam
  // berarti data pribadi menumpuk tanpa ada yang tahu — jadi ia wajib terlihat.
  const dicatat = [];
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    const meledak = () => { throw new Error('basis data terkunci (buatan uji)'); };
    let jadwal;
    assert.doesNotThrow(() => {
      jadwal = denganLingkungan(SIMPAN_UJI, () => jadwalkanBersih(db, {
        jalurFoto: dunia.jalurFoto, bersih: meledak, catat: (...a) => dicatat.push(a.join(' ')),
      }));
    }, 'galat pembersih menjatuhkan penjadwal');
    jadwal.berhenti();
    assert.match(dicatat.join('\n'), /gagal|galat/i,
      `galat pembersih tidak tercatat; yang tercatat: ${JSON.stringify(dicatat)}`);
    assert.match(dicatat.join('\n'), /terkunci/, 'pesan galat aslinya tidak ikut, jadi sebabnya tidak bisa dicari');
  } finally {
    db.close();
    bersihkanDunia(dunia);
  }
});

test(`selang bawaan ${SELANG_BERSIH_MS / 3_600_000} jam dibaca dari satu tempat, bukan disalin`, () => {
  assert.ok(Number.isInteger(SELANG_BERSIH_MS) && SELANG_BERSIH_MS > 0);
  // Cukup sering supaya gerbang yang menyala terus tetap bersih tiap hari, cukup jarang supaya tidak
  // mengganggu: antara satu jam dan satu hari.
  assert.ok(SELANG_BERSIH_MS >= 3_600_000, 'selang di bawah satu jam: pembersih ikut membebani gerbang');
  assert.ok(SELANG_BERSIH_MS <= 24 * 3_600_000, 'selang di atas satu hari: data pribadi menumpuk terlalu lama');
});

// ─── Penjaga: buatServer TIDAK boleh menjadwalkan apa pun ───────────────────────────────────────────

test('⛔ buatServer() tidak menjadwalkan pembersih: 50-an uji memakainya dan folder foto sungguhan akan disapu', () => {
  // Ini bukan kerapian. `pengaturan()` bawaan menunjuk ke data/tgt/foto — folder SUNGGUHAN milik owner. Kalau
  // penjadwal ikut di buatServer(), tiap `npm test` akan menghapus foto di sana.
  const sumber = fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname.slice(1)), '..', 'server.mjs'), 'utf8');
  const badan = sumber.slice(sumber.indexOf('export function buatServer'), sumber.indexOf('export function jalankan'));
  assert.ok(badan.length > 100, 'bentuk server.mjs berubah: penjaga ini tidak lagi memeriksa apa pun');
  assert.doesNotMatch(badan, /jadwalkanBersih/,
    'buatServer() menjadwalkan pembersih: uji akan menghapus foto sungguhan di data/tgt/foto');
  // Dan jalankan() MEMANG memanggilnya.
  const startup = sumber.slice(sumber.indexOf('export function jalankan'));
  assert.match(startup, /jadwalkanBersih/, 'jalankan() tidak menjadwalkan pembersih');
});
