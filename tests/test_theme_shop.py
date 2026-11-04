from pixel_buddy.store import GameStore
from pixel_buddy.theme import THEMES, THEME_PRICES, get_theme, make_stylesheet


def test_theme_catalog_and_accessibility_tokens():
    assert len(THEMES) == 6
    assert THEME_PRICES['white'] == 0
    assert THEMES['white'].background == '#FFFFFF'
    assert THEMES['white'].foreground == '#222222'
    for key, theme in THEMES.items():
        assert theme.name and key in THEME_PRICES
        assert 'QLineEdit' in make_stylesheet(theme)
        assert get_theme(key) is theme


def test_preview_is_not_purchase_and_persists_selection(tmp_path):
    path = tmp_path / 'game.db'
    store = GameStore(path)
    store.growth.coins = 900
    assert store.active_theme == 'white'
    assert 'pink' not in store.owned_themes
    # Merely examining get_theme('pink') does not change the save.
    theme = get_theme('pink')
    assert theme.name == '벚꽃 핑크'
    assert store.growth.coins == 900
    assert '완료' in store.buy_theme('pink')
    assert store.growth.coins == 600
    assert store.active_theme == 'pink'
    assert '완료' in store.buy_theme('dark')
    assert store.growth.coins == 0
    assert '적용' in store.equip_theme('pink')
    assert store.growth.coins == 0
    store.close()
    store = GameStore(path)
    assert store.active_theme == 'pink'
    assert {'pink', 'dark', 'white'} <= store.owned_themes
    assert store.growth.coins == 0
    store.close()


def test_invalid_unowned_and_insufficient_coins(tmp_path):
    store = GameStore(tmp_path / 'game.db')
    assert '부족' in store.buy_theme('dark')
    assert '보유하지' in store.equip_theme('dark')
    assert '존재하지' in store.buy_theme('unknown')
    assert store.active_theme == 'white'
    assert store.growth.coins == 0
    store.close()
