"""Cross-platform launcher for FitPick.

Run this file from Windows, macOS, or Linux:
    python run_app.py
or
    python3 run_app.py
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

from main import ClothingApp  # noqa: E402
import tkinter as tk  # noqa: E402


def main() -> None:
    root = tk.Tk()
    app = ClothingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
