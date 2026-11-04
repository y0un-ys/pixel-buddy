"""Opt-in Windows login startup. No admin permissions or elevated changes."""
import os
import plistlib
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "PixelBuddy"


LAUNCH_AGENT = Path.home() / 'Library' / 'LaunchAgents' / 'com.pixelbuddy.desktop.plist'


def mac_app_path():
    """Resolve the containing .app of a frozen macOS bundle."""
    if sys.platform != 'darwin' or not getattr(sys, 'frozen', False):
        return None
    exe = Path(sys.executable).resolve()
    for parent in exe.parents:
        if parent.suffix == '.app' and (parent / 'Contents' / 'Info.plist').is_file():
            return parent
    return None


def executable_path():
    """Only packaged EXEs are safe to register for GUI startup."""
    if sys.platform == 'darwin':
        app = mac_app_path()
        return (app / 'Contents' / 'MacOS' / 'PixelBuddy') if app else None
    if sys.platform != 'win32' or not getattr(sys, 'frozen', False):
        return None
    path = Path(sys.executable).resolve()
    if path.suffix.lower() != '.exe' or not path.is_file():
        return None
    return path


def command_for(path):
    # Windows CreateProcess quoted executable path; no untrusted user input appended.
    return f'"{path}"'


def is_enabled():
    """Only claim enabled when the registry points at this exact EXE."""
    if sys.platform == 'darwin':
        exe = executable_path()
        try:
            with LAUNCH_AGENT.open('rb') as f:
                data = plistlib.load(f)
            return exe is not None and data.get('ProgramArguments') == [str(exe)]
        except (OSError, ValueError, TypeError):
            return False
    if sys.platform != 'win32':
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
        current = executable_path()
        return current is not None and value == command_for(current)
    except FileNotFoundError:
        return False


def set_enabled(enabled):
    """Returns (success, user-facing description). Writes HKCU only."""
    if sys.platform == 'darwin':
        exe = executable_path()
        if enabled and exe is None:
            return False, '자동 실행은 빌드된 PixelBuddy.app에서만 설정할 수 있어요.'
        try:
            if enabled:
                LAUNCH_AGENT.parent.mkdir(parents=True, exist_ok=True)
                payload = {
                    'Label': 'com.pixelbuddy.desktop',
                    'ProgramArguments': [str(exe)],
                    'RunAtLoad': True,
                    'KeepAlive': False,
                    'LimitLoadToSessionType': 'Aqua',
                }
                with LAUNCH_AGENT.open('wb') as f:
                    plistlib.dump(payload, f)
                return True, 'macOS 다음 로그인부터 Pixel Buddy가 자동 실행돼요.'
            LAUNCH_AGENT.unlink(missing_ok=True)
            return True, 'macOS 로그인 자동 실행을 껐어요.'
        except OSError as error:
            return False, f'macOS 시작 프로그램 설정에 실패했어요: {error}'
    if sys.platform != 'win32':
        return False, 'Windows 또는 macOS에서만 사용할 수 있는 기능이에요.'
    exe = executable_path()
    if exe is None:
        return False, '자동 실행은 빌드한 PixelBuddy.exe에서 설정할 수 있어요.'
    import winreg
    try:
        if enabled:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, command_for(exe))
            return True, 'Windows 로그인 시 Pixel Buddy가 자동으로 실행돼요.'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
        return True, 'Windows 자동 실행을 껐어요.'
    except FileNotFoundError:
        if not enabled:
            return True, 'Windows 자동 실행을 껐어요.'
        return False, '시작 프로그램 등록 경로를 찾을 수 없어요.'
    except OSError as error:
        return False, f'시작 프로그램 설정에 실패했어요: {error}'
