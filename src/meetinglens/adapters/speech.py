"""Offline text-to-speech adapter over pyttsx3 (Windows SAPI5).

pyttsx3's run loop is blocking, so speech runs on a dedicated worker thread draining a
queue: enqueuing a message returns immediately and never delays the capture timer or the
next hotkey (SC-002). No internet is required (FR-026).

Because SAPI is a COM component and this worker is a separate thread, the thread MUST call
CoInitialize before creating the engine — otherwise every spoken message fails silently,
which for an audio-first accessibility tool means total silence. See ``_run``.
"""

from __future__ import annotations

import queue
import threading

import pyttsx3

_STOP = object()  # Sentinel queued to unblock and end the worker thread.


class SpeechAdapter:
    """Speaks queued messages in order on a background thread."""

    def __init__(self) -> None:
        """Start the speech worker thread and wait until its engine is ready (or has failed)."""
        self._queue: queue.Queue = queue.Queue()
        self._ready = threading.Event()
        self._init_error: Exception | None = None
        self._worker = threading.Thread(target=self._run, name="meetinglens-speech", daemon=True)
        self._worker.start()

    def say(self, text: str) -> None:
        """Enqueue a message to be spoken; returns without waiting for speech to finish."""
        self._queue.put(text)

    def stop(self) -> None:
        """Signal the worker to finish and speak nothing further."""
        self._queue.put(_STOP)

    def started_ok(self, timeout: float = 5.0) -> bool:
        """Return whether the speech engine initialised successfully within ``timeout`` seconds."""
        self._ready.wait(timeout)
        return self._init_error is None

    def _run(self) -> None:
        """Worker loop: init COM + engine on this thread, then speak each queued message."""
        self._init_com()
        try:
            engine = pyttsx3.init()
        except Exception as error:  # pragma: no cover - no SAPI voice on host
            self._init_error = error
            self._ready.set()
            return
        self._ready.set()
        while True:
            item = self._queue.get()
            if item is _STOP:
                break
            self._speak_one(engine, item)

    @staticmethod
    def _speak_one(engine, text: str) -> None:
        """Speak one message, recovering from a stuck run loop so the worker never dies.

        A dead speech worker means total silence, so a transient engine error must never
        propagate out of the loop.
        """
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # 'run loop already started' — reset the loop and drop this one message.
            try:
                engine.endLoop()
            except Exception:
                pass

    @staticmethod
    def _init_com() -> None:
        """Initialise COM on this thread so SAPI (a COM object) can be created here."""
        try:
            import comtypes

            comtypes.CoInitialize()
        except Exception:  # pragma: no cover - non-Windows or comtypes absent
            pass
