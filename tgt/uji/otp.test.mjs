// Uji masuk dengan email + OTP (Rencana T5 Task 1, keputusan owner K72).
//
// OTP adalah satu-satunya kunci akun sesudah sandi dicabut, jadi pagarnya diuji lengkap: umur pendek, sekali
// pakai, tersimpan ter-hash, dan jumlah percobaan dibatasi. Tanpa batas percobaan, enam angka bisa ditebak.
//
// Semua email di berkas ini KARANGAN.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import {
  normalkanEmail, mintaOtp, masukDenganOtp, UMUR_OTP_DETIK, MAKS_COBA_OTP,
} from '../akun.mjs';

/** Pengirim tiruan: menangkap OTP alih-alih mengirimnya ke mana pun. */
function penangkap() {
  const kotak = [];
  return { kotak, kirim: (email, kode) => kotak.push({ email, kode }) };
}

const EMAIL = 'Ani.Contoh@Example.Test';

// ─── Email ──────────────────────────────────────────────────────────────────────────────────────────

test('email dinormalkan: huruf besar-kecil dan spasi tidak membuat dua akun', () => {
  assert.equal(normalkanEmail('  Ani.Contoh@Example.Test '), 'ani.contoh@example.test');
  assert.equal(normalkanEmail('ANI.CONTOH@EXAMPLE.TEST'), 'ani.contoh@example.test');
});

test('email yang tidak masuk akal ditolak', () => {
  for (const e of ['', '   ', 'bukan-email', 'a@', '@b.test', 'a b@c.test', null, undefined]) {
    assert.throws(() => normalkanEmail(e), /email/i, `email ${JSON.stringify(e)} seharusnya ditolak`);
  }
});

// ─── Meminta OTP ────────────────────────────────────────────────────────────────────────────────────

test('OTP enam angka dan terkirim ke pengirim yang bisa diganti', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    assert.equal(p.kotak.length, 1);
    assert.equal(p.kotak[0].email, 'ani.contoh@example.test');
    assert.match(p.kotak[0].kode, /^\d{6}$/);
  } finally {
    db.close();
  }
});

test('⛔ OTP TIDAK pernah tersimpan apa adanya di basis data', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const baris = db.prepare('SELECT * FROM otp').all();
    assert.equal(baris.length, 1);
    const teks = JSON.stringify(baris[0]);
    assert.ok(!teks.includes(p.kotak[0].kode), 'OTP tersimpan apa adanya; siapa pun yang membaca basis bisa masuk');
  } finally {
    db.close();
  }
});

test('⛔ meminta OTP memberi jawaban yang SAMA untuk email terdaftar dan belum terdaftar', () => {
  // Jawaban yang berbeda memberi tahu orang luar alamat mana yang punya akun.
  const db = buka(':memory:');
  const p = penangkap();
  try {
    const baru = mintaOtp(db, { email: 'belum.ada@example.test', kirim: p.kirim });
    masukDenganOtp(db, { email: 'belum.ada@example.test', kode: p.kotak[0].kode, nama: 'Orang Baru' });
    const lama = mintaOtp(db, { email: 'belum.ada@example.test', kirim: p.kirim });
    assert.deepEqual(baru, lama, 'jawaban berbeda membocorkan siapa yang punya akun');
  } finally {
    db.close();
  }
});

test('meminta OTP baru membatalkan OTP lama', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const lama = p.kotak[0].kode;
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });

    assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode: lama }), /kode/i,
      'OTP lama masih bisa dipakai sesudah yang baru diminta');
    const baru = p.kotak[1].kode;
    assert.ok(masukDenganOtp(db, { email: EMAIL, kode: baru, nama: 'Ani Contoh' }).id);
  } finally {
    db.close();
  }
});

// ─── Memakai OTP ────────────────────────────────────────────────────────────────────────────────────

test('OTP benar membuat akun baru pada pemakaian pertama', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const orang = masukDenganOtp(db, { email: EMAIL, kode: p.kotak[0].kode, nama: 'Ani Contoh' });
    assert.equal(orang.email, 'ani.contoh@example.test');
    assert.equal(orang.nama, 'Ani Contoh');
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 1);
  } finally {
    db.close();
  }
});

test('OTP benar pada akun yang sudah ada tidak membuat akun kedua', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const pertama = masukDenganOtp(db, { email: EMAIL, kode: p.kotak[0].kode, nama: 'Ani Contoh' });
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const kedua = masukDenganOtp(db, { email: EMAIL, kode: p.kotak[1].kode });
    assert.equal(kedua.id, pertama.id);
    assert.equal(db.prepare('SELECT count(*) AS n FROM pengguna').get().n, 1);
  } finally {
    db.close();
  }
});

test('⛔ OTP hanya bisa dipakai SEKALI', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const kode = p.kotak[0].kode;
    masukDenganOtp(db, { email: EMAIL, kode, nama: 'Ani Contoh' });
    assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode }), /kode/i,
      'OTP yang sama bisa dipakai dua kali: siapa pun yang melihat sekilas bisa masuk belakangan');
  } finally {
    db.close();
  }
});

test('OTP salah ditolak, dan pesannya tidak menyebut benar-salahnya email', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    let pesanKodeSalah;
    let pesanEmailAsing;
    assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode: '000000' }), (e) => {
      pesanKodeSalah = e.message;
      return true;
    });
    assert.throws(() => masukDenganOtp(db, { email: 'tidak.ada@example.test', kode: '000000' }), (e) => {
      pesanEmailAsing = e.message;
      return true;
    });
    assert.equal(pesanKodeSalah, pesanEmailAsing);
  } finally {
    db.close();
  }
});

test('⛔ percobaan OTP dibatasi: enam angka tidak boleh bisa ditebak dengan mencoba terus', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    const benar = p.kotak[0].kode;

    for (let i = 0; i < MAKS_COBA_OTP; i += 1) {
      assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode: '000000' }), /kode/i);
    }
    // Sesudah batas tercapai, kode yang BENAR pun tidak berlaku lagi: kodenya hangus, minta yang baru.
    assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode: benar }), /kode/i,
      'kode masih berlaku sesudah dicoba berkali-kali; ia bisa ditebak');
  } finally {
    db.close();
  }
});

test('OTP kedaluwarsa ditolak', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    assert.ok(UMUR_OTP_DETIK > 0 && UMUR_OTP_DETIK <= 900, `umur OTP ${UMUR_OTP_DETIK} detik di luar dugaan`);
    mintaOtp(db, { email: EMAIL, kirim: p.kirim });
    // Majukan waktu dengan menuakan barisnya langsung, supaya uji tidak perlu menunggu.
    db.prepare(`UPDATE otp SET kedaluwarsa = datetime('now', '-1 second')`).run();
    assert.throws(() => masukDenganOtp(db, { email: EMAIL, kode: p.kotak[0].kode }), /kode/i);
  } finally {
    db.close();
  }
});

test('OTP kedaluwarsa dibersihkan saat ada permintaan baru', () => {
  const db = buka(':memory:');
  const p = penangkap();
  try {
    mintaOtp(db, { email: 'satu@example.test', kirim: p.kirim });
    mintaOtp(db, { email: 'dua@example.test', kirim: p.kirim });
    db.prepare(`UPDATE otp SET kedaluwarsa = datetime('now', '-1 hour')`).run();
    mintaOtp(db, { email: 'tiga@example.test', kirim: p.kirim });
    assert.equal(db.prepare('SELECT count(*) AS n FROM otp').get().n, 1,
      'OTP kedaluwarsa menumpuk; basis data ikut menyimpan email yang tidak perlu lagi (K71)');
  } finally {
    db.close();
  }
});

// ─── Pengirim bawaan ────────────────────────────────────────────────────────────────────────────────

test('⛔ pengirim bawaan TIDAK mengirim ke mana pun, dan itu terlihat jelas', () => {
  // Mengirim surel sungguhan butuh layanan berbayar = keputusan owner (CLAUDE.md §8). Sampai dibeli, OTP
  // hanya tercetak di layar server; yang berbahaya adalah kalau ini terlihat seperti sudah terkirim.
  const db = buka(':memory:');
  const dicetak = [];
  const asli = console.error;
  console.error = (...a) => dicetak.push(a.join(' '));
  try {
    mintaOtp(db, { email: EMAIL });
    const semua = dicetak.join('\n');
    assert.match(semua, /\d{6}/, 'OTP harus tercetak supaya bisa dipakai selama layanan surel belum ada');
    assert.match(semua, /belum|tidak terkirim|tanpa layanan/i, 'harus jelas bahwa surelnya tidak terkirim');
  } finally {
    console.error = asli;
    db.close();
  }
});
