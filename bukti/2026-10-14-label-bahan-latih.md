# Bahan latih baca huruf dibersihkan (K24)

> Rencana 7 Fase 0A, dijalankan 14 Okt 2026 atas lampu hijau owner ("A").
> **Bahan latih untuk mesin buatan sendiri. Belum ada mesin yang dilatih, jadi belum ada angka mesin.**
> Sumber angka: enam ringkasan JSON di folder ini (`2026-10-14-kembar-lintas.json`, `-baca-fpo-latih.json`,
> `-baca-vlm-latih.json`, `-label-curiga-latih.json`, `-latih-koreksi.json`, `-kembar-akhir.json`). Isinya hitungan saja.
> Sebelum disalin ke sini, keenamnya diperiksa tidak memuat satu pun dari 9.739 teks plat dan nama berkas. Pemeriksanya diuji
> dulu pada berkas yang memang berisi plat, dan menemukan 9.632 di antaranya.
> **Dikoreksi 14 Okt:** owner menjelaskan bahwa 11 baris yang disebutnya tanpa keterangan berarti "A benar". Ke-11 plat itu
> dikembalikan ke bahan latih dengan label penerbitnya. Angka di bawah sudah memakai jawaban yang dijelaskan itu; versi
> sebelumnya ada di riwayat git.

## 1. Apa yang dikerjakan

Owner memilih membersihkan label bahan latih sebelum mesin baca huruf pertama dilatih (K24). Ada dua langkah:

1. **Kendaraan kembar lintas sisi, dikenali dari gambar** (otomatis, tanpa waktu owner). Ditambahkan sesudah pengukuran
   sebelum rencana ditulis.
2. **Label latih dibersihkan dengan cara K22:** dua pembaca membaca bahan latih, plat yang mereka baca sama tetapi berbeda
   dari labelnya masuk lembar, dan owner menjawab dengan nomor baris.

Set uji 937 plat dari Rencana 6 **tidak diubah** di langkah mana pun.

## 2. Kendaraan kembar lintas sisi

**Kalibrasi** (diukur sebelum rencana ditulis), dengan sidik gambar dHash 64 bit:
- Pasangan foto berplat sama: 10,9% berjarak ≤ 4.
- Pasangan foto berplat beda (20.000 sampel acak): tak satu pun berjarak ≤ 12.
- Lintas sisi, pada jarak ≤ 4: 21 dari 22 pasangan berlabel hanya beda 1–2 huruf. Itu pola salah ketik label pada
  kendaraan yang sama.

**Aturan:** gambar latih dan gambar uji berjarak ≤ 8 **dan** labelnya berjarak sunting ≤ 2 berarti kendaraan yang sama, dan
plat latihnya dikeluarkan.

| | Pasangan gambar mirip (≤ 8) | Berlabel beda ≤ 2 huruf | Plat latih dikeluarkan | Latih / uji |
|---|---|---|---|---|
| Sebelum label latih dibersihkan | 177 | 27 | **22** | 2.850 → 2.828 / 937 |
| Pemeriksaan ulang pada hasil akhir | 148 | 0 | 0 | 2.824 / 937 |

148 pasangan mirip yang tersisa semuanya berlabel jauh berbeda: potongan plat yang kebetulan mirip.

## 3. Label latih yang dicurigai dan jawaban owner

- **75 dari 2.828 kedatangan latih dicurigai:** mobil-terang 53, mobil-gelap 3, motor-terang 18, motor-gelap 1. Ada 4
  lembar; agen tidak membukanya.
- **Jawaban owner, dalam nomor baris:**

  | Jawaban | Baris | Tindakan |
  |---|---|---|
  | Tulisan B (dua pembaca) benar | 44 | label dibetulkan |
  | Tulisan A (label penerbit) benar | 27 (16 disebut "A", 11 disebut tanpa keterangan lalu dijelaskan owner sebagai "A benar") | label tetap |
  | Tidak tahu (2), salah semua (1), tak bisa dibaca (1) | 4 | plat dikeluarkan |

- **Hasil:** 44 dibetulkan, 4 dikeluarkan. Tidak satu pun label baru sama dengan plat di set uji, jadi tidak ada yang
  dikeluarkan karena bocor. 0 plat di kedua sisi.

**Temuan: dua pembaca bisa sepakat pada bacaan yang salah.** Di set uji (Rencana 6), tulisan B benar pada 29 dari 31 baris
yang dicurigai. Di bahan latih, tulisan A justru benar pada 27 dari 75 baris (36%): kedua pembaca sepakat pada bacaan yang
sama tetapi keliru. Jadi label otomatis dari kesepakatan dua pembaca **tidak boleh dipakai tanpa diperiksa manusia**, dan
taksiran "kira-kira separuh label salah tertangkap" dari Rencana 6 tidak berlaku begitu saja untuk bahan latih.

## 4. Kedua pembaca pada bahan latih

Kedatangan benar, dengan rentang 95%. "Sebelum" = terhadap label penerbit pada 2.828 plat (sesudah kembar dikeluarkan).
"Sesudah" = terhadap label yang sudah dibersihkan pada 2.824 plat.

| Kelompok | Qwen3-VL sebelum | Qwen3-VL sesudah | fast-plate-ocr sebelum | fast-plate-ocr sesudah |
|---|---|---|---|---|
| mobil-terang | 1.283/1.982 (64,7%; 62,6–66,8%) | 1.312/1.978 (66,3%; 64,2–68,4%) | 1.212/1.982 (61,2%; 59,0–63,3%) | 1.242/1.978 (62,8%; 60,6–64,9%) |
| mobil-gelap | 114/163 (69,9%; 62,5–76,5%) | 115/163 (70,6%; 63,1–77,0%) | 119/163 (73,0%; 65,7–79,2%) | 120/163 (73,6%; 66,4–79,8%) |
| motor-terang | 389/646 (60,2%; 56,4–63,9%) | 399/646 (61,8%; 58,0–65,4%) | 369/646 (57,1%; 53,3–60,9%) | 380/646 (58,8%; 55,0–62,6%) |
| motor-gelap | 31/37 (83,8%; 68,9–92,3%) | 32/37 (86,5%; 72,0–94,1%) | 30/37 (81,1%; 65,8–90,5%) | 31/37 (83,8%; 68,9–92,3%) |

Kecepatan: Qwen3-VL 0,305 detik per gambar di kartu grafis; fast-plate-ocr 0,014 detik per gambar di CPU.

Angka ini **bukan angka uji**: bahan latih tidak dipakai menilai mesin. Ia menunjukkan bahwa kedua pembaca berperilaku sama
di bahan latih dan di set uji (sekitar dua dari tiga plat benar). Kenaikan "sesudah" sebagian dibuat oleh caranya sendiri,
seperti di Rencana 6.

## 5. Bahan baca huruf yang berlaku sekarang

`data/keluaran/latih-koreksi/pembagian-koreksi.json` (memuat plat; hanya di laptop):

| Sisi | Plat | Per kelompok (mobil-terang / mobil-gelap / motor-terang / motor-gelap) |
|---|---|---|
| Latih | 2.824 (4.414 gambar) | 1.978 / 163 / 646 / 37 |
| Uji (dari Rencana 6, tidak diubah) | 937 | 638 / 59 / 219 / 21 |

Plat di kedua sisi: 0. Kendaraan kembar lintas sisi menurut aturan di bagian 2: 0.

## 6. Batas, apa adanya

- **Label salah masih tersisa di bahan latih.** Cara K22 hanya menangkap label yang dibantah dua pembaca yang sepakat, dan
  bagian 3 menunjukkan kesepakatan itu sendiri bisa keliru. Berapa yang tersisa belum diukur.
- **Kembar yang tidak tertangkap:** kendaraan yang sama dengan foto yang tidak nyaris kembar (jarak > 8), atau dengan label
  yang beda lebih dari 2 huruf. dHash hanya satu cara sidik gambar.
- **11 baris tanpa keterangan** mula-mula dikeluarkan agar tidak menebak; owner lalu menjelaskan maksudnya "A benar", dan
  `nilai_ulang.py` dijalankan ulang dengan jawaban itu.
- **Kembar di dalam satu sisi tidak diperiksa.** Ini tidak menimbulkan kebocoran, tetapi satu kendaraan bisa muncul sebagai
  dua plat di bahan latih.
- Tetap berlaku: potongan plat, bukan kamera gerbang; terang-gelap adalah taksiran; motor-gelap di set uji hanya 21 plat;
  angka set uji memihak dua pembaca ini (Rencana 6).

## 7. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 101; lab 128 → 136 → 140 → 141. Tiap uji baru terlihat merah dulu. Satu uji lebih banyak dari
  rencana: layar penilai ulang mencetak "plat latih" dan "kedatangan uji" untuk hitungan sisi latih. Angkanya benar,
  tulisannya salah. Ditemukan saat dijalankan, diperbaiki dengan uji lebih dulu.
- **Satu jalan ulang di lab sempat dipotong** dengan `Select-Object -First 1`, pola yang sama dengan `| head` yang dilarang.
  Sesudahnya diperiksa tidak ada container yang tertinggal, lalu dijalankan ulang penuh dengan kode keluar 0.
- **Alat kembar pada data sungguhan** memberi angka yang sama persis dengan pengukuran sebelum rencana ditulis (177, 27).
- Ringkasan sisi uji dihitung ulang sesudah pilihan sisi ditambahkan: sama persis untuk kedua pembaca.

## 8. Berikutnya

Rencana 8: mesin baca huruf buatan sendiri yang pertama. Ia dilatih dengan bahan latih di bagian 5 dan dinilai pada set uji
937 plat. Perbandingannya harus adil terhadap pembaca ketiga (batas "memihak" di Rencana 6). Yang perlu diukur dan
diputuskan lebih dulu: jenis model dan izinnya (dilatih dari nol atau dari bobot awal; P13, P14), dan cara melatih di lab
tanpa jaringan dengan kartu grafis yang dipakai bersama.
