#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
import webbrowser
from common.constants.view import video


# Create a clickable label to open the browser
class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: #0067C0;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            url = video.SUPPORTED_SITES_LIST
            webbrowser.open(url)

    def enterEvent(self, event):
        self.setStyleSheet("color: #0067C0; text-decoration: underline;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setStyleSheet("color: #0067C0; text-decoration: none;")
