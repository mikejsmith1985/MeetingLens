"""Unit tests for LauncherAdapter delegation, with OS calls monkeypatched (T013)."""

from __future__ import annotations

import pytest

from meetinglens.adapters import launcher as launcher_module
from meetinglens.adapters.launcher import LauncherAdapter

pytestmark = pytest.mark.unit


def test_open_url_uses_webbrowser(monkeypatch):
    opened = []
    monkeypatch.setattr(launcher_module.webbrowser, "open", lambda url: opened.append(url))
    LauncherAdapter().open_url("https://copilot.microsoft.com")
    assert opened == ["https://copilot.microsoft.com"]


def test_open_folder_uses_startfile(monkeypatch):
    started = []
    monkeypatch.setattr(launcher_module.os, "startfile", lambda path: started.append(path))
    LauncherAdapter().open_folder("C:/captures")
    assert started == ["C:/captures"]


def test_open_file_uses_startfile(monkeypatch):
    started = []
    monkeypatch.setattr(launcher_module.os, "startfile", lambda path: started.append(path))
    LauncherAdapter().open_file("C:/notes.txt")
    assert started == ["C:/notes.txt"]
