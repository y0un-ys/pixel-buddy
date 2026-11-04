from pathlib import Path

def test_window_titles_use_repository_brand():
    source = (Path(__file__).parents[1] / "src" / "pixel_buddy" / "main.py").read_text(encoding="utf-8")
    assert "self.label = QLabel('🐾 pixel-buddy')" in source
    for label in ("상점", "인벤토리", "설정", "내 작은 동료"):
        assert f"self.setWindowTitle('pixel-buddy · {label}')" in source
