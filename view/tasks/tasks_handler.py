#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


class TasksHandler(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(TasksHandler, cls).__new__(cls)
            cls.__tasks = []
        return cls.instance

    def add_task(self, task):
        task.finished.connect(self.__task_is_completed)
        self.__tasks.append(task)

    def __task_is_completed(self):
        task = self.sender()
        print(task.name)
