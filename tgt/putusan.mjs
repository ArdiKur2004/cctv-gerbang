// Aturan memutuskan membuka gerbang. Rencana T4, keputusan owner K46.
//
// ⛔ BERKAS PALING MENYANGKUT KESELAMATAN DI PRODUK INI. Aturan CLAUDE.md §3 berlaku penuh:
//
//   1. Produk HANYA memberi perintah BUKA. Tidak ada jalan di berkas ini yang menghasilkan perintah tutup,
//      dan ada ujinya. Pengaman gerbang (fotosel, pembatas gaya) tetap milik perangkat gerbang, bukan kita.
//   2. Berkas ini TIDAK menggerakkan apa pun. Ia hanya mengembalikan putusan untuk dicatat dan ditampilkan.
//      Sampai Fase 5, tidak ada keluaran relay sama sekali, dan menyambungkannya butuh keputusan owner.
//   3. RAGU = TIDAK MEMBUKA, kecuali pengecualian K46 yang dirinci di bawah.
//   4. GAGAL KE ARAH MENUTUP: masukan yang tidak dikenal bentuknya tidak pernah membuka.
//
// Ciri kendaraan (jenis, warna, merek) TIDAK ikut memutuskan apa pun (K63): ia hanya dicatat bersama kejadian.
import { normalkanPlat } from './layanan.mjs';

/** Tiga putusan yang mungkin. Daftar putih: nilai lain tidak pernah keluar dari berkas ini. */
export const PUTUSAN = Object.freeze({
  BUKA: 'buka',
  PANGGIL_SATPAM: 'panggil_satpam',
  TIDAK_DIKENAL: 'tidak_dikenal',
});

/** Batas K46: lebih dari dua posisi ragu tidak pernah menyalakan relay. */
export const MAKS_RAGU = 2;

const ARAH_SAH = ['masuk', 'keluar'];
const STATUS_MASUK_AKAL = { masuk: 'di_luar', keluar: 'di_dalam' };

function tolak(alasan, putusan = PUTUSAN.PANGGIL_SATPAM) {
  return { putusan, alasan, plat: null, calon: [], statusJanggal: false, ciriJanggal: false };
}

/**
 * Apakah jenis yang dibaca kamera tidak cocok dengan jenis yang terdaftar?
 *
 * ⛔ Jawabannya HANYA menambah catatan. Ia tidak pernah mengubah putusan — tidak menahan, dan tidak pula
 * melonggarkan. K55 apa adanya: ciri "hanya memberi peringatan ke satpam, tidak menahan gerbang... sampai
 * pengenal ciri terbukti akurat dan owner memutuskan lain". Hari ini jenis benar pada 12 dari 14 mobil, jadi
 * sekitar 1 dari 7 mobil akan salah dikenali; menahan berarti menahan orang yang tidak bersalah tiap hari.
 *
 * "Tak yakin" dan "tidak terbaca" BUKAN ketidakcocokan: mesin yang ragu tidak boleh menjadi penuduh.
 */
function jenisTidakCocok(jenisTerbaca, calon) {
  const terbaca = typeof jenisTerbaca === 'string' ? jenisTerbaca.trim() : '';
  if (!terbaca || terbaca === 'tak_yakin') return false;
  const terdaftar = calon?.jenisKendaraan;
  if (typeof terdaftar !== 'string' || !terdaftar) return false;
  return terbaca !== terdaftar;
}

/**
 * Putuskan apa yang harus terjadi atas satu bacaan plat.
 *
 * @param bacaan      teks plat hasil mesin baca (boleh berspasi; dirapikan di sini)
 * @param ragu        daftar nomor posisi huruf yang mesin tidak yakin, dihitung pada plat yang SUDAH dirapikan
 * @param arah        'masuk' atau 'keluar'
 * @param jenisLokasi 'perumahan' memakai aturan yang lebih ketat (K46)
 * @param daftar      daftar izin: { plat, status: 'di_luar'|'di_dalam', jenis: 'penghuni'|'tamu' }
 */
export function putuskan({ bacaan, ragu, arah, jenisLokasi, daftar, jenisTerbaca } = {}) {
  // ── Semua pemeriksaan bentuk lebih dulu. Apa pun yang tidak dikenal berhenti di sini, tidak membuka. ──
  if (!Array.isArray(daftar)) return tolak('daftar izin tidak terbaca; satpam memutuskan dengan tangan');
  if (typeof arah !== 'string' || !ARAH_SAH.includes(arah)) {
    return tolak(`arah "${arah ?? ''}" tidak dikenal; satpam memutuskan dengan tangan`);
  }
  if (typeof jenisLokasi !== 'string' || !jenisLokasi.trim()) {
    return tolak('jenis lokasi tidak diketahui; aturan yang berlaku tidak bisa ditentukan');
  }

  let plat;
  try {
    plat = normalkanPlat(bacaan);
  } catch {
    return tolak('plat tidak terbaca sama sekali', PUTUSAN.TIDAK_DIKENAL);
  }

  if (!Array.isArray(ragu)) return tolak('daftar posisi ragu tidak terbaca; dianggap tidak bisa dipercaya');
  const posisiRagu = [...new Set(ragu)];
  if (posisiRagu.some((p) => !Number.isInteger(p) || p < 0 || p >= plat.length)) {
    return tolak('posisi ragu di luar jangkauan plat; bacaan tidak bisa dipercaya');
  }

  // ── Pagar K46 yang paling keras, diperiksa SEBELUM mencari calon. ──
  // Sengaja di sini, bukan sesudah: kalau diperiksa belakangan, satu calon tunggal yang meyakinkan bisa
  // menggoda siapa pun untuk melonggarkannya.
  if (posisiRagu.length > MAKS_RAGU) {
    return {
      putusan: PUTUSAN.PANGGIL_SATPAM,
      alasan: `mesin ragu pada ${posisiRagu.length} posisi, lebih dari batas ${MAKS_RAGU}; gerbang tidak dibuka sendiri`,
      plat,
      calon: [],
      statusJanggal: false,
      ciriJanggal: false,
    };
  }

  // ── Cari calon: cocok pada posisi yang YAKIN saja. ──
  const yakin = [...plat].map((huruf, i) => (posisiRagu.includes(i) ? null : huruf));
  const cocok = (lain) => {
    if (lain.length !== plat.length) return false;
    return yakin.every((huruf, i) => huruf === null || huruf === lain[i]);
  };

  const semuaCalon = daftar
    .filter((k) => k && typeof k.plat === 'string')
    .map((k) => ({ ...k, plat: k.plat.toUpperCase() }))
    .filter((k) => cocok(k.plat));

  if (semuaCalon.length === 0) {
    return {
      putusan: PUTUSAN.TIDAK_DIKENAL,
      alasan: `plat ${plat} tidak ada di daftar izin gerbang ini`,
      plat,
      calon: [],
      statusJanggal: false,
      ciriJanggal: false,
    };
  }

  // ── Bacaan yang YAKIN: tidak melewati aturan ragu sama sekali. ──
  if (posisiRagu.length === 0) {
    if (semuaCalon.length > 1) {
      return {
        putusan: PUTUSAN.PANGGIL_SATPAM,
        alasan: `plat ${plat} terdaftar lebih dari sekali di gerbang ini; satpam memeriksa`,
        plat,
        calon: semuaCalon,
        statusJanggal: false,
      ciriJanggal: false,
      };
    }
    const satu = semuaCalon[0];
    const janggal = satu.status !== undefined && satu.status !== STATUS_MASUK_AKAL[arah];
    const tidakCocok = jenisTidakCocok(jenisTerbaca, satu);

    // ⛔ K73 (owner, 26 Okt): status janggal diperlakukan BERBEDA menurut arahnya.
    //
    // KELUAR: tidak dibuka, satpam dipanggil. Owner, apa adanya: "tidak untuk keluar, karena ini berbahaya,
    // bisa jadi anda meloloskan maling atau pencuri dengan platnomor yang sama". Kendaraan yang keluar
    // padahal tidak pernah tercatat masuk adalah tanda yang harus DILIHAT ORANG, bukan diloloskan mesin —
    // dan yang hilang bila mesin salah menahan hanyalah waktu, sementara yang hilang bila mesin salah
    // meloloskan adalah barang orang.
    if (janggal && arah === 'keluar') {
      return {
        putusan: PUTUSAN.PANGGIL_SATPAM,
        alasan: `plat ${plat} terdaftar, tetapi tidak pernah tercatat masuk; keluar harus diperiksa satpam`,
        plat,
        calon: semuaCalon,
        statusJanggal: true,
      ciriJanggal: false,
      };
    }

    // MASUK: tetap dibuka, hanya ditandai supaya satpam diberi notifikasi. Kamera bisa melewatkan satu
    // kejadian, dan menahan orang di gerbang karena catatan kita sendiri meleset menimpa orang yang tidak
    // bersalah. Arah masuk berisiko kecil.
    return {
      putusan: PUTUSAN.BUKA,
      alasan: [
        janggal
          ? `plat ${plat} terdaftar; catatan status sebelumnya janggal untuk arah masuk, tetapi gerbang tetap dibuka`
          : `plat ${plat} terdaftar dan terbaca yakin`,
        // Ciri ditambahkan sebagai KALIMAT TAMBAHAN, bukan mengganti alasannya: yang memutuskan tetap plat.
        tidakCocok
          ? `kamera membaca jenis "${jenisTerbaca}", sedangkan yang terdaftar "${satu.jenisKendaraan}" — dicatat, tidak menahan`
          : '',
      ].filter(Boolean).join('; '),
      plat,
      calon: semuaCalon,
      statusJanggal: janggal,
      ciriJanggal: tidakCocok,
    };
  }

  // ── Bacaan RAGU 1-2 posisi: hanya calon yang statusnya masuk akal untuk arahnya yang dihitung (K46). ──
  const diharapkan = STATUS_MASUK_AKAL[arah];
  const calon = semuaCalon.filter((k) => k.status === undefined || k.status === diharapkan);

  if (calon.length === 0) {
    return {
      putusan: PUTUSAN.PANGGIL_SATPAM,
      alasan: `bacaan ragu, dan tidak ada calon yang statusnya masuk akal untuk arah ${arah}`,
      plat,
      calon: semuaCalon,
      statusJanggal: true,
      ciriJanggal: false,
    };
  }
  if (calon.length > 1) {
    return {
      putusan: PUTUSAN.PANGGIL_SATPAM,
      alasan: `bacaan ragu cocok dengan ${calon.length} plat berstatus sama; mesin tidak boleh menebak`,
      plat,
      calon,
      statusJanggal: false,
      ciriJanggal: false,
    };
  }

  // Tepat satu calon.
  //
  // K72 (owner, 26 Okt): "setiap tamu bisa langsung masuk lewat gerbang depan perumahan". Jenis calon —
  // tamu atau penghuni — TIDAK PERNAH menjadi alasan menahan. Yang menahan hanyalah KERAGUAN: cocok lebih
  // dari satu plat, atau ragu di atas batas. Ini mengoreksi bacaan agen sebelumnya atas K46, yang sempat
  // memanggil satpam untuk tamu di perumahan.
  const satu = calon[0];
  const tidakCocokRagu = jenisTidakCocok(jenisTerbaca, satu);
  return {
    putusan: PUTUSAN.BUKA,
    alasan: [
      `bacaan ragu pada ${posisiRagu.length} posisi, tetapi cocok tepat satu plat: ${satu.plat}`,
      tidakCocokRagu
        ? `kamera membaca jenis "${jenisTerbaca}", sedangkan yang terdaftar "${satu.jenisKendaraan}" — dicatat, tidak menahan`
        : '',
    ].filter(Boolean).join('; '),
    plat,
    calon,
    statusJanggal: false,
    ciriJanggal: tidakCocokRagu,
  };
}
