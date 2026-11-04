"""Shared accessible Qt color tokens for Pixel Buddy management UI."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    foreground: str
    secondary: str
    surface: str
    border: str
    accent: str
    accent_hover: str
    button_text: str
    disabled_background: str
    disabled_text: str
    selection: str
    selection_text: str


DEFAULT_THEME = Theme(
    name="기본 화이트", background="#FFFFFF", foreground="#222222",
    secondary="#60646C", surface="#F3F4F6", border="#D1D5DB",
    accent="#334155", accent_hover="#475569", button_text="#FFFFFF",
    disabled_background="#E5E7EB", disabled_text="#6B7280",
    selection="#BFD5ED", selection_text="#17202F",
)


# Stable IDs are persisted independently of the equipment catalogue.
THEMES = {
    'white': DEFAULT_THEME,
    'pink': Theme('벚꽃 핑크', '#FFF2F6', '#583645', '#735360', '#FFE0EA', '#E8B9C9', '#A63B70', '#8A2A5A', '#FFFFFF', '#F3DCE4', '#765762', '#F8BFDA', '#402132'),
    'mint': Theme('민트 크림', '#F0FFF9', '#244C43', '#44675E', '#D5F5E8', '#A8D6C4', '#25755F', '#185E4A', '#FFFFFF', '#D6EBE2', '#53776C', '#A8E5D1', '#153A31'),
    'lavender': Theme('라벤더', '#F7F3FF', '#483A66', '#695B80', '#E9DDF9', '#CCB9E4', '#7452A2', '#593989', '#FFFFFF', '#E5DDF0', '#716583', '#D8BDF3', '#342449'),
    'dark': Theme('다크 나이트', '#202334', '#F5F3FA', '#C5C1D3', '#30354B', '#535B78', '#7259AD', '#8A6DC6', '#FFFFFF', '#414455', '#B9B5C3', '#51416E', '#FFFFFF'),
    'choco': Theme('초코 브라운', '#FFF6EC', '#503C30', '#79665A', '#EFDCC5', '#D6BA9D', '#845638', '#6C442B', '#FFFFFF', '#E8DBCD', '#7F7065', '#E2C4A5', '#38251A'),
}
THEME_PRICES = {'white': 0, 'pink': 300, 'mint': 400, 'lavender': 450, 'dark': 600, 'choco': 500}


def get_theme(key: str) -> Theme:
    return THEMES.get(key, DEFAULT_THEME)


def make_stylesheet(t: Theme) -> str:
    """One palette for every dialog, including nested scroll areas and popups."""
    return f"""
    QWidget {{ color: {t.foreground}; font-family: 'Malgun Gothic', 'Segoe UI'; font-size: 12px; }}
    QDialog, QScrollArea, QScrollArea QWidget, QScrollArea QWidget#inventoryContent,
    QScrollArea QWidget#inventoryViewport, QTabWidget QWidget {{ background-color: {t.background}; }}
    QLabel {{ color: {t.foreground}; background: transparent; }}
    QLabel#secondaryText {{ color: {t.secondary}; }}
    QLabel#sectionHeading {{ color: {t.foreground}; font-weight: bold; padding-top: 8px; }}
    QFrame#panel, QFrame#inventoryRow {{ background-color: {t.surface}; border-radius: 10px; }}
    QFrame#panel QLabel, QFrame#inventoryRow QLabel {{ color: {t.foreground}; background: transparent; }}
    QPushButton {{ background: {t.accent}; color: {t.button_text}; border: 1px solid {t.accent};
                  border-radius: 8px; padding: 9px 11px; font-weight: bold; }}
    QPushButton:hover {{ background: {t.accent_hover}; border-color: {t.accent_hover}; }}
    QPushButton:disabled {{ background: {t.disabled_background}; color: {t.disabled_text};
                           border-color: {t.border}; }}
    QPushButton#pixelItemTile {{ background: {t.surface}; color: {t.foreground};
                                 border: 2px solid {t.border}; border-radius: 11px; padding: 6px; }}
    QPushButton#pixelItemTile:checked {{ background: {t.selection}; border: 3px solid {t.accent}; }}
    QPushButton#pixelItemTile:hover {{ border-color: {t.accent_hover}; }}
    QLineEdit, QComboBox, QSpinBox {{ background: {t.background}; color: {t.foreground};
                                   selection-background-color: {t.selection}; selection-color: {t.selection_text};
                                   border: 1px solid {t.border}; border-radius: 6px; padding: 7px; }}
    QLineEdit:focus, QComboBox:focus {{ border: 2px solid {t.accent_hover}; }}
    QComboBox QAbstractItemView, QAbstractItemView, QListView {{ background: {t.background};
                          color: {t.foreground}; selection-background-color: {t.selection};
                          selection-color: {t.selection_text}; border: 1px solid {t.border}; }}
    QCheckBox {{ color: {t.foreground}; spacing: 8px; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; }}
    QProgressBar {{ color: {t.foreground}; border: 1px solid {t.border}; border-radius: 6px;
                    background: {t.surface}; text-align: center; height: 15px; }}
    QProgressBar::chunk {{ background: {t.accent}; border-radius: 5px; }}
    QTabWidget::pane {{ border: 1px solid {t.border}; background: {t.background}; }}
    QTabBar::tab {{ color: {t.foreground}; background: {t.surface}; border: 1px solid {t.border};
                    padding: 10px 14px; border-top-left-radius: 7px; border-top-right-radius: 7px; }}
    QTabBar::tab:selected {{ background: {t.selection}; color: {t.foreground}; }}
    QMenu {{ color: {t.foreground}; background: {t.background}; border: 1px solid {t.border}; }}
    QMenu::item:selected {{ background: {t.selection}; color: {t.selection_text}; }}
    QRadioButton {{ color: {t.foreground}; }}
    QGroupBox {{ color: {t.foreground}; border: 1px solid {t.border}; margin-top: 6px; }}
    QToolTip {{ color: {t.foreground}; background: {t.surface}; border: 1px solid {t.border}; }}
    QScrollBar:vertical {{ background: {t.surface}; width: 12px; }}
    QScrollBar::handle:vertical {{ background: {t.border}; min-height: 25px; border-radius: 5px; }}
    """
