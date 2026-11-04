"""SQLite save game and catalog. No input text or visited URLs are stored."""
import json
import sqlite3
from pathlib import Path
from .progression import Growth
from .theme import THEMES, THEME_PRICES

CATALOG = [
    ('hoodie', '포근한 후드티', '의상', 0, 1),
    ('pajamas', '별빛 잠옷', '의상', 120, 2),
    ('suit', '꼬마 정장', '의상', 260, 5),
    ('cat_ears', '고양이 귀', '머리띠', 100, 2),
    ('ribbon', '딸기 리본', '머리띠', 150, 3),
    ('bunny_ears', '토끼 귀', '머리띠', 300, 7),
    ('laptop', '작은 노트북', '컴퓨터', 0, 1),
    ('desktop', '데스크톱 PC', '컴퓨터', 300, 4),
    ('dual', '듀얼 모니터', '컴퓨터', 650, 10),
    ('oak_desk', '원목 책상', '책상', 350, 3),
    ('pink_desk', '벚꽃 책상', '책상', 550, 7),
    ('gaming_desk', '게이밍 책상', '책상', 900, 12),
    ('plant', '작은 화분', '소품', 100, 2),
    ('lamp', '따뜻한 스탠드', '소품', 200, 4),
    ('plushie', '곰인형', '소품', 280, 6),
]
ITEMS = {item[0]: {'name': item[1], 'category': item[2], 'price': item[3], 'level': item[4]} for item in CATALOG}
ANIMALS = {'dog': '강아지', 'cat': '고양이', 'bear': '곰', 'fox': '여우', 'rabbit': '토끼'}
DEFAULT_EQUIP = {'의상': 'hoodie', '머리띠': '', '컴퓨터': 'laptop', '책상': '', '소품': ''}


def preview_equipment(current: dict, item_id: str) -> dict:
    """Build an item preview without changing equipped items or save data."""
    if item_id not in ITEMS:
        raise ValueError(f'Unknown item: {item_id}')
    result = dict(current)
    result[ITEMS[item_id]['category']] = item_id
    return result


class GameStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS save (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)')
        self.conn.commit()
        row = self.conn.execute('SELECT data FROM save WHERE id=1').fetchone()
        data = json.loads(row[0]) if row else {}
        g = data.get('growth', {})
        self.growth = Growth(level=max(1, int(g.get('level', 1))), xp=max(0, int(g.get('xp', 0))),
                             coins=max(0, int(g.get('coins', 0))), total_seconds=max(0, int(g.get('total_seconds', 0))))
        self.owned_themes = set(x for x in data.get('owned_themes', []) if x in THEMES) | {'white'}
        self.active_theme = data.get('active_theme', 'white')
        if self.active_theme not in self.owned_themes:
            self.active_theme = 'white'
        self.activity_seconds = {k: max(0, int(v)) for k,v in data.get('activity_seconds', {}).items() if k in ('typing','mouse','watching','gaming','idle')}
        self.achievements = set(data.get('achievements', []))
        self.presets = {k:v for k,v in data.get('presets', {}).items() if k in ('작업용','게임용','야간용') and isinstance(v, dict)}
        self.room_enabled = bool(data.get('room_enabled', False))
        self.animal = data.get('animal') if data.get('animal') in ANIMALS else None
        self.nickname = str(data.get('nickname', ''))[:16]
        self.scale_percent = max(50, min(125, int(data.get('scale_percent', 75))))
        self.toolbar_visible = bool(data.get('toolbar_visible', True))
        owned = data.get('owned', [])
        self.owned = set(x for x in owned if x in ITEMS) | {'hoodie', 'laptop'}
        equipped = data.get('equipped', {})
        self.equipped = DEFAULT_EQUIP.copy()
        for category in self.equipped:
            item = equipped.get(category)
            if item == '' and category == '머리띠':
                self.equipped[category] = ''
            elif item == '' and category in ('책상', '소품'):
                self.equipped[category] = ''
            elif item in self.owned and ITEMS[item]['category'] == category:
                self.equipped[category] = item

    def change_animal(self, animal: str, nickname: str = None):
        if animal not in ANIMALS:
            return False
        self.animal = animal
        if nickname is not None:
            self.nickname = nickname.strip()[:16] or ANIMALS[animal]
        self.save()
        return True

    def save_preset(self, name):
        if name not in ('작업용','게임용','야간용'):
            return False
        self.presets[name] = dict(self.equipped)
        self.save()
        return True

    def load_preset(self, name):
        if name not in self.presets:
            return False
        for category, item in self.presets[name].items():
            if category in DEFAULT_EQUIP and (item == '' or (item in self.owned and ITEMS[item]['category'] == category)):
                self.equipped[category] = item
        self.save()
        return True

    def award_achievements(self):
        # One-time rewards. Historical saves receive credit without resetting progression.
        checks = {'첫 1시간': (self.growth.total_seconds >= 3600, 40),
                  '함께 10시간': (self.growth.total_seconds >= 36000, 120),
                  '첫 쇼핑': (len(self.owned) > 2, 40),
                  '게임 5시간': (self.activity_seconds.get('gaming',0) >= 18000, 100),
                  '레벨 10': (self.growth.level >= 10, 100)}
        gained = []
        for name, (passed, reward) in checks.items():
            if passed and name not in self.achievements:
                self.achievements.add(name)
                self.growth.coins += reward
                gained.append((name, reward))
        if gained: self.save()
        return gained

    def buy_theme(self, theme_id: str) -> str:
        if theme_id not in THEMES:
            return '존재하지 않는 테마예요.'
        if theme_id in self.owned_themes:
            return '이미 보유한 테마예요.'
        price = THEME_PRICES[theme_id]
        if self.growth.coins < price:
            return '코인이 부족해요.'
        self.growth.coins -= price
        self.owned_themes.add(theme_id)
        self.active_theme = theme_id
        self.save()
        return '테마 구매 및 적용 완료!'

    def equip_theme(self, theme_id: str) -> str:
        if theme_id not in self.owned_themes:
            return '보유하지 않은 테마예요.'
        self.active_theme = theme_id
        self.save()
        return '테마를 적용했어요!'

    def purchase(self, item: str) -> str:
        if item not in ITEMS:
            return '존재하지 않는 아이템이에요.'
        if item in self.owned:
            return '이미 보유한 아이템이에요.'
        info = ITEMS[item]
        if self.growth.level < info['level']:
            return f"Lv.{info['level']}부터 구매할 수 있어요."
        if self.growth.coins < info['price']:
            return '코인이 부족해요.'
        self.growth.coins -= info['price']
        self.owned.add(item)
        self.equipped[info['category']] = item
        self.save()
        return f"{info['name']} 구매 및 장착 완료!"

    def equip(self, item: str) -> str:
        if item == 'none':
            self.equipped['머리띠'] = ''
        elif item in self.owned:
            self.equipped[ITEMS[item]['category']] = item
        else:
            return '보유하지 않은 아이템이에요.'
        self.save()
        return '장착했어요!'

    def save(self):
        data = {'growth': {'level': self.growth.level, 'xp': self.growth.xp,
                           'coins': self.growth.coins, 'total_seconds': self.growth.total_seconds},
                'owned': sorted(self.owned), 'equipped': self.equipped,
                'owned_themes': sorted(self.owned_themes), 'active_theme': self.active_theme,
                'animal': self.animal, 'nickname': self.nickname,
                'scale_percent': self.scale_percent, 'toolbar_visible': self.toolbar_visible,
                'activity_seconds': self.activity_seconds, 'achievements': sorted(self.achievements),
                'presets': self.presets, 'room_enabled': self.room_enabled}
        with self.conn:
            self.conn.execute('INSERT INTO save (id, data) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET data=excluded.data',
                              (json.dumps(data, ensure_ascii=False),))

    def close(self):
        self.save()
        self.conn.close()
