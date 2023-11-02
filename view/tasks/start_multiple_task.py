#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal

import view.tasks
import pkgutil
import sys
from inspect import isclass
from importlib import import_module
from view.tasks.tasks_handler import TasksHandler
from view.tasks import class_names


class StartMultipleTask(QObject):
    all_task_list_completed = pyqtSignal()

    def __init__(self, options, logger, progress_bar, status_bar, task_list, parent):
        super().__init__(parent)
        self.options = options
        self.logger = logger
        self.progress_bar = progress_bar
        self.status_bar = status_bar
        self.task_list = task_list
        self.class_names_modules = {}
        self.task_handler = TasksHandler()
        self.__load_tasks()

    def __load_tasks(self):
        package = view.tasks
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__, prefix=package.__name__ + ".", onerror=lambda x: None
        ):
            # import module if not loaded
            if modname not in sys.modules and not ispkg:
                import_module(modname)

            if modname in sys.modules and not ispkg:
                class_name = class_names.__dict__.get(modname.rsplit(".", 1)[1].upper())

                if class_name and isclass(getattr(sys.modules[modname], class_name)):
                    self.class_names_modules.setdefault(class_name, []).append(
                        sys.modules[modname]
                    )

    def start(self):
        for key in self.class_names_modules.keys():
            if key in self.task_list:
                value = self.class_names_modules.get(key)[0]
                task = getattr(value, key)
                task = task(
                    self.options, self.logger, self.progress_bar, self.status_bar
                )
                task.finished.connect(self.__task_is_completed)

    def __task_is_completed(self):
        if self.task_handler.are_task_names_completed(self.task_list):
            self.all_task_list_completed.emit()
