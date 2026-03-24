# -*- mode: python ; coding: utf-8 -*-

block_cipher = None  # Define block_cipher as None since we are not using encryption

a = Analysis(
    ['tim_gui.py', 'tim_core.py'],
    pathex=['.'],
    binaries=[],  # If you need additional binaries, add them here
    datas=[('style.qss', '.'),  # Add the QSS file here
           ('tim_core.py', '.')],  # Ensure tim_core.py is bundled with the executable
    hiddenimports=[],  # Add hidden imports if needed
    hookspath=[],  # If you have any hooks, specify their path here
    runtime_hooks=[],  # Any runtime hooks can go here
    excludes=[],  # Exclude unnecessary modules here
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # Set to None since we are not using any encryption
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bin2TIM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX for compression, set to False if you want to skip it
    upx_exclude=[],  # List of files to exclude from UPX compression
    runtime_tmpdir=None,
    console=False,  # Set to False for a GUI app (True if you want a terminal window)
    disable_windowed_traceback=False,  # Windowed traceback for errors
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)