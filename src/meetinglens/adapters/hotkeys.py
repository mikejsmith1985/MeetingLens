"""Global hotkey adapter over the ``keyboard`` library.

Hotkeys are registered system-wide so they fire even when Teams, Zoom, or a browser has
focus (FR-005). Registration that fails (a chord already claimed by another app) is reported
back so the caller can speak a warning rather than starting in a silently broken state (FR-007).
"""

from __future__ import annotations

from collections.abc import Callable

import keyboard


class HotkeyAdapter:
    """Registers global hotkey chords and blocks the main thread until exit."""

    def register(self, chord: str, callback: Callable[[], None]) -> bool:
        """Bind ``chord`` to ``callback`` globally; return whether registration succeeded."""
        try:
            keyboard.add_hotkey(chord, callback)
            return True
        except Exception:
            return False

    def wait(self) -> None:
        """Block the calling thread, keeping hotkeys live until the process exits."""
        keyboard.wait()

    def clear(self) -> None:
        """Remove all registered hotkeys (used during shutdown)."""
        keyboard.unhook_all_hotkeys()
