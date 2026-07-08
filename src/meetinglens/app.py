"""AppController: the brain that turns hotkey presses into spoken, stateful actions.

It owns the capture session and coordinates the injected adapters (speech, capture,
clipboard, launcher, tray, scheduler). Adapters are passed in rather than imported, so the
whole controller is unit-testable with fakes in well under 10ms (Article V). All OS-specific
work lives behind those adapters.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from datetime import datetime

from . import messages, notes
from .handoff import run_handoff
from .session import CaptureSession

_CAPTURE_FILENAME_FORMAT = "capture_{index:03d}.png"


class AppController:
    """Routes the five hotkey actions to session logic and spoken feedback."""

    def __init__(
        self,
        config,
        speech,
        capture,
        clipboard,
        launcher,
        tray,
        scheduler,
        captures_folder: str,
        notes_folder: str,
        now_fn: Callable[[], float],
        clock_fn: Callable[[], datetime],
    ) -> None:
        """Wire the controller to its already-constructed adapters and folders."""
        self._config = config
        self._speech = speech
        self._capture = capture
        self._clipboard = clipboard
        self._launcher = launcher
        self._tray = tray
        self._scheduler = scheduler
        self._captures_folder = captures_folder
        self._notes_folder = notes_folder
        self._clock_fn = clock_fn
        self._session = CaptureSession(now_fn)
        self._last_handoff_prompt: str | None = None
        self._on_quit: Callable[[], None] | None = None

    # ----- lifecycle -----------------------------------------------------------------

    def announce_ready(self) -> None:
        """Speak the first-run readiness message naming the start and stop hotkeys (FR-004)."""
        self._speech.say(messages.ready())

    def announce_config_warnings(self) -> None:
        """Speak one warning per config value that fell back to a default (FR-023)."""
        for setting in self._config.warnings:
            self._speech.say(messages.config_warning(setting))

    def set_quit_callback(self, on_quit: Callable[[], None]) -> None:
        """Register the function that actually tears down the process on quit."""
        self._on_quit = on_quit

    # ----- hotkey actions ------------------------------------------------------------

    def on_start(self) -> None:
        """Start a capture session, or announce we are already recording (FR-008, FR-012)."""
        if self._session.is_recording:
            self._speech.say(messages.already_recording(self._session.screenshot_count))
            return
        os.makedirs(self._captures_folder, exist_ok=True)
        self._session.start(self._config.interval_seconds)
        self._tray.set_recording(True)
        self._speech.say(messages.started())
        self._scheduler.start(self._config.interval_seconds, self.on_capture_tick)

    def on_capture_tick(self) -> None:
        """Capture the screen once; count and announce it only if the capture succeeded."""
        if not self._session.is_recording:
            return
        index = self._session.screenshot_count + 1
        path = os.path.join(self._captures_folder, _CAPTURE_FILENAME_FORMAT.format(index=index))
        if not self._capture.capture(path):
            return  # Skipped frame (locked screen / display asleep) — session continues (FR-025).
        count = self._session.note_capture()
        self._speech.say(messages.capture_taken(count))

    def on_stop(self) -> None:
        """Stop capture and launch the summary handoff (FR-015–FR-018)."""
        if not self._session.is_recording:
            self._speech.say(messages.nothing_recording())
            return
        self._scheduler.stop()
        count = self._session.stop()
        self._tray.set_recording(False)
        self._speech.say(messages.stopping(count))
        self._last_handoff_prompt = run_handoff(
            count=count,
            interval_seconds=self._config.interval_seconds,
            ai_chat_url=self._config.ai_chat_url,
            captures_folder=self._captures_folder,
            clipboard=self._clipboard,
            launcher=self._launcher,
            speak=self._speech.say,
            handoff_open_message=messages.handoff_open(),
            handoff_ready_message=messages.handoff_ready(),
        )

    def on_status(self) -> None:
        """Speak the current recording state, count, and elapsed time (FR-013, FR-014)."""
        if self._session.is_recording:
            self._speech.say(
                messages.status_recording(
                    self._session.screenshot_count, self._session.elapsed_minutes()
                )
            )
        else:
            self._speech.say(messages.status_idle())

    def on_save(self) -> None:
        """Save clipboard as notes, guarding empty and our-own-prompt cases (FR-021, FR-027)."""
        clipboard_text = self._clipboard.get_text()
        decision = notes.decide_save(clipboard_text, self._last_handoff_prompt)
        if decision is notes.SaveDecision.EMPTY:
            self._speech.say(messages.nothing_to_save())
            return
        if decision is notes.SaveDecision.STILL_PROMPT:
            self._speech.say(messages.prompt_not_copied())
            return
        path = notes.write_notes(clipboard_text, self._notes_folder, self._clock_fn())
        self._launcher.open_file(path)
        self._speech.say(messages.notes_saved())

    def on_quit(self) -> None:
        """Stop any session, speak goodbye, and tear down the process (FR-028)."""
        if self._session.is_recording:
            self._scheduler.stop()
            self._session.stop()
        self._speech.say(messages.quitting())
        if self._on_quit is not None:
            self._on_quit()
