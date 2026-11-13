# Spec Fase 3 tahap 1: Ciri kendaraan, yaitu jenis, warna, dan merek (S3)

> Ditulis agen 19 Okt 2026, sesudah owner memilih pengenal ciri kendaraan dikerjakan lebih dulu sambil menunggu rekaman HP (K60).
> ✅ **Disetujui owner 19 Okt 2026 (K61).** Jawaban owner: "ya", tanpa mengubah kelas. ~~Status: menunggu persetujuan owner.~~
> **Dasar:**
> - keputusan owner K8, K21, K37, K44, K48, K52, K55, K56, K58, K60 (`SEED.md` §3);
> - spec induk [`2026-10-13-cctv-gerbang-desain-induk.md`](2026-10-13-cctv-gerbang-desain-induk.md) bagian 4 (ciri kendaraan) dan 8.3
>   (aturan ukur);
> - survei [`docs/riset/2026-10-19-catatan-merek-warna-mobil.md`](../docs/riset/2026-10-19-catatan-merek-warna-mobil.md) dan pemeriksaan
>   dataset Roboflow [`bukti/2026-10-19-dataset-roboflow.md`](../bukti/2026-10-19-dataset-roboflow.md).

## 1. Tujuan dan tolak ukur

**Tujuan (K8 tahap 1, K55):**
- tiap kedatangan dicatat bersama jenis, warna, dan merek kendaraannya;
- ciri itu dicocokkan dengan data pendaftaran plat. Bila tidak cocok, satpam diberi peringatan, dan gerbang tetap mengikuti plat;
- nama model adalah tahap 2 (spec induk 4.2), di luar spec ini.

**Kelas (usulan agen; owner boleh mengubah saat menyetujui):**

| Ciri | Mobil | Motor |
|---|---|---|
| Jenis | mobil, pikap, truk, bus (spec induk 4.1, ditambah bus) | motor |
| Warna | putih, hitam, abu-abu atau perak, merah, biru, kuning, hijau, coklat atau krem, lainnya | sama |
| Merek | Toyota, Daihatsu, Honda, Mitsubishi, Suzuki, Wuling, Hyundai, Nissan, Mazda, Isuzu, lainnya | Honda, Yamaha, Suzuki, Kawasaki, lainnya |

Tiap ciri juga boleh berjawab **"tak yakin"**. Contohnya gambar inframerah yang tidak berwarna (K52), kendaraan terpotong, atau logo yang
terlalu kecil. "Tak yakin" tidak pernah memicu peringatan.

**Yang dihitung, per kedatangan kendaraan sah:**

| Ukuran | Arti untuk satpam |
|---|---|
| Ciri benar | Tidak ada peringatan |
| Tak yakin | Tidak ada peringatan; dicatat |
| **Ciri salah** | **Peringatan palsu**: satpam dipanggil untuk kendaraan yang sah |

Untuk plat tiruan (B7), plat sebuah kendaraan dipasangkan dengan ciri kendaraan lain di set uji. Yang dihitung adalah berapa yang
memicu peringatan ("tertangkap").

**Kelompok:** mobil/motor × siang/malam, dengan aturan ukur spec induk 8.3 (jumlah dan rentang 95%; kurang dari 30 ditulis "terlalu
sedikit").

**Sasaran:** spec induk 4.4 menetapkan batas "jarang salah menuduh" dari hasil ukur. Usulan agen: angka putaran pertama dilaporkan
apa adanya, lalu owner menetapkan batas peringatan palsu per 100 kedatangan sah sebelum pembanding dinyalakan di lokasi.

**Tolak ukur:**
- tangkapan owner (181 gambar, K44), dengan pembagian latih/uji per gambar yang sama dengan plat;
- bingkai video riset sisi uji (K49);
- rekaman HP owner (K43), bila sudah ada.

Dataset Roboflow hanya dipakai melatih. Angka di soal ujinya sendiri tidak sebanding dengan kamera kita, karena banyak gambar latih dan
ujinya mirip (Rencana 28).

## 2. Bahan

| Bahan | Isi untuk ciri | Tanda |
|---|---|---|
| Roboflow brand (JMTO) | 7.339 bingkai 1920×1080, 41 kelas merek dan model, satu kotak kendaraan per gambar. Kelas model digabung ke mereknya (mis. Agya → Toyota) | `BOLEH-PRODUK` (K56) |
| Roboflow all-cars-logo | 16.920 gambar, kotak logo 63 kelas | `BOLEH-PRODUK` |
| Roboflow vehicle and license plate | 5.555 gambar, kotak mobil, motor, truk | `BOLEH-PRODUK` |
| Roboflow Merk dan Warna Motor | 8.243 kotak motor: 4 model (Honda Beat, Vario; Yamaha Aerox, NMAX) × warna | `BOLEH-PRODUK` |
| Roboflow car-type | 1.823 gambar, 4 kelas Toyota | `BOLEH-PRODUK`; datanya sedikit (owner) |
| Tangkapan owner | 181 gambar; ciri dilabeli owner (bagian 3) | `BOLEH-PRODUK` (K44) |
| Video riset | bingkai berkendaraan; ciri dilabeli owner | `BOLEH-PRODUK` (K49) |
| Mendeley VTID2, VMID (pilihan) | 5 jenis kendaraan dari CCTV gerbang kampus Thailand (apakah pikap termasuk belum diperiksa); logo 11 merek | CC BY 4.0, boleh menurut K21; diunduh lewat pintu bila dibutuhkan |

Semua dataset dari luar melewati jalur Rencana 28: kunci SHA-256, Defender dengan kontrol positif, `buka_arsip.py`, `periksa_dataset.py`,
dan lembar contoh untuk owner.

## 3. Label, tanpa agen melihat kendaraan

Kendaraan di tangkapan dan video membawa plat, jadi agen tidak membuka gambarnya (K19, `CLAUDE.md` §4).
- **Halaman ciri untuk owner** (seperti halaman pelabelan Rencana 24): satu kartu per kendaraan yang platnya berlabel. Jenis, warna,
  dan merek sudah diisi usulan mesin, dan owner hanya membetulkan yang salah dari daftar pilihan. Perkiraan: sekitar 180 kendaraan di
  tangkapan.
- Halaman itu dibuka owner di laptop dan tidak memuat apa pun dari luar.
- **Usulan mesin tidak pernah dipakai sebagai label tanpa diperiksa owner** (pelajaran Rencana 7).

## 4. Mesin

Ciri dibaca dari potongan kendaraan yang sudah ditemukan rantai (tahap kendaraan, K39).

| Ciri | Calon (dipilih di validasi, seperti Fase 1) |
|---|---|
| Jenis | **Pencari kendaraan dilatih ulang** dari YOLOX COCO dengan kelas mobil, pikap, truk, bus, motor. Bahannya: Roboflow vehicle and license plate, brand, Merk dan Warna Motor, dan kotak kendaraan tangkapan berlabel owner |
| Warna | (a) aturan warna dari piksel badan kendaraan, tanpa latihan; (b) pengklasifikasi kecil yang dilatih dengan Merk dan Warna Motor dan label owner sisi latih; (c) model Intel vehicle-attributes (7 warna) sebagai pembanding |
| Merek | (a) pencari logo YOLOX dari all-cars-logo; (b) pengklasifikasi potongan kendaraan dari brand JMTO; untuk motor, Honda dan Yamaha dari Merk dan Warna Motor |
| Tak yakin | Ambang yakin per ciri dipilih di validasi. Gambar inframerah (hampir tanpa warna) → warna "tak yakin" (K52) |

- **Pencari kendaraan jualan.** Pencari kendaraan rantai sekarang adalah YOLOX COCO apa adanya (`kendaraan-yolox-coco`, tujuan
  "belajar"). Menurut K48, bobot COCO baru boleh dijual sesudah dimodifikasi. Pencari yang dilatih ulang di atas menjadi pencari kendaraan
  jualan, untuk ciri dan juga untuk rantai baca plat.
- **Komponen yang izin bobotnya Apache tetapi data latihnya tidak diungkap** (model Intel, DINOv2) diukur hanya sebagai mesin belajar
  sampai owner memutuskan (akan ditanyakan sebagai P21 bila calon itu ternyata menang). Untuk mesin jualan ciri, bobot awal yang
  dipakai hanya YOLOX (K48).
- **Pilihan diambil di validasi;** set uji dibaca sekali per putaran. Mesin dalam ONNX, berjalan di CPU (spec Fase 1 bagian 5).

## 5. Kamera dan malam

- Malam: warna dibaca bila penerangan cukup (K52). Inframerah → "tak yakin".
- Letak kamera memengaruhi bacaan (K58). Hasil dilaporkan juga menurut tinggi kendaraan dalam piksel. Ukuran logo yang masih terbaca
  menjadi syarat pemasangan, seperti tinggi plat di Fase 1 (K40).

## 6. Putaran kerja dan urutan rencana

| Rencana | Isi |
|---|---|
| 31 | Halaman ciri untuk owner (tangkapan): kartu per kendaraan berplat berlabel, terisi usulan COCO; bahan Roboflow untuk ciri disiapkan (kelas model digabung ke merek, kotak kendaraan) |
| 32 | Jenis: pencari kendaraan jualan dilatih ulang dengan kelas jenis; dibandingkan dengan pencari COCO sekarang (kendaraan ditemukan, plat ditemukan, jenis benar) |
| 33 | Warna: tiga calon; tak yakin untuk inframerah |
| 34 | Merek: pencari logo lawan pengklasifikasi kendaraan; motor Honda dan Yamaha |
| 35 | Ciri masuk rantai dan catatan kedatangan; pembanding dengan data pendaftaran; peringatan palsu dan plat tiruan tertangkap di uji; kecepatan |
| 36 | Laporan putaran pertama; owner menetapkan batas peringatan palsu |

Urutan bisa berubah menurut angka; perubahannya dicatat di `ROADMAP.md` beserta alasannya. Cara bekerja sama dengan spec Fase 1 bagian 7
(K37): agen berhenti untuk lembar dan halaman owner, pembelian, push, serta keputusan tentang apa yang dijual, keselamatan gerbang, dan
data pribadi.

## 7. Keselamatan gerbang

- Ciri **tidak pernah** membuka atau menahan gerbang di Fase 3. Ciri hanya mencatat dan memberi peringatan (K55, spec induk 4.4).
- Baris "Jelas berbeda → Tidak dibuka" di spec induk 4.3 baru berlaku bila owner memutuskannya sesudah peringatan palsu terbukti jarang.

## 8. Data pribadi dan izin

- Ciri yang terkait plat dan jam kedatangan adalah data pribadi (UU PDP). Potongan, halaman, label, dan catatan tinggal di `data/`.
- `bukti/` hanya berisi hitungan, diperiksa dengan kontrol positif.
- Tanpa pengenalan wajah atau identitas orang (U3).
- Mesin jualan hanya memuat bahan `BOLEH-PRODUK`, diperiksa `tools/periksa-jualan.mjs`. CC BY 4.0 wajib atribusi (K56).

## 9. Yang tidak dikerjakan di tahap 1

- Nama model, dan sidik rupa untuk mencocokkan kendaraan dengan dirinya sendiri (spec induk 4.2, tahap 2).
- Warna plat dan analitik pengunjung kafe dan mal (K57, menyusul).
- Menahan gerbang karena ciri (bagian 7).
- Membeli kamera, lampu, atau server: keputusan owner.

## 10. Selesai

Tahap 1 selesai bila salah satu terpenuhi:
- laporan putaran menunjukkan peringatan palsu di bawah batas yang ditetapkan owner, per kelompok, dengan jumlah kedatangan yang cukup;
- **atau** owner memutuskan berhenti atau mengubah arah sesudah membaca laporan putaran mana pun.
