#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status

from view.tasks.task import Task
from common.constants import logger


class SSLKeyLogWorker(QObject):
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
        os.environ["SSLKEYLOGFILE"] = os.path.join(self.folder, "sslkey.log")
        self.finished.emit()


class TaskSSLKeyLog(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.SSLKEYLOG

        self.worker_thread = QThread()
        self.worker = SSLKeyLogWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.worker.folder = self.options["acquisition_directory"]
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SSLKEYLOG_STARTED)
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.SSLKEYLOG_GET)
        self.set_message_on_the_statusbar(logger.SSLKEYLOG_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
