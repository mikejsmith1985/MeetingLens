# Builds the single MeetingLens.exe and publishes it as a GitHub Release asset.
#
# Release runs locally only (constitution Article VIII — never GitHub Actions). The goal is
# an insanely simple download for a visually impaired user: one MeetingLens.exe attached to
# the release, which they download and pin to the taskbar.
#
# Usage:
#   ./scripts/local-release.ps1 -Version v1.0.0
param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "==> Installing build dependency (pyinstaller)"
python -m pip install --quiet --user pyinstaller

Write-Host "==> Building single-file MeetingLens.exe"
python -m PyInstaller --clean --noconfirm build/meetinglens.spec

$exe = Join-Path $repoRoot "dist/MeetingLens.exe"
if (-not (Test-Path $exe)) {
    throw "Build did not produce $exe"
}
Write-Host "==> Built $exe ($([math]::Round((Get-Item $exe).Length / 1MB, 1)) MB)"

Write-Host "==> Tagging $Version"
git tag $Version
git push origin $Version

Write-Host "==> Creating GitHub release $Version with the exe attached"
gh release create $Version $exe `
    --title "MeetingLens $Version" `
    --notes "Download MeetingLens.exe, then pin it to your taskbar (or press Enter on it) to run. No install required. On first run it says: 'MeetingLens is ready. Press Control Alt S to start recording. Press Control Alt X to stop.'"

Write-Host "==> Done. Users can download MeetingLens.exe from the release page."
