# PyInstaller build spec — produces a folder-drop MeetingLens.exe (no terminal to run).
#
# Build locally (Article VIII — never GitHub Actions):
#   pip install pyinstaller
#   pyinstaller build/meetinglens.spec
# Output: dist/MeetingLens/  — zip this folder; the user unzips and double-clicks
# MeetingLens.exe. config.txt ships beside the exe so it is Notepad-editable in place.

block_cipher = None

a = Analysis(
    ["../src/meetinglens/__main__.py"],
    pathex=["../src"],
    binaries=[],
    datas=[("../config.txt", ".")],
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
    [],
    exclude_binaries=True,
    name="MeetingLens",
    console=False,  # tray + speech only; no console window
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="MeetingLens",
)
