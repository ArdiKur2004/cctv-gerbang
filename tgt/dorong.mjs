// Mengirim notifikasi dorong (Web Push) ke perangkat yang berlangganan. Rencana T5, keputusan owner K72.
//
// ⛔ PELAJARAN DARI PEMBUAT QR (Rencana T3): kode penyandian yang diuji dengan pembaca buatan sendiri bisa
// lulus semua uji dan tetap mustahil dipakai di dunia nyata. Berkas ini memakai penyandian baku Web Push
// (RFC 8291 dan RFC 8188) yang dibaca oleh layanan dorong milik Google dan Mozilla — bukan oleh kode kita.
// Karena itu SATU-SATUNYA bukti yang sah bahwa berkas ini bekerja adalah **notifikasi yang benar-benar
// muncul di HP**. Uji di Node hanya menjaga bentuknya; ia TIDAK membuktikan apa pun tentang sampainya.
//
// Tidak ada paket luar: semuanya dari `node:crypto` bawaan (CLAUDE.md §6).
import { createECDH, createHmac, createPrivateKey, createPublicKey, createSign, createCipheriv, randomBytes } from 'node:crypto';

const b64url = (buf) => Buffer.from(buf).toString('base64url');
const dariB64url = (teks) => Buffer.from(String(teks), 'base64url');

// ─── VAPID: membuktikan siapa yang mengirim ─────────────────────────────────────────────────────────

/**
 * Buat sepasang kunci VAPID. Dibuat sekali lalu disimpan; kunci umumnya dipakai peramban saat berlangganan,
 * jadi mengganti kunci berarti semua langganan lama berhenti bekerja.
 */
/**
 * Lapisi kunci rahasia menjadi tepat 32 bita.
 *
 * ⛔ Node mengembalikan kunci rahasia P-256 sebagai BILANGAN, tanpa nol di depan: sekitar 1 dari 256 kunci
 * hanya 31 bita, 1 dari 65.536 hanya 30 bita. Karena `kunciTandaTangan()` menyusun DER PKCS#8 dari panjang
 * TETAP, kunci yang lebih pendek menghasilkan DER rusak — dan seluruh notifikasi dorong mati untuk pemasangan
 * itu, tanpa pesan apa pun, berbulan-bulan sesudah kuncinya dibuat.
 *
 * Ditemukan 26 Okt dari gerbang uji yang merah berselang-seling. Uji ukuran kunci yang hanya memeriksa satu
 * kunci terlihat hijau pada hari ia ditulis: peluang gagalnya 1 dari 256.
 */
function rahasia32(mentah) {
  const buf = Buffer.from(mentah);
  if (buf.length === 32) return buf;
  if (buf.length > 32) throw new Error(`kunci rahasia ${buf.length} bita, lebih dari 32`);
  return Buffer.concat([Buffer.alloc(32 - buf.length), buf]);
}

/** Pasangan kunci VAPID dari satu ECDH yang kuncinya sudah ada. Dipisah supaya bisa diuji dengan kunci tertentu. */
export function kunciVapidDari(ec) {
  return { umum: b64url(ec.getPublicKey()), rahasia: b64url(rahasia32(ec.getPrivateKey())) };
}

export function buatKunciVapid() {
  const ec = createECDH('prime256v1');
  ec.generateKeys();
  return kunciVapidDari(ec);
}

/** Ubah kunci rahasia mentah (32 bita) menjadi kunci yang bisa dipakai menandatangani. */
function kunciTandaTangan(rahasiaB64, umumB64) {
  const ec = createECDH('prime256v1');
  ec.setPrivateKey(dariB64url(rahasiaB64));
  void umumB64;
  // Bungkus menjadi DER PKCS#8 supaya bisa dipakai createSign.
  const awalan = Buffer.from('308187020100301306072a8648ce3d020106082a8648ce3d030107046d306b0201010420', 'hex');
  const tengah = Buffer.from('a144034200', 'hex');
  // rahasia32 dipakai LAGI di sini, bukan hanya saat kunci dibuat: setPrivateKey menerima 32 bita, tetapi
  // getPrivateKey() memotong nol di depannya kembali. Tanpa pelapisan di sini, DER-nya tetap rusak walau
  // kunci yang tersimpan sudah benar panjangnya.
  const der = Buffer.concat([awalan, rahasia32(ec.getPrivateKey()), tengah, ec.getPublicKey()]);
  return createPrivateKey({ key: der, format: 'der', type: 'pkcs8' });
}

/** Tanda tangan ES256 untuk JWT: r dan s mentah 32 bita, bukan DER. */
function jwtVapid({ alamat, rahasia, umum, hubungi }) {
  const asal = new URL(alamat).origin;
  const kepala = b64url(JSON.stringify({ typ: 'JWT', alg: 'ES256' }));
  const isi = b64url(JSON.stringify({
    aud: asal,
    exp: Math.floor(Date.now() / 1000) + 12 * 60 * 60,
    sub: hubungi,
  }));
  const bahan = `${kepala}.${isi}`;
  const penanda = createSign('SHA256');
  penanda.update(bahan);
  const tandaTangan = penanda.sign({ key: kunciTandaTangan(rahasia, umum), dsaEncoding: 'ieee-p1363' });
  return `${bahan}.${b64url(tandaTangan)}`;
}

// ─── Penyandian isi pesan (RFC 8291 + RFC 8188, aes128gcm) ──────────────────────────────────────────

function hkdfExtract(garam, bahan) {
  return createHmac('sha256', garam).update(bahan).digest();
}

function hkdfExpand(prk, keterangan, panjang) {
  return createHmac('sha256', prk).update(Buffer.concat([keterangan, Buffer.from([1])])).digest().subarray(0, panjang);
}

/**
 * Sandikan pesan untuk satu perangkat.
 *
 * Bentuk badannya (RFC 8188): garam(16) || ukuranRekaman(4) || panjangKunci(1) || kunciKita(65) || isi.
 */
function sandikan(pesan, kunciPerangkatB64, rahasiaPerangkatB64) {
  const kunciPerangkat = dariB64url(kunciPerangkatB64);
  const rahasiaPerangkat = dariB64url(rahasiaPerangkatB64);

  const kita = createECDH('prime256v1');
  kita.generateKeys();
  const kunciKita = kita.getPublicKey();
  const bersama = kita.computeSecret(kunciPerangkat);

  // RFC 8291: bahan kunci diturunkan dari rahasia perangkat dan kedua kunci umum.
  const keteranganKunci = Buffer.concat([
    Buffer.from('WebPush: info\0'),
    kunciPerangkat,
    kunciKita,
  ]);
  const ikm = hkdfExpand(hkdfExtract(rahasiaPerangkat, bersama), keteranganKunci, 32);

  const garam = randomBytes(16);
  const prk = hkdfExtract(garam, ikm);
  const cek = hkdfExpand(prk, Buffer.from('Content-Encoding: aes128gcm\0'), 16);
  const nonce = hkdfExpand(prk, Buffer.from('Content-Encoding: nonce\0'), 12);

  // Satu rekaman saja: isi diakhiri penanda 0x02 (rekaman terakhir).
  const teks = Buffer.concat([Buffer.from(pesan, 'utf8'), Buffer.from([2])]);
  const mesin = createCipheriv('aes-128-gcm', cek, nonce);
  const isi = Buffer.concat([mesin.update(teks), mesin.final(), mesin.getAuthTag()]);

  const ukuranRekaman = Buffer.alloc(4);
  ukuranRekaman.writeUInt32BE(4096);
  return Buffer.concat([garam, ukuranRekaman, Buffer.from([kunciKita.length]), kunciKita, isi]);
}

// ─── Pengiriman ─────────────────────────────────────────────────────────────────────────────────────

/**
 * Kirim satu notifikasi ke satu perangkat.
 *
 * Mengembalikan { terkirim, kode, hilang }. `hilang` berarti langganannya sudah tidak berlaku (404 atau 410):
 * perangkatnya dicopot orangnya atau ditolak layanan dorong, dan baris langganannya boleh dibuang.
 */
export async function kirimSatu({ langganan, isi, vapid, ttl = 3600, ambilan = fetch }) {
  const badan = sandikan(JSON.stringify(isi), langganan.kunci, langganan.rahasia);
  const tanda = jwtVapid({
    alamat: langganan.alamat,
    rahasia: vapid.rahasia,
    umum: vapid.umum,
    hubungi: vapid.hubungi,
  });

  const jawaban = await ambilan(langganan.alamat, {
    method: 'POST',
    headers: {
      TTL: String(ttl),
      'Content-Encoding': 'aes128gcm',
      'Content-Type': 'application/octet-stream',
      Authorization: `vapid t=${tanda}, k=${vapid.umum}`,
    },
    body: badan,
  });

  return {
    terkirim: jawaban.ok,
    kode: jawaban.status,
    hilang: jawaban.status === 404 || jawaban.status === 410,
  };
}

/**
 * Kirim ke semua penerima. Satu perangkat yang gagal TIDAK menghentikan yang lain: notifikasi ke satpam lain
 * tetap harus sampai.
 */
export async function kirimSemua({ penerima, isi, vapid, ambilan = fetch }) {
  const hasil = [];
  for (const langganan of penerima) {
    try {
      hasil.push({ alamat: langganan.alamat, ...await kirimSatu({ langganan, isi, vapid, ambilan }) });
    } catch (galat) {
      hasil.push({ alamat: langganan.alamat, terkirim: false, kode: 0, hilang: false, galat: String(galat) });
    }
  }
  return hasil;
}
