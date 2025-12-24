@echo off
chcp 65001 >nul 2>&1
title OPEN WEB BAI DO XE

echo.
echo ========================================
echo OPEN WEB BAI DO XE
echo ========================================
echo.

echo Kiem tra server co dang chay khong...

:: Kiem tra port 5000 co dang duoc su dung khong
netstat -an | find ":5000" >nul
if errorlevel 1 (
    echo Server chua chay!
    echo Hay chay START_WEB.bat truoc
    echo.
    pause
    exit /b 1
)

echo Server dang hoat dong

echo Mo trinh duyet...
start http://localhost:5000

echo.
echo Da mo web interface tai: http://localhost:5000
echo Neu khong tu mo, copy link tren vao trinh duyet
echo.
pause