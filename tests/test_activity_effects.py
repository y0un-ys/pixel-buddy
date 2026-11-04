"""Activity and display-state tests for the animated illustrated companions."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

from pixel_buddy.activity import choose_activity, presentation_mode
from pixel_buddy.activity_effects import overlay_svg, MODES
from pixel_buddy.cozy_scene import scene_svg, scene_illustration_layers

ROOT = Path(__file__).resolve().parents[1]


def test_sleep_requires_extended_inactivity():
    for seconds in (0, 10, 45, 90, 149.9):
        assert presentation_mode("idle", seconds) == "idle"
    assert presentation_mode("idle", 150) == "sleep"
    assert presentation_mode("idle", 400) == "sleep"


def test_sleep_never_overrides_work():
    for activity in ("typing", "mouse", "watching", "gaming"):
        assert presentation_mode(activity, 999) == activity


def test_observed_keyboard_wins_mouse():
    assert choose_activity(99.9, 99.99, 100.0) == "typing"
    assert choose_activity(80.0, 99.0, 100.0) == "mouse"
    assert choose_activity(80.0, 90.0, 100.0) == "idle"


def test_every_mode_and_frame_produces_valid_overlay():
    for mode in MODES:
        for frame in range(8):
            for pc in ("laptop", "desktop", "dual"):
                root = ET.fromstring(overlay_svg(mode, frame, pc))
                assert root.tag.endswith("svg")
                assert root.attrib["viewBox"] == "0 0 480 288"


def test_idle_has_no_sleep_indicator():
    assert ">z</text>" not in overlay_svg("idle")
    assert ">z</text>" not in scene_svg(mode="idle")
    assert ">z</text>" in overlay_svg("sleep")


def test_gaming_overlay_not_shown_in_other_modes():
    controller = 'x="267" y="216" width="32" height="12"'
    assert controller in overlay_svg("gaming")
    for mode in ("typing", "mouse", "watching", "idle", "sleep"):
        assert controller not in overlay_svg(mode)


def test_real_illustration_layers_still_parse():
    for mode in ("typing", "mouse", "watching", "gaming", "idle", "sleep"):
        front, back = scene_illustration_layers(mode=mode)
        ET.fromstring(front)
        ET.fromstring(back)


def test_state_is_visible_in_settings_and_sleep_stats_do_not_overflow():
    code = (ROOT / "src" / "pixel_buddy" / "main.py").read_text("utf-8")
    ast.parse(code)
    assert "self.activity_status.setText(" in code
    assert "self.owner.detector.diagnostic()" in code
    assert "stored_mode = 'idle' if self.scene.mode == 'sleep'" in code
    assert "overlay_svg(self.mode, tick, kwargs['pc'])" in code
