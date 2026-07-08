# MeetingLens

Accessible, audio-first meeting capture for blind users. MeetingLens lives in the system
tray and is driven entirely by global hotkeys and spoken feedback — no window to navigate,
no mouse required. It screenshots your primary screen on an interval during a call, then
hands the images off to Copilot with a ready-made prompt so you get a screen-reader-friendly
summary of everything that was shown.

## Install (end user) — one file, no install

1. Download **`MeetingLens.exe`** from the [Releases page](../../releases/latest).
2. Save it anywhere (your Desktop is fine).
3. To keep it handy: press the Applications/Menu key on the file and choose **Pin to taskbar**.
   Now it is always one keypress away.
4. Press **Enter** on it (or click it) to run.

That is the entire install — no unzip, no folder to open, no setup wizard, no terminal, no
Python. On first run MeetingLens speaks: *"MeetingLens is ready. Press Control Alt S to start
recording. Press Control Alt X to stop."* and quietly writes an editable `config.txt` next to
itself in case you ever want to change a hotkey.

## Web edition (nothing to download): just open a link

The easiest option for a locked-down work PC — it's a website, so nothing is downloaded,
installed, or blocked, and it works with the screen reader you already use:

**→ https://mikejsmith1985.github.io/MeetingLens/**

Open it in Microsoft Edge or Chrome, press **Start capture**, and choose **Entire Screen**.
It screenshots your screen on an interval (speaking each one aloud) while you sit in your
meeting; when you press **Stop**, it downloads the screenshots, copies the Copilot prompt to
your clipboard, and opens Copilot for you.

Trade-off vs. the app: the Start/Stop buttons only respond when the MeetingLens tab is focused
(there are no system-wide hotkeys in a browser), and you grant screen-sharing once per meeting.
Capture itself runs on its own in the background once started.

## No-exe edition (locked-down PCs): `meetinglens.ps1`

If your workplace blocks downloading `.exe` files, use the PowerShell edition — a single text
script with the **same behaviour, including real global hotkeys** (it uses only .NET and the
Windows speech engine, nothing to install).

**Run it** in Windows PowerShell (`powershell.exe`), one of:

```powershell
# A) paste-and-run straight from GitHub (nothing saved to disk):
irm https://raw.githubusercontent.com/mikejsmith1985/MeetingLens/main/meetinglens.ps1 | iex

# B) or save meetinglens.ps1 anywhere and run it:
powershell -ExecutionPolicy Bypass -File meetinglens.ps1
```

Same hotkeys as below. To stop it, press `Ctrl+Alt+Q`. If your PC enforces *Constrained Language
Mode* (some corporate machines do), the script cannot register global hotkeys — use the web
edition instead. Quick self-check: `powershell -File meetinglens.ps1 -SelfTest` prints a report
and exits without registering anything.

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

## Build & release the distributable

```powershell
pip install pyinstaller
pyinstaller build/meetinglens.spec        # → dist/MeetingLens.exe (single file)

# Or build + publish a GitHub release with the exe attached (local pipeline only):
./scripts/local-release.ps1 -Version v1.0.0
```
