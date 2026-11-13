# Draf permintaan izin tertulis: bobot fast-plate-ocr (K26)

> **Status: DISETUJUI OWNER 15 Okt 2026 (K27), BELUM DIKIRIM.** Ditulis agen 15 Okt (Rencana 9 Task 6). Owner mengirimnya
> sendiri sebagai issue baru di GitHub fast-plate-ocr, pada waktu yang owner pilih. Isian `<NAMA PENGIRIM>` dan
> `<NAMA USAHA>` diisi owner saat mengirim. Pekerjaan tidak menunggu pesan ini.

## Kenapa pesan ini perlu

- K26: mesin baca huruf kita dibuat dengan melatih ulang `cct_s_v2_global` milik fast-plate-ocr dengan plat Indonesia,
  lalu dijalankan di server kita sebagai layanan berbayar (K25).
- Kode fast-plate-ocr berizin MIT (`BOLEH-PRODUK`). Bobotnya `BELUM-JELAS`, karena rilis `arg-plates` tidak memuat
  berkas izin untuk bobot (`docs/VONIS-LISENSI.md`).
- Satu-satunya pernyataan pemelihara ada di issue repo lain. Izin tertulis yang menjawab rencana kita secara langsung
  akan mengubah vonis bobot itu.

## Yang sudah dibaca dari sumbernya (15 Okt 2026, API GitHub, hanya membaca)

| Sumber | Isi | Status |
|---|---|---|
| [open-image-models#20](https://github.com/ankandrew/open-image-models/issues/20#issuecomment-4653891541), komentar `ankandrew` (OWNER), 8 Jun 2026 | "Hi, from my end everything is MIT and you can use commercially, that includes source code here and any of the models/weights of https://github.com/ankandrew/fast-plate-ocr. No restrictions. [...] I'm no expert in legals." | Issue ditutup |
| [fast-plate-ocr#98](https://github.com/ankandrew/fast-plate-ocr/issues/98), dibuka orang lain 12 Okt 2026 | Menanyakan izin bobot `cct_s_v2_global.onnx` dan data latihnya, untuk produk komersial | Terbuka, **0 jawaban** |
| [fast-plate-ocr#89](https://github.com/ankandrew/fast-plate-ocr/issues/89#issuecomment-4364146685), jawaban `ankandrew` (OWNER), 2 Mei 2026 | Model OCR dilatih dengan "custom dataset + synthetic data" | Issue ditutup |

## Pilihan saluran (keputusan owner)

| Saluran | Untungnya | Akibatnya |
|---|---|---|
| Komentar di issue #98 | Pertanyaannya sudah ada di sana; jawabannya berguna bagi semua yang bertanya | Publik: rencana kita (Indonesia, layanan gerbang berbayar) terbaca siapa saja |
| Issue baru di fast-plate-ocr | Pertanyaan khusus kita, mudah dirujuk sebagai bukti | Publik, sama seperti di atas |
| Surel pribadi ke pemelihara | Rencana kita tidak terbaca umum | Alamat surelnya belum dicari; jawaban pribadi lebih sulit ditunjukkan sebagai bukti kepada pihak ketiga |

## Pesan (bahasa Inggris, yang dikirim)

> **Title:** Permission to fine-tune the `cct_s_v2_global` weights for a commercial, server-side service
>
> Hi @ankandrew,
>
> Thank you for fast-plate-ocr. We are `<NAMA USAHA>`, a small team in Indonesia building a gate-access service that
> reads vehicle license plates.
>
> We would like to fine-tune the published `cct_s_v2_global` weights (the `.keras` file from the `arg-plates` release) on
> Indonesian license plates, and use the fine-tuned model in a paid service. The model would run only on our own
> servers: customers send a photo and receive a result. We would not distribute the model files.
>
> In open-image-models#20 (8 June 2026) you wrote that "everything is MIT and you can use commercially, that includes
> source code here and any of the models/weights of fast-plate-ocr. No restrictions." The release itself does not state a
> license for the weights, and #98 asks a similar question, so we would like to confirm this in writing for our records:
>
> 1. May we fine-tune `cct_s_v2_global` and use the resulting model commercially, as described above?
> 2. Are there any conditions you would like us to follow, for example attribution in our documentation or keeping the
>    MIT notice?
> 3. As far as you know, does any of the data used to train these weights (the custom dataset and synthetic data you
>    mentioned in #89) come with terms that would restrict commercial use of a fine-tuned model?
>
> If it is easy for you, a one-line license statement for the weights in the release notes would also help other users.
>
> Thank you again for your work.
>
> `<NAMA PENGIRIM>`
> `<NAMA USAHA>`

## Terjemahan (untuk owner, tidak dikirim)

> **Judul:** Izin melatih ulang bobot `cct_s_v2_global` untuk layanan berbayar yang berjalan di server
>
> Halo @ankandrew,
>
> Terima kasih atas fast-plate-ocr. Kami `<NAMA USAHA>`, tim kecil di Indonesia yang membangun layanan akses gerbang
> dengan membaca plat nomor kendaraan.
>
> Kami ingin melatih ulang bobot `cct_s_v2_global` yang Anda terbitkan (berkas `.keras` dari rilis `arg-plates`) dengan
> plat nomor Indonesia, lalu memakai model hasilnya dalam layanan berbayar. Model itu hanya berjalan di server kami
> sendiri: pelanggan mengirim foto dan menerima hasilnya. Berkas modelnya tidak kami bagikan.
>
> Di open-image-models#20 (8 Juni 2026) Anda menulis bahwa "semuanya MIT dan boleh dipakai komersial, termasuk kode di
> sini dan semua model/bobot fast-plate-ocr. Tanpa batasan." Rilisnya sendiri tidak menyebut izin untuk bobot, dan #98
> menanyakan hal serupa, jadi kami ingin memastikannya secara tertulis untuk arsip kami:
>
> 1. Bolehkah kami melatih ulang `cct_s_v2_global` dan memakai model hasilnya secara komersial seperti di atas?
> 2. Adakah syarat yang Anda minta, misalnya menyebut sumber di dokumentasi kami atau menyertakan pemberitahuan MIT?
> 3. Sepengetahuan Anda, apakah ada bahan latih bobot ini (dataset sendiri dan data sintetis yang Anda sebut di #89) yang
>    syaratnya membatasi pemakaian komersial model hasil latih ulang?
>
> Bila tidak merepotkan, satu baris pernyataan izin bobot di catatan rilis juga akan membantu pemakai lain.
>
> Sekali lagi terima kasih atas karya Anda.
>
> `<NAMA PENGIRIM>`
> `<NAMA USAHA>`

## Yang sengaja tidak ada di pesan

- Data plat, nama dataset yang kita pakai, jumlah gambar, dan hasil uji kita.
- Nama lokasi, pelanggan, atau penghuni.
- Janji apa pun yang mengikat owner (harga, waktu, atau kontribusi data).

## Sesudah dijawab

Jawaban disimpan (tautan dan salinan teks) di `docs/lisensi/ankandrew__fast-plate-ocr/`, lalu vonis bobot di
`docs/VONIS-LISENSI.md` ditinjau ulang. Sampai ada jawaban, hasil latih ulang bertanda riset (K15, K21) dan Rencana 10
boleh berjalan.

## Siap tempel (untuk owner)

1. Buka https://github.com/ankandrew/fast-plate-ocr/issues/new (masuk dengan akun GitHub Anda).
2. Kolom judul: `Permission to fine-tune the cct_s_v2_global weights for a commercial, server-side service`
3. Kolom isi: salin teks di bawah, lalu ganti `<NAMA USAHA>` (dua tempat) dan `<NAMA PENGIRIM>` (satu tempat).
4. Sesudah terkirim, beri tahu agen tautannya supaya dicatat.

```text
Hi @ankandrew,

Thank you for fast-plate-ocr. We are <NAMA USAHA>, a small team in Indonesia building a gate-access service that reads vehicle license plates.

We would like to fine-tune the published `cct_s_v2_global` weights (the `.keras` file from the `arg-plates` release) on Indonesian license plates, and use the fine-tuned model in a paid service. The model would run only on our own servers: customers send a photo and receive a result. We would not distribute the model files.

In open-image-models#20 (8 June 2026) you wrote that "everything is MIT and you can use commercially, that includes source code here and any of the models/weights of fast-plate-ocr. No restrictions." The release itself does not state a license for the weights, and #98 asks a similar question, so we would like to confirm this in writing for our records:

1. May we fine-tune `cct_s_v2_global` and use the resulting model commercially, as described above?
2. Are there any conditions you would like us to follow, for example attribution in our documentation or keeping the MIT notice?
3. As far as you know, does any of the data used to train these weights (the custom dataset and synthetic data you mentioned in #89) come with terms that would restrict commercial use of a fine-tuned model?

If it is easy for you, a one-line license statement for the weights in the release notes would also help other users.

Thank you again for your work.

<NAMA PENGIRIM>
<NAMA USAHA>
```
