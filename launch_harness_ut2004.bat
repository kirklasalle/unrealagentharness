@echo off
setlocal
cd /d "%~dp0"
title Unreal Tournament 2004 AI Agent Harness (UE2.5)

echo ======================================================================
echo  UNREAL TOURNAMENT 2004 AI AGENT HARNESS (UE2.5 / v3369+)
echo ======================================================================
echo  Target Root: G:\UnrealTournament2004
echo  Engine Profile: ut2004
echo.

:: 1. Check & Launch UnrealEd 3.0 for UT2004
echo [*] Launching UnrealEd 3.0 for UT2004...
if exist "G:\UnrealTournament2004\System\UnrealEd.exe" (
    cd /d "G:\UnrealTournament2004\System"
    start UnrealEd.exe
    timeout /t 2 /nobreak >nul
)

:: 2. Launch Cockpit UI
echo [*] Starting Native In-Editor Cockpit UI...
cd /d "%~dp0"
python ui\tk_harness_cockpit.py --engine ut2004
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Agent Harness encountered an issue. See logs\ for details.
    pause
)
