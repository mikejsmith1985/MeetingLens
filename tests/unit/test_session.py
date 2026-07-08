"""Unit tests for the CaptureSession state machine (T019)."""

from __future__ import annotations

import pytest

from meetinglens.session import CaptureSession, SessionState

pytestmark = pytest.mark.unit


class _Clock:
    def __init__(self):
        self.value = 100.0

    def now(self):
        return self.value


def test_starts_idle():
    session = CaptureSession(_Clock().now)
    assert session.state == SessionState.IDLE
    assert not session.is_recording
    assert session.screenshot_count == 0


def test_start_sets_recording_and_resets_count():
    clock = _Clock()
    session = CaptureSession(clock.now)
    session.note_capture()  # leftover from an imagined prior run
    session.start(45)
    assert session.is_recording
    assert session.screenshot_count == 0
    assert session.interval_seconds == 45
    assert session.started_at == 100.0


def test_note_capture_increments_and_returns_total():
    session = CaptureSession(_Clock().now)
    session.start(45)
    assert session.note_capture() == 1
    assert session.note_capture() == 2
    assert session.screenshot_count == 2


def test_stop_returns_final_count_and_goes_idle():
    session = CaptureSession(_Clock().now)
    session.start(45)
    session.note_capture()
    assert session.stop() == 1
    assert session.state == SessionState.IDLE


def test_elapsed_minutes_uses_injected_clock():
    clock = _Clock()
    session = CaptureSession(clock.now)
    session.start(45)
    clock.value += 130  # 2 minutes 10 seconds
    assert session.elapsed_minutes() == 2


def test_elapsed_minutes_zero_when_idle():
    session = CaptureSession(_Clock().now)
    assert session.elapsed_minutes() == 0
