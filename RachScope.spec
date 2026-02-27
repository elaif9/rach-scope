# -*- mode: python ; coding: utf-8 -*-
"""
RachScope - Coffee Roasting Monitoring Application
PyInstaller specification file for building executable
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Blocklist: These modules are not used and should be excluded
blocklist = [
    'matplotlib',
    'scipy',
    'PIL',
    'Pillow',
]

# Collect data files and submodules
datas = [
    ('assets', 'assets'),  # Include assets folder
]

# Collect all hidden imports
hiddenimports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'pyqtgraph',
    'pymodbus.client',
    'pymodbus.exceptions',
    'numpy',
    'pandas',
]

# Binary includes
binaries = []

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=blocklist,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RachScope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here: 'assets/icon.ico' for Windows, 'assets/icon.icns' for MacOS
)
