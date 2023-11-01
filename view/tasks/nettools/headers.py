#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from common.utility import get_headers_information
from common.constants import logger, state, status, tasks

from view.tasks.task import Task


class Headers(QObject):
    logger = logging.getLogger("headers")
    finished = pyqtSignal()
    started = pyqtSignal()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def start(self):
        self.started.emit()
        self.logger.info(get_headers_information(self.url))
        self.finished.emit()


class TaskHeaders(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.HEADERS
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.headers_thread = QThread()
        self.headers = Headers()
        self.headers.moveToThread(self.headers_thread)
        self.headers_thread.started.connect(self.headers.start)
        self.headers.started.connect(self.__started)
        self.headers.finished.connect(self.__finished)

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.HEADERS_STARTED)
        self.headers.url = self.options["url"]
        self.headers_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.HEADERS_GET_INFO_URL.format(self.options["url"]))
        self.set_message_on_the_statusbar(logger.HEADERS_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.headers_thread.quit()
        self.headers_thread.wait()
