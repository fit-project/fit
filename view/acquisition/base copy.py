#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from common.constants import logger, status as Status, state as State

import logging.config
from common.config import LogConfigTools
import common.utility

from PyQt6.QtCore import QObject

from view.acquisition.info import AcquisitionInfo
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck


class Base(QObject):
    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None) -> None:
        super().__init__(parent)
        self.logger = logger
        self.log_confing = LogConfigTools()
        self.is_started = False
        self.is_completed = False
        self.send_pyqt_signal = False
        self.increment = 0
        self.total_internal_tasks = 0
        self.total_tasks = 0
        self.info = AcquisitionInfo(parent)

        self.__tasks = []
        self.__progress_bar = progress_bar
        self.__status_bar = status_bar

    def log_start_message(self):
        self.logger.info(logger.ACQUISITION_STARTED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("start", self.get_time()))

    def log_stop_message(self, url):
        self.logger.info(logger.ACQUISITION_STOPPED)
        self.logger.info(logger.ACQUISITION_URL.format(url))

    def log_end_message(self):
        self.logger.info(logger.ACQUISITION_FINISHED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("stop", self.get_time()))

    def add_task(self, task, details=""):
        self.__tasks.append(task)
        self.info.add_task(task.name, task.state, task.status, details)

    def set_state_and_status_tasks(self, task_state, task_status):
        for task in self.__tasks:
            self.update_task(task.name, task_state, task_status)

    def update_task(self, task_name, task_state, task_status, details=""):
        task = self.get_task(task_name)
        if task:
            if task_state is not None:
                task[0].state = task_state
            else:
                task_state = task[0].state

            if task_status is not None:
                task[0].status = task_status
            else:
                task_status = task[0].status

        row = self.info.get_row(task_name)
        if row >= 0:
            self.info.update_task(row, task_state, task_status, details)

    def check_if_all_tasks_have_same_state(self, state_to_check):
        same_state = False

        if len(self.__tasks) == self.total_internal_tasks:
            state = [task.state for task in self.__tasks]
            state = list(set(state))
            if len(state) == 1 and state[0] == state_to_check:
                same_state = True

        return same_state

    def are_all_tasks_status_completed(self):
        is_completed = False

        if len(self.__tasks) == self.total_internal_tasks:
            status = [task.status for task in self.__tasks]
            status = list(set(status))
            if len(status) == 1 and status[0] == Status.COMPLETED:
                is_completed = True

        return is_completed

    def get_tasks(self):
        return self.__tasks

    def clear_tasks(self):
        self.__tasks.clear()

    def get_task(self, task_name):
        return list(filter(lambda task: task.name == task_name, self.__tasks))

    def set_completed_progress_bar(self):
        if self.__progress_bar:
            self.increment = 100 - self.__progress_bar.value()
            self.upadate_progress_bar()

    def upadate_progress_bar(self):
        if self.__progress_bar:
            self.__progress_bar.setValue(self.__progress_bar.value() + self.increment)

    def set_message_on_the_statusbar(self, message):
        if self.__status_bar:
            self.__status_bar.showMessage(message)

    def get_time(self):
        return common.utility.get_ntp_date_and_time(
            NetworkControllerCheck().configuration["ntp_server"]
        )
