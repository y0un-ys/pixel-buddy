"""Pre-rendered chibi character animations.

Frame atlases are arranged as 4 columns x 6 activity rows.
All coordinates are source pixels. Qt paints them without Python imaging deps.
"""
from pathlib import Path

FRAME_WIDTH = 300
FRAME_HEIGHT = 320
FRAME_COUNT = 4
MODE_ORDER = ("typing", "mouse", "watching", "gaming", "idle", "sleep")


def source_rect(mode, frame):
    """Return x, y, width and height for an atlas cell."""
    row = MODE_ORDER.index(mode) if mode in MODE_ORDER else MODE_ORDER.index("idle")
    column = max(0, int(frame)) % FRAME_COUNT
    return (column * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT)


def atlas_path(asset_root, species):
    if species not in ("cat", "dog", "bear", "fox", "rabbit"):
        species = "cat"
    return Path(asset_root) / "assets" / "animations" / (species + ".png")
