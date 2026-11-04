from pixel_buddy.store import GameStore, ANIMALS


def test_animal_and_size_persist(tmp_path):
    path = tmp_path / 'save.sqlite3'
    store = GameStore(path)
    assert set(ANIMALS) == {'dog', 'cat', 'bear', 'fox', 'rabbit'}
    store.animal = 'fox'
    store.nickname = '초코'
    store.scale_percent = 60
    store.toolbar_visible = False
    store.growth.coins = 99
    store.close()
    restored = GameStore(path)
    assert (restored.animal, restored.nickname) == ('fox', '초코')
    assert (restored.scale_percent, restored.toolbar_visible) == (60, False)
    assert restored.growth.coins == 99
    restored.close()


def test_previous_save_prompts_animal_selection(tmp_path):
    path = tmp_path / 'old.sqlite3'
    store = GameStore(path)
    store.growth.coins = 42
    store.close()
    new = GameStore(path)
    assert new.animal is None
    assert new.growth.coins == 42
    new.close()
