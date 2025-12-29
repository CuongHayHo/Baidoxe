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

REM Start Backend
echo [1/2] Starting backend server...
cd /d "%~dp0backend"
if exist ".venv" (
    call .venv\Scripts\activate.bat
)
start "Backend Server" python run.py
echo ✓ Backend server started (http://localhost:5000)
timeout /t 3 /nobreak

REM Start Frontend
echo [2/2] Starting frontend development server...
cd /d "%~dp0frontend"
start "Frontend Dev Server" cmd /k npm run dev
echo ✓ Frontend dev server starting (http://localhost:3000)
echo.

echo ============================================================
echo   System is running!
echo ============================================================
echo.
echo Backend API:   http://localhost:5000
echo Frontend:      http://localhost:3000
echo.
echo Press Ctrl+C in each terminal to stop servers
echo.
timeout /t 5 /nobreak

REM Open browser
start http://localhost:3000
