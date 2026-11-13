// Server TGT. Rencana T2, spec specs/2026-10-26-tgt-versi-1.md.
//
// ⛔ ATURAN YANG DIJAGA UJI: berkas ini TIDAK BOLEH mengimpor `./layanan.mjs`. Satu-satunya pintu ke data adalah
// `./akses.mjs`, yang memeriksa peran. Impor langsung akan menembus semua pagar itu tanpa satu pun uji menjadi
// merah, jadi `tgt/uji/server.test.mjs` membaca sumber berkas ini dan gagal bila impor itu muncul.
//
// Memakai `node:http` bawaan: tidak ada kerangka kerja dan tidak ada dependensi (CLAUDE.md §6).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { buka } from './basis.mjs';
import * as akses from './akses.mjs';
import { buatAkun, masuk, mintaOtp, masukDenganOtp, cetakOtp, PESAN_UNDANGAN_GAGAL } from './akun.mjs';
import { pengaturan, catatanCadangan, kunciVapid } from './pengaturan.mjs';
import { jadwalkanBersih } from './simpan.mjs';
import { periksaRuang } from './ruang.mjs';
import { buatKunciVapid, kirimSemua } from './dorong.mjs';
import { buatJembatan } from './jembatan.mjs';
import { UMUR_SESI_HARI, buatSesi, bacaSesi, hapusSesi } from './sesi.mjs';

const FOLDER_WEB = path.join(path.dirname(fileURLToPath(import.meta.url)), 'web');

const NAMA_KUKI = 'tgt_sesi';
// Dibaca dari sesi.mjs, tidak disalin: kalau umurnya berubah di satu tempat saja, kuki dan baris basis data
// akan kedaluwarsa pada waktu yang berbeda, dan yang terlihat adalah "kadang keluar sendiri".
const UMUR_KUKI_DETIK = UMUR_SESI_HARI * 24 * 60 * 60;

const JENIS_BERKAS = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.webmanifest': 'application/manifest+json',
};

/**
 * Sesi disimpan di BASIS DATA sejak Rencana T8, bukan lagi di sebuah Map di memori.
 *
 * Yang lama punya batas yang tertulis di sini selama lima rencana: server yang dinyalakan ulang membuat semua
 * orang masuk lagi. Itu berhenti menjadi sekadar merepotkan ketika cara masuk utama menjadi tautan undangan
 * SEKALI PAKAI — orang yang terlempar keluar tidak punya cara masuk kembali tanpa meminta tautan baru.
 *
 * Bentuk pemanggilannya sengaja dibiarkan sama (`buat`/`baca`/`hapus`), supaya yang berubah hanya tempat
 * penyimpanannya, bukan jalur-jalur di bawah.
 */
function gudangSesi(db) {
  return {
    buat: (penggunaId) => buatSesi(db, penggunaId),
    baca: (tanda) => bacaSesi(db, tanda),
    hapus: (tanda) => hapusSesi(db, tanda),
  };
}

function tandaDariKuki(kepala) {
  for (const bagian of String(kepala ?? '').split(';')) {
    const [nama, ...nilai] = bagian.trim().split('=');
    if (nama === NAMA_KUKI) return nilai.join('=');
  }
  return undefined;
}

function kirim(res, kode, badan) {
  const teks = JSON.stringify(badan ?? null);
  res.writeHead(kode, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
  res.end(teks);
}

async function bacaJson(req) {
  const potongan = [];
  let panjang = 0;
  for await (const p of req) {
    panjang += p.length;
    // Batas supaya satu permintaan tidak bisa menghabiskan memori.
    if (panjang > 64 * 1024) throw new GalatPermintaan('isi permintaan terlalu besar');
    potongan.push(p);
  }
  if (panjang === 0) return {};
  try {
    return JSON.parse(Buffer.concat(potongan).toString('utf8'));
  } catch {
    throw new GalatPermintaan('isi permintaan bukan JSON yang sah');
  }
}

class GalatPermintaan extends Error {}

// Galat diterjemahkan menjadi kode HTTP di SATU tempat, supaya tidak ada jalur yang lupa dan menjawab 200.
function kodeGalat(e) {
  if (e?.name === 'GalatAkses') {
    if (e.kode === 'perlu_masuk') return 401;
    if (e.kode === 'ditolak') return 403;
    return 404;
  }
  if (e?.name === 'GalatLayanan' || e instanceof GalatPermintaan) return 400;
  return 500;
}

function sajikanBerkas(res, jalurPermintaan) {
  const bersih = decodeURIComponent(jalurPermintaan.split('?')[0]);
  const relatif = bersih === '/' ? 'index.html' : bersih.replace(/^\/+/, '');
  const penuh = path.resolve(FOLDER_WEB, relatif);

  // Jalur yang keluar dari folder web ditolak. Diperiksa sesudah resolve, karena "..", "%2e%2e", dan jalur
  // bertumpuk semuanya berakhir di sini.
  if (penuh !== FOLDER_WEB && !penuh.startsWith(FOLDER_WEB + path.sep)) {
    kirim(res, 404, { galat: 'tidak ditemukan' });
    return;
  }
  let isi;
  try {
    isi = fs.readFileSync(penuh);
  } catch {
    kirim(res, 404, { galat: 'tidak ditemukan' });
    return;
  }
  res.writeHead(200, { 'content-type': JENIS_BERKAS[path.extname(penuh)] ?? 'application/octet-stream' });
  res.end(isi);
}

/**
 * Buat server. `db` disuntikkan supaya uji memakai basis data di memori dan tidak pernah menyentuh berkas
 * sungguhan yang memuat data pribadi.
 */
/**
 * Kirim notifikasi ke perangkat yang berlangganan, lalu buang langganan yang sudah tidak berlaku.
 *
 * ⛔ Kegagalan di sini TIDAK PERNAH menggagalkan kejadiannya: catatan gerbang sudah tersimpan sebelum fungsi
 * ini dipanggil. Yang hilang bila notifikasi gagal hanyalah pemberitahuannya, dan itu dicatat di layar server.
 */
async function doronglahDengan(db, notifikasi, vapid, kirimSemuaFn = kirimSemua) {
  try {
    const hasil = await kirimSemuaFn({
      penerima: notifikasi.penerima,
      isi: { judul: notifikasi.judul, pesan: notifikasi.pesan, sebab: notifikasi.sebab },
      vapid,
    });
    for (const h of hasil) {
      if (h.hilang) db.prepare('DELETE FROM langganan WHERE alamat = ?').run(h.alamat);
      else if (!h.terkirim) console.error(`[tgt] notifikasi gagal (${h.kode}) ke ${h.alamat.slice(0, 40)}…`);
    }
    return hasil;
  } catch (e) {
    console.error('[tgt] notifikasi gagal seluruhnya:', e.message);
    return [];
  }
}

/**
 * @param kirimOtp pengirim OTP yang bisa diganti. Bawaannya `undefined`, yang berarti pengirim bawaan
 *   `akun.mjs`: ia hanya MENCETAK kode di layar server dan tidak mengirim ke mana pun, karena layanan surel
 *   belum dibeli (keputusan owner, CLAUDE.md §8).
 */
export function buatServer({ db, vapid = kunciVapid(buatKunciVapid), kirimOtp, demoOtp = pengaturan().demoOtp,
  jembatan = buatJembatan({ masuk: pengaturan().jalurBacaMasuk, keluar: pengaturan().jalurBacaKeluar }) }) {
  const sesiKita = gudangSesi(db);
  const doronglah = (basis, notifikasi) => doronglahDengan(basis, notifikasi, vapid);

  const kirimSesi = (res, kode, badan, penggunaId) => {
    const tanda = sesiKita.buat(penggunaId);
    res.writeHead(kode, {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      // HttpOnly: tidak terbaca JavaScript halaman. SameSite=Strict: kuki tidak terkirim dari situs lain,
      // jadi ia sekaligus menjadi pagar CSRF yang pertama.
      'set-cookie': `${NAMA_KUKI}=${tanda}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${UMUR_KUKI_DETIK}`,
    });
    res.end(JSON.stringify(badan));
  };

  return http.createServer(async (req, res) => {
    const jalur = req.url ?? '/';
    const cara = req.method ?? 'GET';

    if (!jalur.startsWith('/api/')) {
      if (cara !== 'GET') {
        kirim(res, 405, { galat: 'cara tidak didukung' });
        return;
      }
      sajikanBerkas(res, jalur);
      return;
    }

    const sesi = sesiKita.baca(tandaDariKuki(req.headers.cookie));

    try {
      // ── Tanpa sesi ──
      if (cara === 'POST' && jalur === '/api/daftar') {
        const isi = await bacaJson(req);
        const orang = buatAkun(db, isi);
        kirimSesi(res, 201, { pengguna: orang }, orang.id);
        return;
      }
      if (cara === 'POST' && jalur === '/api/masuk') {
        const isi = await bacaJson(req);
        let orang;
        try {
          orang = masuk(db, isi);
        } catch {
          // Gagal masuk adalah 401, bukan 400: pesannya sama untuk nomor tak ada dan sandi salah.
          kirim(res, 401, { galat: 'nomor WhatsApp atau sandi salah' });
          return;
        }
        kirimSesi(res, 200, { pengguna: orang }, orang.id);
        return;
      }
      // ── Masuk dengan email + OTP (K72). Tanpa sesi, dan jawabannya TIDAK PERNAH memuat kodenya. ──
      if (cara === 'POST' && jalur === '/api/otp') {
        const isi = await bacaJson(req);
        // Mode demo: kodenya ikut keluar supaya bisa ditunjukkan di layar sebelum layanan surel dibeli.
        // Di luar mode demo ia TIDAK PERNAH ikut, dan ada ujinya.
        let kodeDemo = null;
        const tangkap = (alamat, kode) => {
          if (demoOtp) kodeDemo = kode;
          (kirimOtp ?? cetakOtp)(alamat, kode);
        };
        const hasil = mintaOtp(db, { email: isi.email, kirim: tangkap });
        kirim(res, 200, demoOtp ? { ...hasil, demo: true, kode: kodeDemo } : hasil);
        return;
      }
      if (cara === 'POST' && jalur === '/api/otp/masuk') {
        const isi = await bacaJson(req);
        let orang;
        try {
          orang = masukDenganOtp(db, isi);
        } catch {
          // Semua kegagalan OTP menjawab sama: kode salah, kedaluwarsa, habis percobaan, email tak dikenal.
          kirim(res, 401, { galat: 'kode tidak berlaku; mintalah kode baru' });
          return;
        }
        kirimSesi(res, 200, { pengguna: orang }, orang.id);
        return;
      }

      // ── Masuk lewat tautan undangan (Rencana T8). Cara masuk UTAMA sejak persetujuan owner 26 Okt. ──
      // Sengaja tanpa sesi: tautan inilah yang menggantikan sandi. Semua kegagalan menjawab 401 dengan
      // pesan yang SAMA — tanda palsu, tanda bekas, tanda kedaluwarsa, dan orang yang sudah dikeluarkan.
      if (cara === 'POST' && jalur === '/api/tautan-masuk') {
        const isi = await bacaJson(req);
        let hasil;
        try {
          hasil = akses.tukarUndanganMasuk(db, isi.tanda);
        } catch {
          kirim(res, 401, { galat: PESAN_UNDANGAN_GAGAL });
          return;
        }
        kirimSesi(res, 200, hasil, hasil.pengguna.id);
        return;
      }

      if (cara === 'POST' && jalur === '/api/keluar') {
        sesiKita.hapus(tandaDariKuki(req.headers.cookie));
        kirim(res, 200, { keluar: true });
        return;
      }
      // Halaman undangan tamu: sengaja TANPA sesi. Tamu yang datang sekali tidak punya akun (spec §6).
      // akses.undangan() yang menjaga isinya tetap seperlunya.
      const undanganKode = /^\/api\/undangan\/([A-Za-z0-9]{1,32})$/.exec(jalur);
      if (cara === 'GET' && undanganKode) {
        kirim(res, 200, akses.undangan(db, undanganKode[1]));
        return;
      }

      // ── Butuh sesi. Semuanya lewat akses.mjs, yang memeriksa peran sendiri. ──
      if (cara === 'GET' && jalur === '/api/saya') {
        kirim(res, 200, { pengguna: akses.sayaSiapa(db, sesi), grup: akses.grupSaya(db, sesi) });
        return;
      }
      if (cara === 'GET' && jalur === '/api/gerbang') {
        kirim(res, 200, akses.gerbangSaya(db, sesi));
        return;
      }
      if (cara === 'POST' && jalur === '/api/gerbang') {
        kirim(res, 201, akses.buatGerbang(db, sesi, await bacaJson(req)));
        return;
      }
      if (cara === 'POST' && jalur === '/api/grup') {
        kirim(res, 201, akses.buatGrup(db, sesi, await bacaJson(req)));
        return;
      }
      if (cara === 'POST' && jalur === '/api/grup/ikut') {
        kirim(res, 200, akses.ikutGrup(db, sesi, (await bacaJson(req)).kode));
        return;
      }

      const gerbangAktif = /^\/api\/gerbang\/(\d+)\/aktifkan$/.exec(jalur);
      if (cara === 'POST' && gerbangAktif) {
        kirim(res, 200, akses.aktifkanGerbang(db, sesi, Number(gerbangAktif[1])));
        return;
      }
      const gerbangSatu = /^\/api\/gerbang\/(\d+)$/.exec(jalur);
      if (cara === 'GET' && gerbangSatu) {
        kirim(res, 200, akses.lihatGerbang(db, sesi, Number(gerbangSatu[1])));
        return;
      }
      // ── Gerbang: daftar izin, bacaan, catatan, dan buka manual ──
      // ⛔ Tidak ada jalur untuk menutup gerbang, dan tidak ada jalur yang menggerakkan perangkat apa pun
      // (CLAUDE.md §3). Yang keluar dari sini hanya putusan untuk ditampilkan dan dicatat.
      // ── Notifikasi: berlangganan dan berhenti (K72) ──
      if (cara === 'GET' && jalur === '/api/notifikasi/kunci') {
        // Kunci UMUM saja; peramban membutuhkannya untuk berlangganan.
        kirim(res, 200, { kunci: vapid.umum });
        return;
      }
      const langganGrup = /^\/api\/grup\/(\d+)\/langganan$/.exec(jalur);
      if (cara === 'POST' && langganGrup) {
        const isi = await bacaJson(req);
        const baris = akses.berlangganan(db, sesi, Number(langganGrup[1]), isi);
        kirim(res, 201, { berlangganan: true, id: baris.id });
        return;
      }
      if (cara === 'DELETE' && jalur === '/api/langganan') {
        akses.berhentiLangganan(db, sesi, (await bacaJson(req)).alamat);
        kirim(res, 200, { berhenti: true });
        return;
      }

      // ── Dashboard (T7). Tanggal dikirim pemanggil, karena jam setempatnya ada di perangkat, bukan di server. ──
      const gerbangBeranda = /^\/api\/gerbang\/(\d+)\/beranda(?:\?tanggal=([\d-]{10}))?$/.exec(jalur);
      if (cara === 'GET' && gerbangBeranda) {
        const gerbangId = Number(gerbangBeranda[1]);
        const tanggal = gerbangBeranda[2] ?? new Date().toISOString().slice(0, 10);
        kirim(res, 200, {
          tanggal,
          ubin: akses.ubinBeranda(db, sesi, gerbangId, tanggal),
          jam: akses.ringkasanJam(db, sesi, gerbangId, tanggal),
        });
        return;
      }

      const gerbangIzin = /^\/api\/gerbang\/(\d+)\/izin$/.exec(jalur);
      if (cara === 'GET' && gerbangIzin) {
        kirim(res, 200, akses.daftarIzin(db, sesi, Number(gerbangIzin[1])));
        return;
      }
      const gerbangKejadian = /^\/api\/gerbang\/(\d+)\/kejadian$/.exec(jalur);
      if (cara === 'GET' && gerbangKejadian) {
        kirim(res, 200, akses.kejadianTerbaru(db, sesi, Number(gerbangKejadian[1])));
        return;
      }
      const gerbangBacaan = /^\/api\/gerbang\/(\d+)\/bacaan$/.exec(jalur);
      if (cara === 'POST' && gerbangBacaan) {
        const isi = await bacaJson(req);
        const hasil = akses.bacaanGerbang(db, sesi, { ...isi, gerbangId: Number(gerbangBacaan[1]) });

        // Notifikasi dikirim SESUDAH jawaban disiapkan dan TIDAK ditunggu: kotak gerbang harus menerima
        // putusannya cepat, dan layanan dorong yang lambat tidak boleh menahan palang.
        if (hasil.notifikasi?.penerima?.length) void doronglah(db, hasil.notifikasi);

        // Daftar penerima memuat alamat perangkat orang; ia tidak perlu ikut keluar ke kotak gerbang.
        const { notifikasi, ...tanpaPenerima } = hasil;
        kirim(res, 200, {
          ...tanpaPenerima,
          notifikasi: notifikasi ? { judul: notifikasi.judul, pesan: notifikasi.pesan, sebab: notifikasi.sebab } : null,
        });
        return;
      }
      // Gambar dari kamera: dititipkan ke mesin baca, hasilnya dipakai sebagai bacaan gerbang (T6).
      const gerbangKamera = /^\/api\/gerbang\/(\d+)\/kamera$/.exec(jalur);
      if (cara === 'POST' && gerbangKamera) {
        const gerbangId = Number(gerbangKamera[1]);
        const isi = await bacaJson(req);
        // Hak akses diperiksa LEBIH DULU, sebelum gambarnya ditulis ke folder bersama: gambar kendaraan
        // tidak boleh masuk ke antrean hanya karena seseorang memanggil jalur ini.
        akses.pastikanBolehBaca(db, sesi, gerbangId);

        const gambar = Buffer.from(String(isi.gambar ?? '').replace(/^data:[^,]*,/, ''), 'base64');
        if (gambar.length === 0) throw new GalatPermintaan('gambar kosong');
        if (gambar.length > 8 * 1024 * 1024) throw new GalatPermintaan('gambar terlalu besar (maksimal 8 MB)');

        const id = jembatan.kirim(gambar, { gerbangId, arah: isi.arah ?? 'masuk' });
        const dibaca = await jembatan.tungguHasil(id);

        const hasil = akses.bacaanGerbang(db, sesi, {
          gerbangId,
          bacaan: dibaca.plat,
          ragu: dibaca.ragu ?? [],
          arah: isi.arah ?? 'masuk',
          yakin: dibaca.yakin,
          ciriJenis: dibaca.jenis,
          penanda: isi.penanda,
        });
        if (hasil.notifikasi?.penerima?.length) void doronglah(db, hasil.notifikasi);
        const { notifikasi, ...tanpaPenerima } = hasil;
        kirim(res, 200, {
          ...tanpaPenerima,
          dibaca: { jenis: dibaca.jenis, yakin: dibaca.yakin, kendaraan: dibaca.kendaraan, ms: dibaca.ms,
                    polaSah: dibaca.pola_sah },
          notifikasi: notifikasi ? { judul: notifikasi.judul, pesan: notifikasi.pesan, sebab: notifikasi.sebab } : null,
        });
        return;
      }

      const gerbangBuka = /^\/api\/gerbang\/(\d+)\/buka$/.exec(jalur);
      if (cara === 'POST' && gerbangBuka) {
        const isi = await bacaJson(req);
        kirim(res, 200, akses.bukaManual(db, sesi, { ...isi, gerbangId: Number(gerbangBuka[1]) }));
        return;
      }

      const gerbangKendaraan = /^\/api\/gerbang\/(\d+)\/kendaraan$/.exec(jalur);
      if (cara === 'GET' && gerbangKendaraan) {
        kirim(res, 200, akses.kendaraanGerbang(db, sesi, Number(gerbangKendaraan[1])));
        return;
      }
      const gerbangTamu = /^\/api\/gerbang\/(\d+)\/tamu$/.exec(jalur);
      if (cara === 'GET' && gerbangTamu) {
        kirim(res, 200, akses.tamuGerbang(db, sesi, Number(gerbangTamu[1])));
        return;
      }
      if (cara === 'POST' && jalur === '/api/kendaraan') {
        kirim(res, 201, akses.tambahKendaraan(db, sesi, await bacaJson(req)));
        return;
      }
      if (cara === 'POST' && jalur === '/api/tamu') {
        kirim(res, 201, akses.tambahTamu(db, sesi, await bacaJson(req)));
        return;
      }
      const kendaraanSatu = /^\/api\/kendaraan\/(\d+)$/.exec(jalur);
      if (cara === 'DELETE' && kendaraanSatu) {
        akses.hapusKendaraan(db, sesi, Number(kendaraanSatu[1]));
        kirim(res, 200, { dihapus: true });
        return;
      }
      const tamuSatu = /^\/api\/tamu\/(\d+)$/.exec(jalur);
      if (cara === 'DELETE' && tamuSatu) {
        akses.hapusTamu(db, sesi, Number(tamuSatu[1]));
        kirim(res, 200, { dihapus: true });
        return;
      }

      const grupAnggota = /^\/api\/grup\/(\d+)\/anggota$/.exec(jalur);
      if (cara === 'GET' && grupAnggota) {
        kirim(res, 200, akses.anggotaGrup(db, sesi, Number(grupAnggota[1])));
        return;
      }
      const grupAnggotaBaru = /^\/api\/grup\/(\d+)\/anggota$/.exec(jalur);
      if (cara === 'POST' && grupAnggotaBaru) {
        kirim(res, 201, akses.tambahAnggota(db, sesi, Number(grupAnggotaBaru[1]), await bacaJson(req)));
        return;
      }
      // Tautan masuk untuk satu anggota (Rencana T8). Tandanya keluar HANYA di jawaban ini, sekali.
      const grupTautan = /^\/api\/grup\/(\d+)\/anggota\/(\d+)\/tautan$/.exec(jalur);
      if (cara === 'POST' && grupTautan) {
        kirim(res, 201, akses.buatUndanganMasuk(db, sesi, Number(grupTautan[1]), Number(grupTautan[2])));
        return;
      }
      const grupAnggotaKeluar = /^\/api\/grup\/(\d+)\/anggota\/(\d+)$/.exec(jalur);
      if (cara === 'DELETE' && grupAnggotaKeluar) {
        akses.keluarkanAnggota(db, sesi, Number(grupAnggotaKeluar[1]), Number(grupAnggotaKeluar[2]));
        kirim(res, 200, { dikeluarkan: true });
        return;
      }

      const grupPeran = /^\/api\/grup\/(\d+)\/peran$/.exec(jalur);
      if (cara === 'POST' && grupPeran) {
        const isi = await bacaJson(req);
        kirim(res, 200, {
          peran: akses.tetapkanPeran(db, sesi, Number(grupPeran[1]), isi.penggunaId, isi.peran),
        });
        return;
      }

      kirim(res, 404, { galat: 'jalur tidak dikenal' });
    } catch (e) {
      const kode = kodeGalat(e);
      // Jejak galat tidak pernah dikirim ke peramban; galat tak terduga dicatat di layar server saja.
      if (kode === 500) console.error('[tgt] galat tak terduga:', e);
      kirim(res, kode, { galat: kode === 500 ? 'ada galat di server' : e.message });
    }
  });
}

/** Jalankan server dengan basis data dan jalur dari pengaturan (K70: jalur tidak dipaku di kode). */
export function jalankan() {
  const atur = pengaturan();
  fs.mkdirSync(path.dirname(atur.jalurBasis), { recursive: true });
  const db = buka(atur.jalurBasis);
  const server = buatServer({ db });

  // ⛔ Pembersih masa simpan dijadwalkan DI SINI, bukan di buatServer(). Alasannya bukan kerapian: buatServer()
  // dipakai 50-an uji, dan `pengaturan()` bawaan menunjuk ke data/tgt/foto — folder foto SUNGGUHAN. Penjadwal
  // yang ikut di sana akan menghapus foto di sana tiap kali `npm test` dijalankan.
  //
  // Sampai Rencana T10, tidak ada satu pun baris seperti ini: `bersihkan()` hanya dipanggil ujinya sendiri,
  // jadi masa simpan K71 tidak menghapus apa pun selama tujuh rencana. Ada penjaga di
  // tgt/uji/bersih-berkala.test.mjs yang membaca sumber berkas ini dan gagal bila baris ini hilang lagi.
  const jadwalBersih = jadwalkanBersih(db, { jalurFoto: atur.jalurFoto });
  // Urutannya penting: pewaktu dihentikan LEBIH DULU, baru basis datanya ditutup. Kebalikannya membuat
  // pembersih berikutnya menyentuh basis yang sudah tertutup.
  server.on('close', jadwalBersih.berhenti);
  // Berkas basis data dilepas saat server ditutup. Tanpa ini, berkasnya tetap dipegang proses ini — di Windows
  // itu berarti berkas yang tidak bisa dipindah, disalin ke NAS, atau dihapus (K70: cadangan ke NAS nanti).
  server.on('close', () => db.close());

  server.listen(atur.porta, atur.alamat, () => {
    console.error(`TGT jalan di http://${atur.alamat}:${atur.porta}`);
    console.error(`Basis data: ${atur.jalurBasis}`);
    // Keadaan ruang disk disebut sejak awal (owner 26 Okt: jangan mengganggu MES Yanmar). Yang memasang TGT
    // harus bisa melihat angkanya tanpa mencari, bukan menemukannya saat disk sudah penuh.
    console.error(`Ruang disk: ${periksaRuang(path.dirname(atur.jalurBasis)).pesan}`);
    console.error(catatanCadangan(atur));
  });
  return server;
}

if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1].replace(/\\/g, '/')}`).href) {
  jalankan();
}
