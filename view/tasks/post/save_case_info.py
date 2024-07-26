#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import json

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status
from common.constants import logger

from view.tasks.task import Task


class SaveCaseInfoWorker(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def start(self):
        self.started.emit()
        file = os.path.join(self.options.get("acquisition_directory"), "caseinfo.json")

        with open(file, "w") as f:
            json.dump(self.options.get("case_info"), f, ensure_ascii=False)

        self.finished.emit()


class TaskSaveCaseInfo(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.SAVE_CASE_INFO
        self.worker_thread = QThread()
        self.worker = SaveCaseInfoWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SAVE_CASE_INFO_STARTED)
        self.worker.options = self.options
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.SAVE_CASE_INFO)
        self.set_message_on_the_statusbar(logger.SAVE_CASE_INFO_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
