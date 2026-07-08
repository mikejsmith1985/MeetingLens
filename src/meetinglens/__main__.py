"""Entry point: load config, wire the real adapters, register hotkeys, and run.

This is the only module that constructs the OS-touching adapters and injects them into the
controller. It resolves folder paths, registers the five global hotkeys (announcing any that
fail), speaks the readiness message, and hands control to the tray loop (FR-004, FR-005, FR-028).
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime

# Absolute imports (not relative) so this module also works as PyInstaller's top-level
# entry script, where there is no parent package for a relative import to resolve against.
from meetinglens import config as config_module
from meetinglens.adapters.capture import ScreenCaptureAdapter
from meetinglens.adapters.clipboard import ClipboardAdapter
from meetinglens.adapters.hotkeys import HotkeyAdapter
from meetinglens.adapters.launcher import LauncherAdapter
from meetinglens.adapters.scheduler import RepeatingTimer
from meetinglens.adapters.speech import SpeechAdapter
from meetinglens.adapters.tray import TrayAdapter
from meetinglens.app import AppController

_CONFIG_FILENAME = "config.txt"


def _config_path() -> str:
    """Return the path to config.txt sitting next to the installed application.

    In a PyInstaller folder-drop the config ships beside the executable, so resolve
    against the exe directory when frozen and against this file otherwise.
    """
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, _CONFIG_FILENAME)


def _desktop() -> str:
    """Return the current user's Desktop folder."""
    return os.path.join(os.path.expanduser("~"), "Desktop")


def _resolve_folder(configured: str, default: str) -> str:
    """Return the configured folder if set, otherwise the Desktop-based default."""
    return configured if configured else default


def main() -> None:
    """Start MeetingLens: wire everything together and run until the user quits."""
    config_path = _config_path()
    if getattr(sys, "frozen", False):
        # A lone downloaded exe writes its own editable config beside itself on first run.
        config_module.ensure_config_file(config_path)
    config = config_module.load_config(config_path)
    captures_folder = _resolve_folder(
        config.captures_folder, os.path.join(_desktop(), "MeetingCaptures")
    )
    notes_folder = _resolve_folder(config.notes_folder, _desktop())

    speech = SpeechAdapter()
    hotkeys = HotkeyAdapter()

    # The tray's Exit item and the controller reference each other; bind the exit callback
    # late through a small holder so neither has to be constructed twice.
    exit_callback: dict[str, object] = {"fn": lambda: None}
    tray = TrayAdapter(on_exit=lambda: exit_callback["fn"]())

    controller = AppController(
        config=config,
        speech=speech,
        capture=ScreenCaptureAdapter(),
        clipboard=ClipboardAdapter(),
        launcher=LauncherAdapter(),
        tray=tray,
        scheduler=RepeatingTimer(),
        captures_folder=captures_folder,
        notes_folder=notes_folder,
        now_fn=time.monotonic,
        clock_fn=datetime.now,
    )
    exit_callback["fn"] = controller.on_quit

    def shutdown() -> None:
        """Tear down hotkeys, speech, and the tray so the process can exit cleanly."""
        hotkeys.clear()
        speech.stop()
        tray.stop()

    controller.set_quit_callback(shutdown)

    _register_hotkeys(hotkeys, config, controller, speech)
    controller.announce_config_warnings()
    controller.announce_ready()
    tray.run()


def _register_hotkeys(hotkeys, config, controller, speech) -> None:
    """Register all five global hotkeys, speaking a warning for any that fail (FR-007)."""
    bindings = [
        (config.hotkey_start, controller.on_start, "start"),
        (config.hotkey_stop, controller.on_stop, "stop"),
        (config.hotkey_status, controller.on_status, "status"),
        (config.hotkey_save, controller.on_save, "save"),
        (config.hotkey_quit, controller.on_quit, "quit"),
    ]
    for chord, callback, action in bindings:
        if not hotkeys.register(chord, callback):
            from meetinglens import messages

            speech.say(messages.hotkey_failed(action))


if __name__ == "__main__":
    main()
