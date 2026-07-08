"""Builds the Copilot summarisation prompt that is copied to the clipboard on stop.

The prompt is parameterised by the real screenshot count and interval so the AI knows
exactly what it is looking at (FR-016, SC-005). Pure string building — trivially testable.
See specs/001-meeting-capture/contracts/prompt-template.md.
"""

from __future__ import annotations


def build_summarisation_prompt(count: int, interval_seconds: int) -> str:
    """Return the accessibility prompt describing ``count`` screenshots taken every interval.

    Uses the singular word "screenshot" when exactly one was taken so the sentence reads
    naturally for the screen reader.
    """
    noun = "screenshot" if count == 1 else "screenshots"
    return (
        f"I'm attaching {count} {noun} taken every {interval_seconds} seconds during a "
        "meeting. My colleague is blind and this is her only record of what was shown "
        "visually. Please describe each distinct slide or screen in order, including all "
        "visible text, bullet points, chart descriptions, names, dates, and action items. "
        "End with a summary of key takeaways and any action items with owners."
    )
