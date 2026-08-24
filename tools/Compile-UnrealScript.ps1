# Unreal Tournament & UTron Script Compiler
# Uses UCC.exe make to compile .uc source trees into binary .u packages.

param(
    [string]$Package = ""
)

$SystemDir = Join-Path $PSScriptRoot "System"
$UTronSystemDir = Join-Path $PSScriptRoot "UTronProject\System"
$UccExe = Join-Path $SystemDir "UCC.exe"

if (-not (Test-Path $UccExe)) {
    Write-Error "UCC.exe not found at $UccExe"
    exit 1
}

$BackupDir = Join-Path $PSScriptRoot "UTronProject\Backup_U_Files"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " Unreal Tournament / UTron Script Compiler (UCC)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Ensure source trees in UTronProject are also discoverable in root if needed
$UTronPackages = @("UTronMedia", "UTron", "UTronMenu", "UTronBrowser")

# Backup existing .u binaries
Write-Host "`n[1/3] Creating safety backup of current .u packages..." -ForegroundColor Yellow
foreach ($pkg in $UTronPackages) {
    $srcU = Join-Path $UTronSystemDir "$pkg.u"
    if (Test-Path $srcU) {
        $backupPath = Join-Path $BackupDir "${pkg}_$Timestamp.u"
        Copy-Item -Path $srcU -Destination $backupPath -Force
        Write-Host "  -> Backed up $pkg.u" -ForegroundColor Gray
    }
}

# If specific package requested, remove only that one; otherwise remove in reverse dependency order
$TargetsToRebuild = if ($Package) { @($Package) } else { @("UTronBrowser", "UTronMenu", "UTron", "UTronMedia") }

Write-Host "`n[2/3] Preparing workspace for compilation..." -ForegroundColor Yellow
foreach ($target in $TargetsToRebuild) {
    $inSystem = Join-Path $SystemDir "$target.u"
    $inUTron = Join-Path $UTronSystemDir "$target.u"
    if (Test-Path $inSystem) { Remove-Item $inSystem -Force }
    if (Test-Path $inUTron) { Remove-Item $inUTron -Force }
    Write-Host "  -> Flagged $target for recompilation." -ForegroundColor Gray
}

Write-Host "`n[3/3] Executing UCC make..." -ForegroundColor Cyan
Push-Location $SystemDir
try {
    & $UccExe make -INI=UTronEditor.ini
}
finally {
    Pop-Location
}

# Sync newly compiled packages to UTronProject\System if compiled in root System
foreach ($pkg in $UTronPackages) {
    $compiledRoot = Join-Path $SystemDir "$pkg.u"
    $targetUTron = Join-Path $UTronSystemDir "$pkg.u"
    if (Test-Path $compiledRoot) {
        Copy-Item -Path $compiledRoot -Destination $targetUTron -Force
    }
}

Write-Host "`n[COMPLETED] Build process finished. Check output above for any compiler warnings or errors." -ForegroundColor Green
