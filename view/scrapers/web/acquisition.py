#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from view.acquisition.acquisition import Acquisition, AcquisitionStatus
from PyQt6.QtCore import pyqtSignal
from view.tasks.class_names import *


class WebAcquisition(Acquisition):
    task_screenrecorder_is_finished = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.start_tasks = [SCREENRECORDER, PACKETCAPTURE]
        self.stop_tasks = [
            WHOIS,
            NSLOOKUP,
            HEADERS,
            SSLKEYLOG,
            SSLCERTIFICATE,
            TRACEROUTE,
            PACKETCAPTURE,
            TAKE_FULL_PAGE_SCREENSHOT,
            SAVE_PAGE,
        ]

    def stop_screen_recorder(self):
        task = self.tasks_manager.get_task(SCREENRECORDER)
        if task:
            task.finished.connect(self.task_screenrecorder_is_finished.emit)
            task.stop()
        else:
            self.task_screenrecorder_is_finished.emit()
