from pathlib import Path
p=Path(__file__).resolve().parents[1]/'src/pixel_buddy/main.py'
s=p.read_text(encoding='utf8')
s=s.replace('        self.frame = 0\n        self.preview_equipped', '        self.frame = 0\n        self._sprites = {}\n        self.preview_equipped',1)
anchor='''        # Distinct silhouettes and ears, with a big chibi head.
'''
start=s.index(anchor)
end=s.index('''        # Equipment is shared across all animals.''',start)
replacement='''        # Animated 64x56 original pixel sprite sheets. Kept independent of
        # shirts and accessories, which remain wearable as separate layers.
        import os
        from pathlib import Path
        asset_root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2])) / 'assets' / 'sprites'
        mode = self.mode if self.mode in ('typing','mouse','watching','gaming','idle') else 'idle'
        sprite_key = f'{species}_{mode}'
        if sprite_key not in self._sprites:
            self._sprites[sprite_key] = QPixmap(str(asset_root / f'{sprite_key}.png'))
        sheet = self._sprites[sprite_key]
        if not sheet.isNull():
            frame_index = (self.frame // 4) % 4
            p.drawPixmap(QRectF(15, 6+y, 64, 56), sheet, QRectF(frame_index*64, 0, 64, 56))
        else:
            # Graceful fallback for source distributions missing artwork.
            rect(22,27+y,46,32,fur)
            rect(32,45+y,27,14,muzzle)
            rect(32,40+y,6,8,'#413A4D')
            rect(53,40+y,6,8,'#413A4D')
            rect(44,49+y,5,4,'#8B626E')
'''
s=s[:start]+replacement+s[end:]
s=s.replace('''        import os
        from pathlib import Path
''','''        from pathlib import Path
''')
p.write_text(s,encoding='utf8')
