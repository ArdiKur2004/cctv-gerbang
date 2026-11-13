# Merek mobil: dugaan resolusi diuji, dan tidak didukung (Rencana 35, 26 Okt 2026)

> Hitungan saja. Potongan, gambar, dan nama berkas tidak ada di repo (`CLAUDE.md` §4). Angka dibaca dari layar alat dan dari
> `bukti/2026-10-26-merek-mobil-resolusi.json` (dibuat `data/alat-sementara/gabung-bukti-35.mjs`; rentang Wilson 95% dihitung di skrip)
> dan `-pilih.json`.

## Yang diuji

Rencana ini menguji **satu dugaan**, bukan membangun fitur. Di Rencana 34 pengenal merek menjawab "tak yakin" untuk semua 13 potongan
mobil uji. Dugaan pertama ("logo mobil terlalu kecil di CCTV") sudah terbukti salah: potongan mobil owner lebarnya 159/514/1.185 piksel.
Dugaan kedua, yang diuji di sini: **masukan pengenal hanya 96 × 96 piksel**, jadi mobil selebar 514 piksel diperkecil sekitar lima kali
dan logonya hilang.

Tiga pengenal dilatih khusus mobil, dengan masukan 96 (kendali), 192, dan 256 piksel. C96 ada supaya pengaruh "mobil saja" terpisah dari
pengaruh "masukan lebih besar".

## Vonis: dugaan TIDAK didukung

Aturannya ditulis di rencana sebelum angka dilihat: dugaan didukung hanya bila nilai terbaik C192 atau C256 **lebih besar** dari C96.

| Calon | Masukan | Nilai terbaik di validasi owner mobil (17 potongan) | Zaman terbaik | Menit |
|---|---|---|---|---|
| B0 (selalu "Toyota") | — | −5 | — | — |
| **C96 (kendali)** | 96 | **+1** | 18 dari 30 | 1,7 |
| C192 | 192 | 0 | **1 dari 30** | 4,6 |
| C256 | 256 | 0 | **1 dari 30** | 8,1 |

Masukan lebih besar **tidak** menolong. Jadi vonisnya: **tidak didukung**.

Dua tanda bahwa percobaan ini lemah dayanya, dan keduanya penting dibaca bersama vonisnya:
- C192 dan C256 memilih **zaman 1 dari 30**, artinya angka validasinya tidak pernah membaik sesudah zaman pertama;
- nilai terbaik C96 hanya **+1 dari 17 potongan** — praktis tidak ada bedanya dengan nol.

## Diukur sekali di uji (13 potongan mobil owner)

| Calon | Ambang | Benar | Salah | Tak yakin | Nilai |
|---|---|---|---|---|---|
| B0 (selalu "Toyota") | — | 4 (0,13–0,58) | 9 | 0 | −5 |
| **C96 terpilih** | 0,7 | **0** (0–0,23) | 1 | 12 | −1 |
| C192 | 0 | 4 | 9 | 0 | −5 |
| C256 | 0 | 4 | 9 | 0 | −5 |
| M1 lama (semua jenis, 96) | 0 | 1 | 12 | 0 | −11 |

Per kelas, C96: Daihatsu 0 dari 4 (semua tak yakin), Toyota 0 dari 4 (semua tak yakin), Honda 0 dari 3 (1 salah), Suzuki dan "lainnya"
masing-masing 1, keduanya tak yakin.

**Pengenal terpilih benar nol kali dari 13.** Nilai +1 di validasi menjadi −1 di uji. Tidak ada satu pun calon yang mengalahkan tebakan
tetap "selalu Toyota" dalam hal benar, dan tebakan tetap itu sendiri nilainya −5 karena salahnya 9.

## Apa yang sebenarnya sudah terbukti, dan apa yang belum

**Terbukti:** mengenali merek mobil dari **potongan kendaraan utuh** tidak bekerja dengan bahan yang ada sekarang, pada ketiga ukuran
masukan yang dicoba. Dua dugaan agen berturut-turut (logo terlalu kecil; masukan terlalu kecil) **keduanya tidak terbukti**.

**Belum terbukti, dan jangan diklaim:** bahwa resolusi pasti bukan penyebabnya. Validasi hanya 17 potongan dan uji 13, jadi daya
percobaan ini rendah. Yang jujur dikatakan adalah "tidak ada tanda bahwa menaikkan resolusi menolong", bukan "resolusi sudah pasti bukan
masalahnya".

**Dugaan ketiga, belum diuji:** bahannya yang tidak cocok. Dari 3.309 potongan mobil latih, hanya **35** berasal dari tangkapan owner;
3.274 sisanya dari dataset brand yang bingkainya 1920×1080, bukan CCTV. Mesin kemungkinan belajar dunia dataset itu, dan dunia itu
berbeda dengan gerbang.

## Usulan langkah berikutnya (keputusan owner)

1. **Berhenti memperbaiki merek mobil dengan bahan yang ada.** Dua percobaan sudah gagal, dan bahan mobil nyata kita hanya 35 potongan
   latih.
2. **Pasang dulu ciri yang sudah bekerja ke rantai** (jenis untuk semua kendaraan; warna dan merek untuk motor). Itu memberi catatan ciri
   per kedatangan, dan memberi angka dari ujung ke ujung dengan kotak dari pencari, bukan kotak yang owner periksa.
3. **Merek mobil menunggu bahan nyata**, yaitu rekaman HP owner (K43) yang memang sudah ditunggu. Sesudah itu, pencari logo baru layak
   dicoba, dengan catatan dataset logo hanya punya 8 contoh Honda, 1 Nissan, 1 Mazda, dan nol Isuzu.

## Batas

- Validasi owner mobil 17 potongan, uji 13. Dari 16 pasangan calon × ambang yang dinilai pada 17 potongan, calon terbaik hampir pasti
  terlihat lebih baik daripada kenyataannya; terbukti di sini (+1 menjadi −1).
- Merek mobil owner sangat sedikit: sisi latih Toyota 14, Daihatsu 6, Suzuki 4, Honda 3, Mitsubishi 3, sisanya 1.
- Kecepatan tidak diukur; yang tercatat hanya lama latihan (1,7 · 4,6 · 8,1 menit), dan itu bukan kecepatan saat dipakai.
- Ketiga mesin tersimpan dan **tidak dipasang di rantai**.
