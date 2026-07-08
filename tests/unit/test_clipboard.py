"""Unit tests for ClipboardAdapter delegation and empty-handling (T011)."""

from __future__ import annotations

import pytest

from meetinglens.adapters import clipboard as clipboard_module
from meetinglens.adapters.clipboard import ClipboardAdapter

pytestmark = pytest.mark.unit


def test_get_text_returns_clipboard_contents(monkeypatch):
    monkeypatch.setattr(clipboard_module.pyperclip, "paste", lambda: "hello")
    assert ClipboardAdapter().get_text() == "hello"


def test_get_text_returns_empty_when_none(monkeypatch):
    monkeypatch.setattr(clipboard_module.pyperclip, "paste", lambda: None)
    assert ClipboardAdapter().get_text() == ""


def test_get_text_returns_empty_on_error(monkeypatch):
    def _boom():
        raise RuntimeError("no clipboard backend")

    monkeypatch.setattr(clipboard_module.pyperclip, "paste", _boom)
    assert ClipboardAdapter().get_text() == ""


def test_set_text_delegates(monkeypatch):
    copied = []
    monkeypatch.setattr(clipboard_module.pyperclip, "copy", lambda text: copied.append(text))
    ClipboardAdapter().set_text("prompt text")
    assert copied == ["prompt text"]
