from pixel_buddy.theme import DEFAULT_THEME, make_stylesheet


def test_default_light_contrast_palette():
    t = DEFAULT_THEME
    assert t.background == '#FFFFFF'
    assert t.foreground == '#222222'
    assert t.button_text == '#FFFFFF'
    css = make_stylesheet(t)
    for widget in ('QDialog', 'QScrollArea', 'QLineEdit', 'QComboBox', 'QMenu', 'QTabBar', 'QCheckBox'):
        assert widget in css
    assert 'QFrame#inventoryRow' in css
    assert '#29243B' not in css


def test_no_old_dark_inline_widget_styles():
    from pathlib import Path
    main = (Path(__file__).resolve().parents[1] / 'src/pixel_buddy/main.py').read_text(encoding='utf-8')
    for stale_color in ('#F3EAF8', '#393149', '#29243B', '#DBC8EA', '#DEB8F0', '#443B59'):
        assert stale_color not in main
