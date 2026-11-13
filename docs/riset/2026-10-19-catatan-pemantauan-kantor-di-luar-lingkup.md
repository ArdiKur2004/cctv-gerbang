# Memantau kondisi kantor dari CCTV (19 Okt 2026) — DI LUAR LINGKUP CCTV Gerbang

> **Di luar lingkup** (`SEED.md` §5, `CLAUDE.md` §2): produk lain, bukan gerbang plat. Disimpan di sini hanya sebagai catatan atas
> permintaan owner, untuk dipindah ke workspace yang tepat (paling dekat: vision-seed, `anak-seed/02-kantor-kehadiran`, pertanyaan terbuka
> B7 dan H2). Tidak ada kode. Zip "Office" yang diunduh owner tidak dibuka di sini.
>
> **Hanya baca, bukan nasihat hukum.** Disusun agen riset; halaman Roboflow dibaca lewat peramban tanpa akun. Riset vision-seed dipakai ulang
> (`vision-seed/docs/RISET-REPO.md`, `docs/HUKUM-PRIVASI.md`).
>
> **Diperiksa ulang agen utama (19 Okt), semuanya cocok:**
> - README RF-DETR: deteksi N/S/M/L dan Keypoint (Preview) Apache-2.0; Atto, Femto, Pico, XL, 2XL berlisensi PML 1.0;
> - UU PDP Pasal 4 ayat (2) huruf b: data biometrik termasuk data pribadi spesifik;
> - halaman lisensi Ultralytics: "All Ultralytics YOLO trained models fall under the AGPL-3.0 License by default"; pemakaian komersial butuh
>   lisensi Enterprise.
>
> Klaim lain belum diperiksa ulang (bagian 6).

Permintaan owner, apa adanya: "tolong risetkan tentang gambar yang saya upload ini tentang kondisi di dalam kantor, berapa lama orang tersebut
duduk dan menghadap komputer untuk bekerja, untuk menghitung absensi dan juga menghitung jam kerja efektif, dan bagaimana kondisi hubungan
antar karyawan di kantor."

## 1. Ringkasan

- **Bisa diandalkan:** kursi terisi dan berapa lama, per meja atau per area: zona per kursi, pelacak orang, dan jeda beberapa detik supaya
  angka tidak berkedip. Komponennya bebas biaya dan boleh dijual (RF-DETR N–L, `roboflow/trackers`, `supervision`). Akurasi di kantor owner
  belum diukur.
- **Tidak bisa diandalkan:** "menghadap komputer" dari kamera plafon, "jam kerja efektif", dan "hubungan antar karyawan". Kamera hanya
  melihat posisi tubuh, bukan bekerja, berpikir, rapat, atau menelepon. Meta-analisis 94 sampel (23.461 pekerja) tidak menemukan bukti
  pemantauan elektronik menaikkan kinerja, dan menemukan stres naik (Ravid dkk.).
- **Dataset Office (886 gambar) hanya untuk percobaan awal.** Kelasnya hampir sama dengan COCO; uji cuma 88 gambar; asal gambar tidak
  diketahui. Model di halamannya YOLOv8m (AGPL), jadi ditolak untuk produk.
- **Hukum:** absensi wajah = data biometrik (UU PDP Ps. 4); pemantauan karyawan sistematis hampir pasti wajib DPIA (Ps. 34); karyawan berhak
  keberatan atas keputusan otomatis (Ps. 10). Belum ada aturan khusus CCTV di tempat kerja.
- **Risiko terbesar:** angka kamera dipakai untuk memotong gaji, memberi SP, atau menilai orang. Upah tetap wajib dibayar dalam beberapa
  keadaan (PP 36/2021 Ps. 40); data harus "akurat … tidak menyesatkan" (UU PDP Ps. 16). Pembanding: CNIL Prancis mendenda Amazon €32 juta,
  antara lain karena sinyal "diam ≥10 menit" pada pemindai pekerja gudang.

## 2. Per tujuan

| Tujuan | Cara teknis | Keandalan | Risiko hukum | Saran |
|---|---|---|---|---|
| Lama duduk | Orang dan kursi → zona per kursi → pelacak → lama di zona | Tinggi bila kamera diam dan zona per kursi; gambar dari atas berbeda dari foto biasa, jadi detektor dilatih ulang dengan gambar kamera owner | Sedang: DPIA, pemberitahuan (Ps. 21) | Mulai di sini; laporan per area/tim, tanpa wajah; uji 1 hari lawan catatan manual |
| Menghadap komputer | Pose kepala/badan atau arah pandang | Rendah dari kamera plafon (wajah sering tak terlihat); dengan kamera menghadap orang, galat ±12° pada jarak <1 m | Sedang–tinggi; kamera menghadap wajah lebih invasif | Jangan dijanjikan; paling jauh "di kursi dan badan ke arah meja" |
| Absensi | A. kartu/RFID/QR/aplikasi + hitungan orang tanpa identitas · B. kursi = orang · C. wajah dari CCTV · D. mesin wajah di pintu | A tinggi (kartu bisa dititipkan); B sedang; C sedang–rendah; D tinggi | A/B rendah–sedang; C/D tinggi (biometrik; persetujuan karyawan lemah karena posisi timpang; Italia: absensi wajah ilegal tanpa dasar UU) | A, dengan aplikasi absensi yang ada; wajah hanya dengan DPIA, dasar hukum tertulis, dan pilihan non-wajah |
| Jam kerja efektif | Tidak ada cara ilmiahnya; yang terukur hanya "waktu di meja" | Rendah sebagai ukuran kerja | Tinggi bila untuk gaji, SP, PHK (Ps. 10, Ps. 16, PP 36/2021 Ps. 40; SP berurutan) | Jangan dibuat; pakai istilah "waktu di meja per tim"; kinerja dinilai dari hasil kerja |
| Hubungan antar karyawan | ≥2 orang berdekatan dan saling menghadap ≥T menit (F-formation, GCFF) | Rendah untuk "hubungan"; untuk "berkumpul" F1 0,85–0,95 (longgar) dan 0,63–0,86 (ketat), diukur pada orang berdiri, belum pada orang duduk | Tinggi: pemrofilan (Ps. 10, Ps. 34(2)d); UE melarang AI menebak emosi di tempat kerja sejak 2 Feb 2025 (pembanding) | Paling jauh pemakaian area bersama per minggu, tidak per orang; iklim kerja lewat survei anonim |

## 3. Dataset Office dan komponen

**Dataset Office** (universe.roboflow.com/workspace-ocwst/office-0kyrc): pembuat bernama "workspace", tanpa deskripsi, Nov 2023; v3 2.126
gambar karena augmentasi ×3 (latih 1.860, validasi 178, uji 88), 512×512; mAP 92,2% dari "yolov8m Model Upload" pengunggah sendiri; kelas
person, chair, mouse, keyboard, cellphone (semua ada di COCO). Kurang: meja, monitor dari atas, duduk/berdiri, arah kepala, telepon di
tangan, sudut kamera owner. API Roboflow mengirim gambar ke luar negeri (UU PDP Ps. 56), jadi proses di lokasi.

| Komponen | Peran | Lisensi kode / bobot | Vonis |
|---|---|---|---|
| Model Office (yolov8m) | Deteksi | AGPL / AGPL | DITOLAK-AGPL |
| Dataset Office | Bahan latih | label CC BY 4.0; asal gambar tak diketahui | RISET-SAJA; produk BELUM-JELAS |
| RF-DETR N/S/M/L | Deteksi | Apache-2.0 / Apache-2.0 (data latih tak disebut) | kode/bobot BOLEH-PRODUK; data BELUM-JELAS |
| RF-DETR Atto/Femto/Pico/XL/2XL | Deteksi | — / PML 1.0 | bukan untuk produk |
| RF-DETR Keypoint (Preview) | Pose tubuh | Apache-2.0 / Apache-2.0 (COCO keypoints) | BELUM-JELAS (preview) |
| YOLOX | Deteksi | Apache / Apache (COCO) | BOLEH-PRODUK (sejalan K48) |
| roboflow/trackers · supervision | Pelacakan · zona | Apache-2.0 · MIT | BOLEH-PRODUK (dependensi McByte belum diperiksa) |
| boxmot · SORT/DeepSORT | Pelacakan | AGPL · GPL | ditolak |
| rtmlib RTMPose body7 | Pose | Apache (7 dataset belum diperiksa) | BELUM-JELAS |
| ViTPose (transformers) | Pose | Apache (COCO) | BOLEH-PRODUK (vonis vision-seed) |
| Intel OMZ head-pose-adas-0001 | Pose kepala | Apache (data tak diungkap) | BELUM-JELAS |
| 6DRepNet · L2CS · Gaze-LLE | Pose kepala · pandangan | MIT / data NC | RISET-SAJA |
| RAPiD | Orang dari fisheye atas | non-komersial | RISET-SAJA |
| CEPDOF/HABBOF/WEPDTOF | Uji kamera atas | sitasi; komersial tak disebut | BELUM-JELAS |
| GCFF | Deteksi kelompok | MIT | BOLEH-PRODUK (acuan algoritma) |
| InsightFace · SFace · YuNet | Wajah | data NC atau tak disebut | RISET-SAJA · BELUM-JELAS · BELUM-JELAS |

## 4. Produk yang sudah ada

| Produk | Apa | Harga |
|---|---|---|
| ACTi Absence Detection | Zona per meja, alarm bila kosong | tidak dipublikasikan |
| Hikvision Behavior Analysis Server | "absence/sleep on duty" (dari cuplikan) | tidak dipublikasikan |
| Wobot.ai | Checklist dari CCTV | gratis ≤10 kamera; US$9,99/kamera/bulan (dari cuplikan) |
| Spot AI | VMS + AI | ±US$99/kamera/bulan (taksiran pihak ketiga) |
| Butlr | Sensor panas tanpa kamera | custom |
| Nodeflux VisionAIre | People counting, wajah 1:N | tidak dipublikasikan |
| Mekari Talenta · Kerjoo | Absensi aplikasi | Talenta tidak dipublikasikan; Kerjoo Rp 7.800 / 15.275 / 19.175 per karyawan per bulan |
| Mesin absensi wajah (ZKTeco, Hikvision, Fingerspot, Dahua) | Terminal di pintu | Rp 1,1–4,8 juta per unit (artikel 22 Apr 2026) |

Penolakan karyawan: sensor meja OccupEye memicu protes di Barclays (2017); di Daily Telegraph sensornya dicabut di hari pemasangan.

## 5. Jalan bertahap yang aman (usulan)

0. **Dokumen dulu:** tujuan tertulis dan DPIA ringkas; peraturan perusahaan diperbarui dengan masukan wakil pekerja (≥10 pekerja); pemberitahuan
   sesuai Ps. 21 dan papan informasi; pernyataan bahwa angka kamera tidak dipakai untuk sanksi otomatis; pendapat hukum tertulis. PP 33/2026
   berlaku 16 Jan 2027.
1. **Fase 1:** keterisian meja dan lama duduk per area/tim per hari, tanpa wajah dan identitas, diproses di komputer kantor, video tidak
   disimpan; detektor dilatih ulang dengan rekaman kantor sesudah karyawan diberi tahu; akurasi diuji 1 hari lawan catatan manual.
2. **Fase 2:** absensi tetap lewat kartu/aplikasi; kamera hanya mencocokkan jumlah orang, untuk melihat pola, bukan menuduh orang.
3. **Fase 3 (opsional):** pemakaian ruang bersama per area per minggu.
4. **Tidak dikerjakan** tanpa keputusan owner, pendapat hukum, dan DPIA: skor produktivitas per orang, "jam kerja efektif" untuk gaji atau SP,
   emosi, audio, dan pengenalan wajah dari CCTV.

## 6. Belum terverifikasi

- Asal gambar dan jumlah objek per kelas dataset Office; apakah 92,2% berlaku di kamera owner.
- Akurasi keterisian kursi dan pose kepala dari kamera atas di kantor sungguhan (angka tidak ditemukan).
- Isi persis PP 33/2026 soal pemrofilan dan keberatan; apakah kantor "tempat umum" menurut Ps. 17; apakah UU 6/2023 mengubah Ps. 108–111
  UU 13/2003.
- Harga Wobot, Spot AI, Butlr; daftar kejadian Hikvision.
- Data latih bobot RF-DETR; syarat gambar COCO untuk bobot yang dijual; izin komersial dataset BU VIP; kinerja GCFF pada orang duduk.
- Vonis lisensi yang dipakai ulang dari vision-seed tidak dibaca ulang dari sumber aslinya.

## 7. Usul owner sesudahnya (19 Okt): tangan di keyboard atau mouse

Owner, apa adanya: "untuk pemantau kantor dari cctv, mungkin bisa melihat seberapa sering tangan di keyboard atau di mouse saaja, bukan
melihat arah wajah sehingga ini sebagai penanda jam kerja efektifnya".

**Tanggapan agen (belum diriset, belum diukur):**
- **Secara teknis masuk akal untuk dicoba.** Dataset Office sudah punya kelas keyboard dan mouse. Pergelangan tangan bisa didapat dari model
  pose; yang boleh dijual dari daftar di atas hanya ViTPose (RF-DETR Keypoint masih preview). Cara hitungnya: tangan dianggap bekerja bila
  titik pergelangan berada di dalam kotak keyboard atau mouse selama beberapa detik.
- **Dari kamera plafon, tangan sering tertutup** monitor, badan, atau meja. Kamera perlu menghadap meja dari atas atau dari samping, dan
  akurasinya belum diketahui.
- **Ukuran ini tetap bukan ukuran kerja.** Membaca, berpikir, menelepon, rapat, dan bekerja di kertas tidak terhitung. Orang yang bekerja
  dengan pena atau di layar sentuh terlihat "tidak bekerja".
- **Hukumnya sama dengan "waktu diam":** CNIL mendenda Amazon antara lain karena penanda diam ≥10 menit. Aman bila dipakai per tim atau
  per area, tanpa identitas, dan tidak untuk gaji atau SP (UU PDP Ps. 10 dan 16; PP 36/2021 Ps. 40). Pemantauan aktivitas langsung di
  komputer (catatan keyboard dan mouse) lebih tepat daripada kamera, tetapi sama invasifnya.
- Tetap di luar lingkup CCTV Gerbang; tempatnya workspace vision-seed.

**Sumber utama:** universe.roboflow.com/workspace-ocwst/office-0kyrc · raw.githubusercontent.com/roboflow/rf-detr/develop/README.md ·
github.com/roboflow/trackers · github.com/roboflow/supervision · ultralytics.com/license · pasal.id (UU 27/2022 Ps. 4, 10, 16, 21, 34;
PP 36/2021 Ps. 40) · hukumonline.com · pmc.ncbi.nlm.nih.gov/articles/PMC4440729 · vip.bu.edu/projects/vsns/cossy/datasets ·
github.com/duanzhiihao/RAPiD · microsoft.com/research (Ravid dkk.) · lewissilkin.com (CNIL–Amazon) · fpf.org (EU AI Act) ·
acti.com · kerjoo.com/harga · kantorku.id · shrm.org.
