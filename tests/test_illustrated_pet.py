"""Approved illustration integration regression checks."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
import pytest
from PIL import Image, ImageChops
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from pixel_buddy.main import BuddyScene, DesktopBuddy
from pixel_buddy.store import GameStore
from pixel_buddy.cozy_scene import scene_illustration_layers

ROOT = Path(__file__).resolve().parents[1]


def test_all_illustration_files_present():
    animals = ("cat", "dog", "bear", "fox", "rabbit")
    for animal in animals:
        path = ROOT / "assets" / "illustrations" / f"{animal}.png"
        assert path.exists(), str(path)
        assert path.read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))


def test_no_legacy_pet_layers_in_illustration_mode():
    for animal in ("cat", "dog", "bear", "fox", "rabbit"):
        background, foreground = scene_illustration_layers(
            species=animal, mode="typing", prop="plant")
        assert "PET-CHAIR" not in background + foreground
        assert "PET-BODY" not in background + foreground
        assert "PET-PAWS" not in background + foreground
        assert "PET-SCREEN-ACTION" not in background + foreground
        for image in (background, foreground):
            assert ET.fromstring(image).tag.endswith("svg")
        assert "SCENE-FOREGROUND" not in background + foreground


def test_main_scene_loads_illustration_with_fallback():
    source = (ROOT / "src" / "pixel_buddy" / "main.py").read_text("utf-8")
    ast.parse(source)
    assert "scene_illustration_layers(**kwargs)" in source
    assert "'assets' / 'illustrations'" in source
    assert "if illustration.isNull():" in source
    assert "self._illustrations[appearance]" in source


@pytest.fixture(scope="module")
def qt_app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("animal", ("cat", "dog", "bear", "fox", "rabbit"))
@pytest.mark.parametrize("mode", ("typing", "mouse"))
@pytest.mark.parametrize("pc", ("laptop", "desktop", "dual"))
def test_real_working_paws_move_without_bobbing_head(qt_app, animal, mode, pc):
    store = SimpleNamespace(animal=animal, equipped={"컴퓨터": pc})
    scene = BuddyScene(store)
    scene.mode = mode
    images = []
    for frame in range(4):
        scene.frame = frame
        image = scene.grab().toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        images.append(Image.frombytes("RGBA", (image.width(), image.height()),
                                      bytes(image.bits())).convert("RGB"))
    scene.close()
    for first, second in zip(images, images[1:]):
        delta = ImageChops.difference(first, second)
        assert delta.crop((115, 70, 265, 180)).getbbox() is None, (animal, mode, "head")
        hand_motion = delta.crop((200, 190, 260, 219)).convert("L")
        assert sum(hand_motion.histogram()[10:]) > 60, (animal, mode, "paws")


@pytest.mark.parametrize("previous", ("typing", "mouse", "gaming", "watching", "idle", "sleep"))
@pytest.mark.parametrize("expected", ("typing", "mouse", "gaming", "watching", "idle", "sleep"))
def test_auto_mode_changes_on_next_animation_tick(
        qt_app, tmp_path, monkeypatch, previous, expected):
    detected = "idle" if expected == "sleep" else expected
    inactive = 150 if expected == "sleep" else 0
    store = GameStore(tmp_path / "save.sqlite3")
    scene = BuddyScene(store)
    scene.mode = previous
    host = SimpleNamespace(
        store=store, scene=scene, last_tick=100.0, save_tick=100.0,
        _next_event=float("inf"), _last_focus_check=100.0,
        manual_mode="auto", pages={}, dialog=None,
        detector=SimpleNamespace(detect=lambda: detected,
                                 inactive_seconds=lambda: inactive),
    )
    monkeypatch.setattr("pixel_buddy.main.time.monotonic", lambda: 100.0)
    try:
        DesktopBuddy.on_tick(host)
        assert scene.mode == expected
    finally:
        scene.close()
        store.close()


@pytest.mark.parametrize("mode", ("typing", "mouse", "gaming", "watching", "idle", "sleep"))
def test_manual_mode_stays_selected_and_auto_resumes(qt_app, tmp_path, mode):
    store = GameStore(tmp_path / "save.sqlite3")
    scene = BuddyScene(store)
    host = SimpleNamespace(
        manual_mode="auto", scene=scene, pages={},
        detector=SimpleNamespace(detect=lambda: "mouse", inactive_seconds=lambda: 0),
    )
    try:
        DesktopBuddy.set_mode(host, mode)
        assert host.manual_mode == scene.mode == mode
        DesktopBuddy.set_mode(host, "auto")
        assert host.manual_mode == "auto"
        assert scene.mode == "mouse"
    finally:
        scene.close()
        store.close()
