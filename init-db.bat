@echo off
REM ===================================================================
REM Baidoxe Database Initialize Script - Windows
REM ===================================================================

setlocal enabledelayedexpansion
color 0A
title Baidoxe Database Setup

echo.
echo ===================================================================
echo   BAIDOXE - DATABASE INITIALIZATION
echo ===================================================================
echo.

cd backend
call venv\Scripts\activate.bat

echo [1/2] Creating database tables...
python scripts/init_db.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo   ✓ Database initialized
echo.

echo [2/2] Database location:
echo   %cd%\data\parking_system.db
echo.

echo ===================================================================
echo   ✓ DATABASE SETUP COMPLETE
echo ===================================================================
echo.
pause
