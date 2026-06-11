"""Cross-platform path helpers for FitPick.

All app files are resolved relative to this folder so the project works on
Windows, macOS, and Linux regardless of the current terminal location.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path, PureWindowsPath


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR: Path = _base_dir()
APP_DATA_DIR: Path = BASE_DIR / "app_data"
IMAGE_DIR: Path = APP_DATA_DIR / "images"
CLOTHES_IMAGE_DIR: Path = IMAGE_DIR / "clothes"
DB_PATH: Path = Path(os.getenv("FITPICK_DB_PATH", str(BASE_DIR / "clothes.db"))).expanduser()


def ensure_app_dirs() -> None:
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    CLOTHES_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def app_path(*parts: str | os.PathLike[str]) -> Path:
    return BASE_DIR.joinpath(*parts)


def make_relative_to_app(path: str | os.PathLike[str]) -> str:
    """Store movable relative paths when possible."""
    p = Path(path)
    try:
        return p.resolve().relative_to(BASE_DIR).as_posix()
    except Exception:
        return str(path)


def resolve_existing_path(path_value: str | os.PathLike[str] | None) -> str:
    """Resolve saved image/db paths from old or new project versions.

    Handles absolute paths, app-relative paths, and old saved filenames.
    """
    if not path_value:
        return ""
    raw = str(path_value).strip()
    if not raw:
        return ""

    p = Path(raw).expanduser()
    candidates = []
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append(BASE_DIR / p)

    # A database moved from Windows to macOS contains paths such as C:\...\photo.jpg.
    # PureWindowsPath extracts the filename correctly even on non-Windows systems.
    filename = PureWindowsPath(raw).name if "\\" in raw else p.name
    candidates.append(IMAGE_DIR / filename)
    candidates.append(CLOTHES_IMAGE_DIR / filename)

    for candidate in candidates:
        try:
            if candidate.exists():
                return str(candidate)
        except OSError:
            pass
    return str(candidates[0]) if candidates else raw


ensure_app_dirs()
