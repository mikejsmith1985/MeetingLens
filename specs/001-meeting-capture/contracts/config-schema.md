# Contract: `config.txt`

Plain-text, screen-reader-editable, one `key=value` per line. Lines beginning `#` are comments; blank lines ignored; keys case-insensitive; whitespace around `=` trimmed. Unknown keys are ignored (spoken warning). Any missing/invalid value falls back to the default and produces exactly one spoken warning at startup (FR-023).

## Keys

| Key | Type | Default | Notes |
|---|---|---|---|
| `interval_seconds` | integer > 0 | `45` | Capture cadence |
| `hotkey_start` | chord | `Ctrl+Alt+S` | Start session |
| `hotkey_stop` | chord | `Ctrl+Alt+X` | Stop + summarise |
| `hotkey_status` | chord | `Ctrl+Alt+R` | Speak status |
| `hotkey_save` | chord | `Ctrl+Alt+W` | Save clipboard → notes |
| `ai_chat_url` | URL | `https://www.bing.com/chat` | Opened on stop |
| `captures_folder` | path | `%USERPROFILE%\Desktop\MeetingCaptures` | Auto-created |
| `notes_folder` | path | `%USERPROFILE%\Desktop` | Auto-created |

Chord grammar: `Modifier(+Modifier)*+Key`, modifiers ∈ {`Ctrl`,`Alt`,`Shift`,`Win`}, case-insensitive.

## Shipped default `config.txt`

```text
# MeetingLens configuration — edit in Notepad, then restart MeetingLens.
# Time between screenshots, in seconds.
interval_seconds=45
# Global hotkeys (work even when Teams/Zoom/Edge has focus).
hotkey_start=Ctrl+Alt+S
hotkey_stop=Ctrl+Alt+X
hotkey_status=Ctrl+Alt+R
hotkey_save=Ctrl+Alt+W
# Where the summary is generated and where screenshots are stored.
ai_chat_url=https://www.bing.com/chat
```

## Validation contract

- Invalid `interval_seconds` (non-numeric or ≤0) → `45` + warning.
- Unparseable hotkey chord → per-key default + warning.
- A hotkey that fails OS registration (already claimed) → spoken failure naming the action (FR-007); tool keeps running with the remaining hotkeys.
