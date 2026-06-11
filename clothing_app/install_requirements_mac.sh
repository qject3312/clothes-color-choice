#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  exec python3 -m pip install -r requirements.txt
else
  exec python -m pip install -r requirements.txt
fi
