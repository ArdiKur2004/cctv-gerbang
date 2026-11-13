// Uji tautan undangan masuk per orang (Rencana T8 Task 2, persetujuan owner 26 Okt).
//
// ⛔ TAUTAN INI ADALAH KUNCI MASUK. Siapa pun yang memegangnya menjadi orang itu. Karena itu pagarnya diuji
// lebih rapat daripada fitur biasa: sekali pakai, kedaluwarsa, hanya pengelola yang membuatnya, dan tandanya
// tersimpan ter-hash. Satu lubang di sini berarti orang luar masuk sebagai penghuni.
//
// Semua email dan nama di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

import { buka } from '../basis.mjs';
import { mintaOtp, masukDenganOtp, UMUR_UNDANGAN_HARI } from '../akun.mjs';
import * as akses from '../akses.mjs';

const sesi = (orang) => ({ penggunaId: orang.id });

function akunBaru(db, email, nama) {
  let kode;
  mintaOtp(db, { email, kirim: (_e, k) => { kode = k; } });
  return masukDenganOtp(db, { email, kode, nama });
}

function siapkan() {
  const db = buka(':memory:');
  const bos = akunBaru(db, 'bos@example.test', 'Bos Contoh');
  const { grup } = akses.buatGrup(db, sesi(bos), { nama: 'RT 05 Contoh', jenis: 'pribadi' });

  const pakSatpam = akunBaru(db, 'satpam@example.test', 'Pak Satpam');
  akses.ikutGrup(db, sesi(pakSatpam), grup.kode_undangan);
  akses.tetapkanPeran(db, sesi(bos), grup.id, pakSatpam.id, 'satpam');

  const ani = akunBaru(db, 'ani@example.test', 'Ani Contoh');
  akses.ikutGrup(db, sesi(ani), grup.kode_undangan);

  // Pengelola grup LAIN. Ia pengelola, tetapi bukan di grup ini.
  const bosLain = akunBaru(db, 'lain@example.test', 'Bos Lain');
  const grupLain = akses.buatGrup(db, sesi(bosLain), { nama: 'Grup Lain', jenis: 'pribadi' }).grup;

  return { db, grup, bos, pakSatpam, ani, bosLain, grupLain };
}

// ─── Anggota tanpa email ────────────────────────────────────────────────────────────────────────────

test('pengelola membuat anggota TANPA email, cukup namanya', () => {
  // Inti alasan rencana ini ada: banyak warga tidak punya email yang mereka buka. Tautan undangan membuat
  // email menjadi tidak wajib, bukan sekadar lebih murah daripada layanan surel.
  const { db, grup, bos } = siapkan();
  try {
    const orang = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    assert.equal(orang.nama, 'Pak Warga');
    assert.equal(orang.email, null, 'anggota tanpa email seharusnya tersimpan tanpa email, bukan email karangan');
    assert.equal(orang.peran, 'penghuni');
    assert.ok(akses.anggotaGrup(db, sesi(bos), grup.id).some((a) => a.nama === 'Pak Warga'));
  } finally {
    db.close();
  }
});

test('anggota tanpa email DAN tanpa nama ditolak: tidak ada yang bisa dikenali', () => {
  const { db, grup, bos } = siapkan();
  try {
    assert.throws(() => akses.tambahAnggota(db, sesi(bos), grup.id, {}), /nama/i);
    assert.throws(() => akses.tambahAnggota(db, sesi(bos), grup.id, { nama: '   ' }), /nama/i);
  } finally {
    db.close();
  }
});

test('banyak anggota tanpa email boleh ada bersamaan', () => {
  // Kalau email kosong disimpan sebagai string kosong, bukan NULL, indeks unik akan menolak orang kedua.
  const { db, grup, bos } = siapkan();
  try {
    akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Satu' });
    akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Dua' });
    const nama = akses.anggotaGrup(db, sesi(bos), grup.id).map((a) => a.nama);
    assert.ok(nama.includes('Warga Satu') && nama.includes('Warga Dua'));
  } finally {
    db.close();
  }
});

// ─── Membuat tautan ─────────────────────────────────────────────────────────────────────────────────

test('pengelola membuat tautan masuk untuk anggotanya', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const undangan = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);

    assert.equal(typeof undangan.tanda, 'string');
    assert.ok(undangan.tanda.length >= 32, 'tanda terlalu pendek untuk kunci masuk');
    assert.equal(undangan.nama, 'Pak Warga');
    assert.equal(undangan.grup, 'RT 05 Contoh', 'pengelola perlu tahu tautan ini untuk grup yang mana');
    assert.ok(undangan.kedaluwarsa, 'pengelola perlu tahu sampai kapan tautannya berlaku');
  } finally {
    db.close();
  }
});

test('⛔ tanda tautan tersimpan TER-HASH, tidak pernah apa adanya', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);

    const baris = db.prepare('SELECT * FROM undangan_masuk').all();
    assert.equal(baris.length, 1);
    assert.ok(!JSON.stringify(baris).includes(tanda),
      'tanda tersimpan apa adanya: siapa pun yang membaca berkas basis data bisa masuk sebagai orang itu');
    assert.equal(baris[0].tanda_hash, createHash('sha256').update(tanda).digest('base64'));
    assert.equal(baris[0].dibuat_oleh, bos.id, 'siapa yang membuat tautan tidak tercatat');
  } finally {
    db.close();
  }
});

test(`tautan berlaku ${UMUR_UNDANGAN_HARI} hari, dibaca dari satu tempat`, () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    const baris = db.prepare('SELECT kedaluwarsa, dibuat FROM undangan_masuk').get();
    const hari = (Date.parse(`${baris.kedaluwarsa}Z`) - Date.parse(`${baris.dibuat}Z`)) / 86_400_000;
    assert.ok(Math.abs(hari - UMUR_UNDANGAN_HARI) < 0.01, `umur tautan ${hari} hari, bukan ${UMUR_UNDANGAN_HARI}`);
  } finally {
    db.close();
  }
});

test('⛔ satpam dan penghuni TIDAK boleh membuat tautan masuk', () => {
  // Tautan masuk sama kuatnya dengan sandi orang lain. Satpam adalah admin gerbang, bukan pemilik warga;
  // penghuni yang bisa membuat tautan untuk orang lain berarti bisa menjadi orang lain.
  const { db, grup, bos, pakSatpam, ani } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(pakSatpam), grup.id, warga.id), /tidak berhak/i);
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(ani), grup.id, warga.id), /tidak berhak/i);
    // Bahkan untuk dirinya sendiri: penghuni yang sudah masuk tidak butuh tautan baru.
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(ani), grup.id, ani.id), /tidak berhak/i);
    assert.equal(db.prepare('SELECT count(*) AS n FROM undangan_masuk').get().n, 0);
  } finally {
    db.close();
  }
});

test('⛔ pengelola grup lain tidak bisa membuat tautan di grup ini', () => {
  const { db, grup, bos, bosLain } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(bosLain), grup.id, warga.id), /tidak ditemukan/i);
    assert.equal(db.prepare('SELECT count(*) AS n FROM undangan_masuk').get().n, 0);
  } finally {
    db.close();
  }
});

test('tautan hanya bisa dibuat untuk ANGGOTA grup itu', () => {
  const { db, grup, bos, bosLain } = siapkan();
  try {
    // bosLain punya akun, tetapi bukan anggota grup ini.
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(bos), grup.id, bosLain.id), /anggota/i);
    assert.throws(() => akses.buatUndanganMasuk(db, sesi(bos), grup.id, 9999), /anggota/i);
  } finally {
    db.close();
  }
});

test('tanpa sesi, tautan tidak bisa dibuat', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    assert.throws(() => akses.buatUndanganMasuk(db, undefined, grup.id, warga.id), /masuk dulu/i);
  } finally {
    db.close();
  }
});

// ─── Menukar tautan ─────────────────────────────────────────────────────────────────────────────────

test('menukar tautan memberi orang itu, tanpa perlu email atau kode apa pun', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);

    const hasil = akses.tukarUndanganMasuk(db, tanda);
    assert.equal(hasil.pengguna.id, warga.id);
    assert.equal(hasil.pengguna.nama, 'Pak Warga');
    assert.equal(hasil.grup.nama, 'RT 05 Contoh');
    assert.equal(hasil.peran, 'penghuni');
  } finally {
    db.close();
  }
});

test('⛔ tautan SEKALI PAKAI: pemakaian kedua ditolak', () => {
  // Pagar terpenting. Tautan dikirim lewat WhatsApp dan tinggal di riwayat obrolan; kalau ia bisa dipakai
  // berkali-kali, siapa pun yang kelak membaca obrolan itu bisa masuk sebagai orang tersebut.
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);

    akses.tukarUndanganMasuk(db, tanda);
    assert.throws(() => akses.tukarUndanganMasuk(db, tanda), /tidak berlaku/i);
    assert.throws(() => akses.tukarUndanganMasuk(db, tanda), /tidak berlaku/i, 'pemakaian ketiga pun harus ditolak');
  } finally {
    db.close();
  }
});

test('tautan kedaluwarsa ditolak', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    db.prepare("UPDATE undangan_masuk SET kedaluwarsa = datetime('now', '-1 second')").run();
    assert.throws(() => akses.tukarUndanganMasuk(db, tanda), /tidak berlaku/i);
  } finally {
    db.close();
  }
});

test('⛔ tanda palsu, bekas, dan kedaluwarsa memberi pesan yang SAMA', () => {
  // Pesan yang berbeda memberi tahu orang luar tanda mana yang pernah ada.
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    akses.tukarUndanganMasuk(db, tanda);

    const pesan = [];
    for (const coba of [tanda, 'tanda-karangan-yang-tidak-pernah-ada', '', undefined, null, 12345]) {
      try {
        akses.tukarUndanganMasuk(db, coba);
        assert.fail(`tanda ${JSON.stringify(coba)} seharusnya ditolak`);
      } catch (e) {
        pesan.push(e.message);
      }
    }
    assert.equal(new Set(pesan).size, 1, `pesan penolakan berbeda-beda: ${JSON.stringify([...new Set(pesan)])}`);
  } finally {
    db.close();
  }
});

test('⛔ tautan baru MEMATIKAN tautan lama untuk orang yang sama di grup yang sama', () => {
  // Inilah cara pengelola mencabut tautan yang salah kirim: ia membuat yang baru.
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const lama = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id).tanda;
    const baru = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id).tanda;
    assert.notEqual(lama, baru);

    assert.throws(() => akses.tukarUndanganMasuk(db, lama), /tidak berlaku/i,
      'tautan lama masih hidup: salah kirim tidak bisa dicabut');
    assert.equal(akses.tukarUndanganMasuk(db, baru).pengguna.id, warga.id);
  } finally {
    db.close();
  }
});

test('tautan untuk orang lain tidak terbawa saat tautan satu orang diperbarui', () => {
  const { db, grup, bos } = siapkan();
  try {
    const satu = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Satu' });
    const dua = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Dua' });
    const tandaSatu = akses.buatUndanganMasuk(db, sesi(bos), grup.id, satu.id).tanda;
    akses.buatUndanganMasuk(db, sesi(bos), grup.id, dua.id);
    akses.buatUndanganMasuk(db, sesi(bos), grup.id, dua.id);

    assert.equal(akses.tukarUndanganMasuk(db, tandaSatu).pengguna.id, satu.id,
      'tautan Warga Satu ikut mati saat tautan Warga Dua diperbarui');
  } finally {
    db.close();
  }
});

test('⛔ tautan milik orang yang dikeluarkan dari grup tidak berlaku lagi', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    akses.keluarkanAnggota(db, sesi(bos), grup.id, warga.id);
    assert.throws(() => akses.tukarUndanganMasuk(db, tanda), /tidak berlaku/i,
      'orang yang sudah dikeluarkan masih bisa masuk dengan tautan lamanya');
  } finally {
    db.close();
  }
});

test('tautan tidak membocorkan kode undangan grup', () => {
  // Kode undangan grup adalah cara masuk grup bagi siapa pun yang memegangnya. Ia hanya untuk pengelola.
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    const hasil = akses.tukarUndanganMasuk(db, tanda);
    assert.equal(hasil.grup.kode_undangan, undefined, 'kode undangan grup ikut keluar ke penghuni');
  } finally {
    db.close();
  }
});

test('pengelola bisa melihat siapa yang sudah dan belum memakai tautannya', () => {
  // Baris tautan bekas DISIMPAN dan ditandai, bukan dihapus. Alasannya praktis: pengurus RT perlu tahu warga
  // mana yang belum masuk, supaya ia menagihnya — tanpa ini ia hanya bisa menebak. Yang tersimpan hanyalah
  // nomor orang, nomor grup, dan jamnya; tidak ada plat dan tidak ada alamat baru (K71).
  const { db, grup, bos } = siapkan();
  try {
    const sudah = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Sudah' });
    const belum = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Belum' });
    const tanpaTautan = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Warga Tanpa' });

    akses.tukarUndanganMasuk(db, akses.buatUndanganMasuk(db, sesi(bos), grup.id, sudah.id).tanda);
    akses.buatUndanganMasuk(db, sesi(bos), grup.id, belum.id);

    const daftar = akses.anggotaGrup(db, sesi(bos), grup.id);
    const cari = (id) => daftar.find((a) => a.id === id).tautan_masuk;
    assert.equal(cari(sudah.id), 'sudah dipakai');
    assert.equal(cari(belum.id), 'menunggu dipakai');
    assert.equal(cari(tanpaTautan.id), null, 'anggota yang belum pernah dibuatkan tautan seharusnya kosong');
  } finally {
    db.close();
  }
});

test('⛔ tanda tautan tidak pernah ikut keluar lewat daftar anggota', () => {
  const { db, grup, bos } = siapkan();
  try {
    const warga = akses.tambahAnggota(db, sesi(bos), grup.id, { nama: 'Pak Warga' });
    const { tanda } = akses.buatUndanganMasuk(db, sesi(bos), grup.id, warga.id);
    const daftar = JSON.stringify(akses.anggotaGrup(db, sesi(bos), grup.id));
    assert.ok(!daftar.includes(tanda), 'tanda tautan ikut keluar: ia hanya boleh terlihat sekali saat dibuat');
    assert.ok(!daftar.includes('tanda_hash'), 'hash tanda pun tidak perlu keluar');
  } finally {
    db.close();
  }
});
