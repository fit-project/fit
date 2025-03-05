import os
import sys
import shutil

from pathlib import Path


def get_platform():
    platforms = {
        "linux": "lin",
        "linux1": "lin",
        "linux2": "lin",
        "darwin": "macos",
        "win32": "win",
    }

    if sys.platform not in platforms:
        return "other"

    return platforms[sys.platform]


def post_install():
    virtualenv_path = Path(os.environ["VIRTUAL_ENV"])

    if get_platform() == "macos":
        original_framework_path = (
            virtualenv_path
            / "lib/python3.11/site-packages/PyQt6/Qt6/lib/QtWebEngineCore.framework"
        )
        custom_framework_path = Path("INSERT-FRAMEWORK-PATH")

        if original_framework_path.exists() is False:
            print("ERROR: {} doesn't exist".format(original_framework_path))
            return

        if custom_framework_path.exists() is False:
            print("ERROR: {} doesn't exist".format(custom_framework_path))
            return

        try:
            print("INFO: Replacing the framework...")
            shutil.rmtree(original_framework_path)
            shutil.copytree(
                custom_framework_path,
                original_framework_path,
            )
            print("INFO: Framework replaced successfully!")
        except Exception as e:
            print(f"ERROR: An error occurred while replacing the file: {e}")


post_install()
