# Mesin baca huruf buatan sendiri yang pertama (mesin-baca-1)

> Rencana 8 Fase 0A, dijalankan 14 Okt 2026 atas lampu hijau owner ("A").
> **Angka sementara dari bahan luar. Bukan angka produk dan bukan bukti K9.**
> Sumber angka: [`2026-10-14-mesin-baca-1.json`](2026-10-14-mesin-baca-1.json) (catatan latihan dan manifes mesin),
> [`2026-10-14-baca-mesin-1.json`](2026-10-14-baca-mesin-1.json), [`2026-10-14-baca-mesin-1-cpu.json`](2026-10-14-baca-mesin-1-cpu.json),
> dan [`2026-10-14-banding-pembaca.json`](2026-10-14-banding-pembaca.json) di folder ini. Isinya hitungan saja. Sebelum disalin ke
> sini, keempatnya diperiksa tidak memuat satu pun dari 9.739 teks plat dan nama berkas. Pemeriksanya diuji dulu pada bacaan
> mesin, dan menemukan 2.381 di antaranya.

## 1. Mesinnya

- **Bentuk:** CNN kecil (empat blok konvolusi) + LSTM dua arah dua lapis + CTC. Masukannya potongan plat kelabu 48×160,
  keluarannya 40 langkah. Ada 909.925 parameter, dan bobotnya 3,6 MB berformat safetensors (bukan pickle), dengan SHA-256
  dicatat.
- **Dilatih dari nol**, tanpa bobot awal dari pihak mana pun, hanya dari bahan latih INDO-ALPR yang sudah dibersihkan
  (Rencana 7).
- **Tanda mesin** menurut pemeriksa mesin jualan (`tools/periksa-jualan.mjs`): **`BOLEH-PRODUK`**. Tanda ini soal asal bahan,
  bukan soal mutu.

## 2. Latihan

| Hal | Angka |
|---|---|
| Bahan inti | 2.521 plat, 3.954 gambar |
| Validasi (memilih zaman; per plat, dari bahan latih) | 303 plat, 460 gambar |
| Zaman | 80; terbaik zaman 63 |
| Rugi rata-rata | zaman 1: 10,39 → zaman 40: 0,52 → zaman 80: 0,075 |
| Validasi benar per gambar | zaman 30: 1 · zaman 40: 54 · zaman 50: 126 · **zaman 63: 146 dari 460 (31,7%)** · zaman 80: 128 |
| Gambar tak terbaca | 0 |
| Kartu grafis | RTX 4060 laptop, satu job pada satu waktu |

**Bacaan agen:** rugi latihan turun hampir ke nol, sedangkan validasi berhenti di sekitar 32% dan mulai turun sesudah
zaman 63. Mesin **menghafal** bahan latihnya, bukan belajar membaca: 2.521 plat terlalu sedikit untuk melatih dari nol.

## 3. Angka pada set uji (dinilai sekali)

Kedatangan benar, dengan rentang 95%. Cara hitung yang adil untuk mesin ini adalah **911 plat tanpa label pilihan pembaca**
(laporan Rencana 6 bagian 6). Angka pada 937 plat ikut ditulis.

| Kelompok | mesin-baca-1 (911) | Qwen3-VL (911) | fast-plate-ocr (911) | mesin-baca-1 (937) |
|---|---|---|---|---|
| mobil-terang | 200/625 (32,0%; 28,5–35,8%) | 413/625 (66,1%; 62,3–69,7%) | 388/625 (62,1%; 58,2–65,8%) | 205/638 (32,1%; 28,6–35,9%) |
| mobil-gelap | 15/57 (26,3%; 16,6–39,0%) | 39/57 (68,4%; 55,5–79,0%) | 45/57 (78,9%; 66,7–87,5%) | 16/59 (27,1%; 17,4–39,6%) |
| motor-terang | 55/208 (26,4%; 20,9–32,8%) | 135/208 (64,9%; 58,2–71,1%) | 126/208 (60,6%; 53,8–67,0%) | 57/219 (26,0%; 20,7–32,2%) |
| motor-gelap | 5/21, terlalu sedikit | 15/21, terlalu sedikit | 14/21, terlalu sedikit | 5/21, terlalu sedikit |

Rincian mesin-baca-1 pada 937 plat: ragu 49 / 2 / 12 / 2; gambar benar 393 dari 1.094, 18 dari 66, 61 dari 239, 5 dari 23;
bacaan di luar pola plat hanya 9 / 0 / 4 / 0. Jadi bentuk bacaannya hampir selalu seperti plat, tetapi isinya sering salah.

**Kecepatan:** 0,003 detik per gambar di CPU laptop dan 0,006 detik di kartu grafis (satu gambar per panggilan). Bacaan
CPU dan kartu grafis sama persis. Pembanding: fast-plate-ocr 0,011 detik di CPU; Qwen3-VL 0,277 detik di kartu grafis.
Kotak murah belum diukur (B5).

**Artinya (bacaan agen):**

- Mesin pertama kita **jelas lebih lemah** dari kedua pembanding: sekitar 26–32% dibanding 61–79%, dengan rentang yang tidak
  bersentuhan. Itu wajar untuk mesin yang dilatih dari nol dengan 2.521 plat, dan grafik latihannya menunjukkan sebabnya
  (bagian 2): kurang bahan, bukan kurang zaman.
- Yang sudah terbukti: rantainya bekerja dari ujung ke ujung. Bahan bersih masuk, model dilatih tanpa melihat set uji, bobot
  aman tersimpan, angka dinilai adil, dan tanda asal bahannya `BOLEH-PRODUK`. Mesin ini juga kecil dan cepat: 3,6 MB,
  0,003 detik per gambar di CPU laptop.
- Cara yang biasa untuk menutup jarak ini: **lebih banyak bahan**, misalnya plat buatan komputer (usulan U9 butir 4) dan
  variasi gambar yang lebih kuat; atau **mulai dari bobot yang sudah belajar** (izin bobotnya harus jelas, P13 dan P14).
  Memilih di antaranya adalah langkah berikutnya, bukan bagian rencana ini.

## 4. Batas, apa adanya

- **Potongan plat, bukan kamera gerbang.** K9 tidak terbukti dari sini; langkah mencari plat di gambar utuh belum diukur.
- **Satu calon model, satu benih, satu kali latihan.** Spec 8.1 langkah 7 meminta dua atau tiga calon per langkah; itu belum.
- **Label:** set uji masih memuat label salah sekitar 3% (taksiran, Rencana 6). Sisa label salah di bahan latih belum diukur,
  dan kedua pembaca terbukti bisa sepakat pada bacaan salah (Rencana 7).
- **Kecepatan** diukur di laptop, bukan di kotak murah (B5).
- **Set uji dipakai sekali.** Perbaikan apa pun sesudah ini dinilai ulang pada set uji yang sama. Karena itu tiap perbaikan
  harus diputuskan dari validasi bahan latih, bukan dari angka uji, supaya set uji tidak ikut "terhafal" oleh kita.

## 5. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 101; lab 141 → 149 → 151, sama dengan rencana. Tiap uji baru terlihat merah dulu. Lama jalan
  gerbang lab naik dari sekitar 9 menjadi 25 detik karena tiga latihan kecil di CPU.
- Sebelum rencana ditulis, dua andaian kode dibuktikan di lab: safetensors menyimpan tensor tanpa dimensi, dan CTC di kartu
  grafis menerima target yang disambung.
- Baris "zaman 1" di log latihan tertimpa pembungkus stderr PowerShell; isinya ada (rugi 10,3939, validasi 0 dari 460).
  Ke-80 zaman tercatat di `mesin.json`.

## 6. Berikutnya

Laporan ini menutup langkah 7 Fase 0A untuk baca huruf dengan satu calon. Yang tersisa di Fase 0A:
- memperbaiki mesin baca huruf (lebih banyak bahan atau bobot awal);
- mencari plat di foto utuh dan video (langkah 1);
- plat buatan komputer;
- taksiran kecepatan di kotak;
- laporan Fase 0A untuk keputusan owner (lanjut, tunggu lokasi, atau ubah arah).
