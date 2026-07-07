---

description: "Task list for MeetingLens — Accessible Meeting Capture"
---

# Tasks: MeetingLens — Accessible Meeting Capture

**Input**: Design documents from `specs/001-meeting-capture/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED. Constitution Article V mandates Red → Green → Refactor — every implementation task is preceded by a failing test. Unit tests use mocked adapters (<10ms); integration tests exercise the real Windows APIs.

**Organization**: Grouped by user story so each is independently implementable, testable, and demoable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1–US4 (setup/foundational/polish carry no story label)
- Paths are repo-relative; structure per `plan.md`

## Path Conventions

Single-project desktop app: source in `src/meetinglens/`, tests in `tests/unit/` and `tests/integration/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton and tooling.

- [ ] T001 Create project structure: `src/meetinglens/`, `src/meetinglens/adapters/`, `tests/unit/`, `tests/integration/`, `build/` with `__init__.py` files
- [ ] T002 Create `requirements.txt` (keyboard, pyttsx3, Pillow, pystray, pyperclip, pytest) and `pyproject.toml` with pytest config (markers: `unit`, `integration`)
- [ ] T003 [P] Configure lint/format (ruff + black) in `pyproject.toml` and add `.gitignore` for `build/`, `dist/`, `__pycache__/`
- [ ] T004 [P] Add shipped default `config.txt` at repo root per `contracts/config-schema.md`
- [ ] T005 [P] Create `CHANGELOG.md` at repo root with an "Unreleased" section (Article VI)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config, adapters, message catalog, and app bootstrap that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 [P] Unit test config parse + defaults in `tests/unit/test_config.py` (key=value, comments, missing/invalid → defaults) — write to FAIL
- [ ] T007 Implement `Config` model + loader in `src/meetinglens/config.py` per `data-model.md` and `contracts/config-schema.md` (depends on T006)
- [ ] T008 [P] Implement `SpeechAdapter` (offline pyttsx3/SAPI5, dedicated worker thread + queue, non-blocking) in `src/meetinglens/adapters/speech.py`
- [ ] T009 [P] Implement `ScreenCaptureAdapter` (Pillow `ImageGrab`, primary display, returns success/failure so callers can skip) in `src/meetinglens/adapters/capture.py`
- [ ] T010 [P] Implement `HotkeyAdapter` (keyboard, global registration, reports per-action registration failure) in `src/meetinglens/adapters/hotkeys.py`
- [ ] T011 [P] Implement `ClipboardAdapter` (pyperclip read/write, empty-detection) in `src/meetinglens/adapters/clipboard.py`
- [ ] T012 [P] Implement `TrayAdapter` (pystray recording/idle indicator + Exit item) in `src/meetinglens/adapters/tray.py`
- [ ] T013 [P] Implement `LauncherAdapter` (open browser URL, open folder in Explorer, open file in Notepad via `webbrowser`/`os.startfile`) in `src/meetinglens/adapters/launcher.py`
- [ ] T014 [P] Create spoken-message catalog constants in `src/meetinglens/messages.py` per `contracts/spoken-messages.md`
- [ ] T015 [P] Create mocked/fake adapter fixtures in `tests/conftest.py` (fake speech records spoken text; fake capture/clipboard/launcher record calls)
- [ ] T016 [P] Integration tests for adapters in `tests/integration/test_adapters.py` (speech speaks, capture writes a real PNG, clipboard round-trips, launcher opens targets) — real Windows APIs
- [ ] T017 Implement `AppController` skeleton (adapter dependency injection, speech-worker wiring, hotkey → action routing table, shared session lock) in `src/meetinglens/app.py` (depends on T008–T014)
- [ ] T018 Implement entry point `src/meetinglens/__main__.py`: load config, wire adapters, register the four hotkeys, speak `READY` naming start/stop (FR-004), start tray loop (depends on T007, T017)

**Checkpoint**: App launches, speaks readiness, tray visible, hotkeys registered — user stories can now begin.

---

## Phase 3: User Story 1 - Capture visual meeting content hands-free (Priority: P1) 🎯 MVP

**Goal**: Start a session by hotkey, capture the primary screen every interval with a spoken running count, stop by hotkey with a final count — a complete visual record with zero sighted help.

**Independent Test**: Start with `Ctrl+Alt+S` while a slideshow has focus, wait through several intervals, stop with `Ctrl+Alt+X`; hear start/each-capture/final-count speech and find one PNG per interval in `Desktop\MeetingCaptures\`.

- [ ] T019 [P] [US1] Unit test `CaptureSession` state machine in `tests/unit/test_session.py` (idle↔recording, count only on success, already-recording guard, elapsed) — write to FAIL
- [ ] T020 [US1] Implement `CaptureSession` (state, screenshot_count, started_at, interval, repeating capture timer, transitions) in `src/meetinglens/session.py` per `data-model.md` (depends on T019)
- [ ] T021 [US1] Wire **start** action in `AppController` (idle→start: reset count, start timer, speak `START`; recording→speak `ALREADY_RECORDING`, no reset) in `src/meetinglens/app.py` (FR-008, FR-012)
- [ ] T022 [US1] Wire interval **capture callback**: call capture adapter, on success save ordered PNG to captures folder + count++ + speak `CAPTURE`; on failure skip frame, no count change, session continues (FR-009, FR-010, FR-025) in `src/meetinglens/app.py` / `session.py`
- [ ] T023 [US1] Wire **stop** action for capture: idle→speak `NOTHING_RECORDING`; recording→halt timer, speak `STOPPING` final count (handoff added in US2) in `src/meetinglens/app.py` (FR-015)
- [ ] T024 [US1] Ensure captures folder auto-created on start if missing in `src/meetinglens/session.py` (FR-024)
- [ ] T025 [P] [US1] Integration test capture flow in `tests/integration/test_capture.py` (start → real PNGs written per interval → stop; count matches file count)

**Checkpoint**: US1 fully functional and demoable as the MVP.

---

## Phase 4: User Story 2 - Guided handoff to an AI summariser (Priority: P2)

**Goal**: On stop, build the parameterised prompt, copy it to the clipboard, open the AI chat page and captures folder, and speak step-by-step attach/paste guidance.

**Independent Test**: With screenshots present, press `Ctrl+Alt+X`; clipboard holds the prompt with the correct count and interval, the browser opens the AI chat URL, the captures folder opens, and the `HANDOFF_OPEN`/`HANDOFF_READY` guidance is spoken.

- [ ] T026 [P] [US2] Unit test prompt builder in `tests/unit/test_prompt.py` (asserts count, interval, ordered per-screen request, required content) per `contracts/prompt-template.md` — write to FAIL
- [ ] T027 [US2] Implement `build_summarisation_prompt(count, interval)` in `src/meetinglens/prompt.py` (depends on T026)
- [ ] T028 [P] [US2] Unit test handoff sequence in `tests/unit/test_handoff.py` (clipboard written, launcher opens URL + folder, spoken order STOPPING→HANDOFF_OPEN→HANDOFF_READY) — write to FAIL
- [ ] T029 [US2] Implement `Handoff` in `src/meetinglens/handoff.py`: write prompt to clipboard, retain the exact prompt string as `AppController.last_handoff_prompt` (FR-027, feeds US3 save guard), open `ai_chat_url` + captures folder via launcher, enqueue `HANDOFF_OPEN`/`HANDOFF_READY` (depends on T027, T028)
- [ ] T030 [US2] Extend **stop** action in `src/meetinglens/app.py` to invoke `Handoff` after `STOPPING` (FR-015–FR-018) (depends on T023, T029)
- [ ] T031 [P] [US2] Integration test handoff in `tests/integration/test_handoff.py` (clipboard round-trip of real prompt; launcher invoked for URL + folder)

**Checkpoint**: US1 + US2 work independently; a captured session hands off to the AI unaided.

---

## Phase 5: User Story 3 - Save the AI response as accessible notes (Priority: P3)

**Goal**: On the save hotkey, write clipboard text to a timestamped notes file and open it in Notepad; do nothing (but speak) if the clipboard is empty.

**Independent Test**: Copy text, press `Ctrl+Alt+W` → timestamped `MeetingNotes_*.txt` on Desktop, opened in Notepad, `NOTES_SAVED` spoken. Clear clipboard, press again → `NOTHING_TO_SAVE`, no file. Immediately after a handoff (clipboard still holds the prompt), press `Ctrl+Alt+W` → `PROMPT_NOT_COPIED`, no file.

- [ ] T032 [P] [US3] Unit test notes module in `tests/unit/test_notes.py` (timestamped filename format, empty-clipboard → no file, non-overwrite, **clipboard equals last handoff prompt → no file**) per `data-model.md` — write to FAIL
- [ ] T033 [US3] Implement `save_notes(clipboard_text, last_handoff_prompt)` in `src/meetinglens/notes.py`: if text non-empty AND not equal to `last_handoff_prompt`, write `MeetingNotes_YYYY-MM-DD_HH-mm.txt` to notes folder and open in Notepad; otherwise write nothing (depends on T032) (FR-019, FR-020, FR-027)
- [ ] T034 [US3] Wire **save** action in `src/meetinglens/app.py` passing `AppController.last_handoff_prompt` to `save_notes` (non-empty & not prompt→`NOTES_SAVED`; empty→`NOTHING_TO_SAVE`; equals prompt→`PROMPT_NOT_COPIED`; no file in the latter two; works in any session state) (FR-021, FR-027)
- [ ] T035 [P] [US3] Integration test save-notes in `tests/integration/test_notes.py` (real file written with clipboard text and opened; empty clipboard writes nothing; clipboard holding the retained prompt writes nothing and speaks `PROMPT_NOT_COPIED`)

**Checkpoint**: US1–US3 independently functional; full capture-to-notes loop closes.

---

## Phase 6: User Story 4 - Status & screen-reader-editable configuration (Priority: P3)

**Goal**: Speak accurate on-demand status; honour config edits; degrade gracefully on bad config or unregisterable hotkeys.

**Independent Test**: `Ctrl+Alt+R` speaks recording+count+elapsed during a session and idle otherwise; changing `interval_seconds` in `config.txt` and restarting changes cadence; an invalid value yields a spoken `CONFIG_WARNING` and the tool still starts on defaults.

- [ ] T036 [P] [US4] Unit test status action in `tests/unit/test_status.py` (`STATUS_RECORDING` includes count + elapsed minutes; `STATUS_IDLE` when idle) — write to FAIL
- [ ] T037 [US4] Wire **status** action in `src/meetinglens/app.py` (FR-013, FR-014) (depends on T036)
- [ ] T038 [P] [US4] Unit test config graceful degradation in `tests/unit/test_config_defaults.py` (bad interval/hotkey → default + one warning) — write to FAIL
- [ ] T039 [US4] Add config validation warnings (`CONFIG_WARNING`) in `src/meetinglens/config.py` and hotkey-registration-failure speech (`HOTKEY_FAILED`) in `src/meetinglens/app.py`/`__main__.py` (FR-007, FR-023) (depends on T038)
- [ ] T040 [US4] Verify first-run `READY` names the start and stop hotkeys and add regression coverage in `tests/unit/test_status.py` (FR-004)
- [ ] T041 [P] [US4] Integration test status + config reload in `tests/integration/test_status_config.py` (edit interval → restart → new cadence; malformed value → warning + defaults)

**Checkpoint**: All four user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Packaging, docs, robustness, and full validation across stories.

- [ ] T042 [P] Update `CHANGELOG.md` with v1 capabilities (Article VI)
- [ ] T043 [P] Add PyInstaller one-folder build spec `build/meetinglens.spec` producing `MeetingLens.exe` + bundled `config.txt` (folder-drop, no terminal) per research Decision 9
- [ ] T044 Audit Article IV compliance across `src/meetinglens/` (file-purpose comments, doc comments on public functions, functions <40 lines, no magic numbers)
- [ ] T045 [P] Robustness pass: long-session responsiveness (hundreds of screenshots), locked-screen skip verification, folder auto-create for both captures and notes (FR-024, FR-025)
- [ ] T046 Run `quickstart.md` end-to-end validation for all four stories and record evidence (Article X)
- [ ] T047 [P] Verification test for **SC-002** (speech latency) in `tests/integration/test_latency.py`: assert every state-change message is enqueued and begins speaking within 2 seconds of its trigger under an active session
- [ ] T048 [P] Verification test for **SC-003** (hotkey reliability) in `tests/integration/test_hotkey_reliability.py`: with a foreground app holding keyboard focus, fire each global hotkey many times and assert ≥99% are handled

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — **BLOCKS all user stories**.
- **User Stories (Phases 3–6)**: all depend on Foundational. US1 is the MVP; US2 extends US1's stop action (T030 depends on T023); US3 and US4 are independent of each other and of US2.
- **Polish (Phase 7)**: after all target stories complete.

### User Story Dependencies

- **US1 (P1)**: after Foundational — no story dependencies.
- **US2 (P2)**: after Foundational — extends US1's stop wiring (T030 ← T023), otherwise independent.
- **US3 (P3)**: after Foundational — fully independent (save works in any state).
- **US4 (P3)**: after Foundational — independent; status reads session state read-only.

### Within Each Story

Test (fail) → implementation → wiring → integration test. Models before services; core before integration.

### Parallel Opportunities

- Setup: T003, T004, T005 in parallel.
- Foundational: all six adapters (T008–T013) + message catalog (T014) + fixtures (T015) + adapter integration tests (T016) run in parallel; T017 waits on them, T018 waits on T007+T017.
- Once Foundational is done, US1–US4 can be staffed in parallel (mind T030←T023).
- Every `[P]` unit test can be written alongside its siblings.

---

## Parallel Example: Foundational Adapters

```bash
# After T006/T007 (config), launch adapters together:
Task: "Implement SpeechAdapter in src/meetinglens/adapters/speech.py"
Task: "Implement ScreenCaptureAdapter in src/meetinglens/adapters/capture.py"
Task: "Implement HotkeyAdapter in src/meetinglens/adapters/hotkeys.py"
Task: "Implement ClipboardAdapter in src/meetinglens/adapters/clipboard.py"
Task: "Implement TrayAdapter in src/meetinglens/adapters/tray.py"
Task: "Implement LauncherAdapter in src/meetinglens/adapters/launcher.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 Setup → 2. Phase 2 Foundational (CRITICAL) → 3. Phase 3 US1 → 4. **STOP & VALIDATE** capture end-to-end → demo.

### Incremental Delivery

Foundation → US1 (MVP: capture) → US2 (AI handoff) → US3 (save notes) → US4 (status/config) → Polish. Each story adds value without breaking prior ones.

### Parallel Team Strategy

After Foundational: Dev A → US1, Dev B → US2 (coordinate on the stop-action seam), Dev C → US3, Dev D → US4.

---

## Notes

- `[P]` = different files, no incomplete dependency.
- Constitution Article III: create `feature/meeting-capture` before starting; PR to `main`.
- Verify each test FAILS before implementing (Red → Green → Refactor).
- Commit after each task or logical group; update `CHANGELOG.md` for behavior changes.
- Stop at any checkpoint to validate a story independently.
