#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import subprocess

from PyQt6 import QtCore

import ffmpeg_downloader as ffdl
from view.checks.check import Check

from view.dialog import Dialog, DialogButtonTypes


from common.utility import is_cmd
from common.constants.view.tasks import status
from common.constants.view.initial_checks import (
    FFMPEG,
    WAR_FFMPEG_NOT_INSTALLED,
)


class FFmpegInstalledCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run_check(self):
        if is_cmd("ffmpeg") is False:
            dialog = Dialog(
                FFMPEG,
                WAR_FFMPEG_NOT_INSTALLED,
            )
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.set_buttons_type(DialogButtonTypes.QUESTION)

            dialog.left_button.clicked.connect(
                lambda: self.__download_and_install_ffmpeg(dialog)
            )
            dialog.right_button.clicked.connect(lambda: self.__not_install(dialog))

            dialog.exec()
        else:
            self.finished.emit(status.SUCCESS)

    def __not_install(self, dialog=None):
        if dialog:
            dialog.close()
        self.finished.emit(status.FAIL)

    def __download_and_install_ffmpeg(self, dialog=None):
        is_ffmpeg_installed = False

        if dialog:
            dialog.close()

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(500, loop.quit)
        loop.exec()

        ffmpeg_istaller = "ffdl-gui"
        if is_cmd(ffmpeg_istaller):
            result = subprocess.run(ffmpeg_istaller, stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                is_ffmpeg_installed = True

        if is_ffmpeg_installed is True:
            ffdl.add_path()
            self.finished.emit(status.SUCCESS)
