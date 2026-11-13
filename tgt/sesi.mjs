// Sesi TGT yang tersimpan di basis data. Rencana T8 Task 1.
//
// Sebelum ini sesi disimpan di sebuah Map di dalam server, dan batasnya tertulis di sana: server yang
// dinyalakan ulang membuat semua orang masuk lagi. Itu bukan sekadar merepotkan — sejak T8 cara masuk utama
// adalah tautan undangan SEKALI PAKAI, jadi orang yang terlempar keluar tidak punya cara masuk kembali
// tanpa meminta tautan baru. Sesi yang bertahan adalah syarat sekali-pakai itu, bukan hiasan.
//
// ⛔ Tanda sesi adalah KUNCI MASUK. Yang tersimpan hanyalah hash-nya; tandanya sendiri hanya ada di kuki
// peramban orangnya. Membaca berkas basis data tidak cukup untuk memakai sesi orang lain.
import { createHash, randomBytes } from 'node:crypto';

/**
 * Umur sesi. Panjang dengan sengaja: masuknya sekali pakai lewat tautan dari pengelola, jadi sesi yang
 * pendek berarti warga harus minta tautan baru berkali-kali — dan itu akan berakhir dengan pengelola
 * membagikan satu tautan untuk semua orang.
 */
export const UMUR_SESI_HARI = 90;

// Tanda 32 bita acak sudah tidak bisa ditebak, jadi hash cepat sudah cukup: yang dijaga bukan sandi lemah,
// melainkan agar nilai di basis data tidak bisa dipakai apa adanya. Sama dengan `otp.kode_hash`.
function hashTanda(tanda) {
  return createHash('sha256').update(String(tanda)).digest('base64');
}

/** Buang sesi yang sudah lewat kedaluwarsanya. Mengembalikan berapa baris yang dibuang. */
export function bersihkanSesi(db) {
  return db.prepare("DELETE FROM sesi WHERE kedaluwarsa < datetime('now')").run().changes;
}

/**
 * Buat sesi baru untuk satu orang, dan kembalikan TANDANYA.
 *
 * Tandanya hanya dikembalikan di sini, sekali. Sesudah itu tidak ada cara membacanya kembali dari basis data.
 * Pengguna yang tidak ada ditolak oleh kunci asing — bukan dibuatkan.
 */
export function buatSesi(db, penggunaId) {
  bersihkanSesi(db);
  const tanda = randomBytes(32).toString('base64url');
  db.prepare(
    `INSERT INTO sesi (pengguna_id, tanda_hash, kedaluwarsa)
     VALUES (?, ?, datetime('now', ?))`,
  ).run(penggunaId, hashTanda(tanda), `+${UMUR_SESI_HARI} days`);
  return tanda;
}

/**
 * Baca sesi dari tandanya. Yang tidak ada, yang kedaluwarsa, dan yang akunnya sudah hilang semuanya
 * mengembalikan undefined — satu jawaban untuk semua sebab, supaya bedanya tidak bisa dibaca dari luar.
 */
export function bacaSesi(db, tanda) {
  if (typeof tanda !== 'string' || !tanda) return undefined;

  const baris = db.prepare(
    `SELECT sesi.pengguna_id
       FROM sesi JOIN pengguna ON pengguna.id = sesi.pengguna_id
      WHERE sesi.tanda_hash = ? AND sesi.kedaluwarsa >= datetime('now')`,
  ).get(hashTanda(tanda));

  // Dibersihkan di jalan: sesi kedaluwarsa menyimpan jejak siapa masuk kapan lebih lama dari perlunya (K71).
  if (!baris) {
    bersihkanSesi(db);
    return undefined;
  }
  return { penggunaId: baris.pengguna_id };
}

/** Keluar: hapus satu sesi saja, yaitu yang tandanya diberikan. Sesi lain milik orang yang sama tetap hidup. */
export function hapusSesi(db, tanda) {
  if (typeof tanda !== 'string' || !tanda) return 0;
  return db.prepare('DELETE FROM sesi WHERE tanda_hash = ?').run(hashTanda(tanda)).changes;
}
