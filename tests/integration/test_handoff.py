"""Integration test: the handoff prompt round-trips through the real clipboard (T031)."""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration


class _RecordingLauncher:
    def __init__(self):
        self.urls = []
        self.folders = []

    def open_url(self, url):
        self.urls.append(url)

    def open_folder(self, path):
        self.folders.append(path)


@pytest.mark.skipif(importlib.util.find_spec("pyperclip") is None, reason="pyperclip not installed")
def test_prompt_lands_on_real_clipboard():
    from meetinglens.adapters.clipboard import ClipboardAdapter
    from meetinglens.handoff import run_handoff

    clip = ClipboardAdapter()
    launcher = _RecordingLauncher()
    try:
        prompt = run_handoff(
            count=7,
            interval_seconds=45,
            ai_chat_url="https://copilot.microsoft.com",
            captures_folder="C:/captures",
            clipboard=clip,
            launcher=launcher,
            speak=lambda _text: None,
            handoff_open_message="open",
            handoff_ready_message="ready",
        )
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"no clipboard backend: {exc}")

    assert clip.get_text() == prompt
    assert "7" in prompt and "45" in prompt
    assert launcher.urls == ["https://copilot.microsoft.com"]
