#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import logging
import logging.config

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status
from view.tasks.task import Task

from common.utility import whois
from common.constants import logger


class Whois(QObject):
    logger = logging.getLogger("whois")
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
        self.logger.info(whois(self.url))
        self.finished.emit()


class TaskWhois(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.WHOIS

        self.worker_thread = QThread()
        self.worker = Whois()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.WHOIS_STARTED)
        self.worker.url = self.options["url"]
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.WHOIS_GET_INFO_URL.format(self.options["url"]))
        self.set_message_on_the_statusbar(logger.WHOIS_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
