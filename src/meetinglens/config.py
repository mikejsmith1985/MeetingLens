"""Configuration model and plain-text parser for MeetingLens.

The config lives in a Notepad-editable ``key=value`` file so a screen-reader user can
change hotkeys and the capture interval without any structure to navigate. Every value
degrades gracefully to a built-in default and reports a spoken-friendly warning rather
than refusing to start (FR-022, FR-023). This module imports nothing external so it can
be unit-tested in well under 10ms.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Named defaults — no magic values scattered through the code.
DEFAULT_INTERVAL_SECONDS = 45
DEFAULT_HOTKEY_START = "Ctrl+Alt+S"
DEFAULT_HOTKEY_STOP = "Ctrl+Alt+X"
DEFAULT_HOTKEY_STATUS = "Ctrl+Alt+R"
DEFAULT_HOTKEY_SAVE = "Ctrl+Alt+W"
DEFAULT_HOTKEY_QUIT = "Ctrl+Alt+Q"
DEFAULT_AI_CHAT_URL = "https://copilot.microsoft.com"

_VALID_MODIFIERS = {"ctrl", "alt", "shift", "win"}


@dataclass
class Config:
    """User-adjustable settings, already validated and safe to use directly."""

    interval_seconds: int = DEFAULT_INTERVAL_SECONDS
    hotkey_start: str = DEFAULT_HOTKEY_START
    hotkey_stop: str = DEFAULT_HOTKEY_STOP
    hotkey_status: str = DEFAULT_HOTKEY_STATUS
    hotkey_save: str = DEFAULT_HOTKEY_SAVE
    hotkey_quit: str = DEFAULT_HOTKEY_QUIT
    ai_chat_url: str = DEFAULT_AI_CHAT_URL
    # Empty means "resolve to the Desktop default at startup" (see __main__).
    captures_folder: str = ""
    notes_folder: str = ""
    # Human-readable names of settings that fell back to a default; spoken as warnings.
    warnings: list[str] = field(default_factory=list)


def is_valid_chord(chord: str) -> bool:
    """Return whether ``chord`` is a ``Modifier(+Modifier)*+Key`` combination we can register."""
    parts = [part.strip().lower() for part in chord.split("+") if part.strip()]
    if len(parts) < 2:
        return False
    *modifiers, key = parts
    if not modifiers or any(modifier not in _VALID_MODIFIERS for modifier in modifiers):
        return False
    return len(key) >= 1 and key not in _VALID_MODIFIERS


def parse_config(text: str) -> Config:
    """Parse the raw config file text into a validated Config, collecting warnings.

    Unknown keys are ignored, comments (# ...) and blank lines are skipped, and any
    missing or malformed value falls back to its default with a recorded warning.
    """
    raw = _read_pairs(text)
    config = Config()

    config.interval_seconds = _resolve_interval(raw.get("interval_seconds"), config.warnings)
    config.hotkey_start = _resolve_chord(
        raw.get("hotkey_start"), DEFAULT_HOTKEY_START, "hotkey_start", config.warnings
    )
    config.hotkey_stop = _resolve_chord(
        raw.get("hotkey_stop"), DEFAULT_HOTKEY_STOP, "hotkey_stop", config.warnings
    )
    config.hotkey_status = _resolve_chord(
        raw.get("hotkey_status"), DEFAULT_HOTKEY_STATUS, "hotkey_status", config.warnings
    )
    config.hotkey_save = _resolve_chord(
        raw.get("hotkey_save"), DEFAULT_HOTKEY_SAVE, "hotkey_save", config.warnings
    )
    config.hotkey_quit = _resolve_chord(
        raw.get("hotkey_quit"), DEFAULT_HOTKEY_QUIT, "hotkey_quit", config.warnings
    )
    config.ai_chat_url = _resolve_url(raw.get("ai_chat_url"), config.warnings)
    config.captures_folder = (raw.get("captures_folder") or "").strip()
    config.notes_folder = (raw.get("notes_folder") or "").strip()
    return config


def load_config(path: str) -> Config:
    """Load and parse the config file at ``path``; a missing file yields all defaults."""
    try:
        with open(path, encoding="utf-8") as handle:
            return parse_config(handle.read())
    except FileNotFoundError:
        return Config()


def _read_pairs(text: str) -> dict[str, str]:
    """Turn the file body into a lower-cased key -> value map, ignoring comments/blanks."""
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        pairs[key.strip().lower()] = value.strip()
    return pairs


def _resolve_interval(raw_value: str | None, warnings: list[str]) -> int:
    """Return a positive integer interval, warning and defaulting on anything else."""
    if raw_value is None:
        return DEFAULT_INTERVAL_SECONDS
    try:
        seconds = int(raw_value)
    except ValueError:
        warnings.append("interval_seconds")
        return DEFAULT_INTERVAL_SECONDS
    if seconds <= 0:
        warnings.append("interval_seconds")
        return DEFAULT_INTERVAL_SECONDS
    return seconds


def _resolve_chord(raw_value: str | None, default: str, name: str, warnings: list[str]) -> str:
    """Return a valid hotkey chord, warning and defaulting when unparseable."""
    if raw_value is None:
        return default
    if not is_valid_chord(raw_value):
        warnings.append(name)
        return default
    return raw_value


def _resolve_url(raw_value: str | None, warnings: list[str]) -> str:
    """Return a non-empty chat URL, warning and defaulting on a blank value."""
    if raw_value is None:
        return DEFAULT_AI_CHAT_URL
    if not raw_value.strip():
        warnings.append("ai_chat_url")
        return DEFAULT_AI_CHAT_URL
    return raw_value.strip()
