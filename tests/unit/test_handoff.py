"""Unit tests for the handoff orchestration sequence (T028, FR-016/017/027)."""

from __future__ import annotations

import pytest

from meetinglens.handoff import run_handoff

pytestmark = pytest.mark.unit


class _Clip:
    def __init__(self):
        self.text = None

    def set_text(self, text):
        self.text = text


class _Launch:
    def __init__(self):
        self.urls = []
        self.folders = []

    def open_url(self, url):
        self.urls.append(url)

    def open_folder(self, path):
        self.folders.append(path)


def test_handoff_sets_clipboard_opens_targets_and_speaks_in_order():
    clip, launch, spoken = _Clip(), _Launch(), []
    returned = run_handoff(
        count=18,
        interval_seconds=45,
        ai_chat_url="https://copilot.microsoft.com",
        captures_folder="C:/captures",
        clipboard=clip,
        launcher=launch,
        speak=spoken.append,
        handoff_open_message="OPEN",
        handoff_ready_message="READY",
    )
    assert "18" in clip.text and "45" in clip.text
    assert launch.urls == ["https://copilot.microsoft.com"]
    assert launch.folders == ["C:/captures"]
    assert spoken == ["OPEN", "READY"]
    # The returned prompt must equal what was placed on the clipboard, for the save guard.
    assert returned == clip.text
