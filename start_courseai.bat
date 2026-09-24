@echo off
title CourseAI — Intelligent Course Recommendation System
echo ===================================================
echo   Starting CourseAI Server...
echo ===================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo Installing required packages (if needed)...
pip install -r requirements.txt

echo.
echo Launching CourseAI web app on http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000
python app.py
pause
