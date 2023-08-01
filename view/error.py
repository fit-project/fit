#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
from PyQt6.QtWidgets import QMessageBox
from PyQt6 import QtCore


class Error(QMessageBox):
    def __init__(self, severity, title, message, details, parent=None):
        super(Error, self).__init__(parent)
        # enable custom window hint
        self.setWindowFlags(
            QtCore.Qt.WindowType.CustomizeWindowHint
            | QtCore.Qt.WindowType.WindowTitleHint
        )

        self.setIcon(severity)
        self.setWindowTitle(title)
        self.setText(message)
        self.setInformativeText(details)
