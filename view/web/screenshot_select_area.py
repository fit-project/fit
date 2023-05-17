#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

import numpy as np
import cv2
from PIL import ImageGrab, Image

# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QtWidgets.QWidget):
    is_snipping = False

    def __init__(self, parent=None, app=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        self.screen = app.primaryScreen()
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.onSnippingCompleted = None


    def start(self):
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.show()

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            self.begin = QtCore.QPointF()
            self.end = QtCore.QPointF()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRectF(self.begin.x(), self.begin.y(),
                             abs(self.end.x() - self.begin.x()), abs(self.end.y() - self.begin.y()))
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.is_snipping = False
        QtWidgets.QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()

class SelectArea(QtCore.QObject):
    finished = QtCore.pyqtSignal()  # give worker class a finished signal

    def __init__(self, filename, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.filename = filename
        self.snippingWidget = SnippingWidget(app=QtWidgets.QApplication.instance())
        self.snippingWidget.onSnippingCompleted = self.__on_snipping_completed

    
    def __on_snipping_completed(self, frame):
        if frame is None:
            self.__finished()
            return 
        
        frame.save(self.filename)
        self.__finished()

    def snip_area(self):
        self.snippingWidget.start()

    def __finished(self):
          self.finished.emit()
          self.deleteLater()