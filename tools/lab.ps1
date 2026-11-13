<#
.SYNOPSIS
  Satu-satunya pintu menjalankan lab CCTV Gerbang: container lab, GPU, TANPA jaringan.

.DESCRIPTION
  Asal: disalin dari vision-seed @3591530 (tools\lab.ps1) pada 2026-10-13 (K14). Yang diubah di sini: mode -Kamera,
  mode -Jaringan, dan gudang aset dibuang (belum dibutuhkan Fase 0A), dan image lab dijaga lewat ID-nya di kunci vendor
  karena repo ini tidak membangun image sendiri.

  Janji pintu ini:
  - Container jalan dengan --network none. Kode pihak ketiga tak bisa "menelepon pulang".
  - Repo di-mount READ-ONLY ke /kerja. Hanya data\keluaran\ yang bisa ditulis.
  - Tak ada berkas host lain (~/.ssh, kredensial proyek lain) yang terlihat dari dalam container.
  - Root filesystem container read-only, semua capability dicabut, tanpa naik hak akses.
  - Image lab yang ID-nya bukan yang tercatat di tools\vendor.lock.json TIDAK dijalankan (kode 6).

  KUNCI BENGKEL (PRINSIP #3, satu job lab pada satu waktu): named mutex Windows yang SENGAJA sama dengan milik
  vision-seed, karena kedua proyek memakai satu kartu grafis. Job lab keduanya saling menunggu, tak pernah jalan
  bersamaan. Mutex otomatis lepas bila prosesnya mati, jadi tak ada kunci basi. Bila menunggu lebih dari
  VS_KUNCI_TUNGGU_DTK (bawaan 1800), keluar dengan kode 3 = bengkel sibuk, BUKAN uji merah.

  Bendera di depan perintah:
    -Kering    cetak argumen docker sebagai JSON tanpa menjalankannya (dipakai tools\uji\lab.test.mjs)
    -Fpo       jalankan image lab tambahan cctvgerbang-lab-fpo:v1 (K26; ID dari kunci image_lab_fpo). Janji pintu sama.
               Urutannya: -Kering (bila ada) lalu -Fpo.

  Catatan: skrip ini sengaja tanpa blok param(). Dengan `powershell -File`, argumen seperti `-m` milik pytest akan
  dianggap parameter PowerShell bila ada blok param().

.EXAMPLE
  powershell -NoProfile -File tools\lab.ps1 python -V
#>
$ErrorActionPreference = 'Stop'
$image = 'vision-seed-lab:v1'
$akar = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
# Untuk uji rantai (tools\uji\lab.test.mjs): program docker bisa diganti tiruan.
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$sisa = @($args)
$kering = $false
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Kering') { $kering = $true; $sisa = @($sisa | Select-Object -Skip 1) }
$kunciImage = 'image_lab'
if ($sisa.Count -gt 0 -and $sisa[0] -eq '-Fpo') {
    $image = 'cctvgerbang-lab-fpo:v1'
    $kunciImage = 'image_lab_fpo'
    $sisa = @($sisa | Select-Object -Skip 1)
}
if ($sisa.Count -eq 0) { Write-Host 'Pakai: tools\lab.ps1 [-Kering] [-Fpo] <perintah...>'; exit 2 }
if ($sisa[0] -in @('-Kamera', '-Jaringan')) {
    Write-Host "DITOLAK: mode $($sisa[0]) tidak ada di repo ini. Lab hanya berjalan tanpa jaringan."
    exit 2
}

$keluaran = Join-Path $akar 'data\keluaran'
New-Item -ItemType Directory -Force $keluaran | Out-Null
$argumen = @('run', '--rm', '--read-only', '--tmpfs', '/tmp:rw,exec,size=4g', '--cap-drop', 'ALL',
    '--security-opt', 'no-new-privileges', '--env', 'MPLCONFIGDIR=/tmp/mpl', '--env', 'HOME=/tmp',
    '--network', 'none', '--gpus', 'all',
    '--mount', "type=bind,source=$akar,target=/kerja,readonly",
    '--mount', "type=bind,source=$keluaran,target=/kerja/data/keluaran",
    $image) + $sisa

if (-not $kering) {
    # Gagal tertutup: yang dijalankan harus image yang persis tercatat. Tak tercatat, tak ada di mesin, atau berbeda =
    # tidak dijalankan.
    $idKunci = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).$kunciImage.id
    $ErrorActionPreference = 'Continue'
    $idImage = & $docker image inspect $image --format '{{.Id}}' 2>$null
    $ErrorActionPreference = 'Stop'
    if (-not $idKunci -or "$idImage".Trim() -ne $idKunci) {
        Write-Host "IMAGE TAK SESUAI KUNCI: '$image' ber-ID '$idImage', yang tercatat '$idKunci' (tools\vendor.lock.json, $kunciImage)."
        exit 6
    }
}

$tunggu = if ($env:VS_KUNCI_TUNGGU_DTK) { [int]$env:VS_KUNCI_TUNGGU_DTK } else { 1800 }
$kunci = New-Object System.Threading.Mutex($false, 'Global\vision-seed-bengkel')
try {
    try {
        $dapat = $kunci.WaitOne(0)
        if (-not $dapat) {
            Write-Host "Menunggu job lab lain selesai (maks $tunggu dtk)..."
            $dapat = $kunci.WaitOne([TimeSpan]::FromSeconds($tunggu))
        }
    } catch [System.Threading.AbandonedMutexException] {
        $dapat = $true  # pemegang lama mati tanpa melepas; kunci kini sah milik proses ini
    }
    if (-not $dapat) {
        Write-Host "bengkel sedang dipakai job lab lain selama >$tunggu dtk. Ini BUKAN uji merah; ulangi nanti."
        exit 3
    }
    try {
        if ($kering) {
            ConvertTo-Json -InputObject $argumen -Compress
            $kode = 0
        } else {
            & $docker @argumen
            $kode = $LASTEXITCODE
        }
    } finally {
        $kunci.ReleaseMutex()
    }
} finally {
    $kunci.Dispose()
}
exit $kode
