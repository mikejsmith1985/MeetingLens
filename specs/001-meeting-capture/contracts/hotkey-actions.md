# Contract: Hotkey Actions

Five global hotkeys are the entire input surface (FR-005/FR-006). Each maps to one action on the `AppController`. Behaviour is state-dependent per `data-model.md`.

| Hotkey (default) | Action | When IDLE | When RECORDING |
|---|---|---|---|
| `Ctrl+Alt+S` | **Start** | Begin session, reset count, start timer, speak start confirmation | Speak "already recording" — no reset (FR-012) |
| `Ctrl+Alt+X` | **Stop + Summarise** | Speak "nothing being recorded" | End session, speak final count, run handoff (FR-015–FR-018) |
| `Ctrl+Alt+R` | **Status** | Speak idle (FR-014) | Speak recording + count + elapsed (FR-013) |
| `Ctrl+Alt+W` | **Save Notes** | Clipboard→notes file, "nothing to save", or "copy the response first" (FR-019–FR-021, FR-027) | Same — save works regardless of session state |
| `Ctrl+Alt+Q` | **Quit** | Speak `QUIT`, exit (FR-028) | Stop the session first, then speak `QUIT` and exit |

## Action guarantees

- **Non-blocking**: an action enqueues speech and returns fast; it never blocks the capture timer or the next hotkey (SC-002, SC-003).
- **Idempotent-safe**: repeated presses in the same state produce the same guarded outcome (no double sessions, no duplicate resets).
- **Save independent of session**: `Ctrl+Alt+W` is valid at any time.
- **Registration failure**: if any hotkey cannot register, its failure is spoken at startup naming the action (FR-007); other hotkeys still function.

## First-run contract

On first launch after wiring hotkeys, the tool speaks a readiness confirmation naming the start and stop hotkeys (FR-004), e.g. *"MeetingLens is ready. Press Control Alt S to start recording. Press Control Alt X to stop."*
