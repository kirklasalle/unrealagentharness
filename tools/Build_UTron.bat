@echo off
title Unreal Tournament & UTron Script Compiler (UCC Make)
cd /d "%~dp0"
echo ===================================================
echo   UnrealScript Rebuilding Utility (UCC Make)
echo ===================================================
powershell -ExecutionPolicy Bypass -File "%~dp0Compile-UnrealScript.ps1"
pause
