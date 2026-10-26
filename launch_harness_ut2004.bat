@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
title Unreal Tournament 2004 AI Agent Harness (UE2.5 / v3369+)

if not exist "logs" mkdir "logs"
set LAUNCH_LOG=logs\launch_ut2004.log

echo [======================================================================] >> "%LAUNCH_LOG%"
echo [%DATE% %TIME%] Launching UT2004 Agent Harness >> "%LAUNCH_LOG%"

echo ======================================================================
echo  UNREAL TOURNAMENT 2004 AI AGENT HARNESS (UE2.5 / v3369+)
echo ======================================================================
echo  Target Root: G:\UnrealTournament2004
echo  Engine Profile: ut2004
echo.

:: 1. Locate Python Interpreter (Prioritize local virtual environment with pywin32)
set PYTHON_EXE=
if exist "%~dp0.venv\Scripts\python.exe" (
    set PYTHON_EXE="%~dp0.venv\Scripts\python.exe"
    echo [*] Using project virtual environment: .venv\Scripts\python.exe
) else (
    python --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set PYTHON_EXE=python
    ) else (
        py -3 --version >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set PYTHON_EXE=py -3
        ) else (
            python3 --version >nul 2>&1
            if !ERRORLEVEL! EQU 0 (
                set PYTHON_EXE=python3
            )
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python interpreter not found on system PATH!
    pause
    exit /b 1
)

:: 2. Check & Launch UnrealEd 3.0 for UT2004
tasklist /fi "imagename eq UnrealEd.exe" 2>nul | findstr /i "UnrealEd.exe" >nul
if !ERRORLEVEL! EQU 0 (
    echo [*] UnrealEd 3.0 is already running and active.
) else (
    echo [*] Launching UnrealEd 3.0 for UT2004...
    if exist "G:\UnrealTournament2004\System\UnrealEd.exe" (
        echo [*] Starting UnrealEd from G:\UnrealTournament2004\System\UnrealEd.exe...
        cd /d "G:\UnrealTournament2004\System"
        start UnrealEd.exe
        timeout /t 3 /nobreak >nul
    ) else if exist "%~dp0..\System\UnrealEd.exe" (
        echo [*] Starting UnrealEd from %~dp0..\System\UnrealEd.exe...
        cd /d "%~dp0..\System"
        start UnrealEd.exe
        timeout /t 3 /nobreak >nul
    ) else (
        echo [!] Warning: Could not locate UnrealEd.exe in G:\UnrealTournament2004\System or ..\System
    )
)

:: 3. Launch Cockpit UI
echo [*] Starting Native In-Editor Cockpit UI...
cd /d "%~dp0"
%PYTHON_EXE% ui\tk_harness_cockpit.py --engine ut2004 %*
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
