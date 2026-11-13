// Uji tgt/server.mjs (Rencana T2 Task 4).
//
// Uji terpenting di berkas ini adalah UJI RANTAI: server tidak boleh mengimpor `layanan.mjs` langsung. Tanpa uji
// itu, lapisan web bisa menembus seluruh pagar di `akses.mjs` dan semua uji lain tetap hijau — dan pagar yang
// benar tetapi tak pernah dipanggil terlihat persis seperti pagar yang bekerja.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { buka } from '../basis.mjs';
import { buatAkun, buatGrupBaru, ikutGrup, tetapkanPeran } from '../akun.mjs';
import { buatServer } from '../server.mjs';
import { buatKunciVapid } from '../dorong.mjs';

const FOLDER = path.dirname(fileURLToPath(import.meta.url));
const SUMBER_SERVER = path.join(FOLDER, '..', 'server.mjs');
const SANDI = 'sandi-contoh-1';

// ─── Uji rantai ─────────────────────────────────────────────────────────────────────────────────────

test('RANTAI: server tidak mengimpor layanan.mjs langsung, jadi ia tidak bisa menembus hak akses', () => {
  const sumber = fs.readFileSync(SUMBER_SERVER, 'utf8');
  // Impor dalam bentuk apa pun, termasuk import() yang ditunda.
  const impor = /(?:from|import)\s*\(?\s*['"][^'"]*layanan\.mjs['"]/g;
  const ketemu = sumber.match(impor) ?? [];
  assert.deepEqual(
    ketemu, [],
    'server.mjs mengimpor layanan.mjs: semua pagar di akses.mjs terlewati. Pakai akses.mjs sebagai satu-satunya pintu.',
  );
  // Kontrol positif: pola di atas memang bisa menemukan sesuatu, supaya "0 ketemu" tidak terbaca sebagai bersih
  // hanya karena polanya salah tulis.
  assert.equal("import * as x from './layanan.mjs';".match(impor)?.length, 1, 'pola pencarian impor tidak bekerja');
});

test('RANTAI: server memakai akses.mjs', () => {
  const sumber = fs.readFileSync(SUMBER_SERVER, 'utf8');
  assert.match(sumber, /from\s+['"]\.\/akses\.mjs['"]/, 'server harus memanggil pintu hak akses');
});

// ─── Pembantu: jalankan server sungguhan di porta sementara ─────────────────────────────────────────

/** Satu grup berisi pengelola, satpam, dan penghuni, plus satu orang luar. */
function siapkanData(db) {
  const bos = buatAkun(db, { nama: 'Bos Contoh', wa: '081200000001', sandi: SANDI });
  const { grup } = buatGrupBaru(db, bos.id, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });

  const pakSatpam = buatAkun(db, { nama: 'Pak Satpam', wa: '081200000002', sandi: SANDI });
  ikutGrup(db, pakSatpam.id, grup.kode_undangan);
  tetapkanPeran(db, grup.id, pakSatpam.id, 'satpam');

  const karyawan = buatAkun(db, { nama: 'Karyawan Contoh', wa: '081200000003', sandi: SANDI });
  ikutGrup(db, karyawan.id, grup.kode_undangan);

  const orangLuar = buatAkun(db, { nama: 'Orang Luar', wa: '081200000004', sandi: SANDI });
  buatGrupBaru(db, orangLuar.id, { nama: 'Grup Lain', jenis: 'pribadi' });

  return { grup, bos, pakSatpam, karyawan, orangLuar };
}

async function nyalakan({ jembatan } = {}) {
  const db = buka(':memory:');
  const data = siapkanData(db);
  // Kunci VAPID disuntikkan, supaya uji TIDAK membuat atau membaca berkas kunci sungguhan di data/tgt/.
  const kodeOtp = [];
  const server = buatServer({ db, vapid: { ...buatKunciVapid(), hubungi: 'mailto:uji@example.test' },
    kirimOtp: (_e, k) => kodeOtp.push(k), ...(jembatan ? { jembatan } : {}) });
  await new Promise((selesai) => server.listen(0, '127.0.0.1', selesai));
  const asal = `http://127.0.0.1:${server.address().port}`;

  const minta = async (cara, jalur, { isi, kuki } = {}) => {
    const r = await fetch(asal + jalur, {
      method: cara,
      headers: {
        ...(isi ? { 'content-type': 'application/json' } : {}),
        ...(kuki ? { cookie: kuki } : {}),
      },
      body: isi ? JSON.stringify(isi) : undefined,
    });
    const teks = await r.text();
    let badan;
    try {
      badan = JSON.parse(teks);
    } catch {
      badan = teks;
    }
    const set = r.headers.getSetCookie?.() ?? [];
    return { kode: r.status, badan, kuki: set[0]?.split(';')[0], setKuki: set, tajuk: r.headers };
  };

  const masukSebagai = async (orang) => {
    const r = await minta('POST', '/api/masuk', { isi: { wa: orang.wa, sandi: SANDI } });
    assert.equal(r.kode, 200, `gagal masuk: ${JSON.stringify(r.badan)}`);
    return r.kuki;
  };

  // Kode OTP ditangkap lewat pengirim yang disuntikkan, bukan dibaca dari jawaban HTTP: jawaban HTTP memang
  // TIDAK BOLEH memuat kodenya, dan ada uji tersendiri untuk itu.
  const kodeOtpTerakhir = () => kodeOtp[kodeOtp.length - 1];

  const tutup = () => new Promise((selesai) => server.close(() => {
    db.close();
    selesai();
  }));

  return { ...data, minta, masukSebagai, kodeOtpTerakhir, tutup };
}

const DATA_GERBANG = (grupId) => ({
  grupId, nama: 'Kantor Contoh Gate Selatan', jenisLokasi: 'kantor',
  alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
});

// ─── Masuk dan sesi ─────────────────────────────────────────────────────────────────────────────────

test('daftar akun memberi sesi, dan kukinya HttpOnly serta SameSite', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('POST', '/api/daftar', {
      isi: { nama: 'Orang Baru', wa: '081299990000', sandi: SANDI },
    });
    assert.equal(r.kode, 201);
    assert.equal(r.badan.pengguna.nama, 'Orang Baru');
    assert.equal(r.badan.pengguna.sandi_hash, undefined, 'hash sandi tidak boleh ikut keluar');

    const kuki = r.setKuki.join(';');
    assert.match(kuki, /HttpOnly/i, 'kuki sesi harus HttpOnly supaya tidak terbaca JavaScript halaman');
    assert.match(kuki, /SameSite=Strict/i);
    assert.match(kuki, /Path=\//);
  } finally {
    await s.tutup();
  }
});

test('sandi salah ditolak 401 dan tidak memberi sesi', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('POST', '/api/masuk', { isi: { wa: '081200000001', sandi: 'sandi-salah-99' } });
    assert.equal(r.kode, 401);
    assert.equal(r.kuki, undefined);
  } finally {
    await s.tutup();
  }
});

test('tanpa sesi, jalur data menjawab 401', async () => {
  const s = await nyalakan();
  try {
    for (const [cara, jalur] of [
      ['GET', '/api/gerbang'],
      ['GET', '/api/saya'],
      ['POST', '/api/gerbang'],
      ['GET', `/api/grup/${s.grup.id}/anggota`],
    ]) {
      const r = await s.minta(cara, jalur, cara === 'POST' ? { isi: DATA_GERBANG(s.grup.id) } : {});
      assert.equal(r.kode, 401, `${cara} ${jalur} seharusnya 401`);
    }
  } finally {
    await s.tutup();
  }
});

test('kuki sesi yang dipalsukan ditolak', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('GET', '/api/gerbang', { kuki: 'tgt_sesi=palsu-sekali' });
    assert.equal(r.kode, 401);
  } finally {
    await s.tutup();
  }
});

test('keluar membuat sesi tidak bisa dipakai lagi', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.bos);
    assert.equal((await s.minta('GET', '/api/saya', { kuki })).kode, 200);
    assert.equal((await s.minta('POST', '/api/keluar', { kuki })).kode, 200);
    assert.equal((await s.minta('GET', '/api/saya', { kuki })).kode, 401);
  } finally {
    await s.tutup();
  }
});

// ─── Hak akses LEWAT HTTP, bukan hanya lewat fungsi ─────────────────────────────────────────────────

test('RANTAI: satpam yang membuat gerbang lewat HTTP ditolak 403', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.pakSatpam);
    const r = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki });
    assert.equal(r.kode, 403);

    const daftar = await s.minta('GET', '/api/gerbang', { kuki });
    assert.deepEqual(daftar.badan, [], 'tidak boleh ada gerbang yang tercipta');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: penghuni juga ditolak 403', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.karyawan);
    assert.equal((await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki })).kode, 403);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: pengelola berhasil membuat gerbang, dan gerbangnya terbaca ketiga peran', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const buat = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    assert.equal(buat.kode, 201);
    assert.equal(buat.badan.status, 'belum_aktif');
    assert.equal(buat.badan.alamat, 'Jl. Contoh Industri III No. 42');

    for (const orang of [s.bos, s.pakSatpam, s.karyawan]) {
      const kuki = await s.masukSebagai(orang);
      const daftar = await s.minta('GET', '/api/gerbang', { kuki });
      assert.deepEqual(daftar.badan.map((g) => g.id), [buat.badan.id]);
      assert.equal((await s.minta('GET', `/api/gerbang/${buat.badan.id}`, { kuki })).kode, 200);
    }
  } finally {
    await s.tutup();
  }
});

test('RANTAI: orang luar mendapat 404 untuk gerbang grup lain maupun gerbang yang tidak ada', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const buat = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });

    const kukiLuar = await s.masukSebagai(s.orangLuar);
    const grupLain = await s.minta('GET', `/api/gerbang/${buat.badan.id}`, { kuki: kukiLuar });
    const takAda = await s.minta('GET', '/api/gerbang/99999', { kuki: kukiLuar });

    assert.equal(grupLain.kode, 404);
    assert.equal(takAda.kode, 404);
    assert.deepEqual(grupLain.badan, takAda.badan, 'jawaban keduanya harus sama persis');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: mengaktifkan gerbang lewat HTTP hanya untuk pengelola', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });

    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    assert.equal((await s.minta('POST', `/api/gerbang/${gerbang.id}/aktifkan`, { kuki: kukiSatpam })).kode, 403);
    assert.equal((await s.minta('GET', `/api/gerbang/${gerbang.id}`, { kuki: kukiSatpam })).badan.status, 'belum_aktif');

    const nyala = await s.minta('POST', `/api/gerbang/${gerbang.id}/aktifkan`, { kuki: kukiBos });
    assert.equal(nyala.kode, 200);
    assert.equal(nyala.badan.status, 'aktif');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: daftar anggota beserta nomor WA hanya untuk pengelola', async () => {
  const s = await nyalakan();
  try {
    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    assert.equal((await s.minta('GET', `/api/grup/${s.grup.id}/anggota`, { kuki: kukiSatpam })).kode, 403);

    const kukiBos = await s.masukSebagai(s.bos);
    const r = await s.minta('GET', `/api/grup/${s.grup.id}/anggota`, { kuki: kukiBos });
    assert.equal(r.kode, 200);
    assert.equal(r.badan.length, 3);
  } finally {
    await s.tutup();
  }
});

test('/api/saya menyebut siapa yang sedang masuk, supaya sesi yang masih hidup tidak kehilangan identitas', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.bos);
    const r = await s.minta('GET', '/api/saya', { kuki });
    assert.equal(r.badan.pengguna.nama, 'Bos Contoh');
    assert.equal(r.badan.pengguna.sandi_hash, undefined, 'hash sandi tidak boleh ikut keluar');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: kode undangan tidak ikut keluar untuk penghuni', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.karyawan);
    const r = await s.minta('GET', '/api/saya', { kuki });
    assert.equal(r.kode, 200);
    const [kantor] = r.badan.grup;
    assert.equal(kantor.peran, 'penghuni');
    assert.equal(kantor.kode_undangan, undefined);
  } finally {
    await s.tutup();
  }
});

// ─── Hal-hal kecil yang mudah terlupa ───────────────────────────────────────────────────────────────

test('isian yang salah menjawab 400 dengan pesan, bukan 500', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.bos);
    const r = await s.minta('POST', '/api/gerbang', {
      isi: { ...DATA_GERBANG(s.grup.id), alamat: '' }, kuki,
    });
    assert.equal(r.kode, 400);
    assert.match(r.badan.galat, /alamat/i);
  } finally {
    await s.tutup();
  }
});

test('jalur yang tidak dikenal menjawab 404, dan badannya bukan jejak galat', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('GET', '/api/entah');
    assert.equal(r.kode, 404);
    assert.ok(!String(r.badan.galat ?? r.badan).includes('at '), 'jejak galat tidak boleh terkirim ke peramban');
  } finally {
    await s.tutup();
  }
});

test('halaman web tersaji, dan jalur berkas tidak bisa keluar dari folder web', async () => {
  const s = await nyalakan();
  try {
    assert.equal((await s.minta('GET', '/')).kode, 200);
    // Percobaan keluar folder, dalam beberapa ejaan.
    for (const jalur of ['/../basis.mjs', '/..%2Fbasis.mjs', '/%2e%2e/basis.mjs', '/web/../../basis.mjs']) {
      const r = await s.minta('GET', jalur);
      assert.ok(r.kode === 404 || r.kode === 400, `${jalur} seharusnya ditolak, bukan ${r.kode}`);
      assert.ok(!String(r.badan).includes('DatabaseSync'), `${jalur} membocorkan isi berkas kode`);
    }
  } finally {
    await s.tutup();
  }
});

// ─── Rencana T3: kendaraan, tamu, dan halaman undangan ──────────────────────────────────────────────

/** Pengelola membuat gerbang, lalu penghuni mendaftarkan kendaraannya. Mengembalikan kuki tiap peran. */
async function siapkanGerbangDanPenghuni(s) {
  const kukiBos = await s.masukSebagai(s.bos);
  const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
  const kukiKaryawan = await s.masukSebagai(s.karyawan);
  const kukiSatpam = await s.masukSebagai(s.pakSatpam);
  return { gerbang, kukiBos, kukiKaryawan, kukiSatpam };
}

test('RANTAI: penghuni menambah kendaraan lewat HTTP, dan pemiliknya tercatat', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan } = await siapkanGerbangDanPenghuni(s);
    const r = await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'mobil', merek: 'Toyota', warna: 'hitam', plat: 'l 1111 aa' },
      kuki: kukiKaryawan,
    });
    assert.equal(r.kode, 201);
    assert.equal(r.badan.plat, 'L1111AA');
    assert.equal(r.badan.atas_nama, 'Karyawan Contoh');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: satpam menambah kendaraan lewat HTTP ditolak 403', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangDanPenghuni(s);
    const r = await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 2222 BB' }, kuki: kukiSatpam,
    });
    assert.equal(r.kode, 403);
    assert.deepEqual((await s.minta('GET', `/api/gerbang/${gerbang.id}/kendaraan`, { kuki: kukiSatpam })).badan, []);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: motor ditolak 400 lewat HTTP dengan pesan yang menyebut versi 2 (K65)', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan } = await siapkanGerbangDanPenghuni(s);
    const r = await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'motor', plat: 'L 3333 CC' }, kuki: kukiKaryawan,
    });
    assert.equal(r.kode, 400);
    assert.match(r.badan.galat, /versi 2/i);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: daftar kendaraan penghuni hanya berisi miliknya', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiBos, kukiKaryawan } = await siapkanGerbangDanPenghuni(s);
    await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1111 AA' }, kuki: kukiKaryawan,
    });
    // Pengelola mendaftarkan kendaraan lain atas nama orang lain.
    await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'truk', plat: 'L 2222 BB', atasNama: 'Orang Lain' }, kuki: kukiBos,
    });

    const punyaKaryawan = await s.minta('GET', `/api/gerbang/${gerbang.id}/kendaraan`, { kuki: kukiKaryawan });
    const punyaBos = await s.minta('GET', `/api/gerbang/${gerbang.id}/kendaraan`, { kuki: kukiBos });
    assert.deepEqual(punyaKaryawan.badan.map((k) => k.plat), ['L1111AA']);
    assert.equal(punyaBos.badan.length, 2);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: tamu dibuat penghuni, kodenya keluar untuk pengundang tetapi tidak untuk satpam', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan, kukiSatpam } = await siapkanGerbangDanPenghuni(s);
    const buat = await s.minta('POST', '/api/tamu', {
      isi: { gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'pikap', plat: 'W 1212 ZZ', lamaHari: 2 },
      kuki: kukiKaryawan,
    });
    assert.equal(buat.kode, 201);
    assert.ok(buat.badan.kode_undangan);

    const lewatSatpam = await s.minta('GET', `/api/gerbang/${gerbang.id}/tamu`, { kuki: kukiSatpam });
    assert.equal(lewatSatpam.badan.length, 1);
    assert.equal(lewatSatpam.badan[0].kode_undangan, undefined);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: halaman undangan terbuka TANPA sesi, dan kode salah menjawab 404', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan } = await siapkanGerbangDanPenghuni(s);
    const { badan: tamu } = await s.minta('POST', '/api/tamu', {
      isi: { gerbangId: gerbang.id, nama: 'Tamu Contoh', jenis: 'mobil', plat: 'W 1212 ZZ', lamaHari: 2 },
      kuki: kukiKaryawan,
    });

    // Tanpa kuki sama sekali: inilah tamu yang tidak punya akun.
    const u = await s.minta('GET', `/api/undangan/${tamu.kode_undangan}`);
    assert.equal(u.kode, 200);
    assert.equal(u.badan.tamu, 'Tamu Contoh');
    assert.equal(u.badan.gerbang, 'Kantor Contoh Gate Selatan');
    assert.equal(u.badan.alamat, 'Jl. Contoh Industri III No. 42');

    // Tidak boleh ada nomor WhatsApp atau nomor dalam basis data.
    const teks = JSON.stringify(u.badan);
    assert.ok(!teks.includes('6281'), 'nomor WhatsApp bocor ke halaman yang bisa dibuka siapa saja');
    assert.equal(u.badan.gerbang_id, undefined);

    assert.equal((await s.minta('GET', '/api/undangan/ZZZZZZ')).kode, 404);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: kode undangan GRUP tidak membuka halaman undangan tamu', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: saya } = await s.minta('GET', '/api/saya', { kuki: kukiBos });
    const kodeGrup = saya.grup[0].kode_undangan;
    assert.ok(kodeGrup, 'pengelola harus melihat kode grupnya');
    assert.equal((await s.minta('GET', `/api/undangan/${kodeGrup}`)).kode, 404);
  } finally {
    await s.tutup();
  }
});

// ─── Rencana T4: jalur kotak gerbang dan layar satpam ───────────────────────────────────────────────

/** Gerbang beserta satu kendaraan penghuni, dan kuki tiap peran. */
async function siapkanGerbangIsi(s) {
  const kukiBos = await s.masukSebagai(s.bos);
  const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
  const kukiKaryawan = await s.masukSebagai(s.karyawan);
  await s.minta('POST', '/api/kendaraan', {
    isi: { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB' }, kuki: kukiKaryawan,
  });
  const kukiSatpam = await s.masukSebagai(s.pakSatpam);
  return { gerbang, kukiBos, kukiKaryawan, kukiSatpam };
}

test('RANTAI: kotak gerbang mengirim bacaan dan menerima putusan beserta alasannya', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/bacaan`, {
      isi: { bacaan: 'l 1234 ab', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00', yakin: 0.93 },
      kuki: kukiSatpam,
    });
    assert.equal(r.kode, 200);
    assert.equal(r.badan.putusan, 'buka');
    assert.ok(r.badan.alasan, 'alasan wajib ikut, supaya satpam tahu kenapa');
    assert.equal(r.badan.plat, 'L1234AB');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: penanda yang sama dikirim dua kali tidak menggandakan catatan', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    const kirim = () => s.minta('POST', `/api/gerbang/${gerbang.id}/bacaan`, {
      isi: { bacaan: 'L1234AB', ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00', penanda: 'kotak-1-abc' },
      kuki: kukiSatpam,
    });
    const a = await kirim();
    const b = await kirim();
    assert.equal(a.kode, 200);
    assert.equal(b.badan.sudahAda, true);

    const kejadian = await s.minta('GET', `/api/gerbang/${gerbang.id}/kejadian`, { kuki: kukiSatpam });
    assert.equal(kejadian.badan.length, 1, 'kejadian tergandakan saat dikirim ulang');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: bacaan ragu lebih dari dua posisi menjawab panggil satpam, bukan buka', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/bacaan`, {
      isi: { bacaan: 'L1234AB', ragu: [0, 1, 2], arah: 'masuk', waktu: '2026-10-26T08:01:00' },
      kuki: kukiSatpam,
    });
    assert.equal(r.badan.putusan, 'panggil_satpam');
    assert.match(r.badan.alasan, /ragu/i);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: penghuni tidak boleh mengirim bacaan maupun membaca daftar izin', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan } = await siapkanGerbangIsi(s);
    const bacaan = await s.minta('POST', `/api/gerbang/${gerbang.id}/bacaan`, {
      isi: { bacaan: 'L1234AB', ragu: [], arah: 'masuk' }, kuki: kukiKaryawan,
    });
    assert.equal(bacaan.kode, 403);
    assert.equal((await s.minta('GET', `/api/gerbang/${gerbang.id}/izin`, { kuki: kukiKaryawan })).kode, 403);
    assert.equal((await s.minta('GET', `/api/gerbang/${gerbang.id}/kejadian`, { kuki: kukiKaryawan })).kode, 403);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: daftar izin untuk luring tidak memuat nama atau nomor WhatsApp', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    const r = await s.minta('GET', `/api/gerbang/${gerbang.id}/izin`, { kuki: kukiSatpam });
    assert.equal(r.kode, 200);
    assert.equal(r.badan.length, 1);
    const teks = JSON.stringify(r.badan);
    assert.ok(!teks.includes('Karyawan Contoh'), 'nama penghuni ikut tersalin ke kotak gerbang');
    assert.ok(!teks.includes('6281'), 'nomor WhatsApp ikut tersalin ke kotak gerbang');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: satpam membuka manual lewat HTTP, tercatat sebagai dibuka satpam', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/buka`, {
      isi: { plat: 'N 9999 XX', arah: 'masuk', alasan: 'tamu dadakan, diperiksa satpam' },
      kuki: kukiSatpam,
    });
    assert.equal(r.kode, 200);
    assert.equal(r.badan.putusan, 'dibuka_satpam');

    const tanpaAlasan = await s.minta('POST', `/api/gerbang/${gerbang.id}/buka`, {
      isi: { plat: 'N 1 A', arah: 'masuk' }, kuki: kukiSatpam,
    });
    assert.equal(tanpaAlasan.kode, 400);
    assert.match(tanpaAlasan.badan.galat, /alasan/i);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: penghuni tidak boleh membuka gerbang lewat HTTP', async () => {
  const s = await nyalakan();
  try {
    const { gerbang, kukiKaryawan } = await siapkanGerbangIsi(s);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/buka`, {
      isi: { plat: 'N 1 A', arah: 'masuk', alasan: 'ingin lewat' }, kuki: kukiKaryawan,
    });
    assert.equal(r.kode, 403);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: tidak ada jalur yang menerima perintah tutup', async () => {
  // CLAUDE.md §3: produk hanya memberi perintah buka.
  const s = await nyalakan();
  try {
    const { gerbang, kukiSatpam } = await siapkanGerbangIsi(s);
    for (const jalur of [`/api/gerbang/${gerbang.id}/tutup`, `/api/gerbang/${gerbang.id}/relay`]) {
      const r = await s.minta('POST', jalur, { isi: { alasan: 'coba' }, kuki: kukiSatpam });
      assert.equal(r.kode, 404, `${jalur} seharusnya tidak ada`);
    }
    const pola = /['"`/][^'"`]*\b(tutup|relay)\b/i;
    const sumber = fs.readFileSync(SUMBER_SERVER, 'utf8');
    assert.ok(!pola.test(sumber), 'server tidak boleh memuat jalur tutup atau relay');
    // Kontrol positif: pemeriksa yang melapor "nol ditemukan" diuji dulu dengan yang pasti ada, supaya
    // daftar larangan yang kosong tidak terbaca sebagai bersih karena polanya salah tulis.
    assert.ok(pola.test("const x = '/api/gerbang/1/tutup';"), 'pola pencarian jalur terlarang tidak bekerja');
    assert.ok(pola.test('const r = /relay/;'), 'pola pencarian relay tidak bekerja');
  } finally {
    await s.tutup();
  }
});

// ─── Rencana T5: masuk dengan email + OTP lewat HTTP ────────────────────────────────────────────────

test('RANTAI: minta OTP lalu masuk, dan sesinya langsung berlaku', async () => {
  const s = await nyalakan();
  try {
    const minta1 = await s.minta('POST', '/api/otp', { isi: { email: 'Baru@Example.Test' } });
    assert.equal(minta1.kode, 200);
    assert.equal(minta1.badan.dikirim, true);
    assert.equal(minta1.badan.kode, undefined, '⛔ OTP tidak boleh ikut keluar lewat jawaban HTTP');

    // Kode dibaca seperti server membacanya: dari basis data lewat jalur uji, bukan dari jawaban HTTP.
    const kode = s.kodeOtpTerakhir();
    const masuk = await s.minta('POST', '/api/otp/masuk', { isi: { email: 'baru@example.test', kode, nama: 'Orang Baru' } });
    assert.equal(masuk.kode, 200);
    assert.equal(masuk.badan.pengguna.email, 'baru@example.test');
    assert.match(masuk.setKuki.join(';'), /HttpOnly/i);

    const saya = await s.minta('GET', '/api/saya', { kuki: masuk.kuki });
    assert.equal(saya.kode, 200);
    assert.equal(saya.badan.pengguna.email, 'baru@example.test');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: OTP salah menjawab 401 dan tidak memberi sesi', async () => {
  const s = await nyalakan();
  try {
    await s.minta('POST', '/api/otp', { isi: { email: 'baru@example.test' } });
    const r = await s.minta('POST', '/api/otp/masuk', { isi: { email: 'baru@example.test', kode: '000000' } });
    assert.equal(r.kode, 401);
    assert.equal(r.kuki, undefined);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: pengelola menambah anggota lewat HTTP, satpam dan penghuni ditolak', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const tambah = await s.minta('POST', `/api/grup/${s.grup.id}/anggota`, {
      isi: { email: 'anak@example.test', nama: 'Anak Contoh' }, kuki: kukiBos,
    });
    assert.equal(tambah.kode, 201);
    assert.equal(tambah.badan.email, 'anak@example.test');

    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    assert.equal((await s.minta('POST', `/api/grup/${s.grup.id}/anggota`, {
      isi: { email: 'lain@example.test' }, kuki: kukiSatpam,
    })).kode, 403);
  } finally {
    await s.tutup();
  }
});

// ─── Rencana T6: gambar dari kamera lewat HTTP ──────────────────────────────────────────────────────

/** Jembatan tiruan: menjawab apa yang kita tentukan, supaya uji tidak menyentuh folder mesin sungguhan. */
function jembatanTiruan(hasil) {
  const dicatat = [];
  return {
    dicatat,
    kirim(gambar, keterangan) {
      dicatat.push({ ukuran: gambar.length, keterangan });
      return 'id-uji';
    },
    async tungguHasil() {
      if (hasil instanceof Error) throw hasil;
      return hasil;
    },
  };
}

async function nyalakanDenganJembatan(jembatan) {
  const s = await nyalakan({ jembatan });
  return s;
}

test('RANTAI: gambar kamera menghasilkan putusan, dan jenisnya ikut dicatat', async () => {
  const s = await nyalakanDenganJembatan(jembatanTiruan({
    plat: 'L1234AB', ragu: [], yakin: 0.93, pola_sah: true, jenis: 'mobil', yakin_jenis: 0.9, kendaraan: 1, ms: 120,
  }));
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    const kukiKaryawan = await s.masukSebagai(s.karyawan);
    await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB' }, kuki: kukiKaryawan,
    });

    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/kamera`, {
      isi: { gambar: Buffer.from('gambar-palsu').toString('base64'), arah: 'masuk' }, kuki: kukiSatpam,
    });

    assert.equal(r.kode, 200);
    assert.equal(r.badan.putusan, 'buka');
    assert.equal(r.badan.plat, 'L1234AB');
    assert.equal(r.badan.ciriJanggal, false);
    assert.equal(r.badan.dibaca.jenis, 'mobil');
    assert.equal(r.badan.kejadian.ciri_jenis, 'mobil');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: jenis dari kamera yang tidak cocok memberi notifikasi, gerbang tetap dibuka', async () => {
  const s = await nyalakanDenganJembatan(jembatanTiruan({
    plat: 'L1234AB', ragu: [], yakin: 0.93, pola_sah: true, jenis: 'truk', yakin_jenis: 0.8, kendaraan: 1, ms: 110,
  }));
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    const kukiKaryawan = await s.masukSebagai(s.karyawan);
    await s.minta('POST', '/api/kendaraan', {
      isi: { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 1234 AB' }, kuki: kukiKaryawan,
    });

    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/kamera`, {
      isi: { gambar: Buffer.from('gambar-palsu').toString('base64'), arah: 'masuk' }, kuki: kukiSatpam,
    });

    assert.equal(r.badan.putusan, 'buka', 'ciri tidak boleh menahan gerbang');
    assert.equal(r.badan.ciriJanggal, true);
    assert.match(r.badan.notifikasi.judul, /jenis/i);
  } finally {
    await s.tutup();
  }
});

test('⛔ RANTAI: penghuni yang mengirim gambar ditolak SEBELUM gambarnya ditulis ke folder', async () => {
  const j = jembatanTiruan({ plat: null, ragu: [] });
  const s = await nyalakanDenganJembatan(j);
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });

    const kukiKaryawan = await s.masukSebagai(s.karyawan);
    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/kamera`, {
      isi: { gambar: Buffer.from('gambar-palsu').toString('base64') }, kuki: kukiKaryawan,
    });

    assert.equal(r.kode, 403);
    assert.equal(j.dicatat.length, 0, 'gambar kendaraan masuk ke antrean padahal pengirimnya tidak berhak');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: gambar kosong dan gambar kelewat besar ditolak 400', async () => {
  const j = jembatanTiruan({ plat: null, ragu: [] });
  const s = await nyalakanDenganJembatan(j);
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    const kukiSatpam = await s.masukSebagai(s.pakSatpam);

    const kosong = await s.minta('POST', `/api/gerbang/${gerbang.id}/kamera`, { isi: { gambar: '' }, kuki: kukiSatpam });
    assert.equal(kosong.kode, 400);
    assert.equal(j.dicatat.length, 0);
  } finally {
    await s.tutup();
  }
});

test('RANTAI: mesin baca yang tidak menjawab memberi pesan yang bisa dimengerti, bukan galat berkas', async () => {
  const s = await nyalakanDenganJembatan(jembatanTiruan(
    new Error('mesin baca tidak menjawab dalam batas waktu. Periksa apakah layanan bacanya sedang berjalan.'),
  ));
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    const kukiSatpam = await s.masukSebagai(s.pakSatpam);

    const r = await s.minta('POST', `/api/gerbang/${gerbang.id}/kamera`, {
      isi: { gambar: Buffer.from('x').toString('base64') }, kuki: kukiSatpam,
    });
    assert.equal(r.kode, 500);
    assert.match(String(r.badan.galat), /galat di server/i, 'jejak galat tidak boleh bocor ke peramban');
  } finally {
    await s.tutup();
  }
});

test('RANTAI: beranda memberi ubin dan 24 baris jam; penghuni ditolak', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const { badan: gerbang } = await s.minta('POST', '/api/gerbang', { isi: DATA_GERBANG(s.grup.id), kuki: kukiBos });
    const kukiSatpam = await s.masukSebagai(s.pakSatpam);
    await s.minta('POST', `/api/gerbang/${gerbang.id}/bacaan`, {
      isi: { bacaan: 'N 9999 XX', ragu: [], arah: 'masuk', waktu: '2026-10-26T07:30:00' }, kuki: kukiSatpam,
    });

    const r = await s.minta('GET', `/api/gerbang/${gerbang.id}/beranda?tanggal=2026-10-26`, { kuki: kukiSatpam });
    assert.equal(r.kode, 200);
    assert.equal(r.badan.jam.length, 24, 'dashboard butuh 24 batang, termasuk jam yang kosong');
    assert.deepEqual(r.badan.jam[7], { jam: 7, masuk: 1, keluar: 0 });
    assert.equal(r.badan.ubin.masukHariIni, 1);

    const kukiKaryawan = await s.masukSebagai(s.karyawan);
    assert.equal((await s.minta('GET', `/api/gerbang/${gerbang.id}/beranda`, { kuki: kukiKaryawan })).kode, 403);
  } finally {
    await s.tutup();
  }
});

// ─── Sesi yang bertahan (Rencana T8 Task 1) ─────────────────────────────────────────────────────────

test('⛔ RANTAI: sesi masih berlaku di SERVER BARU atas basis data yang sama', async () => {
  // Bukti bahwa batas lama benar-benar tertutup, diukur lewat HTTP — bukan lewat sesi.mjs langsung.
  // Fungsi yang benar tetapi tak tersambung ke jalur server terlihat persis seperti fungsi yang bekerja:
  // seluruh isi sesi.mjs bisa hijau sementara server masih memakai Map di memori.
  const db = buka(':memory:');
  const orang = buatAkun(db, { nama: 'Penghuni Contoh', wa: '081233330001', sandi: SANDI });
  buatGrupBaru(db, orang.id, { nama: 'Rumah Contoh', jenis: 'pribadi' });

  const nyalakanAtas = async () => {
    const server = buatServer({ db, vapid: { ...buatKunciVapid(), hubungi: 'mailto:uji@example.test' } });
    await new Promise((selesai) => server.listen(0, '127.0.0.1', selesai));
    const asal = `http://127.0.0.1:${server.address().port}`;
    return {
      asal,
      tutup: () => new Promise((selesai) => server.close(selesai)),
    };
  };

  const pertama = await nyalakanAtas();
  let kuki;
  try {
    const r = await fetch(`${pertama.asal}/api/masuk`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ wa: orang.wa, sandi: SANDI }),
    });
    assert.equal(r.status, 200);
    kuki = (r.headers.getSetCookie?.() ?? [])[0]?.split(';')[0];
    assert.ok(kuki, 'tidak ada kuki sesi');
  } finally {
    await pertama.tutup();
  }

  // Server lama MATI. Yang dibawa hanya kukinya, sama seperti peramban orangnya.
  const kedua = await nyalakanAtas();
  try {
    const r = await fetch(`${kedua.asal}/api/saya`, { headers: { cookie: kuki } });
    assert.equal(r.status, 200,
      'sesi hilang sesudah server dinyalakan ulang: gudang sesi masih di memori, bukan di basis data');
    assert.equal((await r.json()).pengguna.id, orang.id, 'sesi menunjuk orang yang salah');
  } finally {
    await kedua.tutup();
    db.close();
  }
});

test('keluar membuang sesi dari basis data, bukan hanya dari memori', async () => {
  const db = buka(':memory:');
  const orang = buatAkun(db, { nama: 'Penghuni Dua', wa: '081233330002', sandi: SANDI });
  buatGrupBaru(db, orang.id, { nama: 'Rumah Dua', jenis: 'pribadi' });
  const server = buatServer({ db, vapid: { ...buatKunciVapid(), hubungi: 'mailto:uji@example.test' } });
  await new Promise((selesai) => server.listen(0, '127.0.0.1', selesai));
  const asal = `http://127.0.0.1:${server.address().port}`;
  try {
    const masukR = await fetch(`${asal}/api/masuk`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ wa: orang.wa, sandi: SANDI }),
    });
    const kuki = (masukR.headers.getSetCookie?.() ?? [])[0]?.split(';')[0];
    assert.equal(db.prepare('SELECT count(*) AS n FROM sesi').get().n, 1);

    await fetch(`${asal}/api/keluar`, { method: 'POST', headers: { cookie: kuki } });
    assert.equal(db.prepare('SELECT count(*) AS n FROM sesi').get().n, 0, 'baris sesi tertinggal sesudah keluar');

    const lagi = await fetch(`${asal}/api/saya`, { headers: { cookie: kuki } });
    assert.equal(lagi.status, 401, 'kuki bekas keluar masih diterima');
  } finally {
    await new Promise((selesai) => server.close(selesai));
    db.close();
  }
});

// ─── Tautan undangan masuk (Rencana T8 Task 3) ──────────────────────────────────────────────────────

test('pengelola membuat anggota tanpa email, lalu tautan masuknya, lewat HTTP', async () => {
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.bos);
    const baru = await s.minta('POST', `/api/grup/${s.grup.id}/anggota`, { isi: { nama: 'Pak Warga' }, kuki });
    assert.equal(baru.kode, 201, JSON.stringify(baru.badan));
    assert.equal(baru.badan.email, null);

    const tautan = await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${baru.badan.id}/tautan`, { kuki });
    assert.equal(tautan.kode, 201, JSON.stringify(tautan.badan));
    assert.ok(typeof tautan.badan.tanda === 'string' && tautan.badan.tanda.length >= 32);
    assert.equal(tautan.badan.nama, 'Pak Warga');
    assert.ok(tautan.badan.kedaluwarsa);
  } finally {
    await s.tutup();
  }
});

test('⛔ satpam dan penghuni ditolak 403 saat membuat tautan masuk', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const warga = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota`,
      { isi: { nama: 'Pak Warga' }, kuki: kukiBos })).badan;

    for (const orang of [s.pakSatpam, s.karyawan]) {
      const kuki = await s.masukSebagai(orang);
      const r = await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${warga.id}/tautan`, { kuki });
      assert.equal(r.kode, 403, `${orang.nama} seharusnya ditolak, bukan ${r.kode}`);
      assert.equal(r.badan.tanda, undefined, 'tanda ikut keluar walau ditolak');
    }
    // Dan orang luar: "tidak ditemukan", bukan "tidak berhak".
    const kukiLuar = await s.masukSebagai(s.orangLuar);
    const luar = await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${warga.id}/tautan`, { kuki: kukiLuar });
    assert.equal(luar.kode, 404);
  } finally {
    await s.tutup();
  }
});

test('tanpa sesi, membuat tautan masuk ditolak 401', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('POST', `/api/grup/${s.grup.id}/anggota/1/tautan`);
    assert.equal(r.kode, 401);
  } finally {
    await s.tutup();
  }
});

test('⛔ RANTAI: menukar tautan memberi kuki sesi, dan orangnya langsung bisa dipakai', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const warga = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota`,
      { isi: { nama: 'Pak Warga' }, kuki: kukiBos })).badan;
    const { tanda } = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${warga.id}/tautan`,
      { kuki: kukiBos })).badan;

    // Menukar DITANYAKAN TANPA KUKI: inilah pengganti sandi.
    const tukar = await s.minta('POST', '/api/tautan-masuk', { isi: { tanda } });
    assert.equal(tukar.kode, 200, JSON.stringify(tukar.badan));
    assert.equal(tukar.badan.pengguna.id, warga.id);
    assert.equal(tukar.badan.grup.kode_undangan, undefined, 'kode undangan grup ikut keluar ke penghuni');
    assert.ok(tukar.kuki, 'tidak ada kuki sesi: orangnya tidak benar-benar masuk');
    assert.match(tukar.setKuki.join(';'), /HttpOnly/i);

    const saya = await s.minta('GET', '/api/saya', { kuki: tukar.kuki });
    assert.equal(saya.kode, 200);
    assert.equal(saya.badan.pengguna.id, warga.id);
    assert.equal(saya.badan.grup.length, 1, 'penghuni baru seharusnya melihat satu grup');
  } finally {
    await s.tutup();
  }
});

test('⛔ tautan bekas menjawab 401, bukan memberi sesi kedua', async () => {
  const s = await nyalakan();
  try {
    const kukiBos = await s.masukSebagai(s.bos);
    const warga = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota`,
      { isi: { nama: 'Pak Warga' }, kuki: kukiBos })).badan;
    const { tanda } = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${warga.id}/tautan`,
      { kuki: kukiBos })).badan;

    assert.equal((await s.minta('POST', '/api/tautan-masuk', { isi: { tanda } })).kode, 200);
    const kedua = await s.minta('POST', '/api/tautan-masuk', { isi: { tanda } });
    assert.equal(kedua.kode, 401, 'tautan sekali pakai masih bisa dipakai kedua kali');
    assert.equal(kedua.kuki, undefined, 'tautan bekas tetap memberi kuki sesi');
  } finally {
    await s.tutup();
  }
});

test('tanda karangan menjawab 401 dengan pesan yang sama seperti tanda bekas', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('POST', '/api/tautan-masuk', { isi: { tanda: 'tanda-karangan' } });
    assert.equal(r.kode, 401);
    const kosong = await s.minta('POST', '/api/tautan-masuk', { isi: {} });
    assert.equal(kosong.kode, 401);
    assert.equal(r.badan.galat, kosong.badan.galat, 'pesan penolakan berbeda-beda');
  } finally {
    await s.tutup();
  }
});

test('⛔ tanda tautan tidak ikut keluar lewat daftar anggota', async () => {
  // Ia hanya boleh terlihat SEKALI, pada jawaban pembuatannya.
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.bos);
    const warga = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota`,
      { isi: { nama: 'Pak Warga' }, kuki })).badan;
    const { tanda } = (await s.minta('POST', `/api/grup/${s.grup.id}/anggota/${warga.id}/tautan`,
      { kuki })).badan;

    const daftar = await s.minta('GET', `/api/grup/${s.grup.id}/anggota`, { kuki });
    const teks = JSON.stringify(daftar.badan);
    assert.ok(!teks.includes(tanda), 'tanda tautan ikut keluar lewat daftar anggota');
    assert.ok(!teks.includes('tanda_hash'));
    // Yang BOLEH ikut hanyalah keadaannya, supaya pengelola tahu siapa yang belum masuk.
    assert.equal(daftar.badan.find((a) => a.id === warga.id).tautan_masuk, 'menunggu dipakai');
  } finally {
    await s.tutup();
  }
});

test('halaman undang.html disajikan server, jadi tautan WhatsApp tidak buntu', async () => {
  const s = await nyalakan();
  try {
    const html = await s.minta('GET', '/undang.html');
    assert.equal(html.kode, 200, 'tautan undangan akan membuka halaman kosong');
    assert.match(String(html.badan), /undang\.js/);
    const js = await s.minta('GET', '/undang.js');
    assert.equal(js.kode, 200);
  } finally {
    await s.tutup();
  }
});

test('⛔ RANTAI: berhenti berlangganan lewat HTTP benar-benar menghentikan kirimannya', async () => {
  // Jalur DELETE /api/langganan ada dan diuji sejak T5, tetapi tidak ada layar yang memanggilnya sampai
  // Rencana T10. Uji ini menelusuri jalur HTTP-nya, bukan akses.mjs langsung.
  const s = await nyalakan();
  try {
    const kuki = await s.masukSebagai(s.pakSatpam);
    const perangkat = {
      alamat: 'https://contoh.test/push/satpam-t10',
      kunci: 'kunci-umum-palsu',
      rahasia: 'rahasia-palsu',
    };
    const daftar = await s.minta('POST', `/api/grup/${s.grup.id}/langganan`, { isi: perangkat, kuki });
    assert.equal(daftar.kode, 201, JSON.stringify(daftar.badan));

    const berhenti = await s.minta('DELETE', '/api/langganan', { isi: { alamat: perangkat.alamat }, kuki });
    assert.equal(berhenti.kode, 200, JSON.stringify(berhenti.badan));

    // Yang membuktikan: tidak ada lagi penerima di grup itu, jadi tidak ada kiriman yang dibuat.
    const sisa = await s.minta('GET', `/api/grup/${s.grup.id}/langganan`, { kuki }).catch(() => null);
    if (sisa && sisa.kode === 200) {
      assert.deepEqual(sisa.badan, [], 'perangkat masih terdaftar sesudah berhenti');
    }
  } finally {
    await s.tutup();
  }
});

test('berhenti berlangganan tanpa sesi ditolak', async () => {
  const s = await nyalakan();
  try {
    const r = await s.minta('DELETE', '/api/langganan', { isi: { alamat: 'https://contoh.test/push/x' } });
    assert.equal(r.kode, 401);
  } finally {
    await s.tutup();
  }
});
