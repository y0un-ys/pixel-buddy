#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != 'Darwin' ]]; then
  echo 'This build must run on macOS.'; exit 1
fi
if [[ -d 'dist/PixelBuddy.app' ]]; then
  echo 'Close Pixel Buddy before rebuilding.'
fi
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo 'Python 3.11+ is required. Install Python and retry.'; exit 1
fi
"$PYTHON_BIN" -m venv .venv
VENV_PY="./.venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -e . 'pyinstaller>=6,<7'
"$VENV_PY" -m PyInstaller --noconfirm --clean --windowed --onedir --name PixelBuddy --add-data "assets:assets" --paths src --collect-submodules pynput --hidden-import pynput.keyboard._darwin --hidden-import pynput.mouse._darwin run_pixelbuddy.py
# Use Finder launchable bundle at dist/PixelBuddy.app
if [[ -d 'dist/PixelBuddy.app' ]]; then
  echo 'Created dist/PixelBuddy.app'
  echo 'Move PixelBuddy.app to /Applications before enabling login autostart.'
else
  echo 'Build failed: dist/PixelBuddy.app not found.'; exit 1
fi
