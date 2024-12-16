#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import sys
import subprocess
import shutil
import os

from PyQt6 import QtWidgets, QtCore

from view.dialog import Dialog, DialogButtonTypes
from view.checks.download_and_save import DownloadAndSave
from view.error import Error as ErrorView
from view.checks.check import Check

from common.constants.view.tasks import status

from common.utility import (
    has_new_portable_version,
    get_portable_download_url,
    get_platform,
    resolve_path,
)

from common.constants.view.tasks import status
from common.constants.view.initial_checks import (
    FIT_NEW_VERSION_TITLE,
    FIT_NEW_VERSION_MSG,
    DOWNLOAD_URL_ERROR,
    FIT_NEW_VERSION_DOWNLOAD_TITLE,
    FIT_NEW_VERSION_DOWNLOAD_MSG,
    FIT_NEW_VERSION_DOWNLOAD_ERROR,
    FIT_NEW_VERSION_UNZIP_ERROR,
    FIT_NEW_VERSION_EXCUTE_ERROR,
    FIT_NEW_VERSION_INSTALLATION_TITLE,
    FIT_NEW_VERSION_INSTALLATION_ERROR,
    FIT_NEW_VERSION_INSTALLATION_SUCCESS,
)


class NewPortableVersionCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run_check(self):
        if getattr(sys, "frozen", False) and has_new_portable_version():
            dialog = Dialog(
                FIT_NEW_VERSION_TITLE,
                FIT_NEW_VERSION_MSG,
            )
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.set_buttons_type(DialogButtonTypes.QUESTION)
            dialog.right_button.clicked.connect(lambda: self.__not_install(dialog))
            dialog.left_button.clicked.connect(
                lambda: self.__download_portable_version(dialog)
            )

            dialog.exec()
        else:
            self.finished.emit(status.SUCCESS)

    def __not_install(self, dialog=None):
        if dialog:
            dialog.close()
        self.finished.emit(status.SUCCESS)

    def __download_portable_version(self, dialog=None):
        if dialog:
            dialog.close()
        try:
            url = get_portable_download_url()

            if url is None:
                error_dlg = ErrorView(
                    QtWidgets.QMessageBox.Icon.Critical,
                    FIT_NEW_VERSION_DOWNLOAD_TITLE,
                    DOWNLOAD_URL_ERROR,
                )
                error_dlg.exec()
            donwload_and_save = DownloadAndSave(
                url, FIT_NEW_VERSION_DOWNLOAD_TITLE, FIT_NEW_VERSION_DOWNLOAD_MSG
            )
            # donwload_and_save.finished.connect(self.__unzip_portable_zipfile)
            donwload_and_save.finished.connect(self.__install_portable)
            donwload_and_save.rejected.connect(self.__not_install)
            donwload_and_save.exec()
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                FIT_NEW_VERSION_DOWNLOAD_TITLE,
                FIT_NEW_VERSION_DOWNLOAD_ERROR,
                str(e),
            )
            error_dlg.exec()

    def __install_portable(self, file_path):

        app_dir = os.path.abspath(sys.executable)

        if get_platform() == "macos":
            if app_dir.endswith(".app/Contents/MacOS"):
                app_dir = os.path.dirname(os.path.dirname(os.path.dirname(app_dir)))
                launch_script = resolve_path(
                    "assets/script/mac/install_new_portable_version.sh"
                )
                args = [app_dir, file_path]
            elif get_platform() == "win":
                app_dir = os.path.dirname(app_dir)
                launch_script = resolve_path(
                    "assets/script/win/install_new_portable_version.ps1"
                )
                args = [app_dir, file_path]
            elif sys.platform == "lin":
                app_dir = os.path.dirname(app_dir)
                launch_script = resolve_path(
                    "assets/script/lin/install_new_portable_version.sh"
                )
                args = [app_dir, file_path]

        self.process = QtCore.QProcess(self)
        self.process.errorOccurred.connect(self.__on_process_error)

        self.process.readyReadStandardError.connect(self.__capture_process_output)
        self.process.readyReadStandardOutput.connect(self.__capture_process_output)

        self.process_output = ""  # Buffer to store process output

        self.process.start(launch_script, args)

        self.process.waitForFinished()

        exit_code = self.process.exitCode()
        if exit_code == 0:
            message = FIT_NEW_VERSION_INSTALLATION_SUCCESS
            severity = QtWidgets.QMessageBox.Icon.Information
        else:
            message = FIT_NEW_VERSION_INSTALLATION_ERROR
            severity = QtWidgets.QMessageBox.Icon.Warning

        dialog = Dialog(
            FIT_NEW_VERSION_INSTALLATION_TITLE,
            message,
            "",
            severity,
        )

        dialog.message.setStyleSheet("font-size: 13px;")
        dialog.set_buttons_type(DialogButtonTypes.MESSAGE)
        if exit_code == 0:
            dialog.right_button.clicked.connect(lambda: dialog.close())
            dialog.right_button.clicked.connect(self.__quit)
        else:
            dialog.right_button.clicked.connect(lambda: dialog.close())
            dialog.right_button.clicked.connect(
                lambda: self.finished.emit(status.SUCCESS)
            )

        dialog.content_box.adjustSize()

        dialog.exec()

    def __quit(self):
        try:
            self.__cleanup()
        except Exception as e:
            pass
        if hasattr(self, "process") and self.process is not None:
            self.process.kill()

        sys.exit(0)

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

    def __capture_process_output(self):
        self.process_output += self.process.readAllStandardError().data().decode()
        self.process_output += self.process.readAllStandardOutput().data().decode()
        if self.debug_mode:
            print(self.process_output)