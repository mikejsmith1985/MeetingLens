"""Unit tests for notes save policy and file writing (T032, FR-021, FR-027)."""

from __future__ import annotations

from datetime import datetime

import pytest

from meetinglens import notes

pytestmark = pytest.mark.unit


def test_decide_save_empty_clipboard():
    assert notes.decide_save("", None) is notes.SaveDecision.EMPTY
    assert notes.decide_save("   ", None) is notes.SaveDecision.EMPTY
    assert notes.decide_save(None, None) is notes.SaveDecision.EMPTY


def test_decide_save_still_holds_prompt():
    prompt = "I'm attaching 18 screenshots ..."
    assert notes.decide_save(prompt, prompt) is notes.SaveDecision.STILL_PROMPT


def test_decide_save_real_response():
    assert notes.decide_save("Slide 1: Roadmap", "the prompt") is notes.SaveDecision.SAVE


def test_build_notes_filename_is_timestamped():
    name = notes.build_notes_filename(datetime(2026, 7, 8, 14, 30, 0))
    assert name == "MeetingNotes_2026-07-08_14-30.txt"


def test_write_notes_creates_folder_and_file(tmp_path):
    target = tmp_path / "sub" / "notes"
    path = notes.write_notes("hello notes", str(target), datetime(2026, 7, 8, 9, 5, 0))
    assert path.endswith("MeetingNotes_2026-07-08_09-05.txt")
    with open(path, encoding="utf-8") as handle:
        assert handle.read() == "hello notes"
