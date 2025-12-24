@echo off
chcp 65001 >nul
title BAI DO XE - BACKEND START

echo.
echo ========================================
echo BAI DO XE - BACKEND START
echo ========================================
echo.

cd /d "%~dp0"
cd ..\..
echo Directory: %cd%
echo.

:: Test Python
echo Testing Python...
python --version
if errorlevel 1 (
    echo Python error!
    pause
    exit /b 1
)
echo Python OK
echo.

:: Test Virtual Environment
echo Testing Virtual Environment...
if exist ".venv\Scripts\activate.bat" (
    echo .venv exists
    call .venv\Scripts\activate.bat
    echo Virtual env activated
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)
echo.

:: Install packages
echo Installing backend packages...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo Pip install failed!
    echo Manual command: cd backend && pip install -r requirements.txt
    pause
    exit /b 1
)
echo Backend packages installed
echo.

:: Check backend files
echo Checking backend files...
if exist "run.py" (
    echo Backend run.py found
) else (
    echo Backend run.py NOT FOUND!
    echo Make sure you are in the project root directory
    pause
    exit /b 1
)

if exist "app.py" (
    echo Backend app.py found
) else (
    echo Backend app.py NOT FOUND!
    pause
    exit /b 1
)

if not exist "data\cards.json" (
    if not exist "data" mkdir data
    echo {"cards": {}} > data\cards.json
    echo Created cards.json
)
echo.

:: Start Flask backend
echo Starting Flask backend...
echo ============================================
echo Web: http://localhost:5000
echo Press Ctrl+C to stop
echo Backend logs will appear below
echo ============================================
echo.

python run.py
set RESULT=%errorlevel%

echo.
echo ============================================
if %RESULT% equ 0 (
    echo ✅ Server stopped normally
) else (
    echo ❌ Server error! Exit code: %RESULT%
    echo.
    echo 🔍 Common issues:
    echo   - Port 5000 already in use
    echo   - Missing Python packages
    echo   - Syntax error in api_server.py
    echo   - Antivirus blocking
)
echo ============================================
echo.
echo 💡 Window will stay open. Press any key to close...
pause >nul