// Uji mode demo: OTP ditampilkan di layar supaya bisa didemokan sebelum layanan surel dibeli.
//
// ⛔ Mode ini MEMBUKA KUNCI AKUN SIAPA PUN yang alamat emailnya diketahui: siapa pun yang bisa membuka
// layarnya bisa meminta kode untuk email mana pun dan langsung masuk. Karena itu pagarnya diuji lebih keras
// daripada fiturnya sendiri:
//   1. MATI kecuali dinyalakan dengan sengaja lewat pengaturan;
//   2. saat menyala, layarnya mengatakannya terang-terangan — tidak boleh ada demo yang terlihat seperti
//      keadaan sungguhan;
//   3. tidak ada jalan lain menyalakannya selain pengaturan itu.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { pengaturan } from '../pengaturan.mjs';

const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'web');

function dengan(nilai, jalankan) {
  const asli = process.env.TGT_DEMO_OTP;
  if (nilai === undefined) delete process.env.TGT_DEMO_OTP;
  else process.env.TGT_DEMO_OTP = nilai;
  try {
    jalankan();
  } finally {
    if (asli === undefined) delete process.env.TGT_DEMO_OTP;
    else process.env.TGT_DEMO_OTP = asli;
  }
}

test('⛔ mode demo MATI bila tidak diatur sama sekali', () => {
  dengan(undefined, () => assert.equal(pengaturan().demoOtp, false));
});

test('⛔ hanya nilai yang jelas menyalakannya; yang lain dianggap mati', () => {
  // Gagal ke arah menutup: salah ketik tidak boleh diam-diam menyalakan mode yang membuka kunci akun.
  for (const nilai of ['0', 'false', 'tidak', '', 'yes', 'TRUE ', 'demo', '2']) {
    dengan(nilai, () => assert.equal(pengaturan().demoOtp, false, `nilai ${JSON.stringify(nilai)} menyalakan demo`));
  }
});

test('nilai yang jelas menyalakannya', () => {
  for (const nilai of ['1', 'true']) {
    dengan(nilai, () => assert.equal(pengaturan().demoOtp, true, `nilai ${JSON.stringify(nilai)} seharusnya menyala`));
  }
});

test('layar punya tempat untuk pita peringatan mode demo', () => {
  const app = fs.readFileSync(path.join(WEB, 'app.js'), 'utf8');
  assert.match(app, /MODE DEMO/, 'layar harus menyebut mode demo terang-terangan saat ia menyala');
});
