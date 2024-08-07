#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QAbstractListModel, Qt, QPersistentModelIndex, pyqtSlot
from PyQt6.QtMultimedia import QWindowCapture

__is_tab__ = False


class WindowListModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_list = QWindowCapture.capturableWindows()
        self.checks = {}

    def rowCount(self, QModelIndex):
        return len(self._window_list)

    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            return Qt.CheckState.Unchecked

    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            window = self._window_list[row]
            return window.description()
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

    def window(self, index):
        return self._window_list[index.row()]

    @pyqtSlot()
    def populate(self):
        self.beginResetModel()
        self._window_list = QWindowCapture.capturableWindows()
        self.endResetModel()
