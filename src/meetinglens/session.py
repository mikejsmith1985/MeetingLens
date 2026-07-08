"""Capture-session state machine: what MeetingLens is doing right now.

This is a pure state object — it counts screenshots and tracks timing but does not touch
the screen, threads, or the clock directly (time is injected). Keeping it pure means the
whole start/record/stop lifecycle is unit-testable in microseconds (Article V).
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

_SECONDS_PER_MINUTE = 60


class SessionState(Enum):
    """Whether a capture session is currently running."""

    IDLE = "idle"
    RECORDING = "recording"


class CaptureSession:
    """Tracks recording state, the running screenshot count, and elapsed time."""

    def __init__(self, now_fn: Callable[[], float]) -> None:
        """Create an idle session; ``now_fn`` supplies monotonic seconds for timing."""
        self._now_fn = now_fn
        self.state = SessionState.IDLE
        self.screenshot_count = 0
        self.started_at: float | None = None
        self.interval_seconds = 0

    @property
    def is_recording(self) -> bool:
        """Return whether a session is currently active."""
        return self.state == SessionState.RECORDING

    def start(self, interval_seconds: int) -> None:
        """Begin a fresh session, resetting the count and start time."""
        self.state = SessionState.RECORDING
        self.screenshot_count = 0
        self.started_at = self._now_fn()
        self.interval_seconds = interval_seconds

    def note_capture(self) -> int:
        """Record one successful screenshot and return the new running total.

        Only successful captures advance the count, so a skipped frame (locked screen,
        sleeping display) never inflates the number spoken to the user (FR-025).
        """
        self.screenshot_count += 1
        return self.screenshot_count

    def stop(self) -> int:
        """End the session and return the final screenshot count."""
        self.state = SessionState.IDLE
        return self.screenshot_count

    def elapsed_minutes(self) -> int:
        """Return whole minutes since the session started (0 when idle)."""
        if self.started_at is None:
            return 0
        return int((self._now_fn() - self.started_at) // _SECONDS_PER_MINUTE)
