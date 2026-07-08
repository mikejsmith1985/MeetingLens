"""Primary-screen capture adapter over Pillow's ImageGrab.

Screenshots are saved as lossless PNG so slide text stays legible for the AI to describe.
A capture that fails (locked screen, sleeping display) is reported as ``False`` rather than
raising, so the session can skip the frame and carry on (FR-025).
"""

from __future__ import annotations

from PIL import ImageGrab


class ScreenCaptureAdapter:
    """Grabs the primary display and writes it to a PNG file."""

    def capture(self, path: str) -> bool:
        """Save a screenshot of the primary screen to ``path``; return whether it succeeded."""
        try:
            image = ImageGrab.grab()
            image.save(path, "PNG")
            return True
        except Exception:
            # Locked screen or sleeping display — signal a skipped frame, do not crash.
            return False
