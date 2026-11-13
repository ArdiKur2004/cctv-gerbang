// Uji keputusan owner K74 (26 Okt): SEMUA DATA DISIMPAN, tidak ada yang dihapus.
//
// ⛔ INI MEMBALIK ARAH RENCANA T10, dan sebabnya harus diingat.
// Yang tercatat di SEED.md §3 K71 adalah kalimat owner "data tidak boleh di simpan semua". Sesi sebelumnya
// MENEBAK artinya, memilih bacaan "simpan seminimal mungkin lalu hapus yang lewat masa simpan", dan menulis
// bahwa "keduanya mengarah ke tindakan yang sama". Itu salah: owner mengoreksi bahwa maksudnya **semua data
// wajib disimpan dan tidak boleh dihapus**.
//
// Jadi arah gagalnya dibalik: yang TIDAK DIATUR berarti SIMPAN SELAMANYA. Menghapus data orang hanya terjadi
// bila ada yang menuliskan angkanya dengan sengaja. Salah ketik, peubah lingkungan yang hilang, atau
// pengaturan yang terlewat tidak boleh pernah menghapus apa pun.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { buka } from '../basis.mjs';
import { buatGrup, buatGerbang, tambahTamu, catatKejadian } from '../layanan.mjs';
import { SELAMANYA, masaSimpan, bersihkan, jadwalkanBersih } from '../simpan.mjs';
import { pengaturan } from '../pengaturan.mjs';
import { jalankan } from '../server.mjs';

function hariLalu(n, jam = 8) {
  const t = new Date(Date.now() - n * 24 * 60 * 60 * 1000);
  const dua = (x) => String(x).padStart(2, '0');
  return `${t.getFullYear()}-${dua(t.getMonth() + 1)}-${dua(t.getDate())}T${dua(jam)}:00:00`;
}

/** Basis data berkas berisi data SANGAT tua, plus foto sangat tua. Semuanya di folder sementara sistem. */
function siapkanDunia() {
  const akar = fs.mkdtempSync(path.join(os.tmpdir(), 'tgt-k74-'));
  const jalurBasis = path.join(akar, 'tgt.sqlite');
  const jalurFoto = path.join(akar, 'foto');
  fs.mkdirSync(jalurFoto, { recursive: true });

  const db = buka(jalurBasis);
  const grup = buatGrup(db, { nama: 'PT Contoh', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id, nama: 'Gate Contoh', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });
  catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(3000), arah: 'masuk', plat: 'L1111AA' });
  const tamu = tambahTamu(db, {
    gerbangId: gerbang.id, nama: 'Kurir Contoh', jenis: 'mobil', plat: 'L7777XX', lamaHari: 1,
  });
  catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(3000, 8), arah: 'masuk', plat: 'L7777XX' });
  catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(3000, 9), arah: 'keluar', plat: 'L7777XX' });
  db.close();

  const foto = path.join(jalurFoto, 'sangat-tua.jpg');
  fs.writeFileSync(foto, 'bukan foto sungguhan');
  const lamaMs = (Date.now() - 3000 * 24 * 60 * 60 * 1000) / 1000;
  fs.utimesSync(foto, lamaMs, lamaMs);

  return { akar, jalurBasis, jalurFoto, foto, tamuId: tamu.id };
}

const buang = (dunia) => fs.rmSync(dunia.akar, { recursive: true, force: true });

async function denganLingkungan(nilai, kerja) {
  const semula = {};
  for (const [k, v] of Object.entries(nilai)) {
    semula[k] = process.env[k];
    if (v === null) delete process.env[k];
    else process.env[k] = v;
  }
  try {
    return await kerja();
  } finally {
    for (const [k, v] of Object.entries(semula)) {
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
  }
}

// ─── Bawaan: simpan selamanya ───────────────────────────────────────────────────────────────────────

test('⛔ K74: masa simpan BAWAAN adalah SELAMANYA, bukan angka', async () => {
  // DIBALIK dari T3: dulu bawaannya foto 7 hari, kejadian 90, tamu 30. Angka itu tebakan agen atas kalimat
  // owner, dan tebakannya salah. Sekarang tidak ada angka bawaan sama sekali.
  await denganLingkungan({ TGT_SIMPAN_FOTO: null, TGT_SIMPAN_KEJADIAN: null, TGT_SIMPAN_TAMU: null }, () => {
    const h = masaSimpan();
    assert.deepEqual(h, { foto: SELAMANYA, kejadian: SELAMANYA, tamu: SELAMANYA },
      'masih ada angka masa simpan bawaan: data orang akan terhapus tanpa ada yang memintanya');
    const atur = pengaturan();
    assert.equal(atur.simpanFoto, SELAMANYA);
    assert.equal(atur.simpanKejadian, SELAMANYA);
    assert.equal(atur.simpanTamu, SELAMANYA);
  });
});

test('⛔ K74: bersihkan() dengan masa simpan bawaan TIDAK MENGHAPUS APA PUN', async () => {
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    await denganLingkungan({ TGT_SIMPAN_FOTO: null, TGT_SIMPAN_KEJADIAN: null, TGT_SIMPAN_TAMU: null }, () => {
      const h = bersihkan(db, masaSimpan(), { jalurFoto: dunia.jalurFoto });
      assert.deepEqual(h, { kejadian: 0, tamu: 0, kunjungan: 0, foto: 0 },
        'ada yang dihapus padahal masa simpannya selamanya');
    });
    // Data 3.000 hari pun tetap ada.
    assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 3);
    assert.equal(db.prepare('SELECT count(*) AS n FROM tamu').get().n, 1);
    assert.equal(db.prepare('SELECT count(*) AS n FROM kunjungan').get().n, 1);
    assert.equal(fs.existsSync(dunia.foto), true, 'foto 3.000 hari terhapus');
  } finally {
    db.close();
    buang(dunia);
  }
});

test('⛔ K74 RANTAI: menyalakan server dengan jalankan() TIDAK menghapus apa pun', async () => {
  // Rantainya, bukan cabangnya: di Rencana T10 justru jalur inilah yang menghapus 8 kejadian dan 4 foto.
  const dunia = siapkanDunia();
  try {
    const server = await denganLingkungan({
      TGT_BASIS: dunia.jalurBasis,
      TGT_FOTO: dunia.jalurFoto,
      TGT_PORTA: '0',
      TGT_ALAMAT: '127.0.0.1',
      TGT_SIMPAN_FOTO: null,
      TGT_SIMPAN_KEJADIAN: null,
      TGT_SIMPAN_TAMU: null,
    }, () => jalankan());
    await new Promise((selesai) => server.close(selesai));

    const db = buka(dunia.jalurBasis);
    try {
      assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian').get().n, 3,
        'server menghapus kejadian walau masa simpannya selamanya');
      assert.equal(db.prepare('SELECT count(*) AS n FROM tamu').get().n, 1);
    } finally {
      db.close();
    }
    assert.equal(fs.existsSync(dunia.foto), true, 'server menghapus foto walau masa simpannya selamanya');
  } finally {
    buang(dunia);
  }
});

test('⛔ K74: pengaturan yang SALAH KETIK tidak pernah menghapus apa pun', async () => {
  // Arah gagalnya: apa pun yang tidak terbaca sebagai angka hari = SIMPAN. Dulu nilai seperti ini melempar
  // galat, dan galat saat server menyala bisa membuat orang menghapus pengaturannya lalu memakai bawaan —
  // yang dulu berarti menghapus. Sekarang ia hanya berarti menyimpan.
  for (const salah of ['tujuh', '7 hari', '-3', '0', 'selamanya', ' ']) {
    await denganLingkungan({ TGT_SIMPAN_KEJADIAN: salah }, () => {
      assert.equal(masaSimpan().kejadian, SELAMANYA, `nilai "${salah}" tidak dibaca sebagai simpan selamanya`);
    });
  }
});

// ─── Masih bisa dinyalakan dengan sengaja ───────────────────────────────────────────────────────────

test('masa simpan masih bisa dinyalakan DENGAN SENGAJA, kalau owner memintanya nanti', async () => {
  // Kodenya tidak dicabut: masa simpan mungkin kembali sesudah diperiksa ahli hukum (spec §8, B9). Yang
  // berubah hanyalah arah bawaannya. Uji ini yang membuktikan jalur itu masih utuh.
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    await denganLingkungan({ TGT_SIMPAN_KEJADIAN: '90', TGT_SIMPAN_FOTO: '7', TGT_SIMPAN_TAMU: '30' }, () => {
      const h = bersihkan(db, masaSimpan(), { jalurFoto: dunia.jalurFoto });
      assert.ok(h.kejadian > 0, 'masa simpan yang disetel dengan sengaja tidak menghapus apa pun');
      assert.equal(h.foto, 1);
    });
  } finally {
    db.close();
    buang(dunia);
  }
});

test('masa simpan boleh dinyalakan untuk SEBAGIAN jenis saja', async () => {
  // Owner bisa memutuskan foto dihapus tetapi catatan disimpan selamanya, atau sebaliknya.
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    await denganLingkungan({
      TGT_SIMPAN_FOTO: '7', TGT_SIMPAN_KEJADIAN: null, TGT_SIMPAN_TAMU: null,
    }, () => {
      const h = bersihkan(db, masaSimpan(), { jalurFoto: dunia.jalurFoto });
      assert.equal(h.foto, 1, 'foto tidak terhapus padahal masa simpannya disetel');
      assert.equal(h.kejadian, 0, 'kejadian terhapus padahal masa simpannya selamanya');
      assert.equal(h.tamu, 0);
    });
  } finally {
    db.close();
    buang(dunia);
  }
});

// ─── Penjadwal tidak menyala bila tidak ada yang perlu dihapus ──────────────────────────────────────

test('penjadwal TIDAK menyala bila semua masa simpan selamanya', async () => {
  // Pewaktu yang berjalan tiap 6 jam untuk menghapus nol baris hanyalah beban dan kebisingan di layar.
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    await denganLingkungan({ TGT_SIMPAN_FOTO: null, TGT_SIMPAN_KEJADIAN: null, TGT_SIMPAN_TAMU: null }, () => {
      const dicatat = [];
      const jadwal = jadwalkanBersih(db, { jalurFoto: dunia.jalurFoto, catat: (...a) => dicatat.push(a.join(' ')) });
      try {
        assert.equal(jadwal.pewaktu, undefined, 'pewaktu menyala padahal tidak ada yang perlu dihapus');
        assert.match(dicatat.join('\n'), /selamanya|semua data disimpan/i,
          `keadaannya tidak disebut di layar; yang tercatat: ${JSON.stringify(dicatat)}`);
      } finally {
        jadwal.berhenti();
      }
    });
  } finally {
    db.close();
    buang(dunia);
  }
});

test('penjadwal menyala bila ada SATU saja masa simpan yang disetel', async () => {
  const dunia = siapkanDunia();
  const db = buka(dunia.jalurBasis);
  try {
    await denganLingkungan({ TGT_SIMPAN_FOTO: '7', TGT_SIMPAN_KEJADIAN: null, TGT_SIMPAN_TAMU: null }, () => {
      const jadwal = jadwalkanBersih(db, { jalurFoto: dunia.jalurFoto, catat: () => {} });
      try {
        assert.notEqual(jadwal.pewaktu, undefined, 'penjadwal tidak menyala padahal foto punya masa simpan');
        assert.equal(jadwal.pewaktu.hasRef(), false, 'pewaktu tidak di-unref');
      } finally {
        jadwal.berhenti();
      }
    });
  } finally {
    db.close();
    buang(dunia);
  }
});
