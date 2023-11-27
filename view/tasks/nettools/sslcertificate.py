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
from common.constants import logger, details

from common.utility import (
    check_if_peer_certificate_exist,
    get_peer_PEM_cert,
    save_PEM_cert_to_CER_cert,
)


class SSLCertificate(QObject):
    finished = pyqtSignal(bool)
    started = pyqtSignal()

    def set_options(self, options):
        self.url = options["url"]
        self.folder = options["acquisition_directory"]

    def start(self):
        self.started.emit()
        is_peer_certificate_exist = check_if_peer_certificate_exist(self.url)
        if is_peer_certificate_exist:
            certificate = get_peer_PEM_cert(self.url)
            save_PEM_cert_to_CER_cert(
                os.path.join(self.folder, "server.cer"), certificate
            )

        self.finished.emit(is_peer_certificate_exist)


class TaskSSLCertificate(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.SSLCERTIFICATE

        self.worker_thread = QThread()
        self.worker = SSLCertificate()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.start)
        self.worker.started.connect(self.__started)
        self.worker.finished.connect(self.__finished)

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.worker.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SSLCERTIFICATE_STARTED)
        self.worker_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self, is_peer_certificate_exist):
        msg = logger.SSLCERTIFICATE_GET_FROM_URL.format(self.options["url"])
        if is_peer_certificate_exist is False:
            msg = details.SSLCERTIFICATE_NOT_EXIST.format(self.options["url"])
            self.details = msg

        self.logger.info(msg)
        self.set_message_on_the_statusbar(logger.SSLCERTIFICATE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.worker_thread.quit()
        self.worker_thread.wait()

    def __destroyed_handler(self, _dict):
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
