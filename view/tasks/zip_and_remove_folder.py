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
        self.acquisition_page_folder = options["acquisition_page_folder"]

    def start(self):
        self.started.emit()
        shutil.make_archive(
            self.acquisition_page_folder, "zip", self.acquisition_page_folder
        )

        has_files_downloads_folder = 0
        downloads_folder = os.path.join(self.acquisition_page_folder, "downloads")
        if not os.path.isdir(downloads_folder):
            has_files_downloads_folder = os.listdir(downloads_folder)

        if len(has_files_downloads_folder) > 0:
            shutil.make_archive(downloads_folder, "zip", downloads_folder)
        try:
            shutil.rmtree(self.acquisition_page_folder)
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
    def __init__(
        self, options, logger, progress_bar=None, status_bar=None, parent=None
    ):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.label = labels.ZIP_AND_REMOVE_FOLDER

        self.zip_and_remove_folder_thread = QThread()
        self.zip_and_remove_folder = ZipAndRemoveFolder()
        self.zip_and_remove_folder.moveToThread(self.zip_and_remove_folder_thread)
        self.zip_and_remove_folder_thread.started.connect(
            self.zip_and_remove_folder.start
        )
        self.zip_and_remove_folder.started.connect(self.__started)
        self.zip_and_remove_folder.finished.connect(self.__finished)
        self.zip_and_remove_folder.error.connect(self.__handle_error)

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
        self.zip_and_remove_folder.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.ZIP_AND_REMOVE_FOLDER_STARTED)
        self.zip_and_remove_folder_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self, status=status.SUCCESS):
        self.logger.info(logger.ZIP_AND_REMOVE_FOLDER)
        self.set_message_on_the_statusbar(logger.ZIP_AND_REMOVE_FOLDER_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status)

        self.finished.emit()

        self.zip_and_remove_folder_thread.quit()
        self.zip_and_remove_folder_thread.wait()
