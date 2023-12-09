#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from view.tasks.entire_website.mitm import MitmProxyWorker

from common.utility import find_free_port

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
        controller = self.options.get("entire_website_controller")
        urls = list()

        controller.set_dir(self.options.get("acquisition_directory"))

        port = find_free_port()
        mitm_thread = MitmProxyWorker(port)
        mitm_thread.set_dir(self.options.get("acquisition_directory"))
        mitm_thread.start()
        controller.set_proxy(port)
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
