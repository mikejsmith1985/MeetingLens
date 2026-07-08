"""Unit tests for config parsing, defaults, and graceful degradation (T006, T038)."""

from __future__ import annotations

import pytest

from meetinglens import config as cfg

pytestmark = pytest.mark.unit


def test_defaults_when_empty_text():
    result = cfg.parse_config("")
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS
    assert result.hotkey_start == cfg.DEFAULT_HOTKEY_START
    assert result.hotkey_quit == cfg.DEFAULT_HOTKEY_QUIT
    assert result.ai_chat_url == cfg.DEFAULT_AI_CHAT_URL
    assert result.warnings == []


def test_parses_valid_values_and_ignores_comments_and_unknowns():
    text = "\n".join(
        [
            "# a comment",
            "interval_seconds=10",
            "hotkey_start=Ctrl+Alt+G",
            "unknown_key=whatever",
            "",
            "ai_chat_url=https://example.com/chat",
        ]
    )
    result = cfg.parse_config(text)
    assert result.interval_seconds == 10
    assert result.hotkey_start == "Ctrl+Alt+G"
    assert result.ai_chat_url == "https://example.com/chat"
    assert result.warnings == []


def test_invalid_interval_falls_back_with_warning():
    result = cfg.parse_config("interval_seconds=abc")
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS
    assert "interval_seconds" in result.warnings


def test_non_positive_interval_falls_back_with_warning():
    result = cfg.parse_config("interval_seconds=0")
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS
    assert "interval_seconds" in result.warnings


def test_invalid_hotkey_falls_back_with_warning():
    result = cfg.parse_config("hotkey_start=notachord")
    assert result.hotkey_start == cfg.DEFAULT_HOTKEY_START
    assert "hotkey_start" in result.warnings


def test_blank_url_falls_back_with_warning():
    result = cfg.parse_config("ai_chat_url=   ")
    assert result.ai_chat_url == cfg.DEFAULT_AI_CHAT_URL
    assert "ai_chat_url" in result.warnings


def test_missing_file_yields_defaults(tmp_path):
    result = cfg.load_config(str(tmp_path / "does_not_exist.txt"))
    assert result.interval_seconds == cfg.DEFAULT_INTERVAL_SECONDS


@pytest.mark.parametrize(
    "chord,expected",
    [
        ("Ctrl+Alt+S", True),
        ("ctrl+alt+s", True),
        ("Ctrl+Shift+Alt+K", True),
        ("S", False),
        ("Ctrl+Ctrl", False),
        ("notachord", False),
        ("", False),
    ],
)
def test_is_valid_chord(chord, expected):
    assert cfg.is_valid_chord(chord) is expected
