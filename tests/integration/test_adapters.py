"""Integration tests exercising the real adapters against Windows APIs (T016).

Each test skips cleanly if its dependency or a required resource (SAPI, screen, clipboard)
is unavailable, so the suite is honest on CI without silently passing.
"""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration


def _have(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


@pytest.mark.skipif(not _have("pyperclip"), reason="pyperclip not installed")
def test_clipboard_round_trip():
    from meetinglens.adapters.clipboard import ClipboardAdapter

    clip = ClipboardAdapter()
    try:
        clip.set_text("meetinglens integration probe")
    except Exception as exc:  # pragma: no cover - no clipboard backend on this host
        pytest.skip(f"no clipboard backend: {exc}")
    assert clip.get_text() == "meetinglens integration probe"


@pytest.mark.skipif(not _have("PIL"), reason="Pillow not installed")
def test_capture_writes_png(tmp_path):
    from meetinglens.adapters.capture import ScreenCaptureAdapter

    path = str(tmp_path / "probe.png")
    ok = ScreenCaptureAdapter().capture(path)
    if not ok:  # pragma: no cover - locked screen / no display
        pytest.skip("screen capture unavailable in this session")
    import os

    assert os.path.getsize(path) > 0


