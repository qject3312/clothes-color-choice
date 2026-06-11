@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
    py run_app.py
) else (
    python -m pip install -r requirements.txt
    python run_app.py
)
pause
