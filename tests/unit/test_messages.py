"""Unit tests for the spoken-message catalog (T014, contracts/spoken-messages.md)."""

from __future__ import annotations

import pytest

from meetinglens import messages

pytestmark = pytest.mark.unit


def test_capture_taken_includes_count():
    assert messages.capture_taken(4) == "Screenshot 4 taken."


def test_started_announces_zero():
    assert "0 screenshots" in messages.started()


def test_already_recording_reports_count():
    assert "7" in messages.already_recording(7)


def test_stopping_includes_count():
    assert "18" in messages.stopping(18)


def test_config_warning_names_setting():
    assert "interval_seconds" in messages.config_warning("interval_seconds")


def test_hotkey_failed_names_action():
    assert "start" in messages.hotkey_failed("start")


def test_handoff_messages_are_non_empty():
    assert messages.handoff_open()
    assert messages.handoff_ready()
    assert messages.notes_saved()
    assert messages.nothing_to_save()
