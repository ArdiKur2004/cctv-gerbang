<#
.SYNOPSIS
  Clone repo pihak ketiga ke vendor/ PERSIS di commit yang tercatat di tools/vendor.lock.json.

.DESCRIPTION
  Asal: disalin dari vision-seed @3591530 (tools\klon-terkunci.ps1) pada 2026-10-13 (K14). Yang diubah di sini: alamat
  asal bisa diganti lewat VS_ASAL_GIT, supaya rantainya bisa diuji dengan repo lokal (tools\uji\klon-terkunci.test.mjs).

  Hanya clone + checkout. TIDAK menjalankan install, skrip repo, atau mengunduh bobot:
  Git LFS dimatikan (GIT_LFS_SKIP_SMUDGE=1) sehingga berkas model besar tidak ikut turun.
  Setelah checkout, HEAD dibandingkan dengan SHA di kunci. Beda atau gagal => exit 1.
  Clone != menjalankan: baca kodenya dulu (CLAUDE.md §6) sebelum memasang apa pun.

.EXAMPLE
  powershell -NoProfile -File tools\klon-terkunci.ps1                       # semua entri
  powershell -NoProfile -File tools\klon-terkunci.ps1 -Nama rtmlib,supervision
#>
param(
  [string[]]$Nama,
  [string]$Kunci = (Join-Path $PSScriptRoot 'vendor.lock.json'),
  [string]$Tujuan = (Join-Path (Split-Path -Parent $PSScriptRoot) 'vendor')
)
$ErrorActionPreference = 'Continue'
$env:GIT_LFS_SKIP_SMUDGE = '1'
# Untuk uji rantai: "GitHub" bisa diganti folder lokal. Di luar uji, asalnya selalu github.com.
$asal = if ($env:VS_ASAL_GIT) { $env:VS_ASAL_GIT } else { 'https://github.com/' }

# Lewat `powershell -File`, "-Nama a,b" tiba sebagai SATU string "a,b" (bukan array) — pecah di koma.
$Nama = @($Nama | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

$isi = Get-Content $Kunci -Raw -Encoding UTF8 | ConvertFrom-Json
$entri = @($isi.repo | Where-Object { $Nama.Count -eq 0 -or ($Nama -contains $_.nama) })
if ($Nama.Count -gt 0) {
  $takDikenal = @($Nama | Where-Object { $entri.nama -notcontains $_ })
  if ($takDikenal.Count -gt 0) { Write-Host "TAK ADA DI KUNCI: $($takDikenal -join ', ')"; exit 1 }
}

$gagal = 0
foreach ($e in $entri) {
  $folder = Join-Path $Tujuan $e.nama
  if (-not (Test-Path $folder)) {
    git clone --quiet --filter=blob:none --no-checkout ($asal + $e.repo + ".git") $folder
    if ($LASTEXITCODE -ne 0) { Write-Host "GAGAL  $($e.nama): clone $($e.repo)"; $gagal++; continue }
  }
  git -C $folder cat-file -e ($e.sha + '^{commit}') 2>$null
  if ($LASTEXITCODE -ne 0) { git -C $folder fetch --quiet --tags origin }
  git -C $folder -c advice.detachedHead=false checkout --quiet $e.sha
  if ($LASTEXITCODE -ne 0) { Write-Host "GAGAL  $($e.nama): checkout $($e.sha)"; $gagal++; continue }

  $head = (git -C $folder rev-parse HEAD).Trim()
  if ($head -ne $e.sha) {
    Write-Host "BEDA   $($e.nama): HEAD $head != kunci $($e.sha)"; $gagal++
  } else {
    Write-Host ("OK     {0,-15} {1} @ {2}  [{3}]" -f $e.nama, $e.repo, $e.ref, $e.vonis)
  }
}

if ($gagal -gt 0) { Write-Host "$gagal entri gagal."; exit 1 }
Write-Host "$($entri.Count) entri cocok dengan kunci."
exit 0
