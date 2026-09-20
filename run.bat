@echo off
title Risk Auto Clicker Launcher
if exist "dist\RiskAutoClicker.exe" (
    echo Launching Risk Auto Clicker standalone executable...
    start "" "dist\RiskAutoClicker.exe"
) else (
    echo Launching Risk Auto Clicker via Python...
    python main.py
)
