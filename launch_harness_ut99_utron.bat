@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
title Unreal Tournament 99 UTron Mod AI Agent Harness (OldUnreal 469e)

if not exist "logs" mkdir "logs"
set LAUNCH_LOG=logs\launch_utron.log

echo [======================================================================] >> "%LAUNCH_LOG%"
echo [%DATE% %TIME%] Launching UTron Mod Agent Harness >> "%LAUNCH_LOG%"

echo ======================================================================
echo  UNREAL TOURNAMENT 99 UTRON MOD AI AGENT HARNESS (UE1 / OldUnreal 469e)
echo ======================================================================
echo  Target Root: G:\UnrealTournament
echo  Engine Profile: ut99_utron
echo.

:: 1. Locate Python Interpreter
set PYTHON_EXE=
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=python
) else (
    py -3 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_EXE=py -3
    ) else (
        python3 --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_EXE=python3
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python interpreter not found on system PATH!
    pause
    exit /b 1
)

:: 2. Check & Launch UnrealEd for UTron TC
echo [*] Launching UnrealEd for UTron Total Conversion...
if exist "..\System\UnrealEd.exe" (
    cd /d "%~dp0..\System"
    start UnrealEd.exe INI=UTronEditor.ini
    timeout /t 2 /nobreak >nul
)

:: 3. Launch Cockpit UI
echo [*] Starting Native In-Editor Cockpit UI...
cd /d "%~dp0"
%PYTHON_EXE% ui\tk_harness_cockpit.py --engine ut99_utron %*
set EXIT_CODE=%ERRORLEVEL%

echo [%DATE% %TIME%] Process Exited with Code: %EXIT_CODE% >> "%LAUNCH_LOG%"

if %EXIT_CODE% NEQ 0 (
    echo.
    echo ======================================================================
    echo  [FATAL ERROR] Agent Harness exited with error code: %EXIT_CODE%
    echo  [!] See logs in: %CD%\logs\
    echo ======================================================================
    echo.
    pause
    exit /b %EXIT_CODE%
)

exit /b 0
