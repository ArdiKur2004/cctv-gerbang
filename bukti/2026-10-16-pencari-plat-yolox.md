# Pencari plat buatan sendiri: empat calon YOLOX dilatih, dinilai, dan diukur

> Rencana 13 Fase 0A, dijalankan 16 Okt 2026 atas lampu hijau owner ("A"), termasuk mengukur di Mini PC.
> **Keempat mesin bertanda `RISET-SAJA`**, karena izin bobot awal COCO YOLOX tidak dinyatakan (`BELUM-JELAS`). Angka dari satu
> dataset, bukan angka produk dan bukan bukti K9.
> Sumber angka: tujuh belas berkas `2026-10-16-pencari-yolox-*.json` dan `2026-10-16-cepat-yolox-640-minipc.json` di folder ini.
> Isinya hitungan saja. Sebelum disalin, semuanya diperiksa tidak memuat satu pun dari 10.300 teks plat dan nama berkas.
> Pemeriksanya diuji dulu pada daftar nama berkas plat-lighting, dan menemukan 561 dari 561.

## 1. Yang dilatih

YOLOX @ 4197784 (kode Apache-2.0), dua ukuran model (Nano dan Tiny) kali dua ukuran masukan (416 dan 640 piksel), satu kelas
"plat". Bahan: plat-lighting (CC BY 4.0), sisi latih 393 foto. Bobot awal COCO dari rilis YOLOX, dimuat hanya dengan
`torch.load(weights_only=True)` sesudah SHA-256-nya dicocokkan dengan kunci. 100 zaman per calon; zaman terbaik dan ambang
keyakinan dipilih dengan F1 di sisi validasi (84 foto, 99 plat). Sisi uji tidak dibaca saat melatih.

| Calon | Bobot awal dimuat / dilewati | Zaman terbaik | F1 validasi | Plat ditemukan di validasi | Lama latihan |
|---|---|---|---|---|---|
| Nano-416 | 636 / 6 | 67 | 0,859 | 85 dari 99, kotak palsu 14 | 30,5 menit |
| **Nano-640** | 636 / 6 | 52 | 0,917 | **94 dari 99**, kotak palsu 12 | 36,3 menit |
| Tiny-416 | 456 / 6 | 80 | 0,901 | 91 dari 99, kotak palsu 12 | 32,3 menit |
| Tiny-640 | 456 / 6 | 74 | **0,925** | 92 dari 99, kotak palsu 8 | 48,7 menit |

Yang dilewati hanya kepala kelas COCO (80 kelas) di tiga tingkat, bobot dan bias: 6 tensor. Bobot hasil latih disimpan sebagai
safetensors (bukan pickle), dengan SHA-256 di `mesin.json`.

## 2. Hasil di set uji (dibaca sekali per calon)

84 foto, 102 plat. Plat dihitung ditemukan bila IoU-nya minimal 0,5. Dinilai lewat ONNX (`PencariYolox`), jalur yang sama
dengan yang kelak jalan di server.

| Kelompok | Nano-416 | Nano-640 | Tiny-416 | Tiny-640 | Pembanding (Rencana 12) |
|---|---|---|---|---|---|
| Semua | 91 (82–94%) | **96 (88–97%)** | 94 (85–96%) | **96 (88–97%)** | 31 (22–40%) |
| Terang (99 plat) | 89 (82–94%) | 93 (87–97%) | 91 (85–96%) | 93 (87–97%) | 30 |
| Gelap (3 plat) | 2 | 3 | 3 | 3 | 1 |
| Kecil, tinggi < 3% foto (16 plat) | 10 | 12 | 11 | 13 | 0 |
| Besar (86 plat) | 81 (87–98%) | 84 (92–99%) | 83 (90–99%) | 83 (90–99%) | 31 |
| Kotak palsu | 14 | 14 | 10 | 10 | 51 |

Angka dalam kurung adalah rentang 95%. Kelompok gelap dan kecil terlalu sedikit untuk rentang yang berarti.

- **Keempatnya jauh di atas pembanding siap pakai** (31 dari 102). Pembanding itu dilatih dengan bahan lain pada 384 px.
- **Ukuran masukan 640 menolong plat kecil:** 12–13 dari 16, lawan 10–11 pada 416. Ini sejalan dengan pelajaran Rencana 12.
- **Selisih antarcalon di set uji kecil** dibanding lebar rentangnya, jadi set uji tidak dipakai untuk memilih.

## 3. ONNX sama dengan torch

ONNX disimpan hanya bila deteksinya sama dengan torch pada 20 gambar validasi, **dan** keluaran mentah semua kotak, termasuk
yang di bawah ambang, sama per satuan.

| Calon | Deteksi sama | Selisih koordinat terbesar | Selisih peluang terbesar |
|---|---|---|---|
| Nano-416 | 20 dari 20 | 0,0068 piksel | 1,5e-5 |
| Nano-640 | 20 dari 20 | 0,038 piksel | 1,0e-4 |
| Tiny-416 | 20 dari 20 | 0,0024 piksel | 3,8e-6 |
| Tiny-640 | 20 dari 20 | 0,0092 piksel | 3,2e-6 |

**Penjaga yang salah satuan, dan diperbaiki:** penjaga di rencana memakai satu batas mutlak 1e-2 untuk koordinat (piksel,
sampai 640) dan peluang (0 sampai 1) sekaligus. Ia menolak Nano-640 karena selisih 0,038, padahal deteksinya sama 20 dari 20.
Diagnosis per kolom menunjukkan seluruh selisih ada di koordinat (relatif 1,4e-4, pembulatan float32), sedangkan skor objek ×
kelas hanya berbeda 2,2e-6. Penjaganya diganti: koordinat di bawah 0,5 piksel, peluang di bawah 1e-3. Untuk peluang, batas ini
**lebih ketat** daripada yang lama. Perbaikannya diuji merah dulu (commit 092cbaf).

## 4. Kecepatan

**Foto utuh di laptop** (Ryzen 7 8700F; foto validasi 1080p yang sudah ada di memori; letterbox, model, dan NMS; median tiga
putaran bergiliran):

| Calon | 1 utas | 2 utas | 4 utas |
|---|---|---|---|
| Nano-416 | 12,0 ms | 7,8 ms | 5,8 ms |
| Nano-640 | 28,1 ms | 17,4 ms | 12,3 ms |
| Tiny-416 | 53,2 ms | 29,2 ms | 18,2 ms |
| Tiny-640 | 125,1 ms | 67,4 ms | 43,0 ms |

**Model saja di Mini PC** (Celeron N5095, masukan buatan, bobot acak dengan susunan yang sama; 416 dari Rencana 12, 640 dari
rencana ini):

| Calon | 1 utas | **2 utas** | 4 utas |
|---|---|---|---|
| Nano-416 | 117 ms | **73 ms** | 138 ms |
| Nano-640 | 265 ms | **150 ms** | 90 ms |
| Tiny-416 | 471 ms | **251 ms** | 139 ms |
| Tiny-640 | 1.053 ms | **544 ms** | 310 ms |
| Pembaca huruf (fpo-indo-1) | 183 ms | **100 ms** | 70 ms |

Angka 4 utas di Mini PC tidak bisa dipegang: Mini PC menjalankan layanan lain, dan saat Rencana 12 Nano-416 dengan 4 utas malah
lebih lambat daripada dengan 2 utas. Taksiran memakai 2 utas.

**Taksiran per foto di Mini PC** (bacaan agen, 2 utas, cari plat + baca satu plat, model saja):

| Calon | Per foto | Tiga foto per kedatangan | Terhadap sasaran 2 detik (spec 2.6) |
|---|---|---|---|
| Nano-416 | sekitar 0,17 detik | sekitar 0,5 detik | banyak ruang |
| **Nano-640** | sekitar 0,25 detik | sekitar 0,75 detik | masih ada ruang untuk unggah, dekode, dan pencocokan |
| Tiny-416 | sekitar 0,35 detik | sekitar 1,05 detik | sempit |
| Tiny-640 | sekitar 0,64 detik | sekitar 1,9 detik | **hampir habis** sebelum unggah dan dekode dihitung |

Unggah foto, membuka berkas JPEG, praproses foto 1080p di Celeron, dan pencocokan dengan daftar pengguna belum diukur.

## 5. Usulan agen: Nano-640 untuk Rencana 14

Dipilih dari validasi dan kecepatan, bukan dari angka uji:
- **Di validasi, Nano-640 menemukan plat terbanyak** (94 dari 99). Untuk gerbang, plat yang terlewat berarti gerbang tidak
  terbuka (gagal-buka, K9). Kotak palsu hanya menambah satu kali baca huruf yang tidak cocok dengan daftar, dan "ragu = tidak
  membuka" tetap berlaku.
- **Di Mini PC, Nano-640 3,6 kali lebih cepat daripada Tiny-640** (150 lawan 544 ms dengan 2 utas). Tiny-640 menghabiskan hampir
  seluruh sasaran dua detik untuk tiga foto sebelum unggah dihitung.
- **Tiny-640 punya F1 validasi tertinggi** (0,925) karena kotak palsunya paling sedikit, tetapi menemukan 2 plat lebih sedikit di
  validasi. Bila kelak server pindah ke Hostinger KVM yang lebih kuat, ia bisa ditinjau lagi.

## 6. Batas, apa adanya

- **Satu dataset:** 393 foto latih, 84 validasi, 84 uji, sebagian besar bingkai video 1080p. Kelompok gelap hanya 3 plat, kecil
  16 plat. Kamera gerbang sungguhan belum pernah dilihat.
- **Satu benih** per calon. Selisih antarcalon yang kecil bisa berubah dengan benih lain.
- **Variasi latihan sederhana:** balik horizontal, skala, geser, terang-gelap. Tanpa mosaic dan tanpa variasi bawaan YOLOX
  lainnya.
- **Bobot awal `BELUM-JELAS`,** jadi keempat mesin `RISET-SAJA`. SHA-256 bobot awal dipercaya pada unduhan pertama, karena GitHub
  tidak menerbitkan digest untuk aset 2021.
- **Kecepatan Mini PC dari bobot acak dan masukan buatan**, model saja (K15: model hasil latih tidak dibawa ke sana).
- **Kecepatan laptop dari foto yang sudah di memori;** membuka berkas tidak dihitung.

## 7. Catatan pelaksanaan

- **Gerbang uji:** Node tetap 107; lab 178 → 182 → 188 → 190; uji image tambahan 14 → 17. Tiap uji baru terlihat merah dulu.
  Rencana menyebut lab berakhir di 188; dua uji tambahan berasal dari perbaikan penjaga ONNX (bagian 3).
- **Lama latihan:** keempatnya 2 jam 28 menit berturut-turut (01.29–03.57). Rencana sengaja tidak memberi taksiran, karena
  taksiran Rencana 10 meleset 3,5 kali.
- **Pengukuran kecepatan laptop diulang.** Putaran pertama jatuh bersamaan dengan uji mutasi milik sesi lain di laptop ini
  (vitest dinyalakan berulang, ditambah pemindaian Windows Defender tiap kali). Angka 2 dan 4 utas melonjak: Tiny-640 dengan 4
  utas 114 ms, lawan 43 ms saat tenang. Proses sesi lain itu tidak disentuh. Sesudah uji itu selesai, keempat calon diukur tiga
  putaran bergiliran dengan perekam proses. Satu lonjakan Defender yang tersisa hanya mengenai satu putaran Tiny-416, dan median
  membuangnya. Pelajarannya dicatat di `CLAUDE.md` §7: `docker ps` dan `nvidia-smi` saja tidak cukup untuk menyatakan mesin
  tenang.
- **Mini PC:** prosedur Rencana 12: beban 1,47 sebelum, sampai 3,28 sesudah; venv sementara dengan paket ber-hash; `nice -n 19`,
  `timeout`, `trap`; folder dihapus; tanpa sisa proses (`pgrep -af "[u]kur_onnx_cpu"`).

## 8. Berikutnya

Owner memilih pencari plat untuk rantai utuh. Sesudah itu:
- **Rencana 14:** rantai utuh di video riset (cari plat, potong, baca, gabung per kedatangan) dan kecepatannya.
- **Rencana 15:** laporan Fase 0A, termasuk keputusan soal plat buatan komputer.
