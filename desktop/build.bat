@echo off
REM Baidoxe Desktop App - Windows Build Script

setlocal enabledelayedexpansion

echo.
echo Baidoxe Desktop App - Build Script
echo ===================================
echo.

if "%1%"=="" (
    set PLATFORM=all
) else (
    set PLATFORM=%1
)

if "%2%"=="" (
    set OUTPUT_DIR=dist
) else (
    set OUTPUT_DIR=%2
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo Building React...
call npm run react-build

if "%PLATFORM%"=="windows" goto build_windows
if "%PLATFORM%"=="win" goto build_windows
if "%PLATFORM%"=="w" goto build_windows
if "%PLATFORM%"=="macos" goto build_macos
if "%PLATFORM%"=="mac" goto build_macos
if "%PLATFORM%"=="m" goto build_macos
if "%PLATFORM%"=="linux" goto build_linux
if "%PLATFORM%"=="l" goto build_linux
if "%PLATFORM%"=="all" goto build_all
if "%PLATFORM%"=="a" goto build_all

echo Usage: build.bat [platform]
echo Platforms: windows, macos, linux, all
goto end

:build_windows
echo.
echo Building for Windows...
call npx electron-builder --win
goto success

:build_macos
echo.
echo Building for macOS...
call npx electron-builder --mac
goto success

:build_linux
echo.
echo Building for Linux...
call npx electron-builder --linux
goto success

:build_all
echo.
echo Building for All Platforms...
call npx electron-builder -mwl
goto success

:success
echo.
echo Build completed successfully!
echo Output directory: %OUTPUT_DIR%
dir /s %OUTPUT_DIR%
goto end

:end
endlocal
