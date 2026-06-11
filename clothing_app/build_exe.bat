@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
py -m PyInstaller --noconfirm --onefile --windowed --name FitPickApp --add-data "backend;backend" --add-data "logic;logic" --add-data "model;model" --add-data "views;views" --add-data "app_data;app_data" --hidden-import uvicorn --hidden-import fastapi --hidden-import pydantic --hidden-import PIL --hidden-import requests run_app.py
echo.
echo 완료: dist\FitPickApp.exe 파일을 실행하세요.
pause
