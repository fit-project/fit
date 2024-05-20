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

from controller.configurations.tabs.packetcapture.packetcapture import (
    PacketCapture as PacketCaptureCotroller,
)
from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)
from controller.configurations.tabs.timestamp.timestamp import (
    Timestamp as TimestampController,
)
from controller.configurations.tabs.pec.pec import (
    Pec as PecController,
)
from controller.configurations.tabs.network.networktools import (
    NetworkTools as NetworkToolsController,
)

from common.utility import is_npcap_installed, get_platform


class TasksManager(QObject):
    all_task_list_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_names_modules = dict()
        self.task_handler = TasksHandler()
        self.__load_task_modules()

    def __load_task_modules(self):
        package = view.tasks
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__, prefix=package.__name__ + ".", onerror=lambda x: None
        ):
            # import module if not loaded
            if modname not in sys.modules and not ispkg:
                import_module(modname)

            if modname in sys.modules and not ispkg:
                class_name = class_names.__dict__.get(modname.rsplit(".", 1)[1].upper())

                if (
                    class_name
                    and isclass(getattr(sys.modules[modname], class_name))
                    and bool(self.is_enabled_tasks(class_name))
                ):
                    self.class_names_modules.setdefault(class_name, []).append(
                        sys.modules[modname]
                    )

    def is_enabled_tasks(self, tasks):
        if isinstance(tasks, str):
            tasks = self.__remove_disable_tasks([tasks])
        elif isinstance(tasks, list):
            tasks = self.__remove_disable_tasks(tasks)

        return tasks

    def __remove_disable_tasks(self, tasks):
        _tasks = tasks.copy()
        for task in tasks:
            if (
                task == class_names.PACKETCAPTURE
                and PacketCaptureCotroller().options["enabled"] is False
                or task == class_names.SCREENRECORDER
                and ScreenRecorderConfigurationController().options["enabled"] is False
                or task == class_names.TIMESTAMP
                and TimestampController().options["enabled"] is False
                or task == class_names.PEC_AND_DOWNLOAD_EML
                and PecController().options["enabled"] is False
                or task == class_names.SSLKEYLOG
                and NetworkToolsController().configuration["ssl_keylog"] is False
                or task == class_names.SSLCERTIFICATE
                and NetworkToolsController().configuration["ssl_certificate"] is False
                or task == class_names.HEADERS
                and NetworkToolsController().configuration["headers"] is False
                or task == class_names.WHOIS
                and NetworkToolsController().configuration["whois"] is False
                or task == class_names.NSLOOKUP
                and NetworkToolsController().configuration["nslookup"] is False
                or task == class_names.TRACEROUTE
                and NetworkToolsController().configuration["traceroute"] is False
                or get_platform() == "win"
                and is_npcap_installed() is False
            ):
                _tasks.remove(task)

        return _tasks

    def init_tasks(
        self,
        task_list,
        logger,
        progress_bar,
        status_bar,
    ):
        for key in self.class_names_modules.keys():
            if key in task_list:
                value = self.class_names_modules.get(key)[0]
                task = getattr(value, key)
                task = task(logger, progress_bar, status_bar)

    def get_tasks(self):
        return self.task_handler.get_tasks()

    def get_task(self, name):
        return self.task_handler.get_task(name)

    def clear_tasks(self):
        self.task_handler.clear_tasks()

    def get_task_by_class_name(self, name):
        return self.task_handler.get_task(name)

    def get_tasks_from_class_name(self, names):
        tasks = []
        for name in names:
            task = self.get_task_by_class_name(name)
            if task:
                tasks.append(task)
        return tasks

    def are_task_names_in_the_same_state(self, tasks, state):
        return self.task_handler.are_task_names_in_the_same_state(tasks, state)
