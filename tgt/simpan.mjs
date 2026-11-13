// Masa simpan data TGT. Rencana T3, keputusan owner K71 ("data tidak boleh di simpan semua").
//
// ⛔ Masa simpan yang hanya tertulis di spec tidak menghapus apa pun. Berkas ini yang benar-benar menghapus.
//
// Angkanya DIBACA dari pengaturan, tidak disalin ke sini: angka yang disalin hidup lebih lama daripada angka yang
// benar, dan masa simpan data pribadi akan berubah sesudah diperiksa ahli hukum (spec §8, B9).
import fs from 'node:fs';
import path from 'node:path';

import { pengaturan, SELAMANYA } from './pengaturan.mjs';

export { SELAMANYA };

/**
 * Masa simpan dalam hari, atau `SELAMANYA` (null) yang berarti tidak pernah dihapus.
 *
 * ⛔ K74 (owner, 26 Okt): **semua data wajib disimpan.** Bawaannya SELAMANYA untuk ketiga jenis. Angka hanya
 * berlaku bila ada yang menuliskannya dengan sengaja di `TGT_SIMPAN_*`.
 */
export function masaSimpan() {
  const atur = pengaturan();
  const periksa = (nilai) => (Number.isInteger(nilai) && nilai >= 1 ? nilai : SELAMANYA);
  return {
    foto: periksa(atur.simpanFoto),
    kejadian: periksa(atur.simpanKejadian),
    tamu: periksa(atur.simpanTamu),
  };
}

/** True bila ada setidaknya satu jenis data yang memang diminta dihapus sesudah sekian hari. */
export function adaYangDihapus(hari = masaSimpan()) {
  return [hari.foto, hari.kejadian, hari.tamu].some((h) => Number.isInteger(h) && h >= 1);
}

/**
 * Selang pembersihan. Enam jam: cukup sering supaya gerbang yang menyala terus tetap bersih tiap hari, cukup
 * jarang supaya ia tidak ikut membebani kotak gerbang yang kecil.
 */
export const SELANG_BERSIH_MS = 6 * 60 * 60 * 1000;

const batas = (hari) => `datetime('now', '-${Number(hari)} days')`;

/**
 * Hapus data yang sudah lewat masa simpannya. Mengembalikan jumlah yang dihapus per jenis.
 *
 * Yang TIDAK pernah dihapus di sini:
 * - kendaraan terdaftar penghuni — itu daftar izin, bukan catatan keluar masuk;
 * - tamu yang kunjungannya MASIH TERBUKA, walau sudah lama — menghapusnya membuat satpam kehilangan catatan
 *   siapa yang masih ada di dalam gerbang.
 */
export function bersihkan(db, hari = masaSimpan(), { jalurFoto } = {}) {
  const hasil = { kejadian: 0, tamu: 0, kunjungan: 0, foto: 0 };

  // ⛔ SELAMANYA diperiksa per jenis, dan DI SINI — bukan hanya di pemanggilnya. K74: semua data wajib
  // disimpan, jadi tiap jalur penghapusan punya pagarnya sendiri. Pemanggil yang lupa memeriksa tidak boleh
  // bisa menghapus apa pun.
  const simpanSelamanya = (h) => !Number.isInteger(h) || h < 1;

  if (!simpanSelamanya(hari.kejadian)) {
    hasil.kejadian = db.prepare(
      `DELETE FROM kejadian WHERE waktu < strftime('%Y-%m-%dT%H:%M:%S', ${batas(hari.kejadian)})`,
    ).run().changes;
  }

  // Tamu yang boleh dihapus: tidak punya kunjungan terbuka, DAN kunjungan terakhirnya (atau, bila tidak pernah
  // masuk, saat ia dibuat) sudah lewat masa simpan.
  const calon = simpanSelamanya(hari.tamu) ? [] : db.prepare(
    `SELECT tamu.id
       FROM tamu
      WHERE NOT EXISTS (SELECT 1 FROM kunjungan k WHERE k.tamu_id = tamu.id AND k.keluar IS NULL)
        AND COALESCE(
              (SELECT max(k.keluar) FROM kunjungan k WHERE k.tamu_id = tamu.id),
              tamu.dibuat
            ) < ${batas(hari.tamu)}`,
  ).all().map((t) => t.id);

  for (const id of calon) {
    // Masa simpan tamu (bawaan 30 hari) lebih pendek daripada kejadian (90 hari), jadi saat tamu dihapus,
    // kejadiannya masih ada dan menunjuk kepadanya. Yang dipilih: TAUTANNYA DIPUTUS, kejadiannya tetap.
    // Nama dan undangan tamu tidak disimpan lebih lama dari perlunya (K71), sementara satpam tetap punya
    // catatan apa yang lewat gerbang. Tanpa baris ini, penghapusan gagal karena kunci asing — dan itulah yang
    // terjadi saat pembersih ini pertama dijalankan.
    db.prepare('UPDATE kejadian SET tamu_id = NULL WHERE tamu_id = ?').run(id);
    // Kunjungan lebih dulu: kunci asing menunjuk ke tamu, dan baris yatim adalah catatan yang tak bisa dibaca
    // siapa pun tetapi tetap memakan tempat.
    hasil.kunjungan += db.prepare('DELETE FROM kunjungan WHERE tamu_id = ?').run(id).changes;
    hasil.tamu += db.prepare('DELETE FROM tamu WHERE id = ?').run(id).changes;
  }

  if (!simpanSelamanya(hari.foto)) {
    hasil.foto = bersihkanFoto(jalurFoto ?? pengaturan().jalurFoto, hari.foto);
  }
  return hasil;
}

/**
 * Foto bukti kendaraan: dihapus menurut umur berkasnya. Folder yang belum ada bukan galat — foto baru masuk
 * sejak Rencana T6, dan pembersih ini sudah harus siap sebelum itu.
 *
 * ⛔ Hanya dipanggil bila masa simpan foto memang disetel. Pagar kedua ada di sini juga: masa simpan yang
 * bukan bilangan positif menghapus NOL berkas, bukan semuanya — `Date.now() - null * 86400000` adalah
 * `Date.now()`, yang akan menghapus SELURUH isi folder. Itu kegagalan paling mahal yang mungkin di berkas ini.
 */
function bersihkanFoto(folder, hari) {
  if (!Number.isInteger(hari) || hari < 1) return 0;
  let dihapus = 0;
  const batasMs = Date.now() - hari * 24 * 60 * 60 * 1000;
  let isi;
  try {
    isi = fs.readdirSync(folder, { withFileTypes: true });
  } catch {
    return 0;
  }
  for (const b of isi) {
    if (!b.isFile()) continue;
    const penuh = path.join(folder, b.name);
    try {
      if (fs.statSync(penuh).mtimeMs < batasMs) {
        fs.rmSync(penuh);
        dihapus += 1;
      }
    } catch {
      // Berkas yang sedang dipakai atau sudah hilang dilewati; ia akan terhapus di putaran berikutnya.
    }
  }
  return dihapus;
}

/**
 * Jalankan pembersih sekarang, lalu ulangi tiap `selangMs`. Rencana T10.
 *
 * ⛔ KENAPA INI ADA. Sampai Rencana T10, `bersihkan()` di atas **tidak dipanggil satu pun kode produksi** —
 * hanya oleh ujinya sendiri. Jadi masa simpan yang menurut K71 "ditegakkan di dalam kode" tidak menghapus apa
 * pun selama tujuh rencana, sementara 23 uji terus hijau. Fungsi yang benar tetapi tak pernah dipanggil
 * terlihat persis seperti fungsi yang bekerja.
 *
 * Tiga hal yang disengaja di sini:
 * - **Jalan sekali saat dinyalakan**, bukan menunggu selang pertama. Gerbang yang dinyalakan ulang tiap hari
 *   dengan selang 6 jam akan sama saja dengan tidak pernah bersih.
 * - **Pewaktunya `unref()`**. Prinsip #3: perkakas tidak boleh menahan mesin yang menjalankannya tetap hidup.
 * - **Galat ditangkap tetapi DICATAT.** Basis terkunci atau disk penuh tidak boleh menjatuhkan gerbang; tetapi
 *   galat yang ditelan berarti data pribadi menumpuk tanpa ada yang tahu.
 *
 * `bersih` bisa diganti HANYA untuk uji; pemanggil produksi memakai bawaannya.
 */
export function jadwalkanBersih(db, { jalurFoto, selangMs = SELANG_BERSIH_MS, bersih = bersihkan,
  catat = console.error } = {}) {
  // ⛔ K74 (owner, 26 Okt): semua data wajib disimpan. Bila tidak ada satu pun masa simpan yang disetel,
  // penjadwal ini TIDAK MENYALA sama sekali — bukan menyala lalu menghapus nol baris. Bedanya penting: pewaktu
  // yang hidup tiap 6 jam untuk tidak melakukan apa pun hanyalah beban, dan satu salah ketik di dalamnya bisa
  // mengubahnya menjadi penghapus. Keadaannya disebut di layar, supaya tidak ada yang menyangka ia bekerja.
  // Masa simpan dibaca SEKALI, di sini, lalu dipakai untuk semua putaran berikutnya.
  //
  // Dulu ia dibaca ulang tiap putaran, dan itu tidak konsisten: keputusan "menyala atau tidak" diambil dari
  // pengaturan saat server menyala, sementara "berapa harinya" bisa berubah di tengah jalan. Akibatnya satu
  // kalimat yang dicetak saat start-up tidak lagi menggambarkan apa yang dilakukan putaran-putaran sesudahnya —
  // dan pada data pribadi, kabar di layar yang tidak menggambarkan kenyataan adalah hal yang berbahaya.
  // Terlihat saat uji K74: putaran berikutnya diam-diam berhenti menghapus.
  const hari = masaSimpan();

  if (!adaYangDihapus(hari)) {
    catat('[tgt] masa simpan: SELAMANYA — semua data disimpan, tidak ada yang dihapus (K74). '
      + 'Untuk menyalakan penghapusan, setel TGT_SIMPAN_FOTO / TGT_SIMPAN_KEJADIAN / TGT_SIMPAN_TAMU.');
    return { pewaktu: undefined, pertama: undefined, hari, sekaliJalan: () => undefined, berhenti: () => {} };
  }

  const sebut = (h) => (Number.isInteger(h) && h >= 1 ? `${h} hari` : 'selamanya');
  catat(`[tgt] masa simpan AKTIF: foto ${sebut(hari.foto)}, kejadian ${sebut(hari.kejadian)}, `
    + `tamu ${sebut(hari.tamu)}. Yang lewat masa itu DIHAPUS.`);

  const sekaliJalan = () => {
    try {
      const h = bersih(db, hari, { jalurFoto });
      catat(
        `[tgt] masa simpan: ${h.kejadian} kejadian, ${h.tamu} tamu, ${h.kunjungan} kunjungan, `
        + `${h.foto} foto dihapus`,
      );
      return h;
    } catch (e) {
      // Disebut terang-terangan: kalau ini terus muncul, data pribadi menumpuk dan harus diperiksa orang.
      catat(`[tgt] pembersih masa simpan GAGAL, jadi data pribadi belum terhapus: ${e.message}`);
      return undefined;
    }
  };

  const pertama = sekaliJalan();
  const pewaktu = setInterval(sekaliJalan, selangMs);
  // Supaya `node` tetap bisa keluar sendiri. Pewaktu yang tidak di-unref meninggalkan proses yang hidup
  // selamanya, dan proses yatim seperti itulah yang pernah membekukan laptop ini (insiden 2026-09-03).
  pewaktu.unref();

  return { pewaktu, pertama, hari, sekaliJalan, berhenti: () => clearInterval(pewaktu) };
}
