"""Unit test for the __main__ bootstrap wiring (T018).

Stubs every adapter (and the blocking tray loop) so ``main()`` can be run end-to-end in
memory: it must load config, register all five hotkeys, and speak the readiness message
without raising — a regression guard for the tray/controller wiring cycle.
"""

from __future__ import annotations

import pytest

from meetinglens import __main__ as entry

pytestmark = pytest.mark.unit


class _StubSpeech:
    def __init__(self):
        self.said = []

    def say(self, text):
        self.said.append(text)

    def stop(self):
        pass


class _StubHotkeys:
    def __init__(self):
        self.registered = []

    def register(self, chord, callback):
        self.registered.append(chord)
        return True

    def clear(self):
        pass


class _StubTray:
    def __init__(self, on_exit):
        self.on_exit = on_exit
        self.ran = False

    def set_recording(self, is_recording):
        pass

    def run(self):
        self.ran = True  # do not block

    def stop(self):
        pass


class _Noop:
    def __init__(self, *args, **kwargs):
        pass


def test_main_wires_hotkeys_and_speaks_ready(monkeypatch):
    speech = _StubSpeech()
    hotkeys = _StubHotkeys()
    trays = []

    def _make_tray(on_exit):
        tray = _StubTray(on_exit)
        trays.append(tray)
        return tray

    monkeypatch.setattr(entry, "SpeechAdapter", lambda: speech)
    monkeypatch.setattr(entry, "HotkeyAdapter", lambda: hotkeys)
    monkeypatch.setattr(entry, "TrayAdapter", _make_tray)
    monkeypatch.setattr(entry, "ScreenCaptureAdapter", _Noop)
    monkeypatch.setattr(entry, "ClipboardAdapter", _Noop)
    monkeypatch.setattr(entry, "LauncherAdapter", _Noop)
    monkeypatch.setattr(entry, "RepeatingTimer", _Noop)

    entry.main()

    # All five global hotkeys registered, and the readiness message was spoken.
    assert len(hotkeys.registered) == 5
    assert any("ready" in message.lower() for message in speech.said)
    assert trays and trays[0].ran is True
