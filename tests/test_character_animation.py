"""Checks for shipped animated chibi frame PNGs and source coordinates."""
from pathlib import Path
from PIL import Image, ImageChops
from pixel_buddy.character_animation import (
    atlas_path, source_rect, FRAME_COUNT, FRAME_WIDTH, FRAME_HEIGHT, MODE_ORDER
)

ROOT = Path(__file__).resolve().parents[1]
ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")


def test_atlases_present_for_all_approved_animals():
    for animal in ANIMALS:
        path = atlas_path(ROOT, animal)
        assert path.exists(), path
        with Image.open(path) as im:
            assert im.size == (FRAME_WIDTH * FRAME_COUNT,
                               FRAME_HEIGHT * len(MODE_ORDER))


def test_all_activity_rows_have_actual_distinct_character_frames():
    for animal in ANIMALS:
        with Image.open(atlas_path(ROOT, animal)) as sheet:
            sheet = sheet.convert("RGBA")
            for row, mode in enumerate(MODE_ORDER):
                y = row * FRAME_HEIGHT
                first = sheet.crop((0, y, FRAME_WIDTH, y + FRAME_HEIGHT))
                second = sheet.crop((FRAME_WIDTH, y,
                                     FRAME_WIDTH * 2, y + FRAME_HEIGHT))
                assert ImageChops.difference(first, second).getbbox(), (animal, mode)


def test_working_paws_have_noticeable_frame_motion():
    # Source-art RGB change must be substantial, not a 1px shimmer.
    for animal in ANIMALS:
        with Image.open(atlas_path(ROOT, animal)) as sheet:
            rgba = sheet.convert("RGB")
            for row, mode in enumerate(MODE_ORDER):
                if mode == "idle":
                    continue
                top = row * FRAME_HEIGHT
                a = rgba.crop((0, top, FRAME_WIDTH, top + FRAME_HEIGHT))
                b = rgba.crop((FRAME_WIDTH, top,
                               2 * FRAME_WIDTH, top + FRAME_HEIGHT))
                delta = ImageChops.difference(a, b).convert("L")
                moving_pixels = sum(delta.histogram()[10:])
                assert moving_pixels > 5500, (animal, mode, moving_pixels)


def test_source_frame_order_cycles_and_modes_do_not_overlap():
    for row, mode in enumerate(MODE_ORDER):
        assert source_rect(mode, 0) == (0, row * FRAME_HEIGHT,
                                        FRAME_WIDTH, FRAME_HEIGHT)
        assert source_rect(mode, 1)[0] == FRAME_WIDTH
        assert source_rect(mode, 2)[0] == FRAME_WIDTH * 2
        assert source_rect(mode, 3)[0] == FRAME_WIDTH * 3
        assert source_rect(mode, 4) == source_rect(mode, 0)
    assert source_rect("invalid", 0) == source_rect("idle", 0)


def test_dog_ear_is_not_cut_off_by_image_edge():
    with Image.open(ROOT / "assets" / "illustrations" / "dog.png") as dog:
        assert dog.size == (FRAME_WIDTH, FRAME_HEIGHT)
        bounds = dog.convert("RGBA").getchannel("A").getbbox()
        assert bounds[0] > 2
        assert bounds[2] < FRAME_WIDTH - 2
