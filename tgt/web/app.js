// Layar TGT. Rencana T2: pendaftaran, grup, dan gerbang beralamat.
//
// Halaman ini TIDAK menyimpan hak akses. Ia menyembunyikan tombol yang tidak berguna supaya tidak membingungkan,
// tetapi yang benar-benar menolak adalah server (tgt/akses.mjs). Menyembunyikan tombol bukan pengamanan.
//
// Belum dikerjakan di Rencana T2, dan ditandai jujur di layar, bukan diisi data karangan:
// kendaraan (T3), tamu (T3), layar satpam (T4), dashboard jam (T5), sambungan mesin baca plat (T6).

import { buatLuring } from './luring.js';
import { tanggaBulat } from './tangga.js';

const $ = (id) => document.getElementById(id);

/**
 * Antrean luring untuk layar gerbang. Kejadian yang gagal terkirim disimpan di perangkat dan disusulkan saat
 * tersambung; penanda uniknya membuat kiriman ulang tidak menggandakan catatan di server.
 */
const luring = buatLuring({
  simpanan: globalThis.localStorage,
  kirim: (gerbangId, kejadian) => minta('POST', `/api/gerbang/${gerbangId}/bacaan`, kejadian),
});

// Susulkan saat peramban mengabarkan tersambung lagi, dan sesekali berkala — gerbang bisa tersambung kembali
// tanpa peristiwa "online" muncul (misalnya server yang mati lalu hidup lagi).
const susulkanDanGambar = async () => {
  if (luring.jumlahAntre() === 0) return;
  const hasil = await luring.susulkan();
  if (hasil.terkirim > 0 && keadaan.halaman === 'satpam') gambar();
};
globalThis.addEventListener?.('online', susulkanDanGambar);
setInterval(susulkanDanGambar, 15000);

// ─── Panggilan ke server ────────────────────────────────────────────────────────────────────────────

async function minta(cara, jalur, isi) {
  const r = await fetch(jalur, {
    method: cara,
    headers: isi ? { 'content-type': 'application/json' } : {},
    body: isi ? JSON.stringify(isi) : undefined,
  });
  let badan = null;
  try {
    badan = await r.json();
  } catch {
    badan = null;
  }
  if (!r.ok) {
    const e = new Error(badan?.galat ?? `gagal (${r.status})`);
    e.kode = r.status;
    throw e;
  }
  return badan;
}

// ─── Keadaan ────────────────────────────────────────────────────────────────────────────────────────

const keadaan = {
  pengguna: null,
  grup: [],
  gerbang: [],
  halaman: 'gerbang',
  // Grup yang sedang dibuka. Semua angka dan daftar selalu milik satu grup (K67).
  grupAktif: null,
  // Gerbang yang sedang dibuka di layar satpam.
  gerbangAktif: null,
};

const peranDiGrupAktif = () => keadaan.grup.find((g) => g.id === keadaan.grupAktif)?.peran;
const pengelola = () => peranDiGrupAktif() === 'pengelola';

// ─── Menulis teks dengan aman ───────────────────────────────────────────────────────────────────────

/** Nama orang, nama gerbang, dan alamat datang dari pengguna: selalu lewat sini, jangan lewat innerHTML. */
function teks(induk, isi) {
  induk.textContent = isi ?? '';
  return induk;
}

function unsur(tag, kelas, isi) {
  const el = document.createElement(tag);
  if (kelas) el.className = kelas;
  if (isi !== undefined) el.textContent = isi;
  return el;
}

function pesan(wadah, jenis, judul, rinci) {
  wadah.replaceChildren();
  if (!judul) return;
  const kotak = unsur('div', `pesan ${jenis}`);
  kotak.append(unsur('b', null, judul));
  if (rinci) kotak.append(document.createTextNode(rinci));
  wadah.append(kotak);
}

// ─── Layar masuk dan daftar ─────────────────────────────────────────────────────────────────────────

// Langkah masuk: null = minta kode, atau { email } = sedang menunggu kode untuk alamat itu.
let langkahOtp = null;

// ⛔ Diisi server saat MODE DEMO menyala: kode OTP ditampilkan di layar alih-alih dikirim ke email.
// Mode ini membuka kunci akun siapa pun yang alamat emailnya diketahui, jadi layar harus mengatakannya.
let demoMenyala = false;

function gambarLayarMasuk() {
  $('layar-masuk').hidden = false;
  $('cangkang').hidden = true;

  const menunggu = langkahOtp !== null;
  teks($('judul-masuk'), menunggu ? 'Masukkan kode' : 'Masuk atau daftar');
  teks($('tombol-masuk'), menunggu ? 'Masuk' : 'Kirim kode');

  $('bidang-email').querySelector('input').disabled = menunggu;
  $('bidang-kode').hidden = !menunggu;
  $('bidang-kode').querySelector('input').required = menunggu;
  $('bidang-nama').hidden = !menunggu;

  const tukar = $('tukar-masuk');
  tukar.replaceChildren();
  if (menunggu) {
    tukar.append(document.createTextNode(`Kode dikirim untuk ${langkahOtp.email}. `));
    const tombol = unsur('button', null, 'Ganti email');
    tombol.type = 'button';
    tombol.addEventListener('click', () => {
      langkahOtp = null;
      pesan($('pesan-masuk'), '', '');
      $('form-masuk').reset();
      gambarLayarMasuk();
    });
    tukar.append(tombol);
  } else {
    tukar.append(document.createTextNode('Akun dibuat sendiri saat pertama kali memasukkan kode.'));
  }
}

$('form-masuk').addEventListener('submit', async (e) => {
  e.preventDefault();
  const isian = new FormData(e.target);
  const tombol = $('tombol-masuk');
  tombol.disabled = true;
  try {
    if (langkahOtp === null) {
      const email = String(isian.get('email') ?? '').trim();
      const hasil = await minta('POST', '/api/otp', { email });
      langkahOtp = { email };
      demoMenyala = Boolean(hasil.demo);
      gambarLayarMasuk();
      if (demoMenyala && hasil.kode) {
        // Kodenya ditunjukkan DI SINI, bersama peringatan — bukan diam-diam diisikan ke kolomnya, supaya
        // orang yang melihat layar tahu persis apa yang sedang terjadi.
        pesan($('pesan-masuk'), 'benar', `MODE DEMO — kode Anda: ${hasil.kode}`,
          'Surel tidak dikirim ke mana pun. Mode ini hanya untuk memperagakan, dan harus dimatikan sebelum '
          + 'ada pengguna sungguhan.');
      } else {
        pesan($('pesan-masuk'), 'benar', 'Kode dikirim',
          `Periksa email ${email}. Kodenya berlaku ${Math.round((hasil.berlakuDetik ?? 300) / 60)} menit.`);
      }
    } else {
      const hasil = await minta('POST', '/api/otp/masuk', {
        email: langkahOtp.email,
        kode: String(isian.get('kode') ?? '').trim(),
        nama: String(isian.get('nama') ?? '').trim() || undefined,
      });
      keadaan.pengguna = hasil.pengguna;
      langkahOtp = null;
      e.target.reset();
      $('bidang-email').querySelector('input').disabled = false;
      pesan($('pesan-masuk'), '', '');
      await muatLalulGambar();
    }
  } catch (galat) {
    pesan($('pesan-masuk'), 'salah', 'Tidak bisa dilanjutkan', galat.message);
  } finally {
    tombol.disabled = false;
  }
});


$('tombol-keluar').addEventListener('click', async () => {
  await minta('POST', '/api/keluar');
  keadaan.pengguna = null;
  keadaan.grup = [];
  keadaan.gerbang = [];
  keadaan.grupAktif = null;
  langkahOtp = null;
  gambarLayarMasuk();
});

// ─── Cangkang ───────────────────────────────────────────────────────────────────────────────────────

const HALAMAN = [
  { id: 'gerbang', judul: 'Gerbang dan Alamat', sub: 'Satu gerbang = satu pintu, dengan alamatnya sendiri' },
  { id: 'grup', judul: 'Grup dan Anggota', sub: 'Perusahaan, perumahan, atau rumah pribadi' },
  { id: 'kendaraan', judul: 'Kendaraan', sub: 'Kendaraan terdaftar di gerbang ini' },
  { id: 'tamu', judul: 'Tamu', sub: 'Undangan beserta lama kunjungannya' },
  { id: 'satpam', judul: 'Layar Gerbang', sub: 'Untuk satpam — tetap bekerja saat internet putus' },
  { id: 'beranda', judul: 'Beranda', sub: 'Jam keluar masuk kendaraan hari ini' },
];

function gambarNav() {
  const nav = $('nav');
  nav.replaceChildren();
  for (const h of HALAMAN) {
    const b = unsur('button', 'tab', h.judul);
    b.type = 'button';
    if (h.id === keadaan.halaman) b.setAttribute('aria-current', 'page');
    b.addEventListener('click', () => {
      keadaan.halaman = h.id;
      gambar();
    });
    nav.append(b);
  }
}

function gambar() {
  const h = HALAMAN.find((x) => x.id === keadaan.halaman) ?? HALAMAN[0];
  teks($('judul-halaman'), h.judul);
  teks($('sub-halaman'), h.sub);
  $('aksi-halaman').replaceChildren();
  $('isi').replaceChildren();
  gambarNav();

  if (h.id === 'gerbang') gambarGerbang();
  else if (h.id === 'grup') gambarGrup();
  else if (h.id === 'kendaraan') gambarKendaraan();
  else if (h.id === 'tamu') gambarTamu();
  else if (h.id === 'satpam') gambarLayarGerbang();
  else if (h.id === 'beranda') gambarBeranda();
  else gambarBelum(h);
}

function gambarBelum(h) {
  const kartu = unsur('div', 'kartu');
  const isi = unsur('div', 'kartu-isi belum');
  const cip = unsur('span', 'cip tunggu');
  cip.append(unsur('span', 'titik'), document.createTextNode('Belum dikerjakan'));
  isi.append(
    cip,
    unsur('p', null, `${h.judul} belum dibangun. ${h.sub.replace('Belum dikerjakan — ', 'Dikerjakan di ')}.`),
    unsur('p', 'catatan',
      'Halaman ini sengaja dibiarkan kosong, bukan diisi contoh, supaya tidak ada yang menyangka fiturnya sudah jalan.'),
  );
  kartu.append(isi);
  $('isi').append(kartu);
}

// ─── Halaman Grup ───────────────────────────────────────────────────────────────────────────────────

function gambarGrup() {
  const isi = $('isi');

  if (keadaan.grup.length === 0) {
    isi.append(kartuBuatGrup(), kartuIkutGrup());
    return;
  }

  // Daftar grup
  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, 'Grup saya'));
  kartu.append(kepala);

  const gulir = unsur('div', 'gulir');
  const tabel = document.createElement('table');
  kepalaTabel(tabel, ['Grup', 'Jenis', 'Peran saya', 'Kode undangan', '']);
  const badan = document.createElement('tbody');

  for (const g of keadaan.grup) {
    const tr = document.createElement('tr');
    tr.append(unsur('td', null, g.nama));
    tr.append(unsur('td', null, g.jenis === 'perusahaan' ? 'Perusahaan' : 'Pribadi'));

    const tdPeran = document.createElement('td');
    const cip = unsur('span', `cip ${g.peran === 'pengelola' ? 'baik' : ''}`);
    cip.append(unsur('span', 'titik'), document.createTextNode(g.peran));
    tdPeran.append(cip);
    tr.append(tdPeran);

    const tdKode = document.createElement('td');
    if (g.kode_undangan) tdKode.append(unsur('span', 'kode', g.kode_undangan));
    else tdKode.append(unsur('span', 'ket', 'hanya pengelola'));
    tr.append(tdKode);

    const tdAksi = document.createElement('td');
    if (g.id !== keadaan.grupAktif) {
      const b = unsur('button', 'tombol kecil', 'Buka');
      b.type = 'button';
      b.addEventListener('click', () => {
        keadaan.grupAktif = g.id;
        gambar();
      });
      tdAksi.append(b);
    } else {
      tdAksi.append(unsur('span', 'ket', 'sedang dibuka'));
    }
    tr.append(tdAksi);
    badan.append(tr);
  }
  tabel.append(badan);
  gulir.append(tabel);
  kartu.append(gulir);
  isi.append(kartu);

  if (pengelola()) isi.append(kartuAnggota(), kartuTambahAnggota());
  isi.append(kartuBuatGrup(), kartuIkutGrup());
}

function kartuBuatGrup() {
  const { kartu, isi, wadahPesan } = kerangkaForm('Buat grup baru', 'Anda menjadi pengelolanya');
  const form = document.createElement('form');
  const baris = unsur('div', 'baris');
  baris.append(
    bidang('Nama grup', 'nama', { wajib: true, petunjuk: 'PT Sinar Niaga / Cluster Griya Asri' }),
    bidangPilih('Jenis', 'jenis', [['perusahaan', 'Perusahaan'], ['pribadi', 'Pribadi / perumahan']]),
  );
  const tombol = unsur('button', 'tombol utama', 'Buat grup');
  form.append(baris, tombol);
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    try {
      await minta('POST', '/api/grup', { nama: d.get('nama'), jenis: d.get('jenis') });
      form.reset();
      await muatLalulGambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Grup tidak dibuat', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

function kartuIkutGrup() {
  const { kartu, isi, wadahPesan } = kerangkaForm('Ikut grup lain', 'Pakai kode undangan dari pengelolanya');
  const form = document.createElement('form');
  form.append(
    bidang('Kode undangan', 'kode', { wajib: true, petunjuk: 'Enam huruf dan angka' }),
    unsur('button', 'tombol', 'Ikut grup'),
  );
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await minta('POST', '/api/grup/ikut', { kode: new FormData(form).get('kode') });
      form.reset();
      await muatLalulGambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Tidak bisa ikut grup', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

/**
 * Formulir tambah anggota. Email SENGAJA tidak wajib (Rencana T8): banyak warga tidak punya alamat email
 * yang mereka buka, dan sejak tautan undangan ada, email berhenti menjadi syarat masuk.
 *
 * Sebelum rencana ini, jalur `POST /api/grup/:id/anggota` sudah ada sejak T5 tetapi TIDAK ADA satu pun layar
 * yang memanggilnya — pengelola tidak pernah benar-benar bisa menambah anggota dari aplikasi. Jalur yang
 * benar tetapi tak pernah dipanggil terlihat persis seperti jalur yang bekerja.
 */
function kartuTambahAnggota() {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Tambah anggota', 'Cukup namanya; email tidak wajib',
  );
  const form = document.createElement('form');
  form.append(
    bidang('Nama', 'nama', { wajib: true, petunjuk: 'Nama yang dikenal di lingkungan ini' }),
    bidang('Email (boleh dikosongkan)', 'email', {
      petunjuk: 'Hanya perlu kalau orangnya mau masuk sendiri dengan kode lewat email',
    }),
  );
  const kirim = unsur('button', 'tombol utama', 'Tambahkan');
  kirim.type = 'submit';
  form.append(kirim);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const email = String(data.get('email') ?? '').trim();
    try {
      const orang = await minta('POST', `/api/grup/${keadaan.grupAktif}/anggota`, {
        nama: data.get('nama'),
        // Dikirim HANYA kalau diisi: string kosong akan ditolak sebagai alamat yang tidak terbaca.
        ...(email ? { email } : {}),
      });
      form.reset();
      pesan(wadahPesan, 'baik', `${orang.nama} sudah menjadi anggota`,
        'Berikutnya: tekan "Buat tautan masuk" di daftar di bawah, lalu kirim tautannya lewat WhatsApp Anda.');
      await muatLalulGambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Anggota tidak ditambahkan', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

/** Keadaan tautan per anggota: { [penggunaId]: { tanda, kedaluwarsa } }. Hanya di memori halaman ini. */
const tautanTampil = new Map();

/**
 * Satu baris tautan masuk, muncul sesudah pengelola menekan tombolnya.
 *
 * ⛔ Tandanya hanya bisa dilihat SEKALI. Server tidak menyimpannya apa adanya, jadi tidak ada cara
 * menampilkannya kembali — dan kalimat di layar menyebut itu, supaya pengelola menyalinnya sekarang.
 */
function barisTautan(a, wadahPesan) {
  const simpan = tautanTampil.get(a.id);
  const kotak = unsur('div', 'pesan baik');
  const alamat = `${location.origin}/undang.html#${simpan.tanda}`;

  kotak.append(unsur('b', null, `Tautan masuk untuk ${a.nama}`));
  const bidangTautan = document.createElement('input');
  bidangTautan.readOnly = true;
  bidangTautan.value = alamat;
  bidangTautan.style.width = '100%';
  bidangTautan.addEventListener('focus', () => bidangTautan.select());
  kotak.append(bidangTautan);

  const salin = unsur('button', 'tombol kecil', 'Salin tautan');
  salin.type = 'button';
  salin.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(alamat);
      teks(salin, 'Tersalin');
    } catch {
      // Penyalin peramban butuh izin dan tidak selalu ada. Bidangnya tetap bisa disalin dengan tangan,
      // jadi kegagalan di sini bukan jalan buntu — dan tidak boleh berpura-pura berhasil.
      bidangTautan.select();
      teks(salin, 'Tekan Ctrl+C');
    }
  });
  kotak.append(salin);

  kotak.append(unsur('span', 'bantu',
    `Kirim lewat WhatsApp Anda sendiri. Berlaku sampai ${a.kedaluwarsaTampil ?? simpan.kedaluwarsa}, `
    + 'sekali pakai, dan hanya bisa dilihat sekarang — kalau hilang, buat tautan baru.'));
  void wadahPesan;
  return kotak;
}

function kartuAnggota() {
  const { kartu, isi, wadahPesan } = kerangkaForm('Anggota grup', 'Nomor WhatsApp hanya terlihat oleh pengelola');
  const daftar = unsur('div', 'catatan', 'Memuat…');
  isi.append(daftar);

  minta('GET', `/api/grup/${keadaan.grupAktif}/anggota`).then((anggota) => {
    daftar.replaceChildren();
    const gulir = unsur('div', 'gulir');
    const tabel = document.createElement('table');
    kepalaTabel(tabel, ['Nama', 'Email', 'Peran', 'Tautan masuk', '']);
    const badan = document.createElement('tbody');

    for (const a of anggota) {
      const tr = document.createElement('tr');
      // Nomor WhatsApp dan email boleh kosong sejak Rencana T8: anggota tanpa email hanya punya nama.
      tr.append(unsur('td', null, a.nama), unsur('td', 'jam', a.email ?? a.wa ?? '—'));
      tr.append(unsur('td', null, a.peran));
      tr.append(unsur('td', null, a.tautan_masuk ?? 'belum dibuat'));

      const tdAksi = document.createElement('td');
      const buatTautan = unsur('button', 'tombol kecil', a.tautan_masuk ? 'Buat tautan baru' : 'Buat tautan masuk');
      buatTautan.type = 'button';
      buatTautan.addEventListener('click', async () => {
        buatTautan.disabled = true;
        try {
          const hasil = await minta('POST', `/api/grup/${keadaan.grupAktif}/anggota/${a.id}/tautan`);
          tautanTampil.set(a.id, hasil);
          isi.append(barisTautan({ ...a, kedaluwarsaTampil: hasil.kedaluwarsa }, wadahPesan));
        } catch (galat) {
          pesan(wadahPesan, 'salah', 'Tautan tidak dibuat', galat.message);
        } finally {
          buatTautan.disabled = false;
        }
      });
      tdAksi.append(buatTautan);

      for (const peran of ['pengelola', 'satpam', 'penghuni']) {
        if (peran === a.peran) continue;
        const b = unsur('button', 'tombol kecil', `Jadikan ${peran}`);
        b.type = 'button';
        b.addEventListener('click', async () => {
          try {
            await minta('POST', `/api/grup/${keadaan.grupAktif}/peran`, { penggunaId: a.id, peran });
            await muatLalulGambar();
          } catch (galat) {
            pesan(wadahPesan, 'salah', 'Peran tidak diubah', galat.message);
          }
        });
        tdAksi.append(b);
      }
      tr.append(tdAksi);
      badan.append(tr);
    }
    tabel.append(badan);
    gulir.append(tabel);
    daftar.replaceWith(gulir);
  }).catch((galat) => {
    teks(daftar, '');
    pesan(wadahPesan, 'salah', 'Daftar anggota tidak terbaca', galat.message);
  });

  return kartu;
}

// ─── Halaman Gerbang dan Alamat ─────────────────────────────────────────────────────────────────────

function gambarGerbang() {
  const isi = $('isi');

  if (keadaan.grup.length === 0) {
    const kartu = unsur('div', 'kartu');
    const kosong = unsur('div', 'kosong');
    kosong.append(
      unsur('b', null, 'Buat grup dulu'),
      document.createTextNode('Gerbang menempel pada grup, jadi grupnya dibuat lebih dulu.'),
    );
    const b = unsur('button', 'tombol utama', 'Ke halaman Grup');
    b.type = 'button';
    b.style.marginTop = '12px';
    b.addEventListener('click', () => {
      keadaan.halaman = 'grup';
      gambar();
    });
    kosong.append(document.createElement('br'), b);
    kartu.append(kosong);
    isi.append(kartu);
    return;
  }

  isi.append(pitaGrupAktif());

  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, 'Gerbang terdaftar'));
  kartu.append(kepala);

  const milikGrup = keadaan.gerbang.filter((g) => g.grup_id === keadaan.grupAktif);
  if (milikGrup.length === 0) {
    const kosong = unsur('div', 'kosong');
    kosong.append(
      unsur('b', null, 'Belum ada gerbang'),
      document.createTextNode(pengelola()
        ? 'Tambahkan gerbang pertama beserta alamatnya di bawah.'
        : 'Pengelola grup yang mendaftarkan gerbang.'),
    );
    kartu.append(kosong);
  } else {
    const gulir = unsur('div', 'gulir');
    const tabel = document.createElement('table');
    kepalaTabel(tabel, ['Gerbang', 'Jenis lokasi', 'Alamat', 'Status', '']);
    const badan = document.createElement('tbody');

    for (const g of milikGrup) {
      const tr = document.createElement('tr');
      const tdNama = document.createElement('td');
      tdNama.append(unsur('div', 'nama', g.nama));
      if (g.patokan) tdNama.append(unsur('div', 'ket', g.patokan));
      tr.append(tdNama, unsur('td', null, g.jenis_lokasi));

      const tdAlamat = document.createElement('td');
      tdAlamat.append(unsur('div', null, g.alamat), unsur('div', 'ket', g.kota));
      tr.append(tdAlamat);

      const tdStatus = document.createElement('td');
      const aktif = g.status === 'aktif';
      const cip = unsur('span', `cip ${aktif ? 'baik' : 'tunggu'}`);
      cip.append(unsur('span', 'titik'), document.createTextNode(aktif ? 'Aktif' : 'Belum aktif'));
      tdStatus.append(cip);
      tr.append(tdStatus);

      const tdAksi = document.createElement('td');
      if (!aktif && pengelola()) {
        const b = unsur('button', 'tombol kecil', 'Tandai aktif');
        b.type = 'button';
        b.addEventListener('click', async () => {
          try {
            await minta('POST', `/api/gerbang/${g.id}/aktifkan`);
            await muatLalulGambar();
          } catch (galat) {
            alertGagal(galat);
          }
        });
        tdAksi.append(b);
      }
      tr.append(tdAksi);
      badan.append(tr);
    }
    tabel.append(badan);
    gulir.append(tabel);
    kartu.append(gulir);
  }
  isi.append(kartu);

  // Tombol tambah hanya digambar untuk pengelola. Yang benar-benar menolak tetap server.
  if (pengelola()) isi.append(kartuTambahGerbang());
  else isi.append(pitaBukanPengelola());
}

function pitaGrupAktif() {
  const g = keadaan.grup.find((x) => x.id === keadaan.grupAktif);
  const pita = unsur('div', 'pita');
  const teksnya = unsur('div');
  teksnya.append(unsur('b', null, g ? g.nama : 'Grup'), document.createTextNode(
    ' — semua gerbang, kendaraan, dan catatan di layar ini milik grup ini saja.',
  ));
  pita.append(teksnya);
  if (keadaan.grup.length > 1) {
    const b = unsur('button', 'tombol kecil', 'Ganti grup');
    b.type = 'button';
    b.addEventListener('click', () => {
      keadaan.halaman = 'grup';
      gambar();
    });
    pita.append(b);
  }
  return pita;
}

function pitaBukanPengelola() {
  const pita = unsur('div', 'pita');
  pita.append(unsur('div', null,
    'Hanya pengelola grup yang bisa menambah gerbang atau mengaktifkannya. '
    + 'Peran Anda di grup ini: ' + (peranDiGrupAktif() ?? '—') + '.'));
  return pita;
}

function kartuTambahGerbang() {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Tambah gerbang',
    'Satu pintu = satu gerbang. Contoh: "Kantor Rungkut Gate Selatan"',
  );
  const form = document.createElement('form');
  const baris1 = unsur('div', 'baris');
  baris1.append(
    bidang('Nama gerbang', 'nama', { wajib: true, petunjuk: 'Sebut lokasi dan posisi pintunya' }),
    bidangPilih('Jenis lokasi', 'jenisLokasi', [
      ['kantor', 'Kantor'], ['perumahan', 'Perumahan / klaster'], ['gudang', 'Gudang / pabrik'],
      ['kost', 'Kost'], ['rumah', 'Rumah pribadi'], ['lain', 'Lain-lain'],
    ]),
  );
  const baris2 = unsur('div', 'baris');
  baris2.append(
    bidang('Alamat', 'alamat', { wajib: true, petunjuk: 'Nama jalan dan nomor' }),
    bidang('Kota', 'kota', { wajib: true }),
  );
  const baris3 = unsur('div', 'baris');
  baris3.append(
    bidang('Koordinat (boleh kosong)', 'koordinat', { petunjuk: '-7.3297, 112.7658' }),
    bidang('Patokan (boleh kosong)', 'patokan', { petunjuk: 'Seberang masjid, dekat pos satpam' }),
  );

  const catatan = unsur('p', 'catatan',
    'Gerbang baru berstatus "belum aktif" sampai perangkatnya dipasang. Pemasangan dikerjakan tim operasional IBE '
    + 'di luar aplikasi ini.');

  form.append(baris1, baris2, baris3, catatan, unsur('button', 'tombol utama', 'Simpan gerbang'));
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    try {
      await minta('POST', '/api/gerbang', {
        grupId: keadaan.grupAktif,
        nama: d.get('nama'),
        jenisLokasi: d.get('jenisLokasi'),
        alamat: d.get('alamat'),
        kota: d.get('kota'),
        koordinat: d.get('koordinat'),
        patokan: d.get('patokan'),
      });
      form.reset();
      await muatLalulGambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Gerbang tidak disimpan', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

// ─── Potongan layar yang dipakai berulang ───────────────────────────────────────────────────────────

function kerangkaForm(judul, sub) {
  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, judul));
  if (sub) kepala.append(unsur('span', 'sub', sub));
  const isi = unsur('div', 'kartu-isi');
  const wadahPesan = unsur('div');
  isi.append(wadahPesan);
  kartu.append(kepala, isi);
  return { kartu, isi, wadahPesan };
}

function bidang(judul, nama, { wajib = false, petunjuk } = {}) {
  const label = unsur('label', 'bidang', judul);
  const input = document.createElement('input');
  input.name = nama;
  if (wajib) input.required = true;
  label.append(input);
  if (petunjuk) label.append(unsur('span', 'bantu', petunjuk));
  return label;
}

function bidangPilih(judul, nama, pilihan) {
  const label = unsur('label', 'bidang', judul);
  const pilih = document.createElement('select');
  pilih.name = nama;
  for (const [nilai, tampil] of pilihan) {
    const o = document.createElement('option');
    o.value = nilai;
    o.textContent = tampil;
    pilih.append(o);
  }
  label.append(pilih);
  return label;
}

/**
 * Kepala tabel. Ditulis sebagai pembantu karena rantai `tabel.append(thead).append(baris)` TIDAK bekerja:
 * Node.append() mengembalikan undefined, jadi rantai itu melempar TypeError dan seluruh halaman gagal
 * digambar. Ditemukan 26 Okt saat halaman dibuka di peramban sungguhan; semua uji server hijau saat itu.
 */
function kepalaTabel(tabel, judul) {
  const thead = document.createElement('thead');
  const tr = document.createElement('tr');
  for (const j of judul) tr.append(unsur('th', null, j));
  thead.append(tr);
  tabel.append(thead);
}

function alertGagal(galat) {
  const bilah = $('aksi-halaman');
  bilah.replaceChildren(unsur('span', 'cip lewat', galat.message));
}

// ─── Muat ulang dan jalankan ────────────────────────────────────────────────────────────────────────

async function muatLalulGambar() {
  const [saya, gerbang] = await Promise.all([minta('GET', '/api/saya'), minta('GET', '/api/gerbang')]);
  // Diambil dari server, bukan hanya dari jawaban saat masuk: sesi bisa masih hidup dari kunjungan sebelumnya,
  // dan tanpa baris ini nama pengguna hilang dari rel kiri sesudah halaman dimuat ulang.
  keadaan.pengguna = saya.pengguna;
  keadaan.grup = saya.grup;
  keadaan.gerbang = gerbang;
  if (!keadaan.grup.some((g) => g.id === keadaan.grupAktif)) {
    keadaan.grupAktif = keadaan.grup[0]?.id ?? null;
  }
  $('layar-masuk').hidden = true;
  $('cangkang').hidden = false;
  teks($('nama-saya'), keadaan.pengguna?.nama ?? '');
  gambar();
}

// ─── Halaman Kendaraan ──────────────────────────────────────────────────────────────────────────────

/**
 * Jenis kendaraan versi 1 (K65). "Motor" sengaja ADA tetapi dimatikan, bukan dihilangkan: calon pembeli
 * harus melihat batas versi 1 dengan jujur, bukan menduga-duga kenapa motornya tidak ada.
 */
const JENIS_VERSI_1 = [
  ['mobil', 'Mobil'], ['pikap', 'Pikap'], ['truk', 'Truk'], ['bus', 'Bus'],
];

function pilihJenis(nama = 'jenis') {
  const label = unsur('label', 'bidang', 'Jenis kendaraan');
  const pilih = document.createElement('select');
  pilih.name = nama;
  for (const [nilai, tampil] of JENIS_VERSI_1) {
    const o = document.createElement('option');
    o.value = nilai;
    o.textContent = tampil;
    pilih.append(o);
  }
  const motor = document.createElement('option');
  motor.value = 'motor';
  motor.textContent = 'Motor — menyusul di versi 2';
  motor.disabled = true;
  pilih.append(motor);
  label.append(pilih, unsur('span', 'bantu', 'Versi 1 hanya roda 4 ke atas.'));
  return label;
}

/** Plat digambar seperti plat sungguhan: itu yang paling cepat dikenali satpam. */
function cipPlat(plat) {
  const el = unsur('span', 'plat', plat);
  return el;
}

function butuhGerbang(isi) {
  const gerbangGrup = keadaan.gerbang.filter((g) => g.grup_id === keadaan.grupAktif);
  if (gerbangGrup.length > 0) return gerbangGrup;

  const kartu = unsur('div', 'kartu');
  const kosong = unsur('div', 'kosong');
  kosong.append(
    unsur('b', null, 'Belum ada gerbang'),
    document.createTextNode('Kendaraan dan tamu menempel pada gerbang, jadi gerbangnya dibuat lebih dulu.'),
  );
  const b = unsur('button', 'tombol utama', 'Ke halaman Gerbang');
  b.type = 'button';
  b.style.marginTop = '12px';
  b.addEventListener('click', () => {
    keadaan.halaman = 'gerbang';
    gambar();
  });
  kosong.append(document.createElement('br'), b);
  kartu.append(kosong);
  isi.append(kartu);
  return null;
}

function pilihGerbang(daftarGerbang, nama = 'gerbangId') {
  const label = unsur('label', 'bidang', 'Gerbang');
  const pilih = document.createElement('select');
  pilih.name = nama;
  for (const g of daftarGerbang) {
    const o = document.createElement('option');
    o.value = String(g.id);
    o.textContent = g.nama;
    pilih.append(o);
  }
  label.append(pilih);
  return label;
}

function gambarKendaraan() {
  const isi = $('isi');
  if (keadaan.grup.length === 0) return gambarPerluGrup(isi);
  const daftarGerbang = butuhGerbang(isi);
  if (!daftarGerbang) return undefined;

  isi.append(pitaGrupAktif());

  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, 'Kendaraan terdaftar'));
  if (peranDiGrupAktif() === 'penghuni') {
    kepala.append(unsur('span', 'sub', 'Anda hanya melihat kendaraan milik Anda'));
  }
  kartu.append(kepala);

  const wadahPesan = unsur('div');
  kartu.append(wadahPesan);

  const isiKartu = unsur('div', 'catatan');
  isiKartu.style.padding = '16px';
  teks(isiKartu, 'Memuat…');
  kartu.append(isiKartu);
  isi.append(kartu);

  const boleh = ['pengelola', 'penghuni'].includes(peranDiGrupAktif());
  if (boleh) isi.append(kartuTambahKendaraan(daftarGerbang));
  else isi.append(pitaHanyaBaca('menambah atau menghapus kendaraan'));

  Promise.all(daftarGerbang.map((g) => minta('GET', `/api/gerbang/${g.id}/kendaraan`)))
    .then((perGerbang) => {
      const semua = perGerbang.flat();
      isiKartu.replaceChildren();
      isiKartu.style.padding = '0';
      if (semua.length === 0) {
        const kosong = unsur('div', 'kosong');
        kosong.append(
          unsur('b', null, 'Belum ada kendaraan'),
          document.createTextNode(boleh ? 'Tambahkan kendaraan pertama di bawah.' : 'Penghuni yang mendaftarkan kendaraannya.'),
        );
        isiKartu.append(kosong);
        return;
      }
      const gulir = unsur('div', 'gulir');
      const tabel = document.createElement('table');
      kepalaTabel(tabel, ['Plat', 'Jenis', 'Merek & warna', 'Atas nama', 'Unit', '']);
      const badan = document.createElement('tbody');
      for (const k of semua) {
        const tr = document.createElement('tr');
        const tdPlat = document.createElement('td');
        tdPlat.append(cipPlat(k.plat));
        tr.append(tdPlat, unsur('td', null, k.jenis));
        tr.append(unsur('td', null, [k.merek, k.warna].filter(Boolean).join(' · ') || '—'));
        tr.append(unsur('td', null, k.atas_nama), unsur('td', null, k.unit ?? '—'));

        const tdAksi = document.createElement('td');
        if (boleh) {
          const b = unsur('button', 'tombol kecil', 'Hapus');
          b.type = 'button';
          b.addEventListener('click', async () => {
            try {
              await minta('DELETE', `/api/kendaraan/${k.id}`);
              gambar();
            } catch (galat) {
              pesan(wadahPesan, 'salah', 'Tidak bisa dihapus', galat.message);
            }
          });
          tdAksi.append(b);
        }
        tr.append(tdAksi);
        badan.append(tr);
      }
      tabel.append(badan);
      gulir.append(tabel);
      isiKartu.append(gulir);
    })
    .catch((galat) => {
      teks(isiKartu, '');
      pesan(wadahPesan, 'salah', 'Daftar kendaraan tidak terbaca', galat.message);
    });
  return undefined;
}

function kartuTambahKendaraan(daftarGerbang) {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Tambah kendaraan',
    peranDiGrupAktif() === 'penghuni' ? 'Didaftarkan atas nama Anda' : 'Sebagai pengelola, boleh atas nama siapa pun',
  );
  const form = document.createElement('form');
  const baris1 = unsur('div', 'baris');
  baris1.append(pilihGerbang(daftarGerbang), pilihJenis());
  const baris2 = unsur('div', 'baris');
  baris2.append(
    bidang('Plat nomor', 'plat', { wajib: true, petunjuk: 'Spasi dan tanda hubung boleh, akan dirapikan' }),
    bidang('Merek (boleh kosong)', 'merek', { petunjuk: 'Toyota, Mitsubishi, …' }),
  );
  const baris3 = unsur('div', 'baris');
  baris3.append(
    bidang('Warna (boleh kosong)', 'warna'),
    bidang('Blok atau divisi (boleh kosong)', 'unit'),
  );
  if (peranDiGrupAktif() === 'pengelola') {
    baris3.replaceChildren(
      bidang('Warna (boleh kosong)', 'warna'),
      bidang('Atas nama', 'atasNama', { petunjuk: 'Kosongkan untuk atas nama Anda' }),
    );
  }

  form.append(baris1, baris2, baris3, unsur('button', 'tombol utama', 'Simpan kendaraan'));
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    try {
      await minta('POST', '/api/kendaraan', {
        gerbangId: Number(d.get('gerbangId')),
        jenis: d.get('jenis'),
        plat: d.get('plat'),
        merek: d.get('merek'),
        warna: d.get('warna'),
        unit: d.get('unit'),
        atasNama: d.get('atasNama'),
      });
      form.reset();
      gambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Kendaraan tidak disimpan', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

// ─── Halaman Tamu ───────────────────────────────────────────────────────────────────────────────────

function gambarTamu() {
  const isi = $('isi');
  if (keadaan.grup.length === 0) return gambarPerluGrup(isi);
  const daftarGerbang = butuhGerbang(isi);
  if (!daftarGerbang) return undefined;

  isi.append(pitaGrupAktif());

  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, 'Tamu'));
  if (peranDiGrupAktif() === 'penghuni') kepala.append(unsur('span', 'sub', 'Hanya tamu yang Anda undang'));
  kartu.append(kepala);
  const wadahPesan = unsur('div');
  kartu.append(wadahPesan);
  const isiKartu = unsur('div', 'catatan');
  isiKartu.style.padding = '16px';
  teks(isiKartu, 'Memuat…');
  kartu.append(isiKartu);
  isi.append(kartu);

  const boleh = ['pengelola', 'penghuni'].includes(peranDiGrupAktif());
  if (boleh) isi.append(kartuTambahTamu(daftarGerbang));
  else isi.append(pitaHanyaBaca('mengundang atau menghapus tamu'));

  Promise.all(daftarGerbang.map((g) => minta('GET', `/api/gerbang/${g.id}/tamu`)))
    .then((perGerbang) => {
      const semua = perGerbang.flat();
      isiKartu.replaceChildren();
      isiKartu.style.padding = '0';
      if (semua.length === 0) {
        const kosong = unsur('div', 'kosong');
        kosong.append(unsur('b', null, 'Belum ada tamu'), document.createTextNode(
          boleh ? 'Undang tamu pertama di bawah.' : 'Penghuni dan pengelola yang mengundang tamu.',
        ));
        isiKartu.append(kosong);
        return;
      }
      const gulir = unsur('div', 'gulir');
      const tabel = document.createElement('table');
      kepalaTabel(tabel, ['Tamu', 'Kendaraan', 'Lama', 'Undangan', '']);
      const badan = document.createElement('tbody');
      for (const t of semua) {
        const tr = document.createElement('tr');
        const tdNama = document.createElement('td');
        tdNama.append(unsur('div', 'nama', t.nama));
        if (t.keperluan) tdNama.append(unsur('div', 'ket', t.keperluan));
        if (t.diundang_oleh) tdNama.append(unsur('div', 'ket', `diundang ${t.diundang_oleh}`));
        tr.append(tdNama);

        const tdKend = document.createElement('td');
        tdKend.append(cipPlat(t.plat), unsur('div', 'ket', t.jenis));
        tr.append(tdKend);
        tr.append(unsur('td', null, `${t.lama_hari} hari`));

        const tdUndangan = document.createElement('td');
        if (t.kode_undangan) {
          tdUndangan.append(unsur('span', 'kode', t.kode_undangan));
          const salin = unsur('button', 'tombol kecil', 'Salin tautan');
          salin.type = 'button';
          salin.style.marginLeft = '8px';
          const tautan = `${location.origin}/undangan.html?kode=${t.kode_undangan}`;
          salin.addEventListener('click', async () => {
            try {
              await navigator.clipboard.writeText(tautan);
              teks(salin, 'Tersalin');
            } catch {
              // Peramban bisa menolak menyalin; tautannya ditampilkan supaya tetap bisa dipakai.
              tdUndangan.append(unsur('div', 'ket', tautan));
            }
          });
          const buka = document.createElement('a');
          buka.href = tautan;
          buka.target = '_blank';
          buka.rel = 'noopener';
          buka.className = 'tombol kecil';
          buka.textContent = 'Buka';
          buka.style.marginLeft = '6px';
          tdUndangan.append(salin, buka);
        } else {
          tdUndangan.append(unsur('span', 'ket', 'hanya pengundang dan pengelola'));
        }
        tr.append(tdUndangan);

        const tdAksi = document.createElement('td');
        if (boleh && t.kode_undangan) {
          const b = unsur('button', 'tombol kecil', 'Hapus');
          b.type = 'button';
          b.addEventListener('click', async () => {
            try {
              await minta('DELETE', `/api/tamu/${t.id}`);
              gambar();
            } catch (galat) {
              pesan(wadahPesan, 'salah', 'Tidak bisa dihapus', galat.message);
            }
          });
          tdAksi.append(b);
        }
        tr.append(tdAksi);
        badan.append(tr);
      }
      tabel.append(badan);
      gulir.append(tabel);
      isiKartu.append(gulir);
    })
    .catch((galat) => {
      teks(isiKartu, '');
      pesan(wadahPesan, 'salah', 'Daftar tamu tidak terbaca', galat.message);
    });
  return undefined;
}

function kartuTambahTamu(daftarGerbang) {
  const { kartu, isi, wadahPesan } = kerangkaForm('Tambah tamu', 'Tamu menerima tautan berisi QR');
  const form = document.createElement('form');
  const baris1 = unsur('div', 'baris');
  baris1.append(pilihGerbang(daftarGerbang), bidang('Nama tamu', 'nama', { wajib: true }));
  const baris2 = unsur('div', 'baris');
  baris2.append(
    bidang('Keperluan (boleh kosong)', 'keperluan', { petunjuk: 'Rapat, kirim barang, …' }),
    pilihJenis(),
  );
  const baris3 = unsur('div', 'baris');
  baris3.append(
    bidang('Plat nomor', 'plat', { wajib: true }),
    bidang('Lama kunjungan (hari)', 'lamaHari', { wajib: true, petunjuk: 'Dihitung dari jam masuk, bukan tanggal' }),
  );
  const lama = baris3.querySelector('[name=lamaHari]');
  lama.type = 'number';
  lama.min = '1';
  lama.value = '1';

  form.append(baris1, baris2, baris3, unsur('button', 'tombol utama', 'Simpan tamu'));
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    try {
      await minta('POST', '/api/tamu', {
        gerbangId: Number(d.get('gerbangId')),
        nama: d.get('nama'),
        keperluan: d.get('keperluan'),
        jenis: d.get('jenis'),
        plat: d.get('plat'),
        lamaHari: Number(d.get('lamaHari')),
      });
      form.reset();
      lama.value = '1';
      gambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Tamu tidak disimpan', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

// ─── Beranda: jam keluar masuk (Rencana T7) ─────────────────────────────────────────────────────────

const NS_SVG = 'http://www.w3.org/2000/svg';
const buatSvg = (tag, sifat) => {
  const el = document.createElementNS(NS_SVG, tag);
  for (const k of Object.keys(sifat)) el.setAttribute(k, sifat[k]);
  return el;
};

function gambarBeranda() {
  const isi = $('isi');
  if (keadaan.grup.length === 0) return gambarPerluGrup(isi);
  if (!['pengelola', 'satpam'].includes(peranDiGrupAktif())) {
    isi.append(pitaHanyaBaca('membuka beranda'));
    return undefined;
  }
  const daftarGerbang = butuhGerbang(isi);
  if (!daftarGerbang) return undefined;
  if (!keadaan.gerbangAktif || !daftarGerbang.some((g) => g.id === keadaan.gerbangAktif)) {
    keadaan.gerbangAktif = daftarGerbang[0].id;
  }
  const gerbangIni = daftarGerbang.find((g) => g.id === keadaan.gerbangAktif);

  const pita = unsur('div', 'pita');
  const kiri = unsur('div');
  kiri.append(unsur('b', null, gerbangIni.nama), document.createTextNode(` — ${gerbangIni.alamat}`));
  pita.append(kiri);
  if (daftarGerbang.length > 1) {
    const pilih = document.createElement('select');
    for (const g of daftarGerbang) {
      const o = document.createElement('option');
      o.value = String(g.id);
      o.textContent = g.nama;
      if (g.id === keadaan.gerbangAktif) o.selected = true;
      pilih.append(o);
    }
    pilih.addEventListener('change', () => {
      keadaan.gerbangAktif = Number(pilih.value);
      gambar();
    });
    pita.append(pilih);
  }
  isi.append(pita);

  const wadah = unsur('div');
  teks(wadah, 'Memuat…');
  isi.append(wadah);

  // Tanggal diambil dari jam PERANGKAT, bukan server: jam sibuk sebuah gerbang adalah jam setempatnya.
  const t = new Date();
  const dua = (x) => String(x).padStart(2, '0');
  const tanggal = `${t.getFullYear()}-${dua(t.getMonth() + 1)}-${dua(t.getDate())}`;

  minta('GET', `/api/gerbang/${gerbangIni.id}/beranda?tanggal=${tanggal}`)
    .then(({ ubin, jam }) => {
      wadah.replaceChildren(ubinBeranda(ubin), grafikJam(jam));
    })
    .catch((galat) => {
      wadah.replaceChildren();
      const kotak = unsur('div', 'pesan salah');
      kotak.append(unsur('b', null, 'Angka belum bisa diambil'), document.createTextNode(galat.message));
      wadah.append(kotak);
    });
  return undefined;
}

function ubinBeranda(u) {
  const kotak = unsur('div', 'ubin');
  const butir = [
    ['Di dalam sekarang', u.diDalam, 'kendaraan yang tercatat masuk dan belum keluar'],
    ['Masuk hari ini', u.masukHariIni, ''],
    ['Keluar hari ini', u.keluarHariIni, ''],
    ['Tamu lewat batas', u.lewatBatas, 'gerbang tetap dibuka; pengundangnya diberi tahu'],
  ];
  for (const [label, angka, kaki] of butir) {
    const sel = unsur('div');
    sel.append(unsur('div', 'garis-atas'), unsur('div', 'label', label), unsur('div', 'angka', String(angka)));
    if (kaki) sel.append(unsur('div', 'kaki', kaki));
    kotak.append(sel);
  }
  return kotak;
}

/**
 * Grafik batang per jam, dua deret: masuk dan keluar.
 *
 * Bentuk dan warnanya disalin dari konsep UI yang disetujui owner (K68); pasangan warnanya sudah diperiksa
 * agar tetap terbedakan oleh mata yang sulit membedakan warna, di tema terang maupun gelap. Angkanya SELALU
 * bisa dibuka sebagai tabel di bawahnya, supaya grafik tidak pernah menjadi satu-satunya cara membacanya.
 */
function grafikJam(jam) {
  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  const total = jam.reduce((n, b) => n + b.masuk + b.keluar, 0);
  const judul = unsur('div');
  judul.append(unsur('h2', null, 'Keluar masuk per jam'),
    unsur('div', 'sub', total === 0 ? 'Hari ini belum ada kendaraan yang tercatat' : `Hari ini · ${total} kendaraan`));
  kepala.append(judul);
  kartu.append(kepala);

  const panggung = unsur('div');
  panggung.style.padding = '16px 16px 4px';

  const L = 760;
  const T = 220;
  const kiri = 44;
  const kanan = 8;
  const atas = 22;
  const bawah = 26;
  // Yang dihitung adalah KENDARAAN, jadi tangga sumbunya wajib bilangan bulat: "3,75 kendaraan" tidak ada,
  // dan angka pecahan di sumbu membuat orang berhenti mempercayai grafiknya. Tangganya dipilih dari 1, 2, 5,
  // 10, 20, … supaya tetap mudah dibaca berapa pun ramainya gerbang.
  const tertinggi = Math.max(1, ...jam.map((b) => Math.max(b.masuk, b.keluar)));
  const langkah = tanggaBulat(tertinggi / 4);
  const maks = langkah * 4;
  const lebarJam = (L - kiri - kanan) / jam.length;
  const lebarBatang = Math.min(11, (lebarJam - 6) / 2);

  const svg = buatSvg('svg', {
    viewBox: `0 0 ${L} ${T}`, width: '100%', role: 'img',
    'aria-label': `Grafik batang jumlah kendaraan masuk dan keluar tiap jam. Seluruhnya ${total} kendaraan.`,
  });
  svg.style.display = 'block';

  for (let v = 0; v <= maks; v += langkah) {
    const y = T - bawah - (v / maks) * (T - atas - bawah);
    svg.append(buatSvg('line', { x1: kiri, x2: L - kanan, y1: y, y2: y, stroke: 'var(--garis)', 'stroke-width': 1 }));
    const label = buatSvg('text', {
      x: kiri - 8, y: y + 4, 'text-anchor': 'end', fill: 'var(--tinta-redup)', 'font-size': 11,
      'font-family': 'IBM Plex Mono, monospace',
    });
    label.textContent = String(v);
    svg.append(label);
  }

  for (const [i, b] of jam.entries()) {
    const x0 = kiri + i * lebarJam;
    // Jam ditulis tiap dua jam supaya tidak saling menimpa di layar ponsel.
    if (i % 2 === 0) {
      const label = buatSvg('text', {
        x: x0 + lebarJam / 2, y: T - 8, 'text-anchor': 'middle', fill: 'var(--tinta-redup)', 'font-size': 11,
        'font-family': 'IBM Plex Mono, monospace',
      });
      label.textContent = String(b.jam).padStart(2, '0');
      svg.append(label);
    }
    for (const [nilai, warna, geser] of [[b.masuk, 'var(--seri-masuk)', 0], [b.keluar, 'var(--seri-keluar)', lebarBatang + 2]]) {
      if (nilai === 0) continue;
      const tinggi = Math.max(2, (nilai / maks) * (T - atas - bawah));
      svg.append(buatSvg('rect', {
        x: x0 + (lebarJam - (lebarBatang * 2 + 2)) / 2 + geser, y: T - bawah - tinggi,
        width: lebarBatang, height: tinggi, rx: 4, fill: warna,
      }));
    }
    const kena = buatSvg('rect', { x: x0, y: atas, width: lebarJam, height: T - atas - bawah, fill: 'transparent' });
    kena.style.cursor = 'crosshair';
    kena.addEventListener('pointerenter', (e) => tampilPetunjuk(e, b));
    kena.addEventListener('pointermove', (e) => tampilPetunjuk(e, b));
    kena.addEventListener('pointerleave', sembunyiPetunjuk);
    svg.append(kena);
  }
  svg.append(buatSvg('line', {
    x1: kiri, x2: L - kanan, y1: T - bawah, y2: T - bawah, stroke: 'var(--tinta-redup)', 'stroke-width': 1,
  }));
  panggung.append(svg);
  kartu.append(panggung);

  const kaki = unsur('div', 'grafik-kaki');
  for (const [nama, warna] of [['Masuk', 'var(--seri-masuk)'], ['Keluar', 'var(--seri-keluar)']]) {
    const l = unsur('span', 'legenda');
    const i = document.createElement('i');
    i.style.background = warna;
    l.append(i, document.createTextNode(nama));
    kaki.append(l);
  }

  const gulir = unsur('div', 'gulir');
  gulir.hidden = true;
  const tabel = document.createElement('table');
  kepalaTabel(tabel, ['Jam', ...jam.map((b) => String(b.jam).padStart(2, '0'))]);
  const badan = document.createElement('tbody');
  for (const [nama, kunci] of [['Masuk', 'masuk'], ['Keluar', 'keluar']]) {
    const tr = document.createElement('tr');
    tr.append(unsur('td', null, nama));
    for (const b of jam) tr.append(unsur('td', 'jam', String(b[kunci])));
    badan.append(tr);
  }
  tabel.append(badan);
  gulir.append(tabel);

  const tombol = unsur('button', 'tombol kecil', 'Lihat angka');
  tombol.type = 'button';
  tombol.addEventListener('click', () => {
    gulir.hidden = !gulir.hidden;
    teks(tombol, gulir.hidden ? 'Lihat angka' : 'Sembunyikan angka');
  });
  kaki.append(tombol);

  kartu.append(kaki, gulir);
  return kartu;
}

function petunjukKotak() {
  let el = document.getElementById('petunjuk');
  if (!el) {
    el = unsur('div');
    el.id = 'petunjuk';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    document.body.append(el);
  }
  return el;
}

function tampilPetunjuk(e, b) {
  const p = petunjukKotak();
  p.replaceChildren(unsur('div', 'jam-besar', `Pukul ${String(b.jam).padStart(2, '0')}.00`));
  for (const [nama, nilai, warna] of [['Masuk', b.masuk, 'var(--seri-masuk)'], ['Keluar', b.keluar, 'var(--seri-keluar)']]) {
    const baris = unsur('div', 'b');
    const i = document.createElement('i');
    i.style.cssText = `width:9px;height:9px;border-radius:2px;display:inline-block;background:${warna}`;
    baris.append(i, document.createTextNode(`${nama} ${nilai}`));
    p.append(baris);
  }
  p.style.opacity = '1';
  const r = p.getBoundingClientRect();
  p.style.left = `${Math.min(e.clientX + 14, window.innerWidth - r.width - 10)}px`;
  p.style.top = `${Math.max(10, e.clientY - r.height - 12)}px`;
}

function sembunyiPetunjuk() {
  petunjukKotak().style.opacity = '0';
}

// ─── Layar Gerbang (satpam) ─────────────────────────────────────────────────────────────────────────

/**
 * Putusan ditampilkan dengan KATA dan bentuk, bukan warna saja: layar gerbang dipakai malam hari, oleh orang
 * yang berganti sif, dan sebagian orang sulit membedakan warna.
 */
const RUPA_PUTUSAN = {
  buka: { kelas: 'baik', kata: 'BUKA' },
  panggil_satpam: { kelas: 'tunggu', kata: 'PANGGIL SATPAM' },
  tidak_dikenal: { kelas: 'lewat', kata: 'TIDAK DIKENAL' },
  dibuka_satpam: { kelas: 'baik', kata: 'DIBUKA SATPAM' },
};

function cipPutusan(putusan) {
  const r = RUPA_PUTUSAN[putusan] ?? { kelas: '', kata: putusan ?? '—' };
  const cip = unsur('span', `cip ${r.kelas}`);
  cip.append(unsur('span', 'titik'), document.createTextNode(r.kata));
  return cip;
}

function gambarLayarGerbang() {
  const isi = $('isi');
  if (keadaan.grup.length === 0) return gambarPerluGrup(isi);
  if (!['pengelola', 'satpam'].includes(peranDiGrupAktif())) {
    isi.append(pitaHanyaBaca('membuka layar gerbang'));
    return undefined;
  }
  const daftarGerbang = butuhGerbang(isi);
  if (!daftarGerbang) return undefined;
  if (!keadaan.gerbangAktif || !daftarGerbang.some((g) => g.id === keadaan.gerbangAktif)) {
    keadaan.gerbangAktif = daftarGerbang[0].id;
  }
  const gerbangIni = daftarGerbang.find((g) => g.id === keadaan.gerbangAktif);

  // ── Bilah keadaan: gerbang mana, tersambung atau tidak, berapa yang belum tersusul ──
  const pita = unsur('div', 'pita');
  const kiri = unsur('div');
  kiri.append(unsur('b', null, gerbangIni.nama), document.createTextNode(` — ${gerbangIni.alamat}`));
  pita.append(kiri);
  const penandaSambung = unsur('span', `cip ${navigator.onLine ? 'baik' : 'lewat'}`);
  penandaSambung.append(
    unsur('span', 'titik'),
    document.createTextNode(navigator.onLine ? 'Tersambung' : 'LURING — catatan diantrekan'),
  );
  pita.append(penandaSambung);
  const antre = luring.jumlahAntre();
  if (antre > 0) {
    const cipAntre = unsur('span', 'cip tunggu');
    cipAntre.append(unsur('span', 'titik'), document.createTextNode(`${antre} belum tersusul`));
    pita.append(cipAntre);
  }
  if (daftarGerbang.length > 1) {
    const pilih = document.createElement('select');
    for (const g of daftarGerbang) {
      const o = document.createElement('option');
      o.value = String(g.id);
      o.textContent = g.nama;
      if (g.id === keadaan.gerbangAktif) o.selected = true;
      pilih.append(o);
    }
    pilih.addEventListener('change', () => {
      keadaan.gerbangAktif = Number(pilih.value);
      gambar();
    });
    pita.append(pilih);
  }
  isi.append(pita);

  isi.append(kartuNotifikasi());
  isi.append(kartuCariPlat(gerbangIni));
  isi.append(kartuBukaManual(gerbangIni));
  isi.append(kartuKamera(gerbangIni));
  isi.append(kartuUjiBacaan(gerbangIni));
  isi.append(kartuKejadian(gerbangIni));

  // Salin daftar izin ke perangkat, supaya layar ini tetap berguna saat internet putus.
  minta('GET', `/api/gerbang/${gerbangIni.id}/izin`)
    .then((daftar) => luring.simpanIzin(gerbangIni.id, daftar))
    .catch(() => { /* luring: yang tersimpan sebelumnya tetap dipakai */ });

  return undefined;
}

/**
 * Notifikasi ke HP (K72). Hanya yang janggal yang memberi notifikasi — kendaraan terdaftar yang lewat wajar
 * tidak, supaya satpam tidak berhenti membacanya.
 *
 * Izin notifikasi diminta saat satpam MENEKAN tombolnya, bukan saat halaman dibuka: permintaan izin yang
 * muncul tiba-tiba hampir selalu ditolak orang, dan sesudah ditolak ia sulit dikembalikan.
 */
function kartuNotifikasi() {
  const { kartu, isi, wadahPesan } = kerangkaForm('Notifikasi ke HP', 'Hanya untuk kejadian yang janggal');
  // Namanya SENGAJA bukan `keadaan`: itu nama keadaan aplikasi di berkas ini, dan menutupinya di sini
  // membuat grup yang sedang dibuka tidak terbaca. Sempat terjadi saat berkas ini ditulis.
  const penandaKeadaan = unsur('div', 'catatan');
  const tombol = unsur('button', 'tombol', 'Nyalakan notifikasi');
  tombol.type = 'button';
  // Tombol mematikan (Rencana T10). Jalur `DELETE /api/langganan` sudah ada dan diuji sejak T5, tetapi
  // TIDAK ADA satu pun layar yang memanggilnya: satpam bisa menyalakan notifikasi dan tidak bisa
  // mematikannya. Ada penjaga di tgt/uji/web.test.mjs yang menuntut tiap jalur DELETE punya pemanggil.
  const tombolMati = unsur('button', 'tombol kecil', 'Matikan notifikasi');
  tombolMati.type = 'button';
  tombolMati.hidden = true;

  /** Langganan dorong perangkat INI, bila ada. Dipakai supaya tulisan di layar sesuai kenyataan. */
  const langgananSekarang = async () => {
    try {
      const sw = await navigator.serviceWorker.getRegistration('/sw.js');
      return (await sw?.pushManager.getSubscription()) ?? null;
    } catch {
      return null;
    }
  };

  const bisa = 'serviceWorker' in navigator && 'PushManager' in window;
  if (!bisa) {
    teks(penandaKeadaan, 'Peramban ini tidak mendukung notifikasi dorong. Di gerbang, pasang TGT ke layar '
      + 'depan lewat Chrome di HP Android.');
    tombol.disabled = true;
  } else if (!window.isSecureContext) {
    // Alasan paling sering notifikasi tidak bisa dinyalakan, dan paling membingungkan bila tidak disebut.
    teks(penandaKeadaan, 'Notifikasi hanya bisa dinyalakan lewat HTTPS, atau lewat alamat localhost. '
      + 'Sekarang halaman ini dibuka tanpa keduanya.');
    tombol.disabled = true;
  } else {
    teks(penandaKeadaan, Notification.permission === 'granted'
      ? 'Izin notifikasi sudah diberikan di perangkat ini.'
      : 'Belum menyala di perangkat ini.');
    // Keadaan sebenarnya dibaca dari perangkat, bukan ditebak dari izin: izin yang sudah diberikan TIDAK
    // berarti perangkat ini masih berlangganan. Di HP OPPO uji, langganannya justru hilang sendiri beberapa
    // detik sesudah dibuat, sementara izinnya tetap "granted" — tulisan yang menebak dari izin akan berbohong.
    langgananSekarang().then((l) => {
      if (!l) return;
      teks(penandaKeadaan, 'Menyala di perangkat ini.');
      tombol.hidden = true;
      tombolMati.hidden = false;
    });
  }

  tombolMati.addEventListener('click', async () => {
    tombolMati.disabled = true;
    try {
      const l = await langgananSekarang();
      if (!l) throw new Error('perangkat ini memang tidak sedang berlangganan');
      // Server diberi tahu LEBIH DULU: itu yang menghentikan kiriman. Kalau pelepasan di perangkat yang
      // gagal, yang tertinggal hanyalah langganan yatim yang tidak dikirimi apa pun.
      await minta('DELETE', '/api/langganan', { alamat: l.endpoint });
      await l.unsubscribe();
      pesan(wadahPesan, 'benar', 'Notifikasi dimatikan', 'Perangkat ini tidak akan diberi tahu lagi.');
      teks(penandaKeadaan, 'Tidak menyala di perangkat ini.');
      tombolMati.hidden = true;
      tombol.hidden = false;
      tombol.disabled = false;
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Notifikasi belum dimatikan', galat.message);
    } finally {
      tombolMati.disabled = false;
    }
  });

  tombol.addEventListener('click', async () => {
    tombol.disabled = true;
    try {
      const izin = await Notification.requestPermission();
      if (izin !== 'granted') throw new Error('izin notifikasi tidak diberikan di perangkat ini');

      const sw = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;
      const { kunci } = await minta('GET', '/api/notifikasi/kunci');

      const langganan = await sw.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: Uint8Array.from(atob(kunci.replace(/-/g, '+').replace(/_/g, '/')), (c) => c.charCodeAt(0)),
      });
      const isiLangganan = langganan.toJSON();
      await minta('POST', `/api/grup/${keadaan.grupAktif}/langganan`, {
        alamat: isiLangganan.endpoint,
        kunci: isiLangganan.keys.p256dh,
        rahasia: isiLangganan.keys.auth,
      });
      pesan(wadahPesan, 'benar', 'Notifikasi menyala', 'Perangkat ini akan diberi tahu saat ada yang janggal.');
      teks(penandaKeadaan, 'Menyala di perangkat ini.');
      tombol.hidden = true;
      tombolMati.hidden = false;
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Notifikasi belum menyala', galat.message);
      tombol.disabled = false;
    }
  });

  isi.append(penandaKeadaan, tombol, tombolMati);
  return kartu;
}

function kartuCariPlat(gerbangIni) {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Cari plat',
    'Dipakai saat bacaan tidak terbaca mesin. Bekerja juga saat internet putus.',
  );
  const form = document.createElement('form');
  form.append(bidang('Plat nomor', 'plat', { wajib: true }), unsur('button', 'tombol', 'Cari'));
  const hasil = unsur('div');
  hasil.style.marginTop = '12px';

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const dicari = String(new FormData(form).get('plat') ?? '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    const daftar = luring.bacaIzin(gerbangIni.id);
    hasil.replaceChildren();
    if (daftar === null) {
      pesan(wadahPesan, 'salah', 'Daftar izin belum tersalin', 'Sambungkan sekali supaya bisa dipakai luring.');
      return;
    }
    pesan(wadahPesan, '', '');
    const ketemu = daftar.filter((i) => i.plat === dicari);
    if (ketemu.length === 0) {
      const kotak = unsur('div', 'pesan salah');
      kotak.append(unsur('b', null, 'Tidak terdaftar'), document.createTextNode(
        `Plat ${dicari || '(kosong)'} tidak ada di daftar izin gerbang ini. Satpam yang memutuskan.`,
      ));
      hasil.append(kotak);
      return;
    }
    for (const i of ketemu) {
      const baris = unsur('div', 'pesan benar');
      baris.append(unsur('b', null, 'Terdaftar'));
      baris.append(cipPlat(i.plat), document.createTextNode(` · ${i.jenis} · sekarang ${i.status.replace('_', ' ')}`));
      hasil.append(baris);
    }
  });
  isi.append(form, hasil);
  return kartu;
}

function kartuBukaManual(gerbangIni) {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Buka dengan tangan',
    'Hanya mencatat — belum ada perangkat yang digerakkan',
  );
  const form = document.createElement('form');
  const baris = unsur('div', 'baris');
  baris.append(
    bidang('Plat nomor', 'plat', { wajib: true }),
    bidangPilih('Arah', 'arah', [['masuk', 'Masuk'], ['keluar', 'Keluar']]),
  );
  form.append(
    baris,
    bidang('Alasan', 'alasan', { wajib: true, petunjuk: 'Wajib diisi; tercatat beserta nama Anda' }),
    unsur('p', 'catatan',
      'Tombol ini TIDAK menggerakkan palang. Sampai perangkat gerbang dipasang dan owner menyetujuinya, '
      + 'yang terjadi hanya catatan bahwa Anda membukanya.'),
    unsur('button', 'tombol utama', 'Catat buka manual'),
  );
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    try {
      await minta('POST', `/api/gerbang/${gerbangIni.id}/buka`, {
        plat: d.get('plat'), arah: d.get('arah'), alasan: d.get('alasan'),
      });
      form.reset();
      gambar();
    } catch (galat) {
      pesan(wadahPesan, 'salah', 'Tidak tercatat', galat.message);
    }
  });
  isi.append(form);
  return kartu;
}

/**
 * Kamera gerbang. Mengambil satu gambar, mengirimnya ke mesin baca lewat server, lalu menampilkan putusannya.
 *
 * Dua jalan sengaja disediakan: kamera perangkat DAN unggah berkas. Gerbang tidak boleh buntu hanya karena
 * satu izin ditolak atau satu perangkat tidak punya kamera.
 */
function kartuKamera(gerbangIni) {
  const { kartu, isi, wadahPesan } = kerangkaForm('Kamera gerbang', 'Satu gambar: plat dan jenis kendaraan');

  const panggung = unsur('div', 'kamera');
  const video = document.createElement('video');
  video.autoplay = true;
  video.playsInline = true;
  video.muted = true;
  video.style.cssText = 'width:100%;height:100%;object-fit:cover';
  panggung.append(video);

  const barisTombol = unsur('div');
  barisTombol.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center';

  const pilihArah = bidangPilih('Arah', 'arah', [['masuk', 'Masuk'], ['keluar', 'Keluar']]);
  pilihArah.style.flex = '0 0 150px';
  const tombolNyala = unsur('button', 'tombol', 'Nyalakan kamera');
  tombolNyala.type = 'button';
  const tombolAmbil = unsur('button', 'tombol utama', 'Ambil gambar');
  tombolAmbil.type = 'button';
  tombolAmbil.disabled = true;

  const unggah = document.createElement('input');
  unggah.type = 'file';
  unggah.accept = 'image/*';
  unggah.style.display = 'none';
  const tombolUnggah = unsur('button', 'tombol kecil', 'Atau pilih berkas gambar');
  tombolUnggah.type = 'button';
  tombolUnggah.addEventListener('click', () => unggah.click());

  barisTombol.append(pilihArah, tombolNyala, tombolAmbil, tombolUnggah, unggah);
  const hasil = unsur('div');
  hasil.style.marginTop = '12px';

  let aliran = null;

  const tampilkan = (r) => {
    hasil.replaceChildren();
    const kotak = unsur('div', `pesan ${r.putusan === 'buka' ? 'benar' : 'salah'}`);
    kotak.append(cipPutusan(r.putusan));
    if (r.plat) kotak.append(document.createTextNode(' '), cipPlat(r.plat));
    kotak.append(unsur('div', 'catatan', r.alasan ?? ''));
    const d = r.dibaca ?? {};
    kotak.append(unsur('div', 'catatan',
      `Jenis terbaca: ${d.jenis ?? 'tidak terbaca'}`
      + `${d.kendaraan ? ` · kendaraan terlihat: ${d.kendaraan}` : ''}`
      + `${d.ms ? ` · ${d.ms} ms` : ''}`
      + `${d.polaSah === false ? ' · bentuk plat tidak sesuai pola Indonesia' : ''}`));
    hasil.append(kotak);
    if (r.notifikasi) {
      const n = unsur('div', 'pita');
      n.append(unsur('div', null, `Satpam diberi tahu: ${r.notifikasi.judul} — ${r.notifikasi.pesan}`));
      hasil.append(n);
    }
    gambarUlangKejadian(gerbangIni);
  };

  const kirimGambar = async (dataUrl) => {
    tombolAmbil.disabled = true;
    pesan(wadahPesan, '', '');
    teks(hasil, 'Membaca…');
    try {
      const arah = pilihArah.querySelector('select').value;
      tampilkan(await minta('POST', `/api/gerbang/${gerbangIni.id}/kamera`, { gambar: dataUrl, arah }));
    } catch (galat) {
      hasil.replaceChildren();
      pesan(wadahPesan, 'salah', 'Gambar tidak terbaca', galat.message);
    } finally {
      tombolAmbil.disabled = !aliran;
    }
  };

  tombolNyala.addEventListener('click', async () => {
    tombolNyala.disabled = true;
    try {
      // facingMode "environment": kamera belakang di HP, yang menghadap gerbang.
      aliran = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      video.srcObject = aliran;
      tombolAmbil.disabled = false;
      teks(tombolNyala, 'Kamera menyala');
    } catch (galat) {
      // Sebabnya disebut, dan jalan unggah berkas tetap ada: gerbang tidak boleh buntu karena satu izin.
      pesan(wadahPesan, 'salah', 'Kamera tidak bisa dipakai',
        `${galat.message}. Anda masih bisa memilih berkas gambar di bawah.`);
      tombolNyala.disabled = false;
    }
  });

  tombolAmbil.addEventListener('click', () => {
    const kanvas = document.createElement('canvas');
    kanvas.width = video.videoWidth || 1280;
    kanvas.height = video.videoHeight || 720;
    kanvas.getContext('2d').drawImage(video, 0, 0, kanvas.width, kanvas.height);
    kirimGambar(kanvas.toDataURL('image/jpeg', 0.85));
  });

  unggah.addEventListener('change', () => {
    const berkas = unggah.files?.[0];
    if (!berkas) return;
    const pembaca = new FileReader();
    pembaca.onload = () => kirimGambar(String(pembaca.result));
    pembaca.readAsDataURL(berkas);
  });

  isi.append(panggung, barisTombol,
    unsur('p', 'catatan',
      'Jenis kendaraan hanya DICATAT dan memberi tahu satpam bila tidak cocok; ia tidak pernah menahan gerbang. '
      + 'Jenis benar pada sekitar 12 dari 14 mobil, jadi menahan berarti menahan orang yang tidak bersalah.'),
    hasil);
  return kartu;
}

function kartuUjiBacaan(gerbangIni) {
  const { kartu, isi, wadahPesan } = kerangkaForm(
    'Kirim bacaan percobaan',
    'Sementara, sampai kamera tersambung (Rencana T6)',
  );
  const form = document.createElement('form');
  const baris = unsur('div', 'baris');
  baris.append(
    bidang('Plat terbaca', 'bacaan', { wajib: true }),
    bidangPilih('Arah', 'arah', [['masuk', 'Masuk'], ['keluar', 'Keluar']]),
  );
  form.append(
    baris,
    bidang('Posisi yang diragukan', 'ragu', { petunjuk: 'Nomor posisi dipisah koma, mulai dari 0. Kosongkan bila yakin.' }),
    unsur('p', 'catatan',
      'Ini menggantikan kamera yang belum ada, supaya aturan putusan bisa dilihat bekerja. Bacaannya tercatat '
      + 'seperti bacaan sungguhan.'),
    unsur('button', 'tombol', 'Kirim bacaan'),
  );
  const hasil = unsur('div');
  hasil.style.marginTop = '12px';

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = new FormData(form);
    const ragu = String(d.get('ragu') ?? '').split(',').map((x) => x.trim()).filter(Boolean).map(Number);
    const kejadian = { bacaan: d.get('bacaan'), ragu, arah: d.get('arah') };
    hasil.replaceChildren();
    try {
      const r = await minta('POST', `/api/gerbang/${gerbangIni.id}/bacaan`, kejadian);
      const kotak = unsur('div', 'pesan benar');
      kotak.append(cipPutusan(r.putusan));
      if (r.plat) kotak.append(document.createTextNode(' '), cipPlat(r.plat));
      kotak.append(unsur('div', 'catatan', r.alasan));
      hasil.append(kotak);
      pesan(wadahPesan, '', '');
      gambarUlangKejadian(gerbangIni);
    } catch (galat) {
      // Internet putus: kejadiannya diantrekan, bukan dibuang.
      const penanda = luring.antrekan(gerbangIni.id, kejadian);
      const kotak = unsur('div', 'pesan salah');
      kotak.append(unsur('b', null, 'Tidak bisa menghubungi server'), document.createTextNode(
        `Bacaan disimpan di perangkat (penanda ${penanda.slice(0, 8)}…) dan akan disusulkan saat tersambung. `
        + `Putusan sekarang diambil dari daftar izin yang tersimpan.`,
      ));
      hasil.append(kotak);
      void galat;
      gambar();
    }
  });
  isi.append(form, hasil);
  return kartu;
}

let wadahKejadian = null;

function kartuKejadian(gerbangIni) {
  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, 'Lalu lalang terbaru'), unsur('span', 'sub', 'Ciri hanya dicatat, tidak memberi peringatan'));
  kartu.append(kepala);
  wadahKejadian = unsur('div', 'catatan');
  wadahKejadian.style.padding = '16px';
  teks(wadahKejadian, 'Memuat…');
  kartu.append(wadahKejadian);
  gambarUlangKejadian(gerbangIni);
  return kartu;
}

function gambarUlangKejadian(gerbangIni) {
  const wadah = wadahKejadian;
  if (!wadah) return;
  minta('GET', `/api/gerbang/${gerbangIni.id}/kejadian`).then((daftar) => {
    wadah.replaceChildren();
    wadah.style.padding = '0';
    if (daftar.length === 0) {
      const kosong = unsur('div', 'kosong');
      kosong.append(unsur('b', null, 'Belum ada yang lewat'), document.createTextNode(
        'Kejadian muncul di sini begitu kamera atau bacaan percobaan mengirimkannya.',
      ));
      wadah.append(kosong);
      return;
    }
    const gulir = unsur('div', 'gulir');
    const tabel = document.createElement('table');
    kepalaTabel(tabel, ['Jam', 'Arah', 'Plat', 'Putusan', 'Alasan', 'Ciri']);
    const badan = document.createElement('tbody');
    for (const k of daftar) {
      const tr = document.createElement('tr');
      tr.append(unsur('td', 'jam', (k.waktu ?? '').slice(11, 16)));
      tr.append(unsur('td', null, k.arah));
      const tdPlat = document.createElement('td');
      if (k.plat) tdPlat.append(cipPlat(k.plat));
      else tdPlat.append(unsur('span', 'ket', 'tak terbaca'));
      tr.append(tdPlat);
      const tdPutusan = document.createElement('td');
      tdPutusan.append(cipPutusan(k.putusan));
      tr.append(tdPutusan);
      tr.append(unsur('td', 'ket', k.alasan ?? '—'));
      tr.append(unsur('td', 'ket', [k.ciri_jenis, k.ciri_warna, k.ciri_merek].filter(Boolean).join(' · ') || '—'));
      badan.append(tr);
    }
    tabel.append(badan);
    gulir.append(tabel);
    wadah.append(gulir);
  }).catch(() => {
    wadah.replaceChildren();
    wadah.style.padding = '16px';
    const kotak = unsur('div', 'pesan salah');
    kotak.append(unsur('b', null, 'Luring'), document.createTextNode(
      'Catatan lalu lalang tidak bisa diambil sekarang. Pencarian plat tetap bekerja dari daftar yang tersimpan.',
    ));
    wadah.append(kotak);
  });
}

// ─── Potongan bersama ───────────────────────────────────────────────────────────────────────────────

function gambarPerluGrup(isi) {
  const kartu = unsur('div', 'kartu');
  const kosong = unsur('div', 'kosong');
  kosong.append(unsur('b', null, 'Buat grup dulu'), document.createTextNode(
    'Semua isi aplikasi menempel pada grup dan gerbangnya.',
  ));
  const b = unsur('button', 'tombol utama', 'Ke halaman Grup');
  b.type = 'button';
  b.style.marginTop = '12px';
  b.addEventListener('click', () => {
    keadaan.halaman = 'grup';
    gambar();
  });
  kosong.append(document.createElement('br'), b);
  kartu.append(kosong);
  isi.append(kartu);
  return undefined;
}

function pitaHanyaBaca(apa) {
  const pita = unsur('div', 'pita');
  pita.append(unsur('div', null,
    `Peran Anda di grup ini adalah ${peranDiGrupAktif() ?? '—'}, jadi Anda bisa melihat daftarnya tetapi tidak ${apa}.`));
  return pita;
}

// Sesi bisa masih hidup dari kunjungan sebelumnya: dicoba dulu, dan 401 berarti layar masuk.
try {
  await muatLalulGambar();
} catch (galat) {
  if (galat.kode !== 401) console.error('[tgt] gagal memuat:', galat);
  gambarLayarMasuk();
}
