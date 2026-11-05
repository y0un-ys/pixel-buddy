"""Activity and display-state tests for the animated illustrated companions."""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

from pixel_buddy.activity import choose_activity, presentation_mode
from pixel_buddy.activity_effects import overlay_svg, display_computer, MODES
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
    controller = 'x="271" y="214" width="45" height="15"'
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
    assert "overlay_svg(self.mode, self.frame, kwargs['pc'], species)" in code


def test_keyboard_keys_alternate_without_duplicate_animal_limbs():
    frames = [overlay_svg("typing", n, "laptop", "dog") for n in range(4)]
    for output in frames:
        assert 'x="245" y="219" width="50" height="13"' in output
        assert 'M227 203' not in output
        assert 'Q244 207' not in output
        assert 'stroke-width="12"' not in output
        ET.fromstring(output)
    assert 'cx="257"' in frames[0]
    assert 'cx="281"' in frames[1]
    assert 'cx="257"' in frames[2]
    assert frames[0] != frames[2]


def test_mouse_moves_slightly_without_artificial_arm():
    frames = [overlay_svg("mouse", n) for n in range(4)]
    assert 'cx="281"' in frames[0]
    assert 'cx="284"' in frames[1]
    assert 'cx="287"' in frames[2]
    assert 'cx="284"' in frames[3]
    assert all('M228 203' not in output for output in frames)


def test_cinema_replaces_laptop_only_when_watching():
    assert display_computer("laptop", "watching") == "desktop"
    assert display_computer("laptop", "typing") == "laptop"
    assert display_computer("dual", "watching") == "dual"
    watching = overlay_svg("watching", 0, "desktop")
    assert 'width="57" height="42"' in watching
    assert 'x="270" y="222"' not in watching
    assert 'l-5 -22 h29' in watching
