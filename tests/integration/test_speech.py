"""Integration test for the real speech adapter (T008, T047 support).

The key guarantee: the worker thread initialises the SAPI (COM) engine successfully. This is
a regression guard for the CoInitialize bug — without it, every spoken message fails silently
and an audio-first tool is useless.
"""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(importlib.util.find_spec("pyttsx3") is None, reason="pyttsx3 not installed")
def test_speech_engine_initialises_on_worker_thread():
    from meetinglens.adapters.speech import SpeechAdapter

    speech = SpeechAdapter()
    started = speech.started_ok(timeout=5.0)
    speech.say("integration probe")
    speech.stop()
    if not started:  # pragma: no cover - genuinely no installed voice on this host
        pytest.skip("no SAPI voice available on this host")
    assert started is True
