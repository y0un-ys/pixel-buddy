from pixel_buddy.store import GameStore, preview_equipment
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication, QScrollArea
from pixel_buddy.main import BuddyScene, ShopDialog


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


@pytest.fixture(scope="module")
def qt_app():
    return QApplication.instance() or QApplication([])


def test_shop_preview_and_visible_item_cards_advance(qt_app, tmp_path):
    store = GameStore(tmp_path / "shop.sqlite3")
    store.animal = "cat"
    shop = ShopDialog(SimpleNamespace(store=store, remember_management_position=lambda _: None))
    shop.show()
    shop.resize(650, 640)
    shop.preview_timer.stop()
    shop.categories.setCurrentIndex(2)
    qt_app.processEvents()
    category = shop.categories.widget(2)
    assert category is not None
    scroll = category.findChild(QScrollArea)
    assert scroll is not None
    assert scroll.horizontalScrollBar().maximum() == 0
    before = dict(store.equipped)
    coins = store.growth.coins
    shop.select_item("desktop")
    initial = shop.preview.grab().toImage()
    shop.advance_previews()
    qt_app.processEvents()
    assert shop.preview.frame == 1
    assert shop.tiles["desktop"].canvas.frame == 1
    assert shop.preview.grab().toImage() != initial
    icon_before = shop.tiles["desktop"].icon().cacheKey()
    store.animal = "dog"
    shop.advance_previews()
    assert shop.tiles["desktop"].icon().cacheKey() != icon_before
    assert store.equipped == before
    assert store.growth.coins == coins
    shop.close()
    store.close()


@pytest.mark.parametrize("item_id", ("pajamas", "suit", "streetwear", "cat_ears",
                                    "ribbon", "bunny_ears", "gaming_headset",
                                    "stream_microphone", "ring_light"))
def test_shop_previews_do_not_charge_until_purchase(qt_app, tmp_path, item_id):
    from pixel_buddy.store import ITEMS
    store = GameStore(tmp_path / "shop.sqlite3")
    store.animal = "cat"
    store.growth.level = 30
    store.growth.coins = 10000
    shop = ShopDialog(SimpleNamespace(
        store=store, scene=BuddyScene(store),
        remember_management_position=lambda _: None,
    ))
    shop.select_item(item_id)
    qt_app.processEvents()
    assert shop.buy_button.isEnabled(), item_id
    assert shop.preview.preview_equipped[ITEMS[item_id]["category"]] == item_id
    assert store.growth.coins == 10000
    assert item_id not in store.owned
    assert not shop.preview.grab().isNull()
    shop.close()
    store.close()


def test_purchasing_asset_backed_outfit_persists(qt_app, tmp_path):
    db = tmp_path / "shop.sqlite3"
    store = GameStore(db)
    store.growth.level = 30
    store.growth.coins = 10000
    assert "완료" in store.purchase("streetwear")
    assert store.equipped["의상"] == "streetwear"
    store.close()
    store = GameStore(db)
    assert "streetwear" in store.owned
    assert store.equipped["의상"] == "streetwear"
    store.close()


def test_each_desk_has_a_distinct_actual_render(qt_app, tmp_path):
    store = GameStore(tmp_path / "shop.sqlite3")
    store.animal = "cat"
    scene = BuddyScene(store)
    colors = []
    for item_id in ("oak_desk", "pink_desk", "gaming_desk"):
        scene.preview_equipped = preview_equipment(store.equipped, item_id)
        colors.append(scene.grab().toImage().pixelColor(400, 234).name())
    scene.close()
    store.close()
    assert len(set(colors)) == 3, colors
    # Gaming equipment needs a visibly dark surface, not another light wood tint.
    assert int(colors[2][1:3], 16) < 100


@pytest.mark.parametrize("animal", ("cat", "dog", "bear", "fox", "rabbit"))
def test_pajamas_preview_purchase_and_hoodie_switch(qt_app, tmp_path, monkeypatch, animal):
    store = GameStore(tmp_path / "shop.sqlite3")
    store.animal = animal
    store.growth.level = 2
    store.growth.coins = 500
    scene = BuddyScene(store)
    scene.setFixedSize(320, 192)
    scene.mode = "typing"
    hoodie = scene.grab().toImage()
    shop = ShopDialog(SimpleNamespace(
        store=store, scene=scene, remember_management_position=lambda _: None))
    monkeypatch.setattr("pixel_buddy.main.QMessageBox.information", lambda *_: None)
    shop.preview_timer.stop()
    shop.select_item("pajamas")
    assert shop.buy_button.isEnabled()
    preview = shop.preview.grab().toImage()
    assert preview != hoodie
    assert store.equipped["의상"] == "hoodie"
    assert store.growth.coins == 500
    shop.buy_selected()
    assert store.equipped["의상"] == "pajamas"
    assert store.growth.coins == 380
    assert scene.grab().toImage() == preview
    scene.frame = 1
    assert scene.grab().toImage() != preview
    store.equip("hoodie")
    scene.frame = 0
    assert scene.grab().toImage() == hoodie
    store.equip("pajamas")
    shop.close()
    scene.close()
    store.close()
    restored = GameStore(tmp_path / "shop.sqlite3")
    assert restored.equipped["의상"] == "pajamas"
    assert "pajamas" in restored.owned
    restored.close()
