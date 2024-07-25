#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal
from controller.entire_website import EntireWebsite as EntireWebsiteController

from common.constants.view import entire_site
from common.constants import error


class EntireWebsiteDownloadWorker(QObject):
    download_finished = pyqtSignal(list)
    progress = pyqtSignal()
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def download(self):
        urls = list()
        controller = EntireWebsiteController()
        controller.set_dir(self.options.get("acquisition_directory"))
        controller.set_proxy(self.options.get("proxy_port"))
        for url in self.options.get("urls"):
            try:
                controller.download(url)
                urls.append(url)

            except Exception as e:
                self.error.emit(
                    {
                        "title": entire_site.INVALID_URL,
                        "msg": error.INVALID_URL,
                        "details": str(e),
                    }
                )
            else:
                self.progress.emit()

        self.download_finished.emit(urls)
