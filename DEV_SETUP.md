# Pixel Buddy — Development

`dev` is the active development branch. `main` is for tested/stable releases only.

## Current version

**v0.4.7 — visible 4FPS paw/head motion and repaired floppy dog ear**

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

## v0.4.5 activity verification

- Idle is awake; show sleep cues only after 150 seconds without actual input.
- In Settings, check **현재 상태** and the key/mouse event age and macOS Input Monitoring permission.
- Use the manual state selector to preview typing/mouse/watching/gaming/idle/sleep without waiting for global detection.
- `python tools/preview_illustrated_pet.py` exports screenshots and an `activity_states.png` contact sheet. GitHub Actions uploads the previews as an artifact.
- All animations are non-invasive visual effects over the approved static character PNGs; separate articulated paw frames remain future work.


## v0.4.7 artwork maintenance

- Approved dog portrait source: `assets/illustration_sources/dog_original.png`.
- Regenerate art with `pip install Pillow numpy scipy && python tools/generate_chibi_animations.py`.
- The sprite-building GitHub workflow commits generated character frames and the corrected dog portrait to `dev`.
- Runtime Qt requires no Pillow/numpy/scipy; only PNG files are packaged.
- `tests/test_character_animation.py` verifies movement covers thousands of source pixels per action.
- `tools/preview_illustrated_pet.py` captures adjacent frames with the actual Qt widget.
- Native Apple Silicon and Intel Mac builds still need hands-on verification.
