#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import numpy as np
import sys
import os


from PIL import ImageGrab
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtWidgets import QMessageBox, QApplication

from PyQt6.QtMultimedia import (
    QMediaCaptureSession,
    QWindowCapture,
    QMediaRecorder,
    QScreenCapture,
)

from screeninfo import get_monitors
from common.constants.view.tasks import labels, state, status

from view.tasks.task import Task
from view.error import Error as ErrorView
from view.configurations.screen_recorder_preview.screen_recorder_preview import (
    SourceType,
)

from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)


from common.constants import logger, details
from common.constants import error
from common.constants.view import screenrecorder


class ScreenRecorderWorker(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

        self.destroyed.connect(self.stop)

        self.__video_to_record_session = QMediaCaptureSession()
        self.__window_to_record = QWindowCapture()
        self.__video_to_record_session.setWindowCapture(self.__window_to_record)
        self.__screen_to_record = QScreenCapture()
        self.__video_to_record_session.setScreenCapture(self.__screen_to_record)
        self.__video_recorder = QMediaRecorder()

        self.__video_to_record_session.setRecorder(self.__video_recorder)

    def set_options(self, options):
        self.__video_recorder.setOutputLocation(QUrl.fromLocalFile(options["filename"]))

    def start(self):
        app = QApplication.instance()
        screen_information = getattr(app, "screen_information")
        screen_to_record = screen_information.get("screen_to_record")
        self.__source_type = screen_information.get("source_type")
        try:
            if self.__source_type == SourceType.SCREEN:
                self.__screen_to_record.setScreen(screen_to_record)
                self.__screen_to_record.start()
                self.__video_recorder.record()

            elif self.__source_type == SourceType.WINDOW:
                self.__window_to_record.setWindow(screen_to_record)
                self.__window_to_record.start()
                self.__video_recorder.record()
        except Exception as e:
            self.error.emit(
                {
                    "title": screenrecorder.SCREEN_RECODER,
                    "message": error.SCREEN_RECODER,
                    "details": str(e),
                }
            )

        self.started.emit()

    def stop(self):
        self.__video_recorder.stop()
        if self.__source_type == SourceType.SCREEN:
            self.__screen_to_record.stop()
        elif self.__source_type == SourceType.WINDOW:
            self.__window_to_record.stop()

        self.finished.emit()


class TaskScreenRecorder(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.SCREEN_RECORDER
        self.is_infinite_loop = True

        self.worker_thread = QThread()
        self.worker = ScreenRecorderWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)
        self.worker.error.connect(self.__handle_error)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    @Task.options.getter
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        folder = options["acquisition_directory"]
        options = ScreenRecorderConfigurationController().options
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

        self.worker.set_options(self.options)
        self.worker_thread.start()

    def __started(self):
        self.update_task(
            state.STARTED,
            status.SUCCESS,
            details.SCREEN_RECORDER_STARTED,
        )

        self.logger.info(logger.SCREEN_RECODER_STARTED)
        self.started.emit()

    def stop(self):
        self.update_task(state.STOPPED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SCREEN_RECODER_STOPPED)
        self.worker.stop()

    def __finished(self):
        self.logger.info(logger.SCREEN_RECODER_COMPLETED)
        self.set_message_on_the_statusbar(logger.SCREEN_RECODER_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(
            state.COMPLETED,
            status.SUCCESS,
            details.SCREEN_RECORDER_COMPLETED,
        )

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
