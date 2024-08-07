#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import (
    QAbstractListModel,
    Qt,
    QPersistentModelIndex,
    pyqtSlot,
)
from PyQt6.QtWidgets import QApplication

__is_tab__ = False


class ScreenListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        app = QApplication.instance()
        app.screenAdded.connect(self.screens_changed)
        app.screenRemoved.connect(self.screens_changed)
        app.primaryScreenChanged.connect(self.screens_changed)
        self.checks = {}

    def rowCount(self, index):
        return len(QGuiApplication.screens())

    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.CheckState.Unchecked

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        screen_list = QGuiApplication.screens()
        row = index.row()
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            screen = screen_list[row]
            w = screen.size().width()
            h = screen.size().height()
            dpi = screen.logicalDotsPerInch()
            return f'"{screen.name()}" {w}x{h}, {dpi}DPI'
        elif role == Qt.ItemDataRole.CheckStateRole and col == 0:
            return self.checkState(QPersistentModelIndex(index))
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):

        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.CheckStateRole:
            if self.rowCount(index) == 1 and value == 0:
                value = 2
            self.checks.clear()
            self.checks[QPersistentModelIndex(index)] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable

    def screen(self, index):
        return QGuiApplication.screens()[index.row()]

    @pyqtSlot()
    def screens_changed(self):
        self.beginResetModel()
        self.endResetModel()
