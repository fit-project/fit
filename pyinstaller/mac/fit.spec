# -*- mode: python ; coding: utf-8 -*-
datas = [('../../assets', './assets'), ('../../ui', './ui'), ('../../icon.ico', './icon.ico')]

a = Analysis(
    ['../../fit.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=["./pyinstaller/windows/hooks"],
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
    name='fit',
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
    icon=['../icon.png'],
)
app = BUNDLE(
    exe,
    name='fit.app',
    icon='../icon.png',
    bundle_identifier=None,
)
