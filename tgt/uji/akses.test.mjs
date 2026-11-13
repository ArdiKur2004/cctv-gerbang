// Uji tgt/akses.mjs: pintu hak akses (Rencana T2 Task 3).
//
// Tiap operasi diuji DUA arah: peran yang boleh berhasil, dan tiap peran lain ditolak. Pagar yang hanya diuji
// pada arah "boleh" tidak membuktikan apa pun.
import { test } from 'node:test';
import assert from 'node:assert/strict';

import { buka } from '../basis.mjs';
import { buatAkun, buatGrupBaru, ikutGrup, tetapkanPeran } from '../akun.mjs';
import * as akses from '../akses.mjs';

const SANDI = 'sandi-contoh-1';

/**
 * Satu grup berisi tiga peran, plus satu orang luar dan satu grup lain.
 * Sesi di sini sengaja hanya memuat penggunaId: pagar tidak boleh percaya peran yang dikirim pemanggil.
 */
function siapkan() {
  const db = buka(':memory:');

  const bos = buatAkun(db, { nama: 'Bos Contoh', wa: '081200000001', sandi: SANDI });
  const { grup } = buatGrupBaru(db, bos.id, { nama: 'PT Contoh Niaga', jenis: 'perusahaan' });

  const pakSatpam = buatAkun(db, { nama: 'Pak Satpam', wa: '081200000002', sandi: SANDI });
  ikutGrup(db, pakSatpam.id, grup.kode_undangan);
  tetapkanPeran(db, grup.id, pakSatpam.id, 'satpam');

  const karyawan = buatAkun(db, { nama: 'Karyawan Contoh', wa: '081200000003', sandi: SANDI });
  ikutGrup(db, karyawan.id, grup.kode_undangan);

  const orangLuar = buatAkun(db, { nama: 'Orang Luar', wa: '081200000004', sandi: SANDI });
  const { grup: grupLain } = buatGrupBaru(db, orangLuar.id, { nama: 'Grup Lain', jenis: 'pribadi' });

  const sesi = (orang) => ({ penggunaId: orang.id });
  const gerbang = akses.buatGerbang(db, sesi(bos), {
    grupId: grup.id, nama: 'Kantor Contoh Gate Selatan', jenisLokasi: 'kantor',
    alamat: 'Jl. Contoh Industri III No. 42', kota: 'Surabaya',
  });

  return { db, grup, grupLain, gerbang, sesi, bos, pakSatpam, karyawan, orangLuar };
}

const DATA_GERBANG = (grupId) => ({
  grupId, nama: 'Gate Baru', jenisLokasi: 'kantor', alamat: 'Jl. Contoh 1', kota: 'Surabaya',
});

// ─── Tanpa sesi ─────────────────────────────────────────────────────────────────────────────────────

test('tanpa sesi, semua pintu tertutup', () => {
  const { db, grup, gerbang } = siapkan();
  try {
    for (const [nama, panggil] of [
      ['buatGerbang', (s) => akses.buatGerbang(db, s, DATA_GERBANG(grup.id))],
      ['lihatGerbang', (s) => akses.lihatGerbang(db, s, gerbang.id)],
      ['gerbangSaya', (s) => akses.gerbangSaya(db, s)],
      ['aktifkanGerbang', (s) => akses.aktifkanGerbang(db, s, gerbang.id)],
      ['anggotaGrup', (s) => akses.anggotaGrup(db, s, grup.id)],
      ['grupSaya', (s) => akses.grupSaya(db, s)],
    ]) {
      for (const sesi of [undefined, null, {}, { penggunaId: null }, { penggunaId: 0 }]) {
        assert.throws(() => panggil(sesi), /masuk/i, `${nama} dengan sesi ${JSON.stringify(sesi)} harus ditolak`);
      }
    }
  } finally {
    db.close();
  }
});

test('sesi yang menyebut pengguna tak ada ditolak, bukan dianggap pengguna baru', () => {
  const { db, grup } = siapkan();
  try {
    assert.throws(() => akses.buatGerbang(db, { penggunaId: 9999 }, DATA_GERBANG(grup.id)), /masuk/i);
  } finally {
    db.close();
  }
});

test('peran yang dikirim pemanggil TIDAK dipercaya: peran dibaca dari basis data', () => {
  const { db, grup, karyawan } = siapkan();
  try {
    // Penghuni yang mengaku pengelola tetap ditolak.
    assert.throws(
      () => akses.buatGerbang(db, { penggunaId: karyawan.id, peran: 'pengelola' }, DATA_GERBANG(grup.id)),
      /tidak berhak/i,
    );
  } finally {
    db.close();
  }
});

// ─── Membuat gerbang: pengelola saja ────────────────────────────────────────────────────────────────

test('pengelola boleh membuat gerbang; satpam dan penghuni ditolak', () => {
  const { db, grup, sesi, bos, pakSatpam, karyawan } = siapkan();
  try {
    const g = akses.buatGerbang(db, sesi(bos), DATA_GERBANG(grup.id));
    assert.equal(g.nama, 'Gate Baru');
    assert.equal(g.status, 'belum_aktif');

    for (const orang of [pakSatpam, karyawan]) {
      assert.throws(() => akses.buatGerbang(db, sesi(orang), DATA_GERBANG(grup.id)), /tidak berhak/i);
    }
    assert.equal(akses.gerbangSaya(db, sesi(bos)).length, 2, 'hanya satu gerbang baru yang boleh tercipta');
  } finally {
    db.close();
  }
});

test('pengelola grup lain tidak bisa membuat gerbang di grup ini, dan tidak diberi tahu grup itu ada', () => {
  const { db, grup, sesi, orangLuar } = siapkan();
  try {
    // Sengaja "tidak ditemukan", BUKAN "tidak berhak": jawaban "tidak berhak" akan membenarkan bahwa grup
    // bernomor itu ada, dan orang luar bisa memakainya untuk menebak-nebak isi sistem.
    assert.throws(() => akses.buatGerbang(db, sesi(orangLuar), DATA_GERBANG(grup.id)), /tidak ditemukan/i);
    assert.equal(db.prepare('SELECT count(*) AS n FROM gerbang').get().n, 1, 'tidak ada gerbang yang tercipta');
  } finally {
    db.close();
  }
});

test('mengaktifkan gerbang: pengelola saja', () => {
  const { db, gerbang, sesi, bos, pakSatpam, karyawan } = siapkan();
  try {
    for (const orang of [pakSatpam, karyawan]) {
      assert.throws(() => akses.aktifkanGerbang(db, sesi(orang), gerbang.id), /tidak berhak/i);
    }
    assert.equal(akses.lihatGerbang(db, sesi(bos), gerbang.id).status, 'belum_aktif');
    assert.equal(akses.aktifkanGerbang(db, sesi(bos), gerbang.id).status, 'aktif');
  } finally {
    db.close();
  }
});

// ─── Membaca gerbang: semua anggota, tidak melintas grup ────────────────────────────────────────────

test('ketiga peran boleh membaca gerbang grupnya', () => {
  const { db, gerbang, sesi, bos, pakSatpam, karyawan } = siapkan();
  try {
    for (const orang of [bos, pakSatpam, karyawan]) {
      assert.equal(akses.lihatGerbang(db, sesi(orang), gerbang.id).id, gerbang.id);
      assert.deepEqual(akses.gerbangSaya(db, sesi(orang)).map((g) => g.id), [gerbang.id]);
    }
  } finally {
    db.close();
  }
});

test('orang luar tidak bisa membaca gerbang grup ini, dan daftarnya kosong', () => {
  const { db, gerbang, sesi, orangLuar } = siapkan();
  try {
    assert.throws(() => akses.lihatGerbang(db, sesi(orangLuar), gerbang.id), /tidak ditemukan/i);
    assert.deepEqual(akses.gerbangSaya(db, sesi(orangLuar)), []);
  } finally {
    db.close();
  }
});

test('pesan penolakan tidak membedakan "gerbang tidak ada" dari "bukan grup Anda"', () => {
  const { db, gerbang, sesi, orangLuar } = siapkan();
  try {
    let pesanGrupLain;
    let pesanTakAda;
    assert.throws(() => akses.lihatGerbang(db, sesi(orangLuar), gerbang.id), (e) => {
      pesanGrupLain = e.message;
      return true;
    });
    assert.throws(() => akses.lihatGerbang(db, sesi(orangLuar), 99999), (e) => {
      pesanTakAda = e.message;
      return true;
    });
    assert.equal(
      pesanGrupLain, pesanTakAda,
      'pesan yang berbeda memberi tahu orang luar gerbang mana yang ada',
    );
  } finally {
    db.close();
  }
});

// ─── Anggota grup: nomor WA hanya untuk pengelola ───────────────────────────────────────────────────

test('daftar anggota beserta nomor WA hanya boleh dibaca pengelola', () => {
  const { db, grup, sesi, bos, pakSatpam, karyawan, orangLuar } = siapkan();
  try {
    assert.equal(akses.anggotaGrup(db, sesi(bos), grup.id).length, 3);
    for (const orang of [pakSatpam, karyawan]) {
      assert.throws(() => akses.anggotaGrup(db, sesi(orang), grup.id), /tidak berhak/i);
    }
    assert.throws(() => akses.anggotaGrup(db, sesi(orangLuar), grup.id), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

test('mengubah peran: pengelola saja, dan tidak bisa menyentuh grup lain', () => {
  const { db, grup, sesi, bos, pakSatpam, karyawan, orangLuar } = siapkan();
  try {
    assert.equal(akses.tetapkanPeran(db, sesi(bos), grup.id, karyawan.id, 'satpam'), 'satpam');
    for (const orang of [pakSatpam, karyawan]) {
      assert.throws(() => akses.tetapkanPeran(db, sesi(orang), grup.id, karyawan.id, 'pengelola'), /tidak berhak/i);
    }
    assert.throws(() => akses.tetapkanPeran(db, sesi(orangLuar), grup.id, karyawan.id, 'pengelola'), /tidak ditemukan/i);
  } finally {
    db.close();
  }
});

// ─── Grup: siapa pun yang sudah masuk ───────────────────────────────────────────────────────────────

test('siapa pun yang sudah masuk boleh membuat grup dan ikut grup', () => {
  const { db, sesi, karyawan } = siapkan();
  try {
    const baru = akses.buatGrup(db, sesi(karyawan), { nama: 'Rumah Karyawan', jenis: 'pribadi' });
    assert.equal(baru.peran, 'pengelola');

    // Di grupnya sendiri ia pengelola, di grup kantor tetap penghuni.
    const daftar = akses.grupSaya(db, sesi(karyawan));
    assert.deepEqual(daftar.map((g) => g.peran).sort(), ['pengelola', 'penghuni']);
  } finally {
    db.close();
  }
});

test('grupSaya tidak pernah memuat kode undangan grup yang bukan dikelolanya', () => {
  const { db, sesi, karyawan } = siapkan();
  try {
    // Kode undangan = cara masuk grup. Penghuni yang memegangnya bisa mengundang orang tanpa izin pengelola.
    const [kantor] = akses.grupSaya(db, sesi(karyawan)).filter((g) => g.peran === 'penghuni');
    assert.equal(kantor.kode_undangan, undefined);
  } finally {
    db.close();
  }
});
