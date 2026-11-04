from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'sprites'

def test_sprites_all_animals_modes():
    animals = ('dog','cat','bear','fox','rabbit')
    modes = ('typing','mouse','watching','gaming','idle')
    for animal in animals:
        for mode in modes:
            path = ROOT / f'{animal}_{mode}.png'
            assert path.exists(), str(path)
            png = path.read_bytes()
            assert png[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II', png[16:24]) == (256,56)
            assert len(png) > 100

def test_sprite_bundle_count():
    assert len(list(ROOT.glob('*.png'))) == 25
