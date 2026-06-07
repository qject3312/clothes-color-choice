#!/bin/bash
echo "============================="
echo "  핏픽 - 옷 추천 앱"
echo "============================="
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3가 필요합니다."
    exit 1
fi
if ! python3 -c "import flet" &>/dev/null; then
    echo "[INFO] 의존성 설치 중..."
    pip3 install -r requirements.txt
fi
python3 main.py
