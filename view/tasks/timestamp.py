#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os

import requests
from rfc3161ng.api import RemoteTimestamper

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status

from view.tasks.task import Task

from controller.configurations.tabs.timestamp.timestamp import (
    Timestamp as TimestampController,
)

from common.constants import logger


class Timestamp(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    def set_options(self, options):
        self.server_name = options["server_name"]
        self.cert_url = options["cert_url"]
        self.acquisition_directory = options["acquisition_directory"]
        self.pdf_filename = options["pdf_filename"]

    def apply_timestamp(self):
        self.started.emit()
        pdf_path = os.path.join(self.acquisition_directory, self.pdf_filename)
        ts_path = os.path.join(self.acquisition_directory, "timestamp.tsr")
        cert_path = os.path.join(self.acquisition_directory, "tsa.crt")

        # getting the chain from the authority
        response = requests.get(self.cert_url)
        with open(cert_path, "wb") as f:
            f.write(response.content)

        with open(cert_path, "rb") as f:
            certificate = f.read()

        # create the object
        rt = RemoteTimestamper(
            self.server_name, certificate=certificate, hashname="sha256"
        )

        # file to be certificated
        with open(pdf_path, "rb") as f:
            timestamp = rt.timestamp(data=f.read())

        # saving the timestamp
        with open(ts_path, "wb") as f:
            f.write(timestamp)

        self.finished.emit()


class TaskTimestamp(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.TIMESTAMP

        self.worker_thread = QThread()
        self.worker = Timestamp()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.apply_timestamp)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    @Task.options.getter
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        folder = options["acquisition_directory"]
        pdf_filename = options["pdf_filename"]
        options = TimestampController().options
        options["acquisition_directory"] = folder
        options["pdf_filename"] = pdf_filename
        self._options = options

    def start(self):
        self.worker.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.TIMESTAMP_STARTED)
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(
            logger.TIMESTAMP_APPLY.format(
                self.options["pdf_filename"], self.options["server_name"]
            )
        )
        self.set_message_on_the_statusbar(logger.TIMESTAMP_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
