import plistlib
import sys
from pathlib import Path
from pixel_buddy import autostart


def test_mac_app_path(monkeypatch, tmp_path):
    app = tmp_path / 'PixelBuddy.app'
    exe = app / 'Contents' / 'MacOS' / 'PixelBuddy'
    exe.parent.mkdir(parents=True)
    exe.write_text('')
    (app / 'Contents' / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleName': 'PixelBuddy'}))
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, 'executable', str(exe))
    assert autostart.mac_app_path() == app
    assert autostart.executable_path() == exe


def test_mac_autostart_toggle(monkeypatch, tmp_path):
    app = tmp_path / 'PixelBuddy.app'
    exe = app / 'Contents' / 'MacOS' / 'PixelBuddy'
    exe.parent.mkdir(parents=True)
    exe.write_text('')
    (app / 'Contents' / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleName': 'PixelBuddy'}))
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, 'executable', str(exe))
    agent = tmp_path / 'agents' / 'pixelbuddy.plist'
    monkeypatch.setattr(autostart, 'LAUNCH_AGENT', agent)
    assert autostart.set_enabled(True)[0]
    assert autostart.is_enabled()
    assert plistlib.loads(agent.read_bytes())['ProgramArguments'] == [str(exe)]
    assert autostart.set_enabled(False)[0]
    assert not autostart.is_enabled()
