@echo off
chcp 65001 >nul
title 핏픽 - 옷 추천 앱
echo =============================
echo  핏픽 - 옷 추천 앱
echo =============================
python -c "import flet" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 의존성 설치 중...
    pip install -r requirements.txt
)
python main.py
pause
