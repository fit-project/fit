#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2023 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 
import os
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QRect, Qt, QObject
from PyQt5.QtWidgets import QWidget, QDialog, QLabel


class Spinner(QObject):
	
    def __init__(self):
        super().__init__()
       
        self.initUI()

    def initUI(self):
        self.widget = QWidget()
        self.widget.resize(200, 200)
        self.widget.setWindowFlags(Qt.FramelessWindowHint)
        self.widget.setAttribute(Qt.WA_TranslucentBackground)
        self.centralwidget = QWidget(self.widget)       
        self.label = QLabel(self.centralwidget)
        self.label.setGeometry(QRect(0, 0, 200, 200))
        self.movie = QMovie(os.path.join('assets/images/', 'loader.gif'))
        self.label.setMovie(self.movie)

    def start(self):
        self.movie.start()
        self.widget.show()

    def stop(self):
        self.movie.stop()
        self.widget.hide()