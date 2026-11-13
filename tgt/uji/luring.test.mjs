// Uji tgt/web/luring.js: daftar izin tersimpan dan antrean kejadian saat internet putus (Rencana T4 Task 3).
//
// Gerbang sering di luar jangkauan. Yang paling berbahaya bukan "tidak terkirim", melainkan
// "terkirim dua kali" atau "hilang diam-diam": keduanya diuji di sini.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buatLuring } from '../web/luring.js';

/** Penyimpanan tiruan dengan antarmuka yang sama dengan localStorage. */
function simpananTiruan(awal = {}) {
  const isi = new Map(Object.entries(awal));
  return {
    getItem: (k) => (isi.has(k) ? isi.get(k) : null),
    setItem: (k, v) => isi.set(k, String(v)),
    removeItem: (k) => isi.delete(k),
    _isi: isi,
  };
}

const kejadian = (plat) => ({ bacaan: plat, ragu: [], arah: 'masuk', waktu: '2026-10-26T08:00:00' });

// ─── Daftar izin tersimpan ──────────────────────────────────────────────────────────────────────────

test('daftar izin disimpan dan dibaca kembali per gerbang', () => {
  const l = buatLuring({ simpanan: simpananTiruan(), kirim: async () => {} });
  l.simpanIzin(1, [{ plat: 'L1234AB', jenis: 'penghuni', status: 'di_luar' }]);
  l.simpanIzin(2, [{ plat: 'W1111ZZ', jenis: 'tamu', status: 'di_luar' }]);

  assert.deepEqual(l.bacaIzin(1).map((i) => i.plat), ['L1234AB']);
  assert.deepEqual(l.bacaIzin(2).map((i) => i.plat), ['W1111ZZ']);
  assert.equal(l.bacaIzin(3), null, 'gerbang yang belum pernah disalin harus jelas kosong, bukan daftar kosong');
});

test('daftar izin yang rusak di penyimpanan tidak membuat layar mati', () => {
  // Penyimpanan peramban bisa rusak atau diubah tangan. Yang penting layar gerbang tetap menyala.
  const l = buatLuring({ simpanan: simpananTiruan({ 'tgt.izin.1': 'bukan json' }), kirim: async () => {} });
  assert.equal(l.bacaIzin(1), null);
});

// ─── Antrean kejadian ───────────────────────────────────────────────────────────────────────────────

test('kejadian diantrekan dan jumlahnya terbaca', () => {
  const l = buatLuring({ simpanan: simpananTiruan(), kirim: async () => {} });
  assert.equal(l.jumlahAntre(), 0);
  l.antrekan(1, kejadian('L1234AB'));
  l.antrekan(1, kejadian('L5678CD'));
  assert.equal(l.jumlahAntre(), 2);
});

test('tiap kejadian mendapat penanda sendiri yang tidak pernah sama', () => {
  const l = buatLuring({ simpanan: simpananTiruan(), kirim: async () => {} });
  const penanda = new Set();
  for (let i = 0; i < 50; i += 1) penanda.add(l.antrekan(1, kejadian('L1234AB')));
  assert.equal(penanda.size, 50, 'penanda yang sama akan membuat kejadian hilang saat disusulkan');
});

test('antrean selamat saat halaman dimuat ulang', () => {
  const simpanan = simpananTiruan();
  const l1 = buatLuring({ simpanan, kirim: async () => {} });
  l1.antrekan(1, kejadian('L1234AB'));

  const l2 = buatLuring({ simpanan, kirim: async () => {} });
  assert.equal(l2.jumlahAntre(), 1, 'antrean hilang saat halaman dimuat ulang: kejadian gerbang lenyap');
});

// ─── Penyusulan ─────────────────────────────────────────────────────────────────────────────────────

test('penyusulan mengirim semuanya lalu mengosongkan antrean', async () => {
  const terkirim = [];
  const l = buatLuring({
    simpanan: simpananTiruan(),
    kirim: async (gerbangId, k) => { terkirim.push([gerbangId, k.bacaan, k.penanda]); },
  });
  l.antrekan(1, kejadian('L1234AB'));
  l.antrekan(1, kejadian('L5678CD'));

  const hasil = await l.susulkan();

  assert.equal(hasil.terkirim, 2);
  assert.equal(hasil.tersisa, 0);
  assert.equal(l.jumlahAntre(), 0);
  assert.deepEqual(terkirim.map((t) => t[1]), ['L1234AB', 'L5678CD'], 'urutan kejadian harus terjaga');
  assert.ok(terkirim.every((t) => t[2]), 'penanda wajib ikut terkirim');
});

test('⛔ kejadian yang GAGAL terkirim TIDAK hilang, dan urutannya terjaga', async () => {
  let gagalkan = true;
  const terkirim = [];
  const l = buatLuring({
    simpanan: simpananTiruan(),
    kirim: async (gerbangId, k) => {
      if (gagalkan) throw new Error('internet putus');
      terkirim.push(k.bacaan);
    },
  });
  l.antrekan(1, kejadian('L1111AA'));
  l.antrekan(1, kejadian('L2222BB'));

  const saatPutus = await l.susulkan();
  assert.equal(saatPutus.terkirim, 0);
  assert.equal(saatPutus.tersisa, 2, 'kejadian hilang saat internet putus');
  assert.equal(l.jumlahAntre(), 2);

  gagalkan = false;
  const saatTersambung = await l.susulkan();
  assert.equal(saatTersambung.terkirim, 2);
  assert.equal(l.jumlahAntre(), 0);
  assert.deepEqual(terkirim, ['L1111AA', 'L2222BB'], 'urutan berubah sesudah putus sambung');
});

test('penyusulan berhenti pada kegagalan pertama, supaya urutannya tidak melompat', async () => {
  const terkirim = [];
  const l = buatLuring({
    simpanan: simpananTiruan(),
    kirim: async (gerbangId, k) => {
      if (k.bacaan === 'L2222BB') throw new Error('putus di tengah');
      terkirim.push(k.bacaan);
    },
  });
  l.antrekan(1, kejadian('L1111AA'));
  l.antrekan(1, kejadian('L2222BB'));
  l.antrekan(1, kejadian('L3333CC'));

  const hasil = await l.susulkan();
  assert.deepEqual(terkirim, ['L1111AA']);
  assert.equal(hasil.terkirim, 1);
  assert.equal(hasil.tersisa, 2, 'yang di belakang kegagalan harus tetap menunggu, bukan dilompati');
});

test('penyusulan dua kali berbarengan tidak mengirim kejadian yang sama dua kali', async () => {
  // Layar gerbang bisa memicu penyusulan dari dua tempat sekaligus (timer dan peristiwa "online").
  const terkirim = [];
  const l = buatLuring({
    simpanan: simpananTiruan(),
    kirim: async (gerbangId, k) => {
      await new Promise((r) => setTimeout(r, 10));
      terkirim.push(k.penanda);
    },
  });
  l.antrekan(1, kejadian('L1111AA'));
  l.antrekan(1, kejadian('L2222BB'));

  await Promise.all([l.susulkan(), l.susulkan()]);

  assert.equal(new Set(terkirim).size, terkirim.length, 'ada kejadian yang terkirim dua kali');
  assert.equal(terkirim.length, 2);
  assert.equal(l.jumlahAntre(), 0);
});

test('antrean kosong tidak memanggil pengirim sama sekali', async () => {
  let dipanggil = 0;
  const l = buatLuring({ simpanan: simpananTiruan(), kirim: async () => { dipanggil += 1; } });
  const hasil = await l.susulkan();
  assert.equal(dipanggil, 0);
  assert.deepEqual(hasil, { terkirim: 0, tersisa: 0 });
});

test('penyimpanan yang menolak menulis tidak membuat layar gerbang mati', () => {
  // Peramban bisa menolak menyimpan (jendela penyamaran, kuota penuh). Layar gerbang harus tetap bekerja,
  // walau catatannya tidak selamat dari muat ulang — dan itu harus terlihat dari jumlah antreannya.
  const simpanan = {
    getItem: () => null,
    setItem: () => { throw new Error('kuota penuh'); },
    removeItem: () => {},
  };
  const l = buatLuring({ simpanan, kirim: async () => {} });
  assert.doesNotThrow(() => l.antrekan(1, kejadian('L1234AB')));
  assert.equal(l.jumlahAntre(), 1, 'antrean dalam ingatan tetap jalan walau penyimpanan menolak');
});
