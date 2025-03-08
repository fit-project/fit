#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import sys
import os
import shutil
import atexit
from PyQt6 import QtCore
from view.checks.check import Check
from view.dialog import Dialog, DialogButtonTypes

from common.utility import is_admin, resolve_path, get_platform

from common.constants.view.tasks import status
from common.constants.view.initial_checks import (
    USER_IS_NOT_ADMIN_TITLE,
    USER_IS_NOT_ADMIN_MSG,
)

MACOS_TEMP_ROOT_PRIV_DIR = "/tmp/__FIT__"
MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT = (
    "/tmp/fit_launch_fit_with_admin_privileges.sh"
)

if get_platform() == "macos" and is_admin():

    def clean_up_temp_fit_dir():
        if os.path.exists(MACOS_TEMP_ROOT_PRIV_DIR):
            shutil.rmtree(MACOS_TEMP_ROOT_PRIV_DIR, ignore_errors=True)

    atexit.register(clean_up_temp_fit_dir)


class AdminPrivilegesCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)

        if os.path.exists(MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT):
            os.remove(MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT)

    def __del__(self):
        if (
            hasattr(self, "process")
            and self.process.state() != QtCore.QProcess.ProcessState.NotRunning
        ):
            self.process.kill()
            self.process.waitForFinished()

    def run_check(self):
        if is_admin() is False:
            # dialog = Dialog(USER_IS_NOT_ADMIN_TITLE, USER_IS_NOT_ADMIN_MSG)
            # dialog.message.setStyleSheet("font-size: 13px;")
            # dialog.set_buttons_type(DialogButtonTypes.QUESTION)
            # dialog.right_button.clicked.connect(
            #     lambda: self.__run_fit_with_user_privileges(dialog)
            # )
            # dialog.left_button.clicked.connect(
            #     lambda: self.__run_fit_with_admin_privileges(dialog)
            # )
            # dialog.content_box.adjustSize()

            # dialog.exec()
            self.finished.emit(status.FAIL)
        else:
            self.finished.emit(status.SUCCESS)

    def __run_fit_with_user_privileges(self, dialog):
        dialog.close()
        self.finished.emit(status.FAIL)

    def __quit(self):
        try:
            self.__cleanup()
        except Exception as e:
            pass
        if hasattr(self, "process") and self.process is not None:
            self.process.kill()

        sys.exit(0)

    def __run_fit_with_admin_privileges(self, dialog=None):
        if dialog:
            dialog.close()

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(500, loop.quit)
        loop.exec()

        self.is_finsished = False

        current_app = self.__get_current_app_path()
        python_path = sys.executable

        if get_platform() == "macos":
            original_script = resolve_path(
                "assets/script/mac/launch_fit_with_admin_privileges.sh"
            )

            shutil.copy(original_script, MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT)
            os.chmod(MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT, 0o777)
            os.chown(MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT, os.getuid(), -1)

            launch_script = MACOS_TEMP_ADMIN_PRIVILEGES_LAUNCH_SCRIPT

            if getattr(sys, "frozen", False):
                args = ["", current_app]
            else:
                args = [python_path, current_app]

        elif get_platform() == "win":
            launch_script = "powershell.exe"
            # window_style = "Normal"
            # window_style = "Hidden"
            window_style = "Minimized"
            # window_style = "Maximized"

            powershell_args = (
                f"-NoProfile -ExecutionPolicy Bypass -File \"{resolve_path('assets/script/win/launch_fit_with_admin_privileges.ps1')}\" "
                f'-PythonPath "{python_path}" '
                f'-AppPath "{current_app}"'
            )

            args = [
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    f"Start-Process -FilePath 'powershell.exe' "
                    f"-ArgumentList '{powershell_args}' "
                    f"-WindowStyle {window_style}"
                ),
            ]

        elif sys.platform == "lin":
            launch_script = resolve_path(
                "assets/script/lin/launch_fit_with_admin_privileges.sh"
            )
            args = [python_path, current_app]
        else:
            if self.debug_mode:
                raise OSError("OS not supported.")

        self.process = QtCore.QProcess(self)

        self.process.started.connect(self.__on_process_started)
        self.process.errorOccurred.connect(self.__on_process_error)
        self.process.readyReadStandardError.connect(self.__capture_process_output)
        self.process.readyReadStandardOutput.connect(self.__capture_process_output)

        self.process_output = ""  # Buffer to store process output

        self.process.start(launch_script, args)

    def __on_process_started(self):
        QtCore.QTimer.singleShot(1000, self.__quit)

    def __capture_process_output(self):
        self.process_output += self.process.readAllStandardError().data().decode()
        self.process_output += self.process.readAllStandardOutput().data().decode()
        if self.debug_mode:
            print(self.process_output)

    def __cleanup(self):
        if (
            hasattr(self, "process")
            and self.process.state() != QtCore.QProcess.ProcessState.NotRunning
        ):
            self.process.terminate()
            self.process.waitForFinished()

    def __on_process_error(self, error):
        error_map = {
            QtCore.QProcess.ProcessError.FailedToStart: "Failed to start the process.",
            QtCore.QProcess.ProcessError.Crashed: "The process has crashed.",
            QtCore.QProcess.ProcessError.Timedout: "The process timed out.",
            QtCore.QProcess.ProcessError.WriteError: "Write error in the process.",
            QtCore.QProcess.ProcessError.ReadError: "Read error from the process.",
            QtCore.QProcess.ProcessError.UnknownError: "Unknown error.",
        }
        error_message = error_map.get(error, "Undefined error.")

        if self.debug_mode:
            print(f"Error during process execution: {error_message}")

    def __get_current_app_path(self):
        if getattr(sys, "frozen", False):
            return os.path.abspath(sys.executable)
        else:
            return os.path.abspath(sys.argv[0])

    def closeEvent(self, event):
        if (
            hasattr(self, "process")
            and self.process.state() != QtCore.QProcess.ProcessState.NotRunning
        ):
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
        event.accept()
