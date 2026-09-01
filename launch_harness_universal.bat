@echo off
setlocal enabledelayedexpansion

title UnrealEd AI Agent Harness — Universal Multi-Engine
cd /d "%~dp0"

:: Ensure logs directory exists
if not exist "logs" mkdir "logs"
set LAUNCH_LOG=logs\launch_universal.log

echo [======================================================================] >> "%LAUNCH_LOG%"
echo [%DATE% %TIME%] Launching Standalone Agent Harness Universal >> "%LAUNCH_LOG%"
echo [%DATE% %TIME%] Working Directory: %CD% >> "%LAUNCH_LOG%"
echo [%DATE% %TIME%] Launch Args: %* >> "%LAUNCH_LOG%"

echo ======================================================================
echo   UNREAL ENGINE AI AGENT HARNESS (UNIVERSAL MULTI-ENGINE)
echo   Supports: UT99 GOTY / Unreal TC & Mods / UT2003 / UT2004 / UE2.5+
echo ======================================================================
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
    echo [ERROR] Please install Python 3.10+ and ensure 'Add Python to PATH' is checked.
    echo [%DATE% %TIME%] ERROR: Python interpreter not found on PATH. >> "%LAUNCH_LOG%"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_EXE% --version 2^>^&1') do set PY_VER=%%v
echo [*] Detected Python Runtime: %PY_VER%
echo [*] Logs written to        : %CD%\logs\
echo [%DATE% %TIME%] Using %PYTHON_EXE% (%PY_VER%) >> "%LAUNCH_LOG%"
echo.

:: 2. Launch Cockpit UI
echo [*] Initializing Native Agent Harness Cockpit...
%PYTHON_EXE% ui\tk_harness_cockpit.py %*
set EXIT_CODE=%ERRORLEVEL%

echo [%DATE% %TIME%] Harness Process Exited with Code: %EXIT_CODE% >> "%LAUNCH_LOG%"

if %EXIT_CODE% NEQ 0 (
    echo.
    echo ======================================================================
    echo  [FATAL ERROR] Agent Harness exited with error code: %EXIT_CODE%
    echo  [!] Check the log files for detailed traceback diagnostics:
    echo        Master Log : %CD%\logs\agent_harness.log
    echo        UI Log     : %CD%\logs\harness_ui.log
    echo        Crash Log  : %CD%\logs\agent_harness_crash.log
    echo ======================================================================
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo [*] Standalone Agent Harness closed cleanly.
exit /b 0
