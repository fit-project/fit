#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import sys
import pkgutil
import importlib
from PyQt6 import QtCore
from view import checks

from view.util import disable_network_functionality, enable_network_functionality

from common.constants.view.tasks import status

from view.checks.admin_privileges import AdminPrivilegesCheck


class InitialChecks(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.predefined_order = [
            "NetworkCheck",
            #"AdminPrivilegesCheck",
            "NpcapInstalledCheck",
            "NvidiaGPUInstalledCheck",
            #"NewPortableVersionCheck",
            "FFmpegInstalledCheck",
        ]
        self.module_instances = self.__load_checks_modules()
        self.current_check_index = 0
        self.__network_status = list()

    def run_checks(self):
        self.__run_next_check()

    def __load_checks_modules(self):
        module_instances = []
        for class_name in self.predefined_order:
            for loader, module_name, is_pkg in pkgutil.iter_modules(checks.__path__):
                full_module_name = f"{checks.__name__}.{module_name}"
                module = importlib.import_module(full_module_name)
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    instance = cls()
                    module_instances.append(instance)
                    break
        return module_instances

    def __run_next_check(self):
        if self.current_check_index < len(self.module_instances):
            instance = self.module_instances[self.current_check_index]
            instance.finished.connect(self.__handle_finished)
            instance.run_check()
        else:
            self.finished.emit()

    def __handle_finished(self, result):
        sender = self.sender()
        class_name = sender.__class__.__name__

        if result == status.FAIL:
            if class_name == "NetworkCheck":
                sys.exit(0)
            elif class_name == "AdminPrivilegesCheck":
                self.__network_status.append(result)
                disable_network_functionality()
            elif class_name == "NpcapInstalledCheck":
                self.__network_status.append(result)
                disable_network_functionality()
        if result == status.SUCCESS:
            if class_name == "AdminPrivilegesCheck":
                self.__network_status.append(result)
            elif class_name == "NpcapInstalledCheck":
                self.__network_status.append(result)

        if len(self.__network_status) >= 2 and len(set(self.__network_status)) == 1:
            enable_network_functionality()

        self.current_check_index += 1
        self.__run_next_check()
