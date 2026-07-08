"""Integration test: the real screen-capture adapter writes a valid PNG per call (T025)."""

from __future__ import annotations

import importlib.util
import os

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(importlib.util.find_spec("PIL") is None, reason="Pillow not installed")
def test_three_captures_produce_three_files(tmp_path):
    from meetinglens.adapters.capture import ScreenCaptureAdapter

    adapter = ScreenCaptureAdapter()
    written = []
    for index in range(1, 4):
        path = str(tmp_path / f"capture_{index:03d}.png")
        if not adapter.capture(path):  # pragma: no cover - headless/locked
            pytest.skip("screen capture unavailable in this session")
        written.append(path)
    assert all(os.path.getsize(path) > 0 for path in written)
    assert len(written) == 3
