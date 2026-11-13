<#
.SYNOPSIS
  Mengambil SATU berkas yang tercatat di kunci (arsip atau catatan dataset, atau berkas model untuk alat lab), di container
  terisolasi (spec bagian 8.6).

.DESCRIPTION
  Janji pintu ini:
  - Yang diambil hanya butir yang tercatat di daftar "berkas" pada tools\vendor.lock.json. Pintu ini tidak menerima
    alamat dari baris perintah.
  - Hanya https, dan hanya host di $HOST_BOLEH. Menambah host berarti mengubah berkas ini dan ujinya, bukan sekadar
    menambah baris di kunci. Pengalihan diperiksa ulang oleh pengunduhnya.
  - Container hanya melihat DUA hal dari host: tools\ambil (read-only) dan data\unduhan\<nama> (tempat menulis).
    Repo, bobot model, kunci SSH, dan berkas host lain tidak terlihat. Tanpa GPU, root filesystem read-only, semua
    capability dicabut. Jaringannya terbuka (alat ini memang pengunduh), jadi isolasi berkaslah yang menjaga.
  - Image lab yang ID-nya bukan yang tercatat di kunci TIDAK dijalankan (kode 6).
  - Berhasil atau tidaknya dinilai dari BERKASNYA: sisa .part = gagal (kode 8); pengunduh keluar 0 tanpa berkas jadi
    = gagal (kode 9).
  - Butir yang sha256-nya kosong boleh diunduh sekali untuk diukur, tetapi belum boleh dibuka:
    tools\lab\buka_arsip.py menuntut --sha256.

  Berkas hasil unduhan tinggal di data\ (di-gitignore). Dataset plat memuat data pribadi (CLAUDE.md §4).

  Bendera di depan perintah:
    -Kering    cetak argumen docker sebagai JSON tanpa menjalankannya (dipakai tools\uji\ambil-berkas.test.mjs)

  Kode keluar: 0 berhasil · 2 ditolak atau salah pakai · 6 image tak sesuai kunci · 7 SHA-256 tak cocok ·
  8 unduhan terpotong · 9 tak ada berkas jadi · lainnya = kode dari pengunduh.

.EXAMPLE
  powershell -NoProfile -File tools\ambil-berkas.ps1 plat-lighting
#>
$ErrorActionPreference = 'Stop'
$image = 'vision-seed-lab:v1'
$akar = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$alat = Join-Path $PSScriptRoot 'ambil'
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
# Untuk uji rantai (tools\uji\ambil-berkas.test.mjs): program docker dan folder dasar keluaran bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$dasarKeluar = if ($env:VS_KELUAR) { $env:VS_KELUAR } else { Join-Path $akar 'data\unduhan' }
$HOST_BOLEH = @('data.mendeley.com', 'prod-dcd-datasets-cache-zipfiles.s3.eu-west-1.amazonaws.com', 'codeload.github.com',
    'github.com', 'release-assets.githubusercontent.com')
$MAKS_GB = 20
$PAKAI = 'Pakai: tools\ambil-berkas.ps1 [-Kering] <nama>   (nama dari daftar "berkas" di tools\vendor.lock.json)'

$sisa = @($args)
$kering = $false
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Kering') { $kering = $true; $sisa = @($sisa | Select-Object -Skip 1) }
if ($sisa.Count -ne 1) { Write-Host $PAKAI; exit 2 }
$nama = [string]$sisa[0]
if ($nama -cnotmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Host "DITOLAK: nama '$nama' hanya boleh huruf kecil, angka, dan tanda hubung."
    exit 2
}

$butir = @((Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).berkas | Where-Object { $_.nama -eq $nama })
if ($butir.Count -ne 1) { Write-Host "DITOLAK: '$nama' tidak tercatat tepat sekali di daftar berkas pada kunci vendor."; exit 2 }
$b = $butir[0]
$u = $null
if (-not [System.Uri]::TryCreate([string]$b.url, [System.UriKind]::Absolute, [ref]$u) -or $u.Scheme -ne 'https' -or
    ($HOST_BOLEH -notcontains $u.Host.ToLowerInvariant())) {
    Write-Host "DITOLAK: alamat '$nama' harus https di host yang didaftar ($($HOST_BOLEH -join ', '))."
    exit 2
}
$berkasJadi = [string]$b.berkas
if ($berkasJadi -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') { Write-Host "DITOLAK: nama berkas jadi '$berkasJadi' tidak sah."; exit 2 }
$sha = [string]$b.sha256
if ($sha -and $sha -cnotmatch '^[0-9a-f]{64}$') { Write-Host "DITOLAK: sha256 '$nama' di kunci bukan 64 huruf heksa kecil."; exit 2 }
$gb = 0.0
$angka = [System.Globalization.NumberStyles]::Float
$budaya = [System.Globalization.CultureInfo]::InvariantCulture
if (-not [double]::TryParse([string]$b.maks_gb, $angka, $budaya, [ref]$gb) -or $gb -le 0 -or $gb -gt $MAKS_GB) {
    Write-Host "DITOLAK: maks_gb '$nama' harus angka di atas 0 dan paling banyak $MAKS_GB."
    exit 2
}
$maksByte = [long]($gb * 1GB)

$keluar = Join-Path $dasarKeluar $nama
$argumen = @('run', '--rm', '--read-only', '--tmpfs', '/tmp:rw,size=64m', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--network', 'bridge',
    '--env', 'HOME=/tmp', '--env', 'PYTHONDONTWRITEBYTECODE=1',
    '--mount', "type=bind,source=$alat,target=/alat,readonly",
    '--mount', "type=bind,source=$keluar,target=/keluar",
    '--workdir', '/keluar', $image, 'python', '-I', '/alat/ambil_berkas.py',
    '--alamat', [string]$b.url, '--keluar', '/keluar', '--nama', $berkasJadi, '--maks-byte', "$maksByte")
foreach ($h in $HOST_BOLEH) { $argumen += @('--host', $h) }
if ($sha) { $argumen += @('--sha256', $sha) }

if ($kering) { ConvertTo-Json -InputObject $argumen -Compress; exit 0 }

New-Item -ItemType Directory -Force $keluar | Out-Null
# Image lab dijaga lewat ID-nya di kunci vendor: tak tercatat, tak ada di mesin, atau berbeda = tidak dijalankan.
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
if ($kode -ne 0) { exit $kode }
# Kode 0 dari pengunduh bukan bukti. Yang dinilai adalah berkasnya.
$terpotong = @(Get-ChildItem -LiteralPath $keluar -Filter '*.part' -File)
if ($terpotong.Count -gt 0) {
    Write-Host ("UNDUHAN TERPOTONG: pengunduh keluar 0, tetapi berkas ini belum utuh: {0}." -f (($terpotong | ForEach-Object { $_.Name }) -join ', '))
    exit 8
}
if (-not (Test-Path -LiteralPath (Join-Path $keluar $berkasJadi) -PathType Leaf)) {
    Write-Host "TAK ADA BERKAS JADI: pengunduh keluar 0, tetapi '$berkasJadi' tidak ada di $keluar."
    exit 9
}
if (-not $sha) {
    Write-Host "BELUM DIKUNCI: catat SHA256 di atas pada butir '$nama' di tools\vendor.lock.json, lalu jalankan lagi. Berkas yang belum dikunci tidak boleh dibuka."
}
exit 0
