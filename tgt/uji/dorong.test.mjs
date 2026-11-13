// Uji tgt/dorong.mjs: bentuk kiriman notifikasi dorong (Rencana T5 Task 4).
//
// ⚠️ APA YANG BERKAS INI BISA DAN TIDAK BISA BUKTIKAN.
// Ia memeriksa BENTUK kiriman: panjang kunci, susunan badan pesan, tajuk, dan tanda tangan. Ia TIDAK
// membuktikan bahwa notifikasinya sampai ke HP siapa pun — yang membaca sandinya adalah layanan dorong milik
// Google atau Mozilla dan sistem di HP, bukan kode kita. Pelajaran dari pembuat QR (Rencana T3) berlaku penuh
// di sini: satu-satunya bukti yang sah adalah notifikasi yang benar-benar muncul di HP.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createECDH, createPublicKey, createVerify, randomBytes } from 'node:crypto';

import { buatKunciVapid, kunciVapidDari, kirimSatu, kirimSemua } from '../dorong.mjs';

const b64url = (b) => Buffer.from(b).toString('base64url');

/** Perangkat palsu yang kuncinya sah secara matematis, supaya penyandiannya benar-benar dijalankan. */
function perangkatPalsu(nomor = 1) {
  const ec = createECDH('prime256v1');
  ec.generateKeys();
  return {
    alamat: `https://contoh.test/push/${nomor}`,
    kunci: b64url(ec.getPublicKey()),
    rahasia: b64url(Buffer.alloc(16, nomor)),
    _rahasiaEc: ec,
  };
}

const VAPID = { ...buatKunciVapid(), hubungi: 'mailto:tgt@example.test' };

/** fetch tiruan yang menangkap permintaannya. */
function penangkap(kode = 201) {
  const dicatat = [];
  const ambilan = async (alamat, pilihan) => {
    dicatat.push({ alamat, ...pilihan });
    return { ok: kode >= 200 && kode < 300, status: kode };
  };
  return { dicatat, ambilan };
}

// ─── Kunci VAPID ────────────────────────────────────────────────────────────────────────────────────

test('kunci VAPID berukuran baku: umum 65 bita, rahasia 32 bita', () => {
  const k = buatKunciVapid();
  assert.equal(Buffer.from(k.umum, 'base64url').length, 65, 'kunci umum harus titik P-256 tak termampat');
  assert.equal(Buffer.from(k.rahasia, 'base64url').length, 32);
  assert.equal(Buffer.from(k.umum, 'base64url')[0], 4, 'titik tak termampat diawali 0x04');
});

test('tiap pemanggilan menghasilkan kunci yang berbeda', () => {
  assert.notEqual(buatKunciVapid().umum, buatKunciVapid().umum);
});

// ─── Tanda tangan VAPID ─────────────────────────────────────────────────────────────────────────────

test('⛔ tanda tangan VAPID BENAR-BENAR sah, diperiksa dengan jalur kode yang berbeda', async () => {
  // Menandatangani dan memeriksa adalah dua jalur kode yang berbeda di node:crypto, jadi pemeriksaan ini
  // bukan sekadar mengulang perhitungan yang sama.
  const p = penangkap();
  await kirimSatu({ langganan: perangkatPalsu(), isi: { a: 1 }, vapid: VAPID, ambilan: p.ambilan });

  const izin = p.dicatat[0].headers.Authorization;
  const tanda = /t=([^,]+)/.exec(izin)[1];
  const [kepala, isi, tandaTangan] = tanda.split('.');

  const kunciUmum = createPublicKey({
    key: { kty: 'EC', crv: 'P-256', x: Buffer.from(VAPID.umum, 'base64url').subarray(1, 33).toString('base64url'), y: Buffer.from(VAPID.umum, 'base64url').subarray(33, 65).toString('base64url') },
    format: 'jwk',
  });
  const pemeriksa = createVerify('SHA256');
  pemeriksa.update(`${kepala}.${isi}`);
  assert.ok(
    pemeriksa.verify({ key: kunciUmum, dsaEncoding: 'ieee-p1363' }, Buffer.from(tandaTangan, 'base64url')),
    'tanda tangan VAPID tidak sah; layanan dorong akan menolak semua kiriman',
  );
});

test('isi tanda tangan menyebut tujuan dan masa berlaku yang masuk akal', async () => {
  const p = penangkap();
  await kirimSatu({ langganan: perangkatPalsu(), isi: {}, vapid: VAPID, ambilan: p.ambilan });
  const tanda = /t=([^,]+)/.exec(p.dicatat[0].headers.Authorization)[1];
  const isi = JSON.parse(Buffer.from(tanda.split('.')[1], 'base64url').toString('utf8'));

  assert.equal(isi.aud, 'https://contoh.test', 'tujuan harus asal alamat perangkatnya, bukan alamat penuh');
  assert.equal(isi.sub, 'mailto:tgt@example.test');
  const umurJam = (isi.exp - Math.floor(Date.now() / 1000)) / 3600;
  assert.ok(umurJam > 0 && umurJam <= 24, `masa berlaku ${umurJam} jam di luar batas yang diterima layanan dorong`);
});

// ─── Bentuk badan pesan ─────────────────────────────────────────────────────────────────────────────

test('badan pesan mengikuti susunan baku: garam, ukuran rekaman, kunci, lalu isi', async () => {
  const p = penangkap();
  const pesan = { judul: 'Gerbang perlu diperiksa', pesan: 'L1234AB masuk jam 08:00' };
  await kirimSatu({ langganan: perangkatPalsu(), isi: pesan, vapid: VAPID, ambilan: p.ambilan });

  const badan = p.dicatat[0].body;
  assert.ok(Buffer.isBuffer(badan));
  assert.equal(badan.readUInt32BE(16), 4096, 'ukuran rekaman harus tertulis di posisi 16');
  assert.equal(badan[20], 65, 'panjang kunci pengirim harus 65');
  assert.equal(badan[21], 4, 'kunci pengirim harus titik tak termampat');

  const panjangIsi = badan.length - 86;
  const panjangTeks = JSON.stringify(pesan).length;
  assert.equal(panjangIsi, panjangTeks + 1 + 16, 'isi = teks + penanda rekaman terakhir + tanda keaslian');
});

test('pesan yang sama dikirim dua kali menghasilkan badan yang BERBEDA', async () => {
  // Garamnya acak. Badan yang sama persis berarti garamnya tetap, dan itu melemahkan penyandiannya.
  const p = penangkap();
  const perangkat = perangkatPalsu();
  await kirimSatu({ langganan: perangkat, isi: { a: 1 }, vapid: VAPID, ambilan: p.ambilan });
  await kirimSatu({ langganan: perangkat, isi: { a: 1 }, vapid: VAPID, ambilan: p.ambilan });
  assert.ok(!p.dicatat[0].body.equals(p.dicatat[1].body));
});

test('tajuk kiriman sesuai yang dituntut layanan dorong', async () => {
  const p = penangkap();
  await kirimSatu({ langganan: perangkatPalsu(), isi: {}, vapid: VAPID, ambilan: p.ambilan });
  const t = p.dicatat[0].headers;
  assert.equal(p.dicatat[0].method, 'POST');
  assert.equal(t['Content-Encoding'], 'aes128gcm');
  assert.equal(t['Content-Type'], 'application/octet-stream');
  assert.match(t.Authorization, /^vapid t=[\w-]+\.[\w-]+\.[\w-]+, k=[\w-]+$/);
  assert.ok(Number(t.TTL) > 0);
});

// ─── Kegagalan ──────────────────────────────────────────────────────────────────────────────────────

test('jawaban 404 dan 410 ditandai hilang, supaya langganannya bisa dibuang', async () => {
  for (const kode of [404, 410]) {
    const p = penangkap(kode);
    const h = await kirimSatu({ langganan: perangkatPalsu(), isi: {}, vapid: VAPID, ambilan: p.ambilan });
    assert.equal(h.terkirim, false);
    assert.equal(h.hilang, true);
  }
});

test('jawaban gagal lain tidak ditandai hilang: perangkatnya mungkin hanya sedang tak terjangkau', async () => {
  const p = penangkap(503);
  const h = await kirimSatu({ langganan: perangkatPalsu(), isi: {}, vapid: VAPID, ambilan: p.ambilan });
  assert.equal(h.hilang, false);
});

test('⛔ satu perangkat yang gagal TIDAK menghentikan kiriman ke satpam lain', async () => {
  const dicatat = [];
  const ambilan = async (alamat) => {
    dicatat.push(alamat);
    if (alamat.endsWith('/2')) throw new Error('jaringan putus');
    return { ok: true, status: 201 };
  };
  const hasil = await kirimSemua({
    penerima: [perangkatPalsu(1), perangkatPalsu(2), perangkatPalsu(3)],
    isi: {}, vapid: VAPID, ambilan,
  });
  assert.equal(dicatat.length, 3, 'pengiriman berhenti di tengah; satpam lain tidak diberi tahu');
  assert.deepEqual(hasil.map((h) => h.terkirim), [true, false, true]);
});

// ─── Kunci rahasia yang berawalan nol (ditemukan 26 Okt dari gerbang yang merah berselang-seling) ──

test('⛔ kunci rahasia VAPID SELALU 32 bita, walau nilainya berawalan nol', () => {
  // Node mengembalikan kunci rahasia P-256 sebagai bilangan TANPA nol di depan, jadi sekitar 1 dari 256
  // kunci hanya 31 bita. Itulah sebabnya uji ukuran di atas merah berselang-seling — dan yang jauh lebih
  // buruk: kunciTandaTangan() menyusun DER dari panjang TETAP, jadi kunci 31 bita menghasilkan DER rusak
  // dan seluruh notifikasi dorong mati untuk pemasangan itu. Gagalnya baru terlihat saat notifikasi
  // pertama dikirim, berbulan-bulan sesudah kuncinya dibuat.
  //
  // Diuji dengan kunci yang DIPAKSA berawalan nol, bukan dengan menunggu kebetulan: uji yang bergantung
  // pada peluang 1:256 akan terlihat hijau pada hari ia ditulis.
  const ec = createECDH('prime256v1');
  ec.setPrivateKey(Buffer.concat([Buffer.alloc(1), randomBytes(31)]));
  assert.equal(ec.getPrivateKey().length, 31, 'anggapan ujinya salah: Node ternyata sudah memberi 32 bita');

  const kunci = kunciVapidDari(ec);
  assert.equal(Buffer.from(kunci.rahasia, 'base64url').length, 32,
    'kunci rahasia tidak dilapisi nol di depan: DER yang disusun darinya akan rusak');

  // Dan RANTAINYA, bukan hanya panjangnya: kunci seperti itu harus benar-benar bisa mengirim notifikasi.
  // Tanpa bagian ini, melapisi nol di tempat yang salah tetap lulus.
  return assert.doesNotReject(
    kirimSatu({
      langganan: perangkatPalsu(7),
      isi: { judul: 'Uji', pesan: 'Uji' },
      vapid: { ...kunci, hubungi: 'mailto:tgt@example.test' },
      ambilan: penangkap().ambilan,
    }),
    'kunci berawalan nol tidak bisa dipakai mengirim notifikasi',
  );
});

test('ukuran kunci rahasia benar untuk banyak kunci berturut-turut', () => {
  // Pengganti uji ukuran yang dulu memeriksa satu kunci saja. 1.000 kunci membuat peluang lolosnya kunci
  // 31 bita yang tak terlapisi menjadi sangat kecil, tanpa membuat ujinya lambat.
  for (let i = 0; i < 1000; i += 1) {
    const k = buatKunciVapid();
    assert.equal(Buffer.from(k.rahasia, 'base64url').length, 32, `kunci ke-${i} bukan 32 bita`);
    assert.equal(Buffer.from(k.umum, 'base64url').length, 65);
  }
});
