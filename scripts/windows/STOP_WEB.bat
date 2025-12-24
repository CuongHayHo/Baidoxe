@echo off
chcp 65001 >nul 2>&1
title BAI DO XE - STOP SERVER

echo.
echo ========================================
echo BAI DO XE - STOP SERVER
echo ========================================
echo.

echo Tim va dung cac tien trinh server...

:: Dung Python Flask backend server (port 5000)
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do (
    echo Dung tien trinh Flask backend (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

:: Dung cac tien trinh Python co ten run.py hoac app.py
for /f "tokens=2" %%a in ('tasklist ^| find "python.exe"') do (
    wmic process where "processid=%%a and (commandline like '%%run.py%%' or commandline like '%%app.py%%')" delete >nul 2>&1
)

:: Dung cac tien trinh Node.js neu co
for /f "tokens=5" %%a in ('netstat -ano ^| find ":3000"') do (
    echo Dung tien trinh Node.js (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Da dung tat ca server processes
echo Port 5000 va 3000 da duoc giai phong
echo.
echo Bay gio ban co the chay lai START_WEB.bat
echo.
pause