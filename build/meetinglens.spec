# PyInstaller build spec — produces ONE self-contained MeetingLens.exe.
#
# Delivery is intentionally as simple as Windows allows, because the user is visually
# impaired: a single file. Download MeetingLens.exe, pin it to the taskbar (or press Enter
# on it), and it runs. No unzip, no folder to navigate, no installer, no terminal.
#
# The exe writes its own editable config.txt beside itself on first run (see __main__),
# so nothing else needs to ship with it.
#
# Build locally (Article VIII — never GitHub Actions):
#   pip install pyinstaller
#   pyinstaller build/meetinglens.spec
# Output: dist/MeetingLens.exe

block_cipher = None

a = Analysis(
    ["../src/meetinglens/__main__.py"],
    pathex=["../src"],
    binaries=[],
    datas=[],
    hiddenimports=["comtypes", "pyttsx3.drivers", "pyttsx3.drivers.sapi5"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MeetingLens",
    onefile=True,
    console=False,  # tray + speech only; no console window
    disable_windowed_traceback=False,
)
