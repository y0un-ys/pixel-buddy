"""Local extension protocol, origin checks, expiry and detector integration."""
import http.client
import json

import pytest

from pixel_buddy import activity, browser_media
from pixel_buddy.activity import ActivityDetector
from pixel_buddy.browser_media import BrowserMediaBridge

ORIGIN = 'chrome-extension://' + 'a' * 32


@pytest.fixture(autouse=True)
def isolated_desktop_windows(monkeypatch):
    monkeypatch.setattr(activity, 'visible_video_window', lambda: False)


@pytest.fixture
def bridge():
    bridge = BrowserMediaBridge(port=0)
    yield bridge
    bridge.stop()


def request(bridge, method, path, payload=None, **headers):
    connection = http.client.HTTPConnection('127.0.0.1', bridge.port, timeout=2)
    body = json.dumps(payload) if payload is not None else None
    options = {key: value for key, value in {
        'Origin': ORIGIN, 'Content-Type': 'application/json', **headers}.items()
        if value is not None}
    connection.request(method, path, body=body, headers=options)
    response = connection.getresponse()
    result = response.status, dict(response.getheaders()), json.loads(response.read())
    connection.close()
    return result


def test_play_pause_health_and_expiry(bridge, monkeypatch):
    now = [100.0]
    monkeypatch.setattr(browser_media.time, 'monotonic', lambda: now[0])
    status, headers, payload = request(bridge, 'GET', '/health')
    assert status == 200 and payload == {'connected': True}
    assert headers['Access-Control-Allow-Origin'] == ORIGIN
    assert bridge.playback_for('google chrome') is None
    for playing in (True, False, True):
        status, _, payload = request(
            bridge, 'POST', '/media-state', {'browser': 'chromium', 'playing': playing})
        assert status == 200 and payload == {'accepted': True}
        assert bridge.playback_for('google chrome') is playing
    assert bridge.playback_for('code') is None
    assert bridge.playback_for('safari') is None
    assert bridge.playback_for('chromium') is True
    assert bridge.playback_for('arc.exe') is True
    now[0] = 106.0
    assert bridge.playback_for('google chrome') is None


@pytest.mark.parametrize('origin', ('https://example.com', 'null', '', 'chrome-extension://bad'))
def test_web_pages_cannot_report_playback(bridge, origin):
    status, headers, _ = request(
        bridge, 'POST', '/media-state', {'browser': 'chromium', 'playing': True},
        Origin=origin)
    assert status == 403
    assert 'Access-Control-Allow-Origin' not in headers
    assert bridge.playback_for('google chrome') is None


@pytest.mark.parametrize('payload', (
    {'browser': 'chromium', 'playing': 'true'},
    {'browser': 'chromium', 'playing': 1},
    {'browser': 'safari', 'playing': True},
    {'browser': 'chromium', 'playing': True, 'url': 'must-not-be-accepted'},
    [], None,
))
def test_only_exact_boolean_protocol_is_accepted(bridge, payload):
    status, _, _ = request(bridge, 'POST', '/media-state', payload)
    assert status in (400, 413)
    assert bridge.playback_for('google chrome') is None


def test_host_header_preflight_and_body_limits(bridge):
    assert request(bridge, 'GET', '/health', Host='attacker.invalid')[0] == 403
    assert request(bridge, 'GET', '/other')[0] == 404
    status, headers, _ = request(
        bridge, 'OPTIONS', '/media-state', **{
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'})
    assert status == 200
    assert headers['Access-Control-Allow-Headers'] == 'Content-Type'
    assert request(bridge, 'POST', '/media-state', {'large': 'x' * 150})[0] == 413
    assert request(bridge, 'POST', '/media-state', {}, **{'Content-Type': 'text/plain'})[0] == 415


def test_privileged_extension_health_get_can_omit_origin_but_post_cannot(bridge):
    # Chromium host-permission GET omits Origin; it is a read-only health probe.
    assert request(bridge, 'GET', '/health', Origin=None)[0] == 200
    assert request(bridge, 'GET', '/health', Origin='https://example.com')[0] == 403
    assert request(bridge, 'GET', '/health', Origin=None, Host='wrong.invalid')[0] == 403
    assert request(bridge, 'POST', '/media-state',
                   {'browser': 'chromium', 'playing': True}, Origin=None)[0] == 403


@pytest.mark.parametrize('playing,title,expected', (
    (True, 'Unlisted video website', 'watching'),
    (False, 'YouTube - paused video', 'mouse'),
    (None, 'YouTube - no extension report', 'watching'),
))
def test_real_playback_overrides_title_heuristic(bridge, monkeypatch, playing, title, expected):
    detector = ActivityDetector.__new__(ActivityDetector)
    detector.video_state = bridge.playback_for
    detector.mac_activity = None
    detector.last_key = 99.0
    detector.last_mouse = 99.9
    detector.keyboard_available = True
    monkeypatch.setattr(activity.time, 'monotonic', lambda: 100.0)
    monkeypatch.setattr(activity, 'foreground', lambda: ('google chrome', title.lower()))
    if playing is not None:
        request(bridge, 'POST', '/media-state', {'browser': 'chromium', 'playing': playing})
    assert detector.detect() == expected
