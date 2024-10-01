#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtMultimedia import (
    QMediaCaptureSession,
    QMediaRecorder,
    QScreenCapture,
    QAudioInput,
)

from view.tasks.task import Task
from view.error import Error as ErrorView
from view.util import get_vb_cable_virtual_audio_device

from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)


from common.constants import logger, details
from common.constants import error
from common.constants.view import screenrecorder
from common.constants.view.tasks import labels, state, status


class ScreenRecorderWorker(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

        self.destroyed.connect(self.stop)

        self.__is_enabled_audio_recording = False

        # Video recording
        self.__video_to_record_session = QMediaCaptureSession()
        self.__screen_to_record = QScreenCapture()
        self.__video_to_record_session.setScreenCapture(self.__screen_to_record)
        self.__video_recorder = QMediaRecorder()
        self.__video_recorder.recorderStateChanged.connect(
            self.__video_recorder_state_handler
        )
        self.__video_to_record_session.setRecorder(self.__video_recorder)

    def __video_recorder_state_handler(self, recorder_state):

        if recorder_state == QMediaRecorder.RecorderState.StoppedState:
            self.__join_audio_and_video()

    def set_options(self, options):

        self.__acquisition_directory = options["acquisition_directory"]
        self.__filename = options["filename"]
        app = QApplication.instance()

        screen = app.screenAt(options["window_pos"])
        if screen:
            print(screen.name())
            self.__screen_to_record.setScreen(screen)

        if hasattr(app, "is_enabled_audio_recording"):
            self.__is_enabled_audio_recording = getattr(
                app, "is_enabled_audio_recording"
            )

        if self.__is_enabled_audio_recording is True:
            self.__audio_path = os.path.join(
                self.__acquisition_directory, "screenrecorder/audio"
            )
            self.__video_path = os.path.join(
                self.__acquisition_directory, "screenrecorder/video"
            )
            self.__create_screen_recorder_directories()

            # Set video recording path
            self.__video_recorder.setOutputLocation(
                QUrl.fromLocalFile(os.path.join(self.__video_path, "screenrecorder"))
            )

            # Audio recording
            self.__audio_capture_session = QMediaCaptureSession()
            self.__audio_input = QAudioInput(get_vb_cable_virtual_audio_device())
            self.__audio_capture_session.setAudioInput(self.__audio_input)
            self.__audio_recorder = QMediaRecorder()
            self.__audio_recorder.setOutputLocation(
                QUrl.fromLocalFile(os.path.join(self.__audio_path, "screenrecorder"))
            )
            self.__audio_capture_session.setRecorder(self.__audio_recorder)
        else:
            self.__video_recorder.setOutputLocation(QUrl.fromLocalFile(self.__filename))

    def start(self):
        try:
            self.__screen_to_record.start()
            self.__video_recorder.record()
            if self.__is_enabled_audio_recording is True:
                self.__audio_recorder.record()
        except Exception as e:
            self.error.emit(
                {
                    "title": screenrecorder.SCREEN_RECODER,
                    "message": error.SCREEN_RECODER,
                    "details": str(e),
                }
            )

        self.started.emit()

    def __create_screen_recorder_directories(self):
        if not os.path.exists(self.__audio_path):
            os.makedirs(self.__audio_path)
        if not os.path.exists(self.__video_path):
            os.makedirs(self.__video_path)

    def stop(self):
        self.__video_recorder.stop()
        self.__screen_to_record.stop()
        if self.__is_enabled_audio_recording is True:
            self.__audio_recorder.stop()

    def __join_audio_and_video(self):
        if self.__is_enabled_audio_recording is True:
            from moviepy.editor import VideoFileClip, AudioFileClip

            output_path = self.__filename + ".mp4"
            audio_path = self.__get_file_path(self.__audio_path)
            video_path = self.__get_file_path(self.__video_path)
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)
            video.write_videofile(output_path, codec="libx264", audio_codec="aac")

        self.finished.emit()

    def __get_file_path(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith("screenrecorder"):
                    return os.path.join(root, file)
        return None


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
        options["filename"] = os.path.join(
            options["acquisition_directory"],
            ScreenRecorderConfigurationController().options["filename"],
        )
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
