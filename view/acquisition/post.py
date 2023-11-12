#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
from PyQt6.QtCore import QObject, pyqtSignal

from view.tasks.tasks_handler import TasksHandler
from view.tasks.class_names import *


class PostAcquisition(QObject):
    finished = pyqtSignal()

    def __init__(self, parent: None):
        self.task_handler = TasksHandler()
        super().__init__(parent)

    def start_post_acquisition_sequence(self, increment):
        self.increment = increment
        self.__zip_and_remove()

    def __zip_and_remove(self):
        task = self.task_handler.get_task(ZIP_AND_REMOVE_FOLDER)
        if task:
            task.finished.connect(self.__calculate_acquisition_file_hash)
            task.increment = self.increment
            task.start()

    def __calculate_acquisition_file_hash(self):
        task = self.task_handler.get_task(HASH)
        if task:
            task.finished.connect(self.__generate_pdf_report)
            task.increment = self.increment
            task.start()

    def __generate_pdf_report(self):
        task = self.task_handler.get_task(REPORT)
        if task:
            task.finished.connect(self.__generate_timestamp_report)
            task.increment = self.increment
            task.start()

    def __generate_timestamp_report(self):
        task = self.task_handler.get_task(REPORT)
        if task:
            task.finished.connect(self.__send_pec_and_download_eml)
            task.increment = self.increment
            task.start()
        else:
            task.finished.connect(self.finished.emit)

    def __send_pec_and_download_eml(self):
        task = self.task_handler.get_task(PEC_AND_DOWNLOAD_EML)
        if task:
            task.finished.connect(self.finished.emit)
            task.increment = self.increment
            task.start()
        else:
            task.finished.connect(self.finished.emit)
