"""Unit tests for the RepeatingTimer scheduler logic without real waiting (T017 support).

Timing is not exercised here (that would be slow and flaky); instead the start/stop/re-arm
control logic is verified directly, which is where the bugs would live.
"""

from __future__ import annotations

import pytest

from meetinglens.adapters.scheduler import RepeatingTimer

pytestmark = pytest.mark.unit


def test_starts_and_stops_running_flag():
    timer = RepeatingTimer()
    calls = []
    timer.start(3600, lambda: calls.append(1))  # long interval so it never fires during the test
    assert timer._is_running is True
    timer.stop()
    assert timer._is_running is False


def test_stop_cancels_pending_timer():
    timer = RepeatingTimer()
    timer.start(3600, lambda: None)
    assert timer._timer is not None
    timer.stop()
    assert timer._timer is None


def test_fire_runs_callback_and_rearms_when_running():
    timer = RepeatingTimer()
    calls = []
    timer.start(3600, lambda: calls.append(1))
    first_timer = timer._timer
    timer._fire()
    assert calls == [1]
    # A new single-shot timer should have been armed for the next interval.
    assert timer._timer is not first_timer
    timer.stop()


def test_fire_does_nothing_after_stop():
    timer = RepeatingTimer()
    calls = []
    timer.start(3600, lambda: calls.append(1))
    timer.stop()
    timer._fire()
    assert calls == []
