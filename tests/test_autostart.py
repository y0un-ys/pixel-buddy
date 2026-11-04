import sys
from pathlib import Path
from pixel_buddy import autostart


def test_only_frozen_windows_exe_can_be_registered(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setattr(sys, 'frozen', False, raising=False)
    assert autostart.executable_path() is None
    exe = tmp_path / 'PixelBuddy.exe'
    exe.write_bytes(b'test')
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, 'executable', str(exe))
    assert autostart.executable_path() == exe
    assert autostart.command_for(exe) == f'"{exe}"'


def test_non_windows_cannot_enable(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    assert not autostart.is_enabled()
    assert autostart.set_enabled(True)[0] is False


def test_ui_has_autostart_control():
    s = (Path(__file__).resolve().parents[1] / 'src' / 'pixel_buddy' / 'main.py').read_text(encoding='utf-8')
    assert "QCheckBox('로그인 시 자동 실행 (Windows / macOS)')" in s
    assert 'self.autostart_box.toggled.connect(self.change_autostart)' in s
