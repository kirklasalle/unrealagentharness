@echo off
title Unreal Tournament & UTron Script Extractor
cd /d "%~dp0"
echo ===================================================
echo   UnrealScript Extraction Utility (UCC BatchExport)
echo ===================================================
powershell -ExecutionPolicy Bypass -File "%~dp0Extract-UnrealScript.ps1"
pause
