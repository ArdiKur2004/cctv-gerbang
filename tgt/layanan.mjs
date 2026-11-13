// Layanan TGT: grup, gerbang, kendaraan, tamu. Rencana T1, spec specs/2026-10-26-tgt-versi-1.md.
//
// Aturan produk ditegakkan DI SINI, bukan hanya di layar, supaya layar mana pun — PWA, layar satpam, atau
// pemanggil lain nanti — tidak bisa menembusnya.
import { randomBytes } from 'node:crypto';

/**
 * Jenis kendaraan yang diterima versi 1: hanya roda 4 ke atas (K65, owner 26 Okt).
 * DAFTAR PUTIH, bukan daftar larangan: jenis yang belum dikenal ikut ditolak, jadi ia gagal ke arah membatasi.
 * Motor menyusul di versi 2; jangan menambahkannya di sini tanpa keputusan owner.
 */
export const JENIS_KENDARAAN = Object.freeze(['mobil', 'pikap', 'truk', 'bus']);

/** Jenis grup yang diterima: pendaftaran pribadi atau perusahaan (alur owner langkah 1). */
export const JENIS_GRUP = Object.freeze(['pribadi', 'perusahaan']);

const STATUS_GERBANG_AWAL = 'belum_aktif';

export class GalatLayanan extends Error {
  constructor(pesan) {
    super(pesan);
    this.name = 'GalatLayanan';
  }
}

function wajibTeks(nilai, namaIsian) {
  const teks = typeof nilai === 'string' ? nilai.trim() : '';
  if (!teks) throw new GalatLayanan(`${namaIsian} wajib diisi`);
  return teks;
}

function bolehKosong(nilai) {
  const teks = typeof nilai === 'string' ? nilai.trim() : '';
  return teks || null;
}

/**
 * Bentuk baku plat nomor: huruf besar, tanpa spasi dan tanda baca.
 * Dipakai untuk menyimpan DAN membandingkan, supaya "b 1234 abc", "B-1234-ABC", dan "B1234ABC" adalah satu
 * kendaraan yang sama. Bentuk ini juga yang keluar dari mesin baca plat, jadi pencocokan di T6 tidak perlu
 * menebak ejaan.
 */
export function normalkanPlat(plat) {
  const bersih = String(plat ?? '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (!bersih) throw new GalatLayanan('plat nomor wajib diisi');
  return bersih;
}

function periksaJenisKendaraan(jenis) {
  if (typeof jenis === 'string' && JENIS_KENDARAAN.includes(jenis)) return jenis;
  if (typeof jenis === 'string' && jenis.trim().toLowerCase() === 'motor') {
    throw new GalatLayanan('jenis "motor" belum didukung; motor menyusul di versi 2');
  }
  throw new GalatLayanan(
    `jenis kendaraan "${jenis ?? ''}" tidak dikenal; versi 1 hanya menerima ${JENIS_KENDARAAN.join(', ')}`,
  );
}

function periksaLamaHari(lamaHari) {
  if (!Number.isInteger(lamaHari) || lamaHari < 1) {
    throw new GalatLayanan('lama kunjungan wajib bilangan bulat minimal 1 hari');
  }
  return lamaHari;
}

// Kode undangan dibaca dan diucapkan orang, jadi huruf dan angka yang mudah tertukar (0/O, 1/I) dibuang.
const HURUF_KODE = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

function kodeUndangan(panjang = 6) {
  const acak = randomBytes(panjang);
  let kode = '';
  for (const b of acak) kode += HURUF_KODE[b % HURUF_KODE.length];
  return kode;
}

// Kode undangan harus unik di tabelnya. Peluang bentrok kecil, tetapi "kecil" bukan "tidak ada": coba beberapa kali.
function kodeUnik(db, tabel) {
  for (let i = 0; i < 10; i += 1) {
    const kode = kodeUndangan();
    const ada = db.prepare(`SELECT 1 FROM ${tabel} WHERE kode_undangan = ?`).get(kode);
    if (!ada) return kode;
  }
  throw new GalatLayanan('gagal membuat kode undangan yang unik');
}

// ─── Grup ───────────────────────────────────────────────────────────────────────────────────────────

export function buatGrup(db, { nama, jenis, kodeUndangan: kode } = {}) {
  const namaBersih = wajibTeks(nama, 'nama grup');
  if (!JENIS_GRUP.includes(jenis)) {
    throw new GalatLayanan(`jenis grup "${jenis ?? ''}" tidak dikenal; pilihannya ${JENIS_GRUP.join(' atau ')}`);
  }
  const kodeDipakai = kode ? wajibTeks(kode, 'kode undangan').toUpperCase() : kodeUnik(db, 'grup');
  const { lastInsertRowid } = db
    .prepare('INSERT INTO grup (nama, jenis, kode_undangan) VALUES (?, ?, ?)')
    .run(namaBersih, jenis, kodeDipakai);
  return grup(db, lastInsertRowid);
}

export function grup(db, id) {
  return db.prepare('SELECT * FROM grup WHERE id = ?').get(id);
}

/** Langkah 2 alur owner: ikut grup lain dengan kode undangannya. */
export function grupDariKode(db, kode) {
  const bersih = String(kode ?? '').trim().toUpperCase();
  if (!bersih) return undefined;
  return db.prepare('SELECT * FROM grup WHERE kode_undangan = ?').get(bersih);
}

// ─── Gerbang ────────────────────────────────────────────────────────────────────────────────────────

/**
 * Gerbang adalah satuan utama (K67): ia punya nama DAN alamat, dan semua kendaraan, tamu, serta catatan
 * menempel padanya. Gerbang baru lahir "belum_aktif", karena alatnya belum terpasang — pemasangannya
 * dikerjakan tim operasional IBE di luar aplikasi.
 */
export function buatGerbang(db, { grupId, nama, jenisLokasi, alamat, kota, koordinat, patokan } = {}) {
  const namaBersih = wajibTeks(nama, 'nama gerbang');
  const jenisBersih = wajibTeks(jenisLokasi, 'jenis lokasi');
  const alamatBersih = wajibTeks(alamat, 'alamat gerbang');
  const kotaBersih = wajibTeks(kota, 'kota');
  if (!grup(db, grupId)) throw new GalatLayanan('grup penaung gerbang tidak ditemukan');

  const { lastInsertRowid } = db.prepare(
    `INSERT INTO gerbang (grup_id, nama, jenis_lokasi, alamat, kota, koordinat, patokan, status)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(grupId, namaBersih, jenisBersih, alamatBersih, kotaBersih,
    bolehKosong(koordinat), bolehKosong(patokan), STATUS_GERBANG_AWAL);
  return gerbang(db, lastInsertRowid);
}

export function gerbang(db, id) {
  return db.prepare('SELECT * FROM gerbang WHERE id = ?').get(id);
}

export function gerbangGrup(db, grupId) {
  return db.prepare('SELECT * FROM gerbang WHERE grup_id = ? ORDER BY id').all(grupId);
}

/** Dipakai sesudah tim operasional memasang dan menyambungkan alatnya. */
export function aktifkanGerbang(db, id) {
  if (!gerbang(db, id)) throw new GalatLayanan('gerbang tidak ditemukan');
  db.prepare("UPDATE gerbang SET status = 'aktif' WHERE id = ?").run(id);
  return gerbang(db, id);
}

function wajibGerbang(db, gerbangId) {
  const g = gerbang(db, gerbangId);
  if (!g) throw new GalatLayanan('gerbang tidak ditemukan');
  return g;
}

// ─── Kendaraan ──────────────────────────────────────────────────────────────────────────────────────

export function daftarkanKendaraan(
  db,
  { gerbangId, jenis, merek, warna, plat, atasNama, unit, penggunaId } = {},
) {
  wajibGerbang(db, gerbangId);
  const jenisBersih = periksaJenisKendaraan(jenis);
  const platBersih = normalkanPlat(plat);
  const atasNamaBersih = wajibTeks(atasNama, 'atas nama');

  if (cariKendaraanPlat(db, gerbangId, platBersih)) {
    throw new GalatLayanan(`plat ${platBersih} sudah terdaftar di gerbang ini`);
  }
  const { lastInsertRowid } = db.prepare(
    `INSERT INTO kendaraan (gerbang_id, jenis, merek, warna, plat, atas_nama, unit, pengguna_id)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(gerbangId, jenisBersih, bolehKosong(merek), bolehKosong(warna), platBersih, atasNamaBersih,
    bolehKosong(unit), penggunaId ?? null);
  return kendaraan(db, lastInsertRowid);
}

export function kendaraan(db, id) {
  return db.prepare('SELECT * FROM kendaraan WHERE id = ?').get(id);
}

/** Kendaraan dihapus betulan, bukan ditandai: daftar izin yang menyimpan baris mati menyesatkan satpam. */
export function hapusKendaraan(db, id) {
  // Kejadian lama tetap ada (masa simpannya sendiri), tetapi tautannya diputus supaya tidak menunjuk ke
  // kendaraan yang sudah tidak ada — alasan yang sama dengan penghapusan tamu di tgt/simpan.mjs.
  db.prepare('UPDATE kejadian SET kendaraan_id = NULL WHERE kendaraan_id = ?').run(id);
  return db.prepare('DELETE FROM kendaraan WHERE id = ?').run(id).changes;
}

export function kendaraanGerbang(db, gerbangId) {
  return db.prepare('SELECT * FROM kendaraan WHERE gerbang_id = ? ORDER BY id').all(gerbangId);
}

/** Cari kendaraan terdaftar dari platnya, di dalam SATU gerbang saja (K67). */
export function cariKendaraanPlat(db, gerbangId, plat) {
  return db.prepare('SELECT * FROM kendaraan WHERE gerbang_id = ? AND plat = ?')
    .get(gerbangId, normalkanPlat(plat));
}

// ─── Tamu ───────────────────────────────────────────────────────────────────────────────────────────

/**
 * Langkah 5–8 alur owner. Kendaraan tamu melewati pagar jenis yang sama dengan kendaraan tetap, karena
 * gerbangnya satu dan sama. Tamu tidak punya "atas nama": yang bertanggung jawab adalah pengundangnya.
 */
export function tambahTamu(
  db,
  { gerbangId, nama, keperluan, jenis, merek, warna, plat, lamaHari, diundangOleh, pengundangId } = {},
) {
  wajibGerbang(db, gerbangId);
  const namaBersih = wajibTeks(nama, 'nama tamu');
  const jenisBersih = periksaJenisKendaraan(jenis);
  const platBersih = normalkanPlat(plat);
  const lama = periksaLamaHari(lamaHari);

  const { lastInsertRowid } = db.prepare(
    `INSERT INTO tamu (gerbang_id, nama, keperluan, jenis, merek, warna, plat, lama_hari, kode_undangan,
                       diundang_oleh, pengundang_id)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(gerbangId, namaBersih, bolehKosong(keperluan), jenisBersih, bolehKosong(merek), bolehKosong(warna),
    platBersih, lama, kodeUnik(db, 'tamu'), bolehKosong(diundangOleh), pengundangId ?? null);
  return tamu(db, lastInsertRowid);
}

export function tamu(db, id) {
  return db.prepare('SELECT * FROM tamu WHERE id = ?').get(id);
}

export function hapusTamu(db, id) {
  db.prepare('UPDATE kejadian SET tamu_id = NULL WHERE tamu_id = ?').run(id);
  db.prepare('DELETE FROM kunjungan WHERE tamu_id = ?').run(id);
  return db.prepare('DELETE FROM tamu WHERE id = ?').run(id).changes;
}

export function tamuGerbang(db, gerbangId) {
  return db.prepare('SELECT * FROM tamu WHERE gerbang_id = ? ORDER BY id').all(gerbangId);
}

export function tamuDariKode(db, kode) {
  const bersih = String(kode ?? '').trim().toUpperCase();
  if (!bersih) return undefined;
  return db.prepare('SELECT * FROM tamu WHERE kode_undangan = ?').get(bersih);
}

// ⛔ `cariTamuPlat()` DICABUT di Rencana T10, bukan sekadar tak terpakai. Ia mengembalikan tamu TERBARU
// berplat itu tanpa melihat apakah kunjungannya masih terbuka — yaitu aturan yang sudah terbukti salah dan
// sudah diperbaiki di `catatKejadian` (lihat komentarnya: tanpa itu kunjungan tamu lama tersangkut "di dalam"
// selamanya dan angka beranda ikut salah). Tidak ada satu pun pemanggil, uji pun tidak, jadi membiarkannya
// terekspor hanya mengundang orang memakainya lagi dan mengembalikan bug itu. Yang benar: `tamuBerplat()`
// lalu pilih yang kunjungannya terbuka.

/** Semua tamu berplat ini di gerbang ini, yang terbaru lebih dulu. Plat tamu boleh terdaftar lebih dari sekali:
 *  kurir yang sama bisa diundang berulang kali oleh orang yang berbeda. */
function tamuBerplat(db, gerbangId, plat) {
  return db.prepare('SELECT * FROM tamu WHERE gerbang_id = ? AND plat = ? ORDER BY id DESC')
    .all(gerbangId, normalkanPlat(plat));
}

// ─── Kejadian keluar masuk ──────────────────────────────────────────────────────────────────────────

/**
 * Arah kejadian. Daftar putih: arah yang tidak dikenal ditolak, bukan disimpan apa adanya, supaya angka
 * dashboard tidak pelan-pelan diisi nilai yang tak pernah dihitung siapa pun.
 */
export const ARAH = Object.freeze(['masuk', 'keluar']);

const STATUS_DI_DALAM = 'di_dalam';
const STATUS_SELESAI = 'selesai';
const STATUS_LEWAT_BATAS = 'lewat_batas';

const MILIDETIK_SEHARI = 24 * 60 * 60 * 1000;

/**
 * Waktu kejadian disimpan apa adanya sebagai teks ISO jam setempat ('2026-10-26T08:00:00'), karena itu yang
 * dibaca orang di layar gerbang dan itu pula yang dikelompokkan ringkasan jam. Jangan diubah ke UTC: jam sibuk
 * pagi di Surabaya tidak boleh bergeser tujuh jam di dashboard.
 */
// Bentuknya DIPAKSA, bukan sekadar diharapkan: ringkasanJam memotong huruf ke-12 dan ke-13 sebagai jam, jadi
// bentuk lain ("2026-10-26", "2026-10-26 08:00") akan membuat angka dashboard salah tanpa ada yang mengeluh.
const BENTUK_WAKTU = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/;

function jamSetempatSekarang() {
  const sekarang = new Date();
  const geser = new Date(sekarang.getTime() - sekarang.getTimezoneOffset() * 60 * 1000);
  return geser.toISOString().slice(0, 19);
}

/**
 * Bentuk baku waktu kejadian: `2026-10-26T08:00:00` jam setempat. Kosong berarti "sekarang".
 *
 * DIEKSPOR sejak Rencana T9 karena `akses.bacaanGerbang` harus menormalkan waktunya dengan cara yang SAMA
 * PERSIS sebelum mencari kedatangan yang berjalan. Penormalan yang berbeda sedikit saja membuat pencarian
 * dan penyimpanan memakai waktu yang tidak sama, dan pengelompokan bingkai rusak diam-diam.
 */
export function waktuBaku(waktu) {
  if (waktu instanceof Date) {
    const geser = new Date(waktu.getTime() - waktu.getTimezoneOffset() * 60 * 1000);
    return geser.toISOString().slice(0, 19);
  }
  const teks = typeof waktu === 'string' ? waktu.trim() : '';
  if (!teks) return jamSetempatSekarang();

  const bagian = BENTUK_WAKTU.exec(teks);
  if (!bagian) {
    throw new GalatLayanan(`waktu "${teks}" tidak terbaca; bentuknya harus 2026-10-26T08:00:00 (jam setempat)`);
  }
  const lengkap = bagian[6] ? teks : `${teks}:00`;
  if (Number.isNaN(new Date(lengkap).getTime())) {
    throw new GalatLayanan(`waktu "${teks}" bukan tanggal yang ada`);
  }
  return lengkap;
}

function periksaArah(arah) {
  if (typeof arah === 'string' && ARAH.includes(arah)) return arah;
  throw new GalatLayanan(`arah "${arah ?? ''}" tidak dikenal; pilihannya ${ARAH.join(' atau ')}`);
}

function kunjunganTerbuka(db, tamuId) {
  return db.prepare(
    `SELECT * FROM kunjungan WHERE tamu_id = ? AND keluar IS NULL ORDER BY id DESC`,
  ).get(tamuId);
}

/**
 * Status kunjungan yang ditutup. Batasnya JAM masuk + lama kunjungan, bukan tanggal kalender: tamu yang masuk
 * jam 23:00 dengan izin 1 hari belum lewat batas saat keluar jam 10:00 esok harinya.
 */
function statusKeluar(masuk, keluar, lamaHari) {
  const batas = new Date(masuk).getTime() + lamaHari * MILIDETIK_SEHARI;
  return new Date(keluar).getTime() > batas ? STATUS_LEWAT_BATAS : STATUS_SELESAI;
}

/**
 * Jendela "satu kedatangan" dalam detik (Rencana T9, persetujuan owner 26 Okt).
 *
 * Kamera gerbang menghasilkan belasan bingkai per kendaraan. Bacaan atas plat yang sama, di gerbang yang sama,
 * arah yang sama, di dalam jendela ini dihitung sebagai SATU kedatangan.
 *
 * ⛔ BATAS KESELAMATAN YANG DISETUJUI OWNER: di dalam jendela ini, mesin tidak bisa membedakan "mobil yang
 * sama masih di depan kamera" dari "mobil kedua dengan plat tiruan". Yang membatasi risikonya: jendelanya
 * pendek, bingkai lanjutan TIDAK pernah menghasilkan putusan baru (ia mengembalikan putusan bingkai pertama),
 * dan gerbang untuk plat itu memang sudah terbuka. Memperpanjangnya adalah keputusan owner.
 */
export const JENDELA_KEDATANGAN_DETIK = 20;

/** Jendela yang berlaku. Nilai yang tidak masuk akal memakai bawaan — jendela raksasa akan MENELAN kendaraan
 *  yang benar-benar datang dua kali, jadi arah gagalnya adalah jendela yang pendek, bukan yang panjang. */
export function jendelaKedatangan() {
  const teks = String(process.env.TGT_JENDELA_KEDATANGAN ?? '').trim();
  if (!/^[1-9]\d*$/.test(teks)) return JENDELA_KEDATANGAN_DETIK;
  const n = Number(teks);
  // Lebih dari sepuluh menit bukan "satu kedatangan" lagi, itu menyembunyikan kunjungan kedua.
  return n >= 1 && n <= 600 ? n : JENDELA_KEDATANGAN_DETIK;
}

/**
 * Kejadian pertama dari kedatangan yang sedang berjalan untuk plat ini, bila ada.
 *
 * Syaratnya SEMUA harus sama: gerbang, plat (sudah dinormalkan), dan arah. Gerbang yang berbeda tidak pernah
 * digabung — satu mobil bisa lewat dua gerbang milik satu grup dalam beberapa detik. Arah yang berbeda juga
 * tidak: masuk lalu keluar dua detik kemudian memang aneh, tetapi itu dua peristiwa nyata, dan
 * menggabungkannya akan menyembunyikan kendaraan yang berputar di gerbang.
 *
 * Bacaan TANPA PLAT tidak pernah digabung: menggabung dari waktu saja bisa menyatukan dua kendaraan tak
 * dikenal yang berbeda, dan itu lebih buruk daripada dua baris catatan.
 */
export function kedatanganBerjalan(db, { gerbangId, plat, arah, waktu }) {
  if (!plat) return undefined;
  const detik = jendelaKedatangan();
  return db.prepare(
    `SELECT k.* FROM kejadian k
      WHERE k.gerbang_id = ? AND k.plat = ? AND k.arah = ?
        AND k.waktu <= ?
        AND k.waktu >= strftime('%Y-%m-%dT%H:%M:%S', datetime(?, ?))
      ORDER BY k.waktu DESC, k.id DESC
      LIMIT 1`,
  ).get(gerbangId, plat, arah, waktu, waktu, `-${detik} seconds`);
}

/**
 * Catat satu kendaraan lewat. Yang platnya tak terbaca atau tak terdaftar TETAP dicatat tanpa tautan: itu
 * justru catatan yang dibutuhkan satpam, dan membuangnya akan menyembunyikan kegagalan mesin baca.
 *
 * Mengembalikan barisnya beserta `ulangan`: true bila ia bingkai lanjutan dari kedatangan yang sudah ada.
 */
export function catatKejadian(
  db,
  { gerbangId, waktu, arah, plat, yakin, ciriJenis, ciriWarna, ciriMerek,
    penanda, putusan, alasan, dibukaOleh } = {},
) {
  // Penanda dari kotak gerbang membuat pengiriman ulang aman: yang sudah ada dikembalikan apa adanya.
  const sudah = kejadianDariPenanda(db, penanda);
  if (sudah) return sudah;
  wajibGerbang(db, gerbangId);
  const arahBersih = periksaArah(arah);
  const waktuBersih = waktuBaku(waktu);

  // Plat boleh kosong: bacaan bisa gagal, dan kejadiannya tetap nyata.
  const adaPlat = plat !== null && plat !== undefined && String(plat).trim() !== '';
  const platBersih = adaPlat ? normalkanPlat(plat) : null;

  // Kendaraan terdaftar lebih dulu: plat yang sudah menjadi penghuni tidak dihitung sebagai tamu.
  const kendaraan = platBersih ? cariKendaraanPlat(db, gerbangId, platBersih) : undefined;
  // Bila satu plat terdaftar sebagai beberapa tamu, yang berlaku adalah yang kunjungannya masih TERBUKA.
  // Tanpa ini, kunjungan tamu lama tersangkut "di dalam" selamanya dan angka dashboard ikut salah.
  const calonTamu = !kendaraan && platBersih ? tamuBerplat(db, gerbangId, platBersih) : [];
  const tamu = calonTamu.find((t) => kunjunganTerbuka(db, t.id)) ?? calonTamu[0];

  // ⛔ Dicari SEBELUM barisnya disisipkan. Lihat komentar di bawah: pencarian sesudah insert menemukan baris
  // ini sendiri, dan bingkai sebelumnya tidak pernah terlihat.
  const berjalan = kedatanganBerjalan(db, {
    gerbangId, plat: platBersih, arah: arahBersih, waktu: waktuBersih,
  });

  const { lastInsertRowid } = db.prepare(
    `INSERT INTO kejadian
       (gerbang_id, waktu, arah, plat, yakin, ciri_jenis, ciri_warna, ciri_merek, kendaraan_id, tamu_id,
        penanda, putusan, alasan, dibuka_oleh)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(gerbangId, waktuBersih, arahBersih, platBersih,
    typeof yakin === 'number' ? yakin : null,
    bolehKosong(ciriJenis), bolehKosong(ciriWarna), bolehKosong(ciriMerek),
    kendaraan?.id ?? null, tamu?.id ?? null,
    bolehKosong(penanda), bolehKosong(putusan), bolehKosong(alasan), dibukaOleh ?? null);

  if (tamu) {
    const terbuka = kunjunganTerbuka(db, tamu.id);
    if (arahBersih === 'masuk' && !terbuka) {
      // Bacaan ganda di gerbang tidak boleh menjadi dua kunjungan, jadi kunjungan baru hanya dibuka bila
      // tidak ada yang masih terbuka.
      db.prepare('INSERT INTO kunjungan (tamu_id, masuk, keluar, status) VALUES (?, ?, NULL, ?)')
        .run(tamu.id, waktuBersih, STATUS_DI_DALAM);
    } else if (arahBersih === 'keluar' && terbuka) {
      db.prepare('UPDATE kunjungan SET keluar = ?, status = ? WHERE id = ?')
        .run(waktuBersih, statusKeluar(terbuka.masuk, waktuBersih, tamu.lama_hari), terbuka.id);
    }
    // Keluar tanpa catatan masuk tidak membuat kunjungan: menebak jam masuk akan memalsukan catatan.
  }

  // Pengelompokan kedatangan (Rencana T9). `berjalan` SUDAH dicari sebelum baris ini disisipkan — kalau
  // dicari sesudahnya, pencarian itu menemukan BARIS INI SENDIRI (waktu dan id paling baru) dan bingkai
  // sebelumnya tidak pernah terlihat. Cacat itu sempat ada saat berkas ini ditulis.
  const indukId = berjalan ? (berjalan.kedatangan_id ?? berjalan.id) : Number(lastInsertRowid);
  db.prepare('UPDATE kejadian SET kedatangan_id = ? WHERE id = ?').run(indukId, lastInsertRowid);

  const baris = db.prepare('SELECT * FROM kejadian WHERE id = ?').get(lastInsertRowid);
  return { ...baris, ulangan: indukId !== Number(lastInsertRowid) };
}

/**
 * Di mana tiap plat berada sekarang, menurut kejadian terakhirnya di gerbang ini.
 * Yang belum pernah tercatat dianggap **di luar**: itu arah yang aman, karena satu-satunya akibatnya adalah
 * ia dianggap masuk akal untuk MASUK, bukan untuk keluar dari tempat yang belum pernah ia datangi.
 */
export function statusPlat(db, gerbangId) {
  const baris = db.prepare(
    `SELECT plat, arah FROM kejadian
      WHERE gerbang_id = ? AND plat IS NOT NULL
      ORDER BY waktu, id`,
  ).all(gerbangId);
  const peta = new Map();
  for (const k of baris) peta.set(k.plat, k.arah === 'masuk' ? 'di_dalam' : 'di_luar');
  return peta;
}

/**
 * Daftar izin untuk kotak di gerbang: plat, jenis, dan status. **Tanpa nama orang dan tanpa nomor WhatsApp** —
 * daftar ini disalin ke perangkat di gerbang untuk dipakai saat internet putus, dan perangkat di gerbang tidak
 * membutuhkan data pribadi siapa pun untuk memutuskan membuka.
 */
export function daftarIzin(db, gerbangId) {
  const status = statusPlat(db, gerbangId);
  // `jenis` di sini = penghuni atau tamu. `jenisKendaraan` = mobil/pikap/truk/bus, dipakai membandingkan
  // dengan jenis yang dibaca kamera (T6). Keduanya sengaja bernama beda supaya tidak pernah tertukar.
  const penghuni = db.prepare('SELECT plat, jenis FROM kendaraan WHERE gerbang_id = ?').all(gerbangId)
    .map((k) => ({ plat: k.plat, jenis: 'penghuni', jenisKendaraan: k.jenis }));
  const tamu = db.prepare('SELECT plat, jenis FROM tamu WHERE gerbang_id = ?').all(gerbangId)
    .map((t) => ({ plat: t.plat, jenis: 'tamu', jenisKendaraan: t.jenis }));
  // Plat yang terdaftar sebagai keduanya dihitung sebagai penghuni: itu yang lebih kuat haknya.
  const peta = new Map();
  for (const i of [...tamu, ...penghuni]) peta.set(i.plat, i);
  return [...peta.values()].map((i) => ({ ...i, status: status.get(i.plat) ?? 'di_luar' }));
}

/**
 * Angka ubin beranda untuk satu gerbang pada satu tanggal.
 *
 * `diDalam` dihitung dari status plat (kejadian terakhir), bukan dari selisih masuk dan keluar: selisih akan
 * salah begitu satu kejadian terlewat kamera, dan angka yang salah di beranda lebih buruk daripada tidak ada
 * angka, karena ia terlihat seperti kebenaran.
 */
export function ubinBeranda(db, gerbangId, tanggal) {
  // count(DISTINCT kedatangan_id), bukan count(*): satu kendaraan terlihat di belasan bingkai, dan angka yang
  // menghitung bingkai membuat beranda melaporkan 5 mobil masuk untuk satu mobil (Rencana T9).
  const hitung = (arah) => db.prepare(
    `SELECT count(DISTINCT kedatangan_id) AS n FROM kejadian
      WHERE gerbang_id = ? AND arah = ? AND substr(waktu, 1, 10) = ?`,
  ).get(gerbangId, arah, tanggal).n;

  let diDalam = 0;
  for (const status of statusPlat(db, gerbangId).values()) if (status === 'di_dalam') diDalam += 1;

  const lewatBatas = db.prepare(
    `SELECT count(*) AS n FROM kunjungan
      JOIN tamu ON tamu.id = kunjungan.tamu_id
     WHERE tamu.gerbang_id = ? AND kunjungan.status = 'lewat_batas'`,
  ).get(gerbangId).n;

  return { diDalam, masukHariIni: hitung('masuk'), keluarHariIni: hitung('keluar'), lewatBatas };
}

export function kejadianDariPenanda(db, penanda) {
  if (!penanda) return undefined;
  return db.prepare('SELECT * FROM kejadian WHERE penanda = ?').get(penanda);
}

export function kejadianGerbang(db, gerbangId) {
  return db.prepare('SELECT * FROM kejadian WHERE gerbang_id = ? ORDER BY waktu, id').all(gerbangId);
}

export function kunjunganTamu(db, tamuId) {
  return db.prepare('SELECT * FROM kunjungan WHERE tamu_id = ? ORDER BY id').all(tamuId);
}

/**
 * Angka dashboard: masuk dan keluar per jam untuk satu gerbang pada satu tanggal ('2026-10-26').
 * Selalu 24 baris, termasuk jam yang kosong, supaya grafiknya tidak memadat dan jam lengang tetap terlihat.
 */
export function ringkasanJam(db, gerbangId, tanggal) {
  const baris = Array.from({ length: 24 }, (_, jam) => ({ jam, masuk: 0, keluar: 0 }));
  // Kedatangan dihitung menurut jam BINGKAI PERTAMANYA, bukan jam tiap bingkai: kendaraan yang bingkainya
  // menyeberang pergantian jam tidak boleh terhitung di dua jam sekaligus (Rencana T9).
  const hitungan = db.prepare(
    `SELECT CAST(substr(pertama.waktu, 12, 2) AS INTEGER) AS jam, pertama.arah, count(*) AS n
       FROM (SELECT DISTINCT kedatangan_id FROM kejadian
              WHERE gerbang_id = ? AND substr(waktu, 1, 10) = ?) AS d
       JOIN kejadian AS pertama ON pertama.id = d.kedatangan_id
      GROUP BY jam, pertama.arah`,
  ).all(gerbangId, tanggal);
  for (const h of hitungan) {
    if (h.jam >= 0 && h.jam < 24) baris[h.jam][h.arah] += h.n;
  }
  return baris;
}
