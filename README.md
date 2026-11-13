# cctvgerbang-seed

Seed untuk **CCTV Gerbang**: kamera CCTV membaca plat nomor kendaraan, lalu gerbang terbuka sendiri untuk
kendaraan yang terdaftar. Produk image processing untuk pasar massal Indonesia.

- **Mulai di sini:** [`ROADMAP.md`](ROADMAP.md) — status dan antrean (sumber tunggal pelacakan), lalu serah terima
  terbaru yang ditunjuknya.
- **Visi, lingkup, keputusan:** [`SEED.md`](SEED.md).
- **Yang belum diputuskan dan belum terbukti:** [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md).
- **Aturan proyek:** [`CLAUDE.md`](CLAUDE.md).
- **Riset dasar (13 Okt 2026):** [`docs/riset/`](docs/riset/) — laporan + dua catatan sumbernya. Tiap angka di
  sana diberi tanda keandalan; baca "Cara membaca angka" di awal laporan.
- **Desain yang disetujui:** [`specs/`](specs/) · **rencana:** [`plans/`](plans/) · **vonis izin:**
  [`docs/VONIS-LISENSI.md`](docs/VONIS-LISENSI.md) · **bukti ukur:** `bukti/` (belum ada; diisi Rencana 5).

Workspace VS Code: `../CCTVGerbang.code-workspace`.

**Status 14 Okt 2026:** spec induk disetujui; Fase 0A berjalan (Rencana 1–4 selesai, Rencana 5 menunggu lampu hijau).
Yang ada: alat bengkel di `tools/`, 100 video riset dan dua dataset plat berizin jual di `data/`. Belum ada mesin baca
plat, belum ada perangkat, belum ada angka akurasi. Rincian di `ROADMAP.md`.

⛔ Foto dan rekaman plat kendaraan adalah data pribadi (UU PDP 27/2022). Simpan hanya di `data/`
(di-`.gitignore`); jangan pernah di-commit atau diunggah ke layanan pihak ketiga.
