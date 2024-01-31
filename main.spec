# -*- mode: python ; coding: utf-8 -*-

import os

def collect_subdirectories(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg", ".gif")):  # Add or remove file extensions as needed
                path = os.path.join(root, file)
                # Adjust the destination path as needed
                paths.append((path, os.path.relpath(root, '.')))
    return paths

# Collect all image directories and their files
image_paths = collect_subdirectories('.')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=image_paths + [
        ('sounds/*', 'sounds'), 
        ('fonts/*', 'fonts')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
