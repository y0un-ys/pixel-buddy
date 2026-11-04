"""Source-level checks for UI wiring (Qt integration requires Windows GUI run)."""
from pathlib import Path


def test_management_navigation_is_wired():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'pixel_buddy' / 'main.py').read_text(encoding='utf-8')
    assert "('← 뒤로', 'back')" in source
    assert "('상점', 'shop')" in source
    assert "('인벤토리', 'inventory')" in source
    assert "('설정', 'settings')" in source
    assert 'def navigate_back(self):' in source
    assert "self.ui_settings.setValue('management_position'" in source
    assert "from .theme import DEFAULT_THEME, make_stylesheet" in source


def test_back_always_returns_to_companion_home():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'pixel_buddy' / 'main.py').read_text(encoding='utf-8')
    block = source.split('    def navigate_back(self):', 1)[1].split('    def open_dialog(self):', 1)[0]
    assert "self._show_management('home', record_history=False)" in block
    assert 'self.navigation_history.clear()' in block
    assert 'navigation_history.pop()' not in block
