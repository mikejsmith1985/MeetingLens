"""Unit tests for status and readiness message wording (T036, T040, FR-004/013/014)."""

from __future__ import annotations

import pytest

from meetinglens import messages

pytestmark = pytest.mark.unit


def test_status_recording_includes_count_and_minutes():
    text = messages.status_recording(12, 9)
    assert "12" in text
    assert "9" in text
    assert "Recording" in text


def test_status_idle_prompts_to_start():
    assert "Not recording" in messages.status_idle()


def test_ready_names_start_and_stop_hotkeys():
    ready = messages.ready()
    assert "Control Alt S" in ready
    assert "Control Alt X" in ready


def test_quit_message_present():
    assert "closing" in messages.quitting().lower()


def test_prompt_not_copied_guides_user():
    assert "Control Alt W" in messages.prompt_not_copied()
