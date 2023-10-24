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
from view.tasks.task import Task

from common.utility import traceroute
from common.constants import logger, state, status, tasks


class Traceroute(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.url = options["url"]
        self.folder = options["acquisition_directory"]

    def start(self):
        self.started.emit()
        traceroute(self.url, os.path.join(self.folder, "traceroute.txt"))

        self.finished.emit()


class TaskTraceroute(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.TRACEROUTE
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.traceroute_thread = QThread()
        self.traceorute = Traceroute()
        self.traceorute.moveToThread(self.traceroute_thread)
        self.traceroute_thread.started.connect(self.traceorute.start)
        self.traceorute.started.connect(self.__started)
        self.traceorute.finished.connect(self.__finished)

    def start(self):
        self.traceorute.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.TRACEROUTE_STARTED)
        self.traceroute_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def stop(self):
        pass

    def __finished(self):
        self.logger.info(logger.TRACEROUTE_GET_INFO_URL.format(self.options["url"]))
        self.set_message_on_the_statusbar(logger.TRACEROUTE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.traceroute_thread.quit()
        self.traceroute_thread.wait()
