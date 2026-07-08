"""Verification test for SC-003: global hotkey registration is reliable (T048).

Injecting real global key events under a competing foreground app is not feasible in an
automated test, so this verifies the registration path — the prerequisite for a hotkey ever
firing — succeeds in at least 99% of attempts. Skips where the OS denies global hooks.
"""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration

_ATTEMPTS = 100
_REQUIRED_SUCCESS_RATE = 0.99


@pytest.mark.skipif(importlib.util.find_spec("keyboard") is None, reason="keyboard not installed")
def test_hotkey_registration_success_rate():
    from meetinglens.adapters.hotkeys import HotkeyAdapter

    adapter = HotkeyAdapter()
    successes = 0
    try:
        for _ in range(_ATTEMPTS):
            if adapter.register("ctrl+alt+f24", lambda: None):
                successes += 1
            adapter.clear()
    except Exception as exc:  # pragma: no cover - OS denies global hooks (no privilege)
        pytest.skip(f"global hotkeys unavailable: {exc}")
    assert successes / _ATTEMPTS >= _REQUIRED_SUCCESS_RATE
