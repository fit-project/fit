#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtGui, QtWidgets

from view.case_form import CaseForm


from controller.case import Case as CaseController
from common.constants.view.case import *


class Case(QtWidgets.QDialog):
    def __init__(self, case_info, parent=None):
        super(Case, self).__init__(parent)

        self.case_info = case_info

        self.setObjectName("Case")
        self.setFixedSize(479, 400)
        self.setWindowTitle(
            DIALOG_TITLE.format(self.case_info["name"], str(self.case_info["id"]))
        )
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        self.initUI()
        self.__set_current_config_values()

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def initUI(self):
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setGeometry(QtCore.QRect(10, 350, 441, 32))
        self.button_box.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Save
        )
        self.button_box.setCenterButtons(False)
        self.button_box.setObjectName("save")
        self.form = CaseForm(self)

    def __set_current_config_values(self):
        self.form.set_index_from_case_id(self.case_info["id"])
        self.form.name.setEnabled(False)
        self.form.set_case_information()

    def accept(self) -> None:
        self.case_info = self.form.get_current_case_info()
        CaseController().cases = self.case_info
        return super().accept()

    def reject(self) -> None:
        return super().reject()
