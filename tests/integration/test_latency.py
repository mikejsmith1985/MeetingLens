"""Verification test for SC-002: speech is enqueued far faster than the 2-second budget (T047).

The guarantee is that a state-change message never blocks the caller: ``say`` must return
almost immediately because the actual speaking happens on a worker thread.
"""

from __future__ import annotations

import importlib.util
import time

import pytest

pytestmark = pytest.mark.integration

_LATENCY_BUDGET_SECONDS = 2.0


@pytest.mark.skipif(importlib.util.find_spec("pyttsx3") is None, reason="pyttsx3 not installed")
def test_say_returns_within_budget():
    from meetinglens.adapters.speech import SpeechAdapter

    try:
        speech = SpeechAdapter()
    except Exception as exc:  # pragma: no cover - no SAPI voice
        pytest.skip(f"no speech engine: {exc}")

    worst = 0.0
    for index in range(10):
        start = time.perf_counter()
        speech.say(f"message {index}")
        worst = max(worst, time.perf_counter() - start)
    speech.stop()
    assert worst < _LATENCY_BUDGET_SECONDS
