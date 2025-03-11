import runpy
import os
import stat
import subprocess
from pathlib import Path
from shutil import copy, move

datas = [('../../assets', './assets'), ('../../ui', './ui'), ('../../icon.ico', './icon.ico'), ("../windows/whois/data", "./whois/data")]

config = runpy.run_path("./pyinstaller/pre_build.py")
version = config.get("VERSION")

a = Analysis(
    ['../../fit.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=["./pyinstaller/hooks"],
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
    name='Fit.app',
    icon='../icon.icns',
    bundle_identifier="org.fit-project.fit",
    version=version,
)