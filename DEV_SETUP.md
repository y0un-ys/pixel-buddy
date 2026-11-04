# Pixel Buddy — Development

`dev` is the active development branch. `main` is for tested/stable releases only.

## Current version

**v0.4.1 — activity animation improvements**

The complete source, 25 animal sprite sheets, tests and build scripts are committed to `dev`.

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