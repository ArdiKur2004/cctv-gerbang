<#
.SYNOPSIS
  Membangun image lab tambahan cctvgerbang-lab-fpo:v1 (K26) dari tools\lab-fpo, di atas image lab vision-seed.

.DESCRIPTION
  - Image dasar vision-seed-lab:v1 harus ber-ID persis yang tercatat di tools\vendor.lock.json (image_lab); bila tidak,
    tidak dibangun (kode 6).
  - Daftar paket (requirements.txt) harus ber-SHA-256; bila tidak, ditolak (kode 2). Dockerfile memasangnya dengan
    --require-hashes --no-deps --no-build.
  - Image diberi label sidik SHA-256 (Dockerfile + requirements.txt). Sesudah dibangun, ID image dicatat di kunci
    (image_lab_fpo) supaya tools\lab.ps1 -Fpo hanya menjalankan image itu.
  - Jaringan dipakai docker build untuk mengunduh wheel. Saat jalan, image selalu tanpa jaringan (lab.ps1).

  Bendera: -Kering   cetak argumen docker sebagai JSON tanpa membangun (dipakai tools\uji\image-lab-fpo.test.mjs)

.EXAMPLE
  powershell -NoProfile -File tools\image-lab-fpo.ps1
#>
$ErrorActionPreference = 'Stop'
$folder = if ($env:VS_LAB_FPO_FOLDER) { $env:VS_LAB_FPO_FOLDER } else { Join-Path $PSScriptRoot 'lab-fpo' }
$kunciVendor = if ($env:VS_KUNCI_VENDOR) { $env:VS_KUNCI_VENDOR } else { Join-Path $PSScriptRoot 'vendor.lock.json' }
$docker = if ($env:VS_DOCKER) { $env:VS_DOCKER } else { 'docker' }
$kering = ($args.Count -gt 0 -and $args[0] -eq '-Kering')
$image = 'cctvgerbang-lab-fpo:v1'

$idDasar = [string](Get-Content $kunciVendor -Raw -Encoding UTF8 | ConvertFrom-Json).image_lab.id
$ErrorActionPreference = 'Continue'
$idAda = & $docker image inspect vision-seed-lab:v1 --format '{{.Id}}' 2>$null
$ErrorActionPreference = 'Stop'
if (-not $idDasar -or "$idAda".Trim() -ne $idDasar) {
    Write-Host "IMAGE DASAR TAK SESUAI KUNCI: vision-seed-lab:v1 ber-ID '$idAda', yang tercatat '$idDasar'."
    exit 6
}
$dockerfile = Join-Path $folder 'Dockerfile'
$req = Join-Path $folder 'requirements.txt'
$baris = @(Get-Content $req | Where-Object { $_ -match '^[A-Za-z0-9]' })
$berhash = @(Get-Content $req | Where-Object { $_ -match '--hash=sha256:[0-9a-f]{64}' })
if ($baris.Count -eq 0 -or $berhash.Count -lt $baris.Count) {
    Write-Host "DITOLAK: tiap paket di requirements.txt harus punya --hash=sha256 ($($baris.Count) paket, $($berhash.Count) hash)."
    exit 2
}
$sha = [Security.Cryptography.SHA256]::Create()
$isi = [byte[]]([IO.File]::ReadAllBytes($dockerfile) + [IO.File]::ReadAllBytes($req))
$sidik = -join ($sha.ComputeHash($isi) | ForEach-Object { $_.ToString('x2') })
$argumen = @('build', '--build-arg', "KUNCI_LAB_FPO=$sidik", '-t', $image, $folder)
if ($kering) { ConvertTo-Json -InputObject $argumen -Compress; exit 0 }

& $docker @argumen
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$id = & $docker image inspect $image --format '{{.Id}}'
Write-Host "TERBANGUN $image ID $id SIDIK $sidik"
exit 0
