# fast-plate-ocr yang dilatih ulang dengan plat Indonesia (fpo-indo-1)

> Rencana 10 Fase 0A, dijalankan 15 Okt 2026 atas lampu hijau owner ("A").
> **Angka sementara dari bahan luar. Bukan angka produk dan bukan bukti K9.** Tanda mesin `RISET-SAJA` sampai izin tertulis
> pembuat fast-plate-ocr datang (K26, K27).
> Sumber angka: [`2026-10-15-fpo-indo-1.json`](2026-10-15-fpo-indo-1.json) (manifes mesin dan ringkasan latihan),
> [`2026-10-15-fpo-indo-1-latihan.csv`](2026-10-15-fpo-indo-1-latihan.csv) (catatan per zaman),
> [`2026-10-15-baca-fpo-indo-1.json`](2026-10-15-baca-fpo-indo-1.json), dan
> [`2026-10-15-banding-pembaca-10.json`](2026-10-15-banding-pembaca-10.json) di folder ini. Isinya hitungan saja. Sebelum
> disalin ke sini, keempatnya diperiksa tidak memuat satu pun dari 9.739 teks plat dan nama berkas. Pemeriksanya diuji dulu
> pada bacaan mesin, dan menemukan 2.379 di antaranya.

## 1. Mesinnya

- **Titik berangkat:** `cct_s_v2_global` milik fast-plate-ocr @ 9ce7a5b (bobot `.keras` terbitan, SHA-256 dikunci). Semua
  192 tensor bobot terbitan termuat utuh lewat jalur perintah latih, dan alatnya memeriksa ini sebelum melatih.
- **Dilatih ulang** dengan bawaan pembuatnya: laju belajar 0,001, angkatan 64, EMA, berhenti dini sesudah 100 zaman tanpa
  kemajuan. Benih 0. Keras 3.15.1 di atas torch, di image lab tambahan tanpa jaringan.
- **Tanda mesin** menurut `tools/periksa-jualan.mjs`: **`RISET-SAJA`**, karena bobot awalnya bervonis `BELUM-JELAS`.
  Tanda ini soal asal bahan, bukan soal mutu.

## 2. Latihan

| Hal | Angka |
|---|---|
| Bahan inti | 2.521 plat, 3.954 gambar (sama dengan mesin-baca-1) |
| Validasi (memilih mesin; per plat, dari bahan latih) | 303 plat, 460 gambar (sama dengan mesin-baca-1) |
| Zaman | berhenti dini di zaman 131 dari 150; **terbaik zaman 31** |
| `val_plate_acc` (ukuran fast-plate-ocr) | zaman 1: 0,678 · zaman 10: 0,800 · zaman 20: 0,824 · **zaman 31: 0,851** · zaman 81: 0,841 · zaman 131: 0,826 |
| Rugi validasi | zaman 1: 0,466 · zaman 31: 0,194 · zaman 131: 0,206 |
| **Validasi benar, pembaca yang sama** | **bobot terbitan 301 dari 460 gambar (65,4%) → fpo-indo-1 388 dari 460 (84,3%)** |
| Gambar tak terbaca | 0 |
| Lama latihan | 174,6 menit (76–81 detik per zaman), RTX 4060 laptop |

**Bacaan agen:** sebagian besar kenaikan sudah terjadi dalam 30 zaman pertama. Sesudah zaman 31, rugi latihan terus turun,
tetapi validasi berhenti naik dan rugi validasinya sedikit naik. Mesinnya mulai menghafal, dan pemilihan dengan validasi
mengambil zaman 31.

## 3. Angka pada set uji (dinilai sekali)

Kedatangan benar, dengan rentang 95%. Cara hitung yang adil adalah **911 plat tanpa label pilihan pembaca** (laporan
Rencana 6 bagian 6). Angka tiga pembaca lain sama persis dengan Rencana 8.

| Kelompok | **fpo-indo-1** | fast-plate-ocr terbitan | Qwen3-VL | mesin-baca-1 |
|---|---|---|---|---|
| mobil-terang | **496/625 (79,4%; 76,0–82,3%)** | 388/625 (62,1%; 58,2–65,8%) | 413/625 (66,1%; 62,3–69,7%) | 200/625 (32,0%; 28,5–35,8%) |
| mobil-gelap | **49/57 (86,0%; 74,7–92,7%)** | 45/57 (78,9%; 66,7–87,5%) | 39/57 (68,4%; 55,5–79,0%) | 15/57 (26,3%; 16,6–39,0%) |
| motor-terang | **166/208 (79,8%; 73,8–84,7%)** | 126/208 (60,6%; 53,8–67,0%) | 135/208 (64,9%; 58,2–71,1%) | 55/208 (26,4%; 20,9–32,8%) |
| motor-gelap | 17/21, terlalu sedikit | 14/21, terlalu sedikit | 15/21, terlalu sedikit | 5/21, terlalu sedikit |

Pada seluruh set uji (937 plat) angkanya hampir sama: 506/638 (79,3%), 51/59 (86,4%), 173/219 (79,0%), 17/21. Rincian
fpo-indo-1 pada 937 plat: ragu 18 / 1 / 4 / 0; gambar benar 892 dari 1.094, 57 dari 66, 190 dari 239, 19 dari 23; bacaan di
luar pola plat 0 / 0 / 1 / 0.

**Kecepatan:** 0,044 detik per gambar dengan Keras di kartu grafis, TF32 mati, satu gambar per panggilan. Angka ini bukan
kecepatan server: ekspor ONNX belum jalan (bagian 4), dan menyajikan di server diukur di Rencana 11.

**Artinya (bacaan agen):**

- Pada dua kelompok yang cukup besar, **mobil-terang dan motor-terang, fpo-indo-1 jelas lebih baik daripada ketiga pembaca
  lain**: sekitar 79–80% dibanding 61–66%. Rentang 95%-nya tidak bersentuhan.
- Pada **mobil-gelap**, angkanya lebih tinggi (86%), tetapi rentangnya masih bertumpuk dengan fast-plate-ocr terbitan.
  Kenaikannya belum terbukti untuk kelompok kecil ini.
- Melatih ulang menutup jarak yang tidak bisa ditutup mesin dari nol (Rencana 8: 26–32%), dengan bahan latih yang sama.
- Sekitar 1 dari 5 kedatangan masih salah dibaca. Sebagian bisa jadi label yang salah: set uji ditaksir masih memuat
  sekitar 3% label salah.

## 4. Batas, apa adanya

- **Keuntungan tuan rumah.** fpo-indo-1 dilatih dengan plat dari dataset yang sama dengan set uji (INDO-ALPR, sumber dan
  kamera yang mirip), sedangkan Qwen3-VL dan fast-plate-ocr terbitan belum pernah melihatnya. Sebagian kenaikan bisa
  datang dari situ. Seberapa baik ia membaca di kamera gerbang sungguhan belum diketahui (K9).
- **Potongan plat, bukan foto utuh.** Langkah mencari plat di foto utuh belum diukur.
- **Satu kali latihan, satu benih, pengaturan bawaan.** Tidak ada penyetelan; seberapa jauh hasilnya berubah dengan benih
  lain belum diketahui.
- **Label:** set uji masih memuat label salah sekitar 3% (taksiran, Rencana 6).
- **Ekspor ONNX belum jalan** di Keras + torch ("ONNX export of convolution for kernel of unknown shape"). Penilaian memakai
  Keras langsung, dan uji membuktikan pembaca Keras membaca sama dengan pembaca ONNX terbitan pada bobot terbitan. Cara
  menjalankan mesin ini di server ada di Rencana 11.
- **Izin:** bobot awal belum berizin tertulis. Pesan izin disetujui owner dan akan dikirim owner (K27).

## 5. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 107; lab 152 → 160 → 161; uji image tambahan 5 → 6 → 9. Tiap uji baru terlihat merah dulu.
- **Image lab tambahan dibangun ulang** dengan `NO_ALBUMENTATIONS_UPDATE=1`, karena albumentations mencoba ke pypi.org setiap
  kali dimuat. Sebelum kuncinya diperbarui, pintu lab terbukti menolak image baru (kode 6).
- **Taksiran lama latihan meleset sekitar 3,5 kali** (174,6 menit, bukan sekitar 50 menit). Pada plat buatan, satu zaman
  kira-kira 20 detik; pada bahan sungguhan 76–81 detik. Dugaan sebabnya belum diukur:
  1. TF32 dimatikan di alat ini, sedangkan pengukuran awal memakai TF32.
  2. Gambar asli berformat JPEG dan lebih besar.
  3. Variasi gambar dikerjakan CPU dengan satu pekerja.

  Ini penting bila latihan diulang.
- **`val_plate_acc` fast-plate-ocr (85,1%) sedikit berbeda dari pembaca kita (84,3%)**, selisih sekitar 3 dari 460 gambar.
  Dugaan sebabnya: cara membaca gambar saat latihan berbeda dengan saat inferensi. Angka di laporan ini memakai pembaca yang
  terbukti sama dengan pembaca ONNX terbitan.
- **Satu angka sempat dicurigai.** Pada uji rantai dengan plat buatan, bobot terbitan membaca benar 0 dari 4 gambar.
  Diperiksa: model membaca angka 0 sebagai huruf O pada huruf buatan komputer (ONNX dan Keras sama), dan penghitungnya
  memberi 3 dari 3 bila labelnya diisi bacaan model sendiri.

## 6. Berikutnya

Yang tersisa di Fase 0A:
- menyajikan mesin di server dan kecepatannya (K25), termasuk jalan keluar untuk ekspor;
- mencari plat di foto utuh dan video (langkah 1);
- plat buatan komputer;
- laporan Fase 0A untuk keputusan owner.

Perbaikan fpo-indo-1 (benih lain, penyetelan, bahan tambahan) hanya diputuskan dari validasi bahan latih, supaya set uji
tidak ikut "terhafal".
