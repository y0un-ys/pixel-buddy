"""Render screenshots of the actual BuddyScene widget for design review.

Uses the exact renderer shared by the desktop pet, shop and inventory previews.
Run on a desktop, or use QT_QPA_PLATFORM=offscreen in GitHub Actions.
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication
from pixel_buddy.main import BuddyScene
from pixel_buddy.store import GameStore

ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")


def main():
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "preview_illustrated").resolve()
    destination.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
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
        store.close()
    print(f"Saved real BuddyScene previews to {destination}")


if __name__ == "__main__":
    main()
