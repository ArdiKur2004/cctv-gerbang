// Halaman undangan tamu. Rencana T3.
//
// Dibuka tamu yang TIDAK punya akun, hanya dengan kodenya (spec §6). Karena itu halaman ini:
// - tidak pernah meminta masuk;
// - hanya menampilkan yang dikirim server, dan server sudah menyaring isinya (akses.undangan);
// - tidak menyimpan apa pun di peramban tamu.
import { buatQr } from './qr.js';

const wadah = document.getElementById('wadah');

const unsur = (tag, kelas, isi) => {
  const el = document.createElement(tag);
  if (kelas) el.className = kelas;
  if (isi !== undefined) el.textContent = isi;
  return el;
};

function kartuPesan(judul, rinci) {
  const kartu = unsur('div', 'kartu');
  const isi = unsur('div', 'kosong');
  isi.append(unsur('b', null, judul), document.createTextNode(rinci));
  kartu.append(isi);
  return kartu;
}

/** Gambar QR ke canvas. Zona sunyi 4 modul wajib ada, kalau tidak pemindai sulit menemukan tepinya. */
function gambarQr(teks, skala = 6, sunyi = 4) {
  const qr = buatQr(teks);
  const n = qr.ukuran;
  const sisi = (n + sunyi * 2) * skala;
  const kanvas = document.createElement('canvas');
  kanvas.id = 'qr';
  kanvas.width = sisi;
  kanvas.height = sisi;
  // Ukuran tampil dibatasi lebar layar; piksel aslinya tetap tajam karena image-rendering: pixelated.
  kanvas.style.width = `${Math.min(sisi, 320)}px`;
  const k = kanvas.getContext('2d');
  // Hitam di atas putih, bukan warna merek: pemindai butuh beda terang yang tinggi.
  k.fillStyle = '#ffffff';
  k.fillRect(0, 0, sisi, sisi);
  k.fillStyle = '#000000';
  for (let y = 0; y < n; y += 1) {
    for (let x = 0; x < n; x += 1) {
      if (qr.modul[y][x]) k.fillRect((x + sunyi) * skala, (y + sunyi) * skala, skala, skala);
    }
  }
  kanvas.setAttribute('role', 'img');
  kanvas.setAttribute('aria-label', `Kode QR undangan ${teks}`);
  return kanvas;
}

function baris(judul, nilai) {
  const el = unsur('div', 'baris-data');
  el.append(unsur('b', null, judul), unsur('span', null, nilai));
  return el;
}

async function muat() {
  const kode = new URLSearchParams(location.search).get('kode');
  if (!kode) {
    wadah.replaceChildren(kartuPesan('Tautan tidak lengkap', 'Mintalah tautan undangan yang baru kepada pengundang Anda.'));
    return;
  }

  let u;
  try {
    const r = await fetch(`/api/undangan/${encodeURIComponent(kode)}`);
    if (!r.ok) throw new Error(r.status === 404 ? 'tidak ditemukan' : `gagal (${r.status})`);
    u = await r.json();
  } catch (galat) {
    wadah.replaceChildren(kartuPesan(
      'Undangan tidak ditemukan',
      'Kode undangan ini tidak berlaku, atau sudah dihapus pengundangnya. Mintalah tautan yang baru.',
    ));
    void galat;
    return;
  }

  const kartu = unsur('div', 'kartu');
  const kepala = unsur('div', 'kartu-kepala');
  kepala.append(unsur('h2', null, u.tamu));
  if (u.keperluan) kepala.append(unsur('span', 'sub', u.keperluan));
  kartu.append(kepala);

  const isi = unsur('div', 'kartu-isi');

  // Kode QR lebih dulu: itu yang dipakai di gerbang.
  isi.append(gambarQr(`TGT:${u.kode}`));
  const kodeTeks = unsur('div', null);
  kodeTeks.style.textAlign = 'center';
  kodeTeks.style.marginTop = '10px';
  kodeTeks.append(unsur('span', 'kode', u.kode));
  isi.append(kodeTeks);
  isi.append(unsur('p', 'catatan',
    'Tunjukkan kode ini di gerbang. Bila layar sulit dipindai, satpam bisa mengetik kodenya.'));

  const plat = unsur('div', null);
  plat.style.textAlign = 'center';
  plat.style.margin = '6px 0 10px';
  plat.append(unsur('span', 'plat', u.plat));
  isi.append(plat);

  isi.append(
    baris('Gerbang', u.gerbang ?? '—'),
    baris('Alamat', [u.alamat, u.kota].filter(Boolean).join(', ') || '—'),
  );
  if (u.patokan) isi.append(baris('Patokan', u.patokan));
  isi.append(
    baris('Jenis kendaraan', u.jenis ?? '—'),
    baris('Lama kunjungan', `${u.lama_hari} hari`),
  );
  if (u.diundang_oleh) isi.append(baris('Diundang oleh', u.diundang_oleh));

  kartu.append(isi);

  const pita = unsur('div', 'pita');
  pita.append(unsur('div', null,
    `Lama kunjungan dihitung dari jam Anda masuk, bukan dari pergantian tanggal. Lewat ${u.lama_hari} hari, `
    + 'pengundang Anda diberi tahu — gerbang tetap bisa dibuka.'));

  wadah.replaceChildren(kartu, pita);
}

muat();
