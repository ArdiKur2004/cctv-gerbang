// Uji tgt/notifikasi.mjs: apa yang memanggil satpam, dan apa isi pesannya (Rencana T5 Task 4, K72 dan K73).
//
// Dua bahaya yang dijaga berkas ini:
//   1. notifikasi yang TERLALU SERING — satpam berhenti membacanya, dan yang sungguhan ikut terlewat;
//   2. notifikasi yang MEMBAWA DATA PRIBADI — ia muncul di layar kunci HP, terbaca siapa pun yang lewat.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { perluNotifikasi } from '../notifikasi.mjs';

const kejadian = (lebih = {}) => ({
  waktu: '2026-10-26T08:00:00',
  arah: 'masuk',
  plat: 'L1234AB',
  putusan: 'buka',
  alasan: 'plat L1234AB terdaftar dan terbaca yakin',
  ...lebih,
});

// ─── Yang memanggil satpam ──────────────────────────────────────────────────────────────────────────

test('putusan panggil satpam memanggil satpam', () => {
  const h = perluNotifikasi(kejadian({ putusan: 'panggil_satpam', alasan: 'bacaan ragu cocok dengan 2 plat' }));
  assert.equal(h.perlu, true);
  assert.ok(h.judul && h.pesan);
});

test('plat tidak dikenal memanggil satpam', () => {
  const h = perluNotifikasi(kejadian({ putusan: 'tidak_dikenal', alasan: 'tidak ada di daftar izin' }));
  assert.equal(h.perlu, true);
});

test('⛔ janggal saat KELUAR memanggil satpam, dan pesannya menyebut keluar (K73)', () => {
  const h = perluNotifikasi(kejadian({
    arah: 'keluar', putusan: 'panggil_satpam',
    alasan: 'plat L1234AB terdaftar, tetapi tidak pernah tercatat masuk; keluar harus diperiksa satpam',
  }));
  assert.equal(h.perlu, true);
  assert.match(`${h.judul} ${h.pesan}`, /keluar/i);
});

test('janggal saat MASUK tetap memanggil satpam walau gerbangnya dibuka (K73)', () => {
  // Gerbang dibuka, tetapi satpam tetap diberi tahu. Inilah bagian "tapi satpam tetap diberikan notifikasi".
  const h = perluNotifikasi(kejadian({ putusan: 'buka', statusJanggal: true }));
  assert.equal(h.perlu, true);
  assert.match(`${h.judul} ${h.pesan}`, /masuk|janggal|catatan/i);
});

// ─── Yang TIDAK memanggil satpam ────────────────────────────────────────────────────────────────────

test('⛔ kendaraan terdaftar yang lewat wajar TIDAK memanggil satpam', () => {
  // Kalau yang wajar pun memberi notifikasi, satpam berhenti membacanya dan yang sungguhan ikut terlewat.
  for (const arah of ['masuk', 'keluar']) {
    assert.equal(perluNotifikasi(kejadian({ arah, putusan: 'buka' })).perlu, false);
  }
});

test('yang dibuka satpam sendiri tidak memanggil satpam', () => {
  const h = perluNotifikasi(kejadian({ putusan: 'dibuka_satpam', alasan: 'tamu dadakan (dibuka Pak Satpam)' }));
  assert.equal(h.perlu, false);
});

test('putusan yang tidak dikenal bentuknya memanggil satpam: gagal ke arah memberi tahu', () => {
  // Kalau kelak ada putusan baru dan berkas ini lupa diperbarui, yang terjadi adalah satpam diberi tahu —
  // bukan diam-diam dilewatkan.
  for (const putusan of ['entah', '', null, undefined]) {
    assert.equal(perluNotifikasi(kejadian({ putusan })).perlu, true, `putusan ${putusan} seharusnya memberi tahu`);
  }
});

// ─── Isi pesan ──────────────────────────────────────────────────────────────────────────────────────

test('⛔ pesan TIDAK memuat data pribadi selain plat', () => {
  // Notifikasi muncul di layar kunci HP dan terbaca siapa pun yang lewat.
  const h = perluNotifikasi({
    waktu: '2026-10-26T08:00:00', arah: 'masuk', plat: 'L1234AB', putusan: 'tidak_dikenal',
    alasan: 'plat L1234AB tidak ada di daftar izin gerbang ini',
    // Hal-hal yang kebetulan ikut terbawa dari basis data tidak boleh bocor ke pesannya.
    atas_nama: 'Ani Contoh', email: 'ani@example.test', wa: '6281200000003', diundang_oleh: 'Budi Contoh',
  });
  const teks = `${h.judul} ${h.pesan}`;
  for (const rahasia of ['Ani Contoh', 'ani@example.test', '6281200000003', 'Budi Contoh']) {
    assert.ok(!teks.includes(rahasia), `pesan membocorkan "${rahasia}" ke layar kunci HP`);
  }
  assert.ok(teks.includes('L1234AB'), 'plat justru yang dibutuhkan satpam, jadi ia harus ada');
});

test('pesan menyebut jam dan arah, supaya satpam tahu harus melihat ke mana', () => {
  const h = perluNotifikasi(kejadian({ arah: 'keluar', putusan: 'panggil_satpam', waktu: '2026-10-26T21:45:00' }));
  const teks = `${h.judul} ${h.pesan}`;
  assert.match(teks, /21:45/);
  assert.match(teks, /keluar/i);
});

test('plat yang tidak terbaca tetap memberi pesan yang masuk akal', () => {
  const h = perluNotifikasi(kejadian({ plat: null, putusan: 'tidak_dikenal', alasan: 'plat tidak terbaca' }));
  assert.equal(h.perlu, true);
  assert.ok(h.pesan.length > 0);
  assert.ok(!h.pesan.includes('null'), 'pesan tidak boleh menampilkan kata "null" ke satpam');
});

test('pesan cukup pendek untuk muat di layar kunci', () => {
  const h = perluNotifikasi(kejadian({ putusan: 'panggil_satpam', alasan: 'x'.repeat(500) }));
  assert.ok(h.pesan.length <= 180, `pesan ${h.pesan.length} huruf terlalu panjang untuk notifikasi`);
});

test('kejadian tanpa isi sama sekali tidak membuat pemanggil gagal', () => {
  for (const k of [undefined, null, {}]) {
    const h = perluNotifikasi(k);
    assert.equal(typeof h.perlu, 'boolean');
    if (h.perlu) assert.ok(h.judul && h.pesan);
  }
});
