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


class VideoAcquisition(Acquisition):
    load_finished = pyqtSignal(str, object)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)
        self.start_tasks = [VIDEO]

    def load(self):
        self.task_video = self.tasks_manager.get_task(VIDEO)
        self.task_video.load_finished.connect(self.load_finished.emit)
        self.task_video.load()

    def download(self):
        self.task_video = self.tasks_manager.get_task(VIDEO)
        self.task_video.download_finished.connect(self.start_post_acquisition)
        self.task_video.progress.connect(self.progress.emit)
        self.task_video.download()
