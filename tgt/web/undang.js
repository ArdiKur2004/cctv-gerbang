// Halaman masuk lewat tautan undangan. Rencana T8 Task 4, persetujuan owner 26 Okt.
//
// Dibuka penghuni dari tautan WhatsApp, biasanya sekali saja. Tidak ada email, tidak ada kode, tidak ada sandi:
// tautannya sendiri yang menggantikan semuanya.
//
// ⛔ TANDANYA DIBAWA DI BAGIAN SETELAH '#', bukan sebagai pertanyaan di alamat (?tanda=...). Bagian setelah '#'
// TIDAK dikirim peramban ke server, jadi ia tidak masuk ke catatan server, catatan proksi, atau pengirim rujukan.
// Ia hanya ikut saat kita mengirimnya sendiri dalam badan permintaan.
//
// ⛔ Tautan SEKALI PAKAI, jadi halaman ini TIDAK mengintip isinya lebih dulu untuk memperlihatkan nama grup
// sebelum ditekan: mengintip berarti ada jalur yang memeriksa tanda tanpa memakainya, dan jalur seperti itu
// bisa dipakai menebak tanda sebanyak-banyaknya tanpa jejak. Nama orang dan grupnya diperlihatkan SESUDAH
// berhasil masuk.

const wadah = document.getElementById('wadah');

const unsur = (tag, kelas, isi) => {
  const el = document.createElement(tag);
  if (kelas) el.className = kelas;
  if (isi !== undefined) el.textContent = isi;
  return el;
};

function kartu(judul, rinci) {
  const k = unsur('div', 'kartu');
  const isi = unsur('div', 'kosong');
  isi.append(unsur('b', null, judul));
  if (rinci) isi.append(document.createTextNode(rinci));
  k.append(isi);
  return { k, isi };
}

/** Tanda dari bagian setelah '#'. Dibersihkan dari awalan '#' dan dari sisa persen-penyandian. */
function tandaDariAlamat() {
  const kasar = location.hash.replace(/^#/, '');
  try {
    return decodeURIComponent(kasar);
  } catch {
    return kasar;
  }
}

function tampilkanGagal(pesan) {
  const { k } = kartu('Tautan ini tidak bisa dipakai', pesan);
  const b = unsur('a', 'tombol', 'Buka halaman masuk biasa');
  b.href = '/';
  k.querySelector('.kosong').append(document.createElement('br'), b);
  wadah.replaceChildren(k);
}

async function masuk(tanda) {
  const r = await fetch('/api/tautan-masuk', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ tanda }),
  });
  const badan = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(badan.galat ?? 'tautan masuk tidak berlaku');
  return badan;
}

function mulai() {
  const tanda = tandaDariAlamat();
  if (!tanda) {
    tampilkanGagal(
      'Alamatnya tidak memuat tanda undangan. Mungkin tautannya terpotong saat dikirim — mintalah tautan '
      + 'baru kepada pengelola grup Anda.',
    );
    return;
  }

  const { k, isi } = kartu(
    'Anda diundang masuk',
    'Tekan tombol di bawah untuk masuk. Tautan ini hanya bisa dipakai sekali, jadi sesudah masuk Anda tidak '
    + 'perlu membukanya lagi — aplikasinya akan mengingat Anda di ponsel ini.',
  );
  const tombol = unsur('button', 'tombol utama', 'Masuk sekarang');
  tombol.type = 'button';
  isi.append(document.createElement('br'), tombol);
  wadah.replaceChildren(k);

  tombol.addEventListener('click', async () => {
    tombol.disabled = true;
    tombol.textContent = 'Sedang masuk…';
    try {
      const hasil = await masuk(tanda);
      // Tanda dibuang dari alamat begitu terpakai: ia tidak perlu tinggal di riwayat peramban, dan
      // halaman yang dimuat ulang tidak boleh terlihat seperti gagal hanya karena tandanya sudah habis.
      history.replaceState(null, '', '/undang.html');

      const { k: selesai } = kartu(
        `Selamat datang, ${hasil.pengguna.nama}`,
        `Anda masuk sebagai ${hasil.peran} di ${hasil.grup.nama}. Sebentar lagi halaman utamanya terbuka.`,
      );
      wadah.replaceChildren(selesai);
      // Diberi sedikit waktu supaya kalimat di atas terbaca lebih dulu.
      setTimeout(() => { location.href = '/'; }, 1200);
    } catch (galat) {
      tampilkanGagal(
        `${galat.message} Kalau tautan ini pernah Anda buka sebelumnya, Anda mungkin sudah masuk — coba buka `
        + 'halaman utamanya dulu.',
      );
    }
  });
}

mulai();
