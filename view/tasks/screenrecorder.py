#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import cv2
import numpy as np
import sys
import os


from PIL import ImageGrab
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox

from screeninfo import get_monitors

from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.configurations.tabs.screenrecorder.codec import Codec as CodecController
from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderController,
)

from common.constants import logger, details, state, status, tasks
from common.constants import error
from common.constants.view import screenrecorder


class ScreenRecorder(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.run = True
        self.destroyed.connect(self.stop)
        self.controller = CodecController()

    def set_options(self, options):
        self.width = get_monitors()[0].width
        self.height = get_monitors()[0].height
        codec = next(
            (
                item
                for item in self.controller.codec
                if item["id"] == options["codec_id"]
            )
        )
        self.codec = cv2.VideoWriter_fourcc(*codec["name"])

        # TO-DO find the right way to calculate dynamic FPS
        self.fps = options["fps"]
        self.filename = options["filename"]

    def start(self):
        self.out = cv2.VideoWriter(
            self.filename, self.codec, self.fps, (self.width, self.height)
        )

        self.started.emit()
        try:
            while self.run:
                img = ImageGrab.grab(bbox=(0, 0, self.width, self.height))
                frame = np.array(img)

                # Convert it from BGR(Blue, Green, Red) to RGB(Red, Green, Blue)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.out.write(frame)

        except:
            self.error.emit(
                {
                    "title": screenrecorder.SCREEN_RECODER,
                    "message": error.SCREEN_RECODER,
                    "details": str(sys.exc_info()[0]),
                }
            )

        self.out.release()

        cv2.destroyAllWindows()

        self.finished.emit()

    def stop(self):
        self.run = False


class TaskScreenRecorder(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.SCREEN_RECORDER
        super().__init__(options, logger, table, progress_bar, status_bar, parent)
        self.screenrecorder_thread = QThread()
        self.screenrecorder = ScreenRecorder()
        self.screenrecorder.moveToThread(self.screenrecorder_thread)
        self.screenrecorder_thread.started.connect(self.screenrecorder.start)
        self.screenrecorder.started.connect(self.__started)
        self.screenrecorder.finished.connect(self.__finished)
        self.screenrecorder.error.connect(self.__handle_error)

    @Task.options.getter
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        folder = options["acquisition_directory"]
        options = ScreenRecorderController().options
        options["filename"] = os.path.join(folder, options["filename"])
        self._options = options

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SCREEN_RECODER_STARTED)

        self.screenrecorder.set_options(self.options)
        self.screenrecorder_thread.start()

    def __started(self):
        self.update_task(
            state.STARTED,
            status.COMPLETED,
            details.SCREEN_RECORDER_STARTED,
        )

        self.logger.info(logger.SCREEN_RECODER_STARTED)
        self.started.emit()

    def stop(self):
        self.update_task(state.STOPPED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SCREEN_RECODER_STOPPED)
        self.screenrecorder.stop()

    def __finished(self):
        self.logger.info(logger.SCREEN_RECODER_COMPLETED)
        self.set_message_on_the_statusbar(logger.SCREEN_RECODER_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(
            state.FINISHED,
            status.COMPLETED,
            details.SCREEN_RECORDER_COMPLETED,
        )

        self.finished.emit()

        self.screenrecorder_thread.quit()
        self.screenrecorder_thread.wait()
