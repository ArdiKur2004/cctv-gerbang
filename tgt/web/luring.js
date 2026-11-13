// Mode luring untuk layar gerbang. Rencana T4.
//
// Gerbang sering di luar jangkauan jaringan, dan layar satpam harus tetap bekerja saat server mati.
// Dua bahaya yang dijaga berkas ini, dan keduanya lebih buruk daripada "tidak terkirim":
//   1. kejadian HILANG diam-diam — satpam mengira tercatat, padahal tidak;
//   2. kejadian terkirim DUA KALI — catatan gerbang jadi berbohong tentang berapa kendaraan yang lewat.
//
// Pasangannya di server adalah kolom `penanda` yang unik: kirim ulang aman, karena server mengembalikan
// kejadian yang sudah ada alih-alih membuat yang baru.

const KUNCI_ANTREAN = 'tgt.antrean';
const KUNCI_IZIN = (gerbangId) => `tgt.izin.${gerbangId}`;

/** Penyimpanan yang tidak pernah melempar. Peramban bisa menolak menulis (penyamaran, kuota penuh). */
function simpananAman(simpanan) {
  return {
    baca(kunci) {
      try {
        return simpanan.getItem(kunci);
      } catch {
        return null;
      }
    },
    tulis(kunci, nilai) {
      try {
        simpanan.setItem(kunci, nilai);
        return true;
      } catch {
        // Layar gerbang tetap bekerja; yang hilang hanya ketahanan terhadap muat ulang halaman.
        return false;
      }
    },
  };
}

function penandaBawaan() {
  // crypto.randomUUID ada di peramban modern dan di Node; kalau tidak ada, jatuh ke gabungan waktu dan acak.
  const c = globalThis.crypto;
  if (c && typeof c.randomUUID === 'function') return c.randomUUID();
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 11)}-${Math.random().toString(36).slice(2, 11)}`;
}

/**
 * @param simpanan    antarmuka seperti localStorage
 * @param kirim       async (gerbangId, kejadian) => void; melempar bila gagal
 * @param penandaBaru pembuat penanda, bisa diganti untuk uji
 */
export function buatLuring({ simpanan, kirim, penandaBaru = penandaBawaan } = {}) {
  const simpan = simpananAman(simpanan ?? globalThis.localStorage);

  // Antrean dipegang di ingatan DAN disalin ke penyimpanan. Ingatan supaya tetap jalan saat penyimpanan
  // menolak menulis; penyimpanan supaya selamat saat halaman dimuat ulang.
  let antrean = [];
  try {
    const tersimpan = JSON.parse(simpan.baca(KUNCI_ANTREAN) ?? '[]');
    if (Array.isArray(tersimpan)) antrean = tersimpan;
  } catch {
    antrean = [];
  }

  // Penjaga supaya dua penyusulan yang berbarengan tidak mengirim kejadian yang sama dua kali. Layar gerbang
  // bisa memicunya dari dua tempat sekaligus: pewaktu berkala dan peristiwa "online" peramban.
  let sedangSusul = null;

  const tulisAntrean = () => simpan.tulis(KUNCI_ANTREAN, JSON.stringify(antrean));

  return {
    /** Salin daftar izin ke perangkat, untuk dipakai saat internet putus. */
    simpanIzin(gerbangId, daftar) {
      return simpan.tulis(KUNCI_IZIN(gerbangId), JSON.stringify(daftar));
    },

    /** null berarti BELUM PERNAH disalin — berbeda dengan daftar kosong, dan satpam perlu tahu bedanya. */
    bacaIzin(gerbangId) {
      const teks = simpan.baca(KUNCI_IZIN(gerbangId));
      if (teks === null) return null;
      try {
        const isi = JSON.parse(teks);
        return Array.isArray(isi) ? isi : null;
      } catch {
        return null;
      }
    },

    antrekan(gerbangId, kejadian) {
      const penanda = penandaBaru();
      antrean.push({ ...kejadian, gerbangId, penanda });
      tulisAntrean();
      return penanda;
    },

    jumlahAntre() {
      return antrean.length;
    },

    /**
     * Kirim antrean ke server, berurutan. Berhenti pada kegagalan PERTAMA dan menahan sisanya: melompati yang
     * gagal akan mengacak urutan kejadian gerbang, dan urutan itulah yang dibaca orang saat menelusuri
     * siapa masuk lebih dulu.
     */
    async susulkan() {
      if (sedangSusul) return sedangSusul;
      sedangSusul = (async () => {
        let terkirim = 0;
        while (antrean.length > 0) {
          const k = antrean[0];
          try {
            await kirim(k.gerbangId, k);
          } catch {
            break;
          }
          antrean.shift();
          tulisAntrean();
          terkirim += 1;
        }
        return { terkirim, tersisa: antrean.length };
      })();
      try {
        return await sedangSusul;
      } finally {
        sedangSusul = null;
      }
    },
  };
}
