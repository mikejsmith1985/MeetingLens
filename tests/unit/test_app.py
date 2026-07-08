"""Unit tests for AppController hotkey routing across all user stories.

The fake adapters and the wiring harness live here (rather than a conftest) because this is
their only consumer. They record calls instead of touching the OS, so every test runs in
microseconds with no speech engine, screen, clipboard, or threads (Article V).
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

from meetinglens import messages
from meetinglens.app import AppController
from meetinglens.config import Config
from meetinglens.session import SessionState

pytestmark = pytest.mark.unit


class FakeSpeech:
    def __init__(self):
        self.said: list[str] = []

    def say(self, text):
        self.said.append(text)

    def stop(self):
        self.said.append("<stop>")


class FakeCapture:
    def __init__(self, succeed=True):
        self.succeed = succeed
        self.paths: list[str] = []

    def capture(self, path):
        self.paths.append(path)
        return self.succeed


class FakeClipboard:
    def __init__(self, text=""):
        self.text = text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text


class FakeLauncher:
    def __init__(self):
        self.urls: list[str] = []
        self.folders: list[str] = []
        self.files: list[str] = []

    def open_url(self, url):
        self.urls.append(url)

    def open_folder(self, path):
        self.folders.append(path)

    def open_file(self, path):
        self.files.append(path)


class FakeTray:
    def __init__(self):
        self.recording_states: list[bool] = []

    def set_recording(self, is_recording):
        self.recording_states.append(is_recording)


class FakeScheduler:
    def __init__(self):
        self.callback = None
        self.is_running = False

    def start(self, interval_seconds, callback):
        self.callback = callback
        self.is_running = True

    def stop(self):
        self.is_running = False

    def trigger(self):
        """Simulate one interval elapsing."""
        if self.callback is not None:
            self.callback()


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def monotonic(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


class ControllerHarness:
    """An AppController wired to fakes, with handles to inspect what it did."""

    def __init__(self, tmp_path):
        self.speech = FakeSpeech()
        self.capture = FakeCapture(succeed=True)
        self.clipboard = FakeClipboard()
        self.launcher = FakeLauncher()
        self.tray = FakeTray()
        self.scheduler = FakeScheduler()
        self.clock = FakeClock()
        self.config = Config(interval_seconds=45)
        self.quit_calls: list[bool] = []
        self.controller = AppController(
            config=self.config,
            speech=self.speech,
            capture=self.capture,
            clipboard=self.clipboard,
            launcher=self.launcher,
            tray=self.tray,
            scheduler=self.scheduler,
            captures_folder=str(tmp_path / "captures"),
            notes_folder=str(tmp_path / "notes"),
            now_fn=self.clock.monotonic,
            clock_fn=lambda: datetime(2026, 7, 8, 14, 30, 0),
        )
        self.controller.set_quit_callback(lambda: self.quit_calls.append(True))


@pytest.fixture
def harness(tmp_path) -> ControllerHarness:
    return ControllerHarness(tmp_path)


# ----- US1: capture ------------------------------------------------------------------


def test_start_begins_session_and_speaks(harness):
    harness.controller.on_start()
    assert harness.controller._session.is_recording
    assert harness.speech.said == [messages.started()]
    assert harness.tray.recording_states == [True]
    assert harness.scheduler.is_running


def test_start_creates_captures_folder(harness):
    harness.controller.on_start()
    assert os.path.isdir(harness.controller._captures_folder)


def test_start_while_recording_warns_and_keeps_count(harness):
    harness.controller.on_start()
    harness.scheduler.trigger()  # one screenshot
    harness.controller.on_start()
    assert harness.speech.said[-1] == messages.already_recording(1)
    assert harness.controller._session.screenshot_count == 1


def test_capture_tick_counts_and_announces_on_success(harness):
    harness.controller.on_start()
    harness.scheduler.trigger()
    harness.scheduler.trigger()
    assert harness.speech.said[-1] == messages.capture_taken(2)
    assert len(harness.capture.paths) == 2


def test_capture_tick_skips_frame_on_failure(harness):
    harness.capture.succeed = False
    harness.controller.on_start()
    harness.scheduler.trigger()
    assert harness.controller._session.screenshot_count == 0
    assert messages.capture_taken(1) not in harness.speech.said


def test_stop_when_idle_speaks_nothing_recording(harness):
    harness.controller.on_stop()
    assert harness.speech.said == [messages.nothing_recording()]


# ----- US2: handoff ------------------------------------------------------------------


def test_stop_runs_handoff(harness):
    harness.controller.on_start()
    harness.scheduler.trigger()
    harness.controller.on_stop()
    assert harness.speech.said[-3] == messages.stopping(1)
    assert harness.speech.said[-2] == messages.handoff_open()
    assert harness.speech.said[-1] == messages.handoff_ready()
    assert harness.launcher.urls == [harness.config.ai_chat_url]
    assert harness.launcher.folders == [harness.controller._captures_folder]
    assert "1 screenshot " in harness.clipboard.text
    assert not harness.scheduler.is_running


# ----- US3: save notes ---------------------------------------------------------------


def test_save_writes_notes_and_opens(harness):
    harness.clipboard.text = "Slide 1: Roadmap"
    harness.controller.on_save()
    assert harness.speech.said[-1] == messages.notes_saved()
    assert len(harness.launcher.files) == 1
    assert os.path.isfile(harness.launcher.files[0])


def test_save_empty_clipboard(harness):
    harness.clipboard.text = ""
    harness.controller.on_save()
    assert harness.speech.said == [messages.nothing_to_save()]
    assert harness.launcher.files == []


def test_save_refuses_to_save_our_prompt(harness):
    # After a handoff, the clipboard still holds the prompt we placed there (FR-027 / I1).
    harness.controller.on_start()
    harness.scheduler.trigger()
    harness.controller.on_stop()
    said_before = len(harness.speech.said)
    harness.controller.on_save()
    assert harness.speech.said[said_before:] == [messages.prompt_not_copied()]
    assert harness.launcher.files == []


# ----- US4: status -------------------------------------------------------------------


def test_status_idle(harness):
    harness.controller.on_status()
    assert harness.speech.said == [messages.status_idle()]


def test_status_recording_reports_count_and_minutes(harness):
    harness.controller.on_start()
    harness.scheduler.trigger()
    harness.clock.advance(130)  # 2 minutes
    harness.controller.on_status()
    assert harness.speech.said[-1] == messages.status_recording(1, 2)


# ----- lifecycle: quit + ready -------------------------------------------------------


def test_quit_stops_session_speaks_and_tears_down(harness):
    harness.controller.on_start()
    harness.controller.on_quit()
    assert harness.controller._session.state == SessionState.IDLE
    assert not harness.scheduler.is_running
    assert harness.speech.said[-1] == messages.quitting()
    assert harness.quit_calls == [True]


def test_announce_ready_names_start_and_stop(harness):
    harness.controller.announce_ready()
    ready = harness.speech.said[-1]
    assert "Control Alt S" in ready
    assert "Control Alt X" in ready


def test_announce_config_warnings(harness):
    harness.config.warnings.append("interval_seconds")
    harness.controller.announce_config_warnings()
    assert harness.speech.said == [messages.config_warning("interval_seconds")]
