// Jembatan berkas antara TGT dan mesin baca plat. Rencana T6.
//
// Mesin baca berjalan di lab TANPA JARINGAN (tools/lab.ps1 memakai --network none), dan pagar itu tidak
// dicabut: justru ia yang membuat bobot model dari luar aman dijalankan. Jadi batas antara keduanya berbentuk
// folder, bukan port:
//
//     <masuk>/<id>.png   ← ditulis di sini
//     <masuk>/<id>.json  ← keterangan: gerbang, arah
//     <keluar>/<id>.json ← ditulis mesin baca (tools/lab/layanan_baca.py)
//
// ⛔ Yang paling berbahaya di jembatan ini bukan "lambat", melainkan MENGGANTUNG SELAMANYA: layar satpam yang
// menunggu hasil yang tidak pernah datang membuat gerbang berhenti bekerja tanpa pesan apa pun. Karena itu
// setiap penantian punya batas waktu, dan kiriman yang kedaluwarsa dibersihkan.
//
// ⛔ Kedua folder memuat gambar kendaraan dan nomor plat. Berkasnya dibuang segera sesudah dipakai; ia tidak
// boleh menumpuk di folder antrean (K71).
import fs from 'node:fs';
import path from 'node:path';
import { randomBytes } from 'node:crypto';

import { periksaRuang } from './ruang.mjs';

const BATAS_BAWAAN_MS = 15000;
const JEDA_BAWAAN_MS = 200;

const tidur = (ms) => new Promise((r) => setTimeout(r, ms));

export function buatJembatan({ masuk, keluar, batasMs = BATAS_BAWAAN_MS, jedaMs = JEDA_BAWAAN_MS,
  sisaMinimum } = {}) {
  const jalurMasuk = (id, akhiran) => path.join(masuk, `${id}${akhiran}`);
  const jalurKeluar = (id) => path.join(keluar, `${id}.json`);

  const buang = (jalur) => {
    try {
      fs.rmSync(jalur, { force: true });
    } catch {
      // Berkas yang sedang dipegang proses lain akan terhapus di putaran berikutnya.
    }
  };

  return {
    /**
     * Titipkan satu gambar untuk dibaca. Mengembalikan penanda yang dipakai menunggu hasilnya.
     * Namanya acak dan panjang: folder ini dipakai bersama mesin, dan nama yang bisa ditebak mengundang
     * tabrakan maupun gangguan.
     */
    kirim(gambar, keterangan = {}, akhiran = '.png') {
      fs.mkdirSync(masuk, { recursive: true });

      // ⛔ Pagar ruang disk (owner 26 Okt: "pastikan di PC IBE tidak mengganggu MES Yanmar"). TGT dipasang di
      // komputer yang menjalankan MES, dan disk penuh di sana membuat perangkat lunak lain gagal dengan cara
      // yang sulit dilacak. Yang berhenti adalah tulisan BARU; catatan lama tidak pernah dihapus (K74).
      // Diperiksa SESUDAH folder dibuat, supaya pembacaan ruangnya mengenai disk yang benar.
      const ruang = periksaRuang(masuk, ...(sisaMinimum === undefined ? [] : [sisaMinimum]));
      if (!ruang.cukup) throw new Error(ruang.pesan);

      const id = randomBytes(12).toString('hex');
      // Keterangan ditulis LEBIH DULU, gambarnya belakangan: mesin memungut berdasarkan gambar, jadi saat
      // gambarnya muncul keterangannya sudah pasti ada.
      fs.writeFileSync(jalurMasuk(id, '.json'), JSON.stringify(keterangan));
      fs.writeFileSync(jalurMasuk(id, akhiran), gambar);
      return id;
    },

    /** Hasil yang sudah ada, atau null. Berkasnya dibuang begitu terbaca, jadi ia hanya bisa dibaca sekali. */
    ambil(id) {
      let teks;
      try {
        teks = fs.readFileSync(jalurKeluar(id), 'utf8');
      } catch {
        return null;
      }
      buang(jalurKeluar(id));
      try {
        return JSON.parse(teks);
      } catch {
        return { rusak: true };
      }
    },

    /**
     * Tunggu hasilnya sampai batas waktu. Melempar dengan pesan yang bisa dimengerti satpam — bukan galat
     * berkas — karena yang membacanya adalah orang di gerbang, bukan pemrogram.
     */
    async tungguHasil(id, akhiran = '.png') {
      const batas = Date.now() + batasMs;
      while (Date.now() < batas) {
        const hasil = this.ambil(id);
        if (hasil) {
          if (hasil.rusak) throw new Error('hasil dari mesin baca tidak terbaca (berkasnya rusak)');
          if (hasil.galat) throw new Error(`mesin baca melaporkan: ${hasil.galat}`);
          return hasil;
        }
        await tidur(jedaMs);
      }
      // Kedaluwarsa: gambarnya dibuang supaya tidak menumpuk, dan supaya mesin tidak memproses sesuatu yang
      // sudah tidak ada yang menunggu.
      buang(jalurMasuk(id, akhiran));
      buang(jalurMasuk(id, '.json'));
      throw new Error(
        'mesin baca tidak menjawab dalam batas waktu. Periksa apakah layanan bacanya sedang berjalan.',
      );
    },
  };
}
