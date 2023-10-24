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

from view.tasks.task import Task

from controller.report import Report as ReportController
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck

from common.utility import get_ntp_date_and_time
from common.constants import logger, state, status, tasks


class GenerateReport(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.folder = options["url"]
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


class TaskGenerateReport(Task):
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.REPORTFILE
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.generate_report_thread = QThread()
        self.generate_report = GenerateReport()
        self.generate_report.moveToThread(self.generate_report_thread)
        self.generate_report_thread.started.connect(self.generate_report.start)
        self.generate_report.started.connect(self.__started)
        self.generate_report.finished.connect(self.__finished)

    def start(self):
        self.generate_report.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.GENERATE_PDF_REPORT_STARTED)
        self.generate_report_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def stop(self):
        pass

    def __finished(self):
        self.logger.info(logger.GENERATE_PDF_REPORT)
        self.set_message_on_the_statusbar(logger.GENERATE_PDF_REPORT_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.generate_report_thread.quit()
        self.generate_report_thread.wait()
