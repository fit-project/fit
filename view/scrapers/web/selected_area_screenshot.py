#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import time
from PyQt6 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab


# Refer to https://github.com/harupy/snipping-tool
class SnippingWidget(QtWidgets.QWidget):
    is_snipping = False

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(
            QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.FramelessWindowHint
        )

        self.setGeometry(0, 0, self.screen().size().width(), self.screen().size().height())
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.onSnippingCompleted = None
        self.scale_factor = self.screen().devicePixelRatio()

    def start(self):
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor)
        )
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
            qp.setPen(QtGui.QPen(QtGui.QColor("red"), lw))
        else:
            brush_color = (0, 0, 0, 0)
            lw = 3
            opacity = 0.1
            qp.setPen(QtGui.QPen(QtGui.QColor("green"), lw))

        self.setWindowOpacity(opacity)
        qp.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRectF(
            self.begin.x(),
            self.begin.y(),
            abs(self.end.x() - self.begin.x()),
            abs(self.end.y() - self.begin.y()),
        )
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
        x1, y1, x2, y2 = self.apply_scaling_factor(x1, y1, x2, y2)

        self.repaint()
        QtWidgets.QApplication.processEvents()
        if x1 != x2 and y1 != y2:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        else:
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()

    def apply_scaling_factor(self, x1, y1, x2, y2):
        x1 *= self.scale_factor
        y1 *= self.scale_factor
        x2 *= self.scale_factor
        y2 *= self.scale_factor
        return int(x1), int(y1), int(x2), int(y2)


class SelectAreaScreenshot(QtCore.QObject):
    finished = QtCore.pyqtSignal()  # give worker class a finished signal

    def __init__(self, filename, parent=None):
        super(SelectAreaScreenshot, self, ).__init__(parent=parent)
        self.filename = filename
        self.snippingWidget = SnippingWidget()
        self.snippingWidget.onSnippingCompleted = self.__on_snipping_completed

    def __on_snipping_completed(self, frame):
        if frame is None:
            self.__finished()
            return
        time.sleep(1)
        frame.save(self.filename)
        self.__finished()

    def snip_area(self):
        self.snippingWidget.start()

    def __finished(self):
        self.finished.emit()
        self.deleteLater()
