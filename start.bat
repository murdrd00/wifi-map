@echo off
title WiFi Heatmap Builder

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
    goto :found
)
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python3
    goto :found
)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY=py
    goto :found
)

:: Python not found — show popup and offer to open download page
msg * "Python is required but was not found. Click OK to open the Python download page." 2>nul || (
    echo Python is required but was not found.
    echo Please install Python from https://python.org
    pause
)
start "" https://www.python.org/downloads/
exit /b 1

:found
start "" http://localhost:8199
timeout /t 2 /nobreak >nul
%PY% "%~dp0server.py"
pause
