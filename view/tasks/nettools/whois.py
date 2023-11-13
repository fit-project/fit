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

        self.whois_thread = QThread()
        self.whois = Whois()
        self.whois.moveToThread(self.whois_thread)
        self.whois_thread.started.connect(self.whois.start)
        self.whois.started.connect(self.__started)
        self.whois.finished.connect(self.__finished)

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.WHOIS_STARTED)
        self.whois.url = self.options["url"]
        self.whois_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.WHOIS_GET_INFO_URL.format(self.options["url"]))
        self.set_message_on_the_statusbar(logger.WHOIS_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.whois_thread.quit()
        self.whois_thread.wait()
