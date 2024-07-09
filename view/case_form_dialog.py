#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets, uic

from view.case_form_manager import CaseFormManager
from common.utility import resolve_path, get_version

from controller.case import Case as CaseController
from common.constants.view.case import *


class CaseFormDialog(QtWidgets.QDialog):
    def __init__(self, case_info=None, parent=None):
        super(CaseFormDialog, self).__init__(parent)

        self.__case_info = case_info

        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/case/case.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # SET VERSION
        self.version.setText("v" + get_version())

        # CANCEL BUTTON
        self.cancel_button.clicked.connect(self.reject)
        # SAVE BUTTON
        self.save_button.clicked.connect(self.accept)

        case_name = self.__case_info.get("name")
        self.form_manager = CaseFormManager(self.findChild(QtWidgets.QFrame, "form"))

        self.name = self.findChild(QtWidgets.QComboBox, "name")
        self.name.setCurrentText(case_name)
        self.name.lineEdit().setReadOnly(True)

        if case_name not in self.form_manager.controller.names:
            self.form_manager.cases.append(self.__case_info)

        id = -1
        if "id" in self.__case_info:
            id = self.__case_info.get("id")

        self.title_right_info.setText(DIALOG_TITLE.format(case_name, str(id)))

        self.form_manager.set_case_information()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def accept(self):
        self.__case_info = self.form_manager.get_current_case_info()
        CaseController().cases = self.__case_info
        return super().accept()

    def reject(self):
        return super().reject()
