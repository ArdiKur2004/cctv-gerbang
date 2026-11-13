// Akun, masuk, dan keanggotaan grup TGT. Rencana T2, spec specs/2026-10-26-tgt-versi-1.md §4.
//
// Sandi disimpan ter-hash dengan scrypt dari `node:crypto` — bawaan Node, jadi tidak ada paket baru (CLAUDE.md §6).
// Nomor WA adalah data pribadi: ia tinggal di basis data di data/tgt/ dan tidak pernah dicetak ke log.
import { createHash, randomBytes, randomInt, scryptSync, timingSafeEqual } from 'node:crypto';

import { GalatLayanan, buatGrup, grupDariKode } from './layanan.mjs';

/**
 * Tiga peran (spec §4). DAFTAR PUTIH: peran yang tidak ada di sini ditolak, supaya hak akses tidak bisa diperluas
 * dengan menulis nilai baru ke basis data.
 */
export const PERAN = Object.freeze(['pengelola', 'satpam', 'penghuni']);

const PANJANG_SANDI_MINIMUM = 8;

// Parameter scrypt. Disimpan di dalam hash-nya sendiri, supaya hash lama tetap bisa diperiksa setelah parameter
// ini dinaikkan kelak.
const SCRYPT = { N: 16384, r: 8, p: 1, panjang: 32 };

// Pesan yang SAMA untuk nomor tak terdaftar dan sandi salah. Pesan yang berbeda memberi tahu orang luar nomor
// mana yang punya akun.
const PESAN_MASUK_GAGAL = 'nomor WhatsApp atau sandi salah';

/**
 * Bentuk baku nomor WhatsApp: '6281200000001'. "08...", "+62 812...", dan "62..." adalah orang yang sama, jadi
 * tidak boleh menjadi dua akun.
 */
export function normalkanWa(nomor) {
  const angka = String(nomor ?? '').replace(/\D/g, '');
  let baku = angka;
  if (baku.startsWith('0')) baku = `62${baku.slice(1)}`;
  else if (baku.startsWith('8')) baku = `62${baku}`;

  if (!baku.startsWith('62') || baku.length < 10 || baku.length > 15) {
    throw new GalatLayanan('nomor WhatsApp tidak terbaca; contohnya 081200000001');
  }
  return baku;
}

function hashSandi(sandi) {
  const garam = randomBytes(16);
  const hash = scryptSync(sandi, garam, SCRYPT.panjang, { N: SCRYPT.N, r: SCRYPT.r, p: SCRYPT.p });
  return ['scrypt', SCRYPT.N, SCRYPT.r, SCRYPT.p, garam.toString('base64'), hash.toString('base64')].join('$');
}

function sandiCocok(sandi, tersimpan) {
  const [cara, N, r, p, garamB64, hashB64] = String(tersimpan ?? '').split('$');
  if (cara !== 'scrypt') return false;
  const hash = Buffer.from(hashB64, 'base64');
  const coba = scryptSync(sandi, Buffer.from(garamB64, 'base64'), hash.length, {
    N: Number(N), r: Number(r), p: Number(p),
  });
  return coba.length === hash.length && timingSafeEqual(coba, hash);
}

// Hash sandi tidak pernah keluar dari modul ini: pemanggil mana pun hanya menerima bentuk ini.
function tanpaSandi(baris) {
  if (!baris) return baris;
  const { sandi_hash: _buang, ...sisa } = baris;
  return sisa;
}

// ─── Masuk dengan email + OTP (K72) ─────────────────────────────────────────────────────────────────

/** Umur OTP. Pendek dengan sengaja: ia dikirim lewat surel, dan surel bisa dibaca orang lain belakangan. */
export const UMUR_OTP_DETIK = 300;

/**
 * Batas percobaan. Enam angka hanya aman bila tidak boleh dicoba berkali-kali: tanpa batas ini, seluruh
 * sejuta kemungkinan bisa dicoba dalam hitungan menit.
 */
export const MAKS_COBA_OTP = 5;

// Sengaja sederhana dan ketat: satu @, ada titik di belakangnya, tanpa spasi. Alamat yang aneh ditolak di
// pintu, bukan diterima lalu gagal terkirim diam-diam.
const BENTUK_EMAIL = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/;

export function normalkanEmail(email) {
  const teks = String(email ?? '').trim().toLowerCase();
  if (!BENTUK_EMAIL.test(teks)) throw new GalatLayanan('alamat email tidak terbaca');
  return teks;
}

// Pesan yang SAMA untuk kode salah, kode kedaluwarsa, kode habis percobaan, dan email yang tidak punya
// permintaan: bedanya akan memberi tahu orang luar alamat mana yang punya akun.
const PESAN_OTP_GAGAL = 'kode tidak berlaku; mintalah kode baru';

function hashOtp(email, kode) {
  // Garam dari emailnya sendiri: OTP berumur pendek dan sekali pakai, jadi yang dijaga di sini hanyalah agar
  // siapa pun yang membaca basis data tidak bisa langsung memakai kodenya.
  return createHash('sha256').update(`${email}:${kode}`).digest('base64');
}

/** Pengirim bawaan: TIDAK mengirim ke mana pun. Lihat komentar di mintaOtp(). */
export function cetakOtp(email, kode) {
  console.error(
    `[tgt] OTP untuk ${email}: ${kode} — surel BELUM terkirim ke mana pun, karena layanan surel belum dibeli `
    + '(keputusan owner, CLAUDE.md §8). Sampai itu ada, kode dibaca dari layar ini.',
  );
}

/**
 * Minta OTP untuk satu alamat email.
 *
 * ⛔ Pengirim bawaannya hanya MENCETAK kode di layar server. Mengirim surel sungguhan butuh layanan berbayar,
 * dan itu keputusan owner (`CLAUDE.md` §8). Yang berbahaya bukan "belum terkirim", melainkan kalau ini
 * terlihat seperti sudah terkirim — karena itu kalimat cetakannya menyebut keadaannya terang-terangan.
 *
 * Jawabannya SAMA untuk email yang sudah punya akun dan yang belum.
 */
export function mintaOtp(db, { email, kirim = cetakOtp } = {}) {
  const alamat = normalkanEmail(email);

  // Bersihkan yang sudah kedaluwarsa: menyimpan alamat email lebih lama dari perlunya melanggar K71.
  db.prepare("DELETE FROM otp WHERE kedaluwarsa < datetime('now')").run();

  const kode = String(randomInt(0, 1_000_000)).padStart(6, '0');
  // Permintaan baru MENGGANTI yang lama: kode lama langsung tidak berlaku.
  db.prepare(
    `INSERT INTO otp (email, kode_hash, kedaluwarsa, coba) VALUES (?, ?, datetime('now', ?), 0)
       ON CONFLICT (email) DO UPDATE SET kode_hash = excluded.kode_hash,
                                         kedaluwarsa = excluded.kedaluwarsa,
                                         coba = 0,
                                         dibuat = datetime('now')`,
  ).run(alamat, hashOtp(alamat, kode), `+${UMUR_OTP_DETIK} seconds`);

  kirim(alamat, kode);
  return { dikirim: true, berlakuDetik: UMUR_OTP_DETIK };
}

/**
 * Masuk dengan OTP. Pemakaian pertama sekaligus membuat akunnya: tidak ada langkah "daftar" tersendiri,
 * karena yang membuktikan kepemilikan alamat adalah kode itu sendiri.
 */
export function masukDenganOtp(db, { email, kode, nama } = {}) {
  let alamat;
  try {
    alamat = normalkanEmail(email);
  } catch {
    throw new GalatLayanan(PESAN_OTP_GAGAL);
  }

  const baris = db.prepare("SELECT * FROM otp WHERE email = ? AND kedaluwarsa >= datetime('now')").get(alamat);
  if (!baris) throw new GalatLayanan(PESAN_OTP_GAGAL);

  if (baris.coba >= MAKS_COBA_OTP) {
    // Kodenya hangus, bukan sekadar ditolak: membiarkannya hidup berarti penebak boleh mencoba lagi nanti.
    db.prepare('DELETE FROM otp WHERE email = ?').run(alamat);
    throw new GalatLayanan(PESAN_OTP_GAGAL);
  }

  const diberikan = String(kode ?? '');
  const benar = hashOtp(alamat, diberikan) === baris.kode_hash;
  if (!benar) {
    const sesudah = baris.coba + 1;
    if (sesudah >= MAKS_COBA_OTP) db.prepare('DELETE FROM otp WHERE email = ?').run(alamat);
    else db.prepare('UPDATE otp SET coba = ? WHERE email = ?').run(sesudah, alamat);
    throw new GalatLayanan(PESAN_OTP_GAGAL);
  }

  // Sekali pakai: kode dibuang sebelum akun dikembalikan.
  db.prepare('DELETE FROM otp WHERE email = ?').run(alamat);

  const ada = db.prepare('SELECT * FROM pengguna WHERE email = ?').get(alamat);
  if (ada) return tanpaSandi(ada);

  const namaBersih = typeof nama === 'string' && nama.trim() ? nama.trim() : alamat.split('@')[0];
  const { lastInsertRowid } = db.prepare('INSERT INTO pengguna (nama, email) VALUES (?, ?)')
    .run(namaBersih, alamat);
  return pengguna(db, lastInsertRowid);
}

// ─── Cara lama: nomor WhatsApp + sandi ──────────────────────────────────────────────────────────────

export function buatAkun(db, { nama, wa, sandi } = {}) {
  const namaBersih = typeof nama === 'string' ? nama.trim() : '';
  if (!namaBersih) throw new GalatLayanan('nama wajib diisi');
  const waBersih = normalkanWa(wa);
  if (typeof sandi !== 'string' || sandi.length < PANJANG_SANDI_MINIMUM) {
    throw new GalatLayanan(`sandi minimal ${PANJANG_SANDI_MINIMUM} huruf`);
  }
  if (db.prepare('SELECT 1 FROM pengguna WHERE wa = ?').get(waBersih)) {
    throw new GalatLayanan('nomor WhatsApp itu sudah terdaftar');
  }

  const { lastInsertRowid } = db.prepare('INSERT INTO pengguna (nama, wa, sandi_hash) VALUES (?, ?, ?)')
    .run(namaBersih, waBersih, hashSandi(sandi));
  return pengguna(db, lastInsertRowid);
}

export function pengguna(db, id) {
  return tanpaSandi(db.prepare('SELECT * FROM pengguna WHERE id = ?').get(id));
}

export function masuk(db, { wa, sandi } = {}) {
  // Nomor yang bentuknya salah pun diberi pesan yang sama: bedanya akan memberi tahu bentuk nomor yang dipakai.
  let waBersih;
  try {
    waBersih = normalkanWa(wa);
  } catch {
    throw new GalatLayanan(PESAN_MASUK_GAGAL);
  }
  const baris = db.prepare('SELECT * FROM pengguna WHERE wa = ?').get(waBersih);
  if (!baris || typeof sandi !== 'string' || !sandiCocok(sandi, baris.sandi_hash)) {
    throw new GalatLayanan(PESAN_MASUK_GAGAL);
  }
  return tanpaSandi(baris);
}

// ─── Keanggotaan grup ───────────────────────────────────────────────────────────────────────────────

function wajibPengguna(db, penggunaId) {
  const orang = pengguna(db, penggunaId);
  if (!orang) throw new GalatLayanan('pengguna tidak ditemukan');
  return orang;
}

function periksaPeran(peran) {
  if (typeof peran === 'string' && PERAN.includes(peran)) return peran;
  throw new GalatLayanan(`peran "${peran ?? ''}" tidak dikenal; pilihannya ${PERAN.join(', ')}`);
}

function masukkanAnggota(db, grupId, penggunaId, peran) {
  db.prepare('INSERT INTO anggota (grup_id, pengguna_id, peran) VALUES (?, ?, ?)')
    .run(grupId, penggunaId, periksaPeran(peran));
}

/** Langkah 2 alur owner, cabang "buat baru": pembuatnya langsung menjadi pengelola. */
export function buatGrupBaru(db, penggunaId, { nama, jenis } = {}) {
  wajibPengguna(db, penggunaId);
  const grup = buatGrup(db, { nama, jenis });
  masukkanAnggota(db, grup.id, penggunaId, 'pengelola');
  return { grup, peran: 'pengelola' };
}

/** Langkah 2 alur owner, cabang "ikut grup lain". Yang ikut menjadi penghuni; pengelola menaikkannya kalau perlu. */
export function ikutGrup(db, penggunaId, kode) {
  wajibPengguna(db, penggunaId);
  const grup = grupDariKode(db, kode);
  if (!grup) throw new GalatLayanan('kode undangan tidak dikenal');

  // Yang sudah menjadi anggota tidak diubah: pengelola yang menekan tautan undangannya sendiri tidak boleh
  // turun menjadi penghuni.
  const peranSekarang = peranDi(db, grup.id, penggunaId);
  if (peranSekarang) return { grup, peran: peranSekarang };

  masukkanAnggota(db, grup.id, penggunaId, 'penghuni');
  return { grup, peran: 'penghuni' };
}

/**
 * Pastikan ada akun untuk alamat email ini, lalu masukkan ke grup sebagai penghuni (K72).
 *
 * Email yang SUDAH punya akun dipakai ulang, tidak dibuatkan akun kedua: satu orang bisa menjadi anggota
 * beberapa grup (rumahnya sendiri dan kantornya), dan akun kedua akan memecah kendaraan serta tamunya ke dua
 * akun yang tidak saling tahu. Yang sudah menjadi anggota tidak diubah perannya.
 */
export function tambahAnggota(db, grupId, { email, nama } = {}) {
  const namaBersih = typeof nama === 'string' ? nama.trim() : '';

  // Anggota TANPA email (Rencana T8). Banyak warga tidak punya alamat email yang mereka buka, dan sejak
  // tautan undangan ada, email berhenti menjadi syarat masuk. Email dibiarkan NULL, bukan diisi karangan:
  // alamat karangan akan membuat OTP terkirim ke orang lain kelak.
  if (email === undefined || email === null || String(email).trim() === '') {
    if (!namaBersih) throw new GalatLayanan('nama wajib diisi bila tidak ada alamat email');
    const { lastInsertRowid } = db.prepare('INSERT INTO pengguna (nama) VALUES (?)').run(namaBersih);
    const orangBaru = db.prepare('SELECT * FROM pengguna WHERE id = ?').get(lastInsertRowid);
    masukkanAnggota(db, grupId, orangBaru.id, 'penghuni');
    return { ...tanpaSandi(orangBaru), peran: 'penghuni' };
  }

  const alamat = normalkanEmail(email);
  let orang = db.prepare('SELECT * FROM pengguna WHERE email = ?').get(alamat);
  if (!orang) {
    const namaBersih = typeof nama === 'string' && nama.trim() ? nama.trim() : alamat.split('@')[0];
    const { lastInsertRowid } = db.prepare('INSERT INTO pengguna (nama, email) VALUES (?, ?)')
      .run(namaBersih, alamat);
    orang = db.prepare('SELECT * FROM pengguna WHERE id = ?').get(lastInsertRowid);
  }

  const peranSekarang = peranDi(db, grupId, orang.id);
  if (peranSekarang) return { ...tanpaSandi(orang), peran: peranSekarang };

  masukkanAnggota(db, grupId, orang.id, 'penghuni');
  return { ...tanpaSandi(orang), peran: 'penghuni' };
}

/** Keluarkan anggota dari grup. Akunnya TIDAK dihapus: ia bisa menjadi anggota grup lain. */
export function keluarkanAnggota(db, grupId, penggunaId) {
  const peran = peranDi(db, grupId, penggunaId);
  if (!peran) throw new GalatLayanan('orang itu bukan anggota grup ini');
  if (peran === 'pengelola') {
    const lain = db.prepare(
      "SELECT count(*) AS n FROM anggota WHERE grup_id = ? AND peran = 'pengelola' AND pengguna_id <> ?",
    ).get(grupId, penggunaId).n;
    if (lain === 0) throw new GalatLayanan('grup harus punya setidaknya satu pengelola');
  }
  return db.prepare('DELETE FROM anggota WHERE grup_id = ? AND pengguna_id = ?').run(grupId, penggunaId).changes;
}

export function peranDi(db, grupId, penggunaId) {
  return db.prepare('SELECT peran FROM anggota WHERE grup_id = ? AND pengguna_id = ?')
    .get(grupId, penggunaId)?.peran;
}

/**
 * Ubah peran seseorang di satu grup. Grup tidak boleh kehilangan pengelola terakhirnya: tanpa pagar ini, sebuah
 * grup bisa terkunci dari semua orang dan hanya bisa dibuka dengan menyentuh basis data langsung.
 */
export function tetapkanPeran(db, grupId, penggunaId, peran) {
  const peranBersih = periksaPeran(peran);
  if (!peranDi(db, grupId, penggunaId)) throw new GalatLayanan('orang itu bukan anggota grup ini');

  if (peranBersih !== 'pengelola') {
    const pengelolaLain = db.prepare(
      "SELECT count(*) AS n FROM anggota WHERE grup_id = ? AND peran = 'pengelola' AND pengguna_id <> ?",
    ).get(grupId, penggunaId).n;
    if (pengelolaLain === 0) throw new GalatLayanan('grup harus punya setidaknya satu pengelola');
  }

  db.prepare('UPDATE anggota SET peran = ? WHERE grup_id = ? AND pengguna_id = ?')
    .run(peranBersih, grupId, penggunaId);
  return peranBersih;
}

/** Grup yang orang ini ikuti, beserta perannya di masing-masing. */
export function grupSaya(db, penggunaId) {
  return db.prepare(
    `SELECT grup.*, anggota.peran
       FROM anggota JOIN grup ON grup.id = anggota.grup_id
      WHERE anggota.pengguna_id = ?
      ORDER BY grup.id`,
  ).all(penggunaId);
}

/** Anggota satu grup, beserta perannya. Hash sandi tidak ikut. */
export function anggotaGrup(db, grupId) {
  return db.prepare(
    // Email ikut sejak K72: ia yang menjadi identitas masuk, jadi pengelola perlu melihatnya untuk tahu
    // siapa yang sudah ia undang. Hash sandi tidak pernah ikut.
    //
    // `tautan_masuk` ikut sejak Rencana T8: pengurus RT perlu tahu warga mana yang belum memakai tautannya,
    // supaya ia menagihnya. Yang ikut hanyalah KEADAANNYA — tanda dan hash-nya tidak pernah keluar dari
    // buatUndanganMasuk().
    `SELECT pengguna.id, pengguna.nama, pengguna.email, pengguna.wa, anggota.peran,
            (SELECT CASE WHEN u.dipakai_pada IS NOT NULL      THEN 'sudah dipakai'
                         WHEN u.kedaluwarsa < datetime('now') THEN 'kedaluwarsa'
                         ELSE 'menunggu dipakai' END
               FROM undangan_masuk u
              WHERE u.grup_id = anggota.grup_id AND u.pengguna_id = pengguna.id) AS tautan_masuk
       FROM anggota JOIN pengguna ON pengguna.id = anggota.pengguna_id
      WHERE anggota.grup_id = ?
      ORDER BY pengguna.id`,
  ).all(grupId);
}

// ─── Tautan undangan masuk per orang (Rencana T8, persetujuan owner 26 Okt) ─────────────────────────
//
// Cara masuk utama TGT. Pengelola membuat anggota, menyalin tautannya, dan mengirimnya lewat WhatsApp
// miliknya sendiri. Penghuni menekannya sekali, lalu tidak perlu kode apa pun lagi.
//
// Ini lebih cocok dengan kenyataan daripada OTP lewat surel: pengurus RT memang kenal warganya. Dan ia
// menghapus ketergantungan pada layanan surel berbayar, yang merupakan keputusan owner (CLAUDE.md §8).

/**
 * Umur tautan. Pendek dengan sengaja: tautan tinggal di riwayat WhatsApp, dan riwayat obrolan dibaca orang
 * lain belakangan — terutama HP yang dipinjam atau dijual.
 */
export const UMUR_UNDANGAN_HARI = 14;

// Satu pesan untuk tanda palsu, tanda bekas, tanda kedaluwarsa, dan orang yang sudah dikeluarkan dari grup.
// Bedanya akan memberi tahu orang luar tanda mana yang pernah ada.
export const PESAN_UNDANGAN_GAGAL = 'tautan masuk tidak berlaku; mintalah tautan baru dari pengelola';

// Tanda 32 bita acak tidak bisa ditebak, jadi hash cepat sudah cukup — yang dijaga adalah agar nilai di basis
// data tidak bisa dipakai apa adanya. Sama dengan `otp.kode_hash` dan `sesi.tanda_hash`.
function hashTandaUndangan(tanda) {
  return createHash('sha256').update(String(tanda)).digest('base64');
}

/**
 * Buat tautan masuk untuk satu anggota, dan kembalikan TANDANYA — sekali, di sini saja.
 *
 * Tautan lama orang itu di grup itu DIBUANG lebih dulu. Itulah satu-satunya cara pengelola mencabut tautan
 * yang salah kirim: ia membuat yang baru.
 */
export function buatUndanganMasuk(db, grupId, penggunaId, dibuatOleh) {
  const peran = peranDi(db, grupId, penggunaId);
  if (!peran) throw new GalatLayanan('orang itu bukan anggota grup ini');

  // Yang sudah kedaluwarsa dan belum dipakai tidak perlu disimpan (K71).
  db.prepare("DELETE FROM undangan_masuk WHERE kedaluwarsa < datetime('now') AND dipakai_pada IS NULL").run();
  db.prepare('DELETE FROM undangan_masuk WHERE grup_id = ? AND pengguna_id = ?').run(grupId, penggunaId);

  const tanda = randomBytes(32).toString('base64url');
  db.prepare(
    `INSERT INTO undangan_masuk (pengguna_id, grup_id, tanda_hash, kedaluwarsa, dibuat_oleh)
     VALUES (?, ?, ?, datetime('now', ?), ?)`,
  ).run(penggunaId, grupId, hashTandaUndangan(tanda), `+${UMUR_UNDANGAN_HARI} days`, dibuatOleh ?? null);

  const baris = db.prepare('SELECT kedaluwarsa FROM undangan_masuk WHERE tanda_hash = ?')
    .get(hashTandaUndangan(tanda));
  return {
    tanda,
    kedaluwarsa: baris.kedaluwarsa,
    peran,
    nama: pengguna(db, penggunaId).nama,
    grup: db.prepare('SELECT nama FROM grup WHERE id = ?').get(grupId).nama,
  };
}

/**
 * Tukar tautan dengan orangnya. Dipanggil TANPA sesi: tautan inilah yang menggantikan sandi.
 *
 * SEKALI PAKAI. Pemakaian kedua ditolak, karena tautannya tinggal di riwayat WhatsApp selamanya. Keanggotaan
 * diperiksa lagi di sini, bukan sekadar saat tautan dibuat: orang yang sudah dikeluarkan dari grup tidak boleh
 * masuk dengan tautan lamanya.
 */
export function tukarUndanganMasuk(db, tanda) {
  if (typeof tanda !== 'string' || !tanda) throw new GalatLayanan(PESAN_UNDANGAN_GAGAL);

  const baris = db.prepare(
    `SELECT u.id, u.pengguna_id, u.grup_id, anggota.peran
       FROM undangan_masuk u
       JOIN anggota ON anggota.grup_id = u.grup_id AND anggota.pengguna_id = u.pengguna_id
      WHERE u.tanda_hash = ?
        AND u.kedaluwarsa >= datetime('now')
        AND u.dipakai_pada IS NULL`,
  ).get(hashTandaUndangan(tanda));
  if (!baris) throw new GalatLayanan(PESAN_UNDANGAN_GAGAL);

  // Ditandai terpakai SEBELUM orangnya dikembalikan: kalau penandaan gagal, tidak ada yang masuk.
  db.prepare("UPDATE undangan_masuk SET dipakai_pada = datetime('now') WHERE id = ?").run(baris.id);

  return {
    pengguna: pengguna(db, baris.pengguna_id),
    grup: db.prepare('SELECT * FROM grup WHERE id = ?').get(baris.grup_id),
    peran: baris.peran,
  };
}
