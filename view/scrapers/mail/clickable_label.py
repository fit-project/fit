#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import webbrowser

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from common.constants.view import mail


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            url = mail.TWO_FACTOR_AUTH_URL
            webbrowser.open(url)

    def enterEvent(self, event):
        self.setStyleSheet("text-decoration: underline;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setStyleSheet("text-decoration: none;")
