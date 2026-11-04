"""Regression: desktop timer must actually display all source atlas frames.

A previous build incremented frame every 250 ms but only repainted each fourth
tick. Since source_rect cycles four columns, only frame zero ever appeared.
"""
import ast
from pathlib import Path

from pixel_buddy.character_animation import source_rect

ROOT = Path(__file__).resolve().parents[1]


def test_animation_timer_repaint_not_throttled_to_activity_detection():
    source = (ROOT / "src" / "pixel_buddy" / "main.py").read_text("utf-8")
    tree = ast.parse(source)
    desktop = next(node for node in tree.body
                   if isinstance(node, ast.ClassDef) and node.name == "DesktopBuddy")
    on_tick = next(node for node in desktop.body
                   if isinstance(node, ast.FunctionDef) and node.name == "on_tick")
    repaints = []
    for node in ast.walk(on_tick):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "update"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "scene"):
            repaints.append(node)
    assert len(repaints) == 1
    assert any(isinstance(node, ast.Expr) and node.value is repaints[0]
               for node in on_tick.body), "scene.update must run each tick, outside frame modulo guard"


def test_consecutive_ticks_select_different_character_frames():
    columns = [source_rect("typing", frame)[0] for frame in range(8)]
    assert len(set(columns[:4])) == 4
    assert columns[:4] == columns[4:8]
