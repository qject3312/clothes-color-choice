@echo off
chcp 65001 >nul
title 옷 추천 앱

echo ============================================
echo  옷 추천 앱 시작 중...
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

python -c "import flet" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 의존성 자동 설치...
    pip install -r requirements.txt
)

echo [INFO] 앱 실행 (백엔드 자동 시작)...
python main.py

pause
