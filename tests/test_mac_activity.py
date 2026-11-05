"""Permission-independent event metadata and extension-free visible windows."""
import sys
from types import SimpleNamespace

import pytest

from pixel_buddy import activity, mac_activity
from pixel_buddy.activity import ActivityDetector
from pixel_buddy.mac_activity import MacActivitySource


def test_native_activity_does_not_start_permission_bound_listeners(monkeypatch):
    source = SimpleNamespace(sample=lambda: (None, None))

    def unexpected_listener(**kwargs):
        pytest.fail("Aggregate timing must not install permission-bound listeners")

    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setattr(mac_activity, 'MacActivitySource', lambda: source)
    monkeypatch.setattr(activity, 'mac_input_monitoring_granted', lambda: False)
    monkeypatch.setitem(sys.modules, 'pynput', SimpleNamespace(
        keyboard=SimpleNamespace(Listener=unexpected_listener),
        mouse=SimpleNamespace(Listener=unexpected_listener)))
    detector = ActivityDetector()
    assert detector.mac_activity is source
    assert detector.listener is detector.mouse_listener is None
    detector.stop()


def test_aggregate_input_drives_modes_without_event_tap(monkeypatch):
    counts = {event: 100 for event in (10, 5, 1, 3, 25, 6, 7, 27, 22)}
    ages = {event: 0.0 for event in counts}
    quartz = SimpleNamespace(
        kCGEventSourceStateCombinedSessionState=0, kCGEventKeyDown=10,
        kCGEventMouseMoved=5, kCGEventLeftMouseDown=1, kCGEventRightMouseDown=3,
        kCGEventOtherMouseDown=25, kCGEventLeftMouseDragged=6,
        kCGEventRightMouseDragged=7, kCGEventOtherMouseDragged=27,
        kCGEventScrollWheel=22,
        CGEventSourceCounterForEventType=lambda state, event: counts[event],
        CGEventSourceSecondsSinceLastEventType=lambda state, event: ages[event],
    )
    monkeypatch.setitem(sys.modules, 'Quartz', quartz)
    monkeypatch.setattr(mac_activity.time, 'monotonic', lambda: 100.0)
    monkeypatch.setattr(activity, 'foreground', lambda: ('code', 'editor'))
    monkeypatch.setattr(activity, 'visible_video_window', lambda: False)
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.mac_activity = MacActivitySource()
    detector.video_state = None
    detector.keyboard_available = detector.mouse_available = False
    detector.last_key = detector.last_mouse = -10000.0
    detector.last_input = 90.0
    detector.keyboard_events_seen = detector.mouse_events_seen = 0
    assert detector.detect() == 'idle'  # Startup counts are not new input.
    counts[10] += 1
    ages[10] = 0.3
    assert detector.detect() == 'typing'
    counts[5] += 1
    ages[5] = 0.2
    assert detector.detect() == 'mouse'
    counts[10] += 1
    ages[10] = 0.1
    assert detector.detect() == 'typing'
    counts[22] += 1
    assert detector.detect() == 'mouse'
    assert detector.last_key == 99.9
    assert detector.last_mouse == detector.last_input == 100.0
    assert detector.keyboard_events_seen == detector.mouse_events_seen == 2
    assert not detector.keyboard_available


@pytest.mark.parametrize('permitted,owner,title,layer,expected', (
    (True, 'Google Chrome', 'A video - YouTube', 0, True),
    (True, 'Safari', 'Netflix', 0, True),
    (True, 'Google Chrome', 'Search results', 0, False),
    (True, 'Code', 'YouTube implementation', 0, False),
    (True, 'Google Chrome', 'YouTube', 1, False),
    (False, 'Google Chrome', '', 0, None),
))
def test_visible_video_window_metadata(monkeypatch, permitted, owner, title, layer, expected):
    queries = []

    def windows(options, relative):
        queries.append(options)
        return [{'owner': owner, 'title': title, 'layer': layer}]

    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setitem(sys.modules, 'Quartz', SimpleNamespace(
        CGPreflightScreenCaptureAccess=lambda: permitted,
        kCGWindowListOptionOnScreenOnly=1, kCGWindowListExcludeDesktopElements=16,
        kCGNullWindowID=0, kCGWindowLayer='layer',
        kCGWindowOwnerName='owner', kCGWindowName='title',
        CGWindowListCopyWindowInfo=windows))
    assert activity.visible_video_window() is expected
    assert queries == ([17] if permitted else [])


def test_visible_video_can_select_watching_while_working_in_another_app(monkeypatch):
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.mac_activity = None
    detector.video_state = None
    detector.keyboard_available = True
    detector.last_key = 99.9
    detector.last_mouse = 99.8
    monkeypatch.setattr(activity.time, 'monotonic', lambda: 100.0)
    monkeypatch.setattr(activity, 'foreground', lambda: ('code', 'editor'))
    monkeypatch.setattr(activity, 'visible_video_window', lambda: True)
    assert detector.detect() == 'watching'
    monkeypatch.setattr(activity, 'visible_video_window', lambda: False)
    assert detector.detect() == 'typing'
