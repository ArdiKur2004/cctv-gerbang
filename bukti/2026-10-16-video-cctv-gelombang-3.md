# Video CCTV gelombang ketiga: bahan tolak ukur Fase 1

> Rencana 16 Fase 1, dijalankan 16 Okt 2026 secara mandiri (K37), dengan satu titik berhenti untuk owner: lembar gambar kecil
> diperiksa owner sebelum dibuka agen (K19, jawaban owner "tidak ada yang terbaca"). Video tetap `RISET-SAJA`. Angka di sini
> dibaca dari `data-asal/video-riset.json` dan `data-asal/pembagian-video-fase1.json`.

## 1. Cari, pilih, unduh

- **Pencarian:** 16 kueri lewat pintu `tools/ambil-video.ps1` (hanya daftar), 15 hasil per kueri.
  - Indonesia: gerbang perumahan, rumah, portal, palang, pos satpam, sekolah, apartemen, kantor, parkir motor gedung,
    basement, malam, dan inframerah.
  - Luar negeri: kamera plat di gerbang dan parkiran.
- **Pilihan dari judul:** 88 video, yaitu 45 gerbang/portal Indonesia, 31 parkiran Indonesia, dan 12 kamera plat luar negeri.
  Video hantu, permainan, ulasan alat, vlog, dan video yang sudah ada tidak dipilih, begitu pula yang lebih dari 30 menit atau
  kurang dari 20 detik.
- **Unduhan** dengan sisi terpendek sampai 1080: **77 utuh**, 11 ditolak YouTube. Totalnya 13.908 detik.
  `periksa_utuh.py`: 177 utuh, 0 bermasalah, dari 177.

## 2. Pilah (K19)

| Sudut | Video baru |
|---|---|
| Gerbang | 23 |
| Parkiran | 22 |
| Kamera diam lain | 5 |
| Lain (berita dengan studio atau wawancara, promosi, peragaan, rekaman HP) | 27 |

**Aturan agen:**
- **Sudut:** video dihitung menurut sudut kameranya bila sekitar separuh atau lebih cuplikannya rekaman kamera diam.
- **Malam:** gambar kelabu dengan lampu terang (inframerah) ditandai malam, sedangkan kelabu yang tidak pasti ditandai tak
  jelas.
- **Remang:** basement berlampu.

Sepuluh rekaman gerbang sekolah hanya 352×288: sudutnya pas, tetapi platnya kemungkinan terlalu kecil untuk dibaca.

## 3. Pembagian latih dan uji

Dari 80 video bersudut gerbang (40), parkiran (22), dan kamera diam lain (18), termasuk video gelombang 1 dan 2:

| Lapis | Uji | Latih |
|---|---|---|
| gerbang, siang | 19 | 14 |
| gerbang, malam | 1 | 3 |
| gerbang, campuran / tak jelas | 0 | 3 |
| parkiran, siang | 8 | 6 |
| parkiran, remang / campuran / tak jelas | 5 | 3 |
| kamera diam lain, siang | 5 | 8 |
| kamera diam lain, malam / tak jelas | 3 | 2 |
| **Jumlah** | **41** | **39** |

Tiap video ditentukan dari SHA-256 "fase1/<berkas>"-nya sendiri (`tools/bagi-video.mjs`). Video uji tidak pernah pindah ke latih
saat video baru ditambahkan.

## 4. Batas

- **Malam dari sudut gerbang masih sedikit:** 4 video, dan hanya 1 di sisi uji.
- **Per lapis tidak seimbang**, karena pembagian sengaja tidak diatur per lapis.
- **Sebagian video berita** memuat cuplikan CCTV yang diselingi studio. Yang didominasi studio sudah ditandai "lain".
- **Alat ukur yang keliru, dicatat sebagai temuan:** pintu unduh melaporkan kode 8 ("ada `.part`") untuk 64 unduhan. Penyebabnya
  pintu memeriksa `.part` di seluruh folder, sehingga sesudah satu sisa `.part` dari unduhan gagal, semua unduhan berikutnya
  ikut kode 8. Keberhasilan dinilai dari pemeriksa keutuhan.

## 5. Catatan pelaksanaan

- **Gerbang uji:** Node 111 → 112 (`sudut` parkiran) → 117 (`tools/bagi-video.mjs`). Tiap uji baru terlihat merah dulu.
- **Rencana dikoreksi sebelum dijalankan:** cara membagi semula mengurutkan per lapis, yang bisa memindahkan video uji ke latih
  saat video bertambah. Diganti menjadi keputusan per video.
