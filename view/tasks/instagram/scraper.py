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


class InstagramScrapeWorker(QObject):
    scraped = pyqtSignal()
    progress = pyqtSignal()
    scraped_status = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def scrape(self):
        methods_to_execute = self.options.get("methods_to_execute")
        controller = self.options.get("instagram_controller")
        profile_dir = self.options.get("profile_dir")

        controller.set_dir(profile_dir)

        for method in methods_to_execute:

            __scraped_status = {"method": method}
            method = getattr(controller, method)

            try:
                method()
                __scraped_status["status"] = status.SUCCESS
                __scraped_status["message"] = ""

            except Exception as e:
                __scraped_status["status"] = status.FAIL
                __scraped_status["message"] = str(e)

            self.scraped_status.emit(__scraped_status)
            self.progress.emit()

        self.scraped.emit()
