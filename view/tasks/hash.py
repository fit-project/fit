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


class Hash(QObject):
    logger = logging.getLogger("hashreport")
    finished = pyqtSignal()
    started = pyqtSignal()

    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, folder):
        self._folder = folder

    def start(self):
        self.started.emit()

        files = [f.name for f in os.scandir(self.folder) if f.is_file()]
        for file in files:
            if file != "acquisition.hash":
                filename = os.path.join(self.folder, file)
                file_stats = os.stat(filename)
                self.logger.info(file)
                self.logger.info(
                    "========================================================="
                )
                self.logger.info(f"Size: {file_stats.st_size}")
                algorithm = "md5"
                self.logger.info(f"MD5: {calculate_hash(filename, algorithm)}\n")
                algorithm = "sha1"
                self.logger.info(f"SHA-1: {calculate_hash(filename, algorithm)}\n")
                algorithm = "sha256"
                self.logger.info(f"SHA-256: {calculate_hash(filename, algorithm)}\n")

        self.finished.emit()


class TaskHash(Task):
    def __init__(
        self, options, logger, progress_bar=None, status_bar=None, parent=None
    ):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.label = labels.HASHFILE
        self.calculate_hash_thread = QThread()
        self.calculate_hash = Hash()
        self.calculate_hash.moveToThread(self.calculate_hash_thread)
        self.calculate_hash_thread.started.connect(self.calculate_hash.start)
        self.calculate_hash.started.connect(self.__started)
        self.calculate_hash.finished.connect(self.__finished)

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.CALCULATE_HASHFILE_STARTED)
        self.calculate_hash.folder = self.options["acquisition_directory"]
        self.calculate_hash_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.CALCULATE_HASHFILE)
        self.set_message_on_the_statusbar(logger.CALCULATE_HASHFILE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.calculate_hash_thread.quit()
        self.calculate_hash_thread.wait()
