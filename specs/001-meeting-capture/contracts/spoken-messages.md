# Contract: Spoken Message Catalog

Every state change is spoken within 2 s (SC-002). Messages are parameterised; `{n}`, `{mins}`, `{action}` are filled at runtime. Wording below is the contract the integration tests assert against (substring match on the dynamic parts).

| ID | Trigger | Spoken text |
|---|---|---|
| `READY` | first run wired | "MeetingLens is ready. Press Control Alt S to start recording. Press Control Alt X to stop." |
| `START` | start when idle | "Meeting capture started. 0 screenshots taken so far." |
| `CAPTURE` | each successful capture | "Screenshot {n} taken." |
| `ALREADY_RECORDING` | start when recording | "Already recording. {n} screenshots taken so far." |
| `STATUS_RECORDING` | status when recording | "Recording. {n} screenshots taken. Session running {mins} minutes." |
| `STATUS_IDLE` | status when idle | "Not recording. Press Control Alt S to start." |
| `STOPPING` | stop when recording | "Stopping capture. {n} screenshots taken. Preparing your summary." |
| `NOTHING_RECORDING` | stop when idle | "Nothing is being recorded." |
| `HANDOFF_OPEN` | after Edge opens | "Edge is open with Copilot. Press Tab to reach the chat box, then press Control V to paste your prompt. Then attach your screenshots from the MeetingCaptures folder on your Desktop." |
| `HANDOFF_READY` | after clipboard + folder open | "Your prompt is copied to clipboard. Your screenshots are in the folder that just opened. When Copilot finishes, copy its response and press Control Alt W to save it as your meeting notes." |
| `NOTES_SAVED` | notes written + Notepad open | "Your meeting notes are saved to your Desktop and open in Notepad." |
| `NOTHING_TO_SAVE` | save with empty clipboard | "There is nothing on the clipboard to save." |
| `PROMPT_NOT_COPIED` | save while clipboard still holds the handoff prompt (FR-027) | "That is still your prompt. Copy Copilot's response first, then press Control Alt W." |
| `CONFIG_WARNING` | bad config value | "Warning. {setting} in your config file could not be read. Using the default." |
| `HOTKEY_FAILED` | registration failure | "Warning. The hotkey for {action} could not be registered. It may be in use by another program." |

## Rules

- Numbers are spoken as words-or-digits per the engine's default; tests assert on the numeric value being present.
- Messages are queued to a speech worker thread; ordering is preserved (e.g. `STOPPING` → `HANDOFF_OPEN` → `HANDOFF_READY`).
- No message blocks capture or hotkey handling.
