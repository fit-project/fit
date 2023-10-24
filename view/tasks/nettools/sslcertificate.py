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
from common.constants import logger, state, status, tasks, details

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
    def __init__(
        self, options, logger, table, progress_bar=None, status_bar=None, parent=None
    ):
        self.name = tasks.SSLCERTIFICATE
        super().__init__(options, logger, table, progress_bar, status_bar, parent)

        self.sslcertificate_thread = QThread()
        self.sslcertificate = SSLCertificate()
        self.sslcertificate.moveToThread(self.sslcertificate_thread)
        self.sslcertificate_thread.started.connect(self.sslcertificate.start)
        self.sslcertificate.started.connect(self.__started)
        self.sslcertificate.finished.connect(self.__finished)

    def start(self):
        self.sslcertificate.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SSLCERTIFICATE_STARTED)
        self.sslcertificate_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.COMPLETED)
        self.started.emit()

    def stop(self):
        pass

    def __finished(self, is_peer_certificate_exist):
        msg = logger.SSLCERTIFICATE_GET_FROM_URL.format(self.options["url"])
        if is_peer_certificate_exist is False:
            msg = details.SSLCERTIFICATE_NOT_EXIST.format(self.options["url"])
            self.details = msg

        self.logger.info(msg)
        self.set_message_on_the_statusbar(logger.SSLCERTIFICATE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.FINISHED, status.COMPLETED)

        self.finished.emit()

        self.sslcertificate_thread.quit()
        self.sslcertificate_thread.wait()
