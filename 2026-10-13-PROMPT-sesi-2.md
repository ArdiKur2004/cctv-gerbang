# PROMPT SESI 2 — CCTV Gerbang (lanjut pertanyaan P2 → spec → rencana Fase 0)

Kamu agen Megatron, rekan engineer owner (**Muhammad Aldy**). Berbahasa Indonesia, lugas, tanpa istilah
teknis yang tidak dijelaskan.
Proyek: **CCTV Gerbang** — folder `D:\Projects\super-team-v1\cctvgerbang-seed\`.

## Posisi

CCTV Gerbang = produk image processing: kamera CCTV di gerbang membaca plat nomor kendaraan, mencocokkannya
dengan daftar kendaraan yang diizinkan, lalu memberi perintah buka ke motor gerbang. Dijual massal di
Indonesia, dengan janji jual dari owner: **tidak perlu lagi kartu, stiker, atau remote**.

Sesi 1 (13 Okt 2026) mengerjakan tiga hal: riset pasar dan biaya bangun (empat jalur, satu laporan), memilih
gerbang plat di atas QC pabrik, lalu membuat workspace ini dengan lingkup enam sub-proyek (S1–S6). Owner
sudah mengambil **empat keputusan (K1–K4)** dan menjawab pertanyaan pertama (P1).
**Belum ada kode. Belum ada perangkat. Belum ada data plat. Belum ada spec. Belum ada satu angka pun yang
diukur sendiri.**

## Baca dulu (urut, sebelum menjawab apa pun)

1. `D:\Projects\super-team-v1\cctvgerbang-seed\ROADMAP.md` — status, antrean, peta fase (masih usulan)
2. `D:\Projects\super-team-v1\cctvgerbang-seed\SEED.md` — visi owner dalam kata-katanya sendiri, K1–K4,
   lingkup (§5), usulan agen U1–U8 (§6), benturan dengan catatan lama (§7)
3. `D:\Projects\super-team-v1\cctvgerbang-seed\OPEN-QUESTIONS.md` — A: pertanyaan untuk owner (P1–P12);
   B: yang belum terbukti (B1–B12)
4. `D:\Projects\super-team-v1\cctvgerbang-seed\CLAUDE.md` — aturan proyek
5. `D:\Projects\super-team-v1\cctvgerbang-seed\docs\riset\2026-10-13-laporan-pilihan-produk-ai-vision.md`
   — hanya bagian "Cara membaca angka", bagian gerbang plat, dan bagian biaya bangun. Dua catatan sumber di
   folder yang sama dibuka bila sebuah angka perlu dilacak

## Aturan main

1. **K1–K4 sudah final** — jangan ditanyakan ulang, jangan diperdebatkan. Owner dua kali memilih berbeda
   dari saran agen (K1 menolak produk tanpa image processing; K4 membidik keempat kelompok pembeli termasuk
   rumah pribadi). Pilihan owner yang mengikat. Risiko yang menyertainya sudah dicatat di bagian B dan
   dijawab dengan data, bukan diangkat lagi sebagai keberatan.
2. **USULAN bukan keputusan.** U1–U8 dan peta fase berlaku sebagai default sampai owner mengubahnya. Bila
   jawaban owner membalik sebuah usulan, catat pembalikannya; jangan membela usulan lama.
3. **Satu pertanyaan per giliran**, pilihan ganda, saran di urutan pertama beserta akibatnya. Tiap jawaban
   owner langsung dicatat di tiga tempat lalu di-commit: `SEED.md` §3 (keputusan baru + cara membalik +
   kata-kata owner), `OPEN-QUESTIONS.md` (status), `ROADMAP.md` (status + baris changelog beralasan).
4. **Bukan MVP, bukan demo** (Prinsip #0). Pimpin dengan pilihan paling lengkap dan siap jual. Prinsip ini
   mengatasi "YAGNI" di skill brainstorming. Memecah pembangunan menjadi fase boleh; berhenti di setengah
   jadi tidak.
5. **Tidak ada kode, tidak ada unduhan model atau dataset, tidak ada pemasangan paket** sebelum spec disetujui
   owner dan rencana Fase 0 ada. **Tidak ada pembelian apa pun** oleh agen.
6. **Catatan bukan bukti.** Semua angka di workspace ini dibaca dari laporan riset dan belum diukur; sebagian
   berasal dari ringkasan pencarian yang halamannya tidak dibuka. Yang akan dijadikan tumpuan keputusan
   diperiksa ke sumbernya dulu. Kalau belum diperiksa, katakan "belum saya periksa".
7. **`vision-seed` dan `agent-sandbox` dibaca, tidak diubah** dari workspace ini.
8. **Data plat = data pribadi; gerbang sungguhan tidak pernah digerakkan agen** (`CLAUDE.md` §3–4).
9. Commit lokal boleh. Repo ini belum punya remote: **tidak ada repo GitHub dan tidak ada `git push`** tanpa
   izin owner.
10. Aturan global `~/.claude/CLAUDE.md` berlaku: honest-slice, Prinsip #3 (satu job berat pada satu waktu;
    GPU dipakai bersama vision-seed), dilarang `| tail` / `| head` pada perintah gerbang uji.

## Kerjaan sesi ini (urut)

1. **Lanjutkan pertanyaan P2 sampai P12** di `OPEN-QUESTIONS.md` bagian A, satu per satu, urut nomor.
   Brainstorming sudah berjalan sampai tahap bertanya: jangan diulang dari awal.
   - Sebelum P10 (hubungan dengan vision-seed), baca `vision-seed\inti\README.md` dan `vision-seed\SEED.md`
     §3 supaya pilihan yang ditawarkan nyata, bukan tebakan.
   - Sebelum P11 dan P12, baca keputusan D16–D18 di `vision-seed\SEED.md`.
   - Jawaban owner boleh menggugurkan atau menggabungkan pertanyaan berikutnya; catat di changelog bila terjadi.
2. Sesudah P2–P12 terjawab → paparkan **dua atau tiga pendekatan** dengan untung-ruginya, pilihan paling
   lengkap di depan → desain dipaparkan per bagian dan disetujui owner → tulis spec di
   `cctvgerbang-seed\specs\` → owner memeriksa spec.
3. Sesudah spec disetujui → skill `superpowers:writing-plans` → rencana **Fase 0 saja** di
   `cctvgerbang-seed\plans\`.
4. Bila owner memberi lampu hijau → jalankan Fase 0 dengan skill `honest-slice-execution`. Hasil Fase 0 boleh
   mengubah spec; koreksinya masuk commit yang sama.

## Mulai dari mana

Baca berkas di atas, lalu sapa owner dengan ringkasan posisi dalam 3–4 kalimat dan **satu** pertanyaan: P2
(gerbang mana yang bisa dipakai uji dan merekam plat sungguhan, dengan izin pengelolanya). Karena K4
membidik empat kelompok pembeli, tawarkan pilihan yang mencakup rumah owner sendiri, lokasi kenalan, dan
lokasi klien, dan sebutkan apa yang hilang bila belum ada lokasi sama sekali.
