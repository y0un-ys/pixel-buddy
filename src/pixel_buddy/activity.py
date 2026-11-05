"""Windows/macOS foreground classification, with optional pynput and psutil.
Only the *time* of an input event is retained, never which key was pressed.
"""
import os
import time
import ctypes
from collections.abc import Callable
from ctypes import wintypes
from .browser_media import CHROMIUM_APPS

BROWSERS = CHROMIUM_APPS | {'firefox.exe', 'firefox', 'safari'}
GAMES = {'league of legends.exe', 'valorant-win64-shipping.exe', 'overwatch.exe', 'eldenring.exe',
         'minecraft.exe', 'javaw.exe', 'stardew valley.exe', 'hades.exe', 'hades2.exe',
         'palworld-win64-shipping.exe', 'game.exe', 'genshinimpact.exe'}
VIDEO_TITLE_MARKERS = (
    'youtube', '유튜브', 'netflix', '넷플릭스', 'twitch', 'vimeo',
    'dailymotion', 'tving', '티빙', 'wavve', '웨이브', 'disney+', '디즈니+',
    'disney plus', 'coupang play', 'coupangplay', '쿠팡플레이', '쿠팡 플레이',
    'prime video', 'apple tv', 'bilibili', '네이버tv', 'naver tv',
    'chzzk', '치지직', 'soop', '아프리카tv',
    '.mp4', '.webm', '.m4v', '.mov', 'picture-in-picture', '화면 속 화면',
)


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


def visible_video_window() -> bool | None:
    """Visible browser titles only; None means macOS withheld those titles."""
    if __import__('sys').platform != 'darwin':
        return False
    try:
        import Quartz
        if not Quartz.CGPreflightScreenCaptureAccess():
            return None
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        for window in Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID) or []:
            if window.get(Quartz.kCGWindowLayer, 1) != 0:
                continue
            owner = str(window.get(Quartz.kCGWindowOwnerName, '') or '').lower()
            title = str(window.get(Quartz.kCGWindowName, '') or '').lower()
            if owner in BROWSERS and any(marker in title for marker in VIDEO_TITLE_MARKERS):
                return True
        return False
    except (ImportError, AttributeError, OSError):
        return None


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

    The newest valid recent event selects typing or mouse; ties favor typing.
    An inaccessible keyboard listener must not imply mouse activity.
    No key contents are examined or retained.
    """
    key_recent = keyboard_usable and 0 <= now - last_key < 4.0
    mouse_recent = 0 <= now - last_mouse < 5.0
    if key_recent and (not mouse_recent or last_key >= last_mouse):
        return 'typing'
    if mouse_recent:
        return 'mouse'
    return 'idle'


def presentation_mode(activity, inactive_seconds, sleep_after=150.0):
    """Sleep is a presentation state, never an input-detector event."""
    if activity == 'idle' and inactive_seconds >= sleep_after:
        return 'sleep'
    return activity


class _MacKeyboardListener:
    """Observe key-down timestamps on the main run loop without decoding text.

    pynput's Carbon layout lookup runs on its worker thread and can SIGTRAP on
    recent macOS. A passive Quartz tap needs no keyboard layout or key contents.
    """

    def __init__(self, on_press: Callable[[None], None]) -> None:
        import Quartz
        import CoreFoundation
        self._quartz = Quartz
        self._core = CoreFoundation
        self._on_press = on_press
        self._tap = None

    def start(self) -> None:
        q, cf = self._quartz, self._core
        self._tap = q.CGEventTapCreate(
            q.kCGSessionEventTap, q.kCGHeadInsertEventTap,
            q.kCGEventTapOptionListenOnly, q.CGEventMaskBit(q.kCGEventKeyDown),
            self._handle_event, None)
        if self._tap is None:
            raise PermissionError
        self._source = cf.CFMachPortCreateRunLoopSource(None, self._tap, 0)
        self._loop = cf.CFRunLoopGetCurrent()
        cf.CFRunLoopAddSource(self._loop, self._source, cf.kCFRunLoopCommonModes)

    def _handle_event(self, _proxy, event_type, event, _context):
        q = self._quartz
        if event_type in (q.kCGEventTapDisabledByTimeout, q.kCGEventTapDisabledByUserInput):
            q.CGEventTapEnable(self._tap, True)
        elif event_type == q.kCGEventKeyDown:
            self._on_press(None)
        return event

    def stop(self) -> None:
        if self._tap is not None:
            q, cf = self._quartz, self._core
            q.CGEventTapEnable(self._tap, False)
            cf.CFRunLoopRemoveSource(self._loop, self._source, cf.kCFRunLoopCommonModes)
            cf.CFMachPortInvalidate(self._tap)
            self._tap = None


class ActivityDetector:
    def __init__(self, video_state: Callable[[str], bool | None] | None = None):
        self.video_state = video_state
        self.video_window_state: bool | None = False
        self.mac_activity = None
        if __import__('sys').platform == 'darwin':
            try:
                from .mac_activity import MacActivitySource
                self.mac_activity = MacActivitySource()
            except (ImportError, AttributeError, OSError):
                self.mac_activity = None
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

        # Aggregate event timing needs neither key contents nor a passive tap.
        # Avoid installing permission-bound listeners when this source exists.
        if self.mac_activity is not None:
            return

        # Failure of one listener must not prevent the other one running.
        try:
            if __import__('sys').platform == 'darwin':
                self.listener = _MacKeyboardListener(self._on_key)
            else:
                from pynput import keyboard
                self.listener = keyboard.Listener(on_press=self._on_key)
            self.listener.start()
            self.keyboard_available = True
        except Exception:
            self.listener = None
        try:
            from pynput import mouse
            self.mouse_listener = mouse.Listener(
                on_click=self._on_click, on_move=self._on_move, on_scroll=self._on_scroll)
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

    def _on_scroll(self, *_args):
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
        keyboard_status = ('입력 시각 감지 · 문자 내용 읽지 않음' if self.mac_activity is not None
                           else f'리스너 {"시작" if self.keyboard_available else "실패"}, 권한 {access}')
        video_status = ('화면 기록 권한 필요 — 창 제목만 확인'
                        if self.video_window_state is None else
                        '영상 창 표시됨' if self.video_window_state else '영상 창 없음')
        return (f'키보드: {key_age} ({keyboard_status}) | '
                f'마우스: {mouse_age} | 미입력: {self.inactive_seconds():.0f}s\n'
                f'영상 창 감지: {video_status}')

    def detect(self):
        if self.mac_activity is not None:
            key_time, mouse_time = self.mac_activity.sample()
            if key_time is not None and key_time > self.last_key:
                self.last_key = key_time
                self.last_input = max(self.last_input, key_time)
                self.keyboard_events_seen += 1
            if mouse_time is not None and mouse_time > self.last_mouse:
                self.last_mouse = mouse_time
                self.last_input = max(self.last_input, mouse_time)
                self.mouse_events_seen += 1
        exe, title = foreground()
        if exe in GAMES or any(token in exe for token in ('stardew valley', 'minecraft', 'hades', 'steam game')):
            return 'gaming'
        self.video_window_state = visible_video_window()
        if self.video_window_state:
            return 'watching'
        if exe in BROWSERS:
            playing = self.video_state(exe) if self.video_state is not None else None
            if playing is True:
                return 'watching'
            if playing is None and any(marker in title for marker in VIDEO_TITLE_MARKERS):
                return 'watching'
        now = time.monotonic()
        # Listener.start() does not guarantee TCC permission on macOS.
        # We only classify observed events and never synthesize activity.
        return choose_activity(self.last_key, self.last_mouse, now,
                               self.keyboard_available or self.mac_activity is not None)

    def permission_hint(self):
        if __import__('sys').platform != 'darwin':
            return ''
        if self.mac_activity is not None:
            return '키보드·마우스의 입력 시각만 감지합니다. 입력한 문자나 키 내용은 읽지 않습니다.'
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
