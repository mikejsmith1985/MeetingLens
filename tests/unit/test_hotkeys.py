"""Unit tests for HotkeyAdapter registration success/failure reporting (T010, FR-007)."""

from __future__ import annotations

import pytest

from meetinglens.adapters import hotkeys as hotkeys_module
from meetinglens.adapters.hotkeys import HotkeyAdapter

pytestmark = pytest.mark.unit


def test_register_returns_true_on_success(monkeypatch):
    registered = []
    monkeypatch.setattr(
        hotkeys_module.keyboard,
        "add_hotkey",
        lambda chord, callback: registered.append((chord, callback)),
    )
    assert HotkeyAdapter().register("ctrl+alt+s", lambda: None) is True
    assert registered[0][0] == "ctrl+alt+s"


def test_register_returns_false_when_registration_raises(monkeypatch):
    def _boom(chord, callback):
        raise ValueError("hotkey already claimed")

    monkeypatch.setattr(hotkeys_module.keyboard, "add_hotkey", _boom)
    assert HotkeyAdapter().register("ctrl+alt+s", lambda: None) is False
