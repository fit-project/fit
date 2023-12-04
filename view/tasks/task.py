#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import typing
from PyQt6.QtCore import QObject, pyqtSignal

from common.constants.view.tasks import status as Status, state as State
from view.tasks.tasks_handler import TasksHandler


class Task(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, logger, progress_bar, status_bar, parent):
        super().__init__(parent)

        self.is_infinite_loop = False

        self.logger = logger
        self.progress_bar = progress_bar
        self.status_bar = status_bar

        self.state = State.INITIALIZATED
        self.status = Status.SUCCESS
        self.details = ""
        self.task_handler = TasksHandler()
        self.task_handler.add_task(self)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details):
        self._details = details

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, increment):
        self._increment = increment

    @property
    def sub_tasks(self):
        return self._sub_tasks

    @property
    def is_infinite_loop(self):
        return self._is_infinite_loop

    @is_infinite_loop.setter
    def is_infinite_loop(self, is_infinite_loop):
        self._is_infinite_loop = is_infinite_loop

    @sub_tasks.setter
    def sub_tasks(self, sub_tasks):
        self._sub_tasks = sub_tasks

    def upadate_progress_bar(self):
        if self.progress_bar is not None:
            self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

    def set_message_on_the_statusbar(self, message):
        if self.status_bar is not None:
            self.status_bar.showMessage(message)

    def update_task(self, state, status, details=""):
        self.state = state
        self.status = status
        self.details = details
