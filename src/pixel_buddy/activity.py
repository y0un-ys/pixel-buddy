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


class ActivityDetector:
    def __init__(self):
        self.last_key = 0.0
        self.last_input = time.monotonic()
        self.listener = None
        self.mouse_listener = None
        self.keyboard_available = False
        try:
            from pynput import keyboard, mouse
            self.listener = keyboard.Listener(on_press=self._on_key)
            self.mouse_listener = mouse.Listener(on_click=self._on_click)
            self.listener.start()
            self.mouse_listener.start()
            self.keyboard_available = True
        except Exception:
            self.stop()

    def _on_key(self, _key):
        now = time.monotonic()
        self.last_input = now
        self.last_key = now

    def _on_click(self, *_args):
        self.last_input = time.monotonic()

    def detect(self):
        exe, title = foreground()
        # Classify only the active window: opening Steam in the background is not gaming.
        if exe in GAMES or any(token in exe for token in ('stardew valley', 'minecraft', 'hades', 'steam game')):
            return 'gaming'
        if exe in BROWSERS and ('youtube' in title or 'netflix' in title or 'twitch' in title):
            return 'watching'  # Heuristic: browser tab may be paused.
        now = time.monotonic()
        if self.keyboard_available:
            if now - self.last_key < 3:
                return 'typing'
            if now - self.last_input > 90:
                return 'idle'
            return 'mouse'
        # Without a global listener, fall back to the manual mode selector.
        return 'idle'

    def stop(self):
        for listener in (self.listener, self.mouse_listener):
            try:
                if listener:
                    listener.stop()
            except Exception:
                pass
