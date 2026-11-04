"""Build approved seated chibi frame atlases with gentle local deformations.

Regeneration (developer workstation only):
    python -m pip install Pillow numpy scipy
    python tools/generate_chibi_animations.py

Runtime needs none of these three packages: only the generated PNGs.
"""
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image

ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")
MODES = ("typing", "mouse", "watching", "gaming", "idle", "sleep")
W, H = 300, 320
COUNT = 4
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets" / "illustrations"
OUT = ROOT / "assets" / "animations"


def pad_portrait(animal):
    source = Image.open(BASE / (animal + ".png")).convert("RGBA")
    if source.size == (W, H):
        return source
    canvas = Image.new("RGBA", (W, H))
    canvas.alpha_composite(source, ((W - source.width) // 2, 14))
    return canvas


def morph(frame, mode, phase_index):
    """Spatially smooth local paw/head/tail deformation preserving transparency."""
    phase = (0, 1, 0, -1)[phase_index]
    alternate = (0, -1, 0, 1)[phase_index]
    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    dx = np.zeros((H, W), dtype="float32")
    dy = np.zeros_like(dx)

    def move(x, y, sx, sy, horizontal=0.0, vertical=0.0):
        nonlocal dx, dy
        weight = np.exp(-.5 * ((xx-x)/sx)**2 - .5 * ((yy-y)/sy)**2)
        dx += horizontal * weight
        dy += vertical * weight

    # Locations are anchored to the original approved seated illustration.
    # The moving regions deform together, rather than layering stray paws.
    if mode == "typing":
        move(146, 113, 86, 83, vertical=-1.3*phase)
        move(191, 207, 24, 24, horizontal=1.9*phase, vertical=4.0*phase)
        move(227, 208, 22, 22, horizontal=-1.5*phase, vertical=-3.5*phase)
        move(56, 208, 42, 40, horizontal=1.3*phase)
    elif mode == "mouse":
        move(147, 112, 87, 80, horizontal=1.0*phase)
        move(214, 202, 34, 27, horizontal=5.0*phase, vertical=1.9*alternate)
    elif mode == "watching":
        move(140, 108, 97, 83, vertical=2.4*phase)
        move(196, 203, 31, 31, vertical=1.4*alternate)
    elif mode == "gaming":
        move(146, 113, 85, 81, vertical=-3.2*phase)
        move(184, 203, 32, 28, horizontal=-2.0*phase, vertical=3.7*phase)
        move(224, 204, 30, 26, horizontal=2.1*phase, vertical=-3.0*phase)
        move(57, 201, 43, 43, horizontal=2.0*phase)
    elif mode == "sleep":
        move(143, 113, 90, 95, vertical=3.1+alternate*1.9)
        move(160, 184, 90, 48, vertical=1.8*phase)
    else:
        move(145, 112, 92, 85, vertical=.8*phase)
        move(158, 200, 85, 48, vertical=.9*phase)
        move(55, 197, 41, 41, horizontal=1.5*phase)

    rgba = np.asarray(frame, dtype=np.float32)
    alpha = rgba[:, :, 3] / 255.
    coords = [yy-dy, xx-dx]
    warped_alpha = map_coordinates(alpha, coords, order=1, mode="constant", cval=0)
    warped = np.zeros_like(rgba)
    for channel in range(3):
        premult = rgba[:, :, channel] * alpha
        sampled = map_coordinates(premult, coords, order=1, mode="constant", cval=0)
        warped[:, :, channel] = np.where(
            warped_alpha > .001, sampled / np.maximum(warped_alpha, .001), 0)
    warped[:, :, 3] = warped_alpha * 255.
    return Image.fromarray(np.uint8(np.clip(warped, 0, 255)), "RGBA")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for animal in ANIMALS:
        base = pad_portrait(animal)
        atlas = Image.new("RGBA", (W * COUNT, H * len(MODES)))
        for row, mode in enumerate(MODES):
            for column in range(COUNT):
                atlas.alpha_composite(
                    morph(base, mode, column), (W * column, H * row))
        # P mode with alpha palette is compact and works with Qt QPixmap.
        atlas.quantize(
            colors=192, method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE).save(
                OUT / (animal + ".png"), optimize=True, compress_level=9)
        print(OUT / (animal + ".png"))


if __name__ == "__main__":
    main()
