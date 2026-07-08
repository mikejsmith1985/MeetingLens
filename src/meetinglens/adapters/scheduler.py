"""Repeating-interval scheduler that fires the capture callback on its own thread.

Kept separate from the controller so the capture cadence runs off the main (tray/hotkey)
thread and stays accurate under load (SC-004). Uses only the standard library.
"""

from __future__ import annotations

import threading
from collections.abc import Callable


class RepeatingTimer:
    """Calls a callback every ``interval`` seconds until stopped."""

    def __init__(self) -> None:
        """Create an unstarted timer."""
        self._timer: threading.Timer | None = None
        self._interval = 0
        self._callback: Callable[[], None] | None = None
        self._is_running = False

    def start(self, interval_seconds: int, callback: Callable[[], None]) -> None:
        """Begin firing ``callback`` every ``interval_seconds`` seconds."""
        self._interval = interval_seconds
        self._callback = callback
        self._is_running = True
        self._schedule_next()

    def stop(self) -> None:
        """Stop firing; any pending timer is cancelled."""
        self._is_running = False
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _schedule_next(self) -> None:
        """Arm the next single-shot timer if still running."""
        if not self._is_running:
            return
        self._timer = threading.Timer(self._interval, self._fire)
        self._timer.daemon = True
        self._timer.start()

    def _fire(self) -> None:
        """Run the callback then re-arm, so captures keep coming at a steady cadence."""
        if not self._is_running or self._callback is None:
            return
        self._callback()
        self._schedule_next()
