"""Cross-platform checks for v0.4.2 visual bug fixes, no Qt required."""
import ast
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / 'src' / 'pixel_buddy' / 'main.py').read_text(encoding='utf-8')


def test_no_qwidget_event_shadowing():
    tree = ast.parse(MAIN)
    assert not any(
        isinstance(n, ast.Attribute) and n.attr == 'event' and
        isinstance(n.ctx, ast.Store) for n in ast.walk(tree)
    )


def test_computer_previews_never_use_gaming_mode():
    assert "canvas.mode = 'typing'" in MAIN
    assert "self.preview.mode = 'typing'" in MAIN
    assert "canvas.mode = 'typing' if info['category'] != '컴퓨터' else 'gaming'" not in MAIN


def test_desk_and_prop_boundaries():
    assert "rect(42, 65, 110, 6, desk_top)" in MAIN
    assert "rect(135, 57, 10, 8" in MAIN
    assert "rect(136, 63, 12, 2" in MAIN
    assert "rect(135, 56, 12, 9" in MAIN


def test_mac_topmost_settings_persist():
    assert "self.ui_settings.setValue('always_on_top', self.always_on_top)" in MAIN
    assert "Qt.WindowType.Window if sys.platform == 'darwin'" in MAIN


def test_new_art_matches_compact_dimensions_and_alpha():
    for animal in ('dog', 'cat', 'bear', 'fox', 'rabbit'):
        for mode in ('typing', 'mouse', 'watching', 'gaming', 'idle'):
            png = (ROOT / 'assets' / 'sprites' / f'{animal}_{mode}.png').read_bytes()
            assert png[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II', png[16:24]) == (256, 56)
            assert png[25] == 6
