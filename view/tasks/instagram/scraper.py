#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from PyQt6.QtCore import QObject, pyqtSignal


class InstagramScrapeWorker(QObject):
    scraped = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(object)

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
            method = getattr(controller, method)
            method()
            self.progress.emit()

        self.scraped.emit()
