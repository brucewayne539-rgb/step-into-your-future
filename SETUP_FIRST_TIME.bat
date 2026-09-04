@echo off
title Step Into Your Future - First Time Setup
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  py setup_key.py
) else (
  python setup_key.py
)
