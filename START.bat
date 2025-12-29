@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Baidoxe Parking System - Running
color 0B

echo.
echo ============================================================
echo   BAIDOXE PARKING SYSTEM - STARTING
echo ============================================================
echo.

REM Start Frontend (Production Mode)
echo [1/1] Building and starting desktop app...
cd /d "%~dp0desktop"
cscript.exe "%~dp0run-hidden.vbs" "cmd /c npm run prod --silent"
echo [OK] Desktop app dev server starting (http://localhost:3000)
echo.

echo ============================================================
echo   System is running!
echo ============================================================
echo.
echo Frontend:      http://localhost:3000
echo (Backend will start automatically with Electron app)
echo.
echo Press Ctrl+C in each terminal to stop servers
echo.
timeout /t 5 /nobreak

REM Open browser
start http://localhost:3000
