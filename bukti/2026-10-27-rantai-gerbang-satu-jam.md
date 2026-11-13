# Rantai jualan di rekaman gerbang satu jam (Rencana T9 bagian 2)

> Bahan: `youtube-qfGDsQINans.mp4` (K76) — pintu masuk parkir berpalang, **3.597 detik, 1280x720, 30 bingkai/detik**,
> sudut gerbang, vonis `RISET-SAJA`. Izin dari pemilik videonya, lewat owner.
>
> Setelan rantai **jualan**: pencari kendaraan `kendaraan-jualan-k1` · pencari plat `pencari-cctv2-c1` ambang 0,25 ·
> pembaca `pembaca-lanjut-r4` · `--cara potong --cadangan-utuh` · 2 utas.
>
> ⛔ Angka di sini adalah angka MESIN, belum dinilai manusia. Berapa yang benar-benar kendaraan dan berapa bacaan
> yang benar hanya bisa dijawab owner dari lembar — agen tidak membuka potongan maupun nomor platnya.

## 1. Dua laju contoh, dan hasilnya berlawanan dengan dugaan

Dijalankan dua kali: pada laju bawaan 5 gambar per detik, dan pada **1 gambar per detik** — laju yang sanggup
dilakukan `company-ai` (satu gambar butuh 1 detik di sana).

| | 5 gambar/detik | **1 gambar/detik** |
|---|---|---|
| gambar diperiksa | 17.984 | 3.597 |
| kedatangan | 330 | **123** |
| yakin | 113 (**34%**) | 64 (**52%**) |
| ragu | 217 (66%) | 59 (48%) |
| jalur terbuang (di bawah 2 penampakan) | 960 (74%) | 461 (79%) |
| detik sampai yakin, median | 0,4 detik | **1,0 detik** |
| detik sampai yakin, p95 | 2,8 detik | **2,0 detik** |
| bingkai per kedatangan, rata-rata | 13,0 | 4,8 |
| kotak plat di luar kendaraan dibuang | 0 | 0 |

**Yang mengejutkan: memeriksa LIMA KALI lebih sedikit gambar menaikkan bagian yang yakin dari 34% ke 52%.**

Bacaan agen atas sebabnya: pada 5 gambar per detik, ambang "minimal 2 penampakan" terlalu mudah dilewati —
satu salah-deteksi yang muncul dua bingkai berurutan (0,4 detik) sudah menjadi "kedatangan", lalu gagal
mencapai kesepakatan bacaan dan tercatat "ragu". Pada 1 gambar per detik, ambang yang sama menuntut benda itu
bertahan **2 detik**, dan salah-deteksi sekejap tersaring sendiri. Ini **bacaan agen, bukan kesimpulan** — yang
membuktikannya adalah penilaian owner atas lembarnya.

Kendaraan yang menjadi kedatangan terlihat rata-rata **4,8 detik** di gerbang, masuk akal untuk mobil yang
mendekat, berhenti di palang, lalu lewat.

## 2. ⛔ Di `company-ai`, 1 gambar per detik adalah BATAS, bukan pilihan

Kecepatan per gambar, keduanya 2 utas:

| | laptop (Ryzen 7 8700F) | `company-ai` (Celeron J4025) |
|---|---|---|
| dekode | 1,6 ms | — |
| pencari kendaraan | 68,3 ms | **716 ms** |
| pencari plat | 36,2 ms | **187 ms** |
| pembaca | 14,3 ms | **120 ms** |
| **satu gambar** | **~120 ms** | **~1.023 ms** |

Perbandingannya **8,6×** — ini mengganti perkiraan 6–12× dengan angka terukur.

**Dan di sinilah hitungannya menjadi penting:**

> 3.597 gambar × 1,023 detik = **3.679 detik** untuk video **3.597 detik**.

Artinya pada 1 gambar per detik, `company-ai` berjalan **tepat pas — bahkan 2% di belakang waktu nyata.**
Tidak ada margin sama sekali. Satu gangguan kecil dan ia tertinggal, lalu antreannya menumpuk.

### Tiga jalan keluar, dengan angkanya

| cara | satu gambar | margin pada 1 gambar/detik |
|---|---|---|
| sekarang (kendaraan → plat → baca) | 1.023 ms | **tidak ada** (102% waktu nyata) |
| tanpa tahap kendaraan (plat → baca) | **307 ms** | 3,3× — tetapi lebih sedikit plat ditemukan |
| lewati gambar yang tidak ada geraknya | belum diukur | tergantung berapa bagian gambar yang kosong |

Yang ketiga paling menarik dan **belum dikerjakan**: di gerbang, sebagian besar gambar tidak ada kendaraannya
sama sekali, dan pencari kendaraan (70% dari biayanya) tetap berjalan pada semuanya. Penyaring gerak yang
murah akan memotong pekerjaan itu tanpa mengurangi ketelitian bacaan. Itu usulan, belum diukur.

## 3. Yang MASIH menunggu owner

Lembar penilaian sudah dibuat dan **hanya owner yang membukanya** (memuat nomor plat):

- `data/keluaran/lembar-t9-laju1/` — **120 dari 123 kedatangan** pada 1 gambar per detik (hampir seluruhnya).
  **Ini yang paling berguna**, karena inilah laju yang akan dipakai di `company-ai`.
- `data/keluaran/lembar-t9/` — 120 dari 330 kedatangan pada 5 gambar per detik.

Cara memeriksanya sama seperti sebelumnya: owner menyebut **nomor baris** untuk empat jenis saja — `salah`,
`tak terbaca`, `bukan plat`, `motor`. Baris yang tidak disebut berarti bacaannya benar dan kendaraannya mobil.
Jawabannya diteruskan ke `lembar_rantai.py nilai`.

**Sampai itu dinilai, yang BELUM diketahui:**

1. Berapa dari 123 kedatangan itu benar-benar kendaraan, dan berapa salah-deteksi.
2. Berapa bacaan yang **benar**. "Yakin" hanya berarti mesin sepakat dengan dirinya sendiri — bacaan yang
   yakin tetapi salah adalah keadaan paling berbahaya (gerbang membuka untuk plat yang salah).
3. Berapa yang sepeda motor, yang di versi 1 memang di luar lingkup (K65).

## 4. Yang sudah terjawab dari pertanyaan T9

| pertanyaan | jawaban |
|---|---|
| Berapa bingkai dibutuhkan per kendaraan? | **median 1 detik, p95 2 detik** sampai bacaan yakin, pada 1 gambar/detik |
| Apakah jendela kedatangan 20 detik (K75) pas? | **Ya, longgar.** Kendaraan terlihat rata-rata 4,8 detik — jauh di bawah 20 detik, jadi bingkai satu kendaraan tidak akan terpecah menjadi dua kedatangan. Di sisi lain gerbang ini melewatkan satu kendaraan tiap ~29 detik (123 per jam), jadi 20 detik juga tidak akan menyatukan dua kendaraan berbeda — dan pengelompokan TGT memang hanya menyatukan plat yang SAMA |
| Apakah 1 detik per gambar terasa di palang? | **Pembacaannya tidak menjadi penghambat** (1–2 detik), tetapi **mesinnya tidak punya margin** (102% waktu nyata). Itu yang harus diperbaiki, bukan kecepatan bacanya |

## 5. Batas yang jujur

- Angka di berkas ini **angka mesin**, belum dinilai manusia. Jangan dipakai menjanjikan ketelitian apa pun.
- Satu rekaman, satu lokasi, satu kamera, siang hari. Tidak bisa digeneralkan ke gerbang lain, malam hari,
  atau hujan.
- Kecepatan `company-ai` diukur dengan masukan buatan di model yang sama, bukan dengan menjalankan rantai ini
  di sana. Angka 1.023 ms per gambar sah; perkaliannya menjadi "102% waktu nyata" adalah **hitungan**, bukan
  jalan sungguhan.
- Vonis bahan ini `RISET-SAJA`: ia boleh dipakai **mengukur**, dan melatih mesin yang dijual dengannya adalah
  keputusan owner tersendiri (K76).
