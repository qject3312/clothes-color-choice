#!/bin/bash
# 옷 추천 앱 - macOS / Linux 실행 스크립트

echo "============================================"
echo "  옷 추천 앱 시작 중..."
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3가 설치되어 있지 않습니다."
    exit 1
fi

# Flet 확인
if ! python3 -c "import flet" &> /dev/null; then
    echo "[INFO] 의존성을 설치합니다..."
    pip3 install -r requirements.txt
fi

echo "[INFO] 앱 실행 (백엔드 자동 시작)..."
python3 main.py
