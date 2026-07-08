"""System-tray indicator adapter over pystray.

The tray icon is a purely visual cue for sighted bystanders — recording versus idle — and a
mouse-optional Exit item. No tray interaction is ever required for the core keyboard flow
(FR-001, FR-002); quitting is also available on the quit hotkey.
"""

from __future__ import annotations

from collections.abc import Callable

import pystray
from PIL import Image

_ICON_SIZE = 64
_IDLE_COLOR = (90, 90, 90)
_RECORDING_COLOR = (200, 40, 40)


def _solid_icon(color: tuple[int, int, int]) -> Image.Image:
    """Return a simple solid-colour square icon in the given colour."""
    return Image.new("RGB", (_ICON_SIZE, _ICON_SIZE), color)


class TrayAdapter:
    """Shows a recording/idle tray icon and an Exit menu item."""

    def __init__(self, on_exit: Callable[[], None]) -> None:
        """Build the tray icon; ``on_exit`` is invoked when the user clicks Exit."""
        self._icon = pystray.Icon(
            "MeetingLens",
            _solid_icon(_IDLE_COLOR),
            "MeetingLens (idle)",
            menu=pystray.Menu(pystray.MenuItem("Exit", lambda _icon, _item: on_exit())),
        )

    def set_recording(self, is_recording: bool) -> None:
        """Update the icon colour and tooltip to reflect the recording state."""
        self._icon.icon = _solid_icon(_RECORDING_COLOR if is_recording else _IDLE_COLOR)
        self._icon.title = "MeetingLens (recording)" if is_recording else "MeetingLens (idle)"

    def run(self) -> None:
        """Run the tray event loop (blocks; call on the main thread)."""
        self._icon.run()

    def stop(self) -> None:
        """Remove the tray icon during shutdown."""
        self._icon.stop()
