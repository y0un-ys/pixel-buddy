"""Regression tests for timestamp-only activity classification."""
from pixel_buddy.activity import choose_activity


def test_recent_keyboard_has_priority_over_recent_mouse():
    now = 100.0
    assert choose_activity(99.0, 99.8, now) == "typing"


def test_mouse_requires_a_recent_mouse_event():
    assert choose_activity(-10000.0, 99.0, 100.0) == "mouse"
    assert choose_activity(-10000.0, 90.0, 100.0) == "idle"


def test_keyboard_permission_unavailable_does_not_fake_typing():
    assert choose_activity(99.0, -10000.0, 100.0, False) == "idle"


def test_idle_without_recent_input():
    assert choose_activity(-10000.0, -10000.0, 100.0) == "idle"


def test_invalid_future_timestamp_is_not_typing():
    assert choose_activity(101.0, -10000.0, 100.0) == "idle"
