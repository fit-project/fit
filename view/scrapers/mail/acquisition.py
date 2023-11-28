#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from view.acquisition.acquisition import Acquisition
from PyQt6.QtCore import pyqtSignal
from view.tasks.class_names import *


class MailAcquisition(Acquisition):
    logged_in = pyqtSignal(str)

    search_emails_finished = pyqtSignal(str, dict)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)
        self.start_tasks = [MAIL, PACKETCAPTURE]
        self.stop_tasks = [PACKETCAPTURE]
        self.stop_tasks_is_finished.connect(self.start_post_acquisition)

    def login(self):
        self.task_mail = self.tasks_manager.get_task(MAIL)
        self.task_mail.logged_in.connect(self.logged_in.emit)
        self.task_mail.login()

    def search(self):
        if self.task_mail:
            self.task_mail.search_emails_finished.connect(
                self.search_emails_finished.emit
            )
            self.task_mail.search()

    def download(self):
        if self.task_mail:
            self.task_mail.download_finished.connect(self.stop)
            self.task_mail.progress.connect(self.progress.emit)
            self.task_mail.download()
