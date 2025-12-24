@echo off
chcp 65001 >nul 2>&1

echo ================================================================
echo    PARKING SYSTEM - QUICK START
echo ================================================================
echo.

REM Check if we're in the right directory with backend
if not exist "backend\run.py" (
    echo Error: backend\run.py not found!
    echo Please run this script from the Baidoxe project root folder.
    echo Expected structure: Baidoxe\backend\run.py
    pause
    exit /b 1
)

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! 
    echo Please install Python from: https://python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Installing backend packages...
cd backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Package installation may have issues, but continuing...
) else (
    echo Backend packages installed successfully!
)

echo.
echo Starting Parking System Server...
echo.
echo Web interface will be available at:
echo    http://localhost:5000
echo.
echo Hardware endpoints:
echo    // Lựa chọn 1: Arduino UNO R4 & ESP32 sẽ tạo WiFi AP "UNO-R4-AP"
echo    // Arduino UNO R4: IP 192.168.4.2
echo    // ESP32: IP 192.168.4.5
echo.
echo    // Lựa chọn 2: Arduino UNO R4 & ESP32 sẽ kết nối vào WiFi local (router)
echo    // Thay đổi SSID/Password trong file *.ino rồi upload
echo    // Arduino UNO R4: IP sẽ được cấp từ router
echo    // ESP32: IP sẽ được cấp từ router
echo.
echo To access from other devices on LAN:
echo    http://[YOUR_IP]:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

REM Start the Flask backend
python run.py

echo.
echo Server stopped.
pause