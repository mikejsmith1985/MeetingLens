"""Decides and performs saving clipboard text as timestamped meeting notes.

Two concerns live here, both kept free of clipboard/OS libraries so they unit-test fast:
  * ``decide_save`` — pure policy: is this clipboard text worth saving, or is it empty or
    still our own handoff prompt (FR-021, FR-027)?
  * ``write_notes`` — writes the text to a timestamped file and returns its path.
Opening Notepad and reading the clipboard are adapter concerns handled by the caller.
"""

from __future__ import annotations

import os
from datetime import datetime
from enum import Enum

_NOTES_PREFIX = "MeetingNotes"
_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M"


class SaveDecision(Enum):
    """The outcome of inspecting the clipboard before saving notes."""

    SAVE = "save"
    EMPTY = "empty"
    STILL_PROMPT = "still_prompt"


def decide_save(clipboard_text: str | None, last_handoff_prompt: str | None) -> SaveDecision:
    """Return whether the clipboard should be saved, is empty, or still holds our prompt.

    After a handoff the clipboard contains the prompt we placed there, so pressing save
    before copying Copilot's reply must NOT write the prompt out as meeting notes (FR-027).
    """
    if clipboard_text is None or not clipboard_text.strip():
        return SaveDecision.EMPTY
    if last_handoff_prompt is not None and clipboard_text == last_handoff_prompt:
        return SaveDecision.STILL_PROMPT
    return SaveDecision.SAVE


def build_notes_filename(now: datetime) -> str:
    """Return a timestamped notes filename so repeated saves never overwrite each other."""
    return f"{_NOTES_PREFIX}_{now.strftime(_TIMESTAMP_FORMAT)}.txt"


def write_notes(text: str, notes_folder: str, now: datetime) -> str:
    """Write ``text`` to a timestamped file in ``notes_folder`` and return the full path.

    The folder is created if missing so a fresh machine never fails the save (FR-024).
    """
    os.makedirs(notes_folder, exist_ok=True)
    path = os.path.join(notes_folder, build_notes_filename(now))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path
