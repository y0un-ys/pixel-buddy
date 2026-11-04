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
    """Select an active behavior from observed event timestamps.

    Only actual recent events can trigger typing or mouse animation.
    An inaccessible keyboard listener must not imply mouse activity.
    No key contents are examined or retained.
    """
    if keyboard_usable and 0 <= now - last_key < 4.0:
        return 'typing'
    if 0 <= now - last_mouse < 5.0:
        return 'mouse'
    return 'idle'


def presentation_mode(activity, inactive_seconds, sleep_after=150.0):
    """Sleep is a presentation state, never an input-detector event."""
    if activity == 'idle' and inactive_seconds >= sleep_after:
        return 'sleep'
    return activity


class ActivityDetector:
    def __init__(self):
        self.last_key = -10000.0
        self.last_mouse = -10000.0
        self.last_input = time.monotonic()
        self.listener = None
        self.mouse_listener = None
        self.keyboard_available = False
        self.keyboard_events_seen = 0
        self.mouse_events_seen = 0
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
        self.keyboard_events_seen += 1

    def _on_click(self, *_args):
        self._mark_mouse()

    def _on_move(self, *_args):
        self._mark_mouse()

    def _mark_mouse(self):
        now = time.monotonic()
        self.last_input = now
        self.last_mouse = now
        self.mouse_events_seen += 1

    def inactive_seconds(self):
        return max(0.0, time.monotonic() - self.last_input)

    def diagnostic(self):
        now = time.monotonic()
        key_age = f'{now - self.last_key:.0f}s' if self.keyboard_events_seen else '없음'
        mouse_age = f'{now - self.last_mouse:.0f}s' if self.mouse_events_seen else '없음'
        access = ('미허용' if self.mac_permission is False else '확인 불가' if self.mac_permission is None else '허용')
        return (f'키보드: {key_age} (리스너 {"시작" if self.keyboard_available else "실패"}, 권한 {access}) | '
                f'마우스: {mouse_age} | 미입력: {self.inactive_seconds():.0f}s')

    def detect(self):
        exe, title = foreground()
        if exe in GAMES or any(token in exe for token in ('stardew valley', 'minecraft', 'hades', 'steam game')):
            return 'gaming'
        if exe in BROWSERS and ('youtube' in title or 'netflix' in title or 'twitch' in title):
            return 'watching'
        now = time.monotonic()
        # Listener.start() does not guarantee TCC permission on macOS.
        # We only classify observed events and never synthesize activity.
        return choose_activity(self.last_key, self.last_mouse, now, self.keyboard_available)

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
