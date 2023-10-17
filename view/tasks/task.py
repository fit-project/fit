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

from common.constants import state as STATE, status as STATUS


class Task(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, options, logger, table, progress_bar, status_bar, parent):
        super().__init__(parent)
        self.options = options
        self.logger = logger
        self.table = table
        self.progress_bar = progress_bar
        self.status_bar = status_bar

        self.state = STATE.INITIALIZATED
        self.status = STATUS.DONE
        self.details = ""
        self.table.add_task(self.name, self.state, self.status, self.details)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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

    def upadate_progress_bar(self):
        if self.progress_bar is not None:
            self.progress_bar.setValue(self.progress_bar.value() + self.increment)

    def set_message_on_the_statusbar(self, message):
        if self.status_bar is not None:
            self.status_bar.showMessage(message)

    def update_table(self):
        row = self.table.get_row(self.name)
        if row >= 0:
            self.table.update_task(row, self.state, self.status, self.details)

    def update_task(self, state, status, details=""):
        self.state = state
        self.status = status
        self.details = details
        self.update_table()
