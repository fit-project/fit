#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import state


class TasksHandler(QObject):
    all_tasks_completed = pyqtSignal()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TasksHandler, cls).__new__(cls)
            cls.__tasks = list()
        return cls.instance

    def add_task(self, task):
        task.finished.connect(self.__task_is_completed)
        self.__tasks.append(task)

    def are_task_names_completed(self, names):
        are_completed = False
        __state = list()

        for name in names:
            task = self.get_task(name)

            if task:
                __state.append(task.state)

            if __state:
                __state = list(set(__state))
                if len(__state) == 1 and __state[0] == state.COMPLETED:
                    are_completed = True

        return are_completed

    def get_task(self, name):
        return next(
            (task for task in self.__tasks if task.__class__.__name__ == name), None
        )

    def get_tasks_with_dependencies(self):
        return list(filter(lambda task: len(task.dependencies) >= 1, self.__tasks))

    def __start_tasks_with_dependencies(self):
        for task in self.get_tasks_with_dependencies():
            if task.state is not state.COMPLETED:
                task.start()

    def __are_all_tasks_state_completed(self):
        __state = [task.state for task in self.__tasks]
        __state = list(set(__state))
        if len(__state) == 1 and __state[0] == state.COMPLETED:
            self.all_tasks_completed.emit()

    def __task_is_completed(self):
        self.__start_tasks_with_dependencies()
        self.__are_all_tasks_state_completed()
