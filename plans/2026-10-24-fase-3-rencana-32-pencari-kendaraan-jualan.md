# Fase 3, Rencana 32: Pencari kendaraan jualan — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Di repo ini eksekusi juga wajib memakai skill `honest-slice-execution`. Dikerjakan mandiri
> (K37, K61). Owner dihentikan hanya di akhir.

**Goal:** pencari kendaraan yang boleh dijual. Pencari sekarang (`kendaraan-yolox-coco`) adalah YOLOX COCO apa adanya, bertujuan "belajar".
K48 membolehkan bobot COCO di mesin jualan hanya sesudah dimodifikasi (temuan 19 Okt). Pencari baru dipakai rantai baca plat dan
pengenal ciri.

**Diubah dari spec Fase 3 bagian 4 dan 6, dan kenapa:** spec menaruh jenis di pencari kendaraan berkelas jenis. Di sini pencari kendaraan
dibuat **satu kelas** ("kendaraan"), dan jenis dikenali dari potongan kendaraan bersama warna dan merek di Rencana 33:
1. dataset Roboflow praktis melabeli satu kendaraan utama per gambar: "vehicle and license plate" 4.638 kotak mobil di 4.553 gambar,
   "Merk dan Warna Motor" tepat satu kotak per gambar (`bukti/2026-10-19-dataset-roboflow.json`). Label seperti itu cocok untuk
   mengenali ciri dari potongan, tetapi kurang lengkap untuk melatih pencari;
2. `latih_yolox.py` melatih satu kelas;
3. pikap dan bus hampir tidak ada di data mana pun (label owner: pikap 3, bus 0).

## Architecture

- `tools/lab/dataset_kendaraan.py bangun`: dataset YOLO satu kelas. Untuk tiap gambar sumber:
  - kotak kendaraan dari labelnya (kelas yang diminta, mis. cars, motorcyle, truck) ditulis sebagai kelas 0; kotak lain (plat) dibuang;
  - **label dilengkapi:** pencari COCO sekarang (guru) dijalankan, dan kotaknya yang yakin ≥ 0,4 dan tidak ber-IoU ≥ 0,5 dengan kotak
    label ditambahkan. Ini menutup kendaraan yang tidak dilabeli;
  - sumber berlabel boleh dibatasi per kelas (deterministik dari SHA-256 nama), supaya 2.168 Honda Vario hitam tidak menenggelamkan
    yang lain;
  - sumber tanpa label kendaraan (bingkai CCTV `cctv-fase1`, sisi latih video) hanya memakai kotak guru;
  - `ringkasan.json`: hitungan per sumber (gambar, kotak label, kotak guru) dan daftar bahan.
- `kendaraan.PencariKendaraan` menerima juga mesin satu kelas dari `latih_yolox.py` (keluaran ONNX 6 kolom). Ambangnya dari argumen
  `ambang`, atau dari `kendaraan.json` di folder mesin (`kendaraan.py tetapkan <folder> --ambang <a>`). Tanpa keduanya, mesin ditolak
  (gagal tertutup). Jenis tiap kotak: "kendaraan". Pemanggil (`baca_gambar`, `rantai`, `lembar_bingkai`, `lembar_kendaraan`,
  `halaman_ciri`) tidak berubah.

## Calon (YOLOX-Tiny-640 dari bobot COCO, `--jualan`, 15 zaman, benih 0)

| Calon | Latih | Validasi (memilih zaman) |
|---|---|---|
| K0 | pencari COCO sekarang, pembanding saja (tidak boleh dijual) | — |
| K1 | "vehicle and license plate" (semua sisi; cars, motorcyle, truck) + "Merk dan Warna Motor" (maks. 250 per kelas, semua sisi), dilengkapi guru | sisi valid kedua dataset, dilengkapi guru |
| K2 | K1 + bingkai CCTV `cctv-fase1/train` (kotak guru) | K1 + `cctv-fase1/valid` (kotak guru) |

Tangkapan owner tidak dipakai melatih: seluruh sisi latihnya dipakai memilih.

## Aturan memilih (ditetapkan sebelum angka calon mana pun dilihat)

- Tiap calon pada ambang {0,25; 0,4}: rantai tangkapan (`baca_gambar.jalankan`, kendaraan cadangan utuh, pencari plat C1 ambang 0,25,
  pembaca R4 ONNX, varian v0), dinilai `nilai_label` di **sisi latih**.
- Dibaca benar terbanyak menang. Seri: plat berlabel sisi latih yang tengahnya dimuat kotak kendaraan terbanyak. Seri: K1. Seri: 0,25.
- **Syarat dipakai:** pencari terpilih menjadi pencari kendaraan rantai jualan (`kendaraan.json` ditetapkan) bila dibaca benarnya di
  sisi latih tidak lebih rendah dari K0 lebih dari 2 plat. Bila lebih rendah, hasilnya dilaporkan ke owner dan K0 tetap hanya di rantai
  belajar.
- Pilihan di-commit sebelum uji dibuka.
- **Diukur sekali di uji:** rantai dengan pencari terpilih di tangkapan uji (Rencana 30: 22 dari 34), dan kendaraan pemuat untuk 39
  kendaraan berlabel owner di sisi uji.

## Task 1: Dataset kendaraan

**Files:** Create `tools/lab/dataset_kendaraan.py`, `tools/lab/uji/test_dataset_kendaraan.py`.

- [x] **Step 1: Uji merah** (guru dipalsukan): kelas dipilih dan ditulis 0, plat dibuang, poligon dilewati; kotak guru ditambah hanya
  bila yakin ≥ 0,4 dan IoU < 0,5 dengan label; batas per kelas deterministik; sumber tanpa label memakai kotak guru saja; sisi sumber ke
  sisi tujuan sesuai permintaan; nama berawalan sumber; ringkasan dan bahan; CLI sampai berkas. (**Ditambah:** nama berkas baru dari
  SHA-256 nama asli, karena nama berkas dataset bisa memuat nomor plat; folder keluaran yang sudah ada tidak ditimpa.)
- [x] **Step 2:** Tulis kodenya. Gerbang hijau.

## Task 2: Pencari kendaraan satu kelas

**Files:** Modify `tools/lab/kendaraan.py`; uji `tools/lab/uji/test_kendaraan.py`, `tools/lab/uji_fpo/test_yolox_sungguhan.py`.

- [x] **Step 1: Uji merah:** `tetapkan` menulis `kendaraan.json`; mesin satu kelas tanpa ambang ditolak; ambang argumen mengalahkan
  `kendaraan.json`; mesin COCO tetap seperti dulu. Uji image tambahan: mesin YOLOX satu kelas sungguhan diekspor, ditetapkan, lalu dimuat
  `PencariKendaraan` dan dipanggil lewat `baca_gambar` CLI sampai berkas keluaran. (Merah: `PencariKendaraan` lama gagal `KeyError:
  'ambang'` pada mesin satu kelas. **Ditambah:** `kendaraan.json` diikat ke SHA-256 `mesin.onnx`.)
- [x] **Step 2:** Tulis kodenya. Gerbang lab, image tambahan, Node hijau. (Lab 372 → 385, image tambahan 35 → 36, Node 120.)

## Task 3: Bahan dan pelatihan

- [x] **Step 1:** Bangun dataset K1 dan K2 (guru di CPU). (K1 latih 7.949 gambar: "vehicle and license plate" 5.123 dengan 5.506 kotak
  label dan 9.274 kotak guru; motor 2.826 sesudah batas 250 per kelas. K2 + 864 bingkai CCTV dengan 3.410 kotak guru.)
- [x] **Step 2:** Latih K1 lalu K2 di latar dengan penjaga GPU; ekspor ONNX. (K1 66,3 menit, zaman terbaik 15, F1 validasi 0,929; K2 74
  menit, zaman 13, 0,905; ONNX sama dengan torch 20/20 untuk keduanya.)

## Task 4: Memilih, mengukur, lalu BERHENTI

- [x] **Step 1:** Rantai sisi latih untuk K0, K1, K2 pada {0,25; 0,4}; pilih menurut aturan; commit sebelum uji dibuka. **K1 0,25
  terpilih:** dibaca benar 115 (K1 0,4: 115; K2: 114, 113; K0: 112) dari 125; plat berkendaraan 138 dari 141 (K0 135); kotak di luar
  label 0 (K0 6). Dipakai di rantai jualan: tidak lebih rendah dari K0. `bukti/2026-10-24-pencari-kendaraan-jualan-pilih.json`.
- [x] **Step 2:** `kendaraan.py tetapkan` bila syarat dipakai terpenuhi; rantai di tangkapan uji sekali; kendaraan pemuat di uji;
  `periksa-jualan`. (Ditetapkan ambang 0,25. Uji lewat baris perintah `baca_gambar` dengan `kendaraan.json`: 24 dari 34, Rencana 30: 22;
  0 benar → salah. Plat berkendaraan uji 39 lawan 38 dari 39. `BOLEH-PRODUK` untuk safetensors dan ONNX.)
- [x] **Step 3:** Laporan `bukti/2026-10-24-pencari-kendaraan-jualan.md` dan `.json`, ROADMAP dan changelog, `CLAUDE.md` §7. Gerbang penuh,
  commit. **BERHENTI untuk owner.**

**Batas:** kotak guru berasal dari pencari COCO, jadi pencari baru belajar sebagian dari pencari lama; tangkapan sisi latih hanya 141
plat; uji 39 kendaraan; kecepatan tidak berubah karena susunannya sama (YOLOX-Tiny-640), tetapi itu tidak diukur.
