"""Focused unit tests for config graceful degradation and one-warning-per-setting (T038)."""

from __future__ import annotations

import pytest

from meetinglens import config as cfg

pytestmark = pytest.mark.unit


def test_multiple_bad_values_each_produce_one_warning():
    text = "interval_seconds=-5\nhotkey_stop=xyz\nai_chat_url="
    result = cfg.parse_config(text)
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS
    assert result.hotkey_stop == cfg.DEFAULT_HOTKEY_STOP
    assert result.ai_chat_url == cfg.DEFAULT_AI_CHAT_URL
    assert sorted(result.warnings) == ["ai_chat_url", "hotkey_stop", "interval_seconds"]


def test_good_config_produces_no_warnings():
    text = "interval_seconds=60\nhotkey_start=Ctrl+Alt+P"
    result = cfg.parse_config(text)
    assert result.warnings == []
