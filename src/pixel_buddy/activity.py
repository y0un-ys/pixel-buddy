"""Windows/macOS foreground classification, with optional pynput and psutil.
Only the *time* of an input event is retained, never which key was pressed.
"""
import os
import time
import ctypes
from ctypes import wintypes

BROWSERS = {'chrome.exe', 'msedge.exe', 'firefox.exe', 'whale.exe', 'brave.exe', 'opera.exe', 'google chrome', 'safari', 'firefox', 'naver whale', 'brave browser', 'microsoft edge', 'arc'}
GAMES = {'league of legends.exe', 'valorant-win64-shipping.exe', 'overwatch.exe', 'eldenring.exe',
         'minecraft.exe', 'javaw.exe', 'stardew valley.exe', 'hades.exe', 'hades2.exe',
         'palworld-win64-shipping.exe', 'game.exe', 'genshinimpact.exe'}


def foreground():
    """Return (application name, window title) when platform APIs permit."""
    if __import__('sys').platform == 'darwin':
        return _mac_foreground()
    if os.name != 'nt':
        return '', ''
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return '', ''
        size = user32.GetWindowTextLengthW(hwnd) + 1
        title_buffer = ctypes.create_unicode_buffer(size)
        user32.GetWindowTextW(hwnd, title_buffer, size)
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        import psutil
        exe = psutil.Process(pid.value).name().lower()
        return exe, title_buffer.value.lower()
    except Exception:
        return '', ''


def _mac_foreground():
    """Best-effort frontmost app and window title on macOS.

    Reading window names may require Screen Recording permission on some macOS
    versions. We never request screenshots or inspect window contents.
    """
    try:
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        if app is None:
            return '', ''
        name = str(app.localizedName() or '').lower()
        title = ''
        try:
            import Quartz
            options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
            windows = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID) or []
            for win in windows:
                if win.get(Quartz.kCGWindowOwnerPID) == app.processIdentifier() and win.get(Quartz.kCGWindowLayer, 1) == 0:
                    title = str(win.get(Quartz.kCGWindowName, '') or '').lower()
                    if title:
                        break
        except Exception:
            pass
        return name, title
    except Exception:
        return '', ''


def mac_input_monitoring_granted():
    """Best-effort TCC status; None if the API is unavailable.

    This check does not request permission or read any keystroke.
    """
    if __import__('sys').platform != 'darwin':
        return None
    try:
        import Quartz
        fn = getattr(Quartz, 'CGPreflightListenEventAccess', None)
        return bool(fn()) if fn is not None else None
    except Exception:
        return None


def choose_activity(last_key, last_mouse, now, keyboard_usable=True):
    """Pure classifier: timestamps only, never key contents."""
    if keyboard_usable and 0 <= now - last_key < 4.0:
        return 'typing'
    if 0 <= now - max(last_key, last_mouse) > 90:
        return 'idle'
    if 0 <= now - last_mouse < 6.0:
        return 'mouse'
    return 'idle'


class ActivityDetector:
    def __init__(self):
        self.last_key = -10000.0
        self.last_mouse = -10000.0
        self.last_input = time.monotonic()
        self.listener = None
        self.mouse_listener = None
        self.keyboard_available = False
        self.mouse_available = False
        self.mac_permission = mac_input_monitoring_granted()

        # Failure of one listener must not prevent the other one running.
        try:
            from pynput import keyboard
            self.listener = keyboard.Listener(on_press=self._on_key)
            self.listener.start()
            self.keyboard_available = True
        except Exception:
            self.listener = None
        try:
            from pynput import mouse
            self.mouse_listener = mouse.Listener(on_click=self._on_click, on_move=self._on_move)
            self.mouse_listener.start()
            self.mouse_available = True
        except Exception:
            self.mouse_listener = None

    def _on_key(self, _key):
        now = time.monotonic()
        self.last_input = now
        self.last_key = now

    def _on_click(self, *_args):
        self._mark_mouse()

    def _on_move(self, *_args):
        self._mark_mouse()

    def _mark_mouse(self):
        now = time.monotonic()
        self.last_input = now
        self.last_mouse = now

    def detect(self):
        exe, title = foreground()
        if exe in GAMES or any(token in exe for token in ('stardew valley', 'minecraft', 'hades', 'steam game')):
            return 'gaming'
        if exe in BROWSERS and ('youtube' in title or 'netflix' in title or 'twitch' in title):
            return 'watching'
        now = time.monotonic()
        # On macOS pynput may appear active even though TCC blocks key events.
        # Never report mouse forever merely because the listener started.
        keyboard_usable = self.keyboard_available and self.mac_permission is not False
        return choose_activity(self.last_key, self.last_mouse, now, keyboard_usable)

    def permission_hint(self):
        if __import__('sys').platform != 'darwin':
            return ''
        if self.mac_permission is False:
            return ('⌨ 자동 타이핑 감지 권한이 없어요. macOS 시스템 설정 → '
                    '개인정보 보호 및 보안 → 입력 모니터링에서 PixelBuddy를 허용하고 앱을 재시작하세요.')
        if not self.keyboard_available:
            return ('⌨ 키보드 감지 시작에 실패했어요. 입력 모니터링 및 손쉬운 사용 권한을 '
                    '확인한 후 앱을 재시작하세요.')
        return ('자동 타이핑 감지가 안 되면 macOS 입력 모니터링에서 PixelBuddy를 허용하고 '
                '앱을 재시작하세요. 입력 내용은 읽거나 저장하지 않습니다.')

    def stop(self):
        for listener in (self.listener, self.mouse_listener):
            try:
                if listener:
                    listener.stop()
            except Exception:
                pass
