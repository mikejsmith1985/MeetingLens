"""Launcher adapter: opens the browser, the captures folder, and saved notes.

Uses only the standard library so there is no extra dependency, and relies on the user's
default handlers for each target (FR-017).
"""

from __future__ import annotations

import os
import webbrowser


class LauncherAdapter:
    """Opens URLs, folders, and files with the operating system's default handlers."""

    def open_url(self, url: str) -> None:
        """Open ``url`` in the user's default browser (the AI chat page)."""
        webbrowser.open(url)

    def open_folder(self, path: str) -> None:
        """Open ``path`` in the file explorer so screenshots can be attached."""
        os.startfile(path)  # noqa: S606 - opening a known local folder with the shell.

    def open_file(self, path: str) -> None:
        """Open ``path`` in its default handler (Notepad for the saved notes text file)."""
        os.startfile(path)  # noqa: S606 - opening a file we just wrote.
