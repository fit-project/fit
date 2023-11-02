#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import sslkeylog
import os
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status

from view.tasks.task import Task
from common.constants import logger


class SSLKeyLog(QObject):
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
        sslkeylog.set_keylog(os.path.join(self.folder, "sslkey.log"))

        self.finished.emit()


class TaskSSLKeyLog(Task):
    def __init__(
        self, options, logger, progress_bar=None, status_bar=None, parent=None
    ):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.label = labels.SSLKEYLOG

        self.sslkeylog_thread = QThread()
        self.sslkeylog = SSLKeyLog()
        self.sslkeylog.moveToThread(self.sslkeylog_thread)
        self.sslkeylog_thread.started.connect(self.sslkeylog.start)
        self.sslkeylog.started.connect(self.__started)
        self.sslkeylog.finished.connect(self.__finished)

    def start(self):
        self.sslkeylog.folder = self.options["acquisition_directory"]
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SSLKEYLOG_STARTED)
        self.sslkeylog_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.SSLKEYLOG_GET)
        self.set_message_on_the_statusbar(logger.SSLKEYLOG_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.sslkeylog_thread.quit()
        self.sslkeylog_thread.wait()
