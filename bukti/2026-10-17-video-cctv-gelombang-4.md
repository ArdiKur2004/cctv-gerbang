# Video CCTV gelombang keempat (K41)

> Rencana 22 Fase 1, dijalankan 17 Okt 2026 secara mandiri (K37). Owner menyarankan menambah video dari internet atau YouTube
> (K41), karena plat yang bisa dinilai per lembar uji hanya 18–23. Tidak ada kode baru; semua alat dari Rencana 16. Laporan ini
> hanya berisi hitungan dan teks judul publik.

## 1. Cari, pilih, unduh

- **Kueri:** 16 kueri terarah, masing-masing 15 hasil.
  - **Sasaran:** gerbang tempat kendaraan berhenti dekat kamera, gerbang dan parkiran motor, malam.
  - **Kueri malam 11–13 gagal:** hasilnya hanya video hantu, tutorial kamera, dan ulasan produk.
  - **Tambahan 3 kueri malam (17–19), penyimpangan dari rencana:** rekaman pencurian dari kamera diam di parkiran, minimarket, dan
    kompleks.
- **Dipilih dari judul: 86.** Yang dibuang kebanyakan berita kecelakaan di jalan, video hantu, tutorial, dan ulasan.
- **Terunduh dan utuh: 82** (`periksa_utuh`: 259 utuh, 0 bermasalah). Empat gagal diunduh dan tidak meninggalkan berkas setengah
  jadi.
- **Manifes:** 259 video.

## 2. Pemilahan (lembar gambar kecil, diperiksa owner lebih dulu: "tidak ada yang bisa terbaca")

| Sudut | Jumlah | Isi umumnya |
|---|---|---|
| Gerbang | 26 | Gerbang tol, palang dan karcis parkir, gerbang rumah, demo kamera pembaca plat di palang (sebagian luar negeri) |
| Parkiran | 22 | Parkiran motor kampus, minimarket, masjid, hotel; berita dengan cuplikan CCTV |
| Kamera diam lain | 17 | Rumah, jalan kompleks, halaman kantor, uji pembaca plat di jalan |
| Lain | 17 | Rekaman layar aplikasi, promosi produk, berita studio, animasi; tidak dipakai |

**Menurut kategori, 65 video yang dipakai (tanpa "lain"):**
- siang 46;
- malam 7 (5 kamera diam lain, 2 parkiran);
- remang 5;
- campuran 4;
- tak jelas 3.

Ditambah 17 video "lain" (7 siang, 7 tak jelas, 3 campuran).

## 3. Pembagian latih dan uji

Alat dan aturannya sama dengan sebelumnya: tiap video dibagi menurut SHA-256 "fase1/<berkas>" miliknya sendiri.
- **Tidak ada video lama yang pindah atau hilang**, diperiksa dengan `banding-pembagian-22.mjs` (gagal tertutup).
- **Sesudah gelombang keempat:** uji 41 → **77**, latih 39 → **68**.

**Video baru saja:**

| Lapis | Uji | Latih |
|---|---|---|
| Gerbang siang | 10 | 12 |
| Gerbang campuran / remang / tak jelas | 1 / 1 / 0 | 1 / 0 / 1 |
| Parkiran siang | 12 | 7 |
| Parkiran malam / tak jelas | 1 / 0 | 1 / 1 |
| Kamera diam lain siang | 5 | 0 |
| Kamera diam lain malam / remang / campuran / tak jelas | 2 / 3 / 1 / 0 | 3 / 1 / 1 / 1 |
| **Jumlah** | **36** | **29** |

**Sesudah gelombang keempat, malam di sisi uji:** gerbang 1, parkiran 1, kamera diam lain 3.

## 4. Batas

- **Malam masih sedikit.** Pencarian malam di YouTube kebanyakan memberi video hantu. Lima video malam di sisi uji belum cukup
  untuk kelompok malam.
- **Demo kamera pembaca plat sebagian dari luar negeri** (Vietnam, Thailand, dan lain-lain). Platnya tidak berpola Indonesia,
  jadi bacaannya pasti "ragu". Plat itu tetap berguna untuk menilai pencari plat.
- **Banyak video adalah berita** yang menyelipkan cuplikan CCTV di antara studio dan wawancara. Sebagian gambarnya bukan kamera
  diam.
- **Pemilahan dari gambar kecil yang buram dan judul.** Siang dan malam bisa keliru untuk video yang redup atau kebiruan.
- **Isi plat belum diketahui.** Berapa plat yang cukup jelas untuk dinilai baru terlihat dari lembar owner di putaran berikutnya.

## 5. Catatan pelaksanaan

- **Lembar lama untuk `lembar_kecil.py` harus `ikhtisar.json`, bukan foldernya.** Perintah di rencana disalin keliru. Alat
  menolak tanpa membuat lembar, lalu dijalankan ulang dengan jalur yang benar.
- **Enam video lama dari 13 Okt tidak punya `sudut` sejak dulu.** Mereka sudah ada di lembar kecil lama, dan tidak disentuh di
  sini.
