import runpy
import os
import stat
import subprocess
from pathlib import Path
from shutil import copy, move

datas = [
    ('../../assets/config.ini', './assets/config.ini'),
    ('../../assets/templates/front.html', './assets/templates/front.html'),
    ('../../assets/templates/template_verification.html', './assets/templates/template_verification.html'),
    ('../../assets/templates/template_pec.html', './assets/templates/template_pec.html'),
    ('../../assets/templates/template_web.html', './assets/templates/template_web.html'),
    ('../../assets/templates/template_web_no_whois.html', './assets/templates/template_web_no_whois.html'),
    ('../../assets/templates/template_email.html', './assets/templates/template_email.html'),
    ('../../assets/branding/FIT-640.png', './assets/branding/FIT-640.png'),
    ('../../assets/svg/FIT.svg', './assets/svg/FIT.svg'),
    ('../../assets/images/no-preview.png', './assets/images/no-preview.png'),
    ('../../assets/images/loader.gif', './assets/images/loader.gif'),
    ('../../ui', './ui'),
    ('../../icon.ico', './icon.ico'),
    ("../windows/whois/data", "./whois/data")
]


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