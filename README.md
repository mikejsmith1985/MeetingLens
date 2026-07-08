# MeetingLens

Accessible, audio-first meeting capture for blind users. MeetingLens lives in the system
tray and is driven entirely by global hotkeys and spoken feedback — no window to navigate,
no mouse required. It screenshots your primary screen on an interval during a call, then
hands the images off to Copilot with a ready-made prompt so you get a screen-reader-friendly
summary of everything that was shown.

## Install (end user)

Unzip the release and double-click `MeetingLens.exe`. No terminal, no Python. On first run
it speaks: *"MeetingLens is ready. Press Control Alt S to start recording. Press Control Alt X
to stop."*

## Hotkeys

| Action | Hotkey |
|---|---|
| Start capture | `Ctrl + Alt + S` |
| Stop + generate summary | `Ctrl + Alt + X` |
| Read status aloud | `Ctrl + Alt + R` |
| Save clipboard as notes | `Ctrl + Alt + W` |
| Quit | `Ctrl + Alt + Q` |

All hotkeys are global — they work even when Teams, Zoom, or your browser has focus. Edit
`config.txt` (in Notepad) to change any hotkey, the capture interval, or the AI chat URL.

## Flow

1. `Ctrl+Alt+S` — capture starts; each screenshot is announced and saved to
   `Desktop\MeetingCaptures\`.
2. `Ctrl+Alt+X` — capture stops; the summarisation prompt is copied to your clipboard, your
   browser opens Copilot, and the captures folder opens for attaching. Follow the spoken steps.
3. Copy Copilot's response, then `Ctrl+Alt+W` — the response is saved as a timestamped
   `MeetingNotes_*.txt` on your Desktop and opened in Notepad.

## Develop

```powershell
pip install -r requirements.txt
python -m meetinglens          # run
pytest tests/unit -q           # fast, fully-mocked (<10ms each)
pytest tests/integration -q    # real Windows APIs (SAPI, screen, clipboard)
```

Architecture: pure domain modules (`session`, `config`, `prompt`, `notes`, `handoff`, `app`)
import nothing external; every OS/library touchpoint lives behind an adapter in
`src/meetinglens/adapters/`. See `specs/001-meeting-capture/` for the full spec, plan, and tasks.

## Build the distributable

```powershell
pip install pyinstaller
pyinstaller build/meetinglens.spec
# → dist/MeetingLens/  (zip and ship)
```
