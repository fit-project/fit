#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QRect, Qt, QObject
from PyQt6.QtWidgets import QWidget, QDialog, QLabel


class Spinner(QDialog):
	
    def __init__(self):
        super().__init__()
       
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(200, 200)
        self.centralwidget = QWidget(self)       
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(0, 0, 200, 200))
        self.movie = QMovie(os.path.join('assets/images/', 'loader.gif'))
        self.label.setMovie(self.movie)
        self.setModal(True)

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.hide()