# Izin: INDO-ALPR

- **Sumber:** https://data.mendeley.com/datasets/j3256db3fz/1
- **DOI:** 10.17632/j3256db3fz.1 · versi 1 · terbit 7 September 2023
- **Pembuat:** Vriza Wahyu, Nanik Suciati, Chastine Fatichah, Institut Teknologi Sepuluh Nopember
- **Dibaca:** 2026-10-14, dari catatan API publik (`https://data.mendeley.com/public-api/datasets/j3256db3fz`) yang
  diambil lewat `tools\ambil-berkas.ps1 indo-alpr-catatan` dan dibaca `tools/lab/catatan_mendeley.py izin`.

## Izin, apa adanya

```json
{
  "id": "01d9c749-3c4d-4431-9df3-620b2dcfe144",
  "description": "You can share, copy and modify this dataset so long as you give appropriate credit, provide a link to the CC BY license, and indicate if changes were made, but you may not do so in a way that suggests the rights holder has endorsed you or your use of the dataset. Note that further permission may be required for any content within the dataset that is identified as belonging to a third party.",
  "url": "http://creativecommons.org/licenses/by/4.0",
  "category": "Creative",
  "short_name": "CC BY 4.0",
  "full_name": "Creative Commons Attribution 4.0 International"
}
```

## Yang dipakai dan yang tidak

| Bagian | Jumlah | Dipakai |
|---|---|---|
| `original/train` (folder `44fd8100-281c-4dea-9ba8-e6469d256ec3`) | 4.712 | Ya |
| `original/test` (folder `b6eab52b-d6d1-43b9-a073-4c13afe0fe19`) | 1.462 | Ya |
| `augmentation/…` (sepuluh olahan) | 61.747 | Tidak: turunan dari gambar asli, bukan bahan baru |
| `Dataset Analysis.xlsx` (akar) | 1 | Tidak dibuka |

Seluruhnya 67.922 berkas, 7.748.668.962 byte menurut catatan penerbit.

## Bacaan agen

CC BY 4.0 membolehkan berbagi, menyalin, dan mengubah dataset ini, termasuk untuk tujuan komersial. Syaratnya tiga:
menyebut sumber dengan layak, menautkan izin CC BY, dan menandai bila ada perubahan; dan tidak boleh memberi kesan
bahwa pemilik hak mendukung kita. Satu kalimat membatasi: "further permission may be required for any content within
the dataset that is identified as belonging to a third party". Catatan penerbit tidak menandai satu isi pun sebagai
milik pihak ketiga. **Soal data pribadi:** nama berkasnya adalah nomor plat kendaraan orang lain. Owner menyatakan sudah
berkonsultasi dengan pihak hukum (K21, `OPEN-QUESTIONS.md` B9); nama berkas itu tetap tidak pernah disalin ke repo
(`CLAUDE.md` §4).
