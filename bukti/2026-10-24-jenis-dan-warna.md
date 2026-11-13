# Pengenal jenis dan warna kendaraan (Rencana 33, Fase 3, 24 Okt 2026)

> Hitungan saja. Potongan, gambar, dan nama berkas tidak ada di repo (`CLAUDE.md` §4). Angka dibaca dari layar alat dan dari
> `bukti/2026-10-24-jenis-dan-warna.json` (dibuat `data/alat-sementara/gabung-bukti-33.mjs`; rentang Wilson 95% dihitung di skrip) dan
> `-pilih.json`.
>
> **Ukuran:** menurut spec Fase 3, ciri **salah** berarti satpam dipanggil untuk kendaraan yang sah (peringatan palsu), dan "tak yakin"
> tidak memanggil siapa pun. Jadi tiap calon dinilai dengan **nilai = benar − salah**, bukan benar saja.

## Ringkasan

- **Jenis bisa dipakai.** Pengenal J1 membaca benar **32 dari 37** potongan uji (72–94%), salah 5 (6–28%). Mobil 12 dari 14, motor 20 dari
  21. Pikap dan truk masing-masing 1 potongan dan keduanya salah: terlalu sedikit untuk disimpulkan, tetapi belum ada tanda ia bisa.
- **Warna belum layak memicu peringatan.** W1 benar **16 dari 37** (29–59%), salah 6, dan menjawab "tak yakin" 15 kali. Warna abu-abu atau
  perak **0 benar dari 5**. Hitam 10 dari 16, putih 4 dari 8, merah 2 dari 2.
- **Aturan warna buatan tangan (W0) gagal:** di uji salah 21 dan benar 16, jadi nilainya **−5**. Ia tidak pernah bisa menyatakan ragu.
  Dibuang; yang dipakai mesin W1 dengan ambang.
- **Ambang jenis tidak berpindah dengan baik.** Di validasi, J1 pada ambang 0 hanya salah 1 dari 33, jadi aturan memilih ambang 0. Di uji
  salahnya 5 dari 37. Jadi angka "peringatan palsu" yang jujur adalah angka uji, bukan validasi.
- Kedua mesin terpilih bertanda `BOLEH-PRODUK` (`tools/periksa-jualan.mjs`), ONNX sama dengan torch (40 dari 40 gambar).
- **Belum dipasang di rantai.** Rencana 33 hanya membuat dan mengukur pengenalnya. Pemasangan ke rantai dan pembandingan dengan data
  pendaftaran ada di Rencana 35.

## Bahan: potongan kendaraan berlabel

| Sumber | Potongan | Sisi latih | Validasi | Uji | Catatan |
|---|---|---|---|---|---|
| Label owner | 172 | 102 | 33 | 37 | 8 kartu yang owner tandai "kotak tidak pas" dibuang; 2 warna dijawab "tak yakin" dan tidak menjadi label |
| Roboflow vehicle and license plate | 3.033 | 2.732 | 301 | — | jenis saja (mobil 1.700, motor 1.144, truk 189); 4.067 kotak plat dilewati; 2.938 dibatasi |
| Roboflow Merk dan Warna Motor | 3.084 | 2.638 | 446 | — | jenis motor dan warna; 208 kotak kelas "Biru-Putih" dibuang (dua warna); 4.951 dibatasi |

Warna di label owner: hitam 69, putih 38, merah 28, abu_perak 15, biru 8, lainnya 6, hijau 4, kuning 2. Coklat atau krem: **nol**.
Kotak di bawah 24 piksel akan dilewati; di bahan ini tidak ada.

## Memilih (aturan di rencana sebelum angka; pilihan di-commit `17bdf15` sebelum uji dibuka)

Validasi owner, 33 potongan:

| Ciri | Calon | Ambang | Benar | Salah | Tak yakin | Nilai |
|---|---|---|---|---|---|---|
| Jenis | J0 pencari COCO (tanpa latihan) | 0 | 25 | 4 | 4 | 21 |
| Jenis | **J1** (Roboflow + owner) | **0** | 32 | 1 | 0 | **31** |
| Jenis | J2 (owner saja) | 0 | 30 | 3 | 0 | 27 |
| Warna | W0 aturan piksel (tanpa latihan) | — | 15 | 18 | 0 | −3 |
| Warna | **W1** (Merk dan Warna Motor + owner) | **0,7** | 12 | 3 | 18 | **9** |
| Warna | W2 (owner saja) | 0,7 | 9 | 2 | 22 | 7 |

W1 seri di ambang 0 dan 0,7 (nilai 9); serinya dipecah "salah paling sedikit", jadi 0,7. Penjaga terpenuhi: keduanya mengalahkan calon
tanpa latihan. Menambah bahan Roboflow menolong keduanya (J1 > J2, W1 > W2).

Pelatihan: J1 3,3 menit (zaman terbaik 6 dari 30), J2 0,2 menit (zaman 22), W1 1,6 menit (zaman 25), W2 0,2 menit (zaman 30).

## Diukur sekali di uji (37 potongan owner)

| Ciri | Calon | Ambang | Benar | Salah | Tak yakin | Nilai |
|---|---|---|---|---|---|---|
| Jenis | J0 (pembanding) | 0 | 25 (0,52–0,81) | 2 | 10 | 23 |
| Jenis | **J1 terpilih** | 0 | **32** (0,72–0,94) | **5** (0,06–0,28) | 0 | **27** |
| Jenis | J2 (pembanding) | 0 | 30 | 7 | 0 | 23 |
| Warna | W0 (pembanding) | — | 16 | 21 | 0 | −5 |
| Warna | **W1 terpilih** | 0,7 | **16** (0,29–0,59) | **6** (0,08–0,31) | 15 | **10** |
| Warna | W2 (pembanding) | 0 | 22 | 15 | 0 | 7 |

Per kelas sebenarnya, pengenal terpilih:

| Jenis (J1) | Jumlah | Benar | Salah | | Warna (W1) | Jumlah | Benar | Salah | Tak yakin |
|---|---|---|---|---|---|---|---|---|---|
| mobil | 14 | 12 | 2 | | hitam | 16 | 10 | 2 | 4 |
| motor | 21 | 20 | 1 | | putih | 8 | 4 | 0 | 4 |
| pikap | 1 | 0 | 1 | | abu_perak | 5 | 0 | 3 | 2 |
| truk | 1 | 0 | 1 | | merah | 2 | 2 | 0 | 0 |
| | | | | | lainnya | 3 | 0 | 1 | 2 |
| | | | | | biru, hijau, kuning | 1 tiap kelas | 0 | 0 | 1 tiap kelas |

Catatan: W2 benar lebih banyak (22) tetapi salah jauh lebih banyak (15), jadi nilainya lebih rendah. Itulah gunanya ukuran benar − salah:
pengenal yang berani tetapi sering salah memanggil satpam lebih sering.

## Keputusan yang perlu owner (bisa dibalik)

1. **Jenis:** siap dicatat per kedatangan. Bila dibandingkan dengan data pendaftaran sekarang juga, sekitar **5 dari 37 kendaraan sah akan
   memicu peringatan palsu**. Pilihan: (a) catat saja dulu, tanpa peringatan; (b) peringatan menyala, dengan ambang baru yang dipilih di
   validasi yang lebih besar.
2. **Warna:** saran agen, **hanya dicatat, belum memicu peringatan**. Abu-abu atau perak nol benar dari 5, dan separuh potongan dijawab
   "tak yakin".
3. Keduanya dibalik dengan tidak memasang pengenal di rantai, atau menaikkan ambangnya; tidak ada kode yang perlu diubah.

## Batas

- Uji hanya 37 potongan, dan beberapa kelas hanya 1–3 potongan: angkanya tidak bisa disimpulkan per kelas kecil.
- Validasi owner (33) dipakai untuk memilih zaman **dan** memilih calon, jadi angka validasinya terlalu baik. Terbukti di sini: salah J1
  naik dari 1 (validasi) ke 5 (uji).
- Potongan berlabel jenis condong ke motor: dari seluruh sisi, motor 4.329, mobil 1.766, truk 191, pikap 3, bus 0.
- Warna biru, hijau, kuning, dan "lainnya" hampir tidak ada di bahan latih, dan coklat atau krem **tidak ada sama sekali**.
- Tidak ada gambar inframerah di label owner, jadi saringan "tak yakin" untuk inframerah (K52) hanya diuji dengan gambar buatan.
- Potongan berasal dari kotak kendaraan yang owner periksa, bukan dari rekaman gerbang.
- Mesin J2 dan W2 mencatat bahan dari seluruh dataset potongan, padahal keduanya hanya dilatih dengan potongan owner. Arahnya aman (bahan
  berlebih, bukan kurang), keduanya tidak dipakai, dan temuannya dicatat di `ROADMAP.md`.
