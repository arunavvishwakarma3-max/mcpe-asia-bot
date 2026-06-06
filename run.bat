@echo off
title MCPE ASIA Bot Launcher
echo ==================================================
echo   MCPE ASIA BOT - LAUNCHER
echo ==================================================
echo.
echo [1/2] Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Install failed. Make sure Python is installed and in PATH.
    pause
    exit /b
)
echo.
echo [2/2] Launching bot...
echo.
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Bot stopped. Check your .env token.
)
echo.
pause
