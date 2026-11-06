"""Product images and positioning for the existing Pixel Buddy shop.

All eight product thumbnails are normalized transparent 300x320 RGBA-compatible
PNGs. Coordinates are in BuddyScene's existing logical 480x288 workspace.
Pajama, suit and streetwear variants are full-character illustrations, not overlays.
"""
from pathlib import Path

PRODUCT_IDS = (
    "suit", "streetwear", "cat_ears", "ribbon", "bunny_ears",
    "gaming_headset", "stream_microphone", "ring_light",
)
FULL_PORTRAIT_OUTFITS = ("pajamas", "suit", "streetwear")

# Coordinates are intentionally conservative: preserve faces, chair, paws and
# original seated silhouette. Product art is scaled down for display in-scene.
SCENE_BOXES = {
    "suit": (177, 188, 90, 72),
    "streetwear": (174, 186, 96, 79),
    "cat_ears": (122, 67, 145, 112),
    "ribbon": (172, 82, 51, 47),
    "bunny_ears": (120, 50, 150, 131),
    "gaming_headset": (126, 75, 141, 108),
    "stream_microphone": (378, 157, 82, 81),
    "ring_light": (380, 119, 78, 115),
}


def shop_icon_path(root, item_id):
    if item_id not in PRODUCT_IDS:
        return None
    return Path(root) / "assets" / "shop" / "items" / (item_id + ".png")


def portrait_variant_path(root, species, outfit):
    if outfit not in FULL_PORTRAIT_OUTFITS:
        return None
    if species not in ("cat", "dog", "bear", "fox", "rabbit"):
        return None
    return Path(root) / "assets" / "illustrations" / outfit / (species + ".png")


def equipped_layers(equipment):
    """Draw order from body wearables through headwear and desk ornaments."""
    return tuple(item for item in (
        equipment.get("의상", ""),
        equipment.get("머리띠", ""),
        equipment.get("소품", ""),
    ) if item in SCENE_BOXES)
