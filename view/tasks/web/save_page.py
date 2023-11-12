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


class SavePage(QObject):
    finished = pyqtSignal()
    started = pyqtSignal()

    def set_options(self, options):
        self.folder = options["screenshot_directory"]
        self.current_widget = options["current_widget"]

    def start(self):
        self.started.emit()
        self.folder = os.path.join(self.folder, "acquisition_page")
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)

        self.current_widget.saveResourcesFinished.connect(self.finished.emit)
        self.current_widget.save_resources(self.acquisition_page_folder)


class TaskSavePage(Task):
    def __init__(
        self, options, logger, progress_bar=None, status_bar=None, parent=None
    ):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.label = labels.SAVE_PAGE

        self.save_page_thread = QThread()
        self.save_page = SavePage()
        self.save_page.moveToThread(self.save_page_thread)
        self.save_page_thread.started.connect(self.save_page.start)
        self.save_page.started.connect(self.__started)
        self.save_page.finished.connect(self.__finished)

    def start(self):
        self.save_page.set_options(self.options)
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.SAVE_PAGE_STARTED)
        self.save_page_thread.start()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def __finished(self):
        self.logger.info(logger.SAVE_PAGE)
        self.set_message_on_the_statusbar(logger.SAVE_PAGE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

        self.save_page_thread.quit()
        self.save_page_thread.wait()
