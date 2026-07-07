# Feature Specification: MeetingLens — Accessible Meeting Capture

**Feature Branch**: `001-meeting-capture`

**Created**: 2026-07-07

**Status**: Draft

**Input**: User description: "MeetingLens — Accessible Meeting Capture Tool. A blind user needs to independently capture visual meeting content (slides, shared screens, whiteboards) during video calls and receive a structured, screen-reader-friendly text summary of everything shown — with zero sighted assistance required. Audio-first, keyboard-only, tray-resident, global hotkeys, SAPI speech, periodic screenshots, Copilot handoff, save clipboard notes to Notepad."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture visual meeting content hands-free (Priority: P1)

A blind user joins a video call in which slides and shared screens are presented. Without touching a mouse or navigating any window, she presses a global hotkey to begin capture. The tool takes a screenshot of the primary screen at a fixed interval and speaks a short spoken confirmation after each one, so she always knows capture is working. When the meeting ends she presses another global hotkey to stop. Every image is saved to a predictable folder for later summarisation.

**Why this priority**: This is the irreducible core of the product. Without reliable, spoken, keyboard-driven capture there is nothing to summarise and no independence is gained. It delivers standalone value even before any summary handoff exists — the user ends the meeting with a complete visual record.

**Independent Test**: Start a capture session with the start hotkey while a slideshow plays in another focused application, wait through several intervals, then stop. Verify that spoken confirmations were heard at start, on each capture, and on stop, and that one image per interval exists in the capture folder.

**Acceptance Scenarios**:

1. **Given** the tool is running in the tray and no session is active, **When** the user presses the start hotkey while a video-call app has keyboard focus, **Then** a new capture session begins and the tool speaks a start confirmation announcing zero screenshots taken so far.
2. **Given** a capture session is active, **When** the configured interval elapses, **Then** the primary screen is captured, the image is saved to the capture folder, and the tool speaks the running screenshot count (e.g. "Screenshot 4 taken").
3. **Given** a capture session is active, **When** the user presses the stop hotkey, **Then** capture halts, the tool speaks the final screenshot count, and no further images are captured.
4. **Given** no session is active, **When** the user presses the start hotkey again, **Then** a fresh session begins with the counter reset to zero.

---

### User Story 2 - Guided handoff to an AI summariser (Priority: P2)

After stopping capture, the user needs to get her screenshots described by an AI assistant. The tool prepares everything for her: it places a ready-to-use, context-rich prompt on the clipboard, opens the AI chat page in the browser, opens the folder containing her screenshots so she can attach them, and speaks step-by-step instructions on how to paste the prompt and attach the images. No sighted help is needed to reach the point where the AI can produce a description.

**Why this priority**: This converts a folder of images into an accessible summary path. It depends on P1 having produced captures, but it is the step that realises the product's promise of an independent, screen-reader-friendly account of what was shown.

**Independent Test**: With a folder of captured images present, trigger the stop-and-summarise action and verify the clipboard contains the correctly worded prompt including the actual screenshot count and interval, the browser opens to the AI chat page, the capture folder opens in the file explorer, and spoken guidance describes the paste-and-attach steps.

**Acceptance Scenarios**:

1. **Given** a session has ended with N screenshots captured, **When** the stop-and-summarise action runs, **Then** the tool speaks that it is preparing the summary and announces the number of screenshots taken.
2. **Given** the summarise action is running, **When** it prepares the handoff, **Then** a prompt is placed on the clipboard that states the exact screenshot count and capture interval and requests an ordered, per-screen description including all visible text, names, dates, chart descriptions, and action items with owners.
3. **Given** the summarise action is running, **When** the handoff completes, **Then** the AI chat page is opened in the browser and the capture folder is opened in the file explorer.
4. **Given** the handoff has completed, **When** the tool finishes speaking, **Then** the user has heard clear instructions to paste the prompt, attach the screenshots, and later save the AI response with the save hotkey.

---

### User Story 3 - Save the AI response as accessible meeting notes (Priority: P3)

Once the AI produces its description, the user copies the response to the clipboard and presses a global hotkey. The tool saves the clipboard text as a timestamped notes file to a predictable location and opens it in a plain-text editor so her screen reader can read it immediately. She now has a permanent, accessible record.

**Why this priority**: It closes the loop into a durable, re-readable artefact. It depends on the earlier stories but is separable — the handoff in P2 is still useful even if the user saves the response manually.

**Independent Test**: Place representative text on the clipboard, press the save hotkey, and verify a timestamped notes file is written to the expected location, opened in a plain-text editor, and that a spoken confirmation is heard.

**Acceptance Scenarios**:

1. **Given** the clipboard contains text, **When** the user presses the save hotkey, **Then** the clipboard text is written to a notes file whose name includes the current date and time.
2. **Given** the notes file has been written, **When** saving completes, **Then** the file opens in a plain-text editor and the tool speaks a confirmation that the notes are saved and open.
3. **Given** the clipboard is empty or contains no text, **When** the user presses the save hotkey, **Then** the tool speaks that there is nothing to save and does not create an empty file.

---

### User Story 4 - Check status and adjust behaviour without sighted help (Priority: P3)

At any time the user can press a status hotkey to hear whether a session is running, how many screenshots have been taken, and how long the session has been going. Separately, all hotkeys and the capture interval can be changed by editing a plain-text configuration file that her screen reader can read and edit.

**Why this priority**: Reassurance and control. Blind users cannot glance at a tray icon, so an on-demand spoken status and a screen-reader-editable configuration are what make the tool trustworthy and adaptable, but the product still functions with defaults if this is deferred.

**Independent Test**: During an active session press the status hotkey and confirm the spoken status includes recording state, screenshot count, and elapsed time; then change the interval in the configuration file, restart the tool, and confirm the new interval takes effect.

**Acceptance Scenarios**:

1. **Given** a session is active with several screenshots taken, **When** the user presses the status hotkey, **Then** the tool speaks that it is recording, the current screenshot count, and the elapsed session time.
2. **Given** no session is active, **When** the user presses the status hotkey, **Then** the tool speaks that it is idle and not currently recording.
3. **Given** the configuration file specifies a custom interval and hotkeys, **When** the tool starts, **Then** it uses those values in place of the defaults.
4. **Given** the tool starts for the first time, **When** it finishes initialising, **Then** it speaks a readiness confirmation naming the start and stop hotkeys.

---

### Edge Cases

- **Start pressed while already recording**: The tool should announce that a session is already in progress rather than silently starting a second one or losing the current count.
- **Stop or status pressed with no active session**: The tool should speak that nothing is being recorded instead of failing silently.
- **Screen locked, screen saver active, or display asleep at capture time**: The capture is skipped or produces a blank frame; the tool should not crash and should keep the session running for the next interval.
- **Capture folder or notes destination is missing**: The tool should create the needed folder rather than fail.
- **A hotkey the user configured is already claimed by another application**: The tool should report, by speech, that a hotkey could not be registered rather than starting in a silently broken state.
- **Malformed or partially edited configuration file**: The tool should fall back to defaults for any unreadable value and speak a warning, rather than refusing to start.
- **Save hotkey pressed when the browser/AI response was never copied**: Treated as the empty-clipboard case — spoken notice, no file written.
- **Very long session producing hundreds of screenshots**: The tool should continue capturing and counting without degraded responsiveness of the hotkeys or speech.
- **Only one monitor of a multi-monitor setup is captured**: Multi-monitor is out of scope for v1; the tool captures the primary screen and this limitation is understood.

## Requirements *(mandatory)*

### Functional Requirements

#### Runtime & Interface
- **FR-001**: The tool MUST run without any window the user has to navigate, presenting its entire interface through global hotkeys and spoken audio, with a tray indicator provided only as a visual cue for sighted bystanders.
- **FR-002**: The tool MUST require no mouse interaction for any of its own functions.
- **FR-003**: The tool MUST install and run without the user issuing any terminal commands (single installer or folder drop).
- **FR-004**: On first run the tool MUST speak a readiness confirmation that names the start and stop hotkeys.

#### Global Hotkeys
- **FR-005**: The tool MUST register global hotkeys that trigger even when another application (e.g. a video-call or browser window) has keyboard focus.
- **FR-006**: The tool MUST provide distinct hotkeys to start a capture session, stop-and-summarise, read status, and save notes.
- **FR-007**: If a hotkey cannot be registered (e.g. it is already claimed), the tool MUST announce the failure by speech rather than starting in a silently broken state.

#### Capture
- **FR-008**: On starting a session the tool MUST speak a start confirmation stating that capture has begun and the current screenshot count (zero).
- **FR-009**: While a session is active the tool MUST capture the primary screen at the configured interval (default 45 seconds).
- **FR-010**: After each capture the tool MUST save the image to a predictable, consistently named capture folder and speak the running screenshot count.
- **FR-011**: The tool MUST maintain, per session, a count of screenshots taken and the session start time.
- **FR-012**: Pressing start while a session is already active MUST NOT silently start a second session or reset the running count without notice; the tool MUST announce the already-recording state.

#### Status
- **FR-013**: On the status hotkey during an active session the tool MUST speak the recording state, the current screenshot count, and the elapsed session time.
- **FR-014**: On the status hotkey with no active session the tool MUST speak that it is idle.

#### Stop & Summary Handoff
- **FR-015**: On the stop-and-summarise hotkey the tool MUST end the session, speak the final screenshot count, and announce that it is preparing the summary.
- **FR-016**: The tool MUST place on the clipboard a summarisation prompt that includes the actual screenshot count and capture interval and requests an ordered, per-screen description covering visible text, bullet points, chart descriptions, names, dates, action items, and a closing set of key takeaways and action items with owners.
- **FR-017**: The tool MUST open the AI chat page in the user's browser and open the capture folder in the file explorer so screenshots can be attached.
- **FR-018**: After the handoff the tool MUST speak step-by-step guidance covering how to paste the prompt, attach the screenshots, and later save the response with the save hotkey.

#### Save Notes
- **FR-019**: On the save hotkey the tool MUST read the current clipboard text and, if non-empty, write it to a notes file whose name includes the current date and time.
- **FR-020**: After writing, the tool MUST open the notes file in a plain-text editor and speak a confirmation that notes are saved and open.
- **FR-021**: If the clipboard has no text, the tool MUST speak that there is nothing to save and MUST NOT create an empty file.

#### Configuration
- **FR-022**: The tool MUST read all hotkeys and the capture interval from a plain-text configuration file that a screen reader can read and edit.
- **FR-023**: The tool MUST apply sensible built-in defaults for any configuration value that is missing or unreadable, and speak a warning rather than refusing to start.

#### Robustness
- **FR-024**: The tool MUST create any missing capture or notes destination folder rather than failing.
- **FR-025**: A capture that cannot succeed (locked screen, display asleep) MUST NOT crash the tool or halt the session; the session MUST continue to the next interval.
- **FR-026**: All speech MUST function without an internet connection.

### Key Entities *(include if feature involves data)*

- **Capture Session**: A single recording period. Attributes: start time, running screenshot count, active/idle state, capture interval in effect. Ends when the stop-and-summarise action runs.
- **Screenshot**: One captured image of the primary screen, saved to the capture folder, ordered by capture time, associated with the session that produced it.
- **Summarisation Prompt**: The dynamically composed instruction text placed on the clipboard, parameterised by screenshot count and interval.
- **Meeting Notes File**: A timestamped plain-text file containing the AI response text saved from the clipboard.
- **Configuration**: The plain-text set of user-adjustable values — capture interval and the four hotkeys — with built-in defaults.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A blind user can complete an entire capture-to-notes cycle — start, capture through a meeting, stop, hand off to the AI, and save the response — using only the keyboard and spoken feedback, with zero sighted assistance.
- **SC-002**: Every state change the user cares about (ready, started, each capture, status, stopping, saved, and any error) is announced by speech within 2 seconds of the triggering event.
- **SC-003**: Global hotkeys respond correctly in at least 99% of presses while a video-call application or browser holds keyboard focus.
- **SC-004**: During an active session, exactly one image per configured interval is saved, with no more than one interval's worth of drift over a 60-minute session.
- **SC-005**: The clipboard prompt after stop always states the correct screenshot count and interval matching that session.
- **SC-006**: Saved notes files are readable by a screen reader immediately on open in 100% of saves where the clipboard contained text.
- **SC-007**: A first-time user, following only spoken instructions, reaches the point of a saved meeting-notes file on her first attempt without external help.
- **SC-008**: The tool starts and operates with no internet connection for all capture, speech, status, and save functions.

## Assumptions

- **Single user platform**: The tool targets a desktop operating system with a system tray, an installed browser for the AI chat page, a plain-text editor, and offline text-to-speech available — matching the described environment.
- **AI summariser is external and manual**: v1 does not call any AI API, does not automate the browser, and does not auto-attach images. The user pastes the prompt and attaches screenshots herself; the tool only prepares and guides.
- **Primary screen only**: Multi-monitor capture is out of scope for v1; the tool captures the primary display.
- **No meeting detection**: The tool does not detect or integrate with any specific video-call application; the user controls sessions entirely by hotkey.
- **Predictable locations**: Captured screenshots and saved notes go to well-known, consistently named folders (a dedicated captures folder and the user's desktop) so the user can find and attach them; folders are created if absent.
- **Default interval and hotkeys**: 45-second interval and the four described hotkeys are the shipped defaults, all overridable via the configuration file.
- **Filename timestamps**: Notes filenames embed the local date and time so repeated saves do not overwrite one another.
- **Session model**: One active session at a time; starting is only meaningful when idle, stopping/status only meaningful with context, each handled with a spoken response.
