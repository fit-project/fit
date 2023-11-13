#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from common.constants.view.tasks import labels, state, status

from view.tasks.task import Task
from view.web.full_page_screenshot import FullPageScreenShot as WebFullPageScreenShot


from common.constants import logger


class TaskTakeFullPageScreenShot(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.TAKE_FULL_PAGE_SCREENSHOT

    def start(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.set_message_on_the_statusbar(logger.TAKE_FULL_PAGE_SCREENSHOT_STARTED)
        self.started.emit()
        full_page_screenshot = WebFullPageScreenShot(
            self.options["current_widget"],
            self.options["acquisition_directory"],
            self.options["screenshot_directory"],
        )
        full_page_screenshot.is_running_task = True
        full_page_screenshot.take_screenshot()

        self.__finished()

    def __finished(self):
        self.logger.info(logger.TAKE_FULL_PAGE_SCREENSHOT)
        self.set_message_on_the_statusbar(logger.TAKE_FULL_PAGE_SCREENSHOT_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()
