// Pengaturan TGT. Rencana T2, keputusan owner K70.
//
// ⛔ K70: data TGT tinggal di PC milik IBE, dan NAS akan dibeli nanti. Karena itu **jalur simpan tidak boleh
// dipaku di kode**: memasang NAS harus cukup dengan mengubah pengaturan, bukan membongkar kode.
//
// Semua jalur di sini bawaannya di bawah `data/` yang di-gitignore (CLAUDE.md §4), karena isinya plat nomor,
// nomor WhatsApp, dan jam keluar masuk.
import fs from 'node:fs';
import path from 'node:path';

const BAWAAN = {
  // Berkas basis data.
  basis: 'data/tgt/tgt.sqlite',
  // Foto bukti kendaraan.
  foto: 'data/tgt/foto',
  // Tempat salinan cadangan. Bawaannya KOSONG, dan itu sengaja: selama NAS belum ada, tidak ada cadangan, dan
  // itu harus terlihat sebagai "belum diatur" — bukan tersembunyi di balik jalur yang terdengar meyakinkan.
  cadangan: '',
  porta: '8787',
  // Jembatan ke mesin baca plat (T6). Harus di data/keluaran, karena hanya folder itu yang bisa ditulis
  // dari dalam lab (tools/lab.ps1).
  'baca-masuk': 'data/keluaran/baca-masuk',
  'baca-keluar': 'data/keluaran/baca-keluar',
  alamat: '127.0.0.1',
};

function baca(nama) {
  const dariLingkungan = process.env[`TGT_${nama.toUpperCase()}`];
  return dariLingkungan !== undefined && dariLingkungan !== '' ? dariLingkungan : BAWAAN[nama];
}

export function pengaturan() {
  const cadangan = baca('cadangan');
  return {
    jalurBasis: path.resolve(baca('basis')),
    jalurFoto: path.resolve(baca('foto')),
    // null, bukan jalur palsu: pemanggil harus memeriksanya dan mengakui bila cadangan belum ada.
    jalurCadangan: cadangan ? path.resolve(cadangan) : null,
    porta: Number(baca('porta')),
    alamat: baca('alamat'),
    jalurBacaMasuk: path.resolve(baca('baca-masuk')),
    jalurBacaKeluar: path.resolve(baca('baca-keluar')),
    // ⛔ MODE DEMO: OTP ditampilkan di layar, bukan dikirim. Ia MEMBUKA KUNCI AKUN SIAPA PUN yang alamat
    // emailnya diketahui, jadi ia mati kecuali dinyalakan dengan sengaja. Daftar putih nilai, bukan
    // "apa pun selain kosong": salah ketik tidak boleh diam-diam menyalakannya.
    demoOtp: ['1', 'true'].includes(String(process.env.TGT_DEMO_OTP ?? '')),
    simpanFoto: bacaHari('foto'),
    simpanKejadian: bacaHari('kejadian'),
    simpanTamu: bacaHari('tamu'),
  };
}

/**
 * Kunci VAPID untuk notifikasi dorong. Dibuat sekali lalu DISIMPAN: kunci umumnya dipakai peramban saat
 * berlangganan, jadi mengganti kunci membuat semua langganan lama berhenti bekerja tanpa ada yang mengeluh.
 *
 * Berkasnya di data/ yang di-gitignore, karena memuat kunci rahasia.
 */
export function kunciVapid(buat) {
  const jalur = path.resolve(process.env.TGT_VAPID || 'data/tgt/vapid.json');
  try {
    const isi = JSON.parse(fs.readFileSync(jalur, 'utf8'));
    if (isi.umum && isi.rahasia) return { ...isi, hubungi: isi.hubungi ?? HUBUNGI_BAWAAN };
  } catch {
    // Belum ada, atau rusak: dibuat baru di bawah.
  }
  const baru = { ...buat(), hubungi: HUBUNGI_BAWAAN };
  fs.mkdirSync(path.dirname(jalur), { recursive: true });
  fs.writeFileSync(jalur, JSON.stringify(baru, null, 2));
  return baru;
}

// Alamat yang disertakan saat menghubungi layanan dorong, supaya mereka bisa mengabari bila ada masalah.
const HUBUNGI_BAWAAN = process.env.TGT_HUBUNGI || 'mailto:tgt@anitareply.com';

/**
 * Kalimat untuk dicetak saat server menyala. Ia menyebut dengan jelas bila cadangan belum diatur, supaya batas
 * K70 ("sampai NAS dibeli, belum ada cadangan") terlihat tiap kali, bukan hanya tertulis di dokumen.
 */
export function catatanCadangan(atur = pengaturan()) {
  return atur.jalurCadangan
    ? `Cadangan: ${atur.jalurCadangan}`
    : 'Cadangan: BELUM DIATUR — foto dan catatan belum tersalin ke mana pun (K70, menunggu NAS). '
      + 'Atur dengan TGT_CADANGAN=<jalur>.';
}

/**
 * Masa simpan data dalam hari.
 *
 * ⛔ BAWAANNYA SIMPAN SELAMANYA (K74, owner 26 Okt). Dulu bawaannya foto 7 hari, kejadian 90, tamu 30 —
 * angka itu TEBAKAN agen atas kalimat owner "data tidak boleh di simpan semua", dan tebakannya salah. Owner
 * mengoreksi: **semua data wajib disimpan, tidak boleh dihapus.**
 *
 * Arah gagalnya karena itu dibalik: apa pun yang tidak terbaca sebagai jumlah hari yang masuk akal berarti
 * SIMPAN. Menghapus data orang hanya terjadi bila ada yang menuliskan angkanya dengan sengaja — peubah
 * lingkungan yang hilang, salah ketik, atau pengaturan yang terlewat tidak boleh pernah menghapus apa pun.
 * Ini kebalikan dari gerbang uang yang fail-closed: di sini yang tidak boleh terjadi secara kebetulan adalah
 * MENGHAPUS, bukan menyimpan.
 */
export const SELAMANYA = null;

function bacaHari(nama) {
  const dari = process.env[`TGT_SIMPAN_${nama.toUpperCase()}`];
  if (dari === undefined) return SELAMANYA;
  const teks = String(dari).trim();
  // Hanya bilangan bulat minimal 1 yang dihitung sebagai masa simpan. Semua yang lain — kosong, "tujuh",
  // "7 hari", "0", nilai negatif — berarti simpan selamanya, bukan galat. Galat saat server menyala bisa
  // membuat orang menghapus pengaturannya, dan dulu itu berarti memakai bawaan yang menghapus.
  return /^[1-9]\d*$/.test(teks) ? Number(teks) : SELAMANYA;
}
