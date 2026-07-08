"""Integration test: clipboard text is saved to a real notes file on disk (T035)."""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime

import pytest

from meetinglens import notes

pytestmark = pytest.mark.integration


@pytest.mark.skipif(importlib.util.find_spec("pyperclip") is None, reason="pyperclip not installed")
def test_clipboard_text_written_to_notes_file(tmp_path):
    from meetinglens.adapters.clipboard import ClipboardAdapter

    clip = ClipboardAdapter()
    try:
        clip.set_text("Slide 1: Roadmap\nSlide 2: Timeline")
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"no clipboard backend: {exc}")

    text = clip.get_text()
    decision = notes.decide_save(text, last_handoff_prompt=None)
    assert decision is notes.SaveDecision.SAVE

    path = notes.write_notes(text, str(tmp_path), datetime(2026, 7, 8, 10, 15, 0))
    assert os.path.isfile(path)
    with open(path, encoding="utf-8") as handle:
        assert "Slide 1: Roadmap" in handle.read()
