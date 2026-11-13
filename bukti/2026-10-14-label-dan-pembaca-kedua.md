# Pembaca kedua dan pembetulan label set uji (K22, K23)

> Rencana 6 Fase 0A, dijalankan 14 Okt 2026 atas lampu hijau owner ("a").
> **Angka sementara dari bahan luar. Bukan angka produk dan bukan bukti K9.**
> Sumber angka: [`2026-10-14-baca-fpo-pertama.json`](2026-10-14-baca-fpo-pertama.json),
> [`2026-10-14-label-curiga.json`](2026-10-14-label-curiga.json), dan
> [`2026-10-14-set-uji-koreksi.json`](2026-10-14-set-uji-koreksi.json) di folder ini. Isinya hitungan saja. Sebelum
> disalin ke sini, ketiganya diperiksa tidak memuat satu pun dari 9.718 teks plat dan nama berkas. Pemeriksanya diuji dulu
> pada berkas yang memang berisi plat, dan menemukan 9.699 di antaranya. Angka "sebelum" dibaca dari
> [`2026-10-14-baca-vlm-pertama.json`](2026-10-14-baca-vlm-pertama.json) dan pesan commit Task 3.

## 1. Apa yang dikerjakan

Laporan Rencana 5 ([`2026-10-14-baca-huruf-pertama.md`](2026-10-14-baca-huruf-pertama.md)) menemukan kira-kira 1 dari 10
label penerbit salah. Owner memilih membetulkannya dengan memeriksa yang dicurigai saja (K22). Caranya:

1. Pembaca kedua, fast-plate-ocr (paket jadi), membaca set uji yang sama dengan Qwen3-VL-2B.
2. Plat yang dibaca **sama** oleh kedua pembaca tetapi **berbeda** dari labelnya masuk lembar untuk owner. Lembarnya
   memuat tulisan A (label) dan B (bacaan kedua pembaca), jadi owner cukup menyebut nomor baris.
3. Jawaban owner membetulkan label, lalu kedua pembaca dinilai ulang dari bacaan yang sudah tersimpan.

## 2. Pembaca kedua

- **Model:** fast-plate-ocr @ `9ce7a5b` (klon terkunci), model `cct-s-v2-global`. Konfigurasinya mencantumkan Indonesia,
  dan mode warnanya `rgb`.
- **Bobot:** dua berkas dari rilis GitHub, diambil lewat pintu unduh berkas: 5.262.230 byte dan 1.725 byte. Keduanya cocok
  dengan SHA-256 yang diterbitkan GitHub, dan diperiksa lagi sebelum dimuat. Jalur unduh otomatis bawaan fast-plate-ocr
  tidak dipakai.
- **Izin:** kodenya MIT, bobotnya `BELUM-JELAS`. Jadi ia alat lab, bukan bagian produk.
- **Uji model sungguhan:** plat buatan "B 1234 XYZ" terbaca `B1234XYZ`.
- **Kecepatan:** 0,011 detik per gambar di CPU laptop. Qwen3-VL butuh 0,277 detik per gambar di kartu grafis. Keduanya
  bukan taksiran untuk kotak murah (B5).

## 3. Label yang dicurigai

- **31 dari 945 kedatangan dicurigai:** mobil-terang 17 dari 642, mobil-gelap 2 dari 60, motor-terang 12 dari 221,
  motor-gelap 0 dari 22.
- **Cara ini diuji pada 60 contoh yang sudah diperiksa owner:** dari 6 label yang diketahui salah, 3 tertangkap; dari 54
  label yang diketahui benar, 0 ikut dicurigai.
- **Jawaban owner atas 31 baris:** tulisan B benar pada 29 baris. Baris 7 dan 12 salah, tulisan A maupun B. Owner
  menuliskan tulisan yang benar untuk kedua baris itu di percakapan, tetapi nomor plat dari percakapan tidak disalin ke
  berkas mana pun (`CLAUDE.md` §4), jadi kedua plat dikeluarkan. Dengan begitu, paling sedikit 29 dari 31 yang dicurigai
  memang label salah; pada 54 contoh owner yang labelnya benar, cara ini tidak pernah menuduh.

## 4. Set uji sesudah dibetulkan

| | Kedatangan |
|---|---|
| Set uji semula | 945 |
| Label dibetulkan (tulisan B) | 29 |
| Dikeluarkan: kedua tulisan salah (baris 7, 12) | 2 |
| Dikeluarkan: label salah dari lembar contoh yang tidak tertangkap | 3 |
| Dikeluarkan: label baru ternyata plat di bahan latih (K23) | 3 |
| **Set uji sekarang** | **937** (mobil-terang 638, mobil-gelap 59, motor-terang 219, motor-gelap 21) |
| Plat di kedua sisi | 0 |

**Tentang K23.** Tiga label yang dibetulkan ternyata sama dengan plat yang ada di bahan latih. Dugaannya: kendaraan yang
sama yang salah dilabeli penerbit, sehingga pembagian per plat menaruhnya di dua sisi. Jadi kesalahan label bisa
menyembunyikan kebocoran. Rencana berhenti dan melapor; owner memilih mengeluarkan ketiganya dari set uji (K23), sesuai
spec 8.3: satu plat hanya di satu sisi.

## 5. Kedua pembaca, sebelum dan sesudah label dibetulkan

Kedatangan benar, dengan rentang 95%. "Sebelum" = terhadap label penerbit pada 945 kedatangan. "Sesudah" = terhadap label
yang sudah dibetulkan pada 937 kedatangan.

| Kelompok | Qwen3-VL sebelum | Qwen3-VL sesudah | fast-plate-ocr sebelum | fast-plate-ocr sesudah |
|---|---|---|---|---|
| mobil-terang | 414/642 (64,5%; 60,7–68,1%) | 424/638 (66,5%; 62,7–70,0%) | 390/642 (60,7%; 56,9–64,5%) | 399/638 (62,5%; 58,7–66,2%) |
| mobil-gelap | 39/60 (65,0%; 52,4–75,8%) | 41/59 (69,5%; 56,9–79,7%) | 45/60 (75,0%; 62,8–84,2%) | 47/59 (79,7%; 67,7–88,0%) |
| motor-terang | 135/221 (61,1%; 54,5–67,3%) | 146/219 (66,7%; 60,2–72,6%) | 126/221 (57,0%; 50,4–63,4%) | 137/219 (62,6%; 56,0–68,7%) |
| motor-gelap | 15/22, terlalu sedikit | 15/21, terlalu sedikit | 14/22, terlalu sedikit | 14/21, terlalu sedikit |

**Artinya (bacaan agen):**

- Kedua pembaca membaca benar kira-kira dua dari tiga plat. Itu jauh dari sasaran 99% (K9), dan keduanya pembanding,
  bukan mesin yang akan dijual.
- Kedua pembaca **tidak bisa disebut berbeda** satu sama lain, karena rentangnya saling menutupi di tiap kelompok.
  fast-plate-ocr sekitar 25 kali lebih cepat, dan itu tanpa kartu grafis.
- Kenaikan sesudah label dibetulkan (2–6 poin) sebagian **dibuat oleh caranya sendiri**: 29 label dibetulkan justru karena
  kedua pembaca sepakat, jadi pada plat-plat itu keduanya pasti dinilai benar. Lihat batas di bagian 6.

## 6. Batas, apa adanya

- **Label salah masih tersisa.** Pada contoh owner, cara ini menangkap 3 dari 6 label salah. Taksiran kasar: bila yang
  tertangkap (29 sampai 31) kira-kira separuh dari seluruh label salah, sekitar 30 label salah (sekitar 3%) mungkin masih
  ada di set uji. Taksiran ini bersandar pada 6 contoh saja.
- **Angka "sesudah" memihak dua pembaca ini.** Pada 26 plat yang dibetulkan dan tetap di set uji, label baru dipilih dari
  bacaan yang disepakati keduanya. Pembaca ketiga (misalnya mesin buatan sendiri di Rencana 7) tidak mendapat keuntungan
  itu. Perbandingan yang adil dengan pembaca ketiga perlu memisahkan plat-plat itu, atau memeriksanya dengan cara lain.
- **Label bahan latih belum diperiksa.** Kebocoran serupa K23, yang tersembunyi oleh label salah di sisi latih, belum
  bisa dihitung.
- **Baris 7 dan 12:** owner menyebut keduanya salah dan menuliskan tulisan yang benar. Apakah tulisan owner sama dengan
  label penerbit tidak diperiksa, karena nomor plat dari percakapan tidak disalin ke berkas. Kedua plat dikeluarkan,
  bukan dibetulkan.
- **Baris yang tidak disebut owner** di lembar curiga dibaca agen sebagai "tulisan B benar", sesuai kata owner ("yang
  lainnya warna hijau (B) sudah benar semua").
- Tetap berlaku dari Rencana 5: potongan plat, bukan kamera gerbang (K9 tidak terbukti dari sini); terang-gelap adalah
  taksiran, bukan siang-malam; mobil-motor dibaca dari nomor urut; satu pertanyaan saja yang dicoba pada Qwen3-VL; satu
  model saja yang dicoba pada fast-plate-ocr; motor-gelap terlalu sedikit.

## 7. Catatan pelaksanaan

- **Gerbang uji:** Node 99 → 101; lab 100 → 106 → 111 → 116 → 119 → 127 → 128. Tiap uji baru terlihat merah dulu karena
  fiturnya belum ada. Satu uji lebih banyak dari rencana (127 → 128), untuk aturan K23. Uji daftar host pintu unduh diubah
  dengan sadar, tidak dihapus.
- **`ringkas()` dipisah dari `nilai()`** di `baca_vlm.py` tanpa mengubah perilaku. Uji lama tetap hijau, dan pada data
  sungguhan ringkasan yang dihitung ulang dari bacaan tersimpan sama persis dengan ringkasan lama untuk kedua pembaca.
- **Dua uji model sungguhan** di `tools/lab/uji_gpu/` (di luar gerbang) lulus.

Mengulang (PowerShell, dari akar repo; nomor baris sesuai jawaban owner 14 Okt):

```
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/baca_fpo.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/unduhan /kerja/data/keluaran/baca-fpo
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/label_curiga.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/baca-vlm/hasil.jsonl /kerja/data/keluaran/baca-fpo/hasil.jsonl /kerja/data/keluaran/label-curiga --periksa /kerja/data/keluaran/lembar-contoh/lembar-contoh.json --salah 19,22,25,35,36,54
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/lembar_curiga.py /kerja/data/keluaran/label-curiga/curiga.json /kerja/data/keluaran/dataset/indo-alpr/original /kerja/data/keluaran/lembar-curiga
powershell -NoProfile -File tools\lab.ps1 python /kerja/tools/lab/nilai_ulang.py /kerja/data/keluaran/set-uji-baca/pembagian.json /kerja/data/keluaran/lembar-curiga/lembar-curiga.json /kerja/data/keluaran/lembar-contoh/lembar-contoh.json /kerja/data/keluaran/set-uji-koreksi --b-benar 1,2,3,4,5,6,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31 --keduanya-salah 7,12 --salah-contoh 19,22,25,35,36,54 --hasil qwen3-vl=/kerja/data/keluaran/baca-vlm/hasil.jsonl --hasil fast-plate-ocr=/kerja/data/keluaran/baca-fpo/hasil.jsonl
```

## 8. Berikutnya

Rencana 7 ditulis: mesin belajar pertama untuk baca huruf (dilatih dengan bahan latih, dinilai pada set uji yang sudah
dibetulkan ini, dengan memperhatikan batas "memihak" di bagian 6), mencari plat di foto utuh dan video, plat buatan
komputer, taksiran kecepatan, dan laporan Fase 0A. Dipecah lagi bila terlalu besar.
