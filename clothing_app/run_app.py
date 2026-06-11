"""Cross-platform launcher for FitPick (Flet UI).

Run this file from Windows, macOS, or Linux:
    python run_app.py
or
    python3 run_app.py

main.py 가 Flet 앱이므로 ft.app(target=main) 으로 실행합니다.
백엔드(FastAPI)는 main.py 내부에서 자동으로 기동됩니다.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import flet as ft  # noqa: E402
from main import main as app_main  # noqa: E402


def main() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ft.app(target=app_main)


if __name__ == "__main__":
    main()
