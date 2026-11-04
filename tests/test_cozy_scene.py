"""Portable scene tests; do not need a Qt desktop."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

from pixel_buddy.cozy_scene import ANIMALS, MODES, scene_svg

ROOT = Path(__file__).resolve().parents[1]


def test_source_syntax():
    for filename in ("main.py", "cozy_scene.py", "activity.py"):
        ast.parse((ROOT / "src" / "pixel_buddy" / filename).read_text("utf-8"))


def test_complete_svg_for_all_animals_modes_and_computers():
    for animal in ANIMALS:
        for mode in MODES:
            for pc in ("laptop", "desktop", "dual"):
                content = scene_svg(species=animal, mode=mode, pc=pc, frame=2)
                root = ET.fromstring(content)
                assert root.attrib["viewBox"] == "0 0 480 288"
                assert root.tag.endswith("svg")
                assert len(content) > 3500


def test_every_shop_prop_and_outfit_is_renderable():
    for prop in ("", "plant", "lamp", "plushie"):
        for outfit in ("hoodie", "pajamas", "suit"):
            ET.fromstring(scene_svg("bear", prop=prop, outfit=outfit,
                                   hat="ribbon", room=True, reaction="happy"))


def test_controller_is_only_a_gaming_prop():
    # Controllers and keyboard are mutually exclusive; no old overlaid controls.
    typing = scene_svg(mode="typing", frame=1)
    gaming = scene_svg(mode="gaming", frame=1)
    assert 'M260 216 Q257 209' not in typing
    assert 'M260 216 Q257 209' in gaming
    assert 'rect(77, 63' not in typing


def test_scene_module_is_decoupled_from_qt():
    content = (ROOT / "src" / "pixel_buddy" / "cozy_scene.py").read_text("utf-8")
    assert "PySide6" not in content
