@echo off
cd /d %~dp0
py -m uvicorn backend.app:app --reload
pause
