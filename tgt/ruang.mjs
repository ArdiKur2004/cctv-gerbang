// Pagar ruang disk TGT. Keputusan owner 26 Okt: "pastikan di PC IBE tidak mengganggu MES Yanmar".
//
// ⛔ KENAPA BERKAS INI ADA.
// TGT dipasang di PC yang menjalankan MES Yanmar — perangkat lunak yang dipakai orang sungguhan untuk bekerja
// (K71). Prinsip #3: perkakas yang kita jalankan tidak boleh membunuh mesin yang menjalankannya. Disk penuh di
// mesin produksi bukan gangguan kecil: basis data lain tidak bisa menulis, log berhenti, dan perangkat lunak
// ikut gagal dengan cara yang sulit dilacak.
//
// ⛔ ARAH PAGARNYA: BERHENTI MENULIS, JANGAN PERNAH MENGHAPUS.
// K74 (owner, 26 Okt): semua data wajib disimpan. Jadi saat ruang menipis, yang berhenti adalah tulisan BARU —
// bukan catatan lama yang dihapus untuk memberi tempat. Itu kebalikan dari cara banyak sistem bekerja, dan itu
// disengaja: catatan yang hilang tidak bisa dibuat ulang.
//
// Angka yang diukur 26 Okt, supaya besarannya jelas: basis data TGT tumbuh 190 bita per kejadian — sekitar
// 10 MB setahun pada 150 kendaraan sehari, 100 MB dalam sepuluh tahun. Itu aman di mesin mana pun. Yang akan
// menjadi besar adalah foto bukti (4–42 GB setahun per gerbang, tergantung ukuran gambar), dan foto itu BELUM
// ditulis apa pun hari ini. Pagar ini dipasang sebelum foto ada, bukan sesudah disk MES penuh.
import fs from 'node:fs';

/**
 * Ruang kosong minimum yang harus tetap tersisa di disk. 5 GB: cukup besar supaya MES dan sistem operasinya
 * masih punya ruang bernapas, cukup kecil supaya TGT tidak berhenti menulis di mesin kecil yang sehat.
 * Bisa diubah lewat `TGT_SISA_DISK_GB` tanpa menyentuh kode.
 */
export const SISA_DISK_MINIMUM = 5 * 1024 ** 3;

/** Batas yang berlaku: dari pengaturan bila disetel masuk akal, kalau tidak bawaannya. */
export function batasSisa() {
  const dari = process.env.TGT_SISA_DISK_GB;
  const teks = String(dari ?? '').trim();
  if (!/^[1-9]\d*$/.test(teks)) return SISA_DISK_MINIMUM;
  return Number(teks) * 1024 ** 3;
}

/**
 * Ruang kosong di disk tempat `jalur` berada, dalam bita. `undefined` bila tidak bisa dibaca.
 *
 * Folder yang belum ada bukan galat: folder foto memang belum ada sampai foto pertama ditulis, dan pagar yang
 * melempar di situ akan menjatuhkan gerbang karena hal yang bukan masalah.
 */
export function sisaDisk(jalur) {
  try {
    const s = fs.statfsSync(jalur);
    return s.bavail * s.bsize;
  } catch {
    return undefined;
  }
}

/**
 * Apakah masih boleh menulis di sana.
 *
 * ⛔ ARAH GAGALNYA: ruang yang TIDAK BISA DIBACA dianggap CUKUP. Ini berbeda dari gerbang uang yang
 * fail-closed, dan bedanya disengaja. Kalau pembacaan ruang gagal — izin, sistem berkas yang tidak dikenal,
 * jalur jaringan — yang lebih buruk adalah gerbang berhenti mencatat kendaraan yang lewat. Catatan yang hilang
 * tidak bisa dibuat ulang, sementara disk yang penuh masih memberi tanda lain.
 */
export function ruangCukup(jalur, batas = batasSisa()) {
  const sisa = sisaDisk(jalur);
  if (sisa === undefined) return true;
  return sisa >= batas;
}

const gb = (bita) => (bita / 1024 ** 3).toFixed(1);

/**
 * Keadaan ruang beserta kalimat yang bisa dimengerti orang non-teknis — yang membacanya bisa jadi satpam atau
 * pemilik pabrik, bukan pemrogram. Karena itu tidak ada ENOSPC, statfs, atau errno di kalimatnya.
 */
export function periksaRuang(jalur, batas = batasSisa()) {
  const sisa = sisaDisk(jalur);
  if (sisa === undefined) {
    return {
      cukup: true,
      sisa: undefined,
      pesan: 'Ruang disk belum bisa dibaca di tempat ini, jadi TGT tetap mencatat seperti biasa. '
        + 'Catatan yang hilang tidak bisa dibuat ulang, jadi mencatat lebih penting daripada berhenti.',
    };
  }
  if (sisa >= batas) {
    return { cukup: true, sisa, pesan: `Ruang disk tersisa ${gb(sisa)} GB. Cukup.` };
  }
  return {
    cukup: false,
    sisa,
    pesan: `Ruang disk tersisa ${gb(sisa)} GB, kurang dari batas ${gb(batas)} GB. TGT BERHENTI menyimpan `
      + 'gambar baru supaya tidak mengganggu perangkat lunak lain di komputer ini. '
      + 'Catatan lama TIDAK dihapus — kosongkan ruang atau pindahkan foto ke NAS.',
  };
}
