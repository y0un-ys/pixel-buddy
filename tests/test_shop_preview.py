from pixel_buddy.store import GameStore, preview_equipment


def test_preview_does_not_buy_or_equip(tmp_path):
    store = GameStore(tmp_path / "game.db")
    before = dict(store.equipped)
    coins = store.growth.coins
    owned = set(store.owned)
    look = preview_equipment(store.equipped, "suit")
    assert look["의상"] == "suit"
    assert store.equipped == before
    assert store.growth.coins == coins
    assert store.owned == owned
    store.close()

def test_purchase_requires_action(tmp_path):
    store = GameStore(tmp_path / "game.db")
    store.growth.level = 10
    store.growth.coins = 500
    preview_equipment(store.equipped, "suit")
    assert "suit" not in store.owned
    assert store.growth.coins == 500
    assert "완료" in store.purchase("suit")
    assert store.growth.coins == 240
    assert store.equipped["의상"] == "suit"
    store.close()
