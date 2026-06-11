#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  PYTHON=python
fi

"$PYTHON" -m pip install -r requirements.txt
exec "$PYTHON" run_app.py
