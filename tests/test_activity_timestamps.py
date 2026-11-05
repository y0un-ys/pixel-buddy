"""Regression tests for timestamp-only activity classification."""
import sys
from types import SimpleNamespace

import pytest

from pixel_buddy import activity
from pixel_buddy.activity import ActivityDetector, choose_activity


@pytest.fixture(autouse=True)
def isolated_desktop_windows(monkeypatch):
    monkeypatch.setattr(activity, 'visible_video_window', lambda: False)


def test_newest_input_wins_in_both_transition_directions():
    now = 100.0
    assert choose_activity(99.0, 98.8, now) == "typing"
    assert choose_activity(99.0, 99.9, now) == "mouse"
    assert choose_activity(100.0, 99.9, now) == "typing"


def test_equal_recent_timestamps_favor_keyboard():
    assert choose_activity(99.0, 99.0, 100.0) == "typing"


@pytest.mark.parametrize(("last_key", "last_mouse", "expected"), [
    (96.0, 95.0, "idle"),
    (96.001, 95.0, "typing"),
    (96.0, 95.001, "mouse"),
    (96.0, 99.0, "mouse"),
    (99.0, 95.0, "typing"),
])
def test_input_expiry_boundaries(last_key, last_mouse, expected):
    assert choose_activity(last_key, last_mouse, 100.0) == expected


def test_mouse_requires_a_recent_mouse_event():
    assert choose_activity(-10000.0, 99.0, 100.0) == "mouse"
    assert choose_activity(-10000.0, 90.0, 100.0) == "idle"


def test_keyboard_permission_unavailable_does_not_fake_typing():
    assert choose_activity(99.0, -10000.0, 100.0, False) == "idle"
    assert choose_activity(99.9, 99.0, 100.0, False) == "mouse"
    assert choose_activity(99.9, 95.0, 100.0, False) == "idle"


def test_idle_without_recent_input():
    assert choose_activity(-10000.0, -10000.0, 100.0) == "idle"


@pytest.mark.parametrize(("last_key", "last_mouse", "expected"), [
    (101.0, -10000.0, "idle"),
    (-10000.0, 101.0, "idle"),
    (101.0, 102.0, "idle"),
    (101.0, 99.0, "mouse"),
    (99.0, 101.0, "typing"),
])
def test_future_timestamps_are_ignored(last_key, last_mouse, expected):
    assert choose_activity(last_key, last_mouse, 100.0) == expected


def test_scroll_is_observed_even_when_keyboard_listener_is_unavailable(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    listeners = []
    class MouseListener:
        def __init__(self, **callbacks):
            self.callbacks = callbacks
            self.started = False
            listeners.append(self)

        def start(self):
            self.started = True

    def denied_keyboard_listener(**_callbacks):
        raise RuntimeError("Input monitoring denied")

    monkeypatch.setitem(sys.modules, "pynput", SimpleNamespace(
        keyboard=SimpleNamespace(Listener=denied_keyboard_listener),
        mouse=SimpleNamespace(Listener=MouseListener)))
    monkeypatch.setattr(activity, "mac_input_monitoring_granted", lambda: False)
    monkeypatch.setattr(activity.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(activity, "foreground", lambda: ("", ""))
    detector = ActivityDetector()

    assert not detector.keyboard_available
    assert detector.mouse_available
    assert listeners[0].started
    assert detector.detect() == "idle"
    listeners[0].callbacks["on_scroll"](0, 0, 0, 1)
    assert detector.last_mouse == detector.last_input == 100.0
    assert detector.mouse_events_seen == 1
    assert detector.detect() == "mouse"


@pytest.mark.parametrize(("exe", "title", "expected"), [
    ("minecraft.exe", "", "gaming"),
    ("safari", "youtube", "watching"),
])
def test_foreground_modes_keep_priority_over_recent_input(monkeypatch, exe, title, expected):
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.video_state = None
    detector.mac_activity = None
    detector.last_key = 99.0
    detector.last_mouse = 99.9
    detector.keyboard_available = True
    monkeypatch.setattr(activity.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(activity, "foreground", lambda: (exe, title))
    assert detector.detect() == expected


@pytest.mark.parametrize("title", (
    "Sample film - Vimeo", "Sample film - Dailymotion", "TVING",
    "드라마 - 웨이브", "시리즈 - Disney+", "쿠팡플레이",
    "방송 - 치지직", "방송 - SOOP", "Sample - Prime Video",
    "Sample - Apple TV", "sample.mp4", "sample.webm",
))
def test_browser_video_titles_select_watching(monkeypatch, title):
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.video_state = None
    detector.mac_activity = None
    detector.last_key = 99.0
    detector.last_mouse = 99.9
    detector.keyboard_available = True
    monkeypatch.setattr(activity.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(activity, "foreground", lambda: ("safari", title.lower()))
    assert detector.detect() == "watching"


@pytest.mark.parametrize("exe,title", (
    ("safari", "Video editing documentation"),
    ("safari", "Search results"),
    ("code", "sample.mp4 - editor"),
))
def test_nonvideo_window_keeps_input_mode(monkeypatch, exe, title):
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.video_state = None
    detector.mac_activity = None
    detector.last_key = 99.0
    detector.last_mouse = 99.9
    detector.keyboard_available = True
    monkeypatch.setattr(activity.time, "monotonic", lambda: 100.0)
    monkeypatch.setattr(activity, "foreground", lambda: (exe, title.lower()))
    assert detector.detect() == "mouse"


@pytest.mark.parametrize("tap_available", (True, False))
def test_mac_keyboard_uses_raw_events_and_releases_tap(monkeypatch, tap_available):
    installed = {}
    removed = []
    tap = SimpleNamespace()
    source = SimpleNamespace()
    loop = SimpleNamespace()

    def create_tap(location, placement, options, mask, callback, context):
        installed.update(location=location, options=options, mask=mask, callback=callback)
        return tap if tap_available else None

    quartz = SimpleNamespace(
        kCGSessionEventTap=1, kCGHeadInsertEventTap=0,
        kCGEventTapOptionListenOnly=1, kCGEventKeyDown=10,
        kCGEventTapDisabledByTimeout=-2, kCGEventTapDisabledByUserInput=-1,
        CGEventMaskBit=lambda event: 1 << event, CGEventTapCreate=create_tap,
        CGEventTapEnable=lambda token, enabled: None,
    )
    core = SimpleNamespace(
        kCFRunLoopCommonModes="common",
        CFMachPortCreateRunLoopSource=lambda allocator, token, order: source,
        CFRunLoopGetCurrent=lambda: loop,
        CFRunLoopAddSource=lambda owner, item, mode: installed.update(source=item),
        CFRunLoopRemoveSource=lambda owner, item, mode: removed.append(item),
        CFMachPortInvalidate=lambda token: removed.append(token),
    )

    class MouseListener:
        def __init__(self, **callbacks):
            pass

        def start(self):
            pass

        def stop(self):
            pass

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setitem(sys.modules, "Quartz", quartz)
    monkeypatch.setitem(sys.modules, "CoreFoundation", core)
    monkeypatch.setitem(sys.modules, "pynput", SimpleNamespace(
        keyboard=SimpleNamespace(), mouse=SimpleNamespace(Listener=MouseListener)))
    monkeypatch.setattr(activity, "mac_input_monitoring_granted", lambda: True)
    monkeypatch.setattr(activity.time, "monotonic", lambda: 100.0)
    detector = ActivityDetector()
    if not tap_available:
        assert not detector.keyboard_available
        assert detector.mouse_available
        detector.stop()
        assert removed == []
        return
    try:
        assert detector.keyboard_available
        assert installed["mask"] == 1 << 10
        assert installed["options"] == quartz.kCGEventTapOptionListenOnly
        # No event character/keycode methods exist: timing alone must suffice.
        event = SimpleNamespace()
        assert installed["callback"](None, 10, event, None) is event
        assert detector.last_key == 100.0
        assert detector.keyboard_events_seen == 1
    finally:
        detector.stop()
    assert removed == [source, tap]
