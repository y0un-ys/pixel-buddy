# Pixel Buddy — Development

`dev` is the active development branch. `main` is for tested/stable releases only.

## Current version

**v0.4.4 — approved character PNGs integrated into BuddyScene**

The complete source, legacy 25 animation sprite sheets, five new illustration PNGs, tests and build scripts are committed to `dev`. The preview on GitHub Actions uses the real Qt BuddyScene.

## Quick checks

```bash
python -m pip install -e . pytest
PYTHONPATH=src python -m pytest -q
```

Windows: `build_exe.bat` → `dist/PixelBuddy.exe`.

macOS: `bash build_mac.command` → `dist/PixelBuddy.app`.

The automated tests pass on Linux. Native Windows/macOS GUI and packaging still need testing on those operating systems.

Avoid committing `.venv/`, `dist/`, `build/` and local save databases.

When a milestone is stable, open a PR from `dev` into `main`.