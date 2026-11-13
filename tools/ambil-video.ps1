<#
.SYNOPSIS
  Mengambil video RISET dari YouTube / TikTok dengan yt-dlp, di container terisolasi (keputusan owner K6, K15, K17).

.DESCRIPTION
  Asal: disalin dari vision-seed @3591530 (tools\ambil-video.ps1) pada 2026-10-13 (K14). Yang diubah di sini: perintah
  `suara` dibuang (proyek ini tidak memakai suara), dan image lab dijaga lewat ID-nya di kunci vendor karena repo ini
  tidak membangun image sendiri.

  yt-dlp dijalankan DARI SUMBER yang dikunci dan diaudit (vendor\yt-dlp, commit di tools\vendor.lock.json; laporan audit
  di vision-seed\docs\audit\yt-dlp@3a08bea.md), bukan dari berkas .exe. Tak ada paket yang dipasang: inti yt-dlp tidak
  punya dependensi wajib.

  Janji pintu ini:
  - Container hanya melihat DUA hal dari host: sumber yt-dlp (read-only) dan data\video\riset (tempat menulis).
    Repo, bobot model, kunci SSH, dan berkas host lain tidak terlihat. Tanpa GPU, root filesystem read-only,
    semua capability dicabut. Jaringannya terbuka (alat ini memang pengunduh), jadi isolasi berkaslah yang menjaga.
  - Opsi berisiko yt-dlp dimatikan dan TAK BISA diselundupkan: pintu ini hanya menerima tiga perintah tetap di bawah,
    bukan argumen yt-dlp bebas. Tanpa konfigurasi host, plugin, pembaruan diri, komponen remote, runtime JavaScript,
    maupun --exec.
  - Alat yang tak persis sama dengan yang diaudit TIDAK dijalankan (kode 7): commit harus sama dengan kunci dan
    tak boleh ada berkas yang berubah.
  - Image lab yang ID-nya bukan yang tercatat di kunci TIDAK dijalankan (kode 6).
  - Unduhan yang meninggalkan berkas .part dilaporkan gagal (kode 8), walau pengunduhnya keluar 0.
    BELUM tertangani di pintu ini: pengunduh yang menolak sebelum mulai mengunduh tetap keluar 0, dan pengunduh yang
    gagal bisa meninggalkan berkas .mp4 yang tidak bisa dibuka (terjadi 13 Okt). Karena itu sesudah mengunduh WAJIB:
    tools\lab.ps1 python /kerja/tools/lab/periksa_utuh.py ... ; tools\manifes-video.mjs menolak video baru tanpa itu.
  - Hanya alamat https di YouTube dan TikTok.

  Video hasil unduhan = bahan RISET-SAJA: tinggal di data\ (di-gitignore), tak pernah diunggah, tak masuk build yang dijual.
  Plat nomor di dalamnya adalah data pribadi (CLAUDE.md §4).

  Perintah:
    periksa                        cek alat masih persis seperti yang diaudit (0 = ya, 7 = tidak)
    cari  "<kueri>" [jumlah]       cari di YouTube, hanya daftar (id | detik | kanal | tayangan | judul); bawaan 10
    info  <url>                    keterangan satu video (id | detik | tinggi | lisensi | kanal | tanggal | judul)
    unduh <url> [resolusi-maks]    unduh satu video (mp4, sisi terpendek <= 720 bawaan) + berkas .info.json asal-usulnya

  Bendera di depan perintah:
    -Kering    cetak argumen docker sebagai JSON tanpa menjalankannya (dipakai tools\uji\ambil-video.test.mjs)

.EXAMPLE
  powershell -NoProfile -File tools\ambil-video.ps1 cari "palang parkir otomatis baca plat nomor" 15
.EXAMPLE
  powershell -NoProfile -File tools\ambil-video.ps1 unduh https://www.youtube.com/watch?v=XXXXXXXXXXX 1080
#>
$ErrorActionPreference = 'Stop'
$image = 'vision-seed-lab:v1'
$akar = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$alat = if ($env:VS_ALAT_YTDLP) { $env:VS_ALAT_YTDLP } else { Join-Path $akar 'vendor\yt-dlp' }
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
# Untuk uji rantai (tools\uji\ambil-video.test.mjs): program docker dan folder keluaran bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$HOST_BOLEH = @('www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be', 'www.tiktok.com', 'tiktok.com', 'vt.tiktok.com', 'vm.tiktok.com')
$JUMLAH_BAWAAN = 10; $JUMLAH_MAKS = 50
$TINGGI_BAWAAN = 720; $TINGGI_MIN = 144; $TINGGI_MAKS = 2160
$PAKAI = 'Pakai: tools\ambil-video.ps1 [-Kering] periksa | cari "<kueri>" [jumlah] | info <url> | unduh <url> [resolusi-maks]'

function Test-Alat {
    # Alat dijalankan hanya bila PERSIS yang diaudit: commit = kunci, dan tak ada berkas yang berubah sesudahnya.
    $sha = (Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).repo | Where-Object { $_.nama -eq 'yt-dlp' } | ForEach-Object { $_.sha }
    if (-not $sha) { Write-Host 'DITOLAK: yt-dlp tidak ada di kunci vendor.'; return $false }
    $ErrorActionPreference = 'Continue'
    $head = git -C $alat rev-parse HEAD 2>$null
    $ubah = git -C $alat status --porcelain 2>$null
    $ErrorActionPreference = 'Stop'
    if ("$head".Trim() -ne $sha) {
        Write-Host "DITOLAK: $alat berada di '$head', bukan commit yang diaudit ($sha). Jalankan: tools\klon-terkunci.ps1 -Nama yt-dlp"
        return $false
    }
    if ($ubah) {
        Write-Host "DITOLAK: isi $alat berubah sesudah diaudit:"; $ubah | ForEach-Object { Write-Host "  $_" }
        return $false
    }
    return $true
}

function Test-Url([string]$url) {
    if ($url.StartsWith('-')) { return $false }
    $u = $null
    if (-not [System.Uri]::TryCreate($url, [System.UriKind]::Absolute, [ref]$u)) { return $false }
    return ($u.Scheme -eq 'https') -and ($HOST_BOLEH -contains $u.Host.ToLowerInvariant())
}

$sisa = @($args)
$kering = $false
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Kering') { $kering = $true; $sisa = @($sisa | Select-Object -Skip 1) }
if ($sisa.Count -eq 0) { Write-Host $PAKAI; exit 2 }
$perintah = $sisa[0]

if ($perintah -eq 'periksa') {
    if (Test-Alat) { Write-Host "alat sesuai kunci: $alat"; exit 0 } else { exit 7 }
}

# Opsi yang sama untuk semua perintah: tanpa konfigurasi host, plugin, runtime JS, komponen remote, pembaruan, cache, --exec.
$aman = @('--ignore-config', '--no-plugin-dirs', '--no-js-runtimes', '--no-remote-components', '--no-update',
    '--no-cache-dir', '--no-exec', '--no-progress', '--socket-timeout', '30', '--retries', '3')

switch ($perintah) {
    'cari' {
        if ($sisa.Count -lt 2 -or $sisa.Count -gt 3) { Write-Host $PAKAI; exit 2 }
        $jumlah = $JUMLAH_BAWAAN
        if ($sisa.Count -eq 3 -and -not [int]::TryParse($sisa[2], [ref]$jumlah)) { Write-Host 'DITOLAK: jumlah harus angka.'; exit 2 }
        if ($jumlah -lt 1 -or $jumlah -gt $JUMLAH_MAKS) { Write-Host "DITOLAK: jumlah 1-$JUMLAH_MAKS."; exit 2 }
        $khusus = @('--flat-playlist', '--skip-download', '--print', '%(id)s | %(duration)s | %(channel)s | %(view_count)s | %(title)s',
            ('ytsearch{0}:{1}' -f $jumlah, $sisa[1]))
    }
    'info' {
        if ($sisa.Count -ne 2) { Write-Host $PAKAI; exit 2 }
        if (-not (Test-Url $sisa[1])) { Write-Host "DITOLAK: hanya alamat https YouTube/TikTok ($($HOST_BOLEH -join ', '))."; exit 2 }
        $khusus = @('--no-playlist', '--skip-download', '--print',
            '%(id)s | %(duration)s | %(height)s | %(license)s | %(channel)s | %(upload_date)s | %(title)s', $sisa[1])
    }
    'unduh' {
        if ($sisa.Count -lt 2 -or $sisa.Count -gt 3) { Write-Host $PAKAI; exit 2 }
        if (-not (Test-Url $sisa[1])) { Write-Host "DITOLAK: hanya alamat https YouTube/TikTok ($($HOST_BOLEH -join ', '))."; exit 2 }
        $tinggi = $TINGGI_BAWAAN
        if ($sisa.Count -eq 3 -and -not [int]::TryParse($sisa[2], [ref]$tinggi)) { Write-Host 'DITOLAK: tinggi harus angka.'; exit 2 }
        if ($tinggi -lt $TINGGI_MIN -or $tinggi -gt $TINGGI_MAKS) { Write-Host "DITOLAK: tinggi $TINGGI_MIN-$TINGGI_MAKS."; exit 2 }
        # Satu berkas mp4 tanpa perlu digabung (image lab tak punya ffmpeg): video saja, atau gabungan bila hanya itu yang ada.
        # Batas memakai urutan `res` (sisi TERPENDEK), bukan saringan `height`: video tegak 576x1024 bertinggi 1024, dan
        # saringan height<=720 menolak semua formatnya. `-S res:N` memilih yang terbaik <= N, atau yang terkecil bila semua lebih besar.
        # Batas ukuran dinaikkan 400m -> 1g pada 26 Okt 2026, dengan sengaja dan tetap BERBATAS.
        # Sebabnya: owner memberi satu rekaman pintu masuk parkir berpalang sepanjang SATU JAM (K76) — bahan
        # pertama yang panjang dan menerus, dan itulah yang dibutuhkan untuk menguji pengelompokan kedatangan
        # (K75). Di 720p ia 420 MB, hanya 0,05% di atas batas lama, dan pintu ini menolaknya. Mengunduhnya di
        # resolusi lebih rendah menghasilkan berkas 640x360 yang tidak cukup untuk membaca plat.
        # Batas ini BUKAN pagar lisensi atau pagar isi — ia hanya membatasi berapa banyak yang boleh ditulis
        # container berjaringan ini ke satu folder. 1g masih membatasi; yang dicabut hanya angkanya.
        $khusus = @('--no-playlist', '--write-info-json', '--restrict-filenames', '--no-overwrites', '--max-filesize', '1g',
            '--paths', '/keluar', '-o', '%(extractor)s-%(id)s.%(ext)s', '-f', 'bv*[ext=mp4]/b[ext=mp4]/b', '-S', "res:$tinggi", $sisa[1])
    }
    default { Write-Host "DITOLAK: perintah '$perintah' tak dikenal. $PAKAI"; exit 2 }
}

$riset = if ($env:VS_KELUAR) { $env:VS_KELUAR } else { Join-Path $akar 'data\video\riset' }
New-Item -ItemType Directory -Force $riset | Out-Null
$argumen = @('run', '--rm', '--read-only', '--tmpfs', '/tmp:rw,exec,size=1g', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--network', 'bridge',
    '--env', 'HOME=/tmp', '--env', 'PYTHONPATH=/alat', '--env', 'PYTHONDONTWRITEBYTECODE=1', '--env', 'YTDLP_NO_PLUGINS=1',
    '--mount', "type=bind,source=$alat,target=/alat,readonly",
    '--mount', "type=bind,source=$riset,target=/keluar",
    '--workdir', '/keluar', $image, 'python', '-m', 'yt_dlp') + $aman + $khusus

if ($kering) { ConvertTo-Json -InputObject $argumen -Compress; exit 0 }

if (-not (Test-Alat)) { exit 7 }
# Image lab dijaga lewat ID-nya di kunci vendor. Repo ini tidak membangun image sendiri (K14), jadi yang dijamin adalah
# "image yang dijalankan persis yang dicatat". Tak tercatat, tak ada di mesin, atau berbeda = tidak dijalankan (kode 6).
$idKunci = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).image_lab.id
$ErrorActionPreference = 'Continue'
$idImage = & $docker image inspect $image --format '{{.Id}}' 2>$null
$ErrorActionPreference = 'Stop'
if (-not $idKunci -or "$idImage".Trim() -ne $idKunci) {
    Write-Host "IMAGE TAK SESUAI KUNCI: '$image' ber-ID '$idImage', yang tercatat '$idKunci' (tools\vendor.lock.json, image_lab)."
    exit 6
}

& $docker @argumen
$kode = $LASTEXITCODE
if ($kode -eq 0 -and $perintah -eq 'unduh') {
    # Kode 0 dari pengunduh bukan bukti berkasnya utuh: unduhan yang terpotong di --max-filesize keluar 0 dan
    # meninggalkan berkas .part. Yang dinilai adalah berkasnya.
    $terpotong = @(Get-ChildItem -LiteralPath $riset -Filter '*.part' -File)
    if ($terpotong.Count -gt 0) {
        Write-Host ("UNDUHAN TERPOTONG: pengunduh keluar 0, tetapi berkas ini belum utuh: {0}. Hapus berkas itu, lalu ulangi dengan resolusi lebih rendah." -f (($terpotong | ForEach-Object { $_.Name }) -join ', '))
        exit 8
    }
}
exit $kode
