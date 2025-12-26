@echo off
REM ===================================================================
REM Baidoxe Development Runner - Windows
REM Starts Backend (Flask) + Frontend (React) + Database
REM ===================================================================

setlocal enabledelayedexpansion
color 0A
title Baidoxe Development Server

echo.
echo ===================================================================
echo   BAIDOXE PARKING MANAGEMENT SYSTEM - DEVELOPMENT
echo ===================================================================
echo.

REM Setup Python dependencies if needed
echo [1/4] Setting up Python backend dependencies...
cd backend
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo   Installing Python packages...
pip install -q -r requirements.txt
cd ..
echo   ✓ Backend dependencies installed
echo.

REM Initialize database if needed
if not exist "backend\data\parking_system.db" (
    echo [2/4] Initializing database...
    cd backend
    call venv\Scripts\activate.bat
    python scripts/init_db.py
    cd ..
    echo   ✓ Database initialized
    echo.
)

echo [3/4] Starting Backend (Flask) on http://localhost:5000...
start cmd /k "cd backend && call venv\Scripts\activate.bat && python run.py"
timeout /t 2 /nobreak

echo [4/4] Starting Frontend (React) on http://localhost:3000...
start cmd /k "cd frontend && npm start"
timeout /t 2 /nobreak

echo [4/4] Opening web browser...
timeout /t 3 /nobreak
start http://localhost:3000

echo.
echo ===================================================================
echo   ✓ DEVELOPMENT ENVIRONMENT STARTED
echo ===================================================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:5000/api/docs
echo.
echo To stop: Close the command windows
echo.
pause
