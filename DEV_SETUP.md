# Pixel Buddy — Development

This branch (`dev`) is for work in progress. Merge into `main` only after testing.

Current working version: **v0.4.0 graphics prototype**.

- Windows: `build_exe.bat`
- macOS: `bash build_mac.command`
- Tests: `PYTHONPATH=src python -m pytest -q`

The full source and PNG sprites are not uploaded by this initial bootstrap commit; add the project contents from the prepared source archive before building.

Do not commit `.venv/`, `dist/`, `build/`, or SQLite save files.

The game uses the same assets on Windows and macOS. Native GUI validation remains necessary.
