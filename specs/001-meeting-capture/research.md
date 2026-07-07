# Phase 0 Research: MeetingLens

The feature brief was prescriptive about the stack, so research here confirms each choice against the constitution (Article VII framework-first, Article V testability, offline/accessibility constraints) and resolves the few genuine unknowns. No open `NEEDS CLARIFICATION` remain.

## Decision 1 — Implementation language: Python 3.11

- **Decision**: Python 3.11 rather than AutoHotkey v2.
- **Rationale**: Article V demands unit tests that are 100% mocked and run in <10ms plus a real-infrastructure integration layer. Python's test tooling (`pytest`, dependency injection of adapters, mocking) makes the domain logic cleanly testable; AutoHotkey is lighter but has no comparable unit-test story, pushing all verification to manual/UX. Python also has mature, offline libraries for every required capability. Article I (BEST route over lightest) favours the maintainable, testable option.
- **Alternatives considered**: AutoHotkey v2 (smallest footprint, native hotkeys, but weak testability and awkward SAPI/tray/clipboard composition); C#/.NET WinForms tray app (excellent Windows integration but heavier build/install and more ceremony than warranted for v1).

## Decision 2 — Global hotkeys: `keyboard`

- **Decision**: The `keyboard` library for system-wide hotkey registration.
- **Rationale**: Registers OS-level hotkeys that fire regardless of focused window (FR-005), supports the `ctrl+alt+<key>` chords in the spec, and exposes registration so failures can be caught and spoken (FR-007). Fits behind a thin `HotkeyAdapter`.
- **Alternatives considered**: `pynput` (global listener but hotkey combos are more manual and suppression is fiddlier); native Win32 `RegisterHotKey` via `ctypes` (no dependency, but reimplements what `keyboard` provides — rejected by Article VII framework-first gate).
- **Note**: `keyboard` needs the process to run with normal user rights; some corporate machines flag global keyboard hooks. Mitigation recorded in quickstart (run the shipped binary; hotkey-registration failure is announced, not silent).

## Decision 3 — Speech: `pyttsx3` (SAPI5)

- **Decision**: `pyttsx3` driving the Windows SAPI5 engine.
- **Rationale**: Fully offline (FR-026/SC-008), no API keys (Article IX N/A), uses voices already installed on Windows. Runs its own driver loop so messages can be queued without blocking the capture timer.
- **Alternatives considered**: Direct `win32com` `SAPI.SpVoice` (works, but `pyttsx3` wraps it with a cleaner queue and cross-driver API); cloud TTS (rejected — violates offline constraint).
- **Resolved unknown — blocking**: `pyttsx3`'s `runAndWait()` is blocking. Decision: run speech on a dedicated worker thread with a queue so a spoken sentence never delays a scheduled capture or a subsequent hotkey (supports SC-002 timing and SC-004 drift).

## Decision 4 — Screen capture: `Pillow` `ImageGrab`

- **Decision**: `PIL.ImageGrab.grab()` saving PNG to the captures folder.
- **Rationale**: Simple, dependency-light primary-display capture; PNG is lossless for slide text legibility when the AI describes them. Primary display only matches v1 scope.
- **Alternatives considered**: `mss` (faster multi-monitor capture — deferred with multi-monitor to a later version); `pyautogui.screenshot` (wraps Pillow anyway, adds unneeded input-automation surface).
- **Resolved unknown — locked screen / display asleep**: `ImageGrab` may return black or raise when the session is locked. Decision: wrap each capture in the adapter; on failure, skip the frame, keep the session and timer alive, and do **not** increment the count for a failed frame (FR-025). Optionally speak nothing for a skipped frame to avoid confusing the count.

## Decision 5 — Tray indicator: `pystray`

- **Decision**: `pystray` for a tray icon that shows recording vs idle to sighted bystanders.
- **Rationale**: The brief's stated purpose — a visual cue for sighted helpers — with no navigable menu required. A minimal right-click menu offering "Exit" is acceptable (mouse optional, never required for core flow, satisfying FR-002).
- **Alternatives considered**: No tray at all (loses the sighted-bystander signal the brief asked for); full Win32 `Shell_NotifyIcon` (more code for no benefit — Article VII).

## Decision 6 — Clipboard: `pyperclip`

- **Decision**: `pyperclip` for reading (save-notes) and writing (prompt handoff) clipboard text.
- **Rationale**: Cross-simple text clipboard access; empty/non-text clipboard is detectable to satisfy FR-021 (nothing-to-save path).
- **Alternatives considered**: `win32clipboard` (more capable for non-text formats we don't need); reading via PowerShell (fragile, slow).

## Decision 7 — Launching Edge, Explorer, Notepad

- **Decision**: `webbrowser.open(<ai_chat_url>)` for the browser; `os.startfile(<folder>)` to open the captures folder in Explorer; `os.startfile(<notes_file>)` (or `notepad.exe <file>`) to open notes. All stdlib.
- **Rationale**: No extra dependency; uses the user's default handlers. Opening the folder lets the user Tab to files for attachment (FR-017).
- **Resolved unknown — AI chat URL**: The brief names `bing.com/chat`. Decision: store the target URL in `config.txt` (default to the Copilot/Bing chat URL) so it can be updated without a rebuild when the endpoint changes — avoids hard-coding a volatile URL and keeps it screen-reader-editable.

## Decision 8 — Config format & location

- **Decision**: A flat `key=value` plain-text `config.txt` in the app folder, parsed with the standard library; unknown/missing/malformed keys fall back to named defaults and a spoken warning (FR-022, FR-023).
- **Rationale**: A screen reader can read and edit it in Notepad with zero structure to navigate. Simpler than INI/JSON/YAML and matches the brief's example verbatim.
- **Alternatives considered**: `configparser`/INI (needs a section header, minor extra friction for the user); JSON/YAML (punctuation-heavy, error-prone to hand-edit by ear).
- **Keys**: `interval_seconds`, `hotkey_start`, `hotkey_stop`, `hotkey_status`, `hotkey_save`, plus `ai_chat_url` (new, from Decision 7) and `captures_folder` (defaulted).

## Decision 9 — Packaging / install with no terminal (FR-003, Article VIII)

- **Decision**: PyInstaller one-folder build producing `MeetingLens.exe` plus a bundled `config.txt`, distributed as a zip the user unzips and double-clicks. Release via local `git tag` + `gh release create` (no `scripts/local-release.ps1` exists yet; add one later if the process grows).
- **Rationale**: No Python install or terminal command required to run (FR-003). Article VIII forbids GitHub Actions releases — local pipeline only.
- **Alternatives considered**: One-file PyInstaller (`--onefile`) — slower startup and temp-extraction quirks with `keyboard`/tray; one-folder is more reliable. MSI installer (heavier than needed for v1).

## Decision 10 — Concurrency model

- **Decision**: Main thread runs the tray/`keyboard` loop; a repeating timer thread fires captures at the configured interval; a dedicated speech worker thread drains a message queue. Shared session state guarded by a lock.
- **Rationale**: Keeps hotkeys responsive (SC-003) and speech non-blocking (SC-002) while the capture cadence stays accurate (SC-004). Uses stdlib `threading` — no framework needed.
- **Alternatives considered**: `asyncio` (awkward with the blocking `keyboard`/`pyttsx3` loops); single-threaded polling (risks missed intervals and janky speech).
