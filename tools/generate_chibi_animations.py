"""Build approved seated chibi frame atlases with visible painted-paw poses.

Regeneration (developer workstation only):
    python -m pip install Pillow numpy scipy
    python tools/generate_chibi_animations.py

Runtime needs none of these three packages: only the generated PNGs.
"""
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image, ImageDraw

ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")
MODES = ("typing", "mouse", "watching", "gaming", "idle", "sleep")
W, H = 300, 320
COUNT = 4
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets" / "illustrations"
OUT = ROOT / "assets" / "animations"


def pad_portrait(animal):
    # The legacy repaired dog portrait changed the ear's shape. Reconstruct
    # from the approved original instead, keeping the floppy ear silhouette.
    original = (ROOT / "assets" / "illustration_sources" / "dog_original.png"
                if animal == "dog" else BASE / (animal + ".png"))
    source = Image.open(original).convert("RGBA")
    canvas = Image.new("RGBA", (W, H))
    if animal == "dog":
        # Extend only the portion missing behind the original head.
        # Both ears remain drooping, not upright or windswept.
        ear = Image.new("RGBA", (W, H))
        painter = ImageDraw.Draw(ear)
        painter.ellipse((225, 73, 278, 146), fill="#E7AF8D",
                        outline="#7B536A", width=4)
        painter.ellipse((236, 91, 266, 137), fill="#D49A82")
        canvas.alpha_composite(ear)
    canvas.alpha_composite(source, ((W - source.width) // 2, 14)
                           if source.size != (W, H) else (0, 0))
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

    # More distinguishable poses: the painted paws move 12-30 pixels while
    # their sleeves/head move with them. No new disconnected arm primitives.
    left = (-14, 13, -14, 13)[phase_index]
    right = (14, -14, 14, -14)[phase_index]
    if mode == "typing":
        move(184, 214, 26, 24, horizontal=left * .3, vertical=left)
        move(222, 214, 28, 24, horizontal=right * .2, vertical=right)
        move(151, 112, 94, 79, vertical=(-5, 2, -5, 2)[phase_index])
    elif mode == "mouse":
        move(223, 208, 31, 28, horizontal=(0, 14, 25, 6)[phase_index],
             vertical=(0, -5, 0, 4)[phase_index])
        move(157, 115, 93, 77, horizontal=(-3, 0, 4, 0)[phase_index])
    elif mode == "watching":
        move(220, 209, 28, 28, horizontal=(1, -5, 4, -7)[phase_index],
             vertical=(0, -15, -30, -15)[phase_index])
        move(158, 113, 97, 80, vertical=(2, -2, 4, -2)[phase_index])
    elif mode == "gaming":
        move(187, 210, 28, 29, horizontal=(-8, 7, -9, 9)[phase_index],
             vertical=(12, -12, 14, -13)[phase_index])
        move(222, 209, 29, 28, horizontal=(7, -8, 9, -8)[phase_index],
             vertical=(-11, 13, -12, 14)[phase_index])
        move(154, 110, 95, 83, vertical=(-9, 3, -7, 4)[phase_index])
    elif mode == "sleep":
        move(160, 115, 100, 90, horizontal=(-2, 0, 2, 0)[phase_index],
             vertical=(9, 18, 14, 6)[phase_index])
        move(192, 210, 84, 52, vertical=(3, 8, 4, 0)[phase_index])
    else:
        move(160, 120, 98, 78, vertical=(0, 2, 4, 2)[phase_index])
        move(183, 215, 81, 40, vertical=(0, 1, 2, 1)[phase_index])

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
        # Dog portrait fallback uses exactly the corrected input to this atlas.
        if animal == "dog":
            base.save(BASE / "dog.png", optimize=True)
        # Palette with preserved alpha and no runtime Pillow dependency.
        atlas.quantize(
            colors=224, method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE).save(
                OUT / (animal + ".png"), optimize=True, compress_level=9)
        print(OUT / (animal + ".png"))


if __name__ == "__main__":
    main()
