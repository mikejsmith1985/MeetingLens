"""Integration test for the tray adapter's icon/state logic (T012).

The tray event loop needs a desktop session, so this only constructs the adapter and toggles
recording state (which updates the icon object) without calling the blocking ``run()``.
"""

from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.integration

_HAVE_PYSTRAY = importlib.util.find_spec("pystray") is not None and importlib.util.find_spec("PIL")


@pytest.mark.skipif(not _HAVE_PYSTRAY, reason="pystray/Pillow not installed")
def test_set_recording_updates_icon_title():
    from meetinglens.adapters.tray import TrayAdapter

    try:
        tray = TrayAdapter(on_exit=lambda: None)
    except Exception as exc:  # pragma: no cover - no desktop session
        pytest.skip(f"tray unavailable: {exc}")

    tray.set_recording(True)
    assert "recording" in tray._icon.title.lower()
    tray.set_recording(False)
    assert "idle" in tray._icon.title.lower()
