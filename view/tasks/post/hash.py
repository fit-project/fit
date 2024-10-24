#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status

from common.utility import calculate_hash
from common.constants import logger

from view.tasks.task import Task


class HashWorker(QObject):
    logger = logging.getLogger("hashreport")
    finished = pyqtSignal()
    started = pyqtSignal()

    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, folder):
        self._folder = folder

    @property
    def exclude_list(self):
        return self._exclude_list

    @exclude_list.setter
    def exclude_list(self, exclude_list):
        self._exclude_list = exclude_list

    def start(self):
        self.started.emit()

        files = [f.name for f in os.scandir(self.folder) if f.is_file()]
        for file in files:
            if file != "acquisition.hash" and file not in self.exclude_list:
                filename = os.path.join(self.folder, file)
                file_stats = os.stat(filename)
                self.logger.info(
                    "========================================================="
                )
                self.logger.info(f"Name: {file}")
                self.logger.info(f"Size: {file_stats.st_size}")
                algorithm = "md5"
                self.logger.info(f"MD5: {calculate_hash(filename, algorithm)}")
                algorithm = "sha1"
                self.logger.info(f"SHA-1: {calculate_hash(filename, algorithm)}")
                algorithm = "sha256"
                self.logger.info(f"SHA-256: {calculate_hash(filename, algorithm)}")

        self.finished.emit()


class TaskHash(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.HASHFILE
        self.worker_thread = QThread()
        self.worker = HashWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.CALCULATE_HASHFILE_STARTED)
        self.worker.folder = self.options["acquisition_directory"]
        self.worker.exclude_list = list()
        if "exclude_from_hash_calculation" in self.options:
            self.worker.exclude_list = self.options["exclude_from_hash_calculation"]

        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.CALCULATE_HASHFILE)
        self.set_message_on_the_statusbar(logger.CALCULATE_HASHFILE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
