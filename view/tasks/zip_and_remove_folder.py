#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import shutil
import os

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox


from view.tasks.task import Task
from view.error import Error as ErrorView

from common.constants import logger, error
from common.constants.view.tasks import labels, state, status


class ZipAndRemoveFolder(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal(object)

    def set_options(self, options):
        self.acquisition_content_directory = options["acquisition_content_directory"]

    def start(self):
        self.started.emit()
        shutil.make_archive(
            self.acquisition_content_directory,
            "zip",
            self.acquisition_content_directory,
        )

        has_files_downloads_folder = []

        downloads_folder = os.path.join(self.acquisition_content_directory, "downloads")
        if os.path.isdir(downloads_folder):
            has_files_downloads_folder = os.listdir(downloads_folder)

        if len(has_files_downloads_folder) > 0:
            shutil.make_archive(downloads_folder, "zip", downloads_folder)
        try:
            shutil.rmtree(self.acquisition_content_directory)
            if os.path.isdir(downloads_folder):
                shutil.rmtree(downloads_folder)
            self.finished.emit()

        except OSError as e:
            self.error.emit(
                {
                    "title": labels.ZIP_AND_REMOVE_FOLDER,
                    "message": error.DELETE_PROJECT_FOLDER,
                    "details": "Error: %s - %s." % (e.filename, e.strerror),
                }
            )


class TaskZipAndRemoveFolder(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.ZIP_AND_REMOVE_FOLDER

        self.worker_thread = QThread()
        self.worker = ZipAndRemoveFolder()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)
        self.worker.error.connect(self.__handle_error)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()
        self.__finished(status.FAIL)

    def start(self):
        self.worker.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.ZIP_AND_REMOVE_FOLDER_STARTED)
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self, status=status.SUCCESS):
        self.logger.info(logger.ZIP_AND_REMOVE_FOLDER)
        self.set_message_on_the_statusbar(logger.ZIP_AND_REMOVE_FOLDER_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
