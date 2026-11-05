# Pixel Buddy — Development

`dev` is the active development branch. `main` is for tested/stable releases only.

## Current version

**v0.4.8 — alternated typing contacts, linear mouse, and cinema-style watching**

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

## v0.4.8 animation checks

- Render snapshots with `python tools/preview_illustrated_pet.py`; the CI uploads `activity_states.png` and per-mode snapshots.
- The native gesture overlay is synchronized to 250ms animation ticks.
- The base pose is intentionally held still during typing and mouse movements, to avoid the previous grindstone-like motion.
- Watching temporarily shows a desktop monitor only in the scene; equipped computer metadata is not modified.

## Input transitions and painted-paw verification

- Automatic typing/mouse selection follows the newest observed event, including
  mouse movement, clicks and scrolling. State changes are checked every 250ms.
- Work-mode atlas frames animate the existing painted paws while keeping the
  head and lower body still; devices sit beneath the same painted hand pixels.
- macOS keyboard detection uses a passive Quartz key-down tap on the main run
  loop, without reading key contents or decoding a keyboard layout. This avoids
  the Carbon worker-thread assertion seen with pynput on recent macOS.
- `tools/preview_illustrated_pet.py` captures all five animals, three computers,
  six modes and four frames, plus shared preview/pet sizes on light/dark backgrounds.
- Verify typing -> mouse -> typing, click and scroll, manual -> automatic mode,
  and idle -> sleep -> active transitions before rebuilding the native app.

## Browser video and shop assets

- On macOS, the default extension-free watching heuristic scans visible browser
  window titles, including a YouTube/OTT window beside another active app.
  Paused videos also count while the window is visible; this is intentionally
  not playback detection. Games retain their existing foreground priority.
- macOS may require Screen & System Audio Recording permission to reveal window
  titles. The app checks permission without prompting and explains this in its
  diagnostics; it does not capture screen frames or audio.
- macOS keyboard/mouse activity uses aggregate event counters and last-event
  timestamps, not permission-bound key-content listeners. New event counts are
  baselined at launch so old session activity cannot synthesize typing.
- Development builds are ad-hoc signed: their code-hash designated requirement
  changes after rebuilds, so permissions tied to that identity can be lost.
  Aggregate input activity avoids relying on those listener permissions; window
  title permissions still belong to macOS. Do not modify TCC records.

- Optional Chromium video integration lives in `tools/browser_extension/`.
  See its README for unpacked-install steps. It reports real HTML video
  play/pause state, not page titles or URLs, to loopback port 38673.
- Real extension reports take precedence over title heuristics. Paused video
  does not select watching; missing/stale extension reports use best-effort
  browser-title detection. Watching is selected while a supported browser is
  foreground, not while working in another application.
- App settings show whether the bridge is waiting, connected, or playing.
  Browser extension installation/site permissions require the user's action.
- Audio-only media and browser/internal pages do not count as video. See the
  extension README for closed-shadow-root and background timer limitations.
- The shop's visible cards and main preview now advance the actual character
  atlas. Preview still does not spend coins or persist equipment.
- Pajamas, suit and headwear await compatible illustration assets. Their shop
  purchase/equip controls are disabled so invisible artwork is not sold.
  Existing inventory/save records are preserved. See `ASSET_GUIDE.md`.
- Extension tests: `node --test tools/browser_extension/tests/*.test.mjs`.
