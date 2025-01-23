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
    icon='../icon.png',
    bundle_identifier="org.fit-project.fit",
    version=version,
)

dmg_folder = Path("./dist/fit_dmg")
os.makedirs(dmg_folder, exist_ok=True)
move("./dist/Fit.app", dmg_folder / "Fit.app")

dmg_file = dmg_folder / f"fit-portable-{version}-macos-{os.uname().machine}.dmg"

print("Building", dmg_file)
try:
    os.symlink("/Applications", dmg_folder / "Applications")

    subprocess.run([
        "hdiutil", "create", 
        "-volname", "FitApp", 
        "-srcfolder", str(dmg_folder), 
        "-ov", "-format", "UDZO", 
        str(dmg_file)
    ], check=True)
except FileExistsError:
    print("The symbolic link already exists.")
except subprocess.CalledProcessError as e:
    print(f"Error while creating the DMG: {e}")
except Exception as e:
    print(f"Unexpected error while creating the DMG: {e}")