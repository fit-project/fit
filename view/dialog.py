#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
from PyQt6 import QtCore, QtWidgets, QtGui, uic
from common.utility import resolve_path
from common.constants.view.general import *
from enum import Enum


class DialogButtonTypes(Enum):
    MESSAGE = 1
    QUESTION = 2


class Dialog(QtWidgets.QDialog):
    def __init__(self, title, message, details=None, severity=None, parent=None):
        super(Dialog, self).__init__(parent)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__init_ui()
        self.__set_icon_severity(severity)
        self.__set_title(title)
        self.__set_message(message)
        self.__set_details(details)
        self.__set_buttons_message()
        self.contentBox.adjustSize()
        self.setMinimumWidth(self.contentBox.width())
        self.contentTopBg.setMinimumWidth(self.contentBox.width())

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/dialog/multipurpose.ui"), self)
        self.title = self.findChild(QtWidgets.QLabel, "titleRightInfo")
        self.close_button = self.findChild(QtWidgets.QPushButton, "closeButton")
        self.left_button = self.findChild(QtWidgets.QPushButton, "left_button")
        self.right_button = self.findChild(QtWidgets.QPushButton, "right_button")
        self.message = self.findChild(QtWidgets.QLabel, "message")
        self.details = self.findChild(QtWidgets.QLabel, "details")
        self.icon_severity = self.findChild(QtWidgets.QLabel, "icon_severity")
        self.contentBox = self.findChild(QtWidgets.QFrame, "contentBox")
        self.contentTopBg = self.findChild(QtWidgets.QFrame, "contentTopBg")

    def set_buttons_type(self, buttons_type):
        if buttons_type == DialogButtonTypes.MESSAGE:
            self.__set_buttons_message()
        elif buttons_type == DialogButtonTypes.QUESTION:
            self.__set_buttons_question()

    def __set_title(self, title):
        self.title.setText(title)

    def __set_icon_severity(self, severity):
        if severity is not None:
            icon = None
            if severity == QtWidgets.QMessageBox.Icon.Warning:
                icon = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
            elif severity == QtWidgets.QMessageBox.Icon.Information:
                icon = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation
            elif severity == QtWidgets.QMessageBox.Icon.Question:
                icon = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion
            elif severity == QtWidgets.QMessageBox.Icon.Critical:
                icon = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical

            if icon is not None:
                icon = self.style().standardIcon(icon)
                self.icon_severity.setPixmap(
                    icon.pixmap(icon.actualSize(QtCore.QSize(42, 42)))
                )
            else:
                self.icon_severity.hide()

        else:
            self.icon_severity.hide()

    def __set_message(self, message):
        self.message.setText(message)

    def __set_details(self, details):
        self.details.setText(details)

    def __set_buttons_message(self):
        self.close_button.hide()
        self.left_button.hide()
        self.right_button.setText(OK)

    def __set_buttons_question(self):
        self.close_button.hide()
        self.left_button.setText(YES)
        self.right_button.setText(NO)
        self.left_button.show()
