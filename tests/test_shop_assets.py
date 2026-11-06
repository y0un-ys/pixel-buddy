"""Regression checks for the existing shop's image-backed product catalogue."""
from pathlib import Path

from PIL import Image

from pixel_buddy.shop_assets import (
    PRODUCT_IDS, SCENE_BOXES, shop_icon_path, portrait_variant_path,
    equipped_layers,
)
from pixel_buddy.store import CATALOG, ITEMS, DEFAULT_EQUIP, illustration_item_available

ROOT = Path(__file__).resolve().parents[1]
ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")


def test_exact_product_icons_exist_and_are_transparent():
    assert len(PRODUCT_IDS) == 8
    for item in PRODUCT_IDS:
        path = shop_icon_path(ROOT, item)
        assert path.is_file(), path
        with Image.open(path) as image:
            assert image.size == (300, 320)
            rgba = image.convert("RGBA")
            assert rgba.getchannel("A").getextrema() == (0, 255)
        assert item in ITEMS and illustration_item_available(item)
        assert item in SCENE_BOXES


def test_original_shop_categories_and_old_ids_are_retained():
    assert len(CATALOG) == len(set(row[0] for row in CATALOG))
    assert set(DEFAULT_EQUIP) == {"의상", "머리띠", "컴퓨터", "책상", "소품"}
    assert ITEMS["suit"]["category"] == "의상"
    assert ITEMS["cat_ears"]["category"] == "머리띠"
    assert ITEMS["ribbon"]["category"] == "머리띠"
    assert ITEMS["bunny_ears"]["category"] == "머리띠"
    assert ITEMS["streetwear"]["category"] == "의상"
    assert ITEMS["stream_microphone"]["category"] == "소품"
    assert ITEMS["ring_light"]["category"] == "소품"
    assert ITEMS["gaming_headset"]["category"] == "머리띠"


def test_all_full_outfit_portraits_remain_whole():
    for animal in ANIMALS:
        for outfit in ("pajamas", "suit", "streetwear"):
            path = portrait_variant_path(ROOT, animal, outfit)
            assert path.is_file(), (animal, outfit)
            with Image.open(path) as image:
                assert image.size == (300, 320)
                assert image.convert("RGBA").getchannel("A").getextrema() == (0, 255)
    assert portrait_variant_path(ROOT, "cat", "hoodie") is None


def test_layer_draw_order_and_unknown_items_are_safe():
    sample = {"의상": "streetwear", "머리띠": "ribbon", "소품": "ring_light"}
    assert equipped_layers(sample) == ("streetwear", "ribbon", "ring_light")
    assert shop_icon_path(ROOT, "unknown") is None
    assert not illustration_item_available("unknown")
