"""Pixel Buddy: a tiny transparent desktop companion for Windows and macOS."""
import sys
import time
import random
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint, QRectF, QSize, QSettings
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTabWidget, QGridLayout, QScrollArea,
    QSystemTrayIcon, QMenu, QComboBox, QCheckBox, QMessageBox, QFrame, QLineEdit, QStackedWidget, QSlider)

from .progression import xp_required
from .store import GameStore, CATALOG, ITEMS, ANIMALS, preview_equipment
from .activity import ActivityDetector
from .animation import animation_frame, pose_for

# All management screens use a shared light palette. This is the first
# step toward selectable purchasable themes; do not hard-code widget colors.
from .theme import DEFAULT_THEME, make_stylesheet, THEMES, THEME_PRICES, get_theme

STYLE = make_stylesheet(DEFAULT_THEME)

MODES = {'auto': '자동 감지', 'typing': '⌨ 타이핑', 'watching': '🍿 영상 보기',
         'gaming': '🎮 게임', 'mouse': '🖱 마우스', 'idle': '💤 쉬기'}


class BuddyScene(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.mode = 'typing'
        self.frame = 0
        self._sprites = {}
        self._illustrations = {}
        self.preview_equipped = None  # Temporary look, never persisted
        self.reaction_event = ''
        self.room_view = False
        self.setFixedSize(480, 288)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, _event):
        """Render one coherent seated pet with desk equipment in front.

        Shop previews and the main desktop companion use this same widget.
        The character sheet includes its own chair/paws, so legacy SVG
        character layers must never be drawn at the same time.
        """
        from PySide6.QtCore import QByteArray
        from PySide6.QtSvg import QSvgRenderer
        from .cozy_scene import scene_svg, scene_illustration_layers

        equipment = self.preview_equipped if self.preview_equipped is not None else self.store.equipped
        kwargs = dict(
            species=self.store.animal or 'cat',
            mode=self.mode,
            pc=equipment.get('컴퓨터', 'laptop'),
            prop=equipment.get('소품', ''),
            desk=equipment.get('책상', ''),
            outfit=equipment.get('의상', 'hoodie'),
            hat=equipment.get('머리띠', ''),
            frame=animation_frame(self.frame),
            room=self.room_view,
            reaction=self.reaction_event,
        )
        species = kwargs['species']
        asset_root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))
        if species not in self._illustrations:
            self._illustrations[species] = QPixmap(
                str(asset_root / 'assets' / 'illustrations' / f'{species}.png'))
        illustration = self._illustrations[species]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if illustration.isNull():
            # Safe for older source checkouts that do not have the new PNGs.
            scene = scene_svg(**kwargs)
            QSvgRenderer(QByteArray(scene.encode('utf-8'))).render(
                p, QRectF(0, 0, self.width(), self.height()))
        else:
            background, foreground = scene_illustration_layers(**kwargs)
            p.scale(self.width() / 480.0, self.height() / 288.0)
            QSvgRenderer(QByteArray(background.encode('utf-8'))).render(
                p, QRectF(0, 0, 480, 288))

            # Keep the seated portrait proportions consistent for all animals.
            height = 168
            width = height * illustration.width() / illustration.height()
            center_x = 202
            bob = (0, 1, 0, -1)[animation_frame(self.frame)]
            p.drawPixmap(
                QRectF(center_x - width / 2, 89 + bob, width, height),
                illustration,
                QRectF(0, 0, illustration.width(), illustration.height()),
            )
            QSvgRenderer(QByteArray(foreground.encode('utf-8'))).render(
                p, QRectF(0, 0, 480, 288))
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().drag_pos = event.globalPosition().toPoint() - self.window().pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.window().open_dialog()

    def mouseMoveEvent(self, event):
        window = self.window()
        if window.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window.move(event.globalPosition().toPoint() - window.drag_pos)

    def mouseReleaseEvent(self, event):
        self.window().drag_pos = None

    def mouseDoubleClickEvent(self, event):
        self.window().open_dialog()


class PetToolbar(QFrame):
    def __init__(self, window):
        super().__init__(window)
        self.owner = window
        self.setFixedHeight(34)
        self.setObjectName('petToolbar')
        self.setStyleSheet('QFrame#petToolbar { background: #F3F4F6; border-radius: 8px; } '
                           'QFrame#petToolbar QLabel { color: #222222; } '
                           'QFrame#petToolbar QPushButton { padding: 2px 6px; border-radius: 5px; }')
        row = QHBoxLayout(self)
        row.setContentsMargins(7,3,5,3)
        row.setSpacing(4)
        self.label = QLabel('🐾 pixel-buddy')
        row.addWidget(self.label,1)
        for label, cb, tip in [('-', lambda:window.change_scale(-10), '작게'),
                               ('+', lambda:window.change_scale(10), '크게'),
                               ('⚙', window.open_dialog, '상점과 설정'),
                               ('▁', window.hide_toolbar, '도구바 숨기기'),
                               ('×', window.hide, '트레이로 숨기기')]:
            b = QPushButton(label)
            b.setFixedSize(28,25)
            b.setToolTip(tip)
            b.clicked.connect(cb)
            row.addWidget(b)

    def mousePressEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner.drag_pos = event.globalPosition().toPoint() - self.owner.pos()

    def mouseMoveEvent(self,event):
        if self.owner.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.owner.move(event.globalPosition().toPoint() - self.owner.drag_pos)

    def mouseReleaseEvent(self,event):
        self.owner.drag_pos = None


class AnimalPicker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('pixel-buddy · 함께할 동료 선택')
        self.setMinimumWidth(420)
        self.selected = 'dog'
        root = QVBoxLayout(self)
        title = QLabel('🐾 함께할 동물 친구를 골라주세요')
        title.setStyleSheet('font-size: 18px; font-weight: bold;')
        root.addWidget(title)
        root.addWidget(QLabel('동물별 능력치 차이는 없고, 외형과 개성이 달라요.'))
        row = QGridLayout()
        self.buttons = {}
        for i,(key,label) in enumerate(ANIMALS.items()):
            button = QPushButton(('● ' if key == self.selected else '') + label)
            button.clicked.connect(lambda _,k=key:self.choose(k))
            row.addWidget(button,i//3,i%3)
            self.buttons[key] = button
        root.addLayout(row)
        root.addWidget(QLabel('친구의 이름 (최대 16글자)'))
        self.nickname = QLineEdit()
        # Explicit palette: the global light text color on a native white edit
        # made Korean text invisible on some Windows themes.
        self.nickname.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #222222;
                selection-background-color: #8064A8;
                selection-color: #FFFFFF;
                border: 2px solid #B8A9D2;
                border-radius: 6px;
                padding: 7px 9px;
                font-family: 'Malgun Gothic', 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #9273D0; }
        """)
        self.nickname.setMaxLength(16)
        self.nickname.setText('작은 동료')
        root.addWidget(self.nickname)
        start = QPushButton('함께 생활 시작하기')
        start.clicked.connect(self.accept)
        root.addWidget(start)

    def choose(self,key):
        self.selected = key
        for animal,button in self.buttons.items():
            button.setText(('● ' if animal == key else '') + ANIMALS[animal])


class PixelItemTile(QPushButton):
    """A catalogue card with a pixel-art render of the actual equipment."""
    def __init__(self, store, item_id, on_select, parent=None):
        info = ITEMS[item_id]
        super().__init__(parent)
        self.item_id = item_id
        self.setCheckable(True)
        self.setMinimumHeight(139)
        # The global theme styles these stateful item cards consistently.
        self.setObjectName('pixelItemTile')
        self.clicked.connect(lambda _=False: on_select(item_id))
        # Render the same pixel objects as the main buddy scene so item cards
        # always reflect their real in-game appearance.
        canvas = BuddyScene(store)
        canvas.setFixedSize(160, 96)
        look = preview_equipment(store.equipped, item_id)
        canvas.preview_equipped = look
        canvas.mode = 'typing'  # Computer previews must never show a game controller.
        image = QPixmap(160, 96)
        image.fill(Qt.GlobalColor.transparent)
        canvas.render(image)
        from PySide6.QtGui import QIcon as _Icon
        self.setIcon(_Icon(image))
        self.setIconSize(QSize(158, 92))
        self.setToolTip(f"{info['name']}\n{info['price']} 코인 · Lv.{info['level']}부터 구매")


class BuddyDialog(QDialog):
    """Independent top-level management window, kept above the always-on-top pet."""
    page_key = 'home'

    def __init__(self, owner):
        # IMPORTANT: do not make this a child window of the always-on-top pet.
        # Parent ownership would allow the pet's z-order to obscure the dialog.
        super().__init__(None)
        self.owner = owner
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def install_navigation(self, root):
        nav = QHBoxLayout()
        nav.setSpacing(5)
        for title, key in [('← 뒤로', 'back'), ('⌂ 내 동료', 'home'),
                           ('상점', 'shop'), ('인벤토리', 'inventory'), ('설정', 'settings')]:
            button = QPushButton(title)
            button.setObjectName('nav_' + key)
            button.setMinimumHeight(31)
            button.setStyleSheet('QPushButton { padding:5px 8px; }')
            if key == self.page_key:
                button.setEnabled(False)
            button.clicked.connect(lambda _=False, target=key: self.owner.navigate_back() if target == 'back' else self.owner.open_page(target))
            nav.addWidget(button)
        root.insertLayout(0, nav)

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.isVisible() and hasattr(self.owner, 'remember_management_position'):
            self.owner.remember_management_position(self.pos())

    def closeEvent(self, event):
        self.owner.remember_management_position(self.pos())
        super().closeEvent(event)


class ShopDialog(BuddyDialog):
    page_key = 'shop'
    """Separate store window. Selection is a non-persistent, free preview."""
    def __init__(self, app_window):
        super().__init__(app_window)
        self.owner = app_window
        self.store = app_window.store
        self.setWindowTitle('pixel-buddy · 상점')
        self.resize(760, 735)
        self.setMinimumSize(650, 640)
        self.selected_item = None
        self.tiles = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        header = QHBoxLayout()
        title = QLabel('🛍 꾸미기 상점')
        title.setStyleSheet('font-size:21px;font-weight:bold')
        self.coins = QLabel()
        header.addWidget(title, 1)
        header.addWidget(self.coins)
        root.addLayout(header)
        root.addWidget(QLabel('아이템을 선택하면 먼저 미리보기만 적용돼요. 구매 전에는 코인이 차감되지 않아요.'))
        self.categories = QTabWidget()
        root.addWidget(self.categories, 1)
        for category in ('의상', '머리띠', '컴퓨터', '책상', '소품'):
            tab = QWidget()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            content = QWidget()
            grid = QGridLayout(content)
            grid.setSpacing(10)
            for idx, (item_id, name, cat, price, lvl) in enumerate(x for x in CATALOG if x[2] == category):
                cell = QFrame()
                cell.setObjectName('panel')
                # panel gets its colors from the shared theme stylesheet
                column = QVBoxLayout(cell)
                tile = PixelItemTile(self.store, item_id, self.select_item)
                self.tiles[item_id] = tile
                column.addWidget(tile)
                n = QLabel(name)
                n.setAlignment(Qt.AlignmentFlag.AlignCenter)
                column.addWidget(n)
                price_label = QLabel(f'{price:,} 코인 · Lv.{lvl}')
                price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                price_label.setObjectName('secondaryText')
                column.addWidget(price_label)
                grid.addWidget(cell, idx // 3, idx % 3)
            grid.setRowStretch((sum(1 for x in CATALOG if x[2] == category) + 2) // 3, 1)
            scroll.setWidget(content)
            lay = QVBoxLayout(tab)
            lay.setContentsMargins(0, 8, 0, 0)
            lay.addWidget(scroll)
            self.categories.addTab(tab, category)
        # A separate themed store tab: selection previews visually, but does not mutate save.
        theme_tab = QWidget()
        theme_tab_layout = QVBoxLayout(theme_tab)
        theme_tab_layout.addWidget(QLabel('테마를 고르면 아래에서 미리볼 수 있어요. 구매 버튼을 누르기 전에는 코인이 차감되지 않아요.'))
        theme_grid = QGridLayout()
        self.theme_buttons = {}
        for idx, (theme_id, palette) in enumerate(THEMES.items()):
            card = QPushButton(palette.name + f'\n{THEME_PRICES[theme_id]:,} 코인')
            card.setObjectName('themeCard')
            card.setCheckable(True)
            card.setMinimumHeight(72)
            card.setToolTip(f'{palette.name} · {THEME_PRICES[theme_id]:,} 코인')
            card.clicked.connect(lambda _checked=False, key=theme_id: self.select_theme(key))
            self.theme_buttons[theme_id] = card
            theme_grid.addWidget(card, idx // 3, idx % 3)
        theme_tab_layout.addLayout(theme_grid)
        self.theme_preview = QFrame()
        theme_preview_layout = QVBoxLayout(self.theme_preview)
        self.theme_sample_title = QLabel('pixel-buddy  ·  테마 미리보기')
        self.theme_sample_label = QLabel('내 동료       Lv. 1       100 / 200 XP')
        self.theme_sample_button = QLabel('상점 · 인벤토리 · 설정')
        theme_preview_layout.addWidget(self.theme_sample_title)
        theme_preview_layout.addWidget(self.theme_sample_label)
        theme_preview_layout.addWidget(self.theme_sample_button)
        theme_tab_layout.addWidget(self.theme_preview)
        self.theme_details = QLabel('원하는 테마를 골라주세요.')
        theme_tab_layout.addWidget(self.theme_details)
        self.theme_buy_button = QPushButton('테마 선택')
        self.theme_buy_button.setEnabled(False)
        self.theme_buy_button.clicked.connect(self.buy_selected_theme)
        theme_tab_layout.addWidget(self.theme_buy_button)
        theme_tab_layout.addStretch()
        self.categories.addTab(theme_tab, '테마')
        self.selected_theme = None
        self.select_theme(self.store.active_theme)
        preview_area = QHBoxLayout()
        self.preview = BuddyScene(self.store)
        self.preview.setFixedSize(320, 192)
        self.preview.mode = 'typing'
        preview_area.addWidget(self.preview)
        details_col = QVBoxLayout()
        self.description = QLabel('위에서 아이템을 선택해 주세요.')
        self.description.setWordWrap(True)
        details_col.addWidget(self.description)
        self.buy_button = QPushButton('미리볼 아이템 선택')
        self.buy_button.setEnabled(False)
        self.buy_button.clicked.connect(self.buy_selected)
        details_col.addWidget(self.buy_button)
        self.reset_button = QPushButton('미리보기 초기화')
        self.reset_button.clicked.connect(self.reset_preview)
        details_col.addWidget(self.reset_button)
        details_col.addStretch()
        preview_area.addLayout(details_col, 1)
        root.addLayout(preview_area)
        self.categories.currentChanged.connect(self._tab_changed)
        self.install_navigation(root)
        self.refresh()

    def _tab_changed(self, _index):
        # No stale selection from a different item category.
        self.reset_preview()

    def select_theme(self, theme_id):
        if theme_id not in THEMES:
            return
        self.selected_theme = theme_id
        t = get_theme(theme_id)
        for key, button in self.theme_buttons.items():
            button.setChecked(key == theme_id)
            b = get_theme(key)
            button.setStyleSheet(f'QPushButton {{ background: {b.surface}; color: {b.foreground}; border: 3px solid {t.accent if key == theme_id else b.border}; border-radius: 8px; padding: 8px; }}')
        self.theme_preview.setStyleSheet(f'QFrame {{background:{t.background}; border: 1px solid {t.border};border-radius:8px;}} QLabel {{color:{t.foreground};background:transparent;}}')
        self.theme_sample_button.setStyleSheet(f'background:{t.accent};color:{t.button_text};padding:8px;border-radius:6px;')
        self.refresh_theme()

    def refresh_theme(self):
        key = self.selected_theme
        if not key:
            return
        t = get_theme(key)
        price = THEME_PRICES[key]
        owned = key in self.store.owned_themes
        active = key == self.store.active_theme
        self.theme_details.setText(f'{t.name} · {price:,} 코인' + (' · 보유 중' if owned else ''))
        if active:
            label, enabled = '현재 적용 중', False
        elif owned:
            label, enabled = '테마 적용', True
        elif self.store.growth.coins < price:
            label, enabled = '코인 부족', False
        else:
            label, enabled = f'구매하기 · {price:,} 코인', True
        self.theme_buy_button.setText(label)
        self.theme_buy_button.setEnabled(enabled)
        for theme_id, card in self.theme_buttons.items():
            note = ' · 적용 중' if theme_id == self.store.active_theme else (' · 보유' if theme_id in self.store.owned_themes else '')
            card.setText(f'{THEMES[theme_id].name}\n{THEME_PRICES[theme_id]:,} 코인{note}')

    def buy_selected_theme(self):
        key = self.selected_theme
        if not key:
            return
        if key in self.store.owned_themes:
            result = self.store.equip_theme(key)
        else:
            result = self.store.buy_theme(key)
        self.owner.apply_theme()
        self.refresh()
        QMessageBox.information(self, '테마 상점', result)

    def select_item(self, item_id):
        self.selected_item = item_id
        for key, tile in self.tiles.items():
            tile.setChecked(key == item_id)
        info = ITEMS[item_id]
        equipment = preview_equipment(self.store.equipped, item_id)
        self.preview.preview_equipped = equipment
        self.preview.mode = 'typing'  # Work mode for all shop previews.
        self.preview.update()
        self.refresh()

    def reset_preview(self):
        self.selected_item = None
        self.preview.preview_equipped = None
        self.preview.update()
        for tile in self.tiles.values():
            tile.setChecked(False)
        self.refresh()

    def refresh(self):
        self.coins.setText(f'🪙 {self.store.growth.coins:,} 코인')
        self.refresh_theme()
        item_id = self.selected_item
        if not item_id:
            self.description.setText('카드를 클릭하면 동물 친구에게 미리 적용돼요.\n(구매 또는 장착은 아직 되지 않아요.)')
            self.buy_button.setText('아이템을 선택해 주세요')
            self.buy_button.setEnabled(False)
            return
        info = ITEMS[item_id]
        owned = item_id in self.store.owned
        equipped = self.store.equipped[info['category']] == item_id
        self.description.setText(f"{info['name']}\n필요 레벨: Lv.{info['level']}\n가격: {info['price']:,} 코인" +
                                 ('\n이미 보유한 아이템이에요.' if owned else '\n구매 버튼을 눌러야 구매돼요.'))
        if equipped:
            label, enabled = '이미 장착 중', False
        elif owned:
            label, enabled = '보유 아이템 장착', True
        elif self.store.growth.level < info['level']:
            label, enabled = f"Lv.{info['level']}에 해금", False
        elif self.store.growth.coins < info['price']:
            label, enabled = '코인 부족', False
        else:
            label, enabled = f"구매하기 · {info['price']:,} 코인", True
        self.buy_button.setText(label)
        self.buy_button.setEnabled(enabled)

    def buy_selected(self):
        item_id = self.selected_item
        if not item_id:
            return
        if item_id in self.store.owned:
            result = self.store.equip(item_id)
        else:
            result = self.store.purchase(item_id)
        self.owner.scene.update()
        self.reset_preview()
        self.refresh()
        QMessageBox.information(self, '상점', result)


class InventoryDialog(BuddyDialog):
    page_key = 'inventory'
    def __init__(self, app_window):
        super().__init__(app_window)
        self.owner = app_window
        self.store = app_window.store
        self.setWindowTitle('pixel-buddy · 인벤토리')
        self.resize(460, 480)
        self.root = QVBoxLayout(self)
        self.root.addWidget(QLabel('🎀 내 아이템 · 구매한 아이템을 장착할 수 있어요.'))
        self.container = QWidget()
        self.container.setObjectName('inventoryContent')
        # Don't override the theme with a dark, nested QWidget stylesheet.
        self.layout_items = QVBoxLayout(self.container)
        self.layout_items.setSpacing(10)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName('inventoryScroll')
        scroll.viewport().setObjectName('inventoryViewport')
        scroll.setWidget(self.container)
        self.root.addWidget(scroll)
        self.install_navigation(self.root)
        self.refresh()

    def refresh(self):
        while self.layout_items.count():
            item = self.layout_items.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            if item.layout():
                from PySide6.QtWidgets import QWidget as _W
                _W().setLayout(item.layout())
        for category in ('의상', '머리띠', '컴퓨터', '책상', '소품'):
            heading = QLabel('✦ ' + category)
            heading.setObjectName('sectionHeading')
            self.layout_items.addWidget(heading)
            options = [item for item in sorted(self.store.owned) if ITEMS[item]['category'] == category]
            if category == '머리띠': options = ['none'] + options
            for item_id in options:
                row_widget = QFrame()
                row_widget.setObjectName('inventoryRow')
                row = QHBoxLayout(row_widget)
                name = '머리띠 없음' if item_id == 'none' else ITEMS[item_id]['name']
                active = (self.store.equipped[category] == ('' if item_id == 'none' else item_id))
                row.addWidget(QLabel(name), 1)
                button = QPushButton('장착 중' if active else '장착')
                button.setEnabled(not active)
                button.clicked.connect(lambda _, i=item_id: self.equip_item(i))
                row.addWidget(button)
                self.layout_items.addWidget(row_widget)
        self.layout_items.addStretch()

    def equip_item(self, item_id):
        self.store.equip(item_id)
        self.owner.scene.update()
        self.refresh()


class SettingsDialog(BuddyDialog):
    page_key = 'settings'
    def __init__(self, app_window):
        super().__init__(app_window)
        self.owner = app_window
        self.store = app_window.store
        self.setWindowTitle('pixel-buddy · 설정')
        self.resize(515, 660)
        root_layout = QVBoxLayout(self)
        body = QWidget()
        layout = QVBoxLayout(body)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(body)
        root_layout.addWidget(scroll)
        layout.addWidget(QLabel('⚙ pixel-buddy 설정'))
        layout.addWidget(QLabel('적용할 테마 (구매한 테마만 표시)'))
        self.theme_selector = QComboBox()
        for theme_id in THEMES:
            if theme_id in self.store.owned_themes:
                self.theme_selector.addItem(THEMES[theme_id].name, theme_id)
        self.theme_selector.setCurrentIndex(self.theme_selector.findData(self.store.active_theme))
        self.theme_selector.currentIndexChanged.connect(self.change_theme)
        layout.addWidget(self.theme_selector)
        layout.addWidget(QLabel('동물 변경 (레벨과 구매 아이템 유지)'))
        self.animal_selector = QComboBox()
        for species, label in ANIMALS.items():
            self.animal_selector.addItem(label, species)
        self.animal_selector.setCurrentIndex(self.animal_selector.findData(self.store.animal))
        layout.addWidget(self.animal_selector)
        change_animal_button = QPushButton('선택한 동물로 변경')
        change_animal_button.clicked.connect(self.change_animal)
        layout.addWidget(change_animal_button)
        layout.addWidget(QLabel('책상 프리셋'))
        self.preset_selector = QComboBox()
        self.preset_selector.addItems(['작업용', '게임용', '야간용'])
        layout.addWidget(self.preset_selector)
        preset_actions = QHBoxLayout()
        save_preset = QPushButton('현재 세팅 저장')
        save_preset.clicked.connect(self.save_preset)
        load_preset = QPushButton('세팅 불러오기')
        load_preset.clicked.connect(self.load_preset)
        preset_actions.addWidget(save_preset)
        preset_actions.addWidget(load_preset)
        layout.addLayout(preset_actions)
        self.auto_focus = QCheckBox('전체화면 게임에서 펫 자동 숨기기')
        self.auto_focus.setChecked(bool(self.owner.ui_settings.value('auto_focus', True, type=bool)))
        self.auto_focus.toggled.connect(lambda value:self.owner.ui_settings.setValue('auto_focus', value))
        layout.addWidget(self.auto_focus)
        layout.addWidget(QLabel('펫 투명도'))
        alpha = QSlider(Qt.Orientation.Horizontal)
        alpha.setRange(40, 100)
        alpha.setValue(int(self.owner.ui_settings.value('opacity', 100)))
        alpha.valueChanged.connect(lambda value:(self.owner.setWindowOpacity(value/100), self.owner.ui_settings.setValue('opacity', value)))
        layout.addWidget(alpha)
        layout.addWidget(QLabel('캐릭터 행동 상태'))
        selector = QComboBox()
        for key, label in MODES.items(): selector.addItem(label, key)
        selector.setCurrentIndex(list(MODES).index(self.owner.manual_mode))
        selector.currentIndexChanged.connect(lambda _: self.owner.set_mode(selector.currentData()))
        layout.addWidget(selector)
        layout.addWidget(QLabel('펫 크기'))
        sizes = QComboBox()
        for pct in (50, 60, 70, 75, 80, 90, 100, 110, 125):
            sizes.addItem(f'{pct}%', pct)
        sizes.setCurrentIndex(sizes.findData(self.store.scale_percent))
        sizes.currentIndexChanged.connect(lambda _: self.owner.set_scale(sizes.currentData()))
        layout.addWidget(sizes)
        toolbar = QCheckBox('상단 도구바 표시')
        toolbar.setChecked(self.store.toolbar_visible)
        toolbar.toggled.connect(self.owner.set_toolbar_visible)
        layout.addWidget(toolbar)
        always = QCheckBox('항상 위에 표시')
        always.setChecked(self.owner.always_on_top)
        always.toggled.connect(self.owner.set_always_on_top)
        layout.addWidget(always)
        self.clickthrough = QCheckBox('클릭 통과 모드 (트레이에서 해제 가능)')
        self.clickthrough.toggled.connect(self.owner.set_clickthrough)
        layout.addWidget(self.clickthrough)
        from .autostart import is_enabled, executable_path
        self.autostart_box = QCheckBox('로그인 시 자동 실행 (Windows / macOS)')
        self.autostart_box.setChecked(is_enabled())
        self.autostart_box.setEnabled(executable_path() is not None)
        self.autostart_box.toggled.connect(self.change_autostart)
        layout.addWidget(self.autostart_box)
        if executable_path() is None:
            hint = QLabel('자동 실행은 Windows의 PixelBuddy.exe 또는 Mac의 PixelBuddy.app으로 실행할 때 설정할 수 있어요.')
            hint.setWordWrap(True)
            layout.addWidget(hint)
        note = QLabel('자동 감지는 Windows/macOS 활성 앱·키보드 이벤트를 기준으로 합니다.\n'
                      '입력한 글자는 저장하지 않아요. 영상 재생·게임 승패는 정확히 감지하지 못할 수 있어요.')
        note.setWordWrap(True)
        layout.addWidget(note)
        if sys.platform == 'darwin':
            mac_hint = QLabel(self.owner.detector.permission_hint())
            mac_hint.setWordWrap(True)
            layout.addWidget(mac_hint)
        layout.addStretch()
        self.install_navigation(root_layout)


    def change_animal(self):
        animal = self.animal_selector.currentData()
        if self.store.change_animal(animal):
            self.owner.scene.update()
            if self.owner.dialog: self.owner.dialog.refresh()
            QMessageBox.information(self, '동물 변경', f'{ANIMALS[animal]} 친구로 변경했어요!')

    def save_preset(self):
        self.store.save_preset(self.preset_selector.currentText())
        QMessageBox.information(self, '프리셋', '현재 책상 구성을 저장했어요.')

    def load_preset(self):
        if self.store.load_preset(self.preset_selector.currentText()):
            self.owner.scene.update()
            QMessageBox.information(self, '프리셋', '책상 구성을 불러왔어요.')
        else:
            QMessageBox.information(self, '프리셋', '먼저 해당 프리셋을 저장해 주세요.')

    def change_autostart(self, enabled):
        from .autostart import set_enabled, is_enabled
        ok, message = set_enabled(enabled)
        if not ok:
            self.autostart_box.blockSignals(True)
            self.autostart_box.setChecked(is_enabled())
            self.autostart_box.blockSignals(False)
            QMessageBox.warning(self, '자동 실행 설정', message)

    def change_theme(self, _index):
        theme_id = self.theme_selector.currentData()
        if theme_id and theme_id in self.store.owned_themes:
            self.store.equip_theme(theme_id)
            self.owner.apply_theme()

    def refresh_themes(self):
        current = self.store.active_theme
        self.theme_selector.blockSignals(True)
        self.theme_selector.clear()
        for theme_id in THEMES:
            if theme_id in self.store.owned_themes:
                self.theme_selector.addItem(THEMES[theme_id].name, theme_id)
        self.theme_selector.setCurrentIndex(self.theme_selector.findData(current))
        self.theme_selector.blockSignals(False)


class Management(BuddyDialog):
    page_key = 'home'
    """Small main menu: store, inventory and settings open in separate windows."""
    def __init__(self, app_window):
        super().__init__(app_window)
        self.owner = app_window
        self.store = app_window.store
        self.setWindowTitle('pixel-buddy · 내 작은 동료')
        self.resize(430, 340)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        self.title = QLabel()
        self.title.setStyleSheet('font-size:20px;font-weight:bold')
        self.progress = QProgressBar()
        self.stats = QLabel()
        layout.addWidget(self.title)
        layout.addWidget(self.progress)
        layout.addWidget(self.stats)
        self.achievements_label = QLabel()
        self.achievements_label.setWordWrap(True)
        layout.addWidget(self.achievements_label)
        room_button = QPushButton('🏡 방 미리보기 / 책상으로 돌아오기')
        room_button.clicked.connect(self.owner.toggle_room)
        layout.addWidget(room_button)
        for label, key in [('🛍 상점 열기', 'shop'), ('🎀 인벤토리 열기', 'inventory'), ('⚙ 설정 열기', 'settings')]:
            btn = QPushButton(label)
            btn.setMinimumHeight(43)
            btn.clicked.connect(lambda _, k=key: self.owner.open_page(k))
            layout.addWidget(btn)
        layout.addStretch()
        self.install_navigation(layout)
        self.refresh()

    def refresh(self):
        g = self.store.growth
        self.title.setText(f"🐾 {self.store.nickname or ANIMALS.get(self.store.animal, '동료')} · Lv.{g.level} · {g.coins:,} 코인")
        self.progress.setMaximum(xp_required(g.level))
        self.progress.setValue(g.xp)
        self.progress.setFormat(f'{g.xp} / {xp_required(g.level)} XP')
        hours, rem = divmod(g.total_seconds, 3600)
        self.stats.setText(f'함께한 시간: {hours}시간 {rem // 60}분')
        self.achievements_label.setText('🏆 업적: ' + (', '.join(sorted(self.store.achievements)) or '아직 없어요') + '\n🎮 게임 시간: ' + str(self.store.activity_seconds.get('gaming', 0)//60) + '분')


class DesktopBuddy(QWidget):
    def __init__(self):
        super().__init__()
        path = (Path.home() / 'AppData' / 'Local' / 'PixelBuddy' / 'save.sqlite3' if sys.platform == 'win32' else Path.home() / 'Library' / 'Application Support' / 'PixelBuddy' / 'save.sqlite3' if sys.platform == 'darwin' else Path.home() / '.pixel_buddy' / 'save.sqlite3')
        self.store = GameStore(path)
        self.detector = ActivityDetector()
        self.manual_mode = 'auto'
        self.drag_pos = None
        self.clickthrough = False
        self.dialog = None
        self.pages = {}
        self.navigation_history = []
        self.current_page = None
        self.ui_settings = QSettings('PixelBuddy', 'PixelBuddy')
        self.always_on_top = self.ui_settings.value('always_on_top', True, type=bool)
        self.management_position = self.ui_settings.value('management_position', None)
        self._event_timeout = 0.0
        self._next_event = time.monotonic() + random.uniform(45, 120)
        self._focus_hidden = False
        self._last_focus_check = 0.0
        self._last_activity_save = time.monotonic()
        self.closed = False
        self.setWindowTitle('pixel-buddy')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # A normal frameless window stays visible when switching apps on macOS.
        native_type = Qt.WindowType.Window if sys.platform == 'darwin' else Qt.WindowType.Tool
        flags = Qt.WindowType.FramelessWindowHint | native_type
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.scene = BuddyScene(self.store, self)
        self.toolbar = PetToolbar(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.scene)
        self.set_scale(self.store.scale_percent)
        self.set_toolbar_visible(self.store.toolbar_visible)
        self.move(100, 100)
        self.setWindowOpacity(int(self.ui_settings.value('opacity', 100))/100)
        self.last_tick = time.monotonic()
        self.save_tick = self.last_tick
        self.tick = QTimer(self)
        self.tick.timeout.connect(self.on_tick)
        self.tick.start(250)
        self._create_tray()

    def apply_theme(self):
        QApplication.instance().setStyleSheet(make_stylesheet(get_theme(self.store.active_theme)))
        settings = self.pages.get('settings')
        if settings is not None:
            settings.refresh_themes()

    def _create_tray(self):
        pix = QPixmap(32, 32)
        pix.fill(QColor('#9F8BC0'))
        icon = QIcon(pix)
        self.tray = QSystemTrayIcon(icon, self)
        menu = QMenu()
        menu.addAction('캐릭터 보기', self.show_buddy)
        menu.addAction('상태 / 메뉴', self.open_dialog)
        menu.addAction('상점', lambda:self.open_page('shop'))
        menu.addAction('인벤토리', lambda:self.open_page('inventory'))
        menu.addAction('설정', lambda:self.open_page('settings'))
        menu.addAction('도구바 표시 / 숨기기', lambda:self.set_toolbar_visible(not self.store.toolbar_visible))
        menu.addAction('크게 (+10%)', lambda:self.change_scale(10))
        menu.addAction('작게 (-10%)', lambda:self.change_scale(-10))
        menu.addAction('자동 감지', lambda: self.set_mode('auto'))
        menu.addAction('클릭 통과 해제', lambda: self.set_clickthrough(False))
        menu.addSeparator()
        menu.addAction('종료', self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.open_dialog() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    def on_tick(self):
        now = time.monotonic()
        elapsed = min(2.0, now - self.last_tick)  # Avoid counting Windows sleep/suspend as playtime.
        self.last_tick = now
        levels, coins = self.store.growth.advance(elapsed)
        self.store.activity_seconds[self.scene.mode] = self.store.activity_seconds.get(self.scene.mode, 0) + elapsed
        if now >= self._next_event:
            unique = {'dog': 'happy', 'cat': 'sleep', 'bear': 'snack', 'fox': 'curious', 'rabbit': 'stretch'}
            options = ['coffee','stretch','snack','curious','happy','sleep', unique.get(self.store.animal, 'happy')]
            self.scene.reaction_event = random.choice(options)
            self._event_timeout = now + 3
            self._next_event = now + random.uniform(60, 160)
        if self.scene.reaction_event and now >= self._event_timeout:
            self.scene.reaction_event = ''
        if now - self._last_focus_check >= 2:
            self._last_focus_check = now
            self.check_fullscreen_focus()
        achievements = self.store.award_achievements()
        self.scene.frame += 1
        if self.scene.frame % 4 == 0:
            new_mode = self.detector.detect() if self.manual_mode == 'auto' else self.manual_mode
            if new_mode != self.scene.mode:
                self.scene.mode = new_mode
            self.scene.update()
        if now - self.save_tick >= 15 or levels:
            self.store.save()
            self.save_tick = now
        if self.dialog and self.dialog.isVisible() and self.scene.frame % 8 == 0:
            self.dialog.refresh()
        if levels and 'shop' in self.pages and self.pages['shop'].isVisible():
            self.pages['shop'].refresh()
        if achievements and self.dialog and self.dialog.isVisible():
            self.dialog.refresh()
        if levels:
            self.tray.showMessage('Pixel Buddy 레벨업!', f"Lv.{self.store.growth.level} 달성! 코인 +{coins}", QSystemTrayIcon.MessageIcon.Information, 2500)

    def toggle_room(self):
        # A room-view prototype only; furniture placement remains a future update.
        self.scene.room_view = not self.scene.room_view
        self.scene.update()

    def check_fullscreen_focus(self):
        enabled = self.ui_settings.value('auto_focus', True, type=bool)
        if not enabled or sys.platform != 'win32':
            if self._focus_hidden:
                self.show()
                self._focus_hidden = False
            return
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd: return
            # Ignore our own application windows (e.g. maximized management dialog).
            if hwnd in (int(self.winId()),): return
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            screen = QApplication.screenAt(QPoint(rect.left+10, rect.top+10))
            if screen is None: return
            geo = screen.geometry()
            full = (rect.left <= geo.left() and rect.top <= geo.top() and
                    rect.right >= geo.right() and rect.bottom >= geo.bottom())
            from .activity import foreground, GAMES
            exe, _ = foreground()
            should_hide = full and exe in GAMES
            if should_hide and self.isVisible():
                self.hide(); self._focus_hidden = True
            elif not should_hide and self._focus_hidden:
                self.show(); self._focus_hidden = False
        except Exception:
            pass

    def set_scale(self, percent):
        if percent is None: return
        percent = max(50, min(125, int(percent)))
        self.store.scale_percent = percent
        self.scene.setFixedSize(round(480*percent/100), round(288*percent/100))
        self.toolbar.setFixedWidth(self.scene.width())
        self.setFixedSize(self.scene.width(), self.scene.height() + (36 if self.store.toolbar_visible else 0))
        self.scene.update()
        self.store.save()

    def change_scale(self, delta):
        self.set_scale(self.store.scale_percent + delta)

    def set_toolbar_visible(self, visible):
        self.store.toolbar_visible = bool(visible)
        self.toolbar.setVisible(bool(visible))
        self.setFixedSize(self.scene.width(), self.scene.height() + (36 if visible else 0))
        self.store.save()

    def hide_toolbar(self):
        self.set_toolbar_visible(False)

    def set_mode(self, key):
        self.manual_mode = key
        if key != 'auto':
            self.scene.mode = key
            self.scene.update()

    def set_always_on_top(self, enabled):
        self.always_on_top = bool(enabled)
        self.ui_settings.setValue('always_on_top', self.always_on_top)
        flags = self.windowFlags()
        flag = Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags | flag if self.always_on_top else flags & ~flag)
        self.show()

    def set_clickthrough(self, enabled):
        self.clickthrough = enabled
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)
        # Qt.WindowTransparentForInput helps on Windows with click-through.
        flags = self.windowFlags()
        flag = Qt.WindowType.WindowTransparentForInput
        self.setWindowFlags(flags | flag if enabled else flags & ~flag)
        # Window flag changes can recreate the native Mac window.
        if self.always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.show()
        settings = self.pages.get('settings')
        if settings:
            settings.clickthrough.blockSignals(True)
            settings.clickthrough.setChecked(enabled)
            settings.clickthrough.blockSignals(False)

    def remember_management_position(self, point):
        """Shared persistent position for every management page."""
        if point is None:
            return
        self.management_position = QPoint(point)
        self.ui_settings.setValue('management_position', self.management_position)

    def _management_window(self, page):
        if page == 'home':
            if self.dialog is None:
                self.dialog = Management(self)
            return self.dialog
        classes = {'shop': ShopDialog, 'inventory': InventoryDialog, 'settings': SettingsDialog}
        if page not in self.pages:
            self.pages[page] = classes[page](self)
        return self.pages[page]

    def _show_management(self, page, record_history=True):
        if page not in ('home', 'shop', 'inventory', 'settings'):
            return
        if self.current_page == page:
            target = self._management_window(page)
            target.show()
            target.raise_()
            target.activateWindow()
            return
        if record_history and self.current_page is not None:
            existing = self._management_window(self.current_page)
            if existing.isVisible():
                self.navigation_history.append(self.current_page)
            else:
                self.navigation_history.clear()
        previous = self._management_window(self.current_page) if self.current_page else None
        if previous is not None and previous.isVisible():
            self.remember_management_position(previous.pos())
            previous.hide()
        target = self._management_window(page)
        if page in ('home', 'shop', 'inventory'):
            target.refresh()
        # All pages return to the same screen location, even after app restart.
        if self.management_position is not None:
            pos = self.management_position
            if not isinstance(pos, QPoint):
                pos = QPoint(pos)
            # Keep the window on screen if the monitor layout changed.
            screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
            if screen:
                rect = screen.availableGeometry()
                x = max(rect.left(), min(pos.x(), rect.right() - target.width() + 1))
                y = max(rect.top(), min(pos.y(), rect.bottom() - target.height() + 1))
                target.move(x, y)
        self.current_page = page
        target.show()
        target.raise_()
        target.activateWindow()

    def navigate_back(self):
        # Back always returns to the companion overview, not the previous page.
        # Clear stale navigation entries so future visits stay predictable.
        self.navigation_history.clear()
        self._show_management('home', record_history=False)

    def open_dialog(self):
        self._show_management('home')

    def open_page(self, page):
        self._show_management(page)

    def show_buddy(self):
        self.show()
        self.raise_()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.open_dialog()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, _event):
        self.drag_pos = None

    def mouseDoubleClickEvent(self, _event):
        self.open_dialog()

    def closeEvent(self, event):
        if not self.closed:
            self.hide()
            event.ignore()
        else:
            event.accept()

    def quit_app(self):
        self.tick.stop()
        self.closed = True
        self.detector.stop()
        self.store.close()
        self.tray.hide()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(STYLE)
    window = DesktopBuddy()
    window.apply_theme()
    if not window.store.animal:
        picker = AnimalPicker()
        if picker.exec() != QDialog.DialogCode.Accepted:
            window.quit_app()
            return 0
        window.store.animal = picker.selected
        window.store.nickname = picker.nickname.text().strip() or ANIMALS[picker.selected]
        window.store.save()
    window.show()
    app.aboutToQuit.connect(lambda: None if window.closed else window.quit_app())
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
