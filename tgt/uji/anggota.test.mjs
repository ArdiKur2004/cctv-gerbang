// Uji anggota yang dibuat pemilik akun, dan satpam sebagai admin TGT grupnya (Rencana T5 Task 2-3, K72).
//
// Semua email dan plat di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import { mintaOtp, masukDenganOtp } from '../akun.mjs';
import * as akses from '../akses.mjs';

const sesi = (orang) => ({ penggunaId: orang.id });

/** Buat akun lewat jalur OTP, seperti pengguna sungguhan. */
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

  const orangLuar = akunBaru(db, 'luar@example.test', 'Orang Luar');
  const lain = akses.buatGrup(db, sesi(orangLuar), { nama: 'Grup Lain', jenis: 'pribadi' });

  const gerbang = akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Gerbang Depan RT 05', jenisLokasi: 'perumahan',
    alamat: 'Jl. Contoh Asri 1', kota: 'Sidoarjo',
  });

  return { db, grup, grupLain: lain.grup, gerbang, bos, pakSatpam, ani, orangLuar };
}

// ─── Anggota dibuat pemilik akun (K72) ──────────────────────────────────────────────────────────────

test('pengelola membuat anggota cukup dengan email, dan anggotanya berperan penghuni', () => {
  const { db, grup, bos } = siapkan();
  try {
    const baru = akses.tambahAnggota(db, sesi(bos), grup.id, { email: 'Anak@Example.Test', nama: 'Anak Contoh' });
    assert.equal(baru.email, 'anak@example.test');
    assert.equal(baru.peran, 'penghuni');
    assert.ok(akses.anggotaGrup(db, sesi(bos), grup.id).some((a) => a.email === 'anak@example.test'));
  } finally {
    db.close();
  }
});

test('nama boleh kosong: yang wajib hanya emailnya', () => {
  const { db, grup, bos } = siapkan();
  try {
    const baru = akses.tambahAnggota(db, sesi(bos), grup.id, { email: 'tanpa.nama@example.test' });
    assert.ok(baru.nama, 'nama harus terisi sendiri, bukan kosong di layar');
  } finally {
    db.close();
  }
});

test('⛔ email yang SUDAH punya akun ditambahkan ke grup, bukan dibuatkan akun kedua', () => {
  // Satu orang bisa menjadi anggota beberapa grup (rumah sendiri dan kantor). Membuat akun kedua akan
  // memecah kendaraan dan tamunya ke dua akun yang tidak saling tahu.
  const { db, grupLain, orangLuar, ani } = siapkan();
  try {
    const sebelum = db.prepare('SELECT count(*) AS n FROM pengguna').get().n;
    const hasil = akses.tambahAnggota(db, sesi(orangLuar), grupLain.id, { email: 'ani@example.test' });

    assert.equal(hasil.id, ani.id, 'orang yang sama harus dipakai ulang');
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, sebelum, 'akun kedua terbuat');
    assert.equal(akses.grupSaya(db, sesi(ani)).length, 2, 'ia harus menjadi anggota dua grup');
  } finally {
    db.close();
  }
});

test('menambahkan orang yang sudah menjadi anggota tidak mengubah perannya', () => {
  const { db, grup, bos, pakSatpam } = siapkan();
  try {
    akses.tambahAnggota(db, sesi(bos), grup.id, { email: 'satpam@example.test' });
    const peran = akses.anggotaGrup(db, sesi(bos), grup.id).find((a) => a.id === pakSatpam.id).peran;
    assert.equal(peran, 'satpam', 'satpam turun menjadi penghuni hanya karena ditambahkan ulang');
  } finally {
    db.close();
  }
});

test('satpam dan penghuni TIDAK boleh membuat anggota', () => {
  const { db, grup, pakSatpam, ani } = siapkan();
  try {
    for (const orang of [pakSatpam, ani]) {
      assert.throws(
        () => akses.tambahAnggota(db, sesi(orang), grup.id, { email: 'baru@example.test' }),
        /tidak berhak/i,
      );
    }
    assert.equal(db.prepare("SELECT count(*) AS n FROM pengguna WHERE email = 'baru@example.test'").get().n, 0);
  } finally {
    db.close();
  }
});

test('pengelola grup lain tidak bisa menambah anggota ke grup ini', () => {
  const { db, grup, orangLuar } = siapkan();
  try {
    assert.throws(
      () => akses.tambahAnggota(db, sesi(orangLuar), grup.id, { email: 'baru@example.test' }),
      /tidak ditemukan/i,
    );
  } finally {
    db.close();
  }
});

test('anggota bisa dikeluarkan dari grup, tetapi akunnya tetap ada', () => {
  const { db, grup, bos, ani } = siapkan();
  try {
    akses.keluarkanAnggota(db, sesi(bos), grup.id, ani.id);
    assert.ok(!akses.anggotaGrup(db, sesi(bos), grup.id).some((a) => a.id === ani.id));
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna WHERE id = ?').get(ani.id).n, 1,
      'akun orangnya ikut terhapus; ia bisa jadi anggota grup lain');
  } finally {
    db.close();
  }
});

test('⛔ pengelola terakhir tidak bisa dikeluarkan: grup tidak boleh terkunci dari semua orang', () => {
  const { db, grup, bos } = siapkan();
  try {
    assert.throws(() => akses.keluarkanAnggota(db, sesi(bos), grup.id, bos.id), /pengelola/i);
    assert.ok(akses.anggotaGrup(db, sesi(bos), grup.id).some((a) => a.id === bos.id));
  } finally {
    db.close();
  }
});

test('satpam dan penghuni tidak boleh mengeluarkan anggota', () => {
  const { db, grup, pakSatpam, ani } = siapkan();
  try {
    for (const orang of [pakSatpam, ani]) {
      assert.throws(() => akses.keluarkanAnggota(db, sesi(orang), grup.id, ani.id), /tidak berhak/i);
    }
  } finally {
    db.close();
  }
});

// ─── Satpam sebagai admin TGT grupnya (K72) ─────────────────────────────────────────────────────────

test('satpam BOLEH mendaftarkan tamu beserta lama kunjungan dan alasannya (K72)', () => {
  // DIBALIK. Dulu ini ditolak 403, sesuai spec §4 yang ditulis sebelum K72. Owner mengoreksinya: satpam
  // adalah admin TGT grupnya, dan dialah yang di gerbang saat tamu datang tanpa diundang lebih dulu.
  const { db, gerbang, pakSatpam } = siapkan();
  try {
    const tamu = akses.tambahTamu(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, nama: 'Tamu Dadakan', keperluan: 'antar paket',
      jenis: 'pikap', plat: 'W 7777 QQ', lamaHari: 1,
    });
    assert.equal(tamu.plat, 'W7777QQ');
    assert.equal(tamu.lama_hari, 1);
    assert.equal(tamu.keperluan, 'antar paket');
    assert.equal(tamu.pengundang_id, pakSatpam.id, 'yang mendaftarkan harus tercatat');
  } finally {
    db.close();
  }
});

test('satpam melihat kode undangan tamu yang IA sendiri daftarkan', () => {
  const { db, gerbang, pakSatpam, ani } = siapkan();
  try {
    akses.tambahTamu(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, nama: 'Tamu Satpam', jenis: 'mobil', plat: 'W 1111 AA', lamaHari: 1,
    });
    akses.tambahTamu(db, sesi(ani), {
      gerbangId: gerbang.id, nama: 'Tamu Ani', jenis: 'mobil', plat: 'W 2222 BB', lamaHari: 1,
    });

    const terlihat = akses.tamuGerbang(db, sesi(pakSatpam), gerbang.id);
    const punyaSatpam = terlihat.find((t) => t.nama === 'Tamu Satpam');
    const punyaAni = terlihat.find((t) => t.nama === 'Tamu Ani');
    assert.ok(punyaSatpam.kode_undangan, 'satpam butuh kode tamu yang ia daftarkan sendiri');
    assert.equal(punyaAni.kode_undangan, undefined, 'kode tamu orang lain tetap bukan urusannya');
  } finally {
    db.close();
  }
});

test('⛔ satpam TETAP tidak boleh mengubah daftar kendaraan penghuni', () => {
  // Owner tidak memintanya, dan daftar izin penghuni adalah milik penghuni. Yang diperluas K72 hanya tamu.
  const { db, gerbang, pakSatpam, ani } = siapkan();
  try {
    const mobilAni = akses.tambahKendaraan(db, sesi(ani), {
      gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB',
    });
    assert.throws(
      () => akses.tambahKendaraan(db, sesi(pakSatpam), { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 9 Z' }),
      /tidak berhak/i,
    );
    assert.throws(() => akses.hapusKendaraan(db, sesi(pakSatpam), mobilAni.id), /tidak berhak/i);
  } finally {
    db.close();
  }
});

test('satpam boleh menghapus tamu yang ia daftarkan, tidak boleh menghapus tamu penghuni lain', () => {
  const { db, gerbang, pakSatpam, ani } = siapkan();
  try {
    const punyaSatpam = akses.tambahTamu(db, sesi(pakSatpam), {
      gerbangId: gerbang.id, nama: 'Tamu Satpam', jenis: 'mobil', plat: 'W 1111 AA', lamaHari: 1,
    });
    const punyaAni = akses.tambahTamu(db, sesi(ani), {
      gerbangId: gerbang.id, nama: 'Tamu Ani', jenis: 'mobil', plat: 'W 2222 BB', lamaHari: 1,
    });

    akses.hapusTamu(db, sesi(pakSatpam), punyaSatpam.id);
    assert.throws(() => akses.hapusTamu(db, sesi(pakSatpam), punyaAni.id), /tidak berhak|tidak ditemukan/i);
    assert.equal(akses.tamuGerbang(db, sesi(pakSatpam), gerbang.id).length, 1);
  } finally {
    db.close();
  }
});
