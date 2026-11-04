from pixel_buddy.store import GameStore, ANIMALS, ITEMS
from pathlib import Path


def test_animal_change_preserves_progress(tmp_path):
    db = tmp_path / 'game.db'
    store = GameStore(db)
    store.growth.level = 12
    store.growth.coins = 1550
    assert store.change_animal('fox', '여우별')
    assert store.growth.coins == 1550
    assert store.growth.level == 12
    store.close()
    again = GameStore(db)
    assert again.animal == 'fox'
    assert again.nickname == '여우별'
    assert again.growth.coins == 1550
    again.close()


def test_new_equipment_and_presets(tmp_path):
    store = GameStore(tmp_path / 'game.db')
    assert all(name in ITEMS for name in ('oak_desk','pink_desk','gaming_desk','plant','lamp','plushie'))
    store.growth.level = 20
    store.growth.coins = 5000
    assert '완료' in store.purchase('oak_desk')
    assert '완료' in store.purchase('plant')
    assert store.save_preset('작업용')
    store.purchase('gaming_desk')
    store.purchase('lamp')
    assert store.load_preset('작업용')
    assert store.equipped['책상'] == 'oak_desk'
    assert store.equipped['소품'] == 'plant'
    store.close()


def test_one_time_achievements(tmp_path):
    path = tmp_path / 'game.db'
    store = GameStore(path)
    store.growth.total_seconds = 36000
    store.activity_seconds['gaming'] = 18000
    store.growth.level = 10
    gained = store.award_achievements()
    assert any(name == '게임 5시간' for name, _ in gained)
    assert store.award_achievements() == []
    expected = store.growth.coins
    store.close()
    reloaded = GameStore(path)
    assert reloaded.award_achievements() == []
    assert reloaded.growth.coins == expected
    reloaded.close()


def test_preset_does_not_equip_unowned(tmp_path):
    store = GameStore(tmp_path / 'game.db')
    store.presets['작업용'] = {'의상': 'suit', '컴퓨터': 'dual'}
    assert store.load_preset('작업용')
    assert store.equipped['의상'] == 'hoodie'
    assert store.equipped['컴퓨터'] == 'laptop'
    store.close()
