#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging.config
from PyQt6.QtCore import QObject, pyqtSignal

from view.acquisition.post import PostAcquisition
from view.tasks.tasks_manager import TasksManager
from view.tasks.class_names import *
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck


from common.utility import get_ntp_date_and_time
from common.config import LogConfigTools

from common.constants import logger


class Acquisition(QObject):
    post_acquisition_is_finished = pyqtSignal()
    start_tasks_is_finished = pyqtSignal()
    stop_tasks_is_finished = pyqtSignal()

    def __init__(self, options, logger, progress_bar, status_bar, parent=None):
        super.__init__(parent)
        self.folder = options["acquisition_folder"]
        self.logger = logger
        self.log_confing = LogConfigTools()
        self.start_tasks = list()
        self.stop_tasks = list()
        self.post_tasks = [ZIP_AND_REMOVE_FOLDER, HASH, TIMESTAMP, PEC_AND_DOWNLOAD_EML]

        if self.logger.name == "view.web.web":
            self.log_confing.set_dynamic_loggers()

        self.log_confing.change_filehandlers_path(self.folder)
        logging.config.dictConfig(self.log_confing.config)

        __all_tasks = self.start_tasks + self.stop_tasks + self.post_tasks
        self.tasks_manager = TasksManager(parent)
        self.tasks_manager.init_tasks(
            __all_tasks, options, logger, progress_bar, status_bar
        )

        self.post_acquisition = PostAcquisition()
        self.post_acquisition.finished.connect(self.post_acquisition_is_finished.emit)

    def start(self):
        self.log_start_message()

        for name in self.start_tasks:
            task = self.tasks_manager.get_task(name)
            if task:
                task.started.connect(self.__started_task_handler)
                task.increment = self.calculate_increment()
                task.start()
            else:
                self.start_tasks.remove(name)

        if len(self.start_tasks) == 0:
            self.start_tasks_is_finished.emit()

    def __started_task_handler(self):
        if self.tasks_manager.are_task_names_completed(self.start_tasks):
            self.start_tasks_is_finished.emit()

    def stop(self):
        self.log_stop_message()
        for name in self.stop_tasks:
            task = self.tasks_manager.get_task(name)
            if task:
                task.finished.connect(self.__finished_task_handler)
                task.increment = self.calculate_increment()
                if getattr(task, "__is_infinite_loop__"):
                    task.stop()
                else:
                    task.start()
            else:
                self.stop_tasks.remove(name)

        if len(self.stop_tasks) == 0:
            self.stop_tasks_is_finished.emit()

    def __finished_task_handler(self):
        if self.tasks_manager.are_task_names_completed(self.stop_tasks):
            self.stop_tasks_is_finished.emit()

    def start_post_acquisition(self):
        self.post_acquisition.start_post_acquisition_sequence(
            self.calculate_increment()
        )

    def log_start_message(self):
        self.logger.info(logger.ACQUISITION_STARTED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("start", self.get_time()))

    def log_stop_message(self):
        self.logger.info(logger.ACQUISITION_STOPPED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("stop", self.get_time()))

    def log_end_message(self):
        self.logger.info(logger.ACQUISITION_FINISHED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("stop", self.get_time()))

    def get_time(self):
        return get_ntp_date_and_time(
            NetworkControllerCheck().configuration["ntp_server"]
        )

    def calculate_increment(self, tasks):
        return 100 / len(self.tasks_manager.get_tasks())
