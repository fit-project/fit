#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
from PyQt6 import QtGui, QtCore, QtWidgets

from common.utility import resolve_path
from common.constants.view import general
from view.tasks.tasks_handler import TasksHandler


class TasksInfo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TasksInfo, self).__init__(parent)
        self.task_handler = TasksHandler()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.setObjectName("AcquisitionStatusView")
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(general.INFO)
        self.icon = QtGui.QIcon(
            os.path.join(resolve_path("assets/svg/acquisition"), "info-circle.svg")
        )

        self.table = QtWidgets.QTableWidget(self)

        self.table.resize(500, 400)

        self.table.setColumnCount(3)
        self.table.setColumnWidth(0, 250)

        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "State", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.__load_current_tasks()

    def __load_current_tasks(self):
        for task in self.task_handler.get_tasks():
            row = self.table.rowCount()
            self.table.insertRow(row)
            status = QtWidgets.QTableWidgetItem(task.status)

            if task.details:
                status.setIcon(self.icon)
                status.setToolTip(task.details)

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(task.label))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(task.state))
            self.table.setItem(row, 2, status)

        if self.task_handler.get_tasks():
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item is not None:
                    item.setFlags(
                        QtCore.Qt.ItemFlag.ItemIsEnabled
                        | QtCore.Qt.ItemFlag.ItemIsSelectable
                    )
