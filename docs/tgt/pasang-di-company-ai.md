# Memasang TGT di `company-ai`, tanpa mengganggu MES Yanmar

> Ditulis untuk yang akan memasang TGT di mesin itu. Hasil pemeriksaan **hanya-melihat** pada 26 Okt 2026,
> lewat Tailscale SSH sebagai `{pengguna-ssh-company-ai}`. Tidak ada satu berkas pun yang ditulis ke mesin itu, dan tidak ada
> layanan yang dipasang — pemasangan adalah keputusan owner.
>
> Dasar: K71 (TGT dipasang di PC IBE), K74 (semua data disimpan; jangan mengganggu MES Yanmar).

## 1. Apa yang sebenarnya jalan di sana

`company-ai` bukan mesin khusus MES. Ia mesin serbaguna:

| Yang jalan | Porta | Catatan |
|---|---|---|
| **Odoo** — inilah MES Yanmar | 8069 | `odoo.service` |
| **PostgreSQL 16** | 127.0.0.1:5432 | basis data Odoo |
| Aplikasi Next.js | — | `next-server`, 281 MB memori |
| Docker | — | `dockerd`, 196 MB |
| Chrome + remote debugging | 127.0.0.1:9222 | kemungkinan peramban sekretaris |
| VNC dan noVNC | 5900/5901, 6080 | |
| Tailscale Serve | 443 | ⛔ jangan disentuh |
| tak dikenal | 4400 | pemiliknya butuh root untuk dilihat |

**Odoo sehat:** `/web/login` menjawab **18–57 ms**, dan beban satu menit **0,10** — mesin ini hampir diam.
Angka itu yang harus dibandingkan sesudah TGT jalan.

## 2. Mesinnya: lapang di memori dan disk, LEMAH di prosesor

| | |
|---|---|
| Prosesor | **Intel Celeron J4025, 2 inti, 2,0 GHz** ← satu-satunya yang sempit |
| Memori | 7,3 GB; terpakai 1,6 GB; **tersisa 5,8 GB** |
| Swap | 7,7 GB, hampir tak terpakai |
| Nyala | 50 hari tanpa dinyalakan ulang |
| Node | **v22.23.2** |
| Docker | 29.1.3 |

### Disk, dan kenapa letaknya penting

```
/dev/mapper/ubuntu--vg-ubuntu--lv   40G   24G   14G  65%  /            ← sudah 65%
/dev/mapper/ubuntu--vg-srv--lv      40G  999M   37G   3%  /srv         ← 37 GB kosong
/dev/mapper/ubuntu--vg-erp--lv      12G  301M   11G   3%  /srv/erpdata ← milik ERP
/dev/mapper/ubuntu--vg-log--lv     7.8G  407M  7.0G   6%  /var/log
```

⛔ **TGT harus di `/srv/tgt`, JANGAN di `/home/{pengguna-ssh-company-ai}`.** Folder rumah berada di `/` yang sudah 65% penuh —
dan `/` adalah tempat sistem operasi dan Odoo hidup. `/srv` adalah volume logis **tersendiri**: kalaupun TGT
suatu hari membengkak, ia tidak bisa membuat `/` penuh, dan tidak bisa menyentuh 11 GB milik `/srv/erpdata`.
Pemisahan volume inilah pagar yang paling kuat, lebih kuat daripada pagar mana pun di dalam kode kami.

`{pengguna-ssh-company-ai}` **tidak bisa menulis di `/srv`** tanpa `sudo`, dan `sudo` meminta kata sandi. Jadi langkah 1 di
bawah harus dijalankan owner.

### `/srv/cadangan` sudah ada

Ada `/srv/cadangan/erpxai` (hanya root). Jadi mesin ini **sudah punya kebiasaan cadangan**. Cadangan TGT
sebaiknya ikut ke sana atau ke NAS saat dibeli (K70) — sampai itu ada, TGT menyebut di layar bahwa belum ada
cadangan sama sekali.

## 3. Yang sudah dibuktikan di mesin itu

**Node 22 cukup untuk TGT.** TGT dibangun di Node 24, dan `node:sqlite` masuk sejak Node 22.5 — tetapi itu
diperiksa, bukan diasumsikan. Dijalankan di sana (di memori, tanpa menulis berkas, lalu dihapus):

```
lastInsertRowid: number 1        changes: number 1
ALTER TABLE ADD/DROP COLUMN: bisa     PRAGMA foreign_keys: 1
fs.statfsSync: function          strftime: 2026-10-26T15:53:55
count(DISTINCT ...): bisa
SEMUA YANG DIPAKAI TGT: BISA
```

Yang diperiksa adalah yang memang dipakai TGT: `lastInsertRowid` dan `changes` sebagai angka, `ALTER TABLE`
untuk migrasi naik dan turun, kunci asing, `statfsSync` untuk pagar ruang disk, `strftime` untuk jendela
kedatangan, dan `count(DISTINCT)` untuk beranda.

**Porta 8787 kosong** — bawaan TGT bisa dipakai apa adanya.

## 4. Berapa besar TGT akan tumbuh di sana

Diukur dari basis data sungguhan (190 bita per kejadian):

| Lalu lalang | Catatan setahun | 10 tahun |
|---|---|---|
| 50 kendaraan/hari | 3,3 MB | 33 MB |
| 150 kendaraan/hari | 9,9 MB | 100 MB |
| 400 kendaraan/hari | 26,5 MB | 265 MB |

Dibandingkan 37 GB kosong di `/srv`, **catatan TGT tidak akan pernah menjadi masalah** — bahkan dengan K74
(semua data disimpan selamanya).

**Foto bukti** yang akan besar: 4–42 GB setahun per gerbang tergantung ukuran gambar. Foto itu **belum
dibangun**. Pagarnya sudah ada lebih dulu (`tgt/ruang.mjs`): di bawah 5 GB sisa, TGT berhenti menulis gambar
baru dan **tidak pernah menghapus** catatan lama.

## 4b. Prosesornya diukur: 2–4 kali lebih lambat, dan TANPA AVX

Diukur 26 Okt lewat Node yang sudah terpasang di sana, lewat STDIN — tidak ada berkas yang ditulis ke mesin itu.

| | laptop (Ryzen 7 8700F, 16 inti) | `company-ai` (Celeron J4025, 2 inti) | selisih |
|---|---|---|---|
| bilangan bulat | 230 juta operasi/detik | 120 juta | **1,9× lebih lambat** |
| bilangan pecahan | 1.542 juta operasi/detik | 357 juta | **4,3× lebih lambat** |

**Dan yang lebih menentukan daripada kecepatan: perintah hitung cepat.**

| | sse4_2 | avx | avx2 | fma | avx512 |
|---|---|---|---|---|---|
| `company-ai` | ADA | **tidak ada** | **tidak ada** | **tidak ada** | tidak ada |

onnxruntime — yang menjalankan ketiga mesin di rantai kami — sangat bergantung pada **AVX2 dan FMA**. Tanpa
keduanya ia memakai jalur hitung yang jauh lebih lambat. Jadi selisih 4,3× di atas adalah **batas bawah yang
optimistis** untuk mesin baca; selisih sebenarnya bisa 6–12×.

### Perkiraan, ditandai jelas sebagai perkiraan

Satu gambar butuh **81 ms** di laptop ini. Dengan selisih 6–12×, di `company-ai` kira-kira
**0,5–1 detik per gambar**. Ini **perkiraan**, bukan hasil ukur: perbandingannya dari kerja bilangan di Node,
bukan dari onnxruntime. Angka yang sah hanya didapat dengan menjalankan mesin bacanya di sana.

### Yang sebenarnya menjadi kendala: pengemudi menunggu, BUKAN Odoo

Odoo bisa dilindungi dengan mudah: jalankan mesin baca dengan `nice -n 19`, dan Odoo **selalu menang** saat
prosesornya berebut. Odoo tetap menjawab cepat; yang menjadi lambat hanyalah pembacaan platnya.

Jadi pertanyaannya bergeser: **berapa lama pengemudi menunggu di depan palang.** Rantai membaca beberapa
bingkai per kendaraan, jadi 2–3 bingkai × 0,5–1 detik = **1,5–3 detik** sebelum palang terbuka. Itu masih
masuk akal untuk satu gerbang percontohan, tetapi harus diukur, dan jumlah bingkai per kendaraan adalah
tombol yang paling berpengaruh bila terasa lambat.

### Bila nanti mesinnya di-upgrade (K71: "nanti dipindahkan ke yang lebih besar")

Satu syarat yang jauh lebih berharga daripada jumlah inti: **prosesornya harus punya AVX2 dan FMA.**
Prosesor empat inti ber-AVX2 akan mengalahkan delapan inti tanpa AVX2 untuk pekerjaan ini. Hampir semua
Intel sejak Haswell (2013) dan AMD sejak Zen (2017) punya; yang biasanya **tidak** punya adalah keluarga
Celeron, Pentium Silver, dan Atom. Pembelian adalah keputusan owner (CLAUDE.md §8).

## 4c. Mesin baca DIUKUR di mesin itu — dan Odoo tidak terganggu

Dijalankan 26 Okt dengan izin owner. Satu paket dipasang (`onnxruntime==1.20.1`, hash resmi PyPI, OSV
diperiksa dengan kontrol positif: tidak ada kerentanan), di venv sementara di `/tmp`, `nice -n 19`, lalu
semuanya dihapus dan sisa prosesnya diperiksa.

### Lama satu bingkai, per jumlah utas

| mesin | 1 utas | **2 utas** | 4 utas |
|---|---|---|---|
| pencari kendaraan (`kendaraan-jualan-k1`) | 1.296 ms | **716 ms** | 987 ms |
| pencari plat (`pencari-cctv2-c1`) | 326 ms | **187 ms** | 449 ms |
| pembaca (`pembaca-lanjut-r4`) | 209 ms | **120 ms** | 198 ms |
| **satu bingkai utuh** | 1.831 ms | **1.023 ms** | 1.634 ms |

⛔ **Pakai 2 utas, jangan 4.** Mesinnya 2 inti, dan 4 utas justru **lebih lambat** (1.634 ms lawan 1.023 ms)
karena utasnya berebut inti yang sama. Ini bukan tebakan — ketiga mesin menunjukkan pola yang sama.

**Satu bingkai ≈ 1,0 detik.** Di laptop pengembangan satu gambar butuh 81 ms, jadi mesin ini **12,6× lebih
lambat**. Perkiraan sebelumnya (0,5–1 detik, dari kerja bilangan di Node) ternyata tepat di batas atasnya.

### ⛔ Odoo TIDAK terganggu — ini diukur, bukan dijanjikan

| | Odoo `/web/login` | beban 1 menit |
|---|---|---|
| sebelum | **18 ms** | 0,07 |
| **selama pengukuran** | **25 ms** | 0,39 → naik ke 2,46 |
| sesudah | **20 ms** | 2,46 (menurun) |

Beban naik ke **2,46** — kedua inti benar-benar penuh. Dan Odoo tetap menjawab **25 ms**. Yang membuatnya
begitu adalah `nice -n 19`: sistem operasi selalu memberi prosesor ke Odoo lebih dulu. **Memakai `nice -n 19`
untuk mesin baca adalah syarat, bukan saran.**

Memori tidak bergerak berarti: 1.637 MB terpakai sebelum, 1.632 MB sesudah.

### Yang sebenarnya mahal: pencari kendaraan, 70% dari waktunya

716 ms dari 1.023 ms habis di pencari kendaraan. Itu tombol yang paling berpengaruh bila palang terasa lambat:

| cara | satu bingkai | catatan |
|---|---|---|
| sekarang: kendaraan → plat → baca | **1.023 ms** | menemukan plat paling banyak (Rencana 19, 20) |
| tanpa tahap kendaraan: plat → baca | **307 ms** | **3,3× lebih cepat**, tetapi lebih sedikit plat ditemukan |

Mana yang dipakai adalah **keputusan owner**, karena ia menukar kecepatan palang dengan ketelitian bacaan.
Angka ketelitiannya ada di `bukti/2026-10-16-pencari-plat-cctv.md` dan `bukti/2026-10-17-plat-di-dalam-kendaraan.md`.

### Berapa lama pengemudi menunggu

Rantai membaca beberapa bingkai per kendaraan. Dengan 1,0 detik per bingkai:

- 1 bingkai → **1 detik**
- 2 bingkai → **2 detik**
- 3 bingkai → **3 detik**

Untuk satu gerbang percontohan ini masuk akal. Yang harus diukur berikutnya, dengan rekaman gerbang sungguhan
(K43): berapa bingkai yang benar-benar dibutuhkan sebelum platnya terbaca benar.

## 5. ⛔ Yang BELUM dijawab, dan tidak boleh dianggap beres

**Mesin baca plat belum diukur di prosesor itu.** Membaca satu gambar butuh 81 ms di laptop pengembangan.
Celeron J4025 dua inti jauh lebih lemah, dan **menjalankan inferensi berat di mesin yang menjalankan MES
pabrik adalah pertanyaan rancangan, bukan sekadar pertanyaan kecepatan.** Tiga pilihan:

1. **Mesin baca di kotak gerbang sendiri**, TGT di `company-ai`. Paling aman untuk MES, dan paling masuk akal
   untuk dijual: tiap gerbang membawa kotaknya sendiri.
2. **Keduanya di `company-ai`.** Paling murah untuk percontohan. Harus diukur dulu: kalau membaca satu gambar
   menghabiskan kedua inti selama beberapa detik, Odoo akan terasa berat saat ada kendaraan lewat.
3. **Mesin baca di laptop ini** selama percontohan. Cukup untuk uji, tidak bisa dijual.

Pengukurannya memakai `tools/ukur_onnx_cpu.py` dengan aturan mesin-produksi di `CLAUDE.md` §7 (hanya `/tmp`,
`nice -n 19`, dibersihkan, sisa proses diperiksa, beban dicatat sebelum dan sesudah). Butuh izin owner untuk
menulis berkas ke mesin itu.

**TGT sendiri belum pernah dijalankan di sana.** Yang terbukti baru bahwa Node-nya mendukungnya. Uji coba
sungguhan — menyalin TGT ke `/tmp`, menjalankan 541 ujinya di sana, menyalakannya sebentar di porta 8787, dan
mengukur Odoo sebelum dan selama — sudah disiapkan di
`data/alat-sementara/coba-di-company-ai.sh`, dan **menunggu izin owner** karena ia menulis berkas ke mesin
produksi. Skrip itu tidak memasang layanan, tidak menyentuh `/srv`, dan menghapus jejaknya.

## 6. Langkah memasang, bila owner memutuskan lanjut

```bash
# 1. OWNER (butuh sudo): siapkan tempat di volume /srv yang terpisah
sudo mkdir -p /srv/tgt /srv/tgt/data
sudo chown {pengguna-ssh-company-ai}:{pengguna-ssh-company-ai} /srv/tgt /srv/tgt/data

# 2. Salin TGT (dari laptop ini)
#    Hanya folder tgt/ dan package.json. JANGAN menyalin data/ — isinya plat nomor (§4).
scp -r tgt package.json {pengguna-ssh-company-ai}@{ip-company-ai}:/srv/tgt/

# 3. Jalankan ujinya DI SANA lebih dulu, sebelum dipercaya
cd /srv/tgt && nice -n 19 node --test "tgt/uji/*.test.mjs"

# 4. Coba jalankan dengan tangan, bukan sebagai layanan
cd /srv/tgt && TGT_BASIS=/srv/tgt/data/tgt.sqlite TGT_FOTO=/srv/tgt/data/foto \
  TGT_PORTA=8787 TGT_ALAMAT=127.0.0.1 nice -n 19 node tgt/server.mjs
#    Periksa kalimat pembukanya: ruang disk, masa simpan SELAMANYA, cadangan belum diatur.
#    Lalu ukur Odoo lagi: harus tetap 18–57 ms.

# 5. HTTPS lewat Tailscale, tailnet saja — JANGAN Funnel, dan JANGAN porta 443 atau 8443
#    (keduanya sudah dipakai layanan owner yang lain, dan 443 di sini sudah terbuka ke internet)
sudo tailscale serve --bg --https=8445 http://127.0.0.1:8787
```

**Yang tidak boleh dilakukan:**

- ⛔ jangan menyentuh porta **8069** (Odoo), **5432** (PostgreSQL), **443**, **4400**, **6080**, **9222**;
- ⛔ jangan menyalakan **Tailscale Funnel** untuk TGT — itu membukanya ke internet;
- ⛔ jangan menaruh data TGT di `/home/{pengguna-ssh-company-ai}` atau di mana pun di `/`;
- ⛔ jangan menyalin `data/` dari laptop ini: isinya nomor plat (CLAUDE.md §4);
- ⛔ jangan memasang layanan systemd sebelum langkah 4 terbukti dan Odoo terukur tidak terganggu.
