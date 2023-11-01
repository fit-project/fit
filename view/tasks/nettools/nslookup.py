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

from controller.configurations.tabs.network.networkcheck import (
    NetworkControllerCheck as NetworkCheckController,
)

from common.utility import nslookup
from common.constants import logger, state, status, tasks

from view.tasks.task import Task


class Nslookup(QObject):
    logger = logging.getLogger("nslookup")
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.url = options["url"]
        self.nslookup_dns_server = options["nslookup_dns_server"]
        self.nslookup_enable_tcp = options["nslookup_enable_tcp"]
        self.nslookup_enable_verbose_mode = options["nslookup_enable_verbose_mode"]

    def start(self):
        self.started.emit()
        self.logger.info(
            nslookup(
                self.url,
                self.nslookup_dns_server,
                self.nslookup_enable_tcp,
                self.nslookup_enable_tcp,
            )
        )
        self.finished.emit()


class TaskNslookup(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.NSLOOKUP
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.nslookup_thread = QThread()
        self.nslookup = Nslookup()
        self.nslookup.moveToThread(self.nslookup_thread)
        self.nslookup_thread.started.connect(self.nslookup.start)
        self.nslookup.started.connect(self.__started)
        self.nslookup.finished.connect(self.__finished)

    @Task.options.getter
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        url = options["url"]
        options = NetworkCheckController().configuration
        options["url"] = url
        self._options = options

    def start(self):
        self.nslookup.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.NSLOOKUP_STARTED)

        self.nslookup_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.NSLOOKUP_GET_INFO_URL.format(self.options["url"]))
        self.set_message_on_the_statusbar(logger.NSLOOKUP_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.nslookup_thread.quit()
        self.nslookup_thread.wait()
