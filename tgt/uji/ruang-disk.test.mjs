// Uji pagar ruang disk (keputusan owner 26 Okt: "pastikan di PC IBE tidak mengganggu MES Yanmar").
//
// ⛔ KENAPA PAGAR INI ADA, dan kenapa bentuknya begini.
// TGT akan dipasang di PC yang menjalankan MES Yanmar — perangkat lunak yang dipakai orang sungguhan untuk
// bekerja (K71). Prinsip #3: perkakas yang kita jalankan TIDAK BOLEH membunuh mesin yang menjalankannya.
// Disk penuh di mesin produksi bukan gangguan kecil: basis data tidak bisa menulis, log berhenti, dan
// perangkat lunak lain ikut gagal dengan cara yang sulit dilacak.
//
// Dan sejak K74 (semua data wajib disimpan), pagarnya TIDAK BOLEH berupa penghapusan. Jadi arahnya:
// **berhenti menulis yang baru, jangan pernah menghapus yang lama, dan berteriak.**
//
// Diukur 26 Okt: basis data TGT tumbuh 190 bita per kejadian — 10 MB setahun pada 150 kendaraan sehari. Itu
// aman. Yang akan menjadi besar adalah foto bukti (4–42 GB setahun per gerbang), dan foto itu BELUM ditulis
// apa pun. Pagar ini dipasang sebelum foto ada, bukan sesudah disk MES penuh.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { SISA_DISK_MINIMUM, sisaDisk, ruangCukup, periksaRuang } from '../ruang.mjs';
import { buatJembatan } from '../jembatan.mjs';

function folderSementara() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'tgt-ruang-'));
}

test('sisaDisk membaca ruang kosong sungguhan, dalam bita', () => {
  const s = sisaDisk(os.tmpdir());
  assert.ok(Number.isFinite(s), `sisa disk tidak terbaca: ${s}`);
  assert.ok(s > 0, 'sisa disk nol atau negatif: pembacaannya salah');
  // Laptop ini punya ruang; kalau pembacaannya memberi angka di bawah 1 MB, satuannya pasti salah.
  assert.ok(s > 1024 * 1024, `sisa disk ${s} bita terlalu kecil untuk masuk akal: satuannya salah`);
});

test('sisaDisk pada jalur yang tidak ada memberi undefined, bukan melempar', () => {
  // Folder foto bisa belum ada. Pagar yang melempar di situ akan menjatuhkan gerbang karena hal yang bukan
  // masalah — dan gerbang yang tidak bisa menyala lebih buruk daripada gerbang yang tidak menyimpan foto.
  assert.equal(sisaDisk(path.join(os.tmpdir(), 'folder-tgt-yang-tidak-ada-123456')), undefined);
});

test(`batas bawaan ${SISA_DISK_MINIMUM / 1024 / 1024 / 1024} GB dibaca dari satu tempat, bukan disalin`, () => {
  assert.ok(Number.isInteger(SISA_DISK_MINIMUM));
  // Cukup besar supaya MES dan sistem operasinya masih punya ruang bernapas, cukup kecil supaya TGT tidak
  // berhenti menulis di mesin kecil yang sehat.
  assert.ok(SISA_DISK_MINIMUM >= 1024 ** 3, 'batas di bawah 1 GB: terlalu dekat dengan disk penuh');
  assert.ok(SISA_DISK_MINIMUM <= 20 * 1024 ** 3, 'batas di atas 20 GB: TGT akan menolak menulis di mesin sehat');
});

test('ruangCukup benar saat ruang banyak, dan salah saat batasnya dinaikkan melebihi ruang yang ada', () => {
  const folder = folderSementara();
  try {
    assert.equal(ruangCukup(folder), true, 'ruang di folder sementara seharusnya cukup');
    // Batas dipaksa lebih besar daripada seluruh disk: ini cara menguji cabang "tidak cukup" tanpa benar-benar
    // mengisi disk laptop ini sampai penuh — mengisi disk sungguhan justru melanggar Prinsip #3.
    assert.equal(ruangCukup(folder, Number.MAX_SAFE_INTEGER), false);
  } finally {
    fs.rmSync(folder, { recursive: true, force: true });
  }
});

test('⛔ ruang yang tidak bisa dibaca dianggap CUKUP, bukan tidak cukup', () => {
  // Arah gagalnya disengaja dan berbeda dari gerbang uang. Kalau pembacaan ruang gagal (jaringan, izin, sistem
  // berkas yang tidak dikenal), yang lebih buruk adalah gerbang berhenti mencatat kendaraan yang lewat.
  // Catatan yang hilang tidak bisa dibuat ulang; disk yang penuh masih memberi tanda lain.
  const tidakAda = path.join(os.tmpdir(), 'folder-tgt-yang-tidak-ada-123456');
  assert.equal(ruangCukup(tidakAda), true, 'ruang yang tidak terbaca dianggap tidak cukup: gerbang berhenti mencatat');
});

test('periksaRuang memberi kalimat yang bisa dimengerti, beserta angkanya', () => {
  const folder = folderSementara();
  try {
    const baik = periksaRuang(folder);
    assert.equal(baik.cukup, true);
    assert.match(baik.pesan, /GB/, 'kalimatnya tidak menyebut angka');

    const sempit = periksaRuang(folder, Number.MAX_SAFE_INTEGER);
    assert.equal(sempit.cukup, false);
    assert.match(sempit.pesan, /tidak|kurang|penuh/i);
    // Yang membaca ini bisa jadi satpam atau pemilik pabrik, bukan pemrogram.
    assert.doesNotMatch(sempit.pesan, /ENOSPC|statfs|errno/i, 'kalimatnya memakai istilah pemrogram');
  } finally {
    fs.rmSync(folder, { recursive: true, force: true });
  }
});

// ─── Rantai: jembatan kamera benar-benar menolak menulis saat disk sempit ────────────────────────────

test('⛔ RANTAI: jembatan kamera MENOLAK menulis gambar saat ruang disk di bawah batas', async () => {
  // Rantainya, bukan cabangnya: pagar yang benar tetapi tidak dipasang di jalur tulis terlihat persis seperti
  // pagar yang bekerja. Ini jalur satu-satunya yang menulis gambar hari ini.
  const akar = folderSementara();
  try {
    const jembatan = buatJembatan({
      masuk: path.join(akar, 'masuk'),
      keluar: path.join(akar, 'keluar'),
      // Batas dipaksa setinggi mungkin, bukan dengan mengisi disk sungguhan.
      sisaMinimum: Number.MAX_SAFE_INTEGER,
    });
    await assert.rejects(
      async () => jembatan.kirim(Buffer.from('gambar palsu'), {}, '.png'),
      /ruang|penuh|disk/i,
      'jembatan tetap menulis walau disk sempit',
    );
    // Dan tidak ada berkas yang tertinggal setengah jadi.
    const isi = fs.existsSync(path.join(akar, 'masuk')) ? fs.readdirSync(path.join(akar, 'masuk')) : [];
    assert.deepEqual(isi, [], `ada berkas tertinggal: ${isi.join(', ')}`);
  } finally {
    fs.rmSync(akar, { recursive: true, force: true });
  }
});

test('jembatan kamera tetap bekerja normal saat ruang cukup', () => {
  const akar = folderSementara();
  try {
    const jembatan = buatJembatan({ masuk: path.join(akar, 'masuk'), keluar: path.join(akar, 'keluar') });
    const id = jembatan.kirim(Buffer.from('gambar palsu'), { gerbangId: 1 }, '.png');
    assert.equal(typeof id, 'string');
    assert.ok(fs.readdirSync(path.join(akar, 'masuk')).some((n) => n.startsWith(id)),
      'pagar ruang disk ikut menolak tulisan yang seharusnya boleh');
  } finally {
    fs.rmSync(akar, { recursive: true, force: true });
  }
});
