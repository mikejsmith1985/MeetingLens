"""Orchestrates the stop-and-summarise handoff to Copilot.

On stop, the user needs everything lined up: the prompt on the clipboard, the AI chat page
open in the browser, and the captures folder open to attach from. This module sequences
those steps through injected adapters and returns the prompt it placed on the clipboard so
the controller can later detect that prompt still sitting there (FR-016, FR-017, FR-027).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from .prompt import build_summarisation_prompt


class _Clipboard(Protocol):
    """Minimal clipboard capability the handoff needs."""

    def set_text(self, text: str) -> None: ...


class _Launcher(Protocol):
    """Minimal launcher capability the handoff needs."""

    def open_url(self, url: str) -> None: ...
    def open_folder(self, path: str) -> None: ...


def run_handoff(
    count: int,
    interval_seconds: int,
    ai_chat_url: str,
    captures_folder: str,
    clipboard: _Clipboard,
    launcher: _Launcher,
    speak: Callable[[str], None],
    handoff_open_message: str,
    handoff_ready_message: str,
) -> str:
    """Prepare the summary handoff and return the prompt placed on the clipboard.

    The prompt is copied first, then the browser and folder are opened, then the two
    guidance messages are spoken in order so the user hears them after the windows appear.
    """
    prompt = build_summarisation_prompt(count, interval_seconds)
    clipboard.set_text(prompt)
    launcher.open_url(ai_chat_url)
    launcher.open_folder(captures_folder)
    speak(handoff_open_message)
    speak(handoff_ready_message)
    return prompt
