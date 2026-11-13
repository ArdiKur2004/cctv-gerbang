// Uji tgt/simpan.mjs: masa simpan data (Rencana T3 Task 1, keputusan owner K71).
//
// "Data tidak boleh disimpan semua" (K71). Masa simpan yang hanya tertulis di spec tidak menghapus apa pun, jadi
// penghapusnya diuji DUA ARAH: yang lewat masa simpan hilang, DAN yang masih di dalamnya tetap ada. Uji satu arah
// bisa lulus oleh penghapus yang membuang segalanya.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import { buatGrup, buatGerbang, daftarkanKendaraan, tambahTamu, catatKejadian } from '../layanan.mjs';
import { masaSimpan, bersihkan, SELAMANYA } from '../simpan.mjs';

/** Waktu dalam bentuk yang dipakai kejadian: ISO jam setempat, n hari yang lalu. */
function hariLalu(n, jam = 8) {
  const t = new Date(Date.now() - n * 24 * 60 * 60 * 1000);
  const dua = (x) => String(x).padStart(2, '0');
  return `${t.getFullYear()}-${dua(t.getMonth() + 1)}-${dua(t.getDate())}T${dua(jam)}:00:00`;
}

function siapkan() {
  const db = buka(':memory:');
  const grup = buatGrup(db, { nama: 'PT Contoh', jenis: 'perusahaan' });
  const gerbang = buatGerbang(db, {
    grupId: grup.id, nama: 'Gate Contoh', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
  });
  return { db, gerbang };
}

const hitung = (db, tabel) => db.prepare(`SELECT count(*) AS n FROM ${tabel}`).get().n;

// ─── Masa simpan dibaca, tidak disalin ──────────────────────────────────────────────────────────────

test('masa simpan dibaca dari pengaturan, bukan angka yang dipaku di kode', () => {
  // ⛔ DIBALIK (K74, owner 26 Okt), bukan dihapus. Dulu uji ini menuntut bawaan foto 7 hari dan kejadian 90
  // hari, "sama dengan spec §8". Angka itu tebakan agen atas kalimat owner "data tidak boleh di simpan semua",
  // dan tebakannya salah: owner bermaksud SEMUA DATA WAJIB DISIMPAN. Sekarang yang dijaga adalah tidak ada
  // angka bawaan sama sekali, DAN bahwa angka yang disetel dengan sengaja tetap terbaca.
  const asli = { ...process.env };
  try {
    delete process.env.TGT_SIMPAN_KEJADIAN;
    delete process.env.TGT_SIMPAN_FOTO;
    delete process.env.TGT_SIMPAN_TAMU;
    const bawaan = masaSimpan();
    assert.equal(bawaan.foto, SELAMANYA, 'masih ada masa simpan foto bawaan: foto orang akan terhapus sendiri');
    assert.equal(bawaan.kejadian, SELAMANYA);
    assert.equal(bawaan.tamu, SELAMANYA);

    process.env.TGT_SIMPAN_KEJADIAN = '30';
    assert.equal(masaSimpan().kejadian, 30, 'pengaturan tidak terbaca: angkanya dipaku di kode');
  } finally {
    process.env = asli;
  }
});

test('⛔ masa simpan yang tidak masuk akal berarti SIMPAN SELAMANYA, bukan galat dan bukan menghapus', () => {
  // ⛔ DIBALIK (K74), bukan dihapus. Dulu nilai seperti ini melempar galat. Galat saat server menyala bisa
  // membuat orang menghapus pengaturannya lalu memakai bawaan — dan bawaan yang lama MENGHAPUS. Arah gagalnya
  // sekarang: apa pun yang tidak terbaca sebagai jumlah hari yang masuk akal = simpan. Menghapus data orang
  // hanya terjadi bila ada yang menuliskan angkanya dengan sengaja.
  const asli = { ...process.env };
  try {
    for (const nilai of ['0', '-5', 'entah', '1.5', '', ' ', 'selamanya', '7 hari']) {
      process.env.TGT_SIMPAN_KEJADIAN = nilai;
      assert.doesNotThrow(() => masaSimpan(), `nilai ${nilai} seharusnya tidak melempar galat`);
      assert.equal(masaSimpan().kejadian, SELAMANYA, `nilai "${nilai}" tidak dibaca sebagai simpan selamanya`);
    }
  } finally {
    process.env = asli;
  }
});

// ─── Kejadian ───────────────────────────────────────────────────────────────────────────────────────

test('kejadian yang lewat masa simpan dihapus, yang masih di dalamnya TETAP ADA', () => {
  const { db, gerbang } = siapkan();
  try {
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(200), arah: 'masuk', plat: 'L 1111 AA' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(91), arah: 'masuk', plat: 'L 2222 BB' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(89), arah: 'masuk', plat: 'L 3333 CC' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(1), arah: 'masuk', plat: 'L 4444 DD' });

    const hasil = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hasil.kejadian, 2, 'dua kejadian lewat masa simpan seharusnya terhapus');
    const sisa = db.prepare('SELECT plat FROM kejadian ORDER BY waktu').all().map((k) => k.plat);
    assert.deepEqual(sisa, ['L3333CC', 'L4444DD'], 'kejadian yang masih di dalam masa simpan ikut terbuang');
  } finally {
    db.close();
  }
});

test('kendaraan terdaftar tidak pernah ikut terhapus oleh pembersih kejadian', () => {
  const { db, gerbang } = siapkan();
  try {
    daftarkanKendaraan(db, { gerbangId: gerbang.id, jenis: 'mobil', plat: 'L 5555 EE', atasNama: 'Budi' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(200), arah: 'masuk', plat: 'L 5555 EE' });

    bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hitung(db, 'kendaraan'), 1, 'kendaraan penghuni bukan catatan keluar masuk: ia tidak kedaluwarsa');
    assert.equal(hitung(db, 'kejadian'), 0);
  } finally {
    db.close();
  }
});

// ─── Tamu ───────────────────────────────────────────────────────────────────────────────────────────

test('tamu yang kunjungannya sudah selesai dan lewat masa simpan terhapus beserta kunjungannya', () => {
  const { db, gerbang } = siapkan();
  try {
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Lama', jenis: 'mobil', plat: 'W 1111 AA', lamaHari: 1 });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(60), arah: 'masuk', plat: 'W 1111 AA' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(60, 17), arah: 'keluar', plat: 'W 1111 AA' });
    assert.equal(hitung(db, 'kunjungan'), 1);

    const hasil = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hasil.tamu, 1);
    assert.equal(hitung(db, 'tamu'), 0);
    assert.equal(hitung(db, 'kunjungan'), 0, 'kunjungan tidak boleh tertinggal menunjuk tamu yang sudah hilang');
  } finally {
    db.close();
  }
});

test('tamu dihapus lebih dulu daripada kejadiannya: namanya hilang, catatan gerbangnya tetap', () => {
  // Keputusan rancangan, bukan kebetulan. Masa simpan tamu (30 hari) lebih pendek daripada kejadian (90 hari),
  // jadi saat tamu dihapus, kejadiannya masih ada dan menunjuk kepadanya.
  // Yang dipilih: tautan ke tamu DIPUTUS, kejadiannya TETAP. Alasannya dua-duanya penting —
  // "data tidak boleh disimpan semua" (K71) berarti nama dan undangan tamu tidak disimpan lebih lama dari
  // perlunya, sementara satpam tetap butuh catatan apa yang lewat gerbang selama 90 hari.
  const { db, gerbang } = siapkan();
  try {
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Lama', jenis: 'mobil', plat: 'W 9999 ZZ', lamaHari: 1 });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(60), arah: 'masuk', plat: 'W 9999 ZZ' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(60, 17), arah: 'keluar', plat: 'W 9999 ZZ' });
    assert.equal(db.prepare('SELECT count(*) AS n FROM kejadian WHERE tamu_id IS NOT NULL').get().n, 2);

    bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hitung(db, 'tamu'), 0, 'nama tamu harus hilang sesudah masa simpannya lewat');
    assert.equal(hitung(db, 'kejadian'), 2, 'catatan gerbang belum lewat 90 hari: ia tidak boleh ikut terhapus');
    assert.equal(
      db.prepare('SELECT count(*) AS n FROM kejadian WHERE tamu_id IS NOT NULL').get().n, 0,
      'kejadian masih menunjuk tamu yang sudah dihapus',
    );
  } finally {
    db.close();
  }
});

test('tamu yang kunjungannya baru selesai TIDAK terhapus', () => {
  const { db, gerbang } = siapkan();
  try {
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Kemarin', jenis: 'mobil', plat: 'W 2222 BB', lamaHari: 1 });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(2), arah: 'masuk', plat: 'W 2222 BB' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(2, 17), arah: 'keluar', plat: 'W 2222 BB' });

    bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hitung(db, 'tamu'), 1);
    assert.equal(hitung(db, 'kunjungan'), 1);
  } finally {
    db.close();
  }
});

test('⛔ tamu yang MASIH DI DALAM tidak pernah terhapus, walau sudah sangat lama', () => {
  // Kalau tamu yang masih di dalam ikut terhapus, satpam kehilangan catatan siapa yang ada di dalam gerbang.
  const { db, gerbang } = siapkan();
  try {
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Betah', jenis: 'truk', plat: 'W 3333 CC', lamaHari: 1 });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(300), arah: 'masuk', plat: 'W 3333 CC' });

    const hasil = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hasil.tamu, 0);
    assert.equal(hitung(db, 'tamu'), 1, 'tamu yang masih di dalam terhapus: catatan siapa di dalam gerbang hilang');
    assert.equal(db.prepare('SELECT status FROM kunjungan').get().status, 'di_dalam');
  } finally {
    db.close();
  }
});

test('tamu yang belum pernah masuk sama sekali ikut masa simpan, dihitung dari saat dibuat', () => {
  const { db, gerbang } = siapkan();
  try {
    // Undangan yang tak pernah dipakai tidak boleh tersimpan selamanya (K71).
    tambahTamu(db, { gerbangId: gerbang.id, nama: 'Tamu Batal', jenis: 'mobil', plat: 'W 4444 DD', lamaHari: 1 });
    db.prepare("UPDATE tamu SET dibuat = datetime('now', '-60 days')").run();

    const hasil = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(hasil.tamu, 1);
    assert.equal(hitung(db, 'tamu'), 0);
  } finally {
    db.close();
  }
});

// ─── Sifat umum pembersih ───────────────────────────────────────────────────────────────────────────

test('bersihkan dua kali tidak menghapus apa pun lagi', () => {
  const { db, gerbang } = siapkan();
  try {
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(200), arah: 'masuk', plat: 'L 1111 AA' });
    catatKejadian(db, { gerbangId: gerbang.id, waktu: hariLalu(1), arah: 'masuk', plat: 'L 2222 BB' });

    const pertama = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });
    const kedua = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });

    assert.equal(pertama.kejadian, 1);
    assert.deepEqual({ ...kedua, foto: 0 }, { kejadian: 0, tamu: 0, kunjungan: 0, foto: 0 });
    assert.equal(hitung(db, 'kejadian'), 1);
  } finally {
    db.close();
  }
});

test('bersihkan pada basis kosong tidak gagal dan melaporkan nol', () => {
  const { db } = siapkan();
  try {
    const hasil = bersihkan(db, { kejadian: 90, foto: 7, tamu: 30 });
    assert.equal(hasil.kejadian, 0);
    assert.equal(hasil.tamu, 0);
  } finally {
    db.close();
  }
});
