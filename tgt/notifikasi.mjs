// Apa yang memanggil satpam, dan apa isi pesannya. Rencana T5, keputusan owner K72 dan K73.
//
// Owner, K72: "setiap ada yang janggal, silahkan memanggiil satpam saja, bisa berupa notifikasi di HP saat
// PWA di install".
//
// Dua bahaya yang dijaga berkas ini, dan keduanya membuat notifikasi jadi tidak berguna:
//   1. TERLALU SERING — satpam berhenti membacanya, dan yang sungguhan ikut terlewat. Karena itu kendaraan
//      terdaftar yang lewat wajar TIDAK memberi notifikasi sama sekali.
//   2. MEMBAWA DATA PRIBADI — notifikasi muncul di layar kunci HP dan terbaca siapa pun yang lewat. Karena
//      itu pesannya dirakit dari daftar yang sudah ditentukan, BUKAN dari isi kejadian apa adanya: apa pun
//      yang kebetulan ikut terbawa dari basis data tidak bisa bocor.

const PANJANG_PESAN_MAKS = 180;

/** Putusan yang jelas tidak perlu memanggil siapa pun. Daftar putih: selain ini, satpam diberi tahu. */
const TIDAK_PERLU = new Set(['buka', 'dibuka_satpam']);

const jamDari = (waktu) => (typeof waktu === 'string' && waktu.length >= 16 ? waktu.slice(11, 16) : 'jam tidak tercatat');
const platDari = (plat) => (typeof plat === 'string' && plat ? plat : 'plat tidak terbaca');
const arahDari = (arah) => (arah === 'keluar' ? 'keluar' : 'masuk');

function potong(teks) {
  return teks.length <= PANJANG_PESAN_MAKS ? teks : `${teks.slice(0, PANJANG_PESAN_MAKS - 1)}…`;
}

/**
 * Perlukah satpam diberi tahu tentang kejadian ini, dan apa bunyinya?
 *
 * Mengembalikan { perlu: false } atau { perlu: true, sebab, judul, pesan }.
 */
export function perluNotifikasi(kejadian) {
  const k = kejadian ?? {};
  const putusan = typeof k.putusan === 'string' ? k.putusan : '';
  const jam = jamDari(k.waktu);
  const plat = platDari(k.plat);
  const arah = arahDari(k.arah);

  // Jenis yang dibaca kamera tidak cocok dengan yang terdaftar (T6). Gerbang TETAP dibuka — ciri tidak
  // pernah menahan (K55) — tetapi satpam diberi tahu, karena mobil terdaftar yang muncul sebagai truk
  // adalah hal yang layak dilihat orang. Disebut lebih dulu daripada status janggal, karena lebih berarti.
  if (putusan === 'buka' && k.ciriJanggal) {
    return {
      perlu: true,
      sebab: 'ciri_janggal',
      judul: 'Jenis kendaraan tidak cocok',
      pesan: potong(
        `${plat} ${arah} jam ${jam}. Kamera membaca jenis "${k.ciri_jenis ?? 'tidak terbaca'}", sedangkan yang `
        + 'terdaftar berbeda. Gerbang tetap dibuka; mohon diperiksa.',
      ),
    };
  }

  // Gerbang dibuka, tetapi catatan statusnya janggal (K73, arah masuk): satpam tetap diberi tahu.
  if (putusan === 'buka' && k.statusJanggal) {
    return {
      perlu: true,
      sebab: 'status_janggal',
      judul: 'Catatan janggal di gerbang',
      pesan: potong(
        `${plat} ${arah} jam ${jam}, dan gerbang dibuka. Catatan sebelumnya tidak cocok — mungkin satu kejadian `
        + 'terlewat kamera, mungkin juga bukan kendaraan yang sama.',
      ),
    };
  }

  if (TIDAK_PERLU.has(putusan)) return { perlu: false };

  // Selain itu — termasuk putusan yang tidak dikenal bentuknya — satpam diberi tahu. Gagal ke arah memberi
  // tahu: kalau kelak ada putusan baru dan berkas ini lupa diperbarui, yang terjadi adalah satpam melihatnya,
  // bukan diam-diam dilewatkan.
  if (putusan === 'tidak_dikenal') {
    return {
      perlu: true,
      sebab: 'tidak_dikenal',
      judul: `Kendaraan tak dikenal ${arah}`,
      pesan: potong(`${plat} ${arah} jam ${jam} dan tidak ada di daftar izin gerbang ini.`),
    };
  }

  const janggalKeluar = arah === 'keluar';
  return {
    perlu: true,
    sebab: putusan === 'panggil_satpam' ? 'panggil_satpam' : 'putusan_tidak_dikenal',
    judul: janggalKeluar ? 'Gerbang perlu diperiksa — kendaraan keluar' : 'Gerbang perlu diperiksa',
    pesan: potong(
      janggalKeluar
        ? `${plat} hendak keluar jam ${jam}, dan mesin tidak bisa memastikannya. Gerbang tidak dibuka sendiri.`
        : `${plat} ${arah} jam ${jam}, dan mesin tidak bisa memastikannya. Gerbang tidak dibuka sendiri.`,
    ),
  };
}
