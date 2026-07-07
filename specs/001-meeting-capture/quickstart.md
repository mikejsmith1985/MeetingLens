# Quickstart & Validation: MeetingLens

This guide proves the feature works end-to-end with observable evidence (Article X). It maps each user story to a runnable check. It is a validation guide, not implementation — code lives in `src/` and `tasks.md`.

## Prerequisites

- Windows 10/11 with SAPI5 voices (default), Edge or a default browser, Notepad.
- **Dev**: Python 3.11+, then `pip install -r requirements.txt` (`keyboard`, `pyttsx3`, `Pillow`, `pystray`, `pyperclip`, `pytest`).
- **End user**: unzip the release and double-click `MeetingLens.exe` — no terminal, no Python (FR-003).

## Run (dev)

```powershell
python -m meetinglens
```

Expect to hear the `READY` message (FR-004). A tray icon appears (idle state).

## Story 1 — Capture (P1)

1. Open a slideshow in another window and give it focus.
2. Press `Ctrl+Alt+S`.
   - **Hear**: "Meeting capture started. 0 screenshots taken so far."
3. Wait through 2–3 intervals (default 45 s; for testing set `interval_seconds=5`).
   - **Hear**: "Screenshot 1 taken", "Screenshot 2 taken", …
   - **See on disk**: one PNG per interval in `Desktop\MeetingCaptures\`.
4. Press `Ctrl+Alt+R`.
   - **Hear**: "Recording. N screenshots taken. Session running M minutes."
5. Press `Ctrl+Alt+S` again while recording.
   - **Hear**: "Already recording…" — count is **not** reset.

**Pass**: spoken confirmations at start/each capture/status; exactly one PNG per interval; no reset on second start.

## Story 2 — Handoff (P2)

1. With screenshots present, press `Ctrl+Alt+X`.
   - **Hear**: "Stopping capture. N screenshots taken. Preparing your summary."
   - **Then**: browser opens the AI chat URL; `MeetingCaptures` folder opens in Explorer.
   - **Hear**: the `HANDOFF_OPEN` then `HANDOFF_READY` guidance.
2. Paste the clipboard into a text editor to inspect it.

**Pass**: clipboard contains the prompt with the correct count and interval (SC-005) and all required requests (see `contracts/prompt-template.md`); browser and folder both opened.

## Story 3 — Save notes (P3)

1. Copy any text (simulating the AI response) to the clipboard.
2. Press `Ctrl+Alt+W`.
   - **See on disk**: `Desktop\MeetingNotes_YYYY-MM-DD_HH-mm.txt` containing that text.
   - **Then**: file opens in Notepad.
   - **Hear**: "Your meeting notes are saved to your Desktop and open in Notepad."
3. Clear the clipboard of text, press `Ctrl+Alt+W`.
   - **Hear**: "There is nothing on the clipboard to save." No file created.

**Pass**: timestamped file written and opened only when clipboard has text.

## Story 4 — Status & config (P3)

1. Press `Ctrl+Alt+R` with no session → **Hear** idle message.
2. Edit `config.txt` in Notepad: change `interval_seconds`, restart, start a session → new cadence in effect.
3. Put a deliberately invalid value (e.g. `interval_seconds=abc`), restart → **Hear** a config warning; tool still starts on defaults.

**Pass**: status accurate in both states; config changes honoured; bad config degrades gracefully.

## Edge-case checks

- Lock the screen mid-session → session survives, no crash; count does not advance for skipped frames (FR-025).
- Delete `MeetingCaptures` before starting → folder auto-created (FR-024).
- Occupy `Ctrl+Alt+S` with another app, launch MeetingLens → **Hear** hotkey-registration warning (FR-007).

## Automated tests

```powershell
pytest tests/unit -q          # 100% mocked adapters, <10ms each (Article V)
pytest tests/integration -q   # real SAPI/capture/clipboard/filesystem on Windows
```

**Unit** cover: session state machine, config parse/defaults, prompt building, notes naming, controller routing.
**Integration** cover: speech actually speaks, capture writes a real PNG, clipboard round-trips, notes file lands and opens.
