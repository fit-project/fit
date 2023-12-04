#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import re

from PyQt6.QtCore import QObject, pyqtSignal


class MailDownloadWorker(QObject):
    download_finished = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def download(self):
        # Create acquisition folder
        self.acquisition_mail_dir = os.path.join(
            self.options.get("acquisition_directory"), "acquisition_mail"
        )
        if not os.path.exists(self.acquisition_mail_dir):
            os.makedirs(self.acquisition_mail_dir)

        emails_to_download = self.options.get("emails_to_download")
        controller = self.options.get("mail_controller")

        for folder, emails_list in emails_to_download.items():
            for emails in emails_list:
                email_id = emails.partition("UID: ")[2]
                # Create acquisition folder
                folder_stripped = re.sub(r"[^a-zA-Z0-9]+", "-", folder)
                controller.write_emails(
                    email_id, self.acquisition_mail_dir, folder_stripped, folder
                )
                self.progress.emit()
        controller.write_logs(self.options.get("acquisition_directory"))
        self.download_finished.emit()
