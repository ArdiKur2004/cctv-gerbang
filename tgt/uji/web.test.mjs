// Penjaga berkas layar TGT (Rencana T2 Task 5).
//
// ⚠️ Apa yang berkas ini BISA dan TIDAK BISA buktikan.
// Ia hanya membaca sumbernya; ia tidak membuka halaman, jadi ia TIDAK membuktikan layarnya bekerja.
// Semua uji di sini lahir dari dua cacat yang ditemukan 26 Okt saat halaman dibuka di peramban sungguhan,
// ketika 220 uji lain sudah hijau. Gunanya mencegah cacat yang sama kembali diam-diam, bukan menggantikan
// pembuktian di peramban.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'web');
const baca = (nama) => fs.readFileSync(path.join(WEB, nama), 'utf8');

/**
 * Buang komentar sebelum memindai kode. Tanpa ini, penjaga di bawah menangkap komentar yang justru
 * MENJELASKAN cacatnya — dan itu sudah terjadi sekali saat berkas ini pertama dijalankan.
 */
const tanpaKomentar = (sumber) => sumber.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');

/**
 * SEMUA berkas .js di tgt/web, bukan app.js saja. Penjaga yang hanya melihat satu berkas akan melaporkan
 * bersih sambil tidak melihat berkas layar yang baru ditulis — dan berkas barulah yang paling mungkin memuat
 * cacat yang sama.
 */
const semuaJs = () => fs.readdirSync(WEB).filter((n) => n.endsWith('.js')).map((n) => [n, tanpaKomentar(baca(n))]);

test('gaya.css memaksa [hidden] benar-benar menyembunyikan', () => {
  // Cacat 1: atribut `hidden` hanyalah `display: none` dari gaya bawaan peramban, jadi `.cangkang { display: grid }`
  // dan `label.bidang { display: flex }` mengalahkannya — layar masuk tampil bersamaan dengan cangkang aplikasi.
  const gaya = baca('gaya.css');
  assert.match(
    gaya, /\[hidden\]\s*\{[^}]*display:\s*none\s*!important/,
    'aturan [hidden] { display: none !important } hilang: unsur ber-hidden akan tampil lagi',
  );
  // Kontrol positif: pola di atas memang bisa gagal, bukan cocok dengan apa saja.
  assert.doesNotMatch('[hidden] { display: none; }', /\[hidden\]\s*\{[^}]*display:\s*none\s*!important/);
});

test('tidak ada berkas layar yang merantai append(), karena append() mengembalikan undefined', () => {
  // Cacat 2: `tabel.append(document.createElement('thead')).append(baris)` melempar TypeError dan membuat
  // SELURUH isi halaman gagal digambar — tanpa satu pun uji server menjadi merah.
  const pola = /\.append\([^;]*\)\s*\.append\(/g;
  for (const [nama, isi] of semuaJs()) {
    assert.deepEqual(isi.match(pola) ?? [], [], `${nama}: ada rantai .append(...).append(...), yang melempar galat`);
  }
  assert.equal("t.append(document.createElement('thead')).append(x)".match(pola)?.length, 1,
    'pola pencarian rantai append tidak bekerja');
});

test('tidak ada berkas layar yang memakai innerHTML, karena nama dan alamat datang dari pengguna', () => {
  const pola = /\.innerHTML\s*=/g;
  for (const [nama, isi] of semuaJs()) {
    assert.deepEqual(isi.match(pola) ?? [], [],
      `${nama}: pakai textContent atau unsur(); innerHTML dengan isian pengguna membuka jalan penyisipan skrip`);
  }
  assert.equal('el.innerHTML = x'.match(pola)?.length, 1, 'pola innerHTML tidak bekerja');
});

test('halaman undangan memuat gaya, kodenya, dan pembuat QR', () => {
  const html = baca('undangan.html');
  assert.match(html, /href="gaya\.css"/);
  assert.match(html, /src="undangan\.js"/);
  assert.match(tanpaKomentar(baca('undangan.js')), /from\s+['"]\.\/qr\.js['"]/);
});

test('halaman memuat gaya dan kodenya, dan huruf dari jaringan punya cadangan', () => {
  const html = baca('index.html');
  assert.match(html, /href="gaya\.css"/);
  assert.match(html, /src="app\.js"/);
  const gaya = baca('gaya.css');
  // Huruf dari Google Fonts bisa gagal dimuat di gerbang tanpa jaringan: tiap tumpukan huruf wajib punya
  // cadangan huruf sistem, supaya halamannya tetap terbaca.
  for (const peubah of ['--display', '--teks', '--data']) {
    const baris = new RegExp(`${peubah}:[^;]*;`).exec(gaya)?.[0] ?? '';
    assert.match(baris, /(system-ui|ui-monospace|sans-serif|monospace)/,
      `${peubah} tidak punya huruf cadangan; halaman akan rusak bila Google Fonts tidak termuat`);
  }
});

test('halaman tidak memuat berkas dari luar selain huruf, supaya bisa jalan di jaringan tertutup', () => {
  const html = baca('index.html');
  const luar = [...html.matchAll(/(?:src|href)="(https?:\/\/[^"]+)"/g)].map((m) => m[1]);
  const bukanHuruf = luar.filter((u) => !/fonts\.(googleapis|gstatic)\.com/.test(u));
  assert.deepEqual(bukanHuruf, [],
    'ada berkas dari luar selain huruf: gerbang sering tanpa jaringan (Rencana T4)');
});

test('⛔ tangga sumbu grafik selalu bilangan bulat, berapa pun ramainya gerbang', async () => {
  // Yang dihitung adalah KENDARAAN. "3,75 kendaraan" tidak ada, dan angka pecahan di sumbu membuat orang
  // berhenti mempercayai grafiknya. Sempat terjadi saat beranda pertama dibuka di peramban.
  const { tanggaBulat } = await import('../web/tangga.js');
  for (let tertinggi = 1; tertinggi <= 500; tertinggi += 1) {
    const langkah = tanggaBulat(tertinggi / 4);
    assert.ok(Number.isInteger(langkah), `tangga ${langkah} bukan bilangan bulat untuk tertinggi ${tertinggi}`);
    assert.ok(langkah >= 1);
    assert.ok(langkah * 4 >= tertinggi, `sumbu ${langkah * 4} lebih pendek dari batang tertinggi ${tertinggi}`);
    // Tidak boleh jauh berlebihan: sumbu yang terlalu tinggi membuat semua batang terlihat pendek.
    assert.ok(langkah * 4 <= Math.max(4, tertinggi * 2.5), `sumbu ${langkah * 4} terlalu tinggi untuk ${tertinggi}`);
  }
});

test('halaman masuk lewat tautan memuat gaya dan kodenya', () => {
  const html = baca('undang.html');
  assert.match(html, /href="gaya\.css"/);
  assert.match(html, /src="undang\.js"/);
});

test('⛔ tanda undangan dibawa setelah "#", tidak pernah sebagai pertanyaan di alamat', () => {
  // Bagian setelah '#' tidak dikirim peramban ke server, jadi tandanya tidak masuk catatan server maupun
  // proksi. Kalau kelak ada yang menggantinya menjadi `?tanda=...`, kunci masuk warga akan tertulis di log.
  const app = tanpaKomentar(baca('app.js'));
  const undang = tanpaKomentar(baca('undang.js'));

  assert.match(app, /undang\.html#/, 'tautan yang dibuat pengelola harus memakai "#", bukan "?"');
  const pola = /undang\.html\?/g;
  for (const [nama, isi] of semuaJs()) {
    assert.deepEqual(isi.match(pola) ?? [], [], `${nama}: tanda undangan ditaruh di pertanyaan alamat`);
  }
  assert.equal("a.href = '/undang.html?tanda=' + t".match(pola)?.length, 1, 'pola pencarian tidak bekerja');

  // Dan halamannya memang membaca dari location.hash.
  assert.match(undang, /location\.hash/, 'undang.js tidak membaca tanda dari bagian setelah "#"');
});

test('⛔ halaman masuk lewat tautan tidak mengintip tanda sebelum dipakai', () => {
  // Jalur yang memeriksa tanda tanpa memakainya bisa dipakai menebak tanda sebanyak-banyaknya tanpa jejak.
  // Satu-satunya permintaan yang boleh dibuat halaman ini adalah menukarnya.
  const undang = tanpaKomentar(baca('undang.js'));
  const permintaan = [...undang.matchAll(/fetch\(\s*['"]([^'"]+)['"]/g)].map((m) => m[1]);
  assert.deepEqual(permintaan, ['/api/tautan-masuk'],
    `undang.js memanggil jalur lain: ${JSON.stringify(permintaan)}`);
});

test('⛔ tiap jalur DELETE di server punya pemanggil di layar', () => {
  // Pola yang ketemu tiga kali di Rencana T8 dan T10: jalur yang benar, diuji, dan tidak dipanggil siapa pun.
  // Dari luar ia terlihat persis seperti jalur yang bekerja. Penjaga ini membacanya dari sumber server.
  const server = tanpaKomentar(fs.readFileSync(path.join(WEB, '..', 'server.mjs'), 'utf8'));
  const layar = semuaJs().map(([, isi]) => isi).join('\n');

  /**
   * Awalan jalur yang TETAP dari satu pola regex di sumber server, misalnya `/api/grup/` dari
   * `/^\/api\/grup\/(\d+)\/anggota\/(\d+)$/`. Dibuat sesederhana mungkin: buang `\`, potong di `(` pertama.
   * Pola regex yang menguraikan pola regex lain pernah salah tulis di berkas ini, jadi di sini tidak ada.
   */
  const awalanTetap = (barisPola) => {
    const mulai = barisPola.indexOf('/^');
    const habis = barisPola.indexOf('$/');
    if (mulai < 0 || habis < 0) return '';
    return barisPola.slice(mulai + 2, habis).split('\\d')[0].split('(')[0].replaceAll('\\', '');
  };

  const hilang = [];

  // Bentuk 1: jalur berpola, misalnya `cara === 'DELETE' && kendaraanSatu`.
  for (const m of server.matchAll(/cara === 'DELETE' && (\w+)/g)) {
    const nama = m[1];
    const baris = server.split('\n').find((b) => b.includes(`const ${nama} = `)) ?? '';
    const tetap = awalanTetap(baris);
    if (tetap.length > 5 && !layar.includes(tetap)) hilang.push(`${nama} (${tetap})`);
  }

  // Bentuk 2: jalur tetap, misalnya `cara === 'DELETE' && jalur === '/api/langganan'`. Bentuk ini sempat
  // TERLEWAT oleh penjaga ini saat pertama ditulis, dan justru di bentuk inilah jalur yatimnya berada —
  // penjaga yang hanya mengenal satu bentuk melaporkan bersih sambil tidak melihat apa pun.
  for (const m of server.matchAll(/cara === 'DELETE' && jalur === '([^']+)'/g)) {
    if (!layar.includes(m[1])) hilang.push(`jalur tetap (${m[1]})`);
  }
  // Jalur yang memang bukan untuk layar ditulis di sini DENGAN ALASANNYA, bukan dibiarkan lewat diam-diam.
  const bolehTanpaLayar = [];
  const nyata = hilang.filter((h) => !bolehTanpaLayar.some((b) => h.includes(b)));
  assert.deepEqual(nyata, [], `jalur DELETE tanpa pemanggil di layar: ${nyata.join(', ')}`);

  // Kontrol positif: penjaga ini wajib benar-benar menemukan jalur DELETE, bukan nol karena polanya salah.
  const ketemu = [...server.matchAll(/cara === 'DELETE' && (\w+)/g)].length;
  assert.ok(ketemu >= 3, `hanya ${ketemu} jalur DELETE terbaca: pola pencarian penjaga ini tidak bekerja`);
});
