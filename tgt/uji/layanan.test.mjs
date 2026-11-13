// Uji tgt/layanan.mjs: layanan gerbang, grup, kendaraan, dan tamu (Rencana T1 Task 2).
//
// Semua plat di berkas ini KARANGAN. Basis data uji ada di memori; tidak ada satu pun plat sungguhan di sini.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import {
  JENIS_KENDARAAN,
  normalkanPlat,
  buatGrup,
  buatGerbang,
  aktifkanGerbang,
  gerbangGrup,
  daftarkanKendaraan,
  kendaraanGerbang,
  cariKendaraanPlat,
  tambahTamu,
  tamuGerbang,
  grupDariKode,
} from '../layanan.mjs';

function siapkan() {
  const db = buka(':memory:');
  const grup = buatGrup(db, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id,
    nama: 'Kantor Contoh Gate Selatan',
    jenisLokasi: 'kantor',
    alamat: 'Jl. Contoh Industri III No. 42',
    kota: 'Surabaya',
  });
  return { db, grup, gerbang };
}

// ─── Plat ───────────────────────────────────────────────────────────────────────────────────────────

test('plat dinormalkan: huruf besar, spasi dan tanda baca dibuang', () => {
  assert.equal(normalkanPlat(' b 1234 abc '), 'B1234ABC');
  assert.equal(normalkanPlat('B-1234-ABC'), 'B1234ABC');
  assert.equal(normalkanPlat('b1234abc'), 'B1234ABC');
});

test('plat kosong ditolak', () => {
  assert.throws(() => normalkanPlat('   '), /plat/i);
  assert.throws(() => normalkanPlat('--'), /plat/i);
});

// ─── Gerbang ────────────────────────────────────────────────────────────────────────────────────────

test('gerbang dibuat dengan nama dan alamat, dan lahir berstatus belum aktif', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.equal(gerbang.nama, 'Kantor Contoh Gate Selatan');
    assert.equal(gerbang.alamat, 'Jl. Contoh Industri III No. 42');
    assert.equal(gerbang.status, 'belum_aktif', 'gerbang baru tidak boleh langsung aktif: alatnya belum terpasang');
  } finally {
    db.close();
  }
});

test('gerbang tanpa alamat atau tanpa kota ditolak, karena alamat wajib (K67)', () => {
  const { db, grup } = siapkan();
  try {
    const dasar = { grupId: grup.id, nama: 'Gate Tanpa Alamat', jenisLokasi: 'kantor', kota: 'Surabaya' };
    assert.throws(() => buatGerbang(db, { ...dasar, alamat: '' }), /alamat/i);
    assert.throws(() => buatGerbang(db, { ...dasar, alamat: '   ' }), /alamat/i);
    assert.throws(() => buatGerbang(db, { ...dasar, alamat: 'Jl. Ada', kota: '' }), /kota/i);
    assert.throws(() => buatGerbang(db, { ...dasar, nama: '', alamat: 'Jl. Ada' }), /nama/i);
  } finally {
    db.close();
  }
});

test('gerbang hanya terbaca dari grupnya sendiri', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const grupLain = buatGrup(db, { nama: 'Cluster Contoh', jenis: 'pribadi' });
    buatGerbang(db, {
      grupId: grupLain.id, nama: 'Cluster Contoh Gate Utama', jenisLokasi: 'perumahan',
      alamat: 'Jl. Contoh Asri 1', kota: 'Sidoarjo',
    });

    assert.deepEqual(gerbangGrup(db, grup.id).map((g) => g.id), [gerbang.id]);
    assert.equal(gerbangGrup(db, grupLain.id).length, 1);
  } finally {
    db.close();
  }
});

test('gerbang bisa diaktifkan sesudah alatnya terpasang', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.equal(aktifkanGerbang(db, gerbang.id).status, 'aktif');
  } finally {
    db.close();
  }
});

// ─── Kendaraan: pagar versi 1 (K65) ─────────────────────────────────────────────────────────────────

test('daftar jenis versi 1 hanya roda 4 ke atas, dan tidak memuat motor', () => {
  assert.deepEqual([...JENIS_KENDARAAN].sort(), ['bus', 'mobil', 'pikap', 'truk']);
  assert.ok(!JENIS_KENDARAAN.includes('motor'));
});

test('motor ditolak dengan pesan yang menyebut versi 2 (K65)', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.throws(
      () => daftarkanKendaraan(db, {
        gerbangId: gerbang.id, jenis: 'motor', plat: 'L 1111 AA', atasNama: 'Contoh',
      }),
      /versi 2/i,
    );
  } finally {
    db.close();
  }
});

test('jenis yang belum dikenal ikut ditolak: daftar putih, bukan daftar larangan', () => {
  const { db, gerbang } = siapkan();
  try {
    for (const jenis of ['bajaj', 'sepeda', '', 'MOBILX', undefined]) {
      assert.throws(
        () => daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis, plat: 'L 2222 BB', atasNama: 'Contoh' }),
        /jenis/i,
        `jenis ${JSON.stringify(jenis)} seharusnya ditolak`,
      );
    }
  } finally {
    db.close();
  }
});

test('mobil diterima, platnya tersimpan sudah dinormalkan', () => {
  const { db, gerbang } = siapkan();
  try {
    const k = daftarkanKendaraan(db, {
      gerbangId: gerbang.id, jenis: 'mobil', merek: 'Toyota', warna: 'hitam',
      plat: ' l 9876 xy ', atasNama: 'Budi Contoh', unit: 'Divisi Gudang',
    });
    assert.equal(k.jenis, 'mobil');
    assert.equal(k.plat, 'L9876XY');
    assert.equal(k.atas_nama, 'Budi Contoh');
  } finally {
    db.close();
  }
});

test('kendaraan wajib punya atas nama', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.throws(
      () => daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 3333 CC', atasNama: '  ' }),
      /atas nama/i,
    );
  } finally {
    db.close();
  }
});

// ─── Kendaraan: plat kembar dan batas gerbang ───────────────────────────────────────────────────────

test('plat yang sama tidak boleh dua kali di satu gerbang, walau ejaannya berbeda', () => {
  const { db, gerbang } = siapkan();
  try {
    daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 4444 DD', atasNama: 'Satu' });
    assert.throws(
      () => daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'l-4444-dd', atasNama: 'Dua' }),
      /sudah terdaftar/i,
    );
  } finally {
    db.close();
  }
});

test('plat yang sama BOLEH terdaftar di gerbang lain', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 5555 EE', atasNama: 'Satu' });
    const k = daftarkanKendaraan(db, { gerbangId: lain.id, jenis: 'mobil', plat: 'L 5555 EE', atasNama: 'Satu' });
    assert.equal(k.plat, 'L5555EE');
  } finally {
    db.close();
  }
});

test('daftar kendaraan satu gerbang tidak memuat kendaraan gerbang lain (K67)', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 6666 FF', atasNama: 'Satu' });
    daftarkanKendaraan(db, { gerbangId: lain.id, jenis: 'truk', plat: 'L 7777 GG', atasNama: 'Dua' });

    assert.deepEqual(kendaraanGerbang(db, gerbang.id).map((k) => k.plat), ['L6666FF']);
    assert.deepEqual(kendaraanGerbang(db, lain.id).map((k) => k.plat), ['L7777GG']);
  } finally {
    db.close();
  }
});

test('mencari plat memakai bentuk yang dinormalkan, dan tidak melintas gerbang', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 8888 HH', atasNama: 'Satu' });

    assert.equal(cariKendaraanPlat(db, gerbang.id, 'l 8888 hh').atas_nama, 'Satu');
    assert.equal(cariKendaraanPlat(db, lain.id, 'L8888HH'), undefined, 'plat gerbang lain tidak boleh ikut terbaca');
  } finally {
    db.close();
  }
});

// ─── Tamu ───────────────────────────────────────────────────────────────────────────────────────────

test('tamu disimpan dengan lama kunjungan dan mendapat kode undangan sendiri', () => {
  const { db, gerbang } = siapkan();
  try {
    const t = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Contoh', keperluan: 'kirim barang',
      jenis: 'pikap', plat: 'w 1212 zz', lamaHari: 2, diundangOleh: 'Budi Contoh',
    });
    assert.equal(t.plat, 'W1212ZZ');
    assert.equal(t.lama_hari, 2);
    assert.ok(t.kode_undangan && t.kode_undangan.length >= 4, 'tamu harus punya kode undangan');

    const lain = tambahTamu(db, {
      gerbangId: gerbang.id, nama: 'Tamu Kedua', jenis: 'mobil', plat: 'W 3434 YY', lamaHari: 1,
    });
    assert.notEqual(lain.kode_undangan, t.kode_undangan, 'kode undangan tidak boleh sama');
  } finally {
    db.close();
  }
});

test('lama kunjungan wajib bilangan bulat minimal 1 hari', () => {
  const { db, gerbang } = siapkan();
  try {
    for (const lamaHari of [0, -1, 1.5, '2', undefined, null]) {
      assert.throws(
        () => tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu', jenis: 'mobil', plat: 'W 5656 XX', lamaHari }),
        /lama kunjungan/i,
        `lamaHari ${JSON.stringify(lamaHari)} seharusnya ditolak`,
      );
    }
  } finally {
    db.close();
  }
});

test('kendaraan tamu ikut pagar versi 1: motor ditolak', () => {
  const { db, gerbang } = siapkan();
  try {
    assert.throws(
      () => tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu', jenis: 'motor', plat: 'W 7878 WW', lamaHari: 1 }),
      /versi 2/i,
    );
  } finally {
    db.close();
  }
});

test('daftar tamu satu gerbang tidak memuat tamu gerbang lain', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    const lain = buatGerbang(db, {
      grupId: grup.id, nama: 'Kantor Contoh Gate Utara', jenisLokasi: 'kantor',
      alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
    });
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu A', jenis: 'mobil', plat: 'W 1111 AA', lamaHari: 1 });
    tambahTamu(db, { gerbangId: lain.id, nama: 'Tamu B', jenis: 'mobil', plat: 'W 2222 BB', lamaHari: 1 });

    assert.deepEqual(tamuGerbang(db, gerbang.id).map((t) => t.nama), ['Tamu A']);
    assert.deepEqual(tamuGerbang(db, lain.id).map((t) => t.nama), ['Tamu B']);
  } finally {
    db.close();
  }
});

// ─── Grup ───────────────────────────────────────────────────────────────────────────────────────────

test('grup hanya pribadi atau perusahaan, dan kode undangannya berbeda-beda', () => {
  const db = buka(':memory:');
  try {
    assert.throws(() => buatGrup(db, { nama: 'Salah', jenis: 'yayasan' }), /jenis grup/i);
    const a = buatGrup(db, { nama: 'A', jenis: 'pribadi' });
    const b = buatGrup(db, { nama: 'B', jenis: 'perusahaan' });
    assert.notEqual(a.kode_undangan, b.kode_undangan);
  } finally {
    db.close();
  }
});

test('grup bisa diikuti dengan kode undangannya, dan kode salah tidak membuka grup mana pun', () => {
  const db = buka(':memory:');
  try {
    const a = buatGrup(db, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });
    assert.equal(grupDariKode(db, a.kode_undangan).id, a.id);
    assert.equal(grupDariKode(db, a.kode_undangan.toLowerCase()).id, a.id, 'kode tidak boleh peka huruf besar-kecil');
    assert.equal(grupDariKode(db, 'ZZZZZZ'), undefined);
  } finally {
    db.close();
  }
});
