# Implementation Plan: MeetingLens — Accessible Meeting Capture

**Branch**: `001-meeting-capture` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-meeting-capture/spec.md`

## Summary

MeetingLens is an offline, tray-resident Windows utility that lets a blind user independently capture a video call's visual content and turn it into screen-reader-friendly notes. The entire interface is global hotkeys plus spoken feedback — no window to navigate, no mouse. A capture session screenshots the primary display on a fixed interval, speaking a running count. On stop, the tool builds a context-rich summarisation prompt (with the real screenshot count and interval), copies it to the clipboard, opens the AI chat page and the captures folder, and speaks step-by-step handoff guidance. A save hotkey writes clipboard text to a timestamped notes file and opens it in Notepad.

**Technical approach**: A single Python 3.11 desktop application built from small, single-responsibility modules wired together by an event-driven controller. Each Windows integration (speech, capture, hotkeys, clipboard, browser/explorer launch, config) sits behind a thin adapter interface so the controller and session logic are unit-testable with mocks in <10ms, while adapters are exercised against the real OS in integration tests. Shipped as a PyInstaller folder-drop so it runs with no terminal command.

## Technical Context

**Language/Version**: Python 3.11+ (Windows)

**Primary Dependencies**: `keyboard` (global hotkeys), `pyttsx3` (offline SAPI5 text-to-speech), `Pillow` (primary-screen capture via `ImageGrab`), `pystray` (tray indicator), `pyperclip` (clipboard read/write). Standard library for config parsing, timestamped filenames, threading/timer, and launching Notepad/Edge/Explorer (`os.startfile`, `webbrowser`).

**Storage**: Local filesystem only — PNG screenshots in `~/Desktop/MeetingCaptures/`, timestamped `MeetingNotes_YYYY-MM-DD_HH-mm.txt` on the Desktop, and a plain-text `config.txt` in the app folder. No database.

**Testing**: `pytest` for unit (100% mocked adapters, <10ms each) and integration (real SAPI, real screen capture, real clipboard, real filesystem on Windows). No web/UI layer, so no Cypress.

**Target Platform**: Windows 10/11 desktop with a system tray, an installed Chromium Edge (or default browser), Notepad, and SAPI5 voices (all present by default).

**Project Type**: Single-project desktop application (background/tray tool, no GUI window).

**Performance Goals**: Every user-relevant state change spoken within 2 s of its trigger (SC-002); global hotkeys respond in ≥99% of presses under foreground contention (SC-003); capture drift ≤ one interval over 60 minutes (SC-004). Hotkey handling and speech must never block the capture timer.

**Constraints**: Fully offline for capture, speech, status, and save (SC-008/FR-026). No mouse interaction required (FR-002). No terminal command to install or run (FR-003). Primary display only (v1). Must degrade gracefully — missing folders auto-created, failed captures skipped without crashing, unregisterable hotkeys announced by speech, malformed config falls back to defaults.

**Scale/Scope**: Single local user, one active session at a time; sessions may reach hundreds of screenshots over an hour without responsiveness loss. ~6 modules, four hotkey actions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Status |
|---|---|---|
| I — Prime Directive (BEST route) | Production-ready, testable design over a quick script | ✅ Adapter seams + graceful degradation chosen over a monolithic script |
| II — Process Protection | No wildcard process kills | ✅ App launches Edge/Notepad/Explorer only; never kills processes. Tray exit stops its own PID |
| III — Branching | Work on a feature branch, PR to `main` | ⚠️ Currently on `master`. **Action**: create `feature/meeting-capture` before implementation (see Phase 2 note) |
| IV — Code Quality | Self-documenting names, verb-first functions <40 lines, doc comments, one-line file purpose comment, no magic numbers | ✅ Enforced in module design; interval/hotkeys are named config values, not literals |
| V — Testing (three-layer) | Unit 100% mocked <10ms; integration on real infra; UX via Cypress | ⚠️ Justified deviation: no web UI → **no Cypress**. "Real infrastructure" here = real Windows APIs (SAPI, ImageGrab, clipboard, filesystem), not testcontainers. Red→Green→Refactor still applies. Recorded in Complexity Tracking |
| VI — Documentation | `CHANGELOG.md` is the single source of truth; no ad-hoc status docs | ✅ Behavior changes land in `CHANGELOG.md`; `specs/001-meeting-capture/` is exempt pipeline output |
| VII — Framework-First Gate | Confirm libraries provide capability before building custom | ✅ Hotkeys/speech/capture/tray/clipboard all delegated to established libraries; only session/controller glue and config parsing are custom (documented gap: no library composes these four actions with spoken feedback) |
| VIII — Release | Local pipeline only, never GitHub Actions | ✅ Package with PyInstaller locally; `git tag` + `gh release create` (no `scripts/local-release.ps1` yet) |
| IX — Vault Zero-Knowledge | No plaintext secrets handled by agent | ✅ N/A — app handles no secrets, keys, or tokens |
| X — Verification & Proof | Evidence of behavior, not "it runs" | ✅ `quickstart.md` defines observable proof per user story (heard speech, files on disk, clipboard contents) |
| XI — Output Restraint | ≤1 dashboard file; no internal phase narration | ✅ No dashboard needed; tray icon is the only visual |

**Result**: PASS with two tracked deviations (Article III branch action, Article V Cypress N/A) — both justified, neither blocks design.

## Project Structure

### Documentation (this feature)

```text
specs/001-meeting-capture/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (config schema, hotkey actions, spoken-message catalog)
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
src/meetinglens/
├── __init__.py
├── __main__.py            # Entry point: load config, wire adapters, start tray + hotkey loop
├── app.py                 # AppController: routes hotkey events to session actions, owns spoken feedback
├── session.py             # CaptureSession: state (idle/recording), screenshot count, start time, timer
├── config.py              # Config load/parse/validate with defaults; screen-reader-friendly text format
├── prompt.py              # Builds the parameterised Copilot summarisation prompt
├── notes.py               # Clipboard→timestamped notes file, opens in Notepad
├── handoff.py             # Opens AI chat page + captures folder, sequences spoken guidance
└── adapters/
    ├── __init__.py
    ├── speech.py          # SpeechAdapter over pyttsx3 (offline SAPI5), non-blocking queue
    ├── capture.py         # ScreenCaptureAdapter over Pillow ImageGrab (primary display)
    ├── hotkeys.py         # HotkeyAdapter over `keyboard`, global registration + failure reporting
    ├── clipboard.py       # ClipboardAdapter over pyperclip
    ├── tray.py            # TrayAdapter over pystray (visual-only indicator)
    └── launcher.py        # Opens browser URL / Explorer folder / Notepad file

tests/
├── unit/                  # 100% mocked adapters, <10ms each (session, config, prompt, notes, app routing)
├── integration/          # Real Windows APIs: speech speaks, capture writes a PNG, clipboard round-trips, files land
└── conftest.py            # Fake/mocked adapter fixtures

config.txt                 # Shipped default config (plain text, Notepad-editable)
CHANGELOG.md               # Single source of truth for behavior changes (Article VI)
build/                     # PyInstaller spec + local packaging output (folder-drop distributable)
```

**Structure Decision**: Single-project desktop app (constitution "single project" default). The controller/session/domain modules (`app`, `session`, `config`, `prompt`, `notes`, `handoff`) hold all logic and are pure/mockable; every OS touchpoint is isolated in `adapters/` behind a narrow interface. This satisfies Article V's unit-speed requirement (domain tests never touch the OS) while keeping real-API integration tests honest, and satisfies Article VII by keeping custom code to the glue the libraries don't provide.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Article V — no Cypress UX layer; integration uses real Windows APIs instead of testcontainers | The product has no web UI and no containerisable service; its "infrastructure" is the local Windows shell (SAPI, screen, clipboard, filesystem) | Cypress/testcontainers cannot exercise global hotkeys, SAPI speech, or screen capture; forcing them would test nothing real. Real-API integration tests are the faithful equivalent |
| Adapter-interface indirection over each OS library | Enables <10ms fully-mocked unit tests (Article V) and graceful-degradation seams (skip failed capture, announce hotkey failure) | Calling libraries directly from domain logic would make unit tests hit the OS (too slow, non-deterministic) and scatter error handling |
