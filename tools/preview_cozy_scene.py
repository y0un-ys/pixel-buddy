"""Export real runtime SVG scenes to PNG for visual QA.

Optional dependency: pip install cairosvg
Usage: python tools/preview_cozy_scene.py [output_directory]
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pixel_buddy.cozy_scene import scene_svg, ANIMALS


def main():
    try:
        import cairosvg
    except ImportError:
        raise SystemExit("Install preview dependency: python -m pip install cairosvg")
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "preview_cozy").resolve()
    out.mkdir(parents=True, exist_ok=True)
    specs = [(animal, "typing", "laptop", "plant") for animal in ANIMALS]
    specs += [("cat", "mouse", "desktop", "lamp"),
              ("cat", "watching", "dual", "plushie"),
              ("cat", "gaming", "laptop", "plant")]
    for species, mode, pc, prop in specs:
        name = f"{species}_{mode}_{pc}"
        svg = scene_svg(species, mode, pc, prop, frame=1)
        (out / (name + ".svg")).write_text(svg, encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                        write_to=str(out / (name + ".png")),
                        output_width=960, output_height=576)
        print(out / (name + ".png"))


if __name__ == "__main__":
    main()
