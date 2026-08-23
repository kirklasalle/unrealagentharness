@echo off
title UnrealEd AI Agent Harness - Universal Multi-Engine
cd /d "%~dp0"
echo =========================================================
echo   Launching Universal Standalone Agent Harness
echo   (UT99 GOTY / UTron Mod / UT2003 / UT2004)
echo =========================================================
start "" python ui/tk_harness_cockpit.py
exit /b 0
