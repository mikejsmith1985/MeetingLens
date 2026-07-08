# Changelog — meetinglens

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Forge Workflow initialized with Forge Terminal Workflow Architect
- Accessible, audio-first meeting capture (feature `001-meeting-capture`):
  - Tray-resident, keyboard-only tool driven entirely by global hotkeys and spoken feedback.
  - Capture session: start/stop/status with spoken running screenshot count; screenshots
    saved to `Desktop\MeetingCaptures\` at a configurable interval (default 45 s).
  - Guided handoff on stop: builds a Copilot summarisation prompt (with the real screenshot
    count and interval), copies it to the clipboard, opens the AI chat page and the captures
    folder, and speaks step-by-step attach/paste guidance.
  - Save notes: writes clipboard text to a timestamped `MeetingNotes_*.txt` on the Desktop and
    opens it in Notepad; refuses to save the handoff prompt still sitting on the clipboard.
  - Keyboard quit hotkey (`Ctrl+Alt+Q`) so the app can be closed without a mouse.
  - Plain-text `config.txt` for interval, all five hotkeys, and the AI chat URL, with
    graceful fallback to defaults and spoken warnings on bad values.

### Changed

### Fixed

### Removed
