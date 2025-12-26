@echo off
REM ===================================================================
REM Baidoxe Desktop App Setup - Windows
REM ===================================================================

setlocal enabledelayedexpansion
color 0A
title Baidoxe Desktop App Setup

echo.
echo ===================================================================
echo   BAIDOXE DESKTOP APP SETUP
echo ===================================================================
echo.

REM Check Node.js
echo [1/2] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo   ✓ Node.js %%i installed
echo.

REM Setup Desktop
echo [2/2] Installing Desktop App dependencies...
cd desktop
echo   This may take 5-10 minutes...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install desktop dependencies
    echo Try running: cd desktop && npm install --legacy-peer-deps
    pause
    exit /b 1
)
cd ..
echo   ✓ Desktop setup complete
echo.

echo ===================================================================
echo   ✓ DESKTOP APP READY!
echo ===================================================================
echo.
echo Next step:
echo   Run 'run-dev.bat' to start the application
echo.
pause
