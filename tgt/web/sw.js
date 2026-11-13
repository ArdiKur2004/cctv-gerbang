// Service worker TGT. Rencana T5.
//
// Dua tugasnya:
//   1. menerima notifikasi dorong dan menampilkannya, walau aplikasinya sedang tertutup (K72);
//   2. menyimpan cangkang aplikasi supaya layar gerbang tetap terbuka saat internet putus.
//
// ⛔ Yang TIDAK disimpan: jalur /api/. Daftar izin dan catatan kejadian tidak boleh disajikan dari simpanan
// lama tanpa sepengetahuan satpam — daftar izin basi bisa membuka gerbang untuk kendaraan yang izinnya sudah
// dicabut. Yang luring memakai salinan di localStorage, yang jelas terlihat sebagai salinan (tgt/web/luring.js).

const SIMPANAN = 'tgt-cangkang-v1';
const CANGKANG = ['/', '/index.html', '/gaya.css', '/app.js', '/luring.js', '/qr.js'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(SIMPANAN).then((c) => c.addAll(CANGKANG)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((nama) => Promise.all(nama.filter((n) => n !== SIMPANAN).map((n) => caches.delete(n))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (e) => {
  const alamat = new URL(e.request.url);
  // Jalur data SELALU dari jaringan: lihat alasannya di kepala berkas.
  if (alamat.pathname.startsWith('/api/')) return;
  if (e.request.method !== 'GET') return;

  e.respondWith(
    fetch(e.request)
      .then((jawaban) => {
        // Simpan salinan terbaru supaya kunjungan berikutnya tetap bisa dibuka saat internet putus.
        const salinan = jawaban.clone();
        caches.open(SIMPANAN).then((c) => c.put(e.request, salinan)).catch(() => {});
        return jawaban;
      })
      .catch(() => caches.match(e.request).then((tersimpan) => tersimpan ?? caches.match('/index.html'))),
  );
});

self.addEventListener('push', (e) => {
  let isi = { judul: 'Gerbang perlu diperiksa', pesan: 'Buka TGT untuk melihat.' };
  try {
    if (e.data) isi = { ...isi, ...e.data.json() };
  } catch {
    // Pesan yang tidak terbaca tetap ditampilkan apa adanya: lebih baik satpam melihat sesuatu daripada
    // tidak melihat apa pun.
  }
  e.waitUntil(self.registration.showNotification(isi.judul, {
    body: isi.pesan,
    tag: isi.sebab ?? 'tgt',
    // renotify false: kejadian sejenis yang beruntun mengganti yang lama, bukan menumpuk sampai tak terbaca.
    renotify: false,
    requireInteraction: isi.sebab === 'panggil_satpam',
    data: { halaman: '/?halaman=satpam' },
  }));
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  const tujuan = e.notification.data?.halaman ?? '/';
  e.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((jendela) => {
      const terbuka = jendela.find((j) => j.url.includes(self.registration.scope));
      if (terbuka) return terbuka.focus();
      return self.clients.openWindow(tujuan);
    }),
  );
});
