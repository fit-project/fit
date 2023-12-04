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
from common.constants.view.tasks import state


class Acquisition(QObject):
    post_acquisition_is_finished = pyqtSignal()
    start_tasks_is_finished = pyqtSignal()
    stop_tasks_is_finished = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent):
        super().__init__(parent)
        self.progress_bar = progress_bar
        self.status_bar = status_bar
        self.logger = logger
        self.options = dict()

        self.log_confing = LogConfigTools()
        self.tasks_manager = TasksManager(parent)

        self.options = dict()

        self.start_tasks = list()
        self.stop_tasks = list()
        self.post_tasks = [
            ZIP_AND_REMOVE_FOLDER,
            HASH,
            REPORT,
            TIMESTAMP,
            PEC_AND_DOWNLOAD_EML,
        ]

        self.post_acquisition = PostAcquisition(self.parent())
        self.post_acquisition.finished.connect(self.post_acquisition_is_finished.emit)
        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def load_tasks(self):
        if self.logger.name == "view.scrapers.web.web":
            self.log_confing.set_dynamic_loggers()

        self.log_confing.change_filehandlers_path(self.options["acquisition_directory"])
        logging.config.dictConfig(self.log_confing.config)

        __all_tasks = self.start_tasks + self.stop_tasks + self.post_tasks

        self.tasks_manager.init_tasks(
            __all_tasks, self.logger, self.progress_bar, self.status_bar
        )

    def unload_tasks(self):
        for task in self.tasks_manager.get_tasks():
            task.deleteLater()

        self.tasks_manager.clear_tasks()

    def start(self):
        self.log_start_message()
        tasks = self.tasks_manager.get_tasks_from_class_name(self.start_tasks)

        if len(tasks) == 0:
            self.start_tasks_is_finished.emit()
        else:
            for task in tasks:
                task.started.connect(self.__started_task_handler)
                task.options = self.options
                task.increment = self.calculate_increment()
                task.start()

    def __started_task_handler(self):
        if self.tasks_manager.are_task_names_in_the_same_state(
            self.start_tasks, state.STARTED
        ):
            self.start_tasks_is_finished.emit()

    def stop(self):
        self.log_stop_message()
        tasks = self.tasks_manager.get_tasks_from_class_name(self.stop_tasks)

        if len(tasks) == 0:
            self.stop_tasks_is_finished.emit()
        else:
            for task in tasks:
                task.finished.connect(self.__finished_task_handler)
                task.options = self.options
                task.increment = self.calculate_increment()

                if task.is_infinite_loop:
                    task.stop()
                else:
                    task.start()

    def __finished_task_handler(self):
        if self.tasks_manager.are_task_names_in_the_same_state(
            self.stop_tasks, state.COMPLETED
        ):
            self.stop_tasks_is_finished.emit()

    def start_post_acquisition(self):
        self.post_acquisition.start_post_acquisition_sequence(
            self.calculate_increment(), self.options
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

    def calculate_increment(self):
        return 100 / len(self.tasks_manager.get_tasks())

    def set_completed_progress_bar(self):
        self.progress_bar.setValue(
            self.progress_bar.value() + (100 - self.progress_bar.value())
        )

    def __destroyed_handler(self, __dict):
        self.unload_tasks()
