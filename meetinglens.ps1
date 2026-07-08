# MeetingLens — accessible, audio-first meeting capture, as a single PowerShell script.
#
# A no-exe edition for locked-down PCs: same behaviour as MeetingLens.exe — global hotkeys,
# spoken feedback, interval screen capture, and a guided Copilot handoff — using only .NET and
# SAPI that ship with Windows. Run in Windows PowerShell (powershell.exe, which is STA):
#
#   powershell -ExecutionPolicy Bypass -File meetinglens.ps1
#
# Hotkeys: Start Ctrl+Alt+S · Stop Ctrl+Alt+X · Status Ctrl+Alt+R · Save Ctrl+Alt+W · Quit Ctrl+Alt+Q
#
# -SelfTest runs a quick check of speech, capture, prompt, and config, then exits (no hotkeys).

param([switch]$SelfTest)

$ErrorActionPreference = "Stop"

# ----- constants -----------------------------------------------------------------------
$DEFAULT_INTERVAL = 45
$DEFAULT_URL = "https://copilot.microsoft.com"
$MOD_ALT = 0x0001; $MOD_CONTROL = 0x0002; $MOD_SHIFT = 0x0004; $MOD_WIN = 0x0008
$ID_START = 1; $ID_STOP = 2; $ID_STATUS = 3; $ID_SAVE = 4; $ID_QUIT = 5

# ----- session state -------------------------------------------------------------------
$script:isRecording = $false
$script:count = 0
$script:startTime = $null
$script:lastPrompt = $null
$script:interval = $DEFAULT_INTERVAL
$script:url = $DEFAULT_URL
$script:capturesFolder = Join-Path ([Environment]::GetFolderPath("Desktop")) "MeetingCaptures"
$script:notesFolder = [Environment]::GetFolderPath("Desktop")

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Offline Windows text-to-speech (SAPI). Async speak (flag 1) never blocks the message loop.
$script:voice = New-Object -ComObject SAPI.SpVoice

function Speak([string]$text, [switch]$Sync) {
    <# Speak a message aloud; async by default so hotkeys stay responsive. #>
    $flag = if ($Sync) { 0 } else { 1 }
    [void]$script:voice.Speak($text, $flag)
}

# ----- spoken messages (mirror of the exe's catalog) -----------------------------------
function Msg-Ready { "MeetingLens is ready. Press Control Alt S to start recording. Press Control Alt X to stop." }
function Msg-Started { "Meeting capture started. 0 screenshots taken so far." }
function Msg-Capture([int]$n) { "Screenshot $n taken." }
function Msg-Already([int]$n) { "Already recording. $n screenshots taken so far." }
function Msg-StatusRec([int]$n, [int]$m) { "Recording. $n screenshots taken. Session running $m minutes." }
function Msg-StatusIdle { "Not recording. Press Control Alt S to start." }
function Msg-Stopping([int]$n) { "Stopping capture. $n screenshots taken. Preparing your summary." }
function Msg-NothingRec { "Nothing is being recorded." }
function Msg-HandoffOpen { "Your browser is open with Copilot. Press Tab to reach the chat box, then press Control V to paste your prompt. Then attach your screenshots from the folder that just opened." }
function Msg-HandoffReady { "Your prompt is copied to clipboard. Your screenshots are in the folder that just opened. When Copilot finishes, copy its response and press Control Alt W to save it as your meeting notes." }
function Msg-NotesSaved { "Your meeting notes are saved to your Desktop and open in Notepad." }
function Msg-NothingToSave { "There is nothing on the clipboard to save." }
function Msg-PromptNotCopied { "That is still your prompt. Copy Copilot's response first, then press Control Alt W." }
function Msg-Quitting { "MeetingLens is closing. Goodbye." }

function Build-Prompt([int]$count, [int]$interval) {
    <# The parameterised Copilot summarisation prompt, singular-aware. #>
    $noun = if ($count -eq 1) { "screenshot" } else { "screenshots" }
    "I'm attaching $count $noun taken every $interval seconds during a meeting. " +
    "My colleague is blind and this is her only record of what was shown visually. " +
    "Please describe each distinct slide or screen in order, including all visible text, " +
    "bullet points, chart descriptions, names, dates, and action items. " +
    "End with a summary of key takeaways and any action items with owners."
}

function Take-Screenshot([string]$path) {
    <# Capture the primary screen to a PNG; return $false on failure so a frame can be skipped. #>
    try {
        $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose(); $bmp.Dispose()
        return $true
    } catch { return $false }
}

function Load-Config {
    <# Read config.txt next to the script if present; otherwise keep built-in defaults. #>
    if (-not $PSScriptRoot) { return }
    $path = Join-Path $PSScriptRoot "config.txt"
    if (-not (Test-Path $path)) { return }
    foreach ($line in Get-Content $path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
        $key, $value = $trimmed.Split("=", 2)
        switch ($key.Trim().ToLower()) {
            "interval_seconds" { if ($value -as [int] -and [int]$value -gt 0) { $script:interval = [int]$value } }
            "ai_chat_url"      { if ($value.Trim()) { $script:url = $value.Trim() } }
        }
    }
}

# ----- hotkey actions ------------------------------------------------------------------
function Start-Capture {
    if ($script:isRecording) { Speak (Msg-Already $script:count); return }
    New-Item -ItemType Directory -Force -Path $script:capturesFolder | Out-Null
    $script:isRecording = $true; $script:count = 0; $script:startTime = Get-Date
    Speak (Msg-Started)
    $script:timer.Interval = $script:interval * 1000
    $script:timer.Start()
}

function Capture-Tick {
    if (-not $script:isRecording) { return }
    $index = $script:count + 1
    $path = Join-Path $script:capturesFolder ("capture_{0:D3}.png" -f $index)
    if (-not (Take-Screenshot $path)) { return }  # skipped frame, session continues
    $script:count = $index
    Speak (Msg-Capture $script:count)
}

function Stop-Capture {
    if (-not $script:isRecording) { Speak (Msg-NothingRec); return }
    $script:timer.Stop(); $script:isRecording = $false
    Speak (Msg-Stopping $script:count)
    $script:lastPrompt = Build-Prompt $script:count $script:interval
    Set-Clipboard -Value $script:lastPrompt
    Start-Process $script:url
    Start-Process explorer.exe $script:capturesFolder
    Speak (Msg-HandoffOpen); Speak (Msg-HandoffReady)
}

function Read-Status {
    if ($script:isRecording) {
        $minutes = [int]((Get-Date) - $script:startTime).TotalMinutes
        Speak (Msg-StatusRec $script:count $minutes)
    } else { Speak (Msg-StatusIdle) }
}

function Save-Notes {
    $text = Get-Clipboard -Raw
    if (-not $text -or -not $text.Trim()) { Speak (Msg-NothingToSave); return }
    if ($script:lastPrompt -and $text -eq $script:lastPrompt) { Speak (Msg-PromptNotCopied); return }
    New-Item -ItemType Directory -Force -Path $script:notesFolder | Out-Null
    $name = "MeetingNotes_{0}.txt" -f (Get-Date -Format "yyyy-MM-dd_HH-mm")
    $path = Join-Path $script:notesFolder $name
    Set-Content -Path $path -Value $text -Encoding UTF8
    Start-Process notepad.exe $path
    Speak (Msg-NotesSaved)
}

function Quit-App {
    if ($script:isRecording) { $script:timer.Stop(); $script:isRecording = $false }
    foreach ($b in $ID_START, $ID_STOP, $ID_STATUS, $ID_SAVE, $ID_QUIT) {
        $script:form.Unreg($b)
    }
    # Speak async (a synchronous speak here would deadlock the STA message pump we are running
    # inside), then end the loop from a short timer so the goodbye has time to play.
    Speak (Msg-Quitting)
    $script:exitTimer = New-Object System.Windows.Forms.Timer
    $script:exitTimer.Interval = 2500
    $script:exitTimer.add_Tick({ [System.Windows.Forms.Application]::ExitThread() })
    $script:exitTimer.Start()
}

# ----- self-test path ------------------------------------------------------------------
if ($SelfTest) {
    $tmp = Join-Path $env:TEMP "meetinglens_selftest.png"
    $captured = Take-Screenshot $tmp
    $prompt1 = Build-Prompt 1 45
    $prompt18 = Build-Prompt 18 45
    Speak "MeetingLens self test." -Sync
    Write-Host "capture ok:        $captured ($(if (Test-Path $tmp) { (Get-Item $tmp).Length } else { 0 }) bytes)"
    Write-Host "singular prompt:   $([bool]($prompt1 -match '1 screenshot '))"
    Write-Host "plural prompt:     $([bool]($prompt18 -match '18 screenshots'))"
    Write-Host "prompt has owners: $([bool]($prompt18 -match 'owners'))"
    Write-Host "interval default:  $script:interval"
    Write-Host "url default:       $script:url"
    Remove-Item $tmp -ErrorAction SilentlyContinue
    Write-Host "SELF-TEST COMPLETE"
    return
}

# ----- hidden hotkey window + message loop ---------------------------------------------
Add-Type -ReferencedAssemblies System.Windows.Forms -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class HotkeyForm : Form {
    [DllImport("user32.dll")] public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);
    [DllImport("user32.dll")] public static extern bool UnregisterHotKey(IntPtr hWnd, int id);
    private const int WM_HOTKEY = 0x0312;
    public event Action<int> HotkeyPressed;

    public HotkeyForm() {
        this.ShowInTaskbar = false;
        this.FormBorderStyle = FormBorderStyle.FixedToolWindow;
        this.WindowState = FormWindowState.Minimized;
    }
    protected override void SetVisibleCore(bool value) { base.SetVisibleCore(false); }
    public bool Reg(int id, uint mods, uint vk) { return RegisterHotKey(this.Handle, id, mods, vk); }
    public void Unreg(int id) { UnregisterHotKey(this.Handle, id); }
    protected override void WndProc(ref Message m) {
        if (m.Msg == WM_HOTKEY && HotkeyPressed != null) HotkeyPressed(m.WParam.ToInt32());
        base.WndProc(ref m);
    }
}
"@

Load-Config

$script:form = New-Object HotkeyForm
$script:timer = New-Object System.Windows.Forms.Timer
$script:timer.add_Tick({ Capture-Tick })

$script:form.add_HotkeyPressed({
    param($id)
    switch ($id) {
        1 { Start-Capture }
        2 { Stop-Capture }
        3 { Read-Status }
        4 { Save-Notes }
        5 { Quit-App }
    }
})

# Force the window handle to exist, then register the five global hotkeys (Ctrl+Alt+<key>).
[void]$script:form.Handle
$mods = $MOD_CONTROL -bor $MOD_ALT
$bindings = @(
    @{ id = $ID_START;  vk = 0x53; name = "start" }   # S
    @{ id = $ID_STOP;   vk = 0x58; name = "stop" }    # X
    @{ id = $ID_STATUS; vk = 0x52; name = "status" }  # R
    @{ id = $ID_SAVE;   vk = 0x57; name = "save" }     # W
    @{ id = $ID_QUIT;   vk = 0x51; name = "quit" }     # Q
)
foreach ($b in $bindings) {
    if (-not $script:form.Reg($b.id, $mods, $b.vk)) {
        Speak "Warning. The hotkey for $($b.name) could not be registered. It may be in use by another program."
    }
}

Speak (Msg-Ready)
# A thread message loop (not Application.Run(form)) keeps the invisible hotkey window pumping
# WM_HOTKEY; Quit-App ends it with Application.ExitThread().
[System.Windows.Forms.Application]::Run()
$script:form.Dispose()
