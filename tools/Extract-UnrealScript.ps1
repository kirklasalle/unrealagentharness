# Unreal Tournament & UTron Script Extractor
# Uses UCC.exe batchexport to unpack all .uc classes from binary .u packages into directory trees.

$SystemDir = Join-Path $PSScriptRoot "System"
$UccExe = Join-Path $SystemDir "UCC.exe"

if (-not (Test-Path $UccExe)) {
    Write-Error "UCC.exe not found at $UccExe"
    exit 1
}

# Base Engine Packages
$BasePackages = @(
    "Core",
    "Engine",
    "Editor",
    "UWindow",
    "Fire",
    "IpDrv",
    "UWeb",
    "UBrowser",
    "UnrealShare",
    "UnrealI",
    "UMenu",
    "Botpack",
    "IpServer",
    "UTServerAdmin",
    "UTMenu",
    "UTBrowser",
    "SkeletalChars",
    "epiccustommodels",
    "multimesh",
    "relics",
    "relicsbindings",
    "de",
    "udemo"
)

# UTron Mod Packages
$UTronPackages = @(
    "UTronMedia",
    "UTron",
    "UTronMenu",
    "UTronBrowser"
)

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " Extracting Base Unreal Tournament Packages (.u)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

Push-Location $SystemDir
try {
    foreach ($pkg in $BasePackages) {
        $targetDir = Join-Path $PSScriptRoot "$pkg\Classes"
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Write-Host "-> Exporting $pkg.u to $pkg\Classes\..." -ForegroundColor Yellow
        & $UccExe batchexport "$pkg.u" class uc $targetDir | Out-Null
    }

    Write-Host "`n=================================================" -ForegroundColor Cyan
    Write-Host " Extracting UTron Project Mod Packages (.u)" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan

    foreach ($pkg in $UTronPackages) {
        $targetDir = Join-Path $PSScriptRoot "UTronProject\$pkg\Classes"
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Write-Host "-> Exporting $pkg.u to UTronProject\$pkg\Classes\..." -ForegroundColor Green
        & $UccExe batchexport "$pkg.u" class uc $targetDir | Out-Null
    }
}
finally {
    Pop-Location
}

$totalUc = (Get-ChildItem -Path $PSScriptRoot -Recurse -Filter *.uc).Count
Write-Host "`n[SUCCESS] Extraction complete! Total extracted UnrealScript classes: $totalUc" -ForegroundColor Green
