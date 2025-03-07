# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['fit.py'],
    pathex=[],
    binaries=[],
    datas=[('./assets', 'assets'), ('./ui', 'ui'), ('./icon.ico', 'icon.ico'), ('./pyinstaller/windows/whois/data', 'whois/data')],
    hiddenimports=['reportlab.graphics.barcode.code128', 'view.acquisition', 'view.checks', 'view.configurations', 'view.tasks', 'numpy'],
    hookspath=['./pyinstaller/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='fit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['pyinstaller\\icon.png'],
    append_pkg=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='fit',
)
