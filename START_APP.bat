@echo off
title Step Into Your Future - Live AI Demo
cd /d "%~dp0"
echo.
echo ============================================================
echo   STEP INTO YOUR FUTURE - TODAY!  LIVE AI DEMO
echo ============================================================
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  set PY=py
) else (
  set PY=python
)
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
 echo.
 echo Could not install the required Python packages.
 echo Make sure Python is installed and that this laptop is online.
 pause
 exit /b 1
)
%PY% app.py
pause
