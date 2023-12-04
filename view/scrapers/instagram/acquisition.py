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


class InstagramAcquisition(Acquisition):
    logged_in = pyqtSignal(str, int)
    scraped = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)
        self.start_tasks = [INSTAGRAM]

    def login(self):
        self.task_instagram = self.tasks_manager.get_task(INSTAGRAM)
        self.task_instagram.logged_in.connect(self.logged_in.emit)
        self.task_instagram.login()

    def scrape(self):
        self.task_instagram = self.tasks_manager.get_task(INSTAGRAM)
        self.task_instagram.scraped.connect(self.start_post_acquisition)
        self.task_instagram.progress.connect(self.progress.emit)
        self.task_instagram.scrape()
