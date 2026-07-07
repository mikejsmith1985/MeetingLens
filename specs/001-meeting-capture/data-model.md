# Phase 1 Data Model: MeetingLens

MeetingLens holds no database — its "data" is in-memory session state plus files on disk. Entities below map directly to the spec's Key Entities and drive the module design in `plan.md`.

## Entity: Config

Loaded once at startup from `config.txt`; immutable for the process lifetime.

| Field | Type | Default | Validation |
|---|---|---|---|
| `interval_seconds` | integer | `45` | > 0; non-numeric/≤0 → default + spoken warning |
| `hotkey_start` | hotkey string | `Ctrl+Alt+S` | parseable chord; else default + warning |
| `hotkey_stop` | hotkey string | `Ctrl+Alt+X` | parseable chord; else default + warning |
| `hotkey_status` | hotkey string | `Ctrl+Alt+R` | parseable chord; else default + warning |
| `hotkey_save` | hotkey string | `Ctrl+Alt+W` | parseable chord; else default + warning |
| `ai_chat_url` | string (URL) | Copilot/Bing chat URL | non-empty; else default |
| `captures_folder` | path | `~/Desktop/MeetingCaptures` | created if missing |
| `notes_folder` | path | `~/Desktop` | created if missing |

- **Rules**: Any missing or malformed value falls back to its default and triggers one spoken warning (FR-023). No value is fatal to startup.
- **Source of truth**: FR-022, FR-023; brief's config example.

## Entity: CaptureSession

In-memory, one instance at a time. Owns the capture timer.

| Field | Type | Notes |
|---|---|---|
| `state` | enum `IDLE` \| `RECORDING` | starts `IDLE` |
| `screenshot_count` | integer | reset to 0 on start; incremented only on a **successful** capture |
| `started_at` | timestamp | set on transition to `RECORDING`; `None` when idle |
| `interval_seconds` | integer | copied from Config at start |

**Derived values**

- `elapsed` = now − `started_at` (spoken in status, FR-013).

**State transitions**

| From | Event | Guard | To | Side effects |
|---|---|---|---|---|
| IDLE | start hotkey | — | RECORDING | reset count=0, set `started_at`, start timer, speak start confirmation (FR-008) |
| RECORDING | start hotkey | — | RECORDING | **no reset**; speak "already recording" (FR-012, edge case) |
| RECORDING | interval tick | capture succeeds | RECORDING | save PNG, count++, speak "Screenshot N taken" (FR-009, FR-010) |
| RECORDING | interval tick | capture fails | RECORDING | skip frame, no count change, session continues (FR-025) |
| RECORDING | status hotkey | — | RECORDING | speak recording + count + elapsed (FR-013) |
| IDLE | status hotkey | — | IDLE | speak idle (FR-014) |
| RECORDING | stop hotkey | — | IDLE | stop timer, speak final count, trigger Handoff (FR-015) |
| IDLE | stop hotkey | — | IDLE | speak "nothing being recorded" (edge case) |

- **Invariant**: at most one `RECORDING` session; `screenshot_count` counts only files actually written.
- **Source of truth**: FR-008–FR-015, spec Key Entities "Capture Session".

## Entity: Screenshot

A file, not an in-memory object.

| Property | Value |
|---|---|
| Format | PNG (lossless, legible slide text) |
| Location | `Config.captures_folder` |
| Naming | ordered by capture time (e.g. `capture_001.png`, zero-padded) so attach order matches meeting order |
| Lifetime | persists after session; not auto-deleted in v1 |

- **Source of truth**: FR-010, spec Key Entities "Screenshot".

## Entity: SummarisationPrompt

Composed on stop from the just-ended session; written to the clipboard, never persisted.

| Input | Source |
|---|---|
| screenshot count | `CaptureSession.screenshot_count` |
| interval | `Config.interval_seconds` |

- **Content rules (FR-016)**: states the exact count and interval; requests an ordered, per-screen description including all visible text, bullet points, chart descriptions, names, dates, and action items; ends by asking for key takeaways and action items with owners. Full template lives in `contracts/prompt-template.md`.
- **Source of truth**: FR-016, SC-005, spec Key Entities "Summarisation Prompt".

## Entity: MeetingNotesFile

Written by the save action from clipboard text.

| Property | Value |
|---|---|
| Name | `MeetingNotes_YYYY-MM-DD_HH-mm.txt` (local time) |
| Location | `Config.notes_folder` (Desktop) |
| Content | verbatim clipboard text |
| Precondition | clipboard text non-empty (FR-021) — empty ⇒ no file, spoken notice |
| Post-action | opened in Notepad, spoken confirmation (FR-020) |

- **Invariant**: timestamped names never overwrite prior saves (spec Assumption).
- **Source of truth**: FR-019–FR-021, spec Key Entities "Meeting Notes File".

## Relationships

```text
Config ──configures──▶ CaptureSession (interval, folders)
CaptureSession ──produces──▶ Screenshot* (0..N, ordered)
CaptureSession ──parameterises──▶ SummarisationPrompt (count, interval)
Clipboard text ──saved as──▶ MeetingNotesFile (1)
```
