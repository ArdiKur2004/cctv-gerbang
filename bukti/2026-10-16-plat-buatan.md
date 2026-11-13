# Plat buatan komputer dengan huruf yang digambar sendiri (K35)

> Rencana 18 Fase 1, dijalankan 16 Okt 2026 secara mandiri (K37). Bahan `BOLEH-PRODUK` (`data-asal/bahan.json` butir
> `plat-buatan`). Teks platnya acak, bukan plat orang, jadi agen boleh melihat contohnya.

## 1. Yang dibangun (`tools/lab/plat_buatan.py`)

- **Huruf:** 36 huruf dan angka, ditambah titik, digambar sendiri sebagai garis di kisi 6×10 dan ditebalkan saat digambar.
- **Isi:** pola Perpol 7/2021, yaitu kode wilayah 1–2 huruf (acak), nomor 1–9999, seri 0–3 huruf, dan baris kecil masa berlaku.
- **Warna:** putih/hitam, hitam/putih (plat lama), kuning/hitam, merah/putih, hijau/hitam.
- **Bentuk:** lebar/tinggi motor 2,0–2,6 dan mobil 2,6–3,4. Rentang ini diambil dari kuantil kotak plat nyata di plat-lighting
  (1,97 / 2,49 / 3,25 pada 10/50/90%), yang diukur dari label saja.
- **Variasi:** miring dan perspektif, kecil (tinggi 12–60 px), buram, malam dan silau, inframerah (kelabu), kotor, derau, JPEG.
- **CLI `buat`:** menulis gambar dan `label.csv`, dan hasilnya sama persis untuk benih yang sama.

## 2. Diperbaiki sesudah melihat contoh

Lembar contoh pertama memperlihatkan teks panjang yang dipersempit sampai hurufnya menempel. Pada CJ2229SAK, 9 huruf hanya
menjadi 3 bagian tinta. Uji "huruf tidak saling menempel" ditulis lebih dulu dan terlihat merah. Dari diagnosis rentang x tiap
bagian, sebabnya celah yang termakan tebal garis. Sekarang baris yang terlalu lebar diperkecil utuh dengan bentuk tetap, celah
antarhuruf 0,4 lebar huruf, dan garis 0,14.

## 3. Kemiripan dengan plat nyata (diukur, bukan diklaim)

fpo-indo-1 dilatih hanya dengan plat nyata INDO-ALPR dan tidak pernah melihat huruf buatan ini. Ia membaca benar:
- **96 dari 200 plat buatan bersih (48%)**;
- **91 dari 200 plat buatan yang diubah (46%)**.

Jadi huruf buatan cukup mirip huruf plat nyata untuk dibaca separuhnya tanpa latihan, tetapi belum sama. Plat buatan dipakai
untuk melatih pembaca di Rencana 20, dan hasilnya diukur pada set uji nyata.

## 4. Batas

- **Huruf hanya mirip** huruf plat resmi. Bentuk dan ukuran huruf tidak diatur dalam peraturan yang terbaca.
- **Kode wilayah acak**, tidak mengikuti sebaran kode yang sebenarnya.
- **Variasi buatan belum tentu sama** dengan buram dan silau kamera CCTV sungguhan.

## 5. Catatan pelaksanaan

- **Gerbang lab:** 210 → 215 → 217. Tiap uji baru terlihat merah dulu.
- **Uji image tambahan:** 21 → 22 (suite penuh dijalankan, 22 passed). Uji kemiripan adalah pengukur, jadi tidak pernah merah.
- **Koreksi atas pesan commit 820ea07:** angka "21 → 22" di sana ditulis sebelum suite penuh dijalankan. Suite penuh kemudian
  memastikan 22 passed.
