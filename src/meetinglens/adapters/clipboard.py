"""Clipboard adapter over pyperclip for reading responses and writing the handoff prompt."""

from __future__ import annotations

import pyperclip


class ClipboardAdapter:
    """Reads and writes plain text on the system clipboard."""

    def get_text(self) -> str:
        """Return the current clipboard text, or an empty string if it holds no text."""
        try:
            return pyperclip.paste() or ""
        except Exception:
            return ""

    def set_text(self, text: str) -> None:
        """Place ``text`` on the clipboard, ready for the user to paste into Copilot."""
        pyperclip.copy(text)
