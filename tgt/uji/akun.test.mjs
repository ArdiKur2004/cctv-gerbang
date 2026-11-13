// Uji tgt/akun.mjs: akun, masuk, dan keanggotaan grup (Rencana T2 Task 2).
//
// Semua nomor WA dan sandi di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import {
  PERAN, normalkanWa, buatAkun, masuk, buatGrupBaru, ikutGrup, tetapkanPeran, peranDi, grupSaya,
} from '../akun.mjs';

const SANDI = 'sandi-contoh-1';

function siapkan() {
  const db = buka(':memory:');
  const aldy = buatAkun(db, { nama: 'Aldy Contoh', wa: '081200000001', sandi: SANDI });
  return { db, aldy };
}

// ─── Nomor WA ───────────────────────────────────────────────────────────────────────────────────────

test('nomor WA dinormalkan: 08..., +62..., dan 62... menjadi satu bentuk', () => {
  assert.equal(normalkanWa('081200000001'), '6281200000001');
  assert.equal(normalkanWa('+62 812 0000 0001'), '6281200000001');
  assert.equal(normalkanWa('6281200000001'), '6281200000001');
  assert.equal(normalkanWa('0812-0000-0001'), '6281200000001');
});

test('nomor WA yang tidak masuk akal ditolak', () => {
  for (const nomor of ['', '   ', '0812', 'abcd', '12345678901234567890123']) {
    assert.throws(() => normalkanWa(nomor), /nomor/i, `nomor ${JSON.stringify(nomor)} seharusnya ditolak`);
  }
});

test('satu nomor WA tidak bisa dipakai dua akun, walau ejaannya berbeda', () => {
  const { db } = siapkan();
  try {
    assert.throws(
      () => buatAkun(db, { nama: 'Orang Lain', wa: '+62 812 0000 0001', sandi: SANDI }),
      /sudah terdaftar/i,
    );
  } finally {
    db.close();
  }
});

// ─── Sandi ──────────────────────────────────────────────────────────────────────────────────────────

test('sandi tidak pernah tersimpan apa adanya, dan dua orang bersandi sama punya hash berbeda', () => {
  const { db, aldy } = siapkan();
  try {
    const lain = buatAkun(db, { nama: 'Orang Kedua', wa: '081200000002', sandi: SANDI });
    const hash = (id) => db.prepare('SELECT sandi_hash FROM pengguna WHERE id = ?').get(id).sandi_hash;

    assert.ok(!hash(aldy.id).includes(SANDI), 'sandi tersimpan apa adanya');
    assert.notEqual(hash(aldy.id), hash(lain.id), 'hash dua sandi yang sama harus berbeda (garamnya berbeda)');
  } finally {
    db.close();
  }
});

test('akun yang dikembalikan tidak pernah memuat hash sandi', () => {
  const { db, aldy } = siapkan();
  try {
    assert.equal(aldy.sandi_hash, undefined);
    assert.equal(masuk(db, { wa: '081200000001', sandi: SANDI }).sandi_hash, undefined);
  } finally {
    db.close();
  }
});

test('sandi terlalu pendek ditolak', () => {
  const db = buka(':memory:');
  try {
    assert.throws(() => buatAkun(db, { nama: 'Pendek', wa: '081200000009', sandi: 'abc' }), /sandi/i);
  } finally {
    db.close();
  }
});

test('masuk berhasil dengan sandi benar', () => {
  const { db, aldy } = siapkan();
  try {
    assert.equal(masuk(db, { wa: '+62 812 0000 0001', sandi: SANDI }).id, aldy.id);
  } finally {
    db.close();
  }
});

test('nomor tak terdaftar dan sandi salah memberi pesan yang SAMA', () => {
  const { db } = siapkan();
  try {
    let pesanSandiSalah;
    let pesanNomorTakAda;
    assert.throws(() => masuk(db, { wa: '081200000001', sandi: 'sandi-salah-1' }), (e) => {
      pesanSandiSalah = e.message;
      return true;
    });
    assert.throws(() => masuk(db, { wa: '081200000777', sandi: SANDI }), (e) => {
      pesanNomorTakAda = e.message;
      return true;
    });
    assert.equal(
      pesanSandiSalah, pesanNomorTakAda,
      'pesan yang berbeda memberi tahu orang luar nomor mana yang terdaftar',
    );
  } finally {
    db.close();
  }
});

// ─── Grup dan peran ─────────────────────────────────────────────────────────────────────────────────

test('tiga peran saja, daftar putih', () => {
  assert.deepEqual([...PERAN], ['pengelola', 'satpam', 'penghuni']);
});

test('pembuat grup otomatis menjadi pengelola', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup, peran } = buatGrupBaru(db, aldy.id, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });
    assert.equal(peran, 'pengelola');
    assert.equal(peranDi(db, grup.id, aldy.id), 'pengelola');
  } finally {
    db.close();
  }
});

test('ikut grup dengan kode undangan menjadi penghuni', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup } = buatGrupBaru(db, aldy.id, { nama: 'Cluster Contoh', jenis: 'pribadi' });
    const tetangga = buatAkun(db, { nama: 'Tetangga Contoh', wa: '081200000003', sandi: SANDI });

    const ikut = ikutGrup(db, tetangga.id, grup.kode_undangan);
    assert.equal(ikut.peran, 'penghuni');
    assert.equal(peranDi(db, grup.id, tetangga.id), 'penghuni');
  } finally {
    db.close();
  }
});

test('kode undangan salah tidak memasukkan siapa pun', () => {
  const { db, aldy } = siapkan();
  try {
    assert.throws(() => ikutGrup(db, aldy.id, 'ZZZZZZ'), /kode undangan/i);
    assert.equal(db.prepare('SELECT count(*) AS n FROM anggota').get().n, 0);
  } finally {
    db.close();
  }
});

test('ikut grup yang sama dua kali tidak menggandakan keanggotaan dan tidak mengubah peran', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup } = buatGrupBaru(db, aldy.id, { nama: 'PT Contoh', jenis: 'perusahaan' });
    // Pengelola yang menekan tautan undangannya sendiri tidak boleh turun menjadi penghuni.
    ikutGrup(db, aldy.id, grup.kode_undangan);
    assert.equal(peranDi(db, grup.id, aldy.id), 'pengelola');
    assert.equal(db.prepare('SELECT count(*) AS n FROM anggota').get().n, 1);
  } finally {
    db.close();
  }
});

test('peran bisa diubah menjadi satpam, tetapi peran yang tidak dikenal ditolak', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup } = buatGrupBaru(db, aldy.id, { nama: 'PT Contoh', jenis: 'perusahaan' });
    const pakSatpam = buatAkun(db, { nama: 'Pak Satpam', wa: '081200000004', sandi: SANDI });
    ikutGrup(db, pakSatpam.id, grup.kode_undangan);

    tetapkanPeran(db, grup.id, pakSatpam.id, 'satpam');
    assert.equal(peranDi(db, grup.id, pakSatpam.id), 'satpam');

    for (const peran of ['admin', 'SATPAM', '', undefined]) {
      assert.throws(() => tetapkanPeran(db, grup.id, pakSatpam.id, peran), /peran/i);
    }
    assert.equal(peranDi(db, grup.id, pakSatpam.id), 'satpam', 'peran tidak boleh berubah saat penolakan');
  } finally {
    db.close();
  }
});

test('grup terakhir tidak boleh kehilangan pengelolanya', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup } = buatGrupBaru(db, aldy.id, { nama: 'PT Contoh', jenis: 'perusahaan' });
    assert.throws(() => tetapkanPeran(db, grup.id, aldy.id, 'penghuni'), /pengelola/i);
    assert.equal(peranDi(db, grup.id, aldy.id), 'pengelola');
  } finally {
    db.close();
  }
});

test('orang yang bukan anggota tidak punya peran, dan itu bukan galat', () => {
  const { db, aldy } = siapkan();
  try {
    const { grup } = buatGrupBaru(db, aldy.id, { nama: 'PT Contoh', jenis: 'perusahaan' });
    const orangLuar = buatAkun(db, { nama: 'Orang Luar', wa: '081200000005', sandi: SANDI });
    assert.equal(peranDi(db, grup.id, orangLuar.id), undefined);
  } finally {
    db.close();
  }
});

test('satu orang bisa berada di dua grup dengan peran berbeda', () => {
  const { db, aldy } = siapkan();
  try {
    const sendiri = buatGrupBaru(db, aldy.id, { nama: 'Rumah Aldy', jenis: 'pribadi' });

    const bos = buatAkun(db, { nama: 'Bos Contoh', wa: '081200000006', sandi: SANDI });
    const kantor = buatGrupBaru(db, bos.id, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });
    ikutGrup(db, aldy.id, kantor.grup.kode_undangan);

    assert.equal(peranDi(db, sendiri.grup.id, aldy.id), 'pengelola');
    assert.equal(peranDi(db, kantor.grup.id, aldy.id), 'penghuni');

    const daftar = grupSaya(db, aldy.id);
    assert.deepEqual(
      daftar.map((g) => [g.nama, g.peran]).sort(),
      [['PT Contoh Niaga', 'penghuni'], ['Rumah Aldy', 'pengelola']],
    );
  } finally {
    db.close();
  }
});

test('grupSaya tidak memuat grup yang bukan miliknya', () => {
  const { db, aldy } = siapkan();
  try {
    const orangLain = buatAkun(db, { nama: 'Orang Lain', wa: '081200000007', sandi: SANDI });
    buatGrupBaru(db, orangLain.id, { nama: 'Grup Orang Lain', jenis: 'pribadi' });
    assert.deepEqual(grupSaya(db, aldy.id), []);
  } finally {
    db.close();
  }
});
