// Basis data TGT (Transportation Gate Track) dan migrasinya. Rencana T1, spec specs/2026-10-26-tgt-versi-1.md.
//
// Memakai SQLite bawaan Node 24 (`node:sqlite`), supaya proyek ini tetap NOL dependensi: tiap paket baru masuk
// aturan rantai pasok (CLAUDE.md §6). Node masih menandai modul itu sebagai fitur percobaan, jadi ia mencetak
// ExperimentalWarning. Itu batas yang dicatat, bukan disembunyikan.
//
// Isi basis data sungguhan = plat nomor dan jam keluar masuk, yaitu DATA PRIBADI (CLAUDE.md §4): berkasnya di
// data/tgt/ yang di-gitignore, dan tidak pernah di-commit atau diunggah.
import { DatabaseSync } from 'node:sqlite';

/** Versi skema yang dipasang `buka()`. Naik satu tiap kali susunan tabel berubah. */
export const VERSI_SKEMA = 7;

// Tabel pencatat migrasi. Bukan tabel isi, jadi ia tidak ikut dalam susunan().
const TABEL_MIGRASI = 'migrasi';

// Tiap langkah punya naik DAN turun (CLAUDE.md, aturan migrasi): basis data pelanggan tidak boleh dibangun ulang
// dari nol tiap kali skemanya berubah, dan pencabutan yang tak bisa dibatalkan tidak boleh ada.
const MIGRASI = [
  {
    versi: 1,
    naik: [
      `CREATE TABLE grup (
         id            INTEGER PRIMARY KEY,
         nama          TEXT    NOT NULL,
         jenis         TEXT    NOT NULL,
         kode_undangan TEXT    NOT NULL UNIQUE,
         dibuat        TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      `CREATE TABLE gerbang (
         id           INTEGER PRIMARY KEY,
         grup_id      INTEGER NOT NULL REFERENCES grup(id),
         nama         TEXT    NOT NULL,
         jenis_lokasi TEXT    NOT NULL,
         alamat       TEXT    NOT NULL,
         kota         TEXT    NOT NULL,
         koordinat    TEXT,
         patokan      TEXT,
         status       TEXT    NOT NULL DEFAULT 'belum_aktif',
         dibuat       TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      `CREATE TABLE kendaraan (
         id          INTEGER PRIMARY KEY,
         gerbang_id  INTEGER NOT NULL REFERENCES gerbang(id),
         jenis       TEXT    NOT NULL,
         merek       TEXT,
         warna       TEXT,
         plat        TEXT    NOT NULL,
         atas_nama   TEXT    NOT NULL,
         unit        TEXT,
         dibuat      TEXT    NOT NULL DEFAULT (datetime('now')),
         UNIQUE (gerbang_id, plat)
       )`,
      `CREATE TABLE tamu (
         id            INTEGER PRIMARY KEY,
         gerbang_id    INTEGER NOT NULL REFERENCES gerbang(id),
         nama          TEXT    NOT NULL,
         keperluan     TEXT,
         jenis         TEXT    NOT NULL,
         merek         TEXT,
         warna         TEXT,
         plat          TEXT    NOT NULL,
         lama_hari     INTEGER NOT NULL,
         kode_undangan TEXT    NOT NULL UNIQUE,
         diundang_oleh TEXT,
         dibuat        TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      `CREATE TABLE kunjungan (
         id      INTEGER PRIMARY KEY,
         tamu_id INTEGER NOT NULL REFERENCES tamu(id),
         masuk   TEXT    NOT NULL,
         keluar  TEXT,
         status  TEXT    NOT NULL
       )`,
      `CREATE TABLE kejadian (
         id           INTEGER PRIMARY KEY,
         gerbang_id   INTEGER NOT NULL REFERENCES gerbang(id),
         waktu        TEXT    NOT NULL,
         arah         TEXT    NOT NULL,
         plat         TEXT,
         yakin        REAL,
         ciri_jenis   TEXT,
         ciri_warna   TEXT,
         ciri_merek   TEXT,
         kendaraan_id INTEGER REFERENCES kendaraan(id),
         tamu_id      INTEGER REFERENCES tamu(id)
       )`,
      `CREATE INDEX kejadian_gerbang_waktu ON kejadian (gerbang_id, waktu)`,
      `CREATE INDEX kendaraan_plat ON kendaraan (plat)`,
    ],
    // Urutan cabut dibalik, karena kunci asing menunjuk ke tabel di atasnya.
    turun: [
      'DROP TABLE kejadian',
      'DROP TABLE kunjungan',
      'DROP TABLE tamu',
      'DROP TABLE kendaraan',
      'DROP TABLE gerbang',
      'DROP TABLE grup',
    ],
  },
  {
    versi: 2,
    // Akun dan keanggotaan grup (Rencana T2). Peran disimpan di keanggotaan, bukan di pengguna: satu orang bisa
    // menjadi pengelola di grupnya sendiri dan penghuni di grup lain.
    naik: [
      `CREATE TABLE pengguna (
         id         INTEGER PRIMARY KEY,
         nama       TEXT NOT NULL,
         wa         TEXT NOT NULL UNIQUE,
         sandi_hash TEXT NOT NULL,
         dibuat     TEXT NOT NULL DEFAULT (datetime('now'))
       )`,
      `CREATE TABLE anggota (
         id          INTEGER PRIMARY KEY,
         grup_id     INTEGER NOT NULL REFERENCES grup(id),
         pengguna_id INTEGER NOT NULL REFERENCES pengguna(id),
         peran       TEXT    NOT NULL,
         dibuat      TEXT    NOT NULL DEFAULT (datetime('now')),
         UNIQUE (grup_id, pengguna_id)
       )`,
      // Pemilik kendaraan dan pengundang tamu. Dibutuhkan hak akses "penghuni hanya melihat miliknya sendiri":
      // tanpa kolom ini, pagar itu hanya bisa menebak dari nama, dan nama bukan tanda pengenal.
      // Boleh kosong, karena pengelola bisa mendaftarkan kendaraan atas nama orang yang belum punya akun.
      'ALTER TABLE kendaraan ADD COLUMN pengguna_id INTEGER REFERENCES pengguna(id)',
      'ALTER TABLE tamu ADD COLUMN pengundang_id INTEGER REFERENCES pengguna(id)',
    ],
    // Kolom yang menunjuk ke `pengguna` dicabut LEBIH DULU, baru tabelnya.
    turun: [
      'ALTER TABLE tamu DROP COLUMN pengundang_id',
      'ALTER TABLE kendaraan DROP COLUMN pengguna_id',
      'DROP TABLE anggota',
      'DROP TABLE pengguna',
    ],
  },
  {
    versi: 3,
    // Putusan gerbang pada tiap kejadian (Rencana T4). Semuanya boleh kosong: kejadian lama tidak punya
    // putusan, dan kejadian yang dicatat tangan tidak punya penanda dari kotak gerbang.
    naik: [
      // `penanda` adalah tanda sekali-pakai dari kotak gerbang, supaya penyusulan data sesudah luring tidak
      // menggandakan catatan. UNIQUE di SQLite mengizinkan banyak NULL, jadi kejadian tanpa penanda tetap boleh.
      'ALTER TABLE kejadian ADD COLUMN penanda TEXT',
      'CREATE UNIQUE INDEX kejadian_penanda ON kejadian (penanda) WHERE penanda IS NOT NULL',
      'ALTER TABLE kejadian ADD COLUMN putusan TEXT',
      'ALTER TABLE kejadian ADD COLUMN alasan TEXT',
      'ALTER TABLE kejadian ADD COLUMN dibuka_oleh INTEGER REFERENCES pengguna(id)',
    ],
    turun: [
      'DROP INDEX kejadian_penanda',
      'ALTER TABLE kejadian DROP COLUMN dibuka_oleh',
      'ALTER TABLE kejadian DROP COLUMN alasan',
      'ALTER TABLE kejadian DROP COLUMN putusan',
      'ALTER TABLE kejadian DROP COLUMN penanda',
    ],
  },
  {
    versi: 4,
    // Masuk dengan email + OTP (K72). Sandi dicabut: OTP menjadi satu-satunya kunci akun, jadi tidak boleh ada
    // jalan masuk kedua yang tidak dijaga pagar OTP.
    // Tabel `pengguna` DIBANGUN ULANG, bukan ditambah kolom: di versi 3 `wa` wajib diisi dan `sandi_hash`
    // wajib diisi, padahal akun yang masuk lewat email tidak punya keduanya. Kunci asing dimatikan sebentar
    // selama pembangunan ulang, cara yang dianjurkan SQLite.
    naik: [
      'PRAGMA foreign_keys = OFF',
      `CREATE TABLE pengguna_baru (
         id         INTEGER PRIMARY KEY,
         nama       TEXT NOT NULL,
         email      TEXT,
         wa         TEXT,
         sandi_hash TEXT,
         dibuat     TEXT NOT NULL DEFAULT (datetime('now'))
       )`,
      `INSERT INTO pengguna_baru (id, nama, email, wa, sandi_hash, dibuat)
       SELECT id, nama, NULL, wa, sandi_hash, dibuat FROM pengguna`,
      'DROP TABLE pengguna',
      'ALTER TABLE pengguna_baru RENAME TO pengguna',
      'CREATE UNIQUE INDEX pengguna_email ON pengguna (email) WHERE email IS NOT NULL',
      'CREATE UNIQUE INDEX pengguna_wa ON pengguna (wa) WHERE wa IS NOT NULL',
      `CREATE TABLE otp (
         id          INTEGER PRIMARY KEY,
         email       TEXT    NOT NULL UNIQUE,
         kode_hash   TEXT    NOT NULL,
         kedaluwarsa TEXT    NOT NULL,
         coba        INTEGER NOT NULL DEFAULT 0,
         dibuat      TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      'PRAGMA foreign_keys = ON',
    ],
    // Turun berarti kembali ke cara masuk lama (nomor WhatsApp + sandi). Akun yang hanya punya email TIDAK
    // BISA ADA di sana, jadi penyisipan di bawah akan GAGAL dengan keras bila ada akun seperti itu. Itu
    // disengaja: menebak nomor WhatsApp atau menyisipkan nilai palsu akan memalsukan data orang.
    turun: [
      'PRAGMA foreign_keys = OFF',
      'DROP TABLE otp',
      'DROP INDEX pengguna_email',
      'DROP INDEX pengguna_wa',
      `CREATE TABLE pengguna_lama (
         id         INTEGER PRIMARY KEY,
         nama       TEXT NOT NULL,
         wa         TEXT NOT NULL UNIQUE,
         sandi_hash TEXT NOT NULL,
         dibuat     TEXT NOT NULL DEFAULT (datetime('now'))
       )`,
      `INSERT INTO pengguna_lama (id, nama, wa, sandi_hash, dibuat)
       SELECT id, nama, wa, sandi_hash, dibuat FROM pengguna`,
      'DROP TABLE pengguna',
      'ALTER TABLE pengguna_lama RENAME TO pengguna',
      'PRAGMA foreign_keys = ON',
    ],
  },
  {
    versi: 5,
    // Langganan notifikasi per perangkat (K72). Satu orang bisa punya beberapa perangkat (HP dan layar
    // gerbang), jadi kuncinya adalah alamat perangkatnya, bukan orangnya.
    naik: [
      `CREATE TABLE langganan (
         id          INTEGER PRIMARY KEY,
         pengguna_id INTEGER NOT NULL REFERENCES pengguna(id),
         grup_id     INTEGER NOT NULL REFERENCES grup(id),
         alamat      TEXT    NOT NULL UNIQUE,
         kunci       TEXT    NOT NULL,
         rahasia     TEXT    NOT NULL,
         dibuat      TEXT    NOT NULL DEFAULT (datetime('now')),
         gagal       INTEGER NOT NULL DEFAULT 0
       )`,
      'CREATE INDEX langganan_grup ON langganan (grup_id)',
    ],
    turun: ['DROP TABLE langganan'],
  },
  {
    versi: 6,
    // Sesi yang bertahan, dan tautan undangan masuk per orang (Rencana T8, persetujuan owner 26 Okt).
    //
    // Keduanya menyimpan TANDA YANG TER-HASH, bukan tandanya sendiri: keduanya adalah kunci masuk, jadi
    // membaca berkas basis data tidak boleh cukup untuk memakainya. Sama dengan cara `otp.kode_hash`.
    //
    // ON DELETE CASCADE dipasang dengan sengaja: sesi dan tautan tidak boleh hidup lebih lama daripada akun
    // atau grupnya. Tanpa itu, orang yang akunnya dihapus masih memegang kunci yang berlaku.
    naik: [
      `CREATE TABLE sesi (
         id          INTEGER PRIMARY KEY,
         pengguna_id INTEGER NOT NULL REFERENCES pengguna(id) ON DELETE CASCADE,
         tanda_hash  TEXT    NOT NULL UNIQUE,
         kedaluwarsa TEXT    NOT NULL,
         dibuat      TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      'CREATE INDEX sesi_kedaluwarsa ON sesi (kedaluwarsa)',
      `CREATE TABLE undangan_masuk (
         id           INTEGER PRIMARY KEY,
         pengguna_id  INTEGER NOT NULL REFERENCES pengguna(id) ON DELETE CASCADE,
         grup_id      INTEGER NOT NULL REFERENCES grup(id) ON DELETE CASCADE,
         tanda_hash   TEXT    NOT NULL UNIQUE,
         kedaluwarsa  TEXT    NOT NULL,
         dipakai_pada TEXT,
         dibuat_oleh  INTEGER REFERENCES pengguna(id),
         dibuat       TEXT    NOT NULL DEFAULT (datetime('now'))
       )`,
      'CREATE INDEX undangan_masuk_orang ON undangan_masuk (pengguna_id, grup_id)',
    ],
    turun: ['DROP TABLE undangan_masuk', 'DROP TABLE sesi'],
  },
  {
    versi: 7,
    // Satu kendaraan = satu kedatangan (Rencana T9, persetujuan owner 26 Okt).
    //
    // Kamera gerbang menghasilkan belasan bingkai per kendaraan. Sebelum ini tiap bingkai menjadi kejadian
    // tersendiri, dan akibatnya setiap mobil yang KELUAR menahan gerbang di bingkai keduanya (aturan K73
    // membaca bingkai pertama sebagai "sudah keluar", jadi bingkai kedua terlihat janggal).
    //
    // `kedatangan_id` menunjuk kejadian PERTAMA dari kedatangan itu; bingkai pertama menunjuk dirinya sendiri.
    // Semua bacaan tetap tersimpan (K74) — yang berubah hanya pengelompokannya.
    naik: [
      'ALTER TABLE kejadian ADD COLUMN kedatangan_id INTEGER REFERENCES kejadian(id)',
      // Kejadian lama: tiap baris menjadi kedatangannya sendiri. Menebak pengelompokan kejadian lama akan
      // mengarang data yang tidak pernah ada — dan angka beranda akan berubah tanpa sebab yang bisa dijelaskan.
      'UPDATE kejadian SET kedatangan_id = id WHERE kedatangan_id IS NULL',
      'CREATE INDEX kejadian_kedatangan ON kejadian (kedatangan_id)',
      // Dipakai mencari kedatangan yang sedang berjalan: gerbang + plat + arah, terurut waktu.
      'CREATE INDEX kejadian_cari_kedatangan ON kejadian (gerbang_id, plat, arah, waktu)',
    ],
    turun: [
      'DROP INDEX kejadian_cari_kedatangan',
      'DROP INDEX kejadian_kedatangan',
      'ALTER TABLE kejadian DROP COLUMN kedatangan_id',
    ],
  },
];

function siapkanPencatat(db) {
  db.exec(`CREATE TABLE IF NOT EXISTS ${TABEL_MIGRASI} (
             versi      INTEGER PRIMARY KEY,
             dijalankan TEXT NOT NULL DEFAULT (datetime('now'))
           )`);
}

/** Versi skema basis data ini; 0 berarti belum ada tabel isi apa pun. */
export function versi(db) {
  siapkanPencatat(db);
  const baris = db.prepare(`SELECT max(versi) AS v FROM ${TABEL_MIGRASI}`).get();
  return baris?.v ?? 0;
}

/** Jalankan migrasi naik sampai `sampai` (bawaan: versi terbaru). Yang sudah terpasang dilewati. */
export function naik(db, sampai = VERSI_SKEMA) {
  siapkanPencatat(db);
  const sekarang = versi(db);
  for (const langkah of MIGRASI) {
    if (langkah.versi <= sekarang || langkah.versi > sampai) continue;
    for (const perintah of langkah.naik) db.exec(perintah);
    db.prepare(`INSERT INTO ${TABEL_MIGRASI} (versi) VALUES (?)`).run(langkah.versi);
  }
  return versi(db);
}

/** Jalankan migrasi turun sampai tinggal versi `sampai` (bawaan: 0, yaitu kosong). */
export function turun(db, sampai = 0) {
  siapkanPencatat(db);
  for (const langkah of [...MIGRASI].reverse()) {
    if (langkah.versi <= sampai || langkah.versi > versi(db)) continue;
    for (const perintah of langkah.turun) db.exec(perintah);
    db.prepare(`DELETE FROM ${TABEL_MIGRASI} WHERE versi = ?`).run(langkah.versi);
  }
  return versi(db);
}

/**
 * Daftar "tabel.kolom" dari semua tabel isi, terurut. Dipakai uji migrasi bolak-balik untuk membandingkan
 * susunan sebelum dan sesudah, dan tidak memuat tabel pencatat migrasi.
 */
export function susunan(db) {
  const tabel = db.prepare(
    `SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' AND name <> ?`,
  ).all(TABEL_MIGRASI);
  const kolom = [];
  for (const { name } of tabel) {
    for (const k of db.prepare(`PRAGMA table_info(${name})`).all()) kolom.push(`${name}.${k.name}`);
  }
  return kolom.sort();
}

/**
 * Buka basis data (jalur berkas, atau ':memory:') dan pasang skema terbaru.
 * Kunci asing dinyalakan, karena bawaan SQLite adalah mati — tanpa itu, kendaraan bisa menunjuk gerbang yang
 * tidak ada, dan pagar "semua data menempel pada gerbang" (K67) hanya ada di atas kertas.
 */
export function buka(jalur) {
  const db = new DatabaseSync(jalur);
  db.exec('PRAGMA foreign_keys = ON');
  naik(db);
  return db;
}

/**
 * Buka basis data dan pasang skema HANYA sampai versi tertentu. Dipakai uji migrasi, supaya naik dari basis lama
 * yang sudah berisi data benar-benar dicoba, bukan hanya dari basis kosong.
 * Versi yang tidak ada ditolak, supaya salah tulis tidak menghasilkan basis setengah jadi yang terlihat normal.
 */
export function bukaVersi(jalur, sampai) {
  if (!MIGRASI.some((l) => l.versi === sampai)) {
    const ada = MIGRASI.map((l) => l.versi).join(', ');
    throw new Error(`versi skema ${sampai} tidak ada; yang ada: ${ada}`);
  }
  const db = new DatabaseSync(jalur);
  db.exec('PRAGMA foreign_keys = ON');
  naik(db, sampai);
  return db;
}
