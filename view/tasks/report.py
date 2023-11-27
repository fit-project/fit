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

from view.tasks.task import Task

from controller.report import Report as ReportController
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck

from common.utility import get_ntp_date_and_time
from common.constants import logger


class Report(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.folder = options["acquisition_directory"]
        self.type = options["type"]
        self.case_info = options["case_info"]

    def start(self):
        self.started.emit()

        report = ReportController(self.folder, self.case_info)
        report.generate_pdf(
            self.type,
            get_ntp_date_and_time(NetworkControllerCheck().configuration["ntp_server"]),
        )

        self.finished.emit()


class TaskReport(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.REPORTFILE

        self.worker_thread = QThread()
        self.worker = Report()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.worker.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.GENERATE_PDF_REPORT_STARTED)
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.GENERATE_PDF_REPORT)
        self.set_message_on_the_statusbar(logger.GENERATE_PDF_REPORT_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
