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
            rgba = sheet.convert("RGBA").convert("RGB")
            for row, mode in enumerate(MODE_ORDER):
                if mode == "idle":
                    continue
                top = row * FRAME_HEIGHT
                a = rgba.crop((0, top, FRAME_WIDTH, top + FRAME_HEIGHT))
                b = rgba.crop((FRAME_WIDTH, top,
                               2 * FRAME_WIDTH, top + FRAME_HEIGHT))
                delta = ImageChops.difference(a, b).convert("L")
                moving_pixels = sum(delta.histogram()[10:])
                if mode in ("typing", "mouse"):
                    # Work gestures now move existing paws, not the whole head.
                    paws = delta.crop((163, 181, 254, 247))
                    assert sum(paws.histogram()[10:]) > 300, (animal, mode)
                    assert delta.crop((0, 0, FRAME_WIDTH, 181)).getbbox() is None
                    assert delta.crop((0, 247, FRAME_WIDTH, FRAME_HEIGHT)).getbbox() is None
                else:
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


def test_pajamas_atlases_have_transparent_moving_frames_for_every_animal():
    for animal in ANIMALS:
        with Image.open(atlas_path(ROOT, animal, "pajamas")) as source:
            sheet = source.convert("RGBA")
            assert sheet.size == (1200, 1920)
            assert sheet.getchannel("A").getextrema()[0] == 0
            for mode in MODE_ORDER:
                frames = [sheet.crop((x, y, x + w, y + h))
                          for x, y, w, h in (source_rect(mode, i) for i in range(4))]
                for first, second in zip(frames, frames[1:]):
                    delta = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
                    assert delta.getbbox(), (animal, mode)


def test_pajamas_hand_gestures_do_not_pull_the_legs_or_head():
    for animal in ANIMALS:
        with Image.open(atlas_path(ROOT, animal, "pajamas")) as source:
            sheet = source.convert("RGBA").convert("RGB")
            for mode in ("typing", "mouse", "watching", "gaming", "idle"):
                row = MODE_ORDER.index(mode)
                first = sheet.crop((0, row * 320, 300, (row + 1) * 320))
                for frame in range(1, 4):
                    other = sheet.crop((frame * 300, row * 320,
                                        (frame + 1) * 300, (row + 1) * 320))
                    delta = ImageChops.difference(first, other)
                    assert delta.crop((0, 0, 300, 181)).getbbox() is None, (animal, mode, "head")
                    assert delta.crop((0, 247, 300, 320)).getbbox() is None, (animal, mode, "legs")
