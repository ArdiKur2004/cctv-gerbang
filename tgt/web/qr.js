// Pembuat QR untuk undangan tamu TGT. Rencana T3.
//
// Ditulis sendiri karena repo ini nol dependensi (CLAUDE.md §6) dan gerbang bisa tanpa jaringan, jadi
// memuat pustaka dari internet bukan pilihan.
//
// ⛔ Gambar yang TERLIHAT seperti QR tetapi tidak terbaca adalah kegagalan senyap yang paling mahal: satpam
// akan menyalahkan kameranya, bukan kodenya. Karena itu ada dua lapis pembuktian:
//   1. `bacaKembali()` di berkas ini membongkar matriksnya kembali menjadi teks (menangkap salah penempatan,
//      salah topeng, salah koreksi galat) — tetapi ia buatan kita sendiri, jadi ia TIDAK cukup;
//   2. pembaca bawaan peramban (`BarcodeDetector`), yang sama sekali bukan buatan kita.
//
// Lingkup: mode bita (8 bit), taraf koreksi M, versi 1-10. Cukup untuk tautan undangan; teks yang lebih
// panjang DITOLAK, tidak dipotong.

const TARAF_BIT = { L: 0b01, M: 0b00, Q: 0b11, H: 0b10 };

// Tabel resmi QR untuk taraf M, versi 1-10:
// [jumlah kata sandi EC per blok, blok golongan 1, kata data per blok golongan 1, blok golongan 2, kata data per blok golongan 2]
const BLOK_M = {
  1: [10, 1, 16, 0, 0],
  2: [16, 1, 28, 0, 0],
  3: [26, 1, 44, 0, 0],
  4: [18, 2, 32, 0, 0],
  5: [24, 2, 43, 0, 0],
  6: [16, 4, 27, 0, 0],
  7: [18, 4, 31, 0, 0],
  8: [22, 2, 38, 2, 39],
  9: [22, 3, 36, 2, 37],
  10: [26, 4, 43, 1, 44],
};

// Titik tengah pola penyelaras per versi (versi 1 tidak punya).
const PENYELARAS = {
  1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
  6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50],
};

const VERSI_MAKS = 10;

function tabel(versi, taraf) {
  if (taraf !== 'M') throw new Error(`taraf koreksi "${taraf}" belum didukung; yang ada: M`);
  const t = BLOK_M[versi];
  if (!t) throw new Error(`versi ${versi} di luar 1-${VERSI_MAKS}`);
  const [ec, blok1, data1, blok2, data2] = t;
  return { ec, blok1, data1, blok2, data2, totalData: blok1 * data1 + blok2 * data2 };
}

/** Berapa bita teks yang muat di satu versi. Dibaca dari tabel, tidak disalin sebagai angka tersendiri. */
export function kapasitas(versi, taraf = 'M') {
  const { totalData } = tabel(versi, taraf);
  const bitHitung = versi >= 10 ? 16 : 8;
  return totalData - Math.ceil((4 + bitHitung) / 8);
}

// ─── Lapangan GF(256) untuk Reed-Solomon ────────────────────────────────────────────────────────────

const EKS = new Uint8Array(512);
const LOG = new Uint8Array(256);
{
  let x = 1;
  for (let i = 0; i < 255; i += 1) {
    EKS[i] = x;
    LOG[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d; // polinom primitif QR
  }
  for (let i = 255; i < 512; i += 1) EKS[i] = EKS[i - 255];
}
const kali = (a, b) => (a === 0 || b === 0 ? 0 : EKS[LOG[a] + LOG[b]]);

function polinomGenerator(derajat) {
  let p = [1];
  for (let i = 0; i < derajat; i += 1) {
    const baru = new Array(p.length + 1).fill(0);
    for (let j = 0; j < p.length; j += 1) {
      baru[j] ^= kali(p[j], EKS[i]);
      baru[j + 1] ^= p[j];
    }
    p = baru;
  }
  // Perkalian di atas menyusun koefisien dari suku TERKECIL; pembagian di kataEc() menuntut dari suku
  // TERBESAR. Tanpa pembalikan ini, kata koreksi galatnya salah — dan itu TIDAK terlihat oleh bacaKembali(),
  // yang memang tidak pernah memeriksa koreksi galat. Hanya pemindai sungguhan yang menolaknya (26 Okt).
  return p.reverse();
}

function kataEc(data, jumlah) {
  const gen = polinomGenerator(jumlah);
  const sisa = new Uint8Array(jumlah);
  for (const bita of data) {
    const faktor = bita ^ sisa[0];
    sisa.copyWithin(0, 1);
    sisa[jumlah - 1] = 0;
    for (let i = 0; i < jumlah; i += 1) sisa[i] ^= kali(gen[i + 1], faktor);
  }
  return sisa;
}

// ─── Bit ────────────────────────────────────────────────────────────────────────────────────────────

function penampungBit() {
  const bit = [];
  return {
    bit,
    tulis(nilai, panjang) {
      for (let i = panjang - 1; i >= 0; i -= 1) bit.push((nilai >> i) & 1);
    },
  };
}

// ─── Membuat kata sandi ─────────────────────────────────────────────────────────────────────────────

function kataSandi(bita, versi, taraf) {
  const { ec, blok1, data1, blok2, data2, totalData } = tabel(versi, taraf);
  const p = penampungBit();
  p.tulis(0b0100, 4);                      // mode bita
  p.tulis(bita.length, versi >= 10 ? 16 : 8);
  for (const b of bita) p.tulis(b, 8);

  const maksBit = totalData * 8;
  p.tulis(0, Math.min(4, maksBit - p.bit.length));   // penutup
  while (p.bit.length % 8 !== 0) p.bit.push(0);

  const data = [];
  for (let i = 0; i < p.bit.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j += 1) b = (b << 1) | p.bit[i + j];
    data.push(b);
  }
  // Isian baku bergantian, sesuai standar.
  for (let i = 0; data.length < totalData; i += 1) data.push(i % 2 === 0 ? 0xec : 0x11);

  // Pecah menjadi blok, hitung EC tiap blok, lalu selang-seling.
  const blok = [];
  let pos = 0;
  for (let i = 0; i < blok1; i += 1) {
    blok.push(data.slice(pos, pos + data1));
    pos += data1;
  }
  for (let i = 0; i < blok2; i += 1) {
    blok.push(data.slice(pos, pos + data2));
    pos += data2;
  }
  const blokEc = blok.map((b) => kataEc(b, ec));

  const keluar = [];
  const dataTerpanjang = Math.max(...blok.map((b) => b.length));
  for (let i = 0; i < dataTerpanjang; i += 1) {
    for (const b of blok) if (i < b.length) keluar.push(b[i]);
  }
  for (let i = 0; i < ec; i += 1) {
    for (const b of blokEc) keluar.push(b[i]);
  }
  return keluar;
}

// ─── Kerangka matriks ───────────────────────────────────────────────────────────────────────────────

function kerangka(versi) {
  const n = 4 * versi + 17;
  const modul = Array.from({ length: n }, () => new Array(n).fill(false));
  const pakai = Array.from({ length: n }, () => new Array(n).fill(false));

  const taruh = (y, x, nyala) => {
    modul[y][x] = nyala;
    pakai[y][x] = true;
  };

  const pencari = (y0, x0) => {
    for (let y = -1; y <= 7; y += 1) {
      for (let x = -1; x <= 7; x += 1) {
        const yy = y0 + y;
        const xx = x0 + x;
        if (yy < 0 || yy >= n || xx < 0 || xx >= n) continue;
        const di = y >= 0 && y <= 6 && x >= 0 && x <= 6;
        const tepi = di && (y === 0 || y === 6 || x === 0 || x === 6);
        const inti = y >= 2 && y <= 4 && x >= 2 && x <= 4;
        taruh(yy, xx, tepi || inti);
      }
    }
  };
  pencari(0, 0);
  pencari(0, n - 7);
  pencari(n - 7, 0);

  // Pola waktu
  for (let i = 8; i < n - 8; i += 1) {
    taruh(6, i, i % 2 === 0);
    taruh(i, 6, i % 2 === 0);
  }

  // Pola penyelaras, kecuali yang bertabrakan dengan pola pencari.
  const titik = PENYELARAS[versi];
  for (const cy of titik) {
    for (const cx of titik) {
      const dekatPencari = (cy <= 8 && cx <= 8) || (cy <= 8 && cx >= n - 9) || (cy >= n - 9 && cx <= 8);
      if (dekatPencari) continue;
      for (let y = -2; y <= 2; y += 1) {
        for (let x = -2; x <= 2; x += 1) {
          taruh(cy + y, cx + x, Math.max(Math.abs(y), Math.abs(x)) !== 1);
        }
      }
    }
  }

  // Modul gelap tetap.
  taruh(4 * versi + 9, 8, true);

  // Tempat keterangan format disisihkan dulu; isinya ditulis sesudah topeng dipilih.
  for (let i = 0; i < 9; i += 1) {
    if (!pakai[8][i]) pakai[8][i] = true;
    if (!pakai[i][8]) pakai[i][8] = true;
  }
  for (let i = 0; i < 8; i += 1) {
    pakai[8][n - 1 - i] = true;
    pakai[n - 1 - i][8] = true;
  }

  // Keterangan versi (versi 7 ke atas), dihitung dengan BCH, bukan disalin dari tabel.
  if (versi >= 7) {
    let sisa = versi;
    for (let i = 0; i < 12; i += 1) sisa = (sisa << 1) ^ ((sisa >> 11) * 0x1f25);
    const bit = ((versi << 12) | sisa) & 0x3ffff;
    for (let i = 0; i < 18; i += 1) {
      const nyala = ((bit >> i) & 1) === 1;
      const a = Math.floor(i / 3);
      const b = (i % 3) + n - 11;
      taruh(b, a, nyala);
      taruh(a, b, nyala);
    }
  }

  return { n, modul, pakai };
}

/** Urutan modul data: zigzag dua kolom dari kanan bawah, melompati kolom pola waktu. */
function urutanData(n, pakai) {
  const urut = [];
  let naik = true;
  for (let kanan = n - 1; kanan >= 1; kanan -= 2) {
    // Kolom 6 adalah pola waktu dan DILEWATI seluruhnya: nilai peubahnya diubah supaya pasangan kolom
    // berikutnya bergeser menjadi (5,4), (3,2), (1,0). Versi lama memakai peubah bantu tanpa mengubah
    // `kanan`, sehingga pasangannya menjadi (5,4), (4,3), (2,1) — bertumpuk, dan kolom 0 tidak pernah
    // terpakai. Itu membuat QR tidak terbaca pemindai sungguhan (terbukti di HP, 26 Okt).
    if (kanan === 6) kanan = 5;
    for (let i = 0; i < n; i += 1) {
      const y = naik ? n - 1 - i : i;
      for (const x of [kanan, kanan - 1]) {
        if (!pakai[y][x]) urut.push([y, x]);
      }
    }
    naik = !naik;
  }
  return urut;
}

const TOPENG = [
  (y, x) => (y + x) % 2 === 0,
  (y) => y % 2 === 0,
  (_y, x) => x % 3 === 0,
  (y, x) => (y + x) % 3 === 0,
  (y, x) => (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0,
  (y, x) => ((y * x) % 2) + ((y * x) % 3) === 0,
  (y, x) => (((y * x) % 2) + ((y * x) % 3)) % 2 === 0,
  (y, x) => (((y + x) % 2) + ((y * x) % 3)) % 2 === 0,
];

function tulisFormat(modul, n, taraf, nomorTopeng) {
  const data = (TARAF_BIT[taraf] << 3) | nomorTopeng;
  let sisa = data;
  for (let i = 0; i < 10; i += 1) sisa = (sisa << 1) ^ ((sisa >> 9) * 0x537);
  const bit = (((data << 10) | sisa) ^ 0x5412) & 0x7fff;

  // ⛔ URUTAN BITNYA DARI YANG TERBESAR. Sel pertama di tiap daftar di bawah memuat bit ke-14 (paling
  // berarti), bukan bit ke-0. Versi lama menulisnya terbalik: wilayah datanya sudah benar persis sama dengan
  // QR rujukan, tetapi seluruh keterangan formatnya terbalik, sehingga tidak ada pemindai yang bisa
  // membacanya. Pembaca bacaKembali() di berkas ini memakai urutan yang sama, jadi ia tidak pernah
  // menangkapnya — baru ketahuan saat dibandingkan modul per modul dengan QR buatan OpenCV (26 Okt).
  const ambil = (k) => ((bit >> (14 - k)) & 1) === 1;

  const salinan1 = [
    [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 7], [8, 8],
    [7, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8],
  ];
  const salinan2 = [
    ...Array.from({ length: 7 }, (_, i) => [n - 1 - i, 8]),
    ...Array.from({ length: 8 }, (_, i) => [8, n - 8 + i]),
  ];
  for (const daftar of [salinan1, salinan2]) {
    daftar.forEach(([y, x], k) => { modul[y][x] = ambil(k); });
  }
  modul[n - 8][8] = true; // modul gelap
}

/** Nilai hukuman topeng, aturan 1-4 standar. Makin kecil makin baik. */
function hukuman(modul, n) {
  let nilai = 0;

  // Aturan 1: deretan lima modul sewarna atau lebih.
  for (let i = 0; i < n; i += 1) {
    for (const mendatar of [true, false]) {
      let beruntun = 1;
      for (let j = 1; j < n; j += 1) {
        const a = mendatar ? modul[i][j] : modul[j][i];
        const b = mendatar ? modul[i][j - 1] : modul[j - 1][i];
        if (a === b) {
          beruntun += 1;
        } else {
          if (beruntun >= 5) nilai += beruntun - 2;
          beruntun = 1;
        }
      }
      if (beruntun >= 5) nilai += beruntun - 2;
    }
  }

  // Aturan 2: kotak 2x2 sewarna.
  for (let y = 0; y < n - 1; y += 1) {
    for (let x = 0; x < n - 1; x += 1) {
      const a = modul[y][x];
      if (a === modul[y][x + 1] && a === modul[y + 1][x] && a === modul[y + 1][x + 1]) nilai += 3;
    }
  }

  // Aturan 3: pola 1:1:3:1:1 yang mirip pola pencari.
  const pola = [true, false, true, true, true, false, true, false, false, false, false];
  const polaBalik = [...pola].reverse();
  const cocok = (ambil, i, p) => p.every((v, k) => ambil(i + k) === v);
  for (let i = 0; i < n; i += 1) {
    for (let j = 0; j <= n - 11; j += 1) {
      const mendatar = (k) => modul[i][j + k - j];
      const tegak = (k) => modul[j + k - j][i];
      const ambilM = (k) => (j + k < n ? modul[i][j + k] : false);
      const ambilT = (k) => (j + k < n ? modul[j + k][i] : false);
      void mendatar;
      void tegak;
      if (cocok(ambilM, 0, pola) || cocok(ambilM, 0, polaBalik)) nilai += 40;
      if (cocok(ambilT, 0, pola) || cocok(ambilT, 0, polaBalik)) nilai += 40;
    }
  }

  // Aturan 4: ketimpangan jumlah modul gelap.
  let gelap = 0;
  for (let y = 0; y < n; y += 1) for (let x = 0; x < n; x += 1) if (modul[y][x]) gelap += 1;
  const persen = (gelap * 100) / (n * n);
  nilai += Math.floor(Math.abs(persen - 50) / 5) * 10;

  return nilai;
}

// ─── Pintu utama ────────────────────────────────────────────────────────────────────────────────────

function keBita(teks) {
  if (typeof teks !== 'string' || teks.length === 0) throw new Error('teks QR kosong');
  return [...new TextEncoder().encode(teks)];
}

/**
 * Buat QR dari teks. Mengembalikan { versi, ukuran, modul } dengan `modul[y][x]` bernilai true untuk gelap.
 * Tanpa zona sunyi — itu ditambahkan saat digambar.
 */
export function buatQr(teks, { taraf = 'M', versiPaksa = 0 } = {}) {
  const bita = keBita(teks);

  let versi = 0;
  for (let v = Math.max(1, versiPaksa); v <= VERSI_MAKS; v += 1) {
    if (bita.length <= kapasitas(v, taraf)) {
      versi = v;
      break;
    }
  }
  if (versi === 0) {
    throw new Error(
      `teks ${bita.length} bita tidak muat di QR versi ${VERSI_MAKS}; batasnya ${kapasitas(VERSI_MAKS, taraf)} bita`,
    );
  }

  const kata = kataSandi(bita, versi, taraf);
  const { n, modul, pakai } = kerangka(versi);
  const urut = urutanData(n, pakai);

  for (let i = 0; i < urut.length; i += 1) {
    const bitKe = i;
    const bita8 = kata[Math.floor(bitKe / 8)];
    const nyala = bita8 !== undefined && ((bita8 >> (7 - (bitKe % 8))) & 1) === 1;
    const [y, x] = urut[i];
    modul[y][x] = nyala;
  }

  // Pilih topeng dengan hukuman terkecil. Dicoba di salinan supaya matriks aslinya tidak ikut tertopengi.
  let terbaik = { nomor: 0, nilai: Infinity, hasil: null };
  for (let m = 0; m < 8; m += 1) {
    const salinan = modul.map((baris) => [...baris]);
    for (const [y, x] of urut) if (TOPENG[m](y, x)) salinan[y][x] = !salinan[y][x];
    tulisFormat(salinan, n, taraf, m);
    const nilai = hukuman(salinan, n);
    if (nilai < terbaik.nilai) terbaik = { nomor: m, nilai, hasil: salinan };
  }

  return { versi, taraf, ukuran: n, topeng: terbaik.nomor, modul: terbaik.hasil };
}

/**
 * Bongkar QR buatan `buatQr` kembali menjadi teks.
 *
 * ⚠️ Ini pembaca BUATAN KITA SENDIRI: ia menangkap salah penempatan, salah topeng, dan salah susun blok,
 * tetapi tidak membuktikan pemindai sungguhan bisa membacanya. Pembuktian itu memakai BarcodeDetector peramban.
 * Ia juga tidak memperbaiki galat — ia hanya membaca bagian datanya.
 */
export function bacaKembali(qr) {
  const { versi, taraf, ukuran: n, topeng, modul } = qr;
  const { pakai } = kerangka(versi);
  const urut = urutanData(n, pakai);

  const bit = [];
  for (const [y, x] of urut) {
    const nyala = TOPENG[topeng](y, x) ? !modul[y][x] : modul[y][x];
    bit.push(nyala ? 1 : 0);
  }

  const kata = [];
  for (let i = 0; i + 8 <= bit.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j += 1) b = (b << 1) | bit[i + j];
    kata.push(b);
  }

  // Urai selang-seling blok, lalu ambil bagian datanya saja.
  const { ec, blok1, data1, blok2, data2, totalData } = tabel(versi, taraf);
  const panjang = [...Array(blok1).fill(data1), ...Array(blok2).fill(data2)];
  const blok = panjang.map(() => []);
  let pos = 0;
  const terpanjang = Math.max(...panjang);
  for (let i = 0; i < terpanjang; i += 1) {
    for (let b = 0; b < blok.length; b += 1) {
      if (i < panjang[b]) {
        blok[b].push(kata[pos]);
        pos += 1;
      }
    }
  }
  void ec;
  const data = blok.flat().slice(0, totalData);

  // Bongkar kepala: mode 4 bit, jumlah 8 atau 16 bit.
  const semuaBit = [];
  for (const b of data) for (let j = 7; j >= 0; j -= 1) semuaBit.push((b >> j) & 1);
  const ambil = (mulai, panjangBit) => {
    let nilai = 0;
    for (let i = 0; i < panjangBit; i += 1) nilai = (nilai << 1) | semuaBit[mulai + i];
    return nilai;
  };
  const mode = ambil(0, 4);
  if (mode !== 0b0100) throw new Error(`mode ${mode} bukan mode bita`);
  const bitHitung = versi >= 10 ? 16 : 8;
  const jumlah = ambil(4, bitHitung);

  const isi = new Uint8Array(jumlah);
  for (let i = 0; i < jumlah; i += 1) isi[i] = ambil(4 + bitHitung + i * 8, 8);
  return new TextDecoder().decode(isi);
}

/**
 * Hanya untuk pemeriksaan: kata sandi per blok (data dan koreksi galat), sebelum diselang-seling.
 * Dipakai uji sindrom Reed-Solomon, yang memeriksa sifat matematisnya dan karena itu tidak ikut salah
 * bila pembuat di berkas ini salah.
 */
export function blokUji(teks, { taraf = 'M' } = {}) {
  const bita = keBita(teks);
  let versi = 0;
  for (let v = 1; v <= VERSI_MAKS; v += 1) {
    if (bita.length <= kapasitas(v, taraf)) { versi = v; break; }
  }
  if (versi === 0) throw new Error('teks terlalu panjang');
  const { ec, blok1, data1, blok2, data2, totalData } = tabel(versi, taraf);

  const p = penampungBit();
  p.tulis(0b0100, 4);
  p.tulis(bita.length, versi >= 10 ? 16 : 8);
  for (const b of bita) p.tulis(b, 8);
  p.tulis(0, Math.min(4, totalData * 8 - p.bit.length));
  while (p.bit.length % 8 !== 0) p.bit.push(0);
  const data = [];
  for (let i = 0; i < p.bit.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j += 1) b = (b << 1) | p.bit[i + j];
    data.push(b);
  }
  for (let i = 0; data.length < totalData; i += 1) data.push(i % 2 === 0 ? 0xec : 0x11);

  const blok = [];
  let pos = 0;
  for (let i = 0; i < blok1; i += 1) { blok.push(data.slice(pos, pos + data1)); pos += data1; }
  for (let i = 0; i < blok2; i += 1) { blok.push(data.slice(pos, pos + data2)); pos += data2; }
  return { versi, blok: blok.map((b) => ({ data: b, ec: [...kataEc(b, ec)] })) };
}

/** Hanya untuk pemeriksaan: jumlah modul yang dipakai data pada satu versi. Standar menentukan angkanya. */
export function jumlahModulData(versi) {
  const { n, pakai } = kerangka(versi);
  return urutanData(n, pakai).length;
}

/**
 * Hanya untuk pemeriksaan: kata sandi yang DIAMBIL DARI DALAM MATRIKS, seperti yang dilakukan pemindai
 * (buka topeng, telusuri wilayah data, urai selang-seling blok). Berbeda dengan blokUji(), yang memakai
 * larik di dalam pembuat — selisih antara keduanya berarti ada salah penempatan atau salah topeng.
 */
export function blokDariMatriks(qr) {
  const { versi, taraf, ukuran: n, topeng, modul } = qr;
  const { pakai } = kerangka(versi);
  const urut = urutanData(n, pakai);

  const bit = [];
  for (const [y, x] of urut) bit.push((TOPENG[topeng](y, x) ? !modul[y][x] : modul[y][x]) ? 1 : 0);
  const kata = [];
  for (let i = 0; i + 8 <= bit.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j += 1) b = (b << 1) | bit[i + j];
    kata.push(b);
  }

  const { ec, blok1, data1, blok2, data2 } = tabel(versi, taraf);
  const panjang = [...Array(blok1).fill(data1), ...Array(blok2).fill(data2)];
  const data = panjang.map(() => []);
  let pos = 0;
  for (let i = 0; i < Math.max(...panjang); i += 1) {
    for (let b = 0; b < data.length; b += 1) if (i < panjang[b]) { data[b].push(kata[pos]); pos += 1; }
  }
  const ecBlok = panjang.map(() => []);
  for (let i = 0; i < ec; i += 1) {
    for (let b = 0; b < ecBlok.length; b += 1) { ecBlok[b].push(kata[pos]); pos += 1; }
  }
  return data.map((d, i) => ({ data: d, ec: ecBlok[i] }));
}
