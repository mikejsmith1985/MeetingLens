# Contract: Summarisation Prompt Template

Built on stop, copied to the clipboard (FR-016). `{count}` and `{interval}` are substituted from the just-ended session; the resulting text MUST contain both values (SC-005).

## Template

```text
I'm attaching {count} screenshots taken every {interval} seconds during a meeting.
My colleague is blind and this is her only record of what was shown visually.
Please describe each distinct slide or screen in order, including all visible text,
bullet points, chart descriptions, names, dates, and action items.
End with a summary of key takeaways and any action items with owners.
```

## Required content (assertions)

- Contains the literal screenshot count `{count}`.
- Contains the literal interval `{interval}`.
- Requests **ordered, per-screen** description.
- Requests: visible text, bullet points, chart descriptions, names, dates, action items.
- Requests a closing summary of key takeaways and action items **with owners**.

## Notes

- Singular/plural grace: `{count} screenshots` is acceptable even when count is 1 (v1 keeps it simple).
- The prompt is text-only; the tool does not attach images (out of scope v1) — attachment is done manually by the user.
- The exact prompt string written to the clipboard MUST be retained (as `last_handoff_prompt`) so the save action can detect it still on the clipboard and refuse to save it as notes (FR-027, see `spoken-messages.md` `PROMPT_NOT_COPIED`).
