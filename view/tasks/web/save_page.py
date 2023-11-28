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
from view.scrapers.web.full_page_screenshot import (
    FullPageScreenShot as WebFullPageScreenShot,
)


from common.constants import logger


class TaskSavePage(Task):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.SAVE_PAGE

    def start(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.set_message_on_the_statusbar(logger.SAVE_PAGE_STARTED)
        self.started.emit()

        self.acquisition_directory = self.options["acquisition_directory"]
        self.current_widget = self.options["current_widget"]

        acquisition_page_folder = os.path.join(
            self.acquisition_directory, "acquisition_page"
        )
        if not os.path.isdir(acquisition_page_folder):
            os.makedirs(acquisition_page_folder)

        self.current_widget.saveResourcesFinished.connect(self.__finished)
        self.current_widget.save_resources(acquisition_page_folder)

    def __finished(self):
        self.logger.info(logger.SAVE_PAGE)
        self.set_message_on_the_statusbar(logger.SAVE_PAGE_COMPLETED)
        self.upadate_progress_bar()

        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()
