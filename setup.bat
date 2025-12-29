@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Setup Baidoxe Parking System
color 0A

echo.
echo ============================================================
echo   BAIDOXE PARKING SYSTEM - SETUP
echo ============================================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js
    pause
    exit /b 1
)
echo [OK] Node.js found
echo.

REM Install backend dependencies
echo [3/5] Installing backend dependencies...
cd /d "%~dp0backend"
if exist ".venv" (
    echo Virtual environment found, activating...
    call .venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed
echo.

REM Initialize database
echo [4/5] Initializing database...
python scripts/init_db.py
if errorlevel 1 (
    echo [ERROR] Database initialization failed
    pause
    exit /b 1
)
echo [OK] Database initialized
echo.

REM Install frontend dependencies
echo [5/6] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install -q
if errorlevel 1 (
    echo [WARNING] Frontend npm install had issues, but continuing...
)
echo [OK] Frontend dependencies ready
echo.

REM Install desktop dependencies
echo [6/6] Installing desktop app dependencies...
cd /d "%~dp0desktop"
call npm install -q
if errorlevel 1 (
    echo [WARNING] Desktop npm install had issues, but continuing...
)
echo [OK] Desktop app dependencies ready
echo.

echo ============================================================
echo   SETUP COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo Next steps:
echo   1. Run START.bat to start the system
echo   2. Open http://localhost:3000 in your browser
echo.
pause
