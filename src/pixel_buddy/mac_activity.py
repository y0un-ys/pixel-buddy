"""macOS input activity metadata; no key values or event contents are read."""
import time
from importlib import import_module
from typing import Protocol, cast


class _QuartzEvents(Protocol):
    """PyObjC exports these public symbols dynamically, without Python stubs."""
    kCGEventSourceStateCombinedSessionState: int
    kCGEventKeyDown: int
    kCGEventMouseMoved: int
    kCGEventLeftMouseDown: int
    kCGEventRightMouseDown: int
    kCGEventOtherMouseDown: int
    kCGEventLeftMouseDragged: int
    kCGEventRightMouseDragged: int
    kCGEventOtherMouseDragged: int
    kCGEventScrollWheel: int

    def CGEventSourceCounterForEventType(self, state: int, event: int) -> int: ...
    def CGEventSourceSecondsSinceLastEventType(self, state: int, event: int) -> float: ...


class MacActivitySource:
    def __init__(self):
        # PyObjC resolves these documented exports via module __getattr__.
        # A static ModuleType cannot describe its native symbols.
        Quartz = cast(_QuartzEvents, cast(object, import_module('Quartz')))
        self._quartz = Quartz
        self._state = Quartz.kCGEventSourceStateCombinedSessionState
        self._key = Quartz.kCGEventKeyDown
        self._mouse = (
            Quartz.kCGEventMouseMoved, Quartz.kCGEventLeftMouseDown,
            Quartz.kCGEventRightMouseDown, Quartz.kCGEventOtherMouseDown,
            Quartz.kCGEventLeftMouseDragged, Quartz.kCGEventRightMouseDragged,
            Quartz.kCGEventOtherMouseDragged, Quartz.kCGEventScrollWheel,
        )
        self._counts = {
            event: Quartz.CGEventSourceCounterForEventType(self._state, event)
            for event in (self._key, *self._mouse)
        }

    def sample(self) -> tuple[float | None, float | None]:
        now = time.monotonic()
        key_time = mouse_time = None
        for event, previous in self._counts.items():
            count = self._quartz.CGEventSourceCounterForEventType(self._state, event)
            self._counts[event] = count
            if count <= previous:
                continue
            age = self._quartz.CGEventSourceSecondsSinceLastEventType(self._state, event)
            if not 0 <= age <= now:
                continue
            observed = now - age
            if event == self._key:
                key_time = observed
            else:
                mouse_time = max(mouse_time if mouse_time is not None else observed, observed)
        return key_time, mouse_time
