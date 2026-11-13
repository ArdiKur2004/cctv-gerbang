# SERAH TERIMA — dari sesi 2 (13–14 Okt 2026) ke sesi 3

> Untuk agen yang membuka sesi baru di workspace CCTV Gerbang. Dibaca **sesudah** `ROADMAP.md` dan sebelum bekerja.
> Dokumen ini tidak menggantikan catatan lain: `ROADMAP.md` tetap sumber tunggal status, `SEED.md` §3 tetap sumber
> keputusan owner. Isinya peta: di mana kita, apa berikutnya, bagaimana kita bekerja, dan apa yang pernah salah.
> Bila dokumen ini berbeda dengan `ROADMAP.md`, yang benar `ROADMAP.md` (dan perbedaannya dicatat).

## 1. Posisi dalam satu paragraf

CCTV Gerbang adalah produk image processing yang akan dijual massal di Indonesia: kamera CCTV di gerbang membaca plat
nomor, mencocokkannya dengan daftar izin, lalu memberi perintah buka ke motor gerbang ("tanpa kartu, stiker, atau
remote"). Owner: Muhammad Aldy. Spec induk sudah disetujui (K18) dan Fase 0A (pembuktian dengan bahan dari luar) sedang
berjalan di laptop, tanpa pengeluaran (K6). Rencana 1 sampai 4 Fase 0A selesai: bengkel dan pintu-pintu Docker, vonis
izin sepuluh komponen, ringkasan Perpol 7/2021, 100 video riset terpilah, dan dua dataset plat Indonesia berizin jual
(INDO-ALPR 6.174 potongan plat, dataset pencahayaan 561 foto) tersimpan, terkunci, dan terbukti sama dengan terbitannya.
**Rencana 5 sudah ditulis dan menunggu lampu hijau owner.** Belum ada mesin baca plat dan belum ada satu angka akurasi
pun yang diukur.

## 2. Yang dikerjakan berikutnya, persis

1. Sapa owner dengan ringkasan posisi 3–4 kalimat, lalu **satu** pertanyaan: lampu hijau menjalankan Rencana 5
   ([`plans/2026-10-14-fase-0a-rencana-5-set-uji-baca.md`](plans/2026-10-14-fase-0a-rencana-5-set-uji-baca.md)).
   Owner menjawab dengan kata seperti "Jalankan". Pesan terakhir sesi 2 sudah menjelaskan isinya ke owner; ulangi
   singkat saja, jangan menulis ulang rencananya.
2. Bila disetujui: jalankan Rencana 5 task demi task dengan skill `honest-slice-execution` (pendamping:
   `superpowers:test-driven-development`, `superpowers:verification-before-completion`). Rencana itu ditulis lengkap,
   termasuk kode dan angka gerbang yang diharapkan (lab 51 → 72 → 79 → 83 → 90 → 97; Node tetap 99).
3. Rencana 5 **berhenti di akhir** (Task 6 Step 5): owner diminta membuka tiga lembar contoh label dan menyebut nomor
   baris yang labelnya salah. Agen tidak membuka lembar itu.
4. Sesudah itu: tulis Rencana 6 (pembanding paket jadi seperti fast-plate-ocr, mesin belajar pertama untuk baca huruf,
   mencari plat di foto utuh dan video, plat buatan komputer, taksiran kecepatan, laporan). Pecah lagi bila terlalu
   besar. **P14 ditanyakan ke owner saat bahan mesin jualan dipilih**, tidak sebelumnya.

## 3. Urutan baca

1. [`ROADMAP.md`](ROADMAP.md) sampai habis: status, peta fase, temuan di luar lingkup, changelog (barisnya panjang;
   alasan tiap langkah ada di sana).
2. Dokumen ini.
3. [`SEED.md`](SEED.md) §3 (K1–K21 beserta kata-kata owner dan cara membaliknya) dan §6 (usulan agen U1–U9).
4. [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md): bagian A (P1–P14) dan paragraf "Sesudah …" di bagian B.
5. [`CLAUDE.md`](CLAUDE.md): aturan proyek. Dibaca otomatis, tetapi baca §3–§7 dengan sadar.
6. Rencana yang sedang berjalan (Rencana 5). Spec induk
   ([`specs/2026-10-13-cctv-gerbang-desain-induk.md`](specs/2026-10-13-cctv-gerbang-desain-induk.md)) dibaca bagian
   yang dirujuk rencana; bagian 8 (Fase 0) wajib.

## 4. Keputusan owner (ringkas; yang mengikat ada di `SEED.md` §3)

| # | Isi | | # | Isi |
|---|---|---|---|---|
| K1 | Produk harus image processing | | K12 | Menyambung ke motor gerbang yang ada; terbuka menjual dan memasang motor |
| K2 | Yang digarap: CCTV gerbang plat, bukan QC pabrik | | K13 | Harga menurut pembeli: Rp 5.000/bulan aplikasi untuk umum; paket perusahaan dengan analisis |
| K3 | Workspace `cctvgerbang-seed` | | K14 | Repo mandiri; menyalin bagian vision-seed yang dibutuhkan dengan catatan asal-usul |
| K4 | Keempat kelompok pembeli dibidik, termasuk rumah pribadi | | K15 | Bahan riset-saja boleh untuk belajar dengan pagar (**diubah K21**) |
| K5 | Lokasi uji: lokasi owner, lalu kenalan; sementara belum ada → data luar | | K16 | Mesin baca plat buatan sendiri, bertingkat; paket jadi dan AI serba-bisa sebagai pembanding |
| K6 | Perangkat uji disetujui tapi tidak dibeli; semua di laptop; tanpa biaya | | K17 | Pengumpulan video mentah dimulai mendahului spec |
| K7 | Plat motor sejak awal | | K18 | Spec induk disetujui; peta fase dikunci (0A, 0B, 1–6) |
| K8 | Ciri kendaraan sampai nama model, bertahap | | K19 | Agen hanya melihat gambar kecil buram (plat tak terbaca); owner memeriksa label huruf plat |
| K9 | Gagal-buka sasaran 99% per kelompok (mobil/motor × siang/malam); buka-salah nol | | K20 | Unduhan video gelombang kedua yang diarahkan ke sudut gerbang |
| K10 | Klaster/perumahan dan gudang/pabrik/kantor lebih dulu | | K21 | **Bahan internet boleh melatih model yang dijual, selama sumbernya tidak menyebut larangan dipakai belajar**; nasihat hukum soal plat disampaikan owner |
| K11 | Empat jalur jual: distributor, online, OEM, pemasang CCTV | | | |

**Jangan menanyakan ulang atau memperdebatkan keputusan ini.** Owner beberapa kali memilih berbeda dari saran agen;
pilihan owner yang mengikat. Risikonya dicatat di bagian B dan dijawab dengan data.

## 5. Yang masih terbuka

| Butir | Keadaan |
|---|---|
| **Lampu hijau Rencana 5** | Belum diberikan. Ini pertanyaan pertama sesi 3 |
| **P14** | Apakah label "non-komersial"/"riset saja" dan syarat YouTube (melarang mengunduh tanpa izin) dihitung "larangan" menurut K21. Sampai dijawab: bahan berlabel begitu, termasuk 100 video riset, tidak masuk mesin jualan. Ditanyakan saat bahan mesin jualan dipilih |
| **P13** | Dibaca agen sebagai terjawab oleh K21 (bobot awal berizin permisif boleh). Owner menjawab "ya lanjutkan" atas laporan yang memuat bacaan itu. Tetap bacaan agen |
| **B9 (data pribadi)** | Berisi pernyataan owner (K21) bahwa pihak hukum sudah dimintai nasihat. Agen tidak melihat hasil konsultasinya. Syarat YouTube soal unduhan sudah disampaikan sekali ke owner sebagai hal yang belum tentu tercakup; **jangan diangkat lagi** kecuali owner bertanya |
| **Pilihan C** (owner merekam kendaraan sendiri dengan HP) | Terbuka, belum dikerjakan. Satu-satunya jalan ke malam dan motor dari sudut gerbang sebelum ada lokasi |
| **Fase 0B** | Menunggu lokasi atau kamera. Owner sedang mengurus izin di lokasi kenalan |
| **Ide MiroFish** (agen menirukan komentar orang) | Dicatat di "Temuan di luar lingkup", tidak dikerjakan |

## 6. Cara kita bekerja dan sampai pada kesimpulan

**Alur keputusan.** Agen bertanya satu per satu (pilihan ganda, saran di urutan pertama beserta akibatnya) → owner
menjawab → jawaban dicatat di tiga tempat (`SEED.md` §3 dengan kata-kata owner dan cara membaliknya,
`OPEN-QUESTIONS.md`, `ROADMAP.md` dengan baris changelog beralasan) → commit lokal. Keputusan yang mengubah keputusan
lama (seperti K21 atas K15) diberi catatan di setiap aturan yang bersandar padanya, termasuk spec dan `CLAUDE.md`; teks
yang pernah disetujui tidak dihapus, hanya diberi catatan perubahan.

**Alur membangun.** Spec disetujui → Fase 0A dipecah menjadi rencana kecil yang masing-masing lengkap (kode, uji, angka
yang diharapkan) → owner memberi lampu hijau per rencana → agen menjalankannya dengan TDD: uji ditulis dulu dan
**terlihat merah karena fiturnya belum ada**, lalu hijau, lalu gerbang penuh, lalu commit beralasan → hasil dicatat
dengan angka sebelum→sesudah dan batasnya → laporan ke owner.

**Sebelum menulis rencana, ukur sumbernya dulu.** Rencana 4 dan 5 ditulis sesudah membaca sumber aslinya (API
penerbit, pohon berkas GitHub, statistik gambar di lab) tanpa mengunduh atau membuka gambar. Dua kali isi bahan ternyata
berbeda dari catatan riset (INDO-ALPR punya 61.747 gambar olahan; labelnya di nama berkas; potongan plat, bukan foto
adegan; pembagian latih-uji penerbit bocor). Rencana yang menebak isi bahan akan salah, jadi bila isinya belum
diketahui, rencananya dipecah.

**Aturan bukti.**
- Catatan bukan bukti; angka dibaca dari sumber, tidak disalin dari ingatan (termasuk SHA-256: disalin dengan skrip
  dari berkas catatan asal, tidak diketik).
- Berhasil atau tidaknya unduhan dinilai dari **berkasnya**, bukan kode keluar. Kode keluar bukan 0 juga bukan berarti
  uji merah (kode 3 = bengkel sibuk; kode 6 = image tak sesuai kunci **atau Docker Desktop belum menyala**).
- Yang tidak bisa dibuktikan ditulis sebagai batas. Angka dari bahan luar tidak pernah dilaporkan sebagai "K9 tercapai".
- Temuan di luar lingkup dicatat di ROADMAP, tidak diselundupkan.
- Cacat sepupu dicari: tiap cacat yang ketemu diikuti pencarian cacat serupa di tempat lain.

**Mekanisme data pribadi (paling sering diuji).**
- Nomor plat tidak pernah keluar dari laptop: agen tidak membuka gambar riset apa adanya, dan tidak mencetak nama berkas
  INDO-ALPR (nama berkasnya = nomor plat). Alat lab hanya mencetak hitungan; berkas yang memuat plat
  (`pembagian.json`, `hasil.jsonl`, lembar contoh) tinggal di `data/` dan tidak dibuka agen.
- Agen melihat isi video hanya lewat lembar gambar kecil 48 titik yang dikaburkan, **sesudah owner memeriksanya** (K19).
- Lembar yang platnya terbaca dibuat untuk owner dan tidak dibuka agen.
- Pesan galat bawaan Python bisa memuat jalur berkas: alat yang menyentuh berkas berplat menangkap galat baca-tulisnya
  sendiri.

**Mekanisme pencatatan.** Skrip pencatat sekali pakai ditulis sebagai **berkas** di folder kerja sementara (bukan
`node -e`), membaca berkas dengan `\r\n` diseragamkan, dan memeriksa tiap jangkar ketemu **tepat sekali** sebelum menulis
apa pun. `ROADMAP.md` diubah lewat changelog, tidak ditulis ulang dari ingatan. Commit berbahasa Indonesia, memuat
alasan, diakhiri `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Tidak ada push dan tidak ada repo GitHub.

## 7. Cara berbicara dengan owner

- Owner bukan orang teknis. Bahasa Indonesia sehari-hari, kalimat pendek, analogi bila menolong (owner pernah meminta
  penjelasan ulang dengan analogi untuk P10, dan pernah kehilangan jejak "bagian 1" yang terkubur di pesan panjang).
- Tiap permintaan ke owner berdiri sendiri: apa yang diminta, pilihannya, dan akibatnya, di awal pesan.
- Satu pertanyaan per giliran. Pilihan ganda, saran di depan.
- Owner tidak suka ditanya berulang tentang hal yang sudah diputuskannya ("jangan banyak pertanyaan perihal itu").
  Fakta penting disampaikan **sekali**, singkat, lalu dikerjakan.
- Owner menjawab singkat ("A", "sesuai", "Jalankan", "ya lanjutkan"). Jawaban singkat atas laporan yang memuat bacaan
  agen dicatat sebagai "tidak dikoreksi", bukan sebagai keputusan baru.
- Uang selalu keputusan owner. Agen tidak membeli apa pun.

## 8. Mesin dan alat

| Hal | Keadaan |
|---|---|
| Gerbang uji | `npm test` (Node, 99 lulus) dan `npm run test:lab` (Python di lab, 51 lulus, 1 peringatan "Duplicate name" yang disengaja). Satu suite pada satu waktu; tanpa `\| tail`/`\| head` |
| Pintu Docker | `tools\ambil-video.ps1` (video YouTube/TikTok), `tools\ambil-berkas.ps1` (arsip dataset dari butir kunci), `tools\lab.ps1` (lab tanpa jaringan, repo read-only, hanya `data\keluaran` bisa ditulis). Image `vision-seed-lab:v1` dikunci lewat ID-nya |
| Docker Desktop | `D:\Docker\Docker Desktop.exe`; **tidak menyala sendiri** sesudah laptop dinyalakan ulang |
| Git Bash | Mengubah jalur `/kerja/...` menjadi jalur Windows. Perintah lab yang memuat `/kerja/...` dijalankan lewat PowerShell |
| Kartu grafis | RTX 4060 8 GB, dipakai bersama vision-seed lewat kunci `Global\vision-seed-bengkel`. Periksa `nvidia-smi` sebelum job berat |
| Kunci | `tools/vendor.lock.json`: 11 repo, image lab, 3 butir `berkas` (dataset). Rencana 5 menambah `model_hf` (Qwen3-VL-2B disalin dari vision-seed) |
| vision-seed, agent-sandbox | **Dibaca, tidak diubah.** Jangan `cd` ke sana |

## 9. Bahan yang ada

| Bahan | Letak | Keadaan |
|---|---|---|
| 100 video riset YouTube | `data/video/riset/`, manifes `data-asal/video-riset.json` | `RISET-SAJA`. Terpilah: 17 sudut gerbang (4.176 dtk, 3.451 dari satu video 640×360, **tak satu pun malam**), 13 kamera diam lain, 14 dasbor, 50 lain, 6 tak jelas. Semua terbukti utuh |
| INDO-ALPR bagian asli | `data/keluaran/dataset/indo-alpr/original/` | `BOLEH-PRODUK` (CC BY 4.0). 6.174 potongan plat, tiap berkas cocok SHA-256 penerbit. Label = nomor plat di nama berkas. ~1.150 gambar motor menurut nomor urut (dihitung per gambar, bukan per plat). Pembagian penerbit bocor (713 dari 1.462 gambar uji). ~5% nama tanpa kode wilayah |
| Dataset pencahayaan | `data/keluaran/dataset/plat-lighting/` | `BOLEH-PRODUK` (CC BY 4.0, tanpa berkas LICENSE). 561 foto adegan dengan kotak plat; plat selebar tengah 5% foto; 54 foto gelap |
| Arsip unduhan | `data/unduhan/` | Dikunci SHA-256 di `tools/vendor.lock.json` |
| Daftar bahan | `data-asal/bahan.json` | 11 butir: 2 `BOLEH-PRODUK`, 1 `RISET-SAJA`, 8 `BELUM-JELAS` (bobot) |

## 10. Yang pernah salah (supaya tidak terulang)

| Kejadian | Pelajaran |
|---|---|
| Unduhan terpotong melapor kode 0 (2 dari 49 video) | Nilai dari berkas. Pintu video kini kode 8 bila ada `.part` |
| Satu unduhan meninggalkan `.mp4` rusak yang tercatat "utuh" | `tools/lab/periksa_utuh.py` wajib sebelum `tools/manifes-video.mjs` (manifes menolak video baru tanpa itu) |
| Pemindai repo melewatkan lima jalur unduhan otomatis | Diperbaiki; pemindaian tangan tetap dilakukan |
| `node --test tools/uji/` di Node 24 terlihat seperti uji merah | Pakai `npm test` |
| Klaim "plat motor dua baris" diulang dari catatan | Dikoreksi dari Perpol: nomor satu baris, baris kedua masa berlaku |
| Skrip `node -e` dan heredoc kehilangan garis miring terbalik (tiga kali) | Tulis skrip sebagai berkas |
| Git Bash mengubah `/kerja/...` | Jalankan perintah lab lewat PowerShell |
| Gerbang lab kode 6 sesudah laptop dinyalakan ulang | Docker Desktop belum menyala; periksa `docker version` dulu |
| Catatan usang diwariskan (`bahan.json` "45 video", README "belum ada kode", B12 "belum ada vonis") | Klaim catatan diperiksa dan dikoreksi di commit yang sama |
| `grep -c` bernilai 0 memutus rantai `&&` | Jangan merangkai perintah sesudah `grep -c` |

## 11. Batas yang masih terbuka

- Belum ada CI; hanya gerbang lokal.
- Pintu video masih keluar 0 bila pengunduh menolak sebelum mulai (tertahan oleh pemeriksa keutuhan).
- TikTok belum diambil: alatnya hanya bisa mencari di YouTube.
- K9 tidak bisa dibuktikan dari bahan luar; butuh kamera di posisi gerbang (Fase 0B).
- Siang-malam pada potongan plat tidak bisa ditentukan; Rencana 5 memakai terang-gelap sebagai taksiran.
- Kode wilayah "B" dianggap Polda Metro Jaya: anggapan agen yang belum diperiksa ke lampiran kode wilayah Perpol.
