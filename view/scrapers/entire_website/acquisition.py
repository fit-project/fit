#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import inspect

from view.acquisition.acquisition import Acquisition
from PyQt6.QtCore import pyqtSignal
from view.tasks.class_names import *


class EntireWebsiteAcquisition(Acquisition):
    valid_url = pyqtSignal(str)
    sitemap_finished = pyqtSignal(str, set)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)
        self.caller_function_name = None
        self.start_tasks = [ENTIRE_WEBSITE, PACKETCAPTURE]
        self.stop_tasks = [PACKETCAPTURE]
        self.stop_tasks_is_finished.connect(self.start_post_acquisition)

    def check_is_valid_url(self, url):
        self.caller_function_name = inspect.stack()[1].function
        self.task_entire_websiste = self.tasks_manager.get_task(ENTIRE_WEBSITE)

        if self.task_entire_websiste.receivers(self.task_entire_websiste.valid_url) > 0:
            self.task_entire_websiste.valid_url.disconnect()

        self.task_entire_websiste.valid_url.connect(self.valid_url.emit)
        self.task_entire_websiste.check_is_valid_url(url)

    def get_sitemap(self):
        if self.task_entire_websiste:
            self.task_entire_websiste.sitemap_finished.connect(
                self.sitemap_finished.emit
            )
            self.task_entire_websiste.get_sitemap()

    def download(self):
        if self.task_entire_websiste:
            self.task_entire_websiste.download_finished.connect(self.stop)
            self.task_entire_websiste.progress.connect(self.progress.emit)
            self.task_entire_websiste.download_urls()
