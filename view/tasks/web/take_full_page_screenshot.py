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


class FullPageScreenShot(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.folder = options["screenshot_directory"]
        self.current_widget = options["current_widget"]

    def start(self):
        self.started.emit()
        full_page_screenshot = WebFullPageScreenShot(self.folder, self.current_widget)
        full_page_screenshot.take_screenshot()
        self.finished.emit()


class TaskFullPageScreenShot(Task):
    def __init__(
        self, options, logger, progress_bar=None, status_bar=None, parent=None
    ):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.label = labels.TAKE_FULL_PAGE_SCREENSHOT

        self.full_page_screenshot_thread = QThread()
        self.full_page_screenshot = FullPageScreenShot()
        self.full_page_screenshot.moveToThread(self.full_page_screenshot_thread)
        self.full_page_screenshot_thread.started.connect(
            self.full_page_screenshot.start
        )
        self.full_page_screenshot.started.connect(self.__started)
        self.full_page_screenshot.finished.connect(self.__finished)

    def start(self):
        self.full_page_screenshot.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.TAKE_FULL_PAGE_SCREENSHOT_STARTED)
        self.full_page_screenshot_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.TAKE_FULL_PAGE_SCREENSHOT)
        self.set_message_on_the_statusbar(logger.TAKE_FULL_PAGE_SCREENSHOT_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.full_page_screenshot_thread.quit()
        self.full_page_screenshot_thread.wait()
