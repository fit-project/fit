#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox


from view.tasks.video.load import VideoLoadWorker
from view.tasks.video.download import VideoDownloadWorker

from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.video import Video as VideoController

from common.constants.view.tasks import labels, state, status
from common.constants import logger


class TaskVideo(Task):
    load_finished = pyqtSignal(str, object)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.VIDEO_SCRAPER
        self.sub_task = None
        self.sub_task_thread = None
        self.sub_tasks = [
            {
                "label": labels.LOAD_VIDEO,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.DOWNLOAD_VIDEO,
                "state": self.state,
                "status": self.status,
            },
        ]

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.VIDEO_SCRAPER_STARTED)
        self.logger.info(logger.VIDEO_SCRAPER_STARTED)
        self.options["video_controller"] = VideoController()

        self.__started()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def load(self):
        self.sub_task = VideoLoadWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.load)
        self.sub_task.load_finished.connect(self.__is_load_finished)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options

        self.sub_task_thread.start()

    def __is_load_finished(self, __status, info):
        sub_task_load = next(
            (task for task in self.sub_tasks if task.get("label") == labels.LOAD_VIDEO),
            None,
        )
        if sub_task_load:
            sub_task_load["state"] = state.COMPLETED
            sub_task_load["status"] = __status

        self.logger.info(
            logger.VIDEO_SCRAPER_LOADED.format(self.options.get("url"), __status)
        )
        self.set_message_on_the_statusbar(
            logger.VIDEO_SCRAPER_LOAD_FINISHED.format(__status)
        )

        self.load_finished.emit(__status, info)

        self.__quit_to_sub_task()

    def download(self):
        self.sub_task = VideoDownloadWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.download)
        self.sub_task.download_finished.connect(self.__is_download_finished)
        self.sub_task.progress.connect(self.progress.emit)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

    def __is_download_finished(self):
        sub_task_download = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.DOWNLOAD_VIDEO
            ),
            None,
        )
        if sub_task_download:
            sub_task_download["state"] = state.COMPLETED
            sub_task_download["status"] = status.SUCCESS

        self.logger.info(
            logger.VIDEO_SCRAPER_DOWNLOADED.format(self.options.get("url"))
        )
        self.set_message_on_the_statusbar(logger.VIDEO_SCRAPER_DOWNLOAD_FININISHED)

        self.download_finished.emit()

        self.__quit_to_sub_task()
        self.__finished()

    def __finished(self):
        self.logger.info(logger.VIDEO_SCRAPER_COMPLETED)
        self.set_message_on_the_statusbar(logger.VIDEO_SCRAPER_COMPLETED)
        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

    def __quit_to_sub_task(self):
        if self.sub_task_thread is not None:
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()
            self.sub_task_thread = None
        if self.sub_task is not None:
            self.sub_task = None

    def __destroyed_handler(self, _dict):
        if self.sub_task_thread is not None and self.sub_task_thread.isRunning():
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()
