#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtWidgets


class Check(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)

    def __init__(self, parent=...):
        super().__init__(parent)
        self.debug_mode = "--debug" in QtWidgets.QApplication.instance().arguments()

    def run_check(self):
        pass
