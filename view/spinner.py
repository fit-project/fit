#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

import PyQt6
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QDialog, QLabel

from common.utility import resolve_path


class Spinner(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowFlag(PyQt6.QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(PyQt6.QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.width = 200
        self.height = 200
        self.resize(self.width, self.height)
        self.centralwidget = QWidget(self)
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(0, 0, self.width, self.height))
        self.movie = QMovie(os.path.join(resolve_path("assets/images/"), "loader.gif"))
        self.label.setMovie(self.movie)
        self.setModal(True)

    def set_position(self, x, y):
        widget_x = int(x - self.width / 2)
        widget_y = int(y - self.height / 2)
        self.move(widget_x, widget_y)

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()
