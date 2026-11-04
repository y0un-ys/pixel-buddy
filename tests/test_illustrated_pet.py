"""Approved illustration integration regression checks."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from pixel_buddy.cozy_scene import scene_illustration_layers

ROOT = Path(__file__).resolve().parents[1]


def test_all_illustration_files_present():
    animals = ("cat", "dog", "bear", "fox", "rabbit")
    for animal in animals:
        path = ROOT / "assets" / "illustrations" / f"{animal}.png"
        assert path.exists(), str(path)
        assert path.read_bytes().startswith(b"\\x89PNG\\r\\n\\x1a\\n")


def test_no_legacy_pet_layers_in_illustration_mode():
    for animal in ("cat", "dog", "bear", "fox", "rabbit"):
        background, foreground = scene_illustration_layers(
            species=animal, mode="typing", prop="plant")
        assert "PET-CHAIR" not in background + foreground
        assert "PET-BODY" not in background + foreground
        assert "PET-PAWS" not in background + foreground
        for image in (background, foreground):
            assert ET.fromstring(image).tag.endswith("svg")
        assert "SCENE-FOREGROUND" not in background + foreground


def test_main_scene_loads_illustration_with_fallback():
    source = (ROOT / "src" / "pixel_buddy" / "main.py").read_text("utf-8")
    ast.parse(source)
    assert "scene_illustration_layers(**kwargs)" in source
    assert "'assets' / 'illustrations'" in source
    assert "if illustration.isNull():" in source
    assert "self._illustrations[species]" in source
