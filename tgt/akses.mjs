// Pintu hak akses TGT. Rencana T2, spec specs/2026-10-26-tgt-versi-1.md §4.
//
// ⛔ SATU-SATUNYA pintu yang boleh dipakai lapisan web. `tgt/layanan.mjs` adalah lapisan data MENTAH tanpa hak
// akses — ia dipakai mesin gerbang, yang tidak punya pengguna. Kalau server memanggil `layanan.mjs` langsung,
// semua pagar di berkas ini terlewati tanpa satu pun uji menjadi merah; karena itu ada uji rantai di
// tgt/uji/server.test.mjs yang membaca sumber server dan gagal bila impor itu muncul.
//
// Sifat pagar ini:
// - GAGAL KE ARAH MENUTUP. Peran yang tidak dikenal, sesi yang tidak ada, atau grup yang tidak cocok = ditolak.
//   Daftar putih peran, bukan daftar larangan.
// - Peran selalu DIBACA DARI BASIS DATA, tidak pernah dari apa yang dikirim pemanggil.
// - Pesan penolakan untuk "tidak ada" dan "bukan milik Anda" SAMA, supaya tidak bisa dipakai menebak isi grup lain.
import * as layanan from './layanan.mjs';
import * as akun from './akun.mjs';
import { putuskan } from './putusan.mjs';
import { perluNotifikasi } from './notifikasi.mjs';

export class GalatAkses extends Error {
  constructor(pesan, kode) {
    super(pesan);
    this.name = 'GalatAkses';
    this.kode = kode;
  }
}

const PERLU_MASUK = () => new GalatAkses('silakan masuk dulu', 'perlu_masuk');
const TIDAK_BERHAK = () => new GalatAkses('Anda tidak berhak melakukan ini', 'ditolak');
// Satu pesan untuk "tidak ada" dan "bukan grup Anda".
const TIDAK_DITEMUKAN = () => new GalatAkses('gerbang atau grup tidak ditemukan', 'tidak_ditemukan');

/** Pengguna yang sedang masuk. Sesi yang menunjuk pengguna tak ada ditolak, bukan dibuatkan. */
function wajibMasuk(db, sesi) {
  const id = sesi?.penggunaId;
  if (!id) throw PERLU_MASUK();
  const orang = akun.pengguna(db, id);
  if (!orang) throw PERLU_MASUK();
  return orang;
}

/** Peran orang ini di grup itu, dibaca dari basis data. Bukan anggota = "tidak ditemukan", bukan "tidak berhak". */
function peranDiGrup(db, sesi, grupId) {
  const orang = wajibMasuk(db, sesi);
  const peran = akun.peranDi(db, grupId, orang.id);
  if (!peran) throw TIDAK_DITEMUKAN();
  return { orang, peran };
}

function peranDiGerbang(db, sesi, gerbangId) {
  const orang = wajibMasuk(db, sesi);
  const g = layanan.gerbang(db, gerbangId);
  // Gerbang yang tidak ada dan gerbang grup lain memberi galat yang SAMA.
  if (!g) throw TIDAK_DITEMUKAN();
  const peran = akun.peranDi(db, g.grup_id, orang.id);
  if (!peran) throw TIDAK_DITEMUKAN();
  return { orang, peran, gerbang: g };
}

function wajibPeran(peran, bolehkan) {
  if (!bolehkan.includes(peran)) throw TIDAK_BERHAK();
  return peran;
}

// Kode undangan adalah cara masuk grup: yang memegangnya bisa mengundang orang. Hanya pengelola yang melihatnya.
function tanpaKode(grup) {
  const { kode_undangan: _buang, ...sisa } = grup;
  return sisa;
}

// ─── Grup ───────────────────────────────────────────────────────────────────────────────────────────

/** Siapa pun yang sudah masuk boleh membuat grup; ia menjadi pengelolanya. */
export function buatGrup(db, sesi, data) {
  const orang = wajibMasuk(db, sesi);
  return akun.buatGrupBaru(db, orang.id, data);
}

/** Siapa pun yang sudah masuk boleh ikut grup, bila kode undangannya benar. */
export function ikutGrup(db, sesi, kode) {
  const orang = wajibMasuk(db, sesi);
  const hasil = akun.ikutGrup(db, orang.id, kode);
  return hasil.peran === 'pengelola' ? hasil : { ...hasil, grup: tanpaKode(hasil.grup) };
}

export function grupSaya(db, sesi) {
  const orang = wajibMasuk(db, sesi);
  return akun.grupSaya(db, orang.id).map((g) => (g.peran === 'pengelola' ? g : tanpaKode(g)));
}

/** Siapa yang sedang masuk. Tanpa hash sandi — `akun.pengguna` sudah membuangnya. */
export function sayaSiapa(db, sesi) {
  return wajibMasuk(db, sesi);
}

/** Daftar anggota memuat nomor WhatsApp = data pribadi, jadi hanya pengelola. */
export function anggotaGrup(db, sesi, grupId) {
  const { peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola']);
  return akun.anggotaGrup(db, grupId);
}

/**
 * Pengelola membuat anggota sendiri (K72): cukup emailnya, atau cukup NAMANYA saja sejak Rencana T8.
 * Untuk rumah pribadi anggotanya keluarga, untuk pabrik bisa PIC saja — bentuknya sama, yang berbeda hanya
 * berapa orangnya.
 */
export function tambahAnggota(db, sesi, grupId, data) {
  const { peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola']);
  return akun.tambahAnggota(db, grupId, data);
}

/**
 * Buat tautan masuk untuk satu anggota (Rencana T8). PENGELOLA SAJA.
 *
 * ⛔ Tautan ini sama kuatnya dengan sandi orang itu: yang memegangnya menjadi dia. Satpam adalah admin
 * gerbang, bukan pemilik warga, jadi ia tidak boleh membuatnya; penghuni yang bisa membuat tautan untuk
 * orang lain berarti bisa menjadi orang lain. Tandanya hanya dikembalikan di sini, sekali.
 */
export function buatUndanganMasuk(db, sesi, grupId, penggunaId) {
  const { orang, peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola']);
  return akun.buatUndanganMasuk(db, grupId, penggunaId, orang.id);
}

/**
 * Tukar tautan masuk dengan orangnya. SENGAJA TANPA SESI: tautan inilah yang menggantikan sandi, jadi
 * pemanggilnya memang belum punya sesi. Kode undangan grup dibuang dari jawabannya, karena yang masuk lewat
 * sini menjadi penghuni — dan kode itu adalah cara masuk grup bagi siapa pun yang memegangnya.
 */
export function tukarUndanganMasuk(db, tanda) {
  const hasil = akun.tukarUndanganMasuk(db, tanda);
  return { ...hasil, grup: tanpaKode(hasil.grup) };
}

export function keluarkanAnggota(db, sesi, grupId, penggunaId) {
  const { peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola']);
  return akun.keluarkanAnggota(db, grupId, penggunaId);
}

export function tetapkanPeran(db, sesi, grupId, penggunaId, peranBaru) {
  const { peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola']);
  return akun.tetapkanPeran(db, grupId, penggunaId, peranBaru);
}

// ─── Gerbang ────────────────────────────────────────────────────────────────────────────────────────

/** Membuat gerbang beserta alamatnya: pengelola grup itu saja (spec §4). */
export function buatGerbang(db, sesi, data = {}) {
  const { peran } = peranDiGrup(db, sesi, data.grupId);
  wajibPeran(peran, ['pengelola']);
  return layanan.buatGerbang(db, data);
}

/** Ketiga peran boleh membaca gerbang grupnya. */
export function lihatGerbang(db, sesi, gerbangId) {
  return peranDiGerbang(db, sesi, gerbangId).gerbang;
}

/** Semua gerbang dari semua grup yang orang ini ikuti. */
export function gerbangSaya(db, sesi) {
  const orang = wajibMasuk(db, sesi);
  return akun.grupSaya(db, orang.id).flatMap((g) => layanan.gerbangGrup(db, g.id));
}

/** Mengaktifkan gerbang sesudah alatnya terpasang: pengelola saja. */
export function aktifkanGerbang(db, sesi, gerbangId) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['pengelola']);
  return layanan.aktifkanGerbang(db, gerbangId);
}

// ─── Kendaraan ──────────────────────────────────────────────────────────────────────────────────────

/**
 * Penghuni hanya melihat miliknya. Saringan ini dipakai untuk DAFTAR maupun untuk MENGAMBIL SATU BUTIR —
 * pagar yang hanya menyaring daftar bisa ditembus dengan menebak nomor butirnya.
 */
const miliknya = (baris, kolom, orang) => baris?.[kolom] === orang.id;

export function kendaraanGerbang(db, sesi, gerbangId) {
  const { orang, peran } = peranDiGerbang(db, sesi, gerbangId);
  const semua = layanan.kendaraanGerbang(db, gerbangId);
  return peran === 'penghuni' ? semua.filter((k) => miliknya(k, 'pengguna_id', orang)) : semua;
}

export function kendaraan(db, sesi, kendaraanId) {
  const k = layanan.kendaraan(db, kendaraanId);
  if (!k) throw TIDAK_DITEMUKAN();
  const { orang, peran } = peranDiGerbang(db, sesi, k.gerbang_id);
  // Kendaraan orang lain menjawab "tidak ditemukan", bukan "tidak berhak": jawaban yang berbeda memberi tahu
  // penghuni bahwa kendaraan bernomor itu ada.
  if (peran === 'penghuni' && !miliknya(k, 'pengguna_id', orang)) throw TIDAK_DITEMUKAN();
  return k;
}

/**
 * Pengelola boleh mendaftarkan kendaraan atas nama siapa pun di grupnya; penghuni hanya atas namanya sendiri,
 * dan namanya diambil dari akunnya, bukan dari yang ia ketik. Satpam tidak boleh menambah (spec §4).
 */
export function tambahKendaraan(db, sesi, data = {}) {
  const { orang, peran } = peranDiGerbang(db, sesi, data.gerbangId);
  wajibPeran(peran, ['pengelola', 'penghuni']);

  const milikSendiri = peran === 'penghuni';
  return layanan.daftarkanKendaraan(db, {
    ...data,
    atasNama: milikSendiri ? orang.nama : (data.atasNama || orang.nama),
    penggunaId: milikSendiri ? orang.id : (data.penggunaId ?? null),
  });
}

export function hapusKendaraan(db, sesi, kendaraanId) {
  // kendaraan() sudah menolak milik orang lain untuk penghuni.
  const k = kendaraan(db, sesi, kendaraanId);
  const { peran } = peranDiGerbang(db, sesi, k.gerbang_id);
  wajibPeran(peran, ['pengelola', 'penghuni']);
  return layanan.hapusKendaraan(db, kendaraanId);
}

// ─── Tamu ───────────────────────────────────────────────────────────────────────────────────────────

// Kode undangan tamu adalah cara masuk gerbang. Yang perlu memegangnya hanya pengundangnya (untuk dikirim ke
// tamu) dan pengelola (yang bertanggung jawab atas gerbangnya). Sejak K72 satpam juga mendaftarkan tamu, dan
// ia melihat kode tamu yang IA SENDIRI daftarkan — bukan kode tamu penghuni lain.
function tamuTampak(t, peran, orang) {
  if (peran === 'pengelola' || miliknya(t, 'pengundang_id', orang)) return t;
  const { kode_undangan: _buang, ...sisa } = t;
  return sisa;
}

export function tamuGerbang(db, sesi, gerbangId) {
  const { orang, peran } = peranDiGerbang(db, sesi, gerbangId);
  const semua = layanan.tamuGerbang(db, gerbangId);
  const terlihat = peran === 'penghuni' ? semua.filter((t) => miliknya(t, 'pengundang_id', orang)) : semua;
  return terlihat.map((t) => tamuTampak(t, peran, orang));
}

export function tamu(db, sesi, tamuId) {
  const t = layanan.tamu(db, tamuId);
  if (!t) throw TIDAK_DITEMUKAN();
  const { orang, peran } = peranDiGerbang(db, sesi, t.gerbang_id);
  if (peran === 'penghuni' && !miliknya(t, 'pengundang_id', orang)) throw TIDAK_DITEMUKAN();
  return tamuTampak(t, peran, orang);
}

/**
 * K72: **satpam juga boleh** mendaftarkan tamu — ia admin TGT grupnya, dan dialah yang ada di gerbang saat
 * tamu datang tanpa diundang lebih dulu. Yang tetap bukan wewenangnya adalah daftar kendaraan penghuni.
 */
export function tambahTamu(db, sesi, data = {}) {
  const { orang, peran } = peranDiGerbang(db, sesi, data.gerbangId);
  wajibPeran(peran, ['pengelola', 'penghuni', 'satpam']);
  return layanan.tambahTamu(db, {
    ...data,
    pengundangId: orang.id,
    diundangOleh: orang.nama,
  });
}

export function hapusTamu(db, sesi, tamuId) {
  const t = tamu(db, sesi, tamuId);
  const { orang, peran } = peranDiGerbang(db, sesi, t.gerbang_id);
  wajibPeran(peran, ['pengelola', 'penghuni', 'satpam']);
  // Satpam boleh menghapus yang ia daftarkan sendiri, bukan tamu penghuni lain. Pengelola boleh semuanya.
  if (peran === 'satpam' && !miliknya(t, 'pengundang_id', orang)) throw TIDAK_BERHAK();
  return layanan.hapusTamu(db, tamuId);
}

// ─── Gerbang: daftar izin, bacaan, dan buka manual ──────────────────────────────────────────────────

/**
 * Daftar izin untuk dipakai kotak di gerbang, termasuk saat internet putus.
 * Hanya satpam dan pengelola: daftar ini memberi tahu plat siapa saja yang boleh masuk, dan penghuni tidak
 * perlu mengetahui plat tetangganya.
 */
export function daftarIzin(db, sesi, gerbangId) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['pengelola', 'satpam']);
  return layanan.daftarIzin(db, gerbangId);
}

/**
 * Catatan lalu lalang gerbang. Memuat plat semua orang, jadi bukan untuk dibaca sesama penghuni.
 */
export function kejadianTerbaru(db, sesi, gerbangId, batas = 50) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['pengelola', 'satpam']);
  const semua = layanan.kejadianGerbang(db, gerbangId);
  return semua.slice(-Math.max(1, batas)).reverse();
}

/**
 * Satu bacaan plat dari kotak di gerbang: diputuskan, lalu dicatat beserta putusan dan alasannya.
 *
 * ⛔ Fungsi ini TIDAK menggerakkan apa pun. Ia mengembalikan putusan untuk ditampilkan dan dicatat. Sampai
 * Fase 5 tidak ada keluaran relay sama sekali (CLAUDE.md §3), dan menyambungkannya butuh keputusan owner.
 */
/**
 * Periksa hak mengirim bacaan, TANPA mengirimkannya. Dipakai sebelum gambar dari kamera ditulis ke folder
 * bersama: gambar kendaraan tidak boleh masuk ke antrean hanya karena seseorang memanggil jalurnya.
 */
export function pastikanBolehBaca(db, sesi, gerbangId) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['satpam', 'pengelola']);
  return true;
}

export function bacaanGerbang(db, sesi, data = {}) {
  const { peran, gerbang: g } = peranDiGerbang(db, sesi, data.gerbangId);
  wajibPeran(peran, ['satpam', 'pengelola']);

  // Pengiriman ulang sesudah luring: yang sudah tercatat dikembalikan apa adanya, tidak diputuskan ulang.
  const sudah = layanan.kejadianDariPenanda(db, data.penanda);
  if (sudah) {
    return { putusan: sudah.putusan, alasan: sudah.alasan, plat: sudah.plat, kejadian: sudah, sudahAda: true };
  }

  /**
   * ⛔ BINGKAI LANJUTAN DARI KEDATANGAN YANG SAMA (Rencana T9, persetujuan owner 26 Okt: jendela 20 detik).
   *
   * Kamera gerbang menghasilkan belasan bingkai per kendaraan. Sebelum ini tiap bingkai diputuskan ulang, dan
   * akibatnya SETIAP mobil yang keluar menahan gerbang di bingkai keduanya: bingkai pertama membuat catatan
   * "sudah keluar", jadi bingkai kedua terlihat janggal dan aturan K73 menahannya. Di perumahan 150 mobil
   * sehari, itu 150 panggilan satpam palsu per hari.
   *
   * Yang dilakukan: putusan bingkai PERTAMA dikembalikan apa adanya. **Tidak ada putusan baru yang dibuat di
   * dalam jendela**, jadi tidak ada jalan yang bisa melonggarkan — bingkai lanjutan tidak bisa mengubah
   * `panggil_satpam` menjadi `buka`. Bacaannya tetap DICATAT (K74: semua data disimpan), hanya ditautkan ke
   * kedatangan yang sama dan tidak memicu notifikasi kedua.
   *
   * Batasnya, yang disetujui owner: di dalam jendela itu mesin tidak bisa membedakan "mobil yang sama masih di
   * depan kamera" dari "mobil kedua dengan plat tiruan". Yang membatasi risikonya adalah jendela yang pendek,
   * dan bahwa gerbang untuk plat itu memang sudah terbuka oleh bingkai pertama.
   */
  const platBaku = layanan.normalkanPlat(data.bacaan ?? '');
  // Waktunya dinormalkan dengan fungsi yang SAMA PERSIS dengan yang dipakai saat menyimpan. Jalur kamera
  // tidak mengirim waktu sama sekali (ia berarti "sekarang"), dan tanpa baris ini pencariannya menerima
  // undefined — jalur kamera menjawab 500 tanpa satu pun uji kedatangan menjadi merah.
  const waktuBaku = layanan.waktuBaku(data.waktu);
  const berjalan = platBaku ? layanan.kedatanganBerjalan(db, {
    gerbangId: data.gerbangId,
    plat: platBaku,
    arah: ['masuk', 'keluar'].includes(data.arah) ? data.arah : 'masuk',
    waktu: waktuBaku,
  }) : undefined;

  if (berjalan) {
    const lanjutan = layanan.catatKejadian(db, {
      gerbangId: data.gerbangId,
      waktu: waktuBaku,
      arah: ['masuk', 'keluar'].includes(data.arah) ? data.arah : 'masuk',
      plat: platBaku,
      yakin: data.yakin,
      ciriJenis: data.ciriJenis,
      ciriWarna: data.ciriWarna,
      ciriMerek: data.ciriMerek,
      penanda: data.penanda,
      // Putusan bingkai pertama DISALIN, bukan dihitung ulang.
      putusan: berjalan.putusan,
      alasan: berjalan.alasan,
    });
    return {
      putusan: berjalan.putusan,
      alasan: berjalan.alasan,
      plat: platBaku,
      kejadian: lanjutan,
      notifikasi: null,
      ulangan: true,
      sudahAda: false,
    };
  }

  const hasil = putuskan({
    bacaan: data.bacaan,
    ragu: data.ragu,
    arah: data.arah,
    jenisLokasi: g.jenis_lokasi,
    daftar: layanan.daftarIzin(db, data.gerbangId),
    // Jenis yang dibaca kamera (T6). Ia hanya menambah catatan; yang membuka tetap plat.
    jenisTerbaca: data.ciriJenis,
  });

  const kejadian = layanan.catatKejadian(db, {
    gerbangId: data.gerbangId,
    waktu: waktuBaku,
    // Arah yang tidak dikenal tetap harus tercatat: kejadiannya nyata walau putusannya menolak.
    arah: ['masuk', 'keluar'].includes(data.arah) ? data.arah : 'masuk',
    plat: hasil.plat,
    yakin: data.yakin,
    ciriJenis: data.ciriJenis,
    ciriWarna: data.ciriWarna,
    ciriMerek: data.ciriMerek,
    penanda: data.penanda,
    putusan: hasil.putusan,
    alasan: hasil.alasan,
  });

  // K72: yang janggal memanggil satpam. Penerimanya adalah perangkat yang berlangganan grup gerbang ini.
  // Kejadian tetap tercatat lebih dulu: notifikasi yang gagal tidak boleh membuat catatan ikut hilang.
  const pesan = perluNotifikasi({ ...kejadian, statusJanggal: hasil.statusJanggal, ciriJanggal: hasil.ciriJanggal });
  const notifikasi = pesan.perlu
    ? { ...pesan, penerima: langgananGrup(db, g.grup_id), kejadianId: kejadian.id }
    : null;

  return { ...hasil, kejadian, notifikasi, ulangan: false, sudahAda: false };
}

/**
 * Satpam membuka dengan tangan. Dicatat sebagai `dibuka_satpam`, BUKAN sebagai putusan mesin: siapa yang
 * memutuskan harus selalu bisa dibedakan saat catatan ini dibaca kembali kelak.
 */
export function bukaManual(db, sesi, { gerbangId, plat, arah, alasan, waktu } = {}) {
  const { orang, peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['satpam', 'pengelola']);
  const alasanBersih = typeof alasan === 'string' ? alasan.trim() : '';
  if (!alasanBersih) throw new layanan.GalatLayanan('alasan wajib diisi: satpam mempertanggungjawabkannya');

  return layanan.catatKejadian(db, {
    gerbangId,
    waktu,
    arah: ['masuk', 'keluar'].includes(arah) ? arah : 'masuk',
    plat,
    putusan: 'dibuka_satpam',
    alasan: `${alasanBersih} (dibuka ${orang.nama})`,
    dibukaOleh: orang.id,
  });
}

// ─── Dashboard (T7) ─────────────────────────────────────────────────────────────────────────────────

/**
 * Angka jam keluar masuk untuk grafik. Hanya satpam dan pengelola: angka ini dirangkum dari kejadian, yang
 * memuat plat semua orang, dan jam sibuk sebuah lokasi bukan hal yang perlu diketahui tiap penghuni.
 */
export function ringkasanJam(db, sesi, gerbangId, tanggal) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['pengelola', 'satpam']);
  return layanan.ringkasanJam(db, gerbangId, tanggal);
}

export function ubinBeranda(db, sesi, gerbangId, tanggal) {
  const { peran } = peranDiGerbang(db, sesi, gerbangId);
  wajibPeran(peran, ['pengelola', 'satpam']);
  return layanan.ubinBeranda(db, gerbangId, tanggal);
}

// ─── Langganan notifikasi (K72) ─────────────────────────────────────────────────────────────────────

/**
 * Daftarkan satu PERANGKAT untuk menerima notifikasi grup ini.
 *
 * Kuncinya alamat perangkat, bukan orangnya: satu orang bisa punya HP dan layar gerbang sekaligus, dan
 * perangkat yang sama mendaftar dua kali tidak boleh menerima dua kali.
 *
 * Hanya satpam dan pengelola. Catatan lalu lalang gerbang bukan untuk dibaca sesama penghuni, dan notifikasi
 * membawa potongan catatan itu.
 */
export function berlangganan(db, sesi, grupId, perangkat) {
  const { orang, peran } = peranDiGrup(db, sesi, grupId);
  wajibPeran(peran, ['pengelola', 'satpam']);

  const p = perangkat ?? {};
  const isi = (nilai) => (typeof nilai === 'string' ? nilai.trim() : '');
  const alamat = isi(p.alamat);
  const kunci = isi(p.kunci);
  const rahasia = isi(p.rahasia);
  if (!alamat || !kunci || !rahasia) {
    throw new layanan.GalatLayanan('langganan tidak lengkap: alamat, kunci, dan rahasia perangkat wajib ada');
  }

  db.prepare(
    `INSERT INTO langganan (pengguna_id, grup_id, alamat, kunci, rahasia) VALUES (?, ?, ?, ?, ?)
       ON CONFLICT (alamat) DO UPDATE SET pengguna_id = excluded.pengguna_id,
                                          grup_id = excluded.grup_id,
                                          kunci = excluded.kunci,
                                          rahasia = excluded.rahasia,
                                          gagal = 0`,
  ).run(orang.id, grupId, alamat, kunci, rahasia);
  return db.prepare('SELECT * FROM langganan WHERE alamat = ?').get(alamat);
}

export function berhentiLangganan(db, sesi, alamat) {
  const orang = wajibMasuk(db, sesi);
  return db.prepare('DELETE FROM langganan WHERE alamat = ? AND pengguna_id = ?')
    .run(String(alamat ?? ''), orang.id).changes;
}

/** Perangkat yang berlangganan grup ini. Dipakai di dalam server, bukan jalur yang dibuka ke luar. */
export function langgananGrup(db, grupId) {
  return db.prepare('SELECT * FROM langganan WHERE grup_id = ? ORDER BY id').all(grupId);
}

// ─── Halaman undangan tamu: tanpa akun ──────────────────────────────────────────────────────────────

/**
 * Dibuka tamu yang TIDAK punya akun, hanya dengan kodenya. Karena itu ia mengembalikan **seperlunya saja**:
 * tidak ada nomor WhatsApp, tidak ada nomor dalam basis data, tidak ada daftar penghuni atau kendaraan lain.
 * Kode yang salah menjawab "tidak ditemukan" yang sama dengan kode yang tidak ada.
 */
export function undangan(db, kode) {
  const t = layanan.tamuDariKode(db, kode);
  if (!t) throw TIDAK_DITEMUKAN();
  const g = layanan.gerbang(db, t.gerbang_id);
  return {
    kode: t.kode_undangan,
    tamu: t.nama,
    keperluan: t.keperluan,
    plat: t.plat,
    jenis: t.jenis,
    lama_hari: t.lama_hari,
    diundang_oleh: t.diundang_oleh,
    gerbang: g?.nama,
    alamat: g?.alamat,
    kota: g?.kota,
    patokan: g?.patokan,
  };
}
