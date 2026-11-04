@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Pixel Buddy - Windows EXE Builder

echo =========================================
echo   Pixel Buddy - EXE Build (Windows)
echo =========================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python was not found.
        echo Please install Python 3.11 or newer, or copy this folder into your existing Pixel Buddy project with .venv.
        goto :error
    )
    echo [INFO] Creating build virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
    set "PY=.venv\Scripts\python.exe"
)

echo [1/3] Installing dependencies and PyInstaller...
"%PY%" -m pip install --disable-pip-version-check -e . "pyinstaller>=6,<7"
if errorlevel 1 goto :error

echo [2/3] Creating PixelBuddy.exe (without console)...
REM An active EXE cannot be overwritten on Windows.
tasklist /FI "IMAGENAME eq PixelBuddy.exe" /NH 2>nul | findstr /I /C:"PixelBuddy.exe" >nul
if not errorlevel 1 (
    echo [ERROR] PixelBuddy.exe is still running.
    echo Exit Pixel Buddy from the SYSTEM TRAY and run build_exe.bat again.
    goto :error
)
"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name PixelBuddy --add-data "assets;assets" --paths src --collect-submodules pynput --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 run_pixelbuddy.py
if errorlevel 1 goto :error

if not exist "dist\PixelBuddy.exe" goto :error

echo [3/3] Finished!
echo.
echo Output: %CD%\dist\PixelBuddy.exe
echo Double-click that file to play. No Python needed for normal usage.
echo.
explorer "dist"
pause
exit /b 0

:error
echo.
echo [ERROR] The build did not complete. Check the messages above.
pause
exit /b 1
