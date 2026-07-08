"""Integration test: config is loaded from a real file and degrades gracefully (T041)."""

from __future__ import annotations

import pytest

from meetinglens import config as cfg

pytestmark = pytest.mark.integration


def test_reload_reflects_edited_interval(tmp_path):
    path = tmp_path / "config.txt"
    path.write_text("interval_seconds=5\nhotkey_start=Ctrl+Alt+P\n", encoding="utf-8")
    result = cfg.load_config(str(path))
    assert result.interval_seconds == 5
    assert result.hotkey_start == "Ctrl+Alt+P"
    assert result.warnings == []


def test_malformed_file_falls_back_and_warns(tmp_path):
    path = tmp_path / "config.txt"
    path.write_text("interval_seconds=notanumber\n", encoding="utf-8")
    result = cfg.load_config(str(path))
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS
    assert "interval_seconds" in result.warnings
