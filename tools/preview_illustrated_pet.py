"""Render screenshots of the actual BuddyScene widget for design review.

Uses the exact renderer shared by the desktop pet, shop and inventory previews.
Run on a desktop, or use QT_QPA_PLATFORM=offscreen in GitHub Actions.
"""
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication
from pixel_buddy.main import BuddyScene, ShopDialog
from pixel_buddy.store import GameStore
from pixel_buddy.theme import get_theme, make_stylesheet

ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")


def main():
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "preview_illustrated").resolve()
    destination.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    with tempfile.TemporaryDirectory() as tmp:
        store = GameStore(Path(tmp) / "test.sqlite3")
        atlas = QPixmap(480 * len(ANIMALS), 288)
        atlas.fill(QColor("#FFFFFF"))
        with_atlas = QPainter(atlas)
        for index, animal in enumerate(ANIMALS):
            store.animal = animal
            scene = BuddyScene(store)
            scene.mode = "typing"
            scene.show()
            app.processEvents()
            screenshot = scene.grab()
            assert not screenshot.isNull()
            assert screenshot.save(str(destination / f"{animal}_typing.png"))
            with_atlas.drawPixmap(index * 480, 0, screenshot)
            scene.close()
        with_atlas.end()
        assert atlas.save(str(destination / "all_five.png"))
        # A computer-store preview must use the same art and change the monitor.
        store.animal = "cat"
        scene = BuddyScene(store)
        scene.mode = "typing"
        scene.preview_equipped = dict(store.equipped, **{"컴퓨터": "dual", "소품": "plant"})
        scene.show()
        app.processEvents()
        assert scene.grab().save(str(destination / "cat_shop_preview.png"))
        scene.close()

        # Capture the *actual* rendered state for each activity at two frames.
        # This catches regressions where all states appear asleep or identical.
        modes = ("typing", "mouse", "watching", "gaming", "idle", "sleep")
        atlas_modes = QPixmap(480 * len(modes), 288)
        atlas_modes.fill(QColor("#FFFFFF"))
        painter = QPainter(atlas_modes)
        for index, mode in enumerate(modes):
            scene = BuddyScene(store)
            scene.mode = mode
            scene.frame = 8
            scene.show()
            app.processEvents()
            image = scene.grab()
            assert image.save(str(destination / f"cat_{mode}.png"))
            painter.drawPixmap(index * 480, 0, image)
            scene.frame = 9
            scene.update()
            app.processEvents()
            assert scene.grab().save(str(destination / f"cat_{mode}_frame2.png"))
            from PIL import Image, ImageChops
            first_image = Image.open(destination / f"cat_{mode}.png").convert("RGBA")
            second_image = Image.open(destination / f"cat_{mode}_frame2.png").convert("RGBA")
            # RGBA getbbox() also tests the alpha channel; equal opacity
            # would incorrectly report zero even when visible RGB keys change.
            assert ImageChops.difference(first_image.convert("RGB"), second_image.convert("RGB")).getbbox(), mode
            scene.close()
        painter.end()
        assert atlas_modes.save(str(destination / "activity_states.png"))
        # Exercise the actual shared renderer, not just the atlas files:
        # 5 animals x 3 computers x 6 modes x 4 consecutive timer frames.
        for animal in ANIMALS:
            store.animal = animal
            for pc in ("laptop", "desktop", "dual"):
                sheet = QPixmap(480 * 4, 288 * len(modes))
                sheet.fill(QColor("#FFFFFF"))
                painter = QPainter(sheet)
                scene = BuddyScene(store)
                scene.preview_equipped = dict(store.equipped, **{"컴퓨터": pc})
                for row, mode in enumerate(modes):
                    scene.mode = mode
                    for frame in range(4):
                        scene.frame = frame
                        painter.drawPixmap(frame * 480, row * 288, scene.grab())
                painter.end()
                scene.close()
                assert sheet.save(str(destination / f"behavior_{animal}_{pc}.png"))
        # Shop cards (160), inventory (320), and minimum/default/maximum pet
        # sizes share BuddyScene. Check transparency on light and dark desktops.
        store.animal = "cat"
        for width in (160, 240, 320, 360, 600):
            height = round(width * 288 / 480)
            for background in ("#FFFFFF", "#282638"):
                sheet = QPixmap(width * 4, height * len(modes))
                sheet.fill(QColor(background))
                painter = QPainter(sheet)
                scene = BuddyScene(store)
                scene.setFixedSize(width, height)
                for row, mode in enumerate(modes):
                    scene.mode = mode
                    for frame in range(4):
                        scene.frame = frame
                        painter.drawPixmap(frame * width, row * height, scene.grab())
                painter.end()
                scene.close()
                assert sheet.save(str(destination / f"size_{width}_{background[1:]}.png"))
        store.growth.level = 20
        store.growth.coins = 10000
        owner = SimpleNamespace(store=store, remember_management_position=lambda pos: None)
        for theme in ("white", "dark"):
            app.setStyleSheet(make_stylesheet(get_theme(theme)))
            shop = ShopDialog(owner)
            shop.preview_timer.stop()
            for width, height in ((650, 640), (760, 735)):
                shop.resize(width, height)
                shop.show()
                app.processEvents()
                for category, item in enumerate(("suit", "ribbon", "desktop", "pink_desk", "plant")):
                    shop.categories.setCurrentIndex(category)
                    shop.select_item(item)
                    app.processEvents()
                    shop.advance_previews()
                    app.processEvents()
                    assert shop.grab().save(str(destination / f"shop_{theme}_{width}_{category}.png"))
            shop.close()
        store.close()
    print(f"Saved real BuddyScene previews to {destination}")


if __name__ == "__main__":
    main()
