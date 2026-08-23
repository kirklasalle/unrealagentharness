@echo off
setlocal
cd /d "%~dp0"
title Unreal Tournament 99 UTron Mod AI Agent Harness (OldUnreal 469e)

echo ======================================================================
echo  UNREAL TOURNAMENT 99 UTRON MOD AI AGENT HARNESS (UE1 / OldUnreal 469e)
echo ======================================================================
echo  Target Root: G:\UnrealTournament
echo  Engine Profile: ut99_utron
echo.

:: 1. Check & Launch UnrealEd for UTron TC
echo [*] Launching UnrealEd for UTron Total Conversion...
if exist "..\System\UnrealEd.exe" (
    cd /d "%~dp0..\System"
    start UnrealEd.exe INI=UTronEditor.ini
    timeout /t 2 /nobreak >nul
)

:: 2. Launch Cockpit UI
echo [*] Starting Native In-Editor Cockpit UI...
cd /d "%~dp0"
python ui\tk_harness_cockpit.py --engine ut99_utron
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Agent Harness encountered an issue. See logs\ for details.
    pause
)
