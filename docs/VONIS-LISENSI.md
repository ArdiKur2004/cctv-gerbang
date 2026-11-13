# Vonis izin komponen (B12)

> Dibuat 2026-10-13 dalam Rencana 2 Fase 0A. Tiap vonis dibaca dari berkas pada commit yang dikunci di
> `tools/vendor.lock.json`; buktinya diarsipkan di `docs/lisensi/`. Kode, bobot, dan bahan latih dinilai terpisah
> (`CLAUDE.md` §5). Yang tidak dinyatakan sumbernya ditulis "tidak dinyatakan".
>
> Vonis ini menggantikan vonis sementara di `docs/riset/2026-10-13-catatan-repo-dan-pustaka-baca-plat.md` untuk
> komponen yang tercantum. Komponen bertanda "izin saja" belum diklon dan belum dipindai: yang sudah dibaca hanya
> berkas izin kodenya. Dependensi dan bobotnya belum.

## Arti vonis

| Vonis | Arti |
|---|---|
| `BOLEH-PRODUK` | Izinnya membolehkan produk tertutup yang dijual, dan buktinya diarsipkan |
| `RISET-SAJA` | Hanya untuk belajar di lab (K15). Tidak boleh masuk mesin jualan |
| `DILARANG` | Tidak boleh masuk produk |
| `BELUM-JELAS` | Izin tidak dinyatakan atau belum dibaca. Diperlakukan seperti `RISET-SAJA` sampai jelas |

Aturan yang dipakai, tanpa kelonggaran: bobot baru `BOLEH-PRODUK` bila izin bobotnya dinyatakan permisif **dan** bahan
latihnya dinyatakan boleh dipakai komersial. Salah satu tidak dinyatakan berarti `BELUM-JELAS`.

## Tabel vonis

| Komponen @ commit | Peran | Izin kode | Izin bobot | Bahan latih bobot dan izinnya | Pakai `ultralytics` | Vonis kode | Vonis bobot | Bukti |
|---|---|---|---|---|---|---|---|---|
| `rf-detr` @ `45cb80c` | Pendeteksi acuan | Apache-2.0 | N, S, M, L ditandai "Apache 2.0"; XL dan 2XL "PML 1.0" | Tolok ukur pada COCO; bahan latih per bobot dan izinnya tidak dinyatakan | tidak | `BOLEH-PRODUK` | N–L: `BELUM-JELAS` (izin bobot permisif, izin bahan latih tidak dinyatakan). XL, 2XL: tidak dipakai (PML bukan izin terbuka; teksnya belum dibaca) | `docs/lisensi/roboflow__rf-detr/` · `docs/audit/rf-detr@45cb80c.md` |
| `trackers` @ `3666546` | Pelacak | Apache-2.0 | Inti pelacak tidak memakai bobot | tidak berlaku | tidak | `BOLEH-PRODUK` | tidak berlaku | `docs/lisensi/roboflow__trackers/` · `docs/audit/trackers@3666546.md` |
| `yolox` @ `4197784` | Pendeteksi ringan | Apache-2.0 | tidak dinyatakan | COCO; izinnya tidak dinyatakan | tidak | `BOLEH-PRODUK` | ~~`BELUM-JELAS`~~ **`BOLEH-PRODUK` sejak K48 (19 Okt): keputusan owner, bobot dimodifikasi; risiko hukum dicatat** | `docs/lisensi/Megvii-BaseDetection__YOLOX/` · `docs/audit/yolox@4197784.md` |
| `fast-plate-ocr` @ `9ce7a5b` | Pembaca huruf; bagian pembanding | MIT | tidak dinyatakan | tidak dinyatakan | tidak | `BOLEH-PRODUK` | ~~`BELUM-JELAS`~~ **`BOLEH-PRODUK` sejak K47 (19 Okt): pernyataan pemelihara di GitHub diterima owner** | `docs/lisensi/ankandrew__fast-plate-ocr/` · `docs/audit/fast-plate-ocr@9ce7a5b.md` |
| `open-image-models` @ `eaeb588` | Bagian pembanding (pendeteksi plat) | MIT | tidak dinyatakan; pemeliharanya sendiri ragu apakah GPL berlaku | tidak dinyatakan | tidak | `BOLEH-PRODUK` | `BELUM-JELAS` | `docs/lisensi/ankandrew__open-image-models/` · `docs/audit/open-image-models@eaeb588.md` |
| `fast-alpr` @ `aca4ecd` | Pembanding paket jadi | MIT | tidak punya bobot sendiri; memakai bobot dua komponen di atas | tidak berlaku | tidak | `BOLEH-PRODUK` | tidak berlaku (bawaannya memakai bobot `BELUM-JELAS`) | `docs/lisensi/ankandrew__fast-alpr/` · `docs/audit/fast-alpr@aca4ecd.md` |
| `d-fine` @ `956d170` (izin saja) | Pendeteksi ringan cadangan | Apache-2.0 | belum dibaca | belum dibaca | belum diperiksa | `BOLEH-PRODUK` untuk izinnya; dependensi belum diperiksa | `BELUM-JELAS` | `docs/lisensi/Peterande__D-FINE/` |
| `nanodet` @ `d3fb34f` (izin saja) | Pendeteksi ringan cadangan | Apache-2.0 | belum dibaca | belum dibaca | belum diperiksa | `BOLEH-PRODUK` untuk izinnya; dependensi belum diperiksa | `BELUM-JELAS` | `docs/lisensi/RangiLyu__nanodet/` |
| `paddleocr` @ `b03f464` (izin saja) | Pembaca huruf cadangan | Apache-2.0 | belum dibaca | belum dibaca | belum diperiksa | `BOLEH-PRODUK` untuk izinnya; dependensi belum diperiksa | `BELUM-JELAS` | `docs/lisensi/PaddlePaddle__PaddleOCR/` |
| `qwen3-vl` @ `9658872` (izin saja) | Pelabel otomatis (alat lab) | Apache-2.0 | belum dibaca di repo ini | belum dibaca | belum diperiksa | `BOLEH-PRODUK` untuk izinnya; dependensi belum diperiksa | `BELUM-JELAS` | `docs/lisensi/QwenLM__Qwen3-VL/` |

## Yang ditemukan

1. **Kode kesepuluh komponen berizin permisif** (Apache-2.0 atau MIT), dibaca dari berkas `LICENSE` pada commit yang
   dikunci. Tak satu pun dari enam yang diklon bergantung pada `ultralytics`.
2. **Tidak ada satu pun bobot bawaan yang bervonis `BOLEH-PRODUK`.** Sebabnya sama di semua komponen: repo tidak
   menyatakan izin bahan yang melatih bobotnya, dan sebagian (`yolox`, `fast-plate-ocr`, `open-image-models`) tidak
   menyatakan izin bobotnya sama sekali.
3. **Itu tidak menghalangi rancangan** untuk pembaca huruf dan pendeteksi plat: spec 2.3 sudah menetapkan bobotnya
   dilatih sendiri. Yang terkena adalah **bobot awal**: hampir semua pendeteksi dilatih mulai dari bobot yang sudah
   belajar dari COCO, dan RF-DETR memakai backbone DINOv2.
4. **Tiga komponen mengunduh modelnya sendiri saat dipakai tanpa memeriksa keutuhannya** (`fast-plate-ocr`,
   `open-image-models`, dan `yolox`); `rf-detr` memeriksa MD5. Di lab tanpa jaringan unduhan itu gagal, jadi model
   harus diambil lewat pintu unduh berkas dengan SHA-256 yang dicatat (Rencana 3).
5. **Pemindai statis melewatkan sebagian unduhan otomatis**: jalur `urllib.request.urlopen`, `requests.get`, dan
   `torch.hub.load_state_dict_from_url` tidak ditandainya. Semuanya ditemukan dengan pencarian tangan dan dicatat di
   bagian "Dibaca manual" tiap laporan pindai.
6. **`fast-plate-ocr` mencantumkan Indonesia** di daftar wilayah konfigurasi plat Latin
   (`config/latin_plate_config_v2.yaml` baris 22). Akurasinya pada plat Indonesia tidak dinyatakan.

## Keputusan yang harus diambil owner

Aturan ketat di atas membuat **semua bobot awal `BELUM-JELAS`**, sehingga mesin jualan tidak boleh berangkat dari satu
pun di antaranya. Ada dua jalan, dan memilihnya adalah keputusan usaha, bukan keputusan teknis:

| Pilihan | Artinya | Akibatnya |
|---|---|---|
| Tetap ketat | Mesin jualan dilatih dari nol, hanya dengan bahan bersih | Tidak ada keraguan izin. Butuh bahan jauh lebih banyak dan hasilnya kemungkinan lebih lemah; belum diukur |
| Menerima bobot awal yang izin bobotnya dinyatakan permisif | Bobot seperti RF-DETR N–L (ditandai "Apache 2.0" oleh pembuatnya) boleh menjadi titik berangkat mesin jualan, walau izin bahan latihnya tidak dinyatakan | Jalan yang lazim ditempuh, dan sama dengan vonis "CAMPURAN" di vision-seed. Menyisakan keraguan pada bahan latih pihak ketiga, yang sebaiknya ditanyakan ke ahli hukum bersama B9 |

Sampai owner memutuskan, yang berlaku adalah yang ketat: bobot awal hanya dipakai mesin belajar.

**K47 (owner, 19 Okt), untuk bobot fast-plate-ocr saja:** owner menerima pernyataan pemelihara di GitHub ("everything is MIT and
you can use commercially, that includes ... any of the models/weights ... No restrictions") sebagai izin, selama repo aman. Bobot
itu kini `BOLEH-PRODUK`. Yang tetap terbuka: bahan latih bobot terbitan tidak dinyatakan. Bobot lain tetap ketat sampai owner
memutuskan.

**K48 (owner, 19 Okt), untuk bobot YOLOX COCO:** owner memutuskan bobot yang dimodifikasi (dilatih ulang) boleh dijual, dengan
alasan bahwa di Indonesia model yang dimodifikasi dianggap model baru. Agen menyampaikan bahwa anggapan itu belum diperiksa ahli hukum
(UU 28/2014 Pasal 9) dan menyarankan pemeriksaan bersama B9 sebelum penjualan besar. Bobot itu kini `BOLEH-PRODUK`.

## Beda dengan vonis sementara dari survei 13 Okt

| Komponen | Vonis sementara (survei) | Vonis sekarang | Sebabnya |
|---|---|---|---|
| `rf-detr` | Bobot N–L `BOLEH-PRODUK`; Atto, Femto, Pico, XL, 2XL `DILARANG` | Bobot N–L `BELUM-JELAS`; XL dan 2XL tidak dipakai | Aturan di sini menuntut izin bahan latih dinyatakan, dan repo tidak menyatakannya. Pada commit yang dikunci, README hanya menandai XL dan 2XL sebagai PML; survei membaca cabang `develop` yang lebih baru |
| `yolox` | `BOLEH-PRODUK` | Kode `BOLEH-PRODUK`; bobot `BELUM-JELAS` | Izin bobot tidak dinyatakan di repo. Survei sendiri mencatat "tak ada pernyataan terpisah" tetapi tetap memberi vonis boleh |
| `d-fine` | `BOLEH-PRODUK` (varian COCO saja) | Kode `BOLEH-PRODUK` untuk izinnya; bobot `BELUM-JELAS` | Bobot dan dependensinya belum dibaca dari sumber yang dikunci; survei membacanya dari halaman web |
| `nanodet` | `BOLEH-PRODUK` | Kode `BOLEH-PRODUK` untuk izinnya; bobot `BELUM-JELAS` | Sama |
| `paddleocr` | `BOLEH-PRODUK` | Kode `BOLEH-PRODUK` untuk izinnya; bobot `BELUM-JELAS` | Sama |
| `qwen3-vl` | `BOLEH-PRODUK` (alat lab) | Kode `BOLEH-PRODUK` untuk izinnya; bobot `BELUM-JELAS` | Bobotnya belum dibaca dari repo ini; vonisnya ada di kunci vision-seed |

`fast-alpr`, `fast-plate-ocr`, `open-image-models`, dan `trackers`: tidak berbeda.

## Batas

- Empat komponen "izin saja" belum diklon: dependensi dan bobotnya belum dibaca.
- Teks izin PML 1.0, syarat COCO, dan syarat DINOv2 tidak dibaca.
- Pernyataan pemelihara di issue dicatat sebagai keterangan, bukan sebagai izin.
- Belum ada komponen yang dipasang atau dijalankan.

## Dataset (Rencana 4, 14 Okt 2026)

Vonis di bawah ini soal **hak cipta**. Plat kendaraan orang lain adalah data pribadi; soal itu owner menyatakan sudah
berkonsultasi dengan pihak hukum (K21, 14 Okt; `OPEN-QUESTIONS.md` B9). Agen tidak melihat hasil konsultasinya.

| Bahan | Izin yang tertulis | Bukti | Vonis | Syarat dan batas |
|---|---|---|---|---|
| INDO-ALPR, bagian `original` | CC BY 4.0 | [`lisensi/dataset__indo-alpr/IZIN.md`](lisensi/dataset__indo-alpr/IZIN.md) | `BOLEH-PRODUK` | Menyebut sumber, menautkan izin, menandai perubahan. Folder `augmentation` tidak dipakai |
| Indonesian License Plate Lighting Dataset | CC BY 4.0, tanpa berkas LICENSE | [`lisensi/dataset__plat-lighting/IZIN.md`](lisensi/dataset__plat-lighting/IZIN.md) | `BOLEH-PRODUK` | Menyebut sumber. Pernyataan izin hanya di README dan `data.yaml` |
