"""Generate original cozy chibi four-frame pixel sprite sheets.

Run: python tools/generate_sprites.py
Pillow is needed only to regenerate PNGs, not to run the application.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'sprites'
ROOT.mkdir(parents=True, exist_ok=True)
MODES = ('typing', 'mouse', 'watching', 'gaming', 'idle')
PALETTES = {
    'dog':    ('#EABF93', '#FFF1DA', '#C58D71', '#E9A8A4'),
    'cat':    ('#F2B16D', '#FFF0DA', '#D78D62', '#F7B3B6'),
    'bear':   ('#CAA17D', '#FFE8C8', '#A57660', '#E7AAA5'),
    'fox':    ('#EA995F', '#FFF2DD', '#C17652', '#EFAC9D'),
    'rabbit': ('#F1E2E8', '#FFF7FA', '#C9AFBE', '#F3AECA'),
}
OUTLINE = '#725866'
DARK = '#463C54'


def frame(species: str, mode: str, step: int) -> Image.Image:
    fur, cream, shade, pink = PALETTES[species]
    im = Image.new('RGBA', (64, 56))
    d = ImageDraw.Draw(im)
    dy = -1 if mode in ('typing', 'gaming') and step in (1, 3) else 0
    def r(x0, y0, x1, y1, color):
        d.rectangle((x0, y0+dy, x1, y1+dy), fill=color)
    def e(x0, y0, x1, y1, color):
        d.ellipse((x0, y0+dy, x1, y1+dy), fill=color)
    def poly(points, color):
        d.polygon([(x, y+dy) for x,y in points], fill=color)

    if species == 'cat':
        poly([(12,25),(13,10),(24,18),(29,25)],OUTLINE)
        poly([(35,25),(42,10),(53,25)],OUTLINE)
        poly([(15,23),(16,14),(25,23)],fur)
        poly([(39,23),(42,14),(50,23)],fur)
        poly([(18,22),(18,18),(23,23)],pink)
        poly([(41,23),(45,18),(46,22)],pink)
    elif species == 'fox':
        poly([(11,27),(17,8),(29,23)],OUTLINE)
        poly([(36,23),(48,8),(55,27)],OUTLINE)
        poly([(15,24),(19,13),(26,23)],fur)
        poly([(39,23),(47,13),(52,24)],fur)
        poly([(18,22),(20,18),(24,22)],cream)
        poly([(42,22),(46,18),(47,22)],cream)
    elif species == 'dog':
        e(6,19,22,39,OUTLINE)
        e(42,19,58,39,OUTLINE)
        e(9,22,20,36,shade)
        e(44,22,55,36,shade)
    elif species == 'bear':
        e(9,14,25,30,OUTLINE)
        e(39,14,55,30,OUTLINE)
        e(12,17,22,27,fur)
        e(42,17,52,27,fur)
        e(15,20,19,25,cream)
        e(45,20,49,25,cream)
    elif species == 'rabbit':
        e(14,5,25,31,OUTLINE)
        e(39,5,50,31,OUTLINE)
        e(16,7,23,29,fur)
        e(41,7,48,29,fur)
        e(19,11,21,24,pink)
        e(44,11,46,24,pink)

    e(8,21,56,53,OUTLINE)
    e(10,20,54,51,fur)
    r(13,26,51,48,fur)
    e(14,32,50,51,cream)
    if species == 'cat':
        r(22,22,26,23,shade); r(31,21,35,23,shade); r(41,22,44,23,shade)
    elif species == 'dog':
        e(14,27,23,36,shade)
    elif species == 'fox':
        poly([(12,32),(22,36),(21,45),(12,42)],cream)
        poly([(52,32),(42,36),(43,45),(52,42)],cream)
    elif species == 'rabbit':
        r(26,26,36,27,'#FFFFFF')

    e(13,38,23,43,pink)
    e(41,38,51,43,pink)
    r(15,39,17,39,'#FFE8E2')
    r(44,39,46,39,'#FFE8E2')
    closed = (mode == 'idle' and step in (1,2)) or (mode != 'gaming' and step == 3)
    gaze = 1 if mode == 'mouse' and step in (1,2) else 0
    if closed:
        r(23,34,28,35,DARK)
        r(38,34,43,35,DARK)
        r(22,33,23,34,DARK)
        r(43,33,44,34,DARK)
    else:
        e(22+gaze,31,29+gaze,40,DARK)
        e(37+gaze,31,44+gaze,40,DARK)
        r(24+gaze,32,26+gaze,34,'#FFFFFF')
        r(39+gaze,32,41+gaze,34,'#FFFFFF')
    r(31,40,34,42,shade)
    r(32,42,33,43,shade)
    if mode == 'gaming' and step == 2:
        e(30,44,36,49,DARK); r(32,47,34,48,pink)
    elif mode == 'idle':
        r(30,46,35,46,DARK)
    else:
        r(29,45,31,46,DARK);r(35,45,37,46,DARK)
        r(32,46,34,46,DARK)
    r(26,51,39,52,cream)
    return im


def generate():
    for species in PALETTES:
        for mode in MODES:
            sheet = Image.new('RGBA', (64*4, 56), (0,0,0,0))
            for step in range(4):
                # v0.4.2: one consistent base character per species.
                # Game-specific actions are animated in the QPainter layer.
                sheet.paste(frame(species, 'typing', step), (step*64, 0))
            sheet.save(ROOT / f'{species}_{mode}.png', optimize=True)
    print('Generated 25 cozy sprite sheets')


if __name__ == '__main__':
    generate()
