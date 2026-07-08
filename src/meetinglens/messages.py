"""Spoken-message catalog: the exact text MeetingLens speaks for every state change.

Keeping every phrase in one place means the wording a blind user depends on is easy
to audit and change, and the tests can assert against these builders rather than
duplicating string literals. See specs/001-meeting-capture/contracts/spoken-messages.md.
"""


def ready() -> str:
    """Spoken once at first run so the user knows the tool is listening (FR-004)."""
    return (
        "MeetingLens is ready. Press Control Alt S to start recording. "
        "Press Control Alt X to stop."
    )


def started() -> str:
    """Spoken when a fresh capture session begins."""
    return "Meeting capture started. 0 screenshots taken so far."


def capture_taken(count: int) -> str:
    """Spoken after each successful screenshot, announcing the running total."""
    return f"Screenshot {count} taken."


def already_recording(count: int) -> str:
    """Spoken when start is pressed while already recording, so no session is lost."""
    return f"Already recording. {count} screenshots taken so far."


def status_recording(count: int, minutes: int) -> str:
    """Spoken on the status hotkey during an active session."""
    return f"Recording. {count} screenshots taken. Session running {minutes} minutes."


def status_idle() -> str:
    """Spoken on the status hotkey when no session is active."""
    return "Not recording. Press Control Alt S to start."


def stopping(count: int) -> str:
    """Spoken when a session stops and the summary handoff is about to begin."""
    return f"Stopping capture. {count} screenshots taken. Preparing your summary."


def nothing_recording() -> str:
    """Spoken when stop is pressed but nothing is being recorded."""
    return "Nothing is being recorded."


def handoff_open() -> str:
    """Spoken after the browser opens, guiding the user to paste the prompt."""
    return (
        "Your browser is open with Copilot. Press Tab to reach the chat box, then press "
        "Control V to paste your prompt. Then attach your screenshots from the folder that "
        "just opened."
    )


def handoff_ready() -> str:
    """Spoken after the clipboard and folder are ready, guiding the save step."""
    return (
        "Your prompt is copied to clipboard. Your screenshots are in the folder that just "
        "opened. When Copilot finishes, copy its response and press Control Alt W to save it "
        "as your meeting notes."
    )


def notes_saved() -> str:
    """Spoken after meeting notes are written and opened in Notepad."""
    return "Your meeting notes are saved to your Desktop and open in Notepad."


def nothing_to_save() -> str:
    """Spoken when the save hotkey is pressed with an empty clipboard."""
    return "There is nothing on the clipboard to save."


def prompt_not_copied() -> str:
    """Spoken when the clipboard still holds our handoff prompt instead of a response (FR-027)."""
    return (
        "That is still your prompt. Copy Copilot's response first, then press Control Alt W."
    )


def quitting() -> str:
    """Spoken as the tool exits from the quit hotkey (FR-028)."""
    return "MeetingLens is closing. Goodbye."


def config_warning(setting: str) -> str:
    """Spoken once per bad configuration value, naming the setting that fell back to default."""
    return f"Warning. {setting} in your config file could not be read. Using the default."


def hotkey_failed(action: str) -> str:
    """Spoken when a hotkey cannot be registered, naming the action it was for (FR-007)."""
    return (
        f"Warning. The hotkey for {action} could not be registered. "
        "It may be in use by another program."
    )
