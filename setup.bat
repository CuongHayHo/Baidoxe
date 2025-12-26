@echo off
REM ===================================================================
REM Baidoxe Setup Script - Windows
REM Cài đặt tất cả dependencies cho backend, frontend, desktop
REM ===================================================================

setlocal enabledelayedexpansion
color 0A
title Baidoxe Setup

echo.
echo ===================================================================
echo   BAIDOXE PARKING MANAGEMENT SYSTEM - SETUP
echo ===================================================================
echo.

REM Check Node.js
echo [1/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo   ✓ Node.js %%i installed
echo.

REM Check Python
echo [2/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   ✓ %%i installed
echo.

REM Setup Backend
echo [3/5] Setting up Backend...
cd backend
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo   Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo   ✓ Backend setup complete
cd ..
echo.

REM Setup Frontend
echo [4/5] Setting up Frontend...
cd frontend
echo   Installing dependencies (this may take a few minutes)...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo   ✓ Frontend setup complete
cd ..
echo.

REM Setup Desktop (Optional)
echo [5/5] Setting up Desktop App (optional)...
cd desktop
echo   Installing dependencies (this may take a few minutes)...
call npm install
if errorlevel 1 (
    echo WARNING: Desktop app setup failed (optional)
    echo You can skip this if you only need web + backend
    cd ..
) else (
    echo   ✓ Desktop setup complete
    cd ..
)
echo.

echo ===================================================================
echo   ✓ SETUP COMPLETE!
echo ===================================================================
echo.
echo Next steps:
echo   1. Run 'run-dev.bat' to start development environment
echo   2. Or read INSTALL.md for detailed instructions
echo.
pause
