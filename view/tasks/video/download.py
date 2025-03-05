#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from common.constants.view import video
from common.constants import error


class VideoDownloadWorker(QObject):
    download_finished = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def download(self):
        methods_to_execute = self.options.get("methods_to_execute")
        controller = self.options.get("video_controller")

        controller.set_dir(self.options.get("url_dir"))

        for method in methods_to_execute:
            method = getattr(controller, method)
            try:
                method()
            except Exception as e:
                self.error.emit(
                    {
                        "title": video.INVALID_URL,
                        "msg": error.INVALID_URL,
                        "details": str(e),
                    }
                )
            else:
                self.progress.emit()

        self.download_finished.emit()
