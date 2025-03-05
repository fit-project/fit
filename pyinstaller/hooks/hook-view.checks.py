# FIT hook for PyInstaller

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("view.checks")
