#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import sys
from PyQt6 import QtCore, QtGui, QtWidgets, uic

from common.utility import resolve_path, get_version
from common.constants.view import general
from view.tasks.tasks_handler import TasksHandler


class TasksInfo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TasksInfo, self).__init__(parent)
        self.task_handler = TasksHandler()
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/taskinfo/taskinfo.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # SET VERSION
        self.version.setText("v" + get_version())

        self.icon = QtGui.QIcon(
            os.path.join(resolve_path("ui/icons"), "info-circle.png")
        )

        self.acquisition_table_info.setColumnCount(3)
        self.acquisition_table_info.setColumnWidth(0, 250)

        # Set the table headers
        self.acquisition_table_info.setHorizontalHeaderLabels(
            ["Task", "State", "Status"]
        )
        self.acquisition_table_info.horizontalHeader().setStretchLastSection(True)
        self.__load_current_tasks()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __load_current_tasks(self):
        for task in self.task_handler.get_tasks():
            row = self.acquisition_table_info.rowCount()
            self.acquisition_table_info.insertRow(row)
            status = QtWidgets.QTableWidgetItem(task.status)

            if task.details:
                status.setIcon(self.icon)
                status.setToolTip(task.details)

            self.acquisition_table_info.setItem(
                row, 0, QtWidgets.QTableWidgetItem(task.label)
            )
            self.acquisition_table_info.setItem(
                row, 1, QtWidgets.QTableWidgetItem(task.state)
            )
            self.acquisition_table_info.setItem(row, 2, status)

        if self.task_handler.get_tasks():
            for column in range(self.acquisition_table_info.columnCount()):
                item = self.acquisition_table_info.item(row, column)
                if item is not None:
                    item.setFlags(
                        QtCore.Qt.ItemFlag.ItemIsEnabled
                        | QtCore.Qt.ItemFlag.ItemIsSelectable
                    )
