#!/bin/bash
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install -r requirements.txt
  python3 run_app.py
else
  python -m pip install -r requirements.txt
  python run_app.py
fi
